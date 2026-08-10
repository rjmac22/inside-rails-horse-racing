from __future__ import annotations

import sqlite3

from inside_rails.race_results import (
    ParsedResult,
    ResultKind,
    parse_result,
    profile_result_representation,
)


def test_positive_numeric_position_is_parsed() -> None:
    assert parse_result("12") == ParsedResult(
        "12", ResultKind.FINISH_POSITION, 12, None
    )


def test_numeric_storage_is_parsed_without_losing_raw_value() -> None:
    assert parse_result(1) == ParsedResult(
        1, ResultKind.FINISH_POSITION, 1, None
    )


def test_zero_is_preserved_as_sentinel_not_finish_position() -> None:
    assert parse_result("0") == ParsedResult(
        "0", ResultKind.ZERO_SENTINEL, None, "0"
    )


def test_disqualification_is_distinct() -> None:
    assert parse_result("dsq") == ParsedResult(
        "dsq", ResultKind.DISQUALIFIED, None, "DSQ"
    )


def test_non_finish_code_is_preserved() -> None:
    assert parse_result(" pu ") == ParsedResult(
        " pu ", ResultKind.NON_FINISH_OUTCOME, None, "PU"
    )


def test_blank_and_null_are_missing() -> None:
    assert parse_result("").result_kind is ResultKind.MISSING
    assert parse_result("   ").result_kind is ResultKind.MISSING
    assert parse_result(None).result_kind is ResultKind.MISSING


def test_unfamiliar_text_is_not_silently_rejected() -> None:
    parsed = parse_result("NEWCODE")
    assert parsed.result_kind is ResultKind.NON_FINISH_OUTCOME
    assert parsed.outcome_code == "NEWCODE"


def test_profile_partitions_every_source_row() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE data (pos TEXT)")
        connection.executemany(
            "INSERT INTO data VALUES (?)",
            [("pos",), ("1",), ("12",), ("0",), ("DSQ",), ("PU",), ("",)],
        )
        profile = profile_result_representation(connection)
    finally:
        connection.close()

    assert profile == {
        "data_rows": 6,
        "positive_numeric_position_rows": 2,
        "zero_position_rows": 1,
        "disqualified_rows": 1,
        "other_text_outcome_rows": 1,
        "missing_position_rows": 1,
    }
    assert sum(value for key, value in profile.items() if key != "data_rows") == 6
