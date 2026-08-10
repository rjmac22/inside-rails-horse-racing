from inside_rails.field_governance import (
    FIELD_GOVERNANCE,
    FIELD_GOVERNANCE_BY_NAME,
    SOURCE_FIELDS,
    validate_field_governance,
)


def test_register_validates() -> None:
    validate_field_governance()


def test_all_37_source_fields_are_governed_once() -> None:
    assert len(SOURCE_FIELDS) == 37
    assert len(FIELD_GOVERNANCE) == 37
    assert len(FIELD_GOVERNANCE_BY_NAME) == 37
    assert set(FIELD_GOVERNANCE_BY_NAME) == set(SOURCE_FIELDS)


def test_every_field_has_complete_governance() -> None:
    for row in FIELD_GOVERNANCE:
        assert row.family
        assert row.investigation_group
        assert row.treatment
        assert row.governing_notebook
        assert row.status


def test_notebook_10_groups_are_retained() -> None:
    groups = {row.investigation_group for row in FIELD_GOVERNANCE}
    assert {
        "off_time_and_temporal_semantics",
        "runner_counts_numbers_and_entries",
        "beaten_distance_semantics",
        "race_classification_and_eligibility",
        "runner_characteristics_and_equipment",
        "prize_and_currency_semantics",
        "race_time_semantics",
        "ratings_semantics_and_availability",
        "horse_and_pedigree_identity",
        "connections_and_owner_identity",
        "comment_and_embedded_information",
    }.issubset(groups)


def test_completed_source_field_series_is_reconciled() -> None:
    assert {row.status for row in FIELD_GOVERNANCE} == {
        "closed",
        "preserve",
        "implemented_with_governed_anomaly",
    }
    assert sum(row.status == "closed" for row in FIELD_GOVERNANCE) == 34
    assert sum(row.status == "preserve" for row in FIELD_GOVERNANCE) == 2
    assert sum(
        row.status == "implemented_with_governed_anomaly"
        for row in FIELD_GOVERNANCE
    ) == 1


def test_later_notebooks_are_recorded_as_governing_artifacts() -> None:
    expected = {
        "off": "11",
        "prize": "13",
        "ran": "14",
        "num": "14",
        "btn": "15",
        "class": "16",
        "age": "17",
        "or": "18",
        "horse": "19",
        "jockey": "20",
        "comment": "21",
    }
    for field, notebook in expected.items():
        row = FIELD_GOVERNANCE_BY_NAME[field]
        assert row.governing_notebook == notebook
        assert row.status == "closed"


def test_source_fields_remain_raw_even_when_derived() -> None:
    for field in ("dist", "wgt", "pos", "sp", "prize"):
        assert FIELD_GOVERNANCE_BY_NAME[field].treatment == "deterministic_parsing"

    assert FIELD_GOVERNANCE_BY_NAME["ran"].treatment == "governed_semantic_profile"
    assert FIELD_GOVERNANCE_BY_NAME["num"].treatment == "raw_plus_governed_derivation"
    assert FIELD_GOVERNANCE_BY_NAME["comment"].treatment == "raw_free_text"


def test_preserved_fields_are_explicit() -> None:
    preserved = {
        row.field for row in FIELD_GOVERNANCE if row.status == "preserve"
    }
    assert preserved == {"race_name", "draw"}


def test_starting_price_anomaly_remains_explicit() -> None:
    row = FIELD_GOVERNANCE_BY_NAME["sp"]
    assert row.status == "implemented_with_governed_anomaly"
    assert row.governing_notebook == "08/09"


def test_comment_is_governed_as_raw_free_text() -> None:
    row = FIELD_GOVERNANCE_BY_NAME["comment"]
    assert row.family == "free_text"
    assert row.treatment == "raw_free_text"
    assert row.governing_notebook == "21"
    assert row.status == "closed"
