from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from inside_rails.database.core_structure_prototype import (
    run_core_structure_prototype,
)
from inside_rails.database.core_structure_validator import (
    validate_core_structure_prototype,
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


def _raw_values(**overrides: object) -> list[object]:
    values = {name: "" for name in RAW_COLUMN_NAMES}
    values.update(overrides)
    return [values[name] for name in RAW_COLUMN_NAMES]


def _create_source_database(path: Path) -> None:
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
            _raw_values(
                date="2026-01-01",
                course="Ascot",
                off="13:00",
                race_id=901,
                horse="Horse One",
                num=1,
                prize="",
                ovr_btn=0.5,
            ),
            _raw_values(
                date="2026-01-01",
                course="Ascot",
                off="13:00",
                race_id=901,
                horse="Horse Two",
                num=2,
                prize=100,
                ovr_btn=1,
            ),
            _raw_values(
                date="2026-01-02",
                course="Kempton",
                off="14:00",
                race_id=902,
                horse="Horse Three",
                num="",
                prize=12.5,
                ovr_btn=2.25,
            ),
            _raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Four",
                num=1,
                prize="€12.50",
                ovr_btn=3,
            ),
            _raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Five",
                num=2,
                prize=0,
                ovr_btn="",
            ),
            _raw_values(
                date="2026-01-03",
                course="Newcastle",
                off="15:00",
                race_id=903,
                horse="Horse Six",
                num=3,
                prize=1.75,
                ovr_btn=4.5,
            ),
            _raw_values(
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


def _build_fixture(tmp_path: Path) -> tuple[Path, Path, Path, bytes, bytes]:
    source = tmp_path / "raceform.db"
    candidate = tmp_path / "raw_mirror.sqlite3"
    prototype = tmp_path / "core_prototype.sqlite3"
    _create_source_database(source)
    source_hash = sha256_file(source)
    build_raw_mirror_candidate(
        source,
        candidate,
        baseline=FIXTURE_BASELINE,
        batch_size=2,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
    )
    candidate_hash = sha256_file(candidate)
    run_core_structure_prototype(
        source,
        candidate,
        prototype,
        repository_commit=FIXED_COMMIT,
        race_count=3,
        baseline=FIXTURE_BASELINE,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
        expected_candidate_sha256=candidate_hash,
    )
    return source, candidate, prototype, source_hash, candidate_hash


def _validate_fixture(
    source: Path,
    candidate: Path,
    prototype: Path,
    source_hash: bytes,
    candidate_hash: bytes,
):
    return validate_core_structure_prototype(
        source,
        candidate,
        prototype,
        race_count=3,
        baseline=FIXTURE_BASELINE,
        expected_source_sha256=source_hash,
        expected_candidate_sha256=candidate_hash,
    )


def test_independent_validator_reconciles_complete_prototype(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )

    summary = _validate_fixture(
        source,
        candidate,
        prototype,
        source_hash,
        candidate_hash,
    )

    assert summary.selected_race_count == 3
    assert summary.selected_minimum_source_rowids == (2, 4, 5)
    assert summary.compared_raw_record_count == 7
    assert summary.compared_admitted_record_count == 6
    assert summary.compared_excluded_record_count == 1
    assert summary.raw_value_comparisons == 7 * 37
    assert summary.storage_class_comparisons == 7 * 37
    assert summary.source_record_code_comparisons == 7
    assert summary.structural_status_comparisons == 7
    assert summary.stored_fingerprint_comparisons == 7
    assert summary.recomputed_fingerprint_comparisons == 7
    assert summary.race_code_comparisons == 3
    assert summary.race_grouping_comparisons == 3
    assert summary.race_runner_count_comparisons == 3
    assert summary.runner_code_comparisons == 6
    assert summary.runner_lineage_comparisons == 6
    assert summary.governance_reconciliation_passed is True
    assert summary.metadata_reconciliation_passed is True
    assert summary.schema_inventory_matched is True
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.source_hash_unchanged is True
    assert summary.raw_mirror_candidate_hash_unchanged is True
    assert summary.prototype_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.prototype_file_sha256_hex == sha256_file(prototype).hex()


def test_validator_rejects_prototype_raw_value_corruption(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )
    connection = sqlite3.connect(prototype)
    try:
        connection.execute(
            'UPDATE source_raceform_v1_record SET "horse" = ? WHERE source_rowid = 2',
            ("Tampered Horse",),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="raw value mismatch"):
        _validate_fixture(
            source,
            candidate,
            prototype,
            source_hash,
            candidate_hash,
        )


def test_validator_rejects_race_population_corruption(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )
    connection = sqlite3.connect(prototype)
    try:
        connection.execute(
            "UPDATE core_source_race_occurrence "
            "SET admitted_runner_count = admitted_runner_count + 1 "
            "WHERE source_race_occurrence_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="runner count mismatch"):
        _validate_fixture(
            source,
            candidate,
            prototype,
            source_hash,
            candidate_hash,
        )


def test_validator_rejects_governance_corruption(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )
    connection = sqlite3.connect(prototype)
    try:
        connection.execute(
            "UPDATE governance_release_evidence "
            "SET evidence_description = 'tampered' "
            "WHERE governance_release_evidence_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="governance evidence mismatch"):
        _validate_fixture(
            source,
            candidate,
            prototype,
            source_hash,
            candidate_hash,
        )


def test_validator_rejects_schema_inventory_violation(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )
    connection = sqlite3.connect(prototype)
    try:
        connection.execute("CREATE TABLE unauthorised_table (value INTEGER)")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="schema inventory mismatch"):
        _validate_fixture(
            source,
            candidate,
            prototype,
            source_hash,
            candidate_hash,
        )


def test_validator_rejects_prototype_sqlite_sidecar(tmp_path: Path) -> None:
    source, candidate, prototype, source_hash, candidate_hash = _build_fixture(
        tmp_path
    )
    sidecar = Path(f"{prototype}-wal")
    sidecar.write_bytes(b"unexpected")

    with pytest.raises(RuntimeError, match="unexpected SQLite sidecars"):
        _validate_fixture(
            source,
            candidate,
            prototype,
            source_hash,
            candidate_hash,
        )
