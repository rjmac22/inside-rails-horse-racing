"""Fail-closed acceptance and promotion for the first Inside Rails v1 release."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import uuid

from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_CANDIDATE_SHA256_HEX = (
    "7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2"
)
EXPECTED_CANDIDATE_SIZE_BYTES = 1_730_048_000
EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285

EXPECTED_BUILDER_STAGES = frozenset(
    {
        "persisted_readback",
        "sqlite_integrity",
        "foreign_key_validation",
        "post_load_validation",
    }
)
EXPECTED_RELEASE_STAGES = frozenset(
    {
        *EXPECTED_BUILDER_STAGES,
        "focused_unit_tests",
        "source_wide_validation",
        "project_acceptance_gate",
    }
)

RELEASE_CONTRACT_PATH = "docs/PHASE_4_RELEASE_ACCEPTANCE_AND_PROMOTION_CONTRACT.md"


@dataclass(frozen=True)
class PromotionSummary:
    candidate_path: str
    release_path: str
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
    candidate_hash_unchanged: bool
    release_accepted: bool


def default_candidate_path(project_root: str | Path) -> Path:
    """Return the canonical unreleased Version 1 candidate path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v1_candidate.sqlite3"
    )


def default_release_path(project_root: str | Path) -> Path:
    """Return the canonical accepted Version 1 database path."""

    return (
        Path(project_root)
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v1.sqlite3"
    )


def _timestamp_utc(value: str | None = None) -> str:
    if value is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
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
        raise FileNotFoundError(f"Validated candidate not found: {path}")
    _assert_no_sidecars(path)
    observed_size = path.stat().st_size
    if observed_size != EXPECTED_CANDIDATE_SIZE_BYTES:
        raise RuntimeError(
            "Candidate size mismatch: "
            f"expected {EXPECTED_CANDIDATE_SIZE_BYTES}, observed {observed_size}"
        )
    observed_hash = sha256_file(path).hex()
    if observed_hash != EXPECTED_CANDIDATE_SHA256_HEX:
        raise RuntimeError(
            "Candidate SHA-256 mismatch: "
            f"expected {EXPECTED_CANDIDATE_SHA256_HEX}, observed {observed_hash}"
        )
    return observed_hash


def _read_manifest(connection: sqlite3.Connection) -> tuple[object, ...]:
    row = connection.execute(
        """
        SELECT import_manifest_id, source_version_id, governance_release_id,
               physical_record_count, admitted_record_count, excluded_record_count,
               race_occurrence_count, runner_participation_count,
               persisted_readback_passed, sqlite_integrity_passed,
               foreign_key_check_passed, post_load_validation_passed,
               prior_release_preserved, build_status, failure_reason
        FROM import_manifest
        """
    ).fetchall()
    if len(row) != 1:
        raise RuntimeError(f"Expected exactly one import manifest; observed {len(row)}")
    return tuple(row[0])


def _validate_candidate_database(path: Path) -> tuple[int, int]:
    with connect_read_only(path) as connection:
        configure_governed_connection(connection, query_only=True)
        manifest = _read_manifest(connection)
        expected = (
            1,
            1,
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
            "built",
            None,
        )
        if manifest != expected:
            raise RuntimeError(f"Candidate import manifest mismatch: {manifest!r}")

        stages = {
            str(row[0])
            for row in connection.execute(
                "SELECT validation_stage FROM import_validation_result"
            ).fetchall()
        }
        if stages != EXPECTED_BUILDER_STAGES:
            raise RuntimeError(
                "Candidate validation stages mismatch: "
                f"expected {sorted(EXPECTED_BUILDER_STAGES)}, observed {sorted(stages)}"
            )

        quick_row = connection.execute("PRAGMA quick_check").fetchone()
        quick = "" if quick_row is None else str(quick_row[0])
        if quick != "ok":
            raise RuntimeError(f"Candidate quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Candidate foreign_key_check returned {foreign_key_rows} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID or user_version != SCHEMA_VERSION:
            raise RuntimeError("Candidate SQLite header mismatch")

    return application_id, user_version


def _record_acceptance_evidence(
    connection: sqlite3.Connection,
    *,
    recorded_at_utc: str,
) -> None:
    manifest = _read_manifest(connection)
    import_manifest_id = int(manifest[0])
    governance_release_id = int(manifest[2])

    next_validation_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(import_validation_result_id), 0) + 1 "
            "FROM import_validation_result"
        ).fetchone()[0]
    )
    rows = (
        (
            "focused_unit_tests",
            "phase4_evidence_recorder",
            "1",
            "record prior evidence: docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md",
            "Prior bounded database gate passed on 2026-08-06: 72 passed in 14.54s; "
            f"evidence is bound to candidate SHA-256 {EXPECTED_CANDIDATE_SHA256_HEX}.",
            "docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md",
        ),
        (
            "source_wide_validation",
            "phase4_evidence_recorder",
            "1",
            "record prior evidence: docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md",
            "Prior independent source-wide validation passed on 2026-08-06 and "
            "reconciled 1,851,286 raw records, 189,043 races and 1,851,285 runners; "
            f"evidence is bound to candidate SHA-256 {EXPECTED_CANDIDATE_SHA256_HEX}.",
            "docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md",
        ),
        (
            "project_acceptance_gate",
            "phase4_evidence_recorder",
            "1",
            "record prior evidence: docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md",
            "Prior final repository-wide technical gate passed on 2026-08-06 at "
            "commit bf1d7f7b253edaf7232351e33ada92b039ca97ba: "
            "354 tests passed and all 31 independent validators passed.",
            "docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md",
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
                details_path,
            )
            for offset, (
                stage,
                validator_name,
                validator_version,
                command,
                summary,
                details_path,
            ) in enumerate(rows)
        ],
    )

    existing_contract = connection.execute(
        """
        SELECT 1
        FROM governance_release_evidence
        WHERE governance_release_id = ?
          AND evidence_type = 'document'
          AND evidence_reference = ?
        """,
        (governance_release_id, RELEASE_CONTRACT_PATH),
    ).fetchone()
    if existing_contract is not None:
        raise RuntimeError("Release contract evidence is already attached")

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
            "First Inside Rails Version 1 database release acceptance and promotion "
            "contract, including explicit project-owner acceptance on 2026-08-08.",
        ),
    )


