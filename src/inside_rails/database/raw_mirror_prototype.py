"""Small source-backed proof of exact Source Version 1 raw-mirror preservation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import struct

from inside_rails.database.fingerprints import raceform_v1_row_sha256
from inside_rails.database.identifiers import (
    source_record_code,
    source_relation_code,
    source_version_code,
)
from inside_rails.database.schema import configure_governed_connection, create_minimum_core_schema
from inside_rails.source_sqlite import connect_read_only, quote_identifier, table_columns


@dataclass(frozen=True)
class SourceField:
    ordinal_position: int
    field_name: str
    declared_type: str
    source_not_null: int = 0
    source_default_sql: str | None = None
    source_primary_key_ordinal: int = 0


_FIELD_TYPES = (
    ("date", "NUMERIC"),
    ("course", "TEXT"),
    ("race_id", "INTEGER"),
    ("off", "TEXT"),
    ("race_name", "TEXT"),
    ("type", "TEXT"),
    ("class", "TEXT"),
    ("pattern", "TEXT"),
    ("rating_band", "TEXT"),
    ("age_band", "TEXT"),
    ("sex_rest", "TEXT"),
    ("dist", "TEXT"),
    ("going", "TEXT"),
    ("ran", "INTEGER"),
    ("num", "INTEGER"),
    ("pos", "INTEGER"),
    ("draw", "INTEGER"),
    ("ovr_btn", "NUMERIC"),
    ("btn", "NUMERIC"),
    ("horse", "TEXT"),
    ("age", "INTEGER"),
    ("sex", "TEXT"),
    ("wgt", "TEXT"),
    ("hg", "TEXT"),
    ("time", "TEXT"),
    ("sp", "TEXT"),
    ("jockey", "TEXT"),
    ("trainer", "TEXT"),
    ("prize", "INTEGER"),
    ("or", "INTEGER"),
    ("rpr", "INTEGER"),
    ("ts", "INTEGER"),
    ("sire", "TEXT"),
    ("dam", "TEXT"),
    ("damsire", "TEXT"),
    ("owner", "TEXT"),
    ("comment", "TEXT"),
)
RACEFORM_V1_FIELDS = tuple(
    SourceField(ordinal, name, declared_type)
    for ordinal, (name, declared_type) in enumerate(_FIELD_TYPES)
)
RAW_COLUMN_NAMES = tuple(field.field_name for field in RACEFORM_V1_FIELDS)


@dataclass(frozen=True)
class SourceBaseline:
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    minimum_source_date: str
    maximum_source_date: str


RACEFORM_V1_BASELINE = SourceBaseline(
    physical_record_count=1_851_286,
    admitted_record_count=1_851_285,
    excluded_record_count=1,
    minimum_source_date="2015-01-01",
    maximum_source_date="2026-05-27",
)


@dataclass(frozen=True)
class PrototypeSummary:
    source_path: str
    output_path: str
    source_file_sha256_hex: str
    source_schema_sha256_hex: str
    source_file_size_bytes: int
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    selected_source_rowids: tuple[int, ...]
    copied_record_count: int
    observed_storage_classes: tuple[str, ...]
    value_comparisons: int
    typeof_comparisons: int
    fingerprint_comparisons: int
    quick_check: str
    foreign_key_check_rows: int
    source_hash_unchanged: bool
    persisted_readback_passed: bool


@dataclass(frozen=True)
class _RawRecord:
    source_rowid: int
    values: tuple[object, ...]
    storage_classes: tuple[str, ...]


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> bytes:
    """Return the SHA-256 of one file without loading it into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.digest()


def _normalised_schema_rows(connection: sqlite3.Connection) -> tuple[SourceField, ...]:
    rows = table_columns(connection, "data")
    return tuple(
        SourceField(
            ordinal_position=int(row["cid"]),
            field_name=str(row["name"]),
            declared_type=str(row["type"]),
            source_not_null=int(row["notnull"]),
            source_default_sql=row["dflt_value"],
            source_primary_key_ordinal=int(row["pk"]),
        )
        for row in rows
    )


