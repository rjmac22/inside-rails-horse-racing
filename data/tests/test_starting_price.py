from fractions import Fraction

from inside_rails.starting_price import StartingPriceKind, parse_starting_price


def test_fractional_price_parses_exactly() -> None:
    parsed = parse_starting_price("7/2")
    assert parsed.price_kind == StartingPriceKind.FRACTIONAL
    assert parsed.numerator == 7
    assert parsed.denominator == 2
    assert parsed.fractional_odds == Fraction(7, 2)
    assert parsed.decimal_odds == Fraction(9, 2)
    assert parsed.implied_probability == Fraction(2, 9)
    assert parsed.favourite_marker is None
    assert parsed.favourite_status is None


def test_evens_aliases_parse() -> None:
    for raw in ("EVS", "EVENS", "evs"):
        parsed = parse_starting_price(raw)
        assert parsed.price_kind == StartingPriceKind.EVENS
        assert parsed.decimal_odds == Fraction(2, 1)
        assert parsed.implied_probability == Fraction(1, 2)


def test_known_favourite_markers_are_preserved_separately() -> None:
    expected = {
        "7/2F": ("F", "favourite"),
        "4/1J": ("J", "joint_favourite"),
        "5/1C": ("C", "co_favourite"),
        "EVSF": ("F", "favourite"),
    }
    for raw, (marker, status) in expected.items():
        parsed = parse_starting_price(raw)
        assert parsed.price_kind in {
            StartingPriceKind.FRACTIONAL,
            StartingPriceKind.EVENS,
        }
        assert parsed.favourite_marker == marker
        assert parsed.favourite_status == status


def test_market_context_remains_unresolved() -> None:
    assert parse_starting_price("5/1").market_context_status == "unresolved"
    assert parse_starting_price("5/1C").market_context_status == "unresolved"


def test_missing_values_remain_missing() -> None:
    assert parse_starting_price(None).price_kind == StartingPriceKind.MISSING
    assert parse_starting_price("").price_kind == StartingPriceKind.MISSING
    assert parse_starting_price("   ").price_kind == StartingPriceKind.MISSING


def test_unfamiliar_text_is_preserved_as_unresolved() -> None:
    for raw in ("SP", "FAV", "2.50", "7-2", "7 / 2", "0/1", "1/0", "7/2X"):
        parsed = parse_starting_price(raw)
        assert parsed.price_kind == StartingPriceKind.UNRESOLVED
        assert parsed.raw_sp == raw
        assert parsed.decimal_odds is None


def test_non_text_values_are_unresolved() -> None:
    assert parse_starting_price(2.5).price_kind == StartingPriceKind.UNRESOLVED


def test_fraction_reduction_does_not_replace_raw_components() -> None:
    parsed = parse_starting_price("10/4")
    assert parsed.numerator == 10
    assert parsed.denominator == 4
    assert parsed.fractional_odds == Fraction(5, 2)
