#!/usr/bin/env python3
"""Independently validate Notebook 18 ratings data and semantic evidence."""

from __future__ import annotations

import argparse
from collections import Counter
import sqlite3
from pathlib import Path

from inside_rails.manual_verifications import load_manual_verifications
from inside_rails.ratings import (
    INVALID_RPR_RAW_VALUE,
    INVALID_RPR_SOURCE_ROWID,
    RATING_FIELDS,
    UNAVAILABLE_RATING_TOKEN,
    parse_rating,
)

EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_COUNTS = {
    "or": {"available": 1_116_633, "unavailable": 734_652, "invalid": 0},
    "rpr": {"available": 1_644_175, "unavailable": 207_109, "invalid": 1},
    "ts": {"available": 1_227_384, "unavailable": 623_901, "invalid": 0},
}
EXPECTED_RANGES = {
    "or": (1, 181),
    "rpr": (1, 184),
    "ts": (1, 178),
}
EXPECTED_VERIFICATION_IDS = {
    "NB18-OR-0001",
    "NB18-RPR-0001",
    "NB18-TS-0001",
}
EXPECTED_SEMANTIC_FACTS = {
    "NB18-OR-0001": {
        "source_field": "or",
        "raw_source_value": "or",
        "verified_value": "official handicap mark applicable to the horse for the race; a current pre-race handicap state used to allocate handicap weights",
    },
    "NB18-RPR-0001": {
        "source_field": "rpr",
        "raw_source_value": "rpr",
        "verified_value": "retrospective Racing Post performance rating for the completed race; normally compiled after the race and potentially revised as later form changes the assessment",
    },
    "NB18-TS-0001": {
        "source_field": "ts",
        "raw_source_value": "ts",
        "verified_value": "retrospective speed figure estimating how fast the horse ran in the completed race on that particular day",
    },
}


def default_database() -> Path:
    return Path(
        "data/raw/form_2015-present/form_2015-present/raceform.db"
    )


def default_manual_verifications() -> Path:
    return Path("data/reference/manual_verifications.csv")


def validate_semantic_evidence(path: Path) -> None:
    all_rows = load_manual_verifications(path)
    rows = tuple(
        row
        for row in all_rows
        if row.verification_id.startswith("NB18-")
    )
    ids = {row.verification_id for row in rows}
    if len(rows) != 3 or ids != EXPECTED_VERIFICATION_IDS:
        raise AssertionError(
            "Notebook 18 semantic evidence closure changed; "
            f"missing={sorted(EXPECTED_VERIFICATION_IDS - ids)}, "
            f"extra={sorted(ids - EXPECTED_VERIFICATION_IDS)}"
        )
    if Counter(row.verification_status for row in rows) != Counter({"confirmed": 3}):
        raise AssertionError("all Notebook 18 semantic records must remain confirmed")
    if Counter(row.database_action for row in rows) != Counter(
        {"reference_enrichment": 3}
    ):
        raise AssertionError(
            "all Notebook 18 semantic records must remain reference enrichments"
        )

    indexed = {row.verification_id: row for row in rows}
    for verification_id, expected in EXPECTED_SEMANTIC_FACTS.items():
        row = indexed[verification_id]
        if row.subject_type != "source_value":
            raise AssertionError(f"{verification_id}: subject_type must be source_value")
        if row.governing_notebook != "18":
            raise AssertionError(f"{verification_id}: governing_notebook must be 18")
        if row.verification_status != "confirmed":
            raise AssertionError(f"{verification_id}: verification must be confirmed")
        if row.evidence_type != "publisher_reference":
            raise AssertionError(f"{verification_id}: publisher evidence is required")
        if row.evidence_accessed_date != "2026-08-01":
            raise AssertionError(f"{verification_id}: evidence access date changed")
        if row.confidence != "high" or not row.evidence_locator or not row.notes:
            raise AssertionError(
                f"{verification_id}: confidence, locator and notes must be preserved"
            )
        for field, expected_value in expected.items():
            if getattr(row, field) != expected_value:
                raise AssertionError(
                    f"{verification_id}: {field} changed; "
                    f"observed={getattr(row, field)!r}, expected={expected_value!r}"
                )


