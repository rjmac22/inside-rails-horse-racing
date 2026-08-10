from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import inside_rails.database.accepted_source as accepted_source
from inside_rails.database.raw_mirror_prototype import sha256_file


def test_source_version_1_identity_gate_accepts_exact_hash_and_rejects_mismatch(
    tmp_path: Path,
) -> None:
    source = tmp_path / "raceform.db"
    source.write_bytes(b"controlled Source Version 1 fixture")
    expected = sha256_file(source)

    assert accepted_source.validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected,
    ) == expected

    with pytest.raises(RuntimeError, match="file SHA-256 mismatch"):
        accepted_source.validate_source_version_1_file_identity(
            source,
            expected_source_sha256=bytes.fromhex("00" * 32),
        )


def test_accepted_wrapper_rejects_wrong_source_before_prototype_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    source.write_bytes(b"unaccepted source")
    called = False

    def unexpected_build(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("prototype builder should not have been called")

    monkeypatch.setattr(
        accepted_source,
        "run_raw_mirror_prototype",
        unexpected_build,
    )

    with pytest.raises(RuntimeError, match="file SHA-256 mismatch"):
        accepted_source.run_accepted_raw_mirror_prototype(
            source,
            output,
            expected_source_sha256=bytes.fromhex("11" * 32),
        )

    assert called is False
    assert not output.exists()


def test_accepted_wrapper_deletes_candidate_if_source_changes_after_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    source.write_bytes(b"accepted fixture")
    expected = sha256_file(source)

    def build_then_mutate(*args: object, **kwargs: object) -> object:
        output.write_bytes(b"candidate")
        source.write_bytes(b"changed fixture")
        return SimpleNamespace(
            source_file_sha256_hex=expected.hex(),
            output_path=str(output),
        )

    monkeypatch.setattr(
        accepted_source,
        "run_raw_mirror_prototype",
        build_then_mutate,
    )

    with pytest.raises(RuntimeError, match="file SHA-256 mismatch"):
        accepted_source.run_accepted_raw_mirror_prototype(
            source,
            output,
            expected_source_sha256=expected,
        )

    assert not output.exists()


def test_accepted_wrapper_deletes_candidate_if_builder_records_wrong_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    source.write_bytes(b"accepted fixture")
    expected = sha256_file(source)

    def build_with_wrong_hash(*args: object, **kwargs: object) -> object:
        output.write_bytes(b"candidate")
        return SimpleNamespace(
            source_file_sha256_hex=(bytes.fromhex("22" * 32)).hex(),
            output_path=str(output),
        )

    monkeypatch.setattr(
        accepted_source,
        "run_raw_mirror_prototype",
        build_with_wrong_hash,
    )

    with pytest.raises(RuntimeError, match="recorded a source hash different"):
        accepted_source.run_accepted_raw_mirror_prototype(
            source,
            output,
            expected_source_sha256=expected,
        )

    assert not output.exists()


def test_accepted_wrapper_returns_candidate_when_identity_remains_exact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    source.write_bytes(b"accepted fixture")
    expected = sha256_file(source)
    summary = SimpleNamespace(
        source_file_sha256_hex=expected.hex(),
        output_path=str(output),
    )

    def successful_build(*args: object, **kwargs: object) -> object:
        output.write_bytes(b"candidate")
        return summary

    monkeypatch.setattr(
        accepted_source,
        "run_raw_mirror_prototype",
        successful_build,
    )

    observed = accepted_source.run_accepted_raw_mirror_prototype(
        source,
        output,
        expected_source_sha256=expected,
    )

    assert observed is summary
    assert output.read_bytes() == b"candidate"
