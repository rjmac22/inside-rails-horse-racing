#!/usr/bin/env python3
"""Validate Notebook 09 bounded context against the immutable source."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

from inside_rails.course_jurisdiction import derive_course_jurisdiction
from inside_rails.jurisdiction_context import (
    CONTEXTS,
    OBSERVED_SOURCE_TYPES,
    resolve_jurisdiction_context,
    validate_context_reference,
)
from inside_rails.source_sqlite import connect_read_only


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()

    validate_context_reference()

    with connect_read_only(args.database) as connection:
        races = connection.execute(
            """
            SELECT date, course, off, type
            FROM data
            WHERE rowid <> 1
            GROUP BY date, course, off
            """
        ).fetchall()

    assert len(races) == 189_043
    assert len(CONTEXTS) == 16

    worked_rows: Counter[str] = Counter()
    missing_context: Counter[tuple[str, str]] = Counter()
    france_nh_flat = 0

    for raw_date, raw_course, _off, source_type in races:
        course = derive_course_jurisdiction(raw_course)
        jurisdiction = course["candidate_jurisdiction"]
        if jurisdiction not in {"Great Britain", "Ireland", "France"}:
            continue
        worked_rows[jurisdiction] += 1
        race_date = date.fromisoformat(raw_date)
        context = resolve_jurisdiction_context(jurisdiction, source_type, race_date)
        if context is None:
            missing_context[(jurisdiction, source_type)] += 1
        if jurisdiction == "France" and source_type == "NH Flat":
            france_nh_flat += 1
            assert context is not None
            assert (
                context.native_code_status
                == "unresolved_aqps_source_classification"
            )

    assert set(OBSERVED_SOURCE_TYPES) == {"Flat", "Hurdle", "Chase", "NH Flat"}
    assert not missing_context, dict(missing_context)
    assert france_nh_flat == 23
    assert all(row.wagering_context_status == "unresolved" for row in CONTEXTS)

    print("Jurisdiction-context validation passed.")
    print(f"Provisional races checked: {len(races):,}")
    print(f"Governed context rows: {len(CONTEXTS):,}")
    print(f"Great Britain races covered: {worked_rows['Great Britain']:,}")
    print(f"Ireland races covered: {worked_rows['Ireland']:,}")
    print(f"France races covered: {worked_rows['France']:,}")
    print(f"France source-labelled NH Flat races: {france_nh_flat:,}")
    print("Missing worked-example context assignments: 0")
    print("Wagering-context assignments asserted: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
