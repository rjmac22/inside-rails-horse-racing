from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from inside_rails.database.minimum_core_candidate import (
    build_minimum_core_candidate,
)
from inside_rails.database.minimum_core_validator import (
    validate_minimum_core_candidate,
)
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


def build_fixture(tmp_path: Path) -> tuple[Path, Path, Path, bytes, bytes, bytes]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "raceform.db"
    raw_candidate = tmp_path / "raw_mirror.sqlite3"
    candidate = tmp_path / "minimum_core.sqlite3"
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
    raw_hash = sha256_file(raw_candidate)
    build_minimum_core_candidate(
        source,
        raw_candidate,
        candidate,
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
        expected_candidate_sha256=raw_hash,
    )
    return (
        source,
        raw_candidate,
        candidate,
        source_hash,
        raw_hash,
        sha256_file(candidate),
    )


def validate_fixture(
    source: Path,
    raw_candidate: Path,
    candidate: Path,
    source_hash: bytes,
    raw_hash: bytes,
) -> object:
    return validate_minimum_core_candidate(
        source,
        raw_candidate,
        candidate,
        baseline=FIXTURE_BASELINE,
        expected_race_count=4,
        batch_size=2,
        expected_source_sha256=source_hash,
        expected_raw_mirror_sha256=raw_hash,
        expected_candidate_sha256=sha256_file(candidate),
    )


def test_independent_validator_reconciles_complete_candidate(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, candidate_hash = (
        build_fixture(tmp_path)
    )

    summary = validate_minimum_core_candidate(
        source,
        raw_candidate,
        candidate,
        baseline=FIXTURE_BASELINE,
        expected_race_count=4,
        batch_size=2,
        expected_source_sha256=source_hash,
        expected_raw_mirror_sha256=raw_hash,
        expected_candidate_sha256=candidate_hash,
    )

    assert summary.metadata_row_comparisons == 41
    assert summary.raw_record_comparisons == 8
    assert summary.raw_value_comparisons == 8 * 37
    assert summary.storage_class_comparisons == 8 * 37
    assert summary.source_record_code_comparisons == 8
    assert summary.structural_status_comparisons == 8
    assert summary.stored_fingerprint_comparisons == 8
    assert summary.recomputed_fingerprint_comparisons == 8
    assert summary.race_grouping_comparisons == 4
    assert summary.race_code_comparisons == 4
    assert summary.race_runner_count_comparisons == 4
    assert summary.runner_lineage_comparisons == 7
    assert summary.runner_code_comparisons == 7
    assert summary.manifest_validation_result_count == 4
    assert summary.batch_count == 4
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.schema_inventory_matched is True
    assert summary.metadata_reconciliation_passed is True
    assert summary.governance_reconciliation_passed is True
    assert summary.manifest_reconciliation_passed is True
    assert summary.source_hash_unchanged is True
    assert summary.raw_mirror_candidate_hash_unchanged is True
    assert summary.candidate_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.release_accepted is False


def test_raw_value_corruption_is_detected(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, _ = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            'UPDATE source_raceform_v1_record SET "horse" = ? WHERE source_rowid = 2',
            ("Tampered Horse",),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="raw value mismatch"):
        validate_fixture(source, raw_candidate, candidate, source_hash, raw_hash)


def test_race_code_corruption_is_detected(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, _ = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "UPDATE core_source_race_occurrence "
            "SET source_race_occurrence_code = 'race:tampered:000000001' "
            "WHERE source_race_occurrence_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="race code mismatch"):
        validate_fixture(source, raw_candidate, candidate, source_hash, raw_hash)


def test_runner_code_corruption_is_detected(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, _ = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "UPDATE core_runner_participation "
            "SET runner_participation_code = 'run:tampered:data:0000000002' "
            "WHERE runner_participation_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="runner code mismatch"):
        validate_fixture(source, raw_candidate, candidate, source_hash, raw_hash)


def test_manifest_corruption_is_detected(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, _ = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "UPDATE import_manifest SET build_command = 'tampered command'"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="final import manifest mismatch"):
        validate_fixture(source, raw_candidate, candidate, source_hash, raw_hash)


def test_schema_extension_and_sidecar_fail_closed(tmp_path: Path) -> None:
    source, raw_candidate, candidate, source_hash, raw_hash, _ = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute("CREATE TABLE unauthorised_extension (value INTEGER)")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="schema inventory mismatch"):
        validate_fixture(source, raw_candidate, candidate, source_hash, raw_hash)

    (
        source,
        raw_candidate,
        candidate,
        source_hash,
        raw_hash,
        candidate_hash,
    ) = build_fixture(tmp_path / "sidecar")
    sidecar = Path(f"{candidate}-wal")
    sidecar.write_bytes(b"unexpected")

    with pytest.raises(RuntimeError, match="unexpected SQLite sidecars"):
        validate_minimum_core_candidate(
            source,
            raw_candidate,
            candidate,
            baseline=FIXTURE_BASELINE,
            expected_race_count=4,
            batch_size=2,
            expected_source_sha256=source_hash,
            expected_raw_mirror_sha256=raw_hash,
            expected_candidate_sha256=candidate_hash,
        )
