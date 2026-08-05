# Off-Time and Canonical Race-Time Database Integration

## Scope

Notebook 11 established that source `off` is a UK-facing advertised or scheduled clock representation, not a guaranteed exact actual-off timestamp.

The source text is fully clock-shaped, but the encoding changes at **15 October 2025**:

- before the boundary, values from `1:00` through `12:59` omit the AM/PM branch and require two candidate UK civil datetimes;
- from the boundary onward, source values use explicit 24-hour UK civil time.

The durable implementation now separates:

1. raw clock parsing;
2. governed course identity and timezone assignment;
3. pre-boundary candidate reconstruction;
4. meeting-level branch selection;
5. canonical UK, UTC and course-local timestamps;
6. persisted output and independent source reconciliation.

## Immutable raw fields

Preserve the original source race context unchanged:

- source database and table;
- physical source lineage;
- supplied `race_id`;
- source `date`;
- source `course`;
- source `off`;
- source `race_name`;
- source `type`.

The source date and clock must never be overwritten by reconstructed timestamps.

## Governed course context

Every provisional race must first receive:

- `candidate_course_label`;
- `candidate_jurisdiction`;
- governed `iana_timezone`.

These fields are derived and joined through:

- `src/inside_rails/course_locations.py`;
- `data/reference/course_locations.csv`.

The source clock is UK-facing. The course timezone must **not** be attached directly to raw `date + off`. Reconstruction first produces a UK civil datetime, then canonical UTC, then course-local time.

## Canonical output

The governed output is generated locally at:

`data/processed/race_times/canonical_race_times.csv`

Its grain is exactly one row per provisional race key:

`date + course + off`

Required output fields are:

### Source and governed context

- `date`;
- `course`;
- `off`;
- `race_id`;
- `race_name`;
- `type`;
- `candidate_course_label`;
- `candidate_jurisdiction`;
- `iana_timezone`.

### Preserved pre-boundary candidates

- `candidate_a_uk_naive`;
- `candidate_b_uk_naive`;
- `candidate_a_utc`;
- `candidate_b_utc`;
- `candidate_a_course_local`;
- `candidate_b_course_local`.

Post-boundary rows leave these candidate fields null because their 24-hour source representation is explicit.

### Selected canonical result

- `advertised_start_uk`;
- `advertised_start_utc`;
- `advertised_start_course_local`;
- `selected_branch`;
- `decision_method`;
- `decision_confidence`;
- `temporal_resolution_status`.

Unresolved pre-boundary races retain both candidates and no selected canonical timestamp.

## Governed reconstruction rules

### Pre-boundary candidate construction

For each date-and-course meeting:

1. parse each raw clock on a 12-hour circular scale;
2. identify the first value after the meeting’s largest circular gap;
3. unwrap the meeting into an ordered candidate-A sequence;
4. create candidate B exactly 12 hours later;
5. interpret both candidates using historical `Europe/London` rules;
6. convert valid candidates to UTC;
7. convert UTC to the governed racecourse timezone.

Ambiguous or nonexistent London daylight-saving times remain explicitly classified; they are not silently shifted.

### Branch selection hierarchy

The settled hierarchy is:

1. **course-local dead-of-night rejection** — select the only branch that does not place the complete meeting between midnight and 05:59 course-local;
2. **stable post-boundary course profile** — only for meetings where both London candidate branches are valid, and where at least five explicit meetings exist, select a branch only when it remains uniquely compatible across every governed margin of 60, 90, 120 and 180 minutes;
3. otherwise retain the race unresolved.

DST-edge meetings with an ambiguous or nonexistent candidate are not eligible for profile-based selection. The stable profile is evidence from the current source population, not a universal racing-hours rule. A decision must be stable across all four margins before it is accepted.

### Post-boundary construction

From 15 October 2025 onward:

1. parse source `date + off` as explicit 24-hour UK civil time;
2. apply historical `Europe/London` timezone rules;
3. convert to UTC;
4. convert UTC to the governed course timezone;
5. assign method `explicit_post_boundary_time` and status `resolved`.

