from __future__ import annotations

import sqlite3

from inside_rails.database.racecourse_identity_candidate import (
    V3BaseMetadata,
    _insert_v4_governance_and_manifest,
)


def test_v4_governance_handover_preserves_one_accepted_release() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            """
            CREATE TABLE governance_method (
                governance_method_id INTEGER PRIMARY KEY,
                governance_method_code TEXT NOT NULL,
                method_name TEXT NOT NULL,
                method_version INTEGER NOT NULL,
                repository_commit TEXT NOT NULL,
                method_description TEXT NOT NULL,
                created_at_utc TEXT NOT NULL
            );

            CREATE TABLE governance_release (
                governance_release_id INTEGER PRIMARY KEY,
                governance_release_code TEXT NOT NULL,
                source_version_id INTEGER NOT NULL,
                governance_method_id INTEGER NOT NULL,
                release_status TEXT NOT NULL,
                accepted_date TEXT NOT NULL,
                repository_commit TEXT NOT NULL,
                population_predicate TEXT NOT NULL,
                release_description TEXT NOT NULL,
                superseded_by_release_id INTEGER,
                created_at_utc TEXT NOT NULL
            );

            CREATE UNIQUE INDEX ux_test_one_accepted_governance_release
                ON governance_release(source_version_id)
                WHERE release_status = 'accepted';

            CREATE TABLE governance_release_evidence (
                governance_release_evidence_id INTEGER PRIMARY KEY,
                governance_release_id INTEGER NOT NULL,
                evidence_type TEXT NOT NULL,
                evidence_reference TEXT NOT NULL,
                evidence_sha256 BLOB,
                evidence_description TEXT NOT NULL
            );

            CREATE TABLE import_manifest (
                import_manifest_id INTEGER PRIMARY KEY,
                import_manifest_code TEXT NOT NULL,
                database_release_code TEXT NOT NULL,
                source_version_id INTEGER NOT NULL,
                governance_release_id INTEGER NOT NULL,
                schema_version INTEGER NOT NULL,
                code_commit TEXT NOT NULL,
                reference_data_commit TEXT NOT NULL,
                build_command TEXT NOT NULL,
                build_started_at_utc TEXT NOT NULL,
                build_completed_at_utc TEXT,
                physical_record_count INTEGER NOT NULL,
                admitted_record_count INTEGER NOT NULL,
                excluded_record_count INTEGER NOT NULL,
                race_occurrence_count INTEGER NOT NULL,
                runner_participation_count INTEGER NOT NULL,
                persisted_readback_passed INTEGER NOT NULL,
                sqlite_integrity_passed INTEGER NOT NULL,
                foreign_key_check_passed INTEGER NOT NULL,
                post_load_validation_passed INTEGER NOT NULL,
                prior_database_release_code TEXT NOT NULL,
                prior_release_preserved INTEGER NOT NULL,
                build_status TEXT NOT NULL,
                failure_reason TEXT
            );
            """
        )
        connection.execute(
            """
            INSERT INTO governance_method VALUES (
                1, 'method:v3', 'Database v3', 1, ?, 'prior method', ?
            )
            """,
            ("1" * 40, "2026-08-09T00:00:00.000000Z"),
        )
        connection.execute(
            """
            INSERT INTO governance_release VALUES (
                3, 'release:v3', 1, 1, 'accepted', '2026-08-09', ?,
                'rowid <> 1', 'accepted v3', NULL, ?
            )
            """,
            ("1" * 40, "2026-08-09T00:00:00.000000Z"),
        )

        release_id = _insert_v4_governance_and_manifest(
            connection,
            base=V3BaseMetadata(
                source_version_id=1,
                v3_governance_release_id=3,
                source_file_sha256=b"\x01" * 32,
                prior_database_release_code="db:v3",
            ),
            repository_commit="a" * 40,
            reference_data_commit="b" * 40,
            manifest_code="imp:test",
            database_release_code="db:test",
            build_command="python scripts/build_inside_rails_v4.py",
            created_at_utc="2026-08-11T20:00:00.000000Z",
        )

        assert release_id == 4
        assert connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            WHERE source_version_id = 1
            ORDER BY governance_release_id
            """
        ).fetchall() == [
            (3, "superseded", 4),
            (4, "accepted", None),
        ]
        assert connection.execute(
            "SELECT COUNT(*) FROM governance_release WHERE source_version_id=1 AND release_status='accepted'"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT governance_release_id, build_status FROM import_manifest"
        ).fetchone() == (4, "building")
    finally:
        connection.close()
