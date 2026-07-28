#!/usr/bin/env python3
"""Validate Notebook 08 starting-price arithmetic against the immutable source."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from inside_rails.source_sqlite import connect_read_only
from inside_rails.starting_price import StartingPriceKind, parse_starting_price


EXPECTED_DATA_ROWS = 1_851_285
EXPECTED_UNRESOLVED_VALUES = {"F": 1}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    with connect_read_only(args.database) as connection:
        rows = connection.execute(
            "SELECT sp, COUNT(*) FROM data WHERE rowid <> 1 GROUP BY sp"
        ).fetchall()

    category_rows: Counter[str] = Counter()
    unresolved_values: Counter[str] = Counter()
    total_rows = 0

    for raw_sp, count in rows:
        parsed = parse_starting_price(raw_sp)
        category_rows[parsed.price_kind.value] += count
        total_rows += count
        if parsed.price_kind == StartingPriceKind.UNRESOLVED:
            unresolved_values[str(raw_sp)] += count

    print(f"PASS data_rows: observed={total_rows} expected={EXPECTED_DATA_ROWS}")
    print(f"Distinct raw values: {len(rows)}")
    for kind in StartingPriceKind:
        print(f"{kind.value}_rows: {category_rows[kind.value]}")

    partition = sum(category_rows.values()) == total_rows
    print(f"{'PASS' if partition else 'FAIL'} complete_partition")

    governed_anomaly_matches = dict(unresolved_values) == EXPECTED_UNRESOLVED_VALUES
    print(
        f"{'PASS' if governed_anomaly_matches else 'FAIL'} "
        f"governed_unresolved_values: observed={dict(unresolved_values)!r} "
        f"expected={EXPECTED_UNRESOLVED_VALUES!r}"
    )

    if total_rows != EXPECTED_DATA_ROWS or not partition or not governed_anomaly_matches:
        return 1

    print("\nStarting-price validation passed with one governed source anomaly.")
    print("The lone raw value 'F' is preserved as unresolved: favourite marker present, price missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
