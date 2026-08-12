# Inside Rails Horse-Racing Database

## Practical User Guide — Database v4

**Guide date:** 12 August 2026  
**Accepted database:** `data/processed/database/releases/inside_rails_v4.sqlite3`

## 1. Accepted database

Database v4 is the current accepted Inside Rails SQLite research database.

It preserves the complete Database v3 source/core/governed/external-reconciliation model and adds the completed Great Britain Study 03 racecourse/course identity layer.

Treat the accepted release as immutable and read-only.

```text
path: data/processed/database/releases/inside_rails_v4.sqlite3
file size: 3,137,249,280 bytes
SHA-256: 45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7
manifest status: release_accepted
validation-result rows: 7
physical source records retained: 1,851,286
source-backed runner records: 1,851,285
structural race occurrences: 189,043
reconciled combined runner records: 1,851,288
Great Britain race occurrences: 111,634
SQLite application_id: 1230130259
SQLite user_version: 4
quick_check: ok
foreign-key check rows: 0
```

Final release-boundary evidence:

```text
focused v4/release tests: 13 passed in 1.11s
complete repository suite: 435 passed in 15.47s
applicable independent validators: 32 passed
standalone v4 validator: passed
candidate hash unchanged during promotion: true
accepted v3 preserved: true
```

Preserved v4 candidate:

```text
path: data/processed/database/candidates/inside_rails_v4_candidate.sqlite3
SHA-256: 04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e
status: built
```

Retained v3 release:

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
```

Older releases/candidates are evidence and rollback artefacts, not the normal study database.

## 2. Quick start

From the repository root:

```bash
source .venv/bin/activate
```

For command-line Python:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, use the project `rails` alias.

Open Database v4 read-only in Python:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v4.sqlite3"

with connect_read_only(DATABASE) as connection:
    race_count = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_race_occurrences"
    ).fetchone()[0]
    gb_racecourse_count = connection.execute(
        "SELECT COUNT(*) FROM view_gb_reconciled_race_occurrences_with_racecourse"
    ).fetchone()[0]
    source_runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_source_runner_participations"
    ).fetchone()[0]

print(race_count, gb_racecourse_count, source_runner_count)
```

Expected:

```text
189043 111634 1851285
```

SQLite shell:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v4.sqlite3
```

Useful shell settings:

```sql
.headers on
.mode column
.timer on
```

## 3. Data layers

### Raw evidence

`source_raceform_v1_record` preserves every physical Source Version 1 record, including the retained excluded row.

### Structural core

`core_source_race_occurrence` contains one authorised race occurrence per exact raw `date + course + off` group.

`core_runner_participation` links each admitted source-backed runner to one structural race occurrence.

### Governed semantic / reconciliation layer

Database v4 carries the accepted Database v2/v3 governance and external reconciliation unchanged.

Important retained structures include:

- governed race/runner/temporal/reference layers;
- bounded corrections and supplementations;
- provisional horse/pedigree and participant identity structures;
- `104` manual-verification rows;
- `37` typed external-value resolutions;
- reconciled study-facing race and runner views.

Resolution kinds remain:

- `correction`;
- `enrichment`;
- `invalidation`.

Raw values remain recoverable through lineage.

### Database v4 Study 03 racecourse/course identity layer

Database v4 adds:

- 61 governed racecourse identities;
- 65 GB source-label → racecourse mappings;
- 90 Study 03 course/track inventory rows;
- 86 stable course/track identities;
- 7 unresolved governance rows.

The modelling distinction is:

> `racecourse -> course/track -> time-bounded characteristics`

A racecourse is a venue, not necessarily a single racing course.

Database v4 does **not** infer a physical-track identity for each race where Source Version 1 does not support that assignment.

## 4. Recommended views

### `view_reconciled_race_occurrences`

Grain: one reconciled structural race occurrence.

Rows: **189,043**.

Use for normal race-level analysis when racecourse identity is not required.

### `view_gb_reconciled_race_occurrences_with_racecourse`

Grain: one reconciled Great Britain race occurrence with governed racecourse identity.

Rows: **111,634**.

Distinct race IDs: **111,634**.

Use when the analysis needs the Study 03 racecourse layer. This is the correct starting race interface for Great Britain Study 04.

It adds racecourse identity and resolution provenance but deliberately does not assign a constituent physical course/track to the race.

### `view_gb_racecourse_identity_reference`

Rows: **65**.

Use to inspect the source-label → governed-racecourse bridge.

Newmarket is explicitly split:

- `Newmarket` → `Newmarket — Rowley Mile`;
- `Newmarket (July)` → `Newmarket — July Course`.

### `view_gb_course_track_identities`

Rows: **86**.

Use to inspect stable constituent course/track identities. Do not treat this reference view as a race-assignment table.

### `view_reconciled_source_runner_participations`

Rows: **1,851,285**.

Use when the population must match admitted physical source runners exactly.

### `view_reconciled_runner_records`

Rows: **1,851,288**.

This combines:

- 1,851,285 source-backed runners; plus
- 3 externally verified missing-runner supplementations.

### Specialised carried views

Use `view_governed_horse_occurrence_assignments` only when provisional horse/pedigree identity matters.

Use `view_governed_participant_label_identities` only when accepted participant-label mappings matter.

## 5. Identifier rules

Do not use raw `race_id` as the unique Inside Rails race key.

Prefer stable project-owned textual identifiers such as:

- `source_record_code`;
- `source_race_occurrence_code`;
- `runner_participation_code`;
- `racecourse_identity_code`;
- stable course/track codes `trk:gb:...`.

Internal integer IDs are release-local implementation identifiers.

## 6. Important carried reconciliation rules

Database v4 preserves Database v3's central rule:

> Raw source assertions are immutable. Exact externally established facts are exposed analytically with provenance; known-wrong analytical values without defensible replacements are invalidated rather than silently retained as correct.

Examples carried into v4 include:

- Almendares raw `sp='F'` with reconciled analytical SP `5/2 favourite`;
- Cinnamon Carter raw finish `10` with reconciled finish `12`;
- verified official `1600m` distance enrichments;
- exact externally corrected runner counts for Ohi, Morioka and Gulfstream Park;
- governed beaten-distance correction/invalidation cases;
- Compiegne `5yo+` and Ecstasy age `3`;
- three distinct actual-off enrichments;
- Pegasus 2018 and Arc 2019 official/local-currency prize enrichments.

Raw values remain recoverable and must not be described as though the source originally contained the reconciled values.

## 7. Advertised-start-time governance

Database v4 carries the accepted temporal reconstruction:

```text
total races: 189,043
resolved: 169,465
unresolved: 19,578
pre-boundary races: 178,691
explicit post-boundary races: 10,352
format boundary: 2025-10-15
```

These are advertised/scheduled start-time interpretations, not automatically exact actual-off times.

## 8. Pending post-release overlay

The existing pending registers retain their historical `post_v3` filenames:

- `data/reference/post_v3_external_verification_candidates.csv`;
- `data/reference/post_v3_external_value_resolutions.csv`.

Database v4 does not automatically mean every pending entry has been integrated.

Before applying a pending overlay, check whether the specific resolution is already native to v4.

Reusable helper:

```python
from inside_rails.study_overlay import build_race_overlay_query
```

Apply the overlay only for governed facts not yet native to the accepted release.

## 9. Efficient analytical use

Do not load all 1.85 million runner rows into pandas for ordinary counting/grouping.

Preferred pattern:

1. filter in SQL;
2. aggregate in SQL where practical;
3. load only the result into pandas;
4. use pandas for presentation, modelling or charts.

Example:

```python
import pandas as pd
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v4.sqlite3"

