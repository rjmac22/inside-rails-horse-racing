#!/usr/bin/env python3
"""Independently validate the Inside Rails Database v3 candidate."""

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

from inside_rails.database.external_reconciliation_candidate import (  # noqa: E402
    default_base_release_path,
    default_v3_candidate_path,
)
from inside_rails.database.external_reconciliation_validator import (  # noqa: E402
    validate_external_reconciliation_candidate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=default_v3_candidate_path(ROOT))
    parser.add_argument("--base-release", type=Path, default=default_base_release_path(ROOT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = validate_external_reconciliation_candidate(args.candidate, args.base_release)
    print(json.dumps(asdict(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
