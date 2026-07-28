import pytest

from inside_rails.runner_entries import parse_runner_number, profile_reported_ran


def test_positive_runner_number_is_canonicalised() -> None:
    result = parse_runner_number(7, within_race_multiplicity=1)

    assert result["source_num_storage_class"] == "integer"
    assert result["source_positive_runner_number"] == 7
    assert result["source_num_state"] == "positive_integer"
    assert result["source_num_within_race_multiplicity"] == 1
    assert result["source_num_uniqueness_status"] == "unique_within_race"


def test_shared_positive_runner_number_is_allowed() -> None:
    result = parse_runner_number(1, within_race_multiplicity=3)

    assert result["source_positive_runner_number"] == 1
    assert result["source_num_within_race_multiplicity"] == 3
    assert result["source_num_uniqueness_status"] == "shared_positive_num"


def test_positive_runner_number_can_remain_unassessed() -> None:
    result = parse_runner_number(4)

    assert result["source_positive_runner_number"] == 4
    assert result["source_num_within_race_multiplicity"] is None
    assert result["source_num_uniqueness_status"] == "unassessed"


def test_integer_zero_remains_distinct_and_is_not_canonicalised() -> None:
    result = parse_runner_number(0)

    assert result["source_num_storage_class"] == "integer"
    assert result["source_positive_runner_number"] is None
    assert result["source_num_state"] == "integer_zero"
    assert result["source_num_uniqueness_status"] == "nonpositive_state"


def test_blank_text_remains_distinct_and_is_not_canonicalised() -> None:
    result = parse_runner_number("   ")

    assert result["source_num_storage_class"] == "text"
    assert result["source_positive_runner_number"] is None
    assert result["source_num_state"] == "blank_text"
    assert result["source_num_uniqueness_status"] == "nonpositive_state"


def test_null_is_explicitly_preserved_for_future_source_changes() -> None:
    result = parse_runner_number(None)

    assert result["source_num_storage_class"] == "null"
    assert result["source_num_state"] == "null"
    assert result["source_positive_runner_number"] is None


def test_populated_text_is_invalid_not_reconstructed() -> None:
    result = parse_runner_number("1A")

    assert result["source_num_storage_class"] == "text"
    assert result["source_num_state"] == "invalid"
    assert result["source_positive_runner_number"] is None


def test_negative_integer_is_invalid() -> None:
    result = parse_runner_number(-1)

    assert result["source_num_state"] == "invalid"
    assert result["source_positive_runner_number"] is None


def test_boolean_is_not_treated_as_integer_runner_number() -> None:
    result = parse_runner_number(True)

    assert result["source_num_storage_class"] == "invalid"
    assert result["source_num_state"] == "invalid"
    assert result["source_positive_runner_number"] is None


def test_runner_number_multiplicity_must_be_positive_integer() -> None:
    with pytest.raises(TypeError):
        parse_runner_number(2, within_race_multiplicity=1.5)

    with pytest.raises(TypeError):
        parse_runner_number(2, within_race_multiplicity=True)

    with pytest.raises(ValueError):
        parse_runner_number(2, within_race_multiplicity=0)


def test_consistent_ran_equal_to_row_count_is_only_internally_equal() -> None:
    result = profile_reported_ran([8] * 8)

    assert result["source_reported_ran"] == 8
    assert result["source_runner_row_count"] == 8
    assert result["source_ran_distinct_value_count"] == 1
    assert result["source_ran_consistency_status"] == "consistent"
    assert result["source_row_count_vs_ran_status"] == "equal"
    assert result["source_runner_coverage_status"] == "internally_equal_to_ran"
    assert result["source_ran_external_status"] == "unverified"


def test_consistent_ran_above_stored_rows_is_known_partial() -> None:
    result = profile_reported_ran([8] * 7)

    assert result["source_reported_ran"] == 8
    assert result["source_runner_row_count"] == 7
    assert result["source_row_count_vs_ran_status"] == "below"
    assert result["source_runner_coverage_status"] == "known_partial"


def test_consistent_ran_can_have_more_rows_than_reported() -> None:
    result = profile_reported_ran([4] * 5)

    assert result["source_reported_ran"] == 4
    assert result["source_row_count_vs_ran_status"] == "above"
    assert result["source_runner_coverage_status"] == "unverified"


def test_conflicting_ran_values_are_not_comparable() -> None:
    result = profile_reported_ran([7, 8, 7])

    assert result["source_reported_ran"] is None
    assert result["source_ran_distinct_value_count"] == 2
    assert result["source_ran_consistency_status"] == "conflicting"
    assert result["source_row_count_vs_ran_status"] == "not_comparable"
    assert result["source_runner_coverage_status"] == "unverified"


def test_invalid_ran_value_prevents_consistent_classification() -> None:
    result = profile_reported_ran([8, 8, None])

    assert result["source_reported_ran"] == 8
    assert result["source_ran_consistency_status"] == "invalid"
    assert result["source_row_count_vs_ran_status"] == "not_comparable"


def test_ran_must_be_inside_observed_governed_range() -> None:
    assert profile_reported_ran([0])["source_ran_consistency_status"] == "invalid"
    assert profile_reported_ran([41])["source_ran_consistency_status"] == "invalid"


def test_empty_ran_population_is_missing() -> None:
    result = profile_reported_ran([])

    assert result["source_reported_ran"] is None
    assert result["source_runner_row_count"] == 0
    assert result["source_ran_consistency_status"] == "missing"
    assert result["source_row_count_vs_ran_status"] == "not_comparable"


def test_external_status_can_be_recorded_without_changing_internal_result() -> None:
    result = profile_reported_ran(
        [5] * 5,
        source_runner_coverage_status="known_partial",
        source_ran_external_status="externally_contradicted",
    )

    assert result["source_row_count_vs_ran_status"] == "equal"
    assert result["source_runner_coverage_status"] == "known_partial"
    assert result["source_ran_external_status"] == "externally_contradicted"


def test_unsupported_external_statuses_are_rejected() -> None:
    with pytest.raises(ValueError):
        profile_reported_ran([5] * 5, source_runner_coverage_status="complete")

    with pytest.raises(ValueError):
        profile_reported_ran([5] * 5, source_ran_external_status="correct")


def test_runner_row_count_must_be_nonnegative_integer() -> None:
    with pytest.raises(TypeError):
        profile_reported_ran([5], source_runner_row_count=1.0)

    with pytest.raises(TypeError):
        profile_reported_ran([5], source_runner_row_count=True)

    with pytest.raises(ValueError):
        profile_reported_ran([5], source_runner_row_count=-1)
