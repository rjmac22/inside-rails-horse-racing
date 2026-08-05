#!/usr/bin/env python3
"""Build, write and reload the governed Notebook 11 race-time output."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from inside_rails.course_locations import (
    load_course_locations,
    merge_source_course_locations,
)
from inside_rails.race_time_pipeline import (
    build_canonical_race_times,
    load_canonical_race_times,
    serialise_canonical_race_times,
    validate_exact_temporal_totals,
    validate_timestamp_conversions,
    write_canonical_race_times,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_PROVISIONAL_RACES = 189_043
DEFAULT_DATABASE = Path(
    "data/raw/form_2015-present/form_2015-present/raceform.db"
)
DEFAULT_COURSE_LOCATIONS = Path("data/reference/course_locations.csv")
DEFAULT_OUTPUT = Path(
    "data/processed/race_times/canonical_race_times.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--course-locations",
        type=Path,
        default=DEFAULT_COURSE_LOCATIONS,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_source_races(database: Path) -> pd.DataFrame:
    """Load one exact source row per provisional race key."""

    if not database.exists():
        raise FileNotFoundError(database)
    with connect_read_only(database) as connection:
        races = pd.read_sql_query(
            """
            SELECT DISTINCT date, course, off, race_id, race_name, type
            FROM data
            WHERE rowid <> 1
            ORDER BY date, course, off
            """,
            connection,
        )

    if len(races) != EXPECTED_PROVISIONAL_RACES:
        raise AssertionError(
            "source race projection does not match the governed race population: "
            f"observed={len(races):,}, expected={EXPECTED_PROVISIONAL_RACES:,}"
        )
    duplicate_mask = races.duplicated(["date", "course", "off"], keep=False)
    if duplicate_mask.any():
        examples = (
            races.loc[duplicate_mask, ["date", "course", "off"]]
            .drop_duplicates()
            .head(10)
            .to_dict("records")
        )
        raise AssertionError(
            "source race projection contains non-constant race context: "
            f"{examples}"
        )
    return races


def validate_written_bytes(output: Path, canonical: pd.DataFrame) -> None:
    """Prove the written CSV is the exact serialised governed dataframe."""

    observed = pd.read_csv(output, dtype=str, keep_default_na=False)
    expected = serialise_canonical_race_times(canonical).fillna("").astype(str)
    if tuple(observed.columns) != tuple(expected.columns):
        raise AssertionError("persisted canonical columns changed during write")
    if not observed.equals(expected):
        differing = int((observed != expected).any(axis=1).sum())
        raise AssertionError(
            f"persisted canonical output differs from built output on {differing} rows"
        )


def main() -> None:
    args = parse_args()

    source_races = load_source_races(args.database)
    course_locations = load_course_locations(args.course_locations)
    races_with_locations = merge_source_course_locations(
        source_races,
        course_locations,
        require_all_matches=True,
    )
    if races_with_locations["iana_timezone"].isna().any():
        raise AssertionError("source course join left an unresolved timezone")

    canonical = build_canonical_race_times(races_with_locations)
    validate_exact_temporal_totals(canonical)
    validate_timestamp_conversions(canonical)

    write_canonical_race_times(args.output, canonical)
    validate_written_bytes(args.output, canonical)

    reloaded = load_canonical_race_times(args.output)
    validate_exact_temporal_totals(reloaded)
    validate_timestamp_conversions(reloaded)

    print("Notebook 11 race-time governance build passed.")
    print(f"  source races: {len(source_races):,}")
    print(f"  course-location matches: {len(races_with_locations):,}")
    print(
        "  resolved / unresolved: "
        f"{reloaded['temporal_resolution_status'].eq('resolved').sum():,} / "
        f"{reloaded['temporal_resolution_status'].eq('unresolved').sum():,}"
    )
    for method, count in reloaded["decision_method"].value_counts().items():
        print(f"  {method}: {count:,}")
    print(f"  wrote and reloaded: {args.output}")


if __name__ == "__main__":
    main()
