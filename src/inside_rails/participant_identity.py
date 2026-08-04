"""Conservative participant-label identity helpers established by Notebook 22."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Final, Iterable

RECOGNISED_PERSON_TITLES: Final[frozenset[str]] = frozenset(
    {"mr", "mrs", "miss", "ms", "mlle", "mme", "frau"}
)

TRAINER_MLLE_LAST_DATE_START: Final[date] = date(2023, 7, 1)
TRAINER_MLLE_LAST_DATE_END: Final[date] = date(2023, 12, 31)
TRAINER_MME_FIRST_DATE_START: Final[date] = date(2024, 1, 1)
TRAINER_MME_FIRST_DATE_END: Final[date] = date(2024, 6, 30)


@dataclass(frozen=True)
class TitledParticipantLabel:
    """A preserved raw label plus its strictly separated leading title."""

    raw_label: str
    title: str | None
    post_title_label: str
    comparison_label: str


def collapse_whitespace(value: str) -> str:
    """Collapse internal whitespace without otherwise rewriting the value."""
    return re.sub(r"\s+", " ", value.strip())


def split_recognised_person_title(raw_label: str) -> TitledParticipantLabel:
    """Separate one recognised leading title while preserving the raw label."""
    collapsed = collapse_whitespace(raw_label)
    if not collapsed:
        return TitledParticipantLabel(raw_label, None, "", "")

    first_token, separator, remainder = collapsed.partition(" ")
    title = first_token.casefold()
    if separator and title in RECOGNISED_PERSON_TITLES:
        post_title_label = remainder
        recognised_title: str | None = title
    else:
        post_title_label = collapsed
        recognised_title = None

    return TitledParticipantLabel(
        raw_label=raw_label,
        title=recognised_title,
        post_title_label=post_title_label,
        comparison_label=post_title_label.casefold(),
    )


def owner_token_sequence(raw_label: str) -> tuple[str, ...]:
    """Return casefolded alphanumeric owner tokens in source-presented order."""
    return tuple(re.sub(r"[^a-z0-9]+", " ", raw_label.casefold()).split())


def owner_token_multiset_key(raw_label: str) -> tuple[str, ...]:
    """Return the exact owner token multiset without discarding duplicates."""
    return tuple(sorted(owner_token_sequence(raw_label)))


def has_exact_owner_token_multiset(first_label: str, second_label: str) -> bool:
    """Return whether two non-empty labels contain the same exact tokens."""
    first_key = owner_token_multiset_key(first_label)
    second_key = owner_token_multiset_key(second_label)
    return bool(first_key) and first_key == second_key


def has_reordered_owner_token_sequence(first_label: str, second_label: str) -> bool:
    """Return whether exact owner tokens occur in genuinely different orders."""
    first_tokens = owner_token_sequence(first_label)
    second_tokens = owner_token_sequence(second_label)
    return (
        bool(first_tokens)
        and sorted(first_tokens) == sorted(second_tokens)
        and first_tokens != second_tokens
    )


def is_bounded_trainer_mlle_mme_transition(
    *,
    earlier_title: str | None,
    later_title: str | None,
    earlier_post_title_label: str,
    later_post_title_label: str,
    earlier_last_date: date,
    later_first_date: date,
    active_periods_overlap: bool,
) -> bool:
    """Apply the bounded Notebook 22 provisional trainer-transition rule."""
    return (
        earlier_title == "mlle"
        and later_title == "mme"
        and collapse_whitespace(earlier_post_title_label).casefold()
        == collapse_whitespace(later_post_title_label).casefold()
        and not active_periods_overlap
        and TRAINER_MLLE_LAST_DATE_START
        <= earlier_last_date
        <= TRAINER_MLLE_LAST_DATE_END
        and TRAINER_MME_FIRST_DATE_START
        <= later_first_date
        <= TRAINER_MME_FIRST_DATE_END
    )


def same_race_supported_owner_keys(
    race_owner_labels: Iterable[Iterable[str]],
) -> frozenset[tuple[str, ...]]:
    """Return exact token-multiset keys reordered within one race."""
    supported: set[tuple[str, ...]] = set()
    for labels in race_owner_labels:
        sequences_by_key: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
        for raw_label in labels:
            sequence = owner_token_sequence(raw_label)
            if not sequence:
                continue
            key = tuple(sorted(sequence))
            sequences_by_key.setdefault(key, set()).add(sequence)
        supported.update(
            key for key, sequences in sequences_by_key.items() if len(sequences) > 1
        )
    return frozenset(supported)
