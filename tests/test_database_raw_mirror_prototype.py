from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from inside_rails.database.identifiers import source_record_code, source_version_code
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    run_raw_mirror_prototype,
    sha256_file,
    source_schema_sha256,
    validate_raceform_v1_schema,
)


FIXED_TIMESTAMP = "2026-08-06T00:00:00.000000Z"
FIXTURE_BASELINE = SourceBaseline(
    physical_record_count=5,
    admitted_record_count=4,
    excluded_record_count=1,
    minimum_source_date="2026-01-01",
    maximum_source_date="2026-01-04",
)


def raw_values(**overrides: object) -> list[object]:
    values = {name: "" for name in RAW_COLUMN_NAMES}
    values.update(overrides)
    return [values[name] for name in RAW_COLUMN_NAMES]


def create_source_database(
    path: Path,
    *,
    include_real_example: bool = True,
    date_declared_type: str = "NUMERIC",
) -> None:
    connection = sqlite3.connect(path)
    try:
        column_definitions = []
        for field in RACEFORM_V1_FIELDS:
            declared_type = (
                date_declared_type
                if field.field_name == "date"
                else field.declared_type
            )
            column_definitions.append(f'"{field.field_name}" {declared_type}')
        connection.execute(
            "CREATE TABLE data (" + ", ".join(column_definitions) + ")"
        )
        placeholders = ", ".join("?" for _ in RAW_COLUMN_NAMES)
        connection.execute(
            f"INSERT INTO data VALUES ({placeholders})",
            list(RAW_COLUMN_NAMES),
        )
        connection.execute(
            f"INSERT INTO data VALUES ({placeholders})",
            raw_values(
                date="2026-01-01",
                course="Ascot",
                race_id=901,
                off="13:00",
                prize="",
                num=1,
                ovr_btn=0.5 if include_real_example else 1,
                horse="Horse One",
            ),
        )
        connection.execute(
            f"INSERT INTO data VALUES ({placeholders})",
            raw_values(
                date="2026-01-02",
                course="Ascot",
                race_id=902,
                off="13:30",
                prize=100,
                num="",
                ovr_btn=1,
                horse="Horse Two",
            ),
        )
        connection.execute(
            f"INSERT INTO data VALUES ({placeholders})",
            raw_values(
                date="2026-01-03",
                course="Ascot",
                race_id=903,
                off="14:00",
                prize=12.5,
                num=2,
                ovr_btn=2.25 if include_real_example else 2,
                horse="Horse Three",
            ),
        )
        connection.execute(
            f"INSERT INTO data VALUES ({placeholders})",
            raw_values(
                date="2026-01-04",
                course="Ascot",
                race_id=904,
                off="14:30",
                prize="€12.50",
                num=3,
                ovr_btn=3,
                horse="Horse Four",
            ),
        )
        connection.commit()
    finally:
        connection.close()


def test_source_backed_prototype_persists_exact_values_types_and_fingerprints(
    tmp_path: Path,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)

    summary = run_raw_mirror_prototype(
        source,
        output,
        baseline=FIXTURE_BASELINE,
        created_at_utc=FIXED_TIMESTAMP,
    )

    assert summary.selected_source_rowids == (1, 2, 3, 4, 5)
    assert summary.copied_record_count == 5
    assert summary.observed_storage_classes == ("integer", "real", "text")
    assert summary.value_comparisons == 5 * 37
    assert summary.typeof_comparisons == 5 * 37
    assert summary.fingerprint_comparisons == 5
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.source_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.source_file_sha256_hex == source_hash.hex()
    assert sha256_file(source) == source_hash

    connection = sqlite3.connect(output)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM source_relation_field"
        ).fetchone()[0] == 37
        assert connection.execute(
            "SELECT source_version_code FROM source_version"
        ).fetchone()[0] == source_version_code(source_hash)
        assert connection.execute(
            """
            SELECT source_rowid, source_record_code, structural_status,
                   typeof("prize"), typeof("num"), typeof("ovr_btn")
            FROM source_raceform_v1_record
            ORDER BY source_rowid
            """
        ).fetchall() == [
            (
                1,
                source_record_code(source_hash, 1),
                "retained_excluded_record",
                "text",
                "text",
                "text",
            ),
            (
                2,
                source_record_code(source_hash, 2),
                "admitted_runner_record",
                "text",
                "integer",
                "real",
            ),
            (
                3,
                source_record_code(source_hash, 3),
                "admitted_runner_record",
                "integer",
                "text",
                "integer",
            ),
            (
                4,
                source_record_code(source_hash, 4),
                "admitted_runner_record",
                "real",
                "integer",
                "real",
            ),
            (
                5,
                source_record_code(source_hash, 5),
                "admitted_runner_record",
                "text",
                "integer",
                "integer",
            ),
        ]
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_schema_validation_and_signature_are_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "raceform.db"
    create_source_database(source)

    connection = sqlite3.connect(source)
    try:
        first = validate_raceform_v1_schema(connection)
        second = validate_raceform_v1_schema(connection)
    finally:
        connection.close()

    assert first == second == RACEFORM_V1_FIELDS
    assert source_schema_sha256(first) == source_schema_sha256(second)
    assert len(source_schema_sha256(first)) == 32


def test_schema_mismatch_fails_before_candidate_creation(tmp_path: Path) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    create_source_database(source, date_declared_type="TEXT")

    with pytest.raises(RuntimeError, match="schema mismatch at ordinal 0"):
        run_raw_mirror_prototype(source, output, baseline=FIXTURE_BASELINE)

    assert not output.exists()


def test_missing_required_observed_storage_class_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    create_source_database(source, include_real_example=False)

    with pytest.raises(RuntimeError, match="ovr_btn REAL"):
        run_raw_mirror_prototype(source, output, baseline=FIXTURE_BASELINE)

    assert not output.exists()


def test_baseline_mismatch_and_existing_output_do_not_create_partial_success(
    tmp_path: Path,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "prototype.sqlite3"
    create_source_database(source)
    wrong_baseline = SourceBaseline(
        physical_record_count=6,
        admitted_record_count=5,
        excluded_record_count=1,
        minimum_source_date="2026-01-01",
        maximum_source_date="2026-01-04",
    )

    with pytest.raises(RuntimeError, match="baseline mismatch"):
        run_raw_mirror_prototype(source, output, baseline=wrong_baseline)
    assert not output.exists()

    output.write_bytes(b"existing prototype")
    with pytest.raises(FileExistsError, match="already exists"):
        run_raw_mirror_prototype(source, output, baseline=FIXTURE_BASELINE)
    assert output.read_bytes() == b"existing prototype"
