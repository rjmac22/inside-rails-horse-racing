#!/usr/bin/env python3
"""Validate Notebook 08 starting-price arithmetic against the immutable source."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

from inside_rails.source_sqlite import connect_read_only
from inside_rails.starting_price import StartingPriceKind, parse_starting_price


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    with connect_read_only(args.database) as connection:
        rows = connection.execute(
            "SELECT sp, COUNT(*) FROM data WHERE rowid <> 1 GROUP BY sp"
        ).fetchall()

    category_rows: Counter[str] = Counter()
    unresolved_values: list[tuple[object, int]] = []
    total_rows = 0

    for raw_sp, count in rows:
        parsed = parse_starting_price(raw_sp)
        category_rows[parsed.price_kind.value] += count
        total_rows += count
        if parsed.price_kind == StartingPriceKind.UNRESOLVED:
            unresolved_values.append((raw_sp, count))

    print(f"PASS data_rows: observed={total_rows} expected=1851285")
    print(f"Distinct raw values: {len(rows)}")
    for kind in StartingPriceKind:
        print(f"{kind.value}_rows: {category_rows[kind.value]}")

    partition = sum(category_rows.values()) == total_rows
    print(f"{'PASS' if partition else 'FAIL'} complete_partition")

    if unresolved_values:
        print("FAIL unresolved current values:", file=sys.stderr)
        for value, count in unresolved_values[:20]:
            print(f"  {value!r}: {count}", file=sys.stderr)
        return 1
    if total_rows != 1_851_285 or not partition:
        return 1

    print("\nStarting-price validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
