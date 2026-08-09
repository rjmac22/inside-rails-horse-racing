"""Populate Database v2 Notebook 22 participant-label identity structures."""

from __future__ import annotations

import csv
from hashlib import sha256
from pathlib import Path
import sqlite3
from typing import Any, Iterable

from inside_rails.participant_identity import owner_token_multiset_key


EXPECTED_LABEL_COUNTS = {"jockey": 7_917, "trainer": 10_708, "owner": 98_234}
EXPECTED_IDENTITY_COUNTS = {"jockey": 1, "trainer": 26, "owner": 41}
EXPECTED_MAPPING_COUNTS = {"jockey": 2, "trainer": 52, "owner": 95}
EXPECTED_JOCKEY_CANDIDATES = {"accepted": 1, "confirmed_distinct": 1, "unresolved": 214}
EXPECTED_TRAINER_CANDIDATES = {"accepted": 26, "confirmed_distinct": 0, "unresolved": 27}
EXPECTED_OWNER_CANDIDATES = {"accepted": 41, "confirmed_distinct": 0, "unresolved": 895}
EXPECTED_TRAINER_MAPPED_RUNNER_ROWS = 6_350
EXPECTED_OWNER_MAPPED_RUNNER_ROWS = 9_788
EXPECTED_OWNER_UNRESOLVED_LABELS = 1_822
EXPECTED_OWNER_UNRESOLVED_RUNNER_ROWS = 24_406


class GovernedParticipantIdentityLoadError(RuntimeError):
    """Raised when Notebook 22 governed identity artifacts do not reconcile."""


def _hash_code(namespace: str, *parts: str) -> str:
    payload = "\x1f".join(parts).encode("utf-8")
    return f"{namespace}:{sha256(payload).hexdigest()[:24]}"


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            {key: "" if value is None else value for key, value in row.items()}
            for row in reader
        ]


def _label_code(role: str, raw_label: str) -> str:
    return _hash_code("participant-label", role, raw_label)


def _trainer_candidate_code(strict_key: str) -> str:
    return _hash_code("trainer-candidate", strict_key)


def _owner_candidate_code(token_key: str) -> str:
    return _hash_code("owner-candidate", token_key)


def _owner_key_text(raw_label: str) -> str:
    return " | ".join(owner_token_multiset_key(raw_label))


