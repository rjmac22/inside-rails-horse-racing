#!/usr/bin/env python3
"""Validate Notebook 05 result representation against the immutable source."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from inside_rails.race_results import profile_result_representation
from inside_rails.source_sqlite import connect_read_only

EXPECTED = {
    "data_rows": 1_851_285,
    "positive_numeric_position_rows": 1_756_634,
    "zero_position_rows": 8,
    "disqualified_rows": 619,
    "other_text_outcome_rows": 93_992,
    "missing_position_rows": 32,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    with connect_read_only(args.database) as connection:
        observed = profile_result_representation(connection)

    failures: list[str] = []
    for key, expected in EXPECTED.items():
        actual = observed[key]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status} {key}: observed={actual} expected={expected}")
        if actual != expected:
            failures.append(key)

    represented = sum(
        value for key, value in observed.items() if key != "data_rows"
    )
    partition_ok = represented == observed["data_rows"]
    print(
        f"{'PASS' if partition_ok else 'FAIL'} complete_partition: "
        f"represented={represented} data_rows={observed['data_rows']}"
    )
    if not partition_ok:
        failures.append("complete_partition")

    if failures:
        print("\nRace result validation failed for: " + ", ".join(failures), file=sys.stderr)
        return 1

    print("\nRace result validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
