"""Read-only access and structural profiling for the source SQLite database.

The functions in this module deliberately avoid cleaning or rewriting source
values. They provide reusable technical plumbing for notebooks and validation
scripts while keeping analytical interpretation visible in the notebooks.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator, Sequence

HEADER_ROWID = 1
PROVISIONAL_RACE_COLUMNS = ("date", "course", "off", "race_name")
PROVISIONAL_RUNNER_COLUMNS = (*PROVISIONAL_RACE_COLUMNS, "horse")


def quote_identifier(identifier: str) -> str:
    """Return a safely quoted SQLite identifier."""

    return '"' + identifier.replace('"', '""') + '"'


@contextmanager
def connect_read_only(database_path: str | Path) -> Iterator[sqlite3.Connection]:
    """Open an existing SQLite database in read-only URI mode."""

    path = Path(database_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"SQLite source not found: {path}")

    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        yield connection
    finally:
        connection.close()


def concatenated_key_expression(columns: Sequence[str]) -> str:
    """Build a null-safe SQLite expression for a provisional composite key."""

    if not columns:
        raise ValueError("At least one column is required")

    parts = [
        f"COALESCE(CAST({quote_identifier(column)} AS TEXT), '<NULL>')"
        for column in columns
    ]
    return " || '|' || ".join(parts)


def schema_inventory(connection: sqlite3.Connection) -> list[dict[str, object]]:
    """Return user-defined SQLite schema objects in deterministic order."""

    cursor = connection.execute(
        """
        SELECT type, name, tbl_name, rootpage, sql
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """
    )
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def table_columns(
    connection: sqlite3.Connection,
    table_name: str = "data",
) -> list[dict[str, object]]:
    """Return declared SQLite column metadata for one table."""

    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def profile_source_database(
    connection: sqlite3.Connection,
    table_name: str = "data",
    header_rowid: int = HEADER_ROWID,
) -> dict[str, object]:
    """Return the stable structural assertions established by Notebook 01."""

    table = quote_identifier(table_name)
    race_key = concatenated_key_expression(PROVISIONAL_RACE_COLUMNS)
    runner_key = concatenated_key_expression(PROVISIONAL_RUNNER_COLUMNS)

    row = connection.execute(
        f"""
        SELECT
            COUNT(*) AS physical_rows,
            SUM(CASE WHEN rowid <> ? THEN 1 ELSE 0 END) AS data_rows,
            COUNT(DISTINCT CASE WHEN rowid <> ? THEN {race_key} END)
                AS apparent_races,
            COUNT(DISTINCT CASE WHEN rowid <> ? THEN {runner_key} END)
                AS provisional_runner_keys,
            MIN(CASE WHEN rowid <> ? THEN date END) AS minimum_date,
            MAX(CASE WHEN rowid <> ? THEN date END) AS maximum_date
        FROM {table}
        """,
        (header_rowid,) * 5,
    ).fetchone()

    if row is None:
        raise RuntimeError(f"Unable to profile table: {table_name}")

    physical_rows, data_rows, apparent_races, runner_keys, minimum_date, maximum_date = row
    return {
        "table_name": table_name,
        "physical_rows": physical_rows,
        "data_rows": data_rows,
        "apparent_races": apparent_races,
        "provisional_runner_keys": runner_keys,
        "duplicate_rows_under_provisional_runner_key": data_rows - runner_keys,
        "minimum_date": minimum_date,
        "maximum_date": maximum_date,
        "quick_check": connection.execute("PRAGMA quick_check").fetchone()[0],
        "schema_objects": len(schema_inventory(connection)),
        "declared_columns": len(table_columns(connection, table_name)),
    }
