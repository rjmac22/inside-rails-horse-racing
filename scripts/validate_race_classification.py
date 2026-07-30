#!/usr/bin/env python3
"""Source-wide validation for Notebook 16 governed parsing rules.

This validator reads the immutable SQLite source in read-only mode and checks
that the reusable parsers still cover the complete observed vocabularies under
the required ``rowid <> 1`` predicate. It intentionally validates syntax and
source categories only; it does not reconstruct official race eligibility or a
global race-quality hierarchy.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
import sqlite3
import sys
from typing import Any

# Allow this validator to be run directly from the repository root with
# ``python scripts/validate_race_classification.py`` without requiring an
# editable package installation or a manually supplied PYTHONPATH.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from inside_rails.race_classification import (  # noqa: E402
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier  # noqa: E402


DEFAULT_DATABASE = Path(
    "data/raw/form_2015-present/form_2015-present/raceform.db"
)
SOURCE_TABLE = "data"
DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_PROVISIONAL_RACES = 189_043
RACE_KEY_COLUMNS = ("date", "course", "off")


def _distinct_values(connection: sqlite3.Connection, column: str) -> list[Any]:
    """Return all distinct source values for one governed field."""

    quoted_column = quote_identifier(column)
    quoted_table = quote_identifier(SOURCE_TABLE)
    rows = connection.execute(
        f"""
        SELECT DISTINCT {quoted_column}
        FROM {quoted_table}
        WHERE {DATA_ROW_PREDICATE}
        ORDER BY {quoted_column}
        """
    ).fetchall()
    return [row[0] for row in rows]


def _assert_all_statuses(
    values: list[Any],
    parser: Callable[[Any], dict[str, Any]],
    status_field: str,
    allowed_statuses: set[str],
    field_name: str,
) -> None:
    """Fail with the raw values whose parser status leaves governed policy."""

    failures: list[tuple[Any, str]] = []
    for raw_value in values:
        result = parser(raw_value)
        status = result[status_field]
        if status not in allowed_statuses:
            failures.append((raw_value, status))

    if failures:
        raise AssertionError(
            f"Unexpected {field_name} parser results: {failures!r}"
        )


def _validate_population(connection: sqlite3.Connection) -> None:
    quoted_table = quote_identifier(SOURCE_TABLE)
    runner_rows = connection.execute(
        f"SELECT COUNT(*) FROM {quoted_table} WHERE {DATA_ROW_PREDICATE}"
    ).fetchone()[0]
    if runner_rows != EXPECTED_RUNNER_ROWS:
        raise AssertionError(
            f"Expected {EXPECTED_RUNNER_ROWS:,} runner rows, got {runner_rows:,}."
        )

    race_key = ", ".join(quote_identifier(column) for column in RACE_KEY_COLUMNS)
    provisional_races = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {race_key}
            FROM {quoted_table}
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY {race_key}
        )
        """
    ).fetchone()[0]
    if provisional_races != EXPECTED_PROVISIONAL_RACES:
        raise AssertionError(
            "Expected "
            f"{EXPECTED_PROVISIONAL_RACES:,} provisional races, "
            f"got {provisional_races:,}."
        )


def _validate_race_level_consistency(connection: sqlite3.Connection) -> None:
    """Confirm each governed field is constant within the provisional race key."""

    quoted_table = quote_identifier(SOURCE_TABLE)
    race_key = ", ".join(quote_identifier(column) for column in RACE_KEY_COLUMNS)
    governed_columns = (
        "race_name",
        "type",
        "class",
        "pattern",
        "rating_band",
        "age_band",
        "sex_rest",
    )

    for column in governed_columns:
        quoted_column = quote_identifier(column)
        inconsistent_races = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT {race_key}
                FROM {quoted_table}
                WHERE {DATA_ROW_PREDICATE}
                GROUP BY {race_key}
                HAVING COUNT(
                    DISTINCT COALESCE(CAST({quoted_column} AS TEXT), '<NULL>')
                ) > 1
            )
            """
        ).fetchone()[0]
        if inconsistent_races:
            raise AssertionError(
                f"{column!r} varies within {inconsistent_races:,} provisional races."
            )


def _validate_vocabularies(connection: sqlite3.Connection) -> None:
    _assert_all_statuses(
        _distinct_values(connection, "class"),
        parse_class,
        "class_parse_status",
        {"blank", "canonical"},
        "class",
    )
    _assert_all_statuses(
        _distinct_values(connection, "pattern"),
        parse_pattern,
        "pattern_parse_status",
        {"blank", "canonical"},
        "pattern",
    )
    _assert_all_statuses(
        _distinct_values(connection, "rating_band"),
        parse_rating_band,
        "rating_band_parse_status",
        {"blank", "canonical", "unrecognised_source_form"},
        "rating_band",
    )
    _assert_all_statuses(
        _distinct_values(connection, "age_band"),
        parse_age_band,
        "age_band_syntax",
        {"blank", "exact_age", "open_ended_minimum", "closed_age_range"},
        "age_band",
    )
    _assert_all_statuses(
        _distinct_values(connection, "sex_rest"),
        classify_sex_restriction,
        "sex_rest_interpretation_status",
        {"blank", "explicit_source_category", "overloaded_source_category"},
        "sex_rest",
    )

    unresolved_rating_values = {
        value
        for value in _distinct_values(connection, "rating_band")
        if parse_rating_band(value)["rating_band_parse_status"]
        == "unrecognised_source_form"
    }
    expected_unresolved = {"--", "(75-100)"}
    if unresolved_rating_values != expected_unresolved:
        raise AssertionError(
            "Unexpected unresolved rating-band vocabulary: "
            f"expected {expected_unresolved!r}, got {unresolved_rating_values!r}."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help="Path to the immutable Raceform SQLite source.",
    )
    args = parser.parse_args()

    with connect_read_only(args.database) as connection:
        _validate_population(connection)
        _validate_race_level_consistency(connection)
        _validate_vocabularies(connection)

    print(
        "Race-classification validation passed for "
        f"{EXPECTED_RUNNER_ROWS:,} runner rows and "
        f"{EXPECTED_PROVISIONAL_RACES:,} provisional races."
    )


if __name__ == "__main__":
    main()
