"""File-copy, hash and cleanup controls for minimum-core candidates."""

from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter

from inside_rails.database.minimum_core_candidate_model import (
    COPY_CHUNK_BYTES,
    artifact_paths,
)
from inside_rails.database.raw_mirror_prototype import sha256_file


def remove_output(output: Path) -> None:
    for path in artifact_paths(output):
        path.unlink(missing_ok=True)


def require_no_sidecars(database: Path, *, label: str) -> None:
    sidecars = [path for path in artifact_paths(database)[1:] if path.exists()]
    if sidecars:
        raise RuntimeError(
            f"{label} has unexpected SQLite sidecars: "
            + ", ".join(str(path) for path in sidecars)
        )


def validate_file_hash(path: Path, expected: bytes, *, label: str) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    require_no_sidecars(path, label=label)
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected.hex()}; "
            f"observed {observed.hex()}"
        )
    return observed


def _fsync_directory(path: Path) -> None:
    flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def copy_candidate(source: Path, output: Path) -> tuple[int, float]:
    started = perf_counter()
    copied = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_stream, output.open("xb") as output_stream:
        while True:
            chunk = input_stream.read(COPY_CHUNK_BYTES)
            if not chunk:
                break
            output_stream.write(chunk)
            copied += len(chunk)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    _fsync_directory(output.parent)
    return copied, perf_counter() - started
