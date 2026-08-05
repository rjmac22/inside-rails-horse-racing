#!/usr/bin/env python3
"""Validate the permanent course-location reference and manual provenance."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from inside_rails.course_locations import load_course_locations


EXPECTED_COURSE_IDENTITIES = 395
EXPECTED_DISTINCT_TIMEZONES = 51
EXPECTED_VERIFICATION_IDS = {"NB12-COURSE-0001", "NB12-COURSE-0002"}
VERIFICATION_COLUMNS = (
    "verification_id",
    "source_course",
    "candidate_course_label",
    "candidate_jurisdiction",
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "database_action",
    "notes",
)
REFERENCE_MATCH_COLUMNS = (
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the curated course-location reference."
    )
    parser.add_argument(
        "reference_path",
        nargs="?",
        type=Path,
        default=Path("data/reference/course_locations.csv"),
        help="Path to course_locations.csv",
    )
    parser.add_argument(
        "--verifications",
        type=Path,
        default=Path("data/reference/course_location_verifications.csv"),
        help="Path to Notebook 12 specialist verification records",
    )
    return parser.parse_args()


def load_verifications(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != VERIFICATION_COLUMNS:
            raise AssertionError(
                "Notebook 12 verification columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        rows = tuple(
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        )

    ids = {row["verification_id"] for row in rows}
    if len(rows) != 2 or ids != EXPECTED_VERIFICATION_IDS:
        raise AssertionError(
            f"unexpected Notebook 12 verification closure: ids={sorted(ids)!r}"
        )

    for row in rows:
        verification_id = row["verification_id"]
        if row["verification_status"] != "confirmed":
            raise AssertionError(f"{verification_id}: verification must be confirmed")
        if row["confidence"] != "high":
            raise AssertionError(f"{verification_id}: confidence must be high")
        if row["database_action"] != "reference_enrichment":
            raise AssertionError(
                f"{verification_id}: action must be reference_enrichment"
            )
        if not row["evidence_type"] or not row["evidence_locator"]:
            raise AssertionError(f"{verification_id}: evidence provenance is required")
        if date.fromisoformat(row["evidence_accessed_date"]) != date(2026, 7, 26):
            raise AssertionError(
                f"{verification_id}: expected recovered request date 2026-07-26"
            )
        if not row["notes"]:
            raise AssertionError(f"{verification_id}: notes must not be blank")
    return rows


def main() -> None:
    args = parse_args()

    course_locations = load_course_locations(args.reference_path)
    verifications = load_verifications(args.verifications)

    course_identity_count = len(course_locations)
    assigned_timezone_count = int(course_locations["iana_timezone"].notna().sum())
    unresolved_timezone_count = int(course_locations["iana_timezone"].isna().sum())
    distinct_timezone_count = int(
        course_locations["iana_timezone"].nunique(dropna=True)
    )

    if course_identity_count != EXPECTED_COURSE_IDENTITIES:
        raise AssertionError(
            "Unexpected course-identity count: "
            f"expected {EXPECTED_COURSE_IDENTITIES}, found {course_identity_count}."
        )
    if assigned_timezone_count != EXPECTED_COURSE_IDENTITIES:
        raise AssertionError(
            "Not every course identity has an assigned timezone: "
            f"{assigned_timezone_count} of {EXPECTED_COURSE_IDENTITIES} assigned."
        )
    if unresolved_timezone_count != 0:
        raise AssertionError(
            f"Unresolved timezone assignments found: {unresolved_timezone_count}."
        )
    if distinct_timezone_count != EXPECTED_DISTINCT_TIMEZONES:
        raise AssertionError(
            "Unexpected distinct-timezone count: "
            f"expected {EXPECTED_DISTINCT_TIMEZONES}, found {distinct_timezone_count}."
        )

    indexed = course_locations.set_index(
        ["candidate_course_label", "candidate_jurisdiction"]
    )
    if not indexed.index.is_unique:
        raise AssertionError("Course-location reference contains duplicate identity keys")

    for verification in verifications:
        verification_id = verification["verification_id"]
        key = (
            verification["candidate_course_label"],
            verification["candidate_jurisdiction"],
        )
        if key not in indexed.index:
            raise AssertionError(f"{verification_id}: governed course identity is missing")
        reference_row = indexed.loc[key]
        for column in REFERENCE_MATCH_COLUMNS:
            observed = "" if reference_row[column] is None else str(reference_row[column])
            if observed != verification[column]:
                raise AssertionError(
                    f"{verification_id}: {column} mismatch; "
                    f"reference={observed!r}, verification={verification[column]!r}"
                )
        raw_labels = {
            value.strip() for value in str(reference_row["raw_course_labels"]).split("|")
        }
        if verification["source_course"] not in raw_labels:
            raise AssertionError(
                f"{verification_id}: source course is absent from raw_course_labels"
            )
        if reference_row["location_validation_status"] != "manually_validated":
            raise AssertionError(
                f"{verification_id}: reference row must remain manually_validated"
            )

    print("Course-location reference validation passed")
    print(f"Reference: {args.reference_path}")
    print(f"Course identities: {course_identity_count}")
    print(f"Timezone assignments: {assigned_timezone_count}")
    print(f"Unresolved timezones: {unresolved_timezone_count}")
    print(f"Distinct IANA timezones: {distinct_timezone_count}")
    print(f"Manual provenance records: {len(verifications)}")
    print("Exact verification-to-reference agreement: PASS")


if __name__ == "__main__":
    main()
