from __future__ import annotations

import sqlite3

from inside_rails.race_surface import (
    ALL_WEATHER_UNSPECIFIED,
    EXPLICIT_COURSE_MARKER_EVIDENCE,
    NO_SOURCE_SURFACE_EVIDENCE,
    SURFACE_UNRESOLVED,
    derive_source_supported_surface,
    profile_source_supported_surface,
)


def test_explicit_all_weather_marker_is_governed_surface_evidence() -> None:
    result = derive_source_supported_surface("Kempton (AW)")
    assert result.candidate_surface == ALL_WEATHER_UNSPECIFIED
    assert result.evidence == EXPLICIT_COURSE_MARKER_EVIDENCE


def test_jurisdiction_suffix_does_not_hide_all_weather_marker() -> None:
    result = derive_source_supported_surface("Dundalk (AW) (IRE)")
    assert result.candidate_surface == ALL_WEATHER_UNSPECIFIED


def test_unmarked_course_remains_unresolved() -> None:
    result = derive_source_supported_surface("Ascot")
    assert result.candidate_surface == SURFACE_UNRESOLVED
    assert result.evidence == NO_SOURCE_SURFACE_EVIDENCE


def test_race_name_is_not_used_as_surface_evidence() -> None:
    result = derive_source_supported_surface("Meydan")
    assert result.candidate_surface == SURFACE_UNRESOLVED


def test_null_course_remains_unresolved() -> None:
    result = derive_source_supported_surface(None)
    assert result.candidate_surface == SURFACE_UNRESOLVED


def test_profile_operates_at_distinct_race_grain() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE data (date TEXT, course TEXT, off TEXT)")
    connection.executemany(
        "INSERT INTO data VALUES (?, ?, ?)",
        [
            ("date", "course", "off"),
            ("2026-01-01", "Kempton (AW)", "13:00"),
            ("2026-01-01", "Kempton (AW)", "13:00"),
            ("2026-01-01", "Ascot", "13:30"),
        ],
    )
    try:
        profile = profile_source_supported_surface(connection)
    finally:
        connection.close()

    assert profile == {
        "provisional_races": 2,
        "explicit_all_weather_races": 1,
        "unresolved_surface_races": 1,
        "raw_course_values": 2,
    }
