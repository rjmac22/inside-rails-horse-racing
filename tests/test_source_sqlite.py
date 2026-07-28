from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from inside_rails.source_sqlite import (
    PROVISIONAL_RACE_COLUMNS,
    PROVISIONAL_RUNNER_COLUMNS,
    concatenated_key_expression,
    connect_read_only,
    profile_source_database,
    quote_identifier,
    schema_inventory,
    table_columns,
)


SOURCE_COLUMNS = (
    "date",
    "course",
    "off",
    "race_name",
    "horse",
)


def create_source_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE data (
                date TEXT,
                course TEXT,
                off TEXT,
                race_name TEXT,
                horse TEXT
            )
            """
        )
        connection.executemany(
            "INSERT INTO data VALUES (?, ?, ?, ?, ?)",
            [
                SOURCE_COLUMNS,
                ("2026-01-01", "Ascot", "13:00", "Race A", "Horse One"),
                ("2026-01-01", "Ascot", "13:00", "Race A", "Horse Two"),
                ("2026-01-01", "Ascot", "13:30", "Race B", "Horse One"),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def test_quote_identifier_escapes_embedded_quotes() -> None:
    assert quote_identifier('race"name') == '"race""name"'


def test_concatenated_key_expression_requires_columns() -> None:
    with pytest.raises(ValueError, match="At least one column"):
        concatenated_key_expression(())


def test_concatenated_key_expression_is_null_safe() -> None:
    expression = concatenated_key_expression(("course", "off"))
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE sample (course TEXT, off TEXT)")
        connection.execute("INSERT INTO sample VALUES (?, ?)", ("Ascot", None))
        observed = connection.execute(f"SELECT {expression} FROM sample").fetchone()[0]
    finally:
        connection.close()

    assert observed == "Ascot|<NULL>"


def test_connect_read_only_rejects_missing_database(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="SQLite source not found"):
        with connect_read_only(tmp_path / "missing.db"):
            pass


def test_connect_read_only_prevents_source_mutation(tmp_path: Path) -> None:
    database = tmp_path / "source.db"
    create_source_database(database)

    with connect_read_only(database) as connection:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute(
                "INSERT INTO data VALUES (?, ?, ?, ?, ?)",
                ("2026-01-02", "Ascot", "14:00", "Race C", "Horse Three"),
            )


def test_schema_inventory_excludes_internal_sqlite_objects(tmp_path: Path) -> None:
    database = tmp_path / "source.db"
    create_source_database(database)

    with connect_read_only(database) as connection:
        inventory = schema_inventory(connection)

    assert [(item["type"], item["name"]) for item in inventory] == [("table", "data")]


def test_table_columns_returns_declared_order(tmp_path: Path) -> None:
    database = tmp_path / "source.db"
    create_source_database(database)

    with connect_read_only(database) as connection:
        columns = table_columns(connection)

    assert [column["name"] for column in columns] == list(SOURCE_COLUMNS)


def test_profile_source_database_applies_header_exclusion_and_candidate_keys(
    tmp_path: Path,
) -> None:
    database = tmp_path / "source.db"
    create_source_database(database)

    with connect_read_only(database) as connection:
        profile = profile_source_database(connection)

    assert PROVISIONAL_RACE_COLUMNS == ("date", "course", "off", "race_name")
    assert PROVISIONAL_RUNNER_COLUMNS == (
        "date",
        "course",
        "off",
        "race_name",
        "horse",
    )
    assert profile == {
        "table_name": "data",
        "physical_rows": 4,
        "data_rows": 3,
        "apparent_races": 2,
        "provisional_runner_keys": 3,
        "duplicate_rows_under_provisional_runner_key": 0,
        "minimum_date": "2026-01-01",
        "maximum_date": "2026-01-01",
        "quick_check": "ok",
        "schema_objects": 1,
        "declared_columns": 5,
    }


def test_profile_source_database_reports_duplicate_candidate_runner_keys(
    tmp_path: Path,
) -> None:
    database = tmp_path / "source.db"
    create_source_database(database)

    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "INSERT INTO data VALUES (?, ?, ?, ?, ?)",
            ("2026-01-01", "Ascot", "13:00", "Race A", "Horse One"),
        )
        connection.commit()
    finally:
        connection.close()

    with connect_read_only(database) as connection:
        profile = profile_source_database(connection)

    assert profile["data_rows"] == 4
    assert profile["provisional_runner_keys"] == 3
    assert profile["duplicate_rows_under_provisional_runner_key"] == 1
