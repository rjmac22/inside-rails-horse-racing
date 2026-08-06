from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from inside_rails.database.raw_mirror_candidate import build_raw_mirror_candidate
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
)
from inside_rails.database.raw_mirror_validator import validate_raw_mirror_candidate


FIXED_TIMESTAMP = "2026-08-06T10:00:00.000000Z"
FIXTURE_BASELINE = SourceBaseline(
    physical_record_count=7,
    admitted_record_count=6,
    excluded_record_count=1,
    minimum_source_date="2026-01-01",
    maximum_source_date="2026-01-06",
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
                race_id=901,
                off="13:00",
                num=1,
                prize="",
                ovr_btn=0.5,
                horse="Horse One",
            ),
            raw_values(
                date="2026-01-02",
                course="Ascot",
                race_id=902,
                off="13:30",
                num="",
                prize=100,
                ovr_btn=1,
                horse="Horse Two",
            ),
            raw_values(
                date="2026-01-03",
                course="Ascot",
                race_id=903,
                off="14:00",
                num=2,
                prize=12.5,
                ovr_btn=2.25,
                horse="Horse Three",
            ),
            raw_values(
                date="2026-01-04",
                course="Ascot",
                race_id=904,
                off="14:30",
                num=3,
                prize="€12.50",
                ovr_btn=3,
                horse="Horse Four",
            ),
            raw_values(
                date="2026-01-05",
                course="Ascot",
                race_id=905,
                off="15:00",
                num=4,
                prize=0,
                ovr_btn="",
                horse="Horse Five",
            ),
            raw_values(
                date="2026-01-06",
                course="Ascot",
                race_id=906,
                off="15:30",
                num=5,
                prize=1.75,
                ovr_btn=4.5,
                horse="Horse Six",
            ),
        ]
        connection.executemany(f"INSERT INTO data VALUES ({placeholders})", rows)
        connection.commit()
    finally:
        connection.close()


def build_fixture(tmp_path: Path) -> tuple[Path, Path, bytes]:
    source = tmp_path / "raceform.db"
    candidate = tmp_path / "candidate.sqlite3"
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
    return source, candidate, source_hash


def validate_fixture(
    source: Path,
    candidate: Path,
    source_hash: bytes,
    *,
    batch_size: int = 3,
):
    return validate_raw_mirror_candidate(
        source,
        candidate,
        baseline=FIXTURE_BASELINE,
        batch_size=batch_size,
        expected_source_sha256=source_hash,
    )


def test_independent_validator_reconciles_every_persisted_value_and_type(
    tmp_path: Path,
) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)
    source_hash_before = sha256_file(source)
    candidate_hash_before = sha256_file(candidate)

    summary = validate_fixture(source, candidate, source_hash)

    assert summary.compared_record_count == 7
    assert summary.raw_value_comparisons == 7 * 37
    assert summary.storage_class_comparisons == 7 * 37
    assert summary.source_record_code_comparisons == 7
    assert summary.structural_status_comparisons == 7
    assert summary.stored_fingerprint_comparisons == 7
    assert summary.recomputed_fingerprint_comparisons == 7
    assert summary.batch_size == 3
    assert summary.batch_count == 3
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.schema_inventory_matched is True
    assert summary.metadata_reconciliation_passed is True
    assert summary.raw_population_reconciliation_passed is True
    assert summary.source_hash_unchanged is True
    assert summary.candidate_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.validation_elapsed_seconds > 0
    assert summary.rows_per_second > 0
    assert summary.source_file_sha256_hex == source_hash.hex()
    assert summary.candidate_file_sha256_hex == candidate_hash_before.hex()
    assert sha256_file(source) == source_hash_before
    assert sha256_file(candidate) == candidate_hash_before


def test_validator_rejects_tampered_raw_value(tmp_path: Path) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            """
            UPDATE source_raceform_v1_record
            SET "horse" = 'Tampered Horse'
            WHERE source_rowid = 2
            """
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="Raw value mismatch"):
        validate_fixture(source, candidate, source_hash)


def test_validator_rejects_tampered_stored_fingerprint(tmp_path: Path) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            """
            UPDATE source_raceform_v1_record
            SET row_sha256 = ?
            WHERE source_rowid = 3
            """,
            (bytes.fromhex("00" * 32),),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="Stored row fingerprint mismatch"):
        validate_fixture(source, candidate, source_hash)


def test_validator_rejects_metadata_or_schema_drift(tmp_path: Path) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "UPDATE source_version SET original_filename = 'other.db'"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="Source-version metadata"):
        validate_fixture(source, candidate, source_hash)

    candidate.unlink()
    build_raw_mirror_candidate(
        source,
        candidate,
        baseline=FIXTURE_BASELINE,
        batch_size=2,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
    )
    connection = sqlite3.connect(candidate)
    try:
        connection.execute("CREATE TABLE unexpected_object (value TEXT)")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="schema inventory mismatch"):
        validate_fixture(source, candidate, source_hash)


def test_validator_rejects_incomplete_population(tmp_path: Path) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)
    connection = sqlite3.connect(candidate)
    try:
        connection.execute(
            "DELETE FROM source_raceform_v1_record WHERE source_rowid = 7"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="population mismatch"):
        validate_fixture(source, candidate, source_hash)


def test_validator_rejects_wrong_paths_batch_size_and_sidecars(
    tmp_path: Path,
) -> None:
    source, candidate, source_hash = build_fixture(tmp_path)

    with pytest.raises(ValueError, match="batch_size"):
        validate_fixture(source, candidate, source_hash, batch_size=0)

    with pytest.raises(ValueError, match="paths must differ"):
        validate_raw_mirror_candidate(
            source,
            source,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
        )

    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(FileNotFoundError, match="candidate not found"):
        validate_raw_mirror_candidate(
            source,
            missing,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
        )

    sidecar = Path(f"{candidate}-wal")
    sidecar.write_bytes(b"unexpected")
    with pytest.raises(RuntimeError, match="unexpected SQLite sidecars"):
        validate_fixture(source, candidate, source_hash)
