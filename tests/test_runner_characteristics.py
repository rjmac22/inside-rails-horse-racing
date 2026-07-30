from inside_rails.runner_characteristics import (
    normalise_runner_age,
    normalise_runner_sex,
    parse_runner_headgear,
)


def test_runner_age_preserves_integer_value() -> None:
    assert normalise_runner_age(7) == {
        "raw_age": 7,
        "normalised_age": 7,
        "interpretation_status": "source_recorded_integer",
    }


def test_runner_age_rejects_bool_and_non_integer() -> None:
    assert normalise_runner_age(True)["interpretation_status"] == "unresolved"
    assert normalise_runner_age("7")["interpretation_status"] == "unresolved"
    assert normalise_runner_age(None)["interpretation_status"] == "unresolved"


def test_common_runner_sex_codes_are_normalised() -> None:
    expected = {
        "C": "colt",
        "F": "filly",
        "G": "gelding",
        "H": "horse",
        "M": "mare",
        "R": "rig",
    }
    for raw_value, normalised_value in expected.items():
        result = normalise_runner_sex(raw_value)
        assert result["normalised_sex"] == normalised_value
        assert result["interpretation_status"] == "verified_common_code"
        assert result["verification_id"] == "NB17-SEX-0001"


def test_source_sex_anomalies_require_exact_verification_id() -> None:
    assert normalise_runner_sex("B")["interpretation_status"] == "unresolved"
    assert normalise_runner_sex("BB")["interpretation_status"] == "unresolved"
    assert (
        normalise_runner_sex("B", verification_id="NB17-SEX-0002")[
            "interpretation_status"
        ]
        == "unresolved"
    )
    assert (
        normalise_runner_sex("B", verification_id="NB17-SEX-0003")[
            "normalised_sex"
        ]
        == "filly"
    )
    assert (
        normalise_runner_sex("BB", verification_id="NB17-SEX-0002")[
            "normalised_sex"
        ]
        == "gelding"
    )


def test_unknown_or_malformed_runner_sex_remains_unresolved() -> None:
    for raw_value in (None, "", "X", 1):
        assert normalise_runner_sex(raw_value)["interpretation_status"] == "unresolved"


def test_blank_headgear_means_field_not_supplied() -> None:
    for raw_value in (None, ""):
        result = parse_runner_headgear(raw_value)
        assert result["interpretation_status"] == "blank_field_not_supplied"
        assert result["normalised_components"] == []
        assert result["source_declared_first_time"] is False


def test_headgear_components_preserve_source_order() -> None:
    result = parse_runner_headgear("hct")
    assert result["raw_components"] == ["h", "c", "t"]
    assert result["normalised_components"] == [
        "hood",
        "eyecover",
        "tongue_tie",
    ]
    assert result["component_count"] == 3
    assert result["interpretation_status"] == "fully_decomposed_source_code"


def test_headgear_slash_tokens_are_not_split() -> None:
    result = parse_runner_headgear("e/sp")
    assert result["raw_components"] == ["e/s", "p"]
    assert result["normalised_components"] == ["eyeshield", "cheekpieces"]


def test_trailing_one_is_preserved_as_source_declaration() -> None:
    result = parse_runner_headgear("tp1")
    assert result["normalised_components"] == ["tongue_tie", "cheekpieces"]
    assert result["use_suffix"] == "1"
    assert result["source_declared_first_time"] is True


def test_unseen_suffix_and_malformed_values_remain_unresolved() -> None:
    for raw_value in ("b2", "1", "x", 17):
        result = parse_runner_headgear(raw_value)
        assert result["interpretation_status"] == "unresolved"
        assert result["normalised_components"] == []
