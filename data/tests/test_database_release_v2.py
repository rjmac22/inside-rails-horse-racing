from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

import inside_rails.database.release_v2 as release_v2


def _sha256(path: Path) -> bytes:
    return hashlib.sha256(path.read_bytes()).digest()


def test_release_paths_use_v2_inside_rails_names(tmp_path: Path) -> None:
    assert release_v2.default_candidate_path(tmp_path) == (
        tmp_path
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v2_candidate.sqlite3"
    )
    assert release_v2.default_release_path(tmp_path) == (
        tmp_path
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v2.sqlite3"
    )
    assert release_v2.default_base_release_path(tmp_path) == (
        tmp_path
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v1.sqlite3"
    )


def test_candidate_identity_is_bound_to_exact_validated_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v2_candidate.sqlite3"
    candidate.write_bytes(b"exact validated v2 candidate")
    monkeypatch.setattr(
        release_v2,
        "EXPECTED_CANDIDATE_SHA256_HEX",
        _sha256(candidate).hex(),
    )

    assert release_v2._validate_candidate_identity(candidate) == _sha256(candidate).hex()

    candidate.write_bytes(b"changed v2 candidate")
    with pytest.raises(RuntimeError, match="candidate SHA-256 mismatch"):
        release_v2._validate_candidate_identity(candidate)


