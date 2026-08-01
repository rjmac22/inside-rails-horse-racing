"""Governed parsing for the source ``or``, ``rpr`` and ``ts`` fields.

Notebook 18 established that the three runner-level ratings have different
producers, purposes and timing. Raw values are therefore preserved separately
and the fields must never be collapsed into one generic rating.

Observed source policy:

* a Unicode en dash (``–``) means that the field is unavailable;
* integer values are numeric candidates;
* source rowid 1,619,851 contains the isolated invalid ``rpr`` value 775;
* that exact raw value is preserved but excluded from analytical RPR;
* no replacement is inferred for the invalid value.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Integral, Real
from typing import Any, Literal


RatingField = Literal["or", "rpr", "ts"]
RATING_FIELDS: tuple[RatingField, ...] = ("or", "rpr", "ts")
UNAVAILABLE_RATING_TOKEN = "–"
INVALID_RPR_SOURCE_ROWID = 1_619_851
INVALID_RPR_RAW_VALUE = 775

RATING_MEANINGS: dict[RatingField, str] = {
    "or": "official_pre_race_handicap_mark",
    "rpr": "retrospective_racing_post_performance_rating",
    "ts": "retrospective_racing_post_speed_figure",
}


@dataclass(frozen=True)
class RatingResult:
    """Governed interpretation of one raw runner-level rating value."""

    rating_field: RatingField
    rating_raw: Any
    rating_value: int | None
    rating_status: str
    rating_meaning: str
    source_rowid: int | None
    replacement_status: str | None

    def as_dict(self) -> dict[str, Any]:
        """Return a database-build-friendly mapping."""

        return asdict(self)


def _integer_candidate(raw_value: Any) -> int | None:
    """Return an exact integer candidate without permissive coercion."""

    if isinstance(raw_value, bool):
        return None

    if isinstance(raw_value, Integral):
        return int(raw_value)

    if isinstance(raw_value, Real):
        numeric = float(raw_value)
        if numeric.is_integer():
            return int(numeric)
        return None

    return None


def parse_rating(
    raw_value: Any,
    rating_field: RatingField,
    *,
    source_rowid: int | None = None,
) -> dict[str, Any]:
    """Interpret one source rating under the Notebook 18 governance policy.

    The exact invalid RPR exception is lineage-bound. The function deliberately
    does not infer a corrected value from neighbouring ratings, horse history,
    magnitude or a presumed typographical error.
    """

    if rating_field not in RATING_FIELDS:
        raise ValueError(f"Unsupported rating field: {rating_field!r}")

    meaning = RATING_MEANINGS[rating_field]

    if (
        rating_field == "rpr"
        and source_rowid == INVALID_RPR_SOURCE_ROWID
        and raw_value == INVALID_RPR_RAW_VALUE
    ):
        return RatingResult(
            rating_field=rating_field,
            rating_raw=raw_value,
            rating_value=None,
            rating_status="invalid_source_value",
            rating_meaning=meaning,
            source_rowid=source_rowid,
            replacement_status="unresolved",
        ).as_dict()

    if raw_value == UNAVAILABLE_RATING_TOKEN:
        return RatingResult(
            rating_field=rating_field,
            rating_raw=raw_value,
            rating_value=None,
            rating_status="unavailable",
            rating_meaning=meaning,
            source_rowid=source_rowid,
            replacement_status=None,
        ).as_dict()

    candidate = _integer_candidate(raw_value)
    if candidate is not None:
        return RatingResult(
            rating_field=rating_field,
            rating_raw=raw_value,
            rating_value=candidate,
            rating_status="available",
            rating_meaning=meaning,
            source_rowid=source_rowid,
            replacement_status=None,
        ).as_dict()

    return RatingResult(
        rating_field=rating_field,
        rating_raw=raw_value,
        rating_value=None,
        rating_status="unresolved_source_value",
        rating_meaning=meaning,
        source_rowid=source_rowid,
        replacement_status="unresolved",
    ).as_dict()


def parse_rating_triplet(
    raw_or: Any,
    raw_rpr: Any,
    raw_ts: Any,
    *,
    source_rowid: int | None = None,
) -> dict[str, Any]:
    """Parse all three fields while preserving their independent identities."""

    parsed: dict[str, Any] = {}
    for field, raw_value in (("or", raw_or), ("rpr", raw_rpr), ("ts", raw_ts)):
        result = parse_rating(raw_value, field, source_rowid=source_rowid)
        parsed[f"raw_{field}"] = result["rating_raw"]
        parsed[field] = result["rating_value"]
        parsed[f"{field}_status"] = result["rating_status"]

    return parsed
