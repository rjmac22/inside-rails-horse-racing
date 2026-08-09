"""Populate Database v2's complete Notebook 11 temporal representation."""

from __future__ import annotations

import sqlite3

import pandas as pd

from inside_rails.race_time_pipeline import (
    build_canonical_race_times,
    serialise_canonical_race_times,
    validate_exact_temporal_totals,
    validate_timestamp_conversions,
)


EXPECTED_TEMPORAL_ROWS = 189_043
EXPECTED_RESOLVED_ROWS = 169_465
EXPECTED_UNRESOLVED_ROWS = 19_578


class GovernedTimeLoadError(RuntimeError):
    """Raised when Database v2 temporal construction diverges from Notebook 11."""


_RACE_CONTEXT_SQL = """
WITH first_runner AS (
    SELECT source_race_occurrence_id, MIN(source_record_id) AS source_record_id
    FROM core_runner_participation
    GROUP BY source_race_occurrence_id
)
SELECT
    race.source_race_occurrence_id,
    race.raw_date AS date,
    race.raw_course AS course,
    race.raw_off AS off,
    source.race_id,
    governed.race_name_raw AS race_name,
    governed.race_type_raw AS type,
    governed.candidate_course_label,
    governed.candidate_jurisdiction,
    course.iana_timezone
FROM core_source_race_occurrence AS race
JOIN first_runner
  ON first_runner.source_race_occurrence_id = race.source_race_occurrence_id
JOIN source_raceform_v1_record AS source
  ON source.source_record_id = first_runner.source_record_id
JOIN core_source_race_occurrence_governed AS governed
  ON governed.source_race_occurrence_id = race.source_race_occurrence_id
JOIN reference_course AS course
  ON course.reference_course_id = governed.reference_course_id
ORDER BY race.raw_date, race.raw_course, race.raw_off
"""

_INSERT_SQL = """
INSERT INTO core_source_race_occurrence_time (
    source_race_occurrence_id, governance_release_id,
    candidate_a_uk_naive, candidate_b_uk_naive,
    candidate_a_utc, candidate_b_utc,
    candidate_a_course_local, candidate_b_course_local,
    advertised_start_uk, advertised_start_utc,
    advertised_start_course_local, selected_branch,
    decision_method, decision_confidence, temporal_resolution_status
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def _optional_iso_text(value: object) -> str | None:
    """Convert the canonical CSV representation's empty strings back to null."""

    text = str(value)
    return None if text == "" else text


def populate_governed_race_times(
    connection: sqlite3.Connection,
    *,
    governance_release_id: int,
) -> dict[str, int]:
    """Rebuild and persist the complete governed temporal population.

    The input comes from Database v2's already-populated race extension and
    governed course reference. Notebook 11's durable pipeline independently
    reconstructs both pre-boundary candidates, applies the governed selection
    logic and validates the exact method/resolution totals before any temporal
    rows are inserted.
    """

    manifest = connection.execute(
        "SELECT governance_release_id, build_status FROM import_manifest WHERE import_manifest_id = 1"
    ).fetchone()
    if manifest != (governance_release_id, "building"):
        raise GovernedTimeLoadError(
            f"Temporal loading requires the active building manifest; observed {manifest!r}"
        )

    existing = int(
        connection.execute(
            "SELECT COUNT(*) FROM core_source_race_occurrence_time"
        ).fetchone()[0]
    )
    if existing:
        raise GovernedTimeLoadError(
            f"Temporal loading requires an empty target table; found {existing} rows"
        )

    # Load only one row per race plus the governed course timezone. This bounded
    # frame is the natural grain required by Notebook 11 and avoids loading the
    # 1.85 million runner population into the temporal reconstruction.
    race_context = pd.read_sql_query(_RACE_CONTEXT_SQL, connection)
    if len(race_context) != EXPECTED_TEMPORAL_ROWS:
        raise GovernedTimeLoadError(
            f"Expected {EXPECTED_TEMPORAL_ROWS} race contexts; observed {len(race_context)}"
        )
    if not race_context["source_race_occurrence_id"].is_unique:
        raise GovernedTimeLoadError("Temporal input duplicated a source race occurrence")

    race_ids_by_key = {
        (str(row.date), str(row.course), str(row.off)): int(row.source_race_occurrence_id)
        for row in race_context.itertuples(index=False)
    }
    if len(race_ids_by_key) != EXPECTED_TEMPORAL_ROWS:
        raise GovernedTimeLoadError("Temporal input race keys are not unique")

    # Use the durable Notebook 11 pipeline rather than recreating clock-selection
    # logic inside the database build. Its own exact-total and conversion checks
    # must pass before any temporal record is persisted.
    canonical = build_canonical_race_times(
        race_context.drop(columns=["source_race_occurrence_id"])
    )
    validate_exact_temporal_totals(canonical)
    validate_timestamp_conversions(canonical)
    serialised = serialise_canonical_race_times(canonical)

    insert_rows: list[tuple[object, ...]] = []
    for row in serialised.itertuples(index=False):
        race_key = (str(row.date), str(row.course), str(row.off))
        source_race_occurrence_id = race_ids_by_key.get(race_key)
        if source_race_occurrence_id is None:
            raise GovernedTimeLoadError(
                f"Canonical temporal row lost race key {race_key!r}"
            )

        insert_rows.append(
            (
                source_race_occurrence_id,
                governance_release_id,
                _optional_iso_text(row.candidate_a_uk_naive),
                _optional_iso_text(row.candidate_b_uk_naive),
                _optional_iso_text(row.candidate_a_utc),
                _optional_iso_text(row.candidate_b_utc),
                _optional_iso_text(row.candidate_a_course_local),
                _optional_iso_text(row.candidate_b_course_local),
                _optional_iso_text(row.advertised_start_uk),
                _optional_iso_text(row.advertised_start_utc),
                _optional_iso_text(row.advertised_start_course_local),
                _optional_iso_text(row.selected_branch),
                str(row.decision_method),
                str(row.decision_confidence),
                str(row.temporal_resolution_status),
            )
        )

    connection.executemany(_INSERT_SQL, insert_rows)
    connection.commit()

    # Reconcile the persisted table rather than trusting the pre-insert frame.
    # Any lost row, null-state drift or unexpected resolution partition makes
    # the candidate unusable and must stop the build.
    total, resolved, unresolved = connection.execute(
        """
        SELECT
            COUNT(*),
            SUM(temporal_resolution_status = 'resolved'),
            SUM(temporal_resolution_status = 'unresolved')
        FROM core_source_race_occurrence_time
        """
    ).fetchone()
    if (int(total), int(resolved), int(unresolved)) != (
        EXPECTED_TEMPORAL_ROWS,
        EXPECTED_RESOLVED_ROWS,
        EXPECTED_UNRESOLVED_ROWS,
    ):
        raise GovernedTimeLoadError(
            "Persisted temporal population changed: "
            f"{(total, resolved, unresolved)!r}"
        )

    method_counts = {
        str(method): int(count)
        for method, count in connection.execute(
            """
            SELECT decision_method, COUNT(*)
            FROM core_source_race_occurrence_time
            GROUP BY decision_method
            """
        )
    }
    return {
        "total": int(total),
        "resolved": int(resolved),
        "unresolved": int(unresolved),
        **{f"method:{key}": value for key, value in method_counts.items()},
    }


__all__ = ["GovernedTimeLoadError", "populate_governed_race_times"]
