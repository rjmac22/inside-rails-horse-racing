from __future__ import annotations

import sqlite3

import pytest

from inside_rails.database.schema import (
    APPLICATION_ID,
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    create_governed_integration_schema,
    create_minimum_core_schema,
    upgrade_minimum_core_to_governed_integration_schema,
)


V1_TABLES = {
    "source_provider",
    "source_product",
    "source_version",
    "source_relation",
    "source_relation_field",
    "source_raceform_v1_record",
    "governance_method",
    "governance_release",
    "governance_release_evidence",
    "core_source_race_occurrence",
    "core_runner_participation",
    "import_manifest",
    "import_validation_result",
}

V2_TABLES = {
    "core_source_race_occurrence_governed",
    "core_source_race_occurrence_time",
    "core_runner_participation_governed",
    "reference_course",
    "reference_jurisdiction_context",
    "governance_source_field_treatment",
    "governance_manual_verification",
    "governance_connection_value_decision",
    "governance_runner_record_supplementation",
    "governance_horse_pedigree_specialist_decision",
    "identity_horse_occurrence",
    "identity_runner_horse_occurrence",
    "identity_horse_pedigree_decision",
    "identity_participant_source_label",
    "identity_participant",
    "identity_participant_label_map",
    "identity_participant_candidate",
    "identity_participant_candidate_label",
}

V1_VIEWS = {
    "view_source_record_lineage",
    "view_source_raceform_v1_records",
    "view_core_source_race_occurrences",
    "view_core_runner_participations",
    "view_database_release_evidence",
    "view_import_validation_evidence",
}

V2_VIEWS = {
    "view_governed_race_occurrences",
    "view_governed_horse_occurrence_assignments",
    "view_governed_participant_label_identities",
    "view_governed_source_runner_participations",
    "view_governed_runner_records",
}

TIMESTAMP = "2026-08-09T00:00:00.000000Z"
COMMIT = "1" * 40
SHA = bytes.fromhex("aa" * 32)
SCHEMA_SHA = bytes.fromhex("bb" * 32)


def connect_v2() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    return connection


def seed_minimum_governance(connection: sqlite3.Connection) -> None:
    """Seed only the lineage required for focused v2 constraint tests."""

    connection.execute(
        "INSERT INTO source_provider VALUES (1, 'provider:test', 'Test', 'Test provenance.', ?)",
        (TIMESTAMP,),
    )
    connection.execute(
        """
        INSERT INTO source_product VALUES (
            1, 'product:test', 1, 'Test product', 'Test description.', 'Test use.', ?
        )
        """,
        (TIMESTAMP,),
    )
    connection.execute(
        """
        INSERT INTO source_version VALUES (
            1, 'sv:test', 1, 'raceform.db', 'Fixture.', ?, 1, NULL, ?,
            2, 1, 1, 'rowid <> 1', '2015-01-01', '2026-05-27', 'ok',
            'accepted_exact_source', 'Fixture source.', ?
        )
        """,
        (SHA, SCHEMA_SHA, TIMESTAMP),
    )
    connection.execute(
        "INSERT INTO source_relation VALUES (1, 'rel:test:data', 1, 'data', ?, 37, 2, 1, 'rowid <> 1')",
        (SCHEMA_SHA,),
    )
    for ordinal, field_name in enumerate(("jockey", "trainer", "owner")):
        connection.execute(
            "INSERT INTO source_relation_field VALUES (?, 1, ?, ?, '', 0, NULL, 0)",
            (ordinal + 1, ordinal, field_name),
        )
    connection.execute(
        "INSERT INTO governance_method VALUES (1, 'gm:v2:v1', 'Database v2', 1, ?, 'Fixture.', ?)",
        (COMMIT, TIMESTAMP),
    )
    connection.execute(
        """
        INSERT INTO governance_release VALUES (
            1, 'gr:v2:v1', 1, 1, 'accepted', '2026-08-09', ?,
            'rowid <> 1', 'Fixture v2 release.', NULL, ?
        )
        """,
        (COMMIT, TIMESTAMP),
    )


def test_v2_schema_has_exact_reconciled_inventory_and_views() -> None:
    connection = connect_v2()
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        views = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type = 'view'"
            )
        }
        assert tables == V1_TABLES | V2_TABLES
        assert len(tables) == 31
        assert views == V1_VIEWS | V2_VIEWS
        assert connection.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID
        assert (
            connection.execute("PRAGMA user_version").fetchone()[0]
            == GOVERNED_INTEGRATION_SCHEMA_VERSION
        )
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_v2_runner_schema_uses_notebook_13_confidence_domain() -> None:
    connection = connect_v2()
    try:
        sql = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE type='table' AND name='core_runner_participation_governed'"
        ).fetchone()[0]
        assert "prize_confidence IN ('confirmed', 'unresolved')" in sql
        assert "prize_confidence IN ('high', 'medium', 'low')" not in sql
    finally:
        connection.close()


def test_v2_upgrade_requires_version_1_and_removes_v1_manifest_rows() -> None:
    connection = sqlite3.connect(":memory:")
    create_minimum_core_schema(connection)
    try:
        # The v2 candidate owns its own build evidence; historical v1 release
        # evidence remains in the separately retained immutable v1 database.
        connection.execute(
            "INSERT INTO source_provider VALUES (1, 'provider:test', 'Test', 'Test provenance.', ?)",
            (TIMESTAMP,),
        )
        assert connection.execute("SELECT COUNT(*) FROM import_manifest").fetchone()[0] == 0

        upgrade_minimum_core_to_governed_integration_schema(connection)
        assert connection.execute("SELECT COUNT(*) FROM import_manifest").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0] == 0

        with pytest.raises(ValueError, match="requires schema version 1"):
            upgrade_minimum_core_to_governed_integration_schema(connection)
    finally:
        connection.close()


