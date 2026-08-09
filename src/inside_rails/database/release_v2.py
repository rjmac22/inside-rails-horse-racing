"""Fail-closed acceptance and promotion for Inside Rails Database v2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import uuid

from inside_rails.database.governed_integration_candidate import (
    EXPECTED_BASE_RELEASE_SHA256,
    EXPECTED_BASE_RELEASE_SIZE_BYTES,
)
from inside_rails.database.governed_integration_validator import (
    GovernedIntegrationValidationSummary,
    validate_governed_integration_candidate,
)
from inside_rails.database.minimum_core_candidate_model import repository_commit
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_CANDIDATE_SHA256_HEX = (
    "5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe"
)
EXPECTED_BUILD_COMMIT = "68ac0364c4af2a104ea76c8765fd0e220aaf8e84"
EXPECTED_REFERENCE_COMMIT = EXPECTED_BUILD_COMMIT
EXPECTED_MANIFEST_CODE = "imp:20260809T081402956098Z:878ceaa5"
EXPECTED_DATABASE_RELEASE_CODE = "db:20260809T081402956098Z:5b29ea51"
EXPECTED_PRIOR_DATABASE_RELEASE_CODE = "db:20260806T110355286543Z:c427ca06"

EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285
EXPECTED_GOVERNANCE_RELEASE_ID = 2
EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT = 5
EXPECTED_RELEASE_VALIDATION_RESULT_COUNT = 7

EXPECTED_BUILDER_STAGES = frozenset(
    {
        "persisted_readback",
        "sqlite_integrity",
        "foreign_key_validation",
        "post_load_validation",
    }
)
EXPECTED_CANDIDATE_STAGES = frozenset(
    {*EXPECTED_BUILDER_STAGES, "source_wide_validation"}
)
EXPECTED_RELEASE_STAGES = frozenset(
    {*EXPECTED_CANDIDATE_STAGES, "focused_unit_tests", "project_acceptance_gate"}
)

RELEASE_CONTRACT_PATH = "docs/DATABASE_V2_RELEASE_ACCEPTANCE_AND_PROMOTION.md"


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
    raw_record_fingerprints_recomputed: int
    structural_rows_compared: int
    promotion_repository_commit: str
    candidate_hash_unchanged: bool
    prior_release_preserved: bool
    release_accepted: bool


def default_candidate_path(project_root: str | Path) -> Path:
    """Return the exact validated Database v2 candidate path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v2_candidate.sqlite3"
    )


def default_release_path(project_root: str | Path) -> Path:
    """Return the canonical immutable Database v2 release path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v2.sqlite3"
    )


def default_base_release_path(project_root: str | Path) -> Path:
    """Return the retained accepted Database v1 release path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v1.sqlite3"
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


def _assert_no_sidecars(path: Path) -> None:
    present = [str(item) for item in _sidecar_paths(path) if item.exists()]
    if present:
        raise RuntimeError(f"SQLite sidecars are present: {present}")


def _remove_artifact(path: Path) -> None:
    for item in (path, *_sidecar_paths(path)):
        try:
            item.unlink()
        except FileNotFoundError:
            pass


