from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest

from inside_rails.study_overlay import (
    build_race_overlay_query,
    load_pending_race_resolutions,
)


FIELDNAMES = [
    "resolution_id",
    "verification_id",
    "scope",
    "source_date",
    "source_course",
    "source_off",
    "source_field",
    "resolution_kind",
    "governed_text_value",
    "governed_integer_value",
    "governed_real_value",
    "governed_unit",
    "analytical_action",
    "notes",
]


def write_resolution_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def resolution_row(
    *,
    resolution_id: str,
    verification_id: str,
    source_date: str,
    source_course: str,
    source_off: str,
    source_field: str,
    governed_text_value: str,
    resolution_kind: str = "correction",
    analytical_action: str = "replace",
) -> dict[str, str]:
    return {
        "resolution_id": resolution_id,
        "verification_id": verification_id,
        "scope": "race",
        "source_date": source_date,
        "source_course": source_course,
        "source_off": source_off,
        "source_field": source_field,
        "resolution_kind": resolution_kind,
        "governed_text_value": governed_text_value,
        "governed_integer_value": "",
        "governed_real_value": "",
        "governed_unit": "",
        "analytical_action": analytical_action,
        "notes": "test",
    }


def test_overlay_preserves_database_values_and_exposes_verified_replacements(
    tmp_path: Path,
) -> None:
    register = tmp_path / "post_v3_external_value_resolutions.csv"
    write_resolution_csv(
        register,
        [
            resolution_row(
                resolution_id="RES-1",
                verification_id="VER-1",
                source_date="2015-02-13",
                source_course="Sandown",
                source_off="3:05",
                source_field="type",
                governed_text_value="Chase",
            ),
            resolution_row(
                resolution_id="RES-2",
                verification_id="VER-2",
                source_date="2018-06-08",
                source_course="Stratford",
                source_off="9:00",
                source_field="advertised_start_course_local",
                governed_text_value="2018-06-08T21:00:00+01:00",
            ),
            resolution_row(
                resolution_id="RES-3",
                verification_id="VER-2",
                source_date="2018-06-08",
                source_course="Stratford",
                source_off="9:00",
                source_field="actual_off_course_local",
                governed_text_value="2018-06-08T21:01:00+01:00",
                resolution_kind="enrichment",
                analytical_action="enrich",
            ),
        ],
    )

    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE races (
            raw_date TEXT NOT NULL,
            raw_course TEXT NOT NULL,
            raw_off TEXT NOT NULL,
            race_type_raw TEXT NOT NULL,
            advertised_start_course_local TEXT
        )
        """
    )
    connection.executemany(
        "INSERT INTO races VALUES (?, ?, ?, ?, ?)",
        [
            ("2015-02-13", "Sandown", "3:05", "Flat", "2015-02-13T15:05:00+00:00"),
            ("2018-06-08", "Stratford", "9:00", "Flat", None),
            ("2024-07-12", "Chepstow", "6:25", "Flat", "2024-07-12T18:25:00+01:00"),
        ],
    )

    sql, params = build_race_overlay_query("SELECT * FROM races", register)
    cursor = connection.execute(sql, params)
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
    by_course = {row["raw_course"]: row for row in result}

    sandown = by_course["Sandown"]
    assert sandown["race_type_raw"] == "Flat"
    assert sandown["race_type_study"] == "Chase"
    assert sandown["race_type_study_source"] == "post_v3_external_overlay"
    assert sandown["race_type_study_verification_id"] == "VER-1"

    stratford = by_course["Stratford"]
    assert stratford["advertised_start_course_local"] is None
    assert (
        stratford["advertised_start_course_local_study"]
        == "2018-06-08T21:00:00+01:00"
    )
    assert (
        stratford["advertised_start_course_local_study_source"]
        == "post_v3_external_overlay"
    )
    assert (
        stratford["actual_off_course_local_external"]
        == "2018-06-08T21:01:00+01:00"
    )

    chepstow = by_course["Chepstow"]
    assert chepstow["race_type_study"] == "Flat"
    assert chepstow["race_type_study_source"] == "database_v3"
    assert (
        chepstow["advertised_start_course_local_study"]
        == "2024-07-12T18:25:00+01:00"
    )


def test_duplicate_pending_resolution_for_same_race_field_fails_closed(
    tmp_path: Path,
) -> None:
    register = tmp_path / "post_v3_external_value_resolutions.csv"
    duplicate = resolution_row(
        resolution_id="RES-1",
        verification_id="VER-1",
        source_date="2015-02-13",
        source_course="Sandown",
        source_off="3:05",
        source_field="type",
        governed_text_value="Chase",
    )
    write_resolution_csv(register, [duplicate, {**duplicate, "resolution_id": "RES-2"}])

    with pytest.raises(ValueError, match="Duplicate pending resolution"):
        load_pending_race_resolutions(register)


def test_unsupported_pending_field_fails_closed(tmp_path: Path) -> None:
    register = tmp_path / "post_v3_external_value_resolutions.csv"
    write_resolution_csv(
        register,
        [
            resolution_row(
                resolution_id="RES-1",
                verification_id="VER-1",
                source_date="2015-02-13",
                source_course="Sandown",
                source_off="3:05",
                source_field="unreviewed_field",
                governed_text_value="something",
            )
        ],
    )

    with pytest.raises(ValueError, match="Unsupported post-release race field"):
        load_pending_race_resolutions(register)


def test_wrong_resolution_action_for_supported_field_fails_closed(tmp_path: Path) -> None:
    register = tmp_path / "post_v3_external_value_resolutions.csv"
    write_resolution_csv(
        register,
        [
            resolution_row(
                resolution_id="RES-1",
                verification_id="VER-1",
                source_date="2015-02-13",
                source_course="Sandown",
                source_off="3:05",
                source_field="type",
                governed_text_value="Chase",
                resolution_kind="enrichment",
                analytical_action="enrich",
            )
        ],
    )

    with pytest.raises(ValueError, match="Unsupported resolution treatment"):
        load_pending_race_resolutions(register)


def test_default_pending_register_contains_all_verified_race_type_corrections() -> None:
    """Guard the governed post-v3 register used by reader-facing studies."""

    rows = load_pending_race_resolutions()
    type_rows = [row for row in rows if row["source_field"] == "type"]
    advertised_rows = [
        row
        for row in rows
        if row["source_field"] == "advertised_start_course_local"
    ]
    actual_rows = [
        row for row in rows if row["source_field"] == "actual_off_course_local"
    ]

    # The GB race-type reliability investigation established 25 exact
    # corrections. Three Stratford advertised-time resolutions and three
    # separate actual-off enrichments remain alongside them.
    assert len(rows) == 31
    assert len(type_rows) == 25
    assert len(advertised_rows) == 3
    assert len(actual_rows) == 3
    assert len({row["verification_id"] for row in type_rows}) == 25
