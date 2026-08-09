#!/usr/bin/env python3
"""Build and independently validate one complete disposable Inside Rails Database v2 candidate."""

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

from inside_rails.database.governed_integration_build import (
    build_governed_integration_candidate,
)
from inside_rails.database.governed_integration_candidate import (
    default_base_release_path,
    default_v2_candidate_path,
)


def _current_repository_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-release",
        type=Path,
        default=default_base_release_path(ROOT),
        help="Exact accepted immutable Database v1 release used as the v2 base.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_v2_candidate_path(ROOT),
        help="New disposable Database v2 candidate path; must not already exist.",
    )
    parser.add_argument(
        "--repository-commit",
        default=None,
        help="Exact 40-character code commit; defaults to git rev-parse HEAD.",
    )
    parser.add_argument(
        "--reference-data-commit",
        default=None,
        help="Exact reference-data commit; defaults to the code commit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository_commit = args.repository_commit or _current_repository_commit()
    summary = build_governed_integration_candidate(
        ROOT,
        repository_commit=repository_commit,
        reference_data_commit=args.reference_data_commit or repository_commit,
        base_release_path=args.base_release,
        output_path=args.output,
        build_command="python scripts/build_inside_rails_v2.py",
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
