from __future__ import annotations

import sqlite3

import pytest

from inside_rails.database.schema import (
    APPLICATION_ID,
    EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
    create_external_reconciliation_schema,
    create_governed_integration_schema,
    upgrade_governed_integration_to_external_reconciliation_schema,
)


def test_create_external_reconciliation_schema_has_v3_table_and_views() -> None:
    connection = sqlite3.connect(":memory:")
    create_external_reconciliation_schema(connection)

    assert connection.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID
    assert (
        connection.execute("PRAGMA user_version").fetchone()[0]
        == EXTERNAL_RECONCILIATION_SCHEMA_VERSION
    )
    objects = {
        (kind, name)
        for kind, name in connection.execute(
            "SELECT type, name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
        )
    }
    assert ("table", "governance_external_value_resolution") in objects
    assert ("view", "view_reconciled_race_occurrences") in objects
    assert ("view", "view_reconciled_source_runner_participations") in objects
    assert ("view", "view_reconciled_runner_records") in objects
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_v3_upgrade_requires_v2() -> None:
    connection = sqlite3.connect(":memory:")
    with pytest.raises(ValueError, match="requires an Inside Rails database"):
        upgrade_governed_integration_to_external_reconciliation_schema(connection)

    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    upgrade_governed_integration_to_external_reconciliation_schema(connection)
    with pytest.raises(ValueError, match="requires schema version 2"):
        upgrade_governed_integration_to_external_reconciliation_schema(connection)


def test_external_resolution_table_rejects_incomplete_correction() -> None:
    connection = sqlite3.connect(":memory:")
    create_external_reconciliation_schema(connection)
    # The v3 table is intentionally typed: a correction/enrichment cannot consist
    # only of prose/action metadata with no governed value.
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO governance_external_value_resolution (
                external_value_resolution_id, resolution_code,
                manual_verification_id, source_race_occurrence_id,
                source_field, resolution_kind, analytical_action, notes,
                governance_release_id
            ) VALUES (1,'x',1,1,'sp','correction','replace','x',1)
            """
        )
