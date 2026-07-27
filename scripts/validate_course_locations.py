#!/usr/bin/env python3
"""Validate the permanent Inside Rails course-location reference."""

from __future__ import annotations

import argparse
from pathlib import Path

from inside_rails.course_locations import load_course_locations


EXPECTED_COURSE_IDENTITIES = 394
EXPECTED_DISTINCT_TIMEZONES = 51


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the curated course-location reference."
    )
    parser.add_argument(
        "reference_path",
        nargs="?",
        type=Path,
        default=Path("data/reference/course_locations.csv"),
        help=(
            "Path to course_locations.csv "
            "(default: data/reference/course_locations.csv)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    course_locations = load_course_locations(args.reference_path)

    course_identity_count = len(course_locations)
    assigned_timezone_count = int(
        course_locations["iana_timezone"].notna().sum()
    )
    unresolved_timezone_count = int(
        course_locations["iana_timezone"].isna().sum()
    )
    distinct_timezone_count = int(
        course_locations["iana_timezone"].nunique(dropna=True)
    )

    if course_identity_count != EXPECTED_COURSE_IDENTITIES:
        raise AssertionError(
            "Unexpected course-identity count: "
            f"expected {EXPECTED_COURSE_IDENTITIES}, "
            f"found {course_identity_count}."
        )

    if assigned_timezone_count != EXPECTED_COURSE_IDENTITIES:
        raise AssertionError(
            "Not every course identity has an assigned timezone: "
            f"{assigned_timezone_count} of "
            f"{EXPECTED_COURSE_IDENTITIES} assigned."
        )

    if unresolved_timezone_count != 0:
        raise AssertionError(
            f"Unresolved timezone assignments found: "
            f"{unresolved_timezone_count}."
        )

    if distinct_timezone_count != EXPECTED_DISTINCT_TIMEZONES:
        raise AssertionError(
            "Unexpected distinct-timezone count: "
            f"expected {EXPECTED_DISTINCT_TIMEZONES}, "
            f"found {distinct_timezone_count}."
        )

    print("Course-location reference validation passed")
    print(f"Reference: {args.reference_path}")
    print(f"Course identities: {course_identity_count}")
    print(f"Timezone assignments: {assigned_timezone_count}")
    print(f"Unresolved timezones: {unresolved_timezone_count}")
    print(f"Distinct IANA timezones: {distinct_timezone_count}")


if __name__ == "__main__":
    main()
