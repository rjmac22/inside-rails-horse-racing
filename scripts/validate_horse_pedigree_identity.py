#!/usr/bin/env python3
"""Validate Notebook 19 horse and pedigree identity governance source-wide."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inside_rails.horse_pedigree_identity import (
    derive_identity_outputs,
    load_identity_governance,
    validate_expected_population,
)

SOURCE_DB = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
GOVERNANCE_REFERENCE = (
    PROJECT_ROOT / "data" / "reference" / "horse_pedigree_identity_governance.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "horse_pedigree_identity"


def _print_observed_funnel(outputs: object) -> None:
    counts = outputs.transition_governance["analytical_outcome"].value_counts()
    print("Observed horse and pedigree identity funnel:")
    print(f"  raw contradiction labels: {outputs.raw_contradiction_labels}")
    print(
        "  structured contradiction labels: "
        f"{outputs.structured_contradiction_labels}"
    )
    print(f"  structured pedigree rows: {len(outputs.structured_rows)}")
    print(f"  structured pedigree groups: {len(outputs.structured_groups)}")
    print(
        "  temporally separated horse labels: "
        f"{outputs.separated_groups['horse'].nunique()}"
    )
    print(f"  separated pedigree groups: {len(outputs.separated_groups)}")
    print(f"  governed transitions: {len(outputs.transition_governance)}")
    for outcome in ("Corrected", "Different horse", "Unresolved"):
        print(f"  {outcome}: {int(counts.get(outcome, 0))}")
    print(f"  provisional occurrences: {len(outputs.provisional_occurrences)}")


def main() -> None:
    governance = load_identity_governance(GOVERNANCE_REFERENCE)
    outputs = derive_identity_outputs(SOURCE_DB, GOVERNANCE_REFERENCE)
    _print_observed_funnel(outputs)
    validate_expected_population(outputs)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transition_path = OUTPUT_DIR / "transition_governance.csv"
    occurrence_path = OUTPUT_DIR / "provisional_horse_occurrences.csv"

    outputs.transition_governance.to_csv(transition_path, index=False)
    outputs.provisional_occurrences.to_csv(occurrence_path, index=False)

    transition_reload = pd.read_csv(transition_path)
    occurrence_reload = pd.read_csv(occurrence_path)

    assert len(transition_reload) == len(outputs.transition_governance)
    assert len(occurrence_reload) == len(outputs.provisional_occurrences)
    assert occurrence_reload["provisional_occurrence_id"].is_unique
    assert set(transition_reload["analytical_outcome"]) == {
        "Corrected",
        "Different horse",
    }
    assert not transition_reload["analytical_outcome"].eq("Unresolved").any()
    assert int(occurrence_reload["unresolved_boundaries"].sum()) == 0

    print("Horse and pedigree identity validation passed.")
    print(f"  specialist governance rows: {len(governance.rows)}")
    print(f"  wrote and reloaded: {transition_path.relative_to(PROJECT_ROOT)}")
    print(f"  wrote and reloaded: {occurrence_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
