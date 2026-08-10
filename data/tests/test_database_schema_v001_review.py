from __future__ import annotations

import sqlite3

import pytest

from inside_rails.database.fingerprints import raceform_v1_row_sha256
from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
    runner_participation_code,
    source_race_occurrence_code,
    source_record_code,
    source_relation_code,
    source_version_code,
)
from inside_rails.database.schema import create_minimum_core_schema


SHA_A = bytes.fromhex("aa" * 32)
SHA_B = bytes.fromhex("bb" * 32)
SCHEMA_SHA = bytes.fromhex("cc" * 32)
COMMIT = "1" * 40
TIMESTAMP = "2026-08-06T00:00:00.000000Z"
RAW_COLUMNS = (
    "date",
    "course",
    "race_id",
    "off",
    "race_name",
    "type",
    "class",
    "pattern",
    "rating_band",
    "age_band",
    "sex_rest",
    "dist",
    "going",
    "ran",
    "num",
    "pos",
    "draw",
    "ovr_btn",
    "btn",
    "horse",
    "age",
    "sex",
    "wgt",
    "hg",
    "time",
    "sp",
    "jockey",
    "trainer",
    "prize",
    "or",
    "rpr",
    "ts",
    "sire",
    "dam",
    "damsire",
    "owner",
    "comment",
)

EXPECTED_INDEXES = {
    "ix_core_runner_participation_governance_release",
    "ix_core_runner_participation_race",
    "ix_governance_release_evidence_release",
    "ix_governance_release_source_version_status",
    "ix_import_validation_result_manifest_stage_outcome",
    "ix_source_raceform_v1_record_admitted_race_group",
    "ix_source_raceform_v1_record_structural_status",
    "ux_governance_release_one_accepted_per_source_version",
    "ux_import_manifest_one_release_accepted",
}
EXPECTED_TRIGGERS = {
    "trg_import_manifest_acceptance_insert",
    "trg_import_manifest_acceptance_structural_recheck",
    "trg_import_manifest_acceptance_update",
    "trg_import_manifest_initial_status",
    "trg_import_manifest_state_transition",
    "trg_manifest_governance_compatible_insert",
    "trg_manifest_governance_compatible_update",
    "trg_race_governance_compatible_insert",
    "trg_race_governance_compatible_update",
    "trg_runner_structural_compatible_insert",
    "trg_runner_structural_compatible_update",
}


def connect_schema() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    create_minimum_core_schema(connection)
    return connection


def raw_values(**overrides: object) -> list[object]:
    values = {name: None for name in RAW_COLUMNS}
    values.update(overrides)
    return [values[name] for name in RAW_COLUMNS]


def insert_provider_and_product(connection: sqlite3.Connection) -> None:
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


def insert_source_version(
    connection: sqlite3.Connection,
    *,
    source_version_id: int,
    source_relation_id: int,
    file_sha256: bytes,
) -> None:
    connection.execute(
        """
        INSERT INTO source_version VALUES (
            ?, ?, 1, 'raceform.db', 'Controlled fixture.', ?, 123, NULL, ?,
            2, 1, 1, 'rowid <> 1', '2015-01-01', '2026-05-27', 'ok',
            'accepted_exact_source', 'Retains rowid 1.', ?
        )
        """,
        (
            source_version_id,
            source_version_code(file_sha256),
            file_sha256,
            SCHEMA_SHA,
            TIMESTAMP,
        ),
    )
    connection.execute(
        "INSERT INTO source_relation VALUES (?, ?, ?, 'data', ?, 37, 2, 1, 'rowid <> 1')",
        (
            source_relation_id,
            source_relation_code(file_sha256),
            source_version_id,
            SCHEMA_SHA,
        ),
    )


def insert_governance_method(
    connection: sqlite3.Connection,
    *,
    governance_method_id: int,
) -> None:
    connection.execute(
        "INSERT INTO governance_method VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            governance_method_id,
            governance_method_code("source-v1-structure", governance_method_id),
            "Source Version 1 structural method",
            governance_method_id,
            COMMIT,
            "Fixture structural method.",
            TIMESTAMP,
        ),
    )


