"""Load governed Notebook 09–20 reference and evidence structures into Database v2.

This module is intentionally limited to committed, durable reference artifacts
and finite in-code reference sets. It does not derive the 1.85 million runner
facts or 189 thousand race facts; those population stages are handled
separately so each stage can be validated at its natural grain.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import re
import sqlite3
from typing import Any, Iterable

import pandas as pd

from inside_rails.connection_identity import CONNECTION_FIELDS
from inside_rails.course_locations import load_course_locations
from inside_rails.field_governance import FIELD_GOVERNANCE, validate_field_governance
from inside_rails.horse_pedigree_identity import load_identity_governance
from inside_rails.jurisdiction_context import CONTEXTS, validate_context_reference
from inside_rails.manual_verifications import (
    ManualVerification,
    load_manual_verifications,
)
from inside_rails.runner_record_supplementations import (
    load_runner_record_supplementations,
)


EXPECTED_COURSE_REFERENCES = 395
EXPECTED_JURISDICTION_CONTEXTS = 16
EXPECTED_FIELD_TREATMENTS = 37
EXPECTED_CONNECTION_DECISIONS = 46
EXPECTED_CONNECTION_SUPPLEMENTATIONS = 28
EXPECTED_CONNECTION_UNRESOLVED = 18
EXPECTED_RUNNER_SUPPLEMENTATIONS = 3
EXPECTED_HORSE_SPECIALIST_DECISIONS = 16

_CONNECTION_VERIFICATION_RE = re.compile(r"^NB20-CONNECTION-(\d{4})$")
_SOURCE_ROWID_RE = re.compile(r"(?:^|[; ])source_rowid=(\d+)(?:[; ]|$)")


class GovernedReferenceLoadError(RuntimeError):
    """Raised when a committed governed artifact cannot be reconciled exactly."""


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    text = str(value)
    return text if text != "" else None


def _optional_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _source_field_ids(connection: sqlite3.Connection) -> dict[str, int]:
    rows = connection.execute(
        """
        SELECT field_name, source_relation_field_id
        FROM source_relation_field
        ORDER BY ordinal_position
        """
    ).fetchall()
    mapping = {str(name): int(field_id) for name, field_id in rows}
    if len(mapping) != 37:
        raise GovernedReferenceLoadError(
            f"Expected 37 Source Version 1 field definitions; observed {len(mapping)}"
        )
    return mapping


def _source_record_id_for_rowid(
    connection: sqlite3.Connection,
    source_rowid: int,
) -> int:
    rows = connection.execute(
        """
        SELECT source_record_id
        FROM source_raceform_v1_record
        WHERE source_rowid = ?
          AND structural_status = 'admitted_runner_record'
        """,
        (source_rowid,),
    ).fetchall()
    if len(rows) != 1:
        raise GovernedReferenceLoadError(
            f"Expected one admitted source record for rowid {source_rowid}; observed {len(rows)}"
        )
    return int(rows[0][0])


def _race_id_for_key(
    connection: sqlite3.Connection,
    source_date: str,
    source_course: str,
    source_off: str,
) -> int:
    rows = connection.execute(
        """
        SELECT source_race_occurrence_id
        FROM core_source_race_occurrence
        WHERE raw_date IS ? AND raw_course IS ? AND raw_off IS ?
        """,
        (source_date, source_course, source_off),
    ).fetchall()
    if len(rows) != 1:
        raise GovernedReferenceLoadError(
            "Expected one Source Version 1 race for "
            f"{(source_date, source_course, source_off)!r}; observed {len(rows)}"
        )
    return int(rows[0][0])


def _runner_source_record_id(
    connection: sqlite3.Connection,
    *,
    source_date: str,
    source_course: str,
    source_off: str,
    source_horse: str,
) -> int:
    rows = connection.execute(
        """
        SELECT source.source_record_id
        FROM core_source_race_occurrence AS race
        JOIN core_runner_participation AS runner
          ON runner.source_race_occurrence_id = race.source_race_occurrence_id
        JOIN source_raceform_v1_record AS source
          ON source.source_record_id = runner.source_record_id
        WHERE race.raw_date IS ?
          AND race.raw_course IS ?
          AND race.raw_off IS ?
          AND source.horse IS ?
        """,
        (source_date, source_course, source_off, source_horse),
    ).fetchall()
    if len(rows) != 1:
        raise GovernedReferenceLoadError(
            "Expected one source-backed runner for manual verification locator "
            f"{(source_date, source_course, source_off, source_horse)!r}; "
            f"observed {len(rows)}"
        )
    return int(rows[0][0])


def _manual_source_rowid(row: ManualVerification) -> int | None:
    match = _SOURCE_ROWID_RE.search(row.raw_source_value)
    return int(match.group(1)) if match else None


def _insert_course_reference(
    connection: sqlite3.Connection,
    path: Path,
    governance_release_id: int,
) -> dict[tuple[str, str], int]:
    frame = load_course_locations(path)
    if len(frame) != EXPECTED_COURSE_REFERENCES:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_COURSE_REFERENCES} governed course identities; found {len(frame)}"
        )

    rows: list[tuple[object, ...]] = []
    lookup: dict[tuple[str, str], int] = {}
    for reference_course_id, row in enumerate(frame.itertuples(index=False), start=1):
        values = row._asdict()
        key = (
            str(values["candidate_course_label"]),
            str(values["candidate_jurisdiction"]),
        )
        lookup[key] = reference_course_id
        rows.append(
            (
                reference_course_id,
                *key,
                _optional_text(values["physical_venue_name"]),
                _optional_text(values["locality"]),
                _optional_text(values["region"]),
                _optional_text(values["country"]),
                _optional_float(values["latitude"]),
                _optional_float(values["longitude"]),
                str(values["iana_timezone"]),
                _optional_text(values["location_evidence"]),
                str(values["location_validation_status"]),
                str(values["raw_course_labels"]),
                governance_release_id,
            )
        )

    connection.executemany(
        """
        INSERT INTO reference_course (
            reference_course_id, candidate_course_label, candidate_jurisdiction,
            physical_venue_name, locality, region, country, latitude, longitude,
            iana_timezone, location_evidence, location_validation_status,
            raw_course_labels, governance_release_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return lookup


def _insert_jurisdiction_contexts(
    connection: sqlite3.Connection,
    governance_release_id: int,
) -> dict[tuple[str, str, str, str | None], int]:
    validate_context_reference(CONTEXTS)
    if len(CONTEXTS) != EXPECTED_JURISDICTION_CONTEXTS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_JURISDICTION_CONTEXTS} jurisdiction contexts; found {len(CONTEXTS)}"
        )

    ordered = sorted(
        CONTEXTS,
        key=lambda row: (
            row.jurisdiction,
            row.source_type,
            row.effective_from.isoformat(),
            row.effective_to.isoformat() if row.effective_to else "9999-12-31",
        ),
    )
    lookup: dict[tuple[str, str, str, str | None], int] = {}
    for context_id, row in enumerate(ordered, start=1):
        effective_from = row.effective_from.isoformat()
        effective_to = row.effective_to.isoformat() if row.effective_to else None
        lookup[(row.jurisdiction, row.source_type, effective_from, effective_to)] = context_id
        connection.execute(
            """
            INSERT INTO reference_jurisdiction_context VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                context_id,
                row.jurisdiction,
                row.source_type,
                effective_from,
                effective_to,
                row.regulatory_authority,
                row.administrative_body,
                row.native_code_status,
                row.wagering_context_status,
                row.evidence_scope,
                governance_release_id,
            ),
        )
    return lookup


def _insert_field_governance(
    connection: sqlite3.Connection,
    governance_release_id: int,
    field_ids: dict[str, int],
) -> None:
    validate_field_governance()
    if len(FIELD_GOVERNANCE) != EXPECTED_FIELD_TREATMENTS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_FIELD_TREATMENTS} field-governance rows; found {len(FIELD_GOVERNANCE)}"
        )
    rows = []
    for treatment_id, item in enumerate(FIELD_GOVERNANCE, start=1):
        rows.append(
            (
                treatment_id,
                field_ids[item.field],
                item.family,
                item.investigation_group,
                item.treatment,
                item.governing_notebook,
                item.status,
                governance_release_id,
            )
        )
    connection.executemany(
        "INSERT INTO governance_source_field_treatment VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_manual_verifications(
    connection: sqlite3.Connection,
    path: Path,
    governance_release_id: int,
    field_ids: dict[str, int],
) -> tuple[dict[str, int], dict[str, ManualVerification]]:
    loaded = load_manual_verifications(path)
    ordered = sorted(loaded, key=lambda row: row.verification_id)
    code_to_id: dict[str, int] = {}
    code_to_row: dict[str, ManualVerification] = {}

    for manual_id, row in enumerate(ordered, start=1):
        source_record_id: int | None = None
        source_race_occurrence_id: int | None = None

        embedded_rowid = _manual_source_rowid(row)
        if embedded_rowid is not None:
            source_record_id = _source_record_id_for_rowid(connection, embedded_rowid)

        has_complete_race_key = bool(row.source_date and row.source_course and row.source_off)
        if has_complete_race_key:
            source_race_occurrence_id = _race_id_for_key(
                connection,
                row.source_date,
                row.source_course,
                row.source_off,
            )

        # Runner verifications with a complete locator should resolve to one
        # source record even when the historical register predates explicit rowid
        # storage. This is critical for exact-lineage corrections such as NB17.
        if (
            source_record_id is None
            and row.subject_type == "runner"
            and has_complete_race_key
            and row.source_horse
        ):
            source_record_id = _runner_source_record_id(
                connection,
                source_date=row.source_date,
                source_course=row.source_course,
                source_off=row.source_off,
                source_horse=row.source_horse,
            )

        source_relation_field_id = field_ids.get(row.source_field)
        verified_value = row.verified_value or None
        evidence_accessed_date = row.evidence_accessed_date or None

        connection.execute(
            """
            INSERT INTO governance_manual_verification (
                manual_verification_id, verification_code, subject_type,
                source_record_id, source_race_occurrence_id, reference_course_id,
                source_relation_field_id, source_date, source_course, source_off,
                source_horse, source_field, raw_source_value,
                verification_question, verified_value, verification_status,
                evidence_type, evidence_locator, evidence_accessed_date,
                governing_notebook, confidence, notes, database_action,
                governance_release_id
            ) VALUES (
                ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                manual_id,
                row.verification_id,
                row.subject_type,
                source_record_id,
                source_race_occurrence_id,
                source_relation_field_id,
                row.source_date or None,
                row.source_course or None,
                row.source_off or None,
                row.source_horse or None,
                row.source_field or None,
                row.raw_source_value or None,
                row.verification_question,
                verified_value,
                row.verification_status,
                row.evidence_type,
                row.evidence_locator,
                evidence_accessed_date,
                row.governing_notebook,
                row.confidence,
                row.notes,
                row.database_action,
                governance_release_id,
            ),
        )
        code_to_id[row.verification_id] = manual_id
        code_to_row[row.verification_id] = row

    return code_to_id, code_to_row


