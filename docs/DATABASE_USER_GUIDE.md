# Inside Rails Horse-Racing Database

## Practical User Guide — Database v1

**Guide date:** 8 August 2026  
**Accepted database:** `data/processed/database/releases/inside_rails_v1.sqlite3`

## 1. What this database is

Database v1 is the project's accepted, validated SQLite research database for the supplied historical horse-racing source. It contains:

- the complete retained raw source layer;
- one reconstructed race occurrence for every authorised raw `date + course + off` group;
- one runner participation for every admitted source record;
- stable race, runner and source-record identifiers;
- complete source lineage and build evidence;
- convenient views joining race structure to all 37 raw racing fields.

It is intended for local research, notebook analysis, evidence-backed articles and reusable query development. It is not a live racecard service, a tip generator or a guarantee that a historical pattern will remain profitable.

Treat the accepted release as read-only. The preserved candidate remains in the candidate directory for evidence and rollback, but normal analysis should use the accepted release path above.

### Accepted identity

```text
file size: 1,730,048,000 bytes
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
manifest status: release_accepted
validation-result rows: 7
physical source records retained: 1,851,286
admitted runner records: 1,851,285
reconstructed race occurrences: 189,043
runner participations: 1,851,285
SQLite application_id: 1230130259
SQLite user_version: 1
quick_check: ok
foreign-key check rows: 0
```

The preserved validated candidate remains unchanged at:

```text
path: data/processed/database/candidates/inside_rails_v1_candidate.sqlite3
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
```

The Phase 4 technical gate recorded **354 passing tests** and **all 31 independent validators passing**. The later release-boundary implementation passed **6 focused promotion tests** and the complete repository suite at **360 passing tests** before promotion.

## 2. Two-minute quick start

Run from the repository root:

```bash
cd ~/Documents/inside-rails-horse-racing
source .venv/bin/activate
```

The project uses a `src` layout. Prefix Python commands with `PYTHONPATH=src` unless the package has been installed into the environment.

Confirm the database exists:

```bash
ls -lh data/processed/database/releases/inside_rails_v1.sqlite3
```

Open it read-only in Python:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v1.sqlite3"

with connect_read_only(DATABASE) as connection:
    race_count = connection.execute(
        "SELECT COUNT(*) FROM view_core_source_race_occurrences"
    ).fetchone()[0]
    runner_count = connection.execute(
        "SELECT COUNT(*) FROM view_core_runner_participations"
    ).fetchone()[0]

print(race_count, runner_count)
```

Run it with:

```bash
PYTHONPATH=src python your_script.py
```

Expected counts:

```text
189043 1851285
```

Open it in the SQLite shell:

```bash
sqlite3 -readonly \
  data/processed/database/releases/inside_rails_v1.sqlite3
```

Useful shell settings:

```sql
.headers on
.mode column
.timer on
```

## 3. Database model in plain English

### Retained source records

`source_raceform_v1_record` preserves every physical source record, including the one excluded header-like row at source `rowid = 1`. Original values and SQLite storage classes are retained.

### Reconstructed races

`core_source_race_occurrence` contains one row per authorised race group. A race is reconstructed from the exact raw combination:

```text
date + course + off
```

Use `source_race_occurrence_code` as the stable race identifier. Do not use the raw `race_id` as the primary race key.

### Runner participations

`core_runner_participation` links each admitted raw runner record to exactly one reconstructed race. This provides a reliable one-row-per-runner-in-a-race structure without rewriting the raw racing fields.

## 4. Recommended views

| View | Grain | Best use |
|---|---|---|
| `view_core_runner_participations` | One admitted runner in one reconstructed race | Main analysis view. Includes race code, source lineage and all 37 raw fields. |
| `view_core_source_race_occurrences` | One reconstructed race | Race counts, course/date filtering and actual field size. |
| `view_source_raceform_v1_records` | One retained physical source record | Raw-source inspection, including the retained excluded record. |
| `view_source_record_lineage` | One retained source record | Source row, status and fingerprint auditing. |
| `view_database_release_evidence` | One database build manifest | Build counts, commits and validation flags. |
| `view_import_validation_evidence` | One stored validation result | Builder and release validation evidence. |

For most runner-level analysis, start with `view_core_runner_participations`. For race-level analysis, start with `view_core_source_race_occurrences`.

## 5. Grain and identifiers

A row in `view_core_source_race_occurrences` represents one exact raw `date + course + off` group.

A row in `view_core_runner_participations` represents one admitted source runner record linked to one reconstructed race.

Useful identifiers:

- `runner_participation_code` — stable runner-in-race identity;
- `source_race_occurrence_code` — stable race identity;
- `source_record_code` — stable source-row identity;
- `source_rowid` — original SQLite row number.

The raw source `race_id` is preserved as evidence but is not the authorised structural key.

## 6. Raw field groups

The 37 original fields are preserved as source values rather than universally cleaned analytical variables.

**Race description:** `date`, `course`, `race_id`, `off`, `race_name`, `type`, `class`, `pattern`, `rating_band`, `age_band`, `sex_rest`, `dist`, `going`, `ran`

**Runner and result:** `num`, `pos`, `draw`, `ovr_btn`, `btn`, `horse`, `age`, `sex`, `wgt`, `hg`, `time`

**Market and connections:** `sp`, `jockey`, `trainer`, `owner`

**Ratings and breeding:** `or`, `rpr`, `ts`, `sire`, `dam`, `damsire`

**Money and narrative:** `prize`, `comment`

A column name does not guarantee one uniform type or meaning in every jurisdiction and period. Before arithmetic or grouping, inspect blanks, `typeof(column)`, distinct formats, governed parser conclusions and jurisdiction context.

## 7. Query recipes

### Confirm the population

```sql
SELECT COUNT(*) AS races
FROM view_core_source_race_occurrences;

