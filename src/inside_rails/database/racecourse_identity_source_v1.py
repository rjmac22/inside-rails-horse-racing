"""Source Version 1 racecourse-level refinements for Database v4.

Study 03 deliberately retained ``Newmarket`` as an analytical parent over the
Rowley Mile and July Course.  Source Version 1, however, carries two distinct
source labels (``Newmarket`` and ``Newmarket (July)``), while official Jockey
Club evidence establishes that the Rowley Mile and July Course are two separate
Newmarket racecourses.

This module performs the bounded Database v4 refinement from the completed
Study 03 parent/grouping model to the actual Source Version 1 racecourse layer.
It does not assign race occurrences to physical tracks below racecourse level.
"""

from __future__ import annotations

from dataclasses import replace
import sqlite3

from inside_rails.database.racecourse_identity_reference import Study03ReferenceSummary

EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT = 61

NEWMARKET_STUDY03_GROUPING = "Newmarket"
NEWMARKET_ROWLEY_SOURCE_LABEL = "Newmarket"
NEWMARKET_JULY_SOURCE_LABEL = "Newmarket (July)"
NEWMARKET_ROWLEY_RACECOURSE = "Newmarket — Rowley Mile"
NEWMARKET_JULY_RACECOURSE = "Newmarket — July Course"
NEWMARKET_ROWLEY_RACECOURSE_CODE = "rc:gb:newmarket-rowley-mile"
NEWMARKET_JULY_RACECOURSE_CODE = "rc:gb:newmarket-july-course"
NEWMARKET_ROWLEY_COURSE = "Rowley Mile Course"
NEWMARKET_JULY_COURSE = "July Course"
NEWMARKET_ROWLEY_COURSE_CODE = "trk:gb:newmarket-rowley-mile:rowley-mile-course"
NEWMARKET_JULY_COURSE_CODE = "trk:gb:newmarket-july-course:july-course"

DIRECT_RESOLUTION_METHOD = "study03_identity_direct"
EXPLICIT_SOURCE_LABEL_METHOD = "explicit_source_label"
SOURCE_LABEL_CONVENTION_METHOD = "source_label_convention"
DIRECT_EVIDENCE = "study03_notebook"
NEWMARKET_CONVENTION_EVIDENCE = (
    "docs/DATABASE_V4_GB_RACECOURSE_IDENTITY_INTEGRATION.md"
    "#newmarket-source-version-1-resolution"
)


def _single_row(connection: sqlite3.Connection, sql: str, parameters: tuple[object, ...]) -> tuple:
    rows = connection.execute(sql, parameters).fetchall()
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one row; observed {len(rows)} for {parameters!r}")
    return tuple(rows[0])


