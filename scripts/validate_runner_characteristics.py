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

SOURCE_DB = PROJECT_ROOT / "data/raw/form_2015-present/form_2015-present/raceform.db"
DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_BLANK_HG_ROWS = 1_122_490
EXPECTED_POPULATED_HG_ROWS = 728_795
EXPECTED_DISTINCT_POPULATED_HG = 60
EXPECTED_TRAILING_ONE_ROWS = 5_932
EXPECTED_FIRST_TRAILING_ONE_DATE = "2025-10-15"

OUTPUT_DIR = PROJECT_ROOT / "data/processed/notebook_17_runner_characteristics"
SEX_REFERENCE = OUTPUT_DIR / "runner_sex_governance.csv"
HEADGEAR_REFERENCE = OUTPUT_DIR / "runner_headgear_governance.csv"
DECISIONS_REFERENCE = OUTPUT_DIR / "runner_characteristics_decisions.csv"


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Governed output not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    sex_reference = _read_csv(SEX_REFERENCE)
    headgear_reference = _read_csv(HEADGEAR_REFERENCE)
    decisions_reference = _read_csv(DECISIONS_REFERENCE)

    assert len(sex_reference) == 8
    expected_sex_counts = {row["raw_sex"]: int(row["runner_rows"]) for row in sex_reference}
    assert sum(expected_sex_counts.values()) == EXPECTED_RUNNER_ROWS

    assert len(headgear_reference) == 61
    expected_headgear_counts = {row["raw_hg"]: int(row["runner_rows"]) for row in headgear_reference}
    assert sum(expected_headgear_counts.values()) == EXPECTED_RUNNER_ROWS
    assert {row["source_field"] for row in decisions_reference} == {"age", "sex", "hg"}

    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Source database not found: {SOURCE_DB}")

    with sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True) as connection:
        rows = connection.execute(
            f"SELECT rowid, date, age, sex, hg FROM data WHERE {DATA_ROW_PREDICATE}"
        )
        runner_rows = 0
        sex_counts: Counter[str] = Counter()
        headgear_counts: Counter[str] = Counter()
        trailing_one_dates: list[str] = []
        unresolved_headgear: Counter[str] = Counter()

        for rowid, date, age, sex, hg in rows:
            runner_rows += 1
            sex_counts[str(sex)] += 1
            raw_hg = "" if hg is None else str(hg)
            headgear_counts[raw_hg] += 1

            assert normalise_runner_age(age)["interpretation_status"] != "unresolved"

            if sex in {"C", "F", "G", "H", "M", "R"}:
                assert normalise_runner_sex(sex)["interpretation_status"] == "verified_common_code"
            elif sex == "B":
                assert normalise_runner_sex(
                    sex, verification_id="NB17-SEX-0003"
                )["normalised_sex"] == "filly"
            elif sex == "BB":
                assert normalise_runner_sex(
                    sex, verification_id="NB17-SEX-0002"
                )["normalised_sex"] == "gelding"
            else:
                raise AssertionError(f"Ungoverned sex value {sex!r} at row {rowid}")

            parsed = parse_runner_headgear(raw_hg)
            if raw_hg and parsed["interpretation_status"] == "unresolved":
                unresolved_headgear[raw_hg] += 1
            if parsed["source_declared_first_time"]:
                trailing_one_dates.append(str(date))

    assert runner_rows == EXPECTED_RUNNER_ROWS
    assert dict(sex_counts) == expected_sex_counts
    assert dict(headgear_counts) == expected_headgear_counts
    assert headgear_counts[""] == EXPECTED_BLANK_HG_ROWS
    assert sum(v for k, v in headgear_counts.items() if k) == EXPECTED_POPULATED_HG_ROWS
    assert len([k for k in headgear_counts if k]) == EXPECTED_DISTINCT_POPULATED_HG
    assert not unresolved_headgear, dict(unresolved_headgear)
    assert len(trailing_one_dates) == EXPECTED_TRAILING_ONE_ROWS
    assert min(trailing_one_dates) == EXPECTED_FIRST_TRAILING_ONE_DATE

    print(f"runner rows: {runner_rows:,}")
    print(f"sex values: {len(sex_counts)}; corrected anomalies: 2")
    print(f"headgear: {EXPECTED_BLANK_HG_ROWS:,} blank; {EXPECTED_POPULATED_HG_ROWS:,} populated")
    print(f"trailing-1 rows: {len(trailing_one_dates):,}; first date: {min(trailing_one_dates)}")
    print("runner-characteristics source validation passed")


if __name__ == "__main__":
    main()
