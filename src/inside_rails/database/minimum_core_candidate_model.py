"""Shared contracts for a complete disposable minimum-core candidate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import secrets
import sqlite3
import struct


EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
REPOSITORY_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
HEX_SUFFIX_PATTERN = re.compile(r"[0-9a-f]{8}")
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
COPY_CHUNK_BYTES = 16 * 1024 * 1024

GOVERNANCE_EVIDENCE = (
    (
        "document",
        "docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md",
        "Accepted bounded authorisation for the Source Version 1 structural core.",
    ),
    (
        "document",
        "docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md",
        "Accepted physical schema and identifier contract for minimum core version 1.",
    ),
    (
        "governed_output",
        "docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md",
        "Source-wide raw-mirror build and independent persisted-readback evidence.",
    ),
    (
        "governed_output",
        "docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md",
        "Real-data race-and-runner structural prototype and independent validation evidence.",
    ),
)

VALIDATION_ROWS = (
    (
        "persisted_readback",
        "minimum-core-candidate-builder",
        "1",
        "Complete persisted race, runner and raw-population readback passed.",
    ),
    (
        "sqlite_integrity",
        "sqlite-quick-check",
        sqlite3.sqlite_version,
        "PRAGMA quick_check returned exactly ok.",
    ),
    (
        "foreign_key_validation",
        "sqlite-foreign-key-check",
        sqlite3.sqlite_version,
        "PRAGMA foreign_key_check returned zero rows.",
    ),
    (
        "post_load_validation",
        "minimum-core-candidate-builder",
        "1",
        "Source-wide race grouping, runner lineage, stable codes and counts reconciled.",
    ),
)


@dataclass(frozen=True)
class MinimumCoreCandidateSummary:
    source_path: str
    raw_mirror_candidate_path: str
    output_path: str
    source_file_sha256_hex: str
    raw_mirror_candidate_sha256_hex: str
    copied_raw_mirror_sha256_hex: str
    output_file_sha256_hex: str
    source_file_size_bytes: int
    raw_mirror_candidate_file_size_bytes: int
    output_file_size_bytes: int
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    race_occurrence_count: int
    runner_participation_count: int
    race_batch_count: int
    runner_batch_count: int
    batch_size: int
    copied_bytes: int
    copy_elapsed_seconds: float
    core_population_elapsed_seconds: float
    build_elapsed_seconds: float
    core_rows_per_second: float
    race_readback_comparisons: int
    runner_readback_comparisons: int
    manifest_code: str
    database_release_code: str
    manifest_status: str
    validation_result_count: int
    quick_check: str
    foreign_key_check_rows: int
    application_id: int
    user_version: int
    source_hash_unchanged: bool
    raw_mirror_candidate_hash_unchanged: bool
    persisted_readback_passed: bool
    release_accepted: bool


def positive_integer(value: int, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def repository_commit(value: str, *, name: str) -> str:
    if not isinstance(value, str) or REPOSITORY_COMMIT_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be 40 lowercase hexadecimal characters")
    return value


def expected_hash(value: bytes, *, name: str) -> bytes:
    if not isinstance(value, bytes) or len(value) != 32:
        raise ValueError(f"{name} must contain exactly 32 bytes")
    return value


def timestamp(value: str | None) -> tuple[str, str]:
    text = value or datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
    try:
        parsed = datetime.strptime(text, TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "created_at_utc must use YYYY-MM-DDTHH:MM:SS.ffffffZ"
        ) from exc
    return (
        parsed.strftime(TIMESTAMP_FORMAT),
        parsed.strftime("%Y%m%dT%H%M%S%fZ"),
    )


def suffix(value: str | None, *, name: str) -> str:
    text = value or secrets.token_hex(4)
    if not isinstance(text, str) or HEX_SUFFIX_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{name} must be 8 lowercase hexadecimal characters")
    return text


def artifact_paths(database: Path) -> tuple[Path, ...]:
    return (
        database,
        Path(f"{database}-journal"),
        Path(f"{database}-wal"),
        Path(f"{database}-shm"),
    )


def same_value(left: object, right: object) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        return struct.pack(">d", left) == struct.pack(">d", right)
    return type(left) is type(right) and left == right
