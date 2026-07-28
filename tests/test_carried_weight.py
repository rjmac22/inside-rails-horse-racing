from __future__ import annotations

import math

import pytest

from inside_rails.carried_weight import (
    POUND_TO_KILOGRAM,
    parse_carried_weight,
)


@pytest.mark.parametrize(
    ("raw_wgt", "stones", "pounds", "total_pounds"),
    [
        ("6-12", 6, 12, 96),
        ("9-0", 9, 0, 126),
        ("10-13", 10, 13, 153),
        ("12-11", 12, 11, 179),
        ("7-0", 7, 0, 98),
        ("13-0", 13, 0, 182),
    ],
)
def test_parse_canonical_stones_and_pounds(
    raw_wgt: str,
    stones: int,
    pounds: int,
    total_pounds: int,
) -> None:
    result = parse_carried_weight(raw_wgt)

    assert result["raw_wgt"] == raw_wgt
    assert result["notation_family"] == "stones_and_pounds"
    assert result["parsed_stones"] == stones
    assert result["parsed_pounds"] == pounds
    assert result["source_implied_total_pounds"] == total_pounds
    assert math.isclose(
        result["source_implied_kilograms"],
        total_pounds * POUND_TO_KILOGRAM,
    )
    assert result["parse_status"] == "parsed"
    assert result["ambiguity_flag"] is False
    assert result["anomaly_flags"] == ()
    assert result["official_weight_verified"] is False


def test_pounds_component_above_thirteen_is_unresolved() -> None:
    result = parse_carried_weight("9-14")

    assert result["notation_family"] == "integer_hyphen_integer"
    assert result["parsed_stones"] == 9
    assert result["parsed_pounds"] == 14
    assert result["source_implied_total_pounds"] is None
    assert result["parse_status"] == "unresolved_invalid_pounds_component"
    assert result["anomaly_flags"] == ("pounds_component_outside_0_to_13",)


@pytest.mark.parametrize(
    "raw_wgt",
    ["09-0", "9-00", " 9-0", "9-0 ", "9 - 0", "9/0", "126", "57kg", ""],
)
def test_unrecognised_text_is_preserved_and_unresolved(raw_wgt: str) -> None:
    result = parse_carried_weight(raw_wgt)

    assert result["raw_wgt"] == raw_wgt
    assert result["notation_family"] == "unrecognised_text"
    assert result["parse_status"] == "unresolved_unrecognised_notation"
    assert result["ambiguity_flag"] is True
    assert result["source_implied_total_pounds"] is None
    assert result["source_implied_kilograms"] is None


def test_missing_value_has_explicit_missing_status() -> None:
    result = parse_carried_weight(None)

    assert result["notation_family"] == "missing"
    assert result["parse_status"] == "unresolved_missing"
    assert result["anomaly_flags"] == ("missing_value",)


@pytest.mark.parametrize("raw_wgt", [126, 57.0])
def test_non_text_values_are_not_coerced(raw_wgt: object) -> None:
    result = parse_carried_weight(raw_wgt)

    assert result["notation_family"] == "non_text"
    assert result["parse_status"] == "unresolved_non_text"
    assert result["ambiguity_flag"] is True
    assert result["anomaly_flags"] == ("unexpected_storage_type",)


def test_metric_conversion_is_not_official_weight_verification() -> None:
    result = parse_carried_weight("9-0")

    assert result["source_implied_total_pounds"] == 126
    assert math.isclose(result["source_implied_kilograms"], 57.15263862)
    assert result["official_weight_verified"] is False
