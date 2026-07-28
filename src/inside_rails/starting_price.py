"""Conservative starting-price parsing from Notebook 08."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import re


_FRACTIONAL = re.compile(r"^([1-9][0-9]*)/([1-9][0-9]*)([FJC])?$")
_EVEN = re.compile(r"^(EVS|EVENS)([FJC])?$", re.IGNORECASE)
_MARKER_MEANINGS = {
    "F": "favourite",
    "J": "joint_favourite",
    "C": "co_favourite",
}


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
    favourite_status: str | None
    market_context_status: str


def _unresolved(raw_sp: object) -> ParsedStartingPrice:
    return ParsedStartingPrice(
        raw_sp,
        StartingPriceKind.UNRESOLVED,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "unresolved",
    )


def _missing(raw_sp: object) -> ParsedStartingPrice:
    return ParsedStartingPrice(
        raw_sp,
        StartingPriceKind.MISSING,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "unresolved",
    )


def parse_starting_price(raw_sp: object) -> ParsedStartingPrice:
    """Parse exact source arithmetic without inferring market provenance."""

    if raw_sp is None:
        return _missing(raw_sp)
    if not isinstance(raw_sp, str):
        return _unresolved(raw_sp)

    text = raw_sp.strip()
    if text == "":
        return _missing(raw_sp)

    even_match = _EVEN.fullmatch(text)
    if even_match is not None:
        marker = even_match.group(2)
        marker = marker.upper() if marker else None
        fraction = Fraction(1, 1)
        return ParsedStartingPrice(
            raw_sp,
            StartingPriceKind.EVENS,
            1,
            1,
            fraction,
            Fraction(2, 1),
            Fraction(1, 2),
            marker,
            _MARKER_MEANINGS.get(marker),
            "unresolved",
        )

    match = _FRACTIONAL.fullmatch(text.upper())
    if match is None:
        return _unresolved(raw_sp)

    numerator = int(match.group(1))
    denominator = int(match.group(2))
    marker = match.group(3)
    fraction = Fraction(numerator, denominator)
    decimal = fraction + 1
    probability = Fraction(denominator, numerator + denominator)
    return ParsedStartingPrice(
        raw_sp,
        StartingPriceKind.FRACTIONAL,
        numerator,
        denominator,
        fraction,
        decimal,
        probability,
        marker,
        _MARKER_MEANINGS.get(marker),
        "unresolved",
    )
