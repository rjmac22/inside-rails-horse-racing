"""Derive governed horse and pedigree identity decisions from the source database."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
from typing import Collection

import pandas as pd

DATA_ROW_PREDICATE = "rowid <> 1"
PARENTHESIZED_SUFFIX = re.compile(
    r"^(?P<name>.*?)\s*\((?P<country>[A-Z]{2,3})\)$"
)
BARE_SUFFIX = re.compile(r"^(?P<name>.*?)\s+(?P<country>[A-Z]{2,3})$")

DEFAULT_COUNTRY_SUFFIXES = frozenset(
    {
        "ARG", "AUS", "AUT", "BEL", "BHR", "BRZ", "CAN", "CHI", "CHN",
        "CZE", "DEN", "FR", "GB", "GER", "HK", "HUN", "IND", "IRE", "ITY",
        "JPN", "KOR", "KSA", "MEX", "NZ", "PER", "POL", "QAT", "SAF", "SIN",
        "SPA", "SWE", "SWI", "TUR", "UAE", "URU", "USA", "VEN", "ZIM",
    }
)

GOVERNANCE_COLUMNS = (
    "decision_id",
    "horse",
    "decision_scope",
    "analytical_outcome",
    "raw_sire",
    "raw_dam",
    "raw_damsire",
    "governed_sire",
    "governed_dam",
    "governed_damsire",
    "verification_status",
    "verification_id",
    "evidence_locator",
    "confidence",
    "notes",
)
ALLOWED_OUTCOMES = {"Corrected", "Different horse", "Unresolved"}
ALLOWED_STATUSES = {"confirmed", "unresolved"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}

EXPECTED_GOVERNANCE_ROWS = 16
EXPECTED_RAW_CONTRADICTION_LABELS = 5_573
EXPECTED_STRUCTURED_CONTRADICTION_LABELS = 368
EXPECTED_STRUCTURED_PEDIGREE_ROWS = 96_404
EXPECTED_STRUCTURED_PEDIGREE_GROUPS = 741
EXPECTED_SEPARATED_LABELS = 350
EXPECTED_SEPARATED_GROUPS = 703
EXPECTED_TRANSITIONS = 353
EXPECTED_CORRECTED_TRANSITIONS = 87
EXPECTED_DIFFERENT_HORSE_TRANSITIONS = 261
EXPECTED_UNRESOLVED_TRANSITIONS = 5
EXPECTED_PROVISIONAL_OCCURRENCES = 611


@dataclass(frozen=True)
class IdentityGovernance:
    rows: pd.DataFrame
    full_pedigree_corrections: frozenset[str]
    explicit_partial_splits: frozenset[str]
    unresolved_horses: frozenset[str]


@dataclass(frozen=True)
class IdentityOutputs:
    structured_rows: pd.DataFrame
    structured_groups: pd.DataFrame
    separated_groups: pd.DataFrame
    transition_governance: pd.DataFrame
    provisional_occurrences: pd.DataFrame
    raw_contradiction_labels: int
    structured_contradiction_labels: int


def parse_dam_label(
    raw_value: object,
    allowed_bare_suffixes: Collection[str] = DEFAULT_COUNTRY_SUFFIXES,
) -> tuple[str, str | None, str]:
    """Return reversible dam name, country suffix and observed format."""
    if raw_value is None or pd.isna(raw_value):
        return "", None, "blank"
    raw = str(raw_value).strip()
    if not raw:
        return "", None, "blank"

    parenthesized = PARENTHESIZED_SUFFIX.fullmatch(raw)
    if parenthesized:
        return (
            parenthesized.group("name").strip(),
            parenthesized.group("country"),
            "parenthesized",
        )

    bare = BARE_SUFFIX.fullmatch(raw)
    if bare and bare.group("country") in allowed_bare_suffixes:
        return bare.group("name").strip(), bare.group("country"), "bare"

    return raw, None, "unsuffixed"


def structured_dam_key(
    raw_value: object,
    allowed_bare_suffixes: Collection[str] = DEFAULT_COUNTRY_SUFFIXES,
) -> tuple[str, str, str | None]:
    """Create the Notebook 19 reversible dam key."""
    name, country, suffix_format = parse_dam_label(raw_value, allowed_bare_suffixes)
    if suffix_format == "blank":
        return "blank", "", None
    if suffix_format in {"parenthesized", "bare"}:
        return "parsed_suffix", name, country
    return "raw_unsuffixed", name, None


def load_identity_governance(path: str | Path) -> IdentityGovernance:
    """Load and validate the specialist Notebook 19 governance reference."""
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if tuple(frame.columns) != GOVERNANCE_COLUMNS:
        raise ValueError("horse pedigree governance columns do not match the governed schema")
    if len(frame) != EXPECTED_GOVERNANCE_ROWS:
        raise ValueError(
            f"expected {EXPECTED_GOVERNANCE_ROWS} governance rows, found {len(frame)}"
        )
    if frame["decision_id"].eq("").any() or not frame["decision_id"].is_unique:
        raise ValueError("decision_id values must be populated and unique")
    if frame["horse"].eq("").any():
        raise ValueError("horse values must not be blank")

    invalid_outcomes = set(frame["analytical_outcome"]) - ALLOWED_OUTCOMES
    if invalid_outcomes:
        raise ValueError(f"invalid analytical outcomes: {sorted(invalid_outcomes)}")
    invalid_statuses = set(frame["verification_status"]) - ALLOWED_STATUSES
    if invalid_statuses:
        raise ValueError(f"invalid verification statuses: {sorted(invalid_statuses)}")
    invalid_confidence = set(frame["confidence"]) - ALLOWED_CONFIDENCE
    if invalid_confidence:
        raise ValueError(f"invalid confidence values: {sorted(invalid_confidence)}")
    if frame["verification_id"].eq("").any():
        raise ValueError("verification_id values must not be blank")
    if frame["evidence_locator"].eq("").any():
        raise ValueError("evidence_locator values must not be blank")

    unresolved = frame["analytical_outcome"].eq("Unresolved")
    if not frame.loc[unresolved, "verification_status"].eq("unresolved").all():
        raise ValueError("unresolved outcomes must have unresolved verification status")
    governed_columns = ["governed_sire", "governed_dam", "governed_damsire"]
    if frame.loc[unresolved, governed_columns].ne("").any(axis=None):
        raise ValueError("unresolved rows must not assign governed pedigree values")

    full_corrections = frozenset(
        frame.loc[
            frame["analytical_outcome"].eq("Corrected")
            & frame["decision_scope"].eq("complete_pedigree"),
            "horse",
        ]
    )
    partial_splits = frozenset(
        frame.loc[
            frame["analytical_outcome"].eq("Different horse")
            & frame["decision_scope"].eq("partial_pedigree"),
            "horse",
        ]
    )
    unresolved_horses = frozenset(frame.loc[unresolved, "horse"])
    return IdentityGovernance(
        rows=frame,
        full_pedigree_corrections=full_corrections,
        explicit_partial_splits=partial_splits,
        unresolved_horses=unresolved_horses,
    )


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

    # Preserve null pedigree values. Notebook 19 used pandas nunique with its
    # default dropna=True behaviour, so replacing nulls with empty strings would
    # create false contradiction labels.
    for field in ("horse", "sex", "course", "off"):
        rows[field] = rows[field].fillna("").astype(str)

    rows["race_key"] = list(
        zip(rows["date"], rows["course"], rows["off"], strict=True)
    )
    return rows


def _observed_parenthesized_suffixes(rows: pd.DataFrame) -> frozenset[str]:
    suffixes: set[str] = set(DEFAULT_COUNTRY_SUFFIXES)
    for field in ("horse", "sire", "dam"):
        for value in rows[field].dropna().drop_duplicates():
            match = PARENTHESIZED_SUFFIX.fullmatch(str(value).strip())
            if match:
                suffixes.add(match.group("country"))
    return frozenset(suffixes)


def _contradiction_labels(rows: pd.DataFrame, dam_column: str) -> pd.Index:
    counts = rows.groupby("horse", sort=False).agg(
        sire_values=("sire", "nunique"),
        dam_values=(dam_column, "nunique"),
        damsire_values=("damsire", "nunique"),
    )
    return counts.index[
        counts[["sire_values", "dam_values", "damsire_values"]].gt(1).any(axis=1)
    ]


def _joined_unique(values: pd.Series) -> str:
    return " | ".join(dict.fromkeys(str(value) for value in values if pd.notna(value)))


def build_structured_population(
    source_rows: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, int, int]:
    """Reproduce Notebook 19's raw and structured contradiction stages."""
    required = {
        "source_rowid",
        "horse",
        "sire",
        "dam",
        "damsire",
        "date",
        "age",
        "sex",
        "course",
        "off",
        "race_key",
    }
    missing = required.difference(source_rows.columns)
    if missing:
        raise ValueError(f"missing source columns: {sorted(missing)}")

    rows = source_rows.copy()
    raw_labels = _contradiction_labels(rows, "dam")
    raw_contradiction_rows = rows.loc[rows["horse"].isin(raw_labels)].copy()

    allowed_suffixes = _observed_parenthesized_suffixes(rows)
    parsed = raw_contradiction_rows["dam"].map(
        lambda value: parse_dam_label(value, allowed_suffixes)
    )
    raw_contradiction_rows[
        ["dam_name", "dam_country", "dam_suffix_format"]
    ] = pd.DataFrame(parsed.tolist(), index=raw_contradiction_rows.index)
    raw_contradiction_rows["dam_structured_key"] = raw_contradiction_rows["dam"].map(
        lambda value: structured_dam_key(value, allowed_suffixes)
    )

    structured_labels = _contradiction_labels(
        raw_contradiction_rows, "dam_structured_key"
    )
    remaining_assertion_rows = raw_contradiction_rows.loc[
        raw_contradiction_rows["horse"].isin(structured_labels)
    ].copy()

    groups = (
        remaining_assertion_rows.groupby(
            ["horse", "sire", "dam_structured_key", "damsire"],
            dropna=False,
            as_index=False,
            sort=False,
        )
        .agg(
            runner_rows=("source_rowid", "size"),
            provisional_races=("race_key", "nunique"),
            first_date=("date", "min"),
            last_date=("date", "max"),
            minimum_age=("age", "min"),
            maximum_age=("age", "max"),
            distinct_sexes=("sex", "nunique"),
            sex_values=("sex", _joined_unique),
            raw_dam_labels=("dam", _joined_unique),
            dam_suffix_formats=("dam_suffix_format", _joined_unique),
            course_examples=("course", lambda values: _joined_unique(values)[:500]),
        )
        .sort_values(
            ["horse", "first_date", "last_date", "sire", "damsire"],
            kind="stable",
        )
        .reset_index(drop=True)
    )
    groups["group_number"] = groups.groupby("horse").cumcount() + 1
    groups["groups_for_label"] = groups.groupby("horse")["horse"].transform("size")

    # The notebook retained the complete raw-contradiction population as
    # structured_pedigree_rows after adding reversible dam structure. Only the
    # 368 labels that still contradicted fed the grouped histories.
    return (
        raw_contradiction_rows,
        groups,
        len(raw_labels),
        len(structured_labels),
    )


