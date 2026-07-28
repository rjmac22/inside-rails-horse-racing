#!/usr/bin/env python3
"""Independent smoke validation for governed runner-entry interpretation."""

from __future__ import annotations

from inside_rails.runner_entries import parse_runner_number, profile_reported_ran


def assert_fields(result: dict[str, object], expected: dict[str, object]) -> None:
    """Assert selected governed fields and report the exact mismatch."""

    for field, expected_value in expected.items():
        actual = result[field]
        if actual != expected_value:
            raise AssertionError(
                f"{field=}: expected {expected_value!r}, got {actual!r}; "
                f"full result={result!r}"
            )


def main() -> None:
    """Run independent governed examples for both ``num`` and ``ran``."""

    runner_number_cases = [
        (
            7,
            1,
            {
                "source_positive_runner_number": 7,
                "source_num_state": "positive_integer",
                "source_num_within_race_multiplicity": 1,
                "source_num_uniqueness_status": "unique_within_race",
            },
        ),
        (
            7,
            2,
            {
                "source_positive_runner_number": 7,
                "source_num_state": "positive_integer",
                "source_num_within_race_multiplicity": 2,
                "source_num_uniqueness_status": "shared_positive_num",
            },
        ),
        (
            0,
            None,
            {
                "source_positive_runner_number": None,
                "source_num_state": "integer_zero",
                "source_num_uniqueness_status": "nonpositive_state",
            },
        ),
        (
            "",
            None,
            {
                "source_positive_runner_number": None,
                "source_num_state": "blank_text",
                "source_num_uniqueness_status": "nonpositive_state",
            },
        ),
        (
            "1A",
            None,
            {
                "source_positive_runner_number": None,
                "source_num_state": "invalid",
                "source_num_uniqueness_status": "nonpositive_state",
            },
        ),
    ]

    for raw_num, multiplicity, expected in runner_number_cases:
        result = parse_runner_number(
            raw_num,
            within_race_multiplicity=multiplicity,
        )
        assert_fields(result, expected)

    reported_ran_cases = [
        (
            [8] * 8,
            None,
            {
                "source_reported_ran": 8,
                "source_runner_row_count": 8,
                "source_ran_consistency_status": "consistent",
                "source_row_count_vs_ran_status": "equal",
                "source_runner_coverage_status": "internally_equal_to_ran",
                "source_ran_external_status": "unverified",
            },
        ),
        (
            [8] * 6,
            6,
            {
                "source_reported_ran": 8,
                "source_runner_row_count": 6,
                "source_ran_consistency_status": "consistent",
                "source_row_count_vs_ran_status": "below",
                "source_runner_coverage_status": "known_partial",
            },
        ),
        (
            [8, 9],
            2,
            {
                "source_reported_ran": None,
                "source_ran_consistency_status": "conflicting",
                "source_row_count_vs_ran_status": "not_comparable",
                "source_runner_coverage_status": "unverified",
            },
        ),
        (
            [8] * 8,
            8,
            {
                "source_runner_coverage_status": "externally_verified_complete",
                "source_ran_external_status": "externally_verified",
            },
            {
                "source_runner_coverage_status": "externally_verified_complete",
                "source_ran_external_status": "externally_verified",
            },
        ),
    ]

    for case in reported_ran_cases:
        raw_values, row_count, expected, *overrides = case
        kwargs = overrides[0] if overrides else {}
        result = profile_reported_ran(
            raw_values,
            source_runner_row_count=row_count,
            **kwargs,
        )
        assert_fields(result, expected)

    total_cases = len(runner_number_cases) + len(reported_ran_cases)
    print(f"Runner-entry validation passed for {total_cases} governed cases.")


if __name__ == "__main__":
    main()
