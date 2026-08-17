from __future__ import annotations

from pathlib import Path
import runpy
import sys

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER = REPO_ROOT / "scripts" / "build_notebook_28_bha_historical_depth.py"
NOTEBOOK = REPO_ROOT / "notebooks" / "28_bha_historical_race_data_depth.ipynb"


def _promote_generated_conclusion(notebook) -> None:
    """Replace the placeholder Markdown cell with the executed evidence conclusion."""
    generator = None
    target = None

    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        if "conclusion-generator" in tags:
            generator = cell
        if "generated-conclusion" in tags:
            target = cell

    if generator is None or target is None:
        raise RuntimeError("Notebook 28 conclusion cells are missing expected tags.")

    markdown = None
    for output in generator.get("outputs", []):
        if output.get("output_type") not in {"display_data", "execute_result"}:
            continue
        value = output.get("data", {}).get("text/markdown")
        if value is None:
            continue
        markdown = "".join(value) if isinstance(value, list) else str(value)
        break

    if not markdown:
        raise RuntimeError("Notebook 28 did not emit an evidence-derived Markdown conclusion.")

    target.source = markdown.rstrip() + "\n"


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
        _promote_generated_conclusion(notebook)
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
