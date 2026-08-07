from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3

import pytest

from inside_rails.database.active_resolver import (
    connect_active_database,
    resolve_active_release,
)
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.release_manifest import (
    load_json_object,
    replace_json_atomic,
    write_new_json_atomic,
)
from inside_rails.database.release_model import (
    ACTIVE_MANIFEST_SCHEMA_VERSION,
    RELEASE_MANIFEST_SCHEMA_VERSION,
    ActiveDatabaseManifest,
    ReleaseManifest,
)
from inside_rails.database.release_paths import (
    relative_to_project,
    release_paths,
    safe_release_slug,
)
from inside_rails.database.schema import APPLICATION_ID, SCHEMA_VERSION


DATABASE_RELEASE_CODE = "db:20260807T010200000000Z:1234abcd"
IMPORT_MANIFEST_CODE = "imp:20260807T010100000000Z:8765abcd"
SOURCE_VERSION_CODE = "sv:" + "a" * 24
SOURCE_FILE_SHA256_HEX = "a" * 64
GOVERNANCE_RELEASE_CODE = "gr:" + "a" * 24 + ":source-v1-structure:v1"
CODE_COMMIT = "b" * 40
REFERENCE_COMMIT = "c" * 40
ACCEPTED_AT = "2026-08-07T01:02:00.000000Z"
ACTIVATED_AT = "2026-08-07T01:03:00.000000Z"
REQUIRED_STAGES = (
    "focused_unit_tests",
    "source_wide_validation",
    "persisted_readback",
    "sqlite_integrity",
    "foreign_key_validation",
    "post_load_validation",
    "project_acceptance_gate",
)


def create_accepted_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(f"PRAGMA application_id = {APPLICATION_ID}")
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        connection.executescript(
            """
            CREATE TABLE source_version (
                source_version_id INTEGER PRIMARY KEY,
                source_version_code TEXT NOT NULL,
                file_sha256 BLOB NOT NULL
            );
            CREATE TABLE governance_release (
                governance_release_id INTEGER PRIMARY KEY,
                governance_release_code TEXT NOT NULL
            );
            CREATE TABLE import_manifest (
                import_manifest_id INTEGER PRIMARY KEY,
                database_release_code TEXT NOT NULL,
                import_manifest_code TEXT NOT NULL,
                code_commit TEXT NOT NULL,
                reference_data_commit TEXT NOT NULL,
                build_status TEXT NOT NULL,
                post_load_validation_passed INTEGER NOT NULL,
                source_version_id INTEGER NOT NULL,
                governance_release_id INTEGER NOT NULL
            );
            CREATE TABLE import_validation_result (
                import_manifest_id INTEGER NOT NULL,
                validation_stage TEXT NOT NULL,
                outcome TEXT NOT NULL,
                required_for_acceptance INTEGER NOT NULL
            );
            """
        )
        connection.execute(
            "INSERT INTO source_version VALUES (1, ?, ?)",
            (SOURCE_VERSION_CODE, bytes.fromhex(SOURCE_FILE_SHA256_HEX)),
        )
        connection.execute(
            "INSERT INTO governance_release VALUES (1, ?)",
            (GOVERNANCE_RELEASE_CODE,),
        )
        connection.execute(
            """
            INSERT INTO import_manifest VALUES (
                1, ?, ?, ?, ?, 'release_accepted', 1, 1, 1
            )
            """,
            (
                DATABASE_RELEASE_CODE,
                IMPORT_MANIFEST_CODE,
                CODE_COMMIT,
                REFERENCE_COMMIT,
            ),
        )
        connection.executemany(
            "INSERT INTO import_validation_result VALUES (1, ?, 'passed', 1)",
            [(stage,) for stage in REQUIRED_STAGES],
        )
        connection.commit()
    finally:
        connection.close()


