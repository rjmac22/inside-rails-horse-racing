"""Typed external-manifest contracts for accepted and active database releases."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import PurePosixPath
import re
from typing import Mapping

RELEASE_MANIFEST_SCHEMA_VERSION = 1
ACTIVE_MANIFEST_SCHEMA_VERSION = 1
REQUIRED_VALIDATION_COUNT = 7
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_DATABASE_RELEASE_PATTERN = re.compile(r"db:[0-9]{8}T[0-9]{12}Z:[0-9a-f]{8}")
_IMPORT_MANIFEST_PATTERN = re.compile(r"imp:[0-9]{8}T[0-9]{12}Z:[0-9a-f]{8}")
_SOURCE_VERSION_PATTERN = re.compile(r"sv:[0-9a-f]{24}")
_GOVERNANCE_RELEASE_PATTERN = re.compile(
    r"gr:[0-9a-f]{24}:[a-z0-9]+(?:-[a-z0-9]+)*:v[1-9][0-9]*"
)


def _exact_keys(payload: Mapping[str, object], expected: frozenset[str], *, name: str) -> None:
    observed = frozenset(payload)
    if observed != expected:
        missing = sorted(expected - observed)
        unexpected = sorted(observed - expected)
        raise ValueError(
            f"{name} fields differ: missing={missing!r}, unexpected={unexpected!r}"
        )


def _integer(payload: Mapping[str, object], key: str, *, minimum: int = 0) -> int:
    value = payload[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{key} must be an integer >= {minimum}")
    return value


def _boolean(payload: Mapping[str, object], key: str) -> bool:
    value = payload[key]
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a JSON boolean")
    return value


def _text(payload: Mapping[str, object], key: str) -> str:
    value = payload[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _optional_text(payload: Mapping[str, object], key: str) -> str | None:
    value = payload[key]
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be null or non-empty text")
    return value


def _pattern(value: str, pattern: re.Pattern[str], *, name: str) -> str:
    if pattern.fullmatch(value) is None:
        raise ValueError(f"{name} has an invalid governed format")
    return value


def _timestamp(value: str, *, name: str) -> str:
    try:
        datetime.strptime(value, TIMESTAMP_FORMAT)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DDTHH:MM:SS.ffffffZ") from exc
    return value


def _relative_posix(value: str, *, name: str) -> str:
    if "\\" in value:
        raise ValueError(f"{name} must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{name} must be a safe relative POSIX path")
    return value


@dataclass(frozen=True)
class ReleaseManifest:
    manifest_schema_version: int
    database_release_code: str
    database_relative_path: str
    database_file_sha256_hex: str
    database_file_size_bytes: int
    sqlite_application_id: int
    sqlite_user_version: int
    source_version_code: str
    source_file_sha256_hex: str
    import_manifest_code: str
    governance_release_code: str
    code_commit: str
    reference_data_commit: str
    release_accepted_at_utc: str
    physical_record_count: int
    admitted_record_count: int
    excluded_record_count: int
    race_occurrence_count: int
    runner_participation_count: int
    required_validation_status: str
    required_validation_count: int
    release_gate_evidence_path: str
    prior_database_release_code: str | None
    prior_release_preserved: bool

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ReleaseManifest":
        expected = frozenset(cls.__dataclass_fields__)
        _exact_keys(payload, expected, name="release manifest")

        schema_version = _integer(payload, "manifest_schema_version", minimum=1)
        if schema_version != RELEASE_MANIFEST_SCHEMA_VERSION:
            raise ValueError(f"Unsupported release manifest schema: {schema_version}")

        physical = _integer(payload, "physical_record_count")
        admitted = _integer(payload, "admitted_record_count")
        excluded = _integer(payload, "excluded_record_count")
        if physical != admitted + excluded:
            raise ValueError("Release manifest physical count must equal admitted plus excluded")

        validation_status = _text(payload, "required_validation_status")
        validation_count = _integer(payload, "required_validation_count")
        if validation_status != "passed" or validation_count != REQUIRED_VALIDATION_COUNT:
            raise ValueError("Release manifest must record all seven required validations passed")

        prior_preserved = _boolean(payload, "prior_release_preserved")
        if not prior_preserved:
            raise ValueError("Accepted release must record prior-release preservation")

        prior_code = _optional_text(payload, "prior_database_release_code")
        if prior_code is not None:
            _pattern(prior_code, _DATABASE_RELEASE_PATTERN, name="prior_database_release_code")

        return cls(
            manifest_schema_version=schema_version,
            database_release_code=_pattern(
                _text(payload, "database_release_code"),
                _DATABASE_RELEASE_PATTERN,
                name="database_release_code",
            ),
            database_relative_path=_relative_posix(
                _text(payload, "database_relative_path"),
                name="database_relative_path",
            ),
            database_file_sha256_hex=_pattern(
                _text(payload, "database_file_sha256_hex"),
                _SHA256_PATTERN,
                name="database_file_sha256_hex",
            ),
            database_file_size_bytes=_integer(payload, "database_file_size_bytes", minimum=1),
            sqlite_application_id=_integer(payload, "sqlite_application_id", minimum=1),
            sqlite_user_version=_integer(payload, "sqlite_user_version", minimum=1),
            source_version_code=_pattern(
                _text(payload, "source_version_code"),
                _SOURCE_VERSION_PATTERN,
                name="source_version_code",
            ),
            source_file_sha256_hex=_pattern(
                _text(payload, "source_file_sha256_hex"),
                _SHA256_PATTERN,
                name="source_file_sha256_hex",
            ),
            import_manifest_code=_pattern(
                _text(payload, "import_manifest_code"),
                _IMPORT_MANIFEST_PATTERN,
                name="import_manifest_code",
            ),
            governance_release_code=_pattern(
                _text(payload, "governance_release_code"),
                _GOVERNANCE_RELEASE_PATTERN,
                name="governance_release_code",
            ),
            code_commit=_pattern(
                _text(payload, "code_commit"), _COMMIT_PATTERN, name="code_commit"
            ),
            reference_data_commit=_pattern(
                _text(payload, "reference_data_commit"),
                _COMMIT_PATTERN,
                name="reference_data_commit",
            ),
            release_accepted_at_utc=_timestamp(
                _text(payload, "release_accepted_at_utc"),
                name="release_accepted_at_utc",
            ),
            physical_record_count=physical,
            admitted_record_count=admitted,
            excluded_record_count=excluded,
            race_occurrence_count=_integer(payload, "race_occurrence_count", minimum=1),
            runner_participation_count=_integer(
                payload, "runner_participation_count", minimum=1
            ),
            required_validation_status=validation_status,
            required_validation_count=validation_count,
            release_gate_evidence_path=_relative_posix(
                _text(payload, "release_gate_evidence_path"),
                name="release_gate_evidence_path",
            ),
            prior_database_release_code=prior_code,
            prior_release_preserved=prior_preserved,
        )

    def to_mapping(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ActiveDatabaseManifest:
    active_manifest_schema_version: int
    database_release_code: str
    database_relative_path: str
    release_manifest_relative_path: str
    database_file_sha256_hex: str
    source_version_code: str
    import_manifest_code: str
    code_commit: str
    activated_at_utc: str
    post_load_validation_passed: bool
    previous_active_database_release_code: str | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ActiveDatabaseManifest":
        expected = frozenset(cls.__dataclass_fields__)
        _exact_keys(payload, expected, name="active database manifest")

        schema_version = _integer(payload, "active_manifest_schema_version", minimum=1)
        if schema_version != ACTIVE_MANIFEST_SCHEMA_VERSION:
            raise ValueError(f"Unsupported active manifest schema: {schema_version}")
        if not _boolean(payload, "post_load_validation_passed"):
            raise ValueError("Active database manifest requires passed post-load validation")

        previous_code = _optional_text(payload, "previous_active_database_release_code")
        if previous_code is not None:
            _pattern(
                previous_code,
                _DATABASE_RELEASE_PATTERN,
                name="previous_active_database_release_code",
            )

        return cls(
            active_manifest_schema_version=schema_version,
            database_release_code=_pattern(
                _text(payload, "database_release_code"),
                _DATABASE_RELEASE_PATTERN,
                name="database_release_code",
            ),
            database_relative_path=_relative_posix(
                _text(payload, "database_relative_path"),
                name="database_relative_path",
            ),
            release_manifest_relative_path=_relative_posix(
                _text(payload, "release_manifest_relative_path"),
                name="release_manifest_relative_path",
            ),
            database_file_sha256_hex=_pattern(
                _text(payload, "database_file_sha256_hex"),
                _SHA256_PATTERN,
                name="database_file_sha256_hex",
            ),
            source_version_code=_pattern(
                _text(payload, "source_version_code"),
                _SOURCE_VERSION_PATTERN,
                name="source_version_code",
            ),
            import_manifest_code=_pattern(
                _text(payload, "import_manifest_code"),
                _IMPORT_MANIFEST_PATTERN,
                name="import_manifest_code",
            ),
            code_commit=_pattern(
                _text(payload, "code_commit"), _COMMIT_PATTERN, name="code_commit"
            ),
            activated_at_utc=_timestamp(
                _text(payload, "activated_at_utc"), name="activated_at_utc"
            ),
            post_load_validation_passed=True,
            previous_active_database_release_code=previous_code,
        )

    def to_mapping(self) -> dict[str, object]:
        return asdict(self)
