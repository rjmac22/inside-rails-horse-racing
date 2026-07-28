"""Load and validate the Notebook 02 source-field governance reference."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

EXPECTED_SOURCE_FIELDS: Final[tuple[str, ...]] = (
    "date", "course", "race_id", "off", "race_name", "type", "class",
    "pattern", "rating_band", "age_band", "sex_rest", "dist", "going",
    "ran", "num", "pos", "draw", "ovr_btn", "btn", "horse", "age",
    "sex", "wgt", "hg", "time", "sp", "jockey", "trainer", "prize",
    "or", "rpr", "ts", "sire", "dam", "damsire", "owner", "comment",
)

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "ordinal",
    "source_field",
    "declared_type",
    "grain",
    "field_family",
    "raw_preservation",
    "blank_policy",
    "dash_policy",
    "zero_policy",
    "governed_by",
    "status",
)

ALLOWED_GRAINS: Final[frozenset[str]] = frozenset({"race", "runner"})
ALLOWED_RAW_PRESERVATION: Final[frozenset[str]] = frozenset({"required"})
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {"pending_semantics", "implemented_later"}
)


def load_source_field_governance(path: str | Path) -> pd.DataFrame:
    """Load and validate the governed source-field inventory."""

    frame = pd.read_csv(Path(path), keep_default_na=False)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame]
    if missing_columns:
        raise ValueError(
            "Source-field governance reference is missing required columns: "
            + ", ".join(missing_columns)
        )

    if frame["source_field"].duplicated().any():
        duplicates = sorted(
            frame.loc[frame["source_field"].duplicated(False), "source_field"].unique()
        )
        raise ValueError(f"Duplicate source fields found: {duplicates}")

    ordinals = pd.to_numeric(frame["ordinal"], errors="coerce")
    expected_ordinals = list(range(1, len(frame) + 1))
    if ordinals.isna().any() or ordinals.astype(int).tolist() != expected_ordinals:
        raise ValueError("Source-field ordinals must be contiguous and start at 1.")

    observed_fields = tuple(frame["source_field"])
    if observed_fields != EXPECTED_SOURCE_FIELDS:
        raise ValueError(
            "Source-field governance does not match the governed 37-column schema."
        )

    invalid_grains = sorted(set(frame["grain"]) - ALLOWED_GRAINS)
    if invalid_grains:
        raise ValueError(f"Invalid source-field grains: {invalid_grains}")

    invalid_preservation = sorted(
        set(frame["raw_preservation"]) - ALLOWED_RAW_PRESERVATION
    )
    if invalid_preservation:
        raise ValueError(
            "Every source field must preserve its raw value; invalid values: "
            f"{invalid_preservation}"
        )

    invalid_statuses = sorted(set(frame["status"]) - ALLOWED_STATUSES)
    if invalid_statuses:
        raise ValueError(f"Invalid source-field statuses: {invalid_statuses}")

    policy_columns = ("blank_policy", "dash_policy", "zero_policy", "governed_by")
    for column in policy_columns:
        if frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Source-field governance column must be populated: {column}")

    return frame


def compare_sqlite_schema(
    governance: pd.DataFrame,
    sqlite_columns: list[dict[str, object]],
) -> list[str]:
    """Return human-readable differences between SQLite and governed schema."""

    failures: list[str] = []
    observed_names = tuple(str(column["name"]) for column in sqlite_columns)
    if observed_names != EXPECTED_SOURCE_FIELDS:
        failures.append(
            "SQLite column names/order do not match the governed source schema."
        )

    governed_types = tuple(governance["declared_type"].str.upper())
    observed_types = tuple(str(column["type"]).upper() for column in sqlite_columns)
    if observed_types != governed_types:
        failures.append("SQLite declared types do not match the governance reference.")

    return failures
