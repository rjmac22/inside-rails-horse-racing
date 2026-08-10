from __future__ import annotations

from pathlib import Path
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
from inside_rails.database.schema import (
    APPLICATION_ID,
    MINIMUM_SQLITE_VERSION,
    SCHEMA_VERSION,
    configure_governed_connection,
    create_minimum_core_schema,
    require_supported_sqlite,
    schema_inventory,
)


TABLES = {
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
VIEWS = {
    "view_source_record_lineage",
    "view_source_raceform_v1_records",
    "view_core_source_race_occurrences",
    "view_core_runner_participations",
    "view_database_release_evidence",
    "view_import_validation_evidence",
}
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
METADATA_COLUMNS = (
    "source_record_id",
    "source_record_code",
    "source_version_id",
    "source_relation_id",
    "source_rowid",
    "structural_status",
    "exclusion_reason",
    "row_sha256",
)
SHA_A = bytes.fromhex("aa" * 32)
SHA_B = bytes.fromhex("bb" * 32)
SCHEMA_SHA = bytes.fromhex("cc" * 32)
COMMIT = "1" * 40
TIMESTAMP = "2026-08-05T20:00:00.000000Z"


def connect_schema(path: Path | str = ":memory:") -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    create_minimum_core_schema(connection)
    return connection


def raw_values(**overrides: object) -> list[object]:
    values = {name: None for name in RAW_COLUMNS}
    values.update(overrides)
    return [values[name] for name in RAW_COLUMNS]


def insert_source_metadata(
    connection: sqlite3.Connection,
    *,
    source_version_id: int = 1,
    source_relation_id: int = 1,
    file_sha256: bytes = SHA_A,
    physical_count: int = 2,
    admitted_count: int = 1,
    excluded_count: int = 1,
) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO source_provider VALUES (?, ?, ?, ?, ?)",
        (
            1,
            "provider:community-source",
            "Community source",
            "Provider role unresolved.",
            TIMESTAMP,
        ),
    )
    connection.execute(
        "INSERT OR IGNORE INTO source_product VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            "product:raceform-community-database",
            1,
            "Raceform community database",
            "Bounded Source Version 1 product family.",
            "Private research use only.",
            TIMESTAMP,
        ),
    )
    connection.execute(
        """
        INSERT INTO source_version VALUES (
            ?, ?, 1, 'raceform.db', 'Controlled fixture.', ?, 123, NULL, ?,
            ?, ?, ?, 'rowid <> 1', '2015-01-01', '2026-05-27', 'ok',
            'accepted_exact_source', 'Retains rowid 1 as excluded evidence.', ?
        )
        """,
        (
            source_version_id,
            source_version_code(file_sha256),
            file_sha256,
            SCHEMA_SHA,
            physical_count,
            admitted_count,
            excluded_count,
            TIMESTAMP,
        ),
    )
    connection.execute(
        """
        INSERT INTO source_relation VALUES (?, ?, ?, 'data', ?, 37, ?, ?, 'rowid <> 1')
        """,
        (
            source_relation_id,
            source_relation_code(file_sha256),
            source_version_id,
            SCHEMA_SHA,
            physical_count,
            admitted_count,
        ),
    )


def insert_governance(
    connection: sqlite3.Connection,
    *,
    source_version_id: int = 1,
    governance_method_id: int = 1,
    governance_release_id: int = 1,
    file_sha256: bytes = SHA_A,
) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO governance_method VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            governance_method_id,
            governance_method_code("source-v1-structure", governance_method_id),
            "Source Version 1 structural method",
            governance_method_id,
            COMMIT,
            "Groups admitted rows by raw date, course and off.",
            TIMESTAMP,
        ),
    )
    connection.execute(
        "INSERT INTO governance_release VALUES (?, ?, ?, ?, 'accepted', ?, ?, ?, ?, NULL, ?)",
        (
            governance_release_id,
            governance_release_code(file_sha256, "minimum-core", 1),
            source_version_id,
            governance_method_id,
            "2026-08-05",
            COMMIT,
            "rowid <> 1",
            "Minimum structural core fixture.",
            TIMESTAMP,
        ),
    )


def insert_raw_record(
    connection: sqlite3.Connection,
    *,
    source_record_id: int,
    source_rowid: int,
    values: list[object],
    status: str = "admitted_runner_record",
    exclusion_reason: str | None = None,
    file_sha256: bytes = SHA_A,
    source_version_id: int = 1,
    source_relation_id: int = 1,
) -> None:
    quoted_raw = ", ".join(f'"{name}"' for name in RAW_COLUMNS)
    placeholders = ", ".join("?" for _ in range(len(METADATA_COLUMNS) + len(RAW_COLUMNS)))
    connection.execute(
        f"""
        INSERT INTO source_raceform_v1_record (
            {', '.join(METADATA_COLUMNS)}, {quoted_raw}
        ) VALUES ({placeholders})
        """,
        (
            source_record_id,
            source_record_code(file_sha256, source_rowid),
            source_version_id,
            source_relation_id,
            source_rowid,
            status,
            exclusion_reason,
            raceform_v1_row_sha256(values),
            *values,
        ),
    )


