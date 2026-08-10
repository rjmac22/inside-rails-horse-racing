from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

import inside_rails.database.minimum_core_candidate as core_candidate
from inside_rails.database.raw_mirror_candidate import build_raw_mirror_candidate
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
)


FIXED_TIMESTAMP = "2026-08-06T11:33:00.000000Z"
FIXED_COMMIT = "a" * 40
FIXED_REFERENCE_COMMIT = "b" * 40
FIXED_IMPORT_SUFFIX = "11111111"
FIXED_DATABASE_SUFFIX = "22222222"
FIXTURE_BASELINE = SourceBaseline(
    physical_record_count=8,
    admitted_record_count=7,
    excluded_record_count=1,
    minimum_source_date="2026-01-01",
    maximum_source_date="2026-01-04",
)


def raw_values(**overrides: object) -> list[object]:
    values = {name: "" for name in RAW_COLUMN_NAMES}
    values.update(overrides)
    return [values[name] for name in RAW_COLUMN_NAMES]


def create_source_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        definitions = ", ".join(
            f'"{field.field_name}" {field.declared_type}'
            for field in RACEFORM_V1_FIELDS
        )
        connection.execute(f"CREATE TABLE data ({definitions})")
        placeholders = ", ".join("?" for _ in RAW_COLUMN_NAMES)
        rows = [
            list(RAW_COLUMN_NAMES),
            raw_values(
                date="2026-01-01",
                course="Ascot",
                off="13:00",
                race_id=901,
                horse="Horse One",
                num=1,
                prize="",
                ovr_btn=0.5,
            ),
            raw_values(
                date="2026-01-01",
                course="Ascot",
                off="13:00",
                race_id=901,
                horse="Horse Two",
                num=2,
                prize=100,
                ovr_btn=1,
            ),
            raw_values(
                date="2026-01-02",
                course="Kempton",
                off="14:00",
                race_id=902,
                horse="Horse Three",
                num="",
                prize=12.5,
                ovr_btn=2.25,
            ),
            raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Four",
                num=1,
                prize="€12.50",
                ovr_btn=3,
            ),
            raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Five",
                num=2,
                prize=0,
                ovr_btn="",
            ),
            raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Six",
                num=3,
                prize=1.75,
                ovr_btn=4.5,
            ),
            raw_values(
                date="2026-01-04",
                course="York",
                off="16:00",
                race_id=904,
                horse="Horse Seven",
                num=1,
                prize=250,
                ovr_btn=0,
            ),
        ]
        connection.executemany(f"INSERT INTO data VALUES ({placeholders})", rows)
        connection.commit()
    finally:
        connection.close()


def build_fixture_candidate(tmp_path: Path) -> tuple[Path, Path, bytes, bytes]:
    source = tmp_path / "raceform.db"
    raw_candidate = tmp_path / "raw_mirror.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)
    build_raw_mirror_candidate(
        source,
        raw_candidate,
        baseline=FIXTURE_BASELINE,
        batch_size=2,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
    )
    return source, raw_candidate, source_hash, sha256_file(raw_candidate)


def build_fixture_core(tmp_path: Path) -> tuple[Path, Path, Path, object]:
    source, raw_candidate, source_hash, raw_candidate_hash = build_fixture_candidate(
        tmp_path
    )
    output = tmp_path / "minimum_core.sqlite3"
    summary = core_candidate.build_minimum_core_candidate(
        source,
        raw_candidate,
        output,
        repository_commit=FIXED_COMMIT,
        reference_data_commit=FIXED_REFERENCE_COMMIT,
        build_command="python scripts/build_minimum_core_candidate.py",
        batch_size=2,
        baseline=FIXTURE_BASELINE,
        expected_race_count=4,
        created_at_utc=FIXED_TIMESTAMP,
        import_suffix=FIXED_IMPORT_SUFFIX,
        database_suffix=FIXED_DATABASE_SUFFIX,
        expected_source_sha256=source_hash,
        expected_candidate_sha256=raw_candidate_hash,
    )
    return source, raw_candidate, output, summary


