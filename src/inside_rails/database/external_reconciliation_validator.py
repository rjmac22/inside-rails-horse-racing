"""Independent read-only validation for Database v3 reconciliation candidates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from time import perf_counter

from inside_rails.database.external_reconciliation import (
    EXPECTED_RESOLUTIONS,
    EXPECTED_TOTAL_MANUAL_VERIFICATIONS,
)
from inside_rails.database.external_reconciliation_candidate import (
    EXPECTED_BASE_RELEASE_SHA256,
    EXPECTED_BASE_RELEASE_SIZE_BYTES,
    EXPECTED_ADMITTED_RECORD_COUNT,
    EXPECTED_PHYSICAL_RECORD_COUNT,
    EXPECTED_RACE_OCCURRENCE_COUNT,
    EXPECTED_RUNNER_PARTICIPATION_COUNT,
)
from inside_rails.database.minimum_core_candidate_io import require_no_sidecars, validate_file_hash
from inside_rails.database.schema import (
    APPLICATION_ID,
    EXTERNAL_RECONCILIATION_SCHEMA_VERSION,
    configure_governed_connection,
)
from inside_rails.source_sqlite import connect_read_only


@dataclass(frozen=True)
class ExternalReconciliationValidationSummary:
    candidate_path: str
    base_release_path: str
    manifest_status: str
    physical_source_rows: int
    admitted_source_rows: int
    race_rows: int
    runner_rows: int
    manual_verification_rows: int
    resolution_rows: int
    reconciled_race_rows: int
    reconciled_source_runner_rows: int
    reconciled_runner_rows: int
    raw_record_rows_compared: int
    structural_race_rows_compared: int
    structural_runner_rows_compared: int
    quick_check: str
    foreign_key_check_rows: int
    elapsed_seconds: float


def _compare_ordered_rows(
    candidate: sqlite3.Connection,
    base: sqlite3.Connection,
    query: str,
    *,
    label: str,
) -> int:
    left = candidate.execute(query)
    right = base.execute(query)
    count = 0
    while True:
        left_row = left.fetchone()
        right_row = right.fetchone()
        if left_row is None or right_row is None:
            if left_row != right_row:
                raise RuntimeError(f"Database v3 changed {label} row count/order")
            break
        if tuple(left_row) != tuple(right_row):
            raise RuntimeError(
                f"Database v3 changed {label} at compared row {count + 1}: "
                f"candidate={tuple(left_row)!r}, base={tuple(right_row)!r}"
            )
        count += 1
    return count


def _assert_exact_reconciliations(connection: sqlite3.Connection) -> None:
    almendares = connection.execute(
        """
        SELECT raw_sp, governed_starting_price_numerator,
               governed_starting_price_denominator,
               governed_starting_price_favourite_status,
               governed_starting_price_value_status
        FROM view_reconciled_source_runner_participations
        WHERE source_rowid = 1708860
        """
    ).fetchone()
    if almendares != ("F", 5, 2, "favourite", "externally_corrected"):
        raise RuntimeError(f"Almendares reconciliation mismatch: {almendares!r}")

    cinnamon = connection.execute(
        """
        SELECT raw_pos, governed_finish_position, external_result_context
        FROM view_reconciled_source_runner_participations
        WHERE source_rowid = 55516
        """
    ).fetchone()
    if cinnamon != (10, 12, "dead_heat_for_12th"):
        raise RuntimeError(f"Cinnamon Carter reconciliation mismatch: {cinnamon!r}")

    race_expected = {
        ("2024-06-26", "Ohi (JPN)", "11:07"): 13,
        ("2024-09-03", "Morioka (JPN)", "11:07"): 12,
        ("2023-12-23", "Gulfstream Park (USA)", "9:36"): 9,
    }
    for key, expected in race_expected.items():
        row = connection.execute(
            """
            SELECT governed_runner_count, governed_runner_count_status
            FROM view_reconciled_race_occurrences
            WHERE CAST(raw_date AS TEXT)=? AND CAST(raw_course AS TEXT)=? AND CAST(raw_off AS TEXT)=?
            """,
            key,
        ).fetchone()
        if row != (expected, "externally_corrected"):
            raise RuntimeError(f"Governed runner count mismatch for {key}: {row!r}")

    distances = connection.execute(
        """
        SELECT CAST(raw_date AS TEXT), CAST(raw_course AS TEXT), CAST(raw_off AS TEXT),
               external_official_distance_metres
        FROM view_reconciled_race_occurrences
        WHERE official_distance_resolution_code IS NOT NULL
        ORDER BY 1,2,3
        """
    ).fetchall()
    if distances != [
        ("2015-01-04", "Kyoto (JPN)", "6:45", 1600.0),
        ("2015-01-25", "Sha Tin (HK)", "8:35", 1600.0),
    ]:
        raise RuntimeError(f"Official-distance reconciliation mismatch: {distances!r}")

    age_band = connection.execute(
        """
        SELECT age_band_raw, governed_age_band, governed_stated_minimum_age,
               governed_stated_maximum_age, governed_age_band_open_ended
        FROM view_reconciled_race_occurrences
        WHERE CAST(raw_date AS TEXT)='2017-05-16'
          AND CAST(raw_course AS TEXT)='Compiegne (FR)'
          AND CAST(raw_off AS TEXT)='1:35'
        """
    ).fetchone()
    if age_band != ("5yo", "5yo+", 5, None, 1):
        raise RuntimeError(f"Compiegne age-band reconciliation mismatch: {age_band!r}")

    ecstasy = connection.execute(
        """
        SELECT raw_age, governed_age, governed_age_status
        FROM view_reconciled_source_runner_participations
        WHERE raw_horse='Ecstasy (USA)' AND raw_date='2024-07-27'
          AND raw_course='Woodbine (CAN)' AND raw_off='9:47'
        """
    ).fetchone()
    if ecstasy != (31, 3, "externally_corrected"):
        raise RuntimeError(f"Ecstasy age reconciliation mismatch: {ecstasy!r}")

    gavea = connection.execute(
        """
        SELECT raw_ovr_btn, raw_btn, governed_ovr_btn_numeric, governed_btn_numeric
        FROM view_reconciled_source_runner_participations
        WHERE raw_horse='Gevrey-Chambertain' AND raw_date='2025-04-06'
          AND raw_course='Gavea (BRZ)' AND raw_off='7:35'
        """
    ).fetchone()
    if gavea != (0, 0, 16.5, 16.5):
        raise RuntimeError(f"Gavea beaten-distance reconciliation mismatch: {gavea!r}")

    invalidated = connection.execute(
        """
        SELECT raw_horse, governed_ovr_btn_numeric, governed_btn_numeric,
               governed_ovr_btn_status, governed_btn_status, external_btn_text
        FROM view_reconciled_source_runner_participations
        WHERE ovr_btn_resolution_code IS NOT NULL
          AND raw_horse IN ('Nardo (FR)','Red Fog (USA)','Cabernet Franc (FR)')
        ORDER BY raw_horse
        """
    ).fetchall()
    if len(invalidated) != 3 or any(row[1] is not None or row[2] is not None for row in invalidated):
        raise RuntimeError(f"Known-wrong beaten distances remain analytically numeric: {invalidated!r}")
    nardo = next(row for row in invalidated if row[0] == "Nardo (FR)")
    if nardo[5] != "head":
        raise RuntimeError(f"Nardo text correction missing: {nardo!r}")

    actual_off = connection.execute(
        """
        SELECT COUNT(*) FROM view_reconciled_race_occurrences
        WHERE external_actual_off_time_uk_text IS NOT NULL
        """
    ).fetchone()[0]
    if int(actual_off) != 3:
        raise RuntimeError(f"Expected 3 actual-off enrichments; observed {actual_off}")

    prize = connection.execute(
        """
        SELECT external_official_prize_currency, COUNT(*), SUM(external_official_prize_amount)
        FROM view_reconciled_source_runner_participations
        WHERE external_official_prize_amount IS NOT NULL
        GROUP BY external_official_prize_currency
        ORDER BY external_official_prize_currency
        """
    ).fetchall()
    if prize != [("EUR", 5, 5000000.0), ("USD", 12, 16300000.0)]:
        raise RuntimeError(f"Official prize enrichment mismatch: {prize!r}")


def validate_external_reconciliation_candidate(
    candidate_path: str | Path,
    base_release_path: str | Path,
) -> ExternalReconciliationValidationSummary:
    """Validate v3 without writing either candidate or immutable v2 base."""

    started = perf_counter()
    candidate_path = Path(candidate_path).expanduser().resolve()
    base_release_path = Path(base_release_path).expanduser().resolve()
    require_no_sidecars(candidate_path, label="Database v3 candidate")
    require_no_sidecars(base_release_path, label="Accepted Database v2 release")
    if base_release_path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError("Accepted Database v2 size changed")
    validate_file_hash(
        base_release_path,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v2 release",
    )

    with connect_read_only(candidate_path) as candidate, connect_read_only(base_release_path) as base:
        configure_governed_connection(candidate, query_only=True)
        configure_governed_connection(base, query_only=True)
        if int(candidate.execute("PRAGMA application_id").fetchone()[0]) != APPLICATION_ID:
            raise RuntimeError("Database v3 application_id mismatch")
        if int(candidate.execute("PRAGMA user_version").fetchone()[0]) != EXTERNAL_RECONCILIATION_SCHEMA_VERSION:
            raise RuntimeError("Database v3 user_version mismatch")
        manifest_rows = candidate.execute(
            """
            SELECT schema_version, physical_record_count, admitted_record_count,
                   excluded_record_count, race_occurrence_count,
                   runner_participation_count, build_status, failure_reason
            FROM import_manifest
            """
        ).fetchall()
        if len(manifest_rows) != 1:
            raise RuntimeError(f"Database v3 manifest count mismatch: {len(manifest_rows)}")
        manifest = manifest_rows[0]
        if tuple(manifest[:6]) != (
            3,
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            1,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
        ):
            raise RuntimeError(f"Database v3 manifest population mismatch: {manifest!r}")
        if manifest[6] not in {"built", "validated", "release_accepted"} or manifest[7] is not None:
            raise RuntimeError(f"Database v3 manifest status is not validatable: {manifest!r}")

        releases = candidate.execute(
            """
            SELECT governance_release_id, release_status, superseded_by_release_id
            FROM governance_release WHERE source_version_id=1 ORDER BY governance_release_id
            """
        ).fetchall()
        if releases != [(1, "superseded", 2), (2, "superseded", 3), (3, "accepted", None)]:
            raise RuntimeError(f"Database v3 governance lineage mismatch: {releases!r}")

        physical_rows = int(candidate.execute("SELECT COUNT(*) FROM source_raceform_v1_record").fetchone()[0])
        admitted_rows = int(candidate.execute("SELECT COUNT(*) FROM core_runner_participation").fetchone()[0])
        race_rows = int(candidate.execute("SELECT COUNT(*) FROM core_source_race_occurrence").fetchone()[0])
        runner_rows = admitted_rows
        manual_rows = int(candidate.execute("SELECT COUNT(*) FROM governance_manual_verification").fetchone()[0])
        resolution_rows = int(candidate.execute("SELECT COUNT(*) FROM governance_external_value_resolution").fetchone()[0])
        if (physical_rows, admitted_rows, race_rows, runner_rows, manual_rows, resolution_rows) != (
            EXPECTED_PHYSICAL_RECORD_COUNT,
            EXPECTED_ADMITTED_RECORD_COUNT,
            EXPECTED_RACE_OCCURRENCE_COUNT,
            EXPECTED_RUNNER_PARTICIPATION_COUNT,
            EXPECTED_TOTAL_MANUAL_VERIFICATIONS,
            EXPECTED_RESOLUTIONS,
        ):
            raise RuntimeError("Database v3 core/reconciliation counts changed")

        race_view = int(candidate.execute("SELECT COUNT(*) FROM view_reconciled_race_occurrences").fetchone()[0])
        source_runner_view = int(candidate.execute("SELECT COUNT(*) FROM view_reconciled_source_runner_participations").fetchone()[0])
        runner_view = int(candidate.execute("SELECT COUNT(*) FROM view_reconciled_runner_records").fetchone()[0])
        if (race_view, source_runner_view, runner_view) != (189043, 1851285, 1851288):
            raise RuntimeError(
                f"Database v3 reconciled view counts changed: {(race_view, source_runner_view, runner_view)!r}"
            )

        raw_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT source_record_id, source_rowid, structural_status, row_sha256 FROM source_raceform_v1_record ORDER BY source_record_id",
            label="raw source mirror",
        )
        race_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT source_race_occurrence_id, source_race_occurrence_code, source_version_id, raw_date, raw_course, raw_off, admitted_runner_count, governance_release_id FROM core_source_race_occurrence ORDER BY source_race_occurrence_id",
            label="structural race core",
        )
        runner_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT runner_participation_id, runner_participation_code, source_race_occurrence_id, source_record_id, source_record_status, governance_release_id FROM core_runner_participation ORDER BY runner_participation_id",
            label="structural runner core",
        )
        _assert_exact_reconciliations(candidate)
        quick = str(candidate.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Database v3 quick_check failed: {quick!r}")
        fk_rows = candidate.execute("PRAGMA foreign_key_check").fetchall()
        if fk_rows:
            raise RuntimeError(f"Database v3 foreign_key_check returned rows: {fk_rows[:5]}")
        manifest_status = str(manifest[6])

    validate_file_hash(
        base_release_path,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v2 release after v3 validation",
    )
    return ExternalReconciliationValidationSummary(
        candidate_path=str(candidate_path),
        base_release_path=str(base_release_path),
        manifest_status=manifest_status,
        physical_source_rows=physical_rows,
        admitted_source_rows=admitted_rows,
        race_rows=race_rows,
        runner_rows=runner_rows,
        manual_verification_rows=manual_rows,
        resolution_rows=resolution_rows,
        reconciled_race_rows=race_view,
        reconciled_source_runner_rows=source_runner_view,
        reconciled_runner_rows=runner_view,
        raw_record_rows_compared=raw_compared,
        structural_race_rows_compared=race_compared,
        structural_runner_rows_compared=runner_compared,
        quick_check=quick,
        foreign_key_check_rows=0,
        elapsed_seconds=perf_counter() - started,
    )


__all__ = [
    "ExternalReconciliationValidationSummary",
    "validate_external_reconciliation_candidate",
]
