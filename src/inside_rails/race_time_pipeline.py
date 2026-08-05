"""Build, persist and reload the governed Notebook 11 race-time output."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

from inside_rails.race_times import (
    FORMAT_BOUNDARY,
    RACE_KEY_COLUMNS,
    VALIDATED_TOTALS,
    attach_pre_boundary_timezones,
    build_post_boundary_course_profiles,
    build_post_boundary_times,
    combine_meeting_decisions,
    reconstruct_pre_boundary_candidates,
    select_pre_boundary_canonical_times,
    stable_course_profile_decisions,
    summarise_pre_boundary_meetings,
    validate_canonical_temporal_population,
)


REQUIRED_RACE_COLUMNS: Final[tuple[str, ...]] = (
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

CANDIDATE_TIMESTAMP_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_a_uk_naive",
    "candidate_b_uk_naive",
    "candidate_a_utc",
    "candidate_b_utc",
    "candidate_a_course_local",
    "candidate_b_course_local",
)

SELECTED_TIMESTAMP_COLUMNS: Final[tuple[str, ...]] = (
    "advertised_start_uk",
    "advertised_start_utc",
    "advertised_start_course_local",
)

CANONICAL_OUTPUT_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "course",
    "off",
    "race_id",
    "race_name",
    "type",
    "candidate_course_label",
    "candidate_jurisdiction",
    "iana_timezone",
    *CANDIDATE_TIMESTAMP_COLUMNS,
    *SELECTED_TIMESTAMP_COLUMNS,
    "selected_branch",
    "decision_method",
    "decision_confidence",
    "temporal_resolution_status",
)

EXPECTED_METHOD_COUNTS: Final[dict[str, int]] = {
    "course_local_dead_of_night_rejection": VALIDATED_TOTALS.dead_of_night_races,
    "stable_post_boundary_course_profile": VALIDATED_TOTALS.stable_profile_races,
    "explicit_post_boundary_time": VALIDATED_TOTALS.explicit_post_boundary_races,
    "unresolved": VALIDATED_TOTALS.unresolved_races,
}


def _require_columns(
    frame: pd.DataFrame,
    columns: tuple[str, ...],
    frame_name: str,
) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(
            f"{frame_name} is missing required columns: {', '.join(missing)}"
        )


def _assert_unique_race_keys(frame: pd.DataFrame, frame_name: str) -> None:
    duplicate_mask = frame.duplicated(list(RACE_KEY_COLUMNS), keep=False)
    if duplicate_mask.any():
        examples = (
            frame.loc[duplicate_mask, list(RACE_KEY_COLUMNS)]
            .drop_duplicates()
            .head(10)
            .to_dict("records")
        )
        raise ValueError(f"{frame_name} contains duplicate race keys: {examples}")


def _normalise_course_local_summary_timestamps(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a summary-only copy with comparable local wall-clock timestamps.

    Course-local timestamps are stored as an object series because the source
    spans many IANA timezones. A London DST gap can also place ``NaT`` beside a
    timezone-aware timestamp within one meeting. Pandas cannot apply grouped
    ``min``/``max`` directly to that mixed object representation. Meeting
    decisions need only the local calendar time, so this copy removes timezone
    information while preserving missing candidates. Canonical timestamps in
    the original frame remain timezone-aware and unchanged.
    """

    result = frame.copy()
    for column in (
        "candidate_a_course_local",
        "candidate_b_course_local",
    ):
        result[column] = pd.to_datetime(
            result[column].map(
                lambda value: (
                    pd.NaT
                    if value is None or pd.isna(value)
                    else pd.Timestamp(value).tz_localize(None)
                )
            ),
            errors="raise",
        )
    return result


