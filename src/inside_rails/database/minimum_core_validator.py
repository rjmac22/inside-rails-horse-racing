"""Independent source-wide validation for a complete minimum-core candidate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
import re
import sqlite3
import struct
from time import perf_counter

from inside_rails.database.accepted_source import (
    RACEFORM_V1_FILE_SHA256,
    validate_source_version_1_file_identity,
)
from inside_rails.database.fingerprints import raceform_v1_row_sha256
from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
    runner_participation_code,
    source_race_occurrence_code,
    source_record_code,
)
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_BASELINE,
    RAW_COLUMN_NAMES,
    SourceBaseline,
    sha256_file,
)
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
    create_minimum_core_schema,
    schema_inventory,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier


VALIDATED_RAW_MIRROR_CANDIDATE_SHA256_HEX = (
    "cbc7ac16c0a66f50002e2cf9b17d3bc77795640b7a340537f3cd83d202543f3a"
)
VALIDATED_RAW_MIRROR_CANDIDATE_SHA256 = bytes.fromhex(
    VALIDATED_RAW_MIRROR_CANDIDATE_SHA256_HEX
)
BUILT_MINIMUM_CORE_CANDIDATE_SHA256_HEX = (
    "7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2"
)
BUILT_MINIMUM_CORE_CANDIDATE_SHA256 = bytes.fromhex(
    BUILT_MINIMUM_CORE_CANDIDATE_SHA256_HEX
)
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
_METADATA_TABLES = (
    "source_provider",
    "source_product",
    "source_version",
    "source_relation",
    "source_relation_field",
)
_GOVERNANCE_EVIDENCE = (
    (
        "document",
        "docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md",
        "Accepted bounded authorisation for the Source Version 1 structural core.",
    ),
    (
        "document",
        "docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md",
        "Accepted physical schema and identifier contract for minimum core version 1.",
    ),
    (
        "governed_output",
        "docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md",
        "Source-wide raw-mirror build and independent persisted-readback evidence.",
    ),
    (
        "governed_output",
        "docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md",
        "Real-data race-and-runner structural prototype and independent validation evidence.",
    ),
)
_EXPECTED_VALIDATION_STAGES = (
    ("persisted_readback", "minimum-core-candidate-builder"),
    ("sqlite_integrity", "sqlite-quick-check"),
    ("foreign_key_validation", "sqlite-foreign-key-check"),
    ("post_load_validation", "minimum-core-candidate-builder"),
)
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_IMPORT_CODE_PATTERN = re.compile(r"imp:(\d{8}T\d{12}Z):[0-9a-f]{8}")
_DATABASE_CODE_PATTERN = re.compile(r"db:(\d{8}T\d{12}Z):[0-9a-f]{8}")
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@dataclass(frozen=True)
class MinimumCoreValidationSummary:
    source_path: str
    raw_mirror_candidate_path: str
    candidate_path: str
    source_file_sha256_hex: str
    raw_mirror_candidate_sha256_hex: str
    candidate_file_sha256_hex: str
    source_file_size_bytes: int
    raw_mirror_candidate_file_size_bytes: int
    candidate_file_size_bytes: int
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    metadata_row_comparisons: int
    raw_record_comparisons: int
    raw_value_comparisons: int
    storage_class_comparisons: int
    source_record_code_comparisons: int
    structural_status_comparisons: int
    stored_fingerprint_comparisons: int
    recomputed_fingerprint_comparisons: int
    race_grouping_comparisons: int
    race_code_comparisons: int
    race_runner_count_comparisons: int
    runner_lineage_comparisons: int
    runner_code_comparisons: int
    manifest_validation_result_count: int
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
    governance_reconciliation_passed: bool
    manifest_reconciliation_passed: bool
    source_hash_unchanged: bool
    raw_mirror_candidate_hash_unchanged: bool
    candidate_hash_unchanged: bool
    persisted_readback_passed: bool
    release_accepted: bool


def _positive_integer(value: int, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _expected_hash(value: bytes, *, name: str) -> bytes:
    if not isinstance(value, bytes) or len(value) != 32:
        raise ValueError(f"{name} must contain exactly 32 bytes")
    return value


def _sidecars(database: Path) -> tuple[Path, ...]:
    return (
        Path(f"{database}-journal"),
        Path(f"{database}-wal"),
        Path(f"{database}-shm"),
    )


def _require_file(path: Path, *, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    unexpected = [sidecar for sidecar in _sidecars(path) if sidecar.exists()]
    if unexpected:
        raise RuntimeError(
            f"{label} has unexpected SQLite sidecars: "
            + ", ".join(str(path) for path in unexpected)
        )


def _validate_hash(path: Path, expected: bytes, *, label: str) -> bytes:
    _require_file(path, label=label)
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected.hex()}; "
            f"observed {observed.hex()}"
        )
    return observed


def _same_value(left: object, right: object) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        return struct.pack(">d", left) == struct.pack(">d", right)
    return type(left) is type(right) and left == right


def _value_token(value: object) -> tuple[str, object]:
    if isinstance(value, float):
        return ("float", struct.pack(">d", value))
    if isinstance(value, bytes):
        return ("bytes", value)
    return (type(value).__name__, value)


def _race_key(values: tuple[object, object, object]) -> tuple[tuple[str, object], ...]:
    return tuple(_value_token(value) for value in values)


def _parsed_timestamp(value: object, *, label: str) -> datetime:
    try:
        return datetime.strptime(str(value), _TIMESTAMP_FORMAT)
    except ValueError as exc:
        raise RuntimeError(f"{label} is not a canonical UTC timestamp") from exc


def _expected_schema_inventory() -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(":memory:")
    try:
        create_minimum_core_schema(connection)
        return schema_inventory(connection)
    finally:
        connection.close()


def _validate_structure(connection: sqlite3.Connection) -> tuple[str, int, int, int]:
    if schema_inventory(connection) != _expected_schema_inventory():
        raise RuntimeError("Minimum-core candidate schema inventory mismatch")

    application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if application_id != APPLICATION_ID:
        raise RuntimeError(f"Unexpected candidate application_id: {application_id}")
    if user_version != SCHEMA_VERSION:
        raise RuntimeError(f"Unexpected candidate user_version: {user_version}")

    quick_row = connection.execute("PRAGMA quick_check").fetchone()
    quick = "" if quick_row is None else str(quick_row[0])
    if quick != "ok":
        raise RuntimeError(f"Minimum-core candidate quick_check failed: {quick!r}")
    foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
    if foreign_key_rows:
        raise RuntimeError(
            f"Minimum-core candidate foreign_key_check returned {foreign_key_rows} rows"
        )
    return quick, foreign_key_rows, application_id, user_version


def _compare_metadata(
    raw_connection: sqlite3.Connection,
    candidate_connection: sqlite3.Connection,
) -> int:
    comparisons = 0
    for table in _METADATA_TABLES:
        quoted = quote_identifier(table)
        raw_columns = raw_connection.execute(f"PRAGMA table_info({quoted})").fetchall()
        candidate_columns = candidate_connection.execute(
            f"PRAGMA table_info({quoted})"
        ).fetchall()
        if raw_columns != candidate_columns:
            raise RuntimeError(f"Metadata schema mismatch for {table}")

        raw_rows = raw_connection.execute(
            f"SELECT * FROM {quoted} ORDER BY 1"
        ).fetchall()
        candidate_rows = candidate_connection.execute(
            f"SELECT * FROM {quoted} ORDER BY 1"
        ).fetchall()
        if len(raw_rows) != len(candidate_rows):
            raise RuntimeError(f"Metadata row-count mismatch for {table}")
        for row_number, (raw_row, candidate_row) in enumerate(
            zip(raw_rows, candidate_rows, strict=True),
            start=1,
        ):
            if len(raw_row) != len(candidate_row):
                raise RuntimeError(f"Metadata width mismatch for {table}")
            for raw_value, candidate_value in zip(
                raw_row,
                candidate_row,
                strict=True,
            ):
                if not _same_value(raw_value, candidate_value):
                    raise RuntimeError(
                        f"Metadata mismatch for {table} row {row_number}"
                    )
            comparisons += 1
    return comparisons


def _record_select_sql() -> str:
    raw_columns = ", ".join(quote_identifier(name) for name in RAW_COLUMN_NAMES)
    storage_classes = ", ".join(
        f"typeof({quote_identifier(name)})" for name in RAW_COLUMN_NAMES
    )
    return f"""
        SELECT source_record_id, source_record_code, source_version_id,
               source_relation_id, source_rowid, structural_status,
               exclusion_reason, row_sha256, {raw_columns}, {storage_classes}
        FROM source_raceform_v1_record
        ORDER BY source_rowid
    """


def _compare_raw_records(
    raw_connection: sqlite3.Connection,
    candidate_connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
    batch_size: int,
) -> tuple[int, int, int, int, int, int, int, int]:
    raw_cursor = raw_connection.execute(_record_select_sql())
    candidate_cursor = candidate_connection.execute(_record_select_sql())
    record_count = 0
    raw_value_comparisons = 0
    storage_class_comparisons = 0
    source_code_comparisons = 0
    status_comparisons = 0
    stored_fingerprint_comparisons = 0
    recomputed_fingerprint_comparisons = 0
    batch_count = 0

    while True:
        raw_rows = raw_cursor.fetchmany(batch_size)
        candidate_rows = candidate_cursor.fetchmany(batch_size)
        if not raw_rows and not candidate_rows:
            break
        batch_count += 1
        if len(raw_rows) != len(candidate_rows):
            raise RuntimeError("Candidate raw batch length differs from raw mirror")

        for raw_row, candidate_row in zip(raw_rows, candidate_rows, strict=True):
            record_count += 1
            rowid = int(raw_row[4])
            if int(candidate_row[4]) != rowid:
                raise RuntimeError(f"Candidate raw rowid mismatch at row {record_count}")
            for index in (0, 2, 3, 4, 6):
                if not _same_value(raw_row[index], candidate_row[index]):
                    raise RuntimeError(
                        f"Candidate raw metadata mismatch at source rowid {rowid}"
                    )

            expected_code = source_record_code(source_sha256, rowid)
            if raw_row[1] != expected_code or candidate_row[1] != expected_code:
                raise RuntimeError(
                    f"Candidate source-record code mismatch at source rowid {rowid}"
                )
            source_code_comparisons += 1

            expected_status = (
                "retained_excluded_record"
                if rowid == 1
                else "admitted_runner_record"
            )
            if raw_row[5] != expected_status or candidate_row[5] != expected_status:
                raise RuntimeError(
                    f"Candidate structural status mismatch at source rowid {rowid}"
                )
            status_comparisons += 1

            if raw_row[7] != candidate_row[7]:
                raise RuntimeError(
                    f"Candidate stored fingerprint mismatch at source rowid {rowid}"
                )
            stored_fingerprint_comparisons += 1

            value_start = 8
            value_end = value_start + len(RAW_COLUMN_NAMES)
            raw_values = tuple(raw_row[value_start:value_end])
            candidate_values = tuple(candidate_row[value_start:value_end])
            for raw_value, candidate_value in zip(
                raw_values,
                candidate_values,
                strict=True,
            ):
                if not _same_value(raw_value, candidate_value):
                    raise RuntimeError(
                        f"Candidate raw value mismatch at source rowid {rowid}"
                    )
                raw_value_comparisons += 1

            raw_types = raw_row[value_end:]
            candidate_types = candidate_row[value_end:]
            for raw_type, candidate_type in zip(
                raw_types,
                candidate_types,
                strict=True,
            ):
                if raw_type != candidate_type:
                    raise RuntimeError(
                        f"Candidate storage-class mismatch at source rowid {rowid}"
                    )
                storage_class_comparisons += 1

            recomputed = raceform_v1_row_sha256(candidate_values)
            if recomputed != candidate_row[7]:
                raise RuntimeError(
                    f"Candidate recomputed fingerprint mismatch at source rowid {rowid}"
                )
            recomputed_fingerprint_comparisons += 1

    if record_count != baseline.physical_record_count:
        raise RuntimeError(
            f"Candidate raw record count mismatch: expected "
            f"{baseline.physical_record_count}; observed {record_count}"
        )
    return (
        record_count,
        raw_value_comparisons,
        storage_class_comparisons,
        source_code_comparisons,
        status_comparisons,
        stored_fingerprint_comparisons,
        recomputed_fingerprint_comparisons,
        batch_count,
    )


def _validate_governance(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
) -> str:
    method = connection.execute(
        """
        SELECT governance_method_id, governance_method_code, method_name,
               method_version, repository_commit, method_description,
               created_at_utc
        FROM governance_method
        """
    ).fetchall()
    if len(method) != 1:
        raise RuntimeError("Candidate must contain exactly one governance method")
    method_row = method[0]
    if (
        method_row[0] != 1
        or method_row[1] != governance_method_code("source-v1-structure", 1)
        or method_row[2] != "Source Version 1 structural reconstruction"
        or method_row[3] != 1
        or _COMMIT_PATTERN.fullmatch(str(method_row[4])) is None
        or method_row[5]
        != (
            "Groups admitted raw records by exact date + course + off and creates "
            "one runner participation per admitted source record."
        )
        or not str(method_row[6]).endswith("Z")
    ):
        raise RuntimeError("Candidate governance-method metadata mismatch")

    release = connection.execute(
        """
        SELECT governance_release_id, governance_release_code,
               source_version_id, governance_method_id, release_status,
               accepted_date, repository_commit, population_predicate,
               release_description, superseded_by_release_id, created_at_utc
        FROM governance_release
        """
    ).fetchall()
    if len(release) != 1:
        raise RuntimeError("Candidate must contain exactly one governance release")
    release_row = release[0]
    if (
        release_row[0] != 1
        or release_row[1]
        != governance_release_code(source_sha256, "source-v1-structure", 1)
        or release_row[2:5] != (1, 1, "accepted")
        or release_row[5] != str(release_row[10])[:10]
        or release_row[6] != method_row[4]
        or release_row[7] != "rowid <> 1"
        or release_row[8]
        != (
            "Accepted Source Version 1 structural method used by a complete "
            "disposable minimum-core candidate; this is not an accepted "
            "database release."
        )
        or release_row[9] is not None
        or release_row[10] != method_row[6]
    ):
        raise RuntimeError("Candidate governance-release metadata mismatch")
    _parsed_timestamp(method_row[6], label="Governance timestamp")

    evidence = connection.execute(
        """
        SELECT governance_release_evidence_id, governance_release_id,
               evidence_type, evidence_reference, evidence_sha256,
               evidence_description
        FROM governance_release_evidence
        ORDER BY governance_release_evidence_id
        """
    ).fetchall()
    expected_evidence = [
        (index, 1, evidence_type, reference, None, description)
        for index, (evidence_type, reference, description) in enumerate(
            _GOVERNANCE_EVIDENCE,
            start=1,
        )
    ]
    if evidence != expected_evidence:
        raise RuntimeError("Candidate governance evidence mismatch")
    return str(method_row[4])


def _validate_manifest(
    connection: sqlite3.Connection,
    *,
    baseline: SourceBaseline,
    expected_race_count: int,
    governance_commit: str,
) -> int:
    rows = connection.execute(
        """
        SELECT import_manifest_id, import_manifest_code, database_release_code,
               source_version_id, governance_release_id, schema_version,
               code_commit, reference_data_commit, build_command,
               build_started_at_utc, build_completed_at_utc,
               physical_record_count, admitted_record_count,
               excluded_record_count, race_occurrence_count,
               runner_participation_count, persisted_readback_passed,
               sqlite_integrity_passed, foreign_key_check_passed,
               post_load_validation_passed, prior_database_release_code,
               prior_release_preserved, build_status, failure_reason
        FROM import_manifest
        """
    ).fetchall()
    if len(rows) != 1:
        raise RuntimeError("Candidate must contain exactly one import manifest")
    manifest = rows[0]
    import_match = _IMPORT_CODE_PATTERN.fullmatch(str(manifest[1]))
    database_match = _DATABASE_CODE_PATTERN.fullmatch(str(manifest[2]))
    if import_match is None or database_match is None:
        raise RuntimeError("Candidate import or database-release code is malformed")
    if import_match.group(1) != database_match.group(1):
        raise RuntimeError("Candidate event codes do not share one build timestamp")
    if manifest[10] is None:
        raise RuntimeError("Candidate completion timestamp is missing")
    started_at = _parsed_timestamp(manifest[9], label="Manifest start timestamp")
    completed_at = _parsed_timestamp(
        manifest[10],
        label="Manifest completion timestamp",
    )
    compact_started_at = started_at.strftime("%Y%m%dT%H%M%S%fZ")
    if import_match.group(1) != compact_started_at:
        raise RuntimeError("Candidate event codes do not match the build timestamp")
    if completed_at < started_at:
        raise RuntimeError("Candidate completion timestamp precedes its start")
    if (
        manifest[0] != 1
        or manifest[3:6] != (1, 1, 1)
        or manifest[6] != governance_commit
        or _COMMIT_PATTERN.fullmatch(str(manifest[7])) is None
        or manifest[8] != "python scripts/build_minimum_core_candidate.py"
        or not str(manifest[9]).endswith("Z")
        or manifest[10] is None
        or not str(manifest[10]).endswith("Z")
        or manifest[11:16]
        != (
            baseline.physical_record_count,
            baseline.admitted_record_count,
            baseline.excluded_record_count,
            expected_race_count,
            baseline.admitted_record_count,
        )
        or manifest[16:20] != (1, 1, 1, 1)
        or manifest[20] is not None
        or manifest[21] != 1
        or manifest[22] != "built"
        or manifest[23] is not None
    ):
        raise RuntimeError("Candidate final import manifest mismatch")

    validation_rows = connection.execute(
        """
        SELECT import_validation_result_id, import_manifest_id,
               validation_stage, validator_name, validator_version,
               required_for_acceptance, outcome, executed_at_utc,
               command, result_summary, details_artifact_path
        FROM import_validation_result
        ORDER BY import_validation_result_id
        """
    ).fetchall()
    if len(validation_rows) != len(_EXPECTED_VALIDATION_STAGES):
        raise RuntimeError("Candidate validation-result count mismatch")
    for index, (row, expected) in enumerate(
        zip(validation_rows, _EXPECTED_VALIDATION_STAGES, strict=True),
        start=1,
    ):
        stage, validator_name = expected
        if (
            row[0] != index
            or row[1] != 1
            or row[2] != stage
            or row[3] != validator_name
            or not str(row[4]).strip()
            or row[5] != 1
            or row[6] != "passed"
            or row[7] != manifest[10]
            or row[8] != manifest[8]
            or not str(row[9]).strip()
            or row[10] is not None
        ):
            raise RuntimeError(
                f"Candidate validation-result mismatch at row {index}"
            )

    accepted = int(
        connection.execute(
            "SELECT COUNT(*) FROM import_manifest "
            "WHERE build_status = 'release_accepted'"
        ).fetchone()[0]
    )
    if accepted:
        raise RuntimeError("Disposable candidate must not be release accepted")
    return len(validation_rows)


def _compare_races(
    raw_connection: sqlite3.Connection,
    candidate_connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    expected_race_count: int,
) -> tuple[
    int,
    int,
    int,
    dict[tuple[tuple[str, object], ...], int],
]:
    raw_cursor = raw_connection.execute(
        """
        SELECT "date", "course", "off", MIN(source_rowid), COUNT(*)
        FROM source_raceform_v1_record
        WHERE source_version_id = 1
          AND source_relation_id = 1
          AND structural_status = 'admitted_runner_record'
        GROUP BY "date", "course", "off"
        ORDER BY MIN(source_rowid)
        """
    )
    candidate_cursor = candidate_connection.execute(
        """
        SELECT source_race_occurrence_id, source_race_occurrence_code,
               source_version_id, raw_date, raw_course, raw_off,
               admitted_runner_count, governance_release_id
        FROM core_source_race_occurrence
        ORDER BY source_race_occurrence_id
        """
    )

    grouping_comparisons = 0
    code_comparisons = 0
    count_comparisons = 0
    prior_minimum = 0
    key_to_id: dict[tuple[tuple[str, object], ...], int] = {}
    sentinel = object()
    for expected_id, pair in enumerate(
        zip_longest(raw_cursor, candidate_cursor, fillvalue=sentinel),
        start=1,
    ):
        raw_row, candidate_row = pair
        if raw_row is sentinel or candidate_row is sentinel:
            raise RuntimeError("Candidate race population length mismatch")
        race_id = int(candidate_row[0])
        if race_id != expected_id:
            raise RuntimeError("Candidate race integer ids are not sequential")
        minimum = int(raw_row[3])
        if minimum <= prior_minimum:
            raise RuntimeError("Raw race-group order is not canonical")
        prior_minimum = minimum

        expected_code = source_race_occurrence_code(source_sha256, expected_id)
        if candidate_row[1] != expected_code:
            raise RuntimeError(f"Candidate race code mismatch at race {expected_id}")
        code_comparisons += 1

        if candidate_row[2] != 1 or candidate_row[7] != 1:
            raise RuntimeError(f"Candidate race lineage mismatch at race {expected_id}")
        for raw_value, candidate_value in zip(
            raw_row[:3],
            candidate_row[3:6],
            strict=True,
        ):
            if not _same_value(raw_value, candidate_value):
                raise RuntimeError(
                    f"Candidate race grouping mismatch at race {expected_id}"
                )
        grouping_comparisons += 1

        if int(candidate_row[6]) != int(raw_row[4]):
            raise RuntimeError(
                f"Candidate race runner count mismatch at race {expected_id}"
            )
        count_comparisons += 1

        key = _race_key((raw_row[0], raw_row[1], raw_row[2]))
        if key in key_to_id:
            raise RuntimeError("Canonical race grouping produced a duplicate key")
        key_to_id[key] = expected_id

    if grouping_comparisons != expected_race_count:
        raise RuntimeError(
            f"Candidate race count mismatch: expected {expected_race_count}; "
            f"observed {grouping_comparisons}"
        )
    return grouping_comparisons, code_comparisons, count_comparisons, key_to_id


def _compare_runners(
    raw_connection: sqlite3.Connection,
    candidate_connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
    race_ids: dict[tuple[tuple[str, object], ...], int],
) -> tuple[int, int]:
    raw_cursor = raw_connection.execute(
        """
        SELECT source_record_id, source_rowid, structural_status,
               "date", "course", "off"
        FROM source_raceform_v1_record
        WHERE source_version_id = 1
          AND source_relation_id = 1
          AND structural_status = 'admitted_runner_record'
        ORDER BY source_rowid
        """
    )
    candidate_cursor = candidate_connection.execute(
        """
        SELECT runner.runner_participation_id,
               runner.runner_participation_code,
               runner.source_race_occurrence_id,
               runner.source_record_id,
               runner.source_record_status,
               runner.governance_release_id,
               raw.source_rowid, raw."date", raw."course", raw."off",
               race.raw_date, race.raw_course, race.raw_off
        FROM core_runner_participation AS runner
        JOIN source_raceform_v1_record AS raw
          ON raw.source_record_id = runner.source_record_id
        JOIN core_source_race_occurrence AS race
          ON race.source_race_occurrence_id = runner.source_race_occurrence_id
        ORDER BY runner.runner_participation_id
        """
    )

    lineage_comparisons = 0
    code_comparisons = 0
    sentinel = object()
    prior_rowid = 0
    for expected_id, pair in enumerate(
        zip_longest(raw_cursor, candidate_cursor, fillvalue=sentinel),
        start=1,
    ):
        raw_row, candidate_row = pair
        if raw_row is sentinel or candidate_row is sentinel:
            raise RuntimeError("Candidate runner population length mismatch")
        source_record_id = int(raw_row[0])
        source_rowid = int(raw_row[1])
        if source_rowid <= prior_rowid:
            raise RuntimeError("Raw admitted source rowids are not increasing")
        prior_rowid = source_rowid

        if int(candidate_row[0]) != expected_id:
            raise RuntimeError("Candidate runner integer ids are not sequential")
        expected_code = runner_participation_code(source_sha256, source_rowid)
        if candidate_row[1] != expected_code:
            raise RuntimeError(
                f"Candidate runner code mismatch at runner {expected_id}"
            )
        code_comparisons += 1

        expected_race_id = race_ids.get(
            _race_key((raw_row[3], raw_row[4], raw_row[5]))
        )
        if expected_race_id is None:
            raise RuntimeError(
                f"Raw runner lacks a reconstructed race at source rowid {source_rowid}"
            )
        if (
            int(candidate_row[2]) != expected_race_id
            or int(candidate_row[3]) != source_record_id
            or candidate_row[4] != raw_row[2]
            or candidate_row[5] != 1
            or int(candidate_row[6]) != source_rowid
        ):
            raise RuntimeError(
                f"Candidate runner lineage mismatch at runner {expected_id}"
            )

        for raw_value, candidate_raw, candidate_race in zip(
            raw_row[3:6],
            candidate_row[7:10],
            candidate_row[10:13],
            strict=True,
        ):
            if not (
                _same_value(raw_value, candidate_raw)
                and _same_value(raw_value, candidate_race)
            ):
                raise RuntimeError(
                    f"Candidate runner race grouping mismatch at runner {expected_id}"
                )
        lineage_comparisons += 1

    if lineage_comparisons != baseline.admitted_record_count:
        raise RuntimeError(
            f"Candidate runner count mismatch: expected "
            f"{baseline.admitted_record_count}; observed {lineage_comparisons}"
        )
    return lineage_comparisons, code_comparisons


def validate_minimum_core_candidate(
    source_path: str | Path,
    raw_mirror_candidate_path: str | Path,
    candidate_path: str | Path,
    *,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    expected_race_count: int = EXPECTED_RACE_OCCURRENCE_COUNT,
    batch_size: int = 5_000,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
    expected_raw_mirror_sha256: bytes = VALIDATED_RAW_MIRROR_CANDIDATE_SHA256,
    expected_candidate_sha256: bytes = BUILT_MINIMUM_CORE_CANDIDATE_SHA256,
) -> MinimumCoreValidationSummary:
    source = Path(source_path).expanduser().resolve()
    raw_candidate = Path(raw_mirror_candidate_path).expanduser().resolve()
    candidate = Path(candidate_path).expanduser().resolve()
    batch_size = _positive_integer(batch_size, name="batch_size")
    expected_race_count = _positive_integer(
        expected_race_count,
        name="expected_race_count",
    )
    expected_source_sha256 = _expected_hash(
        expected_source_sha256,
        name="expected_source_sha256",
    )
    expected_raw_mirror_sha256 = _expected_hash(
        expected_raw_mirror_sha256,
        name="expected_raw_mirror_sha256",
    )
    expected_candidate_sha256 = _expected_hash(
        expected_candidate_sha256,
        name="expected_candidate_sha256",
    )

    source_hash = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    raw_hash = _validate_hash(
        raw_candidate,
        expected_raw_mirror_sha256,
        label="Raw-mirror candidate",
    )
    candidate_hash = _validate_hash(
        candidate,
        expected_candidate_sha256,
        label="Minimum-core candidate",
    )
    source_size = source.stat().st_size
    raw_size = raw_candidate.stat().st_size
    candidate_size = candidate.stat().st_size

    started = perf_counter()
    with connect_read_only(raw_candidate) as raw_connection, connect_read_only(
        candidate
    ) as candidate_connection:
        configure_governed_connection(raw_connection, query_only=True)
        configure_governed_connection(candidate_connection, query_only=True)

        quick, foreign_keys, application_id, user_version = _validate_structure(
            candidate_connection
        )
        metadata_comparisons = _compare_metadata(
            raw_connection,
            candidate_connection,
        )
        (
            raw_record_comparisons,
            raw_value_comparisons,
            storage_class_comparisons,
            source_code_comparisons,
            status_comparisons,
            stored_fingerprint_comparisons,
            recomputed_fingerprint_comparisons,
            batch_count,
        ) = _compare_raw_records(
            raw_connection,
            candidate_connection,
            source_sha256=source_hash,
            baseline=baseline,
            batch_size=batch_size,
        )
        governance_commit = _validate_governance(
            candidate_connection,
            source_sha256=source_hash,
        )
        manifest_result_count = _validate_manifest(
            candidate_connection,
            baseline=baseline,
            expected_race_count=expected_race_count,
            governance_commit=governance_commit,
        )
        (
            race_grouping_comparisons,
            race_code_comparisons,
            race_count_comparisons,
            race_ids,
        ) = _compare_races(
            raw_connection,
            candidate_connection,
            source_sha256=source_hash,
            expected_race_count=expected_race_count,
        )
        runner_lineage_comparisons, runner_code_comparisons = _compare_runners(
            raw_connection,
            candidate_connection,
            source_sha256=source_hash,
            baseline=baseline,
            race_ids=race_ids,
        )

    elapsed = perf_counter() - started
    source_unchanged = sha256_file(source) == source_hash
    raw_unchanged = sha256_file(raw_candidate) == raw_hash
    candidate_unchanged = sha256_file(candidate) == candidate_hash
    _require_file(source, label="Source Version 1")
    _require_file(raw_candidate, label="Raw-mirror candidate")
    _require_file(candidate, label="Minimum-core candidate")
    if not source_unchanged:
        raise RuntimeError("Source Version 1 hash changed during validation")
    if not raw_unchanged:
        raise RuntimeError("Raw-mirror candidate hash changed during validation")
    if not candidate_unchanged:
        raise RuntimeError("Minimum-core candidate hash changed during validation")

    rows_per_second = (
        raw_record_comparisons / elapsed if elapsed > 0 else float("inf")
    )
    return MinimumCoreValidationSummary(
        source_path=str(source),
        raw_mirror_candidate_path=str(raw_candidate),
        candidate_path=str(candidate),
        source_file_sha256_hex=source_hash.hex(),
        raw_mirror_candidate_sha256_hex=raw_hash.hex(),
        candidate_file_sha256_hex=candidate_hash.hex(),
        source_file_size_bytes=source_size,
        raw_mirror_candidate_file_size_bytes=raw_size,
        candidate_file_size_bytes=candidate_size,
        physical_record_count=baseline.physical_record_count,
        admitted_record_count=baseline.admitted_record_count,
        excluded_record_count=baseline.excluded_record_count,
        metadata_row_comparisons=metadata_comparisons,
        raw_record_comparisons=raw_record_comparisons,
        raw_value_comparisons=raw_value_comparisons,
        storage_class_comparisons=storage_class_comparisons,
        source_record_code_comparisons=source_code_comparisons,
        structural_status_comparisons=status_comparisons,
        stored_fingerprint_comparisons=stored_fingerprint_comparisons,
        recomputed_fingerprint_comparisons=recomputed_fingerprint_comparisons,
        race_grouping_comparisons=race_grouping_comparisons,
        race_code_comparisons=race_code_comparisons,
        race_runner_count_comparisons=race_count_comparisons,
        runner_lineage_comparisons=runner_lineage_comparisons,
        runner_code_comparisons=runner_code_comparisons,
        manifest_validation_result_count=manifest_result_count,
        batch_size=batch_size,
        batch_count=batch_count,
        validation_elapsed_seconds=elapsed,
        rows_per_second=rows_per_second,
        quick_check=quick,
        foreign_key_check_rows=foreign_keys,
        application_id=application_id,
        user_version=user_version,
        schema_inventory_matched=True,
        metadata_reconciliation_passed=True,
        governance_reconciliation_passed=True,
        manifest_reconciliation_passed=True,
        source_hash_unchanged=True,
        raw_mirror_candidate_hash_unchanged=True,
        candidate_hash_unchanged=True,
        persisted_readback_passed=True,
        release_accepted=False,
    )