SELECT COUNT(*) AS runners
FROM view_core_runner_participations;
```

### Recent reconstructed races at a course

```sql
SELECT
    source_race_occurrence_code,
    raw_date,
    raw_course,
    raw_off,
    admitted_runner_count
FROM view_core_source_race_occurrences
WHERE raw_course = 'Ascot'
ORDER BY CAST(raw_date AS TEXT) DESC, CAST(raw_off AS TEXT) DESC
LIMIT 20;
```

Course labels are raw source labels. Inspect distinct labels before assuming spelling and jurisdiction are canonical.

### Every runner in one race

```sql
SELECT
    num,
    horse,
    pos,
    sp,
    jockey,
    trainer,
    "or",
    rpr,
    ts
FROM view_core_runner_participations
WHERE source_race_occurrence_code = ?
ORDER BY
    CASE
        WHEN typeof(num) IN ('integer', 'real') THEN CAST(num AS REAL)
        ELSE 9999
    END,
    source_rowid;
```

### A horse's recorded history

```sql
SELECT
    source_race_occurrence_code,
    date,
    course,
    off,
    race_name,
    pos,
    sp,
    jockey,
    trainer,
    "or",
    rpr,
    ts
FROM view_core_runner_participations
WHERE horse = ?
ORDER BY CAST(date AS TEXT) DESC, CAST(off AS TEXT) DESC;
```

Use a parameter rather than inserting a horse name directly into SQL.

### Races by year

```sql
SELECT
    substr(CAST(raw_date AS TEXT), 1, 4) AS year,
    COUNT(*) AS races
FROM view_core_source_race_occurrences
GROUP BY year
ORDER BY year;
```

### Actual field-size distribution

```sql
SELECT
    admitted_runner_count AS runners,
    COUNT(*) AS races
FROM view_core_source_race_occurrences
GROUP BY admitted_runner_count
ORDER BY admitted_runner_count;
```

Use `admitted_runner_count` rather than trusting raw `ran` when the question is how many admitted source runners the reconstructed race actually contains.

### Raw trainer-label win rates

```sql
SELECT
    trainer,
    COUNT(*) AS runs,
    SUM(CASE WHEN CAST(pos AS TEXT) = '1' THEN 1 ELSE 0 END) AS wins,
    ROUND(
        100.0 * SUM(CASE WHEN CAST(pos AS TEXT) = '1' THEN 1 ELSE 0 END)
        / COUNT(*),
        1
    ) AS win_percentage
FROM view_core_runner_participations
WHERE trainer IS NOT NULL
  AND trim(CAST(trainer AS TEXT)) <> ''
GROUP BY trainer
HAVING COUNT(*) >= 100
ORDER BY win_percentage DESC, runs DESC
LIMIT 50;
```

This groups exact raw trainer labels. Do not present it as fully identity-resolved trainer statistics without checking variants and transitions.

### Inspect storage types

```sql
SELECT
    typeof(prize) AS storage_type,
    COUNT(*) AS rows,
    COUNT(DISTINCT prize) AS distinct_values
FROM view_core_runner_participations
GROUP BY typeof(prize)
ORDER BY rows DESC;
```

### Find source-marked favourites

```sql
SELECT
    source_race_occurrence_code,
    date,
    course,
    horse,
    pos,
    sp
FROM view_core_runner_participations
WHERE typeof(sp) = 'text'
  AND substr(upper(trim(sp)), -1, 1) IN ('F', 'J', 'C')
LIMIT 100;
```

Use the tested starting-price parser before odds arithmetic.

## 8. Using pandas efficiently

Do not load all 1.85 million runner rows into pandas unless the analysis genuinely requires it. Filter and aggregate in SQLite first.

```python
import pandas as pd
from inside_rails.source_sqlite import connect_read_only

