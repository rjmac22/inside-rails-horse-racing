"""Load and validate the curated course-location reference."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd


IDENTITY_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
]

REQUIRED_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
    "location_evidence",
    "location_validation_status",
]


def load_course_locations(path: str | Path) -> pd.DataFrame:
    """Load and validate the curated course-location reference."""

    reference_path = Path(path)
    frame = pd.read_csv(reference_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            "Course-location reference is missing required columns: "
            + ", ".join(missing_columns)
        )

    duplicate_mask = frame.duplicated(
        subset=IDENTITY_COLUMNS,
        keep=False,
    )

    if duplicate_mask.any():
        duplicates = (
            frame.loc[duplicate_mask, IDENTITY_COLUMNS]
            .drop_duplicates()
            .to_dict("records")
        )
        raise ValueError(
            f"Duplicate candidate course identities found: {duplicates}"
        )

    assigned_timezone_mask = frame["iana_timezone"].notna()

    invalid_timezones = []

    for timezone_name in sorted(
        frame.loc[assigned_timezone_mask, "iana_timezone"].unique()
    ):
        try:
            ZoneInfo(str(timezone_name))
        except ZoneInfoNotFoundError:
            invalid_timezones.append(str(timezone_name))

    if invalid_timezones:
        raise ValueError(
            "Invalid IANA timezone names: "
            + ", ".join(invalid_timezones)
        )

    latitude_values = pd.to_numeric(
        frame["latitude"],
        errors="coerce",
    )
    longitude_values = pd.to_numeric(
        frame["longitude"],
        errors="coerce",
    )

    invalid_latitude_mask = (
        frame["latitude"].notna()
        & ~latitude_values.between(-90, 90)
    )
    invalid_longitude_mask = (
        frame["longitude"].notna()
        & ~longitude_values.between(-180, 180)
    )

    if invalid_latitude_mask.any():
        raise ValueError("Latitude values must fall between -90 and 90.")

    if invalid_longitude_mask.any():
        raise ValueError("Longitude values must fall between -180 and 180.")

    return frame


def merge_course_locations(
    races: pd.DataFrame,
    course_locations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach curated course-location fields to resolved race identities."""

    return races.merge(
        course_locations,
        on=IDENTITY_COLUMNS,
        how="left",
        validate="many_to_one",
    )
