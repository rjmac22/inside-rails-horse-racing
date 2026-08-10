from __future__ import annotations

from inside_rails.beaten_distance import classify_beaten_distance_row
from inside_rails.carried_weight import parse_carried_weight
from inside_rails.comment_information import classify_comment
from inside_rails.prize_money import parse_prize_money
from inside_rails.race_results import parse_result
from inside_rails.ratings import parse_rating_triplet
from inside_rails.runner_characteristics import (
    normalise_runner_age,
    normalise_runner_sex,
    parse_runner_headgear,
)
from inside_rails.runner_entries import parse_runner_number
from inside_rails.starting_price import parse_starting_price


def test_database_v2_population_uses_current_carried_weight_result_keys() -> None:
    result = parse_carried_weight("9-7")
    for key in (
        "notation_family",
        "parsed_stones",
        "parsed_pounds",
        "source_implied_total_pounds",
        "source_implied_kilograms",
        "parse_status",
        "ambiguity_flag",
        "anomaly_flags",
        "official_weight_verified",
    ):
        assert key in result


def test_database_v2_population_uses_current_prize_result_keys() -> None:
    result = parse_prize_money("1000", "GB")
    for key in (
        "prize_source_presented_amount",
        "prize_canonical_minor_units",
        "prize_currency",
        "prize_interpretation_status",
        "prize_interpretation_method",
        "prize_conversion_multiplier",
        "prize_confidence",
    ):
        assert key in result


def test_database_v2_population_uses_current_runner_number_result_keys() -> None:
    result = parse_runner_number(7, within_race_multiplicity=1)
    for key in (
        "source_num_storage_class",
        "source_positive_runner_number",
        "source_num_state",
        "source_num_within_race_multiplicity",
        "source_num_uniqueness_status",
    ):
        assert key in result


def test_database_v2_population_uses_current_beaten_distance_result_keys() -> None:
    result = classify_beaten_distance_row(raw_pos=2, raw_ovr_btn=1.5, raw_btn=1.5)
    for key in (
        "numeric_ovr_btn",
        "ovr_btn_status",
        "numeric_btn",
        "btn_status",
        "positive_official_winner_distance",
        "later_position_zero_overall",
        "same_distance_group",
        "requires_review",
    ):
        assert key in result


def test_database_v2_population_uses_current_runner_characteristic_result_keys() -> None:
    age = normalise_runner_age(4)
    assert "normalised_age" in age
    assert "interpretation_status" in age

    sex = normalise_runner_sex("G", verification_id="NB17-SEX-0001")
    assert "normalised_sex" in sex
    assert "interpretation_status" in sex
    assert "verification_id" in sex

    headgear = parse_runner_headgear("b1")
    for key in (
        "raw_components",
        "normalised_components",
        "component_count",
        "use_suffix",
        "source_declared_first_time",
        "interpretation_status",
    ):
        assert key in headgear


def test_database_v2_population_uses_current_rating_triplet_keys() -> None:
    ratings = parse_rating_triplet(100, 110, 90, source_rowid=2)
    for key in ("or", "or_status", "rpr", "rpr_status", "ts", "ts_status"):
        assert key in ratings


def test_database_v2_population_uses_current_result_starting_price_and_comment_interfaces() -> None:
    result = parse_result(1)
    assert result.result_kind.value == "finish_position"
    assert result.finish_position == 1
    assert result.outcome_code is None

    starting_price = parse_starting_price("5/2F")
    for attribute in (
        "price_kind",
        "numerator",
        "denominator",
        "fractional_odds",
        "decimal_odds",
        "implied_probability",
        "favourite_marker",
        "favourite_status",
        "market_context_status",
    ):
        assert hasattr(starting_price, attribute)

    comment = classify_comment("Led, headed final furlong")
    assert hasattr(comment, "comment_state")
    assert hasattr(comment, "substantive_text")
