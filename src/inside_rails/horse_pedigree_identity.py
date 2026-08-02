"""Derive governed horse and pedigree identity decisions from the source database."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3

import pandas as pd

DATA_ROW_PREDICATE = "rowid <> 1"
COUNTRY_SUFFIX = re.compile(r"^(?P<name>.*?)(?:\s*\((?P<country>[A-Z]{2,3})\)|\s+(?P<bare>[A-Z]{2,3}))$")

FULL_PEDIGREE_CONTINUITY_EXCEPTIONS = {"Felix Felicis (FR)"}
PARTIAL_PEDIGREE_SPLITS = {
    "Lyneham (FR)",
    "Marakan (IRE)",
    "What A Whopper (IRE)",
}
PENDING_AUTHORITY_CASES = {
    "Almavillalobas (GB)",
    "Colwyn Bay (FR)",
    "Diamond Tipp (IRE)",
    "LAziza Des Places (FR)",
    "Runninsonofagun (IRE)",
}

EXPECTED_SEPARATED_LABELS = 350
EXPECTED_SEPARATED_GROUPS = 703
EXPECTED_TRANSITIONS = 353
EXPECTED_CORRECTED_TRANSITIONS = 87
EXPECTED_DIFFERENT_HORSE_TRANSITIONS = 261
EXPECTED_UNRESOLVED_TRANSITIONS = 5
EXPECTED_PROVISIONAL_OCCURRENCES = 611


@dataclass(frozen=True)
class IdentityOutputs:
    structured_groups: pd.DataFrame
    transition_governance: pd.DataFrame
    provisional_occurrences: pd.DataFrame


def parse_dam_label(raw_value: object) -> tuple[str, str | None, str]:
    """Return reversible dam name, country suffix and observed format."""
    if raw_value is None or pd.isna(raw_value):
        return "", None, "blank"
    raw = str(raw_value).strip()
    if not raw:
        return "", None, "blank"
    match = COUNTRY_SUFFIX.fullmatch(raw)
    if not match:
        return raw, None, "unsuffixed"
    country = match.group("country") or match.group("bare")
    suffix_format = "parenthesized" if match.group("country") else "bare"
    return match.group("name").strip(), country, suffix_format


def load_source_rows(database_path: str | Path) -> pd.DataFrame:
    """Load only fields required for the source-wide identity derivation."""
    path = Path(database_path)
    if not path.exists():
        raise FileNotFoundError(path)
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        rows = pd.read_sql_query(
            f"""
            SELECT
                rowid AS source_rowid,
                date,
                course,
                off,
                horse,
                sire,
                dam,
                damsire,
                age,
                sex
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            """,
            connection,
        )
    finally:
        connection.close()
    rows["date"] = pd.to_datetime(rows["date"], errors="raise")
    rows["age"] = pd.to_numeric(rows["age"], errors="coerce")
    for field in ("horse", "sire", "dam", "damsire", "sex"):
        rows[field] = rows[field].fillna("").astype(str)
    return rows


def build_structured_groups(source_rows: pd.DataFrame) -> pd.DataFrame:
    """Build exact-label pedigree assertion groups and their observed histories."""
    required = {"horse", "sire", "dam", "damsire", "date", "age", "sex", "course", "off"}
    missing = required.difference(source_rows.columns)
    if missing:
        raise ValueError(f"missing source columns: {sorted(missing)}")

    rows = source_rows.copy()
    parsed = rows["dam"].map(parse_dam_label)
    rows[["dam_name", "dam_country", "dam_suffix_format"]] = pd.DataFrame(
        parsed.tolist(), index=rows.index
    )
    rows["dam_structured_key"] = list(
        zip(rows["dam_name"], rows["dam_country"], strict=True)
    )

    repeated = rows.groupby("horse").size().loc[lambda values: values.gt(1)].index
    repeated_rows = rows.loc[rows["horse"].isin(repeated)].copy()

    groups = (
        repeated_rows.groupby(
            ["horse", "sire", "dam_structured_key", "damsire"],
            dropna=False,
            as_index=False,
        )
        .agg(
            runner_rows=("source_rowid", "size"),
            provisional_races=("off", "size"),
            first_date=("date", "min"),
            last_date=("date", "max"),
            minimum_age=("age", "min"),
            maximum_age=("age", "max"),
            distinct_sexes=("sex", "nunique"),
            sex_values=("sex", lambda values: " | ".join(dict.fromkeys(values))),
            raw_dam_labels=("dam", lambda values: " | ".join(dict.fromkeys(values))),
            dam_suffix_formats=(
                "dam_suffix_format",
                lambda values: " | ".join(dict.fromkeys(values)),
            ),
            course_examples=("course", lambda values: " | ".join(dict.fromkeys(values))[:500]),
        )
        .sort_values(["horse", "first_date", "last_date"], kind="stable")
        .reset_index(drop=True)
    )
    groups["group_number"] = groups.groupby("horse").cumcount() + 1
    groups["groups_for_label"] = groups.groupby("horse")["horse"].transform("size")
    return groups


def select_temporally_separated_groups(structured_groups: pd.DataFrame) -> pd.DataFrame:
    """Retain contradiction labels whose ordered assertion groups do not overlap."""
    candidates = structured_groups.loc[structured_groups["groups_for_label"].gt(1)].copy()
    candidates["previous_last_date"] = candidates.groupby("horse")["last_date"].shift()
    candidates["boundary_separate"] = (
        candidates["previous_last_date"].isna()
        | candidates["first_date"].gt(candidates["previous_last_date"])
    )
    separated_labels = (
        candidates.groupby("horse")["boundary_separate"].all().loc[lambda values: values].index
    )
    return candidates.loc[candidates["horse"].isin(separated_labels)].reset_index(drop=True)


def build_transition_governance(separated_groups: pd.DataFrame) -> pd.DataFrame:
    """Classify each ordered pedigree boundary into the three analytical outcomes."""
    groups = separated_groups.sort_values(["horse", "group_number"], kind="stable").copy()
    next_columns = ["sire", "dam_structured_key", "damsire", "first_date", "minimum_age"]
    for column in next_columns:
        groups[f"next_{column}"] = groups.groupby("horse")[column].shift(-1)
    transitions = groups.loc[groups["next_first_date"].notna()].copy()
    transitions["sire_changed"] = transitions["sire"].ne(transitions["next_sire"])
    transitions["dam_changed"] = transitions["dam_structured_key"].ne(
        transitions["next_dam_structured_key"]
    )
    transitions["damsire_changed"] = transitions["damsire"].ne(
        transitions["next_damsire"]
    )
    transitions["pedigree_components_changed"] = transitions[
        ["sire_changed", "dam_changed", "damsire_changed"]
    ].sum(axis=1)
    transitions["next_first_date"] = pd.to_datetime(transitions["next_first_date"])
    transitions["gap_days"] = (
        transitions["next_first_date"] - transitions["last_date"]
    ).dt.days

    transitions["analytical_outcome"] = "Corrected"
    transitions["decision_basis"] = "bounded_continuity_or_source_correction"

    full_change = transitions["pedigree_components_changed"].eq(3)
    full_split = full_change & ~transitions["horse"].isin(FULL_PEDIGREE_CONTINUITY_EXCEPTIONS)
    transitions.loc[full_split, "analytical_outcome"] = "Different horse"
    transitions.loc[full_split, "decision_basis"] = (
        "complete_pedigree_change_with_separated_chronology"
    )

    partial_split = transitions["horse"].isin(PARTIAL_PEDIGREE_SPLITS)
    transitions.loc[partial_split, "analytical_outcome"] = "Different horse"
    transitions.loc[partial_split, "decision_basis"] = (
        "material_partial_pedigree_change_with_separated_chronology"
    )

    pending = transitions["horse"].isin(PENDING_AUTHORITY_CASES)
    transitions.loc[pending, "analytical_outcome"] = "Unresolved"
    transitions.loc[pending, "decision_basis"] = "pending_official_confirmation"

    transitions["identity_split"] = transitions["analytical_outcome"].eq("Different horse")
    transitions.loc[transitions["analytical_outcome"].eq("Unresolved"), "identity_split"] = pd.NA
    return transitions.reset_index(drop=True)


def build_provisional_occurrences(
    separated_groups: pd.DataFrame, transition_governance: pd.DataFrame
) -> pd.DataFrame:
    """Assign source-internal occurrence sequences at governed split boundaries."""
    boundaries = transition_governance[
        ["horse", "group_number", "analytical_outcome", "identity_split", "decision_basis"]
    ].copy()
    boundaries["target_group_number"] = boundaries["group_number"] + 1
    boundaries = boundaries.rename(
        columns={
            "analytical_outcome": "boundary_outcome",
            "identity_split": "split_before_group",
            "decision_basis": "boundary_basis",
        }
    )
    groups = separated_groups.merge(
        boundaries[
            [
                "horse",
                "target_group_number",
                "boundary_outcome",
                "split_before_group",
                "boundary_basis",
            ]
        ],
        how="left",
        left_on=["horse", "group_number"],
        right_on=["horse", "target_group_number"],
        validate="one_to_one",
    ).drop(columns=["target_group_number"])
    groups["split_before_group"] = groups["split_before_group"].fillna(False).astype(bool)
    groups["occurrence_sequence"] = (
        groups.groupby("horse")["split_before_group"].cumsum().astype(int) + 1
    )
    groups["provisional_occurrence_id"] = (
        groups["horse"] + "::" + groups["occurrence_sequence"].astype(str).str.zfill(2)
    )
    occurrences = (
        groups.groupby(
            ["horse", "occurrence_sequence", "provisional_occurrence_id"],
            as_index=False,
        )
        .agg(
            pedigree_groups=("group_number", "size"),
            runner_rows=("runner_rows", "sum"),
            first_date=("first_date", "min"),
            last_date=("last_date", "max"),
            minimum_age=("minimum_age", "min"),
            maximum_age=("maximum_age", "max"),
            sex_values=("sex_values", lambda values: " | ".join(dict.fromkeys(values))),
            unresolved_boundaries=(
                "boundary_outcome",
                lambda values: sum(value == "Unresolved" for value in values),
            ),
        )
        .sort_values(["horse", "occurrence_sequence"], kind="stable")
        .reset_index(drop=True)
    )
    return occurrences


def derive_identity_outputs(database_path: str | Path) -> IdentityOutputs:
    """Run the complete source-wide Notebook 19 derivation."""
    source_rows = load_source_rows(database_path)
    structured_groups = build_structured_groups(source_rows)
    separated_groups = select_temporally_separated_groups(structured_groups)
    transitions = build_transition_governance(separated_groups)
    occurrences = build_provisional_occurrences(separated_groups, transitions)
    return IdentityOutputs(separated_groups, transitions, occurrences)


def validate_expected_population(outputs: IdentityOutputs) -> None:
    """Fail loudly when the governed source population changes unexpectedly."""
    groups = outputs.structured_groups
    transitions = outputs.transition_governance
    occurrences = outputs.provisional_occurrences
    outcome_counts = transitions["analytical_outcome"].value_counts().to_dict()

    assert groups["horse"].nunique() == EXPECTED_SEPARATED_LABELS
    assert len(groups) == EXPECTED_SEPARATED_GROUPS
    assert len(transitions) == EXPECTED_TRANSITIONS
    assert outcome_counts == {
        "Different horse": EXPECTED_DIFFERENT_HORSE_TRANSITIONS,
        "Corrected": EXPECTED_CORRECTED_TRANSITIONS,
        "Unresolved": EXPECTED_UNRESOLVED_TRANSITIONS,
    }
    assert len(occurrences) == EXPECTED_PROVISIONAL_OCCURRENCES
    assert occurrences["provisional_occurrence_id"].is_unique
