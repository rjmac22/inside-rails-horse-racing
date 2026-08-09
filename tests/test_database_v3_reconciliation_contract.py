from __future__ import annotations

import csv
from pathlib import Path

from inside_rails.database.external_reconciliation import (
    EXPECTED_NEW_MANUAL_VERIFICATIONS,
    EXPECTED_RESOLUTIONS,
    EXPECTED_TOTAL_MANUAL_VERIFICATIONS,
)
from inside_rails.database.external_reconciliation_candidate import (
    EXPECTED_BASE_RELEASE_SHA256,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_v3_is_bound_to_exact_accepted_v2_hash() -> None:
    assert (
        EXPECTED_BASE_RELEASE_SHA256.hex()
        == "80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe"
    )


def test_missing_external_evidence_register_has_exact_19_rows() -> None:
    rows = _rows("data/reference/external_verification_reconciliation.csv")
    assert len(rows) == EXPECTED_NEW_MANUAL_VERIFICATIONS == 19
    assert len({row["verification_id"] for row in rows}) == 19
    assert EXPECTED_TOTAL_MANUAL_VERIFICATIONS == 104
    assert {row["governing_notebook"] for row in rows} == {"5", "6", "8", "11", "13"}


def test_typed_resolution_register_has_exact_37_rows() -> None:
    rows = _rows("data/reference/external_value_resolutions.csv")
    assert len(rows) == EXPECTED_RESOLUTIONS == 37
    assert len({row["resolution_id"] for row in rows}) == 37
    assert {row["resolution_kind"] for row in rows} == {
        "correction",
        "enrichment",
        "invalidation",
    }


def test_almendares_is_exact_5_to_2_favourite_correction() -> None:
    rows = _rows("data/reference/external_value_resolutions.csv")
    row = next(item for item in rows if item["resolution_id"] == "V3-RES-0004")
    assert row["verification_id"] == "NB08-SP-0004"
    assert row["source_rowid"] == "1708860"
    assert row["source_horse"] == "Almendares (GB)"
    assert row["source_field"] == "sp"
    assert row["governed_numerator"] == "5"
    assert row["governed_denominator"] == "2"
    assert row["governed_marker"] == "favourite"
    assert row["analytical_action"] == "replace"


def test_known_wrong_beaten_distances_do_not_invent_numeric_replacements() -> None:
    rows = _rows("data/reference/external_value_resolutions.csv")
    invalidations = [row for row in rows if row["resolution_kind"] == "invalidation"]
    assert len(invalidations) == 5
    assert all(row["governed_real_value"] == "" for row in invalidations)
    assert all(row["analytical_action"] == "null_known_wrong" for row in invalidations)


def test_external_prize_schedules_are_enrichment_not_source_overwrite() -> None:
    rows = _rows("data/reference/external_value_resolutions.csv")
    prize_rows = [row for row in rows if row["source_field"] == "prize"]
    assert len(prize_rows) == 17
    assert {row["governed_currency"] for row in prize_rows} == {"USD", "EUR"}
    assert all(row["resolution_kind"] == "enrichment" for row in prize_rows)
    assert all(row["analytical_action"] == "enrich_official_local_prize" for row in prize_rows)