def build_structured_groups(source_rows: pd.DataFrame) -> pd.DataFrame:
    """Compatibility wrapper returning the structured pedigree groups."""
    _, groups, _, _ = build_structured_population(source_rows)
    return groups


def select_temporally_separated_groups(
    structured_groups: pd.DataFrame,
) -> pd.DataFrame:
    """Retain contradiction labels whose ordered assertion groups do not overlap."""
    candidates = structured_groups.loc[
        structured_groups["groups_for_label"].gt(1)
    ].copy()
    candidates = candidates.sort_values(
        ["horse", "group_number"], kind="stable"
    ).reset_index(drop=True)
    candidates["previous_last_date"] = candidates.groupby("horse")[
        "last_date"
    ].shift()
    candidates["boundary_separate"] = (
        candidates["previous_last_date"].isna()
        | candidates["first_date"].gt(candidates["previous_last_date"])
    )
    separated_labels = (
        candidates.groupby("horse")["boundary_separate"]
        .all()
        .loc[lambda values: values]
        .index
    )
    return candidates.loc[
        candidates["horse"].isin(separated_labels)
    ].reset_index(drop=True)


def build_transition_governance(
    separated_groups: pd.DataFrame,
    governance: IdentityGovernance,
) -> pd.DataFrame:
    """Classify each ordered pedigree boundary into the three analytical outcomes."""
    groups = separated_groups.sort_values(
        ["horse", "group_number"], kind="stable"
    ).copy()
    next_columns = [
        "sire",
        "dam_structured_key",
        "damsire",
        "first_date",
        "minimum_age",
    ]
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
    transitions["next_first_date"] = pd.to_datetime(
        transitions["next_first_date"]
    )
    transitions["gap_days"] = (
        transitions["next_first_date"] - transitions["last_date"]
    ).dt.days

    transitions["analytical_outcome"] = "Corrected"
    transitions["decision_basis"] = "bounded_continuity_or_source_correction"

    full_change = transitions["pedigree_components_changed"].eq(3)
    full_split = full_change & ~transitions["horse"].isin(
        governance.full_pedigree_corrections
    )
    transitions.loc[full_split, "analytical_outcome"] = "Different horse"
    transitions.loc[full_split, "decision_basis"] = (
        "complete_pedigree_change_with_separated_chronology"
    )

    partial_split = transitions["horse"].isin(
        governance.explicit_partial_splits
    )
    transitions.loc[partial_split, "analytical_outcome"] = "Different horse"
    transitions.loc[partial_split, "decision_basis"] = (
        "material_partial_pedigree_change_with_separated_chronology"
    )

    pending = transitions["horse"].isin(governance.unresolved_horses)
    transitions.loc[pending, "analytical_outcome"] = "Unresolved"
    transitions.loc[pending, "decision_basis"] = "pending_official_confirmation"

    transitions["identity_split"] = transitions["analytical_outcome"].eq(
        "Different horse"
    ).astype("boolean")
    transitions.loc[
        transitions["analytical_outcome"].eq("Unresolved"), "identity_split"
    ] = pd.NA

    decision_lookup = governance.rows.set_index("horse")[
        "verification_id"
    ].to_dict()
    transitions["governing_verification_id"] = transitions["horse"].map(
        decision_lookup
    )
    return transitions.reset_index(drop=True)


