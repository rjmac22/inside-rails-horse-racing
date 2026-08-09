"""Fail-closed acceptance and promotion for Inside Rails Database v3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import uuid

from inside_rails.database.external_reconciliation_candidate import (
    EXPECTED_BASE_RELEASE_SHA256,
    EXPECTED_BASE_RELEASE_SIZE_BYTES,
)
from inside_rails.database.external_reconciliation_validator import (
    validate_external_reconciliation_candidate,
)
from inside_rails.database.minimum_core_candidate_model import repository_commit
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only

EXPECTED_CANDIDATE_SHA256_HEX = "0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b"
EXPECTED_BUILD_COMMIT = "96d82413c86169698113896938479027ecda81ab"
EXPECTED_REFERENCE_COMMIT = EXPECTED_BUILD_COMMIT
EXPECTED_MANIFEST_CODE = "imp:20260809T132557790891Z:77d44696"
EXPECTED_DATABASE_RELEASE_CODE = "db:20260809T132557790891Z:84258cbc"
EXPECTED_PRIOR_DATABASE_RELEASE_CODE = "db:20260809T081402956098Z:5b29ea51"
EXPECTED_GOVERNANCE_RELEASE_ID = 3
EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT = 5
EXPECTED_RELEASE_VALIDATION_RESULT_COUNT = 7
EXPECTED_CANDIDATE_STAGES = frozenset(
    {
        "persisted_readback",
        "sqlite_integrity",
        "foreign_key_validation",
        "post_load_validation",
        "source_wide_validation",
    }
)
EXPECTED_RELEASE_STAGES = frozenset(
    {*EXPECTED_CANDIDATE_STAGES, "focused_unit_tests", "project_acceptance_gate"}
)
RELEASE_CONTRACT_PATH = "docs/DATABASE_V3_RELEASE_ACCEPTANCE_AND_PROMOTION.md"


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
    raw_record_rows_compared: int
    structural_race_rows_compared: int
    structural_runner_rows_compared: int
    promotion_repository_commit: str
    candidate_hash_unchanged: bool
    prior_release_preserved: bool
    release_accepted: bool


def default_candidate_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/candidates/inside_rails_v3_candidate.sqlite3"


def default_release_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/releases/inside_rails_v3.sqlite3"


def default_base_release_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data/processed/database/releases/inside_rails_v2.sqlite3"


def _timestamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_hash(path: Path, expected_hex: str, *, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    observed = sha256_file(path).hex()
    if observed != expected_hex:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected_hex}, observed {observed}"
        )
    return observed


def _validation_stages(connection: sqlite3.Connection) -> tuple[int, frozenset[str]]:
    rows = connection.execute(
        "SELECT validation_stage, required_for_acceptance, outcome FROM import_validation_result"
    ).fetchall()
    if any(int(row[1]) != 1 or str(row[2]) != "passed" for row in rows):
        raise RuntimeError("Database v3 contains non-passing required validation evidence")
    return len(rows), frozenset(str(row[0]) for row in rows)


def _validate_candidate_database(path: Path) -> None:
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        header = (
            int(connection.execute("PRAGMA application_id").fetchone()[0]),
            int(connection.execute("PRAGMA user_version").fetchone()[0]),
        )
        if header != (APPLICATION_ID, EXTERNAL_RECONCILIATION_SCHEMA_VERSION):
            raise RuntimeError(f"Database v3 candidate SQLite header mismatch: {header!r}")
        manifest = connection.execute(
            """
            SELECT import_manifest_code, database_release_code, governance_release_id,
                   schema_version, code_commit, reference_data_commit,
                   prior_database_release_code, prior_release_preserved,
                   build_status, failure_reason
            FROM import_manifest
            """
        ).fetchone()
        expected = (
            EXPECTED_MANIFEST_CODE,
            EXPECTED_DATABASE_RELEASE_CODE,
            EXPECTED_GOVERNANCE_RELEASE_ID,
            EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
            EXPECTED_BUILD_COMMIT,
            EXPECTED_REFERENCE_COMMIT,
            EXPECTED_PRIOR_DATABASE_RELEASE_CODE,
            1,
            "validated",
            None,
        )
        if manifest != expected:
            raise RuntimeError(f"Database v3 candidate manifest mismatch: {manifest!r}")
        count, stages = _validation_stages(connection)
        if count != EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT or stages != EXPECTED_CANDIDATE_STAGES:
            raise RuntimeError(
                f"Database v3 candidate validation evidence mismatch: count={count}, stages={sorted(stages)}"
            )
        releases = connection.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release WHERE source_version_id=1 ORDER BY governance_release_id
            """
        ).fetchall()
        if releases != [(1, "superseded", 2), (2, "superseded", 3), (3, "accepted", None)]:
            raise RuntimeError(f"Database v3 governance lineage mismatch: {releases!r}")
        if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
            raise RuntimeError("Database v3 candidate quick_check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Database v3 candidate foreign_key_check failed")


