# Inside Rails Horse-Racing Database

## Practical User Guide — Database v3

**Guide date:** 9 August 2026  
**Accepted database:** `data/processed/database/releases/inside_rails_v3.sqlite3`

## 1. Accepted database

Database v3 is the current accepted Inside Rails SQLite research database.

It preserves the complete Database v2 source/core/governed model and adds the bounded external-verification reconciliation required after the retrospective notebook-evidence audit.

It contains:

- the complete retained Source Version 1 raw mirror;
- one structural race occurrence per authorised exact raw `date + course + off` group;
- one source-backed runner participation per admitted source record;
- the governed semantic work from Notebooks 04–22;
- governed references, evidence, bounded corrections and supplementations;
- provisional horse/pedigree and participant identity structures;
- `104` manual-verification rows;
- `37` typed external-value resolutions;
- reconciled study-facing race and runner views.

Treat the accepted release as immutable and read-only.

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
file size: 3,137,081,344 bytes
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
manifest status: release_accepted
validation-result rows: 7
physical source records retained: 1,851,286
source-backed runner records: 1,851,285
structural race occurrences: 189,043
reconciled combined runner records: 1,851,288
SQLite application_id: 1230130259
SQLite user_version: 3
quick_check: ok
foreign-key check rows: 0
```

Promotion compared all **1,851,286** raw rows, **189,043** structural race rows and **1,851,285** structural source-runner rows back to accepted Database v2. The candidate hash remained unchanged and Database v2 was preserved.

Preserved validated v3 candidate:

```text
path: data/processed/database/candidates/inside_rails_v3_candidate.sqlite3
SHA-256: 0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b
status: validated
```

Retained Database v2 release:

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
```

Retained Database v1 release:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
```

Older releases and candidates are evidence/rollback artefacts, not the normal study database.

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

Open Database v3 read-only in Python:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v3.sqlite3"

with connect_read_only(DATABASE) as connection:
    race_count = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_race_occurrences"
    ).fetchone()[0]
    source_runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_source_runner_participations"
    ).fetchone()[0]
    combined_runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_runner_records"
    ).fetchone()[0]

print(race_count, source_runner_count, combined_runner_count)
```

Expected:

```text
189043 1851285 1851288
```

SQLite shell:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v3.sqlite3
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

`core_source_race_occurrence` contains one authorised race occurrence per exact raw:

`date + course + off`

`core_runner_participation` links each admitted source-backed runner to one structural race occurrence.

### Database v2 governed semantic extensions

Database v3 retains the governed structures created in v2, including race, runner, temporal, reference, supplementation, horse/pedigree and participant-identity layers.

### Database v3 external reconciliation

New table:

`governance_external_value_resolution`

It stores typed externally supported outcomes linked to durable manual-verification evidence.

Resolution kinds:

- `correction` — a replacement analytical value is externally established;
- `enrichment` — a distinct useful external fact is established without overwriting the raw source concept;
- `invalidation` — the raw analytical value is known wrong but no defensible replacement is available.

Raw values remain recoverable through source lineage.

## 4. Recommended views

### `view_reconciled_race_occurrences`

Grain: one reconciled structural race occurrence.

Rows: **189,043**.

Use for normal race-level analysis.

It carries v2 governed race semantics and applies race-level v3 reconciliation where exact external evidence exists, including corrected runner counts, official-distance enrichment, age-band correction and actual-off enrichment.

### `view_reconciled_source_runner_participations`

Grain: one reconciled source-backed runner participation.

Rows: **1,851,285**.

Use when the analytical population must match admitted physical source runner rows exactly.

It carries raw values alongside governed/reconciled values and applies exact v3 corrections, enrichments and invalidations where supported.

### `view_reconciled_runner_records`

Grain: one reconciled governed runner record including accepted missing-runner supplementations.

Rows: **1,851,288**.

This combines:

- **1,851,285** source-backed runners; plus
- **3** externally verified missing runners.

`record_origin` preserves the distinction.

Unsupported supplemented-runner attributes remain null.

### Carried specialised views

Use `view_governed_horse_occurrence_assignments` only when Notebook 19 provisional horse/pedigree occurrence identity matters.

