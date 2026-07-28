"""Governed Notebook 09 jurisdiction and authority context.

This module contains only the bounded, evidence-backed examples established in
Notebook 09. It does not attempt a complete worldwide racing-authority or
betting-market catalogue.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


OBSERVED_SOURCE_TYPES = ("Flat", "Hurdle", "Chase", "NH Flat")


@dataclass(frozen=True)
class JurisdictionContext:
    jurisdiction: str
    source_type: str
    effective_from: date
    effective_to: date | None
    regulatory_authority: str
    administrative_body: str | None
    native_code_status: str
    wagering_context_status: str
    evidence_scope: str

    def contains(self, race_date: date) -> bool:
        return race_date >= self.effective_from and (
            self.effective_to is None or race_date <= self.effective_to
        )


CONTEXTS: tuple[JurisdictionContext, ...] = tuple(
    [
        JurisdictionContext(
            jurisdiction="Great Britain",
            source_type=source_type,
            effective_from=date(2015, 1, 1),
            effective_to=None,
            regulatory_authority="British Horseracing Authority",
            administrative_body=None,
            native_code_status="source_type_retained",
            wagering_context_status="unresolved",
            evidence_scope="notebook_09_bounded_example",
        )
        for source_type in OBSERVED_SOURCE_TYPES
    ]
    + [
        JurisdictionContext(
            jurisdiction="Ireland",
            source_type=source_type,
            effective_from=date(2015, 1, 1),
            effective_to=date(2017, 12, 31),
            regulatory_authority="Irish Turf Club",
            administrative_body="Horse Racing Ireland",
            native_code_status="source_type_retained",
            wagering_context_status="unresolved",
            evidence_scope="notebook_09_bounded_example",
        )
        for source_type in OBSERVED_SOURCE_TYPES
    ]
    + [
        JurisdictionContext(
            jurisdiction="Ireland",
            source_type=source_type,
            effective_from=date(2018, 1, 1),
            effective_to=None,
            regulatory_authority="Irish Horseracing Regulatory Board",
            administrative_body="Horse Racing Ireland",
            native_code_status="source_type_retained",
            wagering_context_status="unresolved",
            evidence_scope="notebook_09_bounded_example",
        )
        for source_type in OBSERVED_SOURCE_TYPES
    ]
    + [
        JurisdictionContext(
            jurisdiction="France",
            source_type=source_type,
            effective_from=date(2015, 1, 1),
            effective_to=None,
            regulatory_authority="France Galop",
            administrative_body=None,
            native_code_status=(
                "unresolved_aqps_source_classification"
                if source_type == "NH Flat"
                else "source_type_retained"
            ),
            wagering_context_status="unresolved",
            evidence_scope="notebook_09_bounded_example",
        )
        for source_type in OBSERVED_SOURCE_TYPES
    ]
)


def validate_context_reference(
    contexts: Iterable[JurisdictionContext] = CONTEXTS,
) -> None:
    """Raise ``ValueError`` when keys overlap or required values are invalid."""

    rows = tuple(contexts)
    for row in rows:
        if row.source_type not in OBSERVED_SOURCE_TYPES:
            raise ValueError(f"Unsupported source type: {row.source_type!r}")
        if row.effective_to is not None and row.effective_to < row.effective_from:
            raise ValueError(f"Invalid effective period: {row!r}")
        if not row.regulatory_authority:
            raise ValueError(f"Missing regulatory authority: {row!r}")

    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if (left.jurisdiction, left.source_type) != (
                right.jurisdiction,
                right.source_type,
            ):
                continue
            left_end = left.effective_to or date.max
            right_end = right.effective_to or date.max
            if max(left.effective_from, right.effective_from) <= min(
                left_end, right_end
            ):
                raise ValueError(f"Overlapping context periods: {left!r} / {right!r}")


def resolve_jurisdiction_context(
    jurisdiction: str,
    source_type: str,
    race_date: date,
) -> JurisdictionContext | None:
    """Resolve at most one bounded context row for a race."""

    matches = [
        row
        for row in CONTEXTS
        if row.jurisdiction == jurisdiction
        and row.source_type == source_type
        and row.contains(race_date)
    ]
    if len(matches) > 1:
        raise ValueError(
            "Context reference returned more than one row for "
            f"{jurisdiction!r}, {source_type!r}, {race_date!r}"
        )
    return matches[0] if matches else None


validate_context_reference()
