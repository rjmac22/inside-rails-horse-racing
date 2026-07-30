"""Append the procedural closeout cells required for Notebook 15.

This is a one-use repository maintenance script. It modifies the notebook JSON
through nbformat rather than requiring manual editing of a large ``.ipynb``
file. The appended cells:

- record the explicit manual-verification decision;
- persist a compact governed summary of the Notebook 15 conclusions;
- reload the persisted output;
- validate schema, uniqueness and expected decision rows.

Run from the repository root, then execute the appended notebook cells from a
fresh kernel as part of the normal closeout procedure.
"""

from __future__ import annotations

from pathlib import Path

import nbformat


NOTEBOOK_PATH = Path("notebooks/15_beaten_distance_semantics.ipynb")
MARKER = "NOTEBOOK_15_CLOSEOUT_PERSISTENCE_V1"


def main() -> None:
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK_PATH}")

    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)

    if any(MARKER in "".join(cell.get("source", "")) for cell in notebook.cells):
        raise RuntimeError("Notebook 15 closeout persistence cells already exist.")

    notebook.cells.append(
        nbformat.v4.new_markdown_cell(
            """## Closeout evidence and persisted outputs

**Manual-verification decision: `captured`.**

Notebook 15 used bounded external verification to distinguish amended results,
physical dead heats, omitted runners and confirmed source-distance defects.
Reusable provenance is preserved in `data/reference/manual_verifications.csv`
under verification IDs `NB15-BTN-0001` through `NB15-BTN-0017`.

The immutable source remains unchanged. External evidence permits only governed
downstream reconciliation, review classification or documented exception
handling.

The following cell persists a compact notebook decision table. This is not a
copy of bulk source data. It records the field-level conclusions, exception
rules and closeout evidence required by downstream implementation.

`NOTEBOOK_15_CLOSEOUT_PERSISTENCE_V1`
"""
        )
    )

    notebook.cells.append(
        nbformat.v4.new_code_cell(
            """# Persist the compact governed decision output for Notebook 15.
#
# Input grain:
#   One final notebook decision assembled from the completed investigation.
#
# Output grain:
#   One row per beaten-distance interpretation or governed exception rule.
#
# Raw versus derived:
#   This cell does not rewrite any source runner row. It persists only the
#   notebook's derived semantic decisions and their implementation status.
#
# Assumptions deliberately not made:
#   - `btn = 0` is not treated as proof of an official dead heat.
#   - positive winner distance is not automatically corrected.
#   - later zero overall distance is not automatically corrected.
#   - the text sentinel `-` is not converted to numeric zero.

from pathlib import Path

import pandas as pd


NOTEBOOK_15_OUTPUT_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "derived" / "notebook_15_beaten_distance_semantics"
)
NOTEBOOK_15_DECISIONS_PATH = (
    NOTEBOOK_15_OUTPUT_DIRECTORY / "beaten_distance_field_decisions.csv"
)

NOTEBOOK_15_OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

beaten_distance_field_decisions = pd.DataFrame(
    [
        {
            "decision_id": "NB15-DIST-001",
            "raw_field": "ovr_btn",
            "interpreted_meaning": (
                "cumulative distance from the source physical-finish "
                "first-place reference"
            ),
            "status": "confirmed",
            "implementation_action": "parse numeric values and preserve raw value",
            "limitation": (
                "official pos can reflect an amended result while distance "
                "continues to reflect the physical finish"
            ),
        },
        {
            "decision_id": "NB15-DIST-002",
            "raw_field": "btn",
            "interpreted_meaning": (
                "incremental margin from the preceding physical finisher or "
                "stored distance group"
            ),
            "status": "confirmed",
            "implementation_action": "parse numeric values and preserve raw value",
            "limitation": (
                "rounding, grouped margins and amendments can prevent simple "
                "official-position reconstruction"
            ),
        },
        {
            "decision_id": "NB15-DIST-003",
            "raw_field": "ovr_btn|btn",
            "interpreted_meaning": "text sentinel '-' means distance unavailable",
            "status": "confirmed",
            "implementation_action": "retain raw sentinel and derive null numeric value",
            "limitation": "do not convert the sentinel to zero",
        },
        {
            "decision_id": "NB15-DIST-004",
            "raw_field": "ovr_btn",
            "interpreted_meaning": (
                "positive value on official position 1 is an amended-result "
                "indicator or source anomaly"
            ),
            "status": "governed_exception",
            "implementation_action": "flag for review; do not silently correct",
            "limitation": "structure alone does not identify the permitted correction",
        },
        {
            "decision_id": "NB15-DIST-005",
            "raw_field": "ovr_btn",
            "interpreted_meaning": (
                "zero value on a later numeric position can indicate a demoted "
                "physical winner, physical dead heat or source defect"
            ),
            "status": "governed_exception",
            "implementation_action": "flag for review; use governed verification",
            "limitation": "diagnostic but not infallible",
        },
        {
            "decision_id": "NB15-DIST-006",
            "raw_field": "btn",
            "interpreted_meaning": (
                "zero with positive overall distance indicates membership of "
                "a same-distance group"
            ),
            "status": "confirmed_with_limitation",
            "implementation_action": "derive same-distance-group flag",
            "limitation": "does not by itself prove an official dead heat",
        },
        {
            "decision_id": "NB15-DIST-007",
            "raw_field": "ovr_btn|btn",
            "interpreted_meaning": "verified contradictions remain raw-source evidence",
            "status": "required",
            "implementation_action": (
                "apply corrections only through governed downstream reconciliation "
                "with verification provenance"
            ),
            "limitation": "immutable source values must never be overwritten",
        },
    ]
)

required_decision_columns = {
    "decision_id",
    "raw_field",
    "interpreted_meaning",
    "status",
    "implementation_action",
    "limitation",
}

if set(beaten_distance_field_decisions.columns) != required_decision_columns:
    raise ValueError("Notebook 15 decision output has an unexpected schema.")

if beaten_distance_field_decisions["decision_id"].duplicated().any():
    raise ValueError("Notebook 15 decision IDs must be unique.")

beaten_distance_field_decisions.to_csv(
    NOTEBOOK_15_DECISIONS_PATH,
    index=False,
)

print(
    f"Wrote {len(beaten_distance_field_decisions)} decisions to "
    f"{NOTEBOOK_15_DECISIONS_PATH.relative_to(REPOSITORY_ROOT)}"
)
"""
        )
    )

    notebook.cells.append(
        nbformat.v4.new_code_cell(
            """# Reload and validate the persisted Notebook 15 decision output.
#
# Purpose:
#   The notebook wrap-up procedure requires every written file to be reloaded
#   and validated rather than trusting the in-memory dataframe.
#
# Output grain:
#   One persisted decision row per governed beaten-distance rule.

reloaded_beaten_distance_field_decisions = pd.read_csv(
    NOTEBOOK_15_DECISIONS_PATH,
    keep_default_na=False,
)

if len(reloaded_beaten_distance_field_decisions) != 7:
    raise ValueError(
        "Expected seven persisted Notebook 15 decisions, "
        f"found {len(reloaded_beaten_distance_field_decisions)}."
    )

if set(reloaded_beaten_distance_field_decisions.columns) != required_decision_columns:
    raise ValueError("Reloaded Notebook 15 decision schema is invalid.")

if reloaded_beaten_distance_field_decisions["decision_id"].duplicated().any():
    raise ValueError("Reloaded Notebook 15 decision IDs are not unique.")

expected_statuses = {
    "confirmed",
    "confirmed_with_limitation",
    "governed_exception",
    "required",
}
observed_statuses = set(reloaded_beaten_distance_field_decisions["status"])

if not observed_statuses <= expected_statuses:
    raise ValueError(
        "Reloaded Notebook 15 decisions contain an invalid status: "
        f"{sorted(observed_statuses - expected_statuses)}"
    )

display(reloaded_beaten_distance_field_decisions)
"""
        )
    )

    nbformat.write(notebook, NOTEBOOK_PATH)
    print(f"Appended Notebook 15 closeout cells to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
