from __future__ import annotations

import sqlite3

from inside_rails.database.governed_integration_candidate import (
    BaseReleaseMetadata,
    _insert_v2_governance_and_manifest,
)
from inside_rails.database.schema import create_governed_integration_schema


TIMESTAMP = "2026-08-09T00:00:00.000000Z"
COMMIT = "1" * 40
SOURCE_SHA = bytes.fromhex("aa" * 32)
SCHEMA_SHA = bytes.fromhex("bb" * 32)


def _seed_v1_source_and_structural_release(connection: sqlite3.Connection) -> None:
    """Seed only the source/governance lineage needed by the v2 prep helper."""

    connection.execute(
        "INSERT INTO source_provider VALUES (1, 'provider:test', 'Test', 'Fixture.', ?)",
        (TIMESTAMP,),
    )
    connection.execute(
        """
        INSERT INTO source_product VALUES (
            1, 'product:test', 1, 'Test product', 'Fixture.', 'Fixture.', ?
        )
        """,
        (TIMESTAMP,),
    )
    connection.execute(
        """
        INSERT INTO source_version VALUES (
            1, 'sv:test', 1, 'raceform.db', 'Fixture source.', ?, 1, NULL, ?,
            2, 1, 1, 'rowid <> 1', '2015-01-01', '2026-05-27', 'ok',
            'accepted_exact_source', 'Fixture.', ?
        )
        """,
        (SOURCE_SHA, SCHEMA_SHA, TIMESTAMP),
    )
    connection.execute(
        """
        INSERT INTO governance_method VALUES (
            1, 'gm:v1:v1', 'Database v1 structural governance', 1, ?,
            'Fixture structural method.', ?
        )
        """,
        (COMMIT, TIMESTAMP),
    )
    connection.execute(
        """
        INSERT INTO governance_release VALUES (
            1, 'gr:v1:v1', 1, 1, 'accepted', '2026-08-08', ?,
            'rowid <> 1', 'Fixture structural release.', NULL, ?
        )
        """,
        (COMMIT, TIMESTAMP),
    )


def test_v2_preparation_supersedes_structural_governance_without_rewriting_core_lineage() -> None:
    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    try:
        _seed_v1_source_and_structural_release(connection)
        base = BaseReleaseMetadata(
            source_version_id=1,
            structural_governance_release_id=1,
            prior_database_release_code="db:v1",
            source_file_sha256=SOURCE_SHA,
        )

        new_release_id = _insert_v2_governance_and_manifest(
            connection,
            base=base,
            repository_commit=COMMIT,
            reference_data_commit=COMMIT,
            manifest_code="imp:20260809T000000Z:fixture",
            database_release_code="db:20260809T000000Z:fixture",
            build_command="python scripts/build_inside_rails_v2.py",
            created_at_utc=TIMESTAMP,
        )

        assert new_release_id == 2
        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            ORDER BY governance_release_id
            """
        ).fetchall()
        assert releases == [
            (1, "superseded", 2),
            (2, "accepted", None),
        ]
        assert connection.execute(
            """
            SELECT governance_release_id, schema_version, prior_database_release_code,
                   prior_release_preserved, build_status
            FROM import_manifest
            """
        ).fetchone() == (2, 2, "db:v1", 1, "building")
    finally:
        connection.close()
