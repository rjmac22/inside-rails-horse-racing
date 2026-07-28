from pathlib import Path

import pytest

from inside_rails.manual_verifications import (
    ManualVerification,
    load_manual_verifications,
    validate_manual_verifications,
)

REGISTER = Path("data/reference/manual_verifications.csv")


def make_row(**overrides: str) -> ManualVerification:
    values = {
        "verification_id": "MV-0001",
        "subject_type": "race",
        "source_date": "2026-01-01",
        "source_course": "Example",
        "source_off": "14:30",
        "source_horse": "",
        "source_field": "ran",
        "raw_source_value": "10",
        "verification_question": "How many runners were officially recorded?",
        "verified_value": "10",
        "verification_status": "confirmed",
        "evidence_type": "official_result",
        "evidence_locator": "https://example.invalid/result",
        "evidence_accessed_date": "2026-07-29",
        "governing_notebook": "14",
        "confidence": "high",
        "notes": "Illustrative governed test row.",
        "database_action": "evidence_only",
    }
    values.update(overrides)
    return ManualVerification(**values)


def test_empty_governed_register_loads() -> None:
    assert load_manual_verifications(REGISTER) == ()


def test_valid_row_passes() -> None:
    assert validate_manual_verifications([make_row()])[0].verification_id == "MV-0001"


def test_duplicate_ids_fail() -> None:
    with pytest.raises(ValueError, match="duplicate verification_id"):
        validate_manual_verifications([make_row(), make_row()])


def test_invalid_status_fails() -> None:
    with pytest.raises(ValueError, match="invalid verification_status"):
        validate_manual_verifications([make_row(verification_status="maybe")])


def test_missing_evidence_fails() -> None:
    with pytest.raises(ValueError, match="evidence_type and evidence_locator"):
        validate_manual_verifications([make_row(evidence_locator="")])


def test_confirmed_row_requires_verified_value() -> None:
    with pytest.raises(ValueError, match="confirmed rows require verified_value"):
        validate_manual_verifications([make_row(verified_value="")])


def test_at_least_one_source_locator_is_required() -> None:
    with pytest.raises(ValueError, match="at least one source locator"):
        validate_manual_verifications(
            [
                make_row(
                    source_date="",
                    source_course="",
                    source_off="",
                    source_horse="",
                    source_field="",
                    raw_source_value="",
                )
            ]
        )


def test_dates_must_be_iso() -> None:
    with pytest.raises(ValueError, match="source_date must be ISO"):
        validate_manual_verifications([make_row(source_date="01/01/2026")])


def test_database_action_is_governed() -> None:
    with pytest.raises(ValueError, match="invalid database_action"):
        validate_manual_verifications([make_row(database_action="overwrite_source")])
