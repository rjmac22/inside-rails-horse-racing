# Inside Rails Horse-Racing Database

## Practical User Guide — Database v2

**Guide date:** 9 August 2026  
**Accepted database:** `data/processed/database/releases/inside_rails_v2.sqlite3`

## 1. What Database v2 is

Database v2 is the current accepted, validated SQLite research database for Inside Rails.

It combines:

- the complete retained raw Source Version 1 mirror;
- one structural race occurrence for every authorised raw `date + course + off` group;
- one structural runner participation for every admitted source record;
- the governed semantic work established by Notebooks 04–22;
- governed reference data;
- bounded corrections and supplementations;
- provisional horse/pedigree identity work;
- provisional participant identity work;
- complete source, build and release lineage;
- transparent study-facing views.

It is intended for local research, evidence-backed articles, notebook analysis and reusable query development.

It is not a live racecard service, a tip generator or evidence that any historical pattern will remain profitable.

Treat the accepted release as immutable and read-only.

### Accepted identity

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
file size: 3,137,044,480 bytes
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
manifest status: release_accepted
validation-result rows: 7
physical source records retained: 1,851,286
admitted source-backed runner records: 1,851,285
structural race occurrences: 189,043
SQLite application_id: 1230130259
SQLite user_version: 2
quick_check: ok
foreign-key check rows: 0
```

Promotion independently recomputed all **1,851,286** raw-record fingerprints and compared **2,040,328** carried structural rows against the retained accepted Database v1 release.

The exact validated v2 candidate remains preserved at:

```text
path: data/processed/database/candidates/inside_rails_v2_candidate.sqlite3
SHA-256: 5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe
status: validated
```

The prior accepted Database v1 remains preserved at:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
```

## 2. Two-minute quick start

From the repository root:

```bash
cd ~/Documents/inside-rails-horse-racing
source .venv/bin/activate
```

The repository uses a `src` layout. For ordinary command-line Python use:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, use the project `rails` alias so Jupyter starts with the correct absolute `PYTHONPATH`.

Confirm the accepted release exists:

```bash
ls -lh data/processed/database/releases/inside_rails_v2.sqlite3
```

Read a race count in Python:

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

