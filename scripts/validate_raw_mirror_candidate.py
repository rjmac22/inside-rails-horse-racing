#!/usr/bin/env python3
"""Independently validate a complete disposable Source Version 1 raw mirror."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from inside_rails.database.raw_mirror_validator import (  # noqa: E402
    validate_raw_mirror_candidate,
)


DEFAULT_SOURCE = Path(
    "data/raw/form_2015-present/form_2015-present/raceform.db"
)
DEFAULT_CANDIDATE = Path(
    "data/processed/database/candidates/raceform_v1_raw_mirror_candidate.sqlite3"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Independently reconcile every accepted Source Version 1 row "
            "to a complete disposable raw-mirror candidate."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Accepted immutable source SQLite file (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        default=DEFAULT_CANDIDATE,
        help=f"Disposable raw-mirror candidate (default: {DEFAULT_CANDIDATE})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1_000,
        help="Rows fetched from each database per validation batch (default: 1000)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = validate_raw_mirror_candidate(
        args.source,
        args.candidate,
        batch_size=args.batch_size,
    )
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
