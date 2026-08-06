#!/usr/bin/env python3
"""Build a small persisted Source Version 1 race-and-runner core prototype."""

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

from inside_rails.database.core_structure_prototype import run_core_structure_prototype


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
DEFAULT_RAW_MIRROR = (
    ROOT
    / "data"
    / "processed"
    / "database"
    / "candidates"
    / "raceform_v1_raw_mirror_candidate.sqlite3"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "processed"
    / "database"
    / "prototypes"
    / "raceform_v1_core_structure_prototype.sqlite3"
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
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--raw-mirror-candidate",
        type=Path,
        default=DEFAULT_RAW_MIRROR,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--race-count",
        type=int,
        default=3,
        help="Number of first complete race groups to persist.",
    )
    parser.add_argument(
        "--repository-commit",
        default=None,
        help="Exact 40-character code commit; defaults to git rev-parse HEAD.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_core_structure_prototype(
        args.source,
        args.raw_mirror_candidate,
        args.output,
        repository_commit=args.repository_commit or _current_repository_commit(),
        race_count=args.race_count,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
