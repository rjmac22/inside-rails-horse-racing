#!/usr/bin/env python3
"""Build the Inside Rails Database v4 Study 03 racecourse identity candidate."""

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

from inside_rails.database.racecourse_identity_candidate import (  # noqa: E402
    build_racecourse_identity_candidate,
)
from inside_rails.database.study03_snapshot import (  # noqa: E402
    require_completed_study03_snapshot,
)


def _current_commit() -> str:
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
    parser.add_argument("--repository-commit", default=None)
    parser.add_argument("--reference-data-commit", default=None)
    parser.add_argument("--base-release", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require_completed_study03_snapshot(ROOT)
    commit = args.repository_commit or _current_commit()
    summary = build_racecourse_identity_candidate(
        ROOT,
        repository_commit=commit,
        reference_data_commit=args.reference_data_commit or commit,
        base_release_path=args.base_release,
        output_path=args.output,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