def validate(database: Path, manual_verifications: Path) -> None:
    if not database.exists():
        raise FileNotFoundError(f"Source database not found: {database}")

    validate_semantic_evidence(manual_verifications)

    connection = sqlite3.connect(f"file:{database.resolve()}?mode=ro", uri=True)
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM data WHERE rowid <> 1"
        ).fetchone()[0]
        if total != EXPECTED_RUNNER_ROWS:
            raise AssertionError(
                f"Unexpected governed population: {total:,} "
                f"(expected {EXPECTED_RUNNER_ROWS:,})"
            )

        for field in RATING_FIELDS:
            quoted = f'"{field}"'
            invalid_condition = (
                f"rowid = {INVALID_RPR_SOURCE_ROWID} "
                f"AND {quoted} = {INVALID_RPR_RAW_VALUE}"
                if field == "rpr"
                else "0"
            )

            row = connection.execute(
                f"""
                SELECT
                    SUM(CASE
                        WHEN {invalid_condition} THEN 0
                        WHEN typeof({quoted}) = 'integer' THEN 1
                        ELSE 0
                    END) AS available_rows,
                    SUM(CASE
                        WHEN typeof({quoted}) = 'text'
                         AND CAST({quoted} AS TEXT) = ? THEN 1
                        ELSE 0
                    END) AS unavailable_rows,
                    SUM(CASE
                        WHEN {invalid_condition} THEN 1
                        ELSE 0
                    END) AS invalid_rows,
                    SUM(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN 1 ELSE 0
                    END) AS numeric_rows,
                    MIN(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN CAST({quoted} AS INTEGER)
                    END) AS minimum_value,
                    MAX(CASE
                        WHEN NOT ({invalid_condition})
                         AND typeof({quoted}) = 'integer'
                        THEN CAST({quoted} AS INTEGER)
                    END) AS maximum_value,
                    SUM(CASE
                        WHEN NOT ({invalid_condition})
                         AND NOT (
                            typeof({quoted}) = 'integer'
                            OR (
                                typeof({quoted}) = 'text'
                                AND CAST({quoted} AS TEXT) = ?
                            )
                         )
                        THEN 1 ELSE 0
                    END) AS unresolved_rows
                FROM data
                WHERE rowid <> 1
                """,
                (UNAVAILABLE_RATING_TOKEN, UNAVAILABLE_RATING_TOKEN),
            ).fetchone()

            available, unavailable, invalid, numeric, minimum, maximum, unresolved = row
            expected = EXPECTED_COUNTS[field]
            observed = {
                "available": int(available),
                "unavailable": int(unavailable),
                "invalid": int(invalid),
            }

            if observed != expected:
                raise AssertionError(
                    f"Unexpected {field} status counts: {observed}; expected {expected}"
                )
            if int(numeric) != expected["available"]:
                raise AssertionError(f"{field} numeric count did not reconcile")
            if int(unresolved) != 0:
                raise AssertionError(f"{field} has {unresolved} unresolved source rows")
            if (int(minimum), int(maximum)) != EXPECTED_RANGES[field]:
                raise AssertionError(
                    f"Unexpected {field} range: {(minimum, maximum)}; "
                    f"expected {EXPECTED_RANGES[field]}"
                )
            if sum(observed.values()) != EXPECTED_RUNNER_ROWS:
                raise AssertionError(f"{field} statuses do not partition the source")

        anomaly = connection.execute(
            """
            SELECT rpr
            FROM data
            WHERE rowid = ?
            """,
            (INVALID_RPR_SOURCE_ROWID,),
        ).fetchone()
        if anomaly is None or anomaly[0] != INVALID_RPR_RAW_VALUE:
            raise AssertionError("The exact governed RPR anomaly no longer matches")

        parsed_anomaly = parse_rating(
            anomaly[0],
            "rpr",
            source_rowid=INVALID_RPR_SOURCE_ROWID,
        )
        if parsed_anomaly["rating_status"] != "invalid_source_value":
            raise AssertionError("Reusable parser did not exclude the exact anomaly")

    finally:
        connection.close()

    print(f"Ratings validation passed across {EXPECTED_RUNNER_ROWS:,} governed rows.")
    for field in RATING_FIELDS:
        expected = EXPECTED_COUNTS[field]
        minimum, maximum = EXPECTED_RANGES[field]
        print(
            f"  {field}: available={expected['available']:,}; "
            f"unavailable={expected['unavailable']:,}; "
            f"invalid={expected['invalid']:,}; range={minimum}-{maximum}"
        )
    print("  semantic evidence records: 3 confirmed publisher references")
    print("  semantic evidence-to-field agreement: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=default_database(),
        help="Path to the immutable Raceform SQLite source",
    )
    parser.add_argument(
        "--manual-verifications",
        type=Path,
        default=default_manual_verifications(),
        help="Path to the permanent manual-verification register",
    )
    args = parser.parse_args()
    validate(args.database, args.manual_verifications)


if __name__ == "__main__":
    main()
