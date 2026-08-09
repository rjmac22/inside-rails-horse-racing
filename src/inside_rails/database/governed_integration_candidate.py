"""Prepare a fail-closed Database v2 governed-integration candidate.

Database v2 deliberately starts from an exact copied accepted Database v1 release.
The v1 file remains immutable and is independently hash-checked before and after
preparation. The copied candidate is migrated to schema version 2, receives a
new governed integration release and a fresh v2 build manifest, and is then ready
for governed Notebook 04–22 population.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
)
from inside_rails.database.minimum_core_candidate_io import (
    copy_candidate,
    remove_output,
    require_no_sidecars,
    validate_file_hash,
)
from inside_rails.database.minimum_core_candidate_model import (
    artifact_paths,
    repository_commit as validate_repository_commit,
    suffix,
    timestamp,
)
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    SCHEMA_VERSION,
    configure_governed_connection,
    upgrade_minimum_core_to_governed_integration_schema,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_BASE_RELEASE_SHA256 = bytes.fromhex(
    "2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934"
)
EXPECTED_BASE_RELEASE_SIZE_BYTES = 1_730_048_000
EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285
EXPECTED_BASE_VALIDATION_RESULT_COUNT = 7

V2_GOVERNANCE_METHOD_SLUG = "database-v2-governed-integration"
V2_GOVERNANCE_RELEASE_SLUG = "database-v2-governed-integration"
V2_GOVERNANCE_METHOD_VERSION = 1
V2_GOVERNANCE_RELEASE_VERSION = 1

V2_GOVERNANCE_EVIDENCE = (
    (
        "document",
        "docs/DATABASE_V2_GOVERNED_INTEGRATION_DESIGN.md",
        "Canonical Database v2 Notebook 04–22 governed integration design.",
    ),
    (
        "document",
        "docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md",
        "Accepted SQLite architecture and immutable release controls inherited by Database v2.",
    ),
    (
        "document",
        "docs/DATABASE_IMPORT_VALIDATION_GATE.md",
        "Fail-closed database build, validation and last-known-good protection gate.",
    ),
)


@dataclass(frozen=True)
class BaseReleaseMetadata:
    source_version_id: int
    structural_governance_release_id: int
    prior_database_release_code: str
    source_file_sha256: bytes


@dataclass(frozen=True)
class GovernedIntegrationPreparationSummary:
    base_release_path: str
    output_path: str
    base_release_sha256_hex: str
    prepared_candidate_sha256_hex: str
    copied_bytes: int
    copy_elapsed_seconds: float
    source_version_id: int
    structural_governance_release_id: int
    governed_integration_release_id: int
    manifest_code: str
    database_release_code: str
    prior_database_release_code: str
    application_id: int
    user_version: int
    quick_check: str
    foreign_key_check_rows: int
    manifest_status: str


def default_base_release_path(project_root: str | Path) -> Path:
    """Return the exact accepted Database v1 release used as the v2 base."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v1.sqlite3"
    )


