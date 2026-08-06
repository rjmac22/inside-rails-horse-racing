"""Independent validation for the persisted Source Version 1 core prototype."""

from __future__ import annotations

from dataclasses import dataclass
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
_REPOSITORY_COMMIT = re.compile(r"[0-9a-f]{40}")
_SOURCE_METADATA_TABLES = (
    "source_provider",
    "source_product",
    "source_version",
    "source_relation",
    "source_relation_field",
)
_EXPECTED_GOVERNANCE_EVIDENCE = (
    (
        1,
        1,
        "document",
        "docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md",
        None,
        "Accepted bounded authorisation for the Source Version 1 structural core.",
    ),
    (
        2,
        1,
        "document",
        "docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md",
        None,
        "Accepted physical schema and identifier contract for minimum core version 1.",
    ),
    (
        3,
        1,
        "validator",
        "scripts/validate_raw_mirror_candidate.py",
        None,
        "Independent source-wide validation of the complete disposable raw mirror.",
    ),
    (
        4,
        1,
        "governed_output",
        "docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md",
        None,
        "Recorded full-build and persisted-readback evidence for the exact raw mirror.",
    ),
)


@dataclass(frozen=True)
class _RaceGroup:
    race_sequence: int
    raw_date: object
    raw_course: object
    raw_off: object
    minimum_source_rowid: int
    admitted_runner_count: int

    @property
    def key(self) -> tuple[object, object, object]:
        return (self.raw_date, self.raw_course, self.raw_off)


@dataclass(frozen=True)
class _Record:
    source_record_id: int
    source_record_code: str
    source_version_id: int
    source_relation_id: int
    source_rowid: int
    structural_status: str
    exclusion_reason: object
    row_sha256: bytes
    values: tuple[object, ...]
    storage_classes: tuple[str, ...]


@dataclass(frozen=True)
class CoreStructureValidationSummary:
    source_path: str
    raw_mirror_candidate_path: str
    prototype_path: str
    source_file_sha256_hex: str
    raw_mirror_candidate_sha256_hex: str
    prototype_file_sha256_hex: str
    source_file_size_bytes: int
    raw_mirror_candidate_file_size_bytes: int
    prototype_file_size_bytes: int
    selected_race_count: int
    selected_minimum_source_rowids: tuple[int, ...]
    compared_raw_record_count: int
    compared_admitted_record_count: int
    compared_excluded_record_count: int
    raw_value_comparisons: int
    storage_class_comparisons: int
    source_record_code_comparisons: int
    structural_status_comparisons: int
    stored_fingerprint_comparisons: int
    recomputed_fingerprint_comparisons: int
    race_code_comparisons: int
    race_grouping_comparisons: int
    race_runner_count_comparisons: int
    runner_code_comparisons: int
    runner_lineage_comparisons: int
    governance_reconciliation_passed: bool
    metadata_reconciliation_passed: bool
    schema_inventory_matched: bool
    quick_check: str
    foreign_key_check_rows: int
    application_id: int
    user_version: int
    validation_elapsed_seconds: float
    source_hash_unchanged: bool
    raw_mirror_candidate_hash_unchanged: bool
    prototype_hash_unchanged: bool
    persisted_readback_passed: bool


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