def seed_structural_fixture(connection: sqlite3.Connection) -> None:
    insert_source_metadata(connection)
    insert_governance(connection)
    insert_raw_record(
        connection,
        source_record_id=1,
        source_rowid=1,
        status="retained_excluded_record",
        exclusion_reason="Source header-like physical record retained.",
        values=raw_values(date="date", course="course", off="off", horse="horse", **{"or": "or"}),
    )
    admitted = raw_values(
        date="2026-01-01",
        course="Ascot",
        race_id=901,
        off="13:00",
        race_name="Fixture Race",
        horse="Horse One",
        **{"or": 85},
    )
    insert_raw_record(
        connection,
        source_record_id=2,
        source_rowid=2,
        values=admitted,
    )
    connection.execute(
        "INSERT INTO core_source_race_occurrence VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            source_race_occurrence_code(SHA_A, 1),
            1,
            "2026-01-01",
            "Ascot",
            "13:00",
            1,
            1,
        ),
    )
    connection.execute(
        "INSERT INTO core_runner_participation VALUES (?, ?, ?, ?, ?, ?)",
        (
            1,
            runner_participation_code(SHA_A, 2),
            1,
            2,
            "admitted_runner_record",
            1,
        ),
    )


def insert_building_manifest(connection: sqlite3.Connection, *, manifest_id: int = 1) -> None:
    connection.execute(
        """
        INSERT INTO import_manifest VALUES (
            ?, ?, ?, 1, 1, 1, ?, ?, 'python -m inside_rails.database.build', ?, NULL,
            2, 1, 1, 1, 1, 0, 0, 0, 0, NULL, 1, 'building', NULL
        )
        """,
        (
            manifest_id,
            f"imp:20260805T200000000000Z:{manifest_id:08x}",
            f"db:20260805T200000000000Z:{manifest_id:08x}",
            COMMIT,
            COMMIT,
            TIMESTAMP,
        ),
    )


def test_schema_creates_exact_authorised_tables_and_views() -> None:
    connection = connect_schema()
    try:
        observed_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        observed_views = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type = 'view'"
            )
        }
        assert observed_tables == TABLES
        assert observed_views == VIEWS
        assert connection.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        connection.close()


def test_strict_boundary_and_raw_column_contract() -> None:
    connection = connect_schema()
    try:
        table_list = {
            row[1]: row[5]
            for row in connection.execute("PRAGMA table_list")
            if row[1] in TABLES
        }
        assert table_list["source_raceform_v1_record"] == 0
        assert {name for name, strict in table_list.items() if strict == 1} == TABLES - {
            "source_raceform_v1_record"
        }

        columns = connection.execute("PRAGMA table_xinfo(source_raceform_v1_record)").fetchall()
        assert [row[1] for row in columns] == [*METADATA_COLUMNS, *RAW_COLUMNS]
        raw_column_metadata = columns[len(METADATA_COLUMNS) :]
        assert all(row[2] == "" for row in raw_column_metadata)
        table_sql = connection.execute(
            "SELECT sql FROM sqlite_schema "
            "WHERE type = 'table' AND name = 'source_raceform_v1_record'"
        ).fetchone()[0]
        assert '"or"' in table_sql

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO source_provider VALUES ('not-an-integer', 'p', 'l', 'n', ?)",
                (TIMESTAMP,),
            )
    finally:
        connection.close()


def test_minimum_version_and_connection_pragmas_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="3.37.0"):
        require_supported_sqlite((3, 36, 0))
    require_supported_sqlite(MINIMUM_SQLITE_VERSION)

    database = tmp_path / "candidate.sqlite3"
    connection = sqlite3.connect(database)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA trusted_schema").fetchone()[0] == 0
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 2
    finally:
        connection.close()


def test_query_only_consumer_setting_prevents_writes() -> None:
    connection = connect_schema()
    try:
        configure_governed_connection(connection, query_only=True)
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute(
                "INSERT INTO source_provider VALUES (1, 'p', 'l', 'n', ?)", (TIMESTAMP,)
            )
    finally:
        connection.close()


