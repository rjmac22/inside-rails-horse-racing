"""Prepare a fail-closed Database v3 candidate from accepted Database v2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from inside_rails.database.identifiers import governance_method_code, governance_release_code
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
    EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    configure_governed_connection,
    upgrade_governed_integration_to_external_reconciliation_schema,
)
from inside_rails.source_sqlite import connect_read_only

EXPECTED_BASE_RELEASE_SHA256 = bytes.fromhex(
    "80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe"
)
EXPECTED_BASE_RELEASE_SIZE_BYTES = 3_137_044_480
EXPECTED_BASE_DATABASE_RELEASE_CODE = "db:20260809T081402956098Z:5b29ea51"
EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285
EXPECTED_BASE_MANUAL_VERIFICATION_COUNT = 85
EXPECTED_BASE_VALIDATION_RESULT_COUNT = 7

V3_METHOD_SLUG = "database-v3-external-verification-reconciliation"
V3_RELEASE_SLUG = "database-v3-external-verification-reconciliation"
V3_METHOD_VERSION = 1
V3_RELEASE_VERSION = 1
V3_EVIDENCE = (
    ("document", "docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md", "Canonical Database v3 external-verification reconciliation specification."),
    ("governed_output", "data/reference/external_verification_reconciliation.csv", "Nineteen missing durable pre-Notebook-14 external-verification records."),
    ("governed_output", "data/reference/external_value_resolutions.csv", "Typed analytical correction, enrichment and invalidation decisions for Database v3."),
    ("document", "docs/DATABASE_IMPORT_VALIDATION_GATE.md", "Fail-closed database build and validation gate."),
)


@dataclass(frozen=True)
class V2BaseMetadata:
    source_version_id: int
    v2_governance_release_id: int
    source_file_sha256: bytes
    prior_database_release_code: str


@dataclass(frozen=True)
class ExternalReconciliationPreparationSummary:
    base_release_path: str
    output_path: str
    base_release_sha256_hex: str
    copied_bytes: int
    copy_elapsed_seconds: float
    source_version_id: int
    prior_governance_release_id: int
    external_reconciliation_release_id: int
    manifest_code: str
    database_release_code: str
    prior_database_release_code: str
    application_id: int
    user_version: int
    manifest_status: str


def default_base_release_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/releases/inside_rails_v2.sqlite3"


def default_v3_candidate_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/candidates/inside_rails_v3_candidate.sqlite3"


def _validate_base_release(path: Path) -> V2BaseMetadata:
    if not path.is_file():
        raise FileNotFoundError(f"Accepted Database v2 release not found: {path}")
    require_no_sidecars(path, label="Accepted Database v2 release")
    if path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError(
            "Database v2 base size mismatch: "
            f"expected {EXPECTED_BASE_RELEASE_SIZE_BYTES}, observed {path.stat().st_size}"
        )
    validate_file_hash(path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v2 release")

    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        if int(connection.execute("PRAGMA application_id").fetchone()[0]) != APPLICATION_ID:
            raise RuntimeError("Accepted Database v2 application_id mismatch")
        if int(connection.execute("PRAGMA user_version").fetchone()[0]) != GOVERNED_INTEGRATION_SCHEMA_VERSION:
            raise RuntimeError("Accepted Database v2 user_version mismatch")

        manifest = connection.execute(
            """
            SELECT source_version_id, governance_release_id, database_release_code,
                   schema_version, physical_record_count, admitted_record_count,
                   excluded_record_count, race_occurrence_count,
                   runner_participation_count, build_status, failure_reason
            FROM import_manifest
            """
        ).fetchall()
        if len(manifest) != 1:
            raise RuntimeError(f"Accepted Database v2 manifest count changed: {len(manifest)}")
        row = manifest[0]
        expected = (
            GOVERNED_INTEGRATION_SCHEMA_VERSION,
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_EXCLUDED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
            "release_accepted",
            None,
        )
        if tuple(row[3:]) != expected:
            raise RuntimeError(f"Accepted Database v2 manifest mismatch: {row!r}")
        if str(row[2]) != EXPECTED_BASE_DATABASE_RELEASE_CODE:
            raise RuntimeError(f"Accepted Database v2 release code changed: {row[2]!r}")

        validation_count = int(
            connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0]
        )
        if validation_count != EXPECTED_BASE_VALIDATION_RESULT_COUNT:
            raise RuntimeError(
                f"Accepted Database v2 validation count changed: {validation_count}"
            )
        manual_count = int(
            connection.execute("SELECT COUNT(*) FROM governance_manual_verification").fetchone()[0]
        )
        if manual_count != EXPECTED_BASE_MANUAL_VERIFICATION_COUNT:
            raise RuntimeError(f"Accepted Database v2 manual-verification count changed: {manual_count}")
        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            WHERE source_version_id = ?
            ORDER BY governance_release_id
            """,
            (int(row[0]),),
        ).fetchall()
        if releases != [(1, "superseded", 2), (2, "accepted", None)]:
            raise RuntimeError(f"Accepted Database v2 governance lineage mismatch: {releases!r}")
        if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
            raise RuntimeError("Accepted Database v2 quick_check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Accepted Database v2 foreign_key_check failed")
        source_hash = connection.execute(
            "SELECT file_sha256 FROM source_version WHERE source_version_id = ?",
            (int(row[0]),),
        ).fetchone()
        if source_hash is None or not isinstance(source_hash[0], bytes):
            raise RuntimeError("Accepted Database v2 source SHA is unavailable")

    return V2BaseMetadata(
        source_version_id=int(row[0]),
        v2_governance_release_id=int(row[1]),
        source_file_sha256=bytes(source_hash[0]),
        prior_database_release_code=str(row[2]),
    )


