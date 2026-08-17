from __future__ import annotations

from pathlib import Path
import runpy
import sys

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER = REPO_ROOT / "scripts" / "build_notebook_28_bha_historical_depth.py"
NOTEBOOK = REPO_ROOT / "notebooks" / "28_bha_historical_race_data_depth.ipynb"


def main() -> None:
    # Rebuild the governed notebook first. The builder preserves the user's previous
    # local Notebook 28 once in the ignored cache tree before replacing it.
    runpy.run_path(str(BUILDER), run_name="__main__")

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPO_ROOT)}},
        allow_errors=False,
    )

    print("Executing Notebook 28 autonomously...")
    try:
        client.execute()
    except Exception:
        # Preserve partial outputs as debugging evidence rather than discarding them.
        nbformat.write(notebook, NOTEBOOK)
        print(f"Notebook execution failed; partial outputs saved to {NOTEBOOK}", file=sys.stderr)
        raise

    nbformat.write(notebook, NOTEBOOK)
    print(f"Executed Notebook 28 saved to: {NOTEBOOK}")

    summary = (
        REPO_ROOT
        / "data"
        / "cache"
        / "bha_historical_race_data_depth"
        / "historical_depth_boundary_summary.json"
    )
    matrix = (
        REPO_ROOT
        / "data"
        / "cache"
        / "bha_historical_race_data_depth"
        / "historical_depth_probe_matrix.csv"
    )
    print(f"Boundary summary: {summary}")
    print(f"Probe matrix:     {matrix}")


if __name__ == "__main__":
    main()
