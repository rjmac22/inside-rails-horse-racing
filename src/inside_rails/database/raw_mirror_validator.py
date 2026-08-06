"""Independent source-wide validation for a disposable raw-mirror candidate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
import struct
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
    RACEFORM_V1_FIELDS,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
    source_schema_sha256,
    validate_raceform_v1_schema,
)
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
    create_minimum_core_schema,
    schema_inventory,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier


@dataclass(frozen=True)
class RawMirrorValidationSummary:
    source_path: str
    candidate_path: str
    source_file_sha256_hex: str
    candidate_file_sha256_hex: str
    source_schema_sha256_hex: str
    source_file_size_bytes: int
    candidate_file_size_bytes: int
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    compared_record_count: int
    raw_value_comparisons: int
    storage_class_comparisons: int
    source_record_code_comparisons: int
    structural_status_comparisons: int
    stored_fingerprint_comparisons: int
    recomputed_fingerprint_comparisons: int
    batch_size: int
    batch_count: int
    validation_elapsed_seconds: float
    rows_per_second: float
    quick_check: str
    foreign_key_check_rows: int
    application_id: int
    user_version: int
    schema_inventory_matched: bool
    metadata_reconciliation_passed: bool
    raw_population_reconciliation_passed: bool
    source_hash_unchanged: bool
    candidate_hash_unchanged: bool
    persisted_readback_passed: bool


def _validate_batch_size(batch_size: int) -> int:
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    return batch_size


def _same_value(left: object, right: object) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        return struct.pack(">d", left) == struct.pack(">d", right)
    return type(left) is type(right) and left == right


def _candidate_sidecar_paths(candidate: Path) -> tuple[Path, ...]:
    return (
        Path(f"{candidate}-journal"),
        Path(f"{candidate}-wal"),
        Path(f"{candidate}-shm"),
    )


def _validate_source_baseline(
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


def _expected_schema_inventory() -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(":memory:")
    try:
        create_minimum_core_schema(connection)
        return schema_inventory(connection)
    finally:
        connection.close()


def _validate_candidate_structure(
    connection: sqlite3.Connection,
) -> tuple[str, int, int, int]:
    observed_inventory = schema_inventory(connection)
    expected_inventory = _expected_schema_inventory()
    if observed_inventory != expected_inventory:
        raise RuntimeError("Raw-mirror candidate schema inventory mismatch")

    application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if application_id != APPLICATION_ID:
        raise RuntimeError(f"Unexpected candidate application_id: {application_id}")
    if user_version != SCHEMA_VERSION:
        raise RuntimeError(f"Unexpected candidate user_version: {user_version}")

    quick_check_row = connection.execute("PRAGMA quick_check").fetchone()
    quick_check = "" if quick_check_row is None else str(quick_check_row[0])
    if quick_check != "ok":
        raise RuntimeError(f"Raw-mirror candidate quick_check failed: {quick_check!r}")

    foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
    if foreign_key_rows:
        raise RuntimeError(
            f"Raw-mirror candidate foreign_key_check returned {foreign_key_rows} rows"
        )

    return quick_check, foreign_key_rows, application_id, user_version


def _validate_candidate_metadata(
    connection: sqlite3.Connection,
    *,
    source_file_sha256: bytes,
    source_file_size_bytes: int,
    schema_sha256: bytes,
    baseline: SourceBaseline,
) -> None:
    provider = connection.execute(
        """
        SELECT source_provider_id, source_provider_code
        FROM source_provider
        """
    ).fetchall()
    if provider != [(1, "provider:community-source")]:
        raise RuntimeError(f"Unexpected source_provider metadata: {provider!r}")

    product = connection.execute(
        """
        SELECT source_product_id, source_product_code, source_provider_id
        FROM source_product
        """
    ).fetchall()
    if product != [(1, "product:raceform-community-database", 1)]:
        raise RuntimeError(f"Unexpected source_product metadata: {product!r}")

    version = connection.execute(
        """
        SELECT
            source_version_id,
            source_version_code,
            source_product_id,
            original_filename,
            file_sha256,
            file_size_bytes,
            received_date,
            source_schema_sha256,
            physical_record_count,
            admitted_record_count,
            excluded_record_count,
            admission_predicate,
            minimum_source_date,
            maximum_source_date,
            source_integrity_result,
            version_status
        FROM source_version
        """
    ).fetchall()
    expected_version = [
        (
            1,
            source_version_code(source_file_sha256),
            1,
            "raceform.db",
            source_file_sha256,
            source_file_size_bytes,
            None,
            schema_sha256,
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
            "rowid <> 1",
            baseline.minimum_source_date,
            baseline.maximum_source_date,
            "ok",
            "accepted_exact_source",
        )
    ]
    if version != expected_version:
        raise RuntimeError("Source-version metadata does not match the accepted source")

    relation = connection.execute(
        """
        SELECT
            source_relation_id,
            source_relation_code,
            source_version_id,
            relation_name,
            relation_schema_sha256,
            column_count,
            physical_record_count,
            admitted_record_count,
            admission_predicate
        FROM source_relation
        """
    ).fetchall()
    expected_relation = [
        (
            1,
            source_relation_code(source_file_sha256),
            1,
            "data",
            schema_sha256,
            len(RAW_COLUMN_NAMES),
            baseline.physical_record_count,
            baseline.admitted_record_count,
            "rowid <> 1",
        )
    ]
    if relation != expected_relation:
        raise RuntimeError("Source-relation metadata does not match the accepted source")

    fields = connection.execute(
        """
        SELECT
            source_relation_field_id,
            source_relation_id,
            ordinal_position,
            field_name,
            declared_type,
            source_not_null,
            source_default_sql,
            source_primary_key_ordinal
        FROM source_relation_field
        ORDER BY ordinal_position
        """
    ).fetchall()
    expected_fields = [
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
        for index, field in enumerate(RACEFORM_V1_FIELDS, start=1)
    ]
    if fields != expected_fields:
        raise RuntimeError("Source-relation field metadata mismatch")

    forbidden_population = {
        "governance_method": 0,
        "governance_release": 0,
        "governance_release_evidence": 0,
        "core_source_race_occurrence": 0,
        "core_runner_participation": 0,
        "import_manifest": 0,
        "import_validation_result": 0,
    }
    for table_name, expected_count in forbidden_population.items():
        count = int(
            connection.execute(
                f"SELECT COUNT(*) FROM {quote_identifier(table_name)}"
            ).fetchone()[0]
        )
        if count != expected_count:
            raise RuntimeError(
                f"Raw-only candidate unexpectedly populated {table_name}: {count}"
            )


def _raw_population_counts(
    connection: sqlite3.Connection,
) -> tuple[int, int, int]:
    row = connection.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(
                SUM(CASE WHEN structural_status = 'admitted_runner_record' THEN 1 ELSE 0 END),
                0
            ),
            COALESCE(
                SUM(CASE WHEN structural_status = 'retained_excluded_record' THEN 1 ELSE 0 END),
                0
            )
        FROM source_raceform_v1_record
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("Unable to count candidate raw records")
    return int(row[0]), int(row[1]), int(row[2])


def validate_raw_mirror_candidate(
    source_path: str | Path,
    candidate_path: str | Path,
    *,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    batch_size: int = 1_000,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
) -> RawMirrorValidationSummary:
    """Independently reconcile every source row to one persisted raw record."""

    batch_size = _validate_batch_size(batch_size)
    source = Path(source_path).expanduser().resolve()
    candidate = Path(candidate_path).expanduser().resolve()
    if source == candidate:
        raise ValueError("Source and raw-mirror candidate paths must differ")
    if not candidate.is_file():
        raise FileNotFoundError(f"Raw-mirror candidate not found: {candidate}")

    sidecars = [path for path in _candidate_sidecar_paths(candidate) if path.exists()]
    if sidecars:
        raise RuntimeError(
            "Raw-mirror candidate has unexpected SQLite sidecars: "
            + ", ".join(str(path) for path in sidecars)
        )

    started = perf_counter()
    source_hash_before = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    candidate_hash_before = sha256_file(candidate)
    source_file_size_bytes = source.stat().st_size
    candidate_file_size_bytes = candidate.stat().st_size

    compared_records = 0
    raw_value_comparisons = 0
    storage_class_comparisons = 0
    source_record_code_comparisons = 0
    structural_status_comparisons = 0
    stored_fingerprint_comparisons = 0
    recomputed_fingerprint_comparisons = 0
    admitted_records = 0
    excluded_records = 0
    batch_count = 0

    with connect_read_only(source) as source_connection, connect_read_only(
        candidate
    ) as candidate_connection:
        configure_governed_connection(source_connection, query_only=True)
        configure_governed_connection(candidate_connection, query_only=True)

        fields = validate_raceform_v1_schema(source_connection)
        _validate_source_baseline(source_connection, baseline)
        schema_digest = source_schema_sha256(fields)

        (
            quick_check,
            foreign_key_rows,
            application_id,
            user_version,
        ) = _validate_candidate_structure(candidate_connection)
        _validate_candidate_metadata(
            candidate_connection,
            source_file_sha256=source_hash_before,
            source_file_size_bytes=source_file_size_bytes,
            schema_sha256=schema_digest,
            baseline=baseline,
        )

        counts = _raw_population_counts(candidate_connection)
        expected_counts = (
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
        )
        if counts != expected_counts:
            raise RuntimeError(
                "Raw-mirror candidate population mismatch: "
                f"expected {expected_counts!r}; observed {counts!r}"
            )

        quoted_columns = ", ".join(
            quote_identifier(name) for name in RAW_COLUMN_NAMES
        )
        type_columns = ", ".join(
            f"typeof({quote_identifier(name)})" for name in RAW_COLUMN_NAMES
        )
        source_cursor = source_connection.execute(
            f"""
            SELECT rowid, {quoted_columns}, {type_columns}
            FROM "data"
            ORDER BY rowid
            """
        )
        candidate_cursor = candidate_connection.execute(
            f"""
            SELECT
                source_record_id,
                source_record_code,
                source_version_id,
                source_relation_id,
                source_rowid,
                structural_status,
                exclusion_reason,
                row_sha256,
                {quoted_columns},
                {type_columns}
            FROM source_raceform_v1_record
            ORDER BY source_rowid
            """
        )

        while True:
            source_rows = source_cursor.fetchmany(batch_size)
            candidate_rows = candidate_cursor.fetchmany(batch_size)
            if not source_rows and not candidate_rows:
                break
            if len(source_rows) != len(candidate_rows):
                raise RuntimeError(
                    "Source/candidate batch cardinality mismatch: "
                    f"{len(source_rows)} != {len(candidate_rows)}"
                )
            batch_count += 1

            for source_row, candidate_row in zip(
                source_rows, candidate_rows, strict=True
            ):
                compared_records += 1
                source_rowid = int(source_row[0])
                source_value_end = 1 + len(RAW_COLUMN_NAMES)
                source_values = tuple(source_row[1:source_value_end])
                source_types = tuple(
                    str(value) for value in source_row[source_value_end:]
                )

                source_record_id = int(candidate_row[0])
                candidate_code = str(candidate_row[1])
                source_version_id = int(candidate_row[2])
                source_relation_id = int(candidate_row[3])
                candidate_rowid = int(candidate_row[4])
                structural_status = str(candidate_row[5])
                exclusion_reason = candidate_row[6]
                stored_fingerprint = candidate_row[7]
                candidate_value_start = 8
                candidate_value_end = candidate_value_start + len(RAW_COLUMN_NAMES)
                candidate_values = tuple(
                    candidate_row[candidate_value_start:candidate_value_end]
                )
                candidate_types = tuple(
                    str(value) for value in candidate_row[candidate_value_end:]
                )

                if source_record_id != compared_records:
                    raise RuntimeError(
                        "Candidate source_record_id sequence mismatch at "
                        f"source rowid {source_rowid}: "
                        f"{source_record_id} != {compared_records}"
                    )
                if source_version_id != 1 or source_relation_id != 1:
                    raise RuntimeError(
                        f"Candidate lineage identifiers mismatch at source rowid {source_rowid}"
                    )
                if candidate_rowid != source_rowid:
                    raise RuntimeError(
                        "Source/candidate rowid mismatch: "
                        f"{source_rowid} != {candidate_rowid}"
                    )

                expected_code = source_record_code(source_hash_before, source_rowid)
                if candidate_code != expected_code:
                    raise RuntimeError(
                        f"Source-record code mismatch at source rowid {source_rowid}"
                    )
                source_record_code_comparisons += 1

                expected_status = (
                    "retained_excluded_record"
                    if source_rowid == 1
                    else "admitted_runner_record"
                )
                if structural_status != expected_status:
                    raise RuntimeError(
                        f"Structural status mismatch at source rowid {source_rowid}"
                    )
                if source_rowid == 1:
                    excluded_records += 1
                    if (
                        not isinstance(exclusion_reason, str)
                        or not exclusion_reason.strip()
                    ):
                        raise RuntimeError(
                            "Retained excluded source rowid 1 lacks an exclusion reason"
                        )
                else:
                    admitted_records += 1
                    if exclusion_reason is not None:
                        raise RuntimeError(
                            f"Admitted source rowid {source_rowid} has an exclusion reason"
                        )
                structural_status_comparisons += 1

                for ordinal, (source_value, candidate_value) in enumerate(
                    zip(source_values, candidate_values, strict=True)
                ):
                    if not _same_value(source_value, candidate_value):
                        raise RuntimeError(
                            "Raw value mismatch at source rowid "
                            f"{source_rowid}, ordinal {ordinal}"
                        )
                    raw_value_comparisons += 1

                for ordinal, (source_type, candidate_type) in enumerate(
                    zip(source_types, candidate_types, strict=True)
                ):
                    if source_type != candidate_type:
                        raise RuntimeError(
                            "SQLite storage-class mismatch at source rowid "
                            f"{source_rowid}, ordinal {ordinal}: "
                            f"{source_type} != {candidate_type}"
                        )
                    storage_class_comparisons += 1

                expected_fingerprint = raceform_v1_row_sha256(source_values)
                if stored_fingerprint != expected_fingerprint:
                    raise RuntimeError(
                        f"Stored row fingerprint mismatch at source rowid {source_rowid}"
                    )
                stored_fingerprint_comparisons += 1

                if raceform_v1_row_sha256(candidate_values) != expected_fingerprint:
                    raise RuntimeError(
                        f"Recomputed row fingerprint mismatch at source rowid {source_rowid}"
                    )
                recomputed_fingerprint_comparisons += 1

    if compared_records != baseline.physical_record_count:
        raise RuntimeError(
            "Compared raw-record count mismatch: "
            f"{compared_records} != {baseline.physical_record_count}"
        )
    if admitted_records != baseline.admitted_record_count:
        raise RuntimeError(
            "Compared admitted-record count mismatch: "
            f"{admitted_records} != {baseline.admitted_record_count}"
        )
    if excluded_records != baseline.excluded_record_count:
        raise RuntimeError(
            "Compared excluded-record count mismatch: "
            f"{excluded_records} != {baseline.excluded_record_count}"
        )

    source_hash_after = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    candidate_hash_after = sha256_file(candidate)
    if source_hash_after != source_hash_before:
        raise RuntimeError("Immutable source hash changed during validation")
    if candidate_hash_after != candidate_hash_before:
        raise RuntimeError("Raw-mirror candidate hash changed during validation")

    elapsed = perf_counter() - started
    rows_per_second = compared_records / elapsed if elapsed > 0 else float("inf")
    return RawMirrorValidationSummary(
        source_path=str(source),
        candidate_path=str(candidate),
        source_file_sha256_hex=source_hash_before.hex(),
        candidate_file_sha256_hex=candidate_hash_before.hex(),
        source_schema_sha256_hex=schema_digest.hex(),
        source_file_size_bytes=source_file_size_bytes,
        candidate_file_size_bytes=candidate_file_size_bytes,
        physical_record_count=baseline.physical_record_count,
        admitted_record_count=baseline.admitted_record_count,
        excluded_record_count=baseline.excluded_record_count,
        compared_record_count=compared_records,
        raw_value_comparisons=raw_value_comparisons,
        storage_class_comparisons=storage_class_comparisons,
        source_record_code_comparisons=source_record_code_comparisons,
        structural_status_comparisons=structural_status_comparisons,
        stored_fingerprint_comparisons=stored_fingerprint_comparisons,
        recomputed_fingerprint_comparisons=recomputed_fingerprint_comparisons,
        batch_size=batch_size,
        batch_count=batch_count,
        validation_elapsed_seconds=elapsed,
        rows_per_second=rows_per_second,
        quick_check=quick_check,
        foreign_key_check_rows=foreign_key_rows,
        application_id=application_id,
        user_version=user_version,
        schema_inventory_matched=True,
        metadata_reconciliation_passed=True,
        raw_population_reconciliation_passed=True,
        source_hash_unchanged=True,
        candidate_hash_unchanged=True,
        persisted_readback_passed=True,
    )
