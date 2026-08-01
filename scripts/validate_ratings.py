#!/usr/bin/env python3
"""Independently validate the Notebook 18 ratings governance rules."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from inside_rails.ratings import (
    INVALID_RPR_RAW_VALUE,
    INVALID_RPR_SOURCE_ROWID,
    RATING_FIELDS,
    UNAVAILABLE_RATING_TOKEN,
    parse_rating,
)

EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_COUNTS = {
    "or": {"available": 1_116_633, "unavailable": 734_652, "invalid": 0},
    "rpr": {"available": 1_644_175, "unavailable": 207_109, "invalid": 1},
    "ts": {"available": 1_227_384, "unavailable": 623_901, "invalid": 0},
}
EXPECTED_RANGES = {
    "or": (1, 181),
    "rpr": (1, 184),
    "ts": (1, 178),
}


def default_database() -> Path:
    return Path(
        "data/raw/form_2015-present/form_2015-present/raceform.db"
    )


def validate(database: Path) -> None:
    if not database.exists():
        raise FileNotFoundError(f"Source database not found: {database}")

    connection = sqlite3.connect(f"file:{database.resolve()}?mode=ro", uri=True)
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM data WHERE rowid <> 1"
        ).fetchone()[0]
        if total != EXPECTED_RUNNER_ROWS:
            raise AssertionError(
                f"Unexpected governed population: {total:,} "
                f"(expected {EXPECTED_RUNNER_ROWS:,})"
            )

        for field in RATING_FIELDS:
            quoted = f'"{field}"'
            invalid_condition = (
                f"rowid = {INVALID_RPR_SOURCE_ROWID} "
                f"AND {quoted} = {INVALID_RPR_RAW_VALUE}"
                if field == "rpr"
                else "0"
            )

            row = connection.execute(
                f"""
                SELECT
                    SUM(CASE
                        WHEN {invalid_condition} THEN 0
                        WHEN typeof({quoted}) = 'integer' THEN 1
                        ELSE 0
                    END) AS available_rows,
                    SUM(CASE
                        WHEN typeof({quoted}) = 'text'
                         AND CAST({quoted} AS TEXT) = ? THEN 1
                        ELSE 0
                    END) AS unavailable_rows,
                    SUM(CASE
                        WHEN {invalid_condition} THEN 1
                        ELSE 0
                    END) AS invalid_rows,
                    SUM(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN CAST({quoted} AS INTEGER)
                    END IS NOT NULL) AS numeric_rows,
                    MIN(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN CAST({quoted} AS INTEGER)
                    END) AS minimum_value,
                    MAX(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN CAST({quoted} AS INTEGER)
                    END) AS maximum_value,
                    SUM(CASE
                        WHEN NOT ({invalid_condition})
                         AND NOT (
                            typeof({quoted}) = 'integer'
                            OR (
                                typeof({quoted}) = 'text'
                                AND CAST({quoted} AS TEXT) = ?
                            )
                         )
                        THEN 1 ELSE 0
                    END) AS unresolved_rows
                FROM data
                WHERE rowid <> 1
                """,
                (UNAVAILABLE_RATING_TOKEN, UNAVAILABLE_RATING_TOKEN),
            ).fetchone()

            available, unavailable, invalid, numeric, minimum, maximum, unresolved = row
            expected = EXPECTED_COUNTS[field]
            observed = {
                "available": int(available),
                "unavailable": int(unavailable),
                "invalid": int(invalid),
            }

            if observed != expected:
                raise AssertionError(
                    f"Unexpected {field} status counts: {observed}; expected {expected}"
                )
            if int(numeric) != expected["available"]:
                raise AssertionError(f"{field} numeric count did not reconcile")
            if int(unresolved) != 0:
                raise AssertionError(f"{field} has {unresolved} unresolved source rows")
            if (int(minimum), int(maximum)) != EXPECTED_RANGES[field]:
                raise AssertionError(
                    f"Unexpected {field} range: {(minimum, maximum)}; "
                    f"expected {EXPECTED_RANGES[field]}"
                )
            if sum(observed.values()) != EXPECTED_RUNNER_ROWS:
                raise AssertionError(f"{field} statuses do not partition the source")

        anomaly = connection.execute(
            """
            SELECT rpr
            FROM data
            WHERE rowid = ?
            """,
            (INVALID_RPR_SOURCE_ROWID,),
        ).fetchone()
        if anomaly is None or anomaly[0] != INVALID_RPR_RAW_VALUE:
            raise AssertionError("The exact governed RPR anomaly no longer matches")

        parsed_anomaly = parse_rating(
            anomaly[0],
            "rpr",
            source_rowid=INVALID_RPR_SOURCE_ROWID,
        )
        if parsed_anomaly["rating_status"] != "invalid_source_value":
            raise AssertionError("Reusable parser did not exclude the exact anomaly")

    finally:
        connection.close()

    print(f"Ratings validation passed across {EXPECTED_RUNNER_ROWS:,} governed rows.")
    for field in RATING_FIELDS:
        expected = EXPECTED_COUNTS[field]
        minimum, maximum = EXPECTED_RANGES[field]
        print(
            f"  {field}: available={expected['available']:,}; "
            f"unavailable={expected['unavailable']:,}; "
            f"invalid={expected['invalid']:,}; range={minimum}-{maximum}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=default_database(),
        help="Path to the immutable Raceform SQLite source",
    )
    args = parser.parse_args()
    validate(args.database)


if __name__ == "__main__":
    main()
