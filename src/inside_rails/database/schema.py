"""Creation and connection controls for governed Inside Rails SQLite schemas."""

from __future__ import annotations

from importlib.resources import files
import sqlite3
from typing import Any

APPLICATION_ID = 1_230_130_259
SCHEMA_VERSION = 1
GOVERNED_INTEGRATION_SCHEMA_VERSION = 2
EXTERNAL_RECONCILIATION_SCHEMA_VERSION = 3
RACECOURSE_IDENTITY_SCHEMA_VERSION = 4
MINIMUM_SQLITE_VERSION = (3, 37, 0)
_SCHEMA_RESOURCES = (
    "schema/v001_minimum_core.sql",
    "schema/v001_minimum_core_enforcement.sql",
)
_GOVERNED_INTEGRATION_RESOURCES = (
    "schema/v002_governed_integration.sql",
    "schema/v002_governed_integration_corrections.sql",
    "schema/v002_governed_integration_participant_confidence_corrections.sql",
    "schema/v002_governed_integration_enforcement.sql",
    "schema/v002_governed_integration_enforcement_corrections.sql",
    "schema/v002_governed_integration_views.sql",
    "schema/v002_governed_integration_view_corrections.sql",
)
_EXTERNAL_RECONCILIATION_RESOURCES = (
    "schema/v003_external_verification_reconciliation.sql",
    "schema/v003_external_verification_views.sql",
)
_RACECOURSE_IDENTITY_RESOURCES = (
    "schema/v004_racecourse_identity.sql",
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


def _resource_sql(resource: str) -> str:
    package = files("inside_rails.database")
    return package.joinpath(resource).read_text(encoding="utf-8")


def _schema_sql() -> str:
    return "\n".join(_resource_sql(resource) for resource in _SCHEMA_RESOURCES)


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
    """Create accepted minimum-core schema version 1 in a clean database."""

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


def upgrade_minimum_core_to_governed_integration_schema(
    connection: sqlite3.Connection,
) -> None:
    """Upgrade a writable candidate copy of Database v1 to schema version 2."""

    configure_governed_connection(connection)
    if connection.in_transaction:
        raise ValueError("Database v2 schema upgrade requires no active transaction")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise ValueError("Database v2 schema upgrade requires an Inside Rails database")
    observed_version = int(_pragma_scalar(connection, "user_version"))
    if observed_version != SCHEMA_VERSION:
        raise ValueError(
            "Database v2 schema upgrade requires schema version 1; "
            f"found {observed_version}"
        )

    connection.execute("PRAGMA foreign_keys = OFF")
    if _pragma_scalar(connection, "foreign_keys") != 0:
        raise RuntimeError("Unable to disable foreign keys for Database v2 migration")

    try:
        for resource in _GOVERNED_INTEGRATION_RESOURCES:
            connection.executescript(_resource_sql(resource))
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")

    if _pragma_scalar(connection, "foreign_keys") != 1:
        raise RuntimeError("Database v2 migration did not restore foreign-key enforcement")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise RuntimeError("Unexpected SQLite application_id after Database v2 migration")
    if _pragma_scalar(connection, "user_version") != GOVERNED_INTEGRATION_SCHEMA_VERSION:
        raise RuntimeError("Unexpected SQLite user_version after Database v2 migration")

    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise RuntimeError(
            "Database v2 migration produced foreign-key violations: "
            f"{foreign_key_rows[:5]}"
        )


def upgrade_governed_integration_to_external_reconciliation_schema(
    connection: sqlite3.Connection,
) -> None:
    """Upgrade a writable copy of accepted Database v2 to schema version 3.

    Only a disposable candidate copy may be passed here. The migration rebuilds
    the import-manifest tables for v3, adds the typed reconciliation layer and
    creates new study-facing reconciled views. Existing v2 source/core/governed
    rows are not rewritten by the schema migration.
    """

    configure_governed_connection(connection)
    if connection.in_transaction:
        raise ValueError("Database v3 schema upgrade requires no active transaction")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise ValueError("Database v3 schema upgrade requires an Inside Rails database")
    observed_version = int(_pragma_scalar(connection, "user_version"))
    if observed_version != GOVERNED_INTEGRATION_SCHEMA_VERSION:
        raise ValueError(
            "Database v3 schema upgrade requires schema version 2; "
            f"found {observed_version}"
        )

    connection.execute("PRAGMA foreign_keys = OFF")
    if _pragma_scalar(connection, "foreign_keys") != 0:
        raise RuntimeError("Unable to disable foreign keys for Database v3 migration")
    try:
        for resource in _EXTERNAL_RECONCILIATION_RESOURCES:
            connection.executescript(_resource_sql(resource))
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")

    if _pragma_scalar(connection, "foreign_keys") != 1:
        raise RuntimeError("Database v3 migration did not restore foreign-key enforcement")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise RuntimeError("Unexpected SQLite application_id after Database v3 migration")
    if _pragma_scalar(connection, "user_version") != EXTERNAL_RECONCILIATION_SCHEMA_VERSION:
        raise RuntimeError("Unexpected SQLite user_version after Database v3 migration")

    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise RuntimeError(
            "Database v3 migration produced foreign-key violations: "
            f"{foreign_key_rows[:5]}"
        )


def upgrade_external_reconciliation_to_racecourse_identity_schema(
    connection: sqlite3.Connection,
) -> None:
    """Upgrade a writable copy of accepted Database v3 to schema version 4."""

    configure_governed_connection(connection)
    if connection.in_transaction:
        raise ValueError("Database v4 schema upgrade requires no active transaction")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise ValueError("Database v4 schema upgrade requires an Inside Rails database")
    observed_version = int(_pragma_scalar(connection, "user_version"))
    if observed_version != EXTERNAL_RECONCILIATION_SCHEMA_VERSION:
        raise ValueError(
            "Database v4 schema upgrade requires schema version 3; "
            f"found {observed_version}"
        )

    connection.execute("PRAGMA foreign_keys = OFF")
    if _pragma_scalar(connection, "foreign_keys") != 0:
        raise RuntimeError("Unable to disable foreign keys for Database v4 migration")
    try:
        for resource in _RACECOURSE_IDENTITY_RESOURCES:
            connection.executescript(_resource_sql(resource))
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")

    if _pragma_scalar(connection, "foreign_keys") != 1:
        raise RuntimeError("Database v4 migration did not restore foreign-key enforcement")
    if _pragma_scalar(connection, "application_id") != APPLICATION_ID:
        raise RuntimeError("Unexpected SQLite application_id after Database v4 migration")
    if _pragma_scalar(connection, "user_version") != RACECOURSE_IDENTITY_SCHEMA_VERSION:
        raise RuntimeError("Unexpected SQLite user_version after Database v4 migration")

    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise RuntimeError(
            "Database v4 migration produced foreign-key violations: "
            f"{foreign_key_rows[:5]}"
        )


def create_governed_integration_schema(connection: sqlite3.Connection) -> None:
    """Create the complete Database v2 physical schema in a clean database."""

    create_minimum_core_schema(connection)
    upgrade_minimum_core_to_governed_integration_schema(connection)


def create_external_reconciliation_schema(connection: sqlite3.Connection) -> None:
    """Create the complete Database v3 schema in a clean database for tests."""

    create_governed_integration_schema(connection)
    upgrade_governed_integration_to_external_reconciliation_schema(connection)


def create_racecourse_identity_schema(connection: sqlite3.Connection) -> None:
    """Create the complete Database v4 schema in a clean database for tests."""

    create_external_reconciliation_schema(connection)
    upgrade_external_reconciliation_to_racecourse_identity_schema(connection)
