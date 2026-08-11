#!/usr/bin/env python3
"""Independently validate the Inside Rails Database v4 candidate."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inside_rails.database.racecourse_identity_validator import (  # noqa: E402
    validate_racecourse_identity_candidate,
)


def default_candidate() -> Path:
    return ROOT / "data/processed/database/candidates/inside_rails_v4_candidate.sqlite3"


def default_base_release() -> Path:
    return ROOT / "data/processed/database/releases/inside_rails_v3.sqlite3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=default_candidate())
    parser.add_argument("--base-release", type=Path, default=default_base_release())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = validate_racecourse_identity_candidate(
        args.candidate,
        args.base_release,
        ROOT,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
