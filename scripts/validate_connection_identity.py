#!/usr/bin/env python3
"""Validate Notebook 20 connection semantics and governed repairs source-wide."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inside_rails.connection_identity import (
    EXPECTED_EVIDENCE_RECORDS,
    EXPECTED_REPAIR_FIELD_COUNTS,
    EXPECTED_UNRESOLVED_RECORDS,
    build_repair_lookup,
    load_connection_repairs,
    resolve_connection_value,
)
from inside_rails.manual_verifications import load_manual_verifications

SOURCE_DB = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
REPAIR_REFERENCE = (
    PROJECT_ROOT / "data" / "reference" / "connection_identity_repairs.csv"
)
MANUAL_VERIFICATION_REGISTER = (
    PROJECT_ROOT / "data" / "reference" / "manual_verifications.csv"
)

EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_RAW_BLANK_COUNTS = {"jockey": 2, "trainer": 9, "owner": 35}
EXPECTED_RAW_BLANK_OCCURRENCES = 46
EXPECTED_RAW_AFFECTED_ROWS = 43
NOTEBOOK_20_PREFIX = "NB20-CONNECTION-"


def _is_blank(value: object) -> bool:
    return value is None or str(value).strip() == ""


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(SOURCE_DB)

    repairs = load_connection_repairs(REPAIR_REFERENCE)
    repair_lookup = build_repair_lookup(repairs)
    manual_rows = load_manual_verifications(MANUAL_VERIFICATION_REGISTER)
    notebook_rows = tuple(
        row for row in manual_rows if row.verification_id.startswith(NOTEBOOK_20_PREFIX)
    )

    if len(notebook_rows) != EXPECTED_EVIDENCE_RECORDS:
        raise AssertionError(
            f"expected {EXPECTED_EVIDENCE_RECORDS} Notebook 20 verifications, "
            f"found {len(notebook_rows)}"
        )
    confirmed_ids = {
        row.verification_id
        for row in notebook_rows
        if row.verification_status == "confirmed"
    }
    unresolved_rows = tuple(
        row for row in notebook_rows if row.verification_status == "unresolved"
    )
    repair_ids = {repair.verification_id for repair in repairs}
    if confirmed_ids != repair_ids:
        raise AssertionError("confirmed manual verifications do not match repair reference")
    if len(unresolved_rows) != EXPECTED_UNRESOLVED_RECORDS:
        raise AssertionError(
            f"expected {EXPECTED_UNRESOLVED_RECORDS} unresolved records, "
            f"found {len(unresolved_rows)}"
        )
    if any(row.database_action != "preserve_raw_unresolved" for row in unresolved_rows):
        raise AssertionError("unresolved Notebook 20 records must preserve raw unresolved")

    connection = sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        population = connection.execute(
            """
            SELECT
                COUNT(*) AS runner_rows,
                SUM(CASE WHEN jockey IS NULL OR TRIM(jockey) = '' THEN 1 ELSE 0 END)
                    AS blank_jockey,
                SUM(CASE WHEN trainer IS NULL OR TRIM(trainer) = '' THEN 1 ELSE 0 END)
                    AS blank_trainer,
                SUM(CASE WHEN owner IS NULL OR TRIM(owner) = '' THEN 1 ELSE 0 END)
                    AS blank_owner,
                COUNT(DISTINCT CASE
                    WHEN jockey IS NULL OR TRIM(jockey) = ''
                      OR trainer IS NULL OR TRIM(trainer) = ''
                      OR owner IS NULL OR TRIM(owner) = ''
                    THEN rowid
                END) AS affected_rows
            FROM data
            WHERE rowid <> 1
            """
        ).fetchone()

        observed_blank_counts = {
            "jockey": int(population["blank_jockey"]),
            "trainer": int(population["blank_trainer"]),
            "owner": int(population["blank_owner"]),
        }
        if int(population["runner_rows"]) != EXPECTED_RUNNER_ROWS:
            raise AssertionError(
                f"expected {EXPECTED_RUNNER_ROWS} runner rows, "
                f"found {population['runner_rows']}"
            )
        if observed_blank_counts != EXPECTED_RAW_BLANK_COUNTS:
            raise AssertionError(f"unexpected raw blank counts: {observed_blank_counts}")
        if sum(observed_blank_counts.values()) != EXPECTED_RAW_BLANK_OCCURRENCES:
            raise AssertionError("unexpected raw connection blank occurrence count")
        if int(population["affected_rows"]) != EXPECTED_RAW_AFFECTED_ROWS:
            raise AssertionError(
                f"expected {EXPECTED_RAW_AFFECTED_ROWS} affected rows, "
                f"found {population['affected_rows']}"
            )

        placeholders = ",".join("?" for _ in repairs)
        source_rows = connection.execute(
            f"""
            SELECT rowid AS source_rowid, race_id, date, course, off, horse,
                   jockey, trainer, owner
            FROM data
            WHERE rowid <> 1
              AND rowid IN ({placeholders})
            """,
            tuple(repair.source_rowid for repair in repairs),
        ).fetchall()
    finally:
        connection.close()

    by_rowid = {int(row["source_rowid"]): row for row in source_rows}
    if len(by_rowid) != len(repairs):
        raise AssertionError(
            f"expected {len(repairs)} distinct repair source rows, found {len(by_rowid)}"
        )

    applied_counts = {field: 0 for field in EXPECTED_REPAIR_FIELD_COUNTS}
    for repair in repairs:
        row = by_rowid.get(repair.source_rowid)
        if row is None:
            raise AssertionError(f"missing source row {repair.source_rowid}")
        if str(row["race_id"]) != repair.source_race_id:
            raise AssertionError(f"{repair.verification_id}: race_id mismatch")
        for column, expected in (
            ("date", repair.source_date),
            ("course", repair.source_course),
            ("off", repair.source_off),
            ("horse", repair.source_horse),
        ):
            if str(row[column]) != expected:
                raise AssertionError(
                    f"{repair.verification_id}: source {column} mismatch; "
                    f"expected {expected!r}, found {row[column]!r}"
                )
        raw_value = row[repair.source_field]
        if not _is_blank(raw_value):
            raise AssertionError(
                f"{repair.verification_id}: target source value is no longer blank"
            )
        governed = resolve_connection_value(
            repair.source_rowid,
            repair.source_field,
            raw_value,
            repair_lookup,
        )
        if governed.effective_value != repair.governed_value:
            raise AssertionError(f"{repair.verification_id}: repair application failed")
        applied_counts[repair.source_field] += 1

    if applied_counts != EXPECTED_REPAIR_FIELD_COUNTS:
        raise AssertionError(f"unexpected applied repair counts: {applied_counts}")

    remaining_blanks = {
        field: EXPECTED_RAW_BLANK_COUNTS[field] - applied_counts[field]
        for field in EXPECTED_RAW_BLANK_COUNTS
    }
    if remaining_blanks != {"jockey": 0, "trainer": 5, "owner": 13}:
        raise AssertionError(f"unexpected governed unresolved counts: {remaining_blanks}")

    print("Connection identity validation passed.")
    print(f"  governed runner rows: {EXPECTED_RUNNER_ROWS}")
    print(f"  raw blank occurrences: {EXPECTED_RAW_BLANK_OCCURRENCES}")
    print(f"  affected source rows: {EXPECTED_RAW_AFFECTED_ROWS}")
    print(f"  permanent verification records: {len(notebook_rows)}")
    print(f"  governed source supplementations: {len(repairs)}")
    print(f"  unresolved preserved blanks: {len(unresolved_rows)}")
    for field in ("jockey", "trainer", "owner"):
        print(
            f"  {field}: raw blanks={EXPECTED_RAW_BLANK_COUNTS[field]}, "
            f"supplemented={applied_counts[field]}, "
            f"unresolved={remaining_blanks[field]}"
        )


if __name__ == "__main__":
    main()
