#!/usr/bin/env python3
"""Validate Notebook 22 participant identity rules and governed outputs."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
from itertools import combinations
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.participant_identity import (  # noqa: E402
    is_bounded_trainer_mlle_mme_transition,
    owner_token_multiset_key,
    owner_token_sequence,
    split_recognised_person_title,
)

EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_JOCKEY_LABELS = 7_917
EXPECTED_JOCKEY_GROUPS = 212
EXPECTED_JOCKEY_CANDIDATE_LABELS = 426
EXPECTED_JOCKEY_RELATIONSHIPS = 216
EXPECTED_JOCKEY_SAME_PERSON_RELATIONSHIPS = 1
EXPECTED_JOCKEY_DIFFERENT_PEOPLE_RELATIONSHIPS = 1
EXPECTED_JOCKEY_UNRESOLVED_RELATIONSHIPS = 214
EXPECTED_JOCKEY_MAPPED_LABELS = 2
EXPECTED_TRAINER_LABELS = 10_708
EXPECTED_TRAINER_BLANK_ROWS = 9
EXPECTED_TRAINER_CANDIDATE_GROUPS = 53
EXPECTED_TRAINER_ACCEPTED_GROUPS = 26
EXPECTED_TRAINER_ACCEPTED_LABELS = 52
EXPECTED_TRAINER_MAPPED_ROWS = 6_350
EXPECTED_OWNER_LABELS = 98_234
EXPECTED_OWNER_BLANK_ROWS = 35
EXPECTED_OWNER_CANDIDATE_GROUPS = 936
EXPECTED_OWNER_CANDIDATE_LABELS = 1_917
EXPECTED_OWNER_CANDIDATE_ROWS = 34_194
EXPECTED_OWNER_ACCEPTED_GROUPS = 41
EXPECTED_OWNER_ACCEPTED_LABELS = 95
EXPECTED_OWNER_MAPPED_ROWS = 9_788
EXPECTED_OWNER_UNRESOLVED_GROUPS = 895
EXPECTED_OWNER_UNRESOLVED_LABELS = 1_822
EXPECTED_OWNER_UNRESOLVED_ROWS = 24_406


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"missing governed output: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _assert_row_fields(
    row: dict[str, str],
    expected: dict[str, str],
    *,
    context: str,
) -> None:
    observed = {field: row.get(field, "") for field in expected}
    if observed != expected:
        raise AssertionError(f"{context} mismatch: {observed=} {expected=}")


def _label_profile(
    connection: sqlite3.Connection,
    field: str,
) -> tuple[dict[str, int], dict[str, tuple[str, str, int]]]:
    rows = connection.execute(
        f"""
        SELECT {field}, MIN(date), MAX(date), COUNT(*)
        FROM data
        WHERE rowid <> 1
          AND {field} IS NOT NULL
          AND TRIM({field}) <> ''
        GROUP BY {field}
        """
    )
    counts: dict[str, int] = {}
    periods: dict[str, tuple[str, str, int]] = {}
    for raw_label, first_date, last_date, runner_rows in rows:
        counts[raw_label] = runner_rows
        periods[raw_label] = (first_date, last_date, runner_rows)
    return counts, periods


def _comparison_groups_with_title_variation(
    labels: set[str],
    *,
    require_recognised_title: bool = True,
) -> dict[str, list[str]]:
    """Group labels after optional strict title removal.

    Notebook 22 generated jockey candidates from every comparison key containing
    more than one raw label after optional title removal, including one group of
    two untitled labels differing only in whitespace. Trainer candidates remain
    restricted to groups containing at least one recognised titled form.
    """
    grouped: dict[str, list[str]] = defaultdict(list)
    for raw_label in labels:
        governed = split_recognised_person_title(raw_label)
        grouped[governed.comparison_label].append(raw_label)

    return {
        comparison: sorted(raw_labels)
        for comparison, raw_labels in grouped.items()
        if len(raw_labels) > 1
        and (
            not require_recognised_title
            or any(
                split_recognised_person_title(raw_label).title is not None
                for raw_label in raw_labels
            )
        )
    }


def _validate_jockey_review_queue(
    groups: dict[str, list[str]],
    queue: list[dict[str, str]],
) -> None:
    if len(queue) != EXPECTED_JOCKEY_RELATIONSHIPS:
        raise AssertionError(f"unexpected jockey review queue rows: {len(queue)}")

    expected_ids = {
        f"JOCKEY-STRICT-{index:04d}"
        for index in range(1, EXPECTED_JOCKEY_RELATIONSHIPS + 1)
    }
    observed_ids = [row["candidate_pair_id"] for row in queue]
    if len(observed_ids) != len(set(observed_ids)):
        raise AssertionError("duplicate jockey candidate_pair_id values")
    if set(observed_ids) != expected_ids:
        raise AssertionError("jockey candidate_pair_id sequence is incomplete")

    expected_pairs = {
        frozenset(pair)
        for labels in groups.values()
        for pair in combinations(labels, 2)
    }
    observed_pairs = [
        frozenset((row["left_raw_jockey_label"], row["right_raw_jockey_label"]))
        for row in queue
    ]
    if len(observed_pairs) != len(set(observed_pairs)):
        raise AssertionError("duplicate jockey candidate label pairs")
    if set(observed_pairs) != expected_pairs:
        missing = expected_pairs - set(observed_pairs)
        unexpected = set(observed_pairs) - expected_pairs
        raise AssertionError(
            "jockey review queue does not close over the source candidate pairs: "
            f"missing={len(missing)}, unexpected={len(unexpected)}"
        )

    relationship_counts = Counter(row["identity_relationship"] for row in queue)
    expected_relationship_counts = Counter(
        {
            "same_person": EXPECTED_JOCKEY_SAME_PERSON_RELATIONSHIPS,
            "different_people": EXPECTED_JOCKEY_DIFFERENT_PEOPLE_RELATIONSHIPS,
            "unresolved": EXPECTED_JOCKEY_UNRESOLVED_RELATIONSHIPS,
        }
    )
    if relationship_counts != expected_relationship_counts:
        raise AssertionError(
            "unexpected jockey relationship closure: "
            f"{relationship_counts=} {expected_relationship_counts=}"
        )

    rows_by_id = {row["candidate_pair_id"]: row for row in queue}
    oneill = rows_by_id["JOCKEY-STRICT-0001"]
    _assert_row_fields(
        oneill,
        {
            "left_raw_jockey_label": "Miss B ONeill",
            "right_raw_jockey_label": "Mr B ONeill",
            "same_race_collisions": "1",
            "identity_relationship": "different_people",
            "verification_status": "confirmed",
            "verification_id": "NB22-JOCKEY-0001",
            "evidence_type": "published_result",
            "evidence_accessed_date": "2026-08-04",
            "confidence": "high",
            "database_action": "preserve_separate_participant_identities",
            "review_scope_status": "completed",
        },
        context="B ONeill governed decision",
    )
    if not oneill["evidence_locator"] or not oneill["review_notes"]:
        raise AssertionError("B ONeill governed decision lacks preserved evidence")

    velon = rows_by_id["JOCKEY-STRICT-0002"]
    _assert_row_fields(
        velon,
        {
            "left_raw_jockey_label": "Mlle Marie Velon",
            "right_raw_jockey_label": "Mme Marie Velon",
            "identity_relationship": "same_person",
            "left_verified_person_name": "Marie Vélon",
            "right_verified_person_name": "Marie Vélon",
            "verification_status": "confirmed",
            "verification_id": "NB22-JOCKEY-0002",
            "evidence_type": "governing_body_profile; published_jockey_profile",
            "evidence_accessed_date": "2026-08-04",
            "confidence": "high",
            "database_action": "map_both_labels_to_same_participant_identity",
            "review_scope_status": "completed",
        },
        context="Marie Velon governed decision",
    )
    if not velon["evidence_locator"] or not velon["review_notes"]:
        raise AssertionError("Marie Velon governed decision lacks preserved evidence")

    unresolved = [
        row for row in queue if row["identity_relationship"] == "unresolved"
    ]
    unresolved_expected = {
        "verification_status": "not_started",
        "verification_id": "",
        "evidence_type": "",
        "evidence_locator": "",
        "evidence_accessed_date": "",
        "confidence": "",
        "database_action": "preserve_raw_unresolved",
        "review_scope_status": "deferred_until_material_use",
    }
    for row in unresolved:
        _assert_row_fields(
            row,
            unresolved_expected,
            context=f"unresolved jockey decision {row['candidate_pair_id']}",
        )

    mapping = _read_csv(
        PROJECT_ROOT
        / "data/processed/jockey_identity/jockey_provisional_identity_mapping.csv"
    )
    if len(mapping) != EXPECTED_JOCKEY_MAPPED_LABELS:
        raise AssertionError(f"unexpected jockey mapping rows: {len(mapping)}")

    expected_mapping_rows = {
        (
            "JOCKEY-PROVISIONAL-0001",
            "Mlle Marie Velon",
            "mlle_source_label",
            "marie velon",
            "provisional_source_label_identity",
            "targeted_external_profile_verification",
            "high",
            "NB22-JOCKEY-0002",
            "jockey_strict_candidate_review_queue.csv#JOCKEY-STRICT-0002",
            "map_raw_label_to_provisional_jockey_identity",
        ),
        (
            "JOCKEY-PROVISIONAL-0001",
            "Mme Marie Velon",
            "mme_source_label",
            "marie velon",
            "provisional_source_label_identity",
            "targeted_external_profile_verification",
            "high",
            "NB22-JOCKEY-0002",
            "jockey_strict_candidate_review_queue.csv#JOCKEY-STRICT-0002",
            "map_raw_label_to_provisional_jockey_identity",
        ),
    }
    observed_mapping_rows = {
        (
            row["provisional_jockey_id"],
            row["raw_jockey_label"],
            row["label_role"],
            row["strict_comparison_key"],
            row["identity_status"],
            row["mapping_method"],
            row["confidence"],
            row["verification_id"],
            row["evidence_reference"],
            row["database_action"],
        )
        for row in mapping
    }
    if observed_mapping_rows != expected_mapping_rows:
        raise AssertionError(
            "unexpected governed jockey mapping rows: "
            f"{observed_mapping_rows=} {expected_mapping_rows=}"
        )


def _validate_jockeys(connection: sqlite3.Connection) -> None:
    counts, _ = _label_profile(connection, "jockey")
    groups = _comparison_groups_with_title_variation(
        set(counts),
        require_recognised_title=False,
    )
    relationship_count = sum(len(tuple(combinations(labels, 2))) for labels in groups.values())
    candidate_labels = sum(len(labels) for labels in groups.values())

    observed = {
        "labels": len(counts),
        "groups": len(groups),
        "candidate_labels": candidate_labels,
        "relationships": relationship_count,
    }
    expected = {
        "labels": EXPECTED_JOCKEY_LABELS,
        "groups": EXPECTED_JOCKEY_GROUPS,
        "candidate_labels": EXPECTED_JOCKEY_CANDIDATE_LABELS,
        "relationships": EXPECTED_JOCKEY_RELATIONSHIPS,
    }
    if observed != expected:
        raise AssertionError(f"jockey baseline mismatch: {observed=} {expected=}")

    if groups.get("marie velon") != ["Mlle Marie Velon", "Mme Marie Velon"]:
        raise AssertionError(f"unexpected Marie Velon group: {groups.get('marie velon')}")

    collision = connection.execute(
        """
        SELECT date, course, off
        FROM data
        WHERE rowid <> 1
          AND jockey IN ('Miss B ONeill', 'Mr B ONeill')
        GROUP BY date, course, off
        HAVING COUNT(DISTINCT jockey) = 2
        LIMIT 1
        """
    ).fetchone()
    if collision is None:
        raise AssertionError("expected same-race Miss/Mr B ONeill collision not found")

    queue = _read_csv(
        PROJECT_ROOT
        / "data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv"
    )
    _validate_jockey_review_queue(groups, queue)

    print(
        "jockeys: "
        f"{len(counts):,} labels; {len(groups):,} groups; "
        f"{relationship_count:,} candidate relationships; "
        f"{EXPECTED_JOCKEY_SAME_PERSON_RELATIONSHIPS} accepted; "
        f"{EXPECTED_JOCKEY_DIFFERENT_PEOPLE_RELATIONSHIPS} distinct; "
        f"{EXPECTED_JOCKEY_UNRESOLVED_RELATIONSHIPS} unresolved"
    )


def _validate_trainers(connection: sqlite3.Connection) -> None:
    counts, periods = _label_profile(connection, "trainer")
    blank_rows = connection.execute(
        "SELECT COUNT(*) FROM data WHERE rowid <> 1 AND trainer = ''"
    ).fetchone()[0]
    groups = _comparison_groups_with_title_variation(set(counts))

    accepted: list[tuple[str, str]] = []
    for labels in groups.values():
        if len(labels) != 2:
            continue
        governed = [split_recognised_person_title(label) for label in labels]
        earlier_items = [item for item in governed if item.title == "mlle"]
        later_items = [item for item in governed if item.title == "mme"]
        if len(earlier_items) != 1 or len(later_items) != 1:
            continue
        earlier = earlier_items[0]
        later = later_items[0]
        earlier_first, earlier_last, _ = periods[earlier.raw_label]
        later_first, later_last, _ = periods[later.raw_label]
        overlap = max(earlier_first, later_first) <= min(earlier_last, later_last)
        if is_bounded_trainer_mlle_mme_transition(
            earlier_title=earlier.title,
            later_title=later.title,
            earlier_post_title_label=earlier.post_title_label,
            later_post_title_label=later.post_title_label,
            earlier_last_date=date.fromisoformat(earlier_last),
            later_first_date=date.fromisoformat(later_first),
            active_periods_overlap=overlap,
        ):
            accepted.append((earlier.raw_label, later.raw_label))

    accepted_labels = {label for pair in accepted for label in pair}
    mapped_rows = sum(counts[label] for label in accepted_labels)
    observed = {
        "labels": len(counts),
        "blank_rows": blank_rows,
        "candidate_groups": len(groups),
        "accepted_groups": len(accepted),
        "accepted_labels": len(accepted_labels),
        "mapped_rows": mapped_rows,
    }
    expected = {
        "labels": EXPECTED_TRAINER_LABELS,
        "blank_rows": EXPECTED_TRAINER_BLANK_ROWS,
        "candidate_groups": EXPECTED_TRAINER_CANDIDATE_GROUPS,
        "accepted_groups": EXPECTED_TRAINER_ACCEPTED_GROUPS,
        "accepted_labels": EXPECTED_TRAINER_ACCEPTED_LABELS,
        "mapped_rows": EXPECTED_TRAINER_MAPPED_ROWS,
    }
    if observed != expected:
        raise AssertionError(f"trainer baseline mismatch: {observed=} {expected=}")

    decisions = _read_csv(
        PROJECT_ROOT / "data/processed/trainer_identity/trainer_strict_title_decisions.csv"
    )
    mapping = _read_csv(
        PROJECT_ROOT
        / "data/processed/trainer_identity/trainer_provisional_identity_mapping.csv"
    )
    unresolved = _read_csv(
        PROJECT_ROOT
        / "data/processed/trainer_identity/trainer_unresolved_identity_candidates.csv"
    )
    if len(decisions) != 53 or len(mapping) != 52 or len(unresolved) != 27:
        raise AssertionError(
            "unexpected trainer governed output counts: "
            f"decisions={len(decisions)}, mapping={len(mapping)}, unresolved={len(unresolved)}"
        )

    print(
        "trainers: "
        f"{len(counts):,} labels; {len(accepted):,} accepted groups; "
        f"{mapped_rows:,} mapped rows"
    )


def _validate_owners(connection: sqlite3.Connection) -> None:
    counts, _ = _label_profile(connection, "owner")
    blank_rows = connection.execute(
        "SELECT COUNT(*) FROM data WHERE rowid <> 1 AND owner = ''"
    ).fetchone()[0]

    labels_by_key: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for label in counts:
        key = owner_token_multiset_key(label)
        if key:
            labels_by_key[key].append(label)
    candidate_groups = {
        key: sorted(labels) for key, labels in labels_by_key.items() if len(labels) > 1
    }
    candidate_labels = {label for labels in candidate_groups.values() for label in labels}
    candidate_rows = sum(counts[label] for label in candidate_labels)

    supported_keys: set[tuple[str, ...]] = set()
    current_race: tuple[str, str, str] | None = None
    sequences_by_key: dict[tuple[str, ...], set[tuple[str, ...]]] = defaultdict(set)
    placeholders = ",".join("?" for _ in candidate_labels)
    query = f"""
        SELECT date, course, off, owner
        FROM data
        WHERE rowid <> 1
          AND owner IN ({placeholders})
        ORDER BY date, course, off, rowid
    """
    for race_date, course, off, owner in connection.execute(query, tuple(candidate_labels)):
        race = (race_date, course, off)
        if current_race is not None and race != current_race:
            supported_keys.update(
                key for key, sequences in sequences_by_key.items() if len(sequences) > 1
            )
            sequences_by_key = defaultdict(set)
        current_race = race
        key = owner_token_multiset_key(owner)
        sequences_by_key[key].add(owner_token_sequence(owner))
    supported_keys.update(
        key for key, sequences in sequences_by_key.items() if len(sequences) > 1
    )

    accepted_labels = {label for key in supported_keys for label in candidate_groups[key]}
    accepted_rows = sum(counts[label] for label in accepted_labels)
    unresolved_keys = set(candidate_groups) - supported_keys
    unresolved_labels = {label for key in unresolved_keys for label in candidate_groups[key]}
    unresolved_rows = sum(counts[label] for label in unresolved_labels)

    observed = {
        "labels": len(counts),
        "blank_rows": blank_rows,
        "candidate_groups": len(candidate_groups),
        "candidate_labels": len(candidate_labels),
        "candidate_rows": candidate_rows,
        "accepted_groups": len(supported_keys),
        "accepted_labels": len(accepted_labels),
        "accepted_rows": accepted_rows,
        "unresolved_groups": len(unresolved_keys),
        "unresolved_labels": len(unresolved_labels),
        "unresolved_rows": unresolved_rows,
    }
    expected = {
        "labels": EXPECTED_OWNER_LABELS,
        "blank_rows": EXPECTED_OWNER_BLANK_ROWS,
        "candidate_groups": EXPECTED_OWNER_CANDIDATE_GROUPS,
        "candidate_labels": EXPECTED_OWNER_CANDIDATE_LABELS,
        "candidate_rows": EXPECTED_OWNER_CANDIDATE_ROWS,
        "accepted_groups": EXPECTED_OWNER_ACCEPTED_GROUPS,
        "accepted_labels": EXPECTED_OWNER_ACCEPTED_LABELS,
        "accepted_rows": EXPECTED_OWNER_MAPPED_ROWS,
        "unresolved_groups": EXPECTED_OWNER_UNRESOLVED_GROUPS,
        "unresolved_labels": EXPECTED_OWNER_UNRESOLVED_LABELS,
        "unresolved_rows": EXPECTED_OWNER_UNRESOLVED_ROWS,
    }
    if observed != expected:
        raise AssertionError(f"owner baseline mismatch: {observed=} {expected=}")

    decisions = _read_csv(
        PROJECT_ROOT / "data/processed/owner_identity/owner_token_multiset_decisions.csv"
    )
    mapping = _read_csv(
        PROJECT_ROOT
        / "data/processed/owner_identity/owner_provisional_composition_mapping.csv"
    )
    unresolved = _read_csv(
        PROJECT_ROOT
        / "data/processed/owner_identity/owner_unresolved_token_multiset_candidates.csv"
    )
    if len(decisions) != 936 or len(mapping) != 95 or len(unresolved) != 895:
        raise AssertionError(
            "unexpected owner governed output counts: "
            f"decisions={len(decisions)}, mapping={len(mapping)}, unresolved={len(unresolved)}"
        )

    print(
        "owners: "
        f"{len(counts):,} labels; {len(supported_keys):,} accepted groups; "
        f"{accepted_rows:,} mapped rows; {len(unresolved_keys):,} unresolved groups"
    )


def validate(source_database: Path) -> None:
    if not source_database.exists():
        raise FileNotFoundError(source_database)
    connection = sqlite3.connect(
        f"file:{source_database.resolve()}?mode=ro&immutable=1",
        uri=True,
    )
    try:
        runner_rows = connection.execute(
            "SELECT COUNT(*) FROM data WHERE rowid <> 1"
        ).fetchone()[0]
        if runner_rows != EXPECTED_RUNNER_ROWS:
            raise AssertionError(
                f"runner-row mismatch: observed={runner_rows}, expected={EXPECTED_RUNNER_ROWS}"
            )
        _validate_jockeys(connection)
        _validate_trainers(connection)
        _validate_owners(connection)
    finally:
        connection.close()
    print("participant identity validation: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_database",
        nargs="?",
        type=Path,
        default=(
            PROJECT_ROOT
            / "data/raw/form_2015-present/form_2015-present/raceform.db"
        ),
    )
    args = parser.parse_args()
    validate(args.source_database)


if __name__ == "__main__":
    main()
