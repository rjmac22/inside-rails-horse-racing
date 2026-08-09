# Inside Rails Horse-Racing Database

## Practical User Guide — Database v2

**Guide date:** 9 August 2026  
**Accepted database:** `data/processed/database/releases/inside_rails_v2.sqlite3`

## 1. Accepted database

Database v2 is the current accepted Inside Rails SQLite research database.

It contains:

- the complete retained Source Version 1 raw mirror;
- one structural race occurrence per authorised exact raw `date + course + off` group;
- one source-backed runner participation per admitted source record;
- the governed semantic work from Notebooks 04–22;
- governed references, evidence, bounded corrections and supplementations;
- provisional horse/pedigree and participant identity structures;
- transparent study-facing views.

Treat the accepted release as immutable and read-only.

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
file size: 3,137,044,480 bytes
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
manifest status: release_accepted
validation-result rows: 7
physical source records retained: 1,851,286
source-backed runner records: 1,851,285
structural race occurrences: 189,043
SQLite application_id: 1230130259
SQLite user_version: 2
quick_check: ok
foreign-key check rows: 0
```

Promotion independently recomputed all **1,851,286** raw-record fingerprints and compared **2,040,328** carried structural rows against accepted Database v1.

Preserved validated v2 candidate:

```text
path: data/processed/database/candidates/inside_rails_v2_candidate.sqlite3
SHA-256: 5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe
status: validated
```

Retained Database v1 release:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
```

Database v1 and the v2 candidate are evidence/rollback artefacts, not the normal study database.

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

Open Database v2 read-only in Python:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v2.sqlite3"

with connect_read_only(DATABASE) as connection:
    race_count = connection.execute(
        "SELECT COUNT(*) FROM view_governed_race_occurrences"
    ).fetchone()[0]
    source_runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_governed_source_runner_participations"
    ).fetchone()[0]
    combined_runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_governed_runner_records"
    ).fetchone()[0]

print(race_count, source_runner_count, combined_runner_count)
```

Expected:

```text
189043 1851285 1851288
```

SQLite shell:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v2.sqlite3
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

### Governed semantic extensions

Race-level governed material:

- `core_source_race_occurrence_governed`;
- `core_source_race_occurrence_time`.

Runner-level governed material:

- `core_runner_participation_governed`.

Raw values remain recoverable through source lineage.

### Governed references/evidence

Database v2 includes:

- 395 governed course identities/timezones;
- 16 bounded jurisdiction-context rows;
- 37 field-treatment rows;
- 85 manual-verification rows;
- 46 connection blank-field decisions;
- 3 missing-runner supplementations;
- 16 specialist horse/pedigree decisions.

## 4. Recommended views

### `view_governed_race_occurrences`

Grain: one governed structural race occurrence.

Rows: **189,043**.

Use for normal race-level analysis.

Important columns include:

- `source_race_occurrence_code`;
- `raw_date`, `raw_course`, `raw_off`;
- `admitted_runner_count`;
- `candidate_course_label`, `candidate_jurisdiction`;
- `candidate_surface`;
- governed distance fields;
- `source_reported_ran`, `source_runner_row_count` and coverage fields;
- race classification fields;
- course timezone/location fields;
- advertised-start-time fields and `temporal_resolution_status`.

### `view_governed_source_runner_participations`

Grain: one source-backed runner participation.

Rows: **1,851,285**.

Use when the analytical population must match admitted physical source runner rows exactly.

The view deliberately uses explicit raw/governed names such as:

- `raw_date`, `raw_course`, `raw_off`;
- `raw_horse`;
- `raw_pos` plus governed result fields;
- `raw_wgt` plus governed weight fields;
- `raw_sp` plus governed starting-price fields;
- `raw_prize` plus governed prize fields;
- `raw_jockey`, `raw_trainer`, `raw_owner` plus governed labels;
- raw/governed ratings and characteristics;
- provisional horse/participant identity codes where accepted mappings exist.

### `view_governed_runner_records`

Grain: one governed runner record including accepted missing-runner supplementations.

Rows: **1,851,288**.

This combines:

- **1,851,285** source-backed runners; plus
- **3** externally verified missing runners.

`record_origin` makes the distinction explicit.

The three supplemented runners are:

- Saucats — Nantes, 18 June 2024, 2:14;
- Tosen Thunder (JPN) — Ohi, 9 October 2025, 11:07;
- Great Navigator (USA) — Gulfstream Park, 23 December 2023, 9:36.

Unsupported supplemented-runner attributes remain null.

### `view_governed_horse_occurrence_assignments`

Use only when Notebook 19 provisional horse/pedigree occurrence identity matters.

Baseline:

```text
provisional occurrences: 611
transition decisions: 353
Corrected: 92
Different horse: 261
Unresolved: 0
```

### `view_governed_participant_label_identities`

Use only when accepted Notebook 22 mappings matter.

Baseline:

```text
source labels: 116,859
participant candidates: 1,205
accepted provisional identities: 68
accepted label mappings: 149
```

Unresolved candidates remain unresolved.

## 5. Identifier rules

Do not use raw `race_id` as the unique Inside Rails race key.

Prefer stable project-owned textual identifiers such as:

- `source_record_code`;
- `source_race_occurrence_code`;
- `runner_participation_code`.

Internal integer IDs are release-local implementation identifiers.

For race-level work, do not treat runner rows as independent races.

## 6. Important integrated governance

### Surface

Explicit `(AW)` evidence supports only:

`all_weather_unspecified`

Other surface states remain unresolved under that source-only rule.

### Distance

Distance fields are governed parses of literal source notation, not independently verified official distances.

### Starting price

Fractional/evens arithmetic and favourite-marker semantics are governed.

The lone raw value `F` remains unresolved because the source supplies a marker without a price.

### Runner sex

Two exact bounded corrections are integrated:

- Par Coeur (GER): raw `BB` → governed `gelding`;
- La Venezolana (VEN): raw `B` → governed `filly`.

They are exact-record corrections, not global translations.

### Ratings

Source rowid `1619851`, raw `rpr = 775`, is governed as `invalid_source_value` with analytical RPR null. No replacement value is invented.

### Connections

Notebook 20 baseline:

```text
raw blank connection fields: 46
externally supplemented: 28
preserved unresolved: 18
```

A governed connection label is not automatically a real-world participant identity.

### Comments

Comment text is preserved and conservatively state-classified. There is no universal narrative parser.

## 7. Advertised-start-time governance

Database v2 integrates Notebook 11 temporal reconstruction.

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

## 8. Query recipes

### Confirm populations

```sql
SELECT COUNT(*) AS races
FROM view_governed_race_occurrences;