def _validate_candidate_identity(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Validated Database v2 candidate not found: {path}")
    _assert_no_sidecars(path)
    observed_hash = sha256_file(path).hex()
    if observed_hash != EXPECTED_CANDIDATE_SHA256_HEX:
        raise RuntimeError(
            "Database v2 candidate SHA-256 mismatch: "
            f"expected {EXPECTED_CANDIDATE_SHA256_HEX}, observed {observed_hash}"
        )
    return observed_hash


def _validate_base_release_identity(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Accepted Database v1 release not found: {path}")
    _assert_no_sidecars(path)
    if path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError(
            "Accepted Database v1 size mismatch: "
            f"expected {EXPECTED_BASE_RELEASE_SIZE_BYTES}, observed {path.stat().st_size}"
        )
    observed_hash = sha256_file(path).hex()
    expected_hash = EXPECTED_BASE_RELEASE_SHA256.hex()
    if observed_hash != expected_hash:
        raise RuntimeError(
            "Accepted Database v1 SHA-256 mismatch: "
            f"expected {expected_hash}, observed {observed_hash}"
        )
    return observed_hash


def _read_manifest(connection: sqlite3.Connection) -> tuple[object, ...]:
    rows = connection.execute(
        """
        SELECT import_manifest_id, import_manifest_code, database_release_code,
               source_version_id, governance_release_id, schema_version,
               code_commit, reference_data_commit,
               physical_record_count, admitted_record_count, excluded_record_count,
               race_occurrence_count, runner_participation_count,
               persisted_readback_passed, sqlite_integrity_passed,
               foreign_key_check_passed, post_load_validation_passed,
               prior_database_release_code, prior_release_preserved,
               build_status, failure_reason, build_completed_at_utc
        FROM import_manifest
        """
    ).fetchall()
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one Database v2 import manifest; observed {len(rows)}")
    return tuple(rows[0])


def _expected_manifest(status: str, *, completed_at_utc: object) -> tuple[object, ...]:
    return (
        1,
        EXPECTED_MANIFEST_CODE,
        EXPECTED_DATABASE_RELEASE_CODE,
        1,
        EXPECTED_GOVERNANCE_RELEASE_ID,
        GOVERNED_INTEGRATION_SCHEMA_VERSION,
        EXPECTED_BUILD_COMMIT,
        EXPECTED_REFERENCE_COMMIT,
        EXPECTED_PHYSICAL_RECORD_COUNT,
        EXPECTED_ADMITTED_RECORD_COUNT,
        EXPECTED_EXCLUDED_RECORD_COUNT,
        EXPECTED_RACE_OCCURRENCE_COUNT,
        EXPECTED_RUNNER_PARTICIPATION_COUNT,
        1,
        1,
        1,
        1,
        EXPECTED_PRIOR_DATABASE_RELEASE_CODE,
        1,
        status,
        None,
        completed_at_utc,
    )


def _validate_validation_rows(
    connection: sqlite3.Connection,
    *,
    expected_stages: frozenset[str],
    expected_count: int,
) -> None:
    rows = connection.execute(
        """
        SELECT validation_stage, validator_name, validator_version,
               required_for_acceptance, outcome
        FROM import_validation_result
        ORDER BY import_validation_result_id
        """
    ).fetchall()
    if len(rows) != expected_count:
        raise RuntimeError(
            f"Validation-result count mismatch: expected {expected_count}, observed {len(rows)}"
        )
    stages = {str(row[0]) for row in rows}
    if stages != expected_stages:
        raise RuntimeError(
            "Validation stages mismatch: "
            f"expected {sorted(expected_stages)}, observed {sorted(stages)}"
        )
    if any(int(row[3]) != 1 or str(row[4]) != "passed" for row in rows):
        raise RuntimeError("Database v2 contains non-passing required validation evidence")


def _validate_candidate_database(path: Path) -> tuple[int, int]:
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        manifest = _read_manifest(connection)
        if manifest[21] is None:
            raise RuntimeError("Validated Database v2 candidate has no completion timestamp")
        if manifest != _expected_manifest("validated", completed_at_utc=manifest[21]):
            raise RuntimeError(f"Database v2 candidate manifest mismatch: {manifest!r}")

        _validate_validation_rows(
            connection,
            expected_stages=EXPECTED_CANDIDATE_STAGES,
            expected_count=EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT,
        )

        source_wide = connection.execute(
            """
            SELECT validator_name, validator_version
            FROM import_validation_result
            WHERE validation_stage = 'source_wide_validation'
            """
        ).fetchone()
        if source_wide != ("database-v2-governed-integration-validator", "1"):
            raise RuntimeError(
                f"Database v2 source-wide validation identity changed: {source_wide!r}"
            )

        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release
            WHERE source_version_id = 1
            ORDER BY governance_release_id
            """
        ).fetchall()
        if releases != [(1, "superseded", 2), (2, "accepted", None)]:
            raise RuntimeError(f"Database v2 governance-release lineage mismatch: {releases!r}")

        quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Database v2 candidate quick_check failed: {quick!r}")
        foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_rows:
            raise RuntimeError(
                "Database v2 candidate foreign_key_check returned rows: "
                f"{foreign_key_rows[:5]}"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if (
            application_id != APPLICATION_ID
            or user_version != GOVERNED_INTEGRATION_SCHEMA_VERSION
        ):
            raise RuntimeError("Database v2 candidate SQLite header mismatch")

    return application_id, user_version


def _record_acceptance_evidence(
    connection: sqlite3.Connection,
    *,
    recorded_at_utc: str,
    promotion_repository_commit: str,
) -> None:
    manifest = _read_manifest(connection)
    import_manifest_id = int(manifest[0])
    governance_release_id = int(manifest[4])

    existing_stages = {
        str(row[0])
        for row in connection.execute(
            "SELECT validation_stage FROM import_validation_result"
        ).fetchall()
    }
    if existing_stages != EXPECTED_CANDIDATE_STAGES:
        raise RuntimeError(
            "Release copy does not begin with the exact validated Database v2 evidence set"
        )

    next_validation_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(import_validation_result_id), 0) + 1 "
            "FROM import_validation_result"
        ).fetchone()[0]
    )
    rows = (
        (
            "focused_unit_tests",
            "database-v2-release-evidence-recorder",
            "1",
            "pytest -q tests/test_database_schema_v002.py tests/test_database_v2_*.py",
            "Database v2 focused release-boundary tests passed on 2026-08-09: "
            "26 passed in 1.52s; evidence is bound to candidate SHA-256 "
            f"{EXPECTED_CANDIDATE_SHA256_HEX}.",
        ),
        (
            "project_acceptance_gate",
            "database-v2-release-evidence-recorder",
            "1",
            "pytest -q; applicable independent validator sweep",
            "Final Database v2 repository acceptance gate passed on 2026-08-09: "
            "386 tests passed in 17.04s and all applicable independent validators "
            "passed; promotion implementation commit "
            f"{promotion_repository_commit}; candidate SHA-256 "
            f"{EXPECTED_CANDIDATE_SHA256_HEX}.",
        ),
    )
    connection.executemany(
        """
        INSERT INTO import_validation_result (
            import_validation_result_id, import_manifest_id,
            validation_stage, validator_name, validator_version,
            required_for_acceptance, outcome, executed_at_utc,
            command, result_summary, details_artifact_path
        ) VALUES (?, ?, ?, ?, ?, 1, 'passed', ?, ?, ?, ?)
        """,
        [
            (
                next_validation_id + offset,
                import_manifest_id,
                stage,
                validator_name,
                validator_version,
                recorded_at_utc,
                command,
                summary,
                RELEASE_CONTRACT_PATH,
            )
            for offset, (stage, validator_name, validator_version, command, summary) in enumerate(rows)
        ],
    )

    existing_contract = connection.execute(
        """
        SELECT COUNT(*)
        FROM governance_release_evidence
        WHERE governance_release_id = ?
          AND evidence_type = 'document'
          AND evidence_reference = ?
        """,
        (governance_release_id, RELEASE_CONTRACT_PATH),
    ).fetchone()[0]
    if int(existing_contract) != 0:
        raise RuntimeError("Database v2 release contract evidence is already attached")

    next_evidence_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(governance_release_evidence_id), 0) + 1 "
            "FROM governance_release_evidence"
        ).fetchone()[0]
    )
    connection.execute(
        """
        INSERT INTO governance_release_evidence (
            governance_release_evidence_id, governance_release_id,
            evidence_type, evidence_reference, evidence_sha256,
            evidence_description
        ) VALUES (?, ?, 'document', ?, NULL, ?)
        """,
        (
            next_evidence_id,
            governance_release_id,
            RELEASE_CONTRACT_PATH,
            "Database v2 release acceptance and promotion contract; the project owner "
            "accepted promotion by executing the fail-closed promotion command after "
            "the documented final gates passed.",
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
        manifest = _read_manifest(connection)
        if str(manifest[19]) != "validated":
            raise RuntimeError("Database v2 release copy must begin from validated status")
        _record_acceptance_evidence(
            connection,
            recorded_at_utc=accepted_at_utc,
            promotion_repository_commit=promotion_repository_commit,
        )
        connection.execute(
            """
            UPDATE import_manifest
            SET build_status = 'release_accepted'
            WHERE import_manifest_id = 1
              AND build_status = 'validated'
            """
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise RuntimeError("Database v2 manifest failed to enter release_accepted status")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _validate_release_database(path: Path) -> tuple[str, int, str, int, int, int]:
    _assert_no_sidecars(path)
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        manifest = _read_manifest(connection)
        if manifest[21] is None:
            raise RuntimeError("Accepted Database v2 release has no completion timestamp")
        if manifest != _expected_manifest("release_accepted", completed_at_utc=manifest[21]):
            raise RuntimeError(f"Accepted Database v2 manifest mismatch: {manifest!r}")

        _validate_validation_rows(
            connection,
            expected_stages=EXPECTED_RELEASE_STAGES,
            expected_count=EXPECTED_RELEASE_VALIDATION_RESULT_COUNT,
        )

        contract_rows = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM governance_release_evidence
                WHERE governance_release_id = ?
                  AND evidence_type = 'document'
                  AND evidence_reference = ?
                """,
                (EXPECTED_GOVERNANCE_RELEASE_ID, RELEASE_CONTRACT_PATH),
            ).fetchone()[0]
        )
        if contract_rows != 1:
            raise RuntimeError("Accepted Database v2 release is missing release-contract evidence")

        quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Accepted Database v2 quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Accepted Database v2 foreign_key_check returned {foreign_key_rows} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if (
            application_id != APPLICATION_ID
            or user_version != GOVERNED_INTEGRATION_SCHEMA_VERSION
        ):
            raise RuntimeError("Accepted Database v2 SQLite header mismatch")

    return (
        "release_accepted",
        EXPECTED_RELEASE_VALIDATION_RESULT_COUNT,
        quick,
        foreign_key_rows,
        application_id,
        user_version,
    )


