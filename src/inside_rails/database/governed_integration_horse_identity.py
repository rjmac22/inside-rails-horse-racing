"""Populate Database v2 Notebook 19 horse/pedigree identity structures."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd

# Importing this module deliberately patches the contradiction selector in the
# reusable Notebook 19 implementation so blank pedigree strings do not become
# false competing labels. The independent validator uses the same governed rule.
from inside_rails import horse_pedigree_identity_counts as _identity_counts  # noqa: F401
from inside_rails.horse_pedigree_identity import (
    derive_identity_outputs,
    validate_expected_population,
)


EXPECTED_TRANSITIONS = 353
EXPECTED_CORRECTED = 92
EXPECTED_DIFFERENT_HORSE = 261
EXPECTED_UNRESOLVED = 0
EXPECTED_OCCURRENCES = 611


class GovernedHorseIdentityLoadError(RuntimeError):
    """Raised when Notebook 19 outputs cannot be reconciled to Database v2."""


def _decision_code(horse: str, from_group: int, to_group: int) -> str:
    payload = f"{horse}\x1f{from_group}\x1f{to_group}".encode("utf-8")
    return f"horse-transition:{sha256(payload).hexdigest()[:24]}"


def _dam_key_parts(value: object) -> tuple[str, str | None, str | None]:
    if not isinstance(value, tuple) or len(value) != 3:
        raise GovernedHorseIdentityLoadError(
            f"Unexpected structured dam key: {value!r}"
        )
    kind, name, country = value
    kind_text = str(kind)
    if kind_text not in {"blank", "parsed_suffix", "raw_unsuffixed"}:
        raise GovernedHorseIdentityLoadError(
            f"Unexpected structured dam key kind: {kind_text!r}"
        )
    name_text = None if name is None or str(name) == "" else str(name)
    country_text = None if country is None or pd.isna(country) or str(country) == "" else str(country)
    return kind_text, name_text, country_text


def _optional_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value)
    return text if text != "" else None


def _optional_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def _specialist_ids_by_horse(connection: sqlite3.Connection) -> dict[str, int]:
    rows = connection.execute(
        """
        SELECT source_horse_label, horse_pedigree_specialist_decision_id
        FROM governance_horse_pedigree_specialist_decision
        """
    ).fetchall()
    mapping: dict[str, int] = {}
    for horse, decision_id in rows:
        horse_text = str(horse)
        if horse_text in mapping:
            raise GovernedHorseIdentityLoadError(
                f"Notebook 19 specialist governance contains duplicate horse {horse_text!r}"
            )
        mapping[horse_text] = int(decision_id)
    return mapping


def _group_occurrence_mapping(
    separated_groups: pd.DataFrame,
    transitions: pd.DataFrame,
) -> dict[tuple[str, int], str]:
    transition_split = {
        (str(row.horse), int(row.group_number)): (
            None if pd.isna(row.identity_split) else bool(row.identity_split)
        )
        for row in transitions.itertuples(index=False)
    }
    mapping: dict[tuple[str, int], str] = {}
    for horse, groups in separated_groups.groupby("horse", sort=False):
        occurrence_sequence = 1
        ordered = groups.sort_values("group_number", kind="stable")
        for item in ordered.itertuples(index=False):
            group_number = int(item.group_number)
            if group_number > 1:
                previous_boundary = transition_split.get((str(horse), group_number - 1))
                if previous_boundary is None:
                    raise GovernedHorseIdentityLoadError(
                        f"Missing/resolution-null transition before {horse!r} group {group_number}"
                    )
                if previous_boundary:
                    occurrence_sequence += 1
            mapping[(str(horse), group_number)] = (
                f"{horse}::{occurrence_sequence:02d}"
            )
    return mapping


def _runner_assignment_frame(outputs: Any) -> pd.DataFrame:
    separated = outputs.separated_groups[
        ["horse", "sire", "dam_structured_key", "damsire", "group_number"]
    ].copy()
    rows = outputs.structured_rows.loc[
        outputs.structured_rows["horse"].isin(separated["horse"].unique())
    ].copy()
    assignments = rows.merge(
        separated,
        on=["horse", "sire", "dam_structured_key", "damsire"],
        how="inner",
        validate="many_to_one",
    )
    if assignments["source_rowid"].duplicated().any():
        raise GovernedHorseIdentityLoadError(
            "Notebook 19 runner assignment duplicated an immutable source row"
        )

    occurrence_by_group = _group_occurrence_mapping(
        outputs.separated_groups,
        outputs.transition_governance,
    )
    assignments["provisional_occurrence_id"] = [
        occurrence_by_group[(str(horse), int(group_number))]
        for horse, group_number in zip(
            assignments["horse"],
            assignments["group_number"],
            strict=True,
        )
    ]
    expected_rows = int(outputs.provisional_occurrences["runner_rows"].sum())
    if len(assignments) != expected_rows:
        raise GovernedHorseIdentityLoadError(
            "Notebook 19 assignment count does not reconcile with occurrence summaries: "
            f"{len(assignments)} != {expected_rows}"
        )
    return assignments[["source_rowid", "group_number", "provisional_occurrence_id"]]


def _runner_participation_ids(
    connection: sqlite3.Connection,
    source_rowids: list[int],
) -> dict[int, int]:
    result: dict[int, int] = {}
    for start in range(0, len(source_rowids), 800):
        batch = source_rowids[start : start + 800]
        placeholders = ",".join("?" for _ in batch)
        rows = connection.execute(
            f"""
            SELECT source.source_rowid, runner.runner_participation_id
            FROM source_raceform_v1_record AS source
            JOIN core_runner_participation AS runner
              ON runner.source_record_id = source.source_record_id
            WHERE source.source_rowid IN ({placeholders})
            """,
            batch,
        ).fetchall()
        for source_rowid, runner_participation_id in rows:
            result[int(source_rowid)] = int(runner_participation_id)
    if len(result) != len(source_rowids):
        missing = sorted(set(source_rowids) - set(result))[:10]
        raise GovernedHorseIdentityLoadError(
            f"Notebook 19 assignments lost source-backed runner lineage: {missing!r}"
        )
    return result


def populate_governed_horse_identity(
    connection: sqlite3.Connection,
    project_root: str | Path,
    *,
    governance_release_id: int,
) -> dict[str, int]:
    """Rebuild Notebook 19 and materialise its governed relational structures."""

    manifest = connection.execute(
        "SELECT governance_release_id, build_status FROM import_manifest WHERE import_manifest_id = 1"
    ).fetchone()
    if manifest != (governance_release_id, "building"):
        raise GovernedHorseIdentityLoadError(
            f"Horse identity requires the active building manifest; observed {manifest!r}"
        )
    for table in (
        "identity_horse_occurrence",
        "identity_runner_horse_occurrence",
        "identity_horse_pedigree_decision",
    ):
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count:
            raise GovernedHorseIdentityLoadError(
                f"Horse identity requires empty {table}; found {count} rows"
            )

    root = Path(project_root)
    source_path = (
        root
        / "data/raw/form_2015-present/form_2015-present/raceform.db"
    )
    governance_path = root / "data/reference/horse_pedigree_identity_governance.csv"
    outputs = derive_identity_outputs(source_path, governance_path)
    validate_expected_population(outputs)

    transitions = outputs.transition_governance.sort_values(
        ["horse", "group_number"], kind="stable"
    ).reset_index(drop=True)
    outcome_counts = transitions["analytical_outcome"].value_counts().to_dict()
    if len(transitions) != EXPECTED_TRANSITIONS or outcome_counts != {
        "Different horse": EXPECTED_DIFFERENT_HORSE,
        "Corrected": EXPECTED_CORRECTED,
    }:
        raise GovernedHorseIdentityLoadError(
            f"Unexpected Notebook 19 transition partition: {outcome_counts!r}"
        )
    if int(transitions["analytical_outcome"].eq("Unresolved").sum()) != EXPECTED_UNRESOLVED:
        raise GovernedHorseIdentityLoadError("Notebook 19 unexpectedly regained an unresolved transition")

    occurrences = outputs.provisional_occurrences.sort_values(
        ["horse", "occurrence_sequence"], kind="stable"
    ).reset_index(drop=True)
    if len(occurrences) != EXPECTED_OCCURRENCES:
        raise GovernedHorseIdentityLoadError(
            f"Expected {EXPECTED_OCCURRENCES} provisional occurrences; found {len(occurrences)}"
        )

    occurrence_id_by_code: dict[str, int] = {}
    for occurrence_id, row in enumerate(occurrences.itertuples(index=False), start=1):
        code = str(row.provisional_occurrence_id)
        occurrence_id_by_code[code] = occurrence_id
        connection.execute(
            """
            INSERT INTO identity_horse_occurrence VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                occurrence_id,
                code,
                str(row.horse),
                int(row.occurrence_sequence),
                int(row.pedigree_groups),
                int(row.runner_rows),
                pd.Timestamp(row.first_date).date().isoformat(),
                pd.Timestamp(row.last_date).date().isoformat(),
                _optional_int(row.minimum_age),
                _optional_int(row.maximum_age),
                str(row.sex_values),
                int(row.unresolved_boundaries),
                governance_release_id,
            ),
        )

    specialist_by_horse = _specialist_ids_by_horse(connection)
    for decision_id, row in enumerate(transitions.itertuples(index=False), start=1):
        from_kind, from_name, from_country = _dam_key_parts(row.dam_structured_key)
        to_kind, to_name, to_country = _dam_key_parts(row.next_dam_structured_key)
        identity_split = None if pd.isna(row.identity_split) else int(bool(row.identity_split))
        connection.execute(
            """
            INSERT INTO identity_horse_pedigree_decision (
                horse_pedigree_decision_id, horse_pedigree_decision_code,
                source_horse_label, from_pedigree_group_number,
                to_pedigree_group_number, from_sire, from_dam_key_kind,
                from_dam_name, from_dam_country, from_damsire,
                from_first_date, from_last_date, from_minimum_age,
                from_maximum_age, from_runner_rows, from_provisional_races,
                to_sire, to_dam_key_kind, to_dam_name, to_dam_country,
                to_damsire, to_first_date, to_minimum_age, gap_days,
                sire_changed, dam_changed, damsire_changed,
                pedigree_components_changed, analytical_outcome,
                decision_basis, identity_split,
                horse_pedigree_specialist_decision_id, governance_release_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                decision_id,
                _decision_code(str(row.horse), int(row.group_number), int(row.group_number) + 1),
                str(row.horse),
                int(row.group_number),
                int(row.group_number) + 1,
                _optional_text(row.sire),
                from_kind,
                from_name,
                from_country,
                _optional_text(row.damsire),
                pd.Timestamp(row.first_date).date().isoformat(),
                pd.Timestamp(row.last_date).date().isoformat(),
                _optional_int(row.minimum_age),
                _optional_int(row.maximum_age),
                int(row.runner_rows),
                int(row.provisional_races),
                _optional_text(row.next_sire),
                to_kind,
                to_name,
                to_country,
                _optional_text(row.next_damsire),
                pd.Timestamp(row.next_first_date).date().isoformat(),
                _optional_int(row.next_minimum_age),
                int(row.gap_days),
                int(bool(row.sire_changed)),
                int(bool(row.dam_changed)),
                int(bool(row.damsire_changed)),
                int(row.pedigree_components_changed),
                str(row.analytical_outcome),
                str(row.decision_basis),
                identity_split,
                specialist_by_horse.get(str(row.horse)),
                governance_release_id,
            ),
        )

    assignments = _runner_assignment_frame(outputs)
    source_rowids = [int(value) for value in assignments["source_rowid"].tolist()]
    runner_ids = _runner_participation_ids(connection, source_rowids)
    insert_rows = []
    for row in assignments.itertuples(index=False):
        occurrence_code = str(row.provisional_occurrence_id)
        insert_rows.append(
            (
                runner_ids[int(row.source_rowid)],
                occurrence_id_by_code[occurrence_code],
                int(row.group_number),
                governance_release_id,
            )
        )
    connection.executemany(
        "INSERT INTO identity_runner_horse_occurrence VALUES (?, ?, ?, ?)",
        insert_rows,
    )
    connection.commit()

    observed_assignments = int(
        connection.execute("SELECT COUNT(*) FROM identity_runner_horse_occurrence").fetchone()[0]
    )
    if observed_assignments != len(assignments):
        raise GovernedHorseIdentityLoadError(
            f"Persisted horse assignments changed: {observed_assignments} != {len(assignments)}"
        )

    return {
        "transitions": len(transitions),
        "corrected": int(outcome_counts.get("Corrected", 0)),
        "different_horse": int(outcome_counts.get("Different horse", 0)),
        "unresolved": int(outcome_counts.get("Unresolved", 0)),
        "occurrences": len(occurrences),
        "runner_assignments": observed_assignments,
    }


__all__ = [
    "GovernedHorseIdentityLoadError",
    "populate_governed_horse_identity",
]
