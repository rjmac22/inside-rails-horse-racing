from __future__ import annotations

from pathlib import Path
import sqlite3

from inside_rails.database.racecourse_identity_reference import (
    EXPECTED_COURSE_INVENTORY_COUNT,
    EXPECTED_NOTEBOOK_COUNT,
    EXPECTED_RACECOURSE_IDENTITY_COUNT,
    EXPECTED_SOURCE_LABEL_COUNT,
    EXPECTED_STABLE_COURSE_IDENTITY_COUNT,
    EXPECTED_UNRESOLVED_COUNT,
    RESOLVED_STABLE_COLLAPSES,
    Study03ReferenceSummary,
    collect_study03_reference,
)
from inside_rails.database.racecourse_identity_source_v1 import (
    EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT,
    EXPLICIT_SOURCE_LABEL_METHOD,
    NEWMARKET_JULY_RACECOURSE,
    NEWMARKET_ROWLEY_RACECOURSE,
    SOURCE_LABEL_CONVENTION_METHOD,
    apply_source_v1_racecourse_resolution,
)
from inside_rails.database.schema import (
    RACECOURSE_IDENTITY_SCHEMA_VERSION,
    create_racecourse_identity_schema,
)
from inside_rails.database.study03_snapshot import require_completed_study03_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_completed_study03_snapshot_is_unchanged() -> None:
    require_completed_study03_snapshot(ROOT)


def test_completed_study03_reference_population_is_exact() -> None:
    notebooks, mappings, inventory, unresolved = collect_study03_reference(ROOT)

    assert len(notebooks) == EXPECTED_NOTEBOOK_COUNT
    assert len(mappings) == EXPECTED_SOURCE_LABEL_COUNT
    assert (
        len({row["racecourse_identity"] for row in mappings})
        == EXPECTED_RACECOURSE_IDENTITY_COUNT
    )
    assert len(inventory) == EXPECTED_COURSE_INVENTORY_COUNT
    assert len(
        {
            (row["racecourse_identity"], row["stable_course_identity"])
            for row in inventory
        }
    ) == EXPECTED_STABLE_COURSE_IDENTITY_COUNT
    assert len(unresolved) == EXPECTED_UNRESOLVED_COUNT


def test_study03_only_applies_the_governed_national_identity_collapses() -> None:
    assert RESOLVED_STABLE_COLLAPSES == {
        ("Southwell", "All-Weather Flat Track — Fibresand"): "All-Weather Flat Track",
        ("Southwell", "All-Weather Flat Track — Tapeta"): "All-Weather Flat Track",
        ("Newcastle", "Former Flat Turf Track"): "Flat Track",
        ("Newcastle", "All-Weather Tapeta Track"): "Flat Track",
        ("Windsor", "Traditional Figure-of-Eight Turf Course"): "Windsor Turf Course",
        ("Windsor", "2024/25 Jump Extended Left-Hand Oval"): "Windsor Turf Course",
        ("Windsor", "2025/26 Jump Figure-of-Eight Configuration"): "Windsor Turf Course",
    }


def test_database_v4_schema_can_be_created_from_clean_database() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        create_racecourse_identity_schema(connection)
        assert (
            connection.execute("PRAGMA user_version").fetchone()[0]
            == RACECOURSE_IDENTITY_SCHEMA_VERSION
        )
        objects = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type IN ('table','view')"
            )
        }
        assert {
            "reference_racecourse_identity",
            "reference_course_racecourse_map",
            "reference_racecourse_course_identity",
            "reference_racecourse_course_inventory",
            "governance_study03_racecourse_notebook",
            "governance_racecourse_unresolved_question",
            "view_gb_racecourse_identity_reference",
            "view_gb_course_track_identities",
            "view_gb_reconciled_race_occurrences_with_racecourse",
        } <= objects
        map_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(reference_course_racecourse_map)")
        }
        assert {
            "study03_grouping_name",
            "racecourse_resolution_method",
            "racecourse_resolution_evidence",
        } <= map_columns
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()


