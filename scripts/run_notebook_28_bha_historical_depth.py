from __future__ import annotations

import os
from pathlib import Path
import runpy
import shutil
import sys

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
BUILDER = REPO_ROOT / "scripts" / "build_notebook_28_bha_historical_depth.py"
NOTEBOOK = REPO_ROOT / "notebooks" / "28_bha_historical_race_data_depth.ipynb"
CACHE_DIR = REPO_ROOT / "data" / "cache" / "bha_historical_race_data_depth"
BACKUP = CACHE_DIR / "notebook_28_pre_autonomous_backup.ipynb"


def _prepare_repo_pythonpath() -> None:
    """Expose this src-layout repository to both the runner and spawned kernel.

    Pytest already gets ``src`` from ``pyproject.toml``. A standalone Jupyter kernel
    does not inherit pytest's pythonpath setting, so Notebook 28 needs the same repo
    package root supplied explicitly before nbclient launches the kernel.
    """
    src_text = str(SRC_DIR)

    if src_text not in sys.path:
        sys.path.insert(0, src_text)

    existing = os.environ.get("PYTHONPATH", "")
    existing_parts = [part for part in existing.split(os.pathsep) if part]
    if src_text not in existing_parts:
        os.environ["PYTHONPATH"] = os.pathsep.join([src_text, *existing_parts])

    # Parent-process preflight: fail before notebook execution if repository imports
    # are still not resolvable for any unexpected environment reason.
    from inside_rails.bha_api import ACCESS_PROFILE

    print(f"Repository src path: {SRC_DIR}")
    print(f"BHA client import preflight: PASS ({ACCESS_PROFILE})")


def _build_checked_notebook():
    """Build Notebook 28 without invoking the builder's standalone main()."""
    namespace = runpy.run_path(str(BUILDER), run_name="_notebook28_builder")
    notebook = namespace["build_notebook"]()

    # The first plain-string generator version interpreted two embedded ``\n``
    # sequences before they reached generated code cells. Normalise those generated
    # sources here, then compile every code cell before Notebook 28 is replaced.
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue

        source = cell.source
        source = source.replace('print("\n', 'print("\\n')
        source = source.replace(
            'conclusion = "\n".join',
            'conclusion = "\\n".join',
        )

        # Treat a race that cannot be addressed through the upstream public race-list
        # reference as non-usable for transition refinement, while preserving the
        # distinct ``not_addressable`` label in the evidence matrix.
        source = source.replace(
            'return value in {"absent_404", "success_empty"}',
            'return value in {"absent_404", "success_empty", "not_addressable"}',
        )

        cell.source = source

    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook28-cell-{index}", "exec")

    return notebook


def _write_checked_notebook(notebook) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if NOTEBOOK.exists() and not BACKUP.exists():
        shutil.copy2(NOTEBOOK, BACKUP)
        print(f"Backed up existing Notebook 28 to: {BACKUP}")

    nbformat.write(notebook, NOTEBOOK)

    # Round-trip through nbformat and compile again. This catches malformed notebook
    # JSON or source transformations before any live BHA request is made.
    checked = nbformat.read(NOTEBOOK, as_version=4)
    for index, cell in enumerate(checked.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook28-roundtrip-cell-{index}", "exec")

    print(f"Built Notebook 28: {NOTEBOOK}")
    print(f"Cells: {len(checked.cells)}")
    print("Generated code-cell compile check: PASS")
    print("Notebook round-trip check: PASS")


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
    _prepare_repo_pythonpath()

    notebook = _build_checked_notebook()
    _write_checked_notebook(notebook)

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
        print(
            f"Notebook execution failed; partial outputs saved to {NOTEBOOK}",
            file=sys.stderr,
        )
        raise

    nbformat.write(notebook, NOTEBOOK)
    print(f"Executed Notebook 28 saved to: {NOTEBOOK}")

    summary = CACHE_DIR / "historical_depth_boundary_summary.json"
    matrix = CACHE_DIR / "historical_depth_probe_matrix.csv"
    year_matrix = CACHE_DIR / "historical_depth_year_matrix.csv"

    print(f"Boundary summary: {summary}")
    print(f"Probe matrix:     {matrix}")
    print(f"Year matrix:      {year_matrix}")


if __name__ == "__main__":
    main()
