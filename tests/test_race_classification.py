from inside_rails.race_classification import (
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)


def test_class_parser_accepts_canonical_class_value() -> None:
    result = parse_class("Class 3")

    assert result["class_raw"] == "Class 3"
    assert result["class_number"] == 3
    assert result["class_parse_status"] == "canonical"


def test_class_parser_preserves_blank_and_rejects_noncanonical_values() -> None:
    blank = parse_class("")
    noncanonical = parse_class("Grade 1")

    assert blank["class_number"] is None
    assert blank["class_parse_status"] == "blank"
    assert noncanonical["class_number"] is None
    assert noncanonical["class_parse_status"] == "unrecognised"


def test_pattern_parser_keeps_group_and_grade_distinct() -> None:
    group = parse_pattern("Group 1")
    grade = parse_pattern("Grade 1")

    assert group["pattern_family"] == "Group"
    assert group["pattern_level_raw"] == "1"
    assert grade["pattern_family"] == "Grade"
    assert grade["pattern_level_raw"] == "1"
    assert group["pattern_family"] != grade["pattern_family"]


def test_pattern_parser_preserves_listed_as_its_own_family() -> None:
    result = parse_pattern("Listed")

    assert result["pattern_family"] == "Listed"
    assert result["pattern_level_raw"] is None
    assert result["pattern_parse_status"] == "canonical"


def test_rating_band_parser_accepts_only_exact_closed_integer_ranges() -> None:
    result = parse_rating_band("75-100")

    assert result["rating_lower_bound"] == 75
    assert result["rating_upper_bound"] == 100
    assert result["rating_band_parse_status"] == "canonical"


def test_rating_band_parser_leaves_known_unresolved_forms_unparsed() -> None:
    dash = parse_rating_band("--")
    parenthesised = parse_rating_band("(75-100)")

    assert dash["rating_lower_bound"] is None
    assert dash["rating_band_parse_status"] == "unrecognised_source_form"
    assert parenthesised["rating_lower_bound"] is None
    assert parenthesised["rating_band_parse_status"] == "unrecognised_source_form"


def test_rating_band_parser_rejects_reversed_bounds() -> None:
    result = parse_rating_band("100-75")

    assert result["rating_lower_bound"] is None
    assert result["rating_upper_bound"] is None
    assert result["rating_band_parse_status"] == "invalid_range_order"


def test_age_band_parser_handles_exact_age_without_claiming_eligibility() -> None:
    result = parse_age_band("5yo")

    assert result["stated_minimum_age"] == 5
    assert result["stated_maximum_age"] == 5
    assert result["age_band_open_ended"] is False
    assert result["age_band_syntax"] == "exact_age"
    assert result["age_band_interpretation_status"] == "source_stated_bounds_only"


def test_age_band_parser_handles_open_ended_minimum() -> None:
    result = parse_age_band("5yo+")

    assert result["stated_minimum_age"] == 5
    assert result["stated_maximum_age"] is None
    assert result["age_band_open_ended"] is True
    assert result["age_band_syntax"] == "open_ended_minimum"


def test_age_band_parser_handles_closed_range() -> None:
    result = parse_age_band("3-5yo")

    assert result["stated_minimum_age"] == 3
    assert result["stated_maximum_age"] == 5
    assert result["age_band_open_ended"] is False
    assert result["age_band_syntax"] == "closed_age_range"


def test_age_band_parser_preserves_unresolved_and_invalid_forms() -> None:
    reversed_range = parse_age_band("5-3yo")
    unrecognised = parse_age_band("All ages")

    assert reversed_range["age_band_syntax"] == "invalid_range_order"
    assert reversed_range["age_band_interpretation_status"] == "unresolved"
    assert unrecognised["stated_minimum_age"] is None
    assert unrecognised["age_band_syntax"] == "unrecognised"
    assert unrecognised["age_band_interpretation_status"] == "unresolved"


def test_sex_restriction_marks_explicit_combined_categories() -> None:
    result = classify_sex_restriction("C & F")

    assert result["sex_rest_raw"] == "C & F"
    assert result["sex_rest_category"] == "C & F"
    assert result["sex_rest_interpretation_status"] == "explicit_source_category"


def test_sex_restriction_marks_f_as_overloaded_not_fillies_only() -> None:
    result = classify_sex_restriction("F")

    assert result["sex_rest_category"] == "F"
    assert result["sex_rest_interpretation_status"] == "overloaded_source_category"
    assert "permitted_fillies" not in result
    assert "permitted_colts" not in result


def test_sex_restriction_blank_does_not_mean_unrestricted() -> None:
    result = classify_sex_restriction("")

    assert result["sex_rest_category"] is None
    assert result["sex_rest_interpretation_status"] == "blank"
    assert "unrestricted" not in result.values()


def test_non_string_values_are_not_silently_coerced() -> None:
    class_result = parse_class(3)
    pattern_result = parse_pattern(1)
    rating_result = parse_rating_band(100)
    age_result = parse_age_band(5)

    assert class_result["class_parse_status"] == "unrecognised"
    assert pattern_result["pattern_parse_status"] == "unrecognised"
    assert rating_result["rating_band_parse_status"] == "unrecognised_source_form"
    assert age_result["age_band_interpretation_status"] == "unresolved"