query = """
SELECT
    course,
    COUNT(*) AS runner_rows,
    SUM(CASE WHEN CAST(pos AS TEXT) = '1' THEN 1 ELSE 0 END) AS wins
FROM view_core_runner_participations
WHERE CAST(date AS TEXT) >= '2024-01-01'
GROUP BY course
ORDER BY runner_rows DESC
"""

with connect_read_only(DATABASE) as connection:
    course_summary = pd.read_sql_query(query, connection)
```

Recommended pattern:

1. filter in SQL;
2. aggregate in SQL where possible;
3. load only the result into pandas;
4. use pandas for presentation, modelling or charts.

## 9. Tested Python helpers

The database deliberately preserves raw values. Use reusable project modules for interpretations already investigated in notebooks.

```python
from inside_rails.starting_price import parse_starting_price

parsed = parse_starting_price('5/2F')
print(parsed.fractional_odds)
print(parsed.implied_probability)
print(parsed.favourite_status)
```

The starting-price parser handles fractional prices and evens, recognises attached `F`, `J` and `C` markers, preserves missing values and refuses to invent a price for the lone raw value `F`.

General rule: reuse tested logic under `src/inside_rails/` rather than writing a quick parser inside every notebook.

## 10. Performance guidance

Do:

- select only the columns you need;
- filter early;
- aggregate in SQL;
- use `LIMIT` while exploring;
- save stable queries once the population is correct;
- inspect `EXPLAIN QUERY PLAN` when a query is unexpectedly slow.

Avoid:

- `SELECT *` across the complete runner view;
- loading the whole database into pandas for simple counts;
- repeated one-off parsing where reusable logic exists;
- joining on raw labels when a stable identifier is available;
- using raw `race_id` as the race key.

## 11. Safe working rules

Treat database v1 as read-only. Use `connect_read_only` or `sqlite3 -readonly`.

Do not use the database itself as a scratchpad for temporary tables, manual corrections or notebook outputs.

Save analysis outputs separately under a clearly named `data/processed/` or report/output folder.

For a serious result, record:

- database path and SHA-256;
- repository commit;
- exact SQL or Python code;
- population filters and exclusions;
- output row counts;
- interpretation and limitations.

## 12. Important limitations

- The source covers 1 January 2015 to 27 May 2026; it is not a live feed.
- Database v1 is the minimum core, not every governed enrichment as convenient columns.
- Horse, jockey, trainer and owner values remain raw labels and may not be stable identities.
- Mixed text, integer, real, null and blank values are deliberately preserved.
- Prize money, classifications, distance, going and timing conventions vary by jurisdiction.
- Raw implied probability includes bookmaker margin and is not automatically fair probability.
- Historical patterns are not guaranteed betting edges.

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'inside_rails'`

```bash
PYTHONPATH=src python your_script.py
```

For Jupyter:

```bash
PYTHONPATH=src jupyter lab
```

### Unable to open the database

Check the working directory, exact accepted-release path, file existence and read permission.

Do not silently fall back to the candidate or raw source.

### A column behaves strangely

```sql
SELECT typeof(sp), sp, COUNT(*)
FROM view_core_runner_participations
GROUP BY typeof(sp), sp
ORDER BY COUNT(*) DESC
LIMIT 50;
```

### A grouping looks suspicious

Check for raw-label variants, use of `race_id`, unparsed formats or mixed jurisdictions.

## 14. Recommended analysis workflow

1. State the racing question in one sentence.
2. Define the race and runner population before calculating anything.
3. Choose the correct grain.
4. Inspect raw formats, blanks and storage classes.
5. Use stable race codes and source lineage.
6. Apply tested parsers or governed reference data where required.
7. Aggregate in SQL before moving results into pandas.
8. Check sample sizes and exceptions.
9. Compare outcomes with prices rather than only counting winners.
10. Save the code, result and limitations together.

A stronger question than “which horses won most often?” is:

> Under a precisely defined population, did the outcome occur more or less often than the market price implied after accounting for bookmaker margin?

## 15. Useful first projects

- favourite performance by field size, race type and surface;
- market-normalised value by price band;
- course and configuration effects;
- going compared with prior weather reports;
- draw effects under tightly defined course/distance conditions;
- trainer or jockey patterns after identity review;
- class movements and rating changes;
- received racing claims tested source-wide;
- data-quality errors that could mislead a punter reading free racecard data at face value.

The strongest Inside Rails pieces combine a familiar claim, a clearly defined population, transparent code, enough data to measure the effect, honest limits and a plain-English conclusion.

## Quick command card

```bash
source .venv/bin/activate
PYTHONPATH=src python script.py
PYTHONPATH=src jupyter lab
sqlite3 -readonly data/processed/database/releases/inside_rails_v1.sqlite3
git status --short
```