def test_complete_candidate_builds_all_races_runners_and_manifest(
    tmp_path: Path,
) -> None:
    source, raw_candidate, output, summary = build_fixture_core(tmp_path)

    assert summary.physical_record_count == 8
    assert summary.admitted_record_count == 7
    assert summary.excluded_record_count == 1
    assert summary.race_occurrence_count == 4
    assert summary.runner_participation_count == 7
    assert summary.race_batch_count == 2
    assert summary.runner_batch_count == 4
    assert summary.race_readback_comparisons == 4
    assert summary.runner_readback_comparisons == 7
    assert summary.manifest_code == "imp:20260806T113300000000Z:11111111"
    assert summary.database_release_code == "db:20260806T113300000000Z:22222222"
    assert summary.manifest_status == "built"
    assert summary.validation_result_count == 4
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.source_hash_unchanged is True
    assert summary.raw_mirror_candidate_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.release_accepted is False
    assert output.exists()
    assert sha256_file(source).hex() == summary.source_file_sha256_hex
    assert sha256_file(raw_candidate).hex() == summary.raw_mirror_candidate_sha256_hex
    assert sha256_file(output).hex() == summary.output_file_sha256_hex

    connection = sqlite3.connect(output)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM source_raceform_v1_record"
        ).fetchone()[0] == 8
        assert connection.execute(
            "SELECT COUNT(*) FROM core_source_race_occurrence"
        ).fetchone()[0] == 4
        assert connection.execute(
            "SELECT COUNT(*) FROM core_runner_participation"
        ).fetchone()[0] == 7
        assert connection.execute(
            """
            SELECT source_race_occurrence_id, raw_date, raw_course, raw_off,
                   admitted_runner_count
            FROM core_source_race_occurrence
            ORDER BY source_race_occurrence_id
            """
        ).fetchall() == [
            (1, "2026-01-01", "Ascot", "13:00", 2),
            (2, "2026-01-02", "Kempton", "14:00", 1),
            (3, "2026-01-03", "Newcastle", "15:00", 3),
            (4, "2026-01-04", "York", "16:00", 1),
        ]
        manifest = connection.execute(
            """
            SELECT code_commit, reference_data_commit, build_status,
                   persisted_readback_passed, sqlite_integrity_passed,
                   foreign_key_check_passed, post_load_validation_passed,
                   prior_release_preserved, failure_reason
            FROM import_manifest
            """
        ).fetchone()
        assert manifest == (
            FIXED_COMMIT,
            FIXED_REFERENCE_COMMIT,
            "built",
            1,
            1,
            1,
            1,
            1,
            None,
        )
        assert connection.execute(
            """
            SELECT validation_stage, outcome
            FROM import_validation_result
            ORDER BY import_validation_result_id
            """
        ).fetchall() == [
            ("persisted_readback", "passed"),
            ("sqlite_integrity", "passed"),
            ("foreign_key_validation", "passed"),
            ("post_load_validation", "passed"),
        ]
        assert connection.execute(
            "SELECT COUNT(*) FROM import_manifest WHERE build_status = 'release_accepted'"
        ).fetchone()[0] == 0
        # Multiple fail-closed triggers can reject this invalid jump; SQLite does not
        # promise which applicable BEFORE trigger reports first.
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE import_manifest SET build_status = 'release_accepted'"
            )
        connection.rollback()
        assert connection.execute(
            "SELECT build_status FROM import_manifest"
        ).fetchone()[0] == "built"
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_wrong_raw_candidate_hash_fails_before_output_creation(tmp_path: Path) -> None:
    source, raw_candidate, source_hash, _ = build_fixture_candidate(tmp_path)
    output = tmp_path / "minimum_core.sqlite3"

    with pytest.raises(RuntimeError, match="candidate SHA-256 mismatch"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=bytes.fromhex("11" * 32),
        )

    assert not output.exists()


def test_incomplete_raw_candidate_fails_closed_and_removes_copy(tmp_path: Path) -> None:
    source, raw_candidate, source_hash, _ = build_fixture_candidate(tmp_path)
    output = tmp_path / "minimum_core.sqlite3"
    connection = sqlite3.connect(raw_candidate)
    try:
        connection.execute(
            "DELETE FROM source_raceform_v1_record WHERE source_rowid = 8"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="Raw-mirror population mismatch"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=sha256_file(raw_candidate),
        )

    assert not output.exists()


def test_existing_output_is_not_overwritten(tmp_path: Path) -> None:
    source, raw_candidate, source_hash, raw_candidate_hash = build_fixture_candidate(
        tmp_path
    )
    output = tmp_path / "minimum_core.sqlite3"
    output.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="artifact already exists"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=raw_candidate_hash,
        )

    assert output.read_bytes() == b"existing"


def test_invalid_arguments_fail_before_output_creation(tmp_path: Path) -> None:
    source, raw_candidate, source_hash, raw_candidate_hash = build_fixture_candidate(
        tmp_path
    )
    output = tmp_path / "minimum_core.sqlite3"

    with pytest.raises(ValueError, match="batch_size must be a positive integer"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            batch_size=0,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=raw_candidate_hash,
        )
    with pytest.raises(ValueError, match="40 lowercase hexadecimal"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit="not-a-commit",
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=raw_candidate_hash,
        )
    with pytest.raises(ValueError, match="8 lowercase hexadecimal"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            import_suffix="ABC",
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=raw_candidate_hash,
        )

    assert not output.exists()


def test_failed_readback_removes_database_and_sidecars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, raw_candidate, source_hash, raw_candidate_hash = build_fixture_candidate(
        tmp_path
    )
    output = tmp_path / "minimum_core.sqlite3"

    def fail_readback(*args: object, **kwargs: object) -> object:
        Path(f"{output}-journal").write_bytes(b"sidecar")
        raise RuntimeError("forced minimum-core readback failure")

    monkeypatch.setattr(core_candidate, "_readback_core", fail_readback)

    with pytest.raises(RuntimeError, match="forced minimum-core readback failure"):
        core_candidate.build_minimum_core_candidate(
            source,
            raw_candidate,
            output,
            repository_commit=FIXED_COMMIT,
            reference_data_commit=FIXED_REFERENCE_COMMIT,
            batch_size=2,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            created_at_utc=FIXED_TIMESTAMP,
            import_suffix=FIXED_IMPORT_SUFFIX,
            database_suffix=FIXED_DATABASE_SUFFIX,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=raw_candidate_hash,
        )

    assert not output.exists()
    assert not Path(f"{output}-journal").exists()
    assert not Path(f"{output}-wal").exists()
    assert not Path(f"{output}-shm").exists()