def build_provisional_occurrences(
    separated_groups: pd.DataFrame,
    transition_governance: pd.DataFrame,
) -> pd.DataFrame:
    """Assign source-internal occurrence sequences at governed split boundaries."""
    boundaries = transition_governance[
        [
            "horse",
            "group_number",
            "analytical_outcome",
            "identity_split",
            "decision_basis",
        ]
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

    groups["split_before_group"] = (
        groups["split_before_group"].fillna(False).astype(bool)
    )
    groups["occurrence_sequence"] = (
        groups.groupby("horse")["split_before_group"].cumsum().astype(int) + 1
    )
    groups["provisional_occurrence_id"] = (
        groups["horse"]
        + "::"
        + groups["occurrence_sequence"].astype(str).str.zfill(2)
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
            sex_values=("sex_values", _joined_unique),
            unresolved_boundaries=(
                "boundary_outcome",
                lambda values: sum(value == "Unresolved" for value in values),
            ),
        )
        .sort_values(["horse", "occurrence_sequence"], kind="stable")
        .reset_index(drop=True)
    )
    return occurrences


def derive_identity_outputs(
    database_path: str | Path,
    governance_path: str | Path,
) -> IdentityOutputs:
    """Run the complete source-wide Notebook 19 derivation."""
    governance = load_identity_governance(governance_path)
    source_rows = load_source_rows(database_path)
    (
        structured_rows,
        structured_groups,
        raw_label_count,
        structured_label_count,
    ) = build_structured_population(source_rows)
    separated_groups = select_temporally_separated_groups(structured_groups)
    transitions = build_transition_governance(separated_groups, governance)
    occurrences = build_provisional_occurrences(separated_groups, transitions)
    return IdentityOutputs(
        structured_rows=structured_rows,
        structured_groups=structured_groups,
        separated_groups=separated_groups,
        transition_governance=transitions,
        provisional_occurrences=occurrences,
        raw_contradiction_labels=raw_label_count,
        structured_contradiction_labels=structured_label_count,
    )


