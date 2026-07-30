"""Load, validate and join the curated course-location reference."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd

from inside_rails.course_jurisdiction import (
    derive_candidate_course_label,
    derive_candidate_race_jurisdiction,
)

IDENTITY_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
]

SOURCE_CONTEXT_COLUMNS = [
    "course",
    "date",
    "type",
    "race_name",
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


def _require_columns(
    frame: pd.DataFrame,
    columns: list[str],
    frame_name: str,
) -> None:
    missing_columns = [column for column in columns if column not in frame.columns]
    if missing_columns:
        raise ValueError(
            f"{frame_name} is missing required columns: "
            + ", ".join(missing_columns)
        )


def load_course_locations(path: str | Path) -> pd.DataFrame:
    """Load and validate the curated course-location reference."""

    reference_path = Path(path)
    frame = pd.read_csv(reference_path)

    _require_columns(frame, REQUIRED_COLUMNS, "Course-location reference")

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

    latitude_values = pd.to_numeric(frame["latitude"], errors="coerce")
    longitude_values = pd.to_numeric(frame["longitude"], errors="coerce")

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


def derive_source_course_identities(source: pd.DataFrame) -> pd.DataFrame:
    """Derive governed course identities while preserving raw source text."""

    _require_columns(source, SOURCE_CONTEXT_COLUMNS, "Source course data")

    frame = source.copy()
    jurisdiction = frame.apply(derive_candidate_race_jurisdiction, axis=1)
    jurisdiction.columns = [
        "candidate_jurisdiction",
        "course_jurisdiction_evidence",
    ]

    frame["candidate_course_label"] = frame["course"].map(
        derive_candidate_course_label
    )
    frame[[
        "candidate_jurisdiction",
        "course_jurisdiction_evidence",
    ]] = jurisdiction

    return frame


def merge_course_locations(
    races: pd.DataFrame,
    course_locations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach curated fields to rows that already contain resolved identities."""

    _require_columns(races, IDENTITY_COLUMNS, "Resolved race data")
    _require_columns(course_locations, IDENTITY_COLUMNS, "Course-location reference")

    return races.merge(
        course_locations,
        on=IDENTITY_COLUMNS,
        how="left",
        validate="many_to_one",
    )


def merge_source_course_locations(
    source: pd.DataFrame,
    course_locations: pd.DataFrame,
    *,
    require_all_matches: bool = False,
) -> pd.DataFrame:
    """Derive identities and attach governed location fields to raw source rows.

    Raw ``course`` text is retained unchanged. The returned
    ``course_location_match_status`` column makes unmatched source updates an
    explicit review residue. Set ``require_all_matches`` to fail when any row
    has no governed identity match.
    """

    resolved = derive_source_course_identities(source)
    merged = resolved.merge(
        course_locations,
        on=IDENTITY_COLUMNS,
        how="left",
        validate="many_to_one",
        indicator="course_location_match_status",
    )

    unmatched = unmatched_source_course_locations(merged)
    if require_all_matches and not unmatched.empty:
        records = unmatched[
            ["course", *IDENTITY_COLUMNS]
        ].to_dict("records")
        raise ValueError(
            "Unmatched governed course identities found: "
            f"{records}"
        )

    return merged


def unmatched_source_course_locations(merged: pd.DataFrame) -> pd.DataFrame:
    """Return the distinct unmatched raw-label and derived-identity residue."""

    _require_columns(
        merged,
        ["course", *IDENTITY_COLUMNS, "course_location_match_status"],
        "Merged source course data",
    )

    return (
        merged.loc[
            merged["course_location_match_status"] != "both",
            ["course", *IDENTITY_COLUMNS],
        ]
        .drop_duplicates()
        .sort_values(["course", *IDENTITY_COLUMNS])
        .reset_index(drop=True)
    )
