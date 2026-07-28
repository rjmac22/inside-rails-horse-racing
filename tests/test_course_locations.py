from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from inside_rails.course_locations import (
    IDENTITY_COLUMNS,
    REQUIRED_COLUMNS,
    load_course_locations,
    merge_course_locations,
)


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_course_label": "Ascot",
        "candidate_jurisdiction": "Great Britain",
        "physical_venue_name": "Ascot Racecourse",
        "locality": "Ascot",
        "region": "Berkshire",
        "country": "United Kingdom",
        "latitude": 51.416,
        "longitude": -0.676,
        "iana_timezone": "Europe/London",
        "location_evidence": "manual_reference",
        "location_validation_status": "validated",
    }
    row.update(overrides)
    return row


def _write(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    path = tmp_path / "course_locations.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_reference_contract_columns_are_stable() -> None:
    assert IDENTITY_COLUMNS == [
        "candidate_course_label",
        "candidate_jurisdiction",
    ]
    assert set(IDENTITY_COLUMNS).issubset(REQUIRED_COLUMNS)
    assert len(REQUIRED_COLUMNS) == 11


def test_loads_valid_reference(tmp_path: Path) -> None:
    frame = load_course_locations(_write(tmp_path, [_row()]))
    assert len(frame) == 1
    assert frame.loc[0, "iana_timezone"] == "Europe/London"


def test_rejects_missing_required_column(tmp_path: Path) -> None:
    row = _row()
    del row["location_evidence"]
    with pytest.raises(ValueError, match="missing required columns"):
        load_course_locations(_write(tmp_path, [row]))


def test_rejects_duplicate_identity_pair(tmp_path: Path) -> None:
    rows = [_row(), _row(physical_venue_name="Duplicate")]
    with pytest.raises(ValueError, match="Duplicate candidate course identities"):
        load_course_locations(_write(tmp_path, rows))


def test_rejects_invalid_iana_timezone(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid IANA timezone names"):
        load_course_locations(
            _write(tmp_path, [_row(iana_timezone="Europe/NotAZone")])
        )


@pytest.mark.parametrize("latitude", [-90.01, 90.01, "not-a-number"])
def test_rejects_invalid_latitude(tmp_path: Path, latitude: object) -> None:
    with pytest.raises(ValueError, match="Latitude values"):
        load_course_locations(_write(tmp_path, [_row(latitude=latitude)]))


@pytest.mark.parametrize("longitude", [-180.01, 180.01, "not-a-number"])
def test_rejects_invalid_longitude(tmp_path: Path, longitude: object) -> None:
    with pytest.raises(ValueError, match="Longitude values"):
        load_course_locations(_write(tmp_path, [_row(longitude=longitude)]))


def test_nullable_coordinates_are_allowed(tmp_path: Path) -> None:
    frame = load_course_locations(
        _write(tmp_path, [_row(latitude=None, longitude=None)])
    )
    assert pd.isna(frame.loc[0, "latitude"])
    assert pd.isna(frame.loc[0, "longitude"])


def test_merge_is_many_to_one_and_preserves_unmatched_rows() -> None:
    races = pd.DataFrame(
        [
            {
                "candidate_course_label": "Ascot",
                "candidate_jurisdiction": "Great Britain",
                "race_id": 1,
            },
            {
                "candidate_course_label": "Unknown",
                "candidate_jurisdiction": "Nowhere",
                "race_id": 2,
            },
        ]
    )
    reference = pd.DataFrame([_row()])
    merged = merge_course_locations(races, reference)
    assert len(merged) == 2
    assert merged.loc[0, "iana_timezone"] == "Europe/London"
    assert pd.isna(merged.loc[1, "iana_timezone"])
