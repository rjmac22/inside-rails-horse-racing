"""Validate the reusable course and jurisdiction mapping.

Usage:
    PYTHONPATH=src python scripts/validate_course_jurisdiction.py \
        data/raw/form_2015-present/form_2015-present/raceform.db
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from inside_rails.course_jurisdiction import (
    derive_candidate_course_label,
    derive_candidate_race_jurisdiction,
)


DATA_ROW_PREDICATE = "rowid <> 1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    database_path = args.database.resolve()

    if not database_path.exists():
        raise FileNotFoundError(database_path)

    connection = sqlite3.connect(
        f"file:{database_path}?mode=ro",
        uri=True,
    )

    try:
        provisional_races = pd.read_sql_query(
            f"""
            SELECT
                date,
                course,
                off,
                MIN(race_name) AS race_name,
                MIN(type) AS type
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY
                date,
                course,
                off
            """,
            connection,
        )
    finally:
        connection.close()

    duplicate_keys = provisional_races.duplicated(
        subset=["date", "course", "off"],
        keep=False,
    ).sum()

    mapped = provisional_races.copy()

    mapped[
        ["candidate_jurisdiction", "jurisdiction_evidence_source"]
    ] = mapped.apply(
        derive_candidate_race_jurisdiction,
        axis=1,
    )

    mapped["candidate_course_label"] = mapped["course"].map(
        derive_candidate_course_label
    )

    assigned_races = (
        mapped["candidate_jurisdiction"] != "unresolved"
    ).sum()

    candidate_venue_count = (
        mapped[
            ["candidate_jurisdiction", "candidate_course_label"]
        ]
        .drop_duplicates()
        .shape[0]
    )

    identity_forms = (
        mapped
        .groupby(
            ["candidate_jurisdiction", "candidate_course_label"],
            as_index=False,
        )
        .agg(distinct_raw_course_forms=("course", "nunique"))
    )

    multi_form_identity_count = (
        identity_forms["distinct_raw_course_forms"] > 1
    ).sum()

    date_identity_forms = (
        mapped
        .groupby(
            [
                "date",
                "candidate_jurisdiction",
                "candidate_course_label",
            ],
            as_index=False,
        )
        .agg(distinct_raw_course_forms=("course", "nunique"))
    )

    same_date_collision_count = (
        date_identity_forms["distinct_raw_course_forms"] > 1
    ).sum()

    assert len(provisional_races) == 189_043
    assert duplicate_keys == 0
    assert assigned_races == 189_043
    assert candidate_venue_count == 395
    assert multi_form_identity_count == 135
    assert same_date_collision_count == 0

    print("Course-jurisdiction validation passed.")
    print(f"Provisional races: {len(provisional_races):,}")
    print(f"Candidate jurisdictions assigned: {assigned_races:,}")
    print(f"Candidate venue/configuration identities: {candidate_venue_count:,}")
    print(f"Multi-form candidate identities: {multi_form_identity_count:,}")
    print(f"Same-date candidate identity collisions: {same_date_collision_count:,}")


if __name__ == "__main__":
    main()