def create_active_fixture(
    tmp_path: Path,
) -> tuple[Path, ReleaseManifest, ActiveDatabaseManifest]:
    paths = release_paths(tmp_path, DATABASE_RELEASE_CODE)
    create_accepted_database(paths.release_database)
    database_hash = sha256_file(paths.release_database).hex()

    release = ReleaseManifest(
        manifest_schema_version=RELEASE_MANIFEST_SCHEMA_VERSION,
        database_release_code=DATABASE_RELEASE_CODE,
        database_relative_path=relative_to_project(tmp_path, paths.release_database),
        database_file_sha256_hex=database_hash,
        database_file_size_bytes=paths.release_database.stat().st_size,
        sqlite_application_id=APPLICATION_ID,
        sqlite_user_version=SCHEMA_VERSION,
        source_version_code=SOURCE_VERSION_CODE,
        source_file_sha256_hex=SOURCE_FILE_SHA256_HEX,
        import_manifest_code=IMPORT_MANIFEST_CODE,
        governance_release_code=GOVERNANCE_RELEASE_CODE,
        code_commit=CODE_COMMIT,
        reference_data_commit=REFERENCE_COMMIT,
        release_accepted_at_utc=ACCEPTED_AT,
        physical_record_count=8,
        admitted_record_count=7,
        excluded_record_count=1,
        race_occurrence_count=4,
        runner_participation_count=7,
        required_validation_status="passed",
        required_validation_count=7,
        release_gate_evidence_path="docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md",
        prior_database_release_code=None,
        prior_release_preserved=True,
    )
    release_temporary = paths.release_manifest.with_name(
        f"{paths.release_manifest.name}.tmp"
    )
    write_new_json_atomic(
        paths.release_manifest,
        release_temporary,
        release.to_mapping(),
    )

    active = ActiveDatabaseManifest(
        active_manifest_schema_version=ACTIVE_MANIFEST_SCHEMA_VERSION,
        database_release_code=DATABASE_RELEASE_CODE,
        database_relative_path=release.database_relative_path,
        release_manifest_relative_path=relative_to_project(
            tmp_path, paths.release_manifest
        ),
        database_file_sha256_hex=database_hash,
        source_version_code=SOURCE_VERSION_CODE,
        import_manifest_code=IMPORT_MANIFEST_CODE,
        code_commit=CODE_COMMIT,
        activated_at_utc=ACTIVATED_AT,
        post_load_validation_passed=True,
        previous_active_database_release_code=None,
    )
    active_temporary = paths.active_database_manifest.with_name(
        f"{paths.active_database_manifest.name}.tmp"
    )
    replace_json_atomic(
        paths.active_database_manifest,
        active_temporary,
        active.to_mapping(),
    )
    return paths.release_database, release, active


def test_safe_release_slug_is_portable_and_deterministic() -> None:
    assert safe_release_slug(DATABASE_RELEASE_CODE) == (
        "db_20260807T010200000000Z_1234abcd"
    )
    with pytest.raises(ValueError):
        safe_release_slug("db:unsafe")


def test_release_manifest_rejects_path_traversal(tmp_path: Path) -> None:
    _, release, _ = create_active_fixture(tmp_path)
    payload = release.to_mapping()
    payload["database_relative_path"] = "../outside.sqlite3"
    with pytest.raises(ValueError, match="safe relative POSIX path"):
        ReleaseManifest.from_mapping(payload)


def test_active_resolver_verifies_release_and_returns_query_only_connection(
    tmp_path: Path,
) -> None:
    database, release, _ = create_active_fixture(tmp_path)
    original_hash = sha256_file(database)

    resolved = resolve_active_release(tmp_path)
    assert resolved.database_path == database
    assert resolved.release_manifest == release

    with connect_active_database(tmp_path) as connection:
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        assert connection.execute(
            "SELECT database_release_code FROM import_manifest"
        ).fetchone()[0] == DATABASE_RELEASE_CODE
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("CREATE TABLE forbidden_write (value INTEGER)")

    assert sha256_file(database) == original_hash


def test_active_resolver_rejects_changed_database_hash(tmp_path: Path) -> None:
    database, _, _ = create_active_fixture(tmp_path)
    with database.open("r+b") as handle:
        handle.seek(100)
        original = handle.read(1)
        handle.seek(100)
        handle.write(bytes([original[0] ^ 0x01]))

    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        resolve_active_release(tmp_path)


def test_active_resolver_rejects_manifest_disagreement(tmp_path: Path) -> None:
    _, _, active = create_active_fixture(tmp_path)
    paths = release_paths(tmp_path, DATABASE_RELEASE_CODE)
    payload = active.to_mapping()
    payload["code_commit"] = "d" * 40
    paths.active_database_manifest.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="manifests differ"):
        resolve_active_release(tmp_path)


def test_active_resolver_rejects_path_outside_releases(tmp_path: Path) -> None:
    _, release, active = create_active_fixture(tmp_path)
    paths = release_paths(tmp_path, DATABASE_RELEASE_CODE)
    outside_path = "data/processed/database/candidates/not-a-release.sqlite3"

    active_payload = active.to_mapping()
    active_payload["database_relative_path"] = outside_path
    paths.active_database_manifest.write_text(
        json.dumps(active_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    release_payload = release.to_mapping()
    release_payload["database_relative_path"] = outside_path
    paths.release_manifest.write_text(
        json.dumps(release_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes governed releases directory"):
        resolve_active_release(tmp_path)


@pytest.mark.skipif(os.name != "posix", reason="symbolic-link semantics are POSIX-specific")
def test_active_resolver_rejects_database_symlink(tmp_path: Path) -> None:
    database, _, _ = create_active_fixture(tmp_path)
    real_database = database.with_name(f"{database.name}.real")
    database.rename(real_database)
    database.symlink_to(real_database.name)

    with pytest.raises(RuntimeError, match="symbolic link"):
        resolve_active_release(tmp_path)


def test_json_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"value": 1, "value": 2}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate JSON object key"):
        load_json_object(duplicate, name="test manifest")