from __future__ import annotations

import math
import struct

import pytest

from inside_rails.database.fingerprints import (
    ROW_FINGERPRINT_DOMAIN,
    canonical_raceform_v1_row_message,
    encode_sqlite_value,
    raceform_v1_row_sha256,
)


def row_with(*values: object) -> list[object]:
    return [*values, *([None] * (37 - len(values)))]


def test_per_value_encoding_uses_big_endian_ordinal_marker_and_length() -> None:
    encoded = encode_sqlite_value(5, -2)
    assert encoded[:2] == b"\x00\x05"
    assert encoded[2] == 0x01
    assert encoded[3:11] == (8).to_bytes(8, "big")
    assert encoded[11:] == (-2).to_bytes(8, "big", signed=True)


def test_canonical_message_covers_all_sqlite_storage_classes() -> None:
    values = row_with(None, -7, -0.0, "Caf\u00e9 \U0001f3c7", b"\x00\xff", "")
    message = canonical_raceform_v1_row_message(values)

    assert message.startswith(ROW_FINGERPRINT_DOMAIN)
    assert len(raceform_v1_row_sha256(values)) == 32
    assert raceform_v1_row_sha256(values).hex() == (
        "46c28d090c833e8941ea1eb54321fcea9abe2f00894680b56047fc705ea98d36"
    )


def test_storage_class_and_ordinal_are_part_of_the_fingerprint() -> None:
    fingerprints = {
        raceform_v1_row_sha256(row_with(1)),
        raceform_v1_row_sha256(row_with(1.0)),
        raceform_v1_row_sha256(row_with("1")),
        raceform_v1_row_sha256(row_with(b"1")),
    }
    assert len(fingerprints) == 4

    assert raceform_v1_row_sha256(row_with("a", "b")) != raceform_v1_row_sha256(
        row_with("b", "a")
    )


def test_negative_zero_is_retained_as_ieee_754_binary64() -> None:
    encoded = encode_sqlite_value(0, -0.0)
    assert encoded[-8:] == struct.pack(">d", -0.0)
    assert math.copysign(1.0, struct.unpack(">d", encoded[-8:])[0]) == -1.0
    assert raceform_v1_row_sha256(row_with(-0.0)) != raceform_v1_row_sha256(row_with(0.0))


def test_fingerprint_validation_fails_closed() -> None:
    with pytest.raises(ValueError, match="Expected 37"):
        canonical_raceform_v1_row_message([None] * 36)
    with pytest.raises(ValueError, match="unsigned 16-bit"):
        encode_sqlite_value(-1, None)
    with pytest.raises(OverflowError, match="signed 64-bit"):
        encode_sqlite_value(0, 2**63)
    with pytest.raises(TypeError, match="Boolean"):
        encode_sqlite_value(0, True)
    with pytest.raises(TypeError, match="Unsupported"):
        encode_sqlite_value(0, bytearray(b"x"))
