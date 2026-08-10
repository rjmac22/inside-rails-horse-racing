from datetime import date, time

import pytest

from inside_rails.off_time import (
    OffTimeBranch,
    OffTimeKind,
    parse_off_time,
    reconstruct_advertised_time,
)


def test_ambiguous_single_digit_hour_generates_two_candidates() -> None:
    parsed = parse_off_time("4:45")
    assert parsed.kind == OffTimeKind.AMBIGUOUS_12H
    assert parsed.candidate_a == time(4, 45)
    assert parsed.candidate_b == time(16, 45)


def test_ambiguous_two_digit_hour_generates_two_candidates() -> None:
    parsed = parse_off_time("12:30")
    assert parsed.kind == OffTimeKind.AMBIGUOUS_12H
    assert parsed.candidate_a == time(12, 30)
    assert parsed.candidate_b == time(0, 30)


def test_midnight_and_afternoon_values_are_explicit_24_hour() -> None:
    assert parse_off_time("00:01").kind == OffTimeKind.EXPLICIT_24H
    assert parse_off_time("13:05").kind == OffTimeKind.EXPLICIT_24H
    assert parse_off_time("23:59").candidate_a == time(23, 59)


def test_invalid_clock_values_remain_unresolved() -> None:
    for raw in (None, 1405, "", "4.45", "04:5", "24:00", "12:60", " 4:45"):
        assert parse_off_time(raw).kind == OffTimeKind.UNRESOLVED


def test_ambiguous_value_requires_explicit_branch() -> None:
    with pytest.raises(ValueError, match="branch A or B"):
        reconstruct_advertised_time(
            date(2025, 3, 1),
            "6:01",
            OffTimeBranch.EXPLICIT_24H,
            "America/New_York",
        )


def test_explicit_value_requires_explicit_branch() -> None:
    with pytest.raises(ValueError, match="explicit_24h"):
        reconstruct_advertised_time(
            date(2026, 3, 3),
            "14:05",
            OffTimeBranch.A,
            "Europe/London",
        )


def test_branch_b_reconstructs_uk_utc_and_course_local_times() -> None:
    result = reconstruct_advertised_time(
        date(2025, 3, 1),
        "6:01",
        OffTimeBranch.B,
        "America/New_York",
    )
    assert result.advertised_start_uk.isoformat() == "2025-03-01T18:01:00+00:00"
    assert result.advertised_start_utc.isoformat() == "2025-03-01T18:01:00+00:00"
    assert result.advertised_start_course_local.isoformat() == "2025-03-01T13:01:00-05:00"


def test_timezone_conversion_can_change_course_local_date() -> None:
    result = reconstruct_advertised_time(
        date(2021, 4, 11),
        "5:30",
        OffTimeBranch.A,
        "Asia/Hong_Kong",
    )
    assert result.advertised_start_uk.isoformat() == "2021-04-11T05:30:00+01:00"
    assert result.advertised_start_utc.isoformat() == "2021-04-11T04:30:00+00:00"
    assert result.advertised_start_course_local.isoformat() == "2021-04-11T12:30:00+08:00"


def test_unknown_timezone_fails_instead_of_guessing() -> None:
    with pytest.raises(Exception):
        reconstruct_advertised_time(
            date(2025, 1, 1),
            "14:05",
            OffTimeBranch.EXPLICIT_24H,
            "Not/A_Timezone",
        )