def _acceptance_evidence_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE import_manifest (
            import_manifest_id INTEGER PRIMARY KEY,
            import_manifest_code TEXT NOT NULL,
            database_release_code TEXT NOT NULL,
            source_version_id INTEGER NOT NULL,
            governance_release_id INTEGER NOT NULL,
            schema_version INTEGER NOT NULL,
            code_commit TEXT NOT NULL,
            reference_data_commit TEXT NOT NULL,
            physical_record_count INTEGER NOT NULL,
            admitted_record_count INTEGER NOT NULL,
            excluded_record_count INTEGER NOT NULL,
            race_occurrence_count INTEGER NOT NULL,
            runner_participation_count INTEGER NOT NULL,
            persisted_readback_passed INTEGER NOT NULL,
            sqlite_integrity_passed INTEGER NOT NULL,
            foreign_key_check_passed INTEGER NOT NULL,
            post_load_validation_passed INTEGER NOT NULL,
            prior_database_release_code TEXT,
            prior_release_preserved INTEGER NOT NULL,
            build_status TEXT NOT NULL,
            failure_reason TEXT,
            build_completed_at_utc TEXT
        );
        CREATE TABLE import_validation_result (
            import_validation_result_id INTEGER PRIMARY KEY,
            import_manifest_id INTEGER NOT NULL,
            validation_stage TEXT NOT NULL,
            validator_name TEXT NOT NULL,
            validator_version TEXT NOT NULL,
            required_for_acceptance INTEGER NOT NULL,
            outcome TEXT NOT NULL,
            executed_at_utc TEXT NOT NULL,
            command TEXT NOT NULL,
            result_summary TEXT NOT NULL,
            details_artifact_path TEXT
        );
        CREATE TABLE governance_release_evidence (
            governance_release_evidence_id INTEGER PRIMARY KEY,
            governance_release_id INTEGER NOT NULL,
            evidence_type TEXT NOT NULL,
            evidence_reference TEXT NOT NULL,
            evidence_sha256 BLOB,
            evidence_description TEXT NOT NULL
        );
        """
    )
    connection.execute(
        """
        INSERT INTO import_manifest VALUES (
            1, ?, ?, 1, 2, 2, ?, ?,
            1851286, 1851285, 1, 189043, 1851285,
            1, 1, 1, 1, ?, 1, 'validated', NULL,
            '2026-08-09T08:30:00.000000Z'
        )
        """,
        (
            release_v2.EXPECTED_MANIFEST_CODE,
            release_v2.EXPECTED_DATABASE_RELEASE_CODE,
            release_v2.EXPECTED_BUILD_COMMIT,
            release_v2.EXPECTED_REFERENCE_COMMIT,
            release_v2.EXPECTED_PRIOR_DATABASE_RELEASE_CODE,
        ),
    )
    for index, stage in enumerate(sorted(release_v2.EXPECTED_CANDIDATE_STAGES), start=1):
        validator_name = (
            "database-v2-governed-integration-validator"
            if stage == "source_wide_validation"
            else "builder"
        )
        connection.execute(
            """
            INSERT INTO import_validation_result VALUES (
                ?, 1, ?, ?, '1', 1, 'passed',
                '2026-08-09T08:30:00.000000Z', 'command', 'passed', NULL
            )
            """,
            (index, stage, validator_name),
        )
    return connection


def test_record_acceptance_evidence_adds_only_missing_release_stages() -> None:
    connection = _acceptance_evidence_connection()
    try:
        release_v2._record_acceptance_evidence(
            connection,
            recorded_at_utc="2026-08-09T10:30:00.000000Z",
            promotion_repository_commit="a" * 40,
        )

        stages = [
            row[0]
            for row in connection.execute(
                "SELECT validation_stage FROM import_validation_result ORDER BY import_validation_result_id"
            ).fetchall()
        ]
        assert len(stages) == release_v2.EXPECTED_RELEASE_VALIDATION_RESULT_COUNT
        assert set(stages) == release_v2.EXPECTED_RELEASE_STAGES
        assert stages.count("source_wide_validation") == 1
        assert connection.execute(
            """
            SELECT COUNT(*) FROM governance_release_evidence
            WHERE governance_release_id = 2
              AND evidence_reference = ?
            """,
            (release_v2.RELEASE_CONTRACT_PATH,),
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_promotion_preserves_candidate_and_v1_and_publishes_accepted_copy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v2_candidate.sqlite3"
    base = tmp_path / "inside_rails_v1.sqlite3"
    release = tmp_path / "releases" / "inside_rails_v2.sqlite3"
    candidate.write_bytes(b"validated v2 candidate")
    base.write_bytes(b"accepted v1")
    candidate_hash = _sha256(candidate).hex()
    base_hash = _sha256(base).hex()

    monkeypatch.setattr(release_v2, "_validate_candidate_identity", lambda path: candidate_hash)
    monkeypatch.setattr(release_v2, "_validate_candidate_database", lambda path: (1230130259, 2))
    monkeypatch.setattr(release_v2, "_validate_base_release_identity", lambda path: base_hash)

    def accept_copy(
        path: Path,
        *,
        accepted_at_utc: str,
        promotion_repository_commit: str,
    ) -> None:
        path.write_bytes(path.read_bytes() + b"|release accepted")

    monkeypatch.setattr(release_v2, "_accept_release_copy", accept_copy)
    validation = ("release_accepted", 7, "ok", 0, 1230130259, 2)
    monkeypatch.setattr(release_v2, "_validate_release_database", lambda path: validation)
    monkeypatch.setattr(
        release_v2,
        "_validate_release_against_base",
        lambda *args, **kwargs: SimpleNamespace(
            manifest_status="release_accepted",
            raw_record_fingerprints_recomputed=1_851_286,
            structural_rows_compared=2_040_328,
        ),
    )

    summary = release_v2.promote_inside_rails_v2(
        candidate,
        release,
        project_root=tmp_path,
        promotion_repository_commit="a" * 40,
        base_release_path=base,
        accepted_at_utc="2026-08-09T10:30:00.000000Z",
    )

    assert candidate.read_bytes() == b"validated v2 candidate"
    assert base.read_bytes() == b"accepted v1"
    assert release.read_bytes() == b"validated v2 candidate|release accepted"
    assert summary.candidate_sha256_hex == candidate_hash
    assert summary.release_sha256_hex == _sha256(release).hex()
    assert summary.validation_result_count == 7
    assert summary.raw_record_fingerprints_recomputed == 1_851_286
    assert summary.structural_rows_compared == 2_040_328
    assert summary.release_accepted is True
    assert summary.prior_release_preserved is True
    assert not list(release.parent.glob("*.promoting-*.sqlite3"))


def test_promotion_failure_removes_release_and_preserves_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v2_candidate.sqlite3"
    base = tmp_path / "inside_rails_v1.sqlite3"
    release = tmp_path / "releases" / "inside_rails_v2.sqlite3"
    candidate.write_bytes(b"validated v2 candidate")
    base.write_bytes(b"accepted v1")
    candidate_hash = _sha256(candidate).hex()
    base_hash = _sha256(base).hex()

    monkeypatch.setattr(release_v2, "_validate_candidate_identity", lambda path: candidate_hash)
    monkeypatch.setattr(release_v2, "_validate_candidate_database", lambda path: (1230130259, 2))
    monkeypatch.setattr(release_v2, "_validate_base_release_identity", lambda path: base_hash)
    monkeypatch.setattr(release_v2, "_accept_release_copy", lambda *args, **kwargs: None)

    def fail_validation(path: Path) -> tuple[str, int, str, int, int, int]:
        raise RuntimeError("forced v2 release validation failure")

    monkeypatch.setattr(release_v2, "_validate_release_database", fail_validation)

    with pytest.raises(RuntimeError, match="forced v2 release validation failure"):
        release_v2.promote_inside_rails_v2(
            candidate,
            release,
            project_root=tmp_path,
            promotion_repository_commit="a" * 40,
            base_release_path=base,
            accepted_at_utc="2026-08-09T10:30:00.000000Z",
        )

    assert candidate.read_bytes() == b"validated v2 candidate"
    assert base.read_bytes() == b"accepted v1"
    assert not release.exists()
    assert not list(release.parent.glob("*.promoting-*.sqlite3"))


def test_existing_v2_release_is_never_overwritten(tmp_path: Path) -> None:
    candidate = tmp_path / "inside_rails_v2_candidate.sqlite3"
    release = tmp_path / "inside_rails_v2.sqlite3"
    candidate.write_bytes(b"candidate")
    release.write_bytes(b"existing release")

    with pytest.raises(FileExistsError, match="Accepted Database v2 release already exists"):
        release_v2.promote_inside_rails_v2(
            candidate,
            release,
            project_root=tmp_path,
            promotion_repository_commit="a" * 40,
        )

    assert release.read_bytes() == b"existing release"
