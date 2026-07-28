from datetime import date

import pytest

from inside_rails.jurisdiction_context import (
    CONTEXTS,
    JurisdictionContext,
    OBSERVED_SOURCE_TYPES,
    resolve_jurisdiction_context,
    validate_context_reference,
)


def test_reference_contains_bounded_worked_examples() -> None:
    assert len(CONTEXTS) == 16
    assert {row.jurisdiction for row in CONTEXTS} == {
        "Great Britain",
        "Ireland",
        "France",
    }


def test_all_worked_jurisdictions_cover_observed_source_types() -> None:
    for jurisdiction in ("Great Britain", "France"):
        assert {
            row.source_type for row in CONTEXTS if row.jurisdiction == jurisdiction
        } == set(OBSERVED_SOURCE_TYPES)


def test_great_britain_resolves_one_authority_per_source_type() -> None:
    for source_type in OBSERVED_SOURCE_TYPES:
        row = resolve_jurisdiction_context(
            "Great Britain", source_type, date(2026, 1, 1)
        )
        assert row is not None
        assert row.regulatory_authority == "British Horseracing Authority"
        assert row.native_code_status == "source_type_retained"


def test_ireland_authority_changes_at_2018_boundary() -> None:
    old = resolve_jurisdiction_context("Ireland", "Flat", date(2017, 12, 31))
    new = resolve_jurisdiction_context("Ireland", "Flat", date(2018, 1, 1))
    assert old is not None and new is not None
    assert old.regulatory_authority == "Irish Turf Club"
    assert new.regulatory_authority == "Irish Horseracing Regulatory Board"
    assert old.administrative_body == "Horse Racing Ireland"
    assert new.administrative_body == "Horse Racing Ireland"


def test_ireland_has_eight_period_type_context_units() -> None:
    assert sum(row.jurisdiction == "Ireland" for row in CONTEXTS) == 8


def test_france_nh_flat_remains_explicitly_unresolved() -> None:
    row = resolve_jurisdiction_context("France", "NH Flat", date(2020, 1, 1))
    assert row is not None
    assert row.regulatory_authority == "France Galop"
    assert row.native_code_status == "unresolved_aqps_source_classification"


def test_wagering_context_is_not_invented() -> None:
    assert all(row.wagering_context_status == "unresolved" for row in CONTEXTS)


def test_unresearched_jurisdiction_returns_none() -> None:
    assert (
        resolve_jurisdiction_context("United States", "Flat", date(2020, 1, 1))
        is None
    )


def test_unknown_source_type_returns_none() -> None:
    assert (
        resolve_jurisdiction_context("Great Britain", "Trot", date(2020, 1, 1))
        is None
    )


def test_validator_rejects_overlapping_periods() -> None:
    duplicate = JurisdictionContext(
        jurisdiction="Ireland",
        source_type="Flat",
        effective_from=date(2017, 1, 1),
        effective_to=date(2018, 12, 31),
        regulatory_authority="Example",
        administrative_body=None,
        native_code_status="source_type_retained",
        wagering_context_status="unresolved",
        evidence_scope="test",
    )
    with pytest.raises(ValueError, match="Overlapping context periods"):
        validate_context_reference((*CONTEXTS, duplicate))


def test_validator_rejects_invalid_effective_period() -> None:
    invalid = JurisdictionContext(
        jurisdiction="Example",
        source_type="Flat",
        effective_from=date(2020, 1, 2),
        effective_to=date(2020, 1, 1),
        regulatory_authority="Example Authority",
        administrative_body=None,
        native_code_status="source_type_retained",
        wagering_context_status="unresolved",
        evidence_scope="test",
    )
    with pytest.raises(ValueError, match="Invalid effective period"):
        validate_context_reference((invalid,))
