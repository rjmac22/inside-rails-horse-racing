#!/usr/bin/env python3
"""Validate the structural source profile established by Notebook 01."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from inside_rails.source_sqlite import connect_read_only, profile_source_database

EXPECTED_PROFILE = {
    "physical_rows": 1_851_286,
    "data_rows": 1_851_285,
    "apparent_races": 189_043,
    "provisional_runner_keys": 1_851_285,
    "duplicate_rows_under_provisional_runner_key": 0,
    "minimum_date": "2015-01-01",
    "maximum_date": "2026-05-27",
    "quick_check": "ok",
    "schema_objects": 1,
    "declared_columns": 37,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate raceform.db against the Notebook 01 profile."
    )
    parser.add_argument(
        "database",
        type=Path,
        help="Path to the immutable source raceform.db file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    with connect_read_only(args.database) as connection:
        observed = profile_source_database(connection)

    failures: list[str] = []
    for key, expected_value in EXPECTED_PROFILE.items():
        observed_value = observed[key]
        status = "PASS" if observed_value == expected_value else "FAIL"
        print(
            f"{status:4} {key}: observed={observed_value!r} "
            f"expected={expected_value!r}"
        )
        if observed_value != expected_value:
            failures.append(key)

    if failures:
        print("\nValidation failed for: " + ", ".join(failures), file=sys.stderr)
        return 1

    print("\nSource structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
