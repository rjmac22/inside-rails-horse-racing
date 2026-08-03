"""Govern Notebook 20 connection-field verification and supplementation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
import re
from typing import Iterable, Mapping

from inside_rails.manual_verifications import ManualVerification

CONNECTION_FIELDS = frozenset({"jockey", "trainer", "owner"})
COMPLETED_DECISIONS = frozenset(
    {"verified_repair", "conflicting_evidence", "insufficient_evidence"}
)
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low"})
EVIDENCE_CONFIDENCE_BY_DECISION = {
    "verified_repair": frozenset({"high", "medium", "low"}),
    "conflicting_evidence": frozenset({"high", "medium", "low", "conflicting"}),
    "insufficient_evidence": frozenset({"high", "medium", "low", "insufficient"}),
}
EXPECTED_EVIDENCE_RECORDS = 46
EXPECTED_VERIFIED_REPAIRS = 28
EXPECTED_UNRESOLVED_RECORDS = 18
EXPECTED_DECISION_COUNTS = {
    "verified_repair": 28,
    "conflicting_evidence": 5,
    "insufficient_evidence": 13,
}
EXPECTED_FIELD_COUNTS = {"jockey": 2, "trainer": 9, "owner": 35}
EXPECTED_REPAIR_FIELD_COUNTS = {"jockey": 2, "trainer": 4, "owner": 22}
EVIDENCE_ID_PATTERN = re.compile(r"^connection_blank_(\d{3})$")
VERIFICATION_ID_PATTERN = re.compile(r"^NB20-CONNECTION-(\d{4})$")

EVIDENCE_REQUIRED_COLUMNS = (
    "repair_record_id",
    "source_rowid",
    "race_id",
    "date",
    "course",
    "off",
    "horse",
    "missing_source_field",
    "proposed_repaired_value",
    "evidence_source_name",
    "evidence_source_type",
    "evidence_locator",
    "evidence_accessed_date",
    "verification_decision",
    "verification_confidence",
    "reviewer_notes",
)

REPAIR_COLUMNS = (
    "verification_id",
    "repair_record_id",
    "source_rowid",
    "source_race_id",
    "source_date",
    "source_course",
    "source_off",
    "source_horse",
    "source_field",
    "raw_source_value",
    "governed_value",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "notes",
    "database_action",
)


@dataclass(frozen=True)
class ConnectionRepair:
    verification_id: str
    repair_record_id: str
    source_rowid: int
    source_race_id: str
    source_date: str
    source_course: str
    source_off: str
    source_horse: str
    source_field: str
    raw_source_value: str
    governed_value: str
    verification_status: str
    evidence_type: str
    evidence_locator: str
    evidence_accessed_date: str
    confidence: str
    notes: str
    database_action: str


@dataclass(frozen=True)
class GovernedConnectionValue:
    raw_value: str | None
    effective_value: str | None
    value_status: str
    verification_id: str | None
    confidence: str | None


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _is_blank(value: object) -> bool:
    return _clean(value) == ""


def _validate_iso_date(value: str, label: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO YYYY-MM-DD, got {value!r}") from exc


def verification_id_for_repair(repair_record_id: str) -> str:
    """Map a Notebook 20 queue identifier to its permanent register identifier."""
    match = EVIDENCE_ID_PATTERN.fullmatch(repair_record_id)
    if not match:
        raise ValueError(f"invalid repair_record_id: {repair_record_id!r}")
    return f"NB20-CONNECTION-{int(match.group(1)):04d}"


def governed_confidence_for_evidence(evidence: Mapping[str, str]) -> str:
    """Map Notebook 20 decision markers onto the permanent confidence scale.

    The notebook used ``conflicting`` and ``insufficient`` as categorical
    markers for unresolved reviews. They are not confidence levels in the
    permanent register. Preserve those markers in notes, but represent the
    unresolved record itself as low confidence.
    """
    repair_id = _clean(evidence.get("repair_record_id"))
    decision = _clean(evidence.get("verification_decision"))
    confidence = _clean(evidence.get("verification_confidence"))

    allowed = EVIDENCE_CONFIDENCE_BY_DECISION.get(decision)
    if allowed is None:
        raise ValueError(f"{repair_id}: invalid or incomplete decision {decision!r}")
    if confidence not in allowed:
        raise ValueError(
            f"{repair_id}: invalid confidence {confidence!r} for decision {decision!r}"
        )
    if confidence in ALLOWED_CONFIDENCE:
        return confidence
    return "low"


def load_connection_evidence(path: str | Path) -> tuple[dict[str, str], ...]:
    """Load and validate the completed 46-row Notebook 20 evidence log."""
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        missing = [column for column in EVIDENCE_REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"connection evidence log is missing columns: {missing}")
        rows = tuple({key: _clean(value) for key, value in row.items()} for row in reader)

    if len(rows) != EXPECTED_EVIDENCE_RECORDS:
        raise ValueError(
            f"expected {EXPECTED_EVIDENCE_RECORDS} evidence rows, found {len(rows)}"
        )

    expected_ids = {f"connection_blank_{number:03d}" for number in range(1, 47)}
    observed_ids = [row["repair_record_id"] for row in rows]
    if len(observed_ids) != len(set(observed_ids)):
        raise ValueError("repair_record_id values must be unique")
    if set(observed_ids) != expected_ids:
        missing_ids = sorted(expected_ids - set(observed_ids))
        extra_ids = sorted(set(observed_ids) - expected_ids)
        raise ValueError(f"unexpected evidence identifiers; missing={missing_ids}, extra={extra_ids}")

    decision_counts: dict[str, int] = {}
    field_counts: dict[str, int] = {}
    verified_field_counts: dict[str, int] = {}

    for row in rows:
        repair_id = row["repair_record_id"]
        field = row["missing_source_field"]
        decision = row["verification_decision"]

        if field not in CONNECTION_FIELDS:
            raise ValueError(f"{repair_id}: invalid connection field {field!r}")
        if decision not in COMPLETED_DECISIONS:
            raise ValueError(f"{repair_id}: invalid or incomplete decision {decision!r}")
        governed_confidence_for_evidence(row)
        if not row["source_rowid"].isdigit():
            raise ValueError(f"{repair_id}: source_rowid must be a positive integer")
        if int(row["source_rowid"]) <= 0:
            raise ValueError(f"{repair_id}: source_rowid must be positive")
        if not row["date"] or not row["course"] or not row["off"] or not row["horse"]:
            raise ValueError(f"{repair_id}: source race and runner locators are required")
        _validate_iso_date(row["date"], f"{repair_id}: date")
        _validate_iso_date(
            row["evidence_accessed_date"], f"{repair_id}: evidence_accessed_date"
        )
        if not row["evidence_source_name"] or not row["evidence_source_type"]:
            raise ValueError(f"{repair_id}: evidence source name and type are required")
        if not row["evidence_locator"]:
            raise ValueError(f"{repair_id}: evidence_locator is required")
        if not row["reviewer_notes"]:
            raise ValueError(f"{repair_id}: reviewer_notes are required")

        repaired_value = row["proposed_repaired_value"]
        if decision == "verified_repair":
            if not repaired_value:
                raise ValueError(f"{repair_id}: verified repairs require a repaired value")
            if "http://" not in row["evidence_locator"] and "https://" not in row["evidence_locator"]:
                raise ValueError(f"{repair_id}: verified repairs require a direct URL locator")
            verified_field_counts[field] = verified_field_counts.get(field, 0) + 1
        elif repaired_value:
            raise ValueError(f"{repair_id}: unresolved decisions must not assign a repair")

        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        field_counts[field] = field_counts.get(field, 0) + 1

    if decision_counts != EXPECTED_DECISION_COUNTS:
        raise ValueError(f"unexpected decision counts: {decision_counts}")
    if field_counts != EXPECTED_FIELD_COUNTS:
        raise ValueError(f"unexpected evidence field counts: {field_counts}")
    if verified_field_counts != EXPECTED_REPAIR_FIELD_COUNTS:
        raise ValueError(f"unexpected verified-repair field counts: {verified_field_counts}")

    return tuple(sorted(rows, key=lambda row: row["repair_record_id"]))


def build_manual_verifications(
    evidence_rows: Iterable[Mapping[str, str]],
) -> tuple[ManualVerification, ...]:
    """Convert completed Notebook 20 evidence into permanent register rows."""
    output: list[ManualVerification] = []
    for evidence in evidence_rows:
        repair_id = evidence["repair_record_id"]
        field = evidence["missing_source_field"]
        decision = evidence["verification_decision"]
        confidence_marker = evidence["verification_confidence"]
        confirmed = decision == "verified_repair"
        source_rowid = evidence["source_rowid"]
        race_id = evidence["race_id"]
        notes = (
            f"{repair_id}; source_rowid={source_rowid}; evidence decision={decision}; "
            f"evidence confidence marker={confidence_marker}. "
            f"{evidence['reviewer_notes']}"
        )
        if confirmed:
            notes += (
                " Apply only to this exact blank source row and field; preserve the "
                "immutable source value and external provenance."
            )
        else:
            notes += " Preserve the source blank as unresolved; do not infer a value."

        output.append(
            ManualVerification(
                verification_id=verification_id_for_repair(repair_id),
                subject_type="runner",
                source_date=evidence["date"],
                source_course=evidence["course"],
                source_off=evidence["off"],
                source_horse=evidence["horse"],
                source_field=field,
                raw_source_value=(
                    f"blank; source_rowid={source_rowid}; race_id={race_id}; "
                    f"repair_record_id={repair_id}"
                ),
                verification_question=(
                    f"Who was the source-presented {field} for this runner in the target race?"
                ),
                verified_value=evidence["proposed_repaired_value"] if confirmed else "",
                verification_status="confirmed" if confirmed else "unresolved",
                evidence_type=evidence["evidence_source_type"],
                evidence_locator=evidence["evidence_locator"],
                evidence_accessed_date=evidence["evidence_accessed_date"],
                governing_notebook="20",
                confidence=governed_confidence_for_evidence(evidence),
                notes=notes,
                database_action=(
                    "source_supplementation" if confirmed else "preserve_raw_unresolved"
                ),
            )
        )
    return tuple(output)


def build_connection_repairs(
    evidence_rows: Iterable[Mapping[str, str]],
) -> tuple[ConnectionRepair, ...]:
    """Build the 28-row governed supplementation reference."""
    repairs: list[ConnectionRepair] = []
    for evidence in evidence_rows:
        if evidence["verification_decision"] != "verified_repair":
            continue
        repairs.append(
            ConnectionRepair(
                verification_id=verification_id_for_repair(evidence["repair_record_id"]),
                repair_record_id=evidence["repair_record_id"],
                source_rowid=int(evidence["source_rowid"]),
                source_race_id=evidence["race_id"],
                source_date=evidence["date"],
                source_course=evidence["course"],
                source_off=evidence["off"],
                source_horse=evidence["horse"],
                source_field=evidence["missing_source_field"],
                raw_source_value="",
                governed_value=evidence["proposed_repaired_value"],
                verification_status="confirmed",
                evidence_type=evidence["evidence_source_type"],
                evidence_locator=evidence["evidence_locator"],
                evidence_accessed_date=evidence["evidence_accessed_date"],
                confidence=governed_confidence_for_evidence(evidence),
                notes=(
                    f"{evidence['repair_record_id']}; {evidence['reviewer_notes']} "
                    "Supplement only when the exact immutable source field is blank."
                ),
                database_action="source_supplementation",
            )
        )
    return validate_connection_repairs(repairs)


def validate_connection_repairs(
    repairs: Iterable[ConnectionRepair],
) -> tuple[ConnectionRepair, ...]:
    """Validate governed repair structure and no-overwrite constraints."""
    materialised = tuple(repairs)
    if len(materialised) != EXPECTED_VERIFIED_REPAIRS:
        raise ValueError(
            f"expected {EXPECTED_VERIFIED_REPAIRS} connection repairs, found {len(materialised)}"
        )

    verification_ids: set[str] = set()
    repair_ids: set[str] = set()
    keys: set[tuple[int, str]] = set()
    field_counts: dict[str, int] = {}

    for repair in materialised:
        if not VERIFICATION_ID_PATTERN.fullmatch(repair.verification_id):
            raise ValueError(f"invalid verification_id: {repair.verification_id!r}")
        expected_verification_id = verification_id_for_repair(repair.repair_record_id)
        if repair.verification_id != expected_verification_id:
            raise ValueError(
                f"{repair.repair_record_id}: expected verification_id "
                f"{expected_verification_id}, got {repair.verification_id}"
            )
        if repair.verification_id in verification_ids:
            raise ValueError(f"duplicate verification_id: {repair.verification_id}")
        if repair.repair_record_id in repair_ids:
            raise ValueError(f"duplicate repair_record_id: {repair.repair_record_id}")
        verification_ids.add(repair.verification_id)
        repair_ids.add(repair.repair_record_id)

        if repair.source_rowid <= 0:
            raise ValueError(f"{repair.verification_id}: source_rowid must be positive")
        if repair.source_field not in CONNECTION_FIELDS:
            raise ValueError(
                f"{repair.verification_id}: invalid source_field {repair.source_field!r}"
            )
        key = (repair.source_rowid, repair.source_field)
        if key in keys:
            raise ValueError(f"duplicate source-row repair key: {key}")
        keys.add(key)
        if not _is_blank(repair.raw_source_value):
            raise ValueError(f"{repair.verification_id}: repair raw value must be blank")
        if _is_blank(repair.governed_value):
            raise ValueError(f"{repair.verification_id}: governed_value must not be blank")
        if repair.verification_status != "confirmed":
            raise ValueError(f"{repair.verification_id}: repair must be confirmed")
        if repair.database_action != "source_supplementation":
            raise ValueError(
                f"{repair.verification_id}: repair must authorise source_supplementation"
            )
        if repair.confidence not in ALLOWED_CONFIDENCE:
            raise ValueError(f"{repair.verification_id}: invalid confidence")
        if not repair.evidence_type or not repair.evidence_locator or not repair.notes:
            raise ValueError(f"{repair.verification_id}: evidence and notes are required")
        if "http://" not in repair.evidence_locator and "https://" not in repair.evidence_locator:
            raise ValueError(f"{repair.verification_id}: direct evidence URL is required")
        _validate_iso_date(
            repair.evidence_accessed_date,
            f"{repair.verification_id}: evidence_accessed_date",
        )
        _validate_iso_date(repair.source_date, f"{repair.verification_id}: source_date")
        field_counts[repair.source_field] = field_counts.get(repair.source_field, 0) + 1

    if field_counts != EXPECTED_REPAIR_FIELD_COUNTS:
        raise ValueError(f"unexpected repair field counts: {field_counts}")
    return materialised


def load_connection_repairs(path: str | Path) -> tuple[ConnectionRepair, ...]:
    """Load the governed 28-row connection supplementation reference."""
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REPAIR_COLUMNS:
            raise ValueError("connection repair columns do not match the governed schema")
        repairs = tuple(
            ConnectionRepair(
                **{
                    **row,
                    "source_rowid": int(row["source_rowid"]),
                }
            )
            for row in reader
        )
    return validate_connection_repairs(repairs)


def write_connection_repairs(
    path: str | Path, repairs: Iterable[ConnectionRepair]
) -> None:
    """Persist a validated repair reference with stable column ordering."""
    validated = validate_connection_repairs(repairs)
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPAIR_COLUMNS)
        writer.writeheader()
        for repair in validated:
            writer.writerow(asdict(repair))
    temporary.replace(csv_path)


def build_repair_lookup(
    repairs: Iterable[ConnectionRepair],
) -> dict[tuple[int, str], ConnectionRepair]:
    """Return the exact source-row-and-field repair lookup."""
    validated = validate_connection_repairs(repairs)
    return {(repair.source_rowid, repair.source_field): repair for repair in validated}


def resolve_connection_value(
    source_rowid: int,
    source_field: str,
    raw_value: object,
    repair_lookup: Mapping[tuple[int, str], ConnectionRepair],
) -> GovernedConnectionValue:
    """Preserve source-present values and supplement only exact governed blanks."""
    if source_field not in CONNECTION_FIELDS:
        raise ValueError(f"invalid connection field: {source_field!r}")
    repair = repair_lookup.get((source_rowid, source_field))

    if not _is_blank(raw_value):
        if repair is not None:
            raise ValueError(
                f"governed repair {repair.verification_id} would overwrite a populated "
                f"source value at row {source_rowid} field {source_field}"
            )
        raw_text = str(raw_value)
        return GovernedConnectionValue(
            raw_value=raw_text,
            effective_value=raw_text,
            value_status="source_present",
            verification_id=None,
            confidence=None,
        )

    if repair is None:
        return GovernedConnectionValue(
            raw_value=None if raw_value is None else str(raw_value),
            effective_value=None,
            value_status="source_blank_unresolved",
            verification_id=None,
            confidence=None,
        )

    return GovernedConnectionValue(
        raw_value=None if raw_value is None else str(raw_value),
        effective_value=repair.governed_value,
        value_status="externally_supplemented",
        verification_id=repair.verification_id,
        confidence=repair.confidence,
    )