def _source_label_inventory(
    connection: sqlite3.Connection,
    governance_release_id: int,
) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], int]]:
    label_ids: dict[tuple[str, str], int] = {}
    runner_counts: dict[tuple[str, str], int] = {}
    next_id = 1

    for role in ("jockey", "trainer", "owner"):
        rows = connection.execute(
            f"""
            SELECT "{role}", MIN(date), MAX(date), COUNT(*)
            FROM source_raceform_v1_record
            WHERE structural_status = 'admitted_runner_record'
              AND "{role}" IS NOT NULL
              AND length(trim(CAST("{role}" AS TEXT))) > 0
            GROUP BY "{role}"
            ORDER BY CAST("{role}" AS TEXT)
            """
        ).fetchall()
        if len(rows) != EXPECTED_LABEL_COUNTS[role]:
            raise GovernedParticipantIdentityLoadError(
                f"Expected {EXPECTED_LABEL_COUNTS[role]} populated {role} labels; found {len(rows)}"
            )
        for raw_label, first_date, last_date, source_runner_rows in rows:
            raw_text = str(raw_label)
            key = (role, raw_text)
            label_ids[key] = next_id
            runner_counts[key] = int(source_runner_rows)
            connection.execute(
                """
                INSERT INTO identity_participant_source_label VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    next_id,
                    _label_code(role, raw_text),
                    role,
                    raw_text,
                    str(first_date),
                    str(last_date),
                    int(source_runner_rows),
                    governance_release_id,
                ),
            )
            next_id += 1
    return label_ids, runner_counts


def _insert_candidate(
    connection: sqlite3.Connection,
    *,
    candidate_id: int,
    candidate_code: str,
    role: str,
    candidate_key: str,
    candidate_method: str,
    candidate_structure: str | None,
    evidence_status: str | None,
    identity_relationship: str,
    decision_status: str,
    decision_basis: str,
    confidence: str,
    verification_code: str | None,
    evidence_type: str | None,
    evidence_locator: str | None,
    evidence_accessed_date: str | None,
    review_status: str,
    review_notes: str | None,
    database_action: str,
    governance_release_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO identity_participant_candidate VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            candidate_id,
            candidate_code,
            role,
            candidate_key,
            candidate_method,
            candidate_structure,
            evidence_status,
            identity_relationship,
            decision_status,
            decision_basis,
            confidence,
            verification_code,
            evidence_type,
            evidence_locator,
            evidence_accessed_date,
            review_status,
            review_notes,
            database_action,
            governance_release_id,
        ),
    )


def _insert_candidate_member(
    connection: sqlite3.Connection,
    *,
    candidate_id: int,
    source_label_id: int,
    label_role: str | None,
    governance_release_id: int,
) -> None:
    connection.execute(
        "INSERT INTO identity_participant_candidate_label VALUES (?, ?, ?, ?)",
        (candidate_id, source_label_id, label_role, governance_release_id),
    )


def _jockey_candidates(
    connection: sqlite3.Connection,
    path: Path,
    label_ids: dict[tuple[str, str], int],
    governance_release_id: int,
    start_id: int,
) -> tuple[dict[str, int], int]:
    rows = _load_csv(path)
    if len(rows) != sum(EXPECTED_JOCKEY_CANDIDATES.values()):
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected jockey candidate row count: {len(rows)}"
        )
    code_to_id: dict[str, int] = {}
    counts = {key: 0 for key in EXPECTED_JOCKEY_CANDIDATES}
    next_id = start_id

    for row in rows:
        code = row["candidate_pair_id"]
        relationship = row["identity_relationship"]
        if relationship == "same_person":
            decision_status = "accepted"
        elif relationship == "different_people":
            decision_status = "confirmed_distinct"
        elif relationship == "unresolved":
            decision_status = "unresolved"
        else:
            raise GovernedParticipantIdentityLoadError(
                f"{code}: unsupported jockey relationship {relationship!r}"
            )
        counts[decision_status] += 1
        decision_basis = (
            row["review_reason"]
            or row["review_scope_reason"]
            or "strict title-removal candidate relationship"
        )
        review_status = row["review_scope_status"] or (
            "completed" if decision_status != "unresolved" else "deferred_until_material_use"
        )
        _insert_candidate(
            connection,
            candidate_id=next_id,
            candidate_code=code,
            role="jockey",
            candidate_key=row["strict_comparison_key"],
            candidate_method=row["candidate_generation_method"],
            candidate_structure=row["pair_label_structure"] or None,
            evidence_status=row["verification_status"] or None,
            identity_relationship=relationship,
            decision_status=decision_status,
            decision_basis=decision_basis,
            confidence=row["confidence"],
            verification_code=row["verification_id"] or None,
            evidence_type=row["evidence_type"] or None,
            evidence_locator=row["evidence_locator"] or None,
            evidence_accessed_date=row["evidence_accessed_date"] or None,
            review_status=review_status,
            review_notes=row["review_notes"] or None,
            database_action=row["database_action"],
            governance_release_id=governance_release_id,
        )
        for member_role, column in (
            ("left_candidate_label", "left_raw_jockey_label"),
            ("right_candidate_label", "right_raw_jockey_label"),
        ):
            label = row[column]
            label_id = label_ids.get(("jockey", label))
            if label_id is None:
                raise GovernedParticipantIdentityLoadError(
                    f"{code}: jockey candidate label not present in source: {label!r}"
                )
            _insert_candidate_member(
                connection,
                candidate_id=next_id,
                source_label_id=label_id,
                label_role=member_role,
                governance_release_id=governance_release_id,
            )
        code_to_id[code] = next_id
        next_id += 1

    if counts != EXPECTED_JOCKEY_CANDIDATES:
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected jockey decision partition: {counts!r}"
        )
    return code_to_id, next_id


def _trainer_candidates(
    connection: sqlite3.Connection,
    path: Path,
    label_ids: dict[tuple[str, str], int],
    governance_release_id: int,
    start_id: int,
) -> tuple[dict[str, int], int]:
    rows = _load_csv(path)
    if len(rows) != sum(EXPECTED_TRAINER_CANDIDATES.values()):
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected trainer candidate row count: {len(rows)}"
        )
    key_to_id: dict[str, int] = {}
    counts = {key: 0 for key in EXPECTED_TRAINER_CANDIDATES}
    next_id = start_id

    for row in rows:
        strict_key = row["strict_comparison_key"]
        code = _trainer_candidate_code(strict_key)
        relationship = row["identity_relationship"]
        if relationship == "same_provisional_trainer":
            decision_status = "accepted"
        elif relationship == "unresolved":
            decision_status = "unresolved"
        else:
            raise GovernedParticipantIdentityLoadError(
                f"{strict_key}: unsupported trainer relationship {relationship!r}"
            )
        counts[decision_status] += 1
        _insert_candidate(
            connection,
            candidate_id=next_id,
            candidate_code=code,
            role="trainer",
            candidate_key=strict_key,
            candidate_method="strict_title_removal_comparison",
            candidate_structure=row["title_structure"] or None,
            evidence_status=row["chronology_status"] or None,
            identity_relationship=relationship,
            decision_status=decision_status,
            decision_basis=row["decision_basis"],
            confidence=row["confidence"],
            verification_code=None,
            evidence_type=None,
            evidence_locator=None,
            evidence_accessed_date=None,
            review_status=(
                "accepted_source_internal_rule"
                if decision_status == "accepted"
                else "deferred_until_material_use"
            ),
            review_notes=None,
            database_action=row["database_action"],
            governance_release_id=governance_release_id,
        )
        for member_role, column in (
            ("left_candidate_label", "left_raw_trainer_label"),
            ("right_candidate_label", "right_raw_trainer_label"),
        ):
            label = row[column]
            label_id = label_ids.get(("trainer", label))
            if label_id is None:
                raise GovernedParticipantIdentityLoadError(
                    f"{strict_key}: trainer candidate label not in source: {label!r}"
                )
            _insert_candidate_member(
                connection,
                candidate_id=next_id,
                source_label_id=label_id,
                label_role=member_role,
                governance_release_id=governance_release_id,
            )
        key_to_id[strict_key] = next_id
        next_id += 1

    if counts != EXPECTED_TRAINER_CANDIDATES:
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected trainer decision partition: {counts!r}"
        )
    return key_to_id, next_id


def _owner_labels_by_key(
    label_ids: dict[tuple[str, str], int],
) -> dict[str, list[tuple[str, int]]]:
    grouped: dict[str, list[tuple[str, int]]] = {}
    for (role, raw_label), label_id in label_ids.items():
        if role != "owner":
            continue
        key = _owner_key_text(raw_label)
        grouped.setdefault(key, []).append((raw_label, label_id))
    return grouped


def _owner_candidates(
    connection: sqlite3.Connection,
    path: Path,
    label_ids: dict[tuple[str, str], int],
    runner_counts: dict[tuple[str, str], int],
    governance_release_id: int,
    start_id: int,
) -> tuple[dict[str, int], int]:
    rows = _load_csv(path)
    if len(rows) != sum(EXPECTED_OWNER_CANDIDATES.values()):
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected owner candidate row count: {len(rows)}"
        )
    owner_labels = _owner_labels_by_key(label_ids)
    key_to_id: dict[str, int] = {}
    counts = {key: 0 for key in EXPECTED_OWNER_CANDIDATES}
    unresolved_labels: set[str] = set()
    unresolved_runner_rows = 0
    next_id = start_id

    for row in rows:
        token_key = row["token_multiset_key"]
        code = _owner_candidate_code(token_key)
        relationship = row["identity_relationship"]
        if relationship == "same_provisional_ownership_composition":
            decision_status = "accepted"
        elif relationship == "unresolved":
            decision_status = "unresolved"
        else:
            raise GovernedParticipantIdentityLoadError(
                f"{token_key}: unsupported owner relationship {relationship!r}"
            )
        counts[decision_status] += 1
        candidate_labels = owner_labels.get(token_key, [])
        expected_label_count = int(row["raw_label_count"])
        if len(candidate_labels) != expected_label_count:
            raise GovernedParticipantIdentityLoadError(
                f"Owner candidate {token_key!r} expected {expected_label_count} labels; "
                f"source inventory produced {len(candidate_labels)}"
            )
        expected_runner_rows = int(row["combined_runner_rows"])
        actual_runner_rows = sum(
            runner_counts[("owner", label)] for label, _ in candidate_labels
        )
        if actual_runner_rows != expected_runner_rows:
            raise GovernedParticipantIdentityLoadError(
                f"Owner candidate {token_key!r} runner rows changed: "
                f"{actual_runner_rows} != {expected_runner_rows}"
            )

        _insert_candidate(
            connection,
            candidate_id=next_id,
            candidate_code=code,
            role="owner",
            candidate_key=token_key,
            candidate_method="exact_owner_token_multiset",
            candidate_structure=row["candidate_structure"] or None,
            evidence_status=row["evidence_status"] or None,
            identity_relationship=relationship,
            decision_status=decision_status,
            decision_basis=row["decision_basis"],
            confidence=row["confidence"],
            verification_code=None,
            evidence_type=None,
            evidence_locator=None,
            evidence_accessed_date=None,
            review_status=(
                "accepted_source_internal_rule"
                if decision_status == "accepted"
                else "deferred_until_material_use"
            ),
            review_notes=None,
            database_action=row["database_action"],
            governance_release_id=governance_release_id,
        )
        for label, label_id in sorted(candidate_labels):
            _insert_candidate_member(
                connection,
                candidate_id=next_id,
                source_label_id=label_id,
                label_role="composition_member_label",
                governance_release_id=governance_release_id,
            )
            if decision_status == "unresolved":
                unresolved_labels.add(label)
                unresolved_runner_rows += runner_counts[("owner", label)]
        key_to_id[token_key] = next_id
        next_id += 1

    if counts != EXPECTED_OWNER_CANDIDATES:
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected owner decision partition: {counts!r}"
        )
    if len(unresolved_labels) != EXPECTED_OWNER_UNRESOLVED_LABELS:
        raise GovernedParticipantIdentityLoadError(
            f"Expected {EXPECTED_OWNER_UNRESOLVED_LABELS} unresolved owner labels; "
            f"found {len(unresolved_labels)}"
        )
    if unresolved_runner_rows != EXPECTED_OWNER_UNRESOLVED_RUNNER_ROWS:
        raise GovernedParticipantIdentityLoadError(
            f"Expected {EXPECTED_OWNER_UNRESOLVED_RUNNER_ROWS} unresolved owner runner rows; "
            f"found {unresolved_runner_rows}"
        )
    return key_to_id, next_id


def _identity_rows_from_mapping(
    rows: list[dict[str, str]],
    *,
    identity_code_column: str,
    role: str,
    identity_scope: str,
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row[identity_code_column], []).append(row)
    output = []
    for identity_code, members in sorted(grouped.items()):
        statuses = {row["identity_status"] for row in members}
        methods = {row["mapping_method"] for row in members}
        confidences = {row["confidence"] for row in members}
        if len(statuses) != 1 or len(methods) != 1 or len(confidences) != 1:
            raise GovernedParticipantIdentityLoadError(
                f"Accepted {role} identity {identity_code} has inconsistent mapping metadata"
            )
        output.append(
            {
                "identity_code": identity_code,
                "role": role,
                "scope": identity_scope,
                "identity_status": next(iter(statuses)),
                "identity_method": next(iter(methods)),
                "confidence": next(iter(confidences)),
            }
        )
    return output


def _insert_accepted_identities_and_mappings(
    connection: sqlite3.Connection,
    project_root: Path,
    *,
    governance_release_id: int,
    label_ids: dict[tuple[str, str], int],
    runner_counts: dict[tuple[str, str], int],
    jockey_candidates: dict[str, int],
    trainer_candidates: dict[str, int],
    owner_candidates: dict[str, int],
) -> tuple[int, int]:
    jockey_rows = _load_csv(
        project_root / "data/processed/jockey_identity/jockey_provisional_identity_mapping.csv"
    )
    trainer_rows = _load_csv(
        project_root / "data/processed/trainer_identity/trainer_provisional_identity_mapping.csv"
    )
    owner_rows = _load_csv(
        project_root / "data/processed/owner_identity/owner_provisional_composition_mapping.csv"
    )
    if len(jockey_rows) != EXPECTED_MAPPING_COUNTS["jockey"]:
        raise GovernedParticipantIdentityLoadError("Unexpected accepted jockey mapping count")
    if len(trainer_rows) != EXPECTED_MAPPING_COUNTS["trainer"]:
        raise GovernedParticipantIdentityLoadError("Unexpected accepted trainer mapping count")
    if len(owner_rows) != EXPECTED_MAPPING_COUNTS["owner"]:
        raise GovernedParticipantIdentityLoadError("Unexpected accepted owner mapping count")

    identity_specs = (
        _identity_rows_from_mapping(
            jockey_rows,
            identity_code_column="provisional_jockey_id",
            role="jockey",
            identity_scope="person_label_identity",
        )
        + _identity_rows_from_mapping(
            trainer_rows,
            identity_code_column="provisional_trainer_id",
            role="trainer",
            identity_scope="person_label_identity",
        )
        + _identity_rows_from_mapping(
            owner_rows,
            identity_code_column="provisional_owner_composition_id",
            role="owner",
            identity_scope="ownership_composition",
        )
    )
    observed_identity_counts = {
        role: sum(spec["role"] == role for spec in identity_specs)
        for role in EXPECTED_IDENTITY_COUNTS
    }
    if observed_identity_counts != EXPECTED_IDENTITY_COUNTS:
        raise GovernedParticipantIdentityLoadError(
            f"Unexpected accepted participant identity counts: {observed_identity_counts!r}"
        )

    identity_ids: dict[str, int] = {}
    for identity_id, spec in enumerate(identity_specs, start=1):
        identity_ids[spec["identity_code"]] = identity_id
        connection.execute(
            """
            INSERT INTO identity_participant VALUES (
                ?, ?, ?, ?, ?, ?, ?, 'accepted', '22', ?
            )
            """,
            (
                identity_id,
                spec["identity_code"],
                spec["role"],
                spec["scope"],
                spec["identity_status"],
                spec["identity_method"],
                spec["confidence"],
                governance_release_id,
            ),
        )

    mapping_id = 1
    trainer_mapped_runner_rows = 0
    owner_mapped_runner_rows = 0

    def insert_mapping(
        *,
        role: str,
        identity_code: str,
        raw_label: str,
        candidate_id: int,
        label_role: str | None,
        mapping_method: str,
        confidence: str,
        evidence_reference: str | None,
        database_action: str,
    ) -> None:
        nonlocal mapping_id, trainer_mapped_runner_rows, owner_mapped_runner_rows
        source_label_id = label_ids.get((role, raw_label))
        if source_label_id is None:
            raise GovernedParticipantIdentityLoadError(
                f"Accepted {role} mapping label is absent from source: {raw_label!r}"
            )
        connection.execute(
            """
            INSERT INTO identity_participant_label_map VALUES (
                ?, ?, ?, ?, ?, 'accepted', ?, ?, ?, ?, NULL, NULL, ?
            )
            """,
            (
                mapping_id,
                identity_ids[identity_code],
                source_label_id,
                candidate_id,
                label_role,
                mapping_method,
                confidence,
                evidence_reference,
                database_action,
                governance_release_id,
            ),
        )
        if role == "trainer":
            trainer_mapped_runner_rows += runner_counts[(role, raw_label)]
        elif role == "owner":
            owner_mapped_runner_rows += runner_counts[(role, raw_label)]
        mapping_id += 1

    for row in jockey_rows:
        evidence_reference = row["evidence_reference"] or None
        # The persisted direct mapping is specifically governed by
        # JOCKEY-STRICT-0002; do not use the loose comparison key to select a
        # different unresolved title-removal candidate.
        candidate_id = jockey_candidates.get("JOCKEY-STRICT-0002")
        if candidate_id is None:
            raise GovernedParticipantIdentityLoadError("Missing JOCKEY-STRICT-0002 candidate")
        insert_mapping(
            role="jockey",
            identity_code=row["provisional_jockey_id"],
            raw_label=row["raw_jockey_label"],
            candidate_id=candidate_id,
            label_role=row["label_role"] or None,
            mapping_method=row["mapping_method"],
            confidence=row["confidence"],
            evidence_reference=evidence_reference,
            database_action=row["database_action"],
        )

    for row in trainer_rows:
        candidate_id = trainer_candidates.get(row["strict_comparison_key"])
        if candidate_id is None:
            raise GovernedParticipantIdentityLoadError(
                f"Accepted trainer mapping lacks candidate {row['strict_comparison_key']!r}"
            )
        insert_mapping(
            role="trainer",
            identity_code=row["provisional_trainer_id"],
            raw_label=row["raw_trainer_label"],
            candidate_id=candidate_id,
            label_role=row["label_role"] or None,
            mapping_method=row["mapping_method"],
            confidence=row["confidence"],
            evidence_reference=None,
            database_action=row["database_action"],
        )

    for row in owner_rows:
        candidate_id = owner_candidates.get(row["token_multiset_key"])
        if candidate_id is None:
            raise GovernedParticipantIdentityLoadError(
                f"Accepted owner mapping lacks candidate {row['token_multiset_key']!r}"
            )
        insert_mapping(
            role="owner",
            identity_code=row["provisional_owner_composition_id"],
            raw_label=row["raw_owner_label"],
            candidate_id=candidate_id,
            label_role="composition_member_label",
            mapping_method=row["mapping_method"],
            confidence=row["confidence"],
            evidence_reference=None,
            database_action=row["database_action"],
        )

    if trainer_mapped_runner_rows != EXPECTED_TRAINER_MAPPED_RUNNER_ROWS:
        raise GovernedParticipantIdentityLoadError(
            f"Accepted trainer mappings cover {trainer_mapped_runner_rows} rows, "
            f"expected {EXPECTED_TRAINER_MAPPED_RUNNER_ROWS}"
        )
    if owner_mapped_runner_rows != EXPECTED_OWNER_MAPPED_RUNNER_ROWS:
        raise GovernedParticipantIdentityLoadError(
            f"Accepted owner mappings cover {owner_mapped_runner_rows} rows, "
            f"expected {EXPECTED_OWNER_MAPPED_RUNNER_ROWS}"
        )
    return len(identity_specs), mapping_id - 1


def populate_governed_participant_identity(
    connection: sqlite3.Connection,
    project_root: str | Path,
    *,
    governance_release_id: int,
) -> dict[str, int]:
    """Materialise accepted and unresolved Notebook 22 identity governance."""

    manifest = connection.execute(
        "SELECT governance_release_id, build_status FROM import_manifest WHERE import_manifest_id = 1"
    ).fetchone()
    if manifest != (governance_release_id, "building"):
        raise GovernedParticipantIdentityLoadError(
            f"Participant identity requires the active building manifest; observed {manifest!r}"
        )
    for table in (
        "identity_participant_source_label",
        "identity_participant",
        "identity_participant_candidate",
        "identity_participant_candidate_label",
        "identity_participant_label_map",
    ):
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count:
            raise GovernedParticipantIdentityLoadError(
                f"Participant identity requires empty {table}; found {count} rows"
            )

    root = Path(project_root)
    label_ids, runner_counts = _source_label_inventory(
        connection,
        governance_release_id,
    )

    next_candidate_id = 1
    jockey_candidates, next_candidate_id = _jockey_candidates(
        connection,
        root / "data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv",
        label_ids,
        governance_release_id,
        next_candidate_id,
    )
    trainer_candidates, next_candidate_id = _trainer_candidates(
        connection,
        root / "data/processed/trainer_identity/trainer_strict_title_decisions.csv",
        label_ids,
        governance_release_id,
        next_candidate_id,
    )
    owner_candidates, next_candidate_id = _owner_candidates(
        connection,
        root / "data/processed/owner_identity/owner_token_multiset_decisions.csv",
        label_ids,
        runner_counts,
        governance_release_id,
        next_candidate_id,
    )

    candidate_count = next_candidate_id - 1
    expected_candidates = (
        sum(EXPECTED_JOCKEY_CANDIDATES.values())
        + sum(EXPECTED_TRAINER_CANDIDATES.values())
        + sum(EXPECTED_OWNER_CANDIDATES.values())
    )
    if candidate_count != expected_candidates:
        raise GovernedParticipantIdentityLoadError(
            f"Expected {expected_candidates} participant candidates; built {candidate_count}"
        )

    identities, mappings = _insert_accepted_identities_and_mappings(
        connection,
        root,
        governance_release_id=governance_release_id,
        label_ids=label_ids,
        runner_counts=runner_counts,
        jockey_candidates=jockey_candidates,
        trainer_candidates=trainer_candidates,
        owner_candidates=owner_candidates,
    )
    connection.commit()

    return {
        "source_labels": len(label_ids),
        "candidates": candidate_count,
        "identities": identities,
        "accepted_mappings": mappings,
    }


__all__ = [
    "GovernedParticipantIdentityLoadError",
    "populate_governed_participant_identity",
]