def validate_raceform_v1_schema(connection: sqlite3.Connection) -> tuple[SourceField, ...]:
    """Fail unless ``data`` has the exact accepted 37-field declaration."""

    observed = _normalised_schema_rows(connection)
    if observed != RACEFORM_V1_FIELDS:
        max_length = max(len(observed), len(RACEFORM_V1_FIELDS))
        for index in range(max_length):
            expected_item = (
                RACEFORM_V1_FIELDS[index] if index < len(RACEFORM_V1_FIELDS) else None
            )
            observed_item = observed[index] if index < len(observed) else None
            if expected_item != observed_item:
                raise RuntimeError(
                    "Source Version 1 schema mismatch at ordinal "
                    f"{index}: expected {expected_item!r}; observed {observed_item!r}"
                )
        raise RuntimeError("Source Version 1 schema mismatch")
    return observed


def source_schema_sha256(fields: Sequence[SourceField]) -> bytes:
    """Return a deterministic prototype signature for ordered PRAGMA metadata."""

    payload = [
        {
            "declared_type": field.declared_type,
            "field_name": field.field_name,
            "ordinal_position": field.ordinal_position,
            "source_default_sql": field.source_default_sql,
            "source_not_null": field.source_not_null,
            "source_primary_key_ordinal": field.source_primary_key_ordinal,
        }
        for field in fields
    ]
    message = b"inside-rails:raceform-v1-schema:v1\0" + json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(message).digest()


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


