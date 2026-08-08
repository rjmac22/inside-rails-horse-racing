#!/usr/bin/env python3
"""Promote the exact validated Inside Rails v1 candidate to the accepted release."""

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

from inside_rails.database.release_v1 import (  # noqa: E402
    default_candidate_path,
    default_release_path,
    promote_inside_rails_v1,
)


DEFAULT_CANDIDATE = default_candidate_path(ROOT)
DEFAULT_RELEASE = default_release_path(ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        type=Path,
        default=DEFAULT_CANDIDATE,
        help=f"Exact validated candidate (default: {DEFAULT_CANDIDATE})",
    )
    parser.add_argument(
        "--release",
        type=Path,
        default=DEFAULT_RELEASE,
        help=f"Canonical accepted release path (default: {DEFAULT_RELEASE})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = promote_inside_rails_v1(args.candidate, args.release)
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
