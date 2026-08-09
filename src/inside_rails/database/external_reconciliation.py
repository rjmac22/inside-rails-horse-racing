"""Load Database v3 external verification evidence and typed resolutions."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import sqlite3

EXPECTED_EXISTING_MANUAL_VERIFICATIONS = 85
EXPECTED_NEW_MANUAL_VERIFICATIONS = 19
EXPECTED_TOTAL_MANUAL_VERIFICATIONS = 104
EXPECTED_RESOLUTIONS = 37

EVIDENCE_PATH = Path("data/reference/external_verification_reconciliation.csv")
RESOLUTION_PATH = Path("data/reference/external_value_resolutions.csv")


class ExternalReconciliationError(RuntimeError):
    """Raised when the v3 reconciliation inputs cannot be resolved exactly."""


@dataclass(frozen=True)
class ExternalReconciliationSummary:
    existing_manual_verifications: int
    new_manual_verifications: int
    total_manual_verifications: int
    external_value_resolutions: int


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ExternalReconciliationError(f"Governed reconciliation input is empty: {path}")
    return rows


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _integer(value: str | None) -> int | None:
    text = _blank_to_none(value)
    return None if text is None else int(text)


def _real(value: str | None) -> float | None:
    text = _blank_to_none(value)
    return None if text is None else float(text)


def _resolve_race(
    connection: sqlite3.Connection,
    *,
    source_date: str,
    source_course: str,
    source_off: str,
) -> int:
    rows = connection.execute(
        """
        SELECT source_race_occurrence_id
        FROM core_source_race_occurrence
        WHERE CAST(raw_date AS TEXT) = ?
          AND CAST(raw_course AS TEXT) = ?
          AND CAST(raw_off AS TEXT) = ?
        """,
        (source_date, source_course, source_off),
    ).fetchall()
    if len(rows) != 1:
        raise ExternalReconciliationError(
            "Expected one race for external resolution "
            f"{source_date}/{source_course}/{source_off}; observed {len(rows)}"
        )
    return int(rows[0][0])


def _resolve_source_record(
    connection: sqlite3.Connection,
    *,
    race_id: int,
    source_rowid: int | None,
    source_horse: str | None,
    source_position: int | None,
) -> int | None:
    if source_rowid is not None:
        row = connection.execute(
            "SELECT source_record_id FROM source_raceform_v1_record WHERE source_rowid = ?",
            (source_rowid,),
        ).fetchone()
        if row is None:
            raise ExternalReconciliationError(f"Source rowid {source_rowid} was not found")
        source_record_id = int(row[0])
        linked = connection.execute(
            """
            SELECT COUNT(*)
            FROM core_runner_participation
            WHERE source_record_id = ? AND source_race_occurrence_id = ?
            """,
            (source_record_id, race_id),
        ).fetchone()[0]
        if int(linked) != 1:
            raise ExternalReconciliationError(
                f"Source rowid {source_rowid} is not linked to the declared race"
            )
        return source_record_id

    clauses = ["runner.source_race_occurrence_id = ?"]
    parameters: list[object] = [race_id]
    if source_horse is not None:
        clauses.append("CAST(source.horse AS TEXT) = ?")
        parameters.append(source_horse)
    if source_position is not None:
        clauses.append("CAST(source.pos AS INTEGER) = ?")
        parameters.append(source_position)
    if len(clauses) == 1:
        return None

    rows = connection.execute(
        f"""
        SELECT source.source_record_id
        FROM core_runner_participation AS runner
        JOIN source_raceform_v1_record AS source
          ON source.source_record_id = runner.source_record_id
        WHERE {' AND '.join(clauses)}
        """,
        parameters,
    ).fetchall()
    if len(rows) != 1:
        raise ExternalReconciliationError(
            "Expected one source record for external resolution; "
            f"race_id={race_id}, horse={source_horse!r}, position={source_position!r}, "
            f"observed={len(rows)}"
        )
    return int(rows[0][0])


def _source_field_id(connection: sqlite3.Connection, field_name: str | None) -> int | None:
    if field_name is None:
        return None
    row = connection.execute(
        "SELECT source_relation_field_id FROM source_relation_field WHERE field_name = ?",
        (field_name,),
    ).fetchone()
    return None if row is None else int(row[0])


def load_external_reconciliation(
    connection: sqlite3.Connection,
    project_root: str | Path,
    *,
    governance_release_id: int,
) -> ExternalReconciliationSummary:
    """Insert the 19 missed evidence rows and 37 typed v3 resolutions."""

    root = Path(project_root).expanduser().resolve()
    evidence_rows = _read_csv(root / EVIDENCE_PATH)
    resolution_rows = _read_csv(root / RESOLUTION_PATH)
    if len(evidence_rows) != EXPECTED_NEW_MANUAL_VERIFICATIONS:
        raise ExternalReconciliationError(
            f"Expected {EXPECTED_NEW_MANUAL_VERIFICATIONS} reconciliation evidence rows; "
            f"observed {len(evidence_rows)}"
        )
    if len(resolution_rows) != EXPECTED_RESOLUTIONS:
        raise ExternalReconciliationError(
            f"Expected {EXPECTED_RESOLUTIONS} typed resolutions; observed {len(resolution_rows)}"
        )

    existing = int(
        connection.execute("SELECT COUNT(*) FROM governance_manual_verification").fetchone()[0]
    )
    if existing != EXPECTED_EXISTING_MANUAL_VERIFICATIONS:
        raise ExternalReconciliationError(
            f"Database v3 base must contain {EXPECTED_EXISTING_MANUAL_VERIFICATIONS} manual verifications; "
            f"observed {existing}"
        )

    next_manual_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(manual_verification_id), 0) + 1 FROM governance_manual_verification"
        ).fetchone()[0]
    )
    for offset, row in enumerate(evidence_rows):
        source_date = _blank_to_none(row["source_date"])
        source_course = _blank_to_none(row["source_course"])
        source_off = _blank_to_none(row["source_off"])
        source_horse = _blank_to_none(row["source_horse"])
        source_field = _blank_to_none(row["source_field"])
        race_id = None
        if source_date and source_course and source_off:
            race_id = _resolve_race(
                connection,
                source_date=source_date,
                source_course=source_course,
                source_off=source_off,
            )

        source_record_id = None
        if race_id is not None and row["verification_id"] == "NB05-POS-0001":
            source_record_id = _resolve_source_record(
                connection,
                race_id=race_id,
                source_rowid=55_516,
                source_horse=source_horse,
                source_position=None,
            )
        elif race_id is not None and row["verification_id"] == "NB08-SP-0004":
            source_record_id = _resolve_source_record(
                connection,
                race_id=race_id,
                source_rowid=1_708_860,
                source_horse=source_horse,
                source_position=None,
            )

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
            ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                next_manual_id + offset,
                row["verification_id"],
                row["subject_type"],
                source_record_id,
                race_id,
                _source_field_id(connection, source_field),
                source_date,
                source_course,
                source_off,
                source_horse,
                source_field,
                _blank_to_none(row["raw_source_value"]),
                row["verification_question"],
                _blank_to_none(row["verified_value"]),
                row["verification_status"],
                row["evidence_type"],
                row["evidence_locator"],
                _blank_to_none(row["evidence_accessed_date"]),
                row["governing_notebook"],
                row["confidence"],
                row["notes"],
                row["database_action"],
                governance_release_id,
            ),
        )

    total_manual = int(
        connection.execute("SELECT COUNT(*) FROM governance_manual_verification").fetchone()[0]
    )
    if total_manual != EXPECTED_TOTAL_MANUAL_VERIFICATIONS:
        raise ExternalReconciliationError(
            f"Expected {EXPECTED_TOTAL_MANUAL_VERIFICATIONS} total manual verifications; observed {total_manual}"
        )

    verification_ids = {
        str(code): int(identifier)
        for identifier, code in connection.execute(
            "SELECT manual_verification_id, verification_code FROM governance_manual_verification"
        )
    }
    next_resolution_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(external_value_resolution_id), 0) + 1 FROM governance_external_value_resolution"
        ).fetchone()[0]
    )
    for offset, row in enumerate(resolution_rows):
        verification_id = row["verification_id"]
        manual_id = verification_ids.get(verification_id)
        if manual_id is None:
            raise ExternalReconciliationError(
                f"Typed resolution references unknown verification {verification_id!r}"
            )
        race_id = _resolve_race(
            connection,
            source_date=row["source_date"],
            source_course=row["source_course"],
            source_off=row["source_off"],
        )
        source_record_id = None
        if row["scope"] == "runner":
            source_record_id = _resolve_source_record(
                connection,
                race_id=race_id,
                source_rowid=_integer(row["source_rowid"]),
                source_horse=_blank_to_none(row["source_horse"]),
                source_position=_integer(row["source_position"]),
            )
            if source_record_id is None:
                raise ExternalReconciliationError(
                    f"Runner resolution {row['resolution_id']} did not resolve a source record"
                )
        elif row["scope"] != "race":
            raise ExternalReconciliationError(
                f"Unsupported resolution scope {row['scope']!r}"
            )

        connection.execute(
            """
            INSERT INTO governance_external_value_resolution (
                external_value_resolution_id, resolution_code,
                manual_verification_id, source_record_id,
                source_race_occurrence_id, source_field, resolution_kind,
                governed_text_value, governed_integer_value, governed_real_value,
                governed_numerator, governed_denominator, governed_marker,
                governed_currency, governed_unit, analytical_action, notes,
                governance_release_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                next_resolution_id + offset,
                row["resolution_id"],
                manual_id,
                source_record_id,
                race_id,
                row["source_field"],
                row["resolution_kind"],
                _blank_to_none(row["governed_text_value"]),
                _integer(row["governed_integer_value"]),
                _real(row["governed_real_value"]),
                _integer(row["governed_numerator"]),
                _integer(row["governed_denominator"]),
                _blank_to_none(row["governed_marker"]),
                _blank_to_none(row["governed_currency"]),
                _blank_to_none(row["governed_unit"]),
                row["analytical_action"],
                row["notes"],
                governance_release_id,
            ),
        )

    observed_resolutions = int(
        connection.execute("SELECT COUNT(*) FROM governance_external_value_resolution").fetchone()[0]
    )
    if observed_resolutions != EXPECTED_RESOLUTIONS:
        raise ExternalReconciliationError(
            f"Expected {EXPECTED_RESOLUTIONS} external resolutions; observed {observed_resolutions}"
        )

    return ExternalReconciliationSummary(
        existing_manual_verifications=existing,
        new_manual_verifications=EXPECTED_NEW_MANUAL_VERIFICATIONS,
        total_manual_verifications=total_manual,
        external_value_resolutions=observed_resolutions,
    )


__all__ = [
    "ExternalReconciliationError",
    "ExternalReconciliationSummary",
    "load_external_reconciliation",
]