def _insert_connection_decisions(
    connection: sqlite3.Connection,
    governance_release_id: int,
    field_ids: dict[str, int],
    manual_ids: dict[str, int],
    manual_rows: dict[str, ManualVerification],
) -> dict[tuple[int, str], int]:
    nb20 = [
        row
        for code, row in manual_rows.items()
        if _CONNECTION_VERIFICATION_RE.fullmatch(code)
    ]
    if len(nb20) != EXPECTED_CONNECTION_DECISIONS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_CONNECTION_DECISIONS} Notebook 20 decisions; found {len(nb20)}"
        )

    supplemented = 0
    unresolved = 0
    lookup: dict[tuple[int, str], int] = {}
    for decision_id, row in enumerate(
        sorted(nb20, key=lambda item: item.verification_id),
        start=1,
    ):
        match = _CONNECTION_VERIFICATION_RE.fullmatch(row.verification_id)
        assert match is not None
        decision_code = f"connection_blank_{int(match.group(1)):03d}"
        if row.source_field not in CONNECTION_FIELDS:
            raise GovernedReferenceLoadError(
                f"{row.verification_id}: expected jockey/trainer/owner source field"
            )
        source_rowid = _manual_source_rowid(row)
        if source_rowid is None:
            raise GovernedReferenceLoadError(
                f"{row.verification_id}: permanent register lost source_rowid lineage"
            )
        source_record_id = _source_record_id_for_rowid(connection, source_rowid)
        raw_value = connection.execute(
            f'SELECT "{row.source_field}" FROM source_raceform_v1_record WHERE source_record_id = ?',
            (source_record_id,),
        ).fetchone()[0]
        if raw_value is not None and str(raw_value).strip() != "":
            raise GovernedReferenceLoadError(
                f"{row.verification_id}: governed blank decision would overwrite populated source"
            )

        if row.database_action == "source_supplementation":
            if row.verification_status != "confirmed" or not row.verified_value:
                raise GovernedReferenceLoadError(
                    f"{row.verification_id}: supplementation lacks confirmed value"
                )
            governed_value = row.verified_value
            value_status = "externally_supplemented"
            supplemented += 1
        elif row.database_action == "preserve_raw_unresolved":
            governed_value = None
            value_status = "source_blank_unresolved"
            unresolved += 1
        else:
            raise GovernedReferenceLoadError(
                f"{row.verification_id}: unsupported Notebook 20 action {row.database_action!r}"
            )

        connection.execute(
            """
            INSERT INTO governance_connection_value_decision VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                decision_id,
                decision_code,
                source_record_id,
                field_ids[row.source_field],
                manual_ids[row.verification_id],
                governed_value,
                value_status,
                row.confidence,
                governance_release_id,
            ),
        )
        lookup[(source_record_id, row.source_field)] = decision_id

    if supplemented != EXPECTED_CONNECTION_SUPPLEMENTATIONS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_CONNECTION_SUPPLEMENTATIONS} connection supplementations; found {supplemented}"
        )
    if unresolved != EXPECTED_CONNECTION_UNRESOLVED:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_CONNECTION_UNRESOLVED} unresolved connection decisions; found {unresolved}"
        )
    return lookup


def _insert_runner_supplementations(
    connection: sqlite3.Connection,
    path: Path,
    governance_release_id: int,
    manual_ids: dict[str, int],
) -> None:
    rows = load_runner_record_supplementations(path)
    if len(rows) != EXPECTED_RUNNER_SUPPLEMENTATIONS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_RUNNER_SUPPLEMENTATIONS} runner supplementations; found {len(rows)}"
        )
    for row_id, row in enumerate(rows, start=1):
        race_id = _race_id_for_key(connection, *row.race_key)
        existing_horse = connection.execute(
            """
            SELECT COUNT(*)
            FROM core_runner_participation AS runner
            JOIN source_raceform_v1_record AS source
              ON source.source_record_id = runner.source_record_id
            WHERE runner.source_race_occurrence_id = ?
              AND source.horse IS ?
            """,
            (race_id, row.source_horse),
        ).fetchone()[0]
        if existing_horse:
            raise GovernedReferenceLoadError(
                f"{row.supplementation_id}: supposedly missing horse is present in source"
            )
        source_count = int(
            connection.execute(
                "SELECT admitted_runner_count FROM core_source_race_occurrence WHERE source_race_occurrence_id = ?",
                (race_id,),
            ).fetchone()[0]
        )
        if source_count != row.source_runner_rows:
            raise GovernedReferenceLoadError(
                f"{row.supplementation_id}: source runner count changed: {source_count}"
            )
        if row.verification_id not in manual_ids:
            raise GovernedReferenceLoadError(
                f"{row.supplementation_id}: missing permanent verification {row.verification_id}"
            )

        connection.execute(
            """
            INSERT INTO governance_runner_record_supplementation VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'externally_supplemented', ?
            )
            """,
            (
                row_id,
                row.supplementation_id,
                manual_ids[row.verification_id],
                race_id,
                row.source_horse,
                row.source_runner_rows,
                row.source_ran,
                row.published_runners,
                row.verified_pos,
                row.verified_outcome,
                governance_release_id,
            ),
        )


def _insert_horse_specialist_decisions(
    connection: sqlite3.Connection,
    path: Path,
    governance_release_id: int,
    manual_ids: dict[str, int],
) -> dict[str, int]:
    governance = load_identity_governance(path)
    frame = governance.rows
    if len(frame) != EXPECTED_HORSE_SPECIALIST_DECISIONS:
        raise GovernedReferenceLoadError(
            f"Expected {EXPECTED_HORSE_SPECIALIST_DECISIONS} Notebook 19 specialist decisions; found {len(frame)}"
        )

    lookup: dict[str, int] = {}
    ordered = frame.sort_values("decision_id", kind="stable")
    for row_id, row in enumerate(ordered.itertuples(index=False), start=1):
        values = row._asdict()
        specialist_code = str(values["decision_id"])
        verification_code = str(values["verification_id"])
        connection.execute(
            """
            INSERT INTO governance_horse_pedigree_specialist_decision (
                horse_pedigree_specialist_decision_id, specialist_decision_code,
                source_horse_label, decision_scope, analytical_outcome,
                raw_sire, raw_dam, raw_damsire,
                governed_sire, governed_dam, governed_damsire,
                verification_status, verification_code, evidence_locator,
                confidence, notes, manual_verification_id, governance_release_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row_id,
                specialist_code,
                str(values["horse"]),
                str(values["decision_scope"]),
                str(values["analytical_outcome"]),
                _optional_text(values["raw_sire"]),
                _optional_text(values["raw_dam"]),
                _optional_text(values["raw_damsire"]),
                _optional_text(values["governed_sire"]),
                _optional_text(values["governed_dam"]),
                _optional_text(values["governed_damsire"]),
                str(values["verification_status"]),
                verification_code,
                str(values["evidence_locator"]),
                str(values["confidence"]),
                str(values["notes"]),
                manual_ids.get(verification_code),
                governance_release_id,
            ),
        )
        lookup[specialist_code] = row_id
    return lookup


