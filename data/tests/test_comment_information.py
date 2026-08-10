import csv
from pathlib import Path

from inside_rails.comment_information import (
    PROBABLE_PLACEHOLDERS,
    UNRESOLVED_SOURCE_CODES,
    classify_comment,
    is_comment_analytically_available,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_empty_string_is_preserved_source_absence() -> None:
    governed = classify_comment("")
    assert governed.raw_comment == ""
    assert governed.comment_state == "empty_string"
    assert governed.substantive_text is None


def test_unexpected_null_is_not_silently_converted_to_empty() -> None:
    governed = classify_comment(None)
    assert governed.raw_comment is None
    assert governed.comment_state == "unexpected_null"
    assert governed.substantive_text is None


def test_probable_placeholders_are_preserved_without_interpretation() -> None:
    for raw_value in PROBABLE_PLACEHOLDERS:
        governed = classify_comment(raw_value)
        assert governed.raw_comment == raw_value
        assert governed.comment_state == "probable_placeholder"
        assert governed.substantive_text is None


def test_unresolved_source_codes_are_preserved_without_guessing() -> None:
    for raw_value in UNRESOLVED_SOURCE_CODES:
        governed = classify_comment(raw_value)
        assert governed.raw_comment == raw_value
        assert governed.comment_state == "unresolved_source_code"
        assert governed.substantive_text is None


def test_substantive_comment_is_returned_exactly() -> None:
    raw_value = "Held up - ridden 2f out - stayed on(op 5/1)"
    governed = classify_comment(raw_value)
    assert governed.raw_comment == raw_value
    assert governed.comment_state == "substantive_text"
    assert governed.substantive_text == raw_value
    assert is_comment_analytically_available(raw_value)


def test_leading_whitespace_is_not_trimmed() -> None:
    raw_value = " Held up - weakened"
    governed = classify_comment(raw_value)
    assert governed.raw_comment == raw_value
    assert governed.substantive_text == raw_value


def test_unlisted_short_text_remains_substantive() -> None:
    governed = classify_comment("Led")
    assert governed.comment_state == "substantive_text"
    assert governed.substantive_text == "Led"


def test_persisted_notebook_21_outputs_reload_with_expected_baselines() -> None:
    profile_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "comment_information"
        / "comment_source_profile.csv"
    )
    decisions_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "comment_information"
        / "comment_semantic_decisions.csv"
    )

    with profile_path.open(newline="", encoding="utf-8") as handle:
        profile = {row["measure"]: row["value"] for row in csv.DictReader(handle)}
    with decisions_path.open(newline="", encoding="utf-8") as handle:
        decisions = tuple(csv.DictReader(handle))

    assert profile["governed_runner_rows"] == "1851285"
    assert profile["provisional_races"] == "189043"
    assert profile["empty_string_rows"] == "340394"
    assert profile["probable_placeholder_or_unresolved_code_rows"] == "238"
    assert profile["substantive_text_rows"] == "1510653"
    assert len(decisions) == 11
    assert {row["status"] for row in decisions} == {"Confirmed", "Required", "Deferred"}
