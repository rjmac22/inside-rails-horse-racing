#!/usr/bin/env python3
"""Validate Notebook 04's bounded source-supported surface rule."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from inside_rails.race_surface import profile_source_supported_surface
from inside_rails.source_sqlite import connect_read_only

EXPECTED_PROFILE = {
    "provisional_races": 189_043,
    "explicit_all_weather_races": 33_023,
    "unresolved_surface_races": 156_020,
    "raw_course_values": 528,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with connect_read_only(args.database) as connection:
        observed = profile_source_supported_surface(connection)

    failures: list[str] = []
    for key, expected in EXPECTED_PROFILE.items():
        actual = observed[key]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status:4} {key}: observed={actual} expected={expected}")
        if actual != expected:
            failures.append(key)

    if failures:
        print("\nRace surface validation failed for: " + ", ".join(failures), file=sys.stderr)
        return 1

    print("\nRace surface validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
