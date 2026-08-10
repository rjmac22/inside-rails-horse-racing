import csv
from dataclasses import replace
from pathlib import Path

import pytest

from inside_rails.runner_record_supplementations import (
    EXPECTED_COLUMNS,
    load_runner_record_supplementations,
    validate_runner_record_supplementations,
)


REFERENCE = Path("data/reference/runner_record_supplementations.csv")


def test_governed_reference_loads_with_exact_three_missing_runners() -> None:
    rows = load_runner_record_supplementations(REFERENCE)

    assert len(rows) == 3
    assert {row.verification_id for row in rows} == {
        "NB14-RAN-0001",
        "NB14-RAN-0005",
        "NB15-BTN-0001",
    }
    assert {row.source_horse for row in rows} == {
        "Saucats",
        "Tosen Thunder (JPN)",
        "Great Navigator (USA)",
    }
    great_navigator = next(
        row for row in rows if row.source_horse == "Great Navigator (USA)"
    )
    assert great_navigator.verified_pos == 5
    assert great_navigator.verified_outcome == "finished"


def test_reference_columns_are_exact() -> None:
    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == EXPECTED_COLUMNS


def test_duplicate_runner_key_is_rejected() -> None:
    rows = list(load_runner_record_supplementations(REFERENCE))
    rows[1] = replace(
        rows[1],
        source_date=rows[0].source_date,
        source_course=rows[0].source_course,
        source_off=rows[0].source_off,
        source_horse=rows[0].source_horse,
    )
    with pytest.raises(ValueError, match="runner supplementation keys must be unique"):
        validate_runner_record_supplementations(rows)


def test_nonfinish_cannot_assign_a_numeric_position() -> None:
    rows = list(load_runner_record_supplementations(REFERENCE))
    rows[0] = replace(rows[0], verified_pos=8)
    with pytest.raises(ValueError, match="must not assign position"):
        validate_runner_record_supplementations(rows)


def test_finished_runner_requires_a_position() -> None:
    rows = list(load_runner_record_supplementations(REFERENCE))
    rows[2] = replace(rows[2], verified_pos=None)
    with pytest.raises(ValueError, match="requires position"):
        validate_runner_record_supplementations(rows)


def test_supplementation_requires_a_missing_published_runner() -> None:
    rows = list(load_runner_record_supplementations(REFERENCE))
    rows[0] = replace(rows[0], source_runner_rows=rows[0].published_runners)
    with pytest.raises(ValueError, match="absent from the source race population"):
        validate_runner_record_supplementations(rows)