def _require_file_without_sidecars(path: Path, *, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    present = [sidecar for sidecar in _sidecars(path) if sidecar.exists()]
    if present:
        raise RuntimeError(
            f"{label} has unexpected SQLite sidecars: "
            + ", ".join(str(path) for path in present)
        )


def _validate_file_hash(path: Path, expected: bytes, *, label: str) -> bytes:
    _require_file_without_sidecars(path, label=label)
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


def _expected_schema_inventory() -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(":memory:")
    try:
        create_minimum_core_schema(connection)
        return schema_inventory(connection)
    finally:
        connection.close()


def _validate_structure(
    connection: sqlite3.Connection,
    *,
    label: str,
) -> tuple[str, int, int, int]:
    if schema_inventory(connection) != _expected_schema_inventory():
        raise RuntimeError(f"{label} schema inventory mismatch")

    application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if application_id != APPLICATION_ID:
        raise RuntimeError(f"Unexpected {label} application_id: {application_id}")
    if user_version != SCHEMA_VERSION:
        raise RuntimeError(f"Unexpected {label} user_version: {user_version}")

    quick_row = connection.execute("PRAGMA quick_check").fetchone()
    quick_check = "" if quick_row is None else str(quick_row[0])
    if quick_check != "ok":
        raise RuntimeError(f"{label} quick_check failed: {quick_check!r}")
    foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
    if foreign_key_rows:
        raise RuntimeError(
            f"{label} foreign_key_check returned {foreign_key_rows} rows"
        )
    return quick_check, foreign_key_rows, application_id, user_version


def _validate_raw_mirror_boundary(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
) -> None:
    source_version = connection.execute(
        """
        SELECT file_sha256, physical_record_count, admitted_record_count,
               excluded_record_count, admission_predicate
        FROM source_version
        WHERE source_version_id = 1
        """
    ).fetchone()
    expected_source_version = (
        source_sha256,
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        "rowid <> 1",
    )
    if source_version != expected_source_version:
        raise RuntimeError("Raw-mirror source-version metadata mismatch")

    population = connection.execute(
        """
        SELECT COUNT(*),
               SUM(structural_status = 'admitted_runner_record'),
               SUM(structural_status = 'retained_excluded_record')
        FROM source_raceform_v1_record
        WHERE source_version_id = 1 AND source_relation_id = 1
        """
    ).fetchone()
    expected_population = (
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
    )
    if population is None or tuple(int(value) for value in population) != expected_population:
        raise RuntimeError(
            "Raw-mirror population mismatch: "
            f"expected {expected_population!r}; observed {population!r}"
        )

    downstream = connection.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM governance_method),
            (SELECT COUNT(*) FROM governance_release),
            (SELECT COUNT(*) FROM governance_release_evidence),
            (SELECT COUNT(*) FROM core_source_race_occurrence),
            (SELECT COUNT(*) FROM core_runner_participation),
            (SELECT COUNT(*) FROM import_manifest),
            (SELECT COUNT(*) FROM import_validation_result)
        """
    ).fetchone()
    if downstream is None or tuple(int(value) for value in downstream) != (0,) * 7:
        raise RuntimeError(
            "Raw-mirror candidate is not at the required raw-only boundary"
        )


def _compare_source_metadata(
    candidate: sqlite3.Connection,
    prototype: sqlite3.Connection,
) -> None:
    for table in _SOURCE_METADATA_TABLES:
        expected = candidate.execute(
            f"SELECT * FROM {quote_identifier(table)} ORDER BY 1"
        ).fetchall()
        observed = prototype.execute(
            f"SELECT * FROM {quote_identifier(table)} ORDER BY 1"
        ).fetchall()
        if observed != expected:
            raise RuntimeError(f"Prototype source metadata mismatch in {table}")


def _select_groups(
    candidate: sqlite3.Connection,
    race_count: int,
) -> tuple[_RaceGroup, ...]:
    rows = candidate.execute(
        """
        SELECT "date", "course", "off", MIN(source_rowid), COUNT(*)
        FROM source_raceform_v1_record
        WHERE source_version_id = 1
          AND source_relation_id = 1
          AND structural_status = 'admitted_runner_record'
        GROUP BY "date", "course", "off"
        ORDER BY MIN(source_rowid)
        LIMIT ?
        """,
        (race_count,),
    ).fetchall()
    if len(rows) != race_count:
        raise RuntimeError(
            f"Requested {race_count} race groups but raw mirror supplied {len(rows)}"
        )
    groups = tuple(
        _RaceGroup(sequence, row[0], row[1], row[2], int(row[3]), int(row[4]))
        for sequence, row in enumerate(rows, start=1)
    )
    minimums = [group.minimum_source_rowid for group in groups]
    if minimums != sorted(set(minimums)):
        raise RuntimeError("Expected race groups lack unique increasing minimum rowids")
    return groups


def _record_select_sql() -> str:
    raw = ", ".join(quote_identifier(name) for name in RAW_COLUMN_NAMES)
    types = ", ".join(
        f"typeof({quote_identifier(name)})" for name in RAW_COLUMN_NAMES
    )
    return f"""
        SELECT source_record_id, source_record_code, source_version_id,
               source_relation_id, source_rowid, structural_status,
               exclusion_reason, row_sha256, {raw}, {types}
        FROM source_raceform_v1_record
    """


def _as_record(row: tuple[object, ...]) -> _Record:
    value_start = 8
    value_end = value_start + len(RAW_COLUMN_NAMES)
    return _Record(
        source_record_id=int(row[0]),
        source_record_code=str(row[1]),
        source_version_id=int(row[2]),
        source_relation_id=int(row[3]),
        source_rowid=int(row[4]),
        structural_status=str(row[5]),
        exclusion_reason=row[6],
        row_sha256=bytes(row[7]),
        values=tuple(row[value_start:value_end]),
        storage_classes=tuple(str(value) for value in row[value_end:]),
    )


def _expected_records(
    candidate: sqlite3.Connection,
    groups: tuple[_RaceGroup, ...],
    source_sha256: bytes,
) -> tuple[tuple[_Record, ...], dict[int, int]]:
    excluded_row = candidate.execute(
        _record_select_sql() + " WHERE source_rowid = 1"
    ).fetchone()
    if excluded_row is None:
        raise RuntimeError("Raw mirror lacks retained source rowid 1")

    rows: list[tuple[object, ...]] = [excluded_row]
    race_by_rowid: dict[int, int] = {}
    for group in groups:
        group_rows = candidate.execute(
            _record_select_sql()
            + """
              WHERE source_version_id = 1
                AND source_relation_id = 1
                AND structural_status = 'admitted_runner_record'
                AND "date" IS ? AND "course" IS ? AND "off" IS ?
              ORDER BY source_rowid
              """,
            group.key,
        ).fetchall()
        if len(group_rows) != group.admitted_runner_count:
            raise RuntimeError(
                f"Raw-mirror runner count mismatch for race {group.race_sequence}"
            )
        if int(group_rows[0][4]) != group.minimum_source_rowid:
            raise RuntimeError(
                f"Raw-mirror minimum rowid mismatch for race {group.race_sequence}"
            )
        for row in group_rows:
            source_rowid = int(row[4])
            if source_rowid in race_by_rowid:
                raise RuntimeError("Selected race groups overlap in source rowids")
            race_by_rowid[source_rowid] = group.race_sequence
        rows.extend(group_rows)

    records = tuple(sorted((_as_record(row) for row in rows), key=lambda row: row.source_rowid))
    for record in records:
        if record.source_version_id != 1 or record.source_relation_id != 1:
            raise RuntimeError(
                f"Raw-mirror lineage mismatch for source rowid {record.source_rowid}"
            )
        expected_code = source_record_code(source_sha256, record.source_rowid)
        if record.source_record_code != expected_code:
            raise RuntimeError(
                f"Raw-mirror source-record code mismatch for rowid {record.source_rowid}"
            )
        expected_status = (
            "retained_excluded_record"
            if record.source_rowid == 1
            else "admitted_runner_record"
        )
        if record.structural_status != expected_status:
            raise RuntimeError(
                f"Raw-mirror status mismatch for source rowid {record.source_rowid}"
            )
        if record.source_rowid == 1:
            if not record.exclusion_reason:
                raise RuntimeError("Retained source rowid 1 lacks an exclusion reason")
        elif record.exclusion_reason is not None:
            raise RuntimeError(
                f"Admitted rowid {record.source_rowid} has an exclusion reason"
            )
        if raceform_v1_row_sha256(record.values) != record.row_sha256:
            raise RuntimeError(
                f"Raw-mirror fingerprint mismatch for rowid {record.source_rowid}"
            )
    return records, race_by_rowid


def _validate_governance(
    prototype: sqlite3.Connection,
    *,
    source_sha256: bytes,
) -> None:
    methods = prototype.execute(
        "SELECT * FROM governance_method ORDER BY governance_method_id"
    ).fetchall()
    if len(methods) != 1:
        raise RuntimeError("Prototype must contain exactly one governance method")
    method = methods[0]
    expected_method_prefix = (
        1,
        governance_method_code("source-v1-structure", 1),
        "Source Version 1 structural reconstruction",
        1,
    )
    if method[:4] != expected_method_prefix:
        raise RuntimeError("Prototype governance method metadata mismatch")
    method_commit = str(method[4])
    if _REPOSITORY_COMMIT.fullmatch(method_commit) is None:
        raise RuntimeError("Prototype governance method commit is invalid")
    if method[5] != (
        "Groups admitted raw records by exact date + course + off and creates "
        "one runner participation per admitted source record."
    ):
        raise RuntimeError("Prototype governance method description mismatch")
    method_created_at = str(method[6])
    if not method_created_at.endswith("Z"):
        raise RuntimeError("Prototype governance method timestamp is invalid")

    releases = prototype.execute(
        "SELECT * FROM governance_release ORDER BY governance_release_id"
    ).fetchall()
    if len(releases) != 1:
        raise RuntimeError("Prototype must contain exactly one governance release")
    release = releases[0]
    expected_release_prefix = (
        1,
        governance_release_code(source_sha256, "source-v1-structure", 1),
        1,
        1,
        "accepted",
    )
    if release[:5] != expected_release_prefix:
        raise RuntimeError("Prototype governance release metadata mismatch")
    if release[5] != method_created_at[:10]:
        raise RuntimeError("Prototype governance accepted date mismatch")
    if release[6] != method_commit:
        raise RuntimeError("Prototype governance repository commits disagree")
    if release[7] != "rowid <> 1":
        raise RuntimeError("Prototype governance population predicate mismatch")
    if release[8] != (
        "Accepted Source Version 1 structural method; this database remains "
        "a bounded prototype, not an accepted database release."
    ):
        raise RuntimeError("Prototype governance release description mismatch")
    if release[9] is not None or release[10] != method_created_at:
        raise RuntimeError("Prototype governance release lifecycle mismatch")

    evidence = prototype.execute(
        "SELECT * FROM governance_release_evidence "
        "ORDER BY governance_release_evidence_id"
    ).fetchall()
    if evidence != list(_EXPECTED_GOVERNANCE_EVIDENCE):
        raise RuntimeError("Prototype governance evidence mismatch")


def _validate_raw_records(
    prototype: sqlite3.Connection,
    *,
    expected_records: tuple[_Record, ...],
    source_sha256: bytes,
) -> tuple[int, int, int, int, int, int]:
    observed_rows = prototype.execute(
        _record_select_sql() + " ORDER BY source_rowid"
    ).fetchall()
    observed_records = tuple(_as_record(row) for row in observed_rows)
    if len(observed_records) != len(expected_records):
        raise RuntimeError(
            "Prototype raw population mismatch: "
            f"expected {len(expected_records)}; observed {len(observed_records)}"
        )

    value_comparisons = 0
    storage_comparisons = 0
    code_comparisons = 0
    status_comparisons = 0
    stored_fingerprints = 0
    recomputed_fingerprints = 0
    for expected, observed in zip(expected_records, observed_records, strict=True):
        if (
            observed.source_record_id != expected.source_record_id
            or observed.source_version_id != expected.source_version_id
            or observed.source_relation_id != expected.source_relation_id
            or observed.source_rowid != expected.source_rowid
            or observed.exclusion_reason != expected.exclusion_reason
        ):
            raise RuntimeError(
                f"Prototype raw lineage mismatch for source rowid {expected.source_rowid}"
            )

        expected_code = source_record_code(source_sha256, expected.source_rowid)
        if observed.source_record_code != expected_code:
            raise RuntimeError(
                f"Prototype source-record code mismatch for rowid {expected.source_rowid}"
            )
        code_comparisons += 1
        if observed.structural_status != expected.structural_status:
            raise RuntimeError(
                f"Prototype status mismatch for source rowid {expected.source_rowid}"
            )
        status_comparisons += 1

        for ordinal, (expected_value, observed_value) in enumerate(
            zip(expected.values, observed.values, strict=True)
        ):
            if not _same_value(expected_value, observed_value):
                raise RuntimeError(
                    "Prototype raw value mismatch at source rowid "
                    f"{expected.source_rowid}, ordinal {ordinal}"
                )
            value_comparisons += 1
        if observed.storage_classes != expected.storage_classes:
            raise RuntimeError(
                "Prototype storage-class mismatch for source rowid "
                f"{expected.source_rowid}"
            )
        storage_comparisons += len(RAW_COLUMN_NAMES)
        if observed.row_sha256 != expected.row_sha256:
            raise RuntimeError(
                f"Prototype stored fingerprint mismatch for rowid {expected.source_rowid}"
            )
        stored_fingerprints += 1
        if raceform_v1_row_sha256(observed.values) != expected.row_sha256:
            raise RuntimeError(
                "Prototype recomputed fingerprint mismatch for rowid "
                f"{expected.source_rowid}"
            )
        recomputed_fingerprints += 1

    return (
        value_comparisons,
        storage_comparisons,
        code_comparisons,
        status_comparisons,
        stored_fingerprints,
        recomputed_fingerprints,
    )


def _validate_core(
    prototype: sqlite3.Connection,
    *,
    groups: tuple[_RaceGroup, ...],
    expected_records: tuple[_Record, ...],
    race_by_rowid: dict[int, int],
    source_sha256: bytes,
) -> tuple[int, int, int, int, int]:
    observed_races = prototype.execute(
        """
        SELECT source_race_occurrence_id, source_race_occurrence_code,
               source_version_id, raw_date, raw_course, raw_off,
               admitted_runner_count, governance_release_id
        FROM core_source_race_occurrence
        ORDER BY source_race_occurrence_id
        """
    ).fetchall()
    if len(observed_races) != len(groups):
        raise RuntimeError("Prototype race count mismatch")

    race_codes = 0
    race_groups = 0
    race_runner_counts = 0
    for group, observed in zip(groups, observed_races, strict=True):
        expected_code = source_race_occurrence_code(
            source_sha256,
            group.race_sequence,
        )
        if observed[0] != group.race_sequence or observed[1] != expected_code:
            raise RuntimeError(
                f"Prototype race identifier mismatch for sequence {group.race_sequence}"
            )
        race_codes += 1
        if (
            observed[2] != 1
            or not _same_value(observed[3], group.raw_date)
            or not _same_value(observed[4], group.raw_course)
            or not _same_value(observed[5], group.raw_off)
            or observed[7] != 1
        ):
            raise RuntimeError(
                f"Prototype race grouping mismatch for sequence {group.race_sequence}"
            )
        race_groups += 1
        if observed[6] != group.admitted_runner_count:
            raise RuntimeError(
                f"Prototype runner count mismatch for race {group.race_sequence}"
            )
        race_runner_counts += 1

    admitted = tuple(
        record
        for record in expected_records
        if record.structural_status == "admitted_runner_record"
    )
    observed_runners = prototype.execute(
        """
        SELECT runner_participation_id, runner_participation_code,
               source_race_occurrence_id, source_record_id,
               source_record_status, governance_release_id
        FROM core_runner_participation
        ORDER BY runner_participation_id
        """
    ).fetchall()
    if len(observed_runners) != len(admitted):
        raise RuntimeError("Prototype runner participation count mismatch")

    runner_codes = 0
    runner_lineage = 0
    for runner_id, (record, observed) in enumerate(
        zip(admitted, observed_runners, strict=True),
        start=1,
    ):
        expected_code = runner_participation_code(source_sha256, record.source_rowid)
        if observed[0] != runner_id or observed[1] != expected_code:
            raise RuntimeError(
                f"Prototype runner identifier mismatch for rowid {record.source_rowid}"
            )
        runner_codes += 1
        if (
            observed[2] != race_by_rowid[record.source_rowid]
            or observed[3] != record.source_record_id
            or observed[4] != "admitted_runner_record"
            or observed[5] != 1
        ):
            raise RuntimeError(
                f"Prototype runner lineage mismatch for rowid {record.source_rowid}"
            )
        runner_lineage += 1

    mismatches = prototype.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT race.source_race_occurrence_id
            FROM core_source_race_occurrence AS race
            LEFT JOIN core_runner_participation AS runner
              ON runner.source_race_occurrence_id = race.source_race_occurrence_id
            GROUP BY race.source_race_occurrence_id, race.admitted_runner_count
            HAVING COUNT(runner.runner_participation_id) <> race.admitted_runner_count
        )
        """
    ).fetchone()[0]
    if mismatches:
        raise RuntimeError("Prototype race/runner population reconciliation failed")

    if prototype.execute("SELECT COUNT(*) FROM import_manifest").fetchone()[0]:
        raise RuntimeError("Core prototype must not contain an import manifest")
    if prototype.execute(
        "SELECT COUNT(*) FROM import_validation_result"
    ).fetchone()[0]:
        raise RuntimeError("Core prototype must not contain validation results")

    return (
        race_codes,
        race_groups,
        race_runner_counts,
        runner_codes,
        runner_lineage,
    )


