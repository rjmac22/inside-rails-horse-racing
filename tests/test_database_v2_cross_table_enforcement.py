from __future__ import annotations

import sqlite3

import pytest

from inside_rails.database.schema import create_governed_integration_schema


def _connection_without_fk_fixture_burden() -> sqlite3.Connection:
    """Create v2 schema and disable FKs only to isolate cross-table triggers.

    These tests exercise trigger logic rather than the already-tested foreign-key
    graph. Disabling FKs after schema creation keeps the fixtures intentionally
    tiny while leaving every Database v2 trigger active.
    """

    connection = sqlite3.connect(":memory:")
    create_governed_integration_schema(connection)
    connection.execute("PRAGMA foreign_keys = OFF")
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 0
    return connection


def test_jurisdiction_context_rejects_overlapping_effective_periods() -> None:
    connection = _connection_without_fk_fixture_burden()
    try:
        connection.execute(
            """
            INSERT INTO reference_jurisdiction_context VALUES (
                1, 'IRE', 'Flat', '2015-01-01', '2017-12-31',
                'Irish Turf Club', 'HRI', 'source_type_retained',
                'unresolved', 'fixture', 1
            )
            """
        )
        with pytest.raises(sqlite3.IntegrityError, match="effective periods overlap"):
            connection.execute(
                """
                INSERT INTO reference_jurisdiction_context VALUES (
                    2, 'IRE', 'Flat', '2017-12-31', '2018-12-31',
                    'IHRB', 'HRI', 'source_type_retained',
                    'unresolved', 'fixture', 1
                )
                """
            )

        # The day after the first inclusive period is a valid new context.
        connection.execute(
            """
            INSERT INTO reference_jurisdiction_context VALUES (
                2, 'IRE', 'Flat', '2018-01-01', NULL,
                'IHRB', 'HRI', 'source_type_retained',
                'unresolved', 'fixture', 1
            )
            """
        )
        assert connection.execute(
            "SELECT COUNT(*) FROM reference_jurisdiction_context"
        ).fetchone()[0] == 2
    finally:
        connection.close()


def test_candidate_membership_rejects_cross_role_source_label() -> None:
    connection = _connection_without_fk_fixture_burden()
    try:
        connection.execute(
            """
            INSERT INTO identity_participant_source_label VALUES (
                1, 'participant-label:jockey:fixture', 'jockey', 'Same Text',
                '2020-01-01', '2020-01-02', 2, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO identity_participant_candidate VALUES (
                1, 'trainer-candidate:fixture', 'trainer', 'same text',
                'fixture_method', NULL, NULL, 'unresolved', 'unresolved',
                'Fixture candidate.', 'low', NULL, NULL, NULL, NULL,
                'deferred_until_material_use', NULL, 'preserve_raw_unresolved', 1
            )
            """
        )

        with pytest.raises(sqlite3.IntegrityError, match="member role is incompatible"):
            connection.execute(
                "INSERT INTO identity_participant_candidate_label VALUES (1, 1, NULL, 1)"
            )
    finally:
        connection.close()


def test_source_label_can_have_only_one_accepted_identity_mapping() -> None:
    connection = _connection_without_fk_fixture_burden()
    try:
        connection.execute(
            """
            INSERT INTO identity_participant_source_label VALUES (
                1, 'participant-label:jockey:fixture', 'jockey', 'Mlle Example',
                '2020-01-01', '2023-01-01', 5, 1
            )
            """
        )
        for identity_id in (1, 2):
            connection.execute(
                """
                INSERT INTO identity_participant VALUES (
                    ?, ?, 'jockey', 'person_label_identity',
                    'provisional_source_label_identity', 'fixture_method',
                    'high', 'accepted', '22', 1
                )
                """,
                (identity_id, f"JOCKEY-PROVISIONAL-FIXTURE-{identity_id:04d}"),
            )
            connection.execute(
                """
                INSERT INTO identity_participant_candidate VALUES (
                    ?, ?, 'jockey', ?, 'fixture_method', NULL, NULL,
                    'same_person', 'accepted', 'Fixture.', 'high', NULL,
                    NULL, NULL, NULL, 'completed', NULL,
                    'map_raw_label_to_provisional_jockey_identity', 1
                )
                """,
                (
                    identity_id,
                    f"JOCKEY-STRICT-FIXTURE-{identity_id:04d}",
                    f"fixture-{identity_id}",
                ),
            )
            connection.execute(
                "INSERT INTO identity_participant_candidate_label VALUES (?, 1, NULL, 1)",
                (identity_id,),
            )

        connection.execute(
            """
            INSERT INTO identity_participant_label_map VALUES (
                1, 1, 1, 1, NULL, 'accepted', 'fixture_method', 'high',
                NULL, 'map_raw_label_to_provisional_jockey_identity', NULL, NULL, 1
            )
            """
        )
        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
            connection.execute(
                """
                INSERT INTO identity_participant_label_map VALUES (
                    2, 2, 1, 2, NULL, 'accepted', 'fixture_method', 'high',
                    NULL, 'map_raw_label_to_provisional_jockey_identity', NULL, NULL, 1
                )
                """
            )
    finally:
        connection.close()
