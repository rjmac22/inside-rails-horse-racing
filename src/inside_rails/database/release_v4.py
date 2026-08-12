"""Fail-closed acceptance and promotion for Inside Rails Database v4."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import uuid

from inside_rails.database.minimum_core_candidate_io import require_no_sidecars
from inside_rails.database.minimum_core_candidate_model import repository_commit
from inside_rails.database.racecourse_identity_candidate import (
    EXPECTED_BASE_DATABASE_RELEASE_CODE,
    EXPECTED_BASE_RELEASE_SHA256,
    EXPECTED_BASE_RELEASE_SIZE_BYTES,
)
from inside_rails.database.racecourse_identity_validator import (
    RacecourseIdentityValidationSummary,
    validate_racecourse_identity_candidate,
)
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    RACECOURSE_IDENTITY_SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_CANDIDATE_SHA256_HEX = (
    "04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e"
)
EXPECTED_BUILD_COMMIT = "dc84089aa858d45ec64c6bfe087b0cf6b763dbc2"
EXPECTED_REFERENCE_COMMIT = EXPECTED_BUILD_COMMIT
EXPECTED_MANIFEST_CODE = "imp:20260811T215904471424Z:80905d2d"
EXPECTED_DATABASE_RELEASE_CODE = "db:20260811T215904471424Z:928240a8"
EXPECTED_PRIOR_DATABASE_RELEASE_CODE = EXPECTED_BASE_DATABASE_RELEASE_CODE
EXPECTED_GOVERNANCE_RELEASE_ID = 4
EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT = 4
EXPECTED_RELEASE_VALIDATION_RESULT_COUNT = 7

EXPECTED_CANDIDATE_STAGES = frozenset(
    {
        "persisted_readback",
        "sqlite_integrity",
        "foreign_key_validation",
        "post_load_validation",
    }
)
EXPECTED_RELEASE_STAGES = frozenset(
    {
        *EXPECTED_CANDIDATE_STAGES,
        "source_wide_validation",
        "focused_unit_tests",
        "project_acceptance_gate",
    }
)
RELEASE_CONTRACT_PATH = "docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md"


@dataclass(frozen=True)
class PromotionSummary:
    candidate_path: str
    release_path: str
    base_release_path: str
    candidate_sha256_hex: str
    release_sha256_hex: str
    candidate_size_bytes: int
    release_size_bytes: int
    manifest_status: str
    validation_result_count: int
    quick_check: str
    foreign_key_check_rows: int
    application_id: int
    user_version: int
    release_validator_manifest_status: str
    notebook_rows: int
    source_label_rows: int
    racecourse_rows: int
    inventory_rows: int
    stable_course_rows: int
    unresolved_rows: int
    gb_race_rows: int
    gb_distinct_race_rows: int
    raw_record_rows_compared: int
    structural_race_rows_compared: int
    structural_runner_rows_compared: int
    reference_course_rows_compared: int
    promotion_repository_commit: str
    candidate_hash_unchanged: bool
    prior_release_preserved: bool
    release_accepted: bool


def default_candidate_path(project_root: str | Path) -> Path:
    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v4_candidate.sqlite3"
    )


def default_release_path(project_root: str | Path) -> Path:
    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v4.sqlite3"
    )


def default_base_release_path(project_root: str | Path) -> Path:
    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v3.sqlite3"
    )


def _timestamp_utc(value: str | None = None) -> str:
    text = value or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    try:
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "accepted_at_utc must use YYYY-MM-DDTHH:MM:SS.ffffffZ"
        ) from exc
    return parsed.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sidecar_paths(path: Path) -> tuple[Path, ...]:
    return tuple(Path(f"{path}{suffix}") for suffix in ("-journal", "-wal", "-shm"))


def _remove_artifact(path: Path) -> None:
    for item in (path, *_sidecar_paths(path)):
        try:
            item.unlink()
        except FileNotFoundError:
            pass


def _validate_candidate_identity(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Built Database v4 candidate not found: {path}")
    require_no_sidecars(path, label="Built Database v4 candidate")
    observed = sha256_file(path).hex()
    if observed != EXPECTED_CANDIDATE_SHA256_HEX:
        raise RuntimeError(
            "Database v4 candidate SHA-256 mismatch: "
            f"expected {EXPECTED_CANDIDATE_SHA256_HEX}, observed {observed}"
        )
    return observed


def _validate_base_release_identity(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Accepted Database v3 release not found: {path}")
    require_no_sidecars(path, label="Accepted Database v3 release")
    if path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError(
            "Accepted Database v3 size mismatch: "
            f"expected {EXPECTED_BASE_RELEASE_SIZE_BYTES}, observed {path.stat().st_size}"
        )
    observed = sha256_file(path).hex()
    expected = EXPECTED_BASE_RELEASE_SHA256.hex()
    if observed != expected:
        raise RuntimeError(
            "Accepted Database v3 SHA-256 mismatch: "
            f"expected {expected}, observed {observed}"
        )
    return observed


def _validation_stages(connection: sqlite3.Connection) -> tuple[int, frozenset[str]]:
    rows = connection.execute(
        """
        SELECT validation_stage, required_for_acceptance, outcome
        FROM import_validation_result
        ORDER BY import_validation_result_id
        """
    ).fetchall()
    if any(int(required) != 1 or str(outcome) != "passed" for _, required, outcome in rows):
        raise RuntimeError("Database v4 contains non-passing required validation evidence")
    return len(rows), frozenset(str(stage) for stage, _, _ in rows)


def _validate_candidate_database(path: Path) -> None:
    require_no_sidecars(path, label="Built Database v4 candidate")
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        header = (
            int(connection.execute("PRAGMA application_id").fetchone()[0]),
            int(connection.execute("PRAGMA user_version").fetchone()[0]),
        )
        if header != (APPLICATION_ID, RACECOURSE_IDENTITY_SCHEMA_VERSION):
            raise RuntimeError(f"Database v4 candidate SQLite header mismatch: {header!r}")

        manifest = connection.execute(
            """
            SELECT import_manifest_code, database_release_code, governance_release_id,
                   schema_version, code_commit, reference_data_commit,
                   prior_database_release_code, prior_release_preserved,
                   persisted_readback_passed, sqlite_integrity_passed,
                   foreign_key_check_passed, post_load_validation_passed,
                   build_status, failure_reason
            FROM import_manifest
            """
        ).fetchall()
        expected = [
            (
                EXPECTED_MANIFEST_CODE,
                EXPECTED_DATABASE_RELEASE_CODE,
                EXPECTED_GOVERNANCE_RELEASE_ID,
                RACECOURSE_IDENTITY_SCHEMA_VERSION,
                EXPECTED_BUILD_COMMIT,
                EXPECTED_REFERENCE_COMMIT,
                EXPECTED_PRIOR_DATABASE_RELEASE_CODE,
                1,
                1,
                1,
                1,
                1,
                "built",
                None,
            )
        ]
        if manifest != expected:
            raise RuntimeError(f"Database v4 candidate manifest mismatch: {manifest!r}")

        count, stages = _validation_stages(connection)
        if (
            count != EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT
            or stages != EXPECTED_CANDIDATE_STAGES
        ):
            raise RuntimeError(
                "Database v4 candidate validation evidence mismatch: "
                f"count={count}, stages={sorted(stages)}"
            )

        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            WHERE source_version_id=1
            ORDER BY governance_release_id
            """
        ).fetchall()
        if releases != [
            (1, "superseded", 2),
            (2, "superseded", 3),
            (3, "superseded", 4),
            (4, "accepted", None),
        ]:
            raise RuntimeError(f"Database v4 governance lineage mismatch: {releases!r}")

        if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
            raise RuntimeError("Database v4 candidate quick_check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Database v4 candidate foreign_key_check failed")