def validate_expected_population(outputs: IdentityOutputs) -> None:
    """Fail loudly when the governed source population changes unexpectedly."""
    structured_rows = outputs.structured_rows
    structured_groups = outputs.structured_groups
    separated_groups = outputs.separated_groups
    transitions = outputs.transition_governance
    occurrences = outputs.provisional_occurrences
    outcome_counts = transitions["analytical_outcome"].value_counts().to_dict()

    assert outputs.raw_contradiction_labels == EXPECTED_RAW_CONTRADICTION_LABELS, (
        outputs.raw_contradiction_labels,
        EXPECTED_RAW_CONTRADICTION_LABELS,
    )
    assert (
        outputs.structured_contradiction_labels
        == EXPECTED_STRUCTURED_CONTRADICTION_LABELS
    ), (
        outputs.structured_contradiction_labels,
        EXPECTED_STRUCTURED_CONTRADICTION_LABELS,
    )
    assert len(structured_rows) == EXPECTED_STRUCTURED_PEDIGREE_ROWS, (
        len(structured_rows),
        EXPECTED_STRUCTURED_PEDIGREE_ROWS,
    )
    assert len(structured_groups) == EXPECTED_STRUCTURED_PEDIGREE_GROUPS, (
        len(structured_groups),
        EXPECTED_STRUCTURED_PEDIGREE_GROUPS,
    )
    assert separated_groups["horse"].nunique() == EXPECTED_SEPARATED_LABELS, (
        separated_groups["horse"].nunique(),
        EXPECTED_SEPARATED_LABELS,
    )
    assert len(separated_groups) == EXPECTED_SEPARATED_GROUPS, (
        len(separated_groups),
        EXPECTED_SEPARATED_GROUPS,
    )
    assert len(transitions) == EXPECTED_TRANSITIONS, (
        len(transitions),
        EXPECTED_TRANSITIONS,
    )
    assert outcome_counts == {
        "Different horse": EXPECTED_DIFFERENT_HORSE_TRANSITIONS,
        "Corrected": EXPECTED_CORRECTED_TRANSITIONS,
        "Unresolved": EXPECTED_UNRESOLVED_TRANSITIONS,
    }, outcome_counts
    assert len(occurrences) == EXPECTED_PROVISIONAL_OCCURRENCES, (
        len(occurrences),
        EXPECTED_PROVISIONAL_OCCURRENCES,
    )
    assert occurrences["provisional_occurrence_id"].is_unique
    assert transitions["analytical_outcome"].notna().all()
