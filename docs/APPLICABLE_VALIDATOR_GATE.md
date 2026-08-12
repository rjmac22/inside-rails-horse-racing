# Applicable Independent Validator Gate

## Purpose

This document is the permanent re-runnable procedure for the project-level independent-validator gate required by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

It exists because earlier repository gates proved that a generic loop over `scripts/validate_*.py` is unsafe and incomplete: validators do not all have the same command-line contract. Some accept no required positional input because they resolve governed project paths internally, while others require the immutable Source Version 1 SQLite path. Historical Database v1 construction validators also depend on disposable artefacts that are no longer acceptance dependencies.

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
- requires the governed inventory count to remain exactly 35 until deliberately reviewed;
- excludes exactly three historical Database v1 construction-only validators;
- inspects each applicable validator's `argparse.add_argument(...)` declarations using the Python AST without importing or executing the validator;
- resolves required source-database positional inputs to the exact immutable Source Version 1 path;
- resolves a required `reference_path`, should one exist in a future governed CLI, to the governed course-location reference;
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

Governed course-location reference if a future required `reference_path` is introduced:

```text
data/reference/course_locations.csv
```

Validators with optional positional arguments or optional flags keep their own repository-governed defaults; the runner does not redundantly override them.

## Exact current argument map

The current repository contains 35 `validate_*.py` scripts. Eleven applicable validators require the immutable Source Version 1 path as a positional argument:

| Validator | Required positional input |
|---|---|
| `validate_beaten_distances.py` | `database` → Source Version 1 |
| `validate_course_jurisdiction.py` | `database` → Source Version 1 |
| `validate_field_governance.py` | `database` → Source Version 1 |
| `validate_jurisdiction_context.py` | `database` → Source Version 1 |
| `validate_off_time.py` | `database` → Source Version 1 |
| `validate_race_identity.py` | `database` → Source Version 1 |
| `validate_race_results.py` | `database` → Source Version 1 |
| `validate_race_surface.py` | `database` → Source Version 1 |
| `validate_source_fields.py` | `database` → Source Version 1 |
| `validate_source_profile.py` | `database` → Source Version 1 |
| `validate_starting_price.py` | `database` → Source Version 1 |

The other 21 applicable validators currently have no required positional input. They use their own governed defaults or validate self-contained governed artefacts:

```text
validate_carried_weight.py
validate_comment_information.py
validate_connection_identity.py
validate_course_locations.py
validate_course_locations_source.py
validate_horse_pedigree_identity.py
validate_inside_rails_v2_implementation.py
validate_inside_rails_v2.py
validate_inside_rails_v3.py
validate_inside_rails_v4.py
validate_manual_verifications.py
validate_participant_identity.py
validate_prize_money.py
validate_race_classification.py
validate_race_distance.py
validate_race_times.py
validate_ratings.py
validate_runner_characteristics.py
validate_runner_entries.py
validate_runner_entries_source.py
validate_runner_record_supplementations.py
```

This mapping is executable governance, not prose only: `data/tests/test_applicable_validator_gate.py` requires the runner to parse the live validator CLIs and fail if an ungoverned required positional argument appears.

## Historical version-specific reference binding

Historical database validators must validate a release against the evidence snapshot that actually governed that release. They must not silently reinterpret an older database against later mutable reference additions.

Database v2 was built and accepted from repository/reference commit:

```text
68ac0364c4af2a104ea76c8765fd0e220aaf8e84
```

`validate_inside_rails_v2.py` therefore replays the following four reference files from that exact Git commit into a temporary read-only validation root before invoking the independent v2 validator:

```text
data/reference/manual_verifications.csv
data/reference/connection_identity_repairs.csv
data/reference/runner_record_supplementations.csv
data/reference/horse_pedigree_identity_governance.csv
```

That historical snapshot contains the 85 manual-verification rows recorded in the Database v2 release contract. Later additions to the working-tree reference files are valid inputs to later database versions, but they must not retroactively change the v2 validation baseline.

`data/tests/test_inside_rails_v2_historical_validator.py` fails closed if the historical commit, file set or 85-row v2 baseline changes or becomes unavailable.

## Explicit exclusions

Only these three validators are excluded from the current release-acceptance sweep:

| Validator | Reason |
|---|---|
| `validate_core_structure_prototype.py` | Historical Database v1 construction-only validator requiring disposed prototype artefacts. |
| `validate_raw_mirror_candidate.py` | Historical Database v1 construction-only validator requiring the disposed raw-mirror candidate. |
| `validate_minimum_core_candidate.py` | Historical Database v1 construction-only validator requiring the disposed minimum-core candidate. |

They are not dependencies of Database v2, v3 or v4 acceptance. Their exclusion is already part of the Database v2 release record and remains explicit rather than being silently skipped.

Current governed arithmetic:

```text
35 validator scripts
- 3 historical construction-only exclusions
= 32 applicable independent validators
```

## Inspection mode

To inspect the exact commands and exclusions without executing any validator:

```bash
python scripts/run_applicable_validators.py --list
```

Inspection mode is the preferred diagnostic when a validator CLI changes. The runner must be updated and tested before changing the governed argument map or inventory baseline.

## Acceptance use

For Database v3, the final technical sequence was:

```bash
pytest -q
python scripts/run_applicable_validators.py
python scripts/validate_inside_rails_v3.py
```

For the Database v4 candidate, the corresponding release-boundary sequence is:

```bash
pytest -q
python scripts/run_applicable_validators.py
python scripts/validate_inside_rails_v4.py
```

The final standalone version-specific validator is intentionally repeated after the complete sweep at the release boundary so the exact candidate is explicitly revalidated immediately before any promotion step. A successful validator run does not itself promote or modify the candidate.

For future database versions, replace only that final version-specific standalone validation command after the successor release contract defines it. Do not change the project-wide validator runner merely because the accepted database version changes.

## Historical reason this is permanent

The Phase 4 final repository gate on 6 August 2026 exposed three harness errors before the successful all-validator run:

1. an interactive shell was put under `set -euo pipefail`, allowing a failure to terminate that shell;
2. a generic runner omitted required positional database arguments, demonstrated by `validate_beaten_distances.py` correctly rejecting the invocation;
3. a runner omitted `PYTHONPATH=src`, causing a validator import failure.

Those were harness defects, not validator defects. The final corrected Phase 4 sweep passed all 31 then-current validators. The same class of mistake recurred during the Database v3 acceptance work on 9 August 2026 when a generic filename loop again invoked `validate_beaten_distances.py` without its required database argument.

Database v4 deliberately increased the governed inventory from 34 to 35 scripts and the applicable set from 31 to 32 by adding `validate_inside_rails_v4.py`. The runner, its focused test and this document were updated together so the inventory change is explicit rather than silently absorbed.

During the Database v4 acceptance sweep, historical Database v2 validation exposed another permanent lesson: a historical release validator must not read mutable present-day reference files when later releases legitimately extend those references. The v2 validator is now explicitly bound to its accepted build/reference commit.

The repository treats the runner itself as governed implementation, with focused tests, so this procedure does not need to be rediscovered in a later study or release.

## Change rule

If a validator is added, removed, renamed, changes required positional arguments, or becomes non-applicable:

1. do not edit a count merely to make the runner pass;
2. explain the applicability change;
3. update `scripts/run_applicable_validators.py` deliberately;
4. update its focused tests;
5. update this document when the governed procedure changes;
6. rerun focused tests, the complete repository suite and the complete applicable validator gate before release acceptance.
