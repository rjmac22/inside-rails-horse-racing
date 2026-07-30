"""Validate source-wide beaten-distance storage and governed anomaly counts.

This validator is intentionally independent of Notebook 15. It queries the
immutable source directly and fails when the storage contract changes in ways
that the reusable parser does not govern.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


DATA_ROW_PREDICATE = "rowid <> 1"


def validate(database: Path) -> dict[str, int]:
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    query = f"""
    SELECT
        COUNT(*) AS runner_rows,
        SUM(CASE WHEN typeof(ovr_btn) = 'text' THEN 1 ELSE 0 END) AS ovr_text_rows,
        SUM(CASE WHEN typeof(btn) = 'text' THEN 1 ELSE 0 END) AS btn_text_rows,
        SUM(CASE WHEN typeof(ovr_btn) = 'text' AND ovr_btn <> '-' THEN 1 ELSE 0 END)
            AS unexpected_ovr_text_rows,
        SUM(CASE WHEN typeof(btn) = 'text' AND btn <> '-' THEN 1 ELSE 0 END)
            AS unexpected_btn_text_rows,
        SUM(
            CASE
                WHEN typeof(pos) IN ('integer', 'real')
                 AND CAST(pos AS REAL) = 1
                 AND typeof(ovr_btn) IN ('integer', 'real')
                 AND CAST(ovr_btn AS REAL) > 0
                THEN 1 ELSE 0
            END
        ) AS positive_official_winner_distance_rows,
        SUM(
            CASE
                WHEN typeof(pos) IN ('integer', 'real')
                 AND CAST(pos AS REAL) > 1
                 AND typeof(ovr_btn) IN ('integer', 'real')
                 AND CAST(ovr_btn AS REAL) = 0
                THEN 1 ELSE 0
            END
        ) AS later_position_zero_overall_rows,
        SUM(
            CASE
                WHEN typeof(pos) IN ('integer', 'real')
                 AND CAST(pos AS REAL) > 1
                 AND typeof(ovr_btn) IN ('integer', 'real')
                 AND CAST(ovr_btn AS REAL) > 0
                 AND typeof(btn) IN ('integer', 'real')
                 AND CAST(btn AS REAL) = 0
                THEN 1 ELSE 0
            END
        ) AS positive_overall_zero_increment_rows
    FROM data
    WHERE {DATA_ROW_PREDICATE}
    """

    with sqlite3.connect(uri, uri=True) as connection:
        row = connection.execute(query).fetchone()

    names = (
        "runner_rows",
        "ovr_text_rows",
        "btn_text_rows",
        "unexpected_ovr_text_rows",
        "unexpected_btn_text_rows",
        "positive_official_winner_distance_rows",
        "later_position_zero_overall_rows",
        "positive_overall_zero_increment_rows",
    )
    results = {name: int(value or 0) for name, value in zip(names, row, strict=True)}

    if results["unexpected_ovr_text_rows"]:
        raise ValueError("Unexpected populated text values found in ovr_btn.")
    if results["unexpected_btn_text_rows"]:
        raise ValueError("Unexpected populated text values found in btn.")
    if results["ovr_text_rows"] != results["btn_text_rows"]:
        raise ValueError("ovr_btn and btn text-sentinel populations no longer match.")

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    results = validate(args.database)
    for name, value in results.items():
        print(f"{name}: {value:,}")
    print("Beaten-distance source validation passed.")


if __name__ == "__main__":
    main()
