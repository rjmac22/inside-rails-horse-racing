"""Reconstruct canonical race times from UK-facing source clock values."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

FORMAT_BOUNDARY: Final[pd.Timestamp] = pd.Timestamp("2025-10-15")
LONDON_TIMEZONE: Final[str] = "Europe/London"
UTC_TIMEZONE: Final[str] = "UTC"
MEETING_KEY_COLUMNS: Final[tuple[str, str]] = ("date", "course")
RACE_KEY_COLUMNS: Final[tuple[str, str, str]] = ("date", "course", "off")
DEFAULT_PROFILE_MARGINS: Final[tuple[int, ...]] = (60, 90, 120, 180)
DEAD_OF_NIGHT_END_MINUTE: Final[int] = 5 * 60 + 59


@dataclass(frozen=True)
class TemporalTotals:
    """Expected population totals for the validated source snapshot."""

    canonical_races: int = 189_043
    resolved_races: int = 169_465
    unresolved_races: int = 19_578
    dead_of_night_races: int = 111_871
    stable_profile_races: int = 47_242
    explicit_post_boundary_races: int = 10_352


VALIDATED_TOTALS = TemporalTotals()


def require_columns(frame: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    """Raise when a required input column is absent."""

    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")


def parse_12_hour_minutes(value: object) -> int:
    """Parse a source 12-hour clock value into minutes on a 0-719 clock."""

    text = str(value).strip()
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid source clock value: {value!r}")

    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError as error:
        raise ValueError(f"Invalid source clock value: {value!r}") from error

    if not 1 <= hour <= 12 or not 0 <= minute <= 59:
        raise ValueError(f"Invalid 12-hour source clock value: {value!r}")

    return (hour % 12) * 60 + minute


def parse_24_hour_minutes(value: object) -> int:
    """Parse an explicit 24-hour clock value into minutes on a 0-1439 clock."""

    text = str(value).strip()
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid source clock value: {value!r}")

    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError as error:
        raise ValueError(f"Invalid source clock value: {value!r}") from error

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(f"Invalid 24-hour source clock value: {value!r}")

    return hour * 60 + minute


def classify_london_civil_time(value: object) -> str:
    """Classify a naive UK civil timestamp under historical London DST rules."""

    timestamp = pd.Timestamp(value)
    try:
        timestamp.tz_localize(
            LONDON_TIMEZONE,
            ambiguous="raise",
            nonexistent="raise",
        )
        return "valid"
    except ValueError as error:
        message = str(error).lower()
        if "nonexistent" in message:
            return "nonexistent_dst_time"
        if "ambiguous" in message or "cannot infer dst time" in message:
            return "ambiguous_dst_time"
        raise


def circular_meeting_start(values: Sequence[int], period: int = 720) -> int:
    """Return the first value after the largest gap on a circular clock."""

    distinct = sorted({int(value) for value in values})
    if not distinct:
        raise ValueError("At least one meeting clock value is required")
    if len(distinct) == 1:
        return distinct[0]

    gaps = []
    for index, current in enumerate(distinct):
        following = distinct[(index + 1) % len(distinct)]
        if index == len(distinct) - 1:
            following += period
        gaps.append((following - current, index))

    _, largest_gap_index = max(gaps)
    return distinct[(largest_gap_index + 1) % len(distinct)]


def reconstruct_pre_boundary_candidates(races: pd.DataFrame) -> pd.DataFrame:
    """Create two ordered UK civil-time candidates for pre-boundary races."""

    require_columns(races, (*MEETING_KEY_COLUMNS, "off"), "races")
    result = races.copy()
    result["raw_12h_minutes"] = result["off"].map(parse_12_hour_minutes)

    meeting_starts = (
        result.groupby(list(MEETING_KEY_COLUMNS), as_index=False, sort=False)
        .agg(
            meeting_start_12h_minutes=(
                "raw_12h_minutes",
                lambda values: circular_meeting_start(values.tolist()),
            )
        )
    )
    result = result.merge(
        meeting_starts,
        on=list(MEETING_KEY_COLUMNS),
        how="left",
        validate="many_to_one",
    )

    result["candidate_a_minutes_from_source_date"] = (
        result["meeting_start_12h_minutes"]
        + (
            result["raw_12h_minutes"]
            - result["meeting_start_12h_minutes"]
        )
        % 720
    )
    result["candidate_b_minutes_from_source_date"] = (
        result["candidate_a_minutes_from_source_date"] + 720
    )

    source_dates = pd.to_datetime(result["date"], errors="raise")
    result["candidate_a_uk_naive"] = source_dates + pd.to_timedelta(
        result["candidate_a_minutes_from_source_date"], unit="m"
    )
    result["candidate_b_uk_naive"] = source_dates + pd.to_timedelta(
        result["candidate_b_minutes_from_source_date"], unit="m"
    )
    return result


def _london_conversion_lookup(values: pd.Series) -> pd.DataFrame:
    """Convert each distinct naive London datetime once."""

    distinct = pd.Series(pd.unique(values.dropna()), name="uk_naive")
    lookup = pd.DataFrame({"uk_naive": distinct})
    lookup["london_status"] = lookup["uk_naive"].map(classify_london_civil_time)

    valid = lookup["london_status"].eq("valid")
    aware = pd.Series(
        pd.NaT,
        index=lookup.index,
        dtype=f"datetime64[ns, {LONDON_TIMEZONE}]",
    )
    aware.loc[valid] = pd.DatetimeIndex(lookup.loc[valid, "uk_naive"]).tz_localize(
        LONDON_TIMEZONE
    )
    lookup["uk_aware"] = aware
    lookup["utc"] = lookup["uk_aware"].dt.tz_convert(UTC_TIMEZONE)
    return lookup


def attach_pre_boundary_timezones(races: pd.DataFrame) -> pd.DataFrame:
    """Attach London status, UTC, and course-local values to both candidates."""

    require_columns(
        races,
        (
            "candidate_a_uk_naive",
            "candidate_b_uk_naive",
            "iana_timezone",
        ),
        "races",
    )
    result = races.copy()

    all_values = pd.concat(
        [result["candidate_a_uk_naive"], result["candidate_b_uk_naive"]],
        ignore_index=True,
    )
    lookup = _london_conversion_lookup(all_values)

    for branch in ("a", "b"):
        naive_column = f"candidate_{branch}_uk_naive"
        branch_lookup = lookup.rename(
            columns={
                "uk_naive": naive_column,
                "london_status": f"candidate_{branch}_london_status",
                "uk_aware": f"candidate_{branch}_uk_aware",
                "utc": f"candidate_{branch}_utc",
            }
        )
        result = result.merge(
            branch_lookup,
            on=naive_column,
            how="left",
            validate="many_to_one",
        )

        utc_column = f"candidate_{branch}_utc"
        local_column = f"candidate_{branch}_course_local"
        result[local_column] = pd.Series(
            [pd.NaT] * len(result), index=result.index, dtype="object"
        )
        valid_mask = result[utc_column].notna()
        result.loc[valid_mask, local_column] = [
            utc_value.tz_convert(timezone_name)
            for utc_value, timezone_name in zip(
                result.loc[valid_mask, utc_column],
                result.loc[valid_mask, "iana_timezone"],
                strict=True,
            )
        ]

    return result


def build_post_boundary_times(races: pd.DataFrame) -> pd.DataFrame:
    """Parse explicit post-boundary 24-hour UK values into canonical times."""

    require_columns(races, ("date", "off", "iana_timezone"), "races")
    result = races.copy()
    result["off_minutes"] = result["off"].map(parse_24_hour_minutes)
    result["advertised_start_uk_naive"] = pd.to_datetime(
        result["date"], errors="raise"
    ) + pd.to_timedelta(result["off_minutes"], unit="m")
    result["advertised_start_uk"] = result[
        "advertised_start_uk_naive"
    ].dt.tz_localize(
        LONDON_TIMEZONE,
        ambiguous="NaT",
        nonexistent="NaT",
    )
    result["advertised_start_utc"] = result["advertised_start_uk"].dt.tz_convert(
        UTC_TIMEZONE
    )
    result["advertised_start_course_local"] = [
        (
            utc_value.tz_convert(timezone_name)
            if pd.notna(utc_value)
            else pd.NaT
        )
        for utc_value, timezone_name in zip(
            result["advertised_start_utc"],
            result["iana_timezone"],
            strict=True,
        )
    ]
    result["selected_branch"] = "explicit_24h"
    result["decision_method"] = "explicit_post_boundary_time"
    result["decision_confidence"] = "source_explicit"
    return result


def summarise_pre_boundary_meetings(races: pd.DataFrame) -> pd.DataFrame:
    """Summarise candidate local windows and dead-of-night feasibility."""

    require_columns(
        races,
        (
            *MEETING_KEY_COLUMNS,
            "race_id",
            "candidate_course_label",
            "candidate_jurisdiction",
            "iana_timezone",
            "candidate_a_course_local",
            "candidate_b_course_local",
        ),
        "races",
    )
    working = races.copy()
    for branch in ("a", "b"):
        local_column = f"candidate_{branch}_course_local"
        minutes_column = f"candidate_{branch}_local_minutes"
        valid_column = f"candidate_{branch}_valid"
        overnight_column = f"candidate_{branch}_dead_of_night"
        working[minutes_column] = working[local_column].map(
            lambda value: value.hour * 60 + value.minute if pd.notna(value) else pd.NA
        )
        working[valid_column] = working[local_column].notna()
        working[overnight_column] = working[minutes_column].map(
            lambda value: (
                0 <= int(value) <= DEAD_OF_NIGHT_END_MINUTE
                if pd.notna(value)
                else False
            )
        )

    grouped = working.groupby(list(MEETING_KEY_COLUMNS), as_index=False, sort=False)
    summary = grouped.agg(
        candidate_course_label=("candidate_course_label", "first"),
        candidate_jurisdiction=("candidate_jurisdiction", "first"),
        iana_timezone=("iana_timezone", "first"),
        race_count=("race_id", "size"),
        candidate_a_valid_races=("candidate_a_valid", "sum"),
        candidate_b_valid_races=("candidate_b_valid", "sum"),
        candidate_a_local_start=("candidate_a_course_local", "min"),
        candidate_a_local_end=("candidate_a_course_local", "max"),
        candidate_b_local_start=("candidate_b_course_local", "min"),
        candidate_b_local_end=("candidate_b_course_local", "max"),
        candidate_a_dead_of_night_races=("candidate_a_dead_of_night", "sum"),
        candidate_b_dead_of_night_races=("candidate_b_dead_of_night", "sum"),
    )

    for branch in ("a", "b"):
        summary[f"candidate_{branch}_wholly_dead_of_night"] = (
            summary[f"candidate_{branch}_valid_races"].eq(summary["race_count"])
            & summary[f"candidate_{branch}_dead_of_night_races"].eq(
                summary["race_count"]
            )
        )

    a_dead = summary["candidate_a_wholly_dead_of_night"]
    b_dead = summary["candidate_b_wholly_dead_of_night"]
    has_withheld = (
        summary["candidate_a_valid_races"].lt(summary["race_count"])
        | summary["candidate_b_valid_races"].lt(summary["race_count"])
    )
    summary["preliminary_branch_result"] = np.select(
        [
            has_withheld,
            a_dead & ~b_dead,
            b_dead & ~a_dead,
            a_dead & b_dead,
        ],
        [
            "dst_edge_requires_review",
            "candidate_b_only_feasible",
            "candidate_a_only_feasible",
            "both_wholly_dead_of_night",
        ],
        default="both_not_wholly_dead_of_night",
    )
    return summary


def build_post_boundary_course_profiles(races: pd.DataFrame) -> pd.DataFrame:
    """Build observed course-local meeting windows from explicit source times."""

    require_columns(
        races,
        (
            *MEETING_KEY_COLUMNS,
            "race_id",
            "candidate_course_label",
            "candidate_jurisdiction",
            "iana_timezone",
            "advertised_start_course_local",
        ),
        "races",
    )
    working = races.copy()
    working["course_local_minutes"] = working[
        "advertised_start_course_local"
    ].map(lambda value: value.hour * 60 + value.minute)

    meetings = (
        working.groupby(
            [
                *MEETING_KEY_COLUMNS,
                "candidate_course_label",
                "candidate_jurisdiction",
                "iana_timezone",
            ],
            as_index=False,
            sort=False,
        )
        .agg(
            race_count=("race_id", "size"),
            local_start_minutes=("course_local_minutes", "min"),
            local_end_minutes=("course_local_minutes", "max"),
        )
    )

    return (
        meetings.groupby(
            [
                "candidate_course_label",
                "candidate_jurisdiction",
                "iana_timezone",
            ],
            as_index=False,
        )
        .agg(
            observed_meetings=("date", "size"),
            observed_races=("race_count", "sum"),
            earliest_observed_start=("local_start_minutes", "min"),
            latest_observed_start=("local_start_minutes", "max"),
            median_start=("local_start_minutes", "median"),
            earliest_observed_end=("local_end_minutes", "min"),
            latest_observed_end=("local_end_minutes", "max"),
            median_end=("local_end_minutes", "median"),
        )
    )


def stable_course_profile_decisions(
    meeting_summary: pd.DataFrame,
    course_profiles: pd.DataFrame,
    *,
    minimum_observed_meetings: int = 5,
    margins: Sequence[int] = DEFAULT_PROFILE_MARGINS,
) -> pd.DataFrame:
    """Return branch decisions stable across every supplied profile margin."""

    require_columns(
        meeting_summary,
        (
            *MEETING_KEY_COLUMNS,
            "candidate_course_label",
            "candidate_jurisdiction",
            "candidate_a_local_start",
            "candidate_a_local_end",
            "candidate_b_local_start",
            "candidate_b_local_end",
        ),
        "meeting_summary",
    )
    require_columns(
        course_profiles,
        (
            "candidate_course_label",
            "candidate_jurisdiction",
            "observed_meetings",
            "earliest_observed_start",
            "latest_observed_start",
            "earliest_observed_end",
            "latest_observed_end",
        ),
        "course_profiles",
    )
    if not margins:
        raise ValueError("At least one profile margin is required")

    frame = meeting_summary.merge(
        course_profiles,
        on=["candidate_course_label", "candidate_jurisdiction"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_profile"),
    )
    frame = frame.loc[frame["observed_meetings"].ge(minimum_observed_meetings)].copy()

    for branch in ("a", "b"):
        frame[f"candidate_{branch}_start_minutes"] = frame[
            f"candidate_{branch}_local_start"
        ].map(lambda value: value.hour * 60 + value.minute)
        frame[f"candidate_{branch}_end_minutes"] = frame[
            f"candidate_{branch}_local_end"
        ].map(lambda value: value.hour * 60 + value.minute)

    decision_columns = []
    for margin in margins:
        earliest_start = (frame["earliest_observed_start"] - margin).clip(lower=0)
        latest_start = (frame["latest_observed_start"] + margin).clip(upper=1439)
        earliest_end = (frame["earliest_observed_end"] - margin).clip(lower=0)
        latest_end = (frame["latest_observed_end"] + margin).clip(upper=1439)

        compatible = {}
        for branch in ("a", "b"):
            compatible[branch] = frame[f"candidate_{branch}_start_minutes"].between(
                earliest_start, latest_start
            ) & frame[f"candidate_{branch}_end_minutes"].between(
                earliest_end, latest_end
            )

        decision_column = f"decision_{margin}"
        frame[decision_column] = np.select(
            [
                compatible["a"] & ~compatible["b"],
                compatible["b"] & ~compatible["a"],
                compatible["a"] & compatible["b"],
            ],
            ["candidate_a", "candidate_b", "both"],
            default="neither",
        )
        decision_columns.append(decision_column)

    frame["stable_profile_decision"] = frame[decision_columns].apply(
        lambda row: (
            row.iloc[0]
            if row.nunique() == 1 and row.iloc[0] in {"candidate_a", "candidate_b"}
            else "not_stable"
        ),
        axis=1,
    )
    return frame


def combine_meeting_decisions(
    meeting_summary: pd.DataFrame,
    profile_decisions: pd.DataFrame,
) -> pd.DataFrame:
    """Apply dead-of-night decisions before stable course-profile evidence."""

    require_columns(
        meeting_summary,
        (*MEETING_KEY_COLUMNS, "preliminary_branch_result", "race_count"),
        "meeting_summary",
    )
    require_columns(
        profile_decisions,
        (*MEETING_KEY_COLUMNS, "stable_profile_decision"),
        "profile_decisions",
    )
    result = meeting_summary.copy()
    result["selected_branch"] = pd.NA
    result["decision_method"] = "unresolved"
    result["decision_confidence"] = "unresolved"

    mappings = {
        "candidate_a_only_feasible": "candidate_a",
        "candidate_b_only_feasible": "candidate_b",
    }
    for preliminary_result, branch in mappings.items():
        mask = result["preliminary_branch_result"].eq(preliminary_result)
        result.loc[mask, "selected_branch"] = branch
        result.loc[mask, "decision_method"] = (
            "course_local_dead_of_night_rejection"
        )
        result.loc[mask, "decision_confidence"] = "high"

    stable = profile_decisions.loc[
        profile_decisions["stable_profile_decision"].isin(
            ["candidate_a", "candidate_b"]
        ),
        [*MEETING_KEY_COLUMNS, "stable_profile_decision"],
    ].rename(columns={"stable_profile_decision": "profile_selected_branch"})
    result = result.merge(
        stable,
        on=list(MEETING_KEY_COLUMNS),
        how="left",
        validate="one_to_one",
    )
    profile_mask = result["selected_branch"].isna() & result[
        "profile_selected_branch"
    ].notna()
    result.loc[profile_mask, "selected_branch"] = result.loc[
        profile_mask, "profile_selected_branch"
    ]
    result.loc[profile_mask, "decision_method"] = (
        "stable_post_boundary_course_profile"
    )
    result.loc[profile_mask, "decision_confidence"] = "supported"
    return result


def select_pre_boundary_canonical_times(
    races: pd.DataFrame,
    meeting_decisions: pd.DataFrame,
) -> pd.DataFrame:
    """Attach decisions and populate selected canonical timestamps."""

    require_columns(
        races,
        (
            *MEETING_KEY_COLUMNS,
            "candidate_a_uk_aware",
            "candidate_a_utc",
            "candidate_a_course_local",
            "candidate_b_uk_aware",
            "candidate_b_utc",
            "candidate_b_course_local",
        ),
        "races",
    )
    require_columns(
        meeting_decisions,
        (
            *MEETING_KEY_COLUMNS,
            "selected_branch",
            "decision_method",
            "decision_confidence",
        ),
        "meeting_decisions",
    )
    result = races.merge(
        meeting_decisions[
            [
                *MEETING_KEY_COLUMNS,
                "selected_branch",
                "decision_method",
                "decision_confidence",
            ]
        ],
        on=list(MEETING_KEY_COLUMNS),
        how="left",
        validate="many_to_one",
    )
    a_mask = result["selected_branch"].eq("candidate_a")
    b_mask = result["selected_branch"].eq("candidate_b")

    result["advertised_start_uk"] = result["candidate_a_uk_aware"].where(
        a_mask, result["candidate_b_uk_aware"].where(b_mask)
    )
    result["advertised_start_utc"] = result["candidate_a_utc"].where(
        a_mask, result["candidate_b_utc"].where(b_mask)
    )

    selected_local = pd.Series([pd.NaT] * len(result), index=result.index, dtype="object")
    selected_local.loc[a_mask] = result.loc[
        a_mask, "candidate_a_course_local"
    ].to_numpy(dtype="object")
    selected_local.loc[b_mask] = result.loc[
        b_mask, "candidate_b_course_local"
    ].to_numpy(dtype="object")
    result["advertised_start_course_local"] = selected_local
    return result


def validate_canonical_temporal_population(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the canonical race-time integrity checks and pass states."""

    require_columns(
        frame,
        (
            *RACE_KEY_COLUMNS,
            "date",
            "decision_method",
            "advertised_start_uk",
            "advertised_start_utc",
            "advertised_start_course_local",
            "candidate_a_uk_naive",
            "candidate_b_uk_naive",
            "temporal_resolution_status",
        ),
        "frame",
    )
    resolved = frame["temporal_resolution_status"].eq("resolved")
    unresolved = frame["temporal_resolution_status"].eq("unresolved")
    pre_boundary = pd.to_datetime(frame["date"]).lt(FORMAT_BOUNDARY)
    post_boundary = ~pre_boundary

    checks = {
        "one row per candidate race key": ~frame[list(RACE_KEY_COLUMNS)].duplicated().any(),
        "resolved races have selected UK timestamp": frame.loc[
            resolved, "advertised_start_uk"
        ].notna().all(),
        "resolved races have selected UTC timestamp": frame.loc[
            resolved, "advertised_start_utc"
        ].notna().all(),
        "resolved races have selected course-local timestamp": frame.loc[
            resolved, "advertised_start_course_local"
        ].notna().all(),
        "unresolved races have no selected UK timestamp": frame.loc[
            unresolved, "advertised_start_uk"
        ].isna().all(),
        "unresolved races have no selected UTC timestamp": frame.loc[
            unresolved, "advertised_start_utc"
        ].isna().all(),
        "unresolved races have no selected course-local timestamp": frame.loc[
            unresolved, "advertised_start_course_local"
        ].isna().all(),
        "unresolved pre-boundary races retain candidate A": frame.loc[
            unresolved & pre_boundary, "candidate_a_uk_naive"
        ].notna().all(),
        "unresolved pre-boundary races retain candidate B": frame.loc[
            unresolved & pre_boundary, "candidate_b_uk_naive"
        ].notna().all(),
        "post-boundary races are all resolved": frame.loc[
            post_boundary, "temporal_resolution_status"
        ].eq("resolved").all(),
        "post-boundary races use explicit 24h method": frame.loc[
            post_boundary, "decision_method"
        ].eq("explicit_post_boundary_time").all(),
    }
    return pd.DataFrame(
        {"check": list(checks), "passed": [bool(value) for value in checks.values()]}
    )
