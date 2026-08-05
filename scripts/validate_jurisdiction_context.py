#!/usr/bin/env python3
"""Validate Notebook 09 bounded context, provenance and source coverage."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
from pathlib import Path

from inside_rails.course_jurisdiction import derive_candidate_race_jurisdiction
from inside_rails.jurisdiction_context import (
    CONTEXTS,
    OBSERVED_SOURCE_TYPES,
    resolve_jurisdiction_context,
    validate_context_reference,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_VERIFICATION_IDS = {
    "NB09-CONTEXT-0001",
    "NB09-CONTEXT-0002",
    "NB09-CONTEXT-0003",
    "NB09-CONTEXT-0004",
}
REQUIRED_GOVERNANCE_COLUMNS = (
    "verification_id",
    "jurisdiction",
    "effective_from",
    "effective_to",
    "source_types",
    "regulatory_authority",
    "administrative_body",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "database_action",
    "notes",
)


def _parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def load_context_governance(path: Path) -> tuple[dict[str, object], ...]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_GOVERNANCE_COLUMNS:
            raise AssertionError(
                "Notebook 09 governance columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        raw_rows = tuple(reader)

    ids = {row["verification_id"] for row in raw_rows}
    if ids != EXPECTED_VERIFICATION_IDS or len(raw_rows) != 4:
        raise AssertionError(
            f"unexpected Notebook 09 verification closure: ids={sorted(ids)!r}"
        )

    output: list[dict[str, object]] = []
    for raw in raw_rows:
        row = {key: (value or "").strip() for key, value in raw.items()}
        verification_id = row["verification_id"]
        source_types = tuple(row["source_types"].split("|"))
        if source_types != OBSERVED_SOURCE_TYPES:
            raise AssertionError(
                f"{verification_id}: source type coverage changed: {source_types!r}"
            )
        if row["verification_status"] != "confirmed":
            raise AssertionError(f"{verification_id}: context record must be confirmed")
        if row["confidence"] != "high":
            raise AssertionError(f"{verification_id}: expected high confidence")
        if row["database_action"] != "reference_enrichment":
            raise AssertionError(
                f"{verification_id}: context record must authorise reference enrichment"
            )
        if not row["evidence_type"] or not row["evidence_locator"]:
            raise AssertionError(f"{verification_id}: evidence provenance is required")
        locators = [value.strip() for value in row["evidence_locator"].split("|")]
        if not locators or any(not value.startswith("https://") for value in locators):
            raise AssertionError(f"{verification_id}: direct HTTPS locators are required")
        date.fromisoformat(row["evidence_accessed_date"])
        if not row["regulatory_authority"] or not row["notes"]:
            raise AssertionError(f"{verification_id}: authority and notes are required")
        output.append(
            {
                **row,
                "source_types_parsed": source_types,
                "effective_from_parsed": _parse_date(row["effective_from"]),
                "effective_to_parsed": _parse_date(row["effective_to"]),
            }
        )
    return tuple(output)


def _matching_governance(
    context: object,
    governance_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    matches = []
    for row in governance_rows:
        if row["jurisdiction"] != context.jurisdiction:
            continue
        if context.source_type not in row["source_types_parsed"]:
            continue
        if context.effective_from != row["effective_from_parsed"]:
            continue
        if context.effective_to != row["effective_to_parsed"]:
            continue
        matches.append(row)
    if len(matches) != 1:
        raise AssertionError(
            "expected one governed evidence row for context "
            f"{context.jurisdiction!r}/{context.source_type!r}/"
            f"{context.effective_from!s}-{context.effective_to!s}; found {len(matches)}"
        )
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument(
        "--governance",
        type=Path,
        default=Path("data/reference/jurisdiction_context_governance.csv"),
    )
    args = parser.parse_args()

    validate_context_reference()
    governance_rows = load_context_governance(args.governance)

    for context in CONTEXTS:
        evidence = _matching_governance(context, governance_rows)
        if context.regulatory_authority != evidence["regulatory_authority"]:
            raise AssertionError(
                f"{evidence['verification_id']}: regulatory authority mismatch"
            )
        governed_admin = evidence["administrative_body"] or None
        if context.administrative_body != governed_admin:
            raise AssertionError(
                f"{evidence['verification_id']}: administrative body mismatch"
            )
        if context.wagering_context_status != "unresolved":
            raise AssertionError("Notebook 09 does not authorise wagering-context assignment")

    with connect_read_only(args.database) as connection:
        races = connection.execute(
            """
            SELECT date, course, off, race_name, type
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

    for raw_date, raw_course, _off, race_name, source_type in races:
        jurisdiction_result = derive_candidate_race_jurisdiction(
            {
                "date": raw_date,
                "course": raw_course,
                "type": source_type,
                "race_name": race_name,
            }
        )
        jurisdiction = jurisdiction_result.iloc[0]
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
            assert context.native_code_status == "unresolved_aqps_source_classification"

    assert set(OBSERVED_SOURCE_TYPES) == {"Flat", "Hurdle", "Chase", "NH Flat"}
    assert not missing_context, dict(missing_context)
    assert france_nh_flat == 23

    print("Jurisdiction-context validation passed.")
    print(f"Provisional races checked: {len(races):,}")
    print(f"Governed context rows: {len(CONTEXTS):,}")
    print(f"Governed provenance records: {len(governance_rows):,}")
    print(f"Great Britain races covered: {worked_rows['Great Britain']:,}")
    print(f"Ireland races covered: {worked_rows['Ireland']:,}")
    print(f"France races covered: {worked_rows['France']:,}")
    print(f"France source-labelled NH Flat races: {france_nh_flat:,}")
    print("Missing worked-example context assignments: 0")
    print("Wagering-context assignments asserted: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
