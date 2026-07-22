"""Conservative parsing of source carried-weight values.

The exact raw source value is preserved. Current source values use canonical
stones-and-pounds notation, including races from jurisdictions that ordinarily
publish carried weight in kilograms.

Derived pounds are the exact interpretation of the stored source expression.
Derived kilograms are only the literal SI conversion of that expression and
must not be treated as independently verified official metric declarations.

Unfamiliar or malformed values remain unresolved rather than being trimmed,
normalised, or guessed.
"""

from __future__ import annotations

import re
from typing import Any


POUND_TO_KILOGRAM = 0.45359237
CARRIED_WEIGHT_PATTERN = re.compile(r"^(0|[1-9]\d*)-(0|[1-9]\d*)$")


def parse_carried_weight(raw_wgt: Any) -> dict[str, Any]:
    """Parse one canonical stones-and-pounds source value.

    Supported text has the exact form ``<stones>-<pounds>`` with no whitespace
    or leading zeros and with the pounds component between zero and thirteen.
    """
    result: dict[str, Any] = {
        "raw_wgt": raw_wgt,
        "notation_family": None,
        "parsed_stones": None,
        "parsed_pounds": None,
        "source_implied_total_pounds": None,
        "source_implied_kilograms": None,
        "parse_status": "unresolved",
        "ambiguity_flag": False,
        "anomaly_flags": (),
        "official_weight_verified": False,
    }

    if raw_wgt is None:
        result.update(
            {
                "notation_family": "missing",
                "parse_status": "unresolved_missing",
                "anomaly_flags": ("missing_value",),
            }
        )
        return result

    if not isinstance(raw_wgt, str):
        result.update(
            {
                "notation_family": "non_text",
                "parse_status": "unresolved_non_text",
                "ambiguity_flag": True,
                "anomaly_flags": ("unexpected_storage_type",),
            }
        )
        return result

    match = CARRIED_WEIGHT_PATTERN.fullmatch(raw_wgt)

    if match is None:
        result.update(
            {
                "notation_family": "unrecognised_text",
                "parse_status": "unresolved_unrecognised_notation",
                "ambiguity_flag": True,
                "anomaly_flags": ("unrecognised_notation",),
            }
        )
        return result

    stones = int(match.group(1))
    pounds = int(match.group(2))

    if pounds > 13:
        result.update(
            {
                "notation_family": "integer_hyphen_integer",
                "parsed_stones": stones,
                "parsed_pounds": pounds,
                "parse_status": "unresolved_invalid_pounds_component",
                "anomaly_flags": ("pounds_component_outside_0_to_13",),
            }
        )
        return result

    total_pounds = (stones * 14) + pounds

    result.update(
        {
            "notation_family": "stones_and_pounds",
            "parsed_stones": stones,
            "parsed_pounds": pounds,
            "source_implied_total_pounds": total_pounds,
            "source_implied_kilograms": total_pounds * POUND_TO_KILOGRAM,
            "parse_status": "parsed",
            "official_weight_verified": False,
        }
    )

    return result
