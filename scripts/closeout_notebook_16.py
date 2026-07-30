#!/usr/bin/env python3
"""Run the focused local validation required to close Notebook 16.

The script deliberately avoids the complete repository suite and all-validator
sweep, which remain deferred until the end of the source-field series or repair
branch. Use ``--skip-notebook`` when the notebook has already completed a fresh-
kernel execution and only the downstream checks need to be retried.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = PROJECT_ROOT / "notebooks/16_race_classification_and_eligibility.ipynb"
DECISIONS = (
    PROJECT_ROOT
    / "data/derived/notebook_16_race_classification_and_eligibility"
    / "race_classification_field_decisions.csv"
)
EXPECTED_FIELDS = {
    "race_name",
    "type",
    "class",
    "pattern",
    "rating_band",
    "age_band",
    "sex_rest",
}


def run(command: list[str]) -> None:
    """Run one closeout command from the repository root and fail loudly."""

    print(f"\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def validate_persisted_decisions() -> None:
    """Reload the governed decision table and validate its bounded contract."""

    if not DECISIONS.is_file():
        raise FileNotFoundError(f"Missing persisted Notebook 16 decisions: {DECISIONS}")

    with DECISIONS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    required_columns = {
        "field",
        "source_meaning",
        "safe_derived_treatment",
        "unresolved_or_unsafe_treatment",
        "status",
    }
    actual_columns = set(rows[0]) if rows else set()
    if actual_columns != required_columns:
        raise AssertionError(
            f"Unexpected decision columns: expected {required_columns}, got {actual_columns}."
        )

    actual_fields = {row["field"] for row in rows}
    if actual_fields != EXPECTED_FIELDS:
        raise AssertionError(
            f"Unexpected governed fields: expected {EXPECTED_FIELDS}, got {actual_fields}."
        )

    if len(rows) != len(EXPECTED_FIELDS):
        raise AssertionError(
            f"Expected {len(EXPECTED_FIELDS)} decision rows, got {len(rows)}."
        )

    for row in rows:
        for column in required_columns:
            if not row[column].strip():
                raise AssertionError(
                    f"Blank required decision value for field={row['field']!r}, "
                    f"column={column!r}."
                )

    print(
        "Persisted Notebook 16 decision table reloaded successfully: "
        f"{len(rows)} governed fields."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-notebook",
        action="store_true",
        help="Do not execute or rewrite the notebook; run only persisted-output, test and validator checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not NOTEBOOK.is_file():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK}")

    if args.skip_notebook:
        print(
            "Notebook execution skipped; preserving the already executed local notebook.",
            flush=True,
        )
    else:
        run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=900",
                str(NOTEBOOK.relative_to(PROJECT_ROOT)),
            ]
        )

    validate_persisted_decisions()

    run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_race_classification.py",
            "tests/test_manual_verifications.py",
        ]
    )

    run([sys.executable, "scripts/validate_race_classification.py"])
    run([sys.executable, "scripts/validate_manual_verifications.py"])

    print(
        "\nNotebook 16 focused closeout validation passed. "
        "The complete repository suite remains deferred by project policy."
    )


if __name__ == "__main__":
    main()
