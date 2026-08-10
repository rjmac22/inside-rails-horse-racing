import pytest

from inside_rails.ratings import (
    INVALID_RPR_SOURCE_ROWID,
    RATING_MEANINGS,
    UNAVAILABLE_RATING_TOKEN,
    parse_rating,
    parse_rating_triplet,
)


def test_available_integer_is_preserved() -> None:
    result = parse_rating(87, "or", source_rowid=10)

    assert result["rating_raw"] == 87
    assert result["rating_value"] == 87
    assert result["rating_status"] == "available"
    assert result["rating_meaning"] == RATING_MEANINGS["or"]


def test_exact_integral_float_is_accepted_without_rounding() -> None:
    result = parse_rating(71.0, "rpr")

    assert result["rating_value"] == 71
    assert result["rating_status"] == "available"


def test_fractional_numeric_value_is_unresolved() -> None:
    result = parse_rating(71.5, "rpr")

    assert result["rating_value"] is None
    assert result["rating_status"] == "unresolved_source_value"


def test_boolean_is_not_treated_as_integer_rating() -> None:
    result = parse_rating(True, "ts")

    assert result["rating_value"] is None
    assert result["rating_status"] == "unresolved_source_value"


def test_en_dash_is_unavailable_not_zero() -> None:
    result = parse_rating(UNAVAILABLE_RATING_TOKEN, "or")

    assert result["rating_raw"] == UNAVAILABLE_RATING_TOKEN
    assert result["rating_value"] is None
    assert result["rating_status"] == "unavailable"


def test_ascii_hyphen_is_not_silently_normalised() -> None:
    result = parse_rating("-", "or")

    assert result["rating_value"] is None
    assert result["rating_status"] == "unresolved_source_value"


def test_numeric_text_is_not_silently_coerced() -> None:
    result = parse_rating("75", "rpr")

    assert result["rating_value"] is None
    assert result["rating_status"] == "unresolved_source_value"


def test_exact_invalid_rpr_is_excluded_by_lineage() -> None:
    result = parse_rating(
        775,
        "rpr",
        source_rowid=INVALID_RPR_SOURCE_ROWID,
    )

    assert result["rating_raw"] == 775
    assert result["rating_value"] is None
    assert result["rating_status"] == "invalid_source_value"
    assert result["replacement_status"] == "unresolved"


def test_same_numeric_value_elsewhere_is_not_globally_deleted() -> None:
    result = parse_rating(775, "rpr", source_rowid=999)

    assert result["rating_value"] == 775
    assert result["rating_status"] == "available"


def test_invalid_rule_does_not_apply_to_other_fields() -> None:
    result = parse_rating(
        775,
        "ts",
        source_rowid=INVALID_RPR_SOURCE_ROWID,
    )

    assert result["rating_value"] == 775
    assert result["rating_status"] == "available"


def test_triplet_preserves_independent_statuses() -> None:
    result = parse_rating_triplet(
        UNAVAILABLE_RATING_TOKEN,
        68,
        46,
        source_rowid=100,
    )

    assert result == {
        "raw_or": UNAVAILABLE_RATING_TOKEN,
        "or": None,
        "or_status": "unavailable",
        "raw_rpr": 68,
        "rpr": 68,
        "rpr_status": "available",
        "raw_ts": 46,
        "ts": 46,
        "ts_status": "available",
    }


def test_unsupported_field_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="Unsupported rating field"):
        parse_rating(75, "rating")  # type: ignore[arg-type]
