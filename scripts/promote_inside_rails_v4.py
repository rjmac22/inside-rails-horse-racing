#!/usr/bin/env python3
"""Promote the exact built and independently validated Inside Rails Database v4 candidate."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inside_rails.database.release_v4 import (  # noqa: E402
    default_base_release_path,
    default_candidate_path,
    default_release_path,
    promote_inside_rails_v4,
)


DEFAULT_CANDIDATE = default_candidate_path(ROOT)
DEFAULT_RELEASE = default_release_path(ROOT)
DEFAULT_BASE_RELEASE = default_base_release_path(ROOT)


def _current_repository_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        type=Path,
        default=DEFAULT_CANDIDATE,
        help=f"Exact built v4 candidate (default: {DEFAULT_CANDIDATE})",
    )
    parser.add_argument(
        "--release",
        type=Path,
        default=DEFAULT_RELEASE,
        help=f"Canonical immutable v4 release path (default: {DEFAULT_RELEASE})",
    )
    parser.add_argument(
        "--base-release",
        type=Path,
        default=DEFAULT_BASE_RELEASE,
        help=f"Retained accepted v3 base release (default: {DEFAULT_BASE_RELEASE})",
    )
    parser.add_argument(
        "--promotion-commit",
        default=None,
        help="40-character repository commit for the promotion implementation; defaults to git HEAD.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = promote_inside_rails_v4(
        args.candidate,
        args.release,
        project_root=ROOT,
        promotion_repository_commit=args.promotion_commit or _current_repository_commit(),
        base_release_path=args.base_release,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