def load_governed_reference_structures(
    connection: sqlite3.Connection,
    project_root: str | Path,
    *,
    governance_release_id: int,
) -> dict[str, Any]:
    """Populate the finite governed reference/evidence tables transactionally.

    The caller must supply a Database v2 candidate in ``building`` state. No
    stage here modifies immutable source/core rows. Existing target-table rows
    are treated as an error because reference loading is deterministic and must
    not be replayed on top of a partial population.
    """

    root = Path(project_root)
    target_tables = (
        "reference_course",
        "reference_jurisdiction_context",
        "governance_source_field_treatment",
        "governance_manual_verification",
        "governance_connection_value_decision",
        "governance_runner_record_supplementation",
        "governance_horse_pedigree_specialist_decision",
    )
    for table in target_tables:
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count:
            raise GovernedReferenceLoadError(
                f"Reference loading requires empty {table}; found {count} rows"
            )

    manifest = connection.execute(
        "SELECT governance_release_id, build_status FROM import_manifest WHERE import_manifest_id = 1"
    ).fetchone()
    if manifest != (governance_release_id, "building"):
        raise GovernedReferenceLoadError(
            f"Reference loading requires the active building manifest; observed {manifest!r}"
        )

    field_ids = _source_field_ids(connection)
    course_lookup = _insert_course_reference(
        connection,
        root / "data/reference/course_locations.csv",
        governance_release_id,
    )
    jurisdiction_lookup = _insert_jurisdiction_contexts(
        connection,
        governance_release_id,
    )
    _insert_field_governance(connection, governance_release_id, field_ids)
    manual_ids, manual_rows = _insert_manual_verifications(
        connection,
        root / "data/reference/manual_verifications.csv",
        governance_release_id,
        field_ids,
    )
    connection_lookup = _insert_connection_decisions(
        connection,
        governance_release_id,
        field_ids,
        manual_ids,
        manual_rows,
    )
    _insert_runner_supplementations(
        connection,
        root / "data/reference/runner_record_supplementations.csv",
        governance_release_id,
        manual_ids,
    )
    specialist_lookup = _insert_horse_specialist_decisions(
        connection,
        root / "data/reference/horse_pedigree_identity_governance.csv",
        governance_release_id,
        manual_ids,
    )

    return {
        "course_ids": course_lookup,
        "jurisdiction_context_ids": jurisdiction_lookup,
        "source_field_ids": field_ids,
        "manual_verification_ids": manual_ids,
        "manual_verifications": manual_rows,
        "connection_decision_ids": connection_lookup,
        "horse_specialist_decision_ids": specialist_lookup,
    }


__all__ = [
    "GovernedReferenceLoadError",
    "load_governed_reference_structures",
]