def select_representative_source_rowids(connection: sqlite3.Connection) -> tuple[int, ...]:
    """Select a tiny deterministic set proving observed mixed storage classes."""

    requirements = (
        "retained rowid 1",
        "first admitted record",
        "prize NULL",
        "prize INTEGER",
        "prize TEXT",
        "num INTEGER",
        "num TEXT",
        "ovr_btn REAL",
    )
    row = connection.execute(
        """
        SELECT
            MIN(CASE WHEN rowid = 1 THEN rowid END),
            MIN(CASE WHEN rowid <> 1 THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("prize") = 'null' THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("prize") = 'integer' THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("prize") = 'text' THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("num") = 'integer' THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("num") = 'text' THEN rowid END),
            MIN(CASE WHEN rowid <> 1 AND typeof("ovr_btn") = 'real' THEN rowid END)
        FROM "data"
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("Unable to select representative source records")
    missing = [
        name
        for name, source_rowid in zip(requirements, row, strict=True)
        if source_rowid is None
    ]
    if missing:
        raise RuntimeError(
            "Source Version 1 lacks required prototype storage-class examples: "
            + ", ".join(missing)
        )
    return tuple(sorted({int(source_rowid) for source_rowid in row}))


def _fetch_raw_record(connection: sqlite3.Connection, source_rowid: int) -> _RawRecord:
    quoted_columns = ", ".join(quote_identifier(name) for name in RAW_COLUMN_NAMES)
    type_columns = ", ".join(
        f"typeof({quote_identifier(name)})" for name in RAW_COLUMN_NAMES
    )
    row = connection.execute(
        f'SELECT rowid, {quoted_columns}, {type_columns} FROM "data" WHERE rowid = ?',
        (source_rowid,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Source rowid {source_rowid} is missing")
    value_end = 1 + len(RAW_COLUMN_NAMES)
    return _RawRecord(
        source_rowid=int(row[0]),
        values=tuple(row[1:value_end]),
        storage_classes=tuple(str(value) for value in row[value_end:]),
    )


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
            "Private research prototype; no bulk redistribution.",
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
            "Source-backed raw-mirror prototype of the accepted immutable file.",
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
            "All source rows remain in the immutable source; "
            "only selected prototype rows are mirrored.",
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


def _insert_raw_records(
    connection: sqlite3.Connection,
    records: Sequence[_RawRecord],
    source_file_sha256: bytes,
) -> None:
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
    quoted_metadata = [quote_identifier(name) for name in metadata_names]
    quoted_raw = [quote_identifier(name) for name in RAW_COLUMN_NAMES]
    column_sql = ", ".join([*quoted_metadata, *quoted_raw])
    placeholders = ", ".join(
        "?" for _ in range(len(metadata_names) + len(RAW_COLUMN_NAMES))
    )
    sql = f"INSERT INTO source_raceform_v1_record ({column_sql}) VALUES ({placeholders})"
    ordered_records = sorted(records, key=lambda item: item.source_rowid)
    for source_record_id, record in enumerate(ordered_records, start=1):
        excluded = record.source_rowid == 1
        connection.execute(
            sql,
            (
                source_record_id,
                source_record_code(source_file_sha256, record.source_rowid),
                1,
                1,
                record.source_rowid,
                "retained_excluded_record" if excluded else "admitted_runner_record",
                "Retained Source Version 1 rowid 1 exclusion." if excluded else None,
                raceform_v1_row_sha256(record.values),
                *record.values,
            ),
        )


def _same_value(left: object, right: object) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        return struct.pack(">d", left) == struct.pack(">d", right)
    return type(left) is type(right) and left == right


def _validate_persisted_readback(
    source_path: Path,
    output_path: Path,
    source_rowids: Sequence[int],
    source_file_sha256: bytes,
) -> tuple[set[str], int, int, int, str, int]:
    observed_storage_classes: set[str] = set()
    value_comparisons = 0
    typeof_comparisons = 0
    fingerprint_comparisons = 0
    with connect_read_only(source_path) as source, connect_read_only(output_path) as target:
        configure_governed_connection(target, query_only=True)
        copied_count = target.execute(
            "SELECT COUNT(*) FROM source_raceform_v1_record"
        ).fetchone()[0]
        if copied_count != len(source_rowids):
            raise RuntimeError(
                "Prototype raw-record count mismatch: "
                f"expected {len(source_rowids)}; observed {copied_count}"
            )
        for source_rowid in source_rowids:
            source_record = _fetch_raw_record(source, source_rowid)
            quoted_columns = ", ".join(
                quote_identifier(name) for name in RAW_COLUMN_NAMES
            )
            type_columns = ", ".join(
                f"typeof({quote_identifier(name)})" for name in RAW_COLUMN_NAMES
            )
            row = target.execute(
                f"""
                SELECT source_record_code, structural_status, exclusion_reason, row_sha256,
                       {quoted_columns}, {type_columns}
                FROM source_raceform_v1_record
                WHERE source_rowid = ?
                """,
                (source_rowid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"Prototype omitted source rowid {source_rowid}")
            value_start = 4
            value_end = value_start + len(RAW_COLUMN_NAMES)
            target_values = tuple(row[value_start:value_end])
            target_types = tuple(str(value) for value in row[value_end:])
            if row[0] != source_record_code(source_file_sha256, source_rowid):
                raise RuntimeError(
                    f"Deterministic source-record code mismatch for rowid {source_rowid}"
                )
            expected_status = (
                "retained_excluded_record"
                if source_rowid == 1
                else "admitted_runner_record"
            )
            if row[1] != expected_status:
                raise RuntimeError(f"Structural status mismatch for rowid {source_rowid}")
            if source_rowid == 1 and not row[2]:
                raise RuntimeError("Retained excluded record lacks an exclusion reason")
            if source_rowid != 1 and row[2] is not None:
                raise RuntimeError(f"Admitted source rowid {source_rowid} has an exclusion reason")
            for ordinal, (source_value, target_value) in enumerate(
                zip(source_record.values, target_values, strict=True)
            ):
                if not _same_value(source_value, target_value):
                    raise RuntimeError(
                        f"Raw value mismatch at source rowid {source_rowid}, ordinal {ordinal}"
                    )
                value_comparisons += 1
            if source_record.storage_classes != target_types:
                for ordinal, (source_type, target_type) in enumerate(
                    zip(source_record.storage_classes, target_types, strict=True)
                ):
                    if source_type != target_type:
                        raise RuntimeError(
                            "SQLite storage-class mismatch at source rowid "
                            f"{source_rowid}, ordinal {ordinal}: "
                            f"{source_type} != {target_type}"
                        )
            typeof_comparisons += len(RAW_COLUMN_NAMES)
            observed_storage_classes.update(target_types)
            expected_fingerprint = raceform_v1_row_sha256(source_record.values)
            if row[3] != expected_fingerprint:
                raise RuntimeError(f"Stored row fingerprint mismatch for rowid {source_rowid}")
            if raceform_v1_row_sha256(target_values) != expected_fingerprint:
                raise RuntimeError(f"Readback row fingerprint mismatch for rowid {source_rowid}")
            fingerprint_comparisons += 1

        quick_check_row = target.execute("PRAGMA quick_check").fetchone()
        quick_check = "" if quick_check_row is None else str(quick_check_row[0])
        if quick_check != "ok":
            raise RuntimeError(f"Prototype SQLite quick_check failed: {quick_check!r}")
        foreign_key_rows = len(target.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Prototype foreign_key_check returned {foreign_key_rows} rows"
            )

    required_classes = {"null", "integer", "real", "text"}
    if not required_classes.issubset(observed_storage_classes):
        missing = sorted(required_classes - observed_storage_classes)
        raise RuntimeError(f"Prototype sample lacks required observed storage classes: {missing}")
    return (
        observed_storage_classes,
        value_comparisons,
        typeof_comparisons,
        fingerprint_comparisons,
        quick_check,
        foreign_key_rows,
    )


def run_raw_mirror_prototype(
    source_path: str | Path,
    output_path: str | Path,
    *,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    created_at_utc: str | None = None,
) -> PrototypeSummary:
    """Build and validate a tiny persisted raw mirror from the immutable source."""

    source = Path(source_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if source == output:
        raise ValueError("Source and prototype output paths must differ")
    if not source.is_file():
        raise FileNotFoundError(f"SQLite source not found: {source}")
    if output.exists():
        raise FileExistsError(f"Prototype output already exists: {output}")

    source_hash_before = sha256_file(source)
    source_file_size_bytes = source.stat().st_size
    timestamp = created_at_utc or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )

    with connect_read_only(source) as source_connection:
        fields = validate_raceform_v1_schema(source_connection)
        _profile_and_validate_baseline(source_connection, baseline)
        selected_rowids = select_representative_source_rowids(source_connection)
        records = tuple(
            _fetch_raw_record(source_connection, source_rowid)
            for source_rowid in selected_rowids
        )
    schema_digest = source_schema_sha256(fields)

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination = sqlite3.connect(output)
        try:
            configure_governed_connection(destination, durable_candidate=True)
            create_minimum_core_schema(destination)
            destination.execute("BEGIN")
            _insert_source_metadata(
                destination,
                source_file_sha256=source_hash_before,
                source_file_size_bytes=source_file_size_bytes,
                schema_sha256=schema_digest,
                fields=fields,
                baseline=baseline,
                created_at_utc=timestamp,
            )
            _insert_raw_records(destination, records, source_hash_before)
            destination.commit()
        except Exception:
            destination.rollback()
            raise
        finally:
            destination.close()

        (
            observed_storage_classes,
            value_comparisons,
            typeof_comparisons,
            fingerprint_comparisons,
            quick_check,
            foreign_key_rows,
        ) = _validate_persisted_readback(
            source,
            output,
            selected_rowids,
            source_hash_before,
        )
        source_hash_after = sha256_file(source)
        if source_hash_after != source_hash_before:
            raise RuntimeError("Immutable source file hash changed during the prototype run")
    except Exception:
        output.unlink(missing_ok=True)
        raise

    return PrototypeSummary(
        source_path=str(source),
        output_path=str(output),
        source_file_sha256_hex=source_hash_before.hex(),
        source_schema_sha256_hex=schema_digest.hex(),
        source_file_size_bytes=source_file_size_bytes,
        physical_record_count=baseline.physical_record_count,
        admitted_record_count=baseline.admitted_record_count,
        excluded_record_count=baseline.excluded_record_count,
        selected_source_rowids=selected_rowids,
        copied_record_count=len(selected_rowids),
        observed_storage_classes=tuple(sorted(observed_storage_classes)),
        value_comparisons=value_comparisons,
        typeof_comparisons=typeof_comparisons,
        fingerprint_comparisons=fingerprint_comparisons,
        quick_check=quick_check,
        foreign_key_check_rows=foreign_key_rows,
        source_hash_unchanged=True,
        persisted_readback_passed=True,
    )
