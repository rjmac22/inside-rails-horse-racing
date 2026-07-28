"""Conservative starting-price parsing from Notebook 08."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import re


_FRACTIONAL = re.compile(r"^([1-9][0-9]*)/([1-9][0-9]*)([FJ])?$")
_EVENS = re.compile(r"^(EVS|EVENS)([FJ])?$", re.IGNORECASE)


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
    favourite_marker: str | None
    market_context_status: str


def _result(
    raw_sp: object,
    price_kind: StartingPriceKind,
    numerator: int | None = None,
    denominator: int | None = None,
    fractional_odds: Fraction | None = None,
    decimal_odds: Fraction | None = None,
    implied_probability: Fraction | None = None,
    favourite_marker: str | None = None,
) -> ParsedStartingPrice:
    return ParsedStartingPrice(
        raw_sp,
        price_kind,
        numerator,
        denominator,
        fractional_odds,
        decimal_odds,
        implied_probability,
        favourite_marker,
        "unresolved",
    )


def parse_starting_price(raw_sp: object) -> ParsedStartingPrice:
    """Parse exact source arithmetic without inferring market provenance.

    Terminal ``F`` and ``J`` annotations are preserved separately from the odds
    arithmetic. They are source favourite markers, not evidence of bookmaker or
    pool provenance.
    """

    if raw_sp is None:
        return _result(raw_sp, StartingPriceKind.MISSING)
    if not isinstance(raw_sp, str):
        return _result(raw_sp, StartingPriceKind.UNRESOLVED)

    text = raw_sp.strip()
    if text == "":
        return _result(raw_sp, StartingPriceKind.MISSING)

    evens_match = _EVENS.fullmatch(text)
    if evens_match is not None:
        fraction = Fraction(1, 1)
        marker = evens_match.group(2)
        return _result(
            raw_sp,
            StartingPriceKind.EVENS,
            1,
            1,
            fraction,
            Fraction(2, 1),
            Fraction(1, 2),
            marker.upper() if marker else None,
        )

    match = _FRACTIONAL.fullmatch(text.upper())
    if match is None:
        return _result(raw_sp, StartingPriceKind.UNRESOLVED)

    numerator = int(match.group(1))
    denominator = int(match.group(2))
    marker = match.group(3)
    fraction = Fraction(numerator, denominator)
    decimal = fraction + 1
    probability = Fraction(denominator, numerator + denominator)
    return _result(
        raw_sp,
        StartingPriceKind.FRACTIONAL,
        numerator,
        denominator,
        fraction,
        decimal,
        probability,
        marker,
    )
