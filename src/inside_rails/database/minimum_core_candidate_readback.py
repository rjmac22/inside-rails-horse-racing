"""Source-wide persisted readback for complete minimum-core candidates."""

from __future__ import annotations

from pathlib import Path

from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
    runner_participation_code,
    source_race_occurrence_code,
)
from inside_rails.database.minimum_core_candidate_model import (
    GOVERNANCE_EVIDENCE,
    same_value,
)
from inside_rails.database.minimum_core_candidate_seed import expected_schema_inventory
from inside_rails.database.raw_mirror_prototype import SourceBaseline
from inside_rails.database.schema import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    configure_governed_connection,
    schema_inventory,
)
from inside_rails.source_sqlite import connect_read_only


def _validate_raw_population(
    connection: object,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
) -> None:
    if schema_inventory(connection) != expected_schema_inventory():
        raise RuntimeError("Minimum-core candidate schema inventory mismatch")
    version = connection.execute(
        """
        SELECT file_sha256, physical_record_count, admitted_record_count,
               excluded_record_count, admission_predicate
        FROM source_version WHERE source_version_id = 1
        """
    ).fetchone()
    if version != (
        source_sha256,
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        "rowid <> 1",
    ):
        raise RuntimeError("Persisted source-version metadata mismatch")
    population = connection.execute(
        """
        SELECT COUNT(*),
               SUM(structural_status = 'admitted_runner_record'),
               SUM(structural_status = 'retained_excluded_record'),
               SUM(row_sha256 IS NOT NULL)
        FROM source_raceform_v1_record
        """
    ).fetchone()
    expected = (
        baseline.physical_record_count,
        baseline.admitted_record_count,
        baseline.excluded_record_count,
        baseline.physical_record_count,
    )
    if population is None or tuple(int(value) for value in population) != expected:
        raise RuntimeError("Persisted raw population changed during core build")


