from __future__ import annotations

import sqlite3

import pytest

from inside_rails.database.schema import create_governed_integration_schema


def _candidate_values(*, decision_status: str, confidence: str) -> tuple[object, ...]:
    return (
        1,
        "candidate:test",
        "jockey",
        "fixture key",
        "fixture_method",
        None,
        "not_started",
        "unresolved" if decision_status == "unresolved" else "same_person",
        decision_status,
        "Fixture decision basis.",
        confidence,
        None,
        None,
        None,
        None,
        "deferred_until_material_use" if decision_status == "unresolved" else "completed",
        None,
        "preserve_raw_unresolved" if decision_status == "unresolved" else "map_labels",
        1,
    )


def test_unresolved_candidate_may_preserve_blank_unassessed_confidence() -> None:
    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    try:
        # This fixture isolates the candidate confidence-domain CHECK. Notebook 22
        # has unresolved jockey review rows whose persisted confidence is blank.
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute(
            "INSERT INTO identity_participant_candidate VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            _candidate_values(decision_status="unresolved", confidence=""),
        )
        assert connection.execute(
            "SELECT decision_status, confidence FROM identity_participant_candidate"
        ).fetchone() == ("unresolved", "")
    finally:
        connection.close()


def test_decided_candidate_cannot_have_blank_confidence() -> None:
    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO identity_participant_candidate VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _candidate_values(decision_status="accepted", confidence=""),
            )
    finally:
        connection.close()
