#!/usr/bin/env python3
"""Validate Notebook 17 governance directly against the immutable source."""

from __future__ import annotations

import csv
import sqlite3
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.manual_verifications import load_manual_verifications  # noqa: E402
from inside_rails.runner_characteristics import (  # noqa: E402
    normalise_runner_age,
    normalise_runner_sex,
    parse_runner_headgear,
)

SOURCE_DB = PROJECT_ROOT / "data/raw/form_2015-present/form_2015-present/raceform.db"
MANUAL_VERIFICATIONS = PROJECT_ROOT / "data/reference/manual_verifications.csv"
GOVERNANCE_REFERENCE = (
    PROJECT_ROOT / "data/reference/runner_characteristics_governance.csv"
)
DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_AGE_DISTINCT_VALUES = 19
EXPECTED_AGE_MINIMUM = 1
EXPECTED_AGE_MAXIMUM = 31
EXPECTED_SEX_COUNTS = {
    "G": 1_078_420,
    "F": 371_961,
    "M": 190_797,
    "C": 178_499,
    "H": 30_728,
    "R": 878,
    "B": 1,
    "BB": 1,
}
EXPECTED_BLANK_HG_ROWS = 1_122_490
EXPECTED_POPULATED_HG_ROWS = 728_795
EXPECTED_DISTINCT_POPULATED_HG = 60
EXPECTED_TRAILING_ONE_ROWS = 5_932
EXPECTED_FIRST_TRAILING_ONE_DATE = "2025-10-15"
EXPECTED_VERIFICATION_IDS = {
    "NB17-SEX-0001",
    "NB17-HG-0001",
    "NB17-SEX-0002",
    "NB17-SEX-0003",
    "NB17-HG-0002",
}
EXPECTED_STATUS_COUNTS = Counter({"confirmed": 3, "contradicted": 2})
EXPECTED_ACTION_COUNTS = Counter(
    {"reference_enrichment": 3, "source_correction_candidate": 2}
)
EXPECTED_GOVERNANCE_STATUS = {
    "age": "confirmed_source_integer_contextual_semantics",
    "sex": "confirmed_reference_with_exact_corrections",
    "hg": "confirmed_parser_with_source_specific_component",
}
GOVERNANCE_COLUMNS = (
    "source_field",
    "source_meaning",
    "safe_derived_treatment",
    "unresolved_or_unsafe_treatment",
    "status",
)
EXPECTED_VERIFICATION_FACTS = {
    "NB17-SEX-0001": {
        "subject_type": "source_value",
        "source_field": "sex",
        "raw_source_value": "C|F|G|H|M|R",
        "verified_value": "C=colt; F=filly; G=gelding; H=horse; M=mare; R=rig",
        "verification_status": "confirmed",
        "confidence": "high",
        "database_action": "reference_enrichment",
    },
    "NB17-HG-0001": {
        "subject_type": "source_value",
        "source_field": "hg",
        "raw_source_value": "h|b|p|t|v|e|ht|e/c|e/s|b1|b2",
        "verified_value": "h=hood; b=blinkers; p=cheekpieces; t=tongue-tie; v=visor; e=eye hood; ht=hood and tongue-tie; e/c=eyecover; e/s=eyeshield; b1=first-time blinkers; b2=second-time blinkers",
        "verification_status": "confirmed",
        "confidence": "high",
        "database_action": "reference_enrichment",
    },
    "NB17-SEX-0002": {
        "subject_type": "runner",
        "source_date": "2017-10-15",
        "source_course": "Cologne (GER)",
        "source_off": "1:35",
        "source_horse": "Par Coeur (GER)",
        "source_field": "sex",
        "raw_source_value": "BB",
        "verified_value": "G=gelding",
        "verification_status": "contradicted",
        "confidence": "high",
        "database_action": "source_correction_candidate",
    },
    "NB17-SEX-0003": {
        "subject_type": "runner",
        "source_date": "2019-11-29",
        "source_course": "Gulfstream Park (USA)",
        "source_off": "8:30",
        "source_horse": "La Venezolana (VEN)",
        "source_field": "sex",
        "raw_source_value": "B",
        "verified_value": "F=filly",
        "verification_status": "contradicted",
        "confidence": "high",
        "database_action": "source_correction_candidate",
    },
    "NB17-HG-0002": {
        "subject_type": "source_value",
        "source_date": "2023-05-30",
        "source_course": "Redcar",
        "source_off": "4:20",
        "source_horse": "Humble Spark (IRE)",
        "source_field": "hg",
        "raw_source_value": "c",
        "verified_value": "c=eyecover",
        "verification_status": "confirmed",
        "confidence": "high",
        "database_action": "reference_enrichment",
    },
}