def _insert_v3_governance_and_manifest(
    connection: sqlite3.Connection,
    *,
    base: V2BaseMetadata,
    repository_commit: str,
    reference_data_commit: str,
    manifest_code: str,
    database_release_code: str,
    build_command: str,
    created_at_utc: str,
) -> int:
    next_method_id = int(
        connection.execute("SELECT COALESCE(MAX(governance_method_id),0)+1 FROM governance_method").fetchone()[0]
    )
    next_release_id = int(
        connection.execute("SELECT COALESCE(MAX(governance_release_id),0)+1 FROM governance_release").fetchone()[0]
    )
    connection.execute(
        """
        INSERT INTO governance_method (
            governance_method_id, governance_method_code, method_name,
            method_version, repository_commit, method_description, created_at_utc
        ) VALUES (?, ?, 'Database v3 external verification reconciliation', ?, ?, ?, ?)
        """,
        (
            next_method_id,
            governance_method_code(V3_METHOD_SLUG, V3_METHOD_VERSION),
            V3_METHOD_VERSION,
            repository_commit,
            "Reconciles all recovered exact external verification evidence into an analytically usable successor to immutable Database v2 while preserving raw source assertions.",
            created_at_utc,
        ),
    )

    connection.execute(
        """
        INSERT INTO governance_release (
            governance_release_id, governance_release_code, source_version_id,
            governance_method_id, release_status, accepted_date, repository_commit,
            population_predicate, release_description, superseded_by_release_id,
            created_at_utc
        ) VALUES (?, ?, ?, ?, 'superseded', ?, ?, 'rowid <> 1', ?, ?, ?)
        """,
        (
            next_release_id,
            governance_release_code(base.source_file_sha256, V3_RELEASE_SLUG, V3_RELEASE_VERSION),
            base.source_version_id,
            next_method_id,
            created_at_utc[:10],
            repository_commit,
            "Database v3 external-verification reconciliation release.",
            base.v2_governance_release_id,
            created_at_utc,
        ),
    )
    connection.execute(
        """
        UPDATE governance_release
        SET release_status='superseded', superseded_by_release_id=?
        WHERE governance_release_id=? AND release_status='accepted'
        """,
        (next_release_id, base.v2_governance_release_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to supersede Database v2 governance release in v3 copy")
    connection.execute(
        """
        UPDATE governance_release
        SET release_status='accepted', superseded_by_release_id=NULL
        WHERE governance_release_id=? AND release_status='superseded'
        """,
        (next_release_id,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to accept Database v3 governance release")

    next_evidence_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_evidence_id),0)+1 FROM governance_release_evidence"
        ).fetchone()[0]
    )
    for offset, (kind, reference, description) in enumerate(V3_EVIDENCE):
        connection.execute(
            """
            INSERT INTO governance_release_evidence (
                governance_release_evidence_id, governance_release_id,
                evidence_type, evidence_reference, evidence_sha256,
                evidence_description
            ) VALUES (?, ?, ?, ?, NULL, ?)
            """,
            (next_evidence_id + offset, next_release_id, kind, reference, description),
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
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 0,0,0,0, ?,1,'building',NULL)
        """,
        (
            manifest_code,
            database_release_code,
            base.source_version_id,
            next_release_id,
            EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
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


def prepare_external_reconciliation_candidate(
    base_release_path: str | Path,
    output_path: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    build_command: str = "python scripts/build_inside_rails_v3.py",
    created_at_utc: str | None = None,
    import_suffix: str | None = None,
    database_suffix: str | None = None,
) -> ExternalReconciliationPreparationSummary:
    repository_commit = validate_repository_commit(repository_commit, name="repository_commit")
    reference_data_commit = validate_repository_commit(
        reference_data_commit or repository_commit,
        name="reference_data_commit",
    )
    started_at, compact = timestamp(created_at_utc)
    manifest_code = f"imp:{compact}:{suffix(import_suffix, name='import_suffix')}"
    database_release_code = f"db:{compact}:{suffix(database_suffix, name='database_suffix')}"
    base_path = Path(base_release_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if base_path == output:
        raise ValueError("Database v3 candidate must differ from accepted Database v2")
    existing = [item for item in artifact_paths(output) if item.exists()]
    if existing:
        raise FileExistsError("Database v3 candidate artifact already exists: " + ", ".join(map(str, existing)))

    base = _validate_base_release(base_path)
    base_hash_before = validate_file_hash(
        base_path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v2 release"
    )
    try:
        copied_bytes, copy_elapsed = copy_candidate(base_path, output)
        if sha256_file(output) != base_hash_before:
            raise RuntimeError("Database v3 base copy does not match accepted Database v2")
        connection = sqlite3.connect(output)
        try:
            configure_governed_connection(connection, durable_candidate=True)
            upgrade_governed_integration_to_external_reconciliation_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            release_id = _insert_v3_governance_and_manifest(
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
        require_no_sidecars(output, label="Prepared Database v3 candidate")
        validate_file_hash(
            base_path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v2 release after copy"
        )
    except Exception:
        remove_output(output)
        raise

    with connect_read_only(output) as connection:
        configure_governed_connection(connection, query_only=True)
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        manifest_status = str(connection.execute("SELECT build_status FROM import_manifest").fetchone()[0])

    return ExternalReconciliationPreparationSummary(
        base_release_path=str(base_path),
        output_path=str(output),
        base_release_sha256_hex=base_hash_before.hex(),
        copied_bytes=copied_bytes,
        copy_elapsed_seconds=copy_elapsed,
        source_version_id=base.source_version_id,
        prior_governance_release_id=base.v2_governance_release_id,
        external_reconciliation_release_id=release_id,
        manifest_code=manifest_code,
        database_release_code=database_release_code,
        prior_database_release_code=base.prior_database_release_code,
        application_id=application_id,
        user_version=user_version,
        manifest_status=manifest_status,
    )


__all__ = [
    "ExternalReconciliationPreparationSummary",
    "default_base_release_path",
    "default_v3_candidate_path",
    "prepare_external_reconciliation_candidate",
]
