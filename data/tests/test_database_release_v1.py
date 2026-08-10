from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3

import pytest

import inside_rails.database.release_v1 as release_v1


def _sha256(path: Path) -> bytes:
    return hashlib.sha256(path.read_bytes()).digest()


def test_release_paths_use_inside_rails_owned_names(tmp_path: Path) -> None:
    assert release_v1.default_candidate_path(tmp_path) == (
        tmp_path
        / "data"
        / "processed"
        / "database"
        / "candidates"
        / "inside_rails_v1_candidate.sqlite3"
    )
    assert release_v1.default_release_path(tmp_path) == (
        tmp_path
        / "data"
        / "processed"
        / "database"
        / "releases"
        / "inside_rails_v1.sqlite3"
    )


def test_candidate_identity_is_bound_to_exact_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v1_candidate.sqlite3"
    candidate.write_bytes(b"exact candidate bytes")
    monkeypatch.setattr(
        release_v1,
        "EXPECTED_CANDIDATE_SIZE_BYTES",
        candidate.stat().st_size,
    )
    monkeypatch.setattr(
        release_v1,
        "EXPECTED_CANDIDATE_SHA256_HEX",
        _sha256(candidate).hex(),
    )

    assert release_v1._validate_candidate_identity(candidate) == _sha256(candidate).hex()

    candidate.write_bytes(b"changed candidate bytes")
    with pytest.raises(RuntimeError, match="Candidate size mismatch|Candidate SHA-256 mismatch"):
        release_v1._validate_candidate_identity(candidate)


def test_record_acceptance_evidence_adds_three_missing_stages() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            """
            CREATE TABLE import_manifest (
                import_manifest_id INTEGER PRIMARY KEY,
                source_version_id INTEGER NOT NULL,
                governance_release_id INTEGER NOT NULL,
                physical_record_count INTEGER NOT NULL,
                admitted_record_count INTEGER NOT NULL,
                excluded_record_count INTEGER NOT NULL,
                race_occurrence_count INTEGER NOT NULL,
                runner_participation_count INTEGER NOT NULL,
                persisted_readback_passed INTEGER NOT NULL,
                sqlite_integrity_passed INTEGER NOT NULL,
                foreign_key_check_passed INTEGER NOT NULL,
                post_load_validation_passed INTEGER NOT NULL,
                prior_release_preserved INTEGER NOT NULL,
                build_status TEXT NOT NULL,
                failure_reason TEXT
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
                1, 1, 1, 1851286, 1851285, 1, 189043, 1851285,
                1, 1, 1, 1, 1, 'built', NULL
            )
            """
        )
        for index, stage in enumerate(sorted(release_v1.EXPECTED_BUILDER_STAGES), start=1):
            connection.execute(
                """
                INSERT INTO import_validation_result VALUES (
                    ?, 1, ?, 'builder', '1', 1, 'passed',
                    '2026-08-06T00:00:00.000000Z', 'builder', 'passed', NULL
                )
                """,
                (index, stage),
            )

        release_v1._record_acceptance_evidence(
            connection,
            recorded_at_utc="2026-08-08T12:00:00.000000Z",
        )

        stages = {
            row[0]
            for row in connection.execute(
                "SELECT validation_stage FROM import_validation_result"
            ).fetchall()
        }
        assert stages == release_v1.EXPECTED_RELEASE_STAGES
        assert connection.execute(
            """
            SELECT COUNT(*) FROM governance_release_evidence
            WHERE evidence_reference = ?
            """,
            (release_v1.RELEASE_CONTRACT_PATH,),
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_promotion_preserves_candidate_and_publishes_validated_copy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v1_candidate.sqlite3"
    release = tmp_path / "releases" / "inside_rails_v1.sqlite3"
    candidate.write_bytes(b"validated candidate")
    candidate_hash = _sha256(candidate).hex()

    monkeypatch.setattr(
        release_v1,
        "_validate_candidate_identity",
        lambda path: candidate_hash,
    )
    monkeypatch.setattr(release_v1, "_validate_candidate_database", lambda path: None)

    def accept_copy(path: Path, *, accepted_at_utc: str) -> None:
        path.write_bytes(path.read_bytes() + b"|release accepted")

    monkeypatch.setattr(release_v1, "_accept_release_copy", accept_copy)
    validation = ("release_accepted", 7, "ok", 0, 1230130259, 1)
    monkeypatch.setattr(
        release_v1,
        "_validate_release_database",
        lambda path: validation,
    )

    summary = release_v1.promote_inside_rails_v1(
        candidate,
        release,
        accepted_at_utc="2026-08-08T12:00:00.000000Z",
    )

    assert candidate.read_bytes() == b"validated candidate"
    assert release.read_bytes() == b"validated candidate|release accepted"
    assert summary.candidate_sha256_hex == candidate_hash
    assert summary.release_sha256_hex == _sha256(release).hex()
    assert summary.manifest_status == "release_accepted"
    assert summary.release_accepted is True
    assert not list(release.parent.glob("*.promoting-*.sqlite3"))


def test_promotion_failure_removes_staging_and_leaves_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "inside_rails_v1_candidate.sqlite3"
    release = tmp_path / "releases" / "inside_rails_v1.sqlite3"
    candidate.write_bytes(b"validated candidate")
    candidate_hash = _sha256(candidate).hex()

    monkeypatch.setattr(
        release_v1,
        "_validate_candidate_identity",
        lambda path: candidate_hash,
    )
    monkeypatch.setattr(release_v1, "_validate_candidate_database", lambda path: None)
    monkeypatch.setattr(release_v1, "_accept_release_copy", lambda *args, **kwargs: None)

    def fail_validation(path: Path) -> tuple[str, int, str, int, int, int]:
        raise RuntimeError("forced release validation failure")

    monkeypatch.setattr(release_v1, "_validate_release_database", fail_validation)

    with pytest.raises(RuntimeError, match="forced release validation failure"):
        release_v1.promote_inside_rails_v1(
            candidate,
            release,
            accepted_at_utc="2026-08-08T12:00:00.000000Z",
        )

    assert candidate.read_bytes() == b"validated candidate"
    assert not release.exists()
    assert not list(release.parent.glob("*.promoting-*.sqlite3"))


def test_existing_release_is_never_overwritten(tmp_path: Path) -> None:
    candidate = tmp_path / "inside_rails_v1_candidate.sqlite3"
    release = tmp_path / "inside_rails_v1.sqlite3"
    candidate.write_bytes(b"candidate")
    release.write_bytes(b"existing release")

    with pytest.raises(FileExistsError, match="Accepted release already exists"):
        release_v1.promote_inside_rails_v1(candidate, release)

    assert release.read_bytes() == b"existing release"