Use `view_governed_participant_label_identities` only when accepted Notebook 22 mappings matter. Unresolved candidates remain unresolved.

The older v2 `view_governed_race_occurrences`, `view_governed_source_runner_participations` and `view_governed_runner_records` remain available for lineage/comparison, but new general studies should prefer the corresponding `view_reconciled_*` views so v3 corrections are not bypassed.

## 5. Identifier rules

Do not use raw `race_id` as the unique Inside Rails race key.

Prefer stable project-owned textual identifiers such as:

- `source_record_code`;
- `source_race_occurrence_code`;
- `runner_participation_code`.

Internal integer IDs are release-local implementation identifiers.

For race-level work, do not treat runner rows as independent races.

## 6. Important Database v3 reconciliation

The governing rule is:

> Raw source assertions are immutable. When external evidence establishes an exact fact, the governed database exposes that fact as usable analytical data with explicit provenance. When external evidence proves a raw analytical value wrong but no defensible replacement is established, the raw value remains visible while the study-facing analytical value is invalidated rather than silently retained as correct.

Important examples:

### Starting price

Almendares (GB), Del Mar, 20 July 2025, 1:03:

- raw `sp='F'`;
- reconciled price `5/2`;
- decimal odds `3.5`;
- implied probability approximately `0.2857142857`;
- favourite status `favourite`.

The raw parser still correctly refuses to infer a numeric price from bare `F`; the numeric odds come from external evidence.

### Finishing position

Cinnamon Carter (AUS), Morphettville, 16 May 2015:

- raw position `10`;
- reconciled finish position `12`;
- externally verified dead-heat context retained.

### Official distance

Sha Tin 25 January 2015 and Kyoto 4 January 2015 retain raw `dist='1m'` while exposing externally verified official distance `1600m` as a separate enrichment.

### Runner count

Exact externally verified race-count corrections include:

- Ohi 26 June 2024: raw `ran=5` → reconciled `13`;
- Morioka 3 September 2024: raw `ran=5` → reconciled `12`;
- Gulfstream Park 23 December 2023: raw `ran=8` → reconciled `9`.

A corrected count does not invent missing runner identities.

### Beaten distances

- Gavea 6 April 2025 position-2 runner: governed `ovr_btn=16.5`, `btn=16.5` lengths;
- Nardo: the known-wrong numeric zero is invalidated; externally established incremental relation `head` is retained without inventing a numeric head conversion;
- Red Fog and Cabernet Franc: known-wrong zero distances become analytical null where replacement remains unresolved.

### Age/eligibility

- Compiegne 16 May 2017: raw `5yo` → reconciled `5yo+`;
- Ecstasy (USA), Woodbine 27 July 2024: raw age `31` → reconciled age `3`.

### Actual-off time

Three externally reported actual-off observations are exposed separately from the canonical advertised/scheduled start-time reconstruction. Do not use one as a synonym for the other.

### Prize schedules

Externally checked Pegasus 2018 USD and Arc 2019 EUR placing schedules are exposed as distinct official/local-currency enrichment. They do not overwrite raw/source-presented prize values.

## 7. Carried Database v2 governance

Database v3 retains the earlier integrated governance, including:

- explicit `(AW)` evidence supports only `all_weather_unspecified`;
- literal source-distance parsing remains distinct from official-distance enrichment;
- exact Notebook 17 `B` / `BB` sex corrections;
- exact raw `rpr = 775` anomaly analytically null as `invalid_source_value`;
- **28** externally supplemented blank connection labels and **18** unresolved blanks;
- conservative comment classification;
- provisional horse and participant identity treatment.

## 8. Advertised-start-time governance

Database v3 carries Notebook 11 temporal reconstruction.

```text
total races: 189,043
resolved: 169,465
unresolved: 19,578
pre-boundary races: 178,691
explicit post-boundary races: 10,352
```

Methods:

```text
course_local_dead_of_night_rejection: 111,871
stable_post_boundary_course_profile: 47,242
explicit_post_boundary_time: 10,352
unresolved: 19,578
```

Format boundary:

`2025-10-15`

These are reconstructed advertised/scheduled start times, not automatically exact actual-off times.

