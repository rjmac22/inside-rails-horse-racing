"""Canonical typed SHA-256 fingerprints for Source Version 1 raw rows."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Sequence

ROW_FINGERPRINT_DOMAIN = b"inside-rails:raceform-v1-row:v1\0"
SOURCE_FIELD_COUNT = 37
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1


def encode_sqlite_value(ordinal: int, value: object) -> bytes:
    """Encode one SQLite logical value with ordinal, type marker and length."""

    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or not 0 <= ordinal <= 0xFFFF:
        raise ValueError("ordinal must fit an unsigned 16-bit integer")

    if value is None:
        marker = 0x00
        value_bytes = b""
    elif isinstance(value, bool):
        raise TypeError("Boolean values are not an independent SQLite storage class")
    elif isinstance(value, int):
        if not _INT64_MIN <= value <= _INT64_MAX:
            raise OverflowError("SQLite INTEGER fingerprint values must fit signed 64-bit")
        marker = 0x01
        value_bytes = value.to_bytes(8, byteorder="big", signed=True)
    elif isinstance(value, float):
        marker = 0x02
        value_bytes = struct.pack(">d", value)
    elif isinstance(value, str):
        marker = 0x03
        value_bytes = value.encode("utf-8")
    elif isinstance(value, bytes):
        marker = 0x04
        value_bytes = value
    else:
        raise TypeError(f"Unsupported SQLite fingerprint value type: {type(value).__name__}")

    return (
        ordinal.to_bytes(2, byteorder="big", signed=False)
        + bytes((marker,))
        + len(value_bytes).to_bytes(8, byteorder="big", signed=False)
        + value_bytes
    )


def canonical_raceform_v1_row_message(values: Sequence[object]) -> bytes:
    """Return the canonical binary message for exactly 37 raw source values."""

    if len(values) != SOURCE_FIELD_COUNT:
        raise ValueError(f"Expected {SOURCE_FIELD_COUNT} raw values; received {len(values)}")
    return ROW_FINGERPRINT_DOMAIN + b"".join(
        encode_sqlite_value(ordinal, value) for ordinal, value in enumerate(values)
    )


def raceform_v1_row_sha256(values: Sequence[object]) -> bytes:
    """Return the 32-byte canonical Source Version 1 row fingerprint."""

    return hashlib.sha256(canonical_raceform_v1_row_message(values)).digest()
