"""Source-wide disposable raw mirror for accepted Source Version 1."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from time import perf_counter

from inside_rails.database.accepted_source import (
    RACEFORM_V1_FILE_SHA256,
    validate_source_version_1_file_identity,
)
from inside_rails.database.fingerprints import raceform_v1_row_sha256
from inside_rails.database.identifiers import (
    source_record_code,
    source_relation_code,
    source_version_code,
)
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_BASELINE,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    SourceField,
    source_schema_sha256,
    validate_raceform_v1_schema,
)
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
    create_minimum_core_schema,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier


@dataclass(frozen=True)
class RawMirrorCandidateSummary:
    source_path: str
    output_path: str
    source_file_sha256_hex: str
    source_schema_sha256_hex: str
    source_file_size_bytes: int
    output_file_size_bytes: int
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    copied_record_count: int
    copied_admitted_record_count: int
    copied_excluded_record_count: int
    row_fingerprint_count: int
    batch_size: int
    batch_count: int
    build_elapsed_seconds: float
    rows_per_second: float
    quick_check: str
    foreign_key_check_rows: int
    application_id: int
    user_version: int
    source_hash_unchanged: bool
    persisted_structural_checks_passed: bool


def _validate_batch_size(batch_size: int) -> int:
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    return batch_size


def _profile_and_validate_baseline(
    connection: sqlite3.Connection,
    baseline: SourceBaseline,
) -> None:
    row = connection.execute(
        """
        SELECT
            COUNT(*),
            SUM(CASE WHEN rowid <> 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rowid = 1 THEN 1 ELSE 0 END),
            MIN(CASE WHEN rowid <> 1 THEN "date" END),
            MAX(CASE WHEN rowid <> 1 THEN "date" END)
        FROM "data"
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("Unable to profile Source Version 1 data relation")

    observed = SourceBaseline(
        physical_record_count=int(row[0]),
        admitted_record_count=int(row[1]),
        excluded_record_count=int(row[2]),
        minimum_source_date=str(row[3]),
        maximum_source_date=str(row[4]),
    )
    if observed != baseline:
        raise RuntimeError(f"Source Version 1 baseline mismatch: {observed!r}")

    quick_check = connection.execute("PRAGMA quick_check").fetchone()
    if quick_check is None or quick_check[0] != "ok":
        raise RuntimeError(f"Source SQLite quick_check failed: {quick_check!r}")


def _insert_source_metadata(
    connection: sqlite3.Connection,
    *,
    source_file_sha256: bytes,
    source_file_size_bytes: int,
    schema_sha256: bytes,
    fields: Sequence[SourceField],
    baseline: SourceBaseline,
    created_at_utc: str,
) -> None:
    connection.execute(
        "INSERT INTO source_provider VALUES (?, ?, ?, ?, ?)",
        (
            1,
            "provider:community-source",
            "Community source",
            "Publisher, compiler and original racing-authority roles remain unresolved.",
            created_at_utc,
        ),
    )
    connection.execute(
        "INSERT INTO source_product VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            "product:raceform-community-database",
            1,
            "Raceform community database",
            "Exact Source Version 1 product family used by the project.",
            "Private research candidate; no bulk redistribution.",
            created_at_utc,
        ),
    )
    connection.execute(
        """
        INSERT INTO source_version VALUES (
            ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            1,
            source_version_code(source_file_sha256),
            1,
            "raceform.db",
            "Complete disposable raw-mirror candidate of the accepted immutable file.",
            source_file_sha256,
            source_file_size_bytes,
            schema_sha256,
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
            "rowid <> 1",
            baseline.minimum_source_date,
            baseline.maximum_source_date,
            "ok",
            "accepted_exact_source",
            "All physical Source Version 1 rows are mirrored; this is not an accepted release.",
            created_at_utc,
        ),
    )
    connection.execute(
        "INSERT INTO source_relation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            source_relation_code(source_file_sha256),
            1,
            "data",
            schema_sha256,
            len(fields),
            baseline.physical_record_count,
            baseline.admitted_record_count,
            "rowid <> 1",
        ),
    )
    connection.executemany(
        """
        INSERT INTO source_relation_field VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                index,
                1,
                field.ordinal_position,
                field.field_name,
                field.declared_type,
                field.source_not_null,
                field.source_default_sql,
                field.source_primary_key_ordinal,
            )
            for index, field in enumerate(fields, start=1)
        ],
    )