def test_clean_schema_recreation_is_reproducible_and_refuses_dirty_database(tmp_path: Path) -> None:
    inventories = []
    for name in ("first.sqlite3", "second.sqlite3"):
        connection = connect_schema(tmp_path / name)
        try:
            inventories.append(schema_inventory(connection))
            assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
            assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
            with pytest.raises(ValueError, match="clean database"):
                create_minimum_core_schema(connection)
        finally:
            connection.close()

    assert inventories[0] == inventories[1]


def test_untyped_raw_columns_and_strict_any_preserve_storage_classes() -> None:
    connection = connect_schema()
    try:
        insert_source_metadata(connection, physical_count=6, admitted_count=5, excluded_count=1)
        insert_governance(connection)
        samples = [None, -9, -0.0, "009", b"\x00\xff"]
        for offset, sample in enumerate(samples, start=2):
            values = raw_values(date=sample, course=f"course-{offset}", off=f"off-{offset}")
            insert_raw_record(
                connection,
                source_record_id=offset,
                source_rowid=offset,
                values=values,
            )

        observed = connection.execute(
            'SELECT typeof("date") FROM source_raceform_v1_record ORDER BY source_rowid'
        ).fetchall()
        assert [row[0] for row in observed] == ["null", "integer", "real", "text", "blob"]

        connection.execute(
            "INSERT INTO core_source_race_occurrence VALUES (1, ?, 1, ?, ?, ?, 1, 1)",
            (source_race_occurrence_code(SHA_A, 1), -7, -0.0, b"raw-off"),
        )
        assert connection.execute(
            "SELECT typeof(raw_date), typeof(raw_course), typeof(raw_off) "
            "FROM core_source_race_occurrence"
        ).fetchone() == ("integer", "real", "blob")
    finally:
        connection.close()


def test_retained_excluded_record_and_invalid_statuses_fail_closed() -> None:
    connection = connect_schema()
    try:
        insert_source_metadata(connection)
        with pytest.raises(sqlite3.IntegrityError):
            insert_raw_record(
                connection,
                source_record_id=1,
                source_rowid=1,
                status="admitted_runner_record",
                values=raw_values(),
            )
        with pytest.raises(sqlite3.IntegrityError):
            insert_raw_record(
                connection,
                source_record_id=2,
                source_rowid=2,
                status="retained_excluded_record",
                exclusion_reason="wrong row",
                values=raw_values(),
            )
        with pytest.raises(sqlite3.IntegrityError):
            insert_raw_record(
                connection,
                source_record_id=2,
                source_rowid=2,
                status="unknown_status",
                values=raw_values(),
            )
    finally:
        connection.close()


