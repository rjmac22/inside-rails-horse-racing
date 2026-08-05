"""Deterministic textual identifiers for the authorised minimum core."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
import re

_HEX_64 = re.compile(r"[0-9a-f]{64}")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _full_sha256_hex(value: bytes | str) -> str:
    if isinstance(value, bytes):
        if len(value) != 32:
            raise ValueError("SHA-256 bytes must be exactly 32 bytes")
        return value.hex()
    if isinstance(value, str) and _HEX_64.fullmatch(value):
        return value
    raise ValueError("SHA-256 text must be 64 lowercase hexadecimal characters")


def _hash_prefix(value: bytes | str) -> str:
    return _full_sha256_hex(value)[:24]


def _validated_slug(value: str, *, name: str) -> str:
    if not isinstance(value, str) or _SLUG.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase ASCII slug")
    return value


def _padded_positive(value: int, *, width: int, name: str) -> str:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    if value >= 10**width:
        raise ValueError(f"{name} exceeds the {width}-digit identifier width")
    return f"{value:0{width}d}"


def source_version_code(file_sha256: bytes | str) -> str:
    return f"sv:{_hash_prefix(file_sha256)}"


def source_relation_code(file_sha256: bytes | str, relation_slug: str = "data") -> str:
    return f"rel:{_hash_prefix(file_sha256)}:{_validated_slug(relation_slug, name='relation_slug')}"


def source_record_code(file_sha256: bytes | str, source_rowid: int) -> str:
    padded = _padded_positive(source_rowid, width=10, name="source_rowid")
    return f"rec:{_hash_prefix(file_sha256)}:data:{padded}"


def source_race_occurrence_code(file_sha256: bytes | str, race_sequence: int) -> str:
    padded = _padded_positive(race_sequence, width=9, name="race_sequence")
    return f"race:{_hash_prefix(file_sha256)}:{padded}"


def runner_participation_code(file_sha256: bytes | str, source_rowid: int) -> str:
    padded = _padded_positive(source_rowid, width=10, name="source_rowid")
    return f"run:{_hash_prefix(file_sha256)}:data:{padded}"


def governance_method_code(method_slug: str, method_version: int) -> str:
    version = _padded_positive(method_version, width=9, name="method_version").lstrip("0")
    return f"gm:{_validated_slug(method_slug, name='method_slug')}:v{version}"


def governance_release_code(
    file_sha256: bytes | str,
    release_slug: str,
    release_version: int,
) -> str:
    version = _padded_positive(release_version, width=9, name="release_version").lstrip("0")
    slug = _validated_slug(release_slug, name="release_slug")
    return f"gr:{_hash_prefix(file_sha256)}:{slug}:v{version}"


def order_race_groups_by_minimum_source_rowid(
    group_minimum_rowids: Mapping[Hashable, int],
) -> dict[Hashable, int]:
    """Assign one-based race sequences by ascending minimum supporting rowid."""

    observed: set[int] = set()
    ordered: list[tuple[int, Hashable]] = []
    for group, minimum_rowid in group_minimum_rowids.items():
        invalid_type = isinstance(minimum_rowid, bool) or not isinstance(minimum_rowid, int)
        if invalid_type or minimum_rowid <= 0:
            raise ValueError("Every minimum source rowid must be a positive integer")
        if minimum_rowid in observed:
            raise ValueError("Race groups cannot share the same minimum source rowid")
        observed.add(minimum_rowid)
        ordered.append((minimum_rowid, group))

    ordered.sort(key=lambda item: item[0])
    return {group: sequence for sequence, (_, group) in enumerate(ordered, start=1)}
