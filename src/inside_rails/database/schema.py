"""Creation and connection controls for minimum-core SQLite schema version 1."""

from __future__ import annotations

from importlib.resources import files
import sqlite3
from typing import Any

APPLICATION_ID = 1_230_130_259
SCHEMA_VERSION = 1
MINIMUM_SQLITE_VERSION = (3, 37, 0)
_SCHEMA_RESOURCES = (
    "schema/v001_minimum_core.sql",
    "schema/v001_minimum_core_enforcement.sql",
)


def require_supported_sqlite(version: tuple[int, int, int] | None = None) -> None:
    """Fail before schema creation when SQLite lacks STRICT and ANY support."""

    observed = sqlite3.sqlite_version_info if version is None else version
    if observed < MINIMUM_SQLITE_VERSION:
        required = ".".join(map(str, MINIMUM_SQLITE_VERSION))
        actual = ".".join(map(str, observed))
        raise RuntimeError(f"SQLite {required} or later is required; found {actual}")


def _pragma_scalar(connection: sqlite3.Connection, name: str) -> Any:
    row = connection.execute(f"PRAGMA {name}").fetchone()
    if row is None:
        raise RuntimeError(f"PRAGMA {name} returned no result")
    return row[0]


def configure_governed_connection(
    connection: sqlite3.Connection,
    *,
    query_only: bool = False,
    durable_candidate: bool = False,
) -> None:
    """Apply and verify the mandatory governed-connection settings."""

    require_supported_sqlite()
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA trusted_schema = OFF")
    if durable_candidate:
        journal_mode = str(_pragma_scalar(connection, "journal_mode = DELETE")).lower()
        if journal_mode != "delete":
            raise RuntimeError(f"Unable to select DELETE journal mode: {journal_mode}")
        connection.execute("PRAGMA synchronous = FULL")
    if query_only:
        connection.execute("PRAGMA query_only = ON")

    if _pragma_scalar(connection, "foreign_keys") != 1:
        raise RuntimeError("SQLite foreign-key enforcement is not active")
    if _pragma_scalar(connection, "trusted_schema") != 0:
        raise RuntimeError("SQLite trusted_schema must be disabled")
    if durable_candidate and _pragma_scalar(connection, "synchronous") != 2:
        raise RuntimeError("SQLite synchronous mode must be FULL")
    if query_only and _pragma_scalar(connection, "query_only") != 1:
        raise RuntimeError("SQLite query_only mode is not active")


def _schema_sql() -> str:
    package = files("inside_rails.database")
    return "\n".join(
        package.joinpath(resource).read_text(encoding="utf-8")
        for resource in _SCHEMA_RESOURCES
    )


def schema_inventory(connection: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """Return user-defined schema objects in deterministic order."""

    return connection.execute(
        """
        SELECT type, name, COALESCE(sql, '')
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """
    ).fetchall()


def create_minimum_core_schema(connection: sqlite3.Connection) -> None:
    """Create schema version 1 in an otherwise clean SQLite database."""

    configure_governed_connection(connection)
    existing = connection.execute(
        "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' LIMIT 1"
    ).fetchone()
    if existing is not None:
        raise ValueError(f"Schema creation requires a clean database; found {existing[0]!r}")

    connection.executescript(_schema_sql())

    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise RuntimeError("Unexpected SQLite application_id after schema creation")
    if _pragma_scalar(connection, "user_version") != SCHEMA_VERSION:
        raise RuntimeError("Unexpected SQLite user_version after schema creation")
    if _pragma_scalar(connection, "foreign_keys") != 1:
        raise RuntimeError("Schema creation disabled foreign-key enforcement")
