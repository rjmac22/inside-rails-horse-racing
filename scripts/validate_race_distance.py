"""Validate scheduled race-distance parsing against the source database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.race_distance import parse_race_distance


DATA_ROW_PREDICATE = "rowid <> 1"


def main() -> None:
    database_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "form_2015-present"
        / "form_2015-present"
        / "raceform.db"
    )

    if not database_path.exists():
        raise FileNotFoundError(f"Source database not found: {database_path}")

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
                MIN(dist) AS raw_dist,
                COUNT(DISTINCT dist) AS distinct_distance_values
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY date, course, off
            """,
            connection,
        )
    finally:
        connection.close()

    results = pd.DataFrame(
        parse_race_distance(raw_dist)
        for raw_dist in provisional_races["raw_dist"]
    )

    assert len(provisional_races) == 189_043
    assert provisional_races["distinct_distance_values"].eq(1).all()
    assert provisional_races["raw_dist"].nunique() == 63

    assert results["parse_status"].eq("parsed").all()
    assert results["source_implied_yards"].notna().all()
    assert results["source_implied_metres"].notna().all()

    assert results["source_implied_yards"].between(880, 8_030).all()

    # Source-implied conversions are not independently verified official values.
    assert results["official_distance_verified"].eq(False).all()

    # Confirm that unseen or unsupported values are not interpreted automatically.
    assert parse_race_distance("1600m")["parse_status"] == "unresolved"
    assert parse_race_distance(None)["parse_status"] == "unresolved"

    print("Race-distance validation passed.")
    print(f"Provisional races checked: {len(provisional_races):,}")
    print(f"Distinct raw values: {provisional_races['raw_dist'].nunique():,}")
    print(f"Parsed races: {results['parse_status'].eq('parsed').sum():,}")
    print(f"Unresolved races: {results['parse_status'].eq('unresolved').sum():,}")
    print(
        "Official-distance verified rows: "
        f"{results['official_distance_verified'].sum():,}"
    )


if __name__ == "__main__":
    main()
