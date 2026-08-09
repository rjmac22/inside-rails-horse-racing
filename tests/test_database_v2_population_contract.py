from __future__ import annotations

import re
import sqlite3

from inside_rails.database.governed_integration_population import (
    _RACE_INSERT,
    _RUNNER_INSERT,
)
from inside_rails.database.schema import create_governed_integration_schema


def _placeholder_count(sql: str) -> int:
    return len(re.findall(r"\?", sql))


def _column_count(connection: sqlite3.Connection, table: str) -> int:
    return len(connection.execute(f"PRAGMA table_info({table})").fetchall())


def test_race_population_insert_matches_v2_race_extension_width() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_governed_integration_schema(connection)
        assert _placeholder_count(_RACE_INSERT) == _column_count(
            connection,
            "core_source_race_occurrence_governed",
        )
    finally:
        connection.close()


def test_runner_population_insert_matches_v2_runner_extension_width() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_governed_integration_schema(connection)
        assert _placeholder_count(_RUNNER_INSERT) == _column_count(
            connection,
            "core_runner_participation_governed",
        )
    finally:
        connection.close()


def test_v2_study_facing_views_compile_against_empty_schema() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_governed_integration_schema(connection)

        # Selecting from each empty view forces SQLite to resolve every column
        # and dependency. This catches reserved-word quoting mistakes, renamed
        # columns and invalid view dependencies before a full candidate build.
        for view in (
            "view_governed_race_occurrences",
            "view_governed_horse_occurrence_assignments",
            "view_governed_participant_label_identities",
            "view_governed_source_runner_participations",
            "view_governed_runner_records",
        ):
            assert connection.execute(f"SELECT * FROM {view} LIMIT 0").fetchall() == []
    finally:
        connection.close()
