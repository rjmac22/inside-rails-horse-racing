"""Governed parsing and structural flags for source beaten-distance fields.

Notebook 15 established that ``ovr_btn`` is cumulative from the source
physical-finish first-place reference, while ``btn`` is incremental from the
preceding physical finisher or stored distance group. Raw values are always
preserved. This module derives only conservative numeric values and diagnostic
flags; it never silently rewrites source contradictions.
"""

from __future__ import annotations

from numbers import Real
from typing import Any

UNAVAILABLE_SENTINEL = "-"


def parse_beaten_distance(raw_value: Any) -> dict[str, Any]:
    """Parse one raw beaten-distance value without inventing information."""
    result: dict[str, Any] = {
        "raw_value": raw_value,
        "numeric_value": None,
        "availability_status": "unresolved",
        "parse_status": "unresolved",
    }

    if raw_value == UNAVAILABLE_SENTINEL:
        result.update(
            {
                "availability_status": "unavailable",
                "parse_status": "sentinel",
            }
        )
        return result

    if isinstance(raw_value, bool):
        return result

    if isinstance(raw_value, Real):
        numeric_value = float(raw_value)
        result.update(
            {
                "numeric_value": numeric_value,
                "availability_status": "available",
                "parse_status": "parsed",
            }
        )
        return result

    return result


def classify_beaten_distance_row(
    *,
    raw_pos: Any,
    raw_ovr_btn: Any,
    raw_btn: Any,
) -> dict[str, Any]:
    """Parse one runner row and derive Notebook 15 structural review flags."""
    position = _numeric_position(raw_pos)
    overall = parse_beaten_distance(raw_ovr_btn)
    incremental = parse_beaten_distance(raw_btn)

    overall_value = overall["numeric_value"]
    incremental_value = incremental["numeric_value"]

    positive_official_winner_distance = (
        position == 1 and overall_value is not None and overall_value > 0
    )
    later_position_zero_overall = (
        position is not None
        and position > 1
        and overall_value is not None
        and overall_value == 0
    )
    same_distance_group = (
        overall_value is not None
        and overall_value > 0
        and incremental_value is not None
        and incremental_value == 0
    )

    return {
        "raw_pos": raw_pos,
        "numeric_pos": position,
        "raw_ovr_btn": raw_ovr_btn,
        "numeric_ovr_btn": overall_value,
        "ovr_btn_status": overall["availability_status"],
        "raw_btn": raw_btn,
        "numeric_btn": incremental_value,
        "btn_status": incremental["availability_status"],
        "positive_official_winner_distance": positive_official_winner_distance,
        "later_position_zero_overall": later_position_zero_overall,
        "same_distance_group": same_distance_group,
        "requires_review": (
            positive_official_winner_distance or later_position_zero_overall
        ),
    }


def _numeric_position(raw_pos: Any) -> int | None:
    """Return an integral numeric position, preserving text outcomes as null."""
    if isinstance(raw_pos, bool) or not isinstance(raw_pos, Real):
        return None

    numeric = float(raw_pos)
    if not numeric.is_integer() or numeric < 1:
        return None

    return int(numeric)
