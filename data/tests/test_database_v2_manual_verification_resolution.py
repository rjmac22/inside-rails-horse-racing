from __future__ import annotations

import csv
import sqlite3

import pytest

from inside_rails.database.governed_integration_references import (
    GovernedReferenceLoadError,
    _insert_manual_verifications,
)
from inside_rails.database.schema import create_governed_integration_schema
from inside_rails.manual_verifications import EXPECTED_COLUMNS


RACE_DATE = "2023-12-23"
RACE_COURSE = "Gulfstream Park (USA)"
RACE_OFF = "9:36"
HORSE = "Great Navigator (USA)"
TIMESTAMP = "2026-08-09T00:00:00.000000Z"
COMMIT = "1" * 40


def _connection_with_missing_runner_race() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)

    # These tests isolate source-locator resolution. Foreign keys are disabled so
    # the fixture does not have to recreate the full Source Version 1 metadata
    # hierarchy, but the structural race trigger still requires an accepted
    # governance release for the race's source version. Seed that exact minimum
    # governance state explicitly rather than weakening the production trigger.
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute(
        """
        INSERT INTO governance_release (
            governance_release_id, governance_release_code, source_version_id,
            governance_method_id, release_status, accepted_date,
            repository_commit, population_predicate, release_description,
            superseded_by_release_id, created_at_utc
        ) VALUES (
            1, 'gr:fixture:v2', 1, 1, 'accepted', '2026-08-09', ?,
            'rowid <> 1', 'Fixture accepted governance.', NULL, ?
        )
        """,
        (COMMIT, TIMESTAMP),
    )
    connection.execute(
        """
        INSERT INTO core_source_race_occurrence VALUES (
            1, 'race:fixture', 1, ?, ?, ?, 8, 1
        )
        """,
        (RACE_DATE, RACE_COURSE, RACE_OFF),
    )
    return connection


def _write_verification_csv(tmp_path, *, database_action: str) -> str:
    path = tmp_path / "manual_verifications.csv"
    row = {
        "verification_id": "NB15-BTN-FIXTURE",
        "subject_type": "runner",
        "source_date": RACE_DATE,
        "source_course": RACE_COURSE,
        "source_off": RACE_OFF,
        "source_horse": HORSE,
        "source_field": "runner record; pos",
        "raw_source_value": "runner absent; source ran=8",
        "verification_question": "Was the runner omitted from the source?",
        "verified_value": "published_runners=9; missing_horse=Great Navigator (USA); verified_pos=5",
        "verification_status": "confirmed",
        "evidence_type": "published_result",
        "evidence_locator": "https://example.invalid/result",
        "evidence_accessed_date": "2026-07-30",
        "governing_notebook": "15",
        "confidence": "high",
        "notes": "Fixture for a confirmed runner absent from immutable source rows.",
        "database_action": database_action,
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerow(row)
    return str(path)


def test_missing_runner_supplementation_verification_allows_null_source_record(tmp_path) -> None:
    connection = _connection_with_missing_runner_race()
    try:
        path = _write_verification_csv(tmp_path, database_action="source_supplementation")
        ids, _ = _insert_manual_verifications(
            connection,
            path,
            governance_release_id=1,
            field_ids={},
        )

        assert ids == {"NB15-BTN-FIXTURE": 1}
        assert connection.execute(
            """
            SELECT source_record_id, source_race_occurrence_id, source_horse,
                   database_action
            FROM governance_manual_verification
            """
        ).fetchone() == (None, 1, HORSE, "source_supplementation")
    finally:
        connection.close()


def test_non_supplementation_runner_verification_must_resolve_existing_source_record(tmp_path) -> None:
    connection = _connection_with_missing_runner_race()
    try:
        path = _write_verification_csv(tmp_path, database_action="evidence_only")
        with pytest.raises(
            GovernedReferenceLoadError,
            match="did not resolve safely to one source record",
        ):
            _insert_manual_verifications(
                connection,
                path,
                governance_release_id=1,
                field_ids={},
            )
    finally:
        connection.close()
