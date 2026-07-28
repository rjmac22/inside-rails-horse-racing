#!/usr/bin/env python3
"""Validate Notebook 02 field governance against the source SQLite schema."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from inside_rails.source_fields import (
    compare_sqlite_schema,
    load_source_field_governance,
)
from inside_rails.source_sqlite import connect_read_only, table_columns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate source-field governance and the raceform.db schema."
    )
    parser.add_argument("database", type=Path, help="Path to immutable raceform.db")
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("data/reference/source_field_governance.csv"),
        help="Governed source-field reference CSV.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    governance = load_source_field_governance(args.reference)

    with connect_read_only(args.database) as connection:
        sqlite_columns = table_columns(connection)

    failures = compare_sqlite_schema(governance, sqlite_columns)

    print(f"PASS governed fields: {len(governance)}")
    print(f"PASS raw preservation required: {governance['raw_preservation'].eq('required').sum()}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print("PASS SQLite schema matches governed field names, order and declared types.")
    print("\nSource-field governance validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