## Settled source baselines

The complete current-source result is:

- canonical races: **189,043**;
- pre-boundary races: **178,691**;
- explicit post-boundary races: **10,352**;
- resolved races: **169,465**;
- unresolved races: **19,578**.

Decision-method counts are exactly:

- `course_local_dead_of_night_rejection`: **111,871**;
- `stable_post_boundary_course_profile`: **47,242**;
- `explicit_post_boundary_time`: **10,352**;
- `unresolved`: **19,578**.

These are regression baselines for the immutable current source. They must not be changed merely to make a new extract pass.

## Durable implementation

- deterministic reconstruction helpers: `src/inside_rails/race_times.py`;
- source-to-output orchestration, persistence and reload: `src/inside_rails/race_time_pipeline.py`;
- raw clock helpers: `src/inside_rails/off_time.py`;
- focused tests: `tests/test_off_time.py`, `tests/test_race_time_pipeline.py` and `tests/test_race_time_pipeline_dst_regression.py`;
- source builder: `scripts/build_race_time_governance.py`;
- independent output validator: `scripts/validate_race_times.py`;
- raw clock validator: `scripts/validate_off_time.py`.

The archival notebook is not the production regeneration path.

## Persistence contract

`scripts/build_race_time_governance.py` must:

1. open the source SQLite database read-only;
2. load exactly 189,043 unique provisional race contexts;
3. derive and require a governed course-location match for every race;
4. build the complete canonical output;
5. enforce the exact population and method totals;
6. reconcile every resolved UK and course-local timestamp to canonical UTC;
7. write the CSV atomically;
8. compare the persisted strings with the built dataframe;
9. reload the CSV into typed timestamp fields;
10. rerun all integrity, total and conversion checks.

Generated source-derived output must be produced from the user’s local immutable source. It must not be invented or reconstructed through repository metadata alone.

## Independent validation contract

`scripts/validate_race_times.py` starts from the persisted output and independently:

- requires the canonical file to exist;
- reloads and validates its exact schema;
- enforces one row per race key;
- enforces all settled totals and method counts;
- reconciles every source race field, governed course identity and timezone to the immutable SQLite source;
- verifies complete pre/post-boundary populations;
- requires both candidates on every pre-boundary row;
- requires no candidates on explicit post-boundary rows;
- requires no selected branch or canonical timestamp on unresolved rows;
- requires candidate A or B on every resolved pre-boundary row;
- verifies every resolved UK and course-local timestamp by converting from canonical UTC.

A helper-only or optional-file validation is not sufficient for closure.

## Database constraints

The target database must enforce:

- one temporal row per staged race surrogate;
- unique source race key within the current source version;
- exact source and course-reference lineage;
- nullable selected timestamps only when status is unresolved;
- non-null selected UK, UTC and course-local timestamps when status is resolved;
- candidate preservation for every unresolved pre-boundary race;
- no candidate values on explicit post-boundary races;
- constrained decision methods and resolution statuses;
- timezone-aware timestamp storage or exact ISO representation with offsets;
- no conversion based on fixed hand-written UTC offsets.

`advertised_start_course_local` may fall on a different calendar date from source `date`. That is a valid timezone consequence and must not rewrite the source date.

## Source-update procedure

For a new source snapshot:

1. preserve the raw source fields and version;
2. run the raw `off` validator before changing any baseline;
3. validate the complete course-location join;
4. rebuild the canonical output through the production builder;
5. investigate new clock forms, new course identities, DST failures or population changes;
6. compare decision-method and unresolved populations with the previous source;
7. update governed rules only after bounded evidence supports the change;
8. write, reload and independently validate the new output;
9. rebuild dependent database tables;
10. retain the previous version for lineage and comparison.

## Validation commands

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

The build and independent validator must both pass against the local immutable source before the generated CSV is staged for review.
