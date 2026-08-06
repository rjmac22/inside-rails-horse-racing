#!/usr/bin/env python3
"""Run the bounded Source Version 1 raw-mirror persistence prototype."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inside_rails.database.raw_mirror_prototype import run_raw_mirror_prototype


DEFAULT_SOURCE = (
    PROJECT_ROOT
    / "data/raw/form_2015-present/form_2015-present/raceform.db"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "data/processed/database/prototypes/raceform_v1_raw_mirror_prototype.sqlite3"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy only representative Source Version 1 records into a temporary governed "
            "SQLite schema and verify exact value, typeof() and fingerprint readback."
        )
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_raw_mirror_prototype(args.source, args.output)
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
