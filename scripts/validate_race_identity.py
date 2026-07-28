#!/usr/bin/env python3
"""Validate Notebook 03 race and runner-record identity rules."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from inside_rails.race_identity import profile_race_identity
from inside_rails.source_sqlite import connect_read_only

EXPECTED_PROFILE = {
    "data_rows": 1_851_285,
    "candidate_races": 189_043,
    "candidate_runner_records": 1_851_285,
    "race_name_collisions": 0,
    "source_race_id_collisions_within_candidate_race": 0,
    "duplicate_candidate_runner_records": 0,
    "colliding_date_race_id_groups": 8,
    "duplicate_runner_number_groups": 700,
    "distinct_source_race_ids": 188_782,
    "distinct_date_race_ids": 189_035,
    "distinct_dates": 4_130,
    "minimum_source_rowid": 2,
    "maximum_source_rowid": 1_851_286,
    "null_identity_rows": 0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate raceform.db against Notebook 03 identity rules."
    )
    parser.add_argument("database", type=Path, help="Path to immutable raceform.db")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with connect_read_only(args.database) as connection:
        observed = profile_race_identity(connection)

    failures: list[str] = []
    for key, expected in EXPECTED_PROFILE.items():
        actual = observed[key]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status:4} {key}: observed={actual!r} expected={expected!r}")
        if actual != expected:
            failures.append(key)

    if failures:
        print("\nRace identity validation failed for: " + ", ".join(failures), file=sys.stderr)
        return 1

    print("\nRace identity validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