def validate_core_structure_prototype(
    source_path: str | Path,
    raw_mirror_candidate_path: str | Path,
    prototype_path: str | Path,
    *,
    race_count: int = 3,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
    expected_candidate_sha256: bytes = VALIDATED_RAW_MIRROR_CANDIDATE_SHA256,
) -> CoreStructureValidationSummary:
    """Independently reconcile a persisted core prototype to the exact raw mirror."""

    started = perf_counter()
    race_count = _positive_integer(race_count, name="race_count")
    expected_source_sha256 = _expected_hash(
        expected_source_sha256,
        name="expected_source_sha256",
    )
    expected_candidate_sha256 = _expected_hash(
        expected_candidate_sha256,
        name="expected_candidate_sha256",
    )

    source = Path(source_path).expanduser().resolve()
    candidate_path = Path(raw_mirror_candidate_path).expanduser().resolve()
    prototype_path = Path(prototype_path).expanduser().resolve()
    if len({source, candidate_path, prototype_path}) != 3:
        raise ValueError("Source, raw mirror and prototype paths must differ")

    source_hash_before = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    candidate_hash_before = _validate_file_hash(
        candidate_path,
        expected_candidate_sha256,
        label="Raw-mirror candidate",
    )
    _require_file_without_sidecars(prototype_path, label="Core prototype")
    prototype_hash_before = sha256_file(prototype_path)

    with connect_read_only(candidate_path) as candidate, connect_read_only(
        prototype_path
    ) as prototype:
        configure_governed_connection(candidate, query_only=True)
        configure_governed_connection(prototype, query_only=True)
        _validate_structure(candidate, label="Raw-mirror candidate")
        quick_check, foreign_key_rows, application_id, user_version = _validate_structure(
            prototype,
            label="Core prototype",
        )
        _validate_raw_mirror_boundary(
            candidate,
            source_sha256=source_hash_before,
            baseline=baseline,
        )
        _compare_source_metadata(candidate, prototype)
        groups = _select_groups(candidate, race_count)
        expected_records, race_by_rowid = _expected_records(
            candidate,
            groups,
            source_hash_before,
        )
        _validate_governance(prototype, source_sha256=source_hash_before)
        (
            raw_values,
            storage_classes,
            source_codes,
            statuses,
            stored_fingerprints,
            recomputed_fingerprints,
        ) = _validate_raw_records(
            prototype,
            expected_records=expected_records,
            source_sha256=source_hash_before,
        )
        (
            race_codes,
            race_groups,
            race_runner_counts,
            runner_codes,
            runner_lineage,
        ) = _validate_core(
            prototype,
            groups=groups,
            expected_records=expected_records,
            race_by_rowid=race_by_rowid,
            source_sha256=source_hash_before,
        )

    source_hash_after = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    candidate_hash_after = _validate_file_hash(
        candidate_path,
        expected_candidate_sha256,
        label="Raw-mirror candidate",
    )
    _require_file_without_sidecars(prototype_path, label="Core prototype")
    prototype_hash_after = sha256_file(prototype_path)
    if source_hash_after != source_hash_before:
        raise RuntimeError("Immutable source hash changed during validation")
    if candidate_hash_after != candidate_hash_before:
        raise RuntimeError("Raw-mirror candidate hash changed during validation")
    if prototype_hash_after != prototype_hash_before:
        raise RuntimeError("Core prototype hash changed during validation")

    admitted_count = sum(
        record.structural_status == "admitted_runner_record"
        for record in expected_records
    )
    excluded_count = len(expected_records) - admitted_count
    return CoreStructureValidationSummary(
        source_path=str(source),
        raw_mirror_candidate_path=str(candidate_path),
        prototype_path=str(prototype_path),
        source_file_sha256_hex=source_hash_before.hex(),
        raw_mirror_candidate_sha256_hex=candidate_hash_before.hex(),
        prototype_file_sha256_hex=prototype_hash_before.hex(),
        source_file_size_bytes=source.stat().st_size,
        raw_mirror_candidate_file_size_bytes=candidate_path.stat().st_size,
        prototype_file_size_bytes=prototype_path.stat().st_size,
        selected_race_count=len(groups),
        selected_minimum_source_rowids=tuple(
            group.minimum_source_rowid for group in groups
        ),
        compared_raw_record_count=len(expected_records),
        compared_admitted_record_count=admitted_count,
        compared_excluded_record_count=excluded_count,
        raw_value_comparisons=raw_values,
        storage_class_comparisons=storage_classes,
        source_record_code_comparisons=source_codes,
        structural_status_comparisons=statuses,
        stored_fingerprint_comparisons=stored_fingerprints,
        recomputed_fingerprint_comparisons=recomputed_fingerprints,
        race_code_comparisons=race_codes,
        race_grouping_comparisons=race_groups,
        race_runner_count_comparisons=race_runner_counts,
        runner_code_comparisons=runner_codes,
        runner_lineage_comparisons=runner_lineage,
        governance_reconciliation_passed=True,
        metadata_reconciliation_passed=True,
        schema_inventory_matched=True,
        quick_check=quick_check,
        foreign_key_check_rows=foreign_key_rows,
        application_id=application_id,
        user_version=user_version,
        validation_elapsed_seconds=perf_counter() - started,
        source_hash_unchanged=True,
        raw_mirror_candidate_hash_unchanged=True,
        prototype_hash_unchanged=True,
        persisted_readback_passed=True,
    )