def build_canonical_race_times(races_with_locations: pd.DataFrame) -> pd.DataFrame:
    """Build one governed temporal record per provisional race.

    The input must already contain the governed course identity and IANA
    timezone. Pre-boundary meetings are reconstructed through the two settled
    candidate branches. Post-boundary values are parsed as explicit 24-hour UK
    civil times. Unsupported pre-boundary meetings remain unresolved with both
    candidates preserved.
    """

    _require_columns(
        races_with_locations,
        REQUIRED_RACE_COLUMNS,
        "races_with_locations",
    )
    _assert_unique_race_keys(races_with_locations, "races_with_locations")

    frame = races_with_locations.copy()
    frame["date"] = frame["date"].astype(str)
    source_dates = pd.to_datetime(frame["date"], errors="raise")
    if frame["iana_timezone"].isna().any():
        raise ValueError("Every race requires a governed IANA timezone")

    pre_boundary = frame.loc[source_dates.lt(FORMAT_BOUNDARY)].copy()
    post_boundary = frame.loc[source_dates.ge(FORMAT_BOUNDARY)].copy()

    pre_candidates = reconstruct_pre_boundary_candidates(pre_boundary)
    pre_candidates = attach_pre_boundary_timezones(pre_candidates)
    summary_candidates = _normalise_course_local_summary_timestamps(pre_candidates)
    meeting_summary = summarise_pre_boundary_meetings(summary_candidates)

    post_times = build_post_boundary_times(post_boundary)
    course_profiles = build_post_boundary_course_profiles(post_times)
    profile_decisions = stable_course_profile_decisions(
        meeting_summary,
        course_profiles,
    )
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

    for column in CANDIDATE_TIMESTAMP_COLUMNS:
        if column not in post_times.columns:
            post_times[column] = pd.NaT

    canonical = pd.concat(
        [pre_times, post_times],
        ignore_index=True,
        sort=False,
    )
    canonical = canonical.loc[:, list(CANONICAL_OUTPUT_COLUMNS)]
    canonical = canonical.sort_values(list(RACE_KEY_COLUMNS)).reset_index(drop=True)

    checks = validate_canonical_temporal_population(canonical)
    failed = checks.loc[~checks["passed"], "check"].tolist()
    if failed:
        raise AssertionError(
            "canonical race-time construction failed integrity checks: "
            + "; ".join(failed)
        )
    return canonical


def validate_exact_temporal_totals(frame: pd.DataFrame) -> None:
    """Enforce the settled Notebook 11 population and method totals."""

    _require_columns(
        frame,
        (
            *RACE_KEY_COLUMNS,
            "decision_method",
            "temporal_resolution_status",
        ),
        "canonical race times",
    )
    _assert_unique_race_keys(frame, "canonical race times")

    observed_resolved = int(
        frame["temporal_resolution_status"].eq("resolved").sum()
    )
    observed_unresolved = int(
        frame["temporal_resolution_status"].eq("unresolved").sum()
    )
    observed_methods = {
        method: int(frame["decision_method"].eq(method).sum())
        for method in EXPECTED_METHOD_COUNTS
    }

    observed = {
        "canonical_races": len(frame),
        "resolved_races": observed_resolved,
        "unresolved_races": observed_unresolved,
    }
    expected = {
        "canonical_races": VALIDATED_TOTALS.canonical_races,
        "resolved_races": VALIDATED_TOTALS.resolved_races,
        "unresolved_races": VALIDATED_TOTALS.unresolved_races,
    }
    if observed != expected:
        raise AssertionError(
            f"unexpected canonical temporal totals: observed={observed}, "
            f"expected={expected}"
        )
    if observed_methods != EXPECTED_METHOD_COUNTS:
        raise AssertionError(
            f"unexpected temporal decision methods: observed={observed_methods}, "
            f"expected={EXPECTED_METHOD_COUNTS}"
        )
    if set(frame["decision_method"].dropna().unique()) != set(
        EXPECTED_METHOD_COUNTS
    ):
        raise AssertionError("canonical output contains an ungoverned decision method")


def _timestamp_to_iso(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).isoformat()