def apply_source_v1_racecourse_resolution(
    connection: sqlite3.Connection,
    summary: Study03ReferenceSummary,
    *,
    governance_release_id: int,
) -> Study03ReferenceSummary:
    """Refine Study 03's Newmarket parent into the two Source Version 1 racecourses.

    The rule is deliberately bounded to Source Version 1.  ``Newmarket (July)``
    is resolved by its explicit source label; plain ``Newmarket`` is resolved to
    the Rowley Mile by the documented Source Version 1 label convention.  Future
    source versions must revalidate the convention rather than inherit it.
    """

    parent_id, parent_code, parent_kind = _single_row(
        connection,
        """
        SELECT racecourse_identity_id, racecourse_identity_code, identity_kind
        FROM reference_racecourse_identity
        WHERE jurisdiction='Great Britain' AND racecourse_name=?
        """,
        (NEWMARKET_STUDY03_GROUPING,),
    )
    parent_id = int(parent_id)
    if parent_code != "rc:gb:newmarket" or parent_kind != "analytical_grouping":
        raise RuntimeError(
            "Study 03 Newmarket parent changed before Source Version 1 refinement: "
            f"{(parent_code, parent_kind)!r}"
        )

    label_rows = connection.execute(
        """
        SELECT reference_course_id, candidate_course_label
        FROM reference_course
        WHERE candidate_jurisdiction='Great Britain'
          AND candidate_course_label IN (?, ?)
        ORDER BY candidate_course_label
        """,
        (NEWMARKET_ROWLEY_SOURCE_LABEL, NEWMARKET_JULY_SOURCE_LABEL),
    ).fetchall()
    label_ids = {str(label): int(reference_course_id) for reference_course_id, label in label_rows}
    if set(label_ids) != {NEWMARKET_ROWLEY_SOURCE_LABEL, NEWMARKET_JULY_SOURCE_LABEL}:
        raise RuntimeError(f"Source Version 1 Newmarket labels changed: {sorted(label_ids)!r}")

    mapped_parent_ids = {
        str(label): int(racecourse_identity_id)
        for label, racecourse_identity_id in connection.execute(
            """
            SELECT course.candidate_course_label, map.racecourse_identity_id
            FROM reference_course AS course
            JOIN reference_course_racecourse_map AS map
              ON map.reference_course_id = course.reference_course_id
            WHERE course.candidate_jurisdiction='Great Britain'
              AND course.candidate_course_label IN (?, ?)
            """,
            (NEWMARKET_ROWLEY_SOURCE_LABEL, NEWMARKET_JULY_SOURCE_LABEL),
        )
    }
    if mapped_parent_ids != {
        NEWMARKET_ROWLEY_SOURCE_LABEL: parent_id,
        NEWMARKET_JULY_SOURCE_LABEL: parent_id,
    }:
        raise RuntimeError(
            "Study 03 Newmarket source labels no longer share the expected analytical parent: "
            f"{mapped_parent_ids!r}"
        )

    course_rows = connection.execute(
        """
        SELECT course_identity_id, course_name
        FROM reference_racecourse_course_identity
        WHERE racecourse_identity_id=?
        ORDER BY course_name
        """,
        (parent_id,),
    ).fetchall()
    course_ids = {str(name): int(course_identity_id) for course_identity_id, name in course_rows}
    if set(course_ids) != {NEWMARKET_ROWLEY_COURSE, NEWMARKET_JULY_COURSE}:
        raise RuntimeError(
            "Study 03 Newmarket peer course inventory changed before refinement: "
            f"{sorted(course_ids)!r}"
        )

    unresolved_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM governance_racecourse_unresolved_question
            WHERE racecourse_identity_id=?
            """,
            (parent_id,),
        ).fetchone()[0]
    )
    if unresolved_count != 0:
        raise RuntimeError(
            "Newmarket unexpectedly has unresolved parent-level governance rows; "
            "the Source Version 1 split requires explicit handling first"
        )

    # Preserve the completed Study 03 grouping name on every source-label bridge
    # before changing Newmarket from an analytical parent into two racecourses.
    connection.execute(
        """
        UPDATE reference_course_racecourse_map
        SET study03_grouping_name = (
                SELECT racecourse.racecourse_name
                FROM reference_racecourse_identity AS racecourse
                WHERE racecourse.racecourse_identity_id =
                      reference_course_racecourse_map.racecourse_identity_id
            ),
            racecourse_resolution_method = ?,
            racecourse_resolution_evidence = ?
        """,
        (DIRECT_RESOLUTION_METHOD, DIRECT_EVIDENCE),
    )

    connection.execute(
        """
        UPDATE reference_racecourse_identity
        SET racecourse_identity_code=?, racecourse_name=?, identity_kind='venue'
        WHERE racecourse_identity_id=?
          AND racecourse_identity_code='rc:gb:newmarket'
          AND racecourse_name='Newmarket'
          AND identity_kind='analytical_grouping'
        """,
        (NEWMARKET_ROWLEY_RACECOURSE_CODE, NEWMARKET_ROWLEY_RACECOURSE, parent_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to convert Study 03 Newmarket parent to Rowley Mile racecourse")

    july_id = int(
        connection.execute(
            "SELECT COALESCE(MAX(racecourse_identity_id),0)+1 FROM reference_racecourse_identity"
        ).fetchone()[0]
    )
    connection.execute(
        """
        INSERT INTO reference_racecourse_identity (
            racecourse_identity_id, racecourse_identity_code, racecourse_name,
            jurisdiction, identity_kind, governance_release_id
        ) VALUES (?, ?, ?, 'Great Britain', 'venue', ?)
        """,
        (
            july_id,
            NEWMARKET_JULY_RACECOURSE_CODE,
            NEWMARKET_JULY_RACECOURSE,
            governance_release_id,
        ),
    )

    connection.execute(
        """
        UPDATE reference_course_racecourse_map
        SET racecourse_identity_id=?,
            study03_grouping_name=?,
            racecourse_resolution_method=?,
            racecourse_resolution_evidence=?
        WHERE reference_course_id=? AND racecourse_identity_id=?
        """,
        (
            july_id,
            NEWMARKET_STUDY03_GROUPING,
            EXPLICIT_SOURCE_LABEL_METHOD,
            NEWMARKET_CONVENTION_EVIDENCE,
            label_ids[NEWMARKET_JULY_SOURCE_LABEL],
            parent_id,
        ),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to resolve Newmarket (July) to the July Course racecourse")

    connection.execute(
        """
        UPDATE reference_course_racecourse_map
        SET study03_grouping_name=?,
            racecourse_resolution_method=?,
            racecourse_resolution_evidence=?
        WHERE reference_course_id=? AND racecourse_identity_id=?
        """,
        (
            NEWMARKET_STUDY03_GROUPING,
            SOURCE_LABEL_CONVENTION_METHOD,
            NEWMARKET_CONVENTION_EVIDENCE,
            label_ids[NEWMARKET_ROWLEY_SOURCE_LABEL],
            parent_id,
        ),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to resolve plain Newmarket to the Rowley Mile racecourse")

    connection.execute(
        """
        UPDATE reference_racecourse_course_identity
        SET course_identity_code=?
        WHERE course_identity_id=? AND racecourse_identity_id=? AND course_name=?
        """,
        (
            NEWMARKET_ROWLEY_COURSE_CODE,
            course_ids[NEWMARKET_ROWLEY_COURSE],
            parent_id,
            NEWMARKET_ROWLEY_COURSE,
        ),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to retain Rowley Mile course identity under Rowley Mile racecourse")

    connection.execute(
        """
        UPDATE reference_racecourse_course_identity
        SET racecourse_identity_id=?, course_identity_code=?
        WHERE course_identity_id=? AND racecourse_identity_id=? AND course_name=?
        """,
        (
            july_id,
            NEWMARKET_JULY_COURSE_CODE,
            course_ids[NEWMARKET_JULY_COURSE],
            parent_id,
            NEWMARKET_JULY_COURSE,
        ),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Unable to move July Course identity under July Course racecourse")

    identity_count = int(
        connection.execute("SELECT COUNT(*) FROM reference_racecourse_identity").fetchone()[0]
    )
    if identity_count != EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT:
        raise RuntimeError(
            "Source Version 1 racecourse identity count changed: "
            f"expected {EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT}, observed {identity_count}"
        )

    pending = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM reference_course_racecourse_map
            WHERE study03_grouping_name='pending_build_resolution'
               OR racecourse_resolution_method='pending_build_resolution'
               OR racecourse_resolution_evidence='pending_build_resolution'
            """
        ).fetchone()[0]
    )
    if pending != 0:
        raise RuntimeError(f"Racecourse source-label resolution left {pending} pending rows")

    observed_newmarket = connection.execute(
        """
        SELECT course.candidate_course_label,
               racecourse.racecourse_name,
               map.racecourse_resolution_method
        FROM reference_course AS course
        JOIN reference_course_racecourse_map AS map
          ON map.reference_course_id = course.reference_course_id
        JOIN reference_racecourse_identity AS racecourse
          ON racecourse.racecourse_identity_id = map.racecourse_identity_id
        WHERE course.candidate_jurisdiction='Great Britain'
          AND course.candidate_course_label IN (?, ?)
        ORDER BY course.candidate_course_label
        """,
        (NEWMARKET_ROWLEY_SOURCE_LABEL, NEWMARKET_JULY_SOURCE_LABEL),
    ).fetchall()
    expected_newmarket = [
        (
            NEWMARKET_ROWLEY_SOURCE_LABEL,
            NEWMARKET_ROWLEY_RACECOURSE,
            SOURCE_LABEL_CONVENTION_METHOD,
        ),
        (
            NEWMARKET_JULY_SOURCE_LABEL,
            NEWMARKET_JULY_RACECOURSE,
            EXPLICIT_SOURCE_LABEL_METHOD,
        ),
    ]
    # Lexicographic ordering places plain Newmarket before Newmarket (July).
    if observed_newmarket != expected_newmarket:
        raise RuntimeError(
            f"Source Version 1 Newmarket racecourse resolution changed: {observed_newmarket!r}"
        )

    return replace(
        summary,
        racecourse_identity_count=EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT,
    )


__all__ = [
    "DIRECT_RESOLUTION_METHOD",
    "EXPECTED_SOURCE_V1_RACECOURSE_IDENTITY_COUNT",
    "EXPLICIT_SOURCE_LABEL_METHOD",
    "NEWMARKET_JULY_RACECOURSE",
    "NEWMARKET_JULY_SOURCE_LABEL",
    "NEWMARKET_ROWLEY_RACECOURSE",
    "NEWMARKET_ROWLEY_SOURCE_LABEL",
    "SOURCE_LABEL_CONVENTION_METHOD",
    "apply_source_v1_racecourse_resolution",
]
