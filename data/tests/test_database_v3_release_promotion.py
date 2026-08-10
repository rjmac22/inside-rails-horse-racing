from __future__ import annotations

from pathlib import Path

import pytest

from inside_rails.database.release_v3 import (
    EXPECTED_CANDIDATE_SHA256_HEX,
    EXPECTED_CANDIDATE_STAGES,
    EXPECTED_RELEASE_STAGES,
    default_base_release_path,
    default_candidate_path,
    default_release_path,
    promote_inside_rails_v3,
)


VALID_COMMIT = "a" * 40


def test_v3_promotion_is_bound_to_exact_validated_candidate_hash() -> None:
    assert (
        EXPECTED_CANDIDATE_SHA256_HEX
        == "0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b"
    )


def test_v3_release_stages_extend_candidate_stages_only_at_release_boundary() -> None:
    assert EXPECTED_RELEASE_STAGES == EXPECTED_CANDIDATE_STAGES | {
        "focused_unit_tests",
        "project_acceptance_gate",
    }


def test_v3_default_paths_keep_candidate_release_and_v2_distinct(tmp_path: Path) -> None:
    assert default_candidate_path(tmp_path) != default_release_path(tmp_path)
    assert default_candidate_path(tmp_path) != default_base_release_path(tmp_path)
    assert default_release_path(tmp_path) != default_base_release_path(tmp_path)
    assert default_base_release_path(tmp_path).name == "inside_rails_v2.sqlite3"
    assert default_release_path(tmp_path).name == "inside_rails_v3.sqlite3"


def test_v3_promotion_rejects_path_aliasing_before_any_write(tmp_path: Path) -> None:
    shared = tmp_path / "shared.sqlite3"
    with pytest.raises(ValueError, match="must be distinct"):
        promote_inside_rails_v3(
            shared,
            shared,
            project_root=tmp_path,
            promotion_repository_commit=VALID_COMMIT,
            base_release_path=tmp_path / "v2.sqlite3",
        )


def test_v3_promotion_never_overwrites_existing_release(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.sqlite3"
    release = tmp_path / "release.sqlite3"
    base = tmp_path / "v2.sqlite3"
    release.write_bytes(b"existing-release")
    with pytest.raises(FileExistsError, match="already exists"):
        promote_inside_rails_v3(
            candidate,
            release,
            project_root=tmp_path,
            promotion_repository_commit=VALID_COMMIT,
            base_release_path=base,
        )
