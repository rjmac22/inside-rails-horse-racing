"""Batched race and runner population for complete minimum-core candidates."""

from __future__ import annotations

import sqlite3

from inside_rails.database.identifiers import (
    runner_participation_code,
    source_race_occurrence_code,
)


def populate_races(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    expected_race_count: int,
    batch_size: int,
) -> tuple[int, int]:
    cursor = connection.execute(
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
    sequence = 0
    batch_count = 0
    prior_minimum = 0
    insert_sql = (
        "INSERT INTO core_source_race_occurrence VALUES (?, ?, 1, ?, ?, ?, ?, 1)"
    )
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        prepared: list[tuple[object, ...]] = []
        for raw_date, raw_course, raw_off, minimum_rowid, runner_count in rows:
            if raw_date is None or raw_course is None or raw_off is None:
                raise RuntimeError("Admitted race grouping values must not be NULL")
            minimum = int(minimum_rowid)
            if minimum <= prior_minimum:
                raise RuntimeError("Race-group minimum source rowids are not increasing")
            prior_minimum = minimum
            sequence += 1
            prepared.append(
                (
                    sequence,
                    source_race_occurrence_code(source_sha256, sequence),
                    raw_date,
                    raw_course,
                    raw_off,
                    int(runner_count),
                )
            )
        connection.executemany(insert_sql, prepared)
        batch_count += 1

    if sequence != expected_race_count:
        raise RuntimeError(
            f"Race occurrence count mismatch: expected {expected_race_count}; "
            f"observed {sequence}"
        )
    return sequence, batch_count


def populate_runners(
    connection: sqlite3.Connection,
    *,
    source_sha256: bytes,
    expected_runner_count: int,
    batch_size: int,
) -> tuple[int, int]:
    cursor = connection.execute(
        """
        SELECT raw.source_record_id, raw.source_rowid,
               race.source_race_occurrence_id
        FROM source_raceform_v1_record AS raw
        JOIN core_source_race_occurrence AS race
          ON race.source_version_id = raw.source_version_id
         AND race.raw_date IS raw."date"
         AND race.raw_course IS raw."course"
         AND race.raw_off IS raw."off"
        WHERE raw.source_version_id = 1
          AND raw.source_relation_id = 1
          AND raw.structural_status = 'admitted_runner_record'
        ORDER BY raw.source_rowid
        """
    )
    runner_id = 0
    batch_count = 0
    prior_rowid = 0
    insert_sql = (
        "INSERT INTO core_runner_participation VALUES "
        "(?, ?, ?, ?, 'admitted_runner_record', 1)"
    )
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        prepared: list[tuple[object, ...]] = []
        for source_record_id, source_rowid, race_id in rows:
            rowid = int(source_rowid)
            if rowid <= prior_rowid:
                raise RuntimeError("Runner source rowids are not increasing")
            prior_rowid = rowid
            runner_id += 1
            prepared.append(
                (
                    runner_id,
                    runner_participation_code(source_sha256, rowid),
                    int(race_id),
                    int(source_record_id),
                )
            )
        connection.executemany(insert_sql, prepared)
        batch_count += 1

    if runner_id != expected_runner_count:
        raise RuntimeError(
            f"Runner participation count mismatch: expected {expected_runner_count}; "
            f"observed {runner_id}"
        )
    return runner_id, batch_count
