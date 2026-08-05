#!/usr/bin/env python3
"""Validate Notebook 08 starting-price arithmetic and governed external evidence."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from pathlib import Path

from inside_rails.source_sqlite import connect_read_only
from inside_rails.starting_price import StartingPriceKind, parse_starting_price


EXPECTED_DATA_ROWS = 1_851_285
EXPECTED_UNRESOLVED_VALUES = {"F": 1}
EXPECTED_EVIDENCE = {
    "verification_id": "NB08-SP-0001",
    "source_rowid": "1708860",
    "source_date": "2025-07-20",
    "source_course": "Del Mar (USA)",
    "source_off": "1:03",
    "source_horse": "Almendares (GB)",
    "source_field": "sp",
    "raw_source_value": "F",
    "verified_value": "5/2 favourite",
    "verification_status": "confirmed",
    "evidence_accessed_date": "2026-08-05",
    "confidence": "high",
    "database_action": "reference_enrichment",
}
REQUIRED_EVIDENCE_COLUMNS = (
    "verification_id",
    "source_rowid",
    "source_date",
    "source_course",
    "source_off",
    "source_horse",
    "source_field",
    "raw_source_value",
    "verified_value",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "database_action",
    "notes",
)


def load_external_evidence(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_EVIDENCE_COLUMNS:
            raise AssertionError(
                "Notebook 08 evidence columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        rows = tuple(reader)

    if len(rows) != 1:
        raise AssertionError(f"expected one Notebook 08 evidence row, found {len(rows)}")
    row = {key: (value or "").strip() for key, value in rows[0].items()}

    for field, expected in EXPECTED_EVIDENCE.items():
        if row[field] != expected:
            raise AssertionError(
                f"Notebook 08 evidence {field} changed: "
                f"observed={row[field]!r}, expected={expected!r}"
            )
    if not row["evidence_type"] or not row["evidence_locator"].startswith("https://"):
        raise AssertionError("Notebook 08 evidence requires a direct external locator")
    if not row["notes"]:
        raise AssertionError("Notebook 08 evidence notes must not be blank")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("data/reference/starting_price_external_evidence.csv"),
    )
    args = parser.parse_args()

    evidence = load_external_evidence(args.evidence)

    with connect_read_only(args.database) as connection:
        rows = connection.execute(
            "SELECT sp, COUNT(*) FROM data WHERE rowid <> 1 GROUP BY sp"
        ).fetchall()
        source_row = connection.execute(
            """
            SELECT rowid, date, course, off, horse, sp
            FROM data
            WHERE rowid = ?
            """,
            (int(evidence["source_rowid"]),),
        ).fetchone()

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

    if source_row is None:
        raise AssertionError("Notebook 08 evidence source row is missing")
    observed_source = {
        "source_rowid": str(source_row[0]),
        "source_date": str(source_row[1]),
        "source_course": str(source_row[2]),
        "source_off": str(source_row[3]),
        "source_horse": str(source_row[4]),
        "raw_source_value": str(source_row[5]),
    }
    for field, observed in observed_source.items():
        if observed != evidence[field]:
            raise AssertionError(
                f"Notebook 08 evidence source locator mismatch for {field}: "
                f"observed={observed!r}, governed={evidence[field]!r}"
            )

    parsed_anomaly = parse_starting_price(source_row[5])
    if parsed_anomaly.price_kind != StartingPriceKind.UNRESOLVED:
        raise AssertionError("external evidence must not convert raw F into parser-derived odds")

    if total_rows != EXPECTED_DATA_ROWS or not partition or not governed_anomaly_matches:
        return 1

    print("\nStarting-price validation passed with one governed source anomaly.")
    print("The lone raw value 'F' remains parser-unresolved: favourite marker present, price missing.")
    print("Notebook 08 external evidence: 1 confirmed bounded enrichment; no parser overwrite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
