"""Validated scheduled race-distance parsing.

The exact raw source value is preserved.

Derived yards and metres are literal conversions of the source expression
only. They are not guaranteed to equal the original official scheduled
distance for jurisdictions that publish races metrically, because an upstream
provider may have rounded or standardised those distances into
miles-and-furlongs notation.

Only exact raw values observed and validated in Notebook 06 are converted.
Previously unseen values remain unresolved.
"""

from __future__ import annotations

from typing import Any


# Exact raw values validated in Notebook 06.
# Tuple structure: miles, whole furlongs, half-furlong indicator.
VALIDATED_COMPONENTS: dict[str, tuple[int, int, bool]] = {'1m': (1, 0, False),
 '1m1f': (1, 1, False),
 '1m1½f': (1, 1, True),
 '1m2f': (1, 2, False),
 '1m2½f': (1, 2, True),
 '1m3f': (1, 3, False),
 '1m3½f': (1, 3, True),
 '1m4f': (1, 4, False),
 '1m4½f': (1, 4, True),
 '1m5f': (1, 5, False),
 '1m5½f': (1, 5, True),
 '1m6f': (1, 6, False),
 '1m6½f': (1, 6, True),
 '1m7f': (1, 7, False),
 '1m7½f': (1, 7, True),
 '1m½f': (1, 0, True),
 '2m': (2, 0, False),
 '2m1f': (2, 1, False),
 '2m1½f': (2, 1, True),
 '2m2f': (2, 2, False),
 '2m2½f': (2, 2, True),
 '2m3f': (2, 3, False),
 '2m3½f': (2, 3, True),
 '2m4f': (2, 4, False),
 '2m4½f': (2, 4, True),
 '2m5f': (2, 5, False),
 '2m5½f': (2, 5, True),
 '2m6f': (2, 6, False),
 '2m6½f': (2, 6, True),
 '2m7f': (2, 7, False),
 '2m7½f': (2, 7, True),
 '2m½f': (2, 0, True),
 '3m': (3, 0, False),
 '3m1f': (3, 1, False),
 '3m1½f': (3, 1, True),
 '3m2f': (3, 2, False),
 '3m2½f': (3, 2, True),
 '3m3f': (3, 3, False),
 '3m3½f': (3, 3, True),
 '3m4f': (3, 4, False),
 '3m4½f': (3, 4, True),
 '3m5f': (3, 5, False),
 '3m5½f': (3, 5, True),
 '3m6f': (3, 6, False),
 '3m6½f': (3, 6, True),
 '3m7f': (3, 7, False),
 '3m7½f': (3, 7, True),
 '3m½f': (3, 0, True),
 '4f': (0, 4, False),
 '4m': (4, 0, False),
 '4m1f': (4, 1, False),
 '4m1½f': (4, 1, True),
 '4m2f': (4, 2, False),
 '4m2½f': (4, 2, True),
 '4m4½f': (4, 4, True),
 '4m½f': (4, 0, True),
 '4½f': (0, 4, True),
 '5f': (0, 5, False),
 '5½f': (0, 5, True),
 '6f': (0, 6, False),
 '6½f': (0, 6, True),
 '7f': (0, 7, False),
 '7½f': (0, 7, True)}


def parse_race_distance(raw_dist: Any) -> dict[str, Any]:
    """Parse one exact validated source race-distance value.

    ``source_implied_yards`` and ``source_implied_metres`` describe the literal
    source expression. They must not be treated as independently verified
    official race distances.
    """
    result: dict[str, Any] = {
        "raw_dist": raw_dist,
        "miles": None,
        "whole_furlongs": None,
        "has_half_furlong": None,
        "total_furlongs": None,
        "source_implied_yards": None,
        "source_implied_metres": None,
        "official_distance_verified": False,
        "parse_status": "unresolved",
    }

    components = VALIDATED_COMPONENTS.get(raw_dist)

    if components is None:
        return result

    miles, whole_furlongs, has_half_furlong = components

    total_furlongs = (
        miles * 8
        + whole_furlongs
        + (0.5 if has_half_furlong else 0.0)
    )

    source_implied_yards = int(total_furlongs * 220)

    result.update(
        {
            "miles": miles,
            "whole_furlongs": whole_furlongs,
            "has_half_furlong": has_half_furlong,
            "total_furlongs": total_furlongs,
            "source_implied_yards": source_implied_yards,
            "source_implied_metres": source_implied_yards * 0.9144,
            "official_distance_verified": False,
            "parse_status": "parsed",
        }
    )

    return result