Open the database in the SQLite shell:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v2.sqlite3
```

Useful shell settings:

```sql
.headers on
.mode column
.timer on
```

## 3. Data layers in plain English

### Raw evidence

`source_raceform_v1_record` preserves every physical Source Version 1 record, including the retained excluded row.

Raw values remain evidence. Database v2 does not rewrite the historical third-party source.

### Structural racing core

`core_source_race_occurrence` contains one authorised Source Version 1 race occurrence per exact raw:

```text
date + course + off
```

`core_runner_participation` links each admitted source-backed runner to exactly one structural race occurrence.

### Governed semantic extensions

Database v2 adds explicit governed interpretations instead of forcing every study to rebuild them.

Race-level governed material is stored in:

- `core_source_race_occurrence_governed`;
- `core_source_race_occurrence_time`.

Runner-level governed material is stored in:

- `core_runner_participation_governed`.

Raw source values remain recoverable through lineage.

### Governed references and evidence

Database v2 also stores:

- 395 governed course identities and timezones;
- 16 bounded jurisdiction-context rows;
- 37 source-field treatment rows;
- 85 permanent manual-verification rows;
- 46 connection blank-field decisions;
- 3 missing-runner supplementations;
- 16 specialist horse/pedigree decisions.

### Provisional identity layers

Horse/pedigree and participant identities remain deliberately provisional where the underlying notebooks did not establish a universal real-world identity system.

## 4. Recommended views

### `view_governed_race_occurrences`

Grain: one governed structural race occurrence.

Rows: **189,043**.

Use this as the normal race-level study interface.

It brings together structural race identity with governed race semantics and timing while keeping source lineage available.

### `view_governed_source_runner_participations`

Grain: one source-backed runner participation.

Rows: **1,851,285**.

Use when the analytical population must match admitted physical source runner rows exactly.

### `view_governed_runner_records`

Grain: one governed runner record, including the three accepted missing-runner supplementations.

Rows: **1,851,288**.

This is the normal combined runner interface when the study should use all currently governed runner evidence.

The three supplemented runners are:

- Saucats — Nantes, 18 June 2024, 2:14;
- Tosen Thunder (JPN) — Ohi, 9 October 2025, 11:07;
- Great Navigator (USA) — Gulfstream Park, 23 December 2023, 9:36.

Supplemented rows do not receive invented source-record IDs or unsupported fields.

### `view_governed_horse_occurrence_assignments`

Use when Notebook 19 provisional horse/pedigree occurrence identity is material.

Current baseline:

```text
provisional horse occurrences: 611
transition decisions: 353
Corrected: 92
Different horse: 261
Unresolved: 0
```

### `view_governed_participant_label_identities`

Use when accepted Notebook 22 participant mappings are material.

Current baseline:

```text
source labels: 116,859
accepted provisional identities: 68
accepted label mappings: 149
candidate relationships: 1,205
```

Unresolved participant candidates remain unresolved.

## 5. Grain and identifier rules

Do not use the raw supplied `race_id` as a unique Inside Rails race identifier.

Prefer project-owned stable textual codes such as:

- `source_record_code`;
- `source_race_occurrence_code`;
- `runner_participation_code`.

Internal integer IDs are scoped to one built database release and should not be treated as stable external references.

For race-level analysis, do not count runner rows as independent races.

For runner-count work, distinguish:

- admitted physical source runner rows;
- raw source-reported `ran`;
- governed source coverage status;
- combined governed runner records including external supplementations.

## 6. Important integrated governance

Database v2 integrates the Notebook 04–22 decisions instead of merely exposing raw fields.

### Surface

An explicit `(AW)` course marker supports the bounded value:

`all_weather_unspecified`

Other surfaces remain unresolved under that source-only rule unless another governed field supplies context.

### Distance

Distance is a governed parse of the literal source notation.

Do not describe it as independently verified official distance.

### Starting price

Fractional/evens arithmetic and marker semantics are governed.

The lone raw value:

`F`

remains unresolved because a favourite marker alone does not supply a price.

No odds are invented for it.

### Runner sex

Two exact Notebook 17 source anomalies have bounded accepted corrections:

- Par Coeur (GER): raw `BB` → governed `gelding`;
- La Venezolana (VEN): raw `B` → governed `filly`.

These are exact-record corrections, not global code translations.

### Ratings

The exact raw RPR anomaly:

```text
source rowid 1619851
raw rpr = 775
```

is governed as `invalid_source_value` with analytical RPR null.

No replacement rating is invented.

### Connections

Notebook 20 provides:

```text
raw blank connection fields: 46
externally supplemented: 28
preserved unresolved: 18
```

A supplemented jockey/trainer/owner label is still a governed label, not automatically a real-world participant identity.

### Comments

Comment text is preserved and conservatively state-classified.

Database v2 does not contain a universal narrative parser.

## 7. Advertised start-time governance

Database v2 integrates Notebook 11 race-time reconstruction.

Current baseline:

```text
total races: 189,043
resolved: 169,465
unresolved: 19,578
pre-boundary races: 178,691
explicit post-boundary races: 10,352
```

Decision methods:

```text
course_local_dead_of_night_rejection: 111,871
stable_post_boundary_course_profile: 47,242
explicit_post_boundary_time: 10,352
unresolved: 19,578
```

Format boundary:

`2025-10-15`

These values represent reconstructed advertised/scheduled start time, not automatically exact actual-off time.

## 8. Query recipes

### Confirm the study-facing populations

```sql
SELECT COUNT(*) AS races
FROM view_governed_race_occurrences;

SELECT COUNT(*) AS source_backed_runners
FROM view_governed_source_runner_participations;