def insert_governance_release(
    connection: sqlite3.Connection,
    *,
    governance_release_id: int,
    source_version_id: int,
    governance_method_id: int,
    file_sha256: bytes,
    release_version: int,
    release_status: str,
    superseded_by_release_id: int | None,
) -> None:
    connection.execute(
        """
        INSERT INTO governance_release VALUES (
            ?, ?, ?, ?, ?, '2026-08-06', ?, 'rowid <> 1', ?, ?, ?
        )
        """,
        (
            governance_release_id,
            governance_release_code(file_sha256, "minimum-core", release_version),
            source_version_id,
            governance_method_id,
            release_status,
            COMMIT,
            f"Fixture governance release {release_version}.",
            superseded_by_release_id,
            TIMESTAMP,
        ),
    )


def insert_raw_record(
    connection: sqlite3.Connection,
    *,
    source_record_id: int,
    source_rowid: int,
    values: list[object],
    file_sha256: bytes = SHA_A,
    source_version_id: int = 1,
    source_relation_id: int = 1,
) -> None:
    quoted_raw = ", ".join(f'"{name}"' for name in RAW_COLUMNS)
    placeholders = ", ".join("?" for _ in range(8 + len(RAW_COLUMNS)))
    connection.execute(
        f"""
        INSERT INTO source_raceform_v1_record (
            source_record_id, source_record_code, source_version_id, source_relation_id,
            source_rowid, structural_status, exclusion_reason, row_sha256, {quoted_raw}
        ) VALUES ({placeholders})
        """,
        (
            source_record_id,
            source_record_code(file_sha256, source_rowid),
            source_version_id,
            source_relation_id,
            source_rowid,
            "admitted_runner_record",
            None,
            raceform_v1_row_sha256(values),
            *values,
        ),
    )


def seed_two_source_versions(connection: sqlite3.Connection) -> None:
    insert_provider_and_product(connection)
    insert_source_version(
        connection,
        source_version_id=1,
        source_relation_id=1,
        file_sha256=SHA_A,
    )
    insert_source_version(
        connection,
        source_version_id=2,
        source_relation_id=2,
        file_sha256=SHA_B,
    )
    insert_governance_method(connection, governance_method_id=1)
    insert_governance_method(connection, governance_method_id=2)
    insert_governance_release(
        connection,
        governance_release_id=1,
        source_version_id=1,
        governance_method_id=1,
        file_sha256=SHA_A,
        release_version=1,
        release_status="accepted",
        superseded_by_release_id=None,
    )
    insert_governance_release(
        connection,
        governance_release_id=2,
        source_version_id=2,
        governance_method_id=2,
        file_sha256=SHA_B,
        release_version=1,
        release_status="accepted",
        superseded_by_release_id=None,
    )


