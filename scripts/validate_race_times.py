#!/usr/bin/env python3
"""Validate reusable race-time reconstruction helpers."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from inside_rails.race_times import (
    FORMAT_BOUNDARY,
    VALIDATED_TOTALS,
    build_post_boundary_times,
    classify_london_civil_time,
    parse_12_hour_minutes,
    parse_24_hour_minutes,
    reconstruct_pre_boundary_candidates,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate reusable race-time reconstruction helpers."
    )
    parser.add_argument(
        "canonical_path",
        nargs="?",
        type=Path,
        help=(
            "Optional canonical race-time CSV or Parquet file. When supplied, "
            "the validated Notebook 11 population totals are enforced."
        ),
    )
    return parser.parse_args()


def validate_clock_parsers() -> None:
    assert parse_12_hour_minutes("12:30") == 30
    assert parse_12_hour_minutes("1:05") == 65
    assert parse_12_hour_minutes("11:59") == 719
    assert parse_24_hour_minutes("00:30") == 30
    assert parse_24_hour_minutes("13:05") == 785
    assert parse_24_hour_minutes("23:59") == 1439


def validate_dst_classification() -> None:
    assert classify_london_civil_time("2015-03-29 01:30") == (
        "nonexistent_dst_time"
    )
    assert classify_london_civil_time("2015-10-25 01:30") == (
        "ambiguous_dst_time"
    )
    assert classify_london_civil_time("2015-01-01 13:30") == "valid"


def validate_meeting_unwrap() -> None:
    races = pd.DataFrame(
        {
            "date": ["2015-01-01"] * 4,
            "course": ["Example"] * 4,
            "off": ["11:30", "12:05", "12:40", "1:15"],
            "race_id": [1, 2, 3, 4],
        }
    )
    result = reconstruct_pre_boundary_candidates(races)
    expected_a = pd.to_datetime(
        [
            "2015-01-01 11:30",
            "2015-01-01 12:05",
            "2015-01-01 12:40",
            "2015-01-01 13:15",
        ]
    )
    assert result["candidate_a_uk_naive"].tolist() == expected_a.tolist()
    assert (
        result["candidate_b_uk_naive"]
        - result["candidate_a_uk_naive"]
    ).eq(pd.Timedelta(hours=12)).all()


def validate_explicit_post_boundary() -> None:
    races = pd.DataFrame(
        {
            "date": [FORMAT_BOUNDARY.date().isoformat()],
            "course": ["Example"],
            "off": ["13:05"],
            "race_id": [1],
            "iana_timezone": ["Europe/Paris"],
        }
    )
    result = build_post_boundary_times(races)
    assert str(result.loc[0, "advertised_start_uk"]) == (
        "2025-10-15 13:05:00+01:00"
    )
    assert str(result.loc[0, "advertised_start_utc"]) == (
        "2025-10-15 12:05:00+00:00"
    )
    assert str(result.loc[0, "advertised_start_course_local"]) == (
        "2025-10-15 14:05:00+02:00"
    )


def load_canonical(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError("Canonical path must be a CSV or Parquet file")


def validate_population_totals(frame: pd.DataFrame) -> None:
    required = {
        "decision_method",
        "temporal_resolution_status",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "Canonical file is missing required columns: " + ", ".join(missing)
        )

    resolved = int(frame["temporal_resolution_status"].eq("resolved").sum())
    unresolved = int(frame["temporal_resolution_status"].eq("unresolved").sum())
    method_counts = frame["decision_method"].value_counts()

    observed = {
        "canonical_races": len(frame),
        "resolved_races": resolved,
        "unresolved_races": unresolved,
        "dead_of_night_races": int(
            method_counts.get("course_local_dead_of_night_rejection", 0)
        ),
        "stable_profile_races": int(
            method_counts.get("stable_post_boundary_course_profile", 0)
        ),
        "explicit_post_boundary_races": int(
            method_counts.get("explicit_post_boundary_time", 0)
        ),
    }

    for field, value in observed.items():
        expected = getattr(VALIDATED_TOTALS, field)
        if value != expected:
            raise AssertionError(
                f"Unexpected {field}: expected {expected}, found {value}."
            )


def main() -> None:
    args = parse_args()
    validate_clock_parsers()
    validate_dst_classification()
    validate_meeting_unwrap()
    validate_explicit_post_boundary()

    print("Race-time helper validation passed")
    print(f"Format boundary: {FORMAT_BOUNDARY.date()}")

    if args.canonical_path is not None:
        canonical = load_canonical(args.canonical_path)
        validate_population_totals(canonical)
        print("Canonical population totals passed")
        print(f"Canonical races: {len(canonical)}")


if __name__ == "__main__":
    main()