def _raw_insert_sql() -> str:
    metadata_names = (
        "source_record_id",
        "source_record_code",
        "source_version_id",
        "source_relation_id",
        "source_rowid",
        "structural_status",
        "exclusion_reason",
        "row_sha256",
    )
    names = [*metadata_names, *RAW_COLUMN_NAMES]
    columns = ", ".join(quote_identifier(name) for name in names)
    placeholders = ", ".join("?" for _ in names)
    return f"INSERT INTO source_raceform_v1_record ({columns}) VALUES ({placeholders})"


def _candidate_insert_row(
    *,
    source_record_id: int,
    source_rowid: int,
    values: tuple[object, ...],
    source_file_sha256: bytes,
) -> tuple[object, ...]:
    excluded = source_rowid == 1
    return (
        source_record_id,
        source_record_code(source_file_sha256, source_rowid),
        1,
        1,
        source_rowid,
        "retained_excluded_record" if excluded else "admitted_runner_record",
        "Retained Source Version 1 rowid 1 exclusion." if excluded else None,
        raceform_v1_row_sha256(values),
        *values,
    )


def _candidate_artifact_paths(output: Path) -> tuple[Path, ...]:
    return (
        output,
        Path(f"{output}-journal"),
        Path(f"{output}-wal"),
        Path(f"{output}-shm"),
    )


def _remove_candidate_files(output: Path) -> None:
    for path in _candidate_artifact_paths(output):
        path.unlink(missing_ok=True)


