#!/usr/bin/env python3
"""Diagnose resolved Notebook 11 rows that lack selected timestamps."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from inside_rails.course_locations import (
    load_course_locations,
    merge_source_course_locations,
)
from inside_rails.race_time_pipeline import (
    MINIMUM_PROFILE_MEETINGS,
    _empty_profile_decisions,
    _has_eligible_course_profile,
    _normalise_course_local_summary_timestamps,
)
from inside_rails.race_times import (
    FORMAT_BOUNDARY,
    attach_pre_boundary_timezones,
    build_post_boundary_course_profiles,
    build_post_boundary_times,
    combine_meeting_decisions,
    reconstruct_pre_boundary_candidates,
    select_pre_boundary_canonical_times,
    stable_course_profile_decisions,
    summarise_pre_boundary_meetings,
)
from inside_rails.source_sqlite import connect_read_only


DATABASE = Path("data/raw/form_2015-present/form_2015-present/raceform.db")
COURSE_LOCATIONS = Path("data/reference/course_locations.csv")
EXPECTED_RACES = 189_043
SELECTED_COLUMNS = (
    "advertised_start_uk",
    "advertised_start_utc",
    "advertised_start_course_local",
)


def load_source_races() -> pd.DataFrame:
    with connect_read_only(DATABASE) as connection:
        races = pd.read_sql_query(
            """
            SELECT DISTINCT date, course, off, race_id, race_name, type
            FROM data
            WHERE rowid <> 1
            ORDER BY date, course, off
            """,
            connection,
        )
    if len(races) != EXPECTED_RACES:
        raise AssertionError(
            f"expected {EXPECTED_RACES:,} races, found {len(races):,}"
        )
    return races


def main() -> None:
    source = load_source_races()
    locations = load_course_locations(COURSE_LOCATIONS)
    frame = merge_source_course_locations(
        source,
        locations,
        require_all_matches=True,
    )

    source_dates = pd.to_datetime(frame["date"], errors="raise")
    pre = frame.loc[source_dates.lt(FORMAT_BOUNDARY)].copy()
    post = frame.loc[source_dates.ge(FORMAT_BOUNDARY)].copy()

    pre_candidates = attach_pre_boundary_timezones(
        reconstruct_pre_boundary_candidates(pre)
    )
    summary_candidates = _normalise_course_local_summary_timestamps(
        pre_candidates
    )
    meeting_summary = summarise_pre_boundary_meetings(summary_candidates)

    post_times = build_post_boundary_times(post)
    course_profiles = build_post_boundary_course_profiles(post_times)
    if _has_eligible_course_profile(meeting_summary, course_profiles):
        profile_decisions = stable_course_profile_decisions(
            meeting_summary,
            course_profiles,
            minimum_observed_meetings=MINIMUM_PROFILE_MEETINGS,
        )
    else:
        profile_decisions = _empty_profile_decisions()

    meeting_decisions = combine_meeting_decisions(
        meeting_summary,
        profile_decisions,
    )
    pre_times = select_pre_boundary_canonical_times(
        pre_candidates,
        meeting_decisions,
    )
    pre_times["temporal_resolution_status"] = np.where(
        pre_times["selected_branch"].isin(["candidate_a", "candidate_b"]),
        "resolved",
        "unresolved",
    )
    post_times["temporal_resolution_status"] = "resolved"

    pre_missing = pre_times.loc[
        pre_times["temporal_resolution_status"].eq("resolved")
        & pre_times[list(SELECTED_COLUMNS)].isna().any(axis=1)
    ].copy()
    post_missing = post_times.loc[
        post_times["temporal_resolution_status"].eq("resolved")
        & post_times[list(SELECTED_COLUMNS)].isna().any(axis=1)
    ].copy()

    print("Race-time resolution diagnostic")
    print(f"  source races: {len(source):,}")
    print(f"  pre-boundary selected branches: {pre_times['selected_branch'].notna().sum():,}")
    print(f"  pre-boundary rows missing a selected timestamp: {len(pre_missing):,}")
    print(f"  post-boundary rows missing a selected timestamp: {len(post_missing):,}")

    if not pre_missing.empty:
        print("\nPre-boundary missing rows by method / branch / London status:")
        grouped = (
            pre_missing.groupby(
                [
                    "decision_method",
                    "selected_branch",
                    "candidate_a_london_status",
                    "candidate_b_london_status",
                ],
                dropna=False,
            )
            .size()
            .rename("rows")
            .reset_index()
        )
        print(grouped.to_string(index=False))

        print("\nAffected meetings:")
        meetings = (
            pre_missing.groupby(
                ["date", "course", "decision_method", "selected_branch"],
                dropna=False,
            )
            .size()
            .rename("rows")
            .reset_index()
        )
        print(meetings.to_string(index=False))

        print("\nSample affected races:")
        columns = [
            "date",
            "course",
            "off",
            "race_id",
            "selected_branch",
            "decision_method",
            "candidate_a_london_status",
            "candidate_b_london_status",
            "candidate_a_uk_naive",
            "candidate_b_uk_naive",
            "candidate_a_uk_aware",
            "candidate_b_uk_aware",
        ]
        print(pre_missing.loc[:, columns].head(50).to_string(index=False))

    if not post_missing.empty:
        print("\nPost-boundary missing rows:")
        columns = [
            "date",
            "course",
            "off",
            "race_id",
            "advertised_start_uk_naive",
            "advertised_start_uk",
        ]
        print(post_missing.loc[:, columns].head(50).to_string(index=False))


if __name__ == "__main__":
    main()
