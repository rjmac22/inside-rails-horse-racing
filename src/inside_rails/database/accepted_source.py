"""Fail-closed identity gate for the accepted Source Version 1 file."""

from __future__ import annotations

from pathlib import Path

from inside_rails.database.raw_mirror_prototype import (
    PrototypeSummary,
    RACEFORM_V1_BASELINE,
    SourceBaseline,
    run_raw_mirror_prototype,
    sha256_file,
)


RACEFORM_V1_FILE_SHA256_HEX = (
    "77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7"
)
RACEFORM_V1_FILE_SHA256 = bytes.fromhex(RACEFORM_V1_FILE_SHA256_HEX)


def validate_source_version_1_file_identity(
    source_path: str | Path,
    *,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
) -> bytes:
    """Return the source hash only when it matches the accepted exact file."""

    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"SQLite source not found: {source}")
    if len(expected_source_sha256) != 32:
        raise ValueError("Expected Source Version 1 SHA-256 must contain exactly 32 bytes")

    observed = sha256_file(source)
    if observed != expected_source_sha256:
        raise RuntimeError(
            "Source Version 1 file SHA-256 mismatch: "
            f"expected {expected_source_sha256.hex()}; observed {observed.hex()}"
        )
    return observed


def run_accepted_raw_mirror_prototype(
    source_path: str | Path,
    output_path: str | Path,
    *,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    created_at_utc: str | None = None,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
) -> PrototypeSummary:
    """Run the raw-mirror prototype only for the accepted exact source file."""

    source = Path(source_path).expanduser().resolve()
    validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )

    summary: PrototypeSummary | None = None
    try:
        summary = run_raw_mirror_prototype(
            source,
            output_path,
            baseline=baseline,
            created_at_utc=created_at_utc,
        )
        if summary.source_file_sha256_hex != expected_source_sha256.hex():
            raise RuntimeError(
                "Prototype recorded a source hash different from the accepted "
                "Source Version 1 identity"
            )
        validate_source_version_1_file_identity(
            source,
            expected_source_sha256=expected_source_sha256,
        )
    except Exception:
        if summary is not None:
            Path(summary.output_path).unlink(missing_ok=True)
        raise

    return summary