def test_foreign_keys_and_hash_prefix_collisions_fail_closed() -> None:
    connection = connect_schema()
    try:
        insert_source_metadata(connection)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("DELETE FROM source_provider WHERE source_provider_id = 1")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO source_version VALUES (
                    2, ?, 1, 'other.db', 'Different file.', ?, 124, NULL, ?,
                    1, 1, 0, 'rowid <> 1', '2015-01-01', '2026-05-27', 'ok',
                    'accepted_exact_source', 'Different full hash, colliding code.', ?
                )
                """,
                (source_version_code(SHA_A), SHA_B, SCHEMA_SHA, TIMESTAMP),
            )
    finally:
        connection.close()


def test_race_runner_and_manifest_relationship_triggers_fail_closed() -> None:
    connection = connect_schema()
    try:
        seed_structural_fixture(connection)
        insert_source_metadata(
            connection,
            source_version_id=2,
            source_relation_id=2,
            file_sha256=SHA_B,
            physical_count=1,
            admitted_count=1,
            excluded_count=0,
        )
        insert_governance(
            connection,
            source_version_id=2,
            governance_method_id=2,
            governance_release_id=2,
            file_sha256=SHA_B,
        )

        with pytest.raises(sqlite3.IntegrityError, match="race governance"):
            connection.execute(
                "INSERT INTO core_source_race_occurrence VALUES (2, ?, 1, 'x', 'y', 'z', 1, 2)",
                (source_race_occurrence_code(SHA_A, 2),),
            )

        mismatch = raw_values(date="2026-01-01", course="Ascot", off="13:30", horse="Horse Two")
        insert_raw_record(
            connection,
            source_record_id=3,
            source_rowid=3,
            values=mismatch,
        )
        with pytest.raises(sqlite3.IntegrityError, match="structurally incompatible"):
            connection.execute(
                "INSERT INTO core_runner_participation "
                "VALUES (2, ?, 1, 3, 'admitted_runner_record', 1)",
                (runner_participation_code(SHA_A, 3),),
            )
        with pytest.raises(sqlite3.IntegrityError, match="structurally incompatible"):
            connection.execute(
                "INSERT INTO core_runner_participation "
                "VALUES (2, ?, 1, 2, 'admitted_runner_record', 2)",
                (runner_participation_code(SHA_A, 3),),
            )

        with pytest.raises(sqlite3.IntegrityError, match="manifest governance"):
            connection.execute(
                """
                INSERT INTO import_manifest VALUES (
                    1, 'imp:x', 'db:x', 1, 2, 1, ?, ?, 'build', ?, NULL,
                    2, 1, 1, 1, 1, 0, 0, 0, 0, NULL, 1, 'building', NULL
                )
                """,
                (COMMIT, COMMIT, TIMESTAMP),
            )
    finally:
        connection.close()


def test_manifest_statuses_and_forward_only_transitions_fail_closed() -> None:
    connection = connect_schema()
    try:
        seed_structural_fixture(connection)
        insert_building_manifest(connection)

        with pytest.raises(
            sqlite3.IntegrityError, match="invalid import manifest state transition"
        ):
            connection.execute(
                "UPDATE import_manifest SET build_status = 'validated' "
                "WHERE import_manifest_id = 1"
            )

        connection.execute(
            "UPDATE import_manifest SET build_status = 'built', "
            "build_completed_at_utc = ? WHERE import_manifest_id = 1",
            (TIMESTAMP,),
        )
        with pytest.raises(
            sqlite3.IntegrityError, match="invalid import manifest state transition"
        ):
            connection.execute(
                "UPDATE import_manifest SET build_status = 'building' "
                "WHERE import_manifest_id = 1"
            )

        connection.execute(
            """
            UPDATE import_manifest
            SET build_status = 'validated',
                persisted_readback_passed = 1,
                sqlite_integrity_passed = 1,
                foreign_key_check_passed = 1,
                post_load_validation_passed = 1
            WHERE import_manifest_id = 1
            """
        )
        with pytest.raises(sqlite3.IntegrityError, match="incomplete or inconsistent"):
            connection.execute(
                "UPDATE import_manifest SET build_status = 'release_accepted' "
                "WHERE import_manifest_id = 1"
            )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE import_manifest SET build_status = 'not-a-status' "
                "WHERE import_manifest_id = 1"
            )
    finally:
        connection.close()


def test_import_manifest_must_start_building() -> None:
    connection = connect_schema()
    try:
        seed_structural_fixture(connection)
        with pytest.raises(sqlite3.IntegrityError, match="must begin in building"):
            connection.execute(
                """
                INSERT INTO import_manifest VALUES (
                    1, 'imp:x', 'db:x', 1, 1, 1, ?, ?, 'build', ?, ?,
                    2, 1, 1, 1, 1, 1, 1, 1, 1, NULL, 1, 'built', NULL
                )
                """,
                (COMMIT, COMMIT, TIMESTAMP, TIMESTAMP),
            )
    finally:
        connection.close()


def test_six_views_are_transparent_on_controlled_fixture() -> None:
    connection = connect_schema()
    try:
        seed_structural_fixture(connection)
        insert_building_manifest(connection)
        connection.execute(
            """
            INSERT INTO import_validation_result VALUES (
                1, 1, 'focused_unit_tests', 'pytest', ?, 1, 'passed', ?,
                'pytest tests/test_database_schema_v001.py', 'fixture passed', NULL
            )
            """,
            (COMMIT, TIMESTAMP),
        )

        observed = connection.execute(
            "SELECT COUNT(*) FROM view_source_record_lineage"
        ).fetchone()[0]
        assert observed == 2
        observed = connection.execute(
            "SELECT COUNT(*) FROM view_source_raceform_v1_records"
        ).fetchone()[0]
        assert observed == 2
        observed = connection.execute(
            "SELECT COUNT(*) FROM view_core_source_race_occurrences"
        ).fetchone()[0]
        assert observed == 1
        observed = connection.execute(
            "SELECT COUNT(*) FROM view_core_runner_participations"
        ).fetchone()[0]
        assert observed == 1
        observed = connection.execute(
            "SELECT COUNT(*) FROM view_database_release_evidence"
        ).fetchone()[0]
        assert observed == 1
        observed = connection.execute(
            "SELECT COUNT(*) FROM view_import_validation_evidence"
        ).fetchone()[0]
        assert observed == 1

        excluded = connection.execute(
            'SELECT structural_status, "or", typeof("or") '
            "FROM view_source_raceform_v1_records WHERE source_rowid = 1"
        ).fetchone()
        assert excluded == ("retained_excluded_record", "or", "text")
        runner = connection.execute(
            'SELECT source_rowid, "or", typeof("or") FROM view_core_runner_participations'
        ).fetchone()
        assert runner == (2, 85, "integer")
    finally:
        connection.close()
