"""Small persisted Source Version 1 core race-and-runner prototype."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import sqlite3
import struct

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
    configure_governed_connection,
    create_minimum_core_schema,
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
        "validator",
        "scripts/validate_raw_mirror_candidate.py",
        "Independent source-wide validation of the complete disposable raw mirror.",
    ),
    (
        "governed_output",
        "docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md",
        "Recorded full-build and persisted-readback evidence for the exact raw mirror.",
    ),
)
_DATE_INDEX = RAW_COLUMN_NAMES.index("date")
_COURSE_INDEX = RAW_COLUMN_NAMES.index("course")
_OFF_INDEX = RAW_COLUMN_NAMES.index("off")


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
class _RawRecord:
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

    @property
    def race_key(self) -> tuple[object, object, object]:
        return (
            self.values[_DATE_INDEX],
            self.values[_COURSE_INDEX],
            self.values[_OFF_INDEX],
        )


@dataclass(frozen=True)
class CoreStructurePrototypeSummary:
    source_path: str
    raw_mirror_candidate_path: str
    output_path: str
    source_file_sha256_hex: str
    raw_mirror_candidate_sha256_hex: str
    output_file_sha256_hex: str
    selected_race_count: int
    selected_minimum_source_rowids: tuple[int, ...]
    copied_raw_record_count: int
    copied_admitted_record_count: int
    copied_excluded_record_count: int
    core_race_occurrence_count: int
    core_runner_participation_count: int
    candidate_output_value_comparisons: int
    candidate_output_storage_class_comparisons: int
    stored_fingerprint_comparisons: int
    recomputed_fingerprint_comparisons: int
    race_reconciliation_comparisons: int
    runner_reconciliation_comparisons: int
    quick_check: str
    foreign_key_check_rows: int
    source_hash_unchanged: bool
    raw_mirror_candidate_hash_unchanged: bool
    persisted_readback_passed: bool


def _positive_integer(value: int, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _repository_commit(value: str) -> str:
    if not isinstance(value, str) or _REPOSITORY_COMMIT.fullmatch(value) is None:
        raise ValueError("repository_commit must be 40 lowercase hexadecimal characters")
    return value


def _expected_hash(value: bytes, *, name: str) -> bytes:
    if not isinstance(value, bytes) or len(value) != 32:
        raise ValueError(f"{name} must contain exactly 32 bytes")
    return value


def _artifacts(database: Path) -> tuple[Path, ...]:
    return (
        database,
        Path(f"{database}-journal"),
        Path(f"{database}-wal"),
        Path(f"{database}-shm"),
    )


def _remove_output(output: Path) -> None:
    for path in _artifacts(output):
        path.unlink(missing_ok=True)


def _require_no_sidecars(database: Path, *, label: str) -> None:
    sidecars = [path for path in _artifacts(database)[1:] if path.exists()]
    if sidecars:
        raise RuntimeError(
            f"{label} has unexpected SQLite sidecars: "
            + ", ".join(str(path) for path in sidecars)
        )


def _validate_file_hash(
    path: Path,
    expected: bytes,
    *,
    label: str,
) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    _require_no_sidecars(path, label=label)
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


def _validate_raw_candidate(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
) -> None:
    quick = connection.execute("PRAGMA quick_check").fetchone()
    if quick is None or quick[0] != "ok":
        raise RuntimeError(f"Raw-mirror candidate quick_check failed: {quick!r}")
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_keys:
        raise RuntimeError(
            f"Raw-mirror candidate foreign_key_check returned {len(foreign_keys)} rows"
        )

    source_version = connection.execute(
        """
        SELECT file_sha256, physical_record_count, admitted_record_count,
               excluded_record_count, admission_predicate
        FROM source_version
        WHERE source_version_id = 1
        """
    ).fetchone()
    expected_version = (
        source_sha256,
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        "rowid <> 1",
    )
    if source_version != expected_version:
        raise RuntimeError("Raw-mirror candidate source-version metadata mismatch")

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
            "Raw-mirror candidate population mismatch: "
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
            "Raw-mirror candidate is not at the required raw-only boundary: "
            f"{downstream!r}"
        )


def _select_groups(
    connection: sqlite3.Connection,
    race_count: int,
) -> tuple[_RaceGroup, ...]:
    rows = connection.execute(
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
            f"Requested {race_count} race groups but candidate supplied {len(rows)}"
        )
    groups = tuple(
        _RaceGroup(sequence, row[0], row[1], row[2], int(row[3]), int(row[4]))
        for sequence, row in enumerate(rows, start=1)
    )
    minimums = [group.minimum_source_rowid for group in groups]
    if minimums != sorted(set(minimums)):
        raise RuntimeError("Selected race groups lack unique increasing minimum rowids")
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


def _raw_record(row: Sequence[object]) -> _RawRecord:
    value_start = 8
    value_end = value_start + len(RAW_COLUMN_NAMES)
    return _RawRecord(
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


def _selected_records(
    connection: sqlite3.Connection,
    groups: Sequence[_RaceGroup],
    source_sha256: bytes,
) -> tuple[_RawRecord, ...]:
    rows = [
        connection.execute(
            _record_select_sql() + " WHERE source_rowid = 1"
        ).fetchone()
    ]
    if rows[0] is None:
        raise RuntimeError("Raw-mirror candidate lacks retained source rowid 1")

    for group in groups:
        group_rows = connection.execute(
            _record_select_sql()
            + """
              WHERE structural_status = 'admitted_runner_record'
                AND "date" IS ? AND "course" IS ? AND "off" IS ?
              ORDER BY source_rowid
              """,
            group.key,
        ).fetchall()
        if len(group_rows) != group.admitted_runner_count:
            raise RuntimeError(
                f"Candidate runner count changed for race sequence {group.race_sequence}"
            )
        if int(group_rows[0][4]) != group.minimum_source_rowid:
            raise RuntimeError(
                f"Candidate minimum rowid changed for race sequence {group.race_sequence}"
            )
        rows.extend(group_rows)

    records = tuple(_raw_record(row) for row in rows if row is not None)
    rowids = [record.source_rowid for record in records]
    if len(rowids) != len(set(rowids)):
        raise RuntimeError("Selected race groups overlap in source rowids")

    for record in records:
        if record.source_version_id != 1 or record.source_relation_id != 1:
            raise RuntimeError(
                f"Candidate lineage ids mismatch for source rowid {record.source_rowid}"
            )
        expected_code = source_record_code(source_sha256, record.source_rowid)
        if record.source_record_code != expected_code:
            raise RuntimeError(
                f"Candidate source-record code mismatch for rowid {record.source_rowid}"
            )
        expected_status = (
            "retained_excluded_record"
            if record.source_rowid == 1
            else "admitted_runner_record"
        )
        if record.structural_status != expected_status:
            raise RuntimeError(
                f"Candidate status mismatch for source rowid {record.source_rowid}"
            )
        if record.source_rowid == 1 and not record.exclusion_reason:
            raise RuntimeError("Excluded source rowid 1 lacks an exclusion reason")
        if record.source_rowid != 1 and record.exclusion_reason is not None:
            raise RuntimeError(
                f"Admitted source rowid {record.source_rowid} has an exclusion reason"
            )
        if raceform_v1_row_sha256(record.values) != record.row_sha256:
            raise RuntimeError(
                f"Candidate fingerprint mismatch for source rowid {record.source_rowid}"
            )
    return records


def _copy_metadata(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
) -> None:
    for table in _SOURCE_METADATA_TABLES:
        columns = source.execute(
            f"PRAGMA table_info({quote_identifier(table)})"
        ).fetchall()
        names = [str(row[1]) for row in columns]
        quoted = ", ".join(quote_identifier(name) for name in names)
        rows = source.execute(
            f"SELECT {quoted} FROM {quote_identifier(table)} ORDER BY 1"
        ).fetchall()
        placeholders = ", ".join("?" for _ in names)
        target.executemany(
            f"INSERT INTO {quote_identifier(table)} ({quoted}) VALUES ({placeholders})",
            rows,
        )


def _insert_records(
    connection: sqlite3.Connection,
    records: Sequence[_RawRecord],
) -> None:
    names = [
        "source_record_id",
        "source_record_code",
        "source_version_id",
        "source_relation_id",
        "source_rowid",
        "structural_status",
        "exclusion_reason",
        "row_sha256",
        *RAW_COLUMN_NAMES,
    ]
    quoted = ", ".join(quote_identifier(name) for name in names)
    placeholders = ", ".join("?" for _ in names)
    connection.executemany(
        f"INSERT INTO source_raceform_v1_record ({quoted}) VALUES ({placeholders})",
        [
            (
                record.source_record_id,
                record.source_record_code,
                record.source_version_id,
                record.source_relation_id,
                record.source_rowid,
                record.structural_status,
                record.exclusion_reason,
                record.row_sha256,
                *record.values,
            )
            for record in records
        ],
    )


def _insert_governance(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    repository_commit: str,
    timestamp: str,
) -> None:
    connection.execute(
        "INSERT INTO governance_method VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            governance_method_code("source-v1-structure", 1),
            "Source Version 1 structural reconstruction",
            1,
            repository_commit,
            "Groups admitted raw records by exact date + course + off and creates "
            "one runner participation per admitted source record.",
            timestamp,
        ),
    )
    connection.execute(
        "INSERT INTO governance_release VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)",
        (
            1,
            governance_release_code(source_sha256, "source-v1-structure", 1),
            1,
            1,
            "accepted",
            timestamp[:10],
            repository_commit,
            "rowid <> 1",
            "Accepted Source Version 1 structural method; this database remains "
            "a bounded prototype, not an accepted database release.",
            timestamp,
        ),
    )
    connection.executemany(
        "INSERT INTO governance_release_evidence VALUES (?, 1, ?, ?, NULL, ?)",
        [
            (index, evidence_type, reference, description)
            for index, (evidence_type, reference, description) in enumerate(
                _GOVERNANCE_EVIDENCE,
                start=1,
            )
        ],
    )


def _insert_core(
    connection: sqlite3.Connection,
    *,
    groups: Sequence[_RaceGroup],
    records: Sequence[_RawRecord],
    source_sha256: bytes,
) -> None:
    connection.executemany(
        "INSERT INTO core_source_race_occurrence VALUES (?, ?, 1, ?, ?, ?, ?, 1)",
        [
            (
                group.race_sequence,
                source_race_occurrence_code(source_sha256, group.race_sequence),
                group.raw_date,
                group.raw_course,
                group.raw_off,
                group.admitted_runner_count,
            )
            for group in groups
        ],
    )
    group_ids = {group.key: group.race_sequence for group in groups}
    admitted = sorted(
        (
            record
            for record in records
            if record.structural_status == "admitted_runner_record"
        ),
        key=lambda record: record.source_rowid,
    )
    connection.executemany(
        "INSERT INTO core_runner_participation VALUES (?, ?, ?, ?, ?, 1)",
        [
            (
                runner_id,
                runner_participation_code(source_sha256, record.source_rowid),
                group_ids[record.race_key],
                record.source_record_id,
                "admitted_runner_record",
            )
            for runner_id, record in enumerate(admitted, start=1)
        ],
    )


def _validate_output(
    output: Path,
    *,
    candidate: sqlite3.Connection,
    groups: Sequence[_RaceGroup],
    records: Sequence[_RawRecord],
    source_sha256: bytes,
    repository_commit: str,
) -> tuple[int, int, int, int, int, int, str, int]:
    value_comparisons = 0
    type_comparisons = 0
    stored_fingerprints = 0
    recomputed_fingerprints = 0

    with connect_read_only(output) as connection:
        configure_governed_connection(connection, query_only=True)
        for table in _SOURCE_METADATA_TABLES:
            expected = candidate.execute(
                f"SELECT * FROM {quote_identifier(table)} ORDER BY 1"
            ).fetchall()
            observed = connection.execute(
                f"SELECT * FROM {quote_identifier(table)} ORDER BY 1"
            ).fetchall()
            if observed != expected:
                raise RuntimeError(f"Persisted source metadata mismatch in {table}")

        governance = connection.execute(
            """
            SELECT gm.governance_method_code, gm.repository_commit,
                   gr.governance_release_code, gr.release_status,
                   gr.repository_commit, gr.population_predicate
            FROM governance_method AS gm
            JOIN governance_release AS gr
              ON gr.governance_method_id = gm.governance_method_id
            """
        ).fetchone()
        expected_governance = (
            governance_method_code("source-v1-structure", 1),
            repository_commit,
            governance_release_code(source_sha256, "source-v1-structure", 1),
            "accepted",
            repository_commit,
            "rowid <> 1",
        )
        if governance != expected_governance:
            raise RuntimeError("Persisted governance metadata mismatch")
        if connection.execute(
            "SELECT COUNT(*) FROM governance_release_evidence"
        ).fetchone()[0] != len(_GOVERNANCE_EVIDENCE):
            raise RuntimeError("Persisted governance evidence count mismatch")

        for record in records:
            row = connection.execute(
                _record_select_sql() + " WHERE source_rowid = ?",
                (record.source_rowid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    f"Persisted output lacks source rowid {record.source_rowid}"
                )
            observed = _raw_record(row)
            if (
                observed.source_record_id != record.source_record_id
                or observed.source_record_code != record.source_record_code
                or observed.structural_status != record.structural_status
                or observed.exclusion_reason != record.exclusion_reason
            ):
                raise RuntimeError(
                    f"Persisted source metadata mismatch for rowid {record.source_rowid}"
                )
            for ordinal, (expected_value, observed_value) in enumerate(
                zip(record.values, observed.values, strict=True)
            ):
                if not _same_value(expected_value, observed_value):
                    raise RuntimeError(
                        "Candidate/output raw value mismatch at source rowid "
                        f"{record.source_rowid}, ordinal {ordinal}"
                    )
                value_comparisons += 1
            if observed.storage_classes != record.storage_classes:
                raise RuntimeError(
                    f"Candidate/output storage-class mismatch for rowid {record.source_rowid}"
                )
            type_comparisons += len(RAW_COLUMN_NAMES)
            if observed.row_sha256 != record.row_sha256:
                raise RuntimeError(
                    f"Stored fingerprint mismatch for rowid {record.source_rowid}"
                )
            stored_fingerprints += 1
            if raceform_v1_row_sha256(observed.values) != record.row_sha256:
                raise RuntimeError(
                    f"Recomputed fingerprint mismatch for rowid {record.source_rowid}"
                )
            recomputed_fingerprints += 1

        expected_races = [
            (
                group.race_sequence,
                source_race_occurrence_code(source_sha256, group.race_sequence),
                group.raw_date,
                group.raw_course,
                group.raw_off,
                group.admitted_runner_count,
            )
            for group in groups
        ]
        observed_races = connection.execute(
            """
            SELECT source_race_occurrence_id, source_race_occurrence_code,
                   raw_date, raw_course, raw_off, admitted_runner_count
            FROM core_source_race_occurrence
            ORDER BY source_race_occurrence_id
            """
        ).fetchall()
        if observed_races != expected_races:
            raise RuntimeError("Persisted core race occurrences do not reconcile")

        admitted = sorted(
            (
                record
                for record in records
                if record.structural_status == "admitted_runner_record"
            ),
            key=lambda record: record.source_rowid,
        )
        group_ids = {group.key: group.race_sequence for group in groups}
        expected_runners = [
            (
                runner_id,
                runner_participation_code(source_sha256, record.source_rowid),
                group_ids[record.race_key],
                record.source_record_id,
                "admitted_runner_record",
                record.source_rowid,
            )
            for runner_id, record in enumerate(admitted, start=1)
        ]
        observed_runners = connection.execute(
            """
            SELECT runner.runner_participation_id,
                   runner.runner_participation_code,
                   runner.source_race_occurrence_id,
                   runner.source_record_id,
                   runner.source_record_status,
                   raw.source_rowid
            FROM core_runner_participation AS runner
            JOIN source_raceform_v1_record AS raw
              ON raw.source_record_id = runner.source_record_id
            ORDER BY runner.runner_participation_id
            """
        ).fetchall()
        if observed_runners != expected_runners:
            raise RuntimeError("Persisted core runner participations do not reconcile")

        mismatched_counts = connection.execute(
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
        if mismatched_counts:
            raise RuntimeError("Persisted race/runner counts do not reconcile")
        if connection.execute("SELECT COUNT(*) FROM import_manifest").fetchone()[0]:
            raise RuntimeError("Core prototype must not populate import manifests")
        if connection.execute(
            "SELECT COUNT(*) FROM import_validation_result"
        ).fetchone()[0]:
            raise RuntimeError("Core prototype must not populate validation results")

        quick_row = connection.execute("PRAGMA quick_check").fetchone()
        quick = "" if quick_row is None else str(quick_row[0])
        if quick != "ok":
            raise RuntimeError(f"Core prototype quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Core prototype foreign_key_check returned {foreign_key_rows} rows"
            )

    return (
        value_comparisons,
        type_comparisons,
        stored_fingerprints,
        recomputed_fingerprints,
        len(expected_races),
        len(expected_runners),
        quick,
        foreign_key_rows,
    )


def run_core_structure_prototype(
    source_path: str | Path,
    raw_mirror_candidate_path: str | Path,
    output_path: str | Path,
    *,
    repository_commit: str,
    race_count: int = 3,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    created_at_utc: str | None = None,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
    expected_candidate_sha256: bytes = VALIDATED_RAW_MIRROR_CANDIDATE_SHA256,
) -> CoreStructurePrototypeSummary:
    """Build and validate a small governed race-and-runner structural prototype."""

    race_count = _positive_integer(race_count, name="race_count")
    repository_commit = _repository_commit(repository_commit)
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
    output = Path(output_path).expanduser().resolve()
    if len({source, candidate_path, output}) != 3:
        raise ValueError("Source, raw-mirror candidate and output paths must differ")
    existing = [path for path in _artifacts(output) if path.exists()]
    if existing:
        raise FileExistsError(
            "Core prototype artifact already exists: "
            + ", ".join(str(path) for path in existing)
        )

    source_hash_before = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    candidate_hash_before = _validate_file_hash(
        candidate_path,
        expected_candidate_sha256,
        label="Raw-mirror candidate",
    )
    timestamp = created_at_utc or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )

    try:
        with connect_read_only(candidate_path) as candidate:
            configure_governed_connection(candidate, query_only=True)
            _validate_raw_candidate(
                candidate,
                source_sha256=source_hash_before,
                baseline=baseline,
            )
            groups = _select_groups(candidate, race_count)
            records = _selected_records(candidate, groups, source_hash_before)

            output.parent.mkdir(parents=True, exist_ok=True)
            destination = sqlite3.connect(output)
            try:
                configure_governed_connection(destination, durable_candidate=True)
                create_minimum_core_schema(destination)
                destination.execute("BEGIN IMMEDIATE")
                _copy_metadata(candidate, destination)
                _insert_records(destination, records)
                _insert_governance(
                    destination,
                    source_sha256=source_hash_before,
                    repository_commit=repository_commit,
                    timestamp=timestamp,
                )
                _insert_core(
                    destination,
                    groups=groups,
                    records=records,
                    source_sha256=source_hash_before,
                )
                destination.commit()
            except Exception:
                destination.rollback()
                raise
            finally:
                destination.close()

            (
                value_comparisons,
                type_comparisons,
                stored_fingerprints,
                recomputed_fingerprints,
                race_comparisons,
                runner_comparisons,
                quick_check,
                foreign_key_rows,
            ) = _validate_output(
                output,
                candidate=candidate,
                groups=groups,
                records=records,
                source_sha256=source_hash_before,
                repository_commit=repository_commit,
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
        _require_no_sidecars(output, label="Core prototype")
        if source_hash_after != source_hash_before:
            raise RuntimeError("Immutable source hash changed during core prototype")
        if candidate_hash_after != candidate_hash_before:
            raise RuntimeError("Raw-mirror candidate hash changed during core prototype")
    except Exception:
        _remove_output(output)
        raise

    admitted_count = sum(
        record.structural_status == "admitted_runner_record" for record in records
    )
    excluded_count = len(records) - admitted_count
    return CoreStructurePrototypeSummary(
        source_path=str(source),
        raw_mirror_candidate_path=str(candidate_path),
        output_path=str(output),
        source_file_sha256_hex=source_hash_before.hex(),
        raw_mirror_candidate_sha256_hex=candidate_hash_before.hex(),
        output_file_sha256_hex=sha256_file(output).hex(),
        selected_race_count=len(groups),
        selected_minimum_source_rowids=tuple(
            group.minimum_source_rowid for group in groups
        ),
        copied_raw_record_count=len(records),
        copied_admitted_record_count=admitted_count,
        copied_excluded_record_count=excluded_count,
        core_race_occurrence_count=len(groups),
        core_runner_participation_count=admitted_count,
        candidate_output_value_comparisons=value_comparisons,
        candidate_output_storage_class_comparisons=type_comparisons,
        stored_fingerprint_comparisons=stored_fingerprints,
        recomputed_fingerprint_comparisons=recomputed_fingerprints,
        race_reconciliation_comparisons=race_comparisons,
        runner_reconciliation_comparisons=runner_comparisons,
        quick_check=quick_check,
        foreign_key_check_rows=foreign_key_rows,
        source_hash_unchanged=True,
        raw_mirror_candidate_hash_unchanged=True,
        persisted_readback_passed=True,
    )
