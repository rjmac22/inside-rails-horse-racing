#!/usr/bin/env python3
"""Validate Notebook 13 prize-money governance against the immutable source."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from inside_rails.course_jurisdiction import derive_candidate_race_jurisdiction
from inside_rails.prize_money import parse_prize_money
from inside_rails.source_sqlite import connect_read_only


EXPECTED_RUNNER_ROWS = 1_851_285
EXPECTED_PROVISIONAL_RACES = 189_043
EXPECTED_DISTINCT_RAW_VALUES = 47_215
EXPECTED_STORAGE_CLASS_COUNTS = {
    "integer": 225_078,
    "real": 618_026,
    "text": 1_008_181,
}
EXPECTED_STATUS_COUNTS = {
    "blank": 839_715,
    "canonical": 730_318,
    "currency_unresolved": 281_252,
    "invalid": 0,
}
EXPECTED_METHOD_COUNTS = {
    "source_blank_preserved": 839_715,
    "direct_gb_numeric_gbp": 561_852,
    "direct_ireland_euro_text": 168_466,
    "source_presented_amount_currency_unresolved": 281_252,
}
EXPECTED_CURRENCY_COUNTS = {
    "GBP": 561_852,
    "EUR": 168_466,
    "unassigned": 1_120_967,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate governed prize-money parsing source-wide."
    )
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=Path(
            "data/raw/form_2015-present/form_2015-present/raceform.db"
        ),
        help="Path to the immutable source SQLite database.",
    )
    return parser.parse_args()


def _race_jurisdictions(connection: object) -> dict[tuple[str, str, str], str]:
    rows = connection.execute(
        """
        SELECT date, course, off, MIN(race_name), MIN(type)
        FROM data
        WHERE rowid <> 1
        GROUP BY date, course, off
        """
    ).fetchall()
    if len(rows) != EXPECTED_PROVISIONAL_RACES:
        raise AssertionError(
            f"expected {EXPECTED_PROVISIONAL_RACES} provisional races, found {len(rows)}"
        )

    mapping: dict[tuple[str, str, str], str] = {}
    for raw_date, raw_course, raw_off, race_name, source_type in rows:
        result = derive_candidate_race_jurisdiction(
            {
                "date": raw_date,
                "course": raw_course,
                "type": source_type,
                "race_name": race_name,
            }
        )
        jurisdiction = str(result.iloc[0])
        if jurisdiction == "unresolved":
            raise AssertionError(
                "Notebook 13 requires governed jurisdiction for every race; "
                f"unresolved key={(raw_date, raw_course, raw_off)!r}"
            )
        key = (str(raw_date), str(raw_course), str(raw_off))
        if key in mapping:
            raise AssertionError(f"duplicate provisional race key: {key!r}")
        mapping[key] = jurisdiction
    return mapping


def main() -> None:
    args = parse_args()
    if not args.database.exists():
        raise FileNotFoundError(args.database)

    with connect_read_only(args.database) as connection:
        jurisdiction_by_race = _race_jurisdictions(connection)

        storage_rows = connection.execute(
            """
            SELECT typeof(prize), COUNT(*)
            FROM data
            WHERE rowid <> 1
            GROUP BY typeof(prize)
            """
        ).fetchall()
        storage_counts = {str(kind): int(count) for kind, count in storage_rows}
        distinct_raw_values = int(
            connection.execute(
                "SELECT COUNT(DISTINCT prize) FROM data WHERE rowid <> 1"
            ).fetchone()[0]
        )

        status_counts: Counter[str] = Counter()
        method_counts: Counter[str] = Counter()
        currency_counts: Counter[str] = Counter()
        runner_rows = 0

        cursor = connection.execute(
            """
            SELECT date, course, off, prize
            FROM data
            WHERE rowid <> 1
            """
        )
        for raw_date, raw_course, raw_off, raw_prize in cursor:
            key = (str(raw_date), str(raw_course), str(raw_off))
            try:
                jurisdiction = jurisdiction_by_race[key]
            except KeyError as exc:
                raise AssertionError(f"missing jurisdiction for race key {key!r}") from exc

            parsed = parse_prize_money(raw_prize, jurisdiction)
            status = str(parsed["prize_interpretation_status"])
            method = str(parsed["prize_interpretation_method"])
            currency = parsed["prize_currency"] or "unassigned"

            status_counts[status] += 1
            method_counts[method] += 1
            currency_counts[str(currency)] += 1
            runner_rows += 1

            if parsed["prize_raw"] != raw_prize:
                raise AssertionError("prize parser did not preserve the exact raw value")
            if parsed["prize_conversion_multiplier"] is not None:
                raise AssertionError("Notebook 13 does not authorise currency conversion")
            if status == "blank" and parsed["prize_source_presented_amount"] is not None:
                raise AssertionError("blank prize must not become a numeric amount")
            if status == "canonical":
                if parsed["prize_canonical_minor_units"] is None:
                    raise AssertionError("canonical prize requires exact minor units")
                if parsed["prize_currency"] not in {"GBP", "EUR"}:
                    raise AssertionError("canonical prize currency must be GBP or EUR")
            elif parsed["prize_canonical_minor_units"] is not None:
                raise AssertionError(
                    "non-canonical prize must not receive canonical minor units"
                )

    if runner_rows != EXPECTED_RUNNER_ROWS:
        raise AssertionError(
            f"expected {EXPECTED_RUNNER_ROWS} runner rows, found {runner_rows}"
        )
    if storage_counts != EXPECTED_STORAGE_CLASS_COUNTS:
        raise AssertionError(
            f"unexpected prize storage classes: observed={storage_counts}, "
            f"expected={EXPECTED_STORAGE_CLASS_COUNTS}"
        )
    if distinct_raw_values != EXPECTED_DISTINCT_RAW_VALUES:
        raise AssertionError(
            f"expected {EXPECTED_DISTINCT_RAW_VALUES} distinct raw prize values, "
            f"found {distinct_raw_values}"
        )
    if status_counts != Counter(EXPECTED_STATUS_COUNTS):
        raise AssertionError(
            f"unexpected prize status partition: observed={dict(status_counts)}, "
            f"expected={EXPECTED_STATUS_COUNTS}"
        )
    if method_counts != Counter(EXPECTED_METHOD_COUNTS):
        raise AssertionError(
            f"unexpected prize method partition: observed={dict(method_counts)}, "
            f"expected={EXPECTED_METHOD_COUNTS}"
        )
    if currency_counts != Counter(EXPECTED_CURRENCY_COUNTS):
        raise AssertionError(
            f"unexpected prize currency partition: observed={dict(currency_counts)}, "
            f"expected={EXPECTED_CURRENCY_COUNTS}"
        )
    if sum(status_counts.values()) != runner_rows:
        raise AssertionError("prize statuses do not partition the runner population")

    normalised_statuses = {
        key: status_counts[key] for key in EXPECTED_STATUS_COUNTS
    }
    print("Prize-money source-wide validation passed.")
    print(f"  governed runner rows: {runner_rows:,}")
    print(f"  provisional races: {len(jurisdiction_by_race):,}")
    print(f"  distinct raw prize values: {distinct_raw_values:,}")
    print(f"  storage classes: {storage_counts}")
    print(f"  status partition: {normalised_statuses}")
    print(f"  method partition: {dict(method_counts)}")
    print(f"  currency partition: {dict(currency_counts)}")
    print("  canonical currencies: GBP and EUR only")
    print("  foreign exchange conversions applied: 0")


if __name__ == "__main__":
    main()