def _accept_release_copy(path: Path, *, accepted_at_utc: str) -> None:
    connection = sqlite3.connect(path)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        connection.execute("BEGIN IMMEDIATE")
        if str(_read_manifest(connection)[13]) != "built":
            raise RuntimeError("Release copy must begin from built manifest status")
        _record_acceptance_evidence(connection, recorded_at_utc=accepted_at_utc)
        connection.execute(
            "UPDATE import_manifest SET build_status = 'validated' "
            "WHERE import_manifest_id = 1"
        )
        if connection.execute(
            "SELECT build_status FROM import_manifest WHERE import_manifest_id = 1"
        ).fetchone()[0] != "validated":
            raise RuntimeError("Manifest failed to enter validated status")
        connection.execute(
            "UPDATE import_manifest SET build_status = 'release_accepted' "
            "WHERE import_manifest_id = 1"
        )
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
        if str(manifest[13]) != "release_accepted" or manifest[14] is not None:
            raise RuntimeError(f"Release manifest is not accepted: {manifest!r}")
        expected_counts = (
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_EXCLUDED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
        )
        if tuple(int(value) for value in manifest[3:8]) != expected_counts:
            raise RuntimeError("Accepted release population counts changed")
        if tuple(int(value) for value in manifest[8:13]) != (1, 1, 1, 1, 1):
            raise RuntimeError("Accepted release validation flags are incomplete")

        stage_rows = connection.execute(
            """
            SELECT validation_stage, required_for_acceptance, outcome
            FROM import_validation_result
            ORDER BY import_validation_result_id
            """
        ).fetchall()
        stages = {str(row[0]) for row in stage_rows}
        if stages != EXPECTED_RELEASE_STAGES:
            raise RuntimeError(
                "Accepted release validation-stage mismatch: "
                f"expected {sorted(EXPECTED_RELEASE_STAGES)}, observed {sorted(stages)}"
            )
        if any(int(row[1]) != 1 or str(row[2]) != "passed" for row in stage_rows):
            raise RuntimeError("Accepted release contains non-passing required evidence")

        contract_rows = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM governance_release_evidence
                WHERE evidence_type = 'document'
                  AND evidence_reference = ?
                """,
                (RELEASE_CONTRACT_PATH,),
            ).fetchone()[0]
        )
        if contract_rows != 1:
            raise RuntimeError("Accepted release is missing release-contract evidence")

        quick_row = connection.execute("PRAGMA quick_check").fetchone()
        quick = "" if quick_row is None else str(quick_row[0])
        if quick != "ok":
            raise RuntimeError(f"Accepted release quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Accepted release foreign_key_check returned {foreign_key_rows} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID or user_version != SCHEMA_VERSION:
            raise RuntimeError("Accepted release SQLite header mismatch")

    return (
        "release_accepted",
        len(stage_rows),
        quick,
        foreign_key_rows,
        application_id,
        user_version,
    )


def _fsync_directory(path: Path) -> None:
    if os.name != "posix":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def promote_inside_rails_v1(
    candidate_path: str | Path,
    release_path: str | Path,
    *,
    accepted_at_utc: str | None = None,
) -> PromotionSummary:
    """Promote the exact validated candidate without mutating the candidate itself."""

    candidate = Path(candidate_path).resolve()
    release = Path(release_path).resolve()
    accepted_at = _timestamp_utc(accepted_at_utc)

    if candidate == release:
        raise ValueError("Candidate and release paths must be different")
    if release.exists():
        raise FileExistsError(f"Accepted release already exists: {release}")
    _assert_no_sidecars(release)

    candidate_hash_before = _validate_candidate_identity(candidate)
    _validate_candidate_database(candidate)

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
            raise RuntimeError("Promotion copy SHA-256 does not match validated candidate")

        _accept_release_copy(staging, accepted_at_utc=accepted_at)
        (
            manifest_status,
            validation_result_count,
            quick_check,
            foreign_key_check_rows,
            application_id,
            user_version,
        ) = _validate_release_database(staging)

        candidate_hash_after = sha256_file(candidate).hex()
        if candidate_hash_after != candidate_hash_before:
            raise RuntimeError("Validated candidate changed during promotion")

        release_hash = sha256_file(staging).hex()
        release_size = staging.stat().st_size

        if release.exists():
            raise FileExistsError(f"Accepted release appeared during promotion: {release}")
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
            raise RuntimeError("Final release readback changed after atomic publication")
        if sha256_file(release).hex() != release_hash:
            raise RuntimeError("Final release SHA-256 changed after atomic publication")
        if sha256_file(candidate).hex() != candidate_hash_before:
            raise RuntimeError("Validated candidate changed after publication")

        return PromotionSummary(
            candidate_path=str(candidate),
            release_path=str(release),
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
            candidate_hash_unchanged=True,
            release_accepted=True,
        )
    except Exception:
        _remove_artifact(staging)
        if published:
            _remove_artifact(release)
            _fsync_directory(release.parent)
        raise
