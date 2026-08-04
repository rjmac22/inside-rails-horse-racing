from inside_rails.comment_information import (
    PROBABLE_PLACEHOLDERS,
    UNRESOLVED_SOURCE_CODES,
    classify_comment,
    is_comment_analytically_available,
)


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