def test_source_v1_newmarket_parent_is_split_into_two_racecourses() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            """
            CREATE TABLE reference_racecourse_identity (
                racecourse_identity_id INTEGER PRIMARY KEY,
                racecourse_identity_code TEXT NOT NULL UNIQUE,
                racecourse_name TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                identity_kind TEXT NOT NULL,
                governance_release_id INTEGER NOT NULL,
                UNIQUE(jurisdiction, racecourse_name)
            );
            CREATE TABLE reference_course (
                reference_course_id INTEGER PRIMARY KEY,
                candidate_course_label TEXT NOT NULL,
                candidate_jurisdiction TEXT NOT NULL
            );
            CREATE TABLE reference_course_racecourse_map (
                reference_course_id INTEGER PRIMARY KEY,
                racecourse_identity_id INTEGER NOT NULL,
                study03_grouping_name TEXT NOT NULL,
                racecourse_resolution_method TEXT NOT NULL,
                racecourse_resolution_evidence TEXT NOT NULL
            );
            CREATE TABLE reference_racecourse_course_identity (
                course_identity_id INTEGER PRIMARY KEY,
                course_identity_code TEXT NOT NULL UNIQUE,
                racecourse_identity_id INTEGER NOT NULL,
                course_name TEXT NOT NULL
            );
            CREATE TABLE governance_racecourse_unresolved_question (
                unresolved_question_id INTEGER PRIMARY KEY,
                racecourse_identity_id INTEGER NOT NULL
            );
            """
        )
        connection.execute(
            """
            INSERT INTO reference_racecourse_identity
            VALUES (1, 'rc:gb:newmarket', 'Newmarket', 'Great Britain',
                    'analytical_grouping', 4)
            """
        )
        for identity_id in range(2, 61):
            connection.execute(
                """
                INSERT INTO reference_racecourse_identity
                VALUES (?, ?, ?, 'Great Britain', 'venue', 4)
                """,
                (identity_id, f"rc:gb:dummy-{identity_id}", f"Dummy {identity_id}"),
            )
        connection.executemany(
            "INSERT INTO reference_course VALUES (?, ?, 'Great Britain')",
            [
                (10, "Newmarket"),
                (11, "Newmarket (July)"),
                (12, "Dummy"),
            ],
        )
        connection.executemany(
            """
            INSERT INTO reference_course_racecourse_map
            VALUES (?, ?, 'pending_build_resolution',
                    'pending_build_resolution', 'pending_build_resolution')
            """,
            [
                (10, 1),
                (11, 1),
                (12, 2),
            ],
        )
        connection.executemany(
            "INSERT INTO reference_racecourse_course_identity VALUES (?, ?, 1, ?)",
            [
                (20, "trk:gb:newmarket:rowley-mile-course", "Rowley Mile Course"),
                (21, "trk:gb:newmarket:july-course", "July Course"),
            ],
        )
        summary = Study03ReferenceSummary(60, 65, 60, 90, 86, 7)

        refined = apply_source_v1_racecourse_resolution(
            connection,
            summary,
            governance_release_id=4,
        )

        assert refined.racecourse_identity_count == EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT
        assert connection.execute(
            "SELECT COUNT(*) FROM reference_racecourse_identity"
        ).fetchone()[0] == 61
        assert connection.execute(
            """
            SELECT racecourse_name, identity_kind
            FROM reference_racecourse_identity
            WHERE racecourse_identity_id=1
            """
        ).fetchone() == (NEWMARKET_ROWLEY_RACECOURSE, "venue")
        july_id = connection.execute(
            """
            SELECT racecourse_identity_id
            FROM reference_racecourse_identity
            WHERE racecourse_name=?
            """,
            (NEWMARKET_JULY_RACECOURSE,),
        ).fetchone()[0]
        assert connection.execute(
            """
            SELECT course.candidate_course_label,
                   racecourse.racecourse_name,
                   map.racecourse_resolution_method,
                   map.study03_grouping_name
            FROM reference_course AS course
            JOIN reference_course_racecourse_map AS map
              ON map.reference_course_id=course.reference_course_id
            JOIN reference_racecourse_identity AS racecourse
              ON racecourse.racecourse_identity_id=map.racecourse_identity_id
            WHERE course.candidate_course_label IN ('Newmarket','Newmarket (July)')
            ORDER BY CASE course.candidate_course_label WHEN 'Newmarket' THEN 1 ELSE 2 END
            """
        ).fetchall() == [
            ("Newmarket", NEWMARKET_ROWLEY_RACECOURSE, SOURCE_LABEL_CONVENTION_METHOD, "Newmarket"),
            (
                "Newmarket (July)",
                NEWMARKET_JULY_RACECOURSE,
                EXPLICIT_SOURCE_LABEL_METHOD,
                "Newmarket",
            ),
        ]
        assert connection.execute(
            """
            SELECT racecourse_identity_id
            FROM reference_racecourse_course_identity
            WHERE course_name='July Course'
            """
        ).fetchone()[0] == july_id
        assert connection.execute(
            """
            SELECT racecourse_identity_id
            FROM reference_racecourse_course_identity
            WHERE course_name='Rowley Mile Course'
            """
        ).fetchone()[0] == 1
    finally:
        connection.close()
