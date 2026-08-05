#!/usr/bin/env python3
"""Validate Notebook 16 parsers, decisions and external evidence source-wide."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable
import csv
from pathlib import Path
import sqlite3
import sys
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from inside_rails.manual_verifications import load_manual_verifications  # noqa: E402
from inside_rails.race_classification import (  # noqa: E402
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)
from inside_rails.source_sqlite import connect_read_only, quote_identifier  # noqa: E402


DEFAULT_DATABASE = Path(
    "data/raw/form_2015-present/form_2015-present/raceform.db"
)
DEFAULT_MANUAL_VERIFICATIONS = Path("data/reference/manual_verifications.csv")
DEFAULT_FIELD_DECISIONS = Path(
    "data/derived/notebook_16_race_classification_and_eligibility/"
    "race_classification_field_decisions.csv"
)
SOURCE_TABLE = "data"
DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_PROVISIONAL_RACES = 189_043
RACE_KEY_COLUMNS = ("date", "course", "off")
EXPECTED_VERIFICATION_IDS = {
    "NB16-AGE-0001",
    "NB16-AGE-0002",
    "NB16-AGE-0003",
    "NB16-AGE-0004",
}
EXPECTED_VERIFICATION_STATUS_COUNTS = Counter(
    {"contradicted": 2, "confirmed": 1, "partially_confirmed": 1}
)
EXPECTED_VERIFICATION_ACTION_COUNTS = Counter(
    {
        "source_correction_candidate": 2,
        "evidence_only": 1,
        "preserve_raw_unresolved": 1,
    }
)
EXPECTED_VERIFICATION_FACTS = {
    "NB16-AGE-0001": {
        "subject_type": "race",
        "source_date": "2017-05-16",
        "source_course": "Compiegne (FR)",
        "source_off": "1:35",
        "source_horse": "",
        "source_field": "age_band",
        "raw_source_value": "5yo",
        "verified_value": "5yo+",
        "verification_status": "contradicted",
        "confidence": "high",
        "database_action": "source_correction_candidate",
    },
    "NB16-AGE-0002": {
        "subject_type": "runner",
        "source_date": "2024-07-27",
        "source_course": "Woodbine (CAN)",
        "source_off": "9:47",
        "source_horse": "Ecstasy (USA)",
        "source_field": "age",
        "raw_source_value": "31",
        "verified_value": "3",
        "verification_status": "contradicted",
        "confidence": "high",
        "database_action": "source_correction_candidate",
    },
    "NB16-AGE-0003": {
        "subject_type": "race",
        "source_date": "2015-01-17",
        "source_course": "Fair Grounds (USA)",
        "source_off": "8:55",
        "source_horse": "",
        "source_field": "age_band; runner age",
        "raw_source_value": "age_band=4yo; source runner ages include 5, 6 and 7",
        "verified_value": "published condition=4yo; published runner ages include 5 and 7",
        "verification_status": "confirmed",
        "confidence": "high",
        "database_action": "evidence_only",
    },
    "NB16-AGE-0004": {
        "subject_type": "race",
        "source_date": "2015-08-01",
        "source_course": "Greyville (SAF)",
        "source_off": "2:30",
        "source_horse": "",
        "source_field": "age_band; runner age",
        "raw_source_value": "age_band=2yo; all 16 source runner ages=3",
        "verified_value": "published condition=2yo; cause of stored age=3 discrepancy unresolved",
        "verification_status": "partially_confirmed",
        "confidence": "medium",
        "database_action": "preserve_raw_unresolved",
    },
}
EXPECTED_FIELD_DECISION_STATUS = {
    "race_name": "confirmed_raw_source_field",
    "type": "confirmed_source_category",
    "class": "confirmed_structure_contextual_meaning",
    "pattern": "confirmed_structure_jurisdiction_dependent",
    "rating_band": "confirmed_parser_with_unresolved_forms",
    "age_band": "confirmed_syntax_contextual_semantics",
    "sex_rest": "confirmed_source_shorthand_overloaded",
}
FIELD_DECISION_COLUMNS = (
    "field",
    "source_meaning",
    "safe_derived_treatment",
    "unresolved_or_unsafe_treatment",
    "status",
)


def _distinct_values(connection: sqlite3.Connection, column: str) -> list[Any]:
    quoted_column = quote_identifier(column)
    quoted_table = quote_identifier(SOURCE_TABLE)
    rows = connection.execute(
        f"""
        SELECT DISTINCT {quoted_column}
        FROM {quoted_table}
        WHERE {DATA_ROW_PREDICATE}
        ORDER BY {quoted_column}
        """
    ).fetchall()
    return [row[0] for row in rows]


def _assert_all_statuses(
    values: list[Any],
    parser: Callable[[Any], dict[str, Any]],
    status_field: str,
    allowed_statuses: set[str],
    field_name: str,
) -> None:
    failures: list[tuple[Any, str]] = []
    for raw_value in values:
        result = parser(raw_value)
        status = result[status_field]
        if status not in allowed_statuses:
            failures.append((raw_value, status))
    if failures:
        raise AssertionError(f"Unexpected {field_name} parser results: {failures!r}")


def _validate_population(connection: sqlite3.Connection) -> None:
    quoted_table = quote_identifier(SOURCE_TABLE)
    runner_rows = connection.execute(
        f"SELECT COUNT(*) FROM {quoted_table} WHERE {DATA_ROW_PREDICATE}"
    ).fetchone()[0]
    if runner_rows != EXPECTED_RUNNER_ROWS:
        raise AssertionError(
            f"Expected {EXPECTED_RUNNER_ROWS:,} runner rows, got {runner_rows:,}."
        )

    race_key = ", ".join(quote_identifier(column) for column in RACE_KEY_COLUMNS)
    provisional_races = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {race_key}
            FROM {quoted_table}
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY {race_key}
        )
        """
    ).fetchone()[0]
    if provisional_races != EXPECTED_PROVISIONAL_RACES:
        raise AssertionError(
            f"Expected {EXPECTED_PROVISIONAL_RACES:,} provisional races, "
            f"got {provisional_races:,}."
        )


