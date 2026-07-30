"""Conservative parsing and classification of source beaten-distance fields.

Notebook 15 established that:

- ``ovr_btn`` is the cumulative distance from the source's physical
  first-place reference;
- ``btn`` is the incremental margin from the preceding physical finisher or
  stored distance group;
- the text sentinel ``-`` means beaten distance is unavailable;
- zero values can be meaningful and must not be treated as missing;
- official ``pos`` may reflect an amended result while the distance fields
  continue to describe the physical finish.

This module preserves the exact raw values and derives only interpretations
supported by Notebook 15. Diagnostic structures are flagged for review rather
than silently corrected.
"""

from __future__ import annotations

import math
from numbers import Real
from typing import Any


DISTANCE_UNAVAILABLE_SENTINEL = "-"


def _parse_nonnegative_number(raw_value: Any) -> float | None:
    """Return a finite nonnegative numeric value, otherwise ``None``.

    Boolean values are rejected even though Python treats ``bool`` as a
    subclass of ``int``. Source beaten distances are expected to come from
    SQLite integer or real storage classes.
    """

    if isinstance(raw_value, bool):
        return None

    if not isinstance(raw_value, Real):
        return None

    numeric_value = float(raw_value)

    if not math.isfinite(numeric_value) or numeric_value < 0:
        return None

    return numeric_value


def _parse_positive_position(raw_pos: Any) -> int | None:
    """Return a positive integral official position, otherwise ``None``."""

    if isinstance(raw_pos, bool) or not isinstance(raw_pos, Real):
        return None

    numeric_position = float(raw_pos)

    if (
        not math.isfinite(numeric_position)
        or numeric_position <= 0
        or not numeric_position.is_integer()
    ):
        return None

    return int(numeric_position)


def parse_beaten_distances(
    raw_ovr_btn: Any,
    raw_btn: Any,
    raw_pos: Any = None,
) -> dict[str, Any]:
    """Parse one runner's source beaten-distance pair conservatively.

    Parameters
    ----------
    raw_ovr_btn:
        Exact source value from ``ovr_btn``.
    raw_btn:
        Exact source value from ``btn``.
    raw_pos:
        Optional exact source finishing-position value. It is used only to
        identify review patterns; it does not change the parsed distances.

    Returns
    -------
    dict[str, Any]
        Raw values, parsed analytical values and conservative quality flags.

    Notes
    -----
    This function does not:

    - alter or correct raw source values;
    - infer an official dead heat from ``btn = 0`` alone;
    - prove that an amended result occurred;
    - apply externally verified corrections; or
    - reconstruct unavailable distances.
    """

    result: dict[str, Any] = {
        "raw_ovr_btn": raw_ovr_btn,
        "raw_btn": raw_btn,
        "raw_pos": raw_pos,
        "overall_beaten_distance": None,
        "previous_runner_margin": None,
        "distance_available": False,
        "distance_reference_stage": None,
        "distance_value_origin": "raw_source",
        "distance_quality_status": "unresolved",
        "parse_status": "unresolved",
    }

    overall_distance = _parse_nonnegative_number(raw_ovr_btn)
    previous_margin = _parse_nonnegative_number(raw_btn)

    overall_is_unavailable = raw_ovr_btn == DISTANCE_UNAVAILABLE_SENTINEL
    margin_is_unavailable = raw_btn == DISTANCE_UNAVAILABLE_SENTINEL

    # The governed nonfinisher representation is a paired `-` sentinel.
    if overall_is_unavailable and margin_is_unavailable:
        result.update(
            {
                "distance_quality_status": "unavailable_nonfinisher_distance",
                "parse_status": "unavailable",
            }
        )
        return result

    # A numeric pair is the only directly parsed distance representation.
    if overall_distance is not None and previous_margin is not None:
        official_position = _parse_positive_position(raw_pos)

        quality_status = "ordinary_numeric_distance"

        if official_position == 1 and overall_distance > 0:
            quality_status = "review_positive_official_winner_distance"
        elif (
            official_position is not None
            and official_position > 1
            and overall_distance == 0
        ):
            quality_status = "review_later_zero_overall_distance"
        elif overall_distance > 0 and previous_margin == 0:
            quality_status = "same_distance_group"

        result.update(
            {
                "overall_beaten_distance": overall_distance,
                "previous_runner_margin": previous_margin,
                "distance_available": True,
                "distance_reference_stage": (
                    "physical_finish_source_reference"
                ),
                "distance_quality_status": quality_status,
                "parse_status": "parsed",
            }
        )
        return result

    # Mixed numeric/sentinel pairs and all other unseen representations remain
    # unresolved. They are not coerced into missing or numeric values.
    if overall_is_unavailable or margin_is_unavailable:
        result["distance_quality_status"] = "mixed_distance_representation"
    else:
        result["distance_quality_status"] = "invalid_or_unseen_representation"

    return result
