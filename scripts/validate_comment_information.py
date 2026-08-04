#!/usr/bin/env python3
"""Validate Notebook 21 comment governance across the immutable source."""

from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.comment_information import (  # noqa: E402
    PROBABLE_PLACEHOLDERS,
    UNRESOLVED_SOURCE_CODES,
)

EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_NULL_ROWS = 0
EXPECTED_EMPTY_ROWS = 340_394
EXPECTED_PLACEHOLDER_OR_CODE_ROWS = 238
EXPECTED_SUBSTANTIVE_ROWS = 1_510_653
EXPECTED_PROVISIONAL_RACES = 189_043


def _placeholders_sql(values: frozenset[str]) -> str:
    return ", ".join("?" for _ in values)


def validate(source_database: Path) -> None:
    if not source_database.exists():
        raise FileNotFoundError(source_database)

    connection = sqlite3.connect(
        f"file:{source_database.resolve()}?mode=ro&immutable=1",
        uri=True,
    )
    try:
        classified_values = tuple(sorted(PROBABLE_PLACEHOLDERS | UNRESOLVED_SOURCE_CODES))
        placeholders = _placeholders_sql(frozenset(classified_values))
        row = connection.execute(
            f"""
            SELECT
                COUNT(*) AS runner_rows,
                SUM(comment IS NULL) AS null_rows,
                SUM(comment = '') AS empty_rows,
                SUM(comment IN ({placeholders})) AS placeholder_or_code_rows,
                SUM(
                    comment IS NOT NULL
                    AND comment <> ''
                    AND comment NOT IN ({placeholders})
                ) AS substantive_rows
            FROM data
            WHERE rowid <> 1
            """,
            classified_values + classified_values,
        ).fetchone()

        race_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT date, course, off
                FROM data
                WHERE rowid <> 1
                GROUP BY date, course, off
            )
            """
        ).fetchone()[0]
    finally:
        connection.close()

    observed = {
        "runner_rows": row[0],
        "null_rows": row[1],
        "empty_rows": row[2],
        "placeholder_or_code_rows": row[3],
        "substantive_rows": row[4],
        "provisional_races": race_count,
    }
    expected = {
        "runner_rows": EXPECTED_RUNNER_ROWS,
        "null_rows": EXPECTED_NULL_ROWS,
        "empty_rows": EXPECTED_EMPTY_ROWS,
        "placeholder_or_code_rows": EXPECTED_PLACEHOLDER_OR_CODE_ROWS,
        "substantive_rows": EXPECTED_SUBSTANTIVE_ROWS,
        "provisional_races": EXPECTED_PROVISIONAL_RACES,
    }

    if observed != expected:
        raise AssertionError(f"comment validation mismatch: observed={observed}, expected={expected}")
    if sum(
        observed[key]
        for key in ("null_rows", "empty_rows", "placeholder_or_code_rows", "substantive_rows")
    ) != observed["runner_rows"]:
        raise AssertionError("comment states do not partition the governed runner population")

    for key, value in observed.items():
        print(f"{key}: {value:,}")
    print("comment information validation: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_database",
        nargs="?",
        type=Path,
        default=(
            PROJECT_ROOT
            / "data"
            / "raw"
            / "form_2015-present"
            / "form_2015-present"
            / "raceform.db"
        ),
    )
    args = parser.parse_args()
    validate(args.source_database)


if __name__ == "__main__":
    main()
