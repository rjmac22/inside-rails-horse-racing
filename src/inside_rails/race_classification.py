"""Governed parsing for race classification and eligibility source fields.

Notebook 16 established stable syntax rules for ``class``, ``pattern``,
``rating_band``, ``age_band`` and ``sex_rest``.  This module preserves the raw
source value and derives only meanings supported by the source-wide study.

The parsers deliberately do not:

* infer race class from a rating band;
* collapse Group and Grade into one hierarchy;
* treat every exact-looking age band as a universal eligibility rule;
* treat ``sex_rest = F`` as universally meaning fillies-only;
* reconstruct official sex eligibility from source shorthand.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any


_CLASS_RE = re.compile(r"^Class ([1-7])$")
_PATTERN_RE = re.compile(r"^(Group|Grade) ([123ABC])$")
_RATING_BAND_RE = re.compile(r"^(\d+)-(\d+)$")
_AGE_EXACT_RE = re.compile(r"^(\d+)yo$")
_AGE_OPEN_RE = re.compile(r"^(\d+)yo\+$")
_AGE_RANGE_RE = re.compile(r"^(\d+)-(\d+)yo$")

_EXPLICIT_SEX_REST_VALUES = frozenset({"C & F", "C & G", "F & M", "M"})
_OVERLOADED_SEX_REST_VALUES = frozenset({"F"})


def _blank(raw_value: Any) -> bool:
    """Return whether a source value is null or blank text."""

    return raw_value is None or (
        isinstance(raw_value, str) and not raw_value.strip()
    )


def _normalised_text(raw_value: Any) -> str | None:
    """Return stripped text for source strings, otherwise ``None``."""

    if not isinstance(raw_value, str):
        return None
    return raw_value.strip()


@dataclass(frozen=True)
class ClassResult:
    """Governed structural interpretation of one raw ``class`` value."""

    class_raw: Any
    class_number: int | None
    class_parse_status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PatternResult:
    """Governed structural interpretation of one raw ``pattern`` value."""

    pattern_raw: Any
    pattern_family: str | None
    pattern_level_raw: str | None
    pattern_parse_status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RatingBandResult:
    """Governed structural interpretation of one raw ``rating_band`` value."""

    rating_band_raw: Any
    rating_lower_bound: int | None
    rating_upper_bound: int | None
    rating_band_parse_status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgeBandResult:
    """Governed structural interpretation of one raw ``age_band`` value."""

    age_band_raw: Any
    stated_minimum_age: int | None
    stated_maximum_age: int | None
    age_band_open_ended: bool | None
    age_band_syntax: str
    age_band_interpretation_status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SexRestrictionResult:
    """Governed categorisation of one raw ``sex_rest`` value.

    This result does not expose permitted-runner flags because Notebook 16
    showed that the source shorthand is insufficient for authoritative global
    eligibility reconstruction.
    """

    sex_rest_raw: Any
    sex_rest_category: str | None
    sex_rest_interpretation_status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_class(raw_class: Any) -> dict[str, Any]:
    """Parse canonical ``Class N`` syntax without assigning jurisdictional meaning."""

    if _blank(raw_class):
        return ClassResult(raw_class, None, "blank").as_dict()

    text = _normalised_text(raw_class)
    match = _CLASS_RE.fullmatch(text) if text is not None else None
    if match is None:
        return ClassResult(raw_class, None, "unrecognised").as_dict()

    return ClassResult(raw_class, int(match.group(1)), "canonical").as_dict()


def parse_pattern(raw_pattern: Any) -> dict[str, Any]:
    """Parse Listed, Group and Grade families while keeping them distinct."""

    if _blank(raw_pattern):
        return PatternResult(raw_pattern, None, None, "blank").as_dict()

    text = _normalised_text(raw_pattern)
    if text == "Listed":
        return PatternResult(raw_pattern, "Listed", None, "canonical").as_dict()

    match = _PATTERN_RE.fullmatch(text) if text is not None else None
    if match is None:
        return PatternResult(raw_pattern, None, None, "unrecognised").as_dict()

    return PatternResult(
        raw_pattern,
        match.group(1),
        match.group(2),
        "canonical",
    ).as_dict()


def parse_rating_band(raw_rating_band: Any) -> dict[str, Any]:
    """Parse only exact closed integer ``N-N`` rating ranges.

    Source values such as ``--`` and ``(75-100)`` remain explicit unresolved
    forms rather than being coerced into the canonical parser.
    """

    if _blank(raw_rating_band):
        return RatingBandResult(raw_rating_band, None, None, "blank").as_dict()

    text = _normalised_text(raw_rating_band)
    match = _RATING_BAND_RE.fullmatch(text) if text is not None else None
    if match is None:
        return RatingBandResult(
            raw_rating_band,
            None,
            None,
            "unrecognised_source_form",
        ).as_dict()

    lower = int(match.group(1))
    upper = int(match.group(2))
    if lower > upper:
        return RatingBandResult(
            raw_rating_band,
            None,
            None,
            "invalid_range_order",
        ).as_dict()

    return RatingBandResult(raw_rating_band, lower, upper, "canonical").as_dict()


def parse_age_band(raw_age_band: Any) -> dict[str, Any]:
    """Parse observed age-band syntax without enforcing runner eligibility."""

    if _blank(raw_age_band):
        return AgeBandResult(
            raw_age_band,
            None,
            None,
            None,
            "blank",
            "blank",
        ).as_dict()

    text = _normalised_text(raw_age_band)
    if text is None:
        return AgeBandResult(
            raw_age_band,
            None,
            None,
            None,
            "unrecognised",
            "unresolved",
        ).as_dict()

    match = _AGE_EXACT_RE.fullmatch(text)
    if match is not None:
        age = int(match.group(1))
        return AgeBandResult(
            raw_age_band,
            age,
            age,
            False,
            "exact_age",
            "source_stated_bounds_only",
        ).as_dict()

    match = _AGE_OPEN_RE.fullmatch(text)
    if match is not None:
        return AgeBandResult(
            raw_age_band,
            int(match.group(1)),
            None,
            True,
            "open_ended_minimum",
            "source_stated_bounds_only",
        ).as_dict()

    match = _AGE_RANGE_RE.fullmatch(text)
    if match is not None:
        lower = int(match.group(1))
        upper = int(match.group(2))
        if lower > upper:
            return AgeBandResult(
                raw_age_band,
                None,
                None,
                None,
                "invalid_range_order",
                "unresolved",
            ).as_dict()
        return AgeBandResult(
            raw_age_band,
            lower,
            upper,
            False,
            "closed_age_range",
            "source_stated_bounds_only",
        ).as_dict()

    return AgeBandResult(
        raw_age_band,
        None,
        None,
        None,
        "unrecognised",
        "unresolved",
    ).as_dict()


def classify_sex_restriction(raw_sex_rest: Any) -> dict[str, Any]:
    """Categorise source sex-restriction shorthand without inferring eligibility."""

    if _blank(raw_sex_rest):
        return SexRestrictionResult(raw_sex_rest, None, "blank").as_dict()

    text = _normalised_text(raw_sex_rest)
    if text in _EXPLICIT_SEX_REST_VALUES:
        return SexRestrictionResult(
            raw_sex_rest,
            text,
            "explicit_source_category",
        ).as_dict()

    if text in _OVERLOADED_SEX_REST_VALUES:
        return SexRestrictionResult(
            raw_sex_rest,
            text,
            "overloaded_source_category",
        ).as_dict()

    return SexRestrictionResult(
        raw_sex_rest,
        text,
        "unrecognised_source_category",
    ).as_dict()
