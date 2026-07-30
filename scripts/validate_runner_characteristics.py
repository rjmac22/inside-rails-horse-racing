#!/usr/bin/env python3
"""Validate Notebook 17 runner-characteristic rules against the full source."""

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

from inside_rails.runner_characteristics import (  # noqa: E402
    normalise_runner_age,
    normalise_runner_sex,
    parse_runner_headgear,
)

SOURCE_DB = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_SEX_COUNTS = {
    "C": 80_284,
    "F": 360_639,
    "G": 662_772,
    "H": 24_483,
    "M": 722_097,
    "R": 1_008,
    "B": 1,
    "BB": 1,
}
EXPECTED_BLANK_HG_ROWS = 1_122_490
EXPECTED_POPULATED_HG_ROWS = 728_795
EXPECTED_DISTINCT_POPULATED_HG = 60
EXPECTED_TRAILING_ONE_ROWS = 5_932
EXPECTED_FIRST_TRAILING_ONE_DATE = "2025-10-15"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "notebook_17_runner_characteristics"
SEX_REFERENCE = OUTPUT_DIR / "runner_sex_governance.csv"
HEADGEAR_REFERENCE = OUTPUT_DIR / "runner_headgear_governance.csv"
DECISIONS_REFERENCE = OUTPUT_DIR / "runner_characteristics_decisions.csv"


def _connect_read_only(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"Source database not found: {path}")
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Governed output not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    with _connect_read_only(SOURCE_DB) as connection:
        rows = connection.execute(
            f"SELECT rowid, date, age, sex, hg FROM data WHERE {DATA_ROW_PREDICATE}"
        )

        runner_rows = 0
        sex_counts: Counter[str] = Counter()
        headgear_counts: Counter[str] = Counter()
        trailing_one_rows = 0
        trailing_one_dates: list[str] = []
        unresolved_ages = 0
        unresolved_common_sex = 0
        unresolved_headgear: Counter[str] = Counter()

        for rowid, date, age, sex, hg in rows:
            runner_rows += 1
            sex_counts[str(sex)] += 1
            raw_hg = "" if hg is None else str(hg)
            headgear_counts[raw_hg] += 1

            if normalise_runner_age(age)["interpretation_status"] == "unresolved":
                unresolved_ages += 1

            if sex in {"C", "F", "G", "H", "M", "R"}:
                if normalise_runner_sex(sex)["interpretation_status"] == "unresolved":
                    unresolved_common_sex += 1
            elif sex == "B":
                result = normalise_runner_sex(
                    sex, verification_id="NB17-SEX-0003"
                )
                if result["normalised_sex"] != "filly":
                    raise AssertionError(f"B correction failed at source row {rowid}")
            elif sex == "BB":
                result = normalise_runner_sex(
                    sex, verification_id="NB17-SEX-0002"
                )
                if result["normalised_sex"] != "gelding":
                    raise AssertionError(f"BB correction failed at source row {rowid}")
            else:
                raise AssertionError(f"Ungoverned sex value {sex!r} at row {rowid}")

            parsed_headgear = parse_runner_headgear(raw_hg)
            if raw_hg and parsed_headgear["interpretation_status"] == "unresolved":
                unresolved_headgear[raw_hg] += 1
            if parsed_headgear["source_declared_first_time"]:
                trailing_one_rows += 1
                trailing_one_dates.append(str(date))

    assert runner_rows == EXPECTED_RUNNER_ROWS
    assert unresolved_ages == 0
    assert unresolved_common_sex == 0
    assert dict(sex_counts) == EXPECTED_SEX_COUNTS
    assert headgear_counts[""] == EXPECTED_BLANK_HG_ROWS
    assert sum(count for value, count in headgear_counts.items() if value) == EXPECTED_POPULATED_HG_ROWS
    assert len([value for value in headgear_counts if value]) == EXPECTED_DISTINCT_POPULATED_HG
    assert not unresolved_headgear, f"Ungoverned headgear values: {dict(unresolved_headgear)}"
    assert trailing_one_rows == EXPECTED_TRAILING_ONE_ROWS
    assert min(trailing_one_dates) == EXPECTED_FIRST_TRAILING_ONE_DATE

    sex_reference = _read_csv(SEX_REFERENCE)
    headgear_reference = _read_csv(HEADGEAR_REFERENCE)
    decisions_reference = _read_csv(DECISIONS_REFERENCE)

    assert len(sex_reference) == 8
    assert len({row["raw_sex"] for row in sex_reference}) == 8
    assert sum(int(row["runner_rows"]) for row in sex_reference) == EXPECTED_RUNNER_ROWS

    assert len(headgear_reference) == 61
    assert len({row["raw_hg"] for row in headgear_reference}) == 61
    assert sum(int(row["runner_rows"]) for row in headgear_reference) == EXPECTED_RUNNER_ROWS

    assert {row["source_field"] for row in decisions_reference} == {"age", "sex", "hg"}

    print(f"runner rows: {runner_rows:,}")
    print(f"sex values: {len(sex_counts)}; corrected anomalies: 2")
    print(
        "headgear: "
        f"{EXPECTED_BLANK_HG_ROWS:,} blank, "
        f"{EXPECTED_POPULATED_HG_ROWS:,} populated, "
        f"{EXPECTED_DISTINCT_POPULATED_HG} populated values"
    )
    print(
        f"trailing-1 rows: {trailing_one_rows:,}; "
        f"first date: {min(trailing_one_dates)}"
    )
    print("runner-characteristics source validation passed")


if __name__ == "__main__":
    main()
