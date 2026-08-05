from __future__ import annotations

import pytest

from inside_rails.database.identifiers import (
    governance_method_code,
    governance_release_code,
    order_race_groups_by_minimum_source_rowid,
    runner_participation_code,
    source_race_occurrence_code,
    source_record_code,
    source_relation_code,
    source_version_code,
)


SHA_HEX = "ab" * 32
SHA_BYTES = bytes.fromhex(SHA_HEX)
PREFIX = SHA_HEX[:24]


def test_deterministic_identifier_formats() -> None:
    assert source_version_code(SHA_HEX) == f"sv:{PREFIX}"
    assert source_version_code(SHA_BYTES) == f"sv:{PREFIX}"
    assert source_relation_code(SHA_HEX) == f"rel:{PREFIX}:data"
    assert source_record_code(SHA_HEX, 42) == f"rec:{PREFIX}:data:0000000042"
    assert source_race_occurrence_code(SHA_HEX, 17) == f"race:{PREFIX}:000000017"
    assert runner_participation_code(SHA_HEX, 42) == f"run:{PREFIX}:data:0000000042"
    assert governance_method_code("source-v1-structure", 2) == "gm:source-v1-structure:v2"
    assert (
        governance_release_code(SHA_HEX, "minimum-core", 3)
        == f"gr:{PREFIX}:minimum-core:v3"
    )


def test_source_record_and_runner_namespaces_remain_distinct() -> None:
    assert source_record_code(SHA_HEX, 2).replace("rec:", "", 1) == (
        runner_participation_code(SHA_HEX, 2).replace("run:", "", 1)
    )
    assert source_record_code(SHA_HEX, 2) != runner_participation_code(SHA_HEX, 2)


def test_race_sequences_use_minimum_source_rowid_not_mapping_order() -> None:
    first = order_race_groups_by_minimum_source_rowid(
        {("later",): 50, ("first",): 2, ("middle",): 17}
    )
    second = order_race_groups_by_minimum_source_rowid(
        {("middle",): 17, ("later",): 50, ("first",): 2}
    )

    assert first == second == {("first",): 1, ("middle",): 2, ("later",): 3}


def test_identifier_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="64 lowercase"):
        source_version_code(SHA_HEX.upper())
    with pytest.raises(ValueError, match="exactly 32"):
        source_version_code(b"short")
    with pytest.raises(ValueError, match="lowercase ASCII slug"):
        source_relation_code(SHA_HEX, "Data Table")
    with pytest.raises(ValueError, match="positive integer"):
        source_record_code(SHA_HEX, 0)
    with pytest.raises(ValueError, match="10-digit"):
        source_record_code(SHA_HEX, 10_000_000_000)
    with pytest.raises(ValueError, match="positive integer"):
        governance_method_code("method", True)


def test_race_sequence_assignment_rejects_invalid_or_duplicate_minima() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        order_race_groups_by_minimum_source_rowid({("race",): 0})
    with pytest.raises(ValueError, match="cannot share"):
        order_race_groups_by_minimum_source_rowid({("a",): 2, ("b",): 2})