def test_v2_import_manifest_requires_schema_version_2_and_accepted_governance() -> None:
    connection = connect_v2()
    try:
        seed_minimum_governance(connection)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO import_manifest VALUES (
                    1, 'imp:test', 'db:test', 1, 1, 1, ?, ?, 'build', ?, NULL,
                    2, 1, 1, 1, 1, 0, 0, 0, 0, 'db:v1', 1, 'building', NULL
                )
                """,
                (COMMIT, COMMIT, TIMESTAMP),
            )

        connection.execute(
            """
            INSERT INTO import_manifest VALUES (
                1, 'imp:test', 'db:test', 1, 1, 2, ?, ?, 'build', ?, NULL,
                2, 1, 1, 1, 1, 0, 0, 0, 0, 'db:v1', 1, 'building', NULL
            )
            """,
            (COMMIT, COMMIT, TIMESTAMP),
        )
        assert connection.execute("SELECT schema_version FROM import_manifest").fetchone()[0] == 2
    finally:
        connection.close()


def test_connection_decision_rejects_non_connection_source_field() -> None:
    connection = connect_v2()
    try:
        seed_minimum_governance(connection)
        connection.execute(
            "INSERT INTO source_relation_field VALUES (4, 1, 3, 'horse', '', 0, NULL, 0)"
        )
        connection.execute(
            """
            INSERT INTO governance_manual_verification (
                manual_verification_id, verification_code, subject_type,
                source_relation_field_id, verification_question, verified_value,
                verification_status, evidence_type, evidence_locator,
                governing_notebook, confidence, notes, database_action,
                governance_release_id
            ) VALUES (
                1, 'NB20-TEST-0001', 'runner', 4, 'Who?', 'Value', 'confirmed',
                'fixture', 'fixture://evidence', '20', 'high', 'Fixture.',
                'source_supplementation', 1
            )
            """
        )

        # A source record is needed by the connection-decision FK. Keep all raw
        # source values null because this test exercises only the governed field boundary.
        raw_columns = [
            "date", "course", "race_id", "off", "race_name", "type", "class",
            "pattern", "rating_band", "age_band", "sex_rest", "dist", "going",
            "ran", "num", "pos", "draw", "ovr_btn", "btn", "horse", "age",
            "sex", "wgt", "hg", "time", "sp", "jockey", "trainer", "prize",
            "or", "rpr", "ts", "sire", "dam", "damsire", "owner", "comment",
        ]
        quoted = ", ".join(f'"{column}"' for column in raw_columns)
        placeholders = ", ".join("?" for _ in range(8 + len(raw_columns)))
        connection.execute(
            f"""
            INSERT INTO source_raceform_v1_record (
                source_record_id, source_record_code, source_version_id,
                source_relation_id, source_rowid, structural_status,
                exclusion_reason, row_sha256, {quoted}
            ) VALUES ({placeholders})
            """,
            (
                1,
                "rec:test:0000000002",
                1,
                1,
                2,
                "admitted_runner_record",
                None,
                bytes.fromhex("cc" * 32),
                *([None] * len(raw_columns)),
            ),
        )

        with pytest.raises(sqlite3.IntegrityError, match="jockey, trainer or owner"):
            connection.execute(
                """
                INSERT INTO governance_connection_value_decision VALUES (
                    1, 'connection_blank_001', 1, 4, 1, 'Value',
                    'externally_supplemented', 'high', 1
                )
                """
            )
    finally:
        connection.close()


def test_participant_mapping_requires_accepted_candidate_and_matching_role() -> None:
    connection = connect_v2()
    try:
        seed_minimum_governance(connection)
        connection.execute(
            """
            INSERT INTO identity_participant_source_label VALUES (
                1, 'label:jockey:1', 'jockey', 'Mlle Marie Velon',
                '2020-01-01', '2023-12-01', 10, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO identity_participant VALUES (
                1, 'JOCKEY-PROVISIONAL-0001', 'jockey', 'person_label_identity',
                'provisional_source_label_identity', 'targeted_external_profile_verification',
                'high', 'accepted', '22', 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO identity_participant_candidate VALUES (
                1, 'JOCKEY-STRICT-0002', 'jockey', 'marie velon',
                'observed_leading_title_removed_exact_match', 'two_title_bearing_labels',
                'externally_verified', 'same_person', 'unresolved',
                'Fixture decision.', 'high', NULL, NULL, NULL, NULL,
                'completed', NULL, 'preserve_raw_unresolved', 1
            )
            """
        )
        connection.execute(
            "INSERT INTO identity_participant_candidate_label VALUES (1, 1, 'left', 1)"
        )

        with pytest.raises(sqlite3.IntegrityError, match="accepted compatible candidate"):
            connection.execute(
                """
                INSERT INTO identity_participant_label_map VALUES (
                    1, 1, 1, 1, 'mlle_source_label', 'accepted',
                    'targeted_external_profile_verification', 'high', NULL,
                    'map_raw_label_to_provisional_jockey_identity', NULL, NULL, 1
                )
                """
            )

        connection.execute(
            "UPDATE identity_participant_candidate SET decision_status = 'accepted' WHERE participant_candidate_id = 1"
        )
        connection.execute(
            """
            INSERT INTO identity_participant_label_map VALUES (
                1, 1, 1, 1, 'mlle_source_label', 'accepted',
                'targeted_external_profile_verification', 'high', NULL,
                'map_raw_label_to_provisional_jockey_identity', NULL, NULL, 1
            )
            """
        )
        assert connection.execute("SELECT COUNT(*) FROM identity_participant_label_map").fetchone()[0] == 1
    finally:
        connection.close()