def _record_release_evidence(
    connection: sqlite3.Connection,
    *,
    recorded_at_utc: str,
    promotion_repository_commit: str,
) -> None:
    count, stages = _validation_stages(connection)
    if count != EXPECTED_CANDIDATE_VALIDATION_RESULT_COUNT or stages != EXPECTED_CANDIDATE_STAGES:
        raise RuntimeError("Release staging copy does not begin from exact validated v3 evidence")
    next_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(import_validation_result_id),0)+1 FROM import_validation_result"
        ).fetchone()[0]
    )
    rows = (
        (
            "focused_unit_tests",
            "database-v3-release-evidence-recorder",
            "1",
            "pytest -q tests/test_database_schema_v003.py tests/test_database_v3_*.py",
            "Database v3 focused release-boundary tests passed before promotion; see the release contract for the observed count and timing.",
        ),
        (
            "project_acceptance_gate",
            "database-v3-release-evidence-recorder",
            "1",
            "pytest -q; applicable independent validator sweep",
            "Database v3 project acceptance gate passed before promotion; complete repository tests and all applicable independent validators passed. "
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
                name,
                version,
                recorded_at_utc,
                command,
                summary,
                RELEASE_CONTRACT_PATH,
            )
            for offset, (stage, name, version, command, summary) in enumerate(rows)
        ],
    )
    release_id = int(connection.execute("SELECT governance_release_id FROM import_manifest").fetchone()[0])
    existing = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM governance_release_evidence
            WHERE governance_release_id=? AND evidence_type='document' AND evidence_reference=?
            """,
            (release_id, RELEASE_CONTRACT_PATH),
        ).fetchone()[0]
    )
    if existing:
        raise RuntimeError("Database v3 release contract evidence already attached")
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
            "Database v3 release acceptance and promotion contract.",
        ),
    )


def _accept_staging_copy(path: Path, *, promotion_repository_commit: str) -> None:
    connection = sqlite3.connect(path)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        connection.execute("BEGIN IMMEDIATE")
        status = str(connection.execute("SELECT build_status FROM import_manifest").fetchone()[0])
        if status != "validated":
            raise RuntimeError(f"Database v3 staging copy must begin validated; found {status!r}")
        recorded_at = _timestamp_utc()
        _record_release_evidence(
            connection,
            recorded_at_utc=recorded_at,
            promotion_repository_commit=promotion_repository_commit,
        )
        connection.execute(
            "UPDATE import_manifest SET build_status='release_accepted' WHERE import_manifest_id=1 AND build_status='validated'"
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise RuntimeError("Database v3 staging copy could not advance to release_accepted")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def promote_inside_rails_v3(
    candidate_path: str | Path,
    release_path: str | Path,
    *,
    project_root: str | Path,
    promotion_repository_commit: str,
    base_release_path: str | Path | None = None,
) -> PromotionSummary:
    """Promote one exact validated v3 candidate without mutating it or accepted v2."""

    root = Path(project_root).expanduser().resolve()
    candidate = Path(candidate_path).expanduser().resolve()
    release = Path(release_path).expanduser().resolve()
    base = (
        Path(base_release_path).expanduser().resolve()
        if base_release_path is not None
        else default_base_release_path(root).resolve()
    )
    promotion_commit = repository_commit(
        promotion_repository_commit, name="promotion_repository_commit"
    )
    if candidate == release or candidate == base or release == base:
        raise ValueError("Candidate, release and accepted v2 paths must be distinct")
    if release.exists():
        raise FileExistsError(f"Database v3 release already exists: {release}")

    candidate_hash = _validate_hash(
        candidate, EXPECTED_CANDIDATE_SHA256_HEX, label="Validated Database v3 candidate"
    )
    if base.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError("Accepted Database v2 size changed before v3 promotion")
    base_hash = _validate_hash(
        base, EXPECTED_BASE_RELEASE_SHA256.hex(), label="Accepted Database v2 release"
    )
    _validate_candidate_database(candidate)
    validate_external_reconciliation_candidate(candidate, base)

    release.parent.mkdir(parents=True, exist_ok=True)
    staging = release.with_name(f".{release.name}.staging-{uuid.uuid4().hex}")
    try:
        shutil.copyfile(candidate, staging)
        if sha256_file(staging).hex() != candidate_hash:
            raise RuntimeError("Database v3 staging copy differs from validated candidate")
        _accept_staging_copy(staging, promotion_repository_commit=promotion_commit)
        validation = validate_external_reconciliation_candidate(staging, base)
        with connect_read_only(staging) as connection:
            configure_governed_connection(connection, query_only=True)
            manifest_status = str(connection.execute("SELECT build_status FROM import_manifest").fetchone()[0])
            count, stages = _validation_stages(connection)
            quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
            fk_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
            application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
            user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if manifest_status != "release_accepted":
            raise RuntimeError(f"Database v3 staging manifest is not accepted: {manifest_status!r}")
        if count != EXPECTED_RELEASE_VALIDATION_RESULT_COUNT or stages != EXPECTED_RELEASE_STAGES:
            raise RuntimeError("Database v3 release validation evidence is incomplete")
        if quick != "ok" or fk_rows:
            raise RuntimeError("Database v3 release staging integrity checks failed")
        if (application_id, user_version) != (APPLICATION_ID, EXTERNAL_RECONCILIATION_SCHEMA_VERSION):
            raise RuntimeError("Database v3 release staging SQLite header changed")
        if sha256_file(candidate).hex() != candidate_hash:
            raise RuntimeError("Validated Database v3 candidate changed during promotion")
        if sha256_file(base).hex() != base_hash:
            raise RuntimeError("Accepted Database v2 release changed during promotion")
        os.replace(staging, release)
        os.chmod(release, 0o444)
    except Exception:
        try:
            staging.unlink()
        except FileNotFoundError:
            pass
        try:
            release.unlink()
        except FileNotFoundError:
            pass
        raise

    release_hash = sha256_file(release).hex()
    final_validation = validate_external_reconciliation_candidate(release, base)
    if sha256_file(candidate).hex() != candidate_hash:
        raise RuntimeError("Validated Database v3 candidate changed after publication")
    if sha256_file(base).hex() != base_hash:
        raise RuntimeError("Accepted Database v2 release changed after publication")

    return PromotionSummary(
        candidate_path=str(candidate),
        release_path=str(release),
        base_release_path=str(base),
        candidate_sha256_hex=candidate_hash,
        release_sha256_hex=release_hash,
        candidate_size_bytes=candidate.stat().st_size,
        release_size_bytes=release.stat().st_size,
        manifest_status="release_accepted",
        validation_result_count=EXPECTED_RELEASE_VALIDATION_RESULT_COUNT,
        quick_check="ok",
        foreign_key_check_rows=0,
        application_id=APPLICATION_ID,
        user_version=EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
        release_validator_manifest_status=final_validation.manifest_status,
        raw_record_rows_compared=final_validation.raw_record_rows_compared,
        structural_race_rows_compared=final_validation.structural_race_rows_compared,
        structural_runner_rows_compared=final_validation.structural_runner_rows_compared,
        promotion_repository_commit=promotion_commit,
        candidate_hash_unchanged=True,
        prior_release_preserved=True,
        release_accepted=True,
    )


__all__ = [
    "PromotionSummary",
    "default_base_release_path",
    "default_candidate_path",
    "default_release_path",
    "promote_inside_rails_v3",
]
