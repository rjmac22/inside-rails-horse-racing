from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from inside_rails.course_locations import (
    IDENTITY_COLUMNS,
    REQUIRED_COLUMNS,
    derive_source_course_identities,
    load_course_locations,
    merge_course_locations,
    merge_source_course_locations,
    unmatched_source_course_locations,
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


def _source_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "course": "Ascot",
        "date": "2024-06-20",
        "type": "Flat",
        "race_name": "Example Stakes",
        "race_id": 1,
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


@pytest.mark.parametrize(
    ("course", "jurisdiction", "timezone"),
    [
        ("Bordeaux Le Bouscat", "France", "Europe/Paris"),
        ("Chukyo", "Japan", "Asia/Tokyo"),
        ("Cidade Jardim", "Brazil", "America/Sao_Paulo"),
        ("Hipodromo Chile", "Chile", "America/Santiago"),
        ("Les Landes", "Jersey", "Europe/Jersey"),
        ("Monterrico", "Peru", "America/Lima"),
        ("Nakayama", "Japan", "Asia/Tokyo"),
    ],
)
def test_unsuffixed_historical_labels_resolve_through_canonical_identity(
    course: str,
    jurisdiction: str,
    timezone: str,
) -> None:
    source = pd.DataFrame([_source_row(course=course)])
    reference = pd.DataFrame(
        [
            _row(
                candidate_course_label=course,
                candidate_jurisdiction=jurisdiction,
                iana_timezone=timezone,
            )
        ]
    )

    merged = merge_source_course_locations(
        source,
        reference,
        require_all_matches=True,
    )

    assert merged.loc[0, "course"] == course
    assert merged.loc[0, "candidate_course_label"] == course
    assert merged.loc[0, "candidate_jurisdiction"] == jurisdiction
    assert merged.loc[0, "iana_timezone"] == timezone
    assert merged.loc[0, "course_location_match_status"] == "both"


def test_source_identity_derivation_preserves_raw_course_text() -> None:
    source = pd.DataFrame([_source_row(course="Chukyo (JPN)")])
    derived = derive_source_course_identities(source)

    assert derived.loc[0, "course"] == "Chukyo (JPN)"
    assert derived.loc[0, "candidate_course_label"] == "Chukyo"
    assert derived.loc[0, "candidate_jurisdiction"] == "Japan"


def test_unmatched_source_residue_is_explicit() -> None:
    source = pd.DataFrame([_source_row(course="Unknown Course")])
    merged = merge_source_course_locations(source, pd.DataFrame([_row()]))
    unmatched = unmatched_source_course_locations(merged)

    assert unmatched.to_dict("records") == [
        {
            "course": "Unknown Course",
            "candidate_course_label": "Unknown Course",
            "candidate_jurisdiction": "unresolved",
        }
    ]


def test_strict_source_join_rejects_zero_matches() -> None:
    source = pd.DataFrame([_source_row(course="Unknown Course")])

    with pytest.raises(ValueError, match="Unmatched governed course identities"):
        merge_source_course_locations(
            source,
            pd.DataFrame([_row()]),
            require_all_matches=True,
        )


def test_source_join_rejects_multiple_reference_matches() -> None:
    source = pd.DataFrame([_source_row()])
    duplicate_reference = pd.DataFrame([_row(), _row()])

    with pytest.raises(pd.errors.MergeError):
        merge_source_course_locations(source, duplicate_reference)
