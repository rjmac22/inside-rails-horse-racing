#!/usr/bin/env python3
"""Validate the governed 37-field inventory against the immutable source."""

from __future__ import annotations

import argparse
from pathlib import Path

from inside_rails.field_governance import (
    FIELD_GOVERNANCE,
    FIELD_GOVERNANCE_BY_NAME,
    SOURCE_FIELDS,
    validate_field_governance,
)
from inside_rails.source_sqlite import connect_read_only


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    validate_field_governance()

    with connect_read_only(args.database) as connection:
        columns = connection.execute("PRAGMA table_info(data)").fetchall()
        data_rows = connection.execute(
            "SELECT COUNT(*) FROM data WHERE rowid <> 1"
        ).fetchone()[0]

    observed_fields = tuple(row[1] for row in columns)
    assert data_rows == 1_851_285, data_rows
    assert observed_fields == SOURCE_FIELDS, (
        f"source schema changed: observed={observed_fields!r} expected={SOURCE_FIELDS!r}"
    )
    assert set(FIELD_GOVERNANCE_BY_NAME) == set(observed_fields)

    statuses: dict[str, int] = {}
    groups: dict[str, int] = {}
    for row in FIELD_GOVERNANCE:
        statuses[row.status] = statuses.get(row.status, 0) + 1
        groups[row.investigation_group] = groups.get(row.investigation_group, 0) + 1

    print("Field-governance validation passed.")
    print(f"Source rows checked: {data_rows:,}")
    print(f"Source fields governed: {len(observed_fields)}")
    print(f"Distinct investigation groups: {len(groups)}")
    print("Status totals:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
