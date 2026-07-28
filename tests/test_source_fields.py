from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from inside_rails.source_fields import (
    EXPECTED_SOURCE_FIELDS,
    compare_sqlite_schema,
    load_source_field_governance,
)

REFERENCE = Path("data/reference/source_field_governance.csv")


def test_reference_loads_with_all_37_fields() -> None:
    frame = load_source_field_governance(REFERENCE)

    assert len(frame) == 37
    assert tuple(frame["source_field"]) == EXPECTED_SOURCE_FIELDS
    assert frame["raw_preservation"].eq("required").all()
    assert set(frame["grain"]) == {"race", "runner"}


def test_reference_assigns_every_field_to_later_governance() -> None:
    frame = load_source_field_governance(REFERENCE)

    assert frame["governed_by"].str.strip().ne("").all()
    assert frame["status"].isin({"pending_semantics", "implemented_later"}).all()


def test_loader_rejects_missing_required_column(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE).drop(columns=["blank_policy"])
    path = tmp_path / "missing-column.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing required columns: blank_policy"):
        load_source_field_governance(path)


def test_loader_rejects_duplicate_source_field(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE)
    frame.loc[1, "source_field"] = frame.loc[0, "source_field"]
    path = tmp_path / "duplicate.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="Duplicate source fields"):
        load_source_field_governance(path)


def test_loader_rejects_non_contiguous_ordinals(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE)
    frame.loc[2, "ordinal"] = 99
    path = tmp_path / "ordinals.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="ordinals must be contiguous"):
        load_source_field_governance(path)


def test_loader_rejects_schema_reordering(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE)
    frame.loc[[0, 1], "source_field"] = frame.loc[[1, 0], "source_field"].to_numpy()
    path = tmp_path / "reordered.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="does not match the governed 37-column schema"):
        load_source_field_governance(path)


def test_loader_rejects_raw_value_discard_policy(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE)
    frame.loc[0, "raw_preservation"] = "discard"
    path = tmp_path / "discard.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="must preserve its raw value"):
        load_source_field_governance(path)


def test_compare_sqlite_schema_accepts_matching_schema() -> None:
    frame = load_source_field_governance(REFERENCE)
    sqlite_columns = [
        {"name": row.source_field, "type": row.declared_type}
        for row in frame.itertuples(index=False)
    ]

    assert compare_sqlite_schema(frame, sqlite_columns) == []


def test_compare_sqlite_schema_reports_name_and_type_drift() -> None:
    frame = load_source_field_governance(REFERENCE)
    sqlite_columns = [
        {"name": row.source_field, "type": row.declared_type}
        for row in frame.itertuples(index=False)
    ]
    sqlite_columns[0] = {"name": "race_date", "type": "TEXT"}

    assert compare_sqlite_schema(frame, sqlite_columns) == [
        "SQLite column names/order do not match the governed source schema.",
        "SQLite declared types do not match the governance reference.",
    ]