SELECT COUNT(*) AS source_backed_runners
FROM view_governed_source_runner_participations;

SELECT COUNT(*) AS governed_runner_records
FROM view_governed_runner_records;
```

### Source-backed field-size distribution

```sql
SELECT
    source_runner_row_count AS runners,
    COUNT(*) AS races
FROM view_governed_race_occurrences
GROUP BY source_runner_row_count
ORDER BY source_runner_row_count;
```

### Compare source runner rows with source-reported `ran`

```sql
SELECT
    source_row_count_vs_ran_status,
    COUNT(*) AS races
FROM view_governed_race_occurrences
GROUP BY source_row_count_vs_ran_status
ORDER BY races DESC;
```

### Inspect unresolved advertised times

```sql
SELECT COUNT(*) AS unresolved_races
FROM view_governed_race_occurrences
WHERE temporal_resolution_status = 'unresolved';
```

Expected:

`19578`

### Search one raw horse label

```sql
SELECT
    source_race_occurrence_code,
    raw_date,
    raw_course,
    raw_off,
    raw_horse,
    finish_position,
    outcome_code,
    raw_sp,
    starting_price_value_status
FROM view_governed_source_runner_participations
WHERE raw_horse = ?
ORDER BY CAST(raw_date AS TEXT), CAST(raw_off AS TEXT);
```

Use a parameter from Python rather than interpolating a horse name into SQL.

### Check whether rows are source-backed or supplemented

```sql
SELECT record_origin, COUNT(*) AS rows
FROM view_governed_runner_records
GROUP BY record_origin
ORDER BY record_origin;
```

### Inspect view columns

```sql
PRAGMA table_info(view_governed_race_occurrences);
PRAGMA table_info(view_governed_source_runner_participations);
PRAGMA table_info(view_governed_runner_records);
```

## 9. Efficient pandas use

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

DATABASE = "data/processed/database/releases/inside_rails_v2.sqlite3"

query = """
SELECT candidate_jurisdiction, COUNT(*) AS races
FROM view_governed_race_occurrences
GROUP BY candidate_jurisdiction
ORDER BY races DESC
"""

with connect_read_only(DATABASE) as connection:
    summary = pd.read_sql_query(query, connection)
```

## 10. Safe working rules

Do:

- use accepted Database v2;
- open it read-only;
- state observation grain and population;
- state whether the three supplementation rows are included;
- distinguish raw values from governed interpretations;
- save study outputs outside the database;
- record database path/hash and repository commit for serious results.

Do not:

- modify the accepted release;
- silently fall back to Database v1, the v2 candidate or Source Version 1;
- use raw `race_id` as the project race key;
- guess unresolved values;
- convert provisional identity candidates into accepted identities;
- hide reusable database fixes inside a study notebook.

## 11. Limitations

- Source Version 1 covers 1 January 2015 through 27 May 2026; Database v2 is not live.
- Some governed values remain unresolved by design.
- Advertised-start-time reconstruction is not guaranteed exact actual-off time.
- Distance parsing is source-literal, not independently verified official distance.
- Horse and participant identity work remains provisional and scope-bounded.
- Prize currencies outside governed canonical cases remain unresolved rather than guessed or converted.
- Historical relationships are not guaranteed betting edges.

## 12. Troubleshooting

### `ModuleNotFoundError: No module named 'inside_rails'`

Command-line Python:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, use `rails`.

Do not add notebook `sys.path` hacks.

### Database v2 cannot be opened

Check the exact documented path:

```bash
ls -lh data/processed/database/releases/inside_rails_v2.sqlite3
```

Do not silently switch database.

### Unsure about a governed view

Inspect its columns with `PRAGMA table_info(...)` and check the relevant Notebook 04–22 governance documentation before inventing new semantics.

## 13. Recommended study workflow

1. State the racing question in one sentence.
2. Read `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.
3. Use accepted Database v2 read-only.
4. Declare race/runner grain and population.
5. Select the appropriate governed view.
6. Inspect unresolved states and supplementation consequences.
7. Filter and aggregate in SQL.
8. Move only the needed result into pandas.
9. Check sample size, exceptions and market context.
10. Save code, result, interpretation and limitations together.

Database v2 should now let studies use Notebook 04–22 governance directly rather than recreating it with ad hoc joins.

## Quick command card

```bash
source .venv/bin/activate
PYTHONPATH=src python script.py
rails
sqlite3 -readonly data/processed/database/releases/inside_rails_v2.sqlite3
git status --short --branch
```