def _validate_persisted_candidate(
    output: Path,
    baseline: SourceBaseline,
) -> tuple[int, int, int, str, int, int, int]:
    with connect_read_only(output) as connection:
        configure_governed_connection(connection, query_only=True)
        row = connection.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN structural_status = 'admitted_runner_record' THEN 1 ELSE 0 END),
                SUM(CASE WHEN structural_status = 'retained_excluded_record' THEN 1 ELSE 0 END)
            FROM source_raceform_v1_record
            """
        ).fetchone()
        if row is None:
            raise RuntimeError("Unable to read persisted raw-mirror counts")

        copied = int(row[0])
        admitted = int(row[1])
        excluded = int(row[2])
        expected = (
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
        )
        if (copied, admitted, excluded) != expected:
            raise RuntimeError(
                "Persisted raw-mirror count mismatch: "
                f"expected {expected!r}; observed {(copied, admitted, excluded)!r}"
            )

        relation_fields = int(
            connection.execute("SELECT COUNT(*) FROM source_relation_field").fetchone()[0]
        )
        if relation_fields != len(RAW_COLUMN_NAMES):
            raise RuntimeError(
                "Persisted source-field count mismatch: "
                f"expected {len(RAW_COLUMN_NAMES)}; observed {relation_fields}"
            )

        quick_check_row = connection.execute("PRAGMA quick_check").fetchone()
        quick_check = "" if quick_check_row is None else str(quick_check_row[0])
        if quick_check != "ok":
            raise RuntimeError(f"Raw-mirror candidate quick_check failed: {quick_check!r}")

        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Raw-mirror candidate foreign_key_check returned {foreign_key_rows} rows"
            )

        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID:
            raise RuntimeError(f"Unexpected candidate application_id: {application_id}")
        if user_version != SCHEMA_VERSION:
            raise RuntimeError(f"Unexpected candidate user_version: {user_version}")

    return (
        copied,
        admitted,
        excluded,
        quick_check,
        foreign_key_rows,
        application_id,
        user_version,
    )


def build_raw_mirror_candidate(
    source_path: str | Path,
    output_path: str | Path,
    *,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    batch_size: int = 1_000,
    created_at_utc: str | None = None,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
) -> RawMirrorCandidateSummary:
    """Build all physical source rows into a disposable governed candidate."""

    batch_size = _validate_batch_size(batch_size)
    source = Path(source_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if source == output:
        raise ValueError("Source and raw-mirror candidate paths must differ")
    existing_artifacts = [
        path for path in _candidate_artifact_paths(output) if path.exists()
    ]
    if existing_artifacts:
        raise FileExistsError(
            "Raw-mirror candidate artifact already exists: "
            + ", ".join(str(path) for path in existing_artifacts)
        )

    started = perf_counter()
    timestamp = created_at_utc or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    source_hash_before = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    source_file_size_bytes = source.stat().st_size

    with connect_read_only(source) as source_connection:
        fields = validate_raceform_v1_schema(source_connection)
        _profile_and_validate_baseline(source_connection, baseline)
        schema_digest = source_schema_sha256(fields)

        quoted_columns = ", ".join(quote_identifier(name) for name in RAW_COLUMN_NAMES)
        source_cursor = source_connection.execute(
            f'SELECT rowid, {quoted_columns} FROM "data" ORDER BY rowid'
        )

        output.parent.mkdir(parents=True, exist_ok=True)
        copied_count = 0
        admitted_count = 0
        excluded_count = 0
        fingerprint_count = 0
        batch_count = 0
        previous_rowid = 0

        try:
            destination = sqlite3.connect(output)
            try:
                configure_governed_connection(destination, durable_candidate=True)
                create_minimum_core_schema(destination)
                destination.execute("BEGIN IMMEDIATE")
                _insert_source_metadata(
                    destination,
                    source_file_sha256=source_hash_before,
                    source_file_size_bytes=source_file_size_bytes,
                    schema_sha256=schema_digest,
                    fields=fields,
                    baseline=baseline,
                    created_at_utc=timestamp,
                )

                insert_sql = _raw_insert_sql()
                while source_rows := source_cursor.fetchmany(batch_size):
                    insert_rows: list[tuple[object, ...]] = []
                    for row in source_rows:
                        source_rowid = int(row[0])
                        if source_rowid <= previous_rowid:
                            raise RuntimeError(
                                "Source rowids are not strictly increasing: "
                                f"{source_rowid} after {previous_rowid}"
                            )
                        previous_rowid = source_rowid
                        copied_count += 1
                        if source_rowid == 1:
                            excluded_count += 1
                        else:
                            admitted_count += 1

                        values = tuple(row[1:])
                        insert_rows.append(
                            _candidate_insert_row(
                                source_record_id=copied_count,
                                source_rowid=source_rowid,
                                values=values,
                                source_file_sha256=source_hash_before,
                            )
                        )
                        fingerprint_count += 1

                    destination.executemany(insert_sql, insert_rows)
                    batch_count += 1

                observed = (copied_count, admitted_count, excluded_count)
                expected = (
                    baseline.physical_record_count,
                    baseline.admitted_record_count,
                    baseline.excluded_record_count,
                )
                if observed != expected:
                    raise RuntimeError(
                        "Built raw-mirror population mismatch: "
                        f"expected {expected!r}; observed {observed!r}"
                    )
                if batch_count != (copied_count + batch_size - 1) // batch_size:
                    raise RuntimeError("Unexpected raw-mirror batch count")

                destination.commit()
            except Exception:
                destination.rollback()
                raise
            finally:
                destination.close()

            (
                persisted_count,
                persisted_admitted,
                persisted_excluded,
                quick_check,
                foreign_key_rows,
                application_id,
                user_version,
            ) = _validate_persisted_candidate(output, baseline)
            if (persisted_count, persisted_admitted, persisted_excluded) != (
                copied_count,
                admitted_count,
                excluded_count,
            ):
                raise RuntimeError("Persisted counts differ from builder counters")

            source_hash_after = validate_source_version_1_file_identity(
                source,
                expected_source_sha256=expected_source_sha256,
            )
            if source_hash_after != source_hash_before:
                raise RuntimeError("Immutable source hash changed during candidate build")
        except Exception:
            _remove_candidate_files(output)
            raise

    elapsed = perf_counter() - started
    output_file_size_bytes = output.stat().st_size
    rows_per_second = copied_count / elapsed if elapsed > 0 else float("inf")
    return RawMirrorCandidateSummary(
        source_path=str(source),
        output_path=str(output),
        source_file_sha256_hex=source_hash_before.hex(),
        source_schema_sha256_hex=schema_digest.hex(),
        source_file_size_bytes=source_file_size_bytes,
        output_file_size_bytes=output_file_size_bytes,
        physical_record_count=baseline.physical_record_count,
        admitted_record_count=baseline.admitted_record_count,
        excluded_record_count=baseline.excluded_record_count,
        copied_record_count=copied_count,
        copied_admitted_record_count=admitted_count,
        copied_excluded_record_count=excluded_count,
        row_fingerprint_count=fingerprint_count,
        batch_size=batch_size,
        batch_count=batch_count,
        build_elapsed_seconds=elapsed,
        rows_per_second=rows_per_second,
        quick_check=quick_check,
        foreign_key_check_rows=foreign_key_rows,
        application_id=application_id,
        user_version=user_version,
        source_hash_unchanged=True,
        persisted_structural_checks_passed=True,
    )
