# Notebook 11 Closeout — Off-Time and Temporal Semantics

## Status

**Archival analytical record; durable canonical-output repair prepared for local validation and review acceptance.**

Notebook 11 established the temporal interpretation and the settled source-wide decision totals. The cross-notebook audit found that those 189,043 race-level decisions were not persisted in the repository and could not be regenerated through a default production workflow. The old validator exercised helper functions and enforced full totals only when an external file was supplied optionally.

This repair adds the missing source-to-output implementation, focused tests, atomic persistence, typed reload and mandatory independent output validation. It does not change the analytical interpretation or select any previously unresolved race.

## Bounded conclusion

Source `date + off` is a UK-facing advertised civil datetime, not a racecourse-local time and not a guaranteed actual-off timestamp.

The source encoding changes at 15 October 2025:

- pre-boundary values omit AM/PM and require candidate A and candidate B, separated by 12 hours;
- post-boundary values are explicit 24-hour UK civil times.

Pre-boundary branch selection is authorised only by:

1. course-local dead-of-night rejection;
2. a stable post-boundary course profile across every governed margin, restricted to meetings where both candidate branches are valid;
3. otherwise no selection.

Ambiguous or nonexistent London daylight-saving candidates remain unresolved and are not passed into profile-based selection. Unresolved races retain both candidates and no canonical timestamp.

## Governed current-source result

- provisional races: **189,043**;
- pre-boundary races: **178,691**;
- explicit post-boundary races: **10,352**;
- resolved races: **169,465**;
- unresolved races: **19,578**.

Decision methods are exactly:

- course-local dead-of-night rejection: **111,871**;
- stable post-boundary course profile: **47,242**;
- explicit post-boundary time: **10,352**;
- unresolved: **19,578**.

## Durable implementation

- raw clock parser: `src/inside_rails/off_time.py`;
- reconstruction helpers: `src/inside_rails/race_times.py`;
- production orchestration and persistence: `src/inside_rails/race_time_pipeline.py`;
- focused tests: `tests/test_off_time.py`, `tests/test_race_time_pipeline.py` and `tests/test_race_time_pipeline_dst_regression.py`;
- source builder: `scripts/build_race_time_governance.py`;
- raw clock validator: `scripts/validate_off_time.py`;
- independent canonical-output validator: `scripts/validate_race_times.py`;
- integration contract: `docs/OFF_TIME_DATABASE_INTEGRATION.md`;
- generated output: `data/processed/race_times/canonical_race_times.csv`.

## Audit defect and repair

### Defect

The repository previously contained the deterministic helper functions but no default production function that reconstructed every race, no persisted canonical output, and no mandatory independent validator for the complete output.

The integration contract explicitly said the reusable module did not embed the meeting decisions. As a result, the repository’s claimed 169,465 resolved and 19,578 unresolved races existed only inside the archived notebook.

### Repair

The new pipeline:

1. loads one exact source context per provisional race;
2. derives and validates every governed course identity and IANA timezone;
3. reconstructs both pre-boundary branches;
4. derives course-local candidates through canonical UTC;
5. applies the settled dead-of-night and stable-profile hierarchy;
6. excludes DST-edge meetings from profile-based selection when either branch is ambiguous or nonexistent in London civil time;
7. constructs every explicit post-boundary timestamp;
8. preserves unresolved candidates without selecting a timestamp;
9. enforces the exact population and method totals;
10. writes the output atomically;
11. compares persisted strings with the built dataframe;
12. reloads timestamp types;
13. repeats all integrity and conversion checks.

The independent validator then starts from the persisted output and reconciles it exactly to the immutable source and governed course reference.

## Persisted-output status

The generated CSV is deliberately **not created through the GitHub connector**. It is source-derived output and must be generated from the user’s local immutable SQLite database.

This review unit remains prepared rather than accepted until local execution proves:

- the full output builds successfully;
- all exact totals match;
- the CSV writes and reloads without change;
- every source race and timezone reconciles;
- every resolved timestamp conversion agrees through UTC;
- focused tests and both validators pass.

After that evidence is reviewed, the generated CSV may be force-added despite the project’s general processed-data ignore policy.

## Reproducibility classification

The notebook remains a **non-rerunnable archival construction record**.

The new production builder—not a fresh notebook rerun—is the durable regeneration path. It begins from the immutable source, governed course reference and reusable reconstruction functions.

## Manual-verification decision

`not_applicable` for the implemented population-level reconstruction rules.

Notebook 11 used bounded external pilot checks during investigation, but the production decisions are the settled source-wide structural methods recorded in the module and integration contract. No row-level external correction table is applied by the output pipeline.

## Database consequence

Preserve raw `date`, `course` and `off`. Store candidate course identity and timezone separately. Add one canonical temporal record per staged race, preserving both candidates for unresolved pre-boundary races.

Use canonical UTC as the conversion anchor. Do not attach the course timezone directly to raw `date + off`, use fixed UTC offsets, invent a branch for unresolved meetings, or represent the timestamp as actual-off time.

## Focused validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_off_time.py \
  tests/test_race_time_pipeline.py \
  tests/test_race_time_pipeline_dst_regression.py

PYTHONPATH=src .venv/bin/python scripts/validate_off_time.py \
  data/raw/form_2015-present/form_2015-present/raceform.db

PYTHONPATH=src .venv/bin/python \
  scripts/build_race_time_governance.py

PYTHONPATH=src .venv/bin/python \
  scripts/validate_race_times.py
```

The complete repository test suite and all-validator sweep remain deferred until every review unit has been accepted and combined at the final repair-series gate.
