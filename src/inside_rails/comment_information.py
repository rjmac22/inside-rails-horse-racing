"""Govern Notebook 21 comment preservation and source-state classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PROBABLE_PLACEHOLDERS: Final[frozenset[str]] = frozenset({".", "..", "-", " -", "/", "1"})
UNRESOLVED_SOURCE_CODES: Final[frozenset[str]] = frozenset({"A", "B", "V"})


@dataclass(frozen=True)
class GovernedComment:
    """Preserved raw comment plus a conservative governed source state."""

    raw_comment: str | None
    comment_state: str
    substantive_text: str | None


def classify_comment(raw_comment: str | None) -> GovernedComment:
    """Classify a raw comment without trimming, rewriting or semantic parsing.

    Empty strings are source-presented absence. Rare placeholder-like tokens and
    unresolved letter codes remain explicit. Every other non-empty value remains
    substantive raw text, including leading whitespace anomalies.
    """
    if raw_comment is None:
        return GovernedComment(None, "unexpected_null", None)
    if raw_comment == "":
        return GovernedComment(raw_comment, "empty_string", None)
    if raw_comment in PROBABLE_PLACEHOLDERS:
        return GovernedComment(raw_comment, "probable_placeholder", None)
    if raw_comment in UNRESOLVED_SOURCE_CODES:
        return GovernedComment(raw_comment, "unresolved_source_code", None)
    return GovernedComment(raw_comment, "substantive_text", raw_comment)


def is_comment_analytically_available(raw_comment: str | None) -> bool:
    """Return whether the raw value contains substantive preserved commentary."""
    return classify_comment(raw_comment).comment_state == "substantive_text"
