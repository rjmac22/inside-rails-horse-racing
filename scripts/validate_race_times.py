#!/usr/bin/env python3
"""Independently validate the persisted Notebook 11 race-time output."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from inside_rails.course_locations import (
    load_course_locations,
    merge_source_course_locations,
)
from inside_rails.race_time_pipeline import (
    CANDIDATE_TIMESTAMP_COLUMNS,
    load_canonical_race_times,
    validate_exact_temporal_totals,
    validate_timestamp_conversions,
)
from inside_rails.race_times import FORMAT_BOUNDARY
from inside_rails.source_sqlite import connect_read_only


EXPECTED_PROVISIONAL_RACES = 189_043
EXPECTED_PRE_BOUNDARY_RACES = 178_691
EXPECTED_POST_BOUNDARY_RACES = 10_352
DEFAULT_DATABASE = Path(
    "data/raw/form_2015-present/form_2015-present/raceform.db"
)
DEFAULT_COURSE_LOCATIONS = Path("data/reference/course_locations.csv")
DEFAULT_CANONICAL = Path(
    "data/processed/race_times/canonical_race_times.csv"
)
SOURCE_COMPARISON_COLUMNS = (
    "date",
    "course",
    "off",
    "race_id",
    "race_name",
    "type",
    "candidate_course_label",
    "candidate_jurisdiction",
    "iana_timezone",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--course-locations",
        type=Path,
        default=DEFAULT_COURSE_LOCATIONS,
    )
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    return parser.parse_args()


def load_governed_source_races(
    database: Path,
    course_locations_path: Path,
) -> pd.DataFrame:
    if not database.exists():
        raise FileNotFoundError(database)
    with connect_read_only(database) as connection:
        source = pd.read_sql_query(
            """
            SELECT DISTINCT date, course, off, race_id, race_name, type
            FROM data
            WHERE rowid <> 1
            ORDER BY date, course, off
            """,
            connection,
        )
    if len(source) != EXPECTED_PROVISIONAL_RACES:
        raise AssertionError(
            f"expected {EXPECTED_PROVISIONAL_RACES:,} source races, "
            f"found {len(source):,}"
        )
    if source.duplicated(["date", "course", "off"]).any():
        raise AssertionError("source race context is not constant within race keys")

    course_locations = load_course_locations(course_locations_path)
    merged = merge_source_course_locations(
        source,
        course_locations,
        require_all_matches=True,
    )
    if merged["iana_timezone"].isna().any():
        raise AssertionError("governed source race has no IANA timezone")
    return merged


def validate_source_reconciliation(
    canonical: pd.DataFrame,
    source: pd.DataFrame,
) -> None:
    canonical_comparison = canonical.loc[:, list(SOURCE_COMPARISON_COLUMNS)].copy()
    source_comparison = source.loc[:, list(SOURCE_COMPARISON_COLUMNS)].copy()

    for frame in (canonical_comparison, source_comparison):
        for column in SOURCE_COMPARISON_COLUMNS:
            frame[column] = frame[column].fillna("").astype(str)
        frame.sort_values(["date", "course", "off"], inplace=True)
        frame.reset_index(drop=True, inplace=True)

    if not canonical_comparison.equals(source_comparison):
        differing = int((canonical_comparison != source_comparison).any(axis=1).sum())
        raise AssertionError(
            f"canonical output differs from governed source context on {differing} races"
        )


def validate_regime_contract(canonical: pd.DataFrame) -> None:
    dates = pd.to_datetime(canonical["date"], errors="raise")
    pre = dates.lt(FORMAT_BOUNDARY)
    post = dates.ge(FORMAT_BOUNDARY)

    if int(pre.sum()) != EXPECTED_PRE_BOUNDARY_RACES:
        raise AssertionError("pre-boundary population changed")
    if int(post.sum()) != EXPECTED_POST_BOUNDARY_RACES:
        raise AssertionError("post-boundary population changed")

    if not canonical.loc[post, "temporal_resolution_status"].eq("resolved").all():
        raise AssertionError("every post-boundary race must remain resolved")
    if not canonical.loc[post, "decision_method"].eq(
        "explicit_post_boundary_time"
    ).all():
        raise AssertionError("post-boundary races must use the explicit 24-hour method")
    if canonical.loc[post, list(CANDIDATE_TIMESTAMP_COLUMNS)].notna().any().any():
        raise AssertionError("post-boundary races must not carry reconstructed candidates")

    if canonical.loc[pre, "candidate_a_uk_naive"].isna().any():
        raise AssertionError("every pre-boundary race must preserve candidate A")
    if canonical.loc[pre, "candidate_b_uk_naive"].isna().any():
        raise AssertionError("every pre-boundary race must preserve candidate B")

    unresolved = canonical["temporal_resolution_status"].eq("unresolved")
    if not unresolved.loc[pre].equals(
        canonical.loc[pre, "decision_method"].eq("unresolved")
    ):
        raise AssertionError(
            "pre-boundary unresolved status and decision method must agree exactly"
        )
    if canonical.loc[unresolved, "selected_branch"].notna().any():
        raise AssertionError("unresolved races must not select a candidate branch")

    resolved_pre = pre & canonical["temporal_resolution_status"].eq("resolved")
    if not canonical.loc[resolved_pre, "selected_branch"].isin(
        ["candidate_a", "candidate_b"]
    ).all():
        raise AssertionError("resolved pre-boundary races require candidate A or B")


def main() -> None:
    args = parse_args()
    if not args.canonical.exists():
        raise FileNotFoundError(
            f"canonical race-time output not found: {args.canonical}; "
            "run scripts/build_race_time_governance.py first"
        )

    canonical = load_canonical_race_times(args.canonical)
    validate_exact_temporal_totals(canonical)
    validate_timestamp_conversions(canonical)
    validate_regime_contract(canonical)

    source = load_governed_source_races(args.database, args.course_locations)
    validate_source_reconciliation(canonical, source)

    print("Race-time source-wide validation passed.")
    print(f"  canonical races: {len(canonical):,}")
    print(f"  pre-boundary races: {EXPECTED_PRE_BOUNDARY_RACES:,}")
    print(f"  explicit post-boundary races: {EXPECTED_POST_BOUNDARY_RACES:,}")
    print(
        "  resolved / unresolved: "
        f"{canonical['temporal_resolution_status'].eq('resolved').sum():,} / "
        f"{canonical['temporal_resolution_status'].eq('unresolved').sum():,}"
    )
    for method, count in canonical["decision_method"].value_counts().items():
        print(f"  {method}: {count:,}")
    print("  exact source race and timezone reconciliation: PASS")
    print("  resolved UTC / UK / course-local conversion agreement: PASS")


if __name__ == "__main__":
    main()
