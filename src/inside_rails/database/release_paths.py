"""Governed filesystem paths for immutable database releases and the active pointer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re

DATABASE_DIRECTORY_RELATIVE = PurePosixPath("data/processed/database")
RELEASES_DIRECTORY_RELATIVE = DATABASE_DIRECTORY_RELATIVE / "releases"
STAGING_DIRECTORY_RELATIVE = RELEASES_DIRECTORY_RELATIVE / ".staging"
ACTIVE_DATABASE_RELATIVE = DATABASE_DIRECTORY_RELATIVE / "active_database.json"

_DATABASE_RELEASE_PATTERN = re.compile(r"db:[0-9]{8}T[0-9]{12}Z:[0-9a-f]{8}")
_SAFE_RELEASE_SLUG_PATTERN = re.compile(r"db_[0-9]{8}T[0-9]{12}Z_[0-9a-f]{8}")


@dataclass(frozen=True)
class ReleasePaths:
    project_root: Path
    database_directory: Path
    releases_directory: Path
    staging_directory: Path
    staging_database: Path
    staging_manifest: Path
    release_database: Path
    release_manifest: Path
    active_database_manifest: Path


def safe_release_slug(database_release_code: str) -> str:
    """Convert a governed release identity into one portable deterministic filename slug."""

    if not isinstance(database_release_code, str):
        raise ValueError("database_release_code must be text")
    if _DATABASE_RELEASE_PATTERN.fullmatch(database_release_code) is None:
        raise ValueError("database_release_code has an invalid governed format")
    slug = database_release_code.replace(":", "_")
    if _SAFE_RELEASE_SLUG_PATTERN.fullmatch(slug) is None:
        raise RuntimeError("Unable to derive a safe database release slug")
    return slug


def release_paths(project_root: str | Path, database_release_code: str) -> ReleasePaths:
    """Return every governed path for one immutable database release."""

    root = Path(project_root).expanduser().resolve()
    slug = safe_release_slug(database_release_code)
    database_directory = root.joinpath(*DATABASE_DIRECTORY_RELATIVE.parts)
    releases_directory = root.joinpath(*RELEASES_DIRECTORY_RELATIVE.parts)
    staging_directory = root.joinpath(*STAGING_DIRECTORY_RELATIVE.parts)
    stem = f"inside_rails_{slug}"
    return ReleasePaths(
        project_root=root,
        database_directory=database_directory,
        releases_directory=releases_directory,
        staging_directory=staging_directory,
        staging_database=staging_directory / f"{stem}.sqlite3.tmp",
        staging_manifest=staging_directory / f"{stem}.manifest.json.tmp",
        release_database=releases_directory / f"{stem}.sqlite3",
        release_manifest=releases_directory / f"{stem}.manifest.json",
        active_database_manifest=root.joinpath(*ACTIVE_DATABASE_RELATIVE.parts),
    )


def relative_to_project(project_root: str | Path, path: str | Path) -> str:
    """Return a governed POSIX path relative to the project root."""

    root = Path(project_root).expanduser().resolve()
    candidate = Path(path).expanduser().resolve(strict=False)
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes project root: {candidate}") from exc
    return relative.as_posix()


def resolve_release_relative_path(project_root: str | Path, value: str) -> Path:
    """Resolve a manifest path and require it to stay below the releases directory."""

    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Release manifest path must be non-empty POSIX text")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("Release manifest path must be a safe relative path")

    root = Path(project_root).expanduser().resolve()
    releases = root.joinpath(*RELEASES_DIRECTORY_RELATIVE.parts).resolve(strict=False)
    candidate = root.joinpath(*relative.parts).resolve(strict=False)
    try:
        candidate.relative_to(releases)
    except ValueError as exc:
        raise ValueError(f"Release path escapes governed releases directory: {value!r}") from exc
    return candidate


def reject_symlink(path: Path, *, name: str) -> None:
    """Fail when a governed manifest or database file is a symbolic link."""

    if path.is_symlink():
        raise RuntimeError(f"{name} must not be a symbolic link: {path}")


def sqlite_sidecars(database: Path) -> tuple[Path, Path, Path]:
    """Return prohibited SQLite sidecar paths for one database file."""

    return (
        Path(f"{database}-journal"),
        Path(f"{database}-wal"),
        Path(f"{database}-shm"),
    )


def reject_sqlite_sidecars(database: Path) -> None:
    """Fail when any SQLite sidecar exists beside a governed release."""

    present = [str(path) for path in sqlite_sidecars(database) if path.exists()]
    if present:
        raise RuntimeError(f"SQLite sidecars are prohibited: {present!r}")