def default_v2_candidate_path(project_root: str | Path) -> Path:
    """Return the canonical Database v2 candidate path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v2_candidate.sqlite3"
    )


def _validate_base_release(path: Path) -> BaseReleaseMetadata:
    """Prove that the v2 base is the exact accepted Database v1 release."""

    if path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError(
            "Database v1 base-release size mismatch: "
            f"expected {EXPECTED_BASE_RELEASE_SIZE_BYTES}, observed {path.stat().st_size}"
        )
    validate_file_hash(path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v1 release")

    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID or user_version != SCHEMA_VERSION:
            raise RuntimeError("Accepted Database v1 SQLite header mismatch")

        manifest_rows = connection.execute(
            """
            SELECT source_version_id, governance_release_id, database_release_code,
                   schema_version, physical_record_count, admitted_record_count,
                   excluded_record_count, race_occurrence_count,
                   runner_participation_count, persisted_readback_passed,
                   sqlite_integrity_passed, foreign_key_check_passed,
                   post_load_validation_passed, prior_release_preserved,
                   build_status, failure_reason
            FROM import_manifest
            """
        ).fetchall()
        if len(manifest_rows) != 1:
            raise RuntimeError(
                f"Accepted Database v1 must contain exactly one manifest; found {len(manifest_rows)}"
            )
        manifest = manifest_rows[0]
        expected_tail = (
            1,
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_EXCLUDED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
            1,
            1,
            1,
            1,
            1,
            "release_accepted",
            None,
        )
        if tuple(manifest[3:]) != expected_tail:
            raise RuntimeError(f"Accepted Database v1 manifest mismatch: {manifest!r}")

        validation_count = int(
            connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0]
        )
        if validation_count != EXPECTED_BASE_VALIDATION_RESULT_COUNT:
            raise RuntimeError(
                "Accepted Database v1 validation-evidence count mismatch: "
                f"expected {EXPECTED_BASE_VALIDATION_RESULT_COUNT}, observed {validation_count}"
            )

        quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Accepted Database v1 quick_check failed: {quick!r}")
        foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_rows:
            raise RuntimeError(
                "Accepted Database v1 foreign_key_check returned rows: "
                f"{foreign_key_rows[:5]}"
            )

        source_version_id = int(manifest[0])
        structural_release_id = int(manifest[1])
        source_hash_row = connection.execute(
            "SELECT file_sha256 FROM source_version WHERE source_version_id = ?",
            (source_version_id,),
        ).fetchone()
        if source_hash_row is None or not isinstance(source_hash_row[0], bytes):
            raise RuntimeError("Accepted Database v1 source-version SHA-256 is unavailable")
        source_file_sha256 = bytes(source_hash_row[0])

    return BaseReleaseMetadata(
        source_version_id=source_version_id,
        structural_governance_release_id=structural_release_id,
        prior_database_release_code=str(manifest[2]),
        source_file_sha256=source_file_sha256,
    )


def _insert_v2_governance_and_manifest(
    connection: sqlite3.Connection,
    *,
    base: BaseReleaseMetadata,
    repository_commit: str,
    reference_data_commit: str,
    manifest_code: str,
    database_release_code: str,
    build_command: str,
    created_at_utc: str,
) -> int:
    """Create the v2 semantic governance release without rewriting core lineage."""

    next_method_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_method_id), 0) + 1 FROM governance_method"
        ).fetchone()[0]
    )
    next_release_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_id), 0) + 1 FROM governance_release"
        ).fetchone()[0]
    )

    connection.execute(
        """
        INSERT INTO governance_method (
            governance_method_id, governance_method_code, method_name,
            method_version, repository_commit, method_description, created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            next_method_id,
            governance_method_code(
                V2_GOVERNANCE_METHOD_SLUG,
                V2_GOVERNANCE_METHOD_VERSION,
            ),
            "Database v2 governed integration",
            V2_GOVERNANCE_METHOD_VERSION,
            repository_commit,
            "Integrates the accepted Notebook 04–22 governed semantic, correction, supplementation and provisional-identity outputs while preserving Database v1 structural lineage.",
            created_at_utc,
        ),
    )

    # The v1 schema permits only one accepted governance release per source
    # version. Insert the new row temporarily as superseded, supersede the v1
    # release, then atomically make v2 the accepted current release. The final
    # committed state contains no temporary reverse-supersession relationship.
    connection.execute(
        """
        INSERT INTO governance_release (
            governance_release_id, governance_release_code, source_version_id,
            governance_method_id, release_status, accepted_date,
            repository_commit, population_predicate, release_description,
            superseded_by_release_id, created_at_utc
        ) VALUES (?, ?, ?, ?, 'superseded', ?, ?, 'rowid <> 1', ?, ?, ?)
        """,
        (
            next_release_id,
            governance_release_code(
                base.source_file_sha256,
                V2_GOVERNANCE_RELEASE_SLUG,
                V2_GOVERNANCE_RELEASE_VERSION,
            ),
            base.source_version_id,
            next_method_id,
            created_at_utc[:10],
            repository_commit,
            "Database v2 governed integration release for the existing Source Version 1 structural core.",
            base.structural_governance_release_id,
            created_at_utc,
        ),
    )
    connection.execute(
        """
        UPDATE governance_release
        SET release_status = 'superseded', superseded_by_release_id = ?
        WHERE governance_release_id = ? AND release_status = 'accepted'
        """,
        (next_release_id, base.structural_governance_release_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to supersede the Database v1 structural governance release")
    connection.execute(
        """
        UPDATE governance_release
        SET release_status = 'accepted', superseded_by_release_id = NULL
        WHERE governance_release_id = ? AND release_status = 'superseded'
        """,
        (next_release_id,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to accept the Database v2 governance release")

    next_evidence_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_evidence_id), 0) + 1 FROM governance_release_evidence"
        ).fetchone()[0]
    )
    for offset, (evidence_type, evidence_reference, description) in enumerate(
        V2_GOVERNANCE_EVIDENCE
    ):
        connection.execute(
            """
            INSERT INTO governance_release_evidence (
                governance_release_evidence_id, governance_release_id,
                evidence_type, evidence_reference, evidence_sha256,
                evidence_description
            ) VALUES (?, ?, ?, ?, NULL, ?)
            """,
            (
                next_evidence_id + offset,
                next_release_id,
                evidence_type,
                evidence_reference,
                description,
            ),
        )

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
            1, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL,
            ?, ?, ?, ?, ?, 0, 0, 0, 0, ?, 1, 'building', NULL
        )
        """,
        (
            manifest_code,
            database_release_code,
            base.source_version_id,
            next_release_id,
            GOVERNED_INTEGRATION_SCHEMA_VERSION,
            repository_commit,
            reference_data_commit,
            build_command,
            created_at_utc,
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_EXCLUDED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
            base.prior_database_release_code,
        ),
    )

    return next_release_id


def prepare_governed_integration_candidate(
    base_release_path: str | Path,
    output_path: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    build_command: str = "python scripts/build_inside_rails_v2.py",
    created_at_utc: str | None = None,
    import_suffix: str | None = None,
    database_suffix: str | None = None,
) -> GovernedIntegrationPreparationSummary:
    """Copy, migrate and seed a Database v2 candidate ready for population."""

    repository_commit = validate_repository_commit(
        repository_commit,
        name="repository_commit",
    )
    reference_data_commit = validate_repository_commit(
        reference_data_commit or repository_commit,
        name="reference_data_commit",
    )
    if not isinstance(build_command, str) or not build_command.strip():
        raise ValueError("build_command must be non-empty text")

    started_at, compact_timestamp = timestamp(created_at_utc)
    manifest_code = (
        f"imp:{compact_timestamp}:{suffix(import_suffix, name='import_suffix')}"
    )
    database_release_code = (
        f"db:{compact_timestamp}:{suffix(database_suffix, name='database_suffix')}"
    )

    base_release = Path(base_release_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if base_release == output:
        raise ValueError("Database v2 candidate path must differ from Database v1 release")
    existing = [path for path in artifact_paths(output) if path.exists()]
    if existing:
        raise FileExistsError(
            "Database v2 candidate artifact already exists: "
            + ", ".join(str(path) for path in existing)
        )

    base = _validate_base_release(base_release)
    base_hash_before = validate_file_hash(
        base_release,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v1 release",
    )

    try:
        copied_bytes, copy_elapsed = copy_candidate(base_release, output)
        if sha256_file(output) != base_hash_before:
            raise RuntimeError("Database v2 base copy does not match accepted Database v1")

        connection = sqlite3.connect(output)
        try:
            configure_governed_connection(connection, durable_candidate=True)
            upgrade_minimum_core_to_governed_integration_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            v2_release_id = _insert_v2_governance_and_manifest(
                connection,
                base=base,
                repository_commit=repository_commit,
                reference_data_commit=reference_data_commit,
                manifest_code=manifest_code,
                database_release_code=database_release_code,
                build_command=build_command.strip(),
                created_at_utc=started_at,
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        require_no_sidecars(output, label="Database v2 candidate")
        with connect_read_only(output) as connection:
            configure_governed_connection(connection, query_only=True)
            application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
            user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            manifest_status = str(
                connection.execute(
                    "SELECT build_status FROM import_manifest WHERE import_manifest_id = 1"
                ).fetchone()[0]
            )
            quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
            foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
            if application_id != APPLICATION_ID:
                raise RuntimeError("Prepared Database v2 application_id mismatch")
            if user_version != GOVERNED_INTEGRATION_SCHEMA_VERSION:
                raise RuntimeError("Prepared Database v2 user_version mismatch")
            if manifest_status != "building":
                raise RuntimeError("Prepared Database v2 manifest must remain building")
            if quick != "ok" or foreign_key_rows:
                raise RuntimeError("Prepared Database v2 failed SQLite integrity checks")

        base_hash_after = validate_file_hash(
            base_release,
            EXPECTED_BASE_RELEASE_SHA256,
            label="Accepted Database v1 release",
        )
        if base_hash_after != base_hash_before:
            raise RuntimeError("Accepted Database v1 changed during Database v2 preparation")
    except Exception:
        remove_output(output)
        raise

    return GovernedIntegrationPreparationSummary(
        base_release_path=str(base_release),
        output_path=str(output),
        base_release_sha256_hex=base_hash_before.hex(),
        prepared_candidate_sha256_hex=sha256_file(output).hex(),
        copied_bytes=copied_bytes,
        copy_elapsed_seconds=copy_elapsed,
        source_version_id=base.source_version_id,
        structural_governance_release_id=base.structural_governance_release_id,
        governed_integration_release_id=v2_release_id,
        manifest_code=manifest_code,
        database_release_code=database_release_code,
        prior_database_release_code=base.prior_database_release_code,
        application_id=application_id,
        user_version=user_version,
        quick_check=quick,
        foreign_key_check_rows=foreign_key_rows,
        manifest_status=manifest_status,
    )


__all__ = [
    "EXPECTED_BASE_RELEASE_SHA256",
    "EXPECTED_BASE_RELEASE_SIZE_BYTES",
    "GovernedIntegrationPreparationSummary",
    "default_base_release_path",
    "default_v2_candidate_path",
    "prepare_governed_integration_candidate",
]
