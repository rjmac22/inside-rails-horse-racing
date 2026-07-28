from decimal import Decimal

from inside_rails.prize_money import parse_prize_money


def test_blank_is_preserved_as_null_not_zero() -> None:
    result = parse_prize_money("", "Great Britain")

    assert result["prize_interpretation_status"] == "blank"
    assert result["prize_canonical_minor_units"] is None
    assert result["prize_currency"] is None


def test_gb_numeric_value_becomes_exact_gbp_minor_units() -> None:
    result = parse_prize_money(1234.56, "Great Britain")

    assert result["prize_source_presented_amount"] == Decimal("1234.56")
    assert result["prize_canonical_minor_units"] == 123456
    assert result["prize_currency"] == "GBP"
    assert result["prize_interpretation_status"] == "canonical"
    assert result["prize_interpretation_method"] == "direct_gb_numeric_gbp"


def test_irish_euro_text_becomes_exact_eur_minor_units() -> None:
    result = parse_prize_money("€12,345.67", "Ireland")

    assert result["prize_source_presented_amount"] == Decimal("12345.67")
    assert result["prize_canonical_minor_units"] == 1234567
    assert result["prize_currency"] == "EUR"
    assert result["prize_interpretation_status"] == "canonical"
    assert result["prize_interpretation_method"] == "direct_ireland_euro_text"


def test_foreign_numeric_value_is_preserved_but_currency_unresolved() -> None:
    result = parse_prize_money(500000, "United States")

    assert result["prize_source_presented_amount"] == Decimal("500000")
    assert result["prize_canonical_minor_units"] is None
    assert result["prize_currency"] is None
    assert result["prize_interpretation_status"] == "currency_unresolved"
    assert result["prize_conversion_multiplier"] is None


def test_gb_text_is_not_silently_accepted_as_confirmed_numeric_storage() -> None:
    result = parse_prize_money("123.45", "Great Britain")

    assert result["prize_interpretation_status"] == "invalid"
    assert result["prize_canonical_minor_units"] is None


def test_sub_minor_unit_value_is_rejected() -> None:
    result = parse_prize_money(12.345, "Great Britain")

    assert result["prize_interpretation_status"] == "invalid"
    assert result["prize_canonical_minor_units"] is None


def test_negative_value_is_rejected() -> None:
    result = parse_prize_money(-1, "Great Britain")

    assert result["prize_interpretation_status"] == "invalid"
    assert result["prize_canonical_minor_units"] is None


def test_negative_foreign_value_is_invalid_not_currency_unresolved() -> None:
    result = parse_prize_money(-1, "United States")

    assert result["prize_source_presented_amount"] == Decimal("-1")
    assert result["prize_interpretation_status"] == "invalid"
    assert result["prize_canonical_minor_units"] is None


def test_boolean_is_not_treated_as_integer_money() -> None:
    result = parse_prize_money(True, "Great Britain")

    assert result["prize_interpretation_status"] == "invalid"
    assert result["prize_canonical_minor_units"] is None