def serialise_canonical_race_times(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a stable CSV representation with ISO timestamp strings."""

    _require_columns(frame, CANONICAL_OUTPUT_COLUMNS, "canonical race times")
    output = frame.loc[:, list(CANONICAL_OUTPUT_COLUMNS)].copy()
    for column in (*CANDIDATE_TIMESTAMP_COLUMNS, *SELECTED_TIMESTAMP_COLUMNS):
        output[column] = output[column].map(_timestamp_to_iso)
    for column in ("selected_branch", "decision_method", "decision_confidence"):
        output[column] = output[column].fillna("").astype(str)
    return output


def write_canonical_race_times(path: str | Path, frame: pd.DataFrame) -> None:
    """Write the governed output atomically as UTF-8 CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    serialise_canonical_race_times(frame).to_csv(temporary, index=False)
    temporary.replace(output_path)


def _parse_naive_timestamp_series(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values.replace("", pd.NA), errors="raise")


def _parse_uk_timestamp_series(values: pd.Series) -> pd.Series:
    parsed_utc = pd.to_datetime(values.replace("", pd.NA), utc=True, errors="raise")
    return parsed_utc.dt.tz_convert("Europe/London")


def _parse_utc_timestamp_series(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values.replace("", pd.NA), utc=True, errors="raise")


def _parse_mixed_timezone_series(values: pd.Series) -> pd.Series:
    return values.map(lambda value: pd.NaT if value == "" else pd.Timestamp(value))


def load_canonical_race_times(path: str | Path) -> pd.DataFrame:
    """Load and reconstruct timestamp types from the persisted CSV."""

    csv_path = Path(path)
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    if tuple(frame.columns) != CANONICAL_OUTPUT_COLUMNS:
        raise ValueError(
            "canonical race-time columns changed: "
            f"{tuple(frame.columns)!r}"
        )

    for column in ("candidate_a_uk_naive", "candidate_b_uk_naive"):
        frame[column] = _parse_naive_timestamp_series(frame[column])
    for column in ("advertised_start_uk",):
        frame[column] = _parse_uk_timestamp_series(frame[column])
    for column in (
        "candidate_a_utc",
        "candidate_b_utc",
        "advertised_start_utc",
    ):
        frame[column] = _parse_utc_timestamp_series(frame[column])
    for column in (
        "candidate_a_course_local",
        "candidate_b_course_local",
        "advertised_start_course_local",
    ):
        frame[column] = _parse_mixed_timezone_series(frame[column])

    for column in ("selected_branch", "decision_method", "decision_confidence"):
        frame[column] = frame[column].replace("", pd.NA)

    checks = validate_canonical_temporal_population(frame)
    failed = checks.loc[~checks["passed"], "check"].tolist()
    if failed:
        raise AssertionError(
            "persisted canonical race times failed integrity checks: "
            + "; ".join(failed)
        )
    return frame


def validate_timestamp_conversions(frame: pd.DataFrame) -> None:
    """Verify every resolved UK and local timestamp against canonical UTC."""

    _require_columns(
        frame,
        (
            "iana_timezone",
            "advertised_start_uk",
            "advertised_start_utc",
            "advertised_start_course_local",
            "temporal_resolution_status",
        ),
        "canonical race times",
    )
    resolved = frame.loc[
        frame["temporal_resolution_status"].eq("resolved")
    ]
    for row in resolved.itertuples(index=False):
        expected_uk = row.advertised_start_utc.tz_convert("Europe/London")
        expected_local = row.advertised_start_utc.tz_convert(row.iana_timezone)
        if expected_uk.isoformat() != row.advertised_start_uk.isoformat():
            raise AssertionError(
                "advertised_start_uk does not reconcile with canonical UTC for "
                f"{row.date}/{row.course}/{row.off}"
            )
        if expected_local.isoformat() != row.advertised_start_course_local.isoformat():
            raise AssertionError(
                "course-local timestamp does not reconcile with canonical UTC for "
                f"{row.date}/{row.course}/{row.off}"
            )
