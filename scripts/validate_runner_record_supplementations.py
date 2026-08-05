#!/usr/bin/env python3
"""Validate Notebook 14/15 missing-runner decisions and supplementations."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re

from inside_rails.manual_verifications import load_manual_verifications
from inside_rails.runner_record_supplementations import (
    load_runner_record_supplementations,
)
from inside_rails.source_sqlite import connect_read_only


EXPECTED_NOTEBOOK_14_IDS = {
    f"NB14-RAN-{number:04d}" for number in range(1, 6)
}
EXPECTED_NOTEBOOK_15_IDS = {
    f"NB15-BTN-{number:04d}" for number in range(1, 18)
}
EXPECTED_STATUS_COUNTS = {
    "14": Counter({"confirmed": 3, "contradicted": 2}),
    "15": Counter({"confirmed": 13, "contradicted": 4}),
}
EXPECTED_ACTION_COUNTS = {
    "14": Counter(
        {"source_supplementation": 2, "source_correction_candidate": 3}
    ),
    "15": Counter(
        {
            "source_supplementation": 1,
            "evidence_only": 12,
            "source_correction_candidate": 4,
        }
    ),
}
EXPECTED_VERIFIED_FACTS = {
    "NB14-RAN-0001": ("published_runners=8", "missing_horse=Saucats", "outcome=F"),
    "NB14-RAN-0005": (
        "published_runners=16",
        "missing_horse=Tosen Thunder",
        "outcome=did_not_finish",
    ),
    "NB15-BTN-0001": (
        "published_runners=9",
        "missing_horse=Great Navigator (USA)",
        "verified_pos=5",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=Path(
            "data/raw/form_2015-present/form_2015-present/raceform.db"
        ),
    )
    parser.add_argument(
        "--manual-verifications",
        type=Path,
        default=Path("data/reference/manual_verifications.csv"),
    )
    parser.add_argument(
        "--supplementations",
        type=Path,
        default=Path("data/reference/runner_record_supplementations.csv"),
    )
    return parser.parse_args()


def _locator_set(value: str) -> frozenset[str]:
    return frozenset(
        token.strip()
        for token in re.split(r"\s*[;|]\s*", value)
        if token.strip()
    )


def _validate_notebook_partition(
    rows: tuple[object, ...],
    notebook: str,
    expected_ids: set[str],
) -> dict[str, object]:
    ids = {row.verification_id for row in rows}
    if ids != expected_ids or len(rows) != len(expected_ids):
        raise AssertionError(
            f"Notebook {notebook} verification closure changed; "
            f"missing={sorted(expected_ids - ids)}, extra={sorted(ids - expected_ids)}"
        )

    statuses = Counter(row.verification_status for row in rows)
    actions = Counter(row.database_action for row in rows)
    if statuses != EXPECTED_STATUS_COUNTS[notebook]:
        raise AssertionError(
            f"Notebook {notebook} status partition changed: {dict(statuses)}"
        )
    if actions != EXPECTED_ACTION_COUNTS[notebook]:
        raise AssertionError(
            f"Notebook {notebook} action partition changed: {dict(actions)}"
        )

    indexed = {}
    for row in rows:
        if row.governing_notebook != notebook:
            raise AssertionError(
                f"{row.verification_id}: governing_notebook must be {notebook}"
            )
        if not row.evidence_type or not row.evidence_locator:
            raise AssertionError(f"{row.verification_id}: evidence provenance is required")
        if not row.evidence_accessed_date or not row.confidence or not row.notes:
            raise AssertionError(
                f"{row.verification_id}: access date, confidence and notes are required"
            )
        if row.database_action == "source_supplementation":
            if row.verification_status != "confirmed":
                raise AssertionError(
                    f"{row.verification_id}: supplementation must be confirmed"
                )
            if not row.source_horse or not row.verified_value:
                raise AssertionError(
                    f"{row.verification_id}: supplementation requires horse and facts"
                )
        else:
            if row.database_action not in {
                "evidence_only",
                "source_correction_candidate",
            }:
                raise AssertionError(
                    f"{row.verification_id}: unsupported governed action"
                )
        indexed[row.verification_id] = row
    return indexed


def main() -> None:
    args = parse_args()
    if not args.database.exists():
        raise FileNotFoundError(args.database)

    manual_rows = load_manual_verifications(args.manual_verifications)
    notebook_14_rows = tuple(
        row for row in manual_rows if row.verification_id.startswith("NB14-RAN-")
    )
    notebook_15_rows = tuple(
        row for row in manual_rows if row.verification_id.startswith("NB15-BTN-")
    )
    manual_by_id = {
        **_validate_notebook_partition(
            notebook_14_rows, "14", EXPECTED_NOTEBOOK_14_IDS
        ),
        **_validate_notebook_partition(
            notebook_15_rows, "15", EXPECTED_NOTEBOOK_15_IDS
        ),
    }

    supplementations = load_runner_record_supplementations(args.supplementations)
    supplementation_ids = {row.verification_id for row in supplementations}
    expected_supplementation_ids = set(EXPECTED_VERIFIED_FACTS)
    if supplementation_ids != expected_supplementation_ids:
        raise AssertionError(
            "usable supplementation population changed; "
            f"observed={sorted(supplementation_ids)!r}"
        )

    with connect_read_only(args.database) as connection:
        for supplementation in supplementations:
            manual = manual_by_id[supplementation.verification_id]
            for field, governed, permanent in (
                ("source_date", supplementation.source_date, manual.source_date),
                ("source_course", supplementation.source_course, manual.source_course),
                ("source_off", supplementation.source_off, manual.source_off),
                ("source_horse", supplementation.source_horse, manual.source_horse),
                (
                    "evidence_accessed_date",
                    supplementation.evidence_accessed_date,
                    manual.evidence_accessed_date,
                ),
                ("confidence", supplementation.confidence, manual.confidence),
                ("database_action", supplementation.database_action, manual.database_action),
            ):
                if governed != permanent:
                    raise AssertionError(
                        f"{supplementation.verification_id}: {field} differs from "
                        "the permanent verification record"
                    )
            if supplementation.evidence_type != manual.evidence_type:
                raise AssertionError(
                    f"{supplementation.verification_id}: evidence type mismatch"
                )
            if _locator_set(supplementation.evidence_locator) != _locator_set(
                manual.evidence_locator
            ):
                raise AssertionError(
                    f"{supplementation.verification_id}: evidence locator mismatch"
                )
            for fact in EXPECTED_VERIFIED_FACTS[supplementation.verification_id]:
                if fact not in manual.verified_value:
                    raise AssertionError(
                        f"{supplementation.verification_id}: missing verified fact {fact!r}"
                    )

            source_rows = connection.execute(
                """
                SELECT horse, ran
                FROM data
                WHERE rowid <> 1
                  AND date = ?
                  AND course = ?
                  AND off = ?
                """,
                supplementation.race_key,
            ).fetchall()
            if len(source_rows) != supplementation.source_runner_rows:
                raise AssertionError(
                    f"{supplementation.verification_id}: source runner-row count changed; "
                    f"observed={len(source_rows)}, "
                    f"expected={supplementation.source_runner_rows}"
                )
            ran_values = {int(row[1]) for row in source_rows}
            if ran_values != {supplementation.source_ran}:
                raise AssertionError(
                    f"{supplementation.verification_id}: source ran values changed: "
                    f"{sorted(ran_values)!r}"
                )
            source_horses = {str(row[0]) for row in source_rows}
            if supplementation.source_horse in source_horses:
                raise AssertionError(
                    f"{supplementation.verification_id}: supplemented runner is now "
                    "present in the immutable source race"
                )

    print("Runner-record supplementation validation passed.")
    print("  Notebook 14 decisions: 5 (2 supplementations, 3 correction candidates)")
    print(
        "  Notebook 15 decisions: 17 "
        "(1 supplementation, 12 evidence-only, 4 correction candidates)"
    )
    print(f"  usable missing-runner supplementations: {len(supplementations)}")
    print("  exact manual-to-specialist agreement: PASS")
    print("  supplemented runners absent from source races: PASS")
    print("  unsupported runner fields assigned: 0")


if __name__ == "__main__":
    main()
