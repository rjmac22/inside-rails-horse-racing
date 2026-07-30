from __future__ import annotations

import pytest

from inside_rails.beaten_distance import (
    classify_beaten_distance_row,
    parse_beaten_distance,
)


@pytest.mark.parametrize("raw_value", [0, 0.0, 1, 2.5, 186])
def test_numeric_values_are_parsed_without_changing_raw_value(raw_value: object) -> None:
    parsed = parse_beaten_distance(raw_value)

    assert parsed["raw_value"] == raw_value
    assert parsed["numeric_value"] == float(raw_value)
    assert parsed["availability_status"] == "available"
    assert parsed["parse_status"] == "parsed"


def test_dash_sentinel_is_unavailable_not_zero() -> None:
    parsed = parse_beaten_distance("-")

    assert parsed["raw_value"] == "-"
    assert parsed["numeric_value"] is None
    assert parsed["availability_status"] == "unavailable"
    assert parsed["parse_status"] == "sentinel"


@pytest.mark.parametrize("raw_value", [None, "", "nk", "0", True])
def test_unvalidated_values_remain_unresolved(raw_value: object) -> None:
    parsed = parse_beaten_distance(raw_value)

    assert parsed["raw_value"] == raw_value
    assert parsed["numeric_value"] is None
    assert parsed["availability_status"] == "unresolved"
    assert parsed["parse_status"] == "unresolved"


def test_positive_distance_official_winner_is_flagged_not_corrected() -> None:
    classified = classify_beaten_distance_row(
        raw_pos=1,
        raw_ovr_btn=2.5,
        raw_btn=0,
    )

    assert classified["raw_ovr_btn"] == 2.5
    assert classified["numeric_ovr_btn"] == 2.5
    assert classified["positive_official_winner_distance"] is True
    assert classified["requires_review"] is True


def test_later_zero_overall_distance_is_flagged() -> None:
    classified = classify_beaten_distance_row(
        raw_pos=2,
        raw_ovr_btn=0,
        raw_btn=0,
    )

    assert classified["later_position_zero_overall"] is True
    assert classified["requires_review"] is True


def test_zero_increment_with_positive_overall_marks_same_distance_group_only() -> None:
    classified = classify_beaten_distance_row(
        raw_pos=3,
        raw_ovr_btn=4.5,
        raw_btn=0,
    )

    assert classified["same_distance_group"] is True
    assert classified["requires_review"] is False


def test_text_outcome_and_dash_distances_remain_unavailable() -> None:
    classified = classify_beaten_distance_row(
        raw_pos="PU",
        raw_ovr_btn="-",
        raw_btn="-",
    )

    assert classified["numeric_pos"] is None
    assert classified["numeric_ovr_btn"] is None
    assert classified["numeric_btn"] is None
    assert classified["ovr_btn_status"] == "unavailable"
    assert classified["btn_status"] == "unavailable"
    assert classified["requires_review"] is False