def readback_core(
    output: Path,
    *,
    source_sha256: bytes,
    baseline: SourceBaseline,
    expected_race_count: int,
    manifest_code: str,
    database_release_code: str,
) -> tuple[int, int, str, int, int, int]:
    race_comparisons = 0
    runner_comparisons = 0
    with connect_read_only(output) as connection:
        configure_governed_connection(connection, query_only=True)
        _validate_raw_population(
            connection,
            source_sha256=source_sha256,
            baseline=baseline,
        )

        governance = connection.execute(
            """
            SELECT gm.governance_method_code, gr.governance_release_code,
                   gr.release_status, gr.population_predicate
            FROM governance_method AS gm
            JOIN governance_release AS gr
              ON gr.governance_method_id = gm.governance_method_id
            """
        ).fetchone()
        expected_governance = (
            governance_method_code("source-v1-structure", 1),
            governance_release_code(source_sha256, "source-v1-structure", 1),
            "accepted",
            "rowid <> 1",
        )
        if governance != expected_governance:
            raise RuntimeError("Persisted governance metadata mismatch")
        evidence_count = connection.execute(
            "SELECT COUNT(*) FROM governance_release_evidence"
        ).fetchone()[0]
        if evidence_count != len(GOVERNANCE_EVIDENCE):
            raise RuntimeError("Persisted governance evidence count mismatch")

        manifest = connection.execute(
            """
            SELECT import_manifest_code, database_release_code, build_status,
                   persisted_readback_passed, sqlite_integrity_passed,
                   foreign_key_check_passed, post_load_validation_passed
            FROM import_manifest WHERE import_manifest_id = 1
            """
        ).fetchone()
        if manifest != (
            manifest_code,
            database_release_code,
            "building",
            0,
            0,
            0,
            0,
        ):
            raise RuntimeError("Initial persisted import manifest mismatch")
        if connection.execute(
            "SELECT COUNT(*) FROM import_validation_result"
        ).fetchone()[0] != 0:
            raise RuntimeError("Validation results must be empty before finalisation")

        race_cursor = connection.execute(
            """
            SELECT race.source_race_occurrence_id,
                   race.source_race_occurrence_code,
                   race.admitted_runner_count,
                   MIN(raw.source_rowid),
                   COUNT(raw.source_record_id)
            FROM core_source_race_occurrence AS race
            JOIN source_raceform_v1_record AS raw
              ON raw.source_version_id = race.source_version_id
             AND raw.structural_status = 'admitted_runner_record'
             AND raw."date" IS race.raw_date
             AND raw."course" IS race.raw_course
             AND raw."off" IS race.raw_off
            GROUP BY race.source_race_occurrence_id,
                     race.source_race_occurrence_code,
                     race.admitted_runner_count
            ORDER BY race.source_race_occurrence_id
            """
        )
        prior_minimum = 0
        for expected_id, row in enumerate(race_cursor, start=1):
            race_id, code, admitted_count, minimum_rowid, supporting_count = row
            if int(race_id) != expected_id:
                raise RuntimeError("Persisted race integer ids are not sequential")
            if code != source_race_occurrence_code(source_sha256, expected_id):
                raise RuntimeError(f"Persisted race code mismatch at race {expected_id}")
            minimum = int(minimum_rowid)
            if minimum <= prior_minimum:
                raise RuntimeError("Persisted race ordering is not canonical")
            prior_minimum = minimum
            if int(admitted_count) != int(supporting_count):
                raise RuntimeError(f"Persisted race runner count mismatch at race {expected_id}")
            race_comparisons += 1
        if race_comparisons != expected_race_count:
            raise RuntimeError(
                f"Persisted race count mismatch: expected {expected_race_count}; "
                f"observed {race_comparisons}"
            )

        runner_cursor = connection.execute(
            """
            SELECT runner.runner_participation_id,
                   runner.runner_participation_code,
                   runner.source_record_status,
                   runner.governance_release_id,
                   raw.source_rowid,
                   raw."date", raw."course", raw."off",
                   race.raw_date, race.raw_course, race.raw_off,
                   race.governance_release_id
            FROM core_runner_participation AS runner
            JOIN source_raceform_v1_record AS raw
              ON raw.source_record_id = runner.source_record_id
            JOIN core_source_race_occurrence AS race
              ON race.source_race_occurrence_id = runner.source_race_occurrence_id
            ORDER BY runner.runner_participation_id
            """
        )
        prior_rowid = 0
        for expected_id, row in enumerate(runner_cursor, start=1):
            (
                runner_id,
                code,
                status,
                runner_governance,
                source_rowid,
                raw_date,
                raw_course,
                raw_off,
                race_date,
                race_course,
                race_off,
                race_governance,
            ) = row
            if int(runner_id) != expected_id:
                raise RuntimeError("Persisted runner integer ids are not sequential")
            rowid = int(source_rowid)
            if rowid <= prior_rowid:
                raise RuntimeError("Persisted runner source rowids are not increasing")
            prior_rowid = rowid
            if code != runner_participation_code(source_sha256, rowid):
                raise RuntimeError(f"Persisted runner code mismatch at runner {expected_id}")
            if status != "admitted_runner_record":
                raise RuntimeError(f"Persisted runner status mismatch at runner {expected_id}")
            if int(runner_governance) != 1 or int(race_governance) != 1:
                raise RuntimeError(f"Persisted governance mismatch at runner {expected_id}")
            if not (
                same_value(raw_date, race_date)
                and same_value(raw_course, race_course)
                and same_value(raw_off, race_off)
            ):
                raise RuntimeError(f"Persisted runner race grouping mismatch at runner {expected_id}")
            runner_comparisons += 1
        if runner_comparisons != baseline.admitted_record_count:
            raise RuntimeError(
                "Persisted runner count mismatch: expected "
                f"{baseline.admitted_record_count}; observed {runner_comparisons}"
            )

        missing = connection.execute(
            """
            SELECT COUNT(*)
            FROM source_raceform_v1_record AS raw
            LEFT JOIN core_runner_participation AS runner
              ON runner.source_record_id = raw.source_record_id
            WHERE raw.structural_status = 'admitted_runner_record'
              AND runner.runner_participation_id IS NULL
            """
        ).fetchone()[0]
        if int(missing):
            raise RuntimeError(f"Persisted candidate lacks {missing} runner participations")

        quick_row = connection.execute("PRAGMA quick_check").fetchone()
        quick = "" if quick_row is None else str(quick_row[0])
        if quick != "ok":
            raise RuntimeError(f"Minimum-core candidate quick_check failed: {quick!r}")
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if foreign_key_rows:
            raise RuntimeError(
                f"Minimum-core candidate foreign_key_check returned {foreign_key_rows} rows"
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if application_id != APPLICATION_ID or user_version != SCHEMA_VERSION:
            raise RuntimeError("Minimum-core candidate SQLite header mismatch")

    return (
        race_comparisons,
        runner_comparisons,
        quick,
        foreign_key_rows,
        application_id,
        user_version,
    )
