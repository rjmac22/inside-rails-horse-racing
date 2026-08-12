from __future__ import annotations

from pathlib import Path

import pytest

from inside_rails.database.release_v4 import (
    EXPECTED_BUILD_COMMIT,
    EXPECTED_CANDIDATE_SHA256_HEX,
    EXPECTED_CANDIDATE_STAGES,
    EXPECTED_DATABASE_RELEASE_CODE,
    EXPECTED_MANIFEST_CODE,
    EXPECTED_RELEASE_STAGES,
    default_base_release_path,
    default_candidate_path,
    default_release_path,
    promote_inside_rails_v4,
)


VALID_COMMIT = "a" * 40


def test_v4_promotion_is_bound_to_exact_built_candidate() -> None:
    assert (
        EXPECTED_CANDIDATE_SHA256_HEX
        == "04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e"
    )
    assert EXPECTED_BUILD_COMMIT == "dc84089aa858d45ec64c6bfe087b0cf6b763dbc2"
    assert EXPECTED_MANIFEST_CODE == "imp:20260811T215904471424Z:80905d2d"
    assert EXPECTED_DATABASE_RELEASE_CODE == "db:20260811T215904471424Z:928240a8"


def test_v4_release_stages_add_all_acceptance_evidence_only_at_release_boundary() -> None:
    assert EXPECTED_CANDIDATE_STAGES == {
        "persisted_readback",
        "sqlite_integrity",
        "foreign_key_validation",
        "post_load_validation",
    }
    assert EXPECTED_RELEASE_STAGES == EXPECTED_CANDIDATE_STAGES | {
        "source_wide_validation",
        "focused_unit_tests",
        "project_acceptance_gate",
    }


def test_v4_default_paths_keep_candidate_release_and_v3_distinct(tmp_path: Path) -> None:
    assert default_candidate_path(tmp_path) != default_release_path(tmp_path)
    assert default_candidate_path(tmp_path) != default_base_release_path(tmp_path)
    assert default_release_path(tmp_path) != default_base_release_path(tmp_path)
    assert default_base_release_path(tmp_path).name == "inside_rails_v3.sqlite3"
    assert default_release_path(tmp_path).name == "inside_rails_v4.sqlite3"


def test_v4_promotion_rejects_path_aliasing_before_any_write(tmp_path: Path) -> None:
    shared = tmp_path / "shared.sqlite3"
    with pytest.raises(ValueError, match="must be distinct"):
        promote_inside_rails_v4(
            shared,
            shared,
            project_root=tmp_path,
            promotion_repository_commit=VALID_COMMIT,
            base_release_path=tmp_path / "v3.sqlite3",
        )


def test_v4_promotion_never_overwrites_existing_release(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.sqlite3"
    release = tmp_path / "release.sqlite3"
    base = tmp_path / "v3.sqlite3"
    release.write_bytes(b"existing-release")
    with pytest.raises(FileExistsError, match="already exists"):
        promote_inside_rails_v4(
            candidate,
            release,
            project_root=tmp_path,
            promotion_repository_commit=VALID_COMMIT,
            base_release_path=base,
        )


def test_v4_promotion_rejects_stale_release_sidecar_before_any_write(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.sqlite3"
    release = tmp_path / "release.sqlite3"
    base = tmp_path / "v3.sqlite3"
    Path(f"{release}-wal").write_bytes(b"stale")
    with pytest.raises(FileExistsError, match="release artifact already exists"):
        promote_inside_rails_v4(
            candidate,
            release,
            project_root=tmp_path,
            promotion_repository_commit=VALID_COMMIT,
            base_release_path=base,
        )
