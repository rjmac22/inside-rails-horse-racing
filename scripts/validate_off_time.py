#!/usr/bin/env python3
"""Validate Notebook 11 off-time grammar against the immutable source."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from inside_rails.off_time import OffTimeKind, parse_off_time
from inside_rails.source_sqlite import connect_read_only


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    with connect_read_only(args.database) as connection:
        rows = connection.execute(
            "SELECT off, COUNT(*) FROM data WHERE rowid <> 1 GROUP BY off"
        ).fetchall()
        races = connection.execute(
            "SELECT date, course, off, COUNT(DISTINCT off) FROM data WHERE rowid <> 1 GROUP BY date, course, off"
        ).fetchall()

    categories: Counter[str] = Counter()
    unresolved: list[tuple[object, int]] = []
    total_rows = 0
    for raw_off, count in rows:
        parsed = parse_off_time(raw_off)
        categories[parsed.kind.value] += count
        total_rows += count
        if parsed.kind == OffTimeKind.UNRESOLVED:
            unresolved.append((raw_off, count))

    assert total_rows == 1_851_285
    assert len(rows) == 1_380
    assert len(races) == 189_043
    assert not unresolved, unresolved[:20]

    print("Off-time validation passed.")
    print(f"Source rows checked: {total_rows:,}")
    print(f"Distinct raw off values: {len(rows):,}")
    print(f"Provisional races checked: {len(races):,}")
    for kind in OffTimeKind:
        print(f"{kind.value}_rows: {categories[kind.value]:,}")
    print("Unresolved raw off values: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