def _validate_race_level_consistency(connection: sqlite3.Connection) -> None:
    quoted_table = quote_identifier(SOURCE_TABLE)
    race_key = ", ".join(quote_identifier(column) for column in RACE_KEY_COLUMNS)
    governed_columns = (
        "race_name",
        "type",
        "class",
        "pattern",
        "rating_band",
        "age_band",
        "sex_rest",
    )
    for column in governed_columns:
        quoted_column = quote_identifier(column)
        inconsistent_races = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT {race_key}
                FROM {quoted_table}
                WHERE {DATA_ROW_PREDICATE}
                GROUP BY {race_key}
                HAVING COUNT(
                    DISTINCT COALESCE(CAST({quoted_column} AS TEXT), '<NULL>')
                ) > 1
            )
            """
        ).fetchone()[0]
        if inconsistent_races:
            raise AssertionError(
                f"{column!r} varies within {inconsistent_races:,} provisional races."
            )


def _validate_vocabularies(connection: sqlite3.Connection) -> None:
    _assert_all_statuses(
        _distinct_values(connection, "class"),
        parse_class,
        "class_parse_status",
        {"blank", "canonical"},
        "class",
    )
    _assert_all_statuses(
        _distinct_values(connection, "pattern"),
        parse_pattern,
        "pattern_parse_status",
        {"blank", "canonical"},
        "pattern",
    )
    _assert_all_statuses(
        _distinct_values(connection, "rating_band"),
        parse_rating_band,
        "rating_band_parse_status",
        {"blank", "canonical", "unrecognised_source_form"},
        "rating_band",
    )
    _assert_all_statuses(
        _distinct_values(connection, "age_band"),
        parse_age_band,
        "age_band_syntax",
        {"blank", "exact_age", "open_ended_minimum", "closed_age_range"},
        "age_band",
    )
    _assert_all_statuses(
        _distinct_values(connection, "sex_rest"),
        classify_sex_restriction,
        "sex_rest_interpretation_status",
        {"blank", "explicit_source_category", "overloaded_source_category"},
        "sex_rest",
    )

    unresolved_rating_values = {
        value
        for value in _distinct_values(connection, "rating_band")
        if parse_rating_band(value)["rating_band_parse_status"]
        == "unrecognised_source_form"
    }
    expected_unresolved = {"--", "(75-100)"}
    if unresolved_rating_values != expected_unresolved:
        raise AssertionError(
            "Unexpected unresolved rating-band vocabulary: "
            f"expected {expected_unresolved!r}, got {unresolved_rating_values!r}."
        )


def _validate_field_decisions(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELD_DECISION_COLUMNS:
            raise AssertionError(
                "Notebook 16 field-decision columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        rows = tuple(
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        )
    if len(rows) != 7:
        raise AssertionError(f"expected 7 Notebook 16 field decisions, found {len(rows)}")
    indexed = {row["field"]: row for row in rows}
    if len(indexed) != len(rows) or set(indexed) != set(EXPECTED_FIELD_DECISION_STATUS):
        raise AssertionError(
            f"unexpected Notebook 16 field-decision closure: {sorted(indexed)!r}"
        )
    for field, expected_status in EXPECTED_FIELD_DECISION_STATUS.items():
        row = indexed[field]
        if row["status"] != expected_status:
            raise AssertionError(
                f"{field}: decision status changed from {expected_status!r} "
                f"to {row['status']!r}"
            )
        if not row["source_meaning"] or not row["safe_derived_treatment"]:
            raise AssertionError(f"{field}: positive governance text is required")
        if not row["unresolved_or_unsafe_treatment"]:
            raise AssertionError(f"{field}: unresolved/unsafe treatment is required")


def _validate_external_decisions(path: Path) -> dict[str, object]:
    all_rows = load_manual_verifications(path)
    rows = tuple(
        row for row in all_rows if row.verification_id.startswith("NB16-AGE-")
    )
    ids = {row.verification_id for row in rows}
    if len(rows) != 4 or ids != EXPECTED_VERIFICATION_IDS:
        raise AssertionError(
            "Notebook 16 verification closure changed; "
            f"missing={sorted(EXPECTED_VERIFICATION_IDS - ids)}, "
            f"extra={sorted(ids - EXPECTED_VERIFICATION_IDS)}"
        )
    statuses = Counter(row.verification_status for row in rows)
    actions = Counter(row.database_action for row in rows)
    if statuses != EXPECTED_VERIFICATION_STATUS_COUNTS:
        raise AssertionError(f"unexpected Notebook 16 status partition: {dict(statuses)}")
    if actions != EXPECTED_VERIFICATION_ACTION_COUNTS:
        raise AssertionError(f"unexpected Notebook 16 action partition: {dict(actions)}")

    indexed = {row.verification_id: row for row in rows}
    for verification_id, expected in EXPECTED_VERIFICATION_FACTS.items():
        row = indexed[verification_id]
        if row.governing_notebook != "16":
            raise AssertionError(f"{verification_id}: governing_notebook must be 16")
        for field, expected_value in expected.items():
            if getattr(row, field) != expected_value:
                raise AssertionError(
                    f"{verification_id}: {field} changed; "
                    f"observed={getattr(row, field)!r}, expected={expected_value!r}"
                )
        if not row.evidence_type or not row.evidence_locator.startswith("https://"):
            raise AssertionError(f"{verification_id}: direct external evidence is required")
        if row.evidence_accessed_date != "2026-07-30" or not row.notes:
            raise AssertionError(
                f"{verification_id}: access date and notes must remain governed"
            )
    return indexed


def _validate_target_source_rows(connection: sqlite3.Connection) -> None:
    compiegne = connection.execute(
        """
        SELECT DISTINCT age_band
        FROM data
        WHERE rowid <> 1 AND date = '2017-05-16'
          AND course = 'Compiegne (FR)' AND off = '1:35'
        """
    ).fetchall()
    if {str(row[0]) for row in compiegne} != {"5yo"}:
        raise AssertionError("NB16-AGE-0001 source age_band changed")

    ecstasy = connection.execute(
        """
        SELECT age
        FROM data
        WHERE rowid <> 1 AND date = '2024-07-27'
          AND course = 'Woodbine (CAN)' AND off = '9:47'
          AND horse = 'Ecstasy (USA)'
        """
    ).fetchall()
    if [int(row[0]) for row in ecstasy] != [31]:
        raise AssertionError("NB16-AGE-0002 source runner age changed")

    fair_grounds = connection.execute(
        """
        SELECT age_band, age
        FROM data
        WHERE rowid <> 1 AND date = '2015-01-17'
          AND course = 'Fair Grounds (USA)' AND off = '8:55'
        """
    ).fetchall()
    fair_age_bands = {str(row[0]) for row in fair_grounds}
    fair_ages = {int(row[1]) for row in fair_grounds}
    if fair_age_bands != {"4yo"} or not {5, 6, 7}.issubset(fair_ages):
        raise AssertionError("NB16-AGE-0003 source age evidence changed")

    greyville = connection.execute(
        """
        SELECT age_band, age
        FROM data
        WHERE rowid <> 1 AND date = '2015-08-01'
          AND course = 'Greyville (SAF)' AND off = '2:30'
        """
    ).fetchall()
    if len(greyville) != 16:
        raise AssertionError("NB16-AGE-0004 source runner count changed")
    if {str(row[0]) for row in greyville} != {"2yo"}:
        raise AssertionError("NB16-AGE-0004 source age_band changed")
    if {int(row[1]) for row in greyville} != {3}:
        raise AssertionError("NB16-AGE-0004 source runner ages changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--manual-verifications",
        type=Path,
        default=DEFAULT_MANUAL_VERIFICATIONS,
    )
    parser.add_argument(
        "--field-decisions",
        type=Path,
        default=DEFAULT_FIELD_DECISIONS,
    )
    args = parser.parse_args()

    _validate_field_decisions(args.field_decisions)
    _validate_external_decisions(args.manual_verifications)
    with connect_read_only(args.database) as connection:
        _validate_population(connection)
        _validate_race_level_consistency(connection)
        _validate_vocabularies(connection)
        _validate_target_source_rows(connection)

    print(
        "Race-classification validation passed for "
        f"{EXPECTED_RUNNER_ROWS:,} runner rows and "
        f"{EXPECTED_PROVISIONAL_RACES:,} provisional races."
    )
    print("  persisted field decisions: 7")
    print("  governed external decisions: 4")
    print("  decision partition: 2 correction candidates, 1 evidence-only, 1 unresolved")
    print("  automatic external corrections authorised: 0")


if __name__ == "__main__":
    main()
