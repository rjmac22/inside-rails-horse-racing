"""Independent validation for a complete Database v2 governed-integration candidate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from time import perf_counter
from typing import Iterable

from inside_rails.connection_identity import load_connection_repairs
from inside_rails.database.fingerprints import raceform_v1_row_sha256
from inside_rails.database.governed_integration_candidate import (
    EXPECTED_BASE_RELEASE_SHA256,
    EXPECTED_BASE_RELEASE_SIZE_BYTES,
)
from inside_rails.database.minimum_core_candidate_io import (
    require_no_sidecars,
    validate_file_hash,
)
from inside_rails.database.raw_mirror_prototype import RAW_COLUMN_NAMES, sha256_file
from inside_rails.database.schema import (
    APPLICATION_ID,
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    configure_governed_connection,
    create_governed_integration_schema,
    schema_inventory,
)
from inside_rails.horse_pedigree_identity import load_identity_governance
from inside_rails.manual_verifications import load_manual_verifications
from inside_rails.runner_record_supplementations import (
    load_runner_record_supplementations,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier


EXPECTED_TABLE_COUNT = 31
EXPECTED_RACES = 189_043
EXPECTED_RUNNERS = 1_851_285
EXPECTED_COURSES = 395
EXPECTED_JURISDICTION_CONTEXTS = 16
EXPECTED_FIELD_TREATMENTS = 37
EXPECTED_CONNECTION_DECISIONS = 46
EXPECTED_CONNECTION_SUPPLEMENTED = 28
EXPECTED_CONNECTION_UNRESOLVED = 18
EXPECTED_RUNNER_SUPPLEMENTATIONS = 3
EXPECTED_HORSE_SPECIALIST = 16
EXPECTED_HORSE_TRANSITIONS = 353
EXPECTED_HORSE_CORRECTED = 92
EXPECTED_HORSE_DIFFERENT = 261
EXPECTED_HORSE_UNRESOLVED = 0
EXPECTED_HORSE_OCCURRENCES = 611
EXPECTED_PARTICIPANT_LABELS = 116_859
EXPECTED_PARTICIPANT_IDENTITIES = 68
EXPECTED_PARTICIPANT_MAPPINGS = 149
EXPECTED_PARTICIPANT_CANDIDATES = 1_205
EXPECTED_TEMPORAL_RESOLVED = 169_465
EXPECTED_TEMPORAL_UNRESOLVED = 19_578
EXPECTED_TEMPORAL_METHOD_COUNTS = {
    "course_local_dead_of_night_rejection": 111_871,
    "stable_post_boundary_course_profile": 47_242,
    "explicit_post_boundary_time": 10_352,
    "unresolved": 19_578,
}

_METADATA_TABLES = (
    "source_provider",
    "source_product",
    "source_version",
    "source_relation",
    "source_relation_field",
)
_CORE_TABLES = (
    "core_source_race_occurrence",
    "core_runner_participation",
)


@dataclass(frozen=True)
class GovernedIntegrationValidationSummary:
    candidate_path: str
    base_release_path: str
    candidate_sha256_hex: str
    base_release_sha256_hex: str
    schema_table_count: int
    raw_record_fingerprints_recomputed: int
    structural_rows_compared: int
    manual_verification_rows: int
    race_rows: int
    runner_rows: int
    temporal_rows: int
    horse_transition_rows: int
    horse_occurrence_rows: int
    participant_candidate_rows: int
    participant_identity_rows: int
    participant_mapping_rows: int
    quick_check: str
    foreign_key_check_rows: int
    validation_elapsed_seconds: float
    manifest_status: str


class GovernedIntegrationValidationError(RuntimeError):
    """Raised when a Database v2 candidate violates an accepted contract."""


def _expected_schema_inventory() -> list[tuple[str, str, str]]:
    connection = sqlite3.connect(":memory:")
    try:
        create_governed_integration_schema(connection)
        return schema_inventory(connection)
    finally:
        connection.close()


def _compare_small_table(
    base: sqlite3.Connection,
    candidate: sqlite3.Connection,
    table: str,
) -> int:
    quoted = quote_identifier(table)
    base_rows = base.execute(f"SELECT * FROM {quoted} ORDER BY 1").fetchall()
    candidate_rows = candidate.execute(f"SELECT * FROM {quoted} ORDER BY 1").fetchall()
    if base_rows != candidate_rows:
        raise GovernedIntegrationValidationError(
            f"Database v2 changed carried-forward table {table}"
        )
    return len(base_rows)


def _stream_compare_table(
    base: sqlite3.Connection,
    candidate: sqlite3.Connection,
    table: str,
    *,
    batch_size: int,
) -> int:
    quoted = quote_identifier(table)
    base_cursor = base.execute(f"SELECT * FROM {quoted} ORDER BY 1")
    candidate_cursor = candidate.execute(f"SELECT * FROM {quoted} ORDER BY 1")
    compared = 0
    while True:
        base_rows = base_cursor.fetchmany(batch_size)
        candidate_rows = candidate_cursor.fetchmany(batch_size)
        if not base_rows and not candidate_rows:
            break
        if base_rows != candidate_rows:
            raise GovernedIntegrationValidationError(
                f"Database v2 changed carried-forward structural table {table} "
                f"near row {compared + 1}"
            )
        compared += len(base_rows)
    return compared


def _validate_raw_mirror(
    base: sqlite3.Connection,
    candidate: sqlite3.Connection,
    *,
    batch_size: int,
) -> int:
    raw_columns = ", ".join(quote_identifier(name) for name in RAW_COLUMN_NAMES)
    base_cursor = base.execute(
        """
        SELECT source_record_id, source_rowid, structural_status,
               exclusion_reason, row_sha256
        FROM source_raceform_v1_record
        ORDER BY source_record_id
        """
    )
    candidate_cursor = candidate.execute(
        f"""
        SELECT source_record_id, source_rowid, structural_status,
               exclusion_reason, row_sha256, {raw_columns}
        FROM source_raceform_v1_record
        ORDER BY source_record_id
        """
    )
    compared = 0
    while True:
        base_rows = base_cursor.fetchmany(batch_size)
        candidate_rows = candidate_cursor.fetchmany(batch_size)
        if not base_rows and not candidate_rows:
            break
        if len(base_rows) != len(candidate_rows):
            raise GovernedIntegrationValidationError(
                "Database v2 raw mirror row count differs from accepted Database v1"
            )
        for base_row, candidate_row in zip(base_rows, candidate_rows, strict=True):
            if tuple(candidate_row[:5]) != tuple(base_row):
                raise GovernedIntegrationValidationError(
                    f"Database v2 raw lineage/fingerprint changed at source record {base_row[0]}"
                )
            recomputed = raceform_v1_row_sha256(tuple(candidate_row[5:]))
            if recomputed != candidate_row[4]:
                raise GovernedIntegrationValidationError(
                    f"Database v2 raw value changed without matching accepted fingerprint "
                    f"at source rowid {candidate_row[1]}"
                )
            compared += 1
    if compared != 1_851_286:
        raise GovernedIntegrationValidationError(
            f"Database v2 raw mirror expected 1,851,286 rows; observed {compared}"
        )
    return compared


def _count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {quote_identifier(table)}").fetchone()[0])


def _require_count(connection: sqlite3.Connection, table: str, expected: int) -> int:
    observed = _count(connection, table)
    if observed != expected:
        raise GovernedIntegrationValidationError(
            f"{table} expected {expected} rows; observed {observed}"
        )
    return observed


def _validate_governance(connection: sqlite3.Connection) -> str:
    manifest = connection.execute(
        """
        SELECT source_version_id, governance_release_id, schema_version,
               physical_record_count, admitted_record_count, excluded_record_count,
               race_occurrence_count, runner_participation_count,
               prior_database_release_code, prior_release_preserved,
               build_status, failure_reason
        FROM import_manifest
        """
    ).fetchall()
    if len(manifest) != 1:
        raise GovernedIntegrationValidationError(
            f"Database v2 must contain exactly one build manifest; found {len(manifest)}"
        )
    row = manifest[0]
    expected_counts = (2, 1_851_286, 1_851_285, 1, EXPECTED_RACES, EXPECTED_RUNNERS)
    if tuple(row[2:8]) != expected_counts:
        raise GovernedIntegrationValidationError(
            f"Database v2 manifest structural baseline changed: {row!r}"
        )
    if row[8] is None or not str(row[8]).strip() or row[9] != 1:
        raise GovernedIntegrationValidationError(
            "Database v2 manifest lost prior-release preservation evidence"
        )
    if row[11] is not None:
        raise GovernedIntegrationValidationError("Nonfailed Database v2 manifest has failure_reason")

    source_version_id = int(row[0])
    current_release_id = int(row[1])
    releases = connection.execute(
        """
        SELECT governance_release_id, release_status, superseded_by_release_id
        FROM governance_release
        WHERE source_version_id = ?
        ORDER BY governance_release_id
        """,
        (source_version_id,),
    ).fetchall()
    accepted = [item for item in releases if item[1] == "accepted"]
    if accepted != [(current_release_id, "accepted", None)]:
        raise GovernedIntegrationValidationError(
            f"Database v2 current governance release mismatch: {releases!r}"
        )
    structural_release_ids = {
        int(value)
        for value, in connection.execute(
            "SELECT DISTINCT governance_release_id FROM core_source_race_occurrence"
        )
    }
    if len(structural_release_ids) != 1:
        raise GovernedIntegrationValidationError(
            f"Carried-forward structural race rows have multiple governance releases: {structural_release_ids!r}"
        )
    structural_release_id = next(iter(structural_release_ids))
    if structural_release_id == current_release_id:
        raise GovernedIntegrationValidationError(
            "Database v2 incorrectly rewrote Database v1 structural governance lineage"
        )
    structural_row = next(
        (item for item in releases if int(item[0]) == structural_release_id),
        None,
    )
    if structural_row != (structural_release_id, "superseded", current_release_id):
        raise GovernedIntegrationValidationError(
            f"Database v1 structural governance is not correctly superseded: {structural_row!r}"
        )
    return str(row[10])


def _validate_references(
    connection: sqlite3.Connection,
    project_root: Path,
) -> int:
    _require_count(connection, "reference_course", EXPECTED_COURSES)
    _require_count(connection, "reference_jurisdiction_context", EXPECTED_JURISDICTION_CONTEXTS)
    _require_count(connection, "governance_source_field_treatment", EXPECTED_FIELD_TREATMENTS)

    committed_manual = load_manual_verifications(
        project_root / "data/reference/manual_verifications.csv"
    )
    _require_count(connection, "governance_manual_verification", len(committed_manual))
    db_manual = {
        str(code): (str(status), str(action), verified_value)
        for code, status, action, verified_value in connection.execute(
            """
            SELECT verification_code, verification_status, database_action, verified_value
            FROM governance_manual_verification
            """
        )
    }
    for row in committed_manual:
        observed = db_manual.get(row.verification_id)
        expected = (
            row.verification_status,
            row.database_action,
            row.verified_value or None,
        )
        if observed != expected:
            raise GovernedIntegrationValidationError(
                f"Manual verification drift for {row.verification_id}: {observed!r} != {expected!r}"
            )

    _require_count(connection, "governance_connection_value_decision", EXPECTED_CONNECTION_DECISIONS)
    connection_partition = dict(
        connection.execute(
            """
            SELECT value_status, COUNT(*)
            FROM governance_connection_value_decision
            GROUP BY value_status
            """
        ).fetchall()
    )
    if connection_partition != {
        "externally_supplemented": EXPECTED_CONNECTION_SUPPLEMENTED,
        "source_blank_unresolved": EXPECTED_CONNECTION_UNRESOLVED,
    }:
        raise GovernedIntegrationValidationError(
            f"Connection decision partition changed: {connection_partition!r}"
        )

    repairs = load_connection_repairs(
        project_root / "data/reference/connection_identity_repairs.csv"
    )
    db_repairs = {
        (int(source_rowid), str(field_name)): (
            str(verification_code),
            str(governed_value),
            str(confidence),
        )
        for source_rowid, field_name, verification_code, governed_value, confidence in connection.execute(
            """
            SELECT source.source_rowid, field.field_name, verification.verification_code,
                   decision.governed_value, decision.confidence
            FROM governance_connection_value_decision AS decision
            JOIN source_raceform_v1_record AS source
              ON source.source_record_id = decision.source_record_id
            JOIN source_relation_field AS field
              ON field.source_relation_field_id = decision.source_relation_field_id
            JOIN governance_manual_verification AS verification
              ON verification.manual_verification_id = decision.manual_verification_id
            WHERE decision.value_status = 'externally_supplemented'
            """
        )
    }
    expected_repairs = {
        (repair.source_rowid, repair.source_field): (
            repair.verification_id,
            repair.governed_value,
            repair.confidence,
        )
        for repair in repairs
    }
    if db_repairs != expected_repairs:
        raise GovernedIntegrationValidationError(
            "Database v2 connection supplementations do not match the governed 28-row repair reference"
        )

    committed_supplements = load_runner_record_supplementations(
        project_root / "data/reference/runner_record_supplementations.csv"
    )
    _require_count(
        connection,
        "governance_runner_record_supplementation",
        EXPECTED_RUNNER_SUPPLEMENTATIONS,
    )
    db_supplements = {
        str(code): (str(horse), int(source_rows), int(source_ran), int(published), finish, outcome)
        for code, horse, source_rows, source_ran, published, finish, outcome in connection.execute(
            """
            SELECT supplementation_code, source_horse, source_runner_rows,
                   source_reported_ran, published_runner_count,
                   verified_finish_position, verified_outcome
            FROM governance_runner_record_supplementation
            """
        )
    }
    expected_supplements = {
        row.supplementation_id: (
            row.source_horse,
            row.source_runner_rows,
            row.source_ran,
            row.published_runners,
            row.verified_pos,
            row.verified_outcome,
        )
        for row in committed_supplements
    }
    if db_supplements != expected_supplements:
        raise GovernedIntegrationValidationError(
            "Database v2 missing-runner supplementations do not match governed reference"
        )

    specialist = load_identity_governance(
        project_root / "data/reference/horse_pedigree_identity_governance.csv"
    )
    _require_count(
        connection,
        "governance_horse_pedigree_specialist_decision",
        EXPECTED_HORSE_SPECIALIST,
    )
    if len(specialist.rows) != EXPECTED_HORSE_SPECIALIST:
        raise GovernedIntegrationValidationError("Notebook 19 specialist reference changed")
    return len(committed_manual)


def _validate_race_and_time(connection: sqlite3.Connection) -> tuple[int, int]:
    race_rows = _require_count(
        connection,
        "core_source_race_occurrence_governed",
        EXPECTED_RACES,
    )
    unresolved_course = int(
        connection.execute(
            "SELECT COUNT(*) FROM core_source_race_occurrence_governed WHERE reference_course_id IS NULL"
        ).fetchone()[0]
    )
    if unresolved_course:
        raise GovernedIntegrationValidationError(
            f"Database v2 has {unresolved_course} races without governed course reference"
        )

    temporal_rows = _require_count(
        connection,
        "core_source_race_occurrence_time",
        EXPECTED_RACES,
    )
    resolution = dict(
        connection.execute(
            """
            SELECT temporal_resolution_status, COUNT(*)
            FROM core_source_race_occurrence_time
            GROUP BY temporal_resolution_status
            """
        ).fetchall()
    )
    if resolution != {
        "resolved": EXPECTED_TEMPORAL_RESOLVED,
        "unresolved": EXPECTED_TEMPORAL_UNRESOLVED,
    }:
        raise GovernedIntegrationValidationError(
            f"Temporal resolution partition changed: {resolution!r}"
        )
    methods = {
        str(method): int(count)
        for method, count in connection.execute(
            """
            SELECT decision_method, COUNT(*)
            FROM core_source_race_occurrence_time
            GROUP BY decision_method
            """
        )
    }
    if methods != EXPECTED_TEMPORAL_METHOD_COUNTS:
        raise GovernedIntegrationValidationError(
            f"Temporal decision-method partition changed: {methods!r}"
        )
    return race_rows, temporal_rows


def _validate_runner_semantics(connection: sqlite3.Connection) -> int:
    runner_rows = _require_count(
        connection,
        "core_runner_participation_governed",
        EXPECTED_RUNNERS,
    )

    standalone_f = connection.execute(
        """
        SELECT source.source_rowid, governed.starting_price_kind,
               governed.starting_price_value_status,
               governed.starting_price_analytical_numerator,
               governed.starting_price_analytical_denominator,
               governed.starting_price_manual_verification_id
        FROM core_runner_participation_governed AS governed
        JOIN core_runner_participation AS runner
          ON runner.runner_participation_id = governed.runner_participation_id
        JOIN source_raceform_v1_record AS source
          ON source.source_record_id = runner.source_record_id
        WHERE source.sp = 'F'
        """
    ).fetchall()
    if len(standalone_f) != 1 or tuple(standalone_f[0][1:]) != (
        "unresolved",
        "unresolved",
        None,
        None,
        None,
    ):
        raise GovernedIntegrationValidationError(
            f"Notebook 08 standalone F must remain unresolved: {standalone_f!r}"
        )

    sex_corrections = connection.execute(
        """
        SELECT source.sex, source.horse, race.raw_date, race.raw_course, race.raw_off,
               governed.sex_normalised, verification.verification_code
        FROM core_runner_participation_governed AS governed
        JOIN core_runner_participation AS runner
          ON runner.runner_participation_id = governed.runner_participation_id
        JOIN source_raceform_v1_record AS source
          ON source.source_record_id = runner.source_record_id
        JOIN core_source_race_occurrence AS race
          ON race.source_race_occurrence_id = runner.source_race_occurrence_id
        JOIN governance_manual_verification AS verification
          ON verification.manual_verification_id = governed.sex_manual_verification_id
        WHERE governed.sex_interpretation_status = 'verified_source_correction'
        ORDER BY verification.verification_code
        """
    ).fetchall()
    expected_sex = [
        ("BB", "Par Coeur (GER)", "2017-10-15", "Cologne (GER)", "1:35", "gelding", "NB17-SEX-0002"),
        ("B", "La Venezolana (VEN)", "2019-11-29", "Gulfstream Park (USA)", "8:30", "filly", "NB17-SEX-0003"),
    ]
    if sex_corrections != expected_sex:
        raise GovernedIntegrationValidationError(
            f"Notebook 17 exact sex corrections changed: {sex_corrections!r}"
        )

    invalid_rpr = connection.execute(
        """
        SELECT source.source_rowid, source.rpr, governed.rpr_governed, governed.rpr_status
        FROM core_runner_participation_governed AS governed
        JOIN core_runner_participation AS runner
          ON runner.runner_participation_id = governed.runner_participation_id
        JOIN source_raceform_v1_record AS source
          ON source.source_record_id = runner.source_record_id
        WHERE governed.rpr_status = 'invalid_source_value'
        """
    ).fetchall()
    if invalid_rpr != [(1_619_851, 775, None, "invalid_source_value")]:
        raise GovernedIntegrationValidationError(
            f"Notebook 18 exact invalid RPR handling changed: {invalid_rpr!r}"
        )

    connection_states = {
        str(status): int(count)
        for status, count in connection.execute(
            """
            SELECT value_status, COUNT(*)
            FROM (
                SELECT jockey_value_status AS value_status
                FROM core_runner_participation_governed
                UNION ALL
                SELECT trainer_value_status
                FROM core_runner_participation_governed
                UNION ALL
                SELECT owner_value_status
                FROM core_runner_participation_governed
            )
            GROUP BY value_status
            """
        )
    }
    if connection_states.get("externally_supplemented", 0) != 28:
        raise GovernedIntegrationValidationError(
            f"Runner extension lost Notebook 20 supplementations: {connection_states!r}"
        )
    if connection_states.get("source_blank_unresolved", 0) != 18:
        raise GovernedIntegrationValidationError(
            f"Runner extension lost Notebook 20 unresolved blanks: {connection_states!r}"
        )
    return runner_rows


def _validate_horse_identity(connection: sqlite3.Connection) -> tuple[int, int]:
    transitions = _require_count(
        connection,
        "identity_horse_pedigree_decision",
        EXPECTED_HORSE_TRANSITIONS,
    )
    outcomes = {
        str(outcome): int(count)
        for outcome, count in connection.execute(
            """
            SELECT analytical_outcome, COUNT(*)
            FROM identity_horse_pedigree_decision
            GROUP BY analytical_outcome
            """
        )
    }
    if outcomes != {
        "Corrected": EXPECTED_HORSE_CORRECTED,
        "Different horse": EXPECTED_HORSE_DIFFERENT,
    }:
        raise GovernedIntegrationValidationError(
            f"Notebook 19 transition partition changed: {outcomes!r}"
        )
    occurrences = _require_count(
        connection,
        "identity_horse_occurrence",
        EXPECTED_HORSE_OCCURRENCES,
    )

    runninsonofagun = connection.execute(
        """
        SELECT specialist.specialist_decision_code, specialist.analytical_outcome,
               specialist.governed_damsire, specialist.verification_status,
               specialist.confidence
        FROM governance_horse_pedigree_specialist_decision AS specialist
        WHERE specialist.source_horse_label = 'Runninsonofagun (IRE)'
        """
    ).fetchall()
    if runninsonofagun != [
        ("NB19-ID-0013", "Corrected", "Society Rock (IRE)", "confirmed", "high")
    ]:
        raise GovernedIntegrationValidationError(
            f"Runninsonofagun authority correction changed: {runninsonofagun!r}"
        )
    return transitions, occurrences


def _validate_participants(connection: sqlite3.Connection) -> tuple[int, int, int]:
    labels = _require_count(
        connection,
        "identity_participant_source_label",
        EXPECTED_PARTICIPANT_LABELS,
    )
    role_labels = dict(
        connection.execute(
            """
            SELECT participant_role, COUNT(*)
            FROM identity_participant_source_label
            GROUP BY participant_role
            """
        ).fetchall()
    )
    if role_labels != {"jockey": 7_917, "trainer": 10_708, "owner": 98_234}:
        raise GovernedIntegrationValidationError(
            f"Participant source-label partition changed: {role_labels!r}"
        )

    identities = _require_count(
        connection,
        "identity_participant",
        EXPECTED_PARTICIPANT_IDENTITIES,
    )
    mappings = _require_count(
        connection,
        "identity_participant_label_map",
        EXPECTED_PARTICIPANT_MAPPINGS,
    )
    candidates = _require_count(
        connection,
        "identity_participant_candidate",
        EXPECTED_PARTICIPANT_CANDIDATES,
    )

    candidate_partition = {
        (str(role), str(status)): int(count)
        for role, status, count in connection.execute(
            """
            SELECT participant_role, decision_status, COUNT(*)
            FROM identity_participant_candidate
            GROUP BY participant_role, decision_status
            """
        )
    }
    expected_partition = {
        ("jockey", "accepted"): 1,
        ("jockey", "confirmed_distinct"): 1,
        ("jockey", "unresolved"): 214,
        ("trainer", "accepted"): 26,
        ("trainer", "unresolved"): 27,
        ("owner", "accepted"): 41,
        ("owner", "unresolved"): 895,
    }
    if candidate_partition != expected_partition:
        raise GovernedIntegrationValidationError(
            f"Participant candidate partition changed: {candidate_partition!r}"
        )

    marie = connection.execute(
        """
        SELECT identity.participant_identity_code, label.raw_label
        FROM identity_participant_label_map AS map
        JOIN identity_participant AS identity
          ON identity.participant_identity_id = map.participant_identity_id
        JOIN identity_participant_source_label AS label
          ON label.participant_source_label_id = map.participant_source_label_id
        WHERE identity.participant_identity_code = 'JOCKEY-PROVISIONAL-0001'
        ORDER BY label.raw_label
        """
    ).fetchall()
    if marie != [
        ("JOCKEY-PROVISIONAL-0001", "Mlle Marie Velon"),
        ("JOCKEY-PROVISIONAL-0001", "Mme Marie Velon"),
    ]:
        raise GovernedIntegrationValidationError(
            f"Marie Velon direct mapping changed: {marie!r}"
        )
    b_oneill_map = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM identity_participant_label_map AS map
            JOIN identity_participant_source_label AS label
              ON label.participant_source_label_id = map.participant_source_label_id
            WHERE label.raw_label IN ('Miss B ONeill', 'Mr B ONeill')
            """
        ).fetchone()[0]
    )
    if b_oneill_map:
        raise GovernedIntegrationValidationError(
            "Confirmed-distinct B ONeill labels were incorrectly mapped to an accepted identity"
        )
    return candidates, identities, mappings


