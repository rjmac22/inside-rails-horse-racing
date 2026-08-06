from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

import inside_rails.database.raw_mirror_candidate as raw_mirror_candidate
from inside_rails.database.identifiers import source_record_code
from inside_rails.database.raw_mirror_candidate import build_raw_mirror_candidate
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
)


FIXED_TIMESTAMP = "2026-08-06T09:00:00.000000Z"
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


def source_rows(path: Path) -> list[tuple[object, ...]]:
    columns = ", ".join(f'"{name}"' for name in RAW_COLUMN_NAMES)
    connection = sqlite3.connect(path)
    try:
        return connection.execute(
            f'SELECT rowid, {columns} FROM "data" ORDER BY rowid'
        ).fetchall()
    finally:
        connection.close()


def test_full_candidate_copies_every_row_in_batches_and_persists_exact_values(
    tmp_path: Path,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "candidate.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)

    summary = build_raw_mirror_candidate(
        source,
        output,
        baseline=FIXTURE_BASELINE,
        batch_size=2,
        created_at_utc=FIXED_TIMESTAMP,
        expected_source_sha256=source_hash,
    )

    assert summary.copied_record_count == 7
    assert summary.copied_admitted_record_count == 6
    assert summary.copied_excluded_record_count == 1
    assert summary.row_fingerprint_count == 7
    assert summary.batch_size == 2
    assert summary.batch_count == 4
    assert summary.quick_check == "ok"
    assert summary.foreign_key_check_rows == 0
    assert summary.source_hash_unchanged is True
    assert summary.persisted_readback_passed is True
    assert summary.output_file_size_bytes == output.stat().st_size
    assert summary.output_file_size_bytes > 0
    assert summary.build_elapsed_seconds > 0
    assert summary.rows_per_second > 0
    assert sha256_file(source) == source_hash

    expected_rows = source_rows(source)
    raw_columns = ", ".join(f'"{name}"' for name in RAW_COLUMN_NAMES)
    type_columns = ", ".join(f'typeof("{name}")' for name in RAW_COLUMN_NAMES)
    connection = sqlite3.connect(output)
    try:
        observed_rows = connection.execute(
            f"""
            SELECT source_record_id, source_rowid, source_record_code,
                   structural_status, exclusion_reason, length(row_sha256),
                   {raw_columns}, {type_columns}
            FROM source_raceform_v1_record
            ORDER BY source_record_id
            """
        ).fetchall()
        assert len(observed_rows) == len(expected_rows)
        for source_record_id, (source_row, target_row) in enumerate(
            zip(expected_rows, observed_rows, strict=True),
            start=1,
        ):
            source_rowid = int(source_row[0])
            source_values = tuple(source_row[1:])
            target_values = tuple(target_row[6 : 6 + len(RAW_COLUMN_NAMES)])
            target_types = tuple(target_row[6 + len(RAW_COLUMN_NAMES) :])
            assert target_row[0] == source_record_id
            assert target_row[1] == source_rowid
            assert target_row[2] == source_record_code(source_hash, source_rowid)
            assert target_row[3] == (
                "retained_excluded_record"
                if source_rowid == 1
                else "admitted_runner_record"
            )
            assert bool(target_row[4]) is (source_rowid == 1)
            assert target_row[5] == 32
            assert target_values == source_values
            assert target_types == tuple(
                "integer"
                if isinstance(value, int)
                else "real"
                if isinstance(value, float)
                else "text"
                for value in source_values
            )

        assert connection.execute(
            "SELECT COUNT(*) FROM source_relation_field"
        ).fetchone()[0] == 37
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_wrong_source_identity_and_existing_output_fail_before_build(
    tmp_path: Path,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "candidate.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)

    with pytest.raises(RuntimeError, match="file SHA-256 mismatch"):
        build_raw_mirror_candidate(
            source,
            output,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=bytes.fromhex("00" * 32),
        )
    assert not output.exists()

    output.write_bytes(b"existing candidate")
    with pytest.raises(FileExistsError, match="already exists"):
        build_raw_mirror_candidate(
            source,
            output,
            baseline=FIXTURE_BASELINE,
            expected_source_sha256=source_hash,
        )
    assert output.read_bytes() == b"existing candidate"


def test_mid_build_failure_removes_database_and_sidecars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "candidate.sqlite3"
    create_source_database(source)
    source_hash = sha256_file(source)
    real_fingerprint = raw_mirror_candidate.raceform_v1_row_sha256
    calls = 0

    def fail_on_fourth(values: tuple[object, ...]) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 4:
            raise RuntimeError("controlled fingerprint failure")
        return real_fingerprint(values)

    monkeypatch.setattr(
        raw_mirror_candidate,
        "raceform_v1_row_sha256",
        fail_on_fourth,
    )

    with pytest.raises(RuntimeError, match="controlled fingerprint failure"):
        build_raw_mirror_candidate(
            source,
            output,
            baseline=FIXTURE_BASELINE,
            batch_size=2,
            expected_source_sha256=source_hash,
        )

    assert not output.exists()
    assert not Path(f"{output}-journal").exists()
    assert not Path(f"{output}-wal").exists()
    assert not Path(f"{output}-shm").exists()
    assert sha256_file(source) == source_hash


@pytest.mark.parametrize("batch_size", [0, -1, True, 1.5])
def test_invalid_batch_size_fails_before_candidate_creation(
    tmp_path: Path,
    batch_size: object,
) -> None:
    source = tmp_path / "raceform.db"
    output = tmp_path / "candidate.sqlite3"
    create_source_database(source)

    with pytest.raises(ValueError, match="positive integer"):
        build_raw_mirror_candidate(
            source,
            output,
            baseline=FIXTURE_BASELINE,
            batch_size=batch_size,  # type: ignore[arg-type]
            expected_source_sha256=sha256_file(source),
        )

    assert not output.exists()
