#!/usr/bin/env python3
"""Validate Notebook 20 connection semantics and governed repairs source-wide."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inside_rails.connection_identity import (
    EXPECTED_DECISION_COUNTS,
    EXPECTED_EVIDENCE_RECORDS,
    EXPECTED_FIELD_COUNTS,
    EXPECTED_REPAIR_FIELD_COUNTS,
    EXPECTED_UNRESOLVED_RECORDS,
    build_repair_lookup,
    load_connection_repairs,
    resolve_connection_value,
    verification_id_for_repair,
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
EXPECTED_RAW_AFFECTED_ROWS = 44
NOTEBOOK_20_PREFIX = "NB20-CONNECTION-"
EXPECTED_VERIFICATION_IDS = {
    f"{NOTEBOOK_20_PREFIX}{number:04d}" for number in range(1, 47)
}
RAW_LOCATOR_PATTERN = re.compile(
    r"^blank; source_rowid=(?P<source_rowid>[1-9]\d*); "
    r"race_id=(?P<race_id>[^;]+); "
    r"repair_record_id=(?P<repair_record_id>connection_blank_\d{3})$"
)
DECISION_MARKER_PATTERN = re.compile(
    r"(?:^|; )evidence decision="
    r"(?P<decision>verified_repair|conflicting_evidence|insufficient_evidence);"
)


def _is_blank(value: object) -> bool:
    return value is None or str(value).strip() == ""


def _manual_decision_record(row: object) -> dict[str, object]:
    """Parse and validate one permanent Notebook 20 verification row."""
    verification_id = str(row.verification_id)
    if row.governing_notebook != "20":
        raise AssertionError(f"{verification_id}: governing_notebook must be 20")
    if row.subject_type != "runner":
        raise AssertionError(f"{verification_id}: subject_type must be runner")
    if row.source_field not in EXPECTED_FIELD_COUNTS:
        raise AssertionError(
            f"{verification_id}: unexpected source field {row.source_field!r}"
        )

    locator_match = RAW_LOCATOR_PATTERN.fullmatch(row.raw_source_value)
    if locator_match is None:
        raise AssertionError(
            f"{verification_id}: raw_source_value does not preserve the exact "
            "source_rowid, race_id and repair_record_id locator"
        )
    source_rowid = int(locator_match.group("source_rowid"))
    source_race_id = locator_match.group("race_id")
    repair_record_id = locator_match.group("repair_record_id")
    expected_verification_id = verification_id_for_repair(repair_record_id)
    if verification_id != expected_verification_id:
        raise AssertionError(
            f"{verification_id}: repair_record_id implies {expected_verification_id}"
        )

    decision_matches = list(DECISION_MARKER_PATTERN.finditer(row.notes))
    if len(decision_matches) != 1:
        raise AssertionError(
            f"{verification_id}: notes must contain exactly one governed decision marker"
        )
    decision = decision_matches[0].group("decision")

    if decision == "verified_repair":
        if row.verification_status != "confirmed":
            raise AssertionError(f"{verification_id}: verified repair must be confirmed")
        if row.database_action != "source_supplementation":
            raise AssertionError(
                f"{verification_id}: verified repair must authorise source supplementation"
            )
        if _is_blank(row.verified_value):
            raise AssertionError(
                f"{verification_id}: verified repair must assign a governed value"
            )
    else:
        if row.verification_status != "unresolved":
            raise AssertionError(
                f"{verification_id}: unresolved decision must have unresolved status"
            )
        if row.database_action != "preserve_raw_unresolved":
            raise AssertionError(
                f"{verification_id}: unresolved decision must preserve the raw blank"
            )
        if not _is_blank(row.verified_value):
            raise AssertionError(
                f"{verification_id}: unresolved decision must not assign a value"
            )

    return {
        "row": row,
        "key": (source_rowid, row.source_field),
        "source_rowid": source_rowid,
        "source_race_id": source_race_id,
        "repair_record_id": repair_record_id,
        "decision": decision,
    }


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
    observed_verification_ids = {row.verification_id for row in notebook_rows}
    if observed_verification_ids != EXPECTED_VERIFICATION_IDS:
        missing = sorted(EXPECTED_VERIFICATION_IDS - observed_verification_ids)
        extra = sorted(observed_verification_ids - EXPECTED_VERIFICATION_IDS)
        raise AssertionError(
            f"unexpected Notebook 20 verification IDs; missing={missing}, extra={extra}"
        )

    decision_records_by_key: dict[tuple[int, str], dict[str, object]] = {}
    decision_records_by_id: dict[str, dict[str, object]] = {}
    decision_counts: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    for row in notebook_rows:
        record = _manual_decision_record(row)
        key = record["key"]
        if key in decision_records_by_key:
            raise AssertionError(f"duplicate Notebook 20 source-row decision key: {key}")
        decision_records_by_key[key] = record
        decision_records_by_id[row.verification_id] = record
        decision_counts[str(record["decision"])] += 1
        field_counts[row.source_field] += 1

    if dict(decision_counts) != EXPECTED_DECISION_COUNTS:
        raise AssertionError(f"unexpected Notebook 20 decision counts: {dict(decision_counts)}")
    if dict(field_counts) != EXPECTED_FIELD_COUNTS:
        raise AssertionError(f"unexpected Notebook 20 field counts: {dict(field_counts)}")

    confirmed_ids = {
        verification_id
        for verification_id, record in decision_records_by_id.items()
        if record["decision"] == "verified_repair"
    }
    unresolved_ids = observed_verification_ids - confirmed_ids
    if len(unresolved_ids) != EXPECTED_UNRESOLVED_RECORDS:
        raise AssertionError(
            f"expected {EXPECTED_UNRESOLVED_RECORDS} unresolved records, "
            f"found {len(unresolved_ids)}"
        )
    repair_ids = {repair.verification_id for repair in repairs}
    if confirmed_ids != repair_ids:
        missing_repairs = sorted(confirmed_ids - repair_ids)
        unexpected_repairs = sorted(repair_ids - confirmed_ids)
        raise AssertionError(
            "confirmed manual verifications do not match repair reference; "
            f"missing repairs={missing_repairs}, unexpected repairs={unexpected_repairs}"
        )

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

        source_blank_rows = connection.execute(
            """
            SELECT rowid AS source_rowid, race_id, date, course, off, horse,
                   'jockey' AS source_field, jockey AS raw_value
            FROM data
            WHERE rowid <> 1 AND (jockey IS NULL OR TRIM(jockey) = '')
            UNION ALL
            SELECT rowid AS source_rowid, race_id, date, course, off, horse,
                   'trainer' AS source_field, trainer AS raw_value
            FROM data
            WHERE rowid <> 1 AND (trainer IS NULL OR TRIM(trainer) = '')
            UNION ALL
            SELECT rowid AS source_rowid, race_id, date, course, off, horse,
                   'owner' AS source_field, owner AS raw_value
            FROM data
            WHERE rowid <> 1 AND (owner IS NULL OR TRIM(owner) = '')
            """
        ).fetchall()
    finally:
        connection.close()

    source_rows_by_key: dict[tuple[int, str], sqlite3.Row] = {}
    for row in source_blank_rows:
        key = (int(row["source_rowid"]), str(row["source_field"]))
        if key in source_rows_by_key:
            raise AssertionError(f"duplicate source blank key returned: {key}")
        source_rows_by_key[key] = row

    if len(source_rows_by_key) != EXPECTED_RAW_BLANK_OCCURRENCES:
        raise AssertionError(
            f"expected {EXPECTED_RAW_BLANK_OCCURRENCES} source blank keys, "
            f"found {len(source_rows_by_key)}"
        )
    governed_keys = set(decision_records_by_key)
    source_keys = set(source_rows_by_key)
    if governed_keys != source_keys:
        missing_decisions = sorted(source_keys - governed_keys)
        nonblank_or_stale_decisions = sorted(governed_keys - source_keys)
        raise AssertionError(
            "Notebook 20 decisions do not exactly close the raw blank population; "
            f"missing decisions={missing_decisions}, "
            f"stale decisions={nonblank_or_stale_decisions}"
        )

    for key, record in decision_records_by_key.items():
        manual_row = record["row"]
        source_row = source_rows_by_key[key]
        if str(source_row["race_id"]) != record["source_race_id"]:
            raise AssertionError(f"{manual_row.verification_id}: race_id mismatch")
        for column, expected in (
            ("date", manual_row.source_date),
            ("course", manual_row.source_course),
            ("off", manual_row.source_off),
            ("horse", manual_row.source_horse),
        ):
            if str(source_row[column]) != expected:
                raise AssertionError(
                    f"{manual_row.verification_id}: source {column} mismatch; "
                    f"expected {expected!r}, found {source_row[column]!r}"
                )
        if not _is_blank(source_row["raw_value"]):
            raise AssertionError(
                f"{manual_row.verification_id}: governed target is no longer blank"
            )

    applied_counts = {field: 0 for field in EXPECTED_REPAIR_FIELD_COUNTS}
    for repair in repairs:
        record = decision_records_by_id.get(repair.verification_id)
        if record is None:
            raise AssertionError(
                f"{repair.verification_id}: repair has no permanent verification row"
            )
        expected_key = record["key"]
        repair_key = (repair.source_rowid, repair.source_field)
        if repair_key != expected_key:
            raise AssertionError(
                f"{repair.verification_id}: repair key {repair_key} does not match "
                f"manual decision key {expected_key}"
            )
        manual_row = record["row"]
        if repair.governed_value != manual_row.verified_value:
            raise AssertionError(
                f"{repair.verification_id}: governed value does not match manual decision"
            )
        if repair.repair_record_id != record["repair_record_id"]:
            raise AssertionError(
                f"{repair.verification_id}: repair_record_id does not match manual decision"
            )

        source_row = source_rows_by_key[repair_key]
        governed = resolve_connection_value(
            repair.source_rowid,
            repair.source_field,
            source_row["raw_value"],
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
    print(
        "  decision partition: "
        f"verified={decision_counts['verified_repair']}, "
        f"conflicting={decision_counts['conflicting_evidence']}, "
        f"insufficient={decision_counts['insufficient_evidence']}"
    )
    print("  exact raw-blank decision closure: PASS")
    print(f"  governed source supplementations: {len(repairs)}")
    print(f"  unresolved preserved blanks: {len(unresolved_ids)}")
    for field in ("jockey", "trainer", "owner"):
        print(
            f"  {field}: raw blanks={EXPECTED_RAW_BLANK_COUNTS[field]}, "
            f"supplemented={applied_counts[field]}, "
            f"unresolved={remaining_blanks[field]}"
        )


if __name__ == "__main__":
    main()
