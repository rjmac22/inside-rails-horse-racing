"""Governed race and runner-record identity rules from Notebook 03."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Mapping, Sequence

from inside_rails.source_sqlite import quote_identifier

RACE_IDENTITY_COLUMNS = ("date", "course", "off")
RACE_VALIDATION_COLUMNS = ("race_name",)
RUNNER_IDENTITY_COLUMNS = (*RACE_IDENTITY_COLUMNS, "horse")
SOURCE_REFERENCE_COLUMNS = ("race_id", "num")
SOURCE_LINEAGE_COLUMNS = ("rowid",)


@dataclass(frozen=True)
class RaceIdentity:
    date: object
    course: object
    off: object


@dataclass(frozen=True)
class RunnerRecordIdentity:
    race: RaceIdentity
    horse: object


def _require_values(record: Mapping[str, object], columns: Sequence[str]) -> tuple[object, ...]:
    missing = [column for column in columns if column not in record]
    if missing:
        raise KeyError("Missing identity fields: " + ", ".join(missing))

    values = tuple(record[column] for column in columns)
    null_columns = [column for column, value in zip(columns, values, strict=True) if value is None]
    if null_columns:
        raise ValueError("Null identity fields: " + ", ".join(null_columns))
    return values


def race_identity(record: Mapping[str, object]) -> RaceIdentity:
    """Return the candidate natural race identity without normalising raw text."""

    date, course, off = _require_values(record, RACE_IDENTITY_COLUMNS)
    return RaceIdentity(date=date, course=course, off=off)


def runner_record_identity(record: Mapping[str, object]) -> RunnerRecordIdentity:
    """Return the candidate source runner-record identity."""

    race = race_identity(record)
    (horse,) = _require_values(record, ("horse",))
    return RunnerRecordIdentity(race=race, horse=horse)


def profile_race_identity(
    connection: sqlite3.Connection,
    table_name: str = "data",
    header_rowid: int = 1,
) -> dict[str, int]:
    """Reconcile Notebook 03 identity rules against a source table."""

    table = quote_identifier(table_name)
    row = connection.execute(
        f"""
        WITH source AS (
            SELECT rowid, *
            FROM {table}
            WHERE rowid <> ?
        ),
        race_groups AS (
            SELECT date, course, off,
                   COUNT(DISTINCT race_name) AS race_names,
                   COUNT(DISTINCT race_id) AS source_race_ids
            FROM source
            GROUP BY date, course, off
        ),
        runner_groups AS (
            SELECT date, course, off, horse, COUNT(*) AS rows_in_group
            FROM source
            GROUP BY date, course, off, horse
        ),
        date_race_id_groups AS (
            SELECT date, race_id,
                   COUNT(DISTINCT course || '|' || off || '|' || race_name) AS races
            FROM source
            GROUP BY date, race_id
        ),
        number_groups AS (
            SELECT date, course, off, num, COUNT(DISTINCT horse) AS horses
            FROM source
            WHERE num IS NOT NULL
              AND TRIM(CAST(num AS TEXT)) <> ''
            GROUP BY date, course, off, num
        )
        SELECT
            (SELECT COUNT(*) FROM source),
            (SELECT COUNT(*) FROM race_groups),
            (SELECT COUNT(*) FROM runner_groups),
            (SELECT COUNT(*) FROM race_groups WHERE race_names > 1),
            (SELECT COUNT(*) FROM race_groups WHERE source_race_ids > 1),
            (SELECT COUNT(*) FROM runner_groups WHERE rows_in_group > 1),
            (SELECT COUNT(*) FROM date_race_id_groups WHERE races > 1),
            (SELECT COUNT(*) FROM number_groups WHERE horses > 1),
            (SELECT COUNT(DISTINCT race_id) FROM source),
            (SELECT COUNT(DISTINCT date || '|' || race_id) FROM source),
            (SELECT COUNT(DISTINCT date) FROM source),
            (SELECT MIN(rowid) FROM source),
            (SELECT MAX(rowid) FROM source),
            (SELECT COUNT(*) FROM source WHERE date IS NULL OR course IS NULL OR off IS NULL OR horse IS NULL)
        """,
        (header_rowid,),
    ).fetchone()

    if row is None:
        raise RuntimeError(f"Unable to profile race identity for table: {table_name}")

    keys = (
        "data_rows",
        "candidate_races",
        "candidate_runner_records",
        "race_name_collisions",
        "source_race_id_collisions_within_candidate_race",
        "duplicate_candidate_runner_records",
        "colliding_date_race_id_groups",
        "duplicate_runner_number_groups",
        "distinct_source_race_ids",
        "distinct_date_race_ids",
        "distinct_dates",
        "minimum_source_rowid",
        "maximum_source_rowid",
        "null_identity_rows",
    )
    return dict(zip(keys, row, strict=True))
