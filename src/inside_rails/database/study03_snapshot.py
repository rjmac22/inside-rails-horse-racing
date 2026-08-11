"""Fail-closed binding to the completed Study 03 racecourse evidence snapshot."""

from __future__ import annotations

from pathlib import Path
import subprocess

from inside_rails.database.racecourse_identity_reference import (
    RACECOURSE_DIRECTORY,
    STUDY03_EVIDENCE_COMMIT,
    STUDY03_NOTEBOOK,
)


def require_completed_study03_snapshot(project_root: str | Path) -> None:
    """Require current Study 03 notebook bytes to match the completed evidence commit."""

    root = Path(project_root).expanduser().resolve()
    verify = subprocess.run(
        ["git", "cat-file", "-e", f"{STUDY03_EVIDENCE_COMMIT}^{{commit}}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if verify.returncode != 0:
        detail = verify.stderr.strip() or verify.stdout.strip() or "unknown git error"
        raise RuntimeError(
            f"Completed Study 03 evidence commit is unavailable: {STUDY03_EVIDENCE_COMMIT}: {detail}"
        )

    comparison = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            STUDY03_EVIDENCE_COMMIT,
            "--",
            STUDY03_NOTEBOOK,
            RACECOURSE_DIRECTORY,
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if comparison.returncode == 0:
        return
    if comparison.returncode == 1:
        raise RuntimeError(
            "Study 03 racecourse evidence differs from completed evidence commit "
            f"{STUDY03_EVIDENCE_COMMIT}; Database v4 build refused"
        )
    detail = comparison.stderr.strip() or comparison.stdout.strip() or "unknown git error"
    raise RuntimeError(f"Unable to verify completed Study 03 evidence snapshot: {detail}")


__all__ = ["require_completed_study03_snapshot"]
