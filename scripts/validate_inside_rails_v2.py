#!/usr/bin/env python3
"""Independently validate a built or accepted Inside Rails Database v2 artefact read-only."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inside_rails.database.governed_integration_candidate import (  # noqa: E402
    default_base_release_path,
    default_v2_candidate_path,
)
from inside_rails.database.governed_integration_validator import (  # noqa: E402
    validate_governed_integration_candidate,
)


# Database v2 was built and release-accepted from this exact repository/reference
# snapshot. Later database work legitimately extended mutable reference files, so
# historical v2 validation must replay the evidence that actually governed v2.
V2_REFERENCE_COMMIT = "68ac0364c4af2a104ea76c8765fd0e220aaf8e84"
V2_REFERENCE_PATHS = (
    "data/reference/manual_verifications.csv",
    "data/reference/connection_identity_repairs.csv",
    "data/reference/runner_record_supplementations.csv",
    "data/reference/horse_pedigree_identity_governance.csv",
)


def _git_bytes(commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Unable to read Database v2 historical reference {relative_path!r} "
            f"from {commit}: {detail or 'unknown git error'}"
        )
    return result.stdout


@contextmanager
def historical_v2_reference_root() -> Iterator[Path]:
    """Materialize only v2's governed mutable references from its exact Git snapshot."""

    verify = subprocess.run(
        ["git", "cat-file", "-e", f"{V2_REFERENCE_COMMIT}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if verify.returncode != 0:
        detail = verify.stderr.strip() or verify.stdout.strip() or "unknown git error"
        raise RuntimeError(
            f"Database v2 reference commit unavailable: {V2_REFERENCE_COMMIT}: {detail}"
        )

    with TemporaryDirectory(prefix="inside-rails-v2-reference-") as temporary:
        snapshot_root = Path(temporary)
        for relative in V2_REFERENCE_PATHS:
            destination = snapshot_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_git_bytes(V2_REFERENCE_COMMIT, relative))
        yield snapshot_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        type=Path,
        default=default_v2_candidate_path(ROOT),
    )
    parser.add_argument(
        "--base-release",
        type=Path,
        default=default_base_release_path(ROOT),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5_000,
        help="Rows compared per streaming source/core validation batch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with historical_v2_reference_root() as reference_root:
        summary = validate_governed_integration_candidate(
            args.candidate,
            args.base_release,
            reference_root,
            batch_size=args.batch_size,
        )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
