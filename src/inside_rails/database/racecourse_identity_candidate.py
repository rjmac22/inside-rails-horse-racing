"""Build a governed Database v4 candidate with Study 03 racecourse identities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sqlite3
from time import perf_counter

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
from inside_rails.database.racecourse_identity_reference import (
    RACECOURSE_DIRECTORY,
    STUDY03_EVIDENCE_COMMIT,
    STUDY03_NOTEBOOK,
    Study03ReferenceSummary,
    load_study03_racecourse_identity,
)
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
    RACECOURSE_IDENTITY_SCHEMA_VERSION,
    configure_governed_connection,
    upgrade_external_reconciliation_to_racecourse_identity_schema,
)
from inside_rails.source_sqlite import connect_read_only

EXPECTED_BASE_RELEASE_SHA256 = bytes.fromhex(
    "aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0"
)
EXPECTED_BASE_RELEASE_SIZE_BYTES = 3_137_081_344
EXPECTED_BASE_DATABASE_RELEASE_CODE = "db:20260809T132557790891Z:84258cbc"
EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285
EXPECTED_BASE_VALIDATION_RESULT_COUNT = 7
EXPECTED_BASE_GOVERNANCE_RELEASE_ID = 3

V4_METHOD_SLUG = "database-v4-gb-racecourse-course-identity"
V4_RELEASE_SLUG = "database-v4-gb-racecourse-course-identity"
V4_METHOD_VERSION = 1
V4_RELEASE_VERSION = 1
V4_EVIDENCE = (
    (
        "document",
        "docs/DATABASE_V4_GB_RACECOURSE_IDENTITY_INTEGRATION.md",
        "Database v4 Study 03 integration contract.",
    ),
    (
        "repository_artifact",
        STUDY03_NOTEBOOK,
        f"Completed Study 03 national consolidation at evidence commit {STUDY03_EVIDENCE_COMMIT}.",
    ),
    (
        "repository_artifact",
        RACECOURSE_DIRECTORY,
        "Sixty completed per-racecourse evidence notebooks used as the governed reference source.",
    ),
    (
        "document",
        "docs/DATABASE_IMPORT_VALIDATION_GATE.md",
        "Fail-closed database build and validation gate.",
    ),
)

BUILDER_VALIDATION_ROWS = (
    (
        "persisted_readback",
        "database-v4-racecourse-identity-builder",
        "1",
        "Study 03 reference tables read back at 60 notebooks, 65 source mappings, "
        "60 racecourse identities, 90 inventory rows, 86 stable course identities and "
        "7 unresolved questions.",
    ),
    (
        "sqlite_integrity",
        "sqlite-quick-check",
        sqlite3.sqlite_version,
        "PRAGMA quick_check returned exactly ok after Database v4 population.",
    ),
    (
        "foreign_key_validation",
        "sqlite-foreign-key-check",
        sqlite3.sqlite_version,
        "PRAGMA foreign_key_check returned zero rows after Database v4 population.",
    ),
    (
        "post_load_validation",
        "database-v4-racecourse-identity-builder",
        "1",
        "Study 03 source-label mappings reconcile exactly to the existing Great Britain "
        "reference_course population; no race occurrence was assigned to a physical track.",
    ),
)


@dataclass(frozen=True)
class V3BaseMetadata:
    source_version_id: int
    v3_governance_release_id: int
    source_file_sha256: bytes
    prior_database_release_code: str


@dataclass(frozen=True)
class RacecourseIdentityBuildSummary:
    output_path: str
    base_release_path: str
    repository_commit: str
    reference_data_commit: str
    racecourse_identity_release_id: int
    manifest_code: str
    database_release_code: str
    reference: dict[str, int]
    final_candidate_sha256_hex: str
    final_manifest_status: str
    validation_result_count: int
    build_elapsed_seconds: float
    independent_source_wide_validation_required: bool
    release_accepted: bool


def default_base_release_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/releases/inside_rails_v3.sqlite3"


def default_v4_candidate_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/candidates/inside_rails_v4_candidate.sqlite3"


def _validate_base_release(path: Path) -> V3BaseMetadata:
    if not path.is_file():
        raise FileNotFoundError(f"Accepted Database v3 release not found: {path}")
    require_no_sidecars(path, label="Accepted Database v3 release")
    if path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError(
            "Database v3 base size mismatch: "
            f"expected {EXPECTED_BASE_RELEASE_SIZE_BYTES}, observed {path.stat().st_size}"
        )
    validate_file_hash(path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v3 release")

    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        header = (
            int(connection.execute("PRAGMA application_id").fetchone()[0]),
            int(connection.execute("PRAGMA user_version").fetchone()[0]),
        )
        if header != (APPLICATION_ID, EXTERNAL_RECONCILIATION_SCHEMA_VERSION):
            raise RuntimeError(f"Accepted Database v3 SQLite header mismatch: {header!r}")
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
            raise RuntimeError(f"Accepted Database v3 manifest count changed: {len(manifest)}")
        row = manifest[0]
        expected_tail = (
            EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_EXCLUDED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
            "release_accepted",
            None,
        )
        if tuple(row[3:]) != expected_tail:
            raise RuntimeError(f"Accepted Database v3 manifest mismatch: {row!r}")
        if int(row[1]) != EXPECTED_BASE_GOVERNANCE_RELEASE_ID:
            raise RuntimeError(f"Accepted Database v3 governance release changed: {row[1]!r}")
        if str(row[2]) != EXPECTED_BASE_DATABASE_RELEASE_CODE:
            raise RuntimeError(f"Accepted Database v3 release code changed: {row[2]!r}")
        validation_count = int(
            connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0]
        )
        if validation_count != EXPECTED_BASE_VALIDATION_RESULT_COUNT:
            raise RuntimeError(
                f"Accepted Database v3 validation count changed: {validation_count}"
            )
        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            WHERE source_version_id = ?
            ORDER BY governance_release_id
            """,
            (int(row[0]),),
        ).fetchall()
        if releases != [
            (1, "superseded", 2),
            (2, "superseded", 3),
            (3, "accepted", None),
        ]:
            raise RuntimeError(f"Accepted Database v3 governance lineage mismatch: {releases!r}")
        if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
            raise RuntimeError("Accepted Database v3 quick_check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Accepted Database v3 foreign_key_check failed")
        source_hash = connection.execute(
            "SELECT file_sha256 FROM source_version WHERE source_version_id = ?",
            (int(row[0]),),
        ).fetchone()
        if source_hash is None or not isinstance(source_hash[0], bytes):
            raise RuntimeError("Accepted Database v3 source SHA is unavailable")

    return V3BaseMetadata(
        source_version_id=int(row[0]),
        v3_governance_release_id=int(row[1]),
        source_file_sha256=bytes(source_hash[0]),
        prior_database_release_code=str(row[2]),
    )


