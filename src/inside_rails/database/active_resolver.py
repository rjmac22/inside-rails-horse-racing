"""Fail-closed resolution and query-only opening of the active accepted database."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Iterator

from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.release_manifest import load_active_manifest, load_release_manifest
from inside_rails.database.release_model import ActiveDatabaseManifest, ReleaseManifest
from inside_rails.database.release_paths import (
    ACTIVE_DATABASE_RELATIVE,
    reject_sqlite_sidecars,
    reject_symlink,
    release_paths,
    resolve_release_relative_path,
)
from inside_rails.database.schema import APPLICATION_ID, SCHEMA_VERSION, configure_governed_connection


@dataclass(frozen=True)
class ResolvedActiveRelease:
    project_root: Path
    active_manifest_path: Path
    release_manifest_path: Path
    database_path: Path
    active_manifest: ActiveDatabaseManifest
    release_manifest: ReleaseManifest


def _verify_file_identity(path: Path, *, expected_size: int, expected_sha256_hex: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Accepted database not found: {path}")
    observed_size = path.stat().st_size
    if observed_size != expected_size:
        raise RuntimeError(
            f"Accepted database size mismatch: observed={observed_size}, "
            f"expected={expected_size}"
        )
    observed_hash = sha256_file(path).hex()
    if observed_hash != expected_sha256_hex:
        raise RuntimeError(
            f"Accepted database SHA-256 mismatch: observed={observed_hash}, "
            f"expected={expected_sha256_hex}"
        )


def _validate_database_connection(
    connection: sqlite3.Connection,
    manifest: ReleaseManifest,
) -> None:
    configure_governed_connection(connection, query_only=True)

    application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
    if application_id != APPLICATION_ID or application_id != manifest.sqlite_application_id:
        raise RuntimeError("Accepted database application_id mismatch")
    if user_version != SCHEMA_VERSION or user_version != manifest.sqlite_user_version:
        raise RuntimeError("Accepted database user_version mismatch")
    if query_only != 1:
        raise RuntimeError("Accepted database connection is not query-only")

    quick_row = connection.execute("PRAGMA quick_check").fetchone()
    quick = "" if quick_row is None else str(quick_row[0])
    if quick != "ok":
        raise RuntimeError(f"Accepted database quick_check failed: {quick!r}")
    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise RuntimeError(
            f"Accepted database foreign_key_check returned {len(foreign_key_rows)} rows"
        )

    evidence_rows = connection.execute(
        """
        SELECT
            import_manifest.database_release_code,
            import_manifest.import_manifest_code,
            import_manifest.code_commit,
            import_manifest.reference_data_commit,
            import_manifest.build_status,
            import_manifest.post_load_validation_passed,
            source_version.source_version_code,
            lower(hex(source_version.file_sha256)),
            governance_release.governance_release_code
        FROM import_manifest
        JOIN source_version
          ON source_version.source_version_id = import_manifest.source_version_id
        JOIN governance_release
          ON governance_release.governance_release_id = import_manifest.governance_release_id
        """
    ).fetchall()
    if len(evidence_rows) != 1:
        raise RuntimeError(
            f"Accepted database must contain exactly one import manifest; found "
            f"{len(evidence_rows)}"
        )

    expected_evidence = (
        manifest.database_release_code,
        manifest.import_manifest_code,
        manifest.code_commit,
        manifest.reference_data_commit,
        "release_accepted",
        1,
        manifest.source_version_code,
        manifest.source_file_sha256_hex,
        manifest.governance_release_code,
    )
    if evidence_rows[0] != expected_evidence:
        raise RuntimeError(
            "Accepted database identity differs from immutable release manifest: "
            f"observed={evidence_rows[0]!r}, expected={expected_evidence!r}"
        )

    validation_rows = connection.execute(
        """
        SELECT validation_stage, outcome
        FROM import_validation_result
        WHERE import_manifest_id = 1 AND required_for_acceptance = 1
        ORDER BY validation_stage
        """
    ).fetchall()
    if len(validation_rows) != manifest.required_validation_count:
        raise RuntimeError(
            "Accepted database required-validation count differs from release manifest"
        )
    if any(outcome != "passed" for _, outcome in validation_rows):
        raise RuntimeError("Accepted database contains a failed required validation")


def _reconcile_manifests(
    active: ActiveDatabaseManifest,
    release: ReleaseManifest,
) -> None:
    fields = (
        "database_release_code",
        "database_relative_path",
        "database_file_sha256_hex",
        "source_version_code",
        "import_manifest_code",
        "code_commit",
    )
    differences = [
        field for field in fields if getattr(active, field) != getattr(release, field)
    ]
    if differences:
        raise RuntimeError(
            f"Active and immutable release manifests differ for: {differences!r}"
        )


def resolve_active_release(project_root: str | Path) -> ResolvedActiveRelease:
    """Resolve and independently verify every artifact selecting the active database."""

    root = Path(project_root).expanduser().resolve()
    active_path = root.joinpath(*ACTIVE_DATABASE_RELATIVE.parts)
    reject_symlink(active_path, name="active database manifest")
    active = load_active_manifest(active_path)

    release_manifest_path = resolve_release_relative_path(
        root, active.release_manifest_relative_path
    )
    reject_symlink(release_manifest_path, name="immutable release manifest")
    release = load_release_manifest(release_manifest_path)
    _reconcile_manifests(active, release)

    active_database_path = resolve_release_relative_path(root, active.database_relative_path)
    release_database_path = resolve_release_relative_path(root, release.database_relative_path)
    if active_database_path != release_database_path:
        raise RuntimeError("Active and immutable manifests resolve different database paths")

    expected_paths = release_paths(root, release.database_release_code)
    if release_manifest_path != expected_paths.release_manifest:
        raise RuntimeError("Immutable release manifest is not at its governed path")
    if release_database_path != expected_paths.release_database:
        raise RuntimeError("Accepted database is not at its governed path")

    reject_symlink(release_database_path, name="accepted database")
    reject_sqlite_sidecars(release_database_path)
    _verify_file_identity(
        release_database_path,
        expected_size=release.database_file_size_bytes,
        expected_sha256_hex=release.database_file_sha256_hex,
    )

    connection = sqlite3.connect(
        f"file:{release_database_path.as_posix()}?mode=ro",
        uri=True,
    )
    try:
        _validate_database_connection(connection, release)
    finally:
        connection.close()

    return ResolvedActiveRelease(
        project_root=root,
        active_manifest_path=active_path,
        release_manifest_path=release_manifest_path,
        database_path=release_database_path,
        active_manifest=active,
        release_manifest=release,
    )


@contextmanager
def connect_active_database(project_root: str | Path) -> Iterator[sqlite3.Connection]:
    """Open the fully resolved active release through a query-only SQLite connection."""

    resolved = resolve_active_release(project_root)
    connection = sqlite3.connect(
        f"file:{resolved.database_path.as_posix()}?mode=ro",
        uri=True,
    )
    try:
        _validate_database_connection(connection, resolved.release_manifest)
        yield connection
    finally:
        connection.close()