def validate_governed_integration_candidate(
    candidate_path: str | Path,
    base_release_path: str | Path,
    project_root: str | Path,
    *,
    batch_size: int = 5_000,
) -> GovernedIntegrationValidationSummary:
    """Validate Database v2 without modifying either database file."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    candidate_path = Path(candidate_path).expanduser().resolve()
    base_release_path = Path(base_release_path).expanduser().resolve()
    project_root = Path(project_root).expanduser().resolve()
    if candidate_path == base_release_path:
        raise ValueError("Database v2 candidate and Database v1 release must differ")

    require_no_sidecars(candidate_path, label="Database v2 candidate")
    if base_release_path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise GovernedIntegrationValidationError("Accepted Database v1 size changed")
    base_hash = validate_file_hash(
        base_release_path,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v1 release",
    )
    candidate_hash_before = sha256_file(candidate_path)
    started = perf_counter()

    with connect_read_only(base_release_path) as base, connect_read_only(candidate_path) as candidate:
        configure_governed_connection(base, query_only=True)
        configure_governed_connection(candidate, query_only=True)

        if schema_inventory(candidate) != _expected_schema_inventory():
            raise GovernedIntegrationValidationError("Database v2 schema inventory mismatch")
        tables = int(
            candidate.execute(
                "SELECT COUNT(*) FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0]
        )
        if tables != EXPECTED_TABLE_COUNT:
            raise GovernedIntegrationValidationError(
                f"Database v2 expected {EXPECTED_TABLE_COUNT} physical tables; observed {tables}"
            )
        if int(candidate.execute("PRAGMA application_id").fetchone()[0]) != APPLICATION_ID:
            raise GovernedIntegrationValidationError("Database v2 application_id mismatch")
        if int(candidate.execute("PRAGMA user_version").fetchone()[0]) != GOVERNED_INTEGRATION_SCHEMA_VERSION:
            raise GovernedIntegrationValidationError("Database v2 user_version mismatch")

        quick = str(candidate.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise GovernedIntegrationValidationError(f"Database v2 quick_check failed: {quick!r}")
        foreign_key_rows = len(candidate.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise GovernedIntegrationValidationError(
                f"Database v2 foreign_key_check returned {foreign_key_rows} rows"
            )

        # v2 starts from an exact accepted-v1 copy. Recompute every raw row's
        # fingerprint and compare structural source/core tables back to that
        # immutable accepted release before trusting any semantic extension.
        for table in _METADATA_TABLES:
            _compare_small_table(base, candidate, table)
        raw_rows = _validate_raw_mirror(base, candidate, batch_size=batch_size)
        structural_rows = sum(
            _stream_compare_table(base, candidate, table, batch_size=batch_size)
            for table in _CORE_TABLES
        )

        manifest_status = _validate_governance(candidate)
        manual_rows = _validate_references(candidate, project_root)
        race_rows, temporal_rows = _validate_race_and_time(candidate)
        runner_rows = _validate_runner_semantics(candidate)
        horse_transitions, horse_occurrences = _validate_horse_identity(candidate)
        participant_candidates, participant_identities, participant_mappings = (
            _validate_participants(candidate)
        )

    candidate_hash_after = sha256_file(candidate_path)
    if candidate_hash_after != candidate_hash_before:
        raise GovernedIntegrationValidationError(
            "Database v2 candidate changed while opened read-only for validation"
        )
    if validate_file_hash(
        base_release_path,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v1 release",
    ) != base_hash:
        raise GovernedIntegrationValidationError(
            "Accepted Database v1 changed during Database v2 validation"
        )

    return GovernedIntegrationValidationSummary(
        candidate_path=str(candidate_path),
        base_release_path=str(base_release_path),
        candidate_sha256_hex=candidate_hash_after.hex(),
        base_release_sha256_hex=base_hash.hex(),
        schema_table_count=EXPECTED_TABLE_COUNT,
        raw_record_fingerprints_recomputed=raw_rows,
        structural_rows_compared=structural_rows,
        manual_verification_rows=manual_rows,
        race_rows=race_rows,
        runner_rows=runner_rows,
        temporal_rows=temporal_rows,
        horse_transition_rows=horse_transitions,
        horse_occurrence_rows=horse_occurrences,
        participant_candidate_rows=participant_candidates,
        participant_identity_rows=participant_identities,
        participant_mapping_rows=participant_mappings,
        quick_check=quick,
        foreign_key_check_rows=foreign_key_rows,
        validation_elapsed_seconds=perf_counter() - started,
        manifest_status=manifest_status,
    )


__all__ = [
    "GovernedIntegrationValidationError",
    "GovernedIntegrationValidationSummary",
    "validate_governed_integration_candidate",
]
