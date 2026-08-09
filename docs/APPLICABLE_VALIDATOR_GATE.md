# Applicable Independent Validator Gate

## Purpose

This document is the permanent re-runnable procedure for the project-level independent-validator gate required by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

It exists because earlier repository gates proved that a generic loop over `scripts/validate_*.py` is unsafe and incomplete: validators do not all have the same command-line contract. Some accept no positional input because they resolve governed project paths internally, while others require the immutable Source Version 1 SQLite path. Historical Database v1 construction validators also depend on disposable artefacts that are no longer acceptance dependencies.

The canonical runner is:

```text
scripts/run_applicable_validators.py
```

Do not reconstruct an ad-hoc shell loop from validator filenames.

## Canonical command

From the repository root with the project virtual environment active:

```bash
python scripts/run_applicable_validators.py
```

The runner:

- discovers the sorted `scripts/validate_*.py` inventory;
- requires the governed inventory count to remain exactly 34 until deliberately reviewed;
- excludes exactly three historical Database v1 construction-only validators;
- inspects each applicable validator's `argparse.add_argument(...)` declarations using the Python AST without importing or executing the validator;
- resolves required source-database positional inputs to the exact immutable Source Version 1 path;
- resolves a required `reference_path`, should one exist, to the governed course-location reference;
- fails before executing the gate if a validator introduces an unknown required positional argument;
- runs with `PYTHONPATH` explicitly containing `src`;
- runs validators in deterministic filename order;
- stops at the first genuine validator failure;
- captures normal validator output and prints compact `PASS` lines;
- prints the final validator output on failure;
- never enables `set -e`, `set -u` or `pipefail` in the caller's interactive shell;
- never invokes a shell subprocess with `shell=True`.

A validator failure returns a non-zero status from the Python runner. It does not issue an `exit` command to the user's interactive shell.

## Governed inputs

Immutable Source Version 1:

```text
data/raw/form_2015-present/form_2015-present/raceform.db
```

Governed course-location reference when a required `reference_path` is present:

```text
data/reference/course_locations.csv
```

Validators with optional positional arguments keep their own repository-governed defaults; the runner does not redundantly override them.

## Explicit exclusions

Only these validators are excluded from the current release-acceptance sweep:

```text
validate_core_structure_prototype.py
validate_raw_mirror_candidate.py
validate_minimum_core_candidate.py
```

They are historical Database v1 construction-stage validators that require disposable prototype/candidate artefacts no longer present and are not dependencies of Database v2 or v3 acceptance. Their exclusion is already part of the Database v2 release record and remains explicit rather than being silently skipped.

Every other current `validate_*.py` script is applicable. With the present inventory this means:

```text
34 validator scripts
- 3 historical construction-only exclusions
= 31 applicable independent validators
```

## Inspection mode

To inspect the exact planned commands and exclusions without executing any validator:

```bash
python scripts/run_applicable_validators.py --list
```

Inspection mode is the preferred diagnostic when a validator CLI changes. The runner must be updated and tested before changing the governed argument map or inventory baseline.

## Acceptance use

For a database release, the normal final technical sequence is:

```bash
pytest -q
python scripts/run_applicable_validators.py
python scripts/validate_inside_rails_v3.py
```

The final standalone Database v3 validator is intentionally repeated after the complete sweep at the release boundary so the exact candidate is explicitly revalidated immediately before promotion.

For future database versions, replace only that final version-specific standalone validation command after the successor release contract defines it. Do not change the project-wide validator runner merely because the accepted database version changes.

## Historical reason this is permanent

The Phase 4 final repository gate on 6 August 2026 exposed three harness errors before the successful all-validator run:

1. an interactive shell was put under `set -euo pipefail`, allowing a failure to terminate that shell;
2. a generic runner omitted required positional database arguments, demonstrated by `validate_beaten_distances.py` correctly rejecting the invocation;
3. a runner omitted `PYTHONPATH=src`, causing a validator import failure.

Those were harness defects, not validator defects. The final corrected Phase 4 sweep passed all 31 then-current validators. The same class of mistake recurred during the Database v3 acceptance work on 9 August 2026 when a generic filename loop again invoked `validate_beaten_distances.py` without its required database argument.

The repository now treats the runner itself as governed implementation, with focused tests, so this procedure does not need to be rediscovered in a later study or release.

## Change rule

If a validator is added, removed, renamed, changes required positional arguments, or becomes non-applicable:

1. do not edit a count merely to make the runner pass;
2. explain the applicability change;
3. update `scripts/run_applicable_validators.py` deliberately;
4. update its focused tests;
5. update this document when the governed procedure changes;
6. rerun focused tests, the complete repository suite and the complete applicable validator gate before release acceptance.
