#!/usr/bin/env python3
"""Validate the governed course-location join against the full source extract."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from inside_rails.course_locations import (
    IDENTITY_COLUMNS,
    derive_source_course_identities,
    load_course_locations,
    merge_source_course_locations,
    unmatched_source_course_locations,
)

EXPECTED_DISTINCT_RAW_COURSE_LABELS = 528
EXPECTED_CONTEXTUAL_RAW_LABELS = {"Ascot", "Newcastle"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate every source race context against the governed reference."
    )
    parser.add_argument(
        "database_path",
        nargs="?",
        type=Path,
        default=Path(
            "data/raw/form_2015-present/form_2015-present/raceform.db"
        ),
    )
    parser.add_argument(
        "reference_path",
        nargs="?",
        type=Path,
        default=Path("data/reference/course_locations.csv"),
    )
    return parser.parse_args()


def load_source_race_contexts(database_path: Path) -> pd.DataFrame:
    """Load one context row per provisional race without altering source values."""

    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(
            """
            SELECT
                course,
                date,
                MIN(type) AS type,
                MIN(race_name) AS race_name,
                off,
                COUNT(*) AS runner_rows
            FROM data
            WHERE rowid <> 1
            GROUP BY course, date, off
            ORDER BY course, date, off
            """,
            connection,
        )


def main() -> None:
    args = parse_args()
    source = load_source_race_contexts(args.database_path)
    reference = load_course_locations(args.reference_path)

    derived = derive_source_course_identities(source)

    # A raw label is not universally an identity. Ascot and Newcastle are known
    # cross-jurisdiction collisions resolved deterministically from race context.
    raw_identity_counts = (
        derived[["course", *IDENTITY_COLUMNS]]
        .drop_duplicates()
        .groupby("course", dropna=False)
        .size()
    )
    contextual_raw_labels = set(
        raw_identity_counts.loc[raw_identity_counts.gt(1)].index.astype(str)
    )

    if contextual_raw_labels != EXPECTED_CONTEXTUAL_RAW_LABELS:
        details = (
            derived.loc[
                derived["course"].astype(str).isin(contextual_raw_labels),
                ["course", *IDENTITY_COLUMNS],
            ]
            .drop_duplicates()
            .sort_values(["course", *IDENTITY_COLUMNS])
            .to_dict("records")
        )
        raise AssertionError(
            "Unexpected contextual raw course-label set: "
            f"expected {sorted(EXPECTED_CONTEXTUAL_RAW_LABELS)}, "
            f"found {sorted(contextual_raw_labels)}. Mappings: {details}"
        )

    merged = merge_source_course_locations(source, reference)
    unmatched = unmatched_source_course_locations(merged)

    if not unmatched.empty:
        raise AssertionError(
            "Unmatched source course-location residue found: "
            f"{unmatched.to_dict('records')}"
        )

    distinct_raw_labels = int(source["course"].nunique(dropna=False))
    if distinct_raw_labels != EXPECTED_DISTINCT_RAW_COURSE_LABELS:
        raise AssertionError(
            "Unexpected distinct raw course-label count: "
            f"expected {EXPECTED_DISTINCT_RAW_COURSE_LABELS}, "
            f"found {distinct_raw_labels}. Review the unmatched residue and "
            "source update before changing the baseline."
        )

    matched_identities = int(
        merged[IDENTITY_COLUMNS].drop_duplicates().shape[0]
    )

    print("Source-wide course-location join validation passed")
    print(f"Database: {args.database_path}")
    print(f"Reference: {args.reference_path}")
    print(f"Provisional race contexts: {len(source):,}")
    print(f"Distinct raw course labels: {distinct_raw_labels:,}")
    print(f"Matched governed identities: {matched_identities:,}")
    print("Unmatched source race contexts: 0")
    print(
        "Contextual raw labels: "
        + ", ".join(sorted(contextual_raw_labels))
    )


if __name__ == "__main__":
    main()
