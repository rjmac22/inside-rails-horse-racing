from pathlib import Path

import pandas as pd
import pytest

from inside_rails.race_time_pipeline import (
    build_canonical_race_times,
    load_canonical_race_times,
    validate_timestamp_conversions,
    write_canonical_race_times,
)


def _race(
    date: str,
    course: str,
    off: str,
    race_id: int,
    *,
    timezone: str = "Europe/London",
) -> dict[str, object]:
    return {
        "date": date,
        "course": course,
        "off": off,
        "race_id": race_id,
        "race_name": f"Race {race_id}",
        "type": "Flat",
        "candidate_course_label": course,
        "candidate_jurisdiction": "Great Britain",
        "iana_timezone": timezone,
    }


def _synthetic_races() -> pd.DataFrame:
    rows = [
        # Candidate A is wholly dead-of-night; candidate B is selected.
        _race("2025-01-01", "Dead Course", "1:00", 1),
        _race("2025-01-01", "Dead Course", "2:00", 2),
        # Neither branch is dead-of-night. Five explicit meetings establish
        # a stable 19:00 local profile, selecting candidate B for this race.
        _race("2025-01-02", "Profile Course", "7:00", 3),
        # No explicit course profile and neither branch is rejected: unresolved.
        _race("2025-01-03", "Unresolved Course", "7:30", 4),
    ]
    rows.extend(
        _race(f"2025-10-{day:02d}", "Profile Course", "19:00", race_id)
        for day, race_id in zip(range(15, 20), range(5, 10), strict=True)
    )
    return pd.DataFrame(rows)


def test_pipeline_uses_dead_of_night_profile_and_explicit_methods() -> None:
    canonical = build_canonical_race_times(_synthetic_races())

    assert len(canonical) == 9
    assert canonical["temporal_resolution_status"].value_counts().to_dict() == {
        "resolved": 8,
        "unresolved": 1,
    }
    assert canonical["decision_method"].value_counts().to_dict() == {
        "explicit_post_boundary_time": 5,
        "course_local_dead_of_night_rejection": 2,
        "stable_post_boundary_course_profile": 1,
        "unresolved": 1,
    }

    dead = canonical.loc[canonical["course"].eq("Dead Course")]
    assert dead["selected_branch"].eq("candidate_b").all()
    assert dead["advertised_start_uk"].dt.hour.tolist() == [13, 14]

    profile = canonical.loc[
        canonical["date"].eq("2025-01-02")
        & canonical["course"].eq("Profile Course")
    ].iloc[0]
    assert profile["selected_branch"] == "candidate_b"
    assert profile["advertised_start_course_local"].hour == 19

    unresolved = canonical.loc[
        canonical["course"].eq("Unresolved Course")
    ].iloc[0]
    assert unresolved["temporal_resolution_status"] == "unresolved"
    assert pd.isna(unresolved["advertised_start_utc"])
    assert pd.notna(unresolved["candidate_a_uk_naive"])
    assert pd.notna(unresolved["candidate_b_uk_naive"])


def test_pipeline_csv_round_trip_preserves_timestamps(tmp_path: Path) -> None:
    canonical = build_canonical_race_times(_synthetic_races())
    path = tmp_path / "canonical_race_times.csv"

    write_canonical_race_times(path, canonical)
    reloaded = load_canonical_race_times(path)
    validate_timestamp_conversions(reloaded)

    assert reloaded[["date", "course", "off"]].equals(
        canonical[["date", "course", "off"]]
    )
    assert reloaded["decision_method"].fillna("unresolved").tolist() == (
        canonical["decision_method"].fillna("unresolved").tolist()
    )
    resolved = reloaded["temporal_resolution_status"].eq("resolved")
    assert reloaded.loc[resolved, "advertised_start_utc"].notna().all()


def test_duplicate_race_key_fails_before_construction() -> None:
    races = _synthetic_races()
    duplicate = pd.concat([races, races.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate race keys"):
        build_canonical_race_times(duplicate)


def test_missing_timezone_fails_before_construction() -> None:
    races = _synthetic_races()
    races.loc[0, "iana_timezone"] = pd.NA

    with pytest.raises(ValueError, match="governed IANA timezone"):
        build_canonical_race_times(races)
