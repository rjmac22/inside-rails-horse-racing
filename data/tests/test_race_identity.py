from __future__ import annotations

import sqlite3

import pytest

from inside_rails.race_identity import (
    RACE_IDENTITY_COLUMNS,
    RACE_VALIDATION_COLUMNS,
    RUNNER_IDENTITY_COLUMNS,
    RaceIdentity,
    RunnerRecordIdentity,
    profile_race_identity,
    race_identity,
    runner_record_identity,
)


def test_governed_identity_columns_separate_matching_from_validation() -> None:
    assert RACE_IDENTITY_COLUMNS == ("date", "course", "off")
    assert RACE_VALIDATION_COLUMNS == ("race_name",)
    assert RUNNER_IDENTITY_COLUMNS == ("date", "course", "off", "horse")


def test_race_identity_preserves_raw_values() -> None:
    record = {"date": "2026-01-01", "course": " Ascot ", "off": "1:00"}
    assert race_identity(record) == RaceIdentity("2026-01-01", " Ascot ", "1:00")


def test_runner_identity_adds_horse_without_using_runner_number() -> None:
    record = {
        "date": "2026-01-01",
        "course": "Ascot",
        "off": "13:00",
        "horse": "Horse One",
        "num": 0,
    }
    assert runner_record_identity(record) == RunnerRecordIdentity(
        RaceIdentity("2026-01-01", "Ascot", "13:00"),
        "Horse One",
    )


def test_identity_rejects_missing_fields() -> None:
    with pytest.raises(KeyError, match="off"):
        race_identity({"date": "2026-01-01", "course": "Ascot"})


def test_identity_rejects_null_fields() -> None:
    with pytest.raises(ValueError, match="course"):
        race_identity({"date": "2026-01-01", "course": None, "off": "13:00"})


def create_source() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE data (
            date TEXT, course TEXT, off TEXT, race_name TEXT,
            race_id TEXT, num INTEGER, horse TEXT
        )
        """
    )
    connection.executemany(
        "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("date", "course", "off", "race_name", "race_id", "num", "horse"),
            ("2026-01-01", "Ascot", "13:00", "Race A", "10", 1, "Horse One"),
            ("2026-01-01", "Ascot", "13:00", "Race A", "10", 2, "Horse Two"),
            ("2026-01-01", "Ascot", "13:30", "Race B", "10", 1, "Horse Three"),
            ("2026-01-01", "Ascot", "14:00", "Race C", "11", 1, "Horse Four"),
            ("2026-01-01", "Ascot", "14:00", "Race C", "11", 1, "Horse Five"),
        ],
    )
    return connection


def test_profile_reconciles_candidate_identity_and_known_bad_keys() -> None:
    connection = create_source()
    try:
        profile = profile_race_identity(connection)
    finally:
        connection.close()

    assert profile["data_rows"] == 5
    assert profile["candidate_races"] == 3
    assert profile["candidate_runner_records"] == 5
    assert profile["race_name_collisions"] == 0
    assert profile["source_race_id_collisions_within_candidate_race"] == 0
    assert profile["duplicate_candidate_runner_records"] == 0
    assert profile["colliding_date_race_id_groups"] == 1
    assert profile["duplicate_runner_number_groups"] == 1
    assert profile["distinct_source_race_ids"] == 2
    assert profile["distinct_date_race_ids"] == 2
    assert profile["distinct_dates"] == 1
    assert profile["minimum_source_rowid"] == 2
    assert profile["maximum_source_rowid"] == 6
    assert profile["null_identity_rows"] == 0


def test_profile_excludes_blank_runner_numbers_from_duplicate_groups() -> None:
    connection = create_source()
    try:
        connection.executemany(
            "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("2026-01-01", "Ascot", "14:30", "Race D", "12", None, "Horse Six"),
                ("2026-01-01", "Ascot", "14:30", "Race D", "12", None, "Horse Seven"),
            ],
        )
        profile = profile_race_identity(connection)
    finally:
        connection.close()

    assert profile["duplicate_runner_number_groups"] == 1


def test_profile_detects_race_name_collision_inside_candidate_slot() -> None:
    connection = create_source()
    try:
        connection.execute(
            "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("2026-01-01", "Ascot", "13:00", "Different Name", "10", 3, "Horse Six"),
        )
        profile = profile_race_identity(connection)
    finally:
        connection.close()

    assert profile["race_name_collisions"] == 1


def test_profile_detects_duplicate_candidate_runner_record() -> None:
    connection = create_source()
    try:
        connection.execute(
            "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("2026-01-01", "Ascot", "13:00", "Race A", "10", 9, "Horse One"),
        )
        profile = profile_race_identity(connection)
    finally:
        connection.close()

    assert profile["duplicate_candidate_runner_records"] == 1
