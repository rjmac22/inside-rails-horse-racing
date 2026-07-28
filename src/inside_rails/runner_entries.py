"""Governed interpretation of source ``ran`` and ``num`` fields.

Notebook 14 established that ``ran`` is a source-presented race-level count,
not a guaranteed complete starter count. It also established that ``num`` can
be a positive integer, integer zero, or blank text, and that positive values
are not universally unique within a race.

This module preserves those distinctions without reconstructing missing
runners, coupled-entry suffixes, or external field sizes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Integral
from typing import Any, Iterable


@dataclass(frozen=True)
class RunnerNumberResult:
    """Governed interpretation of one raw runner-level ``num`` value."""

    source_num_raw: Any
    source_num_storage_class: str
    source_positive_runner_number: int | None
    source_num_state: str
    source_num_within_race_multiplicity: int | None
    source_num_uniqueness_status: str

    def as_dict(self) -> dict[str, Any]:
        """Return a staging-friendly mapping."""

        return asdict(self)


@dataclass(frozen=True)
class ReportedRanResult:
    """Governed race-level profile of source ``ran`` values."""

    source_reported_ran: int | None
    source_runner_row_count: int
    source_ran_distinct_value_count: int
    source_ran_consistency_status: str
    source_row_count_vs_ran_status: str
    source_runner_coverage_status: str
    source_ran_external_status: str

    def as_dict(self) -> dict[str, Any]:
        """Return a staging-friendly mapping."""

        return asdict(self)


def _source_storage_class(value: Any) -> str:
    """Return the relevant Python-side equivalent of SQLite storage class."""

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "invalid"
    if isinstance(value, Integral):
        return "integer"
    if isinstance(value, str):
        return "text"
    return type(value).__name__


def parse_runner_number(
    raw_num: Any,
    *,
    within_race_multiplicity: int | None = None,
) -> dict[str, Any]:
    """Interpret one source ``num`` value under Notebook 14 policy.

    ``within_race_multiplicity`` is supplied by race-level staging after
    grouping positive integers within the provisional race. A shared value is
    classified, but never interpreted automatically as a coupled entry or a
    duplicate runner.
    """

    storage_class = _source_storage_class(raw_num)

    if storage_class == "text" and not raw_num.strip():
        return RunnerNumberResult(
            source_num_raw=raw_num,
            source_num_storage_class="text",
            source_positive_runner_number=None,
            source_num_state="blank_text",
            source_num_within_race_multiplicity=None,
            source_num_uniqueness_status="nonpositive_state",
        ).as_dict()

    if storage_class == "integer":
        integer_num = int(raw_num)

        if integer_num == 0:
            return RunnerNumberResult(
                source_num_raw=raw_num,
                source_num_storage_class="integer",
                source_positive_runner_number=None,
                source_num_state="integer_zero",
                source_num_within_race_multiplicity=None,
                source_num_uniqueness_status="nonpositive_state",
            ).as_dict()

        if integer_num > 0:
            if within_race_multiplicity is None:
                multiplicity = None
                uniqueness_status = "unassessed"
            else:
                if isinstance(within_race_multiplicity, bool) or not isinstance(
                    within_race_multiplicity, Integral
                ):
                    raise TypeError(
                        "within_race_multiplicity must be an integer when supplied"
                    )
                if int(within_race_multiplicity) < 1:
                    raise ValueError(
                        "within_race_multiplicity must be at least 1 when supplied"
                    )

                multiplicity = int(within_race_multiplicity)
                uniqueness_status = (
                    "unique_within_race"
                    if multiplicity == 1
                    else "shared_positive_num"
                )

            return RunnerNumberResult(
                source_num_raw=raw_num,
                source_num_storage_class="integer",
                source_positive_runner_number=integer_num,
                source_num_state="positive_integer",
                source_num_within_race_multiplicity=multiplicity,
                source_num_uniqueness_status=uniqueness_status,
            ).as_dict()

    if storage_class == "null":
        state = "null"
    else:
        state = "invalid"

    return RunnerNumberResult(
        source_num_raw=raw_num,
        source_num_storage_class=storage_class,
        source_positive_runner_number=None,
        source_num_state=state,
        source_num_within_race_multiplicity=None,
        source_num_uniqueness_status="nonpositive_state",
    ).as_dict()


def profile_reported_ran(
    raw_ran_values: Iterable[Any],
    *,
    source_runner_row_count: int | None = None,
    source_runner_coverage_status: str | None = None,
    source_ran_external_status: str = "unverified",
) -> dict[str, Any]:
    """Profile source ``ran`` values for one provisional race.

    Internal row-count comparison and external validation remain separate.
    Internal equality may produce ``internally_equal_to_ran`` but never an
    externally verified status.
    """

    values = list(raw_ran_values)

    if source_runner_row_count is None:
        source_runner_row_count = len(values)

    if isinstance(source_runner_row_count, bool) or not isinstance(
        source_runner_row_count, Integral
    ):
        raise TypeError("source_runner_row_count must be an integer")
    if int(source_runner_row_count) < 0:
        raise ValueError("source_runner_row_count cannot be negative")

    runner_row_count = int(source_runner_row_count)

    valid_values = [
        int(value)
        for value in values
        if isinstance(value, Integral)
        and not isinstance(value, bool)
        and 1 <= int(value) <= 40
    ]
    invalid_values_present = len(valid_values) != len(values)
    distinct_values = set(valid_values)

    if not values:
        reported_ran = None
        consistency_status = "missing"
    elif invalid_values_present:
        reported_ran = next(iter(distinct_values)) if len(distinct_values) == 1 else None
        consistency_status = "invalid"
    elif len(distinct_values) == 1:
        reported_ran = next(iter(distinct_values))
        consistency_status = "consistent"
    else:
        reported_ran = None
        consistency_status = "conflicting"

    if consistency_status != "consistent" or reported_ran is None:
        row_count_status = "not_comparable"
    elif runner_row_count == reported_ran:
        row_count_status = "equal"
    elif runner_row_count < reported_ran:
        row_count_status = "below"
    else:
        row_count_status = "above"

    allowed_coverage_statuses = {
        "unverified",
        "internally_equal_to_ran",
        "known_partial",
        "externally_verified_complete",
    }

    if source_runner_coverage_status is None:
        if row_count_status == "equal":
            runner_coverage_status = "internally_equal_to_ran"
        elif row_count_status == "below":
            runner_coverage_status = "known_partial"
        else:
            runner_coverage_status = "unverified"
    else:
        if source_runner_coverage_status not in allowed_coverage_statuses:
            raise ValueError(
                "Unsupported source_runner_coverage_status: "
                f"{source_runner_coverage_status!r}"
            )
        runner_coverage_status = source_runner_coverage_status

    allowed_external_statuses = {
        "unverified",
        "externally_verified",
        "externally_contradicted",
    }
    if source_ran_external_status not in allowed_external_statuses:
        raise ValueError(
            "Unsupported source_ran_external_status: "
            f"{source_ran_external_status!r}"
        )

    return ReportedRanResult(
        source_reported_ran=reported_ran,
        source_runner_row_count=runner_row_count,
        source_ran_distinct_value_count=len(distinct_values),
        source_ran_consistency_status=consistency_status,
        source_row_count_vs_ran_status=row_count_status,
        source_runner_coverage_status=runner_coverage_status,
        source_ran_external_status=source_ran_external_status,
    ).as_dict()
