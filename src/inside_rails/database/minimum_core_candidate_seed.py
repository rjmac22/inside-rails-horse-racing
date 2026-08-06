"""Schema-boundary, governance and manifest seeding for core candidates."""

from __future__ import annotations

import sqlite3

from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
)
from inside_rails.database.minimum_core_candidate_model import GOVERNANCE_EVIDENCE
from inside_rails.database.raw_mirror_prototype import SourceBaseline
from inside_rails.database.schema import create_minimum_core_schema, schema_inventory


def expected_schema_inventory() -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(":memory:")
    try:
        create_minimum_core_schema(connection)
        return schema_inventory(connection)
    finally:
        connection.close()


def validate_raw_boundary(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
) -> None:
    if schema_inventory(connection) != expected_schema_inventory():
        raise RuntimeError("Minimum-core candidate schema inventory mismatch")

    version = connection.execute(
        """
        SELECT file_sha256, physical_record_count, admitted_record_count,
               excluded_record_count, admission_predicate
        FROM source_version
        WHERE source_version_id = 1
        """
    ).fetchone()
    expected_version = (
        source_sha256,
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        "rowid <> 1",
    )
    if version != expected_version:
        raise RuntimeError("Raw-mirror source-version metadata mismatch")

    population = connection.execute(
        """
        SELECT COUNT(*),
               SUM(structural_status = 'admitted_runner_record'),
               SUM(structural_status = 'retained_excluded_record'),
               SUM(row_sha256 IS NOT NULL)
        FROM source_raceform_v1_record
        WHERE source_version_id = 1 AND source_relation_id = 1
        """
    ).fetchone()
    expected_population = (
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        baseline.physical_record_count,
    )
    if population is None or tuple(int(value) for value in population) != expected_population:
        raise RuntimeError(
            "Raw-mirror population mismatch: "
            f"expected {expected_population!r}; observed {population!r}"
        )

    downstream = connection.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM governance_method),
            (SELECT COUNT(*) FROM governance_release),
            (SELECT COUNT(*) FROM governance_release_evidence),
            (SELECT COUNT(*) FROM core_source_race_occurrence),
            (SELECT COUNT(*) FROM core_runner_participation),
            (SELECT COUNT(*) FROM import_manifest),
            (SELECT COUNT(*) FROM import_validation_result)
        """
    ).fetchone()
    if downstream is None or tuple(int(value) for value in downstream) != (0,) * 7:
        raise RuntimeError(
            "Raw-mirror candidate is not at the required raw-only boundary: "
            f"{downstream!r}"
        )


def insert_governance(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    repository_commit: str,
    timestamp: str,
) -> None:
    connection.execute(
        "INSERT INTO governance_method VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            governance_method_code("source-v1-structure", 1),
            "Source Version 1 structural reconstruction",
            1,
            repository_commit,
            "Groups admitted raw records by exact date + course + off and creates "
            "one runner participation per admitted source record.",
            timestamp,
        ),
    )
    connection.execute(
        "INSERT INTO governance_release VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)",
        (
            1,
            governance_release_code(source_sha256, "source-v1-structure", 1),
            1,
            1,
            "accepted",
            timestamp[:10],
            repository_commit,
            "rowid <> 1",
            "Accepted Source Version 1 structural method used by a complete disposable "
            "minimum-core candidate; this is not an accepted database release.",
            timestamp,
        ),
    )
    connection.executemany(
        "INSERT INTO governance_release_evidence VALUES (?, 1, ?, ?, NULL, ?)",
        [
            (index, evidence_type, reference, description)
            for index, (evidence_type, reference, description) in enumerate(
                GOVERNANCE_EVIDENCE,
                start=1,
            )
        ],
    )


def insert_manifest(
    connection: sqlite3.Connection,
    *,
    manifest_code: str,
    database_release_code: str,
    repository_commit: str,
    reference_data_commit: str,
    build_command: str,
    started_at: str,
    baseline: SourceBaseline,
    expected_race_count: int,
) -> None:
    connection.execute(
        """
        INSERT INTO import_manifest (
            import_manifest_id, import_manifest_code, database_release_code,
            source_version_id, governance_release_id, schema_version,
            code_commit, reference_data_commit, build_command,
            build_started_at_utc, build_completed_at_utc,
            physical_record_count, admitted_record_count, excluded_record_count,
            race_occurrence_count, runner_participation_count,
            persisted_readback_passed, sqlite_integrity_passed,
            foreign_key_check_passed, post_load_validation_passed,
            prior_database_release_code, prior_release_preserved,
            build_status, failure_reason
        ) VALUES (
            1, ?, ?, 1, 1, 1, ?, ?, ?, ?, NULL,
            ?, ?, ?, ?, ?, 0, 0, 0, 0, NULL, 1, 'building', NULL
        )
        """,
        (
            manifest_code,
            database_release_code,
            repository_commit,
            reference_data_commit,
            build_command,
            started_at,
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
            expected_race_count,
            baseline.admitted_record_count,
        ),
    )