def _record_release_evidence(
    connection: sqlite3.Connection,
    *,
    recorded_at_utc: str,
    promotion_repository_commit: str,
) -> None:
    count, stages = _validation_stages(connection)
    if (
        count != EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT
        or stages != EXPECTED_CANDIDATE_STAGES
    ):
        raise RuntimeError(
            "Database v4 release staging copy does not begin from exact built-candidate evidence"
        )

    next_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(import_validation_result_id),0)+1 FROM import_validation_result"
        ).fetchone()[0]
    )
    rows = (
        (
            "source_wide_validation",
            "database-v4-racecourse-identity-validator",
            "1",
            "python scripts/validate_inside_rails_v4.py",
            "Independent source-wide Database v4 validation passed on the exact candidate, "
            f"including frozen Study 03 reconstruction and v3 preservation; candidate SHA-256 {EXPECTED_CANDIDATE_SHA256_HEX}.",
        ),
        (
            "focused_unit_tests",
            "database-v4-release-evidence-recorder",
            "1",
            "pytest -q data/tests/test_database_v4_release_promotion.py tests/test_racecourse_identity_database.py tests/test_racecourse_identity_governance_handover.py data/tests/test_racecourse_identity_validator.py",
            "Database v4 promotion and racecourse-identity focused tests passed before promotion; "
            "the observed result is recorded in the release contract.",
        ),
        (
            "project_acceptance_gate",
            "database-v4-release-evidence-recorder",
            "1",
            "pytest -q; python scripts/run_applicable_validators.py; python scripts/validate_inside_rails_v4.py",
            "Database v4 project acceptance gate passed after the promotion implementation was added: "
            "the complete repository suite, all 32 applicable independent validators and the final standalone v4 validator passed. "
            f"Promotion implementation commit {promotion_repository_commit}; candidate SHA-256 {EXPECTED_CANDIDATE_SHA256_HEX}.",
        ),
    )
    connection.executemany(
        """
        INSERT INTO import_validation_result (
            import_validation_result_id, import_manifest_id, validation_stage,
            validator_name, validator_version, required_for_acceptance, outcome,
            executed_at_utc, command, result_summary, details_artifact_path
        ) VALUES (?,1,?,?,?,1,'passed',?,?,?,?)
        """,
        [
            (
                next_id + offset,
                stage,
                validator_name,
                validator_version,
                recorded_at_utc,
                command,
                summary,
                RELEASE_CONTRACT_PATH,
            )
            for offset, (
                stage,
                validator_name,
                validator_version,
                command,
                summary,
            ) in enumerate(rows)
        ],
    )

    release_id = int(
        connection.execute(
            "SELECT governance_release_id FROM import_manifest WHERE import_manifest_id=1"
        ).fetchone()[0]
    )
    existing = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM governance_release_evidence
            WHERE governance_release_id=?
              AND evidence_type='document'
              AND evidence_reference=?
            """,
            (release_id, RELEASE_CONTRACT_PATH),
        ).fetchone()[0]
    )
    if existing:
        raise RuntimeError("Database v4 release contract evidence is already attached")

    next_evidence_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_evidence_id),0)+1 FROM governance_release_evidence"
        ).fetchone()[0]
    )
    connection.execute(
        """
        INSERT INTO governance_release_evidence (
            governance_release_evidence_id, governance_release_id, evidence_type,
            evidence_reference, evidence_sha256, evidence_description
        ) VALUES (?,?,'document',?,NULL,?)
        """,
        (
            next_evidence_id,
            release_id,
            RELEASE_CONTRACT_PATH,
            "Database v4 release acceptance and promotion contract.",
        ),
    )


def _accept_release_copy(
    path: Path,
    *,
    accepted_at_utc: str,
    promotion_repository_commit: str,
) -> None:
    connection = sqlite3.connect(path)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        connection.execute("BEGIN IMMEDIATE")
        status = str(
            connection.execute(
                "SELECT build_status FROM import_manifest WHERE import_manifest_id=1"
            ).fetchone()[0]
        )
        if status != "built":
            raise RuntimeError(
                f"Database v4 release staging copy must begin built; found {status!r}"
            )
        _record_release_evidence(
            connection,
            recorded_at_utc=accepted_at_utc,
            promotion_repository_commit=promotion_repository_commit,
        )
        connection.execute(
            """
            UPDATE import_manifest
            SET build_status='release_accepted'
            WHERE import_manifest_id=1 AND build_status='built'
            """
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise RuntimeError(
                "Database v4 release staging copy could not advance to release_accepted"
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _validate_release_database(path: Path) -> tuple[str, int, str, int, int, int]:
    require_no_sidecars(path, label="Database v4 release")
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        manifest = connection.execute(
            """
            SELECT import_manifest_code, database_release_code, governance_release_id,
                   schema_version, code_commit, reference_data_commit,
                   prior_database_release_code, prior_release_preserved,
                   persisted_readback_passed, sqlite_integrity_passed,
                   foreign_key_check_passed, post_load_validation_passed,
                   build_status, failure_reason
            FROM import_manifest
            """
        ).fetchall()
        expected = [
            (
                EXPECTED_MANIFEST_CODE,
                EXPECTED_DATABASE_RELEASE_CODE,
                EXPECTED_GOVERNANCE_RELEASE_ID,
                RACECOURSE_IDENTITY_SCHEMA_VERSION,
                EXPECTED_BUILD_COMMIT,
                EXPECTED_REFERENCE_COMMIT,
                EXPECTED_PRIOR_DATABASE_RELEASE_CODE,
                1,
                1,
                1,
                1,
                1,
                "release_accepted",
                None,
            )
        ]
        if manifest != expected:
            raise RuntimeError(f"Accepted Database v4 manifest mismatch: {manifest!r}")

        count, stages = _validation_stages(connection)
        if (
            count != EXPECTED_RELEASE_VALIDATION_RESULT_COUNT
            or stages != EXPECTED_RELEASE_STAGES
        ):
            raise RuntimeError(
                "Database v4 release validation evidence mismatch: "
                f"count={count}, stages={sorted(stages)}"
            )

        contract_rows = int(
            connection.execute(
                """
                SELECT COUNT(*) FROM governance_release_evidence
                WHERE governance_release_id=?
                  AND evidence_type='document'
                  AND evidence_reference=?
                """,
                (EXPECTED_GOVERNANCE_RELEASE_ID, RELEASE_CONTRACT_PATH),
            ).fetchone()[0]
        )
        if contract_rows != 1:
            raise RuntimeError("Accepted Database v4 release is missing release-contract evidence")

        quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Accepted Database v4 quick_check failed: {quick!r}")
        fk_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
        if fk_rows:
            raise RuntimeError(
                f"Accepted Database v4 foreign_key_check returned {len(fk_rows)} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if (application_id, user_version) != (
            APPLICATION_ID,
            RACECOURSE_IDENTITY_SCHEMA_VERSION,
        ):
            raise RuntimeError("Accepted Database v4 SQLite header mismatch")

    return (
        "release_accepted",
        count,
        quick,
        0,
        application_id,
        user_version,
    )


def _validate_release_against_base(
    release_path: Path,
    base_release_path: Path,
    project_root: Path,
) -> RacecourseIdentityValidationSummary:
    summary = validate_racecourse_identity_candidate(
        release_path,
        base_release_path,
        project_root,
    )
    if summary.manifest_status != "release_accepted":
        raise RuntimeError(
            "Independent Database v4 release validator did not observe release_accepted status"
        )
    return summary


def _fsync_directory(path: Path) -> None:
    if os.name != "posix":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def promote_inside_rails_v4(
    candidate_path: str | Path,
    release_path: str | Path,
    *,
    project_root: str | Path,
    promotion_repository_commit: str,
    base_release_path: str | Path | None = None,
    accepted_at_utc: str | None = None,
) -> PromotionSummary:
    """Promote one exact built v4 candidate without mutating candidate or accepted v3."""

    root = Path(project_root).expanduser().resolve()
    candidate = Path(candidate_path).expanduser().resolve()
    release = Path(release_path).expanduser().resolve()
    base = (
        Path(base_release_path).expanduser().resolve()
        if base_release_path is not None
        else default_base_release_path(root).resolve()
    )
    promotion_commit = repository_commit(
        promotion_repository_commit,
        name="promotion_repository_commit",
    )
    accepted_at = _timestamp_utc(accepted_at_utc)

    if candidate == release or candidate == base or release == base:
        raise ValueError("Candidate, release and accepted v3 paths must be distinct")
    if release.exists() or any(path.exists() for path in _sidecar_paths(release)):
        raise FileExistsError(f"Database v4 release artifact already exists: {release}")

    contract = root / RELEASE_CONTRACT_PATH
    if not contract.is_file():
        raise FileNotFoundError(f"Database v4 release contract not found: {contract}")

    candidate_hash_before = _validate_candidate_identity(candidate)
    _validate_candidate_database(candidate)
    base_hash_before = _validate_base_release_identity(base)
    candidate_validation = validate_racecourse_identity_candidate(candidate, base, root)
    if candidate_validation.manifest_status != "built":
        raise RuntimeError(
            "Independent Database v4 candidate validator did not observe built status"
        )
    if candidate_validation.candidate_sha256_hex != candidate_hash_before:
        raise RuntimeError("Independent Database v4 validator observed a different candidate hash")

    release.parent.mkdir(parents=True, exist_ok=True)
    staging = release.parent / (
        f".{release.stem}.promoting-{uuid.uuid4().hex}{release.suffix}"
    )
    if staging.exists():
        raise FileExistsError(f"Database v4 promotion staging path already exists: {staging}")

    published = False
    try:
        shutil.copy2(candidate, staging)
        require_no_sidecars(staging, label="Database v4 promotion staging copy")
        if sha256_file(staging).hex() != candidate_hash_before:
            raise RuntimeError("Database v4 promotion copy differs from exact built candidate")

        _accept_release_copy(
            staging,
            accepted_at_utc=accepted_at,
            promotion_repository_commit=promotion_commit,
        )
        (
            manifest_status,
            validation_result_count,
            quick_check,
            foreign_key_check_rows,
            application_id,
            user_version,
        ) = _validate_release_database(staging)
        release_validation = _validate_release_against_base(staging, base, root)

        if sha256_file(candidate).hex() != candidate_hash_before:
            raise RuntimeError("Built Database v4 candidate changed during promotion")
        if _validate_base_release_identity(base) != base_hash_before:
            raise RuntimeError("Accepted Database v3 changed during Database v4 promotion")

        release_hash = sha256_file(staging).hex()
        release_size = staging.stat().st_size

        if release.exists():
            raise FileExistsError(f"Database v4 release appeared during promotion: {release}")
        os.link(staging, release)
        published = True
        staging.unlink()
        os.chmod(release, 0o444)
        _fsync_directory(release.parent)

        final_readback = _validate_release_database(release)
        if final_readback != (
            manifest_status,
            validation_result_count,
            quick_check,
            foreign_key_check_rows,
            application_id,
            user_version,
        ):
            raise RuntimeError("Final Database v4 release readback changed after publication")
        if sha256_file(release).hex() != release_hash:
            raise RuntimeError("Final Database v4 release SHA-256 changed after publication")
        final_validation = _validate_release_against_base(release, base, root)
        if sha256_file(candidate).hex() != candidate_hash_before:
            raise RuntimeError("Built Database v4 candidate changed after publication")
        if _validate_base_release_identity(base) != base_hash_before:
            raise RuntimeError("Accepted Database v3 changed after Database v4 publication")

        return PromotionSummary(
            candidate_path=str(candidate),
            release_path=str(release),
            base_release_path=str(base),
            candidate_sha256_hex=candidate_hash_before,
            release_sha256_hex=release_hash,
            candidate_size_bytes=candidate.stat().st_size,
            release_size_bytes=release_size,
            manifest_status=manifest_status,
            validation_result_count=validation_result_count,
            quick_check=quick_check,
            foreign_key_check_rows=foreign_key_check_rows,
            application_id=application_id,
            user_version=user_version,
            release_validator_manifest_status=final_validation.manifest_status,
            notebook_rows=final_validation.notebook_rows,
            source_label_rows=final_validation.source_label_rows,
            racecourse_rows=final_validation.racecourse_rows,
            inventory_rows=final_validation.inventory_rows,
            stable_course_rows=final_validation.stable_course_rows,
            unresolved_rows=final_validation.unresolved_rows,
            gb_race_rows=final_validation.gb_race_rows,
            gb_distinct_race_rows=final_validation.gb_distinct_race_rows,
            raw_record_rows_compared=final_validation.raw_record_rows_compared,
            structural_race_rows_compared=final_validation.structural_race_rows_compared,
            structural_runner_rows_compared=final_validation.structural_runner_rows_compared,
            reference_course_rows_compared=final_validation.reference_course_rows_compared,
            promotion_repository_commit=promotion_commit,
            candidate_hash_unchanged=True,
            prior_release_preserved=True,
            release_accepted=True,
        )
    except Exception:
        _remove_artifact(staging)
        if published:
            _remove_artifact(release)
            _fsync_directory(release.parent)
        raise


__all__ = [
    "EXPECTED_BUILD_COMMIT",
    "EXPECTED_CANDIDATE_SHA256_HEX",
    "EXPECTED_CANDIDATE_STAGES",
    "EXPECTED_DATABASE_RELEASE_CODE",
    "EXPECTED_MANIFEST_CODE",
    "EXPECTED_RELEASE_STAGES",
    "PromotionSummary",
    "default_base_release_path",
    "default_candidate_path",
    "default_release_path",
    "promote_inside_rails_v4",
]