SELECT COUNT(*) AS governed_runner_records
FROM view_governed_runner_records;
```

### Field-size distribution from source-backed physical rows

Use the race-level governed interface rather than grouping raw runner rows yourself:

```sql
SELECT
    source_runner_row_count AS runners,
    COUNT(*) AS races
FROM view_governed_race_occurrences
GROUP BY source_runner_row_count
ORDER BY source_runner_row_count;
```

Before using this result in a study, confirm the exact column name with `PRAGMA table_info(view_governed_race_occurrences)` if the query is being developed interactively. The semantic decision is more important than memorising a view column name.

### Inspect a view schema

```sql
PRAGMA table_info(view_governed_race_occurrences);
PRAGMA table_info(view_governed_runner_records);
```

### Search one horse label without claiming universal horse identity

```sql
SELECT *
FROM view_governed_source_runner_participations
WHERE horse = ?
ORDER BY date, off;
```

Use a parameter in Python rather than interpolating names into SQL.

### Inspect unresolved advertised times

```sql
SELECT COUNT(*)
FROM view_governed_race_occurrences
WHERE temporal_resolution_status = 'unresolved';
```

Expected count:

`19578`

## 9. Using pandas efficiently

Do not load all 1.85 million runner rows into pandas for ordinary counting or grouping.

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

- use the accepted Database v2 release;
- open it read-only;
- state the observation grain;
- state whether supplementations are included;
- use governed views where appropriate;
- retain raw/governed distinction in reporting;
- save study outputs outside the database;
- record database path/hash and repository commit for serious results.

Do not:

- modify the accepted release;
- silently fall back to Database v1 or Source Version 1;
- use the validated candidate for normal studies;
- use raw `race_id` as the project race key;
- turn unresolved values into guessed values;
- turn provisional identity candidates into accepted identities;
- create notebook-local infrastructure for a reusable database defect without escalating it.

## 11. Current limitations

- Source Version 1 covers 1 January 2015 through 27 May 2026; Database v2 is not a live feed.
- Some governed values remain unresolved by design.
- Race-time reconstruction is advertised/scheduled time, not guaranteed exact actual-off time.
- Distance parsing is source-literal, not independently verified official distance.
- Horse and participant identity work remains provisional and role/scope bounded.
- Prize currencies outside the governed canonical cases remain unresolved rather than converted by guesswork.
- Raw labels and narrative text remain available because not every source field should be aggressively normalised.
- Historical statistical relationships are not guaranteed betting edges.

## 12. Troubleshooting

### `ModuleNotFoundError: No module named 'inside_rails'`

For command-line Python:

```bash
PYTHONPATH=src python your_script.py
```

For notebooks, start Jupyter with the project `rails` alias.

Do not add `sys.path` hacks to notebooks.

### Unable to open Database v2

Check:

```bash
ls -lh data/processed/database/releases/inside_rails_v2.sqlite3
```

Do not silently switch to another database.

### Unsure which columns a governed view exposes

Use:

```sql
PRAGMA table_info(view_governed_race_occurrences);
PRAGMA table_info(view_governed_source_runner_participations);
PRAGMA table_info(view_governed_runner_records);
```

### A field still looks strange

Check the relevant Notebook 04–22 governance documentation and reusable implementation before inventing a new parser.

## 13. Recommended study workflow

1. State the racing question in one sentence.
2. Read `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.
3. Use the accepted Database v2 release read-only.
4. Declare race/runner grain and population.
5. Select the appropriate governed view.
6. Inspect unresolved states and supplementation consequences.
7. Filter and aggregate in SQL.
8. Move only the needed result into pandas.
9. Check sample size, exceptions and market context.
10. Save the code, result, interpretation and limitations together.

The database should make studies faster because the project no longer needs to rediscover Notebook 04–22 governance every time a familiar racing question is asked.

## Quick command card

```bash
source .venv/bin/activate
PYTHONPATH=src python script.py
rails
sqlite3 -readonly data/processed/database/releases/inside_rails_v2.sqlite3
git status --short --branch
```
