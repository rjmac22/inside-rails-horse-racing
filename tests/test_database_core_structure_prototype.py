from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

import inside_rails.database.core_structure_prototype as core_prototype
from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
    runner_participation_code,
    source_race_occurrence_code,
)
from inside_rails.database.raw_mirror_candidate import build_raw_mirror_candidate
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
)


FIXED_TIMESTAMP = "2026-08-06T10:30:00.000000Z"
FIXED_COMMIT = "a" * 40
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
    candidate = tmp_path / "raw_mirror.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)
    build_raw_mirror_candidate(
        source,
        candidate,
        baseline=FIXTURE_BASELINE,
        batch_size=2,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
    )
    return source, candidate, source_hash, sha256_file(candidate)


def test_core_prototype_persists_complete_first_races_and_runner_lineage(
    tmp_path: Path,
) -> None:
    source, candidate, source_hash, candidate_hash = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"

    summary = core_prototype.run_core_structure_prototype(
        source,
        candidate,
        output,
        repository_commit=FIXED_COMMIT,
        baseline=FIXTURE_BASELINE,
        race_count=3,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
        expected_candidate_sha256=candidate_hash,
    )

    assert summary.selected_race_count == 3
    assert summary.selected_minimum_source_rowids == (2, 4, 5)
    assert summary.copied_raw_record_count == 7
    assert summary.copied_admitted_record_count == 6
    assert summary.copied_excluded_record_count == 1
    assert summary.core_race_occurrence_count == 3
    assert summary.core_runner_participation_count == 6
    assert summary.candidate_output_value_comparisons == 7 * 37
    assert summary.candidate_output_storage_class_comparisons == 7 * 37
    assert summary.stored_fingerprint_comparisons == 7
    assert summary.recomputed_fingerprint_comparisons == 7
    assert summary.race_reconciliation_comparisons == 3
    assert summary.runner_reconciliation_comparisons == 6
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.source_hash_unchanged is True
    assert summary.raw_mirror_candidate_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.output_file_sha256_hex == sha256_file(output).hex()

    connection = sqlite3.connect(output)
    try:
        assert connection.execute(
            "SELECT source_rowid FROM source_raceform_v1_record ORDER BY source_rowid"
        ).fetchall() == [(1,), (2,), (3,), (4,), (5,), (6,), (7,)]
        assert connection.execute(
            """
            SELECT source_race_occurrence_id, source_race_occurrence_code,
                   raw_date, raw_course, raw_off, admitted_runner_count
            FROM core_source_race_occurrence
            ORDER BY source_race_occurrence_id
            """
        ).fetchall() == [
            (
                1,
                source_race_occurrence_code(source_hash, 1),
                "2026-01-01",
                "Ascot",
                "13:00",
                2,
            ),
            (
                2,
                source_race_occurrence_code(source_hash, 2),
                "2026-01-02",
                "Kempton",
                "14:00",
                1,
            ),
            (
                3,
                source_race_occurrence_code(source_hash, 3),
                "2026-01-03",
                "Newcastle",
                "15:00",
                3,
            ),
        ]
        runner_rows = connection.execute(
            """
            SELECT runner.runner_participation_id,
                   runner.runner_participation_code,
                   runner.source_race_occurrence_id,
                   raw.source_rowid
            FROM core_runner_participation AS runner
            JOIN source_raceform_v1_record AS raw
              ON raw.source_record_id = runner.source_record_id
            ORDER BY runner.runner_participation_id
            """
        ).fetchall()
        assert runner_rows == [
            (1, runner_participation_code(source_hash, 2), 1, 2),
            (2, runner_participation_code(source_hash, 3), 1, 3),
            (3, runner_participation_code(source_hash, 4), 2, 4),
            (4, runner_participation_code(source_hash, 5), 3, 5),
            (5, runner_participation_code(source_hash, 6), 3, 6),
            (6, runner_participation_code(source_hash, 7), 3, 7),
        ]
        assert connection.execute(
            "SELECT governance_method_code FROM governance_method"
        ).fetchone()[0] == governance_method_code("source-v1-structure", 1)
        assert connection.execute(
            "SELECT governance_release_code FROM governance_release"
        ).fetchone()[0] == governance_release_code(
            source_hash,
            "source-v1-structure",
            1,
        )
        assert connection.execute(
            "SELECT COUNT(*) FROM governance_release_evidence"
        ).fetchone()[0] == 4
        assert connection.execute("SELECT COUNT(*) FROM import_manifest").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM import_validation_result"
        ).fetchone()[0] == 0
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_wrong_candidate_hash_fails_before_output_creation(tmp_path: Path) -> None:
    source, candidate, source_hash, _ = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"

    with pytest.raises(RuntimeError, match="candidate SHA-256 mismatch"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=bytes.fromhex("11" * 32),
        )

    assert not output.exists()


def test_candidate_value_corruption_fails_closed(tmp_path: Path) -> None:
    source, candidate, source_hash, _ = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            'UPDATE source_raceform_v1_record SET "horse" = ? WHERE source_rowid = 2',
            ("Tampered Horse",),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="Candidate fingerprint mismatch"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=sha256_file(candidate),
        )

    assert not output.exists()


def test_incomplete_candidate_population_fails_closed(tmp_path: Path) -> None:
    source, candidate, source_hash, _ = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "DELETE FROM source_raceform_v1_record WHERE source_rowid = 3"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="candidate population mismatch"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=sha256_file(candidate),
        )

    assert not output.exists()


def test_existing_output_and_invalid_arguments_fail_without_overwrite(
    tmp_path: Path,
) -> None:
    source, candidate, source_hash, candidate_hash = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"
    output.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="artifact already exists"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=candidate_hash,
        )
    assert output.read_bytes() == b"existing"

    output.unlink()
    with pytest.raises(ValueError, match="race_count must be a positive integer"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            race_count=0,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=candidate_hash,
        )
    with pytest.raises(ValueError, match="40 lowercase hexadecimal"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit="not-a-commit",
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=candidate_hash,
        )
    assert not output.exists()


def test_failed_persisted_validation_removes_database_and_sidecars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, candidate, source_hash, candidate_hash = build_fixture_candidate(tmp_path)
    output = tmp_path / "core_prototype.sqlite3"

    def fail_validation(*args: object, **kwargs: object) -> object:
        Path(f"{output}-journal").write_bytes(b"sidecar")
        raise RuntimeError("forced persisted validation failure")

    monkeypatch.setattr(
        core_prototype,
        "_validate_output",
        fail_validation,
    )

    with pytest.raises(RuntimeError, match="forced persisted validation failure"):
        core_prototype.run_core_structure_prototype(
            source,
            candidate,
            output,
            repository_commit=FIXED_COMMIT,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
            expected_candidate_sha256=candidate_hash,
        )

    assert not output.exists()
    assert not Path(f"{output}-journal").exists()
    assert not Path(f"{output}-wal").exists()
    assert not Path(f"{output}-shm").exists()
