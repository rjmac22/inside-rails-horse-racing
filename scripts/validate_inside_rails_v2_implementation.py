#!/usr/bin/env python3
"""Run fast, source-independent checks on the Database v2 implementation.

This is deliberately a focused preflight rather than the full repository suite or
source-wide Database v2 validator. It catches Python import/syntax failures,
physical-schema drift, invalid study-facing views and committed reference-artifact
count changes before spending time copying/populating the 1.7 GB Database v1
release.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sqlite3
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inside_rails.course_locations import load_course_locations
from inside_rails.database.governed_integration_population import (
    _RACE_INSERT,
    _RUNNER_INSERT,
)
from inside_rails.database.schema import (
    GOVERNED_INTEGRATION_SCHEMA_VERSION,
    create_governed_integration_schema,
)
from inside_rails.field_governance import FIELD_GOVERNANCE, validate_field_governance
from inside_rails.horse_pedigree_identity import load_identity_governance
from inside_rails.jurisdiction_context import CONTEXTS, validate_context_reference
from inside_rails.manual_verifications import load_manual_verifications
from inside_rails.runner_record_supplementations import (
    load_runner_record_supplementations,
)


EXPECTED_TABLES = 31
EXPECTED_V2_VIEWS = {
    "view_governed_race_occurrences",
    "view_governed_horse_occurrence_assignments",
    "view_governed_participant_label_identities",
    "view_governed_source_runner_participations",
    "view_governed_runner_records",
}
EXPECTED_REFERENCE_COUNTS = {
    "course_reference": 395,
    "jurisdiction_context": 16,
    "field_governance": 37,
    "runner_supplementation": 3,
    "horse_specialist_decision": 16,
    "jockey_mapping": 2,
    "trainer_mapping": 52,
    "owner_mapping": 95,
    "jockey_candidate": 216,
    "trainer_candidate": 53,
    "owner_candidate": 936,
}


def _csv_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _placeholder_count(sql: str) -> int:
    return len(re.findall(r"\?", sql))


def main() -> None:
    # Validate each durable finite reference through its production loader where
    # one exists. This ensures a malformed committed artifact fails before any
    # candidate database is copied or populated.
    courses = load_course_locations(ROOT / "data/reference/course_locations.csv")
    validate_context_reference(CONTEXTS)
    validate_field_governance()
    manual = load_manual_verifications(ROOT / "data/reference/manual_verifications.csv")
    supplements = load_runner_record_supplementations(
        ROOT / "data/reference/runner_record_supplementations.csv"
    )
    horse_governance = load_identity_governance(
        ROOT / "data/reference/horse_pedigree_identity_governance.csv"
    )

    observed_references = {
        "course_reference": len(courses),
        "jurisdiction_context": len(CONTEXTS),
        "field_governance": len(FIELD_GOVERNANCE),
        "runner_supplementation": len(supplements),
        "horse_specialist_decision": len(horse_governance.rows),
        "jockey_mapping": _csv_count(
            ROOT / "data/processed/jockey_identity/jockey_provisional_identity_mapping.csv"
        ),
        "trainer_mapping": _csv_count(
            ROOT / "data/processed/trainer_identity/trainer_provisional_identity_mapping.csv"
        ),
        "owner_mapping": _csv_count(
            ROOT / "data/processed/owner_identity/owner_provisional_composition_mapping.csv"
        ),
        "jockey_candidate": _csv_count(
            ROOT / "data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv"
        ),
        "trainer_candidate": _csv_count(
            ROOT / "data/processed/trainer_identity/trainer_strict_title_decisions.csv"
        ),
        "owner_candidate": _csv_count(
            ROOT / "data/processed/owner_identity/owner_token_multiset_decisions.csv"
        ),
    }
    if observed_references != EXPECTED_REFERENCE_COUNTS:
        raise RuntimeError(
            "Database v2 committed reference baseline changed: "
            f"{observed_references!r}"
        )

    connection = sqlite3.connect(":memory:")
    try:
        create_governed_integration_schema(connection)
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if user_version != GOVERNED_INTEGRATION_SCHEMA_VERSION:
            raise RuntimeError(
                f"Expected Database v2 schema version {GOVERNED_INTEGRATION_SCHEMA_VERSION}; "
                f"found {user_version}"
            )

        table_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM sqlite_schema "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0]
        )
        if table_count != EXPECTED_TABLES:
            raise RuntimeError(
                f"Expected {EXPECTED_TABLES} Database v2 physical tables; found {table_count}"
            )

        views = {
            str(name)
            for name, in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type='view'"
            )
        }
        missing_views = EXPECTED_V2_VIEWS - views
        if missing_views:
            raise RuntimeError(
                f"Database v2 is missing study-facing views: {sorted(missing_views)}"
            )

        # Force SQLite to resolve every study-facing view now. LIMIT 0 is enough
        # to catch invalid column names, reserved-word quoting mistakes and
        # broken view dependencies without needing source data.
        for view in sorted(EXPECTED_V2_VIEWS):
            connection.execute(f"SELECT * FROM {view} LIMIT 0").fetchall()

        race_columns = len(
            connection.execute(
                "PRAGMA table_info(core_source_race_occurrence_governed)"
            ).fetchall()
        )
        runner_columns = len(
            connection.execute(
                "PRAGMA table_info(core_runner_participation_governed)"
            ).fetchall()
        )
        if _placeholder_count(_RACE_INSERT) != race_columns:
            raise RuntimeError(
                "Race population INSERT width no longer matches the v2 race extension"
            )
        if _placeholder_count(_RUNNER_INSERT) != runner_columns:
            raise RuntimeError(
                "Runner population INSERT width no longer matches the v2 runner extension"
            )

        quick_check = str(connection.execute("PRAGMA quick_check").fetchone()[0])
        foreign_key_rows = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        if quick_check != "ok" or foreign_key_rows:
            raise RuntimeError(
                "Database v2 in-memory schema failed SQLite integrity checks: "
                f"quick_check={quick_check!r}; foreign_key_rows={foreign_key_rows}"
            )
    finally:
        connection.close()

    print(
        json.dumps(
            {
                "database_v2_implementation_preflight": "PASS",
                "schema_version": GOVERNED_INTEGRATION_SCHEMA_VERSION,
                "physical_tables": EXPECTED_TABLES,
                "study_facing_views": sorted(EXPECTED_V2_VIEWS),
                "manual_verification_rows": len(manual),
                "reference_counts": observed_references,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
