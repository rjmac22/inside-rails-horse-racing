"""Conservative starting-price parsing from Notebook 08."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import re


_FRACTIONAL = re.compile(r"^([1-9][0-9]*)/([1-9][0-9]*)$")
_EVEN_VALUES = {"EVS", "EVENS"}


class StartingPriceKind(StrEnum):
    FRACTIONAL = "fractional"
    EVENS = "evens"
    MISSING = "missing"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ParsedStartingPrice:
    raw_sp: object
    price_kind: StartingPriceKind
    numerator: int | None
    denominator: int | None
    fractional_odds: Fraction | None
    decimal_odds: Fraction | None
    implied_probability: Fraction | None
    market_context_status: str


def parse_starting_price(raw_sp: object) -> ParsedStartingPrice:
    """Parse exact source arithmetic without inferring market provenance."""

    if raw_sp is None:
        return ParsedStartingPrice(raw_sp, StartingPriceKind.MISSING, None, None, None, None, None, "unresolved")
    if not isinstance(raw_sp, str):
        return ParsedStartingPrice(raw_sp, StartingPriceKind.UNRESOLVED, None, None, None, None, None, "unresolved")

    text = raw_sp.strip()
    if text == "":
        return ParsedStartingPrice(raw_sp, StartingPriceKind.MISSING, None, None, None, None, None, "unresolved")

    upper = text.upper()
    if upper in _EVEN_VALUES:
        fraction = Fraction(1, 1)
        return ParsedStartingPrice(raw_sp, StartingPriceKind.EVENS, 1, 1, fraction, Fraction(2, 1), Fraction(1, 2), "unresolved")

    match = _FRACTIONAL.fullmatch(text)
    if match is None:
        return ParsedStartingPrice(raw_sp, StartingPriceKind.UNRESOLVED, None, None, None, None, None, "unresolved")

    numerator = int(match.group(1))
    denominator = int(match.group(2))
    fraction = Fraction(numerator, denominator)
    decimal = fraction + 1
    probability = Fraction(denominator, numerator + denominator)
    return ParsedStartingPrice(raw_sp, StartingPriceKind.FRACTIONAL, numerator, denominator, fraction, decimal, probability, "unresolved")
