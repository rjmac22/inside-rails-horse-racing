#!/usr/bin/env python3
"""Independently validate the persisted Source Version 1 core prototype."""

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

from inside_rails.database.core_structure_validator import (
    validate_core_structure_prototype,
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
    / "raceform_v1_raw_mirror_candidate.sqlite3"
)
DEFAULT_PROTOTYPE = (
    ROOT
    / "data"
    / "processed"
    / "database"
    / "prototypes"
    / "raceform_v1_core_structure_prototype.sqlite3"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--raw-mirror-candidate",
        type=Path,
        default=DEFAULT_RAW_MIRROR,
    )
    parser.add_argument("--prototype", type=Path, default=DEFAULT_PROTOTYPE)
    parser.add_argument(
        "--race-count",
        type=int,
        default=3,
        help="Expected number of first complete race groups in the prototype.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = validate_core_structure_prototype(
        args.source,
        args.raw_mirror_candidate,
        args.prototype,
        race_count=args.race_count,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
