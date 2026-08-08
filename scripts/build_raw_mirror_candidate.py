#!/usr/bin/env python3
"""Build a complete disposable Source Version 1 raw-mirror candidate."""

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

from inside_rails.database.raw_mirror_candidate import build_raw_mirror_candidate


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "processed"
    / "database"
    / "candidates"
    / "inside_rails_v1_raw_mirror_candidate.sqlite3"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to the accepted immutable raceform.db source.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="New disposable candidate path; it must not already exist.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1_000,
        help="Number of source records prepared per SQLite executemany call.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_raw_mirror_candidate(
        args.source,
        args.output,
        batch_size=args.batch_size,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