## 9. Query recipes

### Confirm populations

```sql
SELECT COUNT(*) AS races
FROM view_reconciled_race_occurrences;

SELECT COUNT(*) AS source_backed_runners
FROM view_reconciled_source_runner_participations;

SELECT COUNT(*) AS governed_runner_records
FROM view_reconciled_runner_records;
```

### Inspect race-level field sizes

First inspect the view schema rather than guessing a reconciled column name:

```sql
PRAGMA table_info(view_reconciled_race_occurrences);
```

Then use the documented reconciled runner-count field appropriate to the study definition. Study 01 must state whether it uses the reconciled count, physical source-runner rows or another explicitly governed population.

### Inspect source/reconciled runner fields

```sql
PRAGMA table_info(view_reconciled_source_runner_participations);
PRAGMA table_info(view_reconciled_runner_records);
```

### Check whether rows are source-backed or supplemented

```sql
SELECT record_origin, COUNT(*) AS rows
FROM view_reconciled_runner_records
GROUP BY record_origin
ORDER BY record_origin;
```

## 10. Efficient pandas use

Do not load all 1.85 million source-backed runner rows into pandas for ordinary counting or grouping.

Preferred pattern:

1. filter in SQL;
2. aggregate in SQL where practical;
3. load only the result into pandas;
4. use pandas for presentation, modelling or charts.

Example:

```python
import pandas as pd
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v3.sqlite3"

query = """
SELECT candidate_jurisdiction, COUNT(*) AS races
FROM view_reconciled_race_occurrences
GROUP BY candidate_jurisdiction
ORDER BY races DESC
"""

with connect_read_only(DATABASE) as connection:
    summary = pd.read_sql_query(query, connection)
```

## 11. Safe working rules

Do:

- use accepted Database v3;
- open it read-only;
- prefer the reconciled views for new general studies;
- state observation grain and population;
- state whether the three supplementation rows are included;
- distinguish raw values from governed/reconciled interpretations;
- save study outputs outside the database;
- record database path/hash and repository commit for serious results.

Do not:

- modify the accepted release;
- silently fall back to Database v2, Database v1, a candidate or Source Version 1;
- use raw `race_id` as the project race key;
- restore a known-wrong raw value when v3 invalidates it analytically;
- guess unresolved values;
- convert provisional identity candidates into accepted identities;
- hide reusable database fixes inside a study notebook.

## 12. Limitations

- Source Version 1 covers 1 January 2015 through 27 May 2026; Database v3 is not live.
- Some governed values remain unresolved by design.
- Advertised-start-time reconstruction is not guaranteed exact actual-off time.
- Literal distance parsing is source-derived; externally verified official-distance enrichment exists only where specifically established.
- Horse and participant identity work remains provisional and scope-bounded.
- Prize currencies/schedules outside governed cases remain unresolved rather than guessed or converted.
- Historical relationships are not guaranteed betting edges.

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'inside_rails'`

Command-line Python:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, use `rails`.

Do not add notebook `sys.path` hacks.

### Database v3 cannot be opened

Check the exact documented path:

```bash
ls -lh data/processed/database/releases/inside_rails_v3.sqlite3
```

Do not silently switch database.

### Unsure about a reconciled view

Inspect its columns with `PRAGMA table_info(...)` and check `docs/STUDY_DATABASE_REFERENCE.md` plus `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md` before inventing new semantics.

## 14. Recommended study workflow

1. State the racing question in one sentence.
2. Read `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.
3. Use accepted Database v3 read-only.
4. Declare race/runner grain and population.
5. Select the appropriate reconciled view.
6. Inspect unresolved states, invalidations and supplementation consequences.
7. Filter and aggregate in SQL.
8. Move only the needed result into pandas.
9. Check sample size, exceptions and market context.
10. Save code, result, interpretation and limitations together.

Database v3 should now let studies use the full governed Notebook 04–22 evidence chain, including exact externally resolved facts, without recreating correction logic inside study notebooks.

## Quick command card

```bash
source .venv/bin/activate
PYTHONPATH=src python script.py
rails
sqlite3 -readonly data/processed/database/releases/inside_rails_v3.sqlite3
git status --short --branch
```