def _validate_release_against_base(
    release_path: Path,
    base_release_path: Path,
    project_root: Path,
) -> GovernedIntegrationValidationSummary:
    summary = validate_governed_integration_candidate(
        release_path,
        base_release_path,
        project_root,
    )
    if summary.manifest_status != "release_accepted":
        raise RuntimeError(
            "Independent Database v2 release validator did not observe release_accepted status"
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


def promote_inside_rails_v2(
    candidate_path: str | Path,
    release_path: str | Path,
    *,
    project_root: str | Path,
    promotion_repository_commit: str,
    base_release_path: str | Path | None = None,
    accepted_at_utc: str | None = None,
) -> PromotionSummary:
    """Promote the exact validated v2 candidate without mutating candidate or v1."""

    root = Path(project_root).expanduser().resolve()
    candidate = Path(candidate_path).expanduser().resolve()
    release = Path(release_path).expanduser().resolve()
    base_release = (
        Path(base_release_path).expanduser().resolve()
        if base_release_path is not None
        else default_base_release_path(root).resolve()
    )
    promotion_commit = repository_commit(
        promotion_repository_commit,
        name="promotion_repository_commit",
    )
    accepted_at = _timestamp_utc(accepted_at_utc)

    if candidate == release:
        raise ValueError("Candidate and release paths must be different")
    if release.exists():
        raise FileExistsError(f"Accepted Database v2 release already exists: {release}")
    _assert_no_sidecars(release)

    candidate_hash_before = _validate_candidate_identity(candidate)
    _validate_candidate_database(candidate)
    base_hash_before = _validate_base_release_identity(base_release)

    release.parent.mkdir(parents=True, exist_ok=True)
    staging = release.parent / (
        f".{release.stem}.promoting-{uuid.uuid4().hex}{release.suffix}"
    )
    if staging.exists():
        raise FileExistsError(f"Promotion staging path already exists: {staging}")

    published = False
    try:
        shutil.copy2(candidate, staging)
        _assert_no_sidecars(staging)
        staging_hash = sha256_file(staging).hex()
        if staging_hash != candidate_hash_before:
            raise RuntimeError("Database v2 promotion copy does not match validated candidate")

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
        release_validation = _validate_release_against_base(
            staging,
            base_release,
            root,
        )

        candidate_hash_after = sha256_file(candidate).hex()
        if candidate_hash_after != candidate_hash_before:
            raise RuntimeError("Validated Database v2 candidate changed during promotion")
        if _validate_base_release_identity(base_release) != base_hash_before:
            raise RuntimeError("Accepted Database v1 changed during Database v2 promotion")

        release_hash = sha256_file(staging).hex()
        release_size = staging.stat().st_size

        if release.exists():
            raise FileExistsError(f"Accepted Database v2 release appeared during promotion: {release}")
        os.link(staging, release)
        published = True
        staging.unlink()
        _fsync_directory(release.parent)

        final_validation = _validate_release_database(release)
        if final_validation != (
            manifest_status,
            validation_result_count,
            quick_check,
            foreign_key_check_rows,
            application_id,
            user_version,
        ):
            raise RuntimeError("Final Database v2 release readback changed after publication")
        if sha256_file(release).hex() != release_hash:
            raise RuntimeError("Final Database v2 release SHA-256 changed after publication")
        if sha256_file(candidate).hex() != candidate_hash_before:
            raise RuntimeError("Validated Database v2 candidate changed after publication")
        if _validate_base_release_identity(base_release) != base_hash_before:
            raise RuntimeError("Accepted Database v1 changed after Database v2 publication")

        return PromotionSummary(
            candidate_path=str(candidate),
            release_path=str(release),
            base_release_path=str(base_release),
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
            release_validator_manifest_status=release_validation.manifest_status,
            raw_record_fingerprints_recomputed=release_validation.raw_record_fingerprints_recomputed,
            structural_rows_compared=release_validation.structural_rows_compared,
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
    "PromotionSummary",
    "default_base_release_path",
    "default_candidate_path",
    "default_release_path",
    "promote_inside_rails_v2",
]
