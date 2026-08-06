"""Manifest finalisation and final structural checks for core candidates."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from inside_rails.database.minimum_core_candidate_model import VALIDATION_ROWS
from inside_rails.database.raw_mirror_prototype import SourceBaseline
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only


def finalise_manifest(
    output: Path,
    *,
    completed_at: str,
    build_command: str,
) -> None:
    connection = sqlite3.connect(output)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        connection.execute("BEGIN IMMEDIATE")
        connection.executemany(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id,
                validation_stage, validator_name, validator_version,
                required_for_acceptance, outcome, executed_at_utc,
                command, result_summary, details_artifact_path
            ) VALUES (?, 1, ?, ?, ?, 1, 'passed', ?, ?, ?, NULL)
            """,
            [
                (
                    index,
                    stage,
                    validator_name,
                    validator_version,
                    completed_at,
                    build_command,
                    summary,
                )
                for index, (
                    stage,
                    validator_name,
                    validator_version,
                    summary,
                ) in enumerate(VALIDATION_ROWS, start=1)
            ],
        )
        connection.execute(
            """
            UPDATE import_manifest
            SET build_completed_at_utc = ?,
                persisted_readback_passed = 1,
                sqlite_integrity_passed = 1,
                foreign_key_check_passed = 1,
                post_load_validation_passed = 1,
                build_status = 'built'
            WHERE import_manifest_id = 1
            """,
            (completed_at,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def validate_final_manifest(
    output: Path,
    *,
    manifest_code: str,
    database_release_code: str,
    baseline: SourceBaseline,
    expected_race_count: int,
) -> tuple[str, int, str, int, int, int]:
    with connect_read_only(output) as connection:
        configure_governed_connection(connection, query_only=True)
        manifest = connection.execute(
            """
            SELECT import_manifest_code, database_release_code,
                   physical_record_count, admitted_record_count,
                   excluded_record_count, race_occurrence_count,
                   runner_participation_count, persisted_readback_passed,
                   sqlite_integrity_passed, foreign_key_check_passed,
                   post_load_validation_passed, prior_release_preserved,
                   build_status, failure_reason, build_completed_at_utc
            FROM import_manifest WHERE import_manifest_id = 1
            """
        ).fetchone()
        if manifest is None:
            raise RuntimeError("Final import manifest is missing")
        expected_prefix = (
            manifest_code,
            database_release_code,
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
            expected_race_count,
            baseline.admitted_record_count,
            1,
            1,
            1,
            1,
            1,
            "built",
            None,
        )
        if tuple(manifest[:14]) != expected_prefix or manifest[14] is None:
            raise RuntimeError(f"Final import manifest mismatch: {manifest!r}")

        results = connection.execute(
            """
            SELECT validation_stage, outcome, required_for_acceptance
            FROM import_validation_result
            ORDER BY import_validation_result_id
            """
        ).fetchall()
        expected_results = [
            (stage, "passed", 1) for stage, _, _, _ in VALIDATION_ROWS
        ]
        if results != expected_results:
            raise RuntimeError(f"Final validation-result population mismatch: {results!r}")

        accepted_count = connection.execute(
            "SELECT COUNT(*) FROM import_manifest WHERE build_status = 'release_accepted'"
        ).fetchone()[0]
        if accepted_count:
            raise RuntimeError("Disposable candidate must not be release accepted")

        quick_row = connection.execute("PRAGMA quick_check").fetchone()
        quick = "" if quick_row is None else str(quick_row[0])
        if quick != "ok":
            raise RuntimeError(f"Final minimum-core quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Final minimum-core foreign_key_check returned {foreign_key_rows} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID or user_version != SCHEMA_VERSION:
            raise RuntimeError("Final minimum-core SQLite header mismatch")

    return (
        "built",
        len(results),
        quick,
        foreign_key_rows,
        application_id,
        user_version,
    )
