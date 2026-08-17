from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap


LEGACY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = LEGACY_ROOT.parent / "inside-rails-bha"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(command))
    return subprocess.run(command, cwd=cwd, check=check, text=True)


def scaffold(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise RuntimeError(f"Target already exists and is not empty: {target}")

    target.mkdir(parents=True, exist_ok=True)

    for directory in [
        "data/raw/bha",
        "data/cache",
        "data/derived/parquet",
        "data/reference",
        "data/warehouse",
        "docs",
        "notebooks",
        "reports",
        "scripts",
        "src/inside_rails",
        "tests",
    ]:
        (target / directory).mkdir(parents=True, exist_ok=True)

    source_client = LEGACY_ROOT / "src" / "inside_rails" / "bha_api.py"
    source_tests = LEGACY_ROOT / "tests" / "test_bha_api.py"
    if not source_client.is_file() or not source_tests.is_file():
        raise RuntimeError("Trusted BHA client/test files are missing from the legacy project")

    shutil.copy2(source_client, target / "src" / "inside_rails" / "bha_api.py")
    shutil.copy2(source_tests, target / "tests" / "test_bha_api.py")
    write_text(target / "src" / "inside_rails" / "__init__.py", '"""Inside Rails BHA-first research package."""\n')

    write_text(
        target / ".gitignore",
        r'''
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ipynb_checkpoints/
.DS_Store

# Local BHA/raw analytical data are intentionally not committed.
data/raw/bha/**
data/cache/**
data/derived/parquet/**
data/warehouse/**

# Keep small governed reference material under data/reference tracked.
!data/reference/
!data/reference/**
''',
    )

    write_text(
        target / "pyproject.toml",
        r'''
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "inside-rails-bha"
version = "0.1.0"
description = "BHA-first official-source horse-racing research and local analytics"
requires-python = ">=3.12"
dependencies = [
    "duckdb>=1.1",
    "ipykernel>=6.29",
    "nbclient>=0.10",
    "nbformat>=5.10",
    "pandas>=2.2",
    "pyarrow>=17",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
''',
    )

    write_text(
        target / "README.md",
        r'''
# Inside Rails — BHA-first

This is the successor research project to `inside-rails-horse-racing`.

The architectural reset is deliberate:

- **British Horseracing Authority material is the authoritative source for official Great Britain racing facts.**
- the legacy Inside Rails Database v4 is optional enrichment/reconciliation evidence only;
- raw BHA responses are cached locally and preserved immutably;
- source-shaped local analytical datasets are written as Parquet;
- DuckDB provides fast SQL over local Parquet rather than forcing an early monolithic database schema;
- governed analytical concepts are added only after their source semantics are established.

The old repository is not deleted or rewritten. It remains the historical research lineage that established why this reset is justified.

## Source flow

```text
BHA public/official sources
        |
        v
immutable local response archive
        |
        v
source-shaped Parquet datasets
        |
        +--------------------------+
        |                          |
        v                          v
DuckDB analytical views      governed semantic layers
        |                          |
        +-------------+------------+
                      v
              research / modelling

Legacy Database v4 ---------> optional enrichment only
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
python scripts/check_project.py
```

## First research programme

The first notebooks should answer, in order:

1. What BHA source families are required for a durable local GB racing archive?
2. What is the minimum safe one-time historical acquisition strategy?
3. What race-level predicate identifies a realised official result across the required period?
4. How should raw BHA source objects be materialised into source-shaped Parquet without inventing semantics?
5. Only then: which legacy v4 fields are worth joining back as enrichment?

Every bounded problem uses the autonomous governed notebook workflow in `NOTEBOOK_WORKING_RULES.md`.
''',
    )

    write_text(
        target / "PROJECT_RULES.md",
        r'''
# Inside Rails BHA-first project rules

## 1. Source authority

For official Great Britain racing facts, the British Horseracing Authority is the primary authoritative source.

Legacy Inside Rails Database v4 is **not** the population authority in this project. It may be used only as optional enrichment, reconciliation evidence, anomaly discovery, or historical comparison where its limitations are explicit.

A legacy value must never silently override conflicting BHA official evidence.

## 2. Raw source preservation

Every external BHA response used by the project must be cached with request/provenance metadata. Raw responses are immutable evidence.

Do not clean, normalise, repair or overwrite raw source material in place.

## 3. Local-first analytics

Acquisition may use live BHA resources. Routine analysis should not depend on live HTTP requests.

Durable source-shaped analytical extracts should be stored locally as Parquet. DuckDB should query those files directly or expose rebuildable views over them.

## 4. Source-shaped before canonical

Do not design a grand canonical racing schema before the source objects and their semantics are understood.

Preserve BHA fixture, race, result, runner, going, official and other source families at their natural grains first. Governed analytical concepts may be layered on later.

## 5. Semantics are evidence, not field names

Names such as `resultsAvailable`, `abandonedReasonCode`, `finishTime`, `maxRunners`, `winnersDetails` or any future field are not semantic contracts by themselves.

Each consequential interpretation must be tested against source behaviour and contradiction cases.

## 6. Identity

Preserve BHA identifiers exactly as external provenance. Do not invent Inside Rails canonical identities until a downstream decision actually requires them and the evidence supports the mapping.

## 7. Enrichment boundary

Legacy Database v4 and any other secondary source may supply information missing from BHA, but enrichment must record:

- source;
- original value;
- join method;
- confidence/validation state;
- whether the field is allowed for substantive analysis.

## 8. Database policy

There is no Database v5 inheritance requirement.

Parquet + DuckDB is the default analytical architecture. A persistent relational database should be introduced only if a concrete workload needs one.

## 9. Research workflow

Each bounded problem should become a self-contained notebook with Markdown explaining the question, source hierarchy, method, controls, limitations and decision logic, plus commented code showing exactly how the evidence was produced.

Autonomous execution is the default where the method can be governed safely in advance.
''',
    )

    write_text(
        target / "NOTEBOOK_WORKING_RULES.md",
        r'''
# Inside Rails BHA-first notebook working rules

## Purpose

Notebooks are executable research records, not disposable scratchpads.

## Autonomous governed mode — default

For each bounded problem:

1. state one precise question;
2. identify the exact BHA/source family and observation grain;
3. explain the evidence hierarchy and candidate interpretations in Markdown before testing them;
4. reuse project modules for stable transport/cache/storage plumbing;
5. comment every code cell for a future reader, including what it reads, requests, derives and writes;
6. cache every external response, including empty/error states;
7. start with cheap controls and contradiction tests before scaling acquisition;
8. keep observation, inference, decision and unresolved state distinct;
9. compile-check generated code and round-trip generated notebooks before live requests;
10. save partial outputs on execution failure;
11. derive conclusions from executed evidence, not expected answers;
12. audit the executed notebook before closeout;
13. when the notebook reveals a different next question, close it and open another bounded notebook.

## Interactive mode

Use one-cell-at-a-time interaction only when unforeseen evidence genuinely requires human interpretation before the next method can be specified safely.

## Data safety

- raw BHA cache: immutable;
- Parquet: derived/source-shaped and reproducible;
- DuckDB: rebuildable analytical catalog/views;
- legacy Database v4: read-only optional enrichment;
- no notebook may silently rewrite source evidence.

## Completion

A notebook is complete only when it states:

- what was established;
- what was falsified;
- what remains unresolved;
- exact artifacts created;
- whether the result changes source usage or analytics;
- the next bounded question, if any.
''',
    )

    write_text(
        target / "docs" / "SOURCE_HIERARCHY.md",
        r'''
# Source hierarchy

## Tier 1 — authoritative official evidence

British Horseracing Authority structured resources and official published BHA material are the primary authority for official Great Britain racing facts.

Different BHA source families remain separate evidence layers. A fixture index, fixture detail, race list, race detail and result resource are not assumed to mean the same thing.

## Tier 2 — other official/governance sources

Other official bodies may govern specialised facts where appropriate, for example regulatory/statutory or levy material. Their authority is scoped to the fact they govern.

## Tier 3 — legacy Inside Rails Database v4

Legacy v4 is a secondary enrichment/reconciliation source only.

Known limitation inherited from the predecessor project: the third-party source population used to build v4 is materially incomplete for some GB racing in 2020. Therefore v4 cannot define the complete official race population.

## Tier 4 — other secondary/public/commercial sources

Use only where they add information not available from the authoritative source family. Preserve provenance and do not silently promote them to official truth.

## Conflict rule

Where a secondary source conflicts with authoritative BHA evidence on an official British racing fact, preserve the conflict and use the BHA value for the official fact unless later evidence shows the BHA source family itself is not authoritative for that concept.
''',
    )

    write_text(
        target / "docs" / "ARCHITECTURE.md",
        r'''
# Local data architecture

## Goal

Make acquisition reproducible and analysis fast without prematurely designing another monolithic canonical database.

## Layers

### 1. Immutable response archive

`data/raw/bha/` and/or governed cache namespaces preserve exact BHA responses plus request/provenance metadata.

These files are evidence, not analysis tables.

### 2. Source-shaped Parquet

`data/derived/parquet/`

Materialise source families at their natural grains, for example:

- fixture discovery observations;
- fixture detail;
- fixture race lists;
- race detail;
- official race results;
- runner result rows;
- going/history;
- officials;
- later source families as justified.

The first Parquet form should preserve source fields rather than prematurely rename them into business concepts.

### 3. DuckDB analytical catalog

`data/warehouse/inside_rails.duckdb`

DuckDB should mostly provide views/macros/catalog metadata over Parquet. The database file is rebuildable and is not the source of truth.

### 4. Governed semantic datasets

Only after field semantics are established should the project create analytical concepts such as realised race, governed racecourse/course identity, actual result population, or modelling features.

### 5. Optional enrichment

Legacy v4 may be joined through explicit reconciliation views/tables when it contributes useful information not available from BHA.

## Why this design

- fast local analytics;
- no repeated live HTTP dependency;
- immutable source lineage;
- columnar storage suited to scans/grouping/modelling;
- DuckDB can query Parquet directly;
- source families can evolve independently;
- avoids spending weeks repairing a third-party schema into an artificial canonical model.
''',
    )

    write_text(
        target / "docs" / "INHERITED_FINDINGS.md",
        r'''
# Inherited findings from the predecessor project

These findings explain the reset. They are carried forward as established constraints, while new acquisition/storage implementation begins from scratch.

## Legacy project

Repository: `rjmac22/inside-rails-horse-racing`

Accepted legacy analytical release: Database v4.

## High-confidence inherited findings

1. The legacy third-party source is materially incomplete for Great Britain in parts of 2020; Database v4 inherited that omission.
2. The current BHA public structured estate exposes fixture, race and official result resources sufficient for official-source reconciliation.
3. Fixture-search `resultsAvailable=true` is not a safe semantic completed-racing predicate.
4. A programmed race can survive in a fixture race-list for an abandoned fixture.
5. Worcester, 25 September 2020 provided a concrete race-level counterexample: race `2020:8816:0` remained programmed with race-list `abandonedReasonCode = 0`, while race-detail `resultsAvailable = 0` and the dedicated results endpoint returned no official result.
6. In the 27 May 2026 completed-race control, fixture-race-list non-empty `winnersDetails` and race-detail `resultsAvailable == 1` agreed with the 34 known official-result races.
7. Race-detail `winnersDetails` is not a reliable realised-race signal: it was absent on the completed-race controls inspected in the predecessor project.
8. Historical BHA source depth varies by resource family; do not describe the whole estate with one start date.

## Carry-forward rule

These findings constrain early design decisions, but the new project should re-demonstrate any rule before using it as a population-wide production predicate.
''',
    )

    write_text(
        target / "docs" / "PROJECT_PLAN.md",
        r'''
# Project plan

## Objective

Build a local, reproducible BHA-first Great Britain racing research archive suitable for fast analytics, then use legacy/secondary data only as enrichment where it adds value.

## Phase 0 — source contract and local architecture

- verify the BHA access/client behaviour in the new repo;
- define cache/acquisition manifest conventions;
- inventory the BHA source families required for the first analytical population;
- establish Parquet and DuckDB storage conventions.

## Phase 1 — realised-race population rule

Use a bounded notebook to re-establish and then population-validate the cheapest reliable race-level signal against authoritative result evidence.

Do not acquire the full historical archive before the required source families and predicate are understood.

## Phase 2 — historical official archive

Acquire the minimum source families required for the agreed period, preserving raw responses and producing source-shaped Parquet.

Acquisition must be restartable, cached, manifest-driven and auditable.

## Phase 3 — local analytical catalog

Create DuckDB views over the Parquet layers and validate population counts, keys, null states and source-family relationships.

## Phase 4 — source semantics studies

Study BHA fields/source families directly in bounded autonomous notebooks. Govern concepts before using them analytically.

## Phase 5 — legacy enrichment

Only after the official BHA base is stable, inspect legacy v4 field-by-field for useful enrichment unavailable from BHA. Join selectively and preserve the secondary-source status.

## Phase 6 — reader studies and modelling

Run analytical studies locally. Modelling should use governed local features, not live API calls and not mystery source columns.
''',
    )

    write_text(
        target / "notebooks" / "README.md",
        r'''
# Notebook programme

Use sequential notebooks for bounded source/correctness questions.

Suggested opening sequence:

- `00_bha_source_contract_and_local_storage.ipynb`
- `01_realised_race_predicate_validation.ipynb`
- `02_historical_acquisition_design.ipynb`
- `03_local_archive_population_validation.ipynb`

Do not create later notebooks until the preceding question has actually been answered.
''',
    )

    write_text(
        target / "scripts" / "check_project.py",
        r'''
from __future__ import annotations

from pathlib import Path
import importlib


ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "README.md",
    ROOT / "PROJECT_RULES.md",
    ROOT / "NOTEBOOK_WORKING_RULES.md",
    ROOT / "docs" / "SOURCE_HIERARCHY.md",
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "src" / "inside_rails" / "bha_api.py",
]

missing = [str(path) for path in required if not path.exists()]
if missing:
    raise SystemExit("Missing required project files:\n" + "\n".join(missing))

for module in ["duckdb", "pandas", "pyarrow", "nbformat", "nbclient", "inside_rails.bha_api"]:
    importlib.import_module(module)
    print(f"PASS import {module}")

print(f"PASS project root {ROOT}")
print("Project structure and core imports are ready.")
''',
    )

    write_text(target / "data" / "reference" / ".gitkeep", "")
    write_text(target / "reports" / ".gitkeep", "")


def initialise_git(target: Path) -> None:
    run(["git", "init", "-b", "main"], cwd=target)
    run(["git", "add", "."], cwd=target)
    run(
        [
            "git",
            "commit",
            "-m",
            "Initialize BHA-first Inside Rails project",
        ],
        cwd=target,
    )


def maybe_create_github(target: Path, repo_name: str) -> None:
    gh = shutil.which("gh")
    if gh is None:
        print("\nGitHub CLI not found; local repository is complete.")
        print(f"Create a private GitHub repo named {repo_name!r}, then add it as origin and push main.")
        return

    auth = subprocess.run(
        [gh, "auth", "status"],
        cwd=target,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if auth.returncode != 0:
        print("\nGitHub CLI is installed but not authenticated; local repository is complete.")
        print("Run `gh auth login` later, then create/push the remote.")
        return

    result = subprocess.run(
        [
            gh,
            "repo",
            "create",
            repo_name,
            "--private",
            "--source=.",
            "--remote=origin",
            "--push",
            "--description",
            "Inside Rails BHA-first official-source horse-racing research",
        ],
        cwd=target,
        text=True,
    )
    if result.returncode != 0:
        print("\nAutomatic GitHub repository creation failed; local repository is still complete.")
        print("Create the remote manually later; no local work was lost.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a fresh BHA-first Inside Rails sibling project"
    )
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--repo-name", default="inside-rails-bha")
    parser.add_argument(
        "--no-github",
        action="store_true",
        help="Do not attempt GitHub CLI repository creation even if gh is available",
    )
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    print(f"Legacy project: {LEGACY_ROOT}")
    print(f"New project:    {target}")

    scaffold(target)
    initialise_git(target)

    if not args.no_github:
        maybe_create_github(target, args.repo_name)

    print("\nBHA-first Inside Rails project created successfully.")
    print(f"cd {target}")
    print("python -m venv .venv")
    print("source .venv/bin/activate")
    print("python -m pip install -e '.[dev]'")
    print("pytest -q")
    print("python scripts/check_project.py")


if __name__ == "__main__":
    main()
