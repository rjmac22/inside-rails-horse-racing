from __future__ import annotations

import math

import pytest

from inside_rails.race_distance import VALIDATED_COMPONENTS, parse_race_distance


def test_validated_distance_inventory_contains_expected_source_values() -> None:
    assert len(VALIDATED_COMPONENTS) == 63
    assert VALIDATED_COMPONENTS["4f"] == (0, 4, False)
    assert VALIDATED_COMPONENTS["1m"] == (1, 0, False)
    assert VALIDATED_COMPONENTS["4m4½f"] == (4, 4, True)


@pytest.mark.parametrize(
    ("raw_dist", "miles", "whole_furlongs", "has_half", "total_furlongs", "yards"),
    [
        ("4f", 0, 4, False, 4.0, 880),
        ("5½f", 0, 5, True, 5.5, 1_210),
        ("1m", 1, 0, False, 8.0, 1_760),
        ("1m2½f", 1, 2, True, 10.5, 2_310),
        ("4m4½f", 4, 4, True, 36.5, 8_030),
    ],
)
def test_parse_validated_distances(
    raw_dist: str,
    miles: int,
    whole_furlongs: int,
    has_half: bool,
    total_furlongs: float,
    yards: int,
) -> None:
    parsed = parse_race_distance(raw_dist)

    assert parsed["raw_dist"] == raw_dist
    assert parsed["miles"] == miles
    assert parsed["whole_furlongs"] == whole_furlongs
    assert parsed["has_half_furlong"] is has_half
    assert parsed["total_furlongs"] == total_furlongs
    assert parsed["source_implied_yards"] == yards
    assert math.isclose(parsed["source_implied_metres"], yards * 0.9144)
    assert parsed["official_distance_verified"] is False
    assert parsed["parse_status"] == "parsed"


@pytest.mark.parametrize("raw_dist", [None, "", "1600m", "1m 2f", "1M2F"])
def test_unseen_or_noncanonical_values_remain_unresolved(raw_dist: object) -> None:
    parsed = parse_race_distance(raw_dist)

    assert parsed["raw_dist"] == raw_dist
    assert parsed["miles"] is None
    assert parsed["whole_furlongs"] is None
    assert parsed["has_half_furlong"] is None
    assert parsed["total_furlongs"] is None
    assert parsed["source_implied_yards"] is None
    assert parsed["source_implied_metres"] is None
    assert parsed["official_distance_verified"] is False
    assert parsed["parse_status"] == "unresolved"


def test_all_validated_values_produce_exact_half_furlong_increments() -> None:
    for raw_dist in VALIDATED_COMPONENTS:
        parsed = parse_race_distance(raw_dist)
        doubled = parsed["total_furlongs"] * 2
        assert doubled == int(doubled)


def test_source_implied_metres_are_conversion_not_official_verification() -> None:
    parsed = parse_race_distance("1m")

    assert parsed["source_implied_metres"] == pytest.approx(1_609.344)
    assert parsed["official_distance_verified"] is False