query = """
SELECT governed_racecourse_name, COUNT(*) AS races
FROM view_gb_reconciled_race_occurrences_with_racecourse
GROUP BY governed_racecourse_name
ORDER BY races DESC
"""

with connect_read_only(DATABASE) as connection:
    summary = pd.read_sql_query(query, connection)
```

## 10. Safe working rules

Do:

- use accepted Database v4;
- open it read-only;
- choose the view that matches the study grain;
- state the population and any supplementation/overlay consequence;
- distinguish source values from governed/reconciled interpretations;
- preserve unresolved identity/track questions explicitly;
- save study outputs outside the database;
- record database path/hash and repository commit for serious results.

Do not:

- modify the accepted release;
- silently fall back to v3/v2/v1/a candidate/raw Source Version 1;
- use raw `race_id` as the project race key;
- guess unresolved values;
- infer a race's physical course/track merely because its racecourse is known;
- convert provisional candidates into accepted identities;
- hide reusable correctness fixes inside a study notebook.

## 11. Limitations

- Source Version 1 covers 1 January 2015 through 27 May 2026; Database v4 is not live.
- Some governed values remain unresolved by design.
- Advertised-start-time reconstruction is not guaranteed exact actual-off time.
- Literal distance parsing remains distinct from separately verified official-distance enrichment.
- Horse and participant identity work remains provisional/scope-bounded.
- Study 03 course/track identities are a reference layer; race-to-track assignment is not generally established.
- Historical relationships are not guaranteed betting edges.

## 12. Troubleshooting

### `ModuleNotFoundError: No module named 'inside_rails'`

Command-line Python:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, use `rails`.

Do not add notebook `sys.path` hacks.

### Database v4 cannot be opened

Check the exact documented path:

```bash
ls -lh data/processed/database/releases/inside_rails_v4.sqlite3
```

Do not silently switch database.

### Unsure about a view or field

Inspect its columns with `PRAGMA table_info(...)` and check:

- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- the relevant database integration/release document.

Do not invent new semantics from a column name alone.

## 13. Recommended study workflow

1. State the racing question in one sentence.
2. Read the mandatory study references.
3. Use accepted Database v4 read-only.
4. Declare race/runner/racecourse grain and population.
5. Select the appropriate governed/reconciled view.
6. Inspect unresolved states and overlay consequences.
7. Filter/aggregate in SQL.
8. Move only the needed result into pandas.
9. Check sample size, exceptions and domain context.
10. Save code, result, interpretation and limitations together.

For Great Britain Study 04, start from `view_gb_reconciled_race_occurrences_with_racecourse` but do **not** assume `date + racecourse = meeting/fixture` until the study establishes that concept.

## Quick command card

```bash
source .venv/bin/activate
PYTHONPATH=src python script.py
rails
sqlite3 -readonly data/processed/database/releases/inside_rails_v4.sqlite3
git status --short --branch
```
