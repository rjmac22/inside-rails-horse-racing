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


def test_later_closed_fields_are_reconciled() -> None:
    assert FIELD_GOVERNANCE_BY_NAME["prize"].status == "closed"
    assert FIELD_GOVERNANCE_BY_NAME["prize"].governing_notebook == "13"
    assert FIELD_GOVERNANCE_BY_NAME["ran"].status == "closed"
    assert FIELD_GOVERNANCE_BY_NAME["ran"].governing_notebook == "14"
    assert FIELD_GOVERNANCE_BY_NAME["num"].status == "closed"
    assert FIELD_GOVERNANCE_BY_NAME["num"].governing_notebook == "14"
    assert FIELD_GOVERNANCE_BY_NAME["off"].governing_notebook == "11"


def test_source_fields_remain_raw_even_when_derived() -> None:
    for field in ("dist", "wgt", "pos", "sp", "prize", "ran", "num"):
        assert FIELD_GOVERNANCE_BY_NAME[field].treatment == "deterministic_parsing"


def test_open_semantic_fields_are_not_falsely_closed() -> None:
    for field in ("class", "going", "btn", "or", "horse", "jockey", "comment"):
        assert FIELD_GOVERNANCE_BY_NAME[field].status == "open"


def test_comment_is_governed_as_raw_free_text() -> None:
    row = FIELD_GOVERNANCE_BY_NAME["comment"]
    assert row.family == "free_text"
    assert row.treatment == "raw_free_text"
