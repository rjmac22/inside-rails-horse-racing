"""Deterministic JSON loading and atomic writing for database release manifests."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path

from inside_rails.database.release_model import ActiveDatabaseManifest, ReleaseManifest
from inside_rails.database.release_paths import reject_symlink


def deterministic_json_bytes(payload: Mapping[str, object]) -> bytes:
    """Serialise one manifest deterministically as governed UTF-8 JSON."""

    text = json.dumps(
        dict(payload),
        allow_nan=False,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return f"{text}\n".encode("utf-8")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json_object(path: str | Path, *, name: str) -> dict[str, object]:
    """Load one JSON object while rejecting symlinks, duplicates and non-objects."""

    target = Path(path)
    reject_symlink(target, name=name)
    if not target.is_file():
        raise FileNotFoundError(f"{name} not found: {target}")
    try:
        payload = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read valid {name}: {target}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must contain one JSON object")
    return payload


def load_release_manifest(path: str | Path) -> ReleaseManifest:
    """Load and validate one immutable release manifest."""

    return ReleaseManifest.from_mapping(
        load_json_object(path, name="immutable release manifest")
    )


def load_active_manifest(path: str | Path) -> ActiveDatabaseManifest:
    """Load and validate the active database pointer."""

    return ActiveDatabaseManifest.from_mapping(
        load_json_object(path, name="active database manifest")
    )


def _fsync_directory(directory: Path) -> None:
    """Durably record a rename where directory fsync is supported."""

    if os.name != "posix":
        return
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_temporary_json(path: Path, payload: Mapping[str, object]) -> None:
    with path.open("xb") as handle:
        handle.write(deterministic_json_bytes(payload))
        handle.flush()
        os.fsync(handle.fileno())


def write_new_json_atomic(
    final_path: str | Path,
    temporary_path: str | Path,
    payload: Mapping[str, object],
) -> None:
    """Atomically create one immutable JSON file without overwriting any artifact."""

    final = Path(final_path)
    temporary = Path(temporary_path)
    if final.exists() or final.is_symlink():
        raise FileExistsError(f"Final manifest path already exists: {final}")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"Temporary manifest path already exists: {temporary}")
    if final.parent != temporary.parent:
        raise ValueError("Atomic manifest creation requires final and temporary siblings")

    final.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_temporary_json(temporary, payload)
        os.replace(temporary, final)
        _fsync_directory(final.parent)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def replace_json_atomic(
    final_path: str | Path,
    temporary_path: str | Path,
    payload: Mapping[str, object],
) -> None:
    """Atomically replace the mutable active pointer with complete verified JSON."""

    final = Path(final_path)
    temporary = Path(temporary_path)
    if final.is_symlink():
        raise RuntimeError(f"Active database manifest must not be a symbolic link: {final}")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"Temporary active-manifest path already exists: {temporary}")
    if final.parent != temporary.parent:
        raise ValueError("Atomic pointer replacement requires final and temporary siblings")

    final.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_temporary_json(temporary, payload)
        os.replace(temporary, final)
        _fsync_directory(final.parent)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