def insert_building_manifest(
    connection: sqlite3.Connection,
    *,
    governance_release_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO import_manifest VALUES (
            1, 'imp:20260806T000000000000Z:00000001',
            'db:20260806T000000000000Z:00000001',
            1, ?, 1, ?, ?, 'build', ?, NULL,
            2, 1, 1, 1, 1, 0, 0, 0, 0, NULL, 1, 'building', NULL
        )
        """,
        (governance_release_id, COMMIT, COMMIT, TIMESTAMP),
    )


def test_reviewed_schema_has_exact_authorised_indexes_and_triggers() -> None:
    connection = connect_schema()
    try:
        indexes = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema "
                "WHERE type = 'index' AND name NOT LIKE 'sqlite_%'"
            )
        }
        triggers = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_schema WHERE type = 'trigger'")
        }
        assert indexes == EXPECTED_INDEXES
        assert triggers == EXPECTED_TRIGGERS

        for trigger_name in (
            "trg_race_governance_compatible_insert",
            "trg_race_governance_compatible_update",
            "trg_runner_structural_compatible_insert",
            "trg_runner_structural_compatible_update",
            "trg_manifest_governance_compatible_insert",
            "trg_manifest_governance_compatible_update",
        ):
            trigger_sql = connection.execute(
                "SELECT sql FROM sqlite_schema WHERE type = 'trigger' AND name = ?",
                (trigger_name,),
            ).fetchone()[0]
            assert "gr.release_status = 'accepted'" in trigger_sql

        acceptance_sql = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE type = 'trigger' "
            "AND name = 'trg_import_manifest_acceptance_structural_recheck'"
        ).fetchone()[0]
        assert "race.governance_release_id <> NEW.governance_release_id" in acceptance_sql
        assert 'sr."date" IS race.raw_date' in acceptance_sql
        assert 'sr."course" IS race.raw_course' in acceptance_sql
        assert 'sr."off" IS race.raw_off' in acceptance_sql
    finally:
        connection.close()


def test_superseded_governance_release_cannot_create_race_or_manifest() -> None:
    connection = connect_schema()
    try:
        insert_provider_and_product(connection)
        insert_source_version(
            connection,
            source_version_id=1,
            source_relation_id=1,
            file_sha256=SHA_A,
        )
        insert_governance_method(connection, governance_method_id=1)
        insert_governance_release(
            connection,
            governance_release_id=1,
            source_version_id=1,
            governance_method_id=1,
            file_sha256=SHA_A,
            release_version=1,
            release_status="accepted",
            superseded_by_release_id=None,
        )
        insert_governance_release(
            connection,
            governance_release_id=2,
            source_version_id=1,
            governance_method_id=1,
            file_sha256=SHA_A,
            release_version=2,
            release_status="superseded",
            superseded_by_release_id=1,
        )

        with pytest.raises(sqlite3.IntegrityError, match="not accepted and compatible"):
            connection.execute(
                "INSERT INTO core_source_race_occurrence VALUES (1, ?, 1, 'd', 'c', 'o', 1, 2)",
                (source_race_occurrence_code(SHA_A, 1),),
            )

        with pytest.raises(sqlite3.IntegrityError, match="not accepted and compatible"):
            insert_building_manifest(connection, governance_release_id=2)
    finally:
        connection.close()


def test_relationship_update_triggers_fail_closed() -> None:
    connection = connect_schema()
    try:
        seed_two_source_versions(connection)
        matching = raw_values(date="2026-01-01", course="Ascot", off="13:00", horse="One")
        mismatch = raw_values(date="2026-01-01", course="Ascot", off="13:30", horse="Two")
        insert_raw_record(
            connection,
            source_record_id=1,
            source_rowid=2,
            values=matching,
        )
        insert_raw_record(
            connection,
            source_record_id=2,
            source_rowid=3,
            values=mismatch,
        )
        connection.execute(
            "INSERT INTO core_source_race_occurrence VALUES (1, ?, 1, ?, ?, ?, 1, 1)",
            (source_race_occurrence_code(SHA_A, 1), "2026-01-01", "Ascot", "13:00"),
        )
        connection.execute(
            "INSERT INTO core_runner_participation VALUES (1, ?, 1, 1, ?, 1)",
            (runner_participation_code(SHA_A, 2), "admitted_runner_record"),
        )
        insert_building_manifest(connection, governance_release_id=1)

        with pytest.raises(sqlite3.IntegrityError, match="race governance"):
            connection.execute(
                "UPDATE core_source_race_occurrence "
                "SET governance_release_id = 2 WHERE source_race_occurrence_id = 1"
            )

        with pytest.raises(sqlite3.IntegrityError, match="structurally incompatible"):
            connection.execute(
                "UPDATE core_runner_participation "
                "SET source_record_id = 2 WHERE runner_participation_id = 1"
            )

        with pytest.raises(sqlite3.IntegrityError, match="manifest governance"):
            connection.execute(
                "UPDATE import_manifest SET governance_release_id = 2 "
                "WHERE import_manifest_id = 1"
            )
    finally:
        connection.close()
