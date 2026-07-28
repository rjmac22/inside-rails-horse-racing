#!/usr/bin/env python3
"""Validate Notebook 14 runner-entry findings against the full source SQLite DB."""

from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path("data/raw/form_2015-present/form_2015-present/raceform.db")
RACE_KEY = ("date", "course", "off")
REQUIRED_COLUMNS = {"date", "course", "off", "horse", "ran", "num"}

EXPECTED = {
    "source_runner_rows": 1_851_285,
    "provisional_races": 189_043,
    "ran_distinct_values": 37,
    "ran_min": 1,
    "ran_max": 40,
    "races_equal_to_ran": 189_038,
    "rows_equal_to_ran": 1_851_253,
    "races_below_ran": 5,
    "rows_below_ran": 32,
    "races_above_ran": 0,
    "num_integer_rows": 1_844_253,
    "num_blank_text_rows": 7_032,
    "num_zero_rows": 1_179,
    "num_null_rows": 0,
    "duplicate_positive_num_groups": 523,
    "races_with_duplicate_positive_num": 362,
    "rows_in_duplicate_positive_num_groups": 1_084,
    "max_positive_num_multiplicity": 4,
    "duplicate_runner_identity_groups": 0,
}


def qident(name: str) -> str:
    """Quote one SQLite identifier."""

    return '"' + name.replace('"', '""') + '"'


def find_source_table(connection: sqlite3.Connection) -> str:
    """Return the one table containing all Notebook 14 source fields."""

    candidates: list[str] = []
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for (table_name,) in rows:
        columns = {
            row[1]
            for row in connection.execute(
                f"PRAGMA table_info({qident(table_name)})"
            ).fetchall()
        }
        if REQUIRED_COLUMNS.issubset(columns):
            candidates.append(table_name)

    if len(candidates) != 1:
        raise AssertionError(
            "Expected exactly one source table containing "
            f"{sorted(REQUIRED_COLUMNS)!r}; found {candidates!r}"
        )
    return candidates[0]


def scalar(connection: sqlite3.Connection, sql: str) -> int:
    """Execute a scalar integer query."""

    value = connection.execute(sql).fetchone()[0]
    return int(value or 0)


def assert_expected(name: str, actual: int) -> None:
    """Raise a useful error when a source-wide baseline changes."""

    expected = EXPECTED[name]
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected:,}, got {actual:,}")


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Source database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as connection:
        table = qident(find_source_table(connection))
        base = f"SELECT * FROM {table} WHERE rowid <> 1"

        assert_expected(
            "source_runner_rows",
            scalar(connection, f"SELECT COUNT(*) FROM ({base})"),
        )
        assert_expected(
            "provisional_races",
            scalar(
                connection,
                f"SELECT COUNT(*) FROM ("
                f"SELECT date, course, off FROM ({base}) "
                "GROUP BY date, course, off)"
            ),
        )

        ran_profile = connection.execute(
            f"SELECT COUNT(DISTINCT ran), MIN(ran), MAX(ran) FROM ({base})"
        ).fetchone()
        assert_expected("ran_distinct_values", int(ran_profile[0]))
        assert_expected("ran_min", int(ran_profile[1]))
        assert_expected("ran_max", int(ran_profile[2]))

        race_summary = f"""
            SELECT
                date,
                course,
                off,
                COUNT(*) AS runner_rows,
                COUNT(DISTINCT ran) AS ran_distinct,
                MIN(ran) AS reported_ran
            FROM ({base})
            GROUP BY date, course, off
        """

        comparisons = connection.execute(
            f"""
            SELECT
                SUM(CASE WHEN ran_distinct = 1 AND runner_rows = reported_ran THEN 1 ELSE 0 END),
                SUM(CASE WHEN ran_distinct = 1 AND runner_rows = reported_ran THEN runner_rows ELSE 0 END),
                SUM(CASE WHEN ran_distinct = 1 AND runner_rows < reported_ran THEN 1 ELSE 0 END),
                SUM(CASE WHEN ran_distinct = 1 AND runner_rows < reported_ran THEN runner_rows ELSE 0 END),
                SUM(CASE WHEN ran_distinct = 1 AND runner_rows > reported_ran THEN 1 ELSE 0 END),
                SUM(CASE WHEN ran_distinct <> 1 THEN 1 ELSE 0 END)
            FROM ({race_summary})
            """
        ).fetchone()
        names = (
            "races_equal_to_ran",
            "rows_equal_to_ran",
            "races_below_ran",
            "rows_below_ran",
            "races_above_ran",
        )
        for name, value in zip(names, comparisons[:5], strict=True):
            assert_expected(name, int(value or 0))
        if int(comparisons[5] or 0) != 0:
            raise AssertionError(
                f"Expected no within-race ran conflicts; got {int(comparisons[5]):,} races"
            )

        num_counts = connection.execute(
            f"""
            SELECT
                SUM(CASE WHEN typeof(num) = 'integer' THEN 1 ELSE 0 END),
                SUM(CASE WHEN typeof(num) = 'text' AND trim(num) = '' THEN 1 ELSE 0 END),
                SUM(CASE WHEN typeof(num) = 'integer' AND num = 0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN typeof(num) = 'null' THEN 1 ELSE 0 END),
                SUM(CASE WHEN typeof(num) = 'text' AND trim(num) <> '' THEN 1 ELSE 0 END)
            FROM ({base})
            """
        ).fetchone()
        for name, value in zip(
            (
                "num_integer_rows",
                "num_blank_text_rows",
                "num_zero_rows",
                "num_null_rows",
            ),
            num_counts[:4],
            strict=True,
        ):
            assert_expected(name, int(value or 0))
        if int(num_counts[4] or 0) != 0:
            raise AssertionError(
                f"Expected no populated text num values; got {int(num_counts[4]):,}"
            )

        duplicate_groups = f"""
            SELECT date, course, off, num, COUNT(*) AS multiplicity
            FROM ({base})
            WHERE typeof(num) = 'integer' AND num > 0
            GROUP BY date, course, off, num
            HAVING COUNT(*) > 1
        """
        duplicate_summary = connection.execute(
            f"""
            SELECT
                COUNT(*),
                COUNT(DISTINCT date || char(31) || course || char(31) || off),
                SUM(multiplicity),
                MAX(multiplicity)
            FROM ({duplicate_groups})
            """
        ).fetchone()
        for name, value in zip(
            (
                "duplicate_positive_num_groups",
                "races_with_duplicate_positive_num",
                "rows_in_duplicate_positive_num_groups",
                "max_positive_num_multiplicity",
            ),
            duplicate_summary,
            strict=True,
        ):
            assert_expected(name, int(value or 0))

        duplicate_runner_identity_groups = scalar(
            connection,
            f"""
            SELECT COUNT(*) FROM (
                SELECT date, course, off, horse
                FROM ({base})
                GROUP BY date, course, off, horse
                HAVING COUNT(*) > 1
            )
            """,
        )
        assert_expected(
            "duplicate_runner_identity_groups", duplicate_runner_identity_groups
        )

    print(
        "Source-wide runner-entry validation passed: "
        f"{EXPECTED['source_runner_rows']:,} rows, "
        f"{EXPECTED['provisional_races']:,} races, "
        f"{EXPECTED['duplicate_positive_num_groups']:,} shared-number groups."
    )


if __name__ == "__main__":
    main()
