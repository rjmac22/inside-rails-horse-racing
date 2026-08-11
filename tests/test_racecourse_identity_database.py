from __future__ import annotations

from pathlib import Path
import sqlite3

from inside_rails.database.racecourse_identity_reference import (
    EXPECTED_COURSE_INVENTORY_COUNT,
    EXPECTED_NOTEBOOK_COUNT,
    EXPECTED_RACECOURSE_IDENTITY_COUNT,
    EXPECTED_SOURCE_LABEL_COUNT,
    EXPECTED_STABLE_COURSE_IDENTITY_COUNT,
    EXPECTED_UNRESOLVED_COUNT,
    RESOLVED_STABLE_COLLAPSES,
    collect_study03_reference,
)
from inside_rails.database.schema import (
    RACECOURSE_IDENTITY_SCHEMA_VERSION,
    create_racecourse_identity_schema,
)
from inside_rails.database.study03_snapshot import require_completed_study03_snapshot


ROOT = Path(__file__).resolve().parents[1]
RACECOURSE_DIR = ROOT / "studies/jurisdictions/great_britain/racecourses"


def test_completed_study03_snapshot_is_unchanged() -> None:
    require_completed_study03_snapshot(ROOT)


def test_completed_study03_reference_population_is_exact() -> None:
    notebooks, mappings, inventory, unresolved = collect_study03_reference(ROOT)

    assert len(notebooks) == EXPECTED_NOTEBOOK_COUNT == 61
    assert len(mappings) == EXPECTED_SOURCE_LABEL_COUNT == 65
    assert (
        len({row["racecourse_identity"] for row in mappings})
        == EXPECTED_RACECOURSE_IDENTITY_COUNT
        == 61
    )
    assert len(inventory) == EXPECTED_COURSE_INVENTORY_COUNT == 90
    assert len(
        {
            (row["racecourse_identity"], row["stable_course_identity"])
            for row in inventory
        }
    ) == EXPECTED_STABLE_COURSE_IDENTITY_COUNT == 86
    assert len(unresolved) == EXPECTED_UNRESOLVED_COUNT == 7


def test_newmarket_has_two_separate_racecourse_notebooks_and_mappings() -> None:
    assert not (RACECOURSE_DIR / "newmarket.ipynb").exists()
    assert (RACECOURSE_DIR / "newmarket_rowley_mile.ipynb").is_file()
    assert (RACECOURSE_DIR / "newmarket_july_course.ipynb").is_file()

    _, mappings, inventory, _ = collect_study03_reference(ROOT)
    newmarket_mappings = {
        row["candidate_course_label"]: (
            row["racecourse_identity"],
            row.get("study03_grouping_name"),
            row.get("racecourse_resolution_method"),
        )
        for row in mappings
        if row["candidate_course_label"] in {"Newmarket", "Newmarket (July)"}
    }
    assert newmarket_mappings == {
        "Newmarket": (
            "Newmarket — Rowley Mile",
            "Newmarket",
            "source_label_convention",
        ),
        "Newmarket (July)": (
            "Newmarket — July Course",
            "Newmarket",
            "explicit_source_label",
        ),
    }

    newmarket_inventory = {
        (row["racecourse_identity"], row["stable_course_identity"])
        for row in inventory
        if str(row["racecourse_identity"]).startswith("Newmarket —")
    }
    assert newmarket_inventory == {
        ("Newmarket — Rowley Mile", "Rowley Mile Course"),
        ("Newmarket — July Course", "July Course"),
    }


def test_study03_only_applies_the_governed_national_identity_collapses() -> None:
    assert RESOLVED_STABLE_COLLAPSES == {
        ("Southwell", "All-Weather Flat Track — Fibresand"): "All-Weather Flat Track",
        ("Southwell", "All-Weather Flat Track — Tapeta"): "All-Weather Flat Track",
        ("Newcastle", "Former Flat Turf Track"): "Flat Track",
        ("Newcastle", "All-Weather Tapeta Track"): "Flat Track",
        ("Windsor", "Traditional Figure-of-Eight Turf Course"): "Windsor Turf Course",
        ("Windsor", "2024/25 Jump Extended Left-Hand Oval"): "Windsor Turf Course",
        ("Windsor", "2025/26 Jump Figure-of-Eight Configuration"): "Windsor Turf Course",
    }


def test_database_v4_schema_can_be_created_from_clean_database() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_racecourse_identity_schema(connection)
        assert (
            connection.execute("PRAGMA user_version").fetchone()[0]
            == RACECOURSE_IDENTITY_SCHEMA_VERSION
        )
        objects = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type IN ('table','view')"
            )
        }
        assert {
            "reference_racecourse_identity",
            "reference_course_racecourse_map",
            "reference_racecourse_course_identity",
            "reference_racecourse_course_inventory",
            "governance_study03_racecourse_notebook",
            "governance_racecourse_unresolved_question",
            "view_gb_racecourse_identity_reference",
            "view_gb_course_track_identities",
            "view_gb_reconciled_race_occurrences_with_racecourse",
        } <= objects
        map_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(reference_course_racecourse_map)"
            )
        }
        assert {
            "study03_grouping_name",
            "racecourse_resolution_method",
            "racecourse_resolution_evidence",
        } <= map_columns
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()
