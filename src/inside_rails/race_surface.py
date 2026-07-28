"""Governed source-supported race-surface rules from Notebook 04.

The source only supports a deterministic surface assignment where the raw
course value explicitly contains the ``(AW)`` configuration marker. All other
surface values remain unresolved pending external race-level enrichment.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from inside_rails.source_sqlite import quote_identifier

ALL_WEATHER_MARKER = "(AW)"
ALL_WEATHER_UNSPECIFIED = "all_weather_unspecified"
SURFACE_UNRESOLVED = "unresolved"
EXPLICIT_COURSE_MARKER_EVIDENCE = "explicit_course_all_weather_marker"
NO_SOURCE_SURFACE_EVIDENCE = "no_source_surface_evidence"


@dataclass(frozen=True)
class SourceSurfaceResult:
    candidate_surface: str
    evidence: str


def derive_source_supported_surface(course: object) -> SourceSurfaceResult:
    """Derive only surface information explicitly supported by raw course text."""

    if course is None:
        return SourceSurfaceResult(SURFACE_UNRESOLVED, NO_SOURCE_SURFACE_EVIDENCE)

    course_text = str(course)
    if ALL_WEATHER_MARKER in course_text:
        return SourceSurfaceResult(
            ALL_WEATHER_UNSPECIFIED,
            EXPLICIT_COURSE_MARKER_EVIDENCE,
        )

    return SourceSurfaceResult(SURFACE_UNRESOLVED, NO_SOURCE_SURFACE_EVIDENCE)


def profile_source_supported_surface(
    connection: sqlite3.Connection,
    table_name: str = "data",
    header_rowid: int = 1,
) -> dict[str, int]:
    """Reconcile Notebook 04's bounded surface rule at provisional-race grain."""

    table = quote_identifier(table_name)
    row = connection.execute(
        f"""
        WITH races AS (
            SELECT date, course, off
            FROM {table}
            WHERE rowid <> ?
            GROUP BY date, course, off
        )
        SELECT
            COUNT(*) AS provisional_races,
            SUM(CASE WHEN INSTR(course, '(AW)') > 0 THEN 1 ELSE 0 END)
                AS explicit_all_weather_races,
            SUM(CASE WHEN INSTR(course, '(AW)') = 0 THEN 1 ELSE 0 END)
                AS unresolved_surface_races,
            COUNT(DISTINCT course) AS raw_course_values
        FROM races
        """,
        (header_rowid,),
    ).fetchone()

    if row is None:
        raise RuntimeError(f"Unable to profile race surface for table: {table_name}")

    keys = (
        "provisional_races",
        "explicit_all_weather_races",
        "unresolved_surface_races",
        "raw_course_values",
    )
    return dict(zip(keys, row, strict=True))