def _load_governance(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != GOVERNANCE_COLUMNS:
            raise AssertionError(
                "Notebook 17 governance columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        rows = tuple(
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        )
    if len(rows) != 3:
        raise AssertionError(f"expected 3 governance rows, found {len(rows)}")
    indexed = {row["source_field"]: row for row in rows}
    if len(indexed) != 3 or set(indexed) != set(EXPECTED_GOVERNANCE_STATUS):
        raise AssertionError(
            f"unexpected runner-characteristic fields: {sorted(indexed)!r}"
        )
    for field, expected_status in EXPECTED_GOVERNANCE_STATUS.items():
        row = indexed[field]
        if row["status"] != expected_status:
            raise AssertionError(f"{field}: governance status changed")
        if not row["source_meaning"] or not row["safe_derived_treatment"]:
            raise AssertionError(f"{field}: governed meaning and treatment are required")
        if not row["unresolved_or_unsafe_treatment"]:
            raise AssertionError(f"{field}: unresolved treatment is required")


def _load_verifications(path: Path) -> dict[str, object]:
    all_rows = load_manual_verifications(path)
    rows = tuple(
        row
        for row in all_rows
        if row.verification_id.startswith("NB17-")
    )
    ids = {row.verification_id for row in rows}
    if len(rows) != 5 or ids != EXPECTED_VERIFICATION_IDS:
        raise AssertionError(
            "Notebook 17 verification closure changed; "
            f"missing={sorted(EXPECTED_VERIFICATION_IDS - ids)}, "
            f"extra={sorted(ids - EXPECTED_VERIFICATION_IDS)}"
        )
    statuses = Counter(row.verification_status for row in rows)
    actions = Counter(row.database_action for row in rows)
    if statuses != EXPECTED_STATUS_COUNTS:
        raise AssertionError(f"unexpected Notebook 17 status partition: {dict(statuses)}")
    if actions != EXPECTED_ACTION_COUNTS:
        raise AssertionError(f"unexpected Notebook 17 action partition: {dict(actions)}")

    indexed = {row.verification_id: row for row in rows}
    for verification_id, expected in EXPECTED_VERIFICATION_FACTS.items():
        row = indexed[verification_id]
        if row.governing_notebook != "17":
            raise AssertionError(f"{verification_id}: governing_notebook must be 17")
        for field, expected_value in expected.items():
            if getattr(row, field) != expected_value:
                raise AssertionError(
                    f"{verification_id}: {field} changed; "
                    f"observed={getattr(row, field)!r}, expected={expected_value!r}"
                )
        if not row.evidence_type or not row.evidence_locator:
            raise AssertionError(f"{verification_id}: evidence provenance is required")
        if row.evidence_accessed_date not in {"2026-07-30", "2026-07-31"}:
            raise AssertionError(f"{verification_id}: unexpected evidence access date")
        if not row.notes:
            raise AssertionError(f"{verification_id}: notes must not be blank")
    return indexed


def main() -> None:
    _load_governance(GOVERNANCE_REFERENCE)
    _load_verifications(MANUAL_VERIFICATIONS)

    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Source database not found: {SOURCE_DB}")

    with sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True) as connection:
        age_summary = connection.execute(
            f"""
            SELECT COUNT(*), COUNT(DISTINCT age), MIN(age), MAX(age),
                   COUNT(DISTINCT typeof(age))
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            """
        ).fetchone()
        if tuple(int(value) for value in age_summary) != (
            EXPECTED_RUNNER_ROWS,
            EXPECTED_AGE_DISTINCT_VALUES,
            EXPECTED_AGE_MINIMUM,
            EXPECTED_AGE_MAXIMUM,
            1,
        ):
            raise AssertionError(f"runner-age source profile changed: {age_summary!r}")

        rows = connection.execute(
            f"""
            SELECT rowid, date, course, off, horse, age, sex, hg
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            """
        )
        runner_rows = 0
        sex_counts: Counter[str] = Counter()
        headgear_counts: Counter[str] = Counter()
        trailing_one_dates: list[str] = []
        unresolved_headgear: Counter[str] = Counter()
        corrected_ids: set[str] = set()
        humble_spark_seen = False

        for rowid, source_date, course, off, horse, age, sex, hg in rows:
            runner_rows += 1
            raw_sex = str(sex)
            sex_counts[raw_sex] += 1
            raw_hg = "" if hg is None else str(hg)
            headgear_counts[raw_hg] += 1

            if normalise_runner_age(age)["interpretation_status"] != "source_recorded_integer":
                raise AssertionError(f"unresolved runner age at source row {rowid}")

            if raw_sex in {"C", "F", "G", "H", "M", "R"}:
                result = normalise_runner_sex(raw_sex)
                if result["interpretation_status"] != "verified_common_code":
                    raise AssertionError(f"common sex code failed at row {rowid}")
            elif raw_sex == "B":
                result = normalise_runner_sex(
                    raw_sex,
                    verification_id="NB17-SEX-0003",
                    source_date=str(source_date),
                    source_course=str(course),
                    source_off=str(off),
                    source_horse=str(horse),
                )
                if result["normalised_sex"] != "filly":
                    raise AssertionError("La Venezolana exact correction did not apply")
                corrected_ids.add("NB17-SEX-0003")
            elif raw_sex == "BB":
                result = normalise_runner_sex(
                    raw_sex,
                    verification_id="NB17-SEX-0002",
                    source_date=str(source_date),
                    source_course=str(course),
                    source_off=str(off),
                    source_horse=str(horse),
                )
                if result["normalised_sex"] != "gelding":
                    raise AssertionError("Par Coeur exact correction did not apply")
                corrected_ids.add("NB17-SEX-0002")
            else:
                raise AssertionError(f"ungoverned sex value {sex!r} at row {rowid}")

            parsed = parse_runner_headgear(raw_hg)
            if raw_hg and parsed["interpretation_status"] == "unresolved":
                unresolved_headgear[raw_hg] += 1
            if parsed["source_declared_first_time"]:
                trailing_one_dates.append(str(source_date))
            if int(rowid) == 1_347_987:
                if (
                    str(source_date),
                    str(course),
                    str(off),
                    str(horse),
                ) != ("2023-05-30", "Redcar", "4:20", "Humble Spark (IRE)"):
                    raise AssertionError("NB17-HG-0002 source lineage changed")
                if "c" not in raw_hg:
                    raise AssertionError("NB17-HG-0002 source code no longer contains c")
                humble_spark_seen = True

    if runner_rows != EXPECTED_RUNNER_ROWS:
        raise AssertionError(f"expected {EXPECTED_RUNNER_ROWS} rows, found {runner_rows}")
    if dict(sex_counts) != EXPECTED_SEX_COUNTS:
        raise AssertionError(
            f"runner-sex counts changed: observed={dict(sex_counts)}, "
            f"expected={EXPECTED_SEX_COUNTS}"
        )
    if corrected_ids != {"NB17-SEX-0002", "NB17-SEX-0003"}:
        raise AssertionError(f"exact correction closure changed: {sorted(corrected_ids)!r}")
    if headgear_counts[""] != EXPECTED_BLANK_HG_ROWS:
        raise AssertionError("blank headgear population changed")
    populated_hg = sum(value for key, value in headgear_counts.items() if key)
    if populated_hg != EXPECTED_POPULATED_HG_ROWS:
        raise AssertionError("populated headgear population changed")
    if len([key for key in headgear_counts if key]) != EXPECTED_DISTINCT_POPULATED_HG:
        raise AssertionError("distinct populated headgear vocabulary changed")
    if unresolved_headgear:
        raise AssertionError(f"unresolved current headgear values: {dict(unresolved_headgear)}")
    if len(trailing_one_dates) != EXPECTED_TRAILING_ONE_ROWS:
        raise AssertionError("trailing-1 headgear population changed")
    if min(trailing_one_dates) != EXPECTED_FIRST_TRAILING_ONE_DATE:
        raise AssertionError("first trailing-1 headgear date changed")
    if not humble_spark_seen:
        raise AssertionError("NB17-HG-0002 source row was not found")

    print(f"runner rows: {runner_rows:,}")
    print(f"age values: {EXPECTED_AGE_DISTINCT_VALUES}; range 1-31")
    print(f"sex values: {len(sex_counts)}; exact corrected anomalies: 2")
    print(
        f"headgear: {EXPECTED_BLANK_HG_ROWS:,} blank; "
        f"{EXPECTED_POPULATED_HG_ROWS:,} populated"
    )
    print(
        f"trailing-1 rows: {len(trailing_one_dates):,}; "
        f"first date: {min(trailing_one_dates)}"
    )
    print("governance rows: 3; external decisions: 5")
    print("runner-characteristics source validation passed")


if __name__ == "__main__":
    main()