def _insert_v4_governance_and_manifest(
    connection: sqlite3.Connection,
    *,
    base: V3BaseMetadata,
    repository_commit: str,
    reference_data_commit: str,
    manifest_code: str,
    database_release_code: str,
    build_command: str,
    created_at_utc: str,
) -> int:
    next_method_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_method_id),0)+1 FROM governance_method"
        ).fetchone()[0]
    )
    next_release_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_id),0)+1 FROM governance_release"
        ).fetchone()[0]
    )
    connection.execute(
        """
        INSERT INTO governance_method (
            governance_method_id, governance_method_code, method_name,
            method_version, repository_commit, method_description, created_at_utc
        ) VALUES (?, ?, 'Database v4 GB racecourse/course identity integration', ?, ?, ?, ?)
        """,
        (
            next_method_id,
            governance_method_code(V4_METHOD_SLUG, V4_METHOD_VERSION),
            V4_METHOD_VERSION,
            repository_commit,
            "Integrates completed Study 03 British racecourse identities, source-label "
            "mapping, stable course/track identities, inventory-state lineage and explicit "
            "unresolved residue without fabricating race-to-track assignments.",
            created_at_utc,
        ),
    )
    # Preserve the one-accepted-release invariant while creating the successor.
    # The temporary superseded backlink mirrors the proven v2 -> v3 handover:
    # create the successor without making it accepted, point the prior accepted
    # release forward to it, then atomically promote the successor.
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
            governance_release_code(
                base.source_file_sha256, V4_RELEASE_SLUG, V4_RELEASE_VERSION
            ),
            base.source_version_id,
            next_method_id,
            created_at_utc[:10],
            repository_commit,
            "Database v4 governed British racecourse/course identity reference release.",
            base.v3_governance_release_id,
            created_at_utc,
        ),
    )
    connection.execute(
        """
        UPDATE governance_release
        SET release_status='superseded', superseded_by_release_id=?
        WHERE governance_release_id=? AND release_status='accepted'
        """,
        (next_release_id, base.v3_governance_release_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to supersede Database v3 governance release in v4 copy")
    connection.execute(
        """
        UPDATE governance_release
        SET release_status='accepted', superseded_by_release_id=NULL
        WHERE governance_release_id=? AND release_status='superseded'
        """,
        (next_release_id,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to accept Database v4 governance release")

    next_evidence_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_evidence_id),0)+1 "
            "FROM governance_release_evidence"
        ).fetchone()[0]
    )
    for offset, (kind, reference, description) in enumerate(V4_EVIDENCE):
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
                kind,
                reference,
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
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 0,0,0,0, ?,1,'building',NULL)
        """,
        (
            manifest_code,
            database_release_code,
            base.source_version_id,
            next_release_id,
            RACECOURSE_IDENTITY_SCHEMA_VERSION,
            repository_commit,
            reference_data_commit,
            build_command.strip(),
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


def _finish_builder_stage(
    connection: sqlite3.Connection,
    *,
    completed_at_utc: str,
) -> tuple[str, int]:
    expected_counts = (60, 65, 60, 90, 86, 7)
    observed_counts = (
        int(connection.execute(
            "SELECT COUNT(*) FROM governance_study03_racecourse_notebook"
        ).fetchone()[0]),
        int(connection.execute(
            "SELECT COUNT(*) FROM reference_course_racecourse_map"
        ).fetchone()[0]),
        int(connection.execute(
            "SELECT COUNT(*) FROM reference_racecourse_identity"
        ).fetchone()[0]),
        int(connection.execute(
            "SELECT COUNT(*) FROM reference_racecourse_course_inventory"
        ).fetchone()[0]),
        int(connection.execute(
            "SELECT COUNT(*) FROM reference_racecourse_course_identity"
        ).fetchone()[0]),
        int(connection.execute(
            "SELECT COUNT(*) FROM governance_racecourse_unresolved_question"
        ).fetchone()[0]),
    )
    if observed_counts != expected_counts:
        raise RuntimeError(
            f"Database v4 Study 03 persisted counts changed: {observed_counts!r}"
        )
    if int(connection.execute(
        "SELECT COUNT(*) FROM view_gb_racecourse_identity_reference"
    ).fetchone()[0]) != 65:
        raise RuntimeError("Database v4 source-label identity view count changed")
    if int(connection.execute(
        "SELECT COUNT(*) FROM view_gb_course_track_identities"
    ).fetchone()[0]) != 86:
        raise RuntimeError("Database v4 stable course identity view count changed")

    quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
    if quick != "ok":
        raise RuntimeError(f"Database v4 quick_check failed: {quick!r}")
    fk_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if fk_rows:
        raise RuntimeError(f"Database v4 foreign_key_check returned rows: {fk_rows[:5]}")

    for validation_id, (stage, name, version, summary) in enumerate(
        BUILDER_VALIDATION_ROWS, start=1
    ):
        command = (
            "python scripts/build_inside_rails_v4.py"
            if stage in {"persisted_readback", "post_load_validation"}
            else f"PRAGMA {'quick_check' if stage == 'sqlite_integrity' else 'foreign_key_check'}"
        )
        connection.execute(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id, validation_stage,
                validator_name, validator_version, required_for_acceptance,
                outcome, executed_at_utc, command, result_summary,
                details_artifact_path
            ) VALUES (?,1,?,?,?,1,'passed',?,?,?,?)
            """,
            (
                validation_id,
                stage,
                name,
                version,
                completed_at_utc,
                command,
                summary,
                "docs/DATABASE_V4_GB_RACECOURSE_IDENTITY_INTEGRATION.md",
            ),
        )

    connection.execute(
        """
        UPDATE import_manifest
        SET build_completed_at_utc=?, persisted_readback_passed=1,
            sqlite_integrity_passed=1, foreign_key_check_passed=1,
            post_load_validation_passed=1, build_status='built'
        WHERE import_manifest_id=1 AND build_status='building'
        """,
        (completed_at_utc,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Database v4 builder could not advance manifest to built")
    connection.commit()
    status = str(
        connection.execute(
            "SELECT build_status FROM import_manifest WHERE import_manifest_id=1"
        ).fetchone()[0]
    )
    validation_count = int(
        connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0]
    )
    return status, validation_count


def build_racecourse_identity_candidate(
    project_root: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    base_release_path: str | Path | None = None,
    output_path: str | Path | None = None,
    build_command: str = "python scripts/build_inside_rails_v4.py",
    import_suffix: str | None = None,
    database_suffix: str | None = None,
) -> RacecourseIdentityBuildSummary:
    """Copy accepted v3, add Study 03 governed identities, and stop at built candidate."""

    started = perf_counter()
    root = Path(project_root).expanduser().resolve()
    repository_commit = validate_repository_commit(
        repository_commit, name="repository_commit"
    )
    reference_commit = validate_repository_commit(
        reference_data_commit or repository_commit,
        name="reference_data_commit",
    )
    started_at, compact = timestamp(None)
    manifest_code = f"imp:{compact}:{suffix(import_suffix, name='import_suffix')}"
    database_release_code = f"db:{compact}:{suffix(database_suffix, name='database_suffix')}"

    base_path = (
        Path(base_release_path).expanduser().resolve()
        if base_release_path
        else default_base_release_path(root).resolve()
    )
    output = (
        Path(output_path).expanduser().resolve()
        if output_path
        else default_v4_candidate_path(root).resolve()
    )
    if base_path == output:
        raise ValueError("Database v4 candidate must differ from accepted Database v3")
    existing = [item for item in artifact_paths(output) if item.exists()]
    if existing:
        raise FileExistsError(
            "Database v4 candidate artifact already exists: "
            + ", ".join(map(str, existing))
        )

    base = _validate_base_release(base_path)
    base_hash_before = validate_file_hash(
        base_path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v3 release"
    )
    try:
        copied_bytes, _ = copy_candidate(base_path, output)
        if copied_bytes != EXPECTED_BASE_RELEASE_SIZE_BYTES:
            raise RuntimeError(
                f"Database v4 base copy size changed: {copied_bytes}"
            )
        if sha256_file(output) != base_hash_before:
            raise RuntimeError("Database v4 base copy does not match accepted Database v3")

        connection = sqlite3.connect(output)
        try:
            configure_governed_connection(connection, durable_candidate=True)
            upgrade_external_reconciliation_to_racecourse_identity_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            release_id = _insert_v4_governance_and_manifest(
                connection,
                base=base,
                repository_commit=repository_commit,
                reference_data_commit=reference_commit,
                manifest_code=manifest_code,
                database_release_code=database_release_code,
                build_command=build_command,
                created_at_utc=started_at,
            )
            reference_summary: Study03ReferenceSummary = load_study03_racecourse_identity(
                connection,
                root,
                governance_release_id=release_id,
            )
            connection.commit()
            completed_at, _ = timestamp(None)
            final_status, validation_count = _finish_builder_stage(
                connection, completed_at_utc=completed_at
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        require_no_sidecars(output, label="Built Database v4 candidate")
        validate_file_hash(
            base_path,
            EXPECTED_BASE_RELEASE_SHA256,
            label="Accepted Database v3 release after v4 build",
        )
        with connect_read_only(output) as connection:
            configure_governed_connection(connection, query_only=True)
            if int(connection.execute("PRAGMA user_version").fetchone()[0]) != RACECOURSE_IDENTITY_SCHEMA_VERSION:
                raise RuntimeError("Database v4 candidate user_version changed after build")
            if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
                raise RuntimeError("Database v4 candidate failed final read-only quick_check")
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Database v4 candidate failed final read-only foreign_key_check")
    except Exception:
        remove_output(output)
        raise

    return RacecourseIdentityBuildSummary(
        output_path=str(output),
        base_release_path=str(base_path),
        repository_commit=repository_commit,
        reference_data_commit=reference_commit,
        racecourse_identity_release_id=release_id,
        manifest_code=manifest_code,
        database_release_code=database_release_code,
        reference=asdict(reference_summary),
        final_candidate_sha256_hex=sha256_file(output).hex(),
        final_manifest_status=final_status,
        validation_result_count=validation_count,
        build_elapsed_seconds=perf_counter() - started,
        independent_source_wide_validation_required=True,
        release_accepted=False,
    )


__all__ = [
    "RacecourseIdentityBuildSummary",
    "build_racecourse_identity_candidate",
    "default_base_release_path",
    "default_v4_candidate_path",
]
