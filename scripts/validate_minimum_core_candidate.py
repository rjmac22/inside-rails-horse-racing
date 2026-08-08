#!/usr/bin/env python3
"""Independently validate a complete Source Version 1 minimum-core candidate."""

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

from inside_rails.database.minimum_core_validator import (
    validate_minimum_core_candidate,
)


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
    / "inside_rails_v1_raw_mirror_candidate.sqlite3"
)
DEFAULT_CANDIDATE = (
    ROOT
    / "data"
    / "processed"
    / "database"
    / "candidates"
    / "inside_rails_v1_candidate.sqlite3"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--raw-mirror-candidate",
        type=Path,
        default=DEFAULT_RAW_MIRROR,
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=DEFAULT_CANDIDATE,
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5_000,
        help="Raw records compared per fetch batch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = validate_minimum_core_candidate(
        args.source,
        args.raw_mirror_candidate,
        args.candidate,
        batch_size=args.batch_size,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
