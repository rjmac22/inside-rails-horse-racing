# Retrospective Manual-Verification Candidates

Generated from committed notebook source and plain-text outputs.
Every candidate requires review before becoming a governed row in `data/reference/manual_verifications.csv`.
Candidate cells found: **390**.

## `notebooks/00_project_scope_and_methodology.ipynb`

### Cell 2

Matched: `racecard`

```text
## Current Source Scope

The downloaded Kaggle dataset contains several related data products rather than one unified database.

The current primary source for the first phase of the project is:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Other supplied products include:

- historical archives covering 1988–2004;
- historical archives covering 2005–2014;
- recent form HTML files;
- daily racecards;
- BHA ratings data;
- Betfair data.

These products will not be combined automatically.

Each source must first be treated as a separate product with its own:

- structure;
- date coverage;
- identifiers;
- update pattern;
- racing meaning;
- data-quality issues;
- potential overlaps with other products.

Relationships between products will only be created after their fields, entities and business meanings have been profiled and compared.
```

### Cell 3

Matched: `manual`, `manually`

```text
## Project Boundaries

### In scope

The project will:

- inspect and document the supplied source data;
- profile tables, columns, types, values and relationships;
- investigate racing-domain meaning before transformation;
- identify entities, candidate keys and business rules;
- design a relational target model;
- build reproducible staging, core and analytical layers;
- validate transformations with explicit tests;
- document limitations, assumptions and unresolved issues;
- preserve a clear audit trail from source to final database.

### Out of scope for the initial database build

The initial phase will not:

- build a betting model;
- claim predictive value from unvalidated fields;
- scrape additional racing websites;
- overwrite or manually edit raw source files;
- merge separate source products solely because their names appear similar;
- impute missing values without a defensible racing or analytical reason;
- remove duplicate-looking records before determining what they represent;
- treat unusual values as errors merely because they are statistical outliers.

The scope may be expanded later, but only through an explicit and documented decision.
```

### Cell 7

Matched: `external`

```text
## Use of External Methodology

The project may draw on techniques from the 2024 book *Data Cleaning with Python for Data Analytics and Modeling* and from established data-engineering practice.

Ideas from external sources will be evaluated rather than copied automatically.

A technique will only be adopted when it:

- fits the structure and meaning of the racing data;
- preserves traceability to the original source;
- improves reproducibility or data quality;
- can be explained and tested;
- does not conceal uncertainty;
- remains appropriate for a relational database project.

Techniques will be adapted or rejected when they rely on assumptions that are unsuitable for this project.

In particular, the project will not assume that:

- missing values should always be imputed;
- duplicate-looking rows should always be deleted;
- outliers are necessarily errors;
- data should be altered merely to make a distribution more regular;
- every source column belongs in the final core model;
- generic cleaning rules are more reliable than racing-domain interpretation.

Where an external method influences a significant decision, the notebook should explain:

1. the original idea;
2. how it was adapted;
3. why it is appropriate here;
4. how the result was validated.
```

### Cell 10

Matched: `published result`

```text
## Missing Values, Duplicates and Outliers

Missing values, duplicate-looking records and unusual values will be investigated in context rather than handled by generic automatic rules.

### Missing values

A missing value may mean:

- the information was not recorded;
- the field was not applicable;
- the value was not yet known at the time of collection;
- the source used another field or code to represent the information;
- the record is incomplete;
- the source extraction failed.

These possibilities must be distinguished where practical. Missingness may itself contain useful information and should not be removed through automatic imputation.

### Duplicate-looking records

Rows that appear identical may represent:

- genuine duplicate ingestion;
- repeated snapshots of changing information;
- separate runners or races with incomplete identifiers;
- amended or republished results;
- records that differ only in fields not initially inspected.

Duplicates will therefore be tested against the expected grain of the table before any removal rule is considered.

### Outliers and unusual values

Extreme values may reflect:

- exceptional but valid race conditions or performances;
- different units or encodings;
- historical rule changes;
- data-entry or extraction errors;
- a field whose meaning has been misunderstood.

Statistical rarity alone is not sufficient evidence that a value is wrong.
```

## `notebooks/01_source_database_structure_profile.ipynb`

### Cell 30

Matched: `manual`

```text
# List the columns that count distinct values for fields expected to describe
# the race rather than an individual runner.
consistency_fields = [
    "distinct_dates",
    "distinct_courses",
    "distinct_off_times",
    "distinct_race_names",
    "distinct_types",
    "distinct_classes",
    "distinct_distances",
    "distinct_going_values",
    "distinct_ran_values",
]

# Count how many apparently race-level fields conflict within each race_id.
#
# This score is used only to rank groups for manual inspection. It is not a
# final data-quality severity measure.
race_level_consistency["inconsistent_field_count"] = sum(
    race_level_consistency[column].gt(1).astype(int)
    for column in consistency_fields
)

# Show the ten race_id groups with the greatest number of conflicting fields.
# Larger groups are shown first when the conflict count is tied.
most_inconsistent_race_ids = (
    race_level_consistency
    .sort_values(
        ["inconsistent_field_count", "row_count"],
        ascending=[False, False],
    )
    .head(10)
    .reset_index(drop=True)
)

display(most_inconsistent_race_ids)
   race_id  row_count  distinct_dates  distinct_courses  distinct_off_times  \
0   630000         57               4                 5                   5   
1   620000         45               3                 4                   3   
2   739000         43               4                 4                   4   
3   740000         38               3                 3                   3   
4   649000         36               3                 3                   3   
5   650007         36               3                 3                   3   
6   653000         35               3                 3                   3   
7   883000         35               3                 3
…
```

### Cell 45

Matched: `external`

```text
**Initial contextual hypothesis**

The lower 2020 volume is likely related to COVID-19 disruption, including periods when racing was suspended or operated under restrictions.

That explanation is plausible from external historical context, but it is not demonstrated by the source database itself. The structural finding here is simply that 2020 contains materially fewer races and runner rows than surrounding complete years.
```

### Cell 66

Matched: `checked against`

```text
### Rare `sex` code findings

**Profiling evidence**

The two rare runner-sex values occur in international Flat-racing records:

- `BB`: Par Coeur at Cologne, Germany, on 15 October 2017;
- `B`: La Venezolana at Gulfstream Park, United States, on 29 November 2019.

**Interpretation**

The values may be jurisdiction-specific sex descriptions or source abbreviations rather than simple data-entry errors.

Their precise meaning is not established by the database itself. They should remain unchanged until checked against reliable racing-domain documentation or the original source representation.
```

### Cell 88

Matched: `racing post`

```text
# Create a concise field-investigation register from the structural evidence
# collected so far.
#
# This does not clean or redesign the data. It records why selected source
# fields need additional profiling in later notebooks.
field_investigation_register = pd.DataFrame(
    [
        {
            "field": "race_id",
            "observed_issue": "Reused across different dates, courses and races",
            "later_question": "Can a reliable source race identifier be reconstructed?",
        },
        {
            "field": "course",
            "observed_issue": "Combines course identity, jurisdiction and surface markers",
            "later_question": "How should course, country and surface be separated?",
        },
        {
            "field": "num",
            "observed_issue": "Blank, zero and shared positive values occur",
            "later_question": "Which numbering conventions apply by jurisdiction?",
        },
        {
            "field": "pos",
            "observed_issue": "Contains finishing positions and non-finish codes",
            "later_question": "How should numeric placings and outcome codes be represented?",
        },
        {
            "field": "or",
            "observed_issue": "Contains integers and dash placeholders",
            "later_question": "How should unavailable official ratings be represented?",
        },
        {
            "field": "rpr",
            "observed_issue": "Contains integers and dash placeholders",
            "later_question": "How should unavailable Racing Post Ratings be represented?",
        },
        {
            "field": "ts",
            "observed_issue": "Contains integers and dash placeholders",
            "later_question": "How should unavailable Topspeed ratings be represented?",
…
```

## `notebooks/02_source_field_quality_profile.ipynb`

### Cell 41

Matched: `verified`

```text
### Runner identity and demographics — interim findings

#### `num`

The field is declared as `INTEGER` but uses mixed SQLite storage:

- 1,844,253 rows contain integers;
- 7,032 rows contain blank text;
- numeric values range from 0 to 40.

The value `0` occurs 1,179 times and is concentrated in particular jurisdictions and meetings. It appears to function as a source convention in at least some races rather than as an ordinary runner number.

Populated positive values are not universally unique within a race:

- 523 duplicated positive-number groups;
- 362 apparent races affected;
- 29 courses affected;
- up to four runners share one positive number.

These duplicates are heavily concentrated in South American and North American racing and may represent jurisdiction-specific coupled-entry or betting-number conventions.

`num` must therefore not be used as a universal runner identifier without further domain rules.

#### `horse`

The field is fully populated and has no outer whitespace.

Every one of the 208,631 distinct stored horse names ends with a terminal parenthesised suffix. There are 51 distinct suffix forms.

Removing the suffix would be unsafe:

- 200,156 distinct base names remain;
- 7,635 base names occur with multiple suffixes;
- some base names occur with as many as five suffixes.

The complete stored name should therefore remain intact until the suffix has been separately verified and parsed.

#### `age`

The field is fully populated and stored consistently as integers.

Most values range from 2 to 16. Rare older ages of 17 and 18 were supported by consistent histories for long-running National Hunt horses.

Two separate quality patterns were identified:

- one Australian-bred horse is stored as age 1 in five British 2-year-old races, suggesting a system
…
```

### Cell 65

Matched: `racing post`

```text
# Profile the performance-measure fields:
# prize, official rating, Racing Post Rating, and Topspeed.
#
# This first pass records missingness, distinct counts, and SQLite storage
# classes without yet interpreting the values.

performance_fields = [
    "prize",
    "or",
    "rpr",
    "ts",
]

performance_profile_rows = []

for field in performance_fields:
    quoted_field = f'"{field}"'

    result = pd.read_sql_query(
        f"""
        SELECT
            COUNT(*) AS total_rows,

            SUM(
                CASE
                    WHEN {quoted_field} IS NULL
                    THEN 1 ELSE 0
                END
            ) AS null_count,

            SUM(
                CASE
                    WHEN typeof({quoted_field}) = 'text'
                     AND length(trim({quoted_field})) = 0
                    THEN 1 ELSE 0
                END
            ) AS blank_text_count,

            COUNT(DISTINCT {quoted_field})
                AS distinct_non_null_values,

            SUM(
                CASE
                    WHEN typeof({quoted_field}) = 'null'
                    THEN 1 ELSE 0
                END
            ) AS storage_null,

            SUM(
                CASE
                    WHEN typeof({quoted_field}) = 'integer'
                    THEN 1 ELSE 0
                END
            ) AS storage_integer,

            SUM(
                CASE
                    WHEN typeof({quoted_field}) = 'real'
                    THEN 1 ELSE 0
                END
            ) AS storage_real,

            SUM(
                CASE
                    WHEN typeof({quoted_field}) = 'text'
                    THEN 1 ELSE 0
                END
            ) AS storage_text,

            SUM(
                CASE
                    WHEN typeof({quoted
…
```

### Cell 68

Matched: `racing post`

```text
## Performance and prize fields: findings

### `prize`

- The field contains no SQL `NULL` values.
- Missing values are stored as blank text.
- Populated values use two storage conventions:
  - numeric SQLite values for non-euro prize amounts;
  - text beginning with `€` for euro-denominated prize amounts.
- Euro values may contain:
  - decimal amounts;
  - thousands separators.
- No other non-blank text formats were found.
- Currency must therefore be preserved or derived separately rather than
  treating `prize` as one currency-neutral numeric field.

### `or`

- Official ratings are stored as integers when available.
- Missing values are represented by the en dash `–`.
- Numeric values range from 1 to 181.
- The maximum value of 181 appears twice for the same high-class hurdle horse
  and is not treated as an obvious source error.

### `rpr`

- Racing Post Ratings are stored as integers when available.
- Missing values are represented by the en dash `–`.
- Almost all values are within a plausible range.
- One row contains `rpr = 775`, which is an obvious isolated source anomaly and
  should be retained in the raw layer but flagged during transformation.

### `ts`

- Topspeed ratings are stored as integers when available.
- Missing values are represented by the en dash `–`.
- Numeric values range from 1 to 178.
- No obvious extreme anomalies were identified.

### Transformation implications

The raw values should remain unchanged. A later transformation layer should:

1. convert `–` to missing for `or`, `rpr`, and `ts`;
2. cast valid ratings to nullable integers;
3. flag implausible rating outliers such as `rpr = 775`;
4. parse `prize` into separate numeric amount and currency fields;
5. preserve the original `prize` value for auditability.
```

## `notebooks/03_race_identity_and_source_key_reconstruction.ipynb`

### Cell 10

Matched: `racecard`

```text
# Test whether runner number is unique within each provisional race.
#
# The source field `num` may represent a racecard number rather than a unique
# participant identifier. Coupled entries in some jurisdictions can share a
# betting number, and malformed or duplicated values may also occur.
#
# Blank runner numbers are excluded from this test because they represent
# missing values rather than an attempted identifier.

duplicate_num_within_race_sql = f"""
WITH numbered_runner_groups AS (
    SELECT
        date,
        course,
        off,
        race_name,
        CAST(num AS TEXT) AS num,
        COUNT(*) AS runner_rows,
        COUNT(DISTINCT horse) AS distinct_horses,
        COUNT(DISTINCT CAST(race_id AS TEXT)) AS distinct_race_ids
    FROM {SOURCE_TABLE}
    WHERE {DATA_ROW_PREDICATE}
      AND TRIM(CAST(num AS TEXT)) <> ''
    GROUP BY
        date,
        course,
        off,
        race_name,
        CAST(num AS TEXT)
    HAVING COUNT(*) > 1
)
SELECT
    date,
    course,
    off,
    race_name,
    num,
    runner_rows,
    distinct_horses,
    distinct_race_ids
FROM numbered_runner_groups
ORDER BY
    runner_rows DESC,
    date,
    course,
    off,
    race_name,
    num
"""

duplicate_num_within_race = pd.read_sql_query(
    duplicate_num_within_race_sql,
    connection,
)

print(
    "Provisional race + runner-number groups containing multiple rows:",
    len(duplicate_num_within_race),
)

duplicate_num_within_race

Provisional race + runner-number groups containing multiple rows: 700

           date             course    off  \
0    2026-03-21             Chukyo  06:20   
1    2016-12-07  Lyon-La Soie (FR)   5:10   
2    2018-11-04        Kyoto (JPN)   6:01   
3    2026-03-21           Nakayama  06:45   
4    2018-08-16     Mombetsu (JPN)  11:07
…
```

### Cell 11

Matched: `racecard`

```text
# Separate duplicate runner-number groups into zero and non-zero values.
#
# This distinguishes races where `num = 0` behaves like a missing-value
# sentinel from races where a non-zero betting or racecard number is shared
# by multiple horses, potentially representing coupled entries.

duplicate_num_profile_sql = f"""
WITH duplicate_number_groups AS (
    SELECT
        date,
        course,
        off,
        race_name,
        TRIM(CAST(num AS TEXT)) AS num_text,
        COUNT(*) AS runner_rows,
        COUNT(DISTINCT horse) AS distinct_horses
    FROM {SOURCE_TABLE}
    WHERE {DATA_ROW_PREDICATE}
      AND TRIM(CAST(num AS TEXT)) <> ''
    GROUP BY
        date,
        course,
        off,
        race_name,
        TRIM(CAST(num AS TEXT))
    HAVING COUNT(*) > 1
)
SELECT
    CASE
        WHEN num_text IN ('0', '0.0') THEN 'zero'
        ELSE 'non-zero'
    END AS number_category,
    COUNT(*) AS duplicate_groups,
    SUM(runner_rows) AS runner_rows,
    MIN(runner_rows) AS minimum_rows_per_group,
    MAX(runner_rows) AS maximum_rows_per_group
FROM duplicate_number_groups
GROUP BY number_category
ORDER BY number_category DESC
"""

duplicate_num_profile = pd.read_sql_query(
    duplicate_num_profile_sql,
    connection,
)

duplicate_num_profile
  number_category  duplicate_groups  runner_rows  minimum_rows_per_group  \
0            zero               177         1170                       2   
1        non-zero               523         1084                       2   

   maximum_rows_per_group  
0                      17  
1                       4
```

### Cell 29

Matched: `racecard`

```text
# Consolidate the principal identity findings into one validation table.
#
# This cell does not create identifiers or design the target schema. It records
# the observed evidence supporting or rejecting each source-key candidate.
#
# The resulting table will make the distinction clear between:
# - uniqueness in the current extract;
# - semantic suitability as an identity rule;
# - and source-lineage usefulness.

identity_evidence = pd.DataFrame(
    [
        {
            "candidate_or_field": "race_id",
            "observed_groups_or_rows": 188_782,
            "collision_or_reuse_evidence": "206 values occur on multiple dates",
            "current_extract_unique": False,
            "provisional_role": "Preserve as a source attribute only",
        },
        {
            "candidate_or_field": "date + race_id",
            "observed_groups_or_rows": 189_035,
            "collision_or_reuse_evidence": "8 pairs each describe two different races",
            "current_extract_unique": False,
            "provisional_role": "Insufficient race identity",
        },
        {
            "candidate_or_field": "date + course + off",
            "observed_groups_or_rows": 189_043,
            "collision_or_reuse_evidence": "No collisions observed",
            "current_extract_unique": True,
            "provisional_role": "Leading candidate race identity",
        },
        {
            "candidate_or_field": "date + course + off + race_name",
            "observed_groups_or_rows": 189_043,
            "collision_or_reuse_evidence": "No collisions observed",
            "current_extract_unique": True,
            "provisional_role": "Conservative provisional race grouping",
        },
        {
            "candidate_or_field": "race grouping + horse",
            "obse
…
```

### Cell 30

Matched: `racecard`

```text
## Interim identity findings

### Observations

1. The supplied `race_id` is not globally unique.

   - 188,782 distinct values occur across 189,043 provisional races.
   - 206 `race_id` values occur on more than one date.
   - One identifier occurs on five separate dates.
   - The repeated identifiers refer to unrelated races across different dates, courses and jurisdictions.

2. Adding `date` does not make `race_id` reliable.

   - There are 189,035 distinct `date + race_id` combinations.
   - Eight combinations each contain two clearly different races.
   - These collisions include different courses or different races at the same course.

3. The descriptive race grouping is internally consistent.

   - `date + course + off + race_name` produces 189,043 groups.
   - No descriptive group contains multiple `race_id` values.
   - No `date + course + off` combination contains multiple race names.
   - `date + course + off` therefore also produces 189,043 groups in this extract.
   - Every identity component is populated on every data-like row.
   - Trimming outer whitespace and ignoring case does not merge any race groups.

4. Off-time is necessary for race identity.

   - Omitting `off` creates 451 colliding `date + course + race_name` groups.
   - Those groups contain 967 actual races.
   - Merging them would lose 516 races and affect 10,410 runner rows.
   - Up to six races at one meeting share the same supplied race name.

5. Horse name is unique within the provisional race grouping.

   - `date + course + off + race_name + horse` produces 1,851,285 groups.
   - No horse occurs twice within one provisional race.
   - No horse appears in multiple provisional races at the same course on the same date.

6. Runner number is not an individual-runner identifier.

   - 700 p
…
```

### Cell 32

Matched: `racecard`

```text
## Notebook conclusion

### Answer to the bounded question

A race can be identified reliably within the current source by using the descriptive meeting slot:

`date + course + off`

This combination produces 189,043 distinct race groups and has no observed collisions in the current extract.

For conservative source reconstruction, `race_name` should remain attached to the grouping:

`date + course + off + race_name`

Although `race_name` does not create any additional groups in this extract, it provides a descriptive validation field and may expose anomalies in future or amended snapshots.

A runner record can be identified within a reconstructed race by adding the supplied horse name:

`date + course + off + race_name + horse`

This combination is complete and unique across all 1,851,285 data-like source rows.

These combinations are suitable as **candidate natural matching rules**, not as permanent database identifiers.

### Why the supplied identifiers are insufficient

The supplied `race_id` cannot serve as a globally unique race key:

- 206 values occur on multiple dates;
- some values are reused for unrelated races across courses and jurisdictions;
- eight `date + race_id` combinations each refer to two different races.

The supplied `num` cannot serve as an individual-runner key:

- 700 race-and-number groups contain multiple horses;
- `0` frequently acts as an unavailable-number sentinel;
- non-zero values may represent coupled betting entries;
- some duplicate non-zero values do not behave consistently enough to support one universal interpretation.

### Repeated and amended records

No exact repeated records were found:

- no duplicate rows exist across all supplied columns;
- no horse occurs twice within one provisional race;
- no horse occurs in multiple pr
…
```

## `notebooks/04_course_jurisdiction_and_surface_mapping.ipynb`

### Cell 21

Matched: `external`

```text
# Measure race-level surface coverage using only direct source evidence.
#
# Evidence hierarchy for this diagnostic:
#
# 1. An explicit surface term in race_name:
#    - Turf
#    - Dirt
#    - Polytrack
#    - Tapeta
#    - other All-Weather Track wording
#
# 2. If race_name has no explicit surface term, a course name containing
#    "(AW)" supplies broad all-weather evidence.
#
# 3. Otherwise, surface remains unresolved.
#
# This cell does not use external course knowledge or infer that all British
# Flat races are turf. It measures only what can be derived directly from the
# current source fields.

def derive_direct_surface_evidence(row):
    """Return provisional surface and evidence source from direct raw evidence."""
    if row["race_name_marks_turf"]:
        return pd.Series(
            ["turf", "race_name_explicit_turf"]
        )

    if row["race_name_marks_dirt"]:
        return pd.Series(
            ["dirt", "race_name_explicit_dirt"]
        )

    if row["race_name_marks_polytrack"]:
        return pd.Series(
            ["synthetic_polytrack", "race_name_explicit_polytrack"]
        )

    if row["race_name_marks_tapeta"]:
        return pd.Series(
            ["synthetic_tapeta", "race_name_explicit_tapeta"]
        )

    if row["race_name_marks_all_weather_track"]:
        return pd.Series(
            ["all_weather_unspecified", "race_name_explicit_all_weather"]
        )

    if row["course_marks_aw"]:
        return pd.Series(
            ["all_weather_unspecified", "course_name_aw_marker"]
        )

    return pd.Series(
        ["unresolved", "no_direct_surface_evidence"]
    )

surface_evidence[
    ["direct_surface", "surface_evidence_source"]
] = surface_evidence.apply(
    derive_direct_surface_evidence,
    axis=1,
)

direct_surface_cove
…
```

### Cell 36

Matched: `external`

```text
# Inspect every post-suffix-change Flat race at the three colliding course names.
#
# This produces the small race-level set that may require either:
# - direct contextual classification from source fields; or
# - external race-result verification.
#
# Useful evidence includes:
# - full race name;
# - off time;
# - going;
# - distance;
# - horse, jockey and trainer nationality context;
# - whether the race name explicitly states a surface.
#
# One representative runner is selected per provisional race, preferring
# the winner where available. No jurisdiction is assigned in this cell.

post_change_collision_flat_sql = f"""
WITH ranked_rows AS (
    SELECT
        rowid AS source_rowid,
        date,
        course,
        off,
        race_name,
        type,
        race_id,
        dist,
        going,
        age,
        class,
        ran,
        horse,
        jockey,
        trainer,
        draw,
        time,
        pos,
        ROW_NUMBER() OVER (
            PARTITION BY
                date,
                course,
                off,
                race_name,
                type
            ORDER BY
                CASE
                    WHEN CAST(pos AS TEXT) = '1' THEN 0
                    ELSE 1
                END,
                rowid
        ) AS row_rank
    FROM {SOURCE_TABLE}
    WHERE {DATA_ROW_PREDICATE}
      AND course IN ('Ascot', 'Sandown', 'Newcastle')
      AND type = 'Flat'
      AND date >= '2025-10-15'
)
SELECT
    source_rowid,
    date,
    course,
    off,
    race_name,
    race_id,
    dist,
    going,
    age,
    class,
    ran,
    horse,
    jockey,
    trainer,
    draw,
    time
FROM ranked_rows
WHERE row_rank = 1
ORDER BY
    course,
    date,
    off
"""

post_change_collision_flat_races = pd.read_sql_query(
    pos
…
```

### Cell 40

Matched: `external`

```text
### Surface derivation reset

An earlier attempt derived surface from words such as `Turf`, `Dirt`, `Polytrack`, `Tapeta` and `All-Weather` in `race_name`.

Inspection showed that these terms frequently occur in sponsor names, promotions, memorials and series titles rather than describing the racing surface. That derivation was therefore rejected.

From this point onward:

- `race_name` is not used to derive canonical surface;
- only an explicit `(AW)` marker in raw `course` provides direct source-level surface evidence;
- all remaining surface values stay unresolved pending later external enrichment.
```

### Cell 45

Matched: `external`

```text
# Build the candidate venue/configuration inventory required for curated
# surface mapping.
#
# One row is produced for each:
#     candidate jurisdiction + candidate course label
#
# The inventory retains configuration markers such as:
# - (AW)
# - (July)
# - (RH)
# - (Perth)
#
# It reports:
# - raw course forms represented;
# - race and runner volume;
# - disciplines observed;
# - date coverage;
# - whether the source itself explicitly marks the configuration as AW.
#
# This is the appropriate grain for external venue/surface research.
# No additional surface is inferred in this cell.

runner_counts_by_race = pd.read_sql_query(
    f"""
    SELECT
        date,
        course,
        off,
        race_name,
        type,
        COUNT(*) AS runner_rows
    FROM {SOURCE_TABLE}
    WHERE {DATA_ROW_PREDICATE}
    GROUP BY
        date,
        course,
        off,
        race_name,
        type
    """,
    connection,
)

venue_configuration_inventory = (
    surface_course_only_profile
    .merge(
        runner_counts_by_race,
        on=[
            "date",
            "course",
            "off",
            "race_name",
            "type",
        ],
        how="left",
    )
    .groupby(
        [
            "candidate_jurisdiction",
            "candidate_course_label",
        ],
        as_index=False,
    )
    .agg(
        raw_course_forms=("course", "nunique"),
        raw_course_values=(
            "course",
            lambda values: tuple(sorted(set(values))),
        ),
        provisional_races=("race_name", "size"),
        runner_rows=("runner_rows", "sum"),
        disciplines=(
            "type",
            lambda values: tuple(sorted(set(values))),
        ),
        active_dates=("date", "nunique"),
        first_date=("date", "min"),
…
```

### Cell 46

Matched: `external`

```text
# Prioritise the curated surface-reference backlog by database coverage.
#
# The source directly supports seven all-weather configurations.
# The remaining 388 configurations require external or curated reference data.
#
# This cell ranks the unresolved configurations by provisional race volume and
# calculates cumulative coverage. It shows how many races and runner rows would
# be covered by researching the top:
# - 10
# - 25
# - 50
# - 100
# - 200
# - all remaining configurations
#
# No surface value is inferred or assigned.

surface_reference_backlog = (
    venue_configuration_inventory.loc[
        ~venue_configuration_inventory["source_aw_marker_present"]
    ]
    .sort_values(
        [
            "provisional_races",
            "runner_rows",
            "candidate_jurisdiction",
            "candidate_course_label",
        ],
        ascending=[False, False, True, True],
    )
    .reset_index(drop=True)
)

surface_reference_backlog["research_priority"] = (
    surface_reference_backlog.index + 1
)

surface_reference_backlog["cumulative_races"] = (
    surface_reference_backlog["provisional_races"].cumsum()
)

surface_reference_backlog["cumulative_runner_rows"] = (
    surface_reference_backlog["runner_rows"].cumsum()
)

total_backlog_races = surface_reference_backlog[
    "provisional_races"
].sum()

total_backlog_runner_rows = surface_reference_backlog[
    "runner_rows"
].sum()

surface_reference_backlog["cumulative_race_coverage"] = (
    surface_reference_backlog["cumulative_races"]
    / total_backlog_races
)

surface_reference_backlog["cumulative_runner_coverage"] = (
    surface_reference_backlog["cumulative_runner_rows"]
    / total_backlog_runner_rows
)

priority_thresholds = [
    10,
    25,
    50,
    100,
    200,
    len(surface_reference_ba
…
```

### Cell 47

Matched: `external`, `verified`

```text
# Consolidate Notebook 04's candidate mapping recommendations.
#
# This records the conclusions supported by the profiling work without
# implementing a final production schema.
#
# Distinctions:
# - raw source attributes must always be preserved;
# - candidate derived attributes are supported by current evidence;
# - unresolved attributes require a better external source rather than
#   increasingly speculative inference.

notebook_04_recommendations = pd.DataFrame(
    [
        {
            "area": "Raw course",
            "recommendation": (
                "Preserve the exact raw course value unchanged."
            ),
            "status": "Required source attribute",
            "reason": (
                "Parenthetical elements encode jurisdiction, surface, "
                "configuration, orientation and location context."
            ),
        },
        {
            "area": "Candidate jurisdiction",
            "recommendation": (
                "Derive jurisdiction using explicit terminal codes, "
                "historical suffix links, curated British configurations "
                "and narrowly bounded race-context collision rules."
            ),
            "status": "Candidate derived attribute",
            "reason": (
                "All 189,043 provisional races were assigned while keeping "
                "Ascot, Newcastle and Sandown cross-jurisdiction identities "
                "separate."
            ),
        },
        {
            "area": "Candidate venue identity",
            "recommendation": (
                "Use candidate jurisdiction plus the course label after "
                "removing only a recognised terminal jurisdiction suffix."
            ),
            "status": "Candidate natural identity",
            "reas
…
```

### Cell 48

Matched: `external`

```text
# Build the quantitative evidence summary for Notebook 04 closeout.
#
# This cell records the principal observed counts supporting the recommendations.
# It does not introduce any new inference.

notebook_04_evidence_summary = pd.DataFrame(
    [
        {
            "finding": "Raw course values",
            "value": 528,
            "unit": "distinct raw values",
            "interpretation": (
                "Raw course is descriptive source data, not a clean venue key."
            ),
        },
        {
            "finding": "Provisional races",
            "value": 189043,
            "unit": "date + course + off groups",
            "interpretation": (
                "Current race-level profiling grain."
            ),
        },
        {
            "finding": "Candidate venue/configuration identities",
            "value": 395,
            "unit": "jurisdiction-qualified identities",
            "interpretation": (
                "Recognised terminal jurisdiction suffixes removed while "
                "configuration markers are retained."
            ),
        },
        {
            "finding": "Candidate venues with multiple raw forms",
            "value": 135,
            "unit": "candidate identities",
            "interpretation": (
                "Mostly suffixed-to-unsuffixed source-format variants."
            ),
        },
        {
            "finding": "Same-date candidate venue collisions",
            "value": 0,
            "unit": "collision records",
            "interpretation": (
                "No evidence that the candidate venue identity merges "
                "coexisting raw venue forms."
            ),
        },
        {
            "finding": "Jurisdiction-assigned races",
            "value": 189043,
            "uni
…
```

### Cell 49

Matched: `external`

```text
## Notebook 04 conclusion

### Main conclusion

The source supports a reliable candidate mapping for jurisdiction and venue/configuration identity, but it does not support complete race-surface derivation on its own.

### What the source supports

- Preserve the exact raw `course` value unchanged.
- Derive candidate jurisdiction using:
  - recognised terminal jurisdiction codes;
  - historical links between suffixed and unsuffixed course forms;
  - curated British course/configuration values;
  - narrowly bounded rules for Ascot, Newcastle and Sandown.
- Use:

  `candidate_jurisdiction + candidate_course_label`

  as the candidate venue/configuration identity, where only a recognised terminal jurisdiction suffix is removed.
- Retain meaningful configuration markers such as `(AW)`, `(July)`, `(RH)` and `(Perth)`.
- Assign `all_weather_unspecified` only where the raw course explicitly contains `(AW)`.
- Preserve raw `type` and flag the 16 explicit NH Flat conflicts for separate validation.

### Evidence

- 528 distinct raw course values.
- 189,043 provisional races.
- 395 candidate jurisdiction-qualified venue/configuration identities.
- 135 candidate identities represented by multiple raw course forms.
- 0 same-date collisions between multiple raw forms of the same candidate identity.
- Candidate jurisdiction assigned to all 189,043 provisional races.
- 33,023 races, or 17.47%, have direct course-level all-weather evidence.
- 156,020 races remain unresolved for surface.
- Race-name surface inference was rejected because sponsor names, promotions, memorials and series titles repeatedly produced false matches.

### Interpretation

The candidate jurisdiction and venue/configuration mappings are sufficiently supported for later staging design.

Surface is different. The sour
…
```

### Cell 52

Matched: `external`

```text
# Write the Notebook 04 closeout record.
#
# This records the final validated findings and the files affected by the
# notebook. It does not modify the raw source database.

from pathlib import Path
import json

closeout_path = (
    PROJECT_ROOT
    / "docs"
    / "NOTEBOOK_04_CLOSEOUT.json"
)

notebook_04_closeout = {
    "notebook": "notebooks/04_course_jurisdiction_and_surface_mapping.ipynb",
    "status": "complete",
    "source_database": (
        "data/raw/form_2015-present/form_2015-present/raceform.db"
    ),
    "source_table": "data",
    "profiling_grain": {
        "provisional_race_key": [
            "date",
            "course",
            "off",
        ],
        "provisional_races": 189043,
    },
    "validated_findings": {
        "raw_course_values": 528,
        "candidate_jurisdictions_assigned": 189043,
        "candidate_venue_configuration_identities": 395,
        "candidate_venues_with_multiple_raw_forms": 135,
        "same_date_candidate_venue_collisions": 0,
        "course_supported_all_weather_races": 33023,
        "course_supported_surface_coverage_pct": 17.47,
        "surface_unresolved_from_source": 156020,
        "explicit_nh_flat_type_conflicts": 8,
    },
    "decisions": [
        "Preserve the exact raw course value.",
        (
            "Derive candidate jurisdiction using recognised terminal codes, "
            "historical suffix links, curated British configurations and "
            "bounded collision rules."
        ),
        (
            "Use candidate jurisdiction plus candidate course label as the "
            "candidate venue/configuration identity."
        ),
        (
            "Remove only recognised terminal jurisdiction suffixes from the "
            "candidate course label."
        ),
        (
…
```

### Cell 57

Matched: `external`

```text
# Update the project entry documentation after completing Notebook 04.
#
# Changes:
# - replace the README's "next study" statement with the validated Notebook 04
#   findings and the next bounded study;
# - mark course/jurisdiction/surface mapping complete in the project plan;
# - set Notebook 05 as the current next action.
#
# The raw source database is not modified.

from pathlib import Path

readme_path = PROJECT_ROOT / "README.md"
project_plan_path = PROJECT_ROOT / "docs" / "PROJECT_PLAN.md"

readme_text = readme_path.read_text(encoding="utf-8")

old_readme_text = (
    "The next bounded study is course, jurisdiction and surface mapping. "
    "Final target-schema design remains deferred."
)

new_readme_text = """Notebook 04 established that:

- all 189,043 provisional races can receive a candidate jurisdiction;
- 528 raw course values reduce to 395 jurisdiction-qualified candidate venue/configuration identities;
- recognised terminal jurisdiction suffixes can be removed while retaining meaningful markers such as `(AW)`, `(July)`, `(RH)` and `(Perth)`;
- the 135 candidate identities represented by multiple raw forms have no same-date form collisions;
- 33,023 races have direct all-weather evidence from an explicit `(AW)` course marker;
- `race_name` is not reliable for surface derivation;
- the remaining 156,020 surface values require later external race-level enrichment;
- eight reproducible explicit NH Flat/type conflicts require separate validation.

The next bounded study is finishing position and non-finish outcomes. Final target-schema design remains deferred."""

assert old_readme_text in readme_text

readme_path.write_text(
    readme_text.replace(old_readme_text, new_readme_text),
    encoding="utf-8",
)

project_plan_text = project_plan_path.read_text(enc
…
```

### Cell 60

Matched: `https://`

```text
# Push the completed Notebook 04 commit to origin/main and verify alignment.

import subprocess

push_result = subprocess.run(
    ["git", "push", "origin", "main"],
    cwd=PROJECT_ROOT,
    check=True,
    capture_output=True,
    text=True,
)

print(push_result.stdout or push_result.stderr)

verification = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--branch",
    ],
    cwd=PROJECT_ROOT,
    check=True,
    capture_output=True,
    text=True,
)

print("Repository verification:")
print(verification.stdout)

To https://github.com/rjmac22/inside-rails-horse-racing.git
   9182461..abfa869  main -> main

Repository verification:
## main...origin/main
```

## `notebooks/05_finishing_position_and_non_finish_outcomes.ipynb`

### Cell 24

Matched: `https://`, `external`, `published result`, `verified`

```text
# Record the externally verified Morphettville source anomaly separately from
# the general profiling logic.
#
# This does not alter or overwrite the raw source record. It creates a
# notebook-level audit record describing:
# - the exact source row affected;
# - the observed raw values;
# - the externally supported result;
# - the handling decision for later staging work.
#
# Final schema design remains deferred.

externally_verified_source_anomalies = pd.DataFrame(
    [
        {
            "source_rowid": 55516,
            "date": "2015-05-16",
            "course": "Morphettville (AUS)",
            "off": "4:38",
            "race_id": 627591,
            "horse": "Cinnamon Carter (AUS)",

            # Exact raw source values.
            "raw_pos": 10,
            "raw_btn": 0.50,
            "raw_ovr_btn": 8.75,

            # Externally supported published result.
            "verified_finish_position": 12,
            "verified_dead_heat": True,
            "verified_tied_with": "Mighty Maher (AUS)",
            "verified_position_13_skipped": True,

            # The published margin differs slightly across representation and
            # rounding conventions, so it is recorded descriptively rather
            # than used to overwrite the raw distance value.
            "verified_margin_note": (
                "Published result places Cinnamon Carter in a dead heat for "
                "12th with Mighty Maher; source position 10 is inconsistent."
            ),

            # External evidence retained for reproducibility and audit.
            "verification_source": "Breednet SA Fillies Classic 2015 result",
            "verification_url": (
                "https://www.breednet.com.au/stakes-race-results/"
                "race-history?racename=sajc+fi
…
```

### Cell 42

Matched: `external`, `verified`

```text
# Add candidate validation flags for the result anomalies established so far.
#
# These flags remain separate from the candidate result representation:
# - they describe source quality or unusual result structure;
# - they do not overwrite pos, ran, btn, or ovr_btn;
# - one source row may legitimately carry more than one flag.
#
# Flags covered here:
# - unresolved numeric pos = 0;
# - numeric pos greater than ran;
# - duplicate positive numeric position within a provisional race;
# - duplicate position with inconsistent ovr_btn values;
# - race source-row count below ran;
# - externally verified Morphettville source anomaly.

result_validation_flags = pd.read_sql_query(
    f"""
    WITH race_counts AS (
        SELECT
            date,
            course,
            off,
            COUNT(*) AS source_rows,
            MIN(ran) AS recorded_ran
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
        GROUP BY
            date,
            course,
            off
    ),
    duplicate_positions AS (
        SELECT
            date,
            course,
            off,
            CAST(pos AS INTEGER) AS numeric_pos,
            COUNT(*) AS runners_at_position,
            COUNT(
                DISTINCT CAST(ovr_btn AS TEXT)
            ) AS distinct_ovr_btn_values
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
          AND typeof(pos) = 'integer'
          AND CAST(pos AS INTEGER) > 0
        GROUP BY
            date,
            course,
            off,
            CAST(pos AS INTEGER)
        HAVING COUNT(*) > 1
    )
    SELECT
        d.rowid AS source_rowid,

        CASE
            WHEN typeof(d.pos) = 'integer'
             AND CAST(d.pos AS INTEGER) = 0
            THEN 1 ELSE 0
        END AS unresolved_zero_position_flag,
…
```

### Cell 43

Matched: `external`, `verified`

```text
# Recalculate the refined result summary directly from the complete source.
#
# The previous race-position group count incorrectly joined to
# affected_races_profile, which contains only the small anomaly-race subset.
# This version counts supported dead-heat groups from the full source query.
#
# Ordinary supported dead heats remain separate from validation issues.

refined_result_flag_summary = pd.read_sql_query(
    f"""
    WITH race_counts AS (
        SELECT
            date,
            course,
            off,
            COUNT(*) AS source_rows,
            MIN(ran) AS recorded_ran
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
        GROUP BY
            date,
            course,
            off
    ),
    duplicate_positions AS (
        SELECT
            date,
            course,
            off,
            CAST(pos AS INTEGER) AS numeric_pos,
            COUNT(*) AS runners_at_position,
            COUNT(
                DISTINCT CAST(ovr_btn AS TEXT)
            ) AS distinct_ovr_btn_values
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
          AND typeof(pos) = 'integer'
          AND CAST(pos AS INTEGER) > 0
        GROUP BY
            date,
            course,
            off,
            CAST(pos AS INTEGER)
        HAVING COUNT(*) > 1
    ),
    row_flags AS (
        SELECT
            d.rowid AS source_rowid,
            d.date,
            d.course,
            d.off,

            CASE
                WHEN duplicates.runners_at_position > 1
                 AND duplicates.distinct_ovr_btn_values = 1
                THEN 1 ELSE 0
            END AS candidate_dead_heat_flag,

            CASE
                WHEN duplicates.runners_at_position > 1
                 AND duplicates.distinct_ovr_btn_values > 1
…
```

### Cell 44

Matched: `external`, `verified`

```text
# Assemble a notebook-level candidate runner-result view from the validated
# source conventions and anomaly checks.
#
# This is deliberately not a final target schema. It demonstrates which
# candidate attributes can be derived reproducibly while retaining:
# - exact raw result fields;
# - source row lineage;
# - supported dead-heat evidence;
# - unresolved and contradictory source patterns.
#
# Candidate attributes:
# - numeric finishing position, where raw pos is a positive integer;
# - raw textual outcome code and validated semantic mapping;
# - broad result representation;
# - candidate dead-heat flag;
# - distance availability;
# - separate validation flags.
#
# No raw source value is corrected or overwritten.

candidate_runner_results = pd.read_sql_query(
    f"""
    WITH race_counts AS (
        SELECT
            date,
            course,
            off,
            COUNT(*) AS source_rows,
            MIN(ran) AS recorded_ran
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
        GROUP BY
            date,
            course,
            off
    ),
    duplicate_positions AS (
        SELECT
            date,
            course,
            off,
            CAST(pos AS INTEGER) AS numeric_pos,
            COUNT(*) AS runners_at_position,
            COUNT(
                DISTINCT CAST(ovr_btn AS TEXT)
            ) AS distinct_ovr_btn_values
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
          AND typeof(pos) = 'integer'
          AND CAST(pos AS INTEGER) > 0
        GROUP BY
            date,
            course,
            off,
            CAST(pos AS INTEGER)
        HAVING COUNT(*) > 1
    )
    SELECT
        -- Physical source lineage.
        d.rowid AS source_rowid,

        -- Current provisional race identity.
…
```

### Cell 45

Matched: `external`, `verified`

```text
# Validate the assembled candidate runner-result view against the established
# full-source totals and notebook findings.
#
# These checks confirm:
# - one candidate row exists for every source data row;
# - source_rowid remains unique;
# - the result representations reconcile to the complete source total;
# - candidate dead-heat counts reproduce the validated full-source counts;
# - textual outcome counts reproduce the validated mapping inventory;
# - anomaly and incomplete-race counts remain unchanged.
#
# No source or candidate value is modified.

candidate_result_validation_checks = pd.DataFrame(
    [
        {
            "check": "candidate rows equal source data rows",
            "observed": len(candidate_runner_results),
            "expected": 1_851_285,
        },
        {
            "check": "source_rowid is unique",
            "observed": candidate_runner_results[
                "source_rowid"
            ].nunique(),
            "expected": 1_851_285,
        },
        {
            "check": "unclassified candidate representations",
            "observed": candidate_runner_results[
                "candidate_result_representation"
            ].isna().sum(),
            "expected": 0,
        },
        {
            "check": "positive numeric finishing-position rows",
            "observed": candidate_runner_results[
                "candidate_finish_position"
            ].notna().sum(),
            "expected": 1_756_666,
        },
        {
            "check": "candidate dead-heat runner records",
            "observed": candidate_runner_results[
                "candidate_dead_heat_flag"
            ].sum(),
            "expected": 6_020,
        },
        {
            "check": "textual outcome rows including DSQ",
            "observed": can
…
```

### Cell 46

Matched: `external`, `verified`

```text
# Record the bounded result-attribute decisions supported by Notebook 05.
#
# This is not a final schema specification. It distinguishes:
# - exact raw source attributes that must be preserved;
# - candidate attributes that can be derived reproducibly;
# - validation flags that must remain separate from the result itself;
# - unresolved concepts that must not be normalised automatically.
#
# Each recommendation is grounded in the complete-source profiling and
# reconciliation checks completed above.

result_attribute_decision_register = pd.DataFrame(
    [
        {
            "attribute_area": "Source lineage",
            "attribute": "source_rowid",
            "status": "preserve",
            "reason": (
                "Provides immutable physical lineage to the exact SQLite "
                "source runner record."
            ),
        },
        {
            "attribute_area": "Raw race context",
            "attribute": "raw_ran",
            "status": "preserve",
            "reason": (
                "Matches source-row count in 189,038 of 189,043 races but must "
                "remain independent because five extracts contain fewer rows "
                "than the recorded field size."
            ),
        },
        {
            "attribute_area": "Raw result",
            "attribute": "raw_pos",
            "status": "preserve",
            "reason": (
                "Carries positive numeric positions, numeric zero, and 11 "
                "validated textual outcome codes in one source field."
            ),
        },
        {
            "attribute_area": "Raw distance",
            "attribute": "raw_btn",
            "status": "preserve",
            "reason": (
                "Usually represents an incremental beaten distance but is not "
…
```

### Cell 47

Matched: `external`, `verified`, `official result`

```text
## Conclusion

### Main conclusion

The source result fields can be represented reliably without replacing or normalising the raw values.

A later staging layer can derive a structured result representation from `pos`, while preserving `ran`, `pos`, `btn`, and `ovr_btn` exactly as supplied.

### Supporting evidence

All 1,851,285 source runner records can be classified into one of four candidate representations:

- 1,756,666 positive numeric finishing positions;
- 93,992 mapped textual outcomes;
- 619 disqualified runners;
- 8 unresolved zero-position records.

The 11 textual `pos` codes are stable source conventions validated through the runner comments:

- `BD` — brought down;
- `CO` — carried out;
- `DSQ` — disqualified;
- `F` — fell;
- `LFT` — left or failed to take part;
- `PU` — pulled up;
- `REF` — refused at an obstacle;
- `RO` — ran out;
- `RR` — refused to race;
- `SU` — slipped up;
- `UR` — unseated rider.

Duplicate positive numeric positions normally represent dead heats. There are 3,006 supported duplicated race-position groups covering 6,020 runner records. These groups share the same cumulative beaten-distance value and generally follow the expected skipped-rank sequence.

`DSQ` must remain separate from ordinary non-finish outcomes. All 619 disqualified runners retain numeric `btn` and `ovr_btn` values, often preserving the on-course finish before the official result was amended.

The beaten-distance fields cannot be treated as a universally additive or position-consistent sequence. Small arithmetic differences are widespread, while amended results can leave `ovr_btn` anchored to the original on-course order rather than the final official `pos`.

### Source anomalies and unresolved cases

The source contains a small bounded set of result anomalies:

- 8
…
```

## `notebooks/06_race_distance_parsing.ipynb`

### Cell 31

Matched: `manual`, `manually`, `external`

```text
## Additional validation required: international distance conversion

### Issue identified

The source expresses every observed `dist` value in miles-and-furlongs notation, including races from jurisdictions that commonly publish scheduled distances in metres.

Therefore, converting the source value to metres does not necessarily recover the original official metric distance exactly.

For example, a race officially scheduled over 1,600 metres could potentially appear as `1m` in the source. Direct conversion of one mile produces 1,609.344 metres, which would overstate the official scheduled distance by 9.344 metres.

### Revised question

Before accepting derived metres as an analytical race distance, determine:

> Do the source’s miles-and-furlongs values preserve international scheduled distances exactly, or are metric races rounded into approximate imperial categories?

### Method

The study will not manually verify every race individually.

Instead it will:

1. isolate jurisdictions that commonly use metric scheduled distances;
2. profile the imperial values used for those races;
3. calculate the implied metre values;
4. look for repeated mappings consistent with standard metric distances such as 1,000m, 1,200m, 1,400m, 1,600m, 2,000m and 2,400m;
5. externally verify representative races and any ambiguous mappings;
6. classify derived metres as exact, approximate or unresolved according to the evidence.

### Consequence

Until this validation is complete:

- raw `dist` remains valid source evidence;
- exact integer yards represent the source expression reproducibly;
- derived metres must not yet be described as the original official scheduled distance;
- the distance investigation is not closed.
```

### Cell 33

Matched: `external`, `checked against`

```text
# Select a small, reproducible verification sample from major metric jurisdictions
# and common source distance values.
#
# One race is selected for each jurisdiction-and-distance combination so that
# the race can be checked against an authoritative external result source.
# This is targeted validation, not an attempt to research all 37,472 races.

VERIFICATION_JURISDICTIONS = {
    "(FR)",
    "(HK)",
    "(AUS)",
    "(UAE)",
    "(JPN)",
    "(GER)",
}

VERIFICATION_RAW_DISTANCES = {
    "5f",
    "6f",
    "7f",
    "1m",
    "1m2f",
    "1m4f",
}

verification_candidates_df = pd.read_sql_query(
    f"""
    WITH provisional_races AS (
        SELECT
            date,
            course,
            off,
            MIN(race_name) AS race_name,
            MIN(type) AS race_type,
            MIN(dist) AS raw_dist,
            MIN(race_id) AS source_race_id,
            COUNT(*) AS runner_records
        FROM {SOURCE_TABLE}
        WHERE {DATA_ROW_PREDICATE}
        GROUP BY date, course, off
    )
    SELECT *
    FROM provisional_races
    """,
    connection,
)

verification_candidates_df["terminal_course_suffix"] = (
    verification_candidates_df["course"]
    .str.extract(r"(\([^()]+\))\s*$", expand=False)
    .fillna("<NO_SUFFIX>")
)

verification_sample_df = (
    verification_candidates_df.loc[
        verification_candidates_df["terminal_course_suffix"].isin(
            VERIFICATION_JURISDICTIONS
        )
        & verification_candidates_df["raw_dist"].isin(
            VERIFICATION_RAW_DISTANCES
        )
    ]
    .sort_values(
        [
            "terminal_course_suffix",
            "raw_dist",
            "date",
            "course",
            "off",
        ]
    )
    .groupby(
        ["terminal_course_suffix", "raw_dist"],
        as_index
…
```

### Cell 34

Matched: `external`, `verified`

```text
## External verification: metric races were approximated

### Observation

Authoritative race records confirm that at least some international metric races were represented approximately in the source `dist` field.

Verified examples:

| Date | Course | Race | Source `dist` | Official distance | Literal source conversion |
|---|---|---|---:|---:|---:|
| 2015-01-25 | Sha Tin (HK) | Stewards' Cup | `1m` | 1,600m | 1,609.344m |
| 2015-01-04 | Kyoto (JPN) | Sports Nippon Sho Kyoto Kimpai | `1m` | 1,600m | 1,609.344m |

Official sources:

- Hong Kong Jockey Club, *The Stewards' Cup — 1600 Metres — Sha Tin — Sunday 25 January 2015*
- Japan Racing Association, *2015 Kyoto Kimpai — course 1,600 metres*

### Interpretation

For these verified races, the source `dist` value is not an exact preservation of the official scheduled distance.

Instead, the official 1,600-metre distance has been represented as the nearby imperial category `1m`.

Consequently:

- `1m` remains an exact representation of what this source recorded;
- `1,760` yards is an exact conversion of that source expression;
- `1,609.344` metres is only the literal SI conversion of the source expression;
- it must not be presented as the verified official scheduled distance.

The evidence supports upstream standardisation or approximation, but does not yet identify whether it was performed by the original racing-data provider, an intermediate website or the dataset creator.

### Revised database consequence

Preserve a clear distinction between:

1. **raw source distance** — exact `dist` text;
2. **source-implied yards/metres** — deterministic conversion of that text;
3. **official scheduled distance** — separate enrichment requiring authoritative evidence.

Do not label the source-implied metre value simply as `dista
…
```

### Cell 35

Matched: `verified`

```text
## Scope decision for initial database use

### Decision

The initial analytical database will prioritise UK and Irish racing.

For those races, the source `dist` field can be retained and converted into source-implied yards and metres for early analytical work, subject to the normal preservation of the raw value.

International races will not be discarded. They will remain available with:

- exact raw `dist`;
- source-implied yards;
- source-implied metres;
- an explicit indication that the official scheduled distance has not yet been independently verified.

### Deferred enrichment

Exact official distances for metric jurisdictions will be treated as a separate enrichment workstream.

That enrichment may later use:

- other supplied source products;
- official racing-authority results;
- a suitably licensed international results source;
- race-level matching by date, course, off time and race name.

### Practical consequence

Unresolved international distance provenance does not need to delay construction or early use of the database.

Analyses requiring exact official distance should initially be limited to jurisdictions where the source representation is sufficiently trusted, or should explicitly use the source-implied distance rather than claim an official measurement.
```

### Cell 36

Matched: `verified`

```text
# Rename the derived metric field so it does not imply an independently verified
# official scheduled distance.
#
# The module will now return:
# - source_implied_yards
# - source_implied_metres
#
# These are exact conversions of the raw source expression, not necessarily the
# original official distance for international metric races.

module_path = PROJECT_ROOT / "src" / "inside_rails" / "race_distance.py"
module_text = module_path.read_text(encoding="utf-8")

module_text = module_text.replace(
    '"total_yards": None,\n        "distance_metres": None,',
    '"source_implied_yards": None,\n        "source_implied_metres": None,',
)

module_text = module_text.replace(
    '"total_yards": total_yards,\n            "distance_metres": total_yards * 0.9144,',
    '"source_implied_yards": total_yards,\n'
    '            "source_implied_metres": total_yards * 0.9144,',
)

module_path.write_text(module_text, encoding="utf-8")

# Reload and inspect one known value.
race_distance = importlib.reload(race_distance)

print(f"Updated: {module_path}")
print(race_distance.parse_race_distance("1m"))

Updated: /home/rob/Documents/inside-rails-horse-racing/src/inside_rails/race_distance.py
{'raw_dist': '1m', 'miles': 1, 'whole_furlongs': 0, 'has_half_furlong': False, 'total_furlongs': 8.0, 'source_implied_yards': 1760, 'source_implied_metres': 1609.344, 'parse_status': 'parsed'}
```

### Cell 37

Matched: `verified`

```text
# Rewrite the reusable distance module with explicit warnings that derived
# yards and metres describe the source expression, not necessarily the
# independently verified official scheduled distance.

from pathlib import Path
from pprint import pformat

module_path = PROJECT_ROOT / "src" / "inside_rails" / "race_distance.py"

validated_components = {
    raw_dist: (
        int(parsed["miles"]),
        int(parsed["whole_furlongs"]),
        bool(parsed["has_half_furlong"]),
    )
    for raw_dist, parsed in validated_distance_lookup.items()
}

module_content = f'''"""Validated scheduled race-distance parsing.

The exact raw source value is preserved.

Derived yards and metres are literal conversions of the source expression
only. They are not guaranteed to equal the original official scheduled
distance for jurisdictions that publish races metrically, because an upstream
provider may have rounded or standardised those distances into
miles-and-furlongs notation.

Only exact raw values observed and validated in Notebook 06 are converted.
Previously unseen values remain unresolved.
"""

from __future__ import annotations

from typing import Any

# Exact raw values validated in Notebook 06.
# Tuple structure: miles, whole furlongs, half-furlong indicator.
VALIDATED_COMPONENTS: dict[str, tuple[int, int, bool]] = {
    pformat(validated_components, sort_dicts=True, width=88)
}

def parse_race_distance(raw_dist: Any) -> dict[str, Any]:
    """Parse one exact validated source race-distance value.

    ``source_implied_yards`` and ``source_implied_metres`` describe the literal
    source expression. They must not be treated as independently verified
    official race distances.
    """
    result: dict[str, Any] = {{
        "raw_dist": raw_dist,
        "miles": None,
        "
…
```

### Cell 38

Matched: `verified`

```text
# Update the independent validation script to match the clarified field names
# and confirm that source-implied distances are never presented as verified
# official distances.

validation_script_path = (
    PROJECT_ROOT / "scripts" / "validate_race_distance.py"
)

validation_script_content = '''"""Validate scheduled race-distance parsing against the source database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.race_distance import parse_race_distance

DATA_ROW_PREDICATE = "rowid <> 1"

def main() -> None:
    database_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "form_2015-present"
        / "form_2015-present"
        / "raceform.db"
    )

    if not database_path.exists():
        raise FileNotFoundError(f"Source database not found: {database_path}")

    connection = sqlite3.connect(
        f"file:{database_path}?mode=ro",
        uri=True,
    )

    try:
        provisional_races = pd.read_sql_query(
            f"""
            SELECT
                date,
                course,
                off,
                MIN(dist) AS raw_dist,
                COUNT(DISTINCT dist) AS distinct_distance_values
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY date, course, off
            """,
            connection,
        )
    finally:
        connection.close()

    results = pd.DataFrame(
        parse_race_distance(raw_dist)
        for raw_dist in provisional_races["raw_dist"]
    )

    assert len(provisional_races) == 189_043
    assert provisional_races["distin
…
```

### Cell 39

Matched: `verified`

```text
# Run the updated independent validation script.

validation_result = subprocess.run(
    [
        str(PROJECT_ROOT / ".venv" / "bin" / "python"),
        str(PROJECT_ROOT / "scripts" / "validate_race_distance.py"),
    ],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True,
)

print(validation_result.stdout)

if validation_result.stderr:
    print(validation_result.stderr)

assert validation_result.returncode == 0, (
    f"Validation script failed with exit code "
    f"{validation_result.returncode}"
)

Race-distance validation passed.
Provisional races checked: 189,043
Distinct raw values: 63
Parsed races: 189,043
Unresolved races: 0
Official-distance verified rows: 0
```

### Cell 40

Matched: `external`, `verified`

```text
# Conclusion

## Answer

The source `dist` field is complete, internally consistent and reproducibly parseable for the current extract.

All 189,043 provisional races use one of 63 validated miles-and-furlongs expressions. These values can be converted exactly into source-implied yards and deterministically into source-implied metres.

However, those conversions represent what the source expressed. They do not necessarily reproduce the original official scheduled distance for international races from jurisdictions that commonly publish distances metrically.

## Evidence

- 1,851,285 runner records contain a non-blank text `dist` value.
- Every provisional race contains one consistent raw distance.
- There are 63 distinct raw distance values.
- All 63 values parse successfully.
- All 189,043 provisional races receive source-implied yards and metres.
- Zero current-source races remain unresolved.
- The standalone validation script passes across the complete race population.
- All returned records explicitly have `official_distance_verified = False`.
- External checks found metric races officially scheduled over 1,600 metres represented by the source as `1m`.

## Interpretation

The raw `dist` value is reliable evidence of the source representation.

`source_implied_yards` is an exact conversion of that representation.

`source_implied_metres` is a literal SI conversion of the source representation, but it must not be described as the independently verified official distance.

For UK and Irish racing, the source representation is suitable for initial analytical work, while retaining the raw value and the same provenance warning.

International official distances require a separate enrichment process where exact jurisdiction-native distances are analytically important.

##
…
```

## `notebooks/07_carried_weight_parsing.ipynb`

### Cell 0

Matched: `verified`

```text
# Carried Weight Parsing

## Bounded question

> How is carried weight represented in the source, and which values can be parsed reproducibly?

## Source and grain

This notebook examines the `wgt` field in the read-only SQLite source:

- **Database:** `data/raw/form_2015-present/form_2015-present/raceform.db`
- **Table:** `data`
- **Runner-record grain:** one physical source row per runner record
- **Physical source lineage:** preserve the original SQLite `rowid`
- **Data-row predicate:** `rowid <> 1`

The source contains 1,851,285 data-like runner records after excluding the imported header row at `rowid = 1`.

## Evidence-first method

The analysis will proceed from observed source values rather than assumed racing conventions. It will:

1. profile SQLite storage classes, missing values, sentinels and distinct raw values;
2. identify notation families and recurring structural patterns;
3. test candidate parsing rules against every observed value;
4. examine anomalies and ambiguous values in their runner, race and jurisdiction context;
5. distinguish exact source evidence from derived quantities;
6. preserve values that cannot be interpreted safely as unresolved rather than guessing;
7. define failure-detecting validation for both current and unseen future values.

Observations, interpretations and design consequences will be recorded separately.

## Explicit exclusions

This notebook will not:

- reopen race-distance analysis;
- alter or overwrite the raw `wgt` field;
- assume that every value uses British stones-and-pounds notation;
- infer undocumented allowances or corrections from weight alone;
- treat derived kilograms as independently verified official metric weights;
- design the final staging or target database schema;
- silently accept unfamiliar future nota
…
```

### Cell 17

Matched: `verified`

```text
# Define a conservative carried-weight parser.
#
# Current accepted notation:
#     <stones>-<pounds>
#
# Validation rules:
# - the raw value must be a Python string;
# - it must use canonical integer-hyphen-integer notation;
# - neither component may contain leading zeros;
# - the pounds component must be between 0 and 13;
# - unfamiliar or malformed future values remain unresolved;
# - kilograms are labelled as source-implied conversions only.

from dataclasses import asdict, dataclass
from typing import Optional

POUND_TO_KILOGRAM = 0.45359237
CARRIED_WEIGHT_PATTERN = re.compile(r"^(0|[1-9]\d*)-(0|[1-9]\d*)$")

@dataclass(frozen=True)
class CarriedWeightParse:
    raw_wgt: object
    notation_family: str
    parsed_stones: Optional[int]
    parsed_pounds: Optional[int]
    source_implied_total_pounds: Optional[int]
    source_implied_kilograms: Optional[float]
    parse_status: str
    ambiguity_flag: bool
    anomaly_flags: tuple[str, ...]
    official_weight_verified: bool

def parse_carried_weight(raw_wgt: object) -> CarriedWeightParse:
    """Parse only canonical stones-and-pounds source notation."""

    if raw_wgt is None:
        return CarriedWeightParse(
            raw_wgt=raw_wgt,
            notation_family="missing",
            parsed_stones=None,
            parsed_pounds=None,
            source_implied_total_pounds=None,
            source_implied_kilograms=None,
            parse_status="unresolved_missing",
            ambiguity_flag=False,
            anomaly_flags=("missing_value",),
            official_weight_verified=False,
        )

    if not isinstance(raw_wgt, str):
        return CarriedWeightParse(
            raw_wgt=raw_wgt,
            notation_family="non_text",
            parsed_stones=None,
            parsed_pounds=None,
…
```

### Cell 20

Matched: `verified`

```text
## Complete-source validation result

### Observation

The conservative carried-weight parser reconciles completely against the current source:

- **Data-like runner records:** 1,851,285
- **Distinct raw `wgt` values:** 79
- **Distinct values parsed:** 79
- **Runner records parsed:** 1,851,285
- **Unresolved current values:** 0
- **Component mismatches against independent SQL parsing:** 0
- **Total-pound mismatches against independent SQL calculation:** 0

All current values use canonical integer-hyphen-integer notation. The left component ranges from 6 to 12 and the right component ranges from 0 to 13.

### Interpretation

The current `wgt` field can be parsed reproducibly as stones and pounds:

\[
\text{source-implied total pounds}
=
(\text{stones} \times 14) + \text{pounds}
\]

The evidence supporting this interpretation is:

- every current record uses the same notation structure;
- the second component never exceeds 13;
- all raw values are canonical and map one-to-one to total pounds;
- resulting ranges are coherent with Flat, Hurdle, Chase and NH Flat contexts;
- unusual extreme values remain internally coherent within their races;
- clearly metric international jurisdictions still use the same imperial notation.

### Provenance limitation

The raw source does not preserve native metric notation for jurisdictions that ordinarily publish carried weight in kilograms.

A literal conversion may therefore be derived as:

\[
\text{source-implied kilograms}
=
\text{source-implied total pounds} \times 0.45359237
\]

However, this value is only the SI equivalent of the stored source expression. It must not be presented as a recovered or independently verified official metric carried weight.

For example, a stored value of `9-0` implies exactly 126 pounds and approximately
…
```

### Cell 21

Matched: `verified`

```text
## Notebook conclusion

### Defensible parsing rule

The source `wgt` field is consistently represented as canonical stones-and-pounds text:

    <stones>-<pounds>

A value is deterministically parseable when:

- it is stored as text;
- it contains exactly two unsigned integer components separated by one hyphen;
- neither component uses leading zeros;
- the pounds component is between `0` and `13`.

Derived values are:

    source_implied_total_pounds = (parsed_stones × 14) + parsed_pounds
    source_implied_kilograms = source_implied_total_pounds × 0.45359237

### Current-source result

Across all 1,851,285 data-like runner records:

- all values are SQLite text;
- there are no SQL `NULL` or blank values;
- there are 79 distinct raw values;
- all 79 values use canonical stones-and-pounds notation;
- all 1,851,285 runner records parse successfully;
- no current values remain unresolved;
- independent Python and SQLite calculations agree for every observed value.

The observed range is:

    6-12 to 12-11
    96 to 179 source-implied pounds
    43.544868 to 81.193034 source-implied kilograms

### Known exceptions and contextual anomalies

No malformed, fractional, pounds-only or metric notation occurs in the current source.

Some unusual weights and race-level spreads occur, but inspection shows that the weight strings themselves remain structurally valid and internally coherent. Contextual anomalies in fields such as race type must therefore remain separate from weight parse validity.

### International provenance limitation

The source uses stones-and-pounds notation even for jurisdictions that ordinarily publish carried weight in kilograms.

Consequently:

- raw `wgt` is exact source evidence;
- total pounds are the exact interpretation of the stored expression;
- kil
…
```

## `notebooks/08_starting_price_parsing.ipynb`

### Cell 0

Matched: `verified`

```text
# 08 — Starting-Price Parsing

## Bounded question

> How is starting price represented in the source, and which values can be parsed reproducibly?

## Source and grain

This notebook studies the starting-price field in the immutable source database:

- **Database:** `data/raw/form_2015-present/form_2015-present/raceform.db`
- **Table:** `data`
- **Runner-record grain:** one physical source row per runner record
- **Data-row predicate:** `rowid <> 1`
- **Physical source lineage:** preserve the original SQLite `rowid`

The exact starting-price column name will be confirmed from the existing source-field profile before any source query assumes it.

## Evidence-first method

The analysis will proceed from the stored values themselves:

1. confirm the exact source column and SQLite storage classes;
2. identify SQL `NULL`, blank, sentinel and other missing-value conventions;
3. profile distinct raw values and runner-record frequencies;
4. classify observed notation families and annotations;
5. test deterministic parsing rules against every distinct current value;
6. inspect ambiguous, malformed, unusual and jurisdiction-specific cases in context;
7. distinguish exact source evidence from derived analytical values;
8. define failure-detecting validation for both supported and deliberately unsupported inputs.

Observations, interpretation and design decisions will remain separate.

## Explicit exclusions

This notebook will not:

- reopen race-distance or carried-weight analysis;
- infer prices that are not present in the source;
- silently repair malformed or ambiguous values;
- assume that every price is fractional before profiling the field;
- treat candidate decimal odds or implied probabilities as independent official evidence;
- design the final staging or target databas
…
```

### Cell 26

Matched: `external`

```text
# Select a compact external-validation sample spanning the important observed
# notation families. We will look these races up individually before deciding
# what the stored fractions represent upstream.
#
# The sample includes:
# - ordinary British fractional prices;
# - odds-on and even-money prices;
# - favourite, joint-favourite and co-favourite markers;
# - unreduced fractions;
# - precision-heavy international fractions;
# - extreme long prices;
# - the standalone favourite marker already inspected.

external_validation_targets = [
    "Evs",
    "EvensF",
    "EvsJ",
    "6/4F",
    "100/30J",
    "4/1C",
    "30/100F",
    "34/100F",
    "145/20",
    "52/10",
    "885/100",
    "181/10",
    "1000/1",
    "F",
]

placeholders = ", ".join("?" for _ in external_validation_targets)

with sqlite3.connect(READ_ONLY_DB_URI, uri=True) as connection:
    external_validation_sample = pd.read_sql_query(
        f"""
        WITH ranked AS (
            SELECT
                rowid AS source_rowid,
                date,
                course,
                off,
                race_name,
                type,
                ran,
                num,
                pos,
                horse,
                sp,
                ROW_NUMBER() OVER (
                    PARTITION BY sp
                    ORDER BY date, course, off, rowid
                ) AS occurrence_number
            FROM {SOURCE_TABLE}
            WHERE {DATA_ROW_PREDICATE}
              AND sp IN ({placeholders})
        )
        SELECT
            source_rowid,
            date,
            course,
            off,
            race_name,
            type,
            ran,
            num,
            pos,
            horse,
            sp
        FROM ranked
        WHERE occurrence_number = 1
…
```

### Cell 27

Matched: `external`, `checked against`, `verified`, `racing post`

```text
## External validation of the stratified starting-price sample

A stratified sample of 13 runner records was checked against independent or
jurisdiction-relevant public sources where retrievable.

| Raw `sp` | Runner and race | External finding | Assessment |
|---|---|---|---|
| `Evs` | More Than A Party — 2015 Hurricane Bertie Stakes, Gulfstream Park | No sufficiently clear independent archived price located | Not independently verified |
| `EvensF` | Ptit Zig — 2015 Dipper Novices' Chase, Cheltenham | Contemporary reporting describes Ptit Zig as the **evens favourite** | Exact agreement |
| `EvsJ` | Russian Bolero — 2015 JCB Novices' Hurdle, Warwick | No sufficiently clear independent archived price located | Not independently verified |
| `6/4F` | Major Rowan — 2015 Southwell handicap | No sufficiently clear independent archived price located | Not independently verified |
| `100/30J` | White Arm — 2015 Dunsany Handicap Chase, Navan | No sufficiently clear independent archived price located | Not independently verified |
| `4/1C` | Really Unique — 2015 Thurles Handicap Hurdle | Independent result sources report **4/1 co-favourite**; one states that Really Unique was one of three 4/1 co-favourites | Exact agreement |
| `30/100F` | Lady Sabelia — 2015 What A Summer Stakes, Laurel Park | Contemporary reports describe Lady Sabelia as **3/10 favourite** or **1/5 favourite**, depending on the reporting source | Arithmetic agreement with 3/10; evidence of variation between quoted pre-race or returned prices |
| `34/100F` | Close Your Eyes — 2019 Premio EBF Terme di Merano | No sufficiently clear jurisdiction-native archived returned price located | Not independently verified |
| `145/20` | Presley — 2018 Premio Federico Tesio, San Siro | No sufficiently clear archived retur
…
```

### Cell 28

Matched: `external`, `verified`

```text
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StartingPriceParse:
    raw_sp: object
    notation_family: str
    numerator: Optional[int]
    denominator: Optional[int]
    favourite_marker: Optional[str]
    parse_status: str
    anomaly_flags: tuple[str, ...]

def parse_starting_price(raw_sp: object) -> StartingPriceParse:
    """
    Parse only information explicitly encoded in the source `sp` value.

    External corrections, including the verified 5/2 price for the standalone
    `F` record, are deliberately excluded from this source-string parser.
    """
    if raw_sp is None:
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="missing",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="unresolved",
            anomaly_flags=("sql_null",),
        )

    if not isinstance(raw_sp, str):
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="unfamiliar",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="unresolved",
            anomaly_flags=("non_text_value",),
        )

    if raw_sp == "":
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="missing",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="missing",
            anomaly_flags=(),
        )

    if raw_sp != raw_sp.strip():
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="unfamiliar",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status
…
```

### Cell 32

Matched: `external`

```text
# Tighten the parser so favourite markers are returned only for fully supported
# structures. Unsupported strings such as `5/2JF` must remain wholly unresolved.

def parse_starting_price(raw_sp: object) -> StartingPriceParse:
    """
    Parse only information explicitly encoded in the source `sp` value.

    External corrections and enrichments are deliberately excluded from this
    source-string parser.
    """
    if raw_sp is None:
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="missing",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="unresolved",
            anomaly_flags=("sql_null",),
        )

    if not isinstance(raw_sp, str):
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="unfamiliar",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="unresolved",
            anomaly_flags=("non_text_value",),
        )

    if raw_sp == "":
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="missing",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="missing",
            anomaly_flags=(),
        )

    if raw_sp != raw_sp.strip():
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="unfamiliar",
            numerator=None,
            denominator=None,
            favourite_marker=None,
            parse_status="unresolved",
            anomaly_flags=("outer_whitespace",),
        )

    if raw_sp == "F":
        return StartingPriceParse(
            raw_sp=raw_sp,
            notation_family="favourite_
…
```

### Cell 34

Matched: `external`

```text
# Profile empty starting-price values in race and runner context before deciding
# which records require individual external investigation.
with sqlite3.connect(READ_ONLY_DB_URI, uri=True) as connection:
    missing_sp_profile = pd.read_sql_query(
        f"""
        WITH race_context AS (
            SELECT
                date,
                course,
                off,
                COUNT(*) AS source_runner_records,
                MAX(ran) AS declared_ran,
                SUM(CASE WHEN sp = '' THEN 1 ELSE 0 END) AS blank_sp_rows,
                COUNT(DISTINCT CASE WHEN sp <> '' THEN sp END) AS nonblank_sp_values
            FROM {SOURCE_TABLE}
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY
                date,
                course,
                off
        )
        SELECT
            CASE
                WHEN r.blank_sp_rows = r.source_runner_records
                    THEN 'all_runners_blank'
                WHEN r.blank_sp_rows > 0
                    THEN 'some_runners_blank'
                ELSE 'no_blank_sp'
            END AS race_blank_pattern,
            COUNT(DISTINCT d.date || '|' || d.course || '|' || d.off)
                AS provisional_races,
            COUNT(*) AS blank_runner_records,
            SUM(CASE WHEN d.pos = '' THEN 1 ELSE 0 END) AS blank_pos_rows,
            SUM(CASE WHEN d.pos = '0' THEN 1 ELSE 0 END) AS zero_pos_rows,
            SUM(CASE WHEN d.pos = 'DSQ' THEN 1 ELSE 0 END) AS dsq_rows,
            SUM(
                CASE
                    WHEN d.pos IN (
                        'BD', 'CO', 'F', 'LFT', 'PU',
                        'REF', 'RO', 'RR', 'SU', 'UR'
                    )
                    THEN 1 ELSE 0
                END
            ) AS nonfinish_rows,
            SUM(
…
```

### Cell 38

Matched: `external`

```text
# Summarise which finishing positions received prices in each sampled
# partial-blank race before checking the races externally.

partial_blank_position_summary = (
    partial_blank_runner_context
    .assign(
        has_price=lambda frame: frame["sp"].ne(""),
        numeric_position=lambda frame: pd.to_numeric(
            frame["pos"],
            errors="coerce",
        ),
    )
    .groupby(
        ["date", "course", "off", "race_name"],
        as_index=False,
    )
    .agg(
        runner_records=("source_rowid", "count"),
        priced_runner_records=("has_price", "sum"),
        blank_runner_records=("has_price", lambda values: (~values).sum()),
        best_position_with_price=(
            "numeric_position",
            lambda values: values[
                partial_blank_runner_context.loc[values.index, "sp"].ne("")
            ].min(),
        ),
        worst_position_with_price=(
            "numeric_position",
            lambda values: values[
                partial_blank_runner_context.loc[values.index, "sp"].ne("")
            ].max(),
        ),
        priced_positions=(
            "numeric_position",
            lambda values: ", ".join(
                str(int(position))
                for position in sorted(
                    values[
                        partial_blank_runner_context.loc[values.index, "sp"].ne("")
                    ].dropna()
                )
            ),
        ),
        priced_raw_values=(
            "sp",
            lambda values: ", ".join(
                value for value in values if value != ""
            ),
        ),
    )
)

partial_blank_position_summary
         date            course    off  \
0  2015-12-12  San Isidro (ARG)   9:15   
1  2016-09-04  Monterrico (PER)  11:20   
2  2019-10-13   Pa
…
```

### Cell 39

Matched: `external`

```text
# Classify every partial-blank race by which finishing positions contain prices.
#
# This tests whether nonblank values systematically belong to:
# - the winner only;
# - a contiguous leading group such as positions 1–5;
# - non-contiguous finishers;
# - runners with non-numeric outcomes.
#
# External evidence from the sampled Deauville race shows that a winner-only
# value may be a converted tote win dividend rather than an ordinary SP.

with sqlite3.connect(READ_ONLY_DB_URI, uri=True) as connection:
    partial_blank_position_patterns = pd.read_sql_query(
        f"""
        WITH partial_blank_races AS (
            SELECT
                date,
                course,
                off
            FROM {SOURCE_TABLE}
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY
                date,
                course,
                off
            HAVING
                SUM(CASE WHEN sp = '' THEN 1 ELSE 0 END) > 0
                AND SUM(CASE WHEN sp <> '' THEN 1 ELSE 0 END) > 0
        ),
        priced_positions AS (
            SELECT
                d.date,
                d.course,
                d.off,
                COUNT(*) AS source_runner_records,
                SUM(CASE WHEN d.sp <> '' THEN 1 ELSE 0 END) AS priced_runners,
                MIN(
                    CASE
                        WHEN d.sp <> ''
                         AND CAST(d.pos AS TEXT) GLOB '[1-9]*'
                        THEN CAST(d.pos AS INTEGER)
                    END
                ) AS minimum_priced_position,
                MAX(
                    CASE
                        WHEN d.sp <> ''
                         AND CAST(d.pos AS TEXT) GLOB '[1-9]*'
                        THEN CAST(d.pos AS INTEGER)
                    END
                ) AS maximum_priced_p
…
```

### Cell 40

Matched: `manual`, `external`

```text
## Partial starting-price coverage as a retained source behaviour

Among the 194 provisional races containing both blank and nonblank `sp` values,
the placement of nonblank prices is strongly structured.

Observed patterns include:

- 122 races in which only the winner has a nonblank price;
- races in which prices are present for a contiguous group of leading finishers;
- smaller groups with other finishing-position patterns;
- four races in which priced records include a non-numeric finishing outcome.

External inspection of a sampled Deauville winner-only race showed that the
winner's stored fraction corresponded to the published win tote dividend.

This establishes that a blank runner-level `sp` does not always mean an
accidental missing starting price. Depending on the race and jurisdiction, the
field may contain:

- a conventional starting price for every runner;
- a returned win dividend for the winner only;
- returns for a limited set of leading finishers;
- no supplied price or dividend for the race;
- genuinely incomplete or anomalous source coverage.

### Consequence retained for later database design

The eventual database must not collapse all blank `sp` values into one
undifferentiated missing-price category.

It will need to preserve enough race-level context to distinguish, where
supported by evidence:

- complete runner-level price coverage;
- winner-only return coverage;
- leading-finisher return coverage;
- all-runners-blank race-level coverage absence;
- irregular partial coverage;
- unresolved cases requiring manual or external review.

This notebook records the source behaviour and validation evidence only.
The final staging and target-schema implementation remains deferred.
```

### Cell 41

Matched: `external`

```text
# Identify the partial-blank races whose priced runners follow an irregular
# position pattern, including races with priced non-numeric outcomes.
#
# These are the cases most likely to require contextual or external review
# before we can describe their source semantics defensibly.

with sqlite3.connect(READ_ONLY_DB_URI, uri=True) as connection:
    irregular_partial_price_races = pd.read_sql_query(
        f"""
        WITH partial_blank_races AS (
            SELECT
                date,
                course,
                off
            FROM {SOURCE_TABLE}
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY
                date,
                course,
                off
            HAVING
                SUM(CASE WHEN sp = '' THEN 1 ELSE 0 END) > 0
                AND SUM(CASE WHEN sp <> '' THEN 1 ELSE 0 END) > 0
        ),
        race_context AS (
            SELECT
                d.date,
                d.course,
                d.off,
                MAX(d.race_name) AS race_name,
                MAX(d.ran) AS declared_ran,
                COUNT(*) AS source_runner_records,
                SUM(CASE WHEN d.sp <> '' THEN 1 ELSE 0 END) AS priced_runners,
                MIN(
                    CASE
                        WHEN d.sp <> ''
                         AND CAST(d.pos AS TEXT) GLOB '[1-9]*'
                        THEN CAST(d.pos AS INTEGER)
                    END
                ) AS minimum_priced_position,
                MAX(
                    CASE
                        WHEN d.sp <> ''
                         AND CAST(d.pos AS TEXT) GLOB '[1-9]*'
                        THEN CAST(d.pos AS INTEGER)
                    END
                ) AS maximum_priced_position,
                COUNT(
                    DISTINCT CASE
…
```

### Cell 43

Matched: `external`, `verified`

```text
## Externally verified special blank-price case

One irregular partial-coverage race contains a blank `sp` for Modern Games,
winner of the 2021 Breeders' Cup Juvenile Turf at Del Mar.

Modern Games was mistakenly removed from the pari-mutuel wagering pools before
the race. Although subsequently permitted to compete, he ran for purse money
only and was not treated as the winner for wagering purposes.

Therefore:

- the blank `sp` is not an accidental missing value;
- Modern Games completed and won the race;
- no runner-level pari-mutuel return applied to him;
- the second-finishing horse was treated as the wagering winner;
- finishing position alone cannot determine whether a price should exist.

### Retained source consequence

Blank starting-price values may represent at least:

- race-level absence of supplied price data;
- winner-only or leading-finisher tote-return coverage;
- a runner excluded from the wagering pool;
- irregular source omissions requiring further review.

The eventual database must preserve runner-level wagering applicability
separately from finishing position and raw price availability where such
evidence can be established.
```

### Cell 44

Matched: `external`

```text
## Revision to the field interpretation

The source column is named `sp`, but the observed evidence shows that it does not
consist exclusively of conventional runner-level starting prices.

Depending on race and jurisdiction, the field may contain:

- a conventional fixed-odds starting price;
- a fractional representation of a pari-mutuel or tote win dividend;
- returns supplied only for the winner;
- returns supplied for a limited group of leading finishers;
- a favourite-status marker without a numeric source price;
- a blank value because the runner was excluded from wagering;
- a blank value because no race-level price or return was supplied;
- an unexplained source omission.

Therefore, throughout the remainder of this notebook:

- `raw_sp` refers only to the exact stored source value;
- parsed numerator and denominator describe the arithmetic fraction encoded in
  that value;
- no parsed fraction is automatically labelled a conventional starting price;
- no derived value is automatically treated as comparable across races;
- market type and wagering applicability remain separate classification
  questions;
- ambiguous cases remain unresolved until supported by race context or external
  evidence.

The bounded question is consequently refined to:

> How is the source `sp` field represented, which values can be parsed
> reproducibly, and what limits prevent it from being treated globally as a
> conventional starting-price field?
```

### Cell 50

Matched: `external`, `verified`

```text
## Notebook conclusion

### Bounded answer

The source column is named `sp`, but it cannot be interpreted globally as a
conventional runner-level starting-price field.

It is a mixed source price-and-return field whose meaning varies by race,
course, jurisdiction and wagering context.

### Current source representation

Across all 1,851,285 data-like runner records:

- every `sp` value is stored as SQLite text;
- there are 843 distinct raw values;
- 9,097 records contain an empty string;
- there are no SQL `NULL` values;
- there are no whitespace-only values;
- there are no values with outer whitespace.

The current nonblank notation consists of:

- fractional expressions;
- textual even-money expressions:
  - `Evs`;
  - `EvensF`;
  - `EvsJ`;
- terminal favourite markers:
  - `F`;
  - `J`;
  - `C`;
- one standalone `F` value without a numeric component.

No current value uses decimal-odds notation or another unsupported structure.

### Reproducible parsing rule

The current source supports deterministic parsing of:

```text
<numerator>/<denominator>[optional marker]
```

where:

- numerator and denominator are positive integers;
- the optional terminal marker is `F`, `J` or `C`;
- fractions are not required to be in lowest terms.

The textual even-money values map arithmetically to `1/1`, while preserving
their exact raw notation and any favourite marker.

The parser preserves separately:

- exact raw `sp`;
- notation family;
- raw numerator;
- raw denominator;
- favourite marker;
- parse status;
- anomaly flags.

### Parser coverage

The final notebook parser processed all 1,851,285 data-like runner records:

- 1,842,187 records contain a reproducibly parsed numeric fraction;
- 9,097 records contain an explicit empty string;
- one record contains a standalone favourite
…
```

## `notebooks/09_course_jurisdiction_racing_authority_and_betting_market_context.ipynb`

### Cell 0

Matched: `external`, `verified`

```text
# 09 — Course Jurisdiction, Racing Authority and Betting-Market Context

## Purpose

The completed distance, carried-weight and starting-price studies established that the source converts international racing information into superficially consistent British-style text without necessarily preserving its original jurisdictional meaning.

A parsed value may therefore be arithmetically valid while remaining contextually ambiguous:

- a source distance expressed in miles and furlongs may approximate an official metric distance;
- a source weight expressed in stones and pounds may represent a converted official kilogram declaration;
- a fractional value in `sp` may represent a conventional fixed-odds starting price, a fractionalised tote or pari-mutuel return, or another published market measure.

These values must not be compared across jurisdictions under false equivalence.

## Bounded question

> How can each source course or race be assigned a defensible jurisdiction, racing-authority and betting-market context, with explicit evidence and confidence, so that international distance, carried-weight and source price-or-return values are not compared under false equivalence?

## Starting point

Notebook 04 already established a bounded candidate course-mapping method:

- preserve the exact raw `course` value;
- derive candidate jurisdiction from recognised terminal codes, historical suffix links, curated British configurations and bounded collision rules;
- remove only recognised terminal jurisdiction suffixes;
- retain meaningful venue or configuration markers such as `(AW)`, `(July)`, `(RH)` and `(Perth)`;
- combine candidate jurisdiction and candidate course label as the provisional venue/configuration identity.

That work assigned all **189,043** provisional races to a c
…
```

### Cell 4

Matched: `manual`, `manually`

```text
# Extract the settled jurisdiction-mapping definitions from Notebook 04 into
# a reusable module without manually retyping its curated mappings.
#
# This reads Notebook 04, selects the established mapping constants and helper
# functions by name, and writes their original source into:
# src/inside_rails/course_jurisdiction.py

import ast
import json
from pathlib import Path

NOTEBOOK_04_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "04_course_jurisdiction_and_surface_mapping.ipynb"
)

MODULE_PATH = (
    PROJECT_ROOT
    / "src"
    / "inside_rails"
    / "course_jurisdiction.py"
)

TARGET_NAMES = {
    "terminal_code_to_jurisdiction",
    "historical_course_to_code",
    "curated_british_course_configurations",
    "established_unsuffixed_british_courses",
    "extract_terminal_jurisdiction_code",
    "derive_candidate_race_jurisdiction",
}

with NOTEBOOK_04_PATH.open("r", encoding="utf-8") as notebook_file:
    notebook_04 = json.load(notebook_file)

selected_blocks = []

for cell in notebook_04["cells"]:
    if cell.get("cell_type") != "code":
        continue

    source = "".join(cell.get("source", []))

    try:
        tree = ast.parse(source)
    except SyntaxError:
        continue

    lines = source.splitlines(keepends=True)

    for node in tree.body:
        defined_names = set()

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.add(node.name)

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]

            for target in targets:
                if isinstance(target, ast.Name):
                    defined_names.add(target.id)

        if defined_names & TARGET_NAMES:
            selected_blocks.appen
…
```

### Cell 19

Matched: `external`

```text
# Build the first-pass rules-context investigation units.
#
# This does not yet assign a regulator or formal rules framework.
# It only identifies the observed combinations of:
# - candidate jurisdiction;
# - source racing code;
# - active date period;
# - race and course coverage.
#
# These combinations will guide the external authority and rules research.

rules_context_units = (
    candidate_jurisdiction_evidence
    .groupby(
        [
            "candidate_jurisdiction",
            "type",
        ],
        as_index=False,
    )
    .agg(
        provisional_races=("course", "size"),
        candidate_course_identities=("candidate_course_label", "nunique"),
        first_date=("date", "min"),
        last_date=("date", "max"),
    )
    .sort_values(
        [
            "provisional_races",
            "candidate_jurisdiction",
            "type",
        ],
        ascending=[False, True, True],
    )
    .reset_index(drop=True)
)

print(f"Observed jurisdiction-and-code units: {len(rules_context_units):,}")

rules_context_units

Observed jurisdiction-and-code units: 56

   candidate_jurisdiction     type  provisional_races  \
0           Great Britain     Flat              70218   
1           Great Britain   Hurdle              22645   
2           Great Britain    Chase              15671   
3                  France     Flat              15514   
4                 Ireland     Flat              14763   
5                 Ireland   Hurdle               9667   
6               Hong Kong     Flat               7481   
7           United States     Flat               6023   
8                 Ireland    Chase               4833   
9               Australia     Flat               4059   
10          Great Britain  NH Flat               3100   
11
…
```

### Cell 20

Matched: `verified`

```text
## Observed jurisdiction-and-code units

The source contains 56 observed combinations of candidate jurisdiction and source `type`.

These combinations are investigation units, not yet formal rules-framework assignments.

The large populations support immediate separate study of:

- Great Britain: Flat, Hurdle, Chase and NH Flat
- Ireland: Flat, Hurdle, Chase and NH Flat
- France: Flat, Hurdle and Chase
- United States: predominantly Flat, with smaller Hurdle and Chase populations
- Japan: predominantly Flat, with small obstacle-racing populations

Several very small combinations require caution. A source label such as `Hurdle`, `Chase` or `NH Flat` does not by itself prove that the race falls under a British-style rules category with the same regulatory meaning.

The next stage must therefore distinguish:

- the source's broad race-type label
- the jurisdiction's native racing code
- the applicable formal rules framework
- the responsible regulator
- the effective date period

Thin combinations will remain unresolved until their race context and governing rules can be verified.
```

### Cell 21

Matched: `https://`

```text
# Record the first evidence-backed Great Britain rules-context assignments.
#
# These rows assign the regulatory authority and broad native racing code.
# They do not yet claim that one unchanged edition of the Rules of Racing
# applied throughout 2015–2026. Formal rules-version periods remain unresolved.

great_britain_rules_context = pd.DataFrame(
    [
        {
            "candidate_jurisdiction": "Great Britain",
            "source_type": "Flat",
            "regulatory_authority": "British Horseracing Authority",
            "authority_abbreviation": "BHA",
            "native_racing_code": "Flat racing",
            "rules_framework": "BHA Rules of Racing",
            "rules_version_period": "requires date-period segmentation",
            "classification_level": "jurisdiction_and_racing_code",
            "evidence_status": "official_authority_evidence",
            "confidence": "high",
            "evidence_url": (
                "https://www.britishhorseracing.com/"
                "regulation/rules-guides/"
            ),
        },
        {
            "candidate_jurisdiction": "Great Britain",
            "source_type": "Hurdle",
            "regulatory_authority": "British Horseracing Authority",
            "authority_abbreviation": "BHA",
            "native_racing_code": "Hurdle racing",
            "rules_framework": "BHA Rules of Racing",
            "rules_version_period": "requires date-period segmentation",
            "classification_level": "jurisdiction_and_racing_code",
            "evidence_status": "official_authority_evidence",
            "confidence": "high",
            "evidence_url": (
                "https://www.britishhorseracing.com/"
                "regulation/rules-guides/"
            ),
        },
        {
            "c
…
```

### Cell 22

Matched: `https://`

```text
# Join the evidence-backed Great Britain rules context to the observed
# jurisdiction-and-code units and confirm that every British source type
# receives exactly one rules-context assignment.

great_britain_rules_coverage = (
    rules_context_units.loc[
        rules_context_units["candidate_jurisdiction"] == "Great Britain"
    ]
    .merge(
        great_britain_rules_context,
        left_on=["candidate_jurisdiction", "type"],
        right_on=["candidate_jurisdiction", "source_type"],
        how="left",
        validate="one_to_one",
    )
)

missing_assignments = (
    great_britain_rules_coverage["regulatory_authority"].isna().sum()
)

print(
    "Great Britain jurisdiction-and-code units: "
    f"{len(great_britain_rules_coverage):,}"
)
print(f"Missing rules-context assignments: {missing_assignments:,}")

assert len(great_britain_rules_coverage) == 4
assert missing_assignments == 0

great_britain_rules_coverage

Great Britain jurisdiction-and-code units: 4
Missing rules-context assignments: 0

  candidate_jurisdiction     type  provisional_races  \
0          Great Britain     Flat              70218   
1          Great Britain   Hurdle              22645   
2          Great Britain    Chase              15671   
3          Great Britain  NH Flat               3100   

   candidate_course_identities  first_date   last_date source_type  \
0                           43  2015-01-01  2026-05-27        Flat   
1                           43  2015-01-01  2026-05-27      Hurdle   
2                           43  2015-01-01  2026-05-27       Chase   
3                           44  2015-01-01  2026-05-26     NH Flat   

            regulatory_authority authority_abbreviation  \
0  British Horseracing Authority                    BHA   
1  British Horseracing Authorit
…
```

## `notebooks/11_off_time_and_temporal_semantics.ipynb`

### Cell 50

Matched: `external`

```text
## External validation strategy

Source-only meeting context may recover the missing AM/PM interpretation for many pre-15 October 2025 records, but it cannot establish the answer with certainty in every case.

Candidate reconstructions should therefore be externally validated against authoritative or contemporaneous race records.

External validation should test:

* whether `off` represents scheduled, advertised or actual off-time;
* whether the displayed clock is consistently aligned to UK civil time;
* whether the source follows GMT and BST transitions;
* whether meeting-context AM/PM reconstruction is correct;
* whether any jurisdiction, course or period follows a different convention.

Validation should use a stratified sample rather than isolated convenient examples. The sample should include:

* UK and Irish afternoon meetings;
* French meetings spanning noon;
* Hong Kong and Japanese meetings around UK clock changes;
* Australian and New Zealand meetings shown during UK morning hours;
* complete cards and single-race records;
* meetings with uniquely plausible and competing AM/PM interpretations.

The source-only analysis will first classify candidate recoverability. External evidence will then be used to validate the method and resolve selected ambiguous cases.
```

### Cell 52

Matched: `external`

```text
# Measure the shortest coherent span of each pre-boundary meeting on a
# 12-hour clock.
#
# Each raw time is converted to a minute position from 0 to 719:
#   12:xx becomes 0:xx on the circular clock
#   1:xx through 11:xx retain their ordinary positions
#
# The largest gap between consecutive values identifies the most natural
# place to "cut" the circle. The remaining arc is the shortest meeting span.
#
# This recovers relative ordering and duration only. The complete sequence
# remains ambiguous by a 12-hour shift until externally validated.

pre_boundary_clock_values = pd.read_sql_query(
    f"""
    SELECT
        date,
        course,
        off,
        CAST(SUBSTR(off, 1, INSTR(off, ':') - 1) AS INTEGER) AS hour_value,
        CAST(SUBSTR(off, INSTR(off, ':') + 1) AS INTEGER) AS minute_value
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND date < '2025-10-15'
    GROUP BY
        date,
        course,
        off
    ORDER BY
        date,
        course
    """,
    connection,
)

pre_boundary_clock_values["clock_12_minutes"] = (
    (pre_boundary_clock_values["hour_value"] % 12) * 60
    + pre_boundary_clock_values["minute_value"]
)

def shortest_circular_span(values: pd.Series) -> pd.Series:
    """Return the shortest span containing all values on a 720-minute clock."""
    ordered = sorted(values.astype(int).tolist())
    count = len(ordered)

    if count <= 1:
        return pd.Series(
            {
                "provisional_races": count,
                "shortest_span_minutes": 0,
                "largest_unused_gap_minutes": 720,
                "possible_cut_count": 1,
            }
        )

    circular_gaps = [
        ordered[index + 1] - ordered[index]
        for index in range(count - 1)
    ]
    circular_gaps.append(ordered[0] + 720
…
```

### Cell 55

Matched: `external`, `racecard`

```text
## Stratified external-validation sample

The 32 meetings with source-only spans above six hours are largely plausible long cards rather than clear reconstruction failures.

They include:

* major United States cards extending across much of the UK evening;
* large French cards containing up to 15 races;
* sparse imported records where only selected races are present.

A six-hour threshold is therefore not a suitable validity rule.

The principal unresolved issue remains the absolute 12-hour interpretation of pre-boundary values. External validation should now compare selected source records with contemporaneous racecards or results.

The validation sample will include:

* ordinary UK and Irish afternoon cards;
* French cards crossing noon in the source clock;
* Australian and East Asian cards appearing during the UK morning;
* major North American evening cards;
* single-race and sparse imported records;
* unusually long meetings;
* meetings near UK daylight-saving transitions.

The next step constructs a reproducible stratified sample from the source.
```

### Cell 56

Matched: `external`

```text
# Construct a genuinely stratified external-validation sample.
#
# Each broad region contributes examples from several analytically useful
# meeting types where available:
#
#   * single-race or sparse records;
#   * large cards;
#   * cards containing very low source-clock hours;
#   * cards crossing 12 on the old unlabeled clock;
#   * ordinary multi-race cards.
#
# A maximum of two meetings is selected per region and stratum so that sparse
# records cannot dominate the sample.

validation_candidates = pd.read_sql_query(
    f"""
    WITH provisional_races AS (
        SELECT
            date,
            course,
            off,
            race_id,
            race_name,
            MIN(rowid) AS first_source_rowid,
            CAST(SUBSTR(off, 1, INSTR(off, ':') - 1) AS INTEGER) AS hour_value,
            CAST(SUBSTR(off, INSTR(off, ':') + 1) AS INTEGER) AS minute_value
        FROM data
        WHERE {DATA_ROW_PREDICATE}
          AND date < '2025-10-15'
        GROUP BY
            date,
            course,
            off,
            race_id,
            race_name
    ),
    classified_races AS (
        SELECT
            *,
            CASE
                WHEN course LIKE '%(AUS)%'
                    THEN 'Australia'
                WHEN course LIKE '%(NZ)%'
                    THEN 'New Zealand'
                WHEN course LIKE '%(JPN)%'
                    THEN 'Japan'
                WHEN course LIKE '%(HK)%'
                    THEN 'Hong Kong'
                WHEN course LIKE '%(USA)%'
                    THEN 'United States'
                WHEN course LIKE '%(FR)%'
                    THEN 'France'
                WHEN course LIKE '%(IRE)%'
                    THEN 'Ireland'
                WHEN course NOT LIKE '%(%'
                     OR course LI
…
```

### Cell 57

Matched: `external`

```text
### Race-level external-validation sheet

The corrected sample contains 62 meetings distributed across the required regions and meeting types.

External validation will begin with representative races from each meeting rather than every race. For multi-race cards, the sample will include:

* the first race by reconstructed relative order;
* a middle race;
* the final race.

For single-race meetings, the sole available race will be included.

This should normally be sufficient to determine:

* which 12-hour-shifted interpretation is correct;
* whether the reconstructed meeting sequence is coherent;
* whether `off` corresponds to an advertised race time or an actual starting time;
* and whether the UK civil-time interpretation holds across the card.

Any meeting showing disagreement can then be expanded to all races.
```

### Cell 58

Matched: `external`

```text
# Expand the stratified meeting sample into representative race-level records.
#
# Pre-boundary times are ordered on the 12-hour circular clock using the
# largest unused gap as the cut point. This recovers a relative sequence but
# does not yet choose between the two absolute UK-time candidates separated
# by 12 hours.

sample_races = pre_boundary_clock_values.merge(
    validation_candidates[
        [
            "date",
            "course",
            "broad_region",
            "validation_stratum",
            "provisional_races",
        ]
    ],
    on=["date", "course"],
    how="inner",
)

def unwrap_meeting(group: pd.DataFrame) -> pd.DataFrame:
    """Recover the shortest relative ordering on the 12-hour clock."""
    group = group.copy()

    ordered_positions = sorted(
        group["clock_12_minutes"].astype(int).tolist()
    )

    if len(ordered_positions) == 1:
        cut_after = ordered_positions[0]
    else:
        gaps = []

        for index, value in enumerate(ordered_positions):
            next_value = (
                ordered_positions[index + 1]
                if index + 1 < len(ordered_positions)
                else ordered_positions[0] + 720
            )

            gaps.append(
                {
                    "value": value,
                    "gap": next_value - value,
                }
            )

        cut_after = max(
            gaps,
            key=lambda item: item["gap"],
        )["value"]

    group["relative_minutes"] = group["clock_12_minutes"].where(
        group["clock_12_minutes"] > cut_after,
        group["clock_12_minutes"] + 720,
    )

    group["relative_minutes"] = (
        group["relative_minutes"]
        - group["relative_minutes"].min()
    )

    return (
        group
        .sort_values(
…
```

### Cell 59

Matched: `external`

```text
### Pilot external-validation set

The race-level sheet contains 148 representative records across 62 meetings.

External validation will begin with a smaller pilot designed to test the principal reconstruction cases:

* Australian racing shown during the UK morning;
* Hong Kong and Japanese racing across GMT and BST;
* French and Irish afternoon cards crossing `12`;
* North American racing shown during the UK evening;
* one sparse or single-race record.

The pilot will establish:

* whether the external advertised time matches the source `off`;
* whether the correct pre-boundary interpretation is the morning or afternoon candidate;
* whether the date is a UK-facing racing date or the racecourse-local date;
* and whether the source time is scheduled or actual off-time.

If the pilot confirms a stable method, the same procedure can be applied to the remaining validation sheet.
```

### Cell 60

Matched: `external`

```text
# Select a small, explicit pilot sample for external validation.
#
# These meetings cover the major regions and ambiguity types without relying
# on random selection. Three representative races are retained for full cards
# and the sole race is retained for single-race records.

pilot_meetings = pd.DataFrame(
    [
        {
            "date": "2018-10-20",
            "course": "Caulfield (AUS)",
            "pilot_reason": "Australian full card in UK morning",
        },
        {
            "date": "2024-04-06",
            "course": "Randwick (AUS)",
            "pilot_reason": "Recent Australian full card",
        },
        {
            "date": "2024-06-30",
            "course": "Curragh (IRE)",
            "pilot_reason": "Irish afternoon card using low hours",
        },
        {
            "date": "2017-03-05",
            "course": "Auteuil (FR)",
            "pilot_reason": "French card crossing 12",
        },
        {
            "date": "2021-04-11",
            "course": "Sha Tin (HK)",
            "pilot_reason": "Hong Kong card during UK BST",
        },
        {
            "date": "2025-03-01",
            "course": "Gulfstream Park (USA)",
            "pilot_reason": "North American evening card",
        },
        {
            "date": "2025-10-11",
            "course": "Keeneland (USA)",
            "pilot_reason": "Single-race record near format boundary",
        },
    ]
)

pilot_external_validation = (
    external_validation_sheet
    .merge(
        pilot_meetings,
        on=["date", "course"],
        how="inner",
    )
    [
        [
            "date",
            "course",
            "pilot_reason",
            "representative_position",
            "race_sequence",
            "off",
            "relative_minutes",
…
```

### Cell 61

Matched: `external`, `racecard`

```text
### Pilot records prepared for external lookup

Four requested pilot meetings are present in the stratified race-level validation sheet:

* Caulfield on 20 October 2018;
* Randwick on 6 April 2024;
* Gulfstream Park on 1 March 2025;
* Keeneland on 11 October 2025.

The requested Curragh, Auteuil and Sha Tin meetings were not selected into the current 62-meeting sheet, so they did not appear in the pilot output. They can be added separately later.

Before external lookup, each pilot record needs its source race name and source race reference. These fields will make contemporaneous racecards and results much easier to identify accurately.
```

### Cell 62

Matched: `external`

```text
# Enrich the pilot records with source race identity and two possible
# pre-boundary UK clock interpretations.
#
# For hours 1 through 11:
#   candidate A retains the apparent morning time;
#   candidate B adds 12 hours.
#
# Hour 12 has two possible interpretations:
#   00:xx or 12:xx.
#
# External evidence will determine which candidate is correct.

pilot_validation_lookup = pd.read_sql_query(
    f"""
    SELECT
        date,
        course,
        off,
        race_id,
        race_name
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND (
          (date = '2018-10-20' AND course = 'Caulfield (AUS)')
          OR
          (date = '2024-04-06' AND course = 'Randwick (AUS)')
          OR
          (date = '2025-03-01' AND course = 'Gulfstream Park (USA)')
          OR
          (date = '2025-10-11' AND course = 'Keeneland (USA)')
      )
    GROUP BY
        date,
        course,
        off,
        race_id,
        race_name
    """,
    connection,
)

pilot_validation_lookup = (
    pilot_external_validation
    .merge(
        pilot_validation_lookup,
        on=["date", "course", "off"],
        how="left",
        validate="one_to_one",
    )
)

def format_minutes(total_minutes: int) -> str:
    """Format minutes after midnight as HH:MM."""
    total_minutes %= 24 * 60
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

def absolute_time_candidates(raw_off: str) -> tuple[str, str]:
    """Return the two UK-clock candidates separated by 12 hours."""
    raw_hour, raw_minute = map(int, raw_off.split(":"))

    first_minutes = (raw_hour % 12) * 60 + raw_minute
    second_minutes = first_minutes + 12 * 60

    return (
        format_minutes(first_minutes),
        format_minutes(second_minutes),
    )

candidate_pairs = pilot_validation_lookup["o
…
```

### Cell 63

Matched: `external`

```text
### Initial external-validation findings

The first external checks support the proposed UK-time reconstruction.

For the Australian meetings:

* Caulfield values `2:15`, `4:45` and `7:50` correspond to UK morning times;
* Randwick `2:25` corresponds to `02:25` UK time;
* the 12-hour-shifted afternoon candidates are not credible.

For the North American meetings:

* Gulfstream values `6:01`, `9:04` and `11:14` correspond to `18:01`, `21:04` and `23:14` UK time;
* Keeneland `10:16` corresponds to `22:16` UK time;
* the unshifted morning candidates are not credible.

The pilot therefore confirms that pre-boundary low-hour values cannot be assigned globally to either AM or PM. Their correct interpretation depends on the meeting.

The Keeneland validation also distinguishes two temporal concepts:

* the source value is `10:16`, reconstructed as an advertised UK time of `22:16`;
* an external result records the actual off-time as `22:17`.

This supports treating source `off` provisionally as an advertised or scheduled UK-facing time rather than assuming it records the exact moment the race started.

Further external validation is still required before applying the reconstruction method to the full pre-boundary population.
```

### Cell 64

Matched: `external`, `racing post`

```text
# Record the initial external-validation findings.
#
# These results distinguish the selected absolute UK-time candidate and,
# where evidence permits, advertised time from actual off-time.
#
# The evidence URLs and access date should be retained for auditability.

pilot_validation_results = pd.DataFrame(
    [
        {
            "date": "2018-10-20",
            "course": "Caulfield (AUS)",
            "race_id": 714541,
            "raw_off": "2:15",
            "reconstructed_uk_time": "02:15",
            "selected_candidate": "A",
            "external_advertised_time": "02:15",
            "external_actual_off_time": None,
            "external_source": "Racing Post",
            "validation_result": "confirmed",
            "temporal_semantics": "advertised_or_scheduled_time",
            "confidence": "high",
        },
        {
            "date": "2018-10-20",
            "course": "Caulfield (AUS)",
            "race_id": 714545,
            "raw_off": "4:45",
            "reconstructed_uk_time": "04:45",
            "selected_candidate": "A",
            "external_advertised_time": "04:45",
            "external_actual_off_time": None,
            "external_source": "Racing Post",
            "validation_result": "confirmed",
            "temporal_semantics": "advertised_or_scheduled_time",
            "confidence": "high",
        },
        {
            "date": "2018-10-20",
            "course": "Caulfield (AUS)",
            "race_id": 714667,
            "raw_off": "7:50",
            "reconstructed_uk_time": "07:50",
            "selected_candidate": "A",
            "external_advertised_time": "07:50",
            "external_actual_off_time": None,
            "external_source": "Racing Post",
            "validation_result": "confirmed",
…
```

### Cell 65

Matched: `external`

```text
### Second external-validation pilot

The initial pilot confirms that different meetings can require different
12-hour candidates.

The correct interpretation must not be generalised by country or continent
alone. It depends on:

* the individual racecourse location;
* the source date;
* the course-local timezone and daylight-saving regime;
* the UK GMT/BST regime;
* the plausible local race schedule;
* and external validation.

The validated Caulfield and Randwick examples use the unshifted UK-morning
candidate. The validated Gulfstream Park and Keeneland examples use the
candidate shifted forward by 12 hours.

These are meeting-specific findings, not universal jurisdictional rules.

It also provides evidence that source `off` represents an advertised or scheduled UK-facing time rather than the exact actual start.

The current confirmed sample does not yet include:

* Britain or Ireland;
* France;
* Hong Kong;
* Japan.

A second targeted pilot will therefore select representative meetings directly from the source rather than requiring them to appear in the earlier stratified sample.

The second pilot will focus on:

* an Irish afternoon card;
* a French card crossing `12`;
* a Hong Kong card during UK winter or summer time;
* a Japanese race;
* and an ordinary British afternoon card.

External validation of these records will test whether the same reconstruction logic applies across the remaining major regions.
```

### Cell 66

Matched: `external`

```text
# Prepare a second targeted external-validation pilot.
#
# These meetings are selected explicitly to cover regions absent from the
# initial confirmed pilot. First, middle and final races are retained where
# full cards are available.

second_pilot_meetings = pd.DataFrame(
    [
        {
            "date": "2024-06-30",
            "course": "Curragh (IRE)",
            "pilot_reason": "Irish afternoon card using low hours",
        },
        {
            "date": "2017-03-05",
            "course": "Auteuil (FR)",
            "pilot_reason": "French card crossing 12",
        },
        {
            "date": "2021-04-11",
            "course": "Sha Tin (HK)",
            "pilot_reason": "Hong Kong card during UK BST",
        },
        {
            "date": "2019-11-24",
            "course": "Kyoto (JPN)",
            "pilot_reason": "Japanese race during UK GMT",
        },
        {
            "date": "2024-07-13",
            "course": "Newmarket (July)",
            "pilot_reason": "Ordinary British afternoon card",
        },
    ]
)

second_pilot_races = pd.read_sql_query(
    f"""
    SELECT
        date,
        course,
        off,
        race_id,
        race_name,
        CAST(SUBSTR(off, 1, INSTR(off, ':') - 1) AS INTEGER) AS hour_value,
        CAST(SUBSTR(off, INSTR(off, ':') + 1) AS INTEGER) AS minute_value
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND (
          (date = '2024-06-30' AND course = 'Curragh (IRE)')
          OR
          (date = '2017-03-05' AND course = 'Auteuil (FR)')
          OR
          (date = '2021-04-11' AND course = 'Sha Tin (HK)')
          OR
          (date = '2019-11-24' AND course = 'Kyoto (JPN)')
          OR
          (date = '2024-07-13' AND course = 'Newmarket (July)')
      )
    GROUP BY
        date,
…
```

### Cell 67

Matched: `external`

```text
### Partial findings from the second validation pilot

Direct external evidence confirms the afternoon candidate for the Irish and
British examples.

For the Curragh on 30 June 2024:

* source `off`: `1:10`;
* reconstructed advertised UK/Irish time: `13:10`;
* externally reported actual off-time: approximately `13:10:07`.

For Newmarket on 13 July 2024:

* source `off`: `1:40`;
* reconstructed advertised UK time: `13:40`;
* externally reported actual off-time: approximately `13:41`.

These examples further support treating source `off` as an advertised or
scheduled minute rather than the exact actual starting timestamp.

The Auteuil, Kyoto and Sha Tin candidates remain pending direct race-level
external confirmation. Their plausible timezone interpretation alone is not
sufficient to mark them validated.
```

### Cell 68

Matched: `external`, `racing post`

```text
# Record only the second-pilot findings directly confirmed by external
# race-level evidence.
#
# Auteuil, Kyoto and Sha Tin remain pending rather than being inferred from
# timezone plausibility alone.

second_pilot_validation_results = pd.DataFrame(
    [
        {
            "date": "2024-06-30",
            "course": "Curragh (IRE)",
            "race_id": 871044,
            "raw_off": "1:10",
            "reconstructed_uk_time": "13:10",
            "selected_candidate": "B",
            "external_advertised_time": "13:10",
            "external_actual_off_time": "13:10:07",
            "external_source": "Racing Post",
            "validation_result": "confirmed",
            "temporal_semantics": (
                "advertised_time_with_second_level_actual_off"
            ),
            "confidence": "high",
        },
        {
            "date": "2024-07-13",
            "course": "Newmarket (July)",
            "race_id": 870497,
            "raw_off": "1:40",
            "reconstructed_uk_time": "13:40",
            "selected_candidate": "B",
            "external_advertised_time": "13:40",
            "external_actual_off_time": "13:41:02",
            "external_source": "Racing TV / Sky Sports",
            "validation_result": "confirmed",
            "temporal_semantics": (
                "advertised_time_not_exact_actual_off"
            ),
            "confidence": "high",
        },
    ]
)

second_pilot_validation_results
         date            course  race_id raw_off reconstructed_uk_time  \
0  2024-06-30     Curragh (IRE)   871044    1:10                 13:10   
1  2024-07-13  Newmarket (July)   870497    1:40                 13:40   

  selected_candidate external_advertised_time external_actual_off_time  \
0                  B
…
```

### Cell 69

Matched: `external`

```text
### Combined confirmed validation evidence

The two validation pilots currently provide direct race-level confirmation for:

* Caulfield, Australia;
* Randwick, Australia;
* Gulfstream Park, United States;
* Keeneland, United States;
* the Curragh, Ireland;
* Newmarket, Britain.

Both possible pre-boundary 12-hour candidates are required in practice.

The evidence therefore rules out any global AM/PM conversion rule. The correct
candidate must be determined using meeting context, racecourse location,
date-specific timezone relationships and external evidence.

The confirmed records also support interpreting source `off` as the advertised
or scheduled UK-facing race time. Where precise actual off-times are available,
they can differ from the source value by seconds or minutes.
```

### Cell 70

Matched: `external`

```text
# Combine all directly confirmed external-validation results and summarise
# what the evidence currently establishes.

confirmed_validation_results = pd.concat(
    [
        pilot_validation_results,
        second_pilot_validation_results,
    ],
    ignore_index=True,
)

confirmed_validation_summary = pd.DataFrame(
    [
        {
            "confirmed_races": len(confirmed_validation_results),
            "confirmed_meetings": confirmed_validation_results[
                ["date", "course"]
            ].drop_duplicates().shape[0],
            "courses": confirmed_validation_results["course"].nunique(),
            "candidate_a_confirmations": int(
                (
                    confirmed_validation_results["selected_candidate"] == "A"
                ).sum()
            ),
            "candidate_b_confirmations": int(
                (
                    confirmed_validation_results["selected_candidate"] == "B"
                ).sum()
            ),
            "records_with_precise_actual_off": int(
                confirmed_validation_results[
                    "external_actual_off_time"
                ].notna().sum()
            ),
            "advertised_time_matches_source": int(
                (
                    confirmed_validation_results["reconstructed_uk_time"]
                    == confirmed_validation_results[
                        "external_advertised_time"
                    ]
                ).sum()
            ),
            "validation_failures": int(
                (
                    confirmed_validation_results["validation_result"]
                    != "confirmed"
                ).sum()
            ),
        }
    ]
)

confirmed_validation_summary
   confirmed_races  confirmed_meetings  courses  candidate_a_confirmatio
…
```

### Cell 71

Matched: `external`

```text
## Database treatment of `off`

The reconstruction target is the advertised UK-facing race time.

Precise actual off-times are not required for the current database because they
would introduce a different temporal concept and reduce consistency across the
source population.

The database should therefore preserve and distinguish:

* `off_raw`: the exact source text;
* `off_format_regime`: the applicable raw-format regime;
* `off_uk_time`: the reconstructed advertised UK civil time;
* `off_reconstruction_method`: direct 24-hour parsing, meeting-context recovery
  or external validation;
* `off_reconstruction_confidence`: deterministic, high, provisional or
  unresolved.

Actual off-times should not overwrite the advertised source time. They may be
added later as a separate enrichment field if a specific analytical use
requires them.

For records from 15 October 2025 onward, `off_uk_time` is deterministically
available from the fixed-width `HH:MM` source value.

For records before 15 October 2025, the source clock omits AM/PM. The correct
UK civil time must therefore be reconstructed at meeting level before conversion
to UTC. The reconstruction will use the meeting sequence, course and date
timezone context, and external validation where the source-only evidence does
not determine the correct 12-hour branch.
```

### Cell 72

Matched: `external`

```text
## Agreed temporal reconstruction model

The source `date + off` pair will be treated as a UK-facing advertised civil
datetime.

Reconstruction will proceed as follows:

1. preserve source `date` and `off` exactly;
2. recover the correct pre-boundary 12-hour candidate where required;
3. interpret the reconstructed datetime in `Europe/London`;
4. convert it to UTC;
5. use UTC as the canonical database timestamp;
6. derive racecourse-local datetime later from UTC and the course's IANA
   timezone.

The database may therefore contain three legitimate date representations:

* source or UK-facing date;
* UTC date;
* racecourse-local date.

These describe the same advertised race-start instant in different temporal
systems.

The canonical field should be:

`advertised_start_utc`

Source-facing and local representations should remain available for audit,
display and external matching, but should not replace the UTC timestamp.
```

### Cell 73

Matched: `manual`, `external`

```text
## Source-supported reconstruction of pre-boundary meetings

The temporal model is now settled:

* source `date + off` represents a UK-facing advertised datetime;
* records from 15 October 2025 onward provide direct `HH:MM` UK civil times;
* earlier records omit AM/PM and require meeting-level reconstruction;
* the selected UK civil datetime will be converted to canonical UTC.

Before relying on manual external validation for every earlier meeting, the
source itself may provide additional evidence.

Many racecourses occur in both temporal regimes. Their post-boundary records
show directly which UK clock windows those courses commonly occupy. These
observed windows can be compared with the two 12-hour candidates for earlier
meetings.

This evidence must be used cautiously:

* race schedules can change by season and meeting type;
* individual courses may stage daytime, evening or night meetings;
* daylight-saving relationships vary by date;
* and empirical course patterns cannot replace external validation where both
  candidates remain plausible.

The next step will measure how much of the pre-boundary population belongs to
courses that also have directly interpretable post-boundary records.
```

### Cell 89

Matched: `external`, `verified`

```text
### Post-boundary course windows are descriptive only

The circular clock-span calculation corrected the artificial midnight-boundary
ranges produced by linear minimum and maximum values.

However, even resolved course identities can occupy broad UK-time windows across
different dates, seasons and meeting types.

These post-boundary distributions will therefore not be used as deterministic
or probabilistic AM/PM reconstruction rules for earlier records.

They remain useful only as descriptive context and as a way to identify records
that merit external checking.

Pre-boundary times will be accepted only when supported by externally verifiable
race or meeting evidence. Unverified records will remain unresolved rather than
receive an inferred timestamp.
```

### Cell 90

Matched: `external`

```text
For records before 15 October 2025, no AM/PM candidate will be accepted solely
because it resembles the usual time window for that course.

The reconstructed UK civil time must be supported by externally verifiable
race or meeting evidence. Once one race in a meeting is securely anchored, the
remaining races may be reconstructed from the internally consistent meeting
sequence.

Records that cannot be established with sufficient evidence will retain both
12-hour candidates and an unresolved reconstruction status rather than receive
a guessed timestamp.
```

### Cell 91

Matched: `external`, `verified`

```text
## Meeting-level validation and reconstruction workflow

Pre-boundary `off` values will be reconstructed at meeting level rather than
race by race.

For each candidate meeting identified by `date + course`, the workflow will:

1. preserve every raw `off` value;
2. generate the two possible UK civil-time branches for each race;
3. reconstruct the internally consistent race sequence for each branch;
4. resolve candidate course identity and jurisdiction;
5. obtain external evidence for at least one race or the meeting card;
6. use the verified anchor to select the correct 12-hour branch for the meeting;
7. assign reconstructed UK civil datetimes to the remaining races only where
   their sequence is internally consistent with the verified meeting;
8. convert accepted UK datetimes through `Europe/London` to canonical UTC;
9. retain unresolved status where no sufficiently reliable external anchor can
   be obtained.

The resulting reconstruction should distinguish:

* `externally_verified`;
* `meeting_sequence_derived_from_verified_anchor`;
* `unresolved`.

No timestamp should be assigned solely from a course's usual racing window.
```

### Cell 93

Matched: `external`, `verified`

```text
# Measure the external-validation workload by jurisdiction and meeting size.
#
# Multi-race meetings can be reconstructed from one securely verified anchor
# when the remaining race sequence is internally consistent. Single-race
# meetings require direct evidence for that race.

pre_boundary_validation_workload = (
    pre_boundary_meeting_candidates
    .assign(
        meeting_structure=lambda frame: frame["race_count"].map(
            lambda count: "single_race" if count == 1 else "multi_race"
        )
    )
    .groupby(
        ["candidate_jurisdictions", "meeting_structure"],
        as_index=False,
    )
    .agg(
        meetings=("date", "size"),
        races=("race_count", "sum"),
        earliest_date=("date", "min"),
        latest_date=("date", "max"),
    )
    .sort_values(
        ["candidate_jurisdictions", "meeting_structure"]
    )
    .reset_index(drop=True)
)

pre_boundary_validation_workload
   candidate_jurisdictions meeting_structure  meetings  races earliest_date  \
0                Argentina        multi_race       104    336    2015-02-07   
1                Argentina       single_race        80     80    2015-01-03   
2                Australia        multi_race       770   3285    2015-01-01   
3                Australia       single_race       513    513    2015-01-01   
4                  Bahrain        multi_race        24     74    2021-11-19   
..                     ...               ...       ...    ...           ...   
59    United Arab Emirates       single_race       264    264    2015-01-04   
60           United States        multi_race      1186   4147    2015-01-03   
61           United States       single_race      1716   1716    2015-01-01   
62                 Uruguay        multi_race        25     53    2015-01-06   
6
…
```

### Cell 95

Matched: `external`, `verified`

```text
### Validation workload is concentrated efficiently

Multi-race meetings account for 25,380 of the 31,441 pre-boundary meetings and
172,630 of the 178,691 pre-boundary races.

Therefore, one securely verified anchor per multi-race meeting could establish
the correct 12-hour branch for 96.61% of the old race population, subject to
internal sequence consistency.

Single-race meetings account for 6,061 records, or 3.39% of pre-boundary races.
They cannot inherit a branch from neighbouring races and therefore require
direct external evidence.

The validation workflow will consequently maintain two queues:

* multi-race meetings requiring one reliable meeting or race anchor;
* single-race meetings requiring direct race-level validation.

Unverified records in either queue will remain unresolved.
```

### Cell 97

Matched: `external`

```text
# Create a compact external-validation pilot:
# the earliest and latest eligible multi-race meeting in each jurisdiction.

ordered_multi_race_candidates = (
    multi_race_validation_candidates
    .sort_values(
        [
            "candidate_jurisdictions",
            "date",
            "course",
        ]
    )
)

earliest_by_jurisdiction = (
    ordered_multi_race_candidates
    .drop_duplicates(
        subset=["candidate_jurisdictions"],
        keep="first",
    )
    .assign(sample_position="earliest")
)

latest_by_jurisdiction = (
    ordered_multi_race_candidates
    .drop_duplicates(
        subset=["candidate_jurisdictions"],
        keep="last",
    )
    .assign(sample_position="latest")
)

compact_multi_race_validation_sample = (
    pd.concat(
        [
            earliest_by_jurisdiction,
            latest_by_jurisdiction,
        ],
        ignore_index=True,
    )
    .drop_duplicates(
        subset=["date", "course"],
        keep="first",
    )
    .sort_values(
        [
            "candidate_jurisdictions",
            "sample_position",
            "date",
            "course",
        ]
    )
    .reset_index(drop=True)
)

print("Sample rows:", len(compact_multi_race_validation_sample))

compact_multi_race_validation_sample[
    [
        "sample_position",
        "date",
        "course",
        "candidate_jurisdictions",
        "race_count",
        "first_off_raw",
        "last_off_raw",
        "branch_a_start_uk",
        "branch_a_end_uk",
        "branch_b_start_uk",
        "branch_b_end_uk",
        "first_race_name",
    ]
].head(10)

Sample rows: 60

  sample_position        date               course candidate_jurisdictions  \
0        earliest  2015-02-07     San Isidro (ARG)               Argentina   
1          latest  2
…
```

### Cell 98

Matched: `verified`

```text
### Local-time feasibility can eliminate impossible branches

Course and timezone evidence may be used to reject a pre-boundary branch when
that branch places the meeting at a demonstrably implausible racecourse-local
time.

This differs from choosing the branch that merely resembles the course's usual
schedule.

For each meeting:

1. convert both candidate UK civil-time branches to the resolved course-local
   timezone for that historical date;
2. calculate the local start and end of each candidate meeting;
3. reject a branch only where its complete local meeting window falls within a
   verified non-racing period;
4. accept the remaining branch where exactly one candidate remains feasible;
5. retain both candidates where both local windows remain plausible.

A course's typical time distribution may support investigation, but it should
not by itself establish the branch. The exclusion rule must be based on strong
course or jurisdiction evidence that racing is not staged during the rejected
local-time window.
```

### Cell 99

Matched: `external`, `racecard`

```text
### Accepted use of local-time feasibility

Local racecourse time may be used to resolve the missing pre-boundary AM/PM
branch where one candidate produces a clearly unreasonable racing schedule.

This is treated as a defensible temporal constraint rather than a statistical
prediction from typical race times.

A branch may be selected where:

* course identity and jurisdiction are resolved;
* the applicable historical IANA timezone is known;
* one candidate produces a normal or credible local meeting window;
* and the alternative places the meeting wholly within an unreasonable
  overnight period.

Where both candidates remain credible, the record will remain unresolved unless
external racecard evidence is available.

The selected branch should retain:

* the reconstruction rule;
* the course timezone used;
* the rejected local-time window;
* and a confidence or review status.

The course-to-IANA-timezone mapping should be implemented as reusable project
code rather than defined only inside this notebook.
```

### Cell 101

Matched: `validation_status`

```text
### Course location is the basis of timezone assignment

An IANA timezone should not be assigned directly from raw course text or broad
jurisdiction.

Each candidate course identity must first be linked to a physical racing venue.
The venue's geographical location then determines the applicable historical
IANA timezone.

The reusable course-location reference should contain:

* `candidate_course_label`;
* `candidate_jurisdiction`;
* `physical_venue_name`;
* `locality`;
* `region`;
* `country`;
* `latitude`;
* `longitude`;
* `iana_timezone`;
* `location_evidence`;
* `location_validation_status`.

The temporal reconstruction workflow will therefore be:

1. resolve the candidate physical venue;
2. obtain its geographical location;
3. assign the location's IANA timezone;
4. convert both UK-time candidates into historical course-local time;
5. reject a candidate only where it creates an unreasonable local meeting
   window.

This course-location reference should become a reusable project dimension
rather than a Notebook 11-only lookup.
```

### Cell 102

Matched: `external`, `validation_status`

```text
# Create the controlled course-location reference scaffold.
#
# Venue location and timezone fields remain deliberately blank until they are
# supported by an external venue source. Race times must not be used to infer
# the location or timezone.

course_location_reference = (
    pre_boundary_course_timezone_scope[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "raw_course_labels",
            "provisional_races",
            "meeting_dates",
            "earliest_date",
            "latest_date",
        ]
    ]
    .copy()
)

course_location_reference["physical_venue_name"] = pd.NA
course_location_reference["locality"] = pd.NA
course_location_reference["region"] = pd.NA
course_location_reference["country"] = pd.NA
course_location_reference["latitude"] = pd.NA
course_location_reference["longitude"] = pd.NA
course_location_reference["iana_timezone"] = pd.NA
course_location_reference["location_evidence"] = pd.NA
course_location_reference["location_validation_status"] = "unassigned"

course_location_reference = course_location_reference[
    [
        "candidate_course_label",
        "candidate_jurisdiction",
        "physical_venue_name",
        "locality",
        "region",
        "country",
        "latitude",
        "longitude",
        "iana_timezone",
        "location_evidence",
        "location_validation_status",
        "raw_course_labels",
        "provisional_races",
        "meeting_dates",
        "earliest_date",
        "latest_date",
    ]
].sort_values(
    [
        "candidate_jurisdiction",
        "candidate_course_label",
    ]
).reset_index(drop=True)

print("Course identities requiring location validation:", len(course_location_reference))

course_location_reference.head(20)

Course identities
…
```

### Cell 103

Matched: `external`

```text
## Reusable course-location reference

The 394 candidate course identities will be maintained in a reusable reference
dataset rather than embedded in Notebook 11.

The proposed project files are:

* `data/reference/course_locations.csv`
* `src/inside_rails/course_locations.py`

The CSV will contain the curated physical venue and timezone assignments.

The Python module will:

* load the reference;
* validate required columns;
* reject duplicate course identities;
* validate IANA timezone names;
* and provide a reusable merge function for notebooks and later database
  construction.

Notebook 11 will use this reference to convert both candidate UK datetimes into
historical racecourse-local time.

Location and timezone assignments must be based on external venue-location
evidence, not inferred from the source race times.
```

### Cell 104

Matched: `manual`, `manually`, `validation_status`

```text
# Write the controlled course-location scaffold to the reusable reference area.
#
# Existing manually curated values are preserved if the file already exists.
# Newly discovered course identities are appended with blank location fields.

reference_directory = project_root / "data" / "reference"
reference_directory.mkdir(parents=True, exist_ok=True)

course_locations_path = reference_directory / "course_locations.csv"

reference_columns = [
    "candidate_course_label",
    "candidate_jurisdiction",
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
    "location_evidence",
    "location_validation_status",
    "raw_course_labels",
    "provisional_races",
    "meeting_dates",
    "earliest_date",
    "latest_date",
]

if course_locations_path.exists():
    existing_course_locations = pd.read_csv(course_locations_path)

    identity_columns = [
        "candidate_course_label",
        "candidate_jurisdiction",
    ]

    course_location_export = (
        existing_course_locations
        .merge(
            course_location_reference,
            on=identity_columns,
            how="outer",
            suffixes=("_existing", "_current"),
        )
    )

    for column in reference_columns:
        if column in identity_columns:
            continue

        existing_column = f"{column}_existing"
        current_column = f"{column}_current"

        if existing_column in course_location_export.columns:
            course_location_export[column] = (
                course_location_export[existing_column]
                .combine_first(course_location_export.get(current_column))
            )
        elif current_column in course_location_export.columns:
            course_location_export[column]
…
```

### Cell 105

Matched: `validation_status`

```text
# Create the reusable course-location reference module.
#
# The module validates the reference structure, uniqueness, coordinates and
# IANA timezone names. It does not assign or infer any locations.

course_locations_module_path = (
    project_root / "src" / "inside_rails" / "course_locations.py"
)

course_locations_module_text = '''"""Load and validate the curated course-location reference."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd

IDENTITY_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
]

REQUIRED_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
    "location_evidence",
    "location_validation_status",
]

def load_course_locations(path: str | Path) -> pd.DataFrame:
    """Load and validate the curated course-location reference."""

    reference_path = Path(path)
    frame = pd.read_csv(reference_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            "Course-location reference is missing required columns: "
            + ", ".join(missing_columns)
        )

    duplicate_mask = frame.duplicated(
        subset=IDENTITY_COLUMNS,
        keep=False,
    )

    if duplicate_mask.any():
        duplicates = (
            frame.loc[duplicate_mask, IDENTITY_COLUMNS]
            .drop_duplicates()
            .to_dict("records")
        )
        raise ValueError(
            f"Duplicate candidate course identities found: {duplicates}"
        )

    assigned_timezone_
…
```

### Cell 110

Matched: `validation_status`

```text
# Confirm whether Firenze is absent from the governed reference and inspect
# the existing Italian course-location records before extending it.

validated_course_locations.loc[
    validated_course_locations["candidate_jurisdiction"].eq("Italy"),
    [
        "candidate_course_label",
        "physical_venue_name",
        "locality",
        "region",
        "country",
        "iana_timezone",
        "location_validation_status",
    ],
].sort_values("candidate_course_label").reset_index(drop=True)
  candidate_course_label physical_venue_name locality region country  \
0             Capannelle                 NaN      NaN    NaN     NaN   
1                 Merano                 NaN      NaN    NaN     NaN   
2                 Naples                 NaN      NaN    NaN     NaN   
3                   Pisa                 NaN      NaN    NaN     NaN   
4               San Siro                 NaN      NaN    NaN     NaN   
5               Siracusa                 NaN      NaN    NaN     NaN   
6                 Varese                 NaN      NaN    NaN     NaN   

  iana_timezone location_validation_status  
0   Europe/Rome                 unassigned  
1   Europe/Rome                 unassigned  
2   Europe/Rome                 unassigned  
3   Europe/Rome                 unassigned  
4   Europe/Rome                 unassigned  
5   Europe/Rome                 unassigned  
6   Europe/Rome                 unassigned
```

### Cell 111

Matched: `validation_status`

```text
# Add the new post-boundary Firenze identity to the governed course reference.
#
# The permanent reference currently governs timezone assignments even where
# detailed venue metadata remains unpopulated.

firenze_reference_row = {
    "candidate_course_label": "Firenze",
    "candidate_jurisdiction": "Italy",
    "physical_venue_name": "Ippodromo del Visarno Cesare Meli",
    "locality": "Florence",
    "region": "Tuscany",
    "country": "Italy",
    "latitude": pd.NA,
    "longitude": pd.NA,
    "iana_timezone": "Europe/Rome",
    "location_evidence": (
        "Italian racing authority and City of Florence identify Firenze racing "
        "as Ippodromo del Visarno Cesare Meli"
    ),
    "location_validation_status": "timezone_validated",
    "raw_course_labels": "Firenze",
    "provisional_races": 1,
    "meeting_dates": 1,
    "earliest_date": "2026-04-25",
    "latest_date": "2026-04-25",
}

course_location_export = pd.read_csv(course_locations_path)

identity_mask = (
    course_location_export["candidate_course_label"].eq("Firenze")
    & course_location_export["candidate_jurisdiction"].eq("Italy")
)

if not identity_mask.any():
    course_location_export = pd.concat(
        [
            course_location_export,
            pd.DataFrame([firenze_reference_row]),
        ],
        ignore_index=True,
    )

course_location_export = (
    course_location_export
    .sort_values(
        ["candidate_jurisdiction", "candidate_course_label"]
    )
    .reset_index(drop=True)
)

course_location_export.to_csv(course_locations_path, index=False)

validated_course_locations = course_locations.load_course_locations(
    course_locations_path
)

print("Reference rows:", len(validated_course_locations))
print(
    "Assigned timezones:",
    validated_course_locations["ian
…
```

### Cell 132

Matched: `manual`

```text
# Build a reproducible manual-validation sample that:
# - covers the principal evidence categories;
# - avoids duplicate meetings across categories;
# - spreads selections across the pre-boundary date range.

def select_spread_sample(
    frame,
    category,
    count,
    used_meetings,
):
    candidates = (
        frame
        .drop_duplicates(["date", "course"])
        .copy()
    )

    candidates["meeting_key"] = list(
        zip(candidates["date"], candidates["course"])
    )

    candidates = candidates.loc[
        ~candidates["meeting_key"].isin(used_meetings)
    ].sort_values(["date", "course"])

    if len(candidates) <= count:
        selected = candidates.copy()
    else:
        selected_positions = np.linspace(
            0,
            len(candidates) - 1,
            count,
        ).round().astype(int)

        selected = candidates.iloc[
            np.unique(selected_positions)
        ].copy()

    selected["validation_category"] = category

    used_meetings.update(selected["meeting_key"])

    return selected

used_validation_meetings = set()
validation_sample_parts = []

validation_sample_parts.append(
    select_spread_sample(
        stable_profile_details.loc[
            stable_profile_details[
                "stable_profile_decision"
            ].eq("candidate_a")
        ],
        "stable_profile_candidate_a",
        6,
        used_validation_meetings,
    )
)

validation_sample_parts.append(
    select_spread_sample(
        stable_profile_details.loc[
            stable_profile_details[
                "stable_profile_decision"
            ].eq("candidate_b")
        ],
        "stable_profile_candidate_b",
        6,
        used_validation_meetings,
    )
)

validation_sample_parts.append(
    select_spread_sample(
        p
…
```

### Cell 133

Matched: `manual`, `external`, `racecard`

```text
# Select a compact high-value subset for external racecard validation.

priority_validation_keys = [
    ("2015-04-12", "Oaklawn Park (USA)"),
    ("2015-01-04", "Abu Dhabi (UAE)"),
    ("2015-03-29", "Auteuil (FR)"),
    ("2019-10-27", "Wexford (IRE)"),
    ("2023-10-29", "Aintree"),
    ("2016-07-07", "Newbury"),
    ("2021-05-27", "Carlisle"),
    ("2023-07-26", "Sandown"),
    ("2015-01-02", "Valparaiso Sporting Club (CHI)"),
    ("2020-08-15", "San Sebastian (SPA)"),
    ("2024-06-26", "Happy Valley (HK)"),
    ("2017-03-19", "Nakayama (JPN)"),
    ("2018-04-28", "Santa Anita (USA)"),
    ("2022-08-07", "Del Mar (USA)"),
]

priority_validation_sample = (
    manual_validation_sample
    .assign(
        meeting_key=lambda frame: list(
            zip(frame["date"], frame["course"])
        )
    )
    .loc[
        lambda frame: frame["meeting_key"].isin(
            priority_validation_keys
        )
    ]
    .drop(columns="meeting_key")
    .copy()
)

priority_validation_sample[
    "expected_branch_from_current_evidence"
] = priority_validation_sample[
    "validation_category"
].map(
    {
        "stable_profile_candidate_a": "candidate_a",
        "stable_profile_candidate_b": "candidate_b",
        "summer_profile_mismatch": "candidate_b_expected",
        "dst_edge": "candidate_b_expected",
        "single_race_meeting": "manual_check",
        "international_sanity_check": "manual_check",
    }
)

priority_validation_sample.sort_values(
    ["validation_category", "date", "course"]
).reset_index(drop=True)
           validation_category        date               course  \
0                     dst_edge  2015-03-29         Auteuil (FR)   
1                     dst_edge  2019-10-27        Wexford (IRE)   
2                     dst_edge  2023-10-29
…
```

### Cell 134

Matched: `external`, `racecard`, `official result`

```text
### External validation pilot

A focused external validation pilot tested reconstructed branches against
historical racecards and official results.

The checked meetings included:

* DST-transition meetings in France, Ireland and Great Britain;
* summer evening meetings in Great Britain;
* Japanese afternoon racing;
* Hong Kong evening racing;
* United States racing displayed through the UK-facing source clock.

Eight checked meetings across six jurisdictions matched the reconstructed
course-local branch:

* Auteuil, 29 March 2015 — candidate B, 14:00–17:55;
* Wexford, 27 October 2019 — candidate B, 12:50–16:20;
* Aintree, 29 October 2023 — candidate B, 12:50–16:20;
* Nakayama, 19 March 2017 — candidate A, 15:45;
* Happy Valley, 26 June 2024 — candidate A, 18:40–22:50;
* Newbury, 7 July 2016 — candidate B, 18:00–21:10;
* Carlisle, 27 May 2021 — candidate B, 17:30–20:50;
* Santa Anita, 28 April 2018 — candidate B, 14:35–15:07.

The pilot therefore produced eight correct branch selections from eight checks.
It supports the UK-facing clock interpretation, the historical timezone
conversion, the course-local feasibility rule, and the treatment of summer
evening racing as a seasonal limitation of the current post-boundary profiles.
```

## `notebooks/12_course_timezone_resolution_completed_archive.ipynb`

### Cell 0

Matched: `manual`, `manually`

```text
# Notebook 12 — Course Location and Timezone Mapping

## Purpose

Build and validate the reusable physical racecourse-location reference required by Notebook 11.

This notebook will:

- inspect the existing 394-row course-location scaffold and validator;
- design a cached, rate-limited geocoding workflow;
- retain every query and raw provider response for audit;
- validate candidate venues against course identity and jurisdiction;
- derive historical IANA timezones from accepted coordinates;
- classify every course as validated, manually reviewed, or explicitly unresolved;
- save the completed reference to `data/reference/course_locations.csv`.

No source racing data will be modified, and no bulk API requests will be made until the environment, provider requirements, cache design, and validation rules have been inspected.
```

### Cell 3

Matched: `manual`, `validation_status`, `nominatim`

```text
import pandas as pd

course_locations_path = repo_root / "data/reference/course_locations.csv"
course_locations = pd.read_csv(course_locations_path)

print("Rows:", len(course_locations))
print("Columns:", len(course_locations.columns))
print("\nColumn names:")
print(course_locations.columns.tolist())

display(course_locations.head(3))

Rows: 394
Columns: 22

Column names:
['candidate_course_label', 'candidate_jurisdiction', 'physical_venue_name', 'locality', 'region', 'country', 'latitude', 'longitude', 'iana_timezone', 'location_evidence', 'location_validation_status', 'raw_course_labels', 'provisional_races', 'meeting_dates', 'earliest_date', 'latest_date', 'has_reusable_location', 'address_line', 'suburb', 'postcode', 'provider_place_id', 'provider_display_name']

  candidate_course_label candidate_jurisdiction  \
0               La Plata              Argentina   
1                Palermo              Argentina   
2             San Isidro              Argentina   

              physical_venue_name      locality  \
0           Hipódromo de La Plata      La Plata   
1  Hipódromo Argentino de Palermo  Buenos Aires   
2                             NaN           NaN   

                            region    country   latitude  longitude  \
0                     Buenos Aires  Argentina -34.901267 -57.943804   
1  Autonomous City of Buenos Aires  Argentina -34.566398 -58.425727   
2                              NaN        NaN        NaN        NaN   

                    iana_timezone  \
0  America/Argentina/Buenos_Aires   
1  America/Argentina/Buenos_Aires   
2                             NaN   

                                   location_evidence  ... provisional_races  \
0  Nominatim manual selection from query 'Hipódro...  ...                37   
1  Nominatim manual
…
```

### Cell 4

Matched: `validation_status`

```text
course_locations_module_path = (
    repo_root / "src/inside_rails/course_locations.py"
)

print(course_locations_module_path.read_text())

"""Load and validate the curated course-location reference."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd

IDENTITY_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
]

REQUIRED_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "latitude",
    "longitude",
    "iana_timezone",
    "location_evidence",
    "location_validation_status",
]

def load_course_locations(path: str | Path) -> pd.DataFrame:
    """Load and validate the curated course-location reference."""

    reference_path = Path(path)
    frame = pd.read_csv(reference_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            "Course-location reference is missing required columns: "
            + ", ".join(missing_columns)
        )

    duplicate_mask = frame.duplicated(
        subset=IDENTITY_COLUMNS,
        keep=False,
    )

    if duplicate_mask.any():
        duplicates = (
            frame.loc[duplicate_mask, IDENTITY_COLUMNS]
            .drop_duplicates()
            .to_dict("records")
        )
        raise ValueError(
            f"Duplicate candidate course identities found: {duplicates}"
        )

    assigned_timezone_mask = frame["iana_timezone"].notna()

    invalid_timezones = []

    for timezone_name in sorted(
        frame.loc[assigned_timezone_mask, "iana_timezone"].unique()
    ):
        try:
…
```

### Cell 5

Matched: `external`

```text
from importlib.util import find_spec

packages = [
    "geopy",
    "timezonefinder",
    "requests",
    "requests_cache",
]

print("Package availability:")
for package in packages:
    status = "installed" if find_spec(package) else "missing"
    print(f"{status:9} | {package}")

print("\nExisting cache-like paths:")
cache_like_paths = sorted(
    path.relative_to(repo_root)
    for path in repo_root.rglob("*")
    if "cache" in path.name.lower()
    and ".git" not in path.parts
)

if cache_like_paths:
    for path in cache_like_paths[:50]:
        print(path)
else:
    print("None found")

Package availability:
installed | geopy
installed | timezonefinder
installed | requests
missing   | requests_cache

Existing cache-like paths:
.venv/lib/python3.12/site-packages/IPython/__pycache__
.venv/lib/python3.12/site-packages/IPython/core/__pycache__
.venv/lib/python3.12/site-packages/IPython/core/magics/__pycache__
.venv/lib/python3.12/site-packages/IPython/extensions/__pycache__
.venv/lib/python3.12/site-packages/IPython/extensions/deduperreload/__pycache__
.venv/lib/python3.12/site-packages/IPython/external/__pycache__
.venv/lib/python3.12/site-packages/IPython/lib/__pycache__
.venv/lib/python3.12/site-packages/IPython/sphinxext/__pycache__
.venv/lib/python3.12/site-packages/IPython/sphinxext/tests/__pycache__
.venv/lib/python3.12/site-packages/IPython/terminal/__pycache__
.venv/lib/python3.12/site-packages/IPython/terminal/pt_inputhooks/__pycache__
.venv/lib/python3.12/site-packages/IPython/terminal/shortcuts/__pycache__
.venv/lib/python3.12/site-packages/IPython/testing/__pycache__
.venv/lib/python3.12/site-packages/IPython/testing/plugin/__pycache__
.venv/lib/python3.12/site-packages/IPython/utils/__pycache__
.venv/lib/python3.12/site-packages/PIL/__pycache__
.venv/lib
…
```

### Cell 10

Matched: `external`

```text
# Inspect the candidate jurisdictions before designing geocoding queries.
#
# This cell does not modify any files or send any external requests.
#
# It shows:
# - how many candidate course identities belong to each jurisdiction;
# - representative course labels from each jurisdiction;
# - whether jurisdiction values are already consistent enough to map to
#   geocoder country names and country codes.

jurisdiction_profile = (
    course_locations
    .groupby("candidate_jurisdiction", dropna=False)
    .agg(
        candidate_courses=("candidate_course_label", "size"),
        sample_courses=(
            "candidate_course_label",
            lambda values: ", ".join(sorted(values.astype(str))[:5]),
        ),
    )
    .reset_index()
    .sort_values(
        ["candidate_courses", "candidate_jurisdiction"],
        ascending=[False, True],
    )
)

print("Distinct jurisdictions:", len(jurisdiction_profile))
display(jurisdiction_profile)

Distinct jurisdictions: 36

   candidate_jurisdiction  candidate_courses  \
10                 France                 73   
12          Great Britain                 65   
34          United States                 56   
1               Australia                 51   
16                Ireland                 27   
18                  Japan                 21   
11                Germany                 17   
20            New Zealand                 14   
27           South Africa                  9   
17                  Italy                  7   
31            Switzerland                  5   
33   United Arab Emirates                  5   
5                  Canada                  4   
0               Argentina                  3   
3                 Belgium                  3   
4                  Brazil                  3   
6
…
```

### Cell 11

Matched: `external`

```text
# Identify course labels that occur in more than one jurisdiction.
#
# These collisions are especially important for geocoding because a query
# based only on the course name could return a geographically valid but
# completely wrong racing venue.
#
# This cell is read-only and sends no external requests.

duplicate_label_mask = course_locations.duplicated(
    subset=["candidate_course_label"],
    keep=False,
)

cross_jurisdiction_labels = (
    course_locations.loc[
        duplicate_label_mask,
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "raw_course_labels",
            "provisional_races",
        ],
    ]
    .sort_values(
        ["candidate_course_label", "candidate_jurisdiction"]
    )
    .reset_index(drop=True)
)

print(
    "Course labels appearing in multiple jurisdictions:",
    cross_jurisdiction_labels["candidate_course_label"].nunique(),
)

display(cross_jurisdiction_labels)

Course labels appearing in multiple jurisdictions: 3

  candidate_course_label candidate_jurisdiction raw_course_labels  \
0                  Ascot              Australia       Ascot (AUS)   
1                  Ascot          Great Britain             Ascot   
2              Newcastle              Australia   Newcastle (AUS)   
3              Newcastle          Great Britain         Newcastle   
4                Sandown              Australia     Sandown (AUS)   
5                Sandown          Great Britain           Sandown   

   provisional_races  
0                204  
1               1734  
2                 77  
3                930  
4                 65  
5               1631
```

### Cell 13

Matched: `external`

```text
# Define the country and territory controls used by the geocoding workflow.
#
# Each candidate jurisdiction maps to:
# - query_country: text included in the search query;
# - country_codes: ISO alpha-2 codes acceptable in returned results.
#
# The mapping is deliberately explicit so provider naming differences do not
# silently weaken country validation. This cell sends no external requests.

JURISDICTION_GEOCODING_RULES = {
    "Argentina": {
        "query_country": "Argentina",
        "country_codes": {"ar"},
    },
    "Australia": {
        "query_country": "Australia",
        "country_codes": {"au"},
    },
    "Bahrain": {
        "query_country": "Bahrain",
        "country_codes": {"bh"},
    },
    "Belgium": {
        "query_country": "Belgium",
        "country_codes": {"be"},
    },
    "Brazil": {
        "query_country": "Brazil",
        "country_codes": {"br"},
    },
    "Canada": {
        "query_country": "Canada",
        "country_codes": {"ca"},
    },
    "Chile": {
        "query_country": "Chile",
        "country_codes": {"cl"},
    },
    "China": {
        "query_country": "China",
        "country_codes": {"cn"},
    },
    "Czech Republic": {
        "query_country": "Czechia",
        "country_codes": {"cz"},
    },
    "Denmark": {
        "query_country": "Denmark",
        "country_codes": {"dk"},
    },
    "France": {
        "query_country": "France",
        "country_codes": {"fr"},
    },
    "Germany": {
        "query_country": "Germany",
        "country_codes": {"de"},
    },
    "Great Britain": {
        "query_country": "United Kingdom",
        "country_codes": {"gb"},
    },
    "Guernsey": {
        "query_country": "Guernsey",
        "country_codes": {"gg"},
    },
    "Hong Kong": {
        "query_country": "Hong Kon
…
```

### Cell 18

Matched: `external`, `nominatim`

```text
# Create deterministic identifiers for geocoding requests and raw responses.
#
# A SHA-256 digest is derived from the provider, full candidate identity,
# exact query, country filter and result limit.
#
# Using request content rather than row position means:
# - restarting the notebook produces the same identifier;
# - the same request can be detected before contacting the provider;
# - course-label collisions remain separate;
# - changing the query or request parameters creates a new cache record.
#
# This cell does not create files or send external requests.

import hashlib
import json

def build_geocoding_cache_record_id(
    *,
    provider,
    candidate_course_label,
    candidate_jurisdiction,
    exact_query,
    country_code_filter,
    result_limit,
):
    """Return a stable identifier for one exact geocoding request."""

    request_identity = {
        "provider": provider,
        "candidate_course_label": candidate_course_label,
        "candidate_jurisdiction": candidate_jurisdiction,
        "exact_query": exact_query,
        "country_code_filter": country_code_filter,
        "result_limit": result_limit,
    }

    canonical_json = json.dumps(
        request_identity,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

test_record_ids = []

for _, row in geocoding_candidates.head(3).iterrows():
    country_code = next(
        iter(
            JURISDICTION_GEOCODING_RULES[
                row["candidate_jurisdiction"]
            ]["country_codes"]
        )
    )

    test_record_ids.append(
        build_geocoding_cache_record_id(
            provider="nominatim",
            candidate_course_label=row["candidate_course_label"
…
```

### Cell 19

Matched: `external`

```text
## Reuse of accepted course locations

Racecourses are treated as stable physical venues.

Before preparing or sending any geocoding request, the workflow must check the
existing course-location reference.

A candidate course identity requires no further geocoding when it already has:

- an accepted validation status;
- a physical venue name;
- valid latitude and longitude;
- a valid IANA timezone.

The accepted reference takes precedence over the request cache. This prevents
repeat lookups even when the original provider query or response cache is not
available.

A new external request is permitted only when the course is:

- unassigned;
- unresolved;
- ambiguous;
- previously rejected without an accepted alternative;
- explicitly marked for refresh because the stored evidence is defective.

The cache prevents duplicate requests. The completed course-location reference
prevents unnecessary requests permanently.
```

### Cell 20

Matched: `manual`, `manually`, `external`, `validation_status`

```text
# Classify whether each course identity already has a reusable accepted location.
#
# A course is considered complete only when it has:
# - an accepted validation status;
# - a nonblank physical venue name;
# - valid numeric coordinates;
# - a nonblank IANA timezone.
#
# This cell is read-only. It does not create cache files, modify the reference,
# or send any external requests.

ACCEPTED_LOCATION_STATUSES = {
    "automatically_validated",
    "manually_validated",
    "validated",
}

def nonblank_text(series):
    """Return True where values contain non-whitespace text."""

    return (
        series.notna()
        & series.astype(str).str.strip().ne("")
    )

latitude_values = pd.to_numeric(
    course_locations["latitude"],
    errors="coerce",
)
longitude_values = pd.to_numeric(
    course_locations["longitude"],
    errors="coerce",
)

course_locations["has_reusable_location"] = (
    course_locations["location_validation_status"].isin(
        ACCEPTED_LOCATION_STATUSES
    )
    & nonblank_text(course_locations["physical_venue_name"])
    & latitude_values.between(-90, 90)
    & longitude_values.between(-180, 180)
    & nonblank_text(course_locations["iana_timezone"])
)

print(
    "Reusable accepted locations:",
    int(course_locations["has_reusable_location"].sum()),
)
print(
    "Course identities requiring processing:",
    int((~course_locations["has_reusable_location"]).sum()),
)

display(
    course_locations[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "location_validation_status",
            "has_reusable_location",
        ]
    ]
    .groupby(
        ["location_validation_status", "has_reusable_location"],
        dropna=False,
    )
    .size()
    .rename("candidate_courses")
    .reset_in
…
```

### Cell 21

Matched: `https://`, `external`, `nominatim`

```text
# Define the Nominatim provider configuration.
#
# This cell sends no external requests.
#
# The public Nominatim service requires:
# - an application-specific User-Agent;
# - a maximum rate of one request per second;
# - local caching of all responses;
# - single-threaded use for a small one-off batch.
#
# The repository URL identifies the application without exposing personal data.
# Country codes will be supplied as hard result filters, while multiple results
# are retained so that the first match is never accepted automatically.

NOMINATIM_PROVIDER = "nominatim"
NOMINATIM_DOMAIN = "nominatim.openstreetmap.org"
NOMINATIM_USER_AGENT = (
    "inside-rails-course-location-mapping/"
    "0.1 "
    "(https://github.com/rjmac22/inside-rails-horse-racing)"
)

NOMINATIM_RESULT_LIMIT = 5
NOMINATIM_MINIMUM_DELAY_SECONDS = 1.1
NOMINATIM_LANGUAGE = "en"

NOMINATIM_REQUEST_OPTIONS = {
    "addressdetails": True,
    "extratags": True,
    "namedetails": True,
    "exactly_one": False,
    "limit": NOMINATIM_RESULT_LIMIT,
    "language": NOMINATIM_LANGUAGE,
}

print("Provider:", NOMINATIM_PROVIDER)
print("Domain:", NOMINATIM_DOMAIN)
print("User-Agent:", NOMINATIM_USER_AGENT)
print("Result limit:", NOMINATIM_RESULT_LIMIT)
print("Minimum delay:", NOMINATIM_MINIMUM_DELAY_SECONDS)
print("Request options:", NOMINATIM_REQUEST_OPTIONS)

Provider: nominatim
Domain: nominatim.openstreetmap.org
User-Agent: inside-rails-course-location-mapping/0.1 (https://github.com/rjmac22/inside-rails-horse-racing)
Result limit: 5
Minimum delay: 1.1
Request options: {'addressdetails': True, 'extratags': True, 'namedetails': True, 'exactly_one': False, 'limit': 5, 'language': 'en'}
```

### Cell 24

Matched: `external`

```text
# Load existing geocoding cache files when they are present.
#
# This cell is read-only:
# - it does not create either cache file;
# - it does not modify the course-location reference;
# - it does not send any external requests.
#
# An absent manifest is represented by an empty DataFrame with the agreed
# schema. This lets later cells use the same logic on both first and resumed
# notebook runs.

if geocoding_cache_path.exists():
    geocoding_cache = pd.read_csv(geocoding_cache_path)
else:
    geocoding_cache = pd.DataFrame(
        columns=GEOCODING_CACHE_COLUMNS
    )

if geocoding_raw_responses_path.exists():
    raw_response_line_count = sum(
        1
        for line in geocoding_raw_responses_path.open(
            "r",
            encoding="utf-8",
        )
        if line.strip()
    )
else:
    raw_response_line_count = 0

missing_cache_columns = [
    column
    for column in GEOCODING_CACHE_COLUMNS
    if column not in geocoding_cache.columns
]

print("Manifest rows:", len(geocoding_cache))
print("Raw-response records:", raw_response_line_count)
print("Missing manifest columns:", missing_cache_columns)

Manifest rows: 76
Raw-response records: 76
Missing manifest columns: []
```

### Cell 25

Matched: `nominatim`

```text
# Create the geocoding client and enforce the provider delay centrally.
#
# This cell does not contact Nominatim.
#
# All later lookups must use `rate_limited_geocode` rather than calling the
# geocoder directly. This ensures that every request observes the configured
# minimum delay and remains single-threaded.
#
# Raw result dictionaries are requested so that provider names, addresses,
# place identifiers, classifications and coordinates can be preserved in the
# audit cache.

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

nominatim_geocoder = Nominatim(
    user_agent=NOMINATIM_USER_AGENT,
    domain=NOMINATIM_DOMAIN,
    timeout=20,
)

rate_limited_geocode = RateLimiter(
    nominatim_geocoder.geocode,
    min_delay_seconds=NOMINATIM_MINIMUM_DELAY_SECONDS,
    max_retries=1,
    error_wait_seconds=5,
    swallow_exceptions=False,
)

print("Geocoder class:", type(nominatim_geocoder).__name__)
print("Provider domain:", nominatim_geocoder.domain)
print("Minimum delay:", NOMINATIM_MINIMUM_DELAY_SECONDS)
print("Client created without sending a request.")

Geocoder class: Nominatim
Provider domain: nominatim.openstreetmap.org
Minimum delay: 1.1
Client created without sending a request.
```

### Cell 26

Matched: `external`, `nominatim`

```text
# Prepare one controlled geocoding test without sending the request.
#
# La Plata is used because it is the first scaffold identity and should have a
# clearly identifiable racing venue. The cell:
# - retrieves the full candidate identity;
# - applies the jurisdiction country-code rule;
# - generates the deterministic cache identifier;
# - checks the completed reference and request cache;
# - prints the exact request that the next cell would send.
#
# No external request is made and no file is created or modified.

test_candidate = geocoding_candidates.iloc[0]

test_jurisdiction = test_candidate["candidate_jurisdiction"]
test_country_code = sorted(
    JURISDICTION_GEOCODING_RULES[test_jurisdiction]["country_codes"]
)[0]

test_cache_record_id = build_geocoding_cache_record_id(
    provider=NOMINATIM_PROVIDER,
    candidate_course_label=test_candidate["candidate_course_label"],
    candidate_jurisdiction=test_jurisdiction,
    exact_query=test_candidate["geocoding_query"],
    country_code_filter=test_country_code,
    result_limit=NOMINATIM_RESULT_LIMIT,
)

test_reference_row = course_locations.loc[
    (course_locations["candidate_course_label"]
     == test_candidate["candidate_course_label"])
    & (course_locations["candidate_jurisdiction"]
       == test_jurisdiction)
].iloc[0]

test_is_reusable = bool(
    test_reference_row["has_reusable_location"]
)

test_is_cached = bool(
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(test_cache_record_id)
    .any()
)

print("Candidate:", test_candidate["candidate_course_label"])
print("Jurisdiction:", test_jurisdiction)
print("Exact query:", test_candidate["geocoding_query"])
print("Country-code filter:", test_country_code)
print("Result limit:", NOMINATIM_RESULT_LIMIT)
print("Cache record ID:", test_cache_re
…
```

### Cell 28

Matched: `external`, `nominatim`

```text
# Send one controlled Nominatim test request for La Plata and cache the
# complete outcome, or reuse the same request when it is already cached.
#
# Exact request:
# - La Plata racecourse, Argentina
#
# This is the first, generic English-language query in the controlled
# La Plata test. It tests whether the provider can identify the racecourse
# directly from the source course label, a generic venue term and country.
#
# The request uses:
# - the rate-limited Nominatim client created earlier;
# - the Argentina country-code filter;
# - the fixed result limit defined for this notebook.
#
# Before sending anything, the cell builds the deterministic cache record ID
# from the provider and exact request parameters. This means the same request
# has the same identity on every notebook run.
#
# When the exact request is already present in the manifest:
# - no external request is sent;
# - the saved request status and result count are reused;
# - neither cache file receives a duplicate record.
#
# When the request is not already cached, the cell writes to:
# - data/cache/course_geocoding_cache.csv
# - data/cache/course_geocoding_responses.jsonl
#
# The manifest stores the searchable request summary and later review fields.
# The JSONL file preserves the complete raw provider response, including
# successful zero-result responses and request errors.
#
# This cell does not:
# - select a returned result;
# - infer that the first result is correct;
# - derive a timezone;
# - update data/reference/course_locations.csv.

generic_query = test_candidate["geocoding_query"]

# Build the stable identity for this exact provider request. Any material
# change to the query, country filter or result limit creates a different
# cache record rather than overwriting this request.
generic_cache_r
…
```

### Cell 29

Matched: `manual`, `manually`

```text
## Fallback query strategy

A successful API request with no results does not make the course unresolved.
It means only that the exact query formulation failed.

For each unresolved course, geocoding may proceed through an ordered set of
distinct cached queries:

1. `<course label> racecourse, <country>`
2. `<course label>, <country>`
3. a jurisdiction-appropriate racing-venue term, such as:
   - `Hipódromo` for Spanish- and Portuguese-speaking jurisdictions;
   - `Hippodrome` for relevant French-language searches;
   - `Rennbahn` for German-language searches;
4. a manually supplied known venue name or alias where automated formulations
   remain unsuccessful.

Every formulation is a separate cached request with its own deterministic
identifier and raw response.

An empty result is never overwritten or silently retried. The next fallback
query is attempted only because it is materially different from the cached
failed formulation.
```

### Cell 30

Matched: `external`

```text
# Define ordered venue-search terms for each jurisdiction.
#
# The first term remains the generic English "racecourse".
# Additional terms reflect common local naming conventions and are used only
# when an earlier exact query has already been cached with no usable result.
#
# This cell does not send external requests or modify any files.

JURISDICTION_VENUE_TERMS = {
    "Argentina": ["racecourse", "hipódromo", "hipodromo"],
    "Australia": ["racecourse"],
    "Bahrain": ["racecourse"],
    "Belgium": ["racecourse", "hippodrome"],
    "Brazil": ["racecourse", "hipódromo", "hipodromo"],
    "Canada": ["racecourse", "racetrack"],
    "Chile": ["racecourse", "hipódromo", "hipodromo"],
    "China": ["racecourse"],
    "Czech Republic": ["racecourse", "závodiště"],
    "Denmark": ["racecourse", "galopbane"],
    "France": ["racecourse", "hippodrome"],
    "Germany": ["racecourse", "rennbahn"],
    "Great Britain": ["racecourse"],
    "Guernsey": ["racecourse"],
    "Hong Kong": ["racecourse"],
    "Hungary": ["racecourse", "versenypálya"],
    "Ireland": ["racecourse"],
    "Italy": ["racecourse", "ippodromo"],
    "Japan": ["racecourse"],
    "Jersey": ["racecourse"],
    "New Zealand": ["racecourse"],
    "Norway": ["racecourse", "galoppbane"],
    "Peru": ["racecourse", "hipódromo", "hipodromo"],
    "Poland": ["racecourse", "tor wyścigów konnych"],
    "Qatar": ["racecourse"],
    "Saudi Arabia": ["racecourse"],
    "Singapore": ["racecourse"],
    "South Africa": ["racecourse"],
    "South Korea": ["racecourse"],
    "Spain": ["racecourse", "hipódromo", "hipodromo"],
    "Sweden": ["racecourse", "galoppbana"],
    "Switzerland": ["racecourse", "hippodrome", "rennbahn"],
    "Turkey": ["racecourse", "hipodromu"],
    "United Arab Emirates": ["racecourse"],
    "United
…
```

### Cell 31

Matched: `external`, `nominatim`

```text
# Generate the ordered fallback queries for the La Plata test identity.
#
# This cell sends no external requests and modifies no files.
#
# Each materially different query receives its own deterministic cache ID.
# A query is eligible only when:
# - the exact request is not already cached; and
# - the course does not already have a reusable accepted location.
#
# `not test_is_reusable` is calculated once because it is a single Python
# boolean, while `~already_cached` operates element-by-element on a Series.

test_venue_terms = JURISDICTION_VENUE_TERMS[test_jurisdiction]

test_fallback_queries = pd.DataFrame(
    {
        "venue_term": test_venue_terms,
        "exact_query": [
            (
                f"{test_candidate['candidate_course_label']} "
                f"{venue_term}, "
                f"{test_candidate['query_country']}"
            )
            for venue_term in test_venue_terms
        ],
    }
)

test_fallback_queries["cache_record_id"] = (
    test_fallback_queries.apply(
        lambda row: build_geocoding_cache_record_id(
            provider=NOMINATIM_PROVIDER,
            candidate_course_label=(
                test_candidate["candidate_course_label"]
            ),
            candidate_jurisdiction=test_jurisdiction,
            exact_query=row["exact_query"],
            country_code_filter=test_country_code,
            result_limit=NOMINATIM_RESULT_LIMIT,
        ),
        axis=1,
    )
)

cached_record_ids = set(
    geocoding_cache["cache_record_id"].astype(str)
)

test_fallback_queries["already_cached"] = (
    test_fallback_queries["cache_record_id"].isin(
        cached_record_ids
    )
)

reference_requires_lookup = not test_is_reusable

test_fallback_queries["eligible_for_request"] = (
    ~test_fallback_queries["already_cached"
…
```

### Cell 32

Matched: `nominatim`

```text
# Send or reuse the accented local-term request for La Plata.
#
# This cell is safe to rerun:
# - when the exact request exists in the cache, it reuses the saved outcome;
# - otherwise it sends exactly one rate-limited request and caches it.
#
# It does not select or accept a course location.

fallback_request = (
    test_fallback_queries.loc[
        test_fallback_queries["venue_term"].eq("hipódromo")
    ]
    .iloc[0]
)

fallback_query = fallback_request["exact_query"]
fallback_cache_record_id = fallback_request["cache_record_id"]

fallback_cache_mask = (
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(fallback_cache_record_id)
)

fallback_is_cached = bool(fallback_cache_mask.any())

if fallback_is_cached:
    cached_fallback_row = geocoding_cache.loc[
        fallback_cache_mask
    ].iloc[0]

    request_status = cached_fallback_row["request_status"]

    cached_result_count = pd.to_numeric(
        cached_fallback_row["result_count"],
        errors="coerce",
    )

    result_count = (
        0
        if pd.isna(cached_result_count)
        else int(cached_result_count)
    )

    print("Request action: reused cached result")

else:
    requested_at_utc = datetime.now(timezone.utc).isoformat()
    raw_response_record_id = fallback_cache_record_id

    request_status = "pending"
    result_count = 0
    raw_results = []
    error_type = None
    error_message = None

    try:
        locations = rate_limited_geocode(
            fallback_query,
            country_codes=test_country_code,
            **NOMINATIM_REQUEST_OPTIONS,
        )

        if locations is None:
            locations = []

        raw_results = [
            location.raw
            for location in locations
        ]

        result_count = len(raw_results)
        reque
…
```

### Cell 33

Matched: `external`

```text
# Read the cached raw response for the successful La Plata fallback and present
# the returned alternatives in a compact review table.
#
# This cell is read-only:
# - it sends no external request;
# - it does not modify either cache file;
# - it does not update course_locations.csv.
#
# The table preserves the provider result order and shows the fields needed to
# judge whether a result is genuinely the racecourse rather than merely a place
# elsewhere in La Plata.

fallback_raw_record = None

with geocoding_raw_responses_path.open(
    "r",
    encoding="utf-8",
) as raw_file:
    for line in raw_file:
        if not line.strip():
            continue

        record = json.loads(line)

        if (
            record.get("raw_response_record_id")
            == fallback_cache_record_id
        ):
            fallback_raw_record = record
            break

if fallback_raw_record is None:
    raise RuntimeError(
        "The cached raw response for the fallback request was not found."
    )

review_rows = []

for result_index, result in enumerate(
    fallback_raw_record["results"]
):
    address = result.get("address", {})

    review_rows.append(
        {
            "result_index": result_index,
            "display_name": result.get("display_name"),
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
            "osm_type": result.get("osm_type"),
            "osm_id": result.get("osm_id"),
            "category": result.get("category"),
            "type": result.get("type"),
            "name": result.get("name"),
            "city_or_locality": (
                address.get("city")
                or address.get("town")
                or address.get("municipality")
                or address.get("village")
            ),
…
```

### Cell 34

Matched: `external`

```text
# Mark the successful fallback request as reviewed with no usable result.
#
# This cell updates only the geocoding manifest:
# - no external request is sent;
# - the raw provider response remains unchanged;
# - no course location is accepted into course_locations.csv.
#
# The request itself succeeded, but every returned candidate is geographically
# or semantically wrong for the La Plata racecourse. The review therefore
# records that a more precise venue name or alias is required.

fallback_manifest_mask = (
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(fallback_cache_record_id)
)

matching_manifest_rows = int(
    fallback_manifest_mask.sum()
)

if matching_manifest_rows != 1:
    raise RuntimeError(
        "Expected exactly one manifest row for the fallback request, "
        f"found {matching_manifest_rows}."
    )

geocoding_cache.loc[
    fallback_manifest_mask,
    "review_status",
] = "reviewed_no_usable_result"

geocoding_cache.loc[
    fallback_manifest_mask,
    "review_notes",
] = (
    "All three returned results rejected: one residential feature in "
    "Gualeguaychu and two residential features in Mar del Plata. "
    "None is the La Plata racecourse or a racing venue in La Plata."
)

geocoding_cache.to_csv(
    geocoding_cache_path,
    index=False,
)

display(
    geocoding_cache.loc[
        fallback_manifest_mask,
        [
            "exact_query",
            "request_status",
            "result_count",
            "review_status",
            "review_notes",
        ],
    ]
)
                     exact_query        request_status  result_count  \
1  La Plata hipódromo, Argentina  success_with_results             3   

               review_status  \
1  reviewed_no_usable_result   

                                        revi
…
```

### Cell 35

Matched: `manual`, `nominatim`

```text
# Prepare a precise manual-alias query for the unresolved La Plata course.
#
# The generic and local-term formulations have already failed to identify the
# venue. This query uses the full local venue-name pattern instead:
# "Hipódromo de La Plata, Argentina".
#
# This cell:
# - generates a separate deterministic cache identifier;
# - confirms that the exact query is not already cached;
# - does not contact Nominatim;
# - does not modify either cache file or course_locations.csv.

manual_alias_query = "Hipódromo de La Plata, Argentina"

manual_alias_cache_record_id = build_geocoding_cache_record_id(
    provider=NOMINATIM_PROVIDER,
    candidate_course_label=test_candidate[
        "candidate_course_label"
    ],
    candidate_jurisdiction=test_jurisdiction,
    exact_query=manual_alias_query,
    country_code_filter=test_country_code,
    result_limit=NOMINATIM_RESULT_LIMIT,
)

manual_alias_is_cached = bool(
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(manual_alias_cache_record_id)
    .any()
)

manual_alias_is_eligible = (
    not test_is_reusable
    and not manual_alias_is_cached
)

print("Manual alias query:", manual_alias_query)
print("Cache record ID:", manual_alias_cache_record_id)
print("Exact request already cached:", manual_alias_is_cached)
print("Eligible for request:", manual_alias_is_eligible)

Manual alias query: Hipódromo de La Plata, Argentina
Cache record ID: f29ac5baf793331c1b0ec642ecdc882d744cd7daf87369ecd20a8ddf98ef08c7
Exact request already cached: True
Eligible for request: False
```

### Cell 36

Matched: `manual`, `external`, `nominatim`

```text
# Send one precise manual-alias Nominatim request for Hipódromo de La Plata,
# or reuse the same request when it is already present in the cache.
#
# Exact request:
# - Hipódromo de La Plata, Argentina
#
# This is the third query in the controlled La Plata test. It uses the known
# full venue name after:
# - the generic English query returned no results;
# - the broader local-term query returned unrelated residential alternatives.
#
# This is a manual alias, not an automatically inferred course name. The
# reason for using it must therefore remain visible in the notebook and in the
# later location-evidence text.
#
# The request uses:
# - the rate-limited Nominatim client created earlier;
# - the Argentina country-code filter;
# - the fixed result limit defined for this notebook.
#
# The deterministic cache record ID was prepared earlier from the exact
# provider request. It prevents duplicate external requests on later runs.
#
# When the exact request is already present in the manifest:
# - no external request is sent;
# - the saved request status and result count are reused;
# - neither cache file receives a duplicate record.
#
# When the request is not already cached, the cell writes to:
# - data/cache/course_geocoding_cache.csv
# - data/cache/course_geocoding_responses.jsonl
#
# The manifest stores the searchable request summary and later review fields.
# The JSONL file preserves the complete raw provider response, including
# successful zero-result responses and request errors.
#
# This cell does not:
# - automatically select result index 0 or any other result;
# - assume that an exact text match is geographically correct;
# - derive a timezone;
# - update data/reference/course_locations.csv.
#
# Candidate comparison and the manual selection of result index 1 occur
…
```

### Cell 37

Matched: `manual`, `external`

```text
# Read and display the cached alternatives returned for the precise manual alias.
#
# This cell is read-only:
# - it sends no external request;
# - it does not modify either cache file;
# - it does not update course_locations.csv.
#
# The provider order is retained so we can review the exact venue identity,
# coordinates, classification, locality and country before accepting anything.

manual_alias_raw_record = None

with geocoding_raw_responses_path.open(
    "r",
    encoding="utf-8",
) as raw_file:
    for line in raw_file:
        if not line.strip():
            continue

        record = json.loads(line)

        if (
            record.get("raw_response_record_id")
            == manual_alias_cache_record_id
        ):
            manual_alias_raw_record = record
            break

if manual_alias_raw_record is None:
    raise RuntimeError(
        "The cached raw response for the manual-alias request was not found."
    )

manual_alias_review_rows = []

for result_index, result in enumerate(
    manual_alias_raw_record["results"]
):
    address = result.get("address", {})

    manual_alias_review_rows.append(
        {
            "result_index": result_index,
            "display_name": result.get("display_name"),
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
            "osm_type": result.get("osm_type"),
            "osm_id": result.get("osm_id"),
            "category": result.get("category"),
            "type": result.get("type"),
            "name": result.get("name"),
            "city_or_locality": (
                address.get("city")
                or address.get("town")
                or address.get("municipality")
                or address.get("village")
            ),
            "state_or_region": (
…
```

### Cell 38

Matched: `manual`, `external`

```text
# Derive and validate the IANA timezone for the genuine La Plata result.
#
# Result index 1 has been identified as the plausible course because:
# - its name is Hipódromo de La Plata;
# - its locality is La Plata;
# - its region is Buenos Aires;
# - its provider type is sports_centre.
#
# This cell is read-only:
# - it sends no external request;
# - it does not modify the cache;
# - it does not update course_locations.csv.
#
# The timezone is derived from the selected coordinates and then validated
# through Python's ZoneInfo implementation.

from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

selected_result_index = 1
selected_result = manual_alias_raw_record["results"][
    selected_result_index
]

selected_latitude = float(selected_result["lat"])
selected_longitude = float(selected_result["lon"])

timezone_finder = TimezoneFinder()

selected_iana_timezone = timezone_finder.timezone_at(
    lat=selected_latitude,
    lng=selected_longitude,
)

timezone_validation_error = None

try:
    ZoneInfo(selected_iana_timezone)
    timezone_is_valid = True
except Exception as exc:
    timezone_is_valid = False
    timezone_validation_error = str(exc)

selected_address = selected_result.get("address", {})

print("Selected result index:", selected_result_index)
print("Selected name:", selected_result.get("name"))
print("Locality:", selected_address.get("city"))
print("Region:", selected_address.get("state"))
print("Latitude:", selected_latitude)
print("Longitude:", selected_longitude)
print("Derived IANA timezone:", selected_iana_timezone)
print("Timezone validates:", timezone_is_valid)

if timezone_validation_error:
    print("Validation error:", timezone_validation_error)

Selected result index: 1
Selected name: Hipódromo de La Plata
Locality: La Plata
Regi
…
```

### Cell 39

Matched: `manual`, `manually`

```text
# Record the reviewed La Plata selection in the geocoding manifest.
#
# This cell updates only course_geocoding_cache.csv.
#
# It records:
# - the selected provider result;
# - provider identity and display name;
# - coordinates;
# - country, venue-type and name-match assessments;
# - the completed manual-review status.
#
# It does not modify course_locations.csv. The selected location and derived
# timezone will be validated together in a separate proposed-reference row
# before the final reference is changed.

manual_alias_manifest_mask = (
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(manual_alias_cache_record_id)
)

matching_manifest_rows = int(
    manual_alias_manifest_mask.sum()
)

if matching_manifest_rows != 1:
    raise RuntimeError(
        "Expected exactly one manifest row for the manual-alias request, "
        f"found {matching_manifest_rows}."
    )

selected_provider_place_id = (
    f"{selected_result.get('osm_type')}:"
    f"{selected_result.get('osm_id')}"
)

selected_display_name = selected_result.get(
    "display_name"
)

selected_country_code = (
    selected_address.get("country_code", "")
    .strip()
    .lower()
)

country_code_match = (
    selected_country_code == test_country_code
)

venue_type_match = (
    selected_result.get("type")
    in {"sports_centre", "raceway", "stadium", "track"}
)

name_match_status = (
    "exact_local_venue_name"
    if selected_result.get("name")
    == "Hipódromo de La Plata"
    else "non_exact"
)

geocoding_cache.loc[
    manual_alias_manifest_mask,
    "selected_result_index",
] = selected_result_index

geocoding_cache.loc[
    manual_alias_manifest_mask,
    "selected_provider_place_id",
] = selected_provider_place_id

geocoding_cache.loc[
    manual_alias_manifest_mask,
    "selected_
…
```

### Cell 40

Matched: `manual`, `manually`, `external`, `validation_status`, `nominatim`

```text
# Build and validate the proposed course-location reference row for La Plata.
#
# This cell is read-only:
# - it does not send an external request;
# - it does not modify the geocoding cache;
# - it does not write to course_locations.csv.
#
# Several currently blank reference columns were loaded by pandas as float64.
# Before assigning text values, this cell explicitly converts the relevant
# text columns to object dtype. Coordinate columns are explicitly numeric.

test_reference_mask = (
    course_locations["candidate_course_label"]
    .eq(test_candidate["candidate_course_label"])
    & course_locations["candidate_jurisdiction"]
    .eq(test_jurisdiction)
)

matching_reference_rows = int(test_reference_mask.sum())

if matching_reference_rows != 1:
    raise RuntimeError(
        "Expected exactly one La Plata reference row, "
        f"found {matching_reference_rows}."
    )

proposed_course_location = (
    course_locations.loc[test_reference_mask]
    .copy()
)

text_location_columns = [
    "physical_venue_name",
    "locality",
    "region",
    "country",
    "iana_timezone",
    "location_evidence",
    "location_validation_status",
]

for column in text_location_columns:
    proposed_course_location[column] = (
        proposed_course_location[column].astype("object")
    )

for column in ["latitude", "longitude"]:
    proposed_course_location[column] = pd.to_numeric(
        proposed_course_location[column],
        errors="coerce",
    )

proposed_course_location["physical_venue_name"] = (
    selected_result.get("name")
)
proposed_course_location["locality"] = (
    selected_address.get("city")
)
proposed_course_location["region"] = (
    selected_address.get("state")
)
proposed_course_location["country"] = (
    selected_address.get("country")
)
proposed_c
…
```

### Cell 41

Matched: `manual`, `manually`, `validation_status`

```text
# Permanently update the La Plata course-location reference.
#
# This cell writes to:
# - data/reference/course_locations.csv
#
# It changes only the existing identity:
# - candidate_course_label = La Plata
# - candidate_jurisdiction = Argentina
#
# All other rows and source-coverage fields remain unchanged.
#
# The repository uses a `src` package layout. Because this notebook is running
# directly rather than through an installed package, the repository's `src`
# directory is added to sys.path before importing the project validator.
#
# The cell is safe to rerun:
# - one changed row means the validated La Plata reference is written;
# - zero changed rows means the same validated reference is already saved;
# - more than one changed row indicates an unexpected reference change.
#
# After writing, or reusing the existing saved row, the cell reloads the CSV
# through the normal project reference loader so duplicate identities,
# coordinate ranges and IANA timezone values are validated.

import sys

src_path = repo_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from inside_rails.course_locations import load_course_locations

reference_before_write = course_locations.copy()
updated_course_locations = course_locations.copy()

# Blank text columns may currently have float dtype because every value was
# initially missing. Convert the location fields before assigning text.
for column in text_location_columns:
    updated_course_locations[column] = (
        updated_course_locations[column].astype("object")
    )

# Copy only the proposed location fields into the existing La Plata row.
for column in proposed_course_location.columns:
    updated_course_locations.loc[
        test_reference_mask,
        column,
    ] = proposed_course_loca
…
```

### Cell 42

Matched: `manual`, `manually`, `external`, `validation_status`

```text
# Recalculate reusable-location status after saving the La Plata reference.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# The expected result is:
# - La Plata is now reusable;
# - one course is reusable overall;
# - 393 courses still require location work.

accepted_location_statuses = {
    "automatically_validated",
    "manually_validated",
    "validated",
}

course_locations["has_reusable_location"] = (
    course_locations["location_validation_status"]
    .isin(accepted_location_statuses)
    & course_locations["physical_venue_name"].notna()
    & pd.to_numeric(
        course_locations["latitude"],
        errors="coerce",
    ).between(-90, 90)
    & pd.to_numeric(
        course_locations["longitude"],
        errors="coerce",
    ).between(-180, 180)
    & course_locations["iana_timezone"].notna()
)

la_plata_reusable = course_locations.loc[
    course_locations["candidate_course_label"].eq("La Plata")
    & course_locations["candidate_jurisdiction"].eq("Argentina"),
    [
        "candidate_course_label",
        "candidate_jurisdiction",
        "physical_venue_name",
        "iana_timezone",
        "location_validation_status",
        "has_reusable_location",
    ],
]

print(
    "Reusable course locations:",
    int(course_locations["has_reusable_location"].sum()),
)
print(
    "Courses still requiring location work:",
    int((~course_locations["has_reusable_location"]).sum()),
)

display(la_plata_reusable)

Reusable course locations: 36
Courses still requiring location work: 358

  candidate_course_label candidate_jurisdiction    physical_venue_name  \
0               La Plata              Argentina  Hipódromo de La Plata
…
```

### Cell 43

Matched: `manual`, `manually`, `external`

```text
# Summarise the complete La Plata geocoding audit trail.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# It confirms that the course has:
# - one generic query with no results;
# - one local-term query whose results were reviewed and rejected;
# - one precise alias query with a manually selected result;
# - exactly one reusable final reference row.

la_plata_cache_history = (
    geocoding_cache.loc[
        geocoding_cache["candidate_course_label"].eq("La Plata")
        & geocoding_cache["candidate_jurisdiction"].eq("Argentina"),
        [
            "requested_at_utc",
            "exact_query",
            "request_status",
            "result_count",
            "selected_result_index",
            "selected_provider_place_id",
            "review_status",
            "review_notes",
        ],
    ]
    .sort_values("requested_at_utc")
    .reset_index(drop=True)
)

la_plata_raw_record_count = 0

with geocoding_raw_responses_path.open(
    "r",
    encoding="utf-8",
) as raw_file:
    for line in raw_file:
        if not line.strip():
            continue

        record = json.loads(line)

        if (
            record.get("candidate_course_label") == "La Plata"
            and record.get("candidate_jurisdiction") == "Argentina"
        ):
            la_plata_raw_record_count += 1

audit_checks = {
    "three manifest attempts": len(la_plata_cache_history) == 3,
    "three raw responses": la_plata_raw_record_count == 3,
    "one selected attempt": (
        la_plata_cache_history["review_status"]
        .eq("manually_selected")
        .sum()
        == 1
    ),
    "one reusable reference": (
        course_locations.loc[
            course_locations[
…
```

### Cell 44

Matched: `external`

```text
# Close successful zero-result requests as reviewed.
#
# This cell updates only course_geocoding_cache.csv.
#
# It is safe to rerun:
# - only rows still marked "not_reviewed" are changed;
# - already closed rows remain unchanged;
# - zero matching rows is a valid resumed-notebook outcome.
#
# A successful request with zero alternatives needs no candidate review.
# The timestamp remains in the displayed columns so the final table can be
# sorted without raising a KeyError.
#
# No external request is sent and course_locations.csv is not modified.

zero_result_mask = (
    geocoding_cache["request_status"].eq("success_no_results")
    & geocoding_cache["result_count"].fillna(0).eq(0)
    & geocoding_cache["review_status"].eq("not_reviewed")
)

zero_result_rows_to_close = int(zero_result_mask.sum())

if zero_result_rows_to_close > 0:
    geocoding_cache.loc[
        zero_result_mask,
        "review_status",
    ] = "reviewed_no_results"

    geocoding_cache.loc[
        zero_result_mask,
        "review_notes",
    ] = (
        "Request completed successfully but returned no provider results."
    )

    geocoding_cache.to_csv(
        geocoding_cache_path,
        index=False,
    )

zero_result_review = (
    geocoding_cache.loc[
        geocoding_cache["request_status"].eq("success_no_results"),
        [
            "requested_at_utc",
            "candidate_course_label",
            "candidate_jurisdiction",
            "exact_query",
            "request_status",
            "result_count",
            "review_status",
            "review_notes",
        ],
    ]
    .sort_values("requested_at_utc")
    .reset_index(drop=True)
)

unclosed_zero_result_rows = int(
    (
        zero_result_review["result_count"].fillna(0).eq(0)
        & ~zero_result_review["review_s
…
```

### Cell 45

Matched: `manual`, `manually`, `external`

```text
# Verify the zero-result review update.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# The timestamp is included before sorting so the audit history displays in
# request order.

la_plata_review_history = geocoding_cache.loc[
    geocoding_cache["candidate_course_label"].eq("La Plata")
    & geocoding_cache["candidate_jurisdiction"].eq("Argentina"),
    [
        "requested_at_utc",
        "exact_query",
        "request_status",
        "result_count",
        "review_status",
        "review_notes",
    ],
].sort_values("requested_at_utc")

display(la_plata_review_history)

print(
    "Zero-result request closed:",
    la_plata_review_history.loc[
        la_plata_review_history["request_status"].eq(
            "success_no_results"
        ),
        "review_status",
    ].eq("reviewed_no_results").all(),
)
                   requested_at_utc                       exact_query  \
0  2026-07-26T13:11:34.250680+00:00    La Plata racecourse, Argentina   
1  2026-07-26T13:15:32.809207+00:00     La Plata hipódromo, Argentina   
2  2026-07-26T13:18:33.361871+00:00  Hipódromo de La Plata, Argentina   
5  2026-07-27T00:34:10.167834+00:00     La Plata hipodromo, Argentina   

         request_status  result_count              review_status  \
0    success_no_results             0        reviewed_no_results   
1  success_with_results             3  reviewed_no_usable_result   
2  success_with_results             2          manually_selected   
5  success_with_results             4               not_reviewed   

                                        review_notes  
0  Request completed successfully but returned no...  
1  All three returned results rejected: one resid..
…
```

### Cell 46

Matched: `manual`, `manually`, `external`

```text
## Reusable per-course processing rule

Each unresolved course is processed through the following controlled sequence:

1. Skip the course when the accepted reference already contains a reusable
   physical venue, valid coordinates and valid IANA timezone.

2. Generate an ordered set of materially different exact queries:
   - generic English venue term;
   - jurisdiction-specific venue terms;
   - known full venue names or aliases when required.

3. Before every request, calculate the deterministic cache identifier and skip
   the external call when the exact request already exists in the manifest.

4. Send no more than one request at a time through the rate-limited client.

5. Cache every outcome:
   - successful response with alternatives;
   - successful response with no alternatives;
   - provider or network error.

6. Review returned alternatives before selection. A result is not accepted
   merely because it is first or because the request returned matches.

7. Record one terminal review outcome:
   - `reviewed_no_results`;
   - `reviewed_no_usable_result`;
   - `manually_selected`;
   - a later automated-selection status only where explicit validation rules
     support it.

8. Derive the IANA timezone from the selected coordinates and validate it with
   `ZoneInfo`.

9. Build and validate a proposed reference row before updating
   `course_locations.csv`.

10. Once accepted, later notebook runs reuse the reference and issue no
    further geocoding requests for that course unless an explicit refresh or
    historical-location review is required.
```

### Cell 47

Matched: `external`

```text
# Inspect the next unresolved course-location identities.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# It preserves the existing reference order and displays the first 20 courses
# that do not yet have a reusable validated location. Available source-coverage
# columns are included so the next controlled test can be chosen deliberately
# rather than simply taking an arbitrary course.

identity_columns = [
    "candidate_course_label",
    "candidate_jurisdiction",
]

possible_coverage_columns = [
    "provisional_races",
    "runner_records",
    "first_date",
    "last_date",
]

available_coverage_columns = [
    column
    for column in possible_coverage_columns
    if column in course_locations.columns
]

unresolved_course_locations = (
    course_locations.loc[
        ~course_locations["has_reusable_location"],
        identity_columns + available_coverage_columns,
    ]
    .reset_index()
    .rename(columns={"index": "reference_row_index"})
)

print(
    "Unresolved course identities:",
    len(unresolved_course_locations),
)
print(
    "Available coverage columns:",
    available_coverage_columns,
)

display(
    unresolved_course_locations.head(20)
)

Unresolved course identities: 358
Available coverage columns: ['provisional_races']

    reference_row_index candidate_course_label candidate_jurisdiction  \
0                     2             San Isidro              Argentina   
1                     3                 Albury              Australia   
2                     4          Alice springs              Australia   
3                     5               Armidale              Australia   
4                     6                  Ascot              A
…
```

### Cell 48

Matched: `manual`, `manually`, `external`, `validation_status`

```text
# Diagnose why the saved La Plata row is being classified as unresolved.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# It displays the saved fields used by the reusable-location rule and
# recalculates each component separately.

la_plata_diagnostic = course_locations.loc[
    course_locations["candidate_course_label"].eq("La Plata")
    & course_locations["candidate_jurisdiction"].eq("Argentina")
].copy()

la_plata_diagnostic["status_is_accepted"] = (
    la_plata_diagnostic["location_validation_status"]
    .isin(accepted_location_statuses)
)

la_plata_diagnostic["venue_is_present"] = (
    la_plata_diagnostic["physical_venue_name"].notna()
)

la_plata_diagnostic["latitude_is_valid"] = pd.to_numeric(
    la_plata_diagnostic["latitude"],
    errors="coerce",
).between(-90, 90)

la_plata_diagnostic["longitude_is_valid"] = pd.to_numeric(
    la_plata_diagnostic["longitude"],
    errors="coerce",
).between(-180, 180)

la_plata_diagnostic["timezone_is_present"] = (
    la_plata_diagnostic["iana_timezone"].notna()
)

la_plata_diagnostic["recalculated_reusable_location"] = (
    la_plata_diagnostic["status_is_accepted"]
    & la_plata_diagnostic["venue_is_present"]
    & la_plata_diagnostic["latitude_is_valid"]
    & la_plata_diagnostic["longitude_is_valid"]
    & la_plata_diagnostic["timezone_is_present"]
)

display(
    la_plata_diagnostic[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "physical_venue_name",
            "latitude",
            "longitude",
            "iana_timezone",
            "location_validation_status",
            "has_reusable_location",
            "status_is_accepted",
            "venue
…
```

### Cell 49

Matched: `manual`, `manually`, `external`, `validation_status`

```text
# Recalculate reusable-location status for the complete reference.
#
# This cell is read-only with respect to project files:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# `has_reusable_location` is a derived notebook field rather than a persisted
# source field. It must therefore be recalculated whenever course_locations is
# reloaded from disk.
#
# A course is reusable only when it has:
# - an accepted validation status;
# - a nonblank physical venue name;
# - valid latitude and longitude;
# - a nonblank IANA timezone.

accepted_location_statuses = {
    "automatically_validated",
    "manually_validated",
    "validated",
}

course_locations["has_reusable_location"] = (
    course_locations["location_validation_status"]
    .isin(accepted_location_statuses)
    & course_locations["physical_venue_name"].notna()
    & pd.to_numeric(
        course_locations["latitude"],
        errors="coerce",
    ).between(-90, 90)
    & pd.to_numeric(
        course_locations["longitude"],
        errors="coerce",
    ).between(-180, 180)
    & course_locations["iana_timezone"].notna()
)

print(
    "Reusable course locations:",
    int(course_locations["has_reusable_location"].sum()),
)
print(
    "Courses still requiring location work:",
    int((~course_locations["has_reusable_location"]).sum()),
)

display(
    course_locations.loc[
        course_locations["candidate_course_label"].eq("La Plata")
        & course_locations["candidate_jurisdiction"].eq("Argentina"),
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "location_validation_status",
            "has_reusable_location",
        ],
    ]
)

Reusable course locations: 36
Courses still requirin
…
```

### Cell 50

Matched: `external`

```text
# Identify the existing jurisdiction and venue-rule objects.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify project files;
# - it does not alter the geocoding cache.
#
# It lists currently defined notebook variables whose names suggest they hold
# jurisdiction mappings, country-code rules or venue-term rules.
#
# `globals()` is copied to a list first because directly iterating over the
# live dictionary can raise "dictionary changed size during iteration" in a
# notebook environment.

rule_name_keywords = (
    "jurisdiction",
    "venue",
    "country",
    "term",
)

possible_rule_objects = []

for variable_name, variable_value in list(globals().items()):
    if not any(
        keyword in variable_name.lower()
        for keyword in rule_name_keywords
    ):
        continue

    possible_rule_objects.append(
        {
            "variable_name": variable_name,
            "object_type": type(variable_value).__name__,
            "shape": (
                str(variable_value.shape)
                if hasattr(variable_value, "shape")
                else pd.NA
            ),
            "columns": (
                ", ".join(map(str, variable_value.columns))
                if isinstance(variable_value, pd.DataFrame)
                else pd.NA
            ),
        }
    )

possible_rule_objects = (
    pd.DataFrame(possible_rule_objects)
    .sort_values("variable_name")
    .reset_index(drop=True)
)

display(possible_rule_objects)
                   variable_name object_type    shape  \
0   JURISDICTION_GEOCODING_RULES        dict      NaN   
1       JURISDICTION_VENUE_TERMS        dict      NaN   
2                   country_code         str      NaN   
3             country_code_match        bool      NaN   
4      cross_ju
…
```

### Cell 51

Matched: `external`

```text
# Inspect the Argentina geocoding and venue-term rules.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify project files;
# - it does not alter either geocoding cache.
#
# It displays the exact dictionary values already defined earlier in the
# notebook so the Palermo request-planning cell can use their real structure
# rather than assuming column names or dataframe layouts.

argentina_geocoding_rule = (
    JURISDICTION_GEOCODING_RULES.get("Argentina")
)

argentina_venue_terms = (
    JURISDICTION_VENUE_TERMS.get("Argentina")
)

print("Argentina geocoding rule:")
display(argentina_geocoding_rule)

print()
print("Argentina venue terms:")
display(argentina_venue_terms)

print()
print(
    "Geocoding-rule object type:",
    type(argentina_geocoding_rule).__name__,
)
print(
    "Venue-terms object type:",
    type(argentina_venue_terms).__name__,
)

Argentina geocoding rule:

{'query_country': 'Argentina', 'country_codes': {'ar'}}

Argentina venue terms:

['racecourse', 'hipódromo', 'hipodromo']

Geocoding-rule object type: dict
Venue-terms object type: list
```

### Cell 52

Matched: `external`, `nominatim`

```text
# Prepare the next controlled course test: Palermo, Argentina.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# It selects Palermo from the unresolved reference and shows:
# - the existing jurisdiction geocoding rule;
# - the ordered generic and Argentina-specific venue queries;
# - the deterministic cache identity of every exact request;
# - whether any request has already been cached.
#
# The purpose is to inspect the planned requests before deciding whether an
# external provider call is necessary.

next_course_label = "Palermo"
next_jurisdiction = "Argentina"

next_reference_mask = (
    course_locations["candidate_course_label"].eq(next_course_label)
    & course_locations["candidate_jurisdiction"].eq(next_jurisdiction)
)

next_reference_rows = course_locations.loc[
    next_reference_mask
]

if len(next_reference_rows) != 1:
    raise RuntimeError(
        "Expected exactly one Palermo, Argentina reference row, "
        f"found {len(next_reference_rows)}."
    )

next_course = next_reference_rows.iloc[0]

# Read the jurisdiction rules using the dictionary structures defined earlier
# in this notebook. The geocoding rule supplies the provider-facing country
# name and the set of accepted country-code filters.
next_geocoding_rule = (
    JURISDICTION_GEOCODING_RULES[next_jurisdiction]
)

next_country_name = next_geocoding_rule[
    "query_country"
]

next_country_codes = sorted(
    next_geocoding_rule["country_codes"]
)

if len(next_country_codes) != 1:
    raise RuntimeError(
        "Expected exactly one Argentina country-code filter, "
        f"found {next_country_codes}."
    )

next_country_code = next_country_codes[0]

# Preserve the venue-term order d
…
```

### Cell 53

Matched: `external`, `nominatim`

```text
# Send or reuse the generic Palermo geocoding request.
#
# Exact request:
# - Palermo racecourse, Argentina
#
# This is the first query in the Palermo sequence. It tests the generic
# English venue term before trying the Argentina-specific alternatives.
#
# The cell is safe to rerun:
# - if the exact request is already cached, no external request is made;
# - otherwise one rate-limited request is sent and the complete outcome is
#   written to both geocoding cache files.
#
# It writes only when the request is new:
# - data/cache/course_geocoding_cache.csv
# - data/cache/course_geocoding_responses.jsonl
#
# This cell does not select a result, derive a timezone, or update the final
# course-location reference.

palermo_generic_request = (
    next_candidate_queries.loc[
        next_candidate_queries["query_order"].eq(1)
    ]
    .iloc[0]
)

palermo_generic_query = (
    palermo_generic_request["exact_query"]
)

palermo_generic_cache_record_id = (
    palermo_generic_request["cache_record_id"]
)

palermo_generic_cache_mask = (
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(palermo_generic_cache_record_id)
)

palermo_generic_is_cached = bool(
    palermo_generic_cache_mask.any()
)

if palermo_generic_is_cached:
    # Reuse the previously saved provider outcome.
    cached_palermo_generic_row = geocoding_cache.loc[
        palermo_generic_cache_mask
    ].iloc[0]

    request_status = cached_palermo_generic_row[
        "request_status"
    ]

    cached_result_count = pd.to_numeric(
        cached_palermo_generic_row["result_count"],
        errors="coerce",
    )

    result_count = (
        0
        if pd.isna(cached_result_count)
        else int(cached_result_count)
    )

    print("Request action: reused cached result")

else:
    requested_at_utc
…
```

### Cell 54

Matched: `external`, `nominatim`

```text
# Send or reuse the accented local-term Palermo geocoding request.
#
# Exact request:
# - Palermo hipódromo, Argentina
#
# This is the second query in the Palermo sequence. It uses the
# Argentina-specific accented venue term after the generic English query
# returned no results.
#
# The cell is safe to rerun:
# - if the exact request is already cached, no external request is made;
# - otherwise one rate-limited request is sent and the complete outcome is
#   written to both geocoding cache files.
#
# It writes only when the request is new:
# - data/cache/course_geocoding_cache.csv
# - data/cache/course_geocoding_responses.jsonl
#
# This cell does not select a result, derive a timezone, or update the final
# course-location reference.

palermo_accented_request = (
    next_candidate_queries.loc[
        next_candidate_queries["query_order"].eq(2)
    ]
    .iloc[0]
)

palermo_accented_query = (
    palermo_accented_request["exact_query"]
)

palermo_accented_cache_record_id = (
    palermo_accented_request["cache_record_id"]
)

palermo_accented_cache_mask = (
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(palermo_accented_cache_record_id)
)

palermo_accented_is_cached = bool(
    palermo_accented_cache_mask.any()
)

if palermo_accented_is_cached:
    # Reuse the previously saved provider outcome.
    cached_palermo_accented_row = geocoding_cache.loc[
        palermo_accented_cache_mask
    ].iloc[0]

    request_status = cached_palermo_accented_row[
        "request_status"
    ]

    cached_result_count = pd.to_numeric(
        cached_palermo_accented_row["result_count"],
        errors="coerce",
    )

    result_count = (
        0
        if pd.isna(cached_result_count)
        else int(cached_result_count)
    )

    print("Request action: reused ca
…
```

### Cell 55

Matched: `external`

```text
# Inspect the cached results from the accented Palermo query.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache file;
# - it does not write to course_locations.csv.
#
# It retrieves the complete raw response associated with:
# - Palermo hipódromo, Argentina
#
# The results are flattened into review fields so we can determine whether
# any candidate is genuinely the Palermo racecourse rather than accepting the
# first provider result automatically.

palermo_accented_raw_record = None

with geocoding_raw_responses_path.open(
    "r",
    encoding="utf-8",
) as raw_file:
    for line in raw_file:
        if not line.strip():
            continue

        raw_record = json.loads(line)

        if (
            raw_record.get("cache_record_id")
            == palermo_accented_cache_record_id
        ):
            palermo_accented_raw_record = raw_record
            break

if palermo_accented_raw_record is None:
    raise RuntimeError(
        "The cached raw response for the accented Palermo query "
        "could not be found."
    )

palermo_accented_results = (
    palermo_accented_raw_record.get("results", [])
)

palermo_accented_review_rows = []

for result_index, result in enumerate(
    palermo_accented_results
):
    address = result.get("address") or {}

    provider_place_id = (
        f"{result.get('osm_type')}:{result.get('osm_id')}"
        if result.get("osm_type") is not None
        and result.get("osm_id") is not None
        else pd.NA
    )

    palermo_accented_review_rows.append(
        {
            "result_index": result_index,
            "provider_place_id": provider_place_id,
            "display_name": result.get("display_name"),
            "name": result.get("name"),
            "category": resu
…
```

### Cell 56

Matched: `manual`, `manually`, `external`

```text
# Record the manual review decision for the Palermo requests.
#
# Decisions:
# - "Palermo racecourse, Argentina" returned no results and is marked as a
#   reviewed no-result request.
# - "Palermo hipódromo, Argentina" returned three alternatives.
# - result index 0 is selected because it is the physical racecourse:
#   Hipódromo Argentino de Palermo.
#
# The nearby bicycle-rental and casino results are not selected.
#
# This cell:
# - makes no external request;
# - updates the existing manifest rows only;
# - writes the updated manifest to the geocoding cache CSV;
# - does not yet update course_locations.csv or derive the timezone.
#
# It is safe to rerun because it assigns the same review values each time.

palermo_selected_result_index = 0

if palermo_selected_result_index >= len(
    palermo_accented_results
):
    raise RuntimeError(
        "The selected Palermo result index is outside the "
        "available cached results."
    )

palermo_selected_result = (
    palermo_accented_results[
        palermo_selected_result_index
    ]
)

palermo_selected_address = (
    palermo_selected_result.get("address") or {}
)

palermo_selected_provider_place_id = (
    f"{palermo_selected_result.get('osm_type')}:"
    f"{palermo_selected_result.get('osm_id')}"
)

# Mark the generic English request as reviewed with no results.
geocoding_cache.loc[
    geocoding_cache["cache_record_id"]
    .astype(str)
    .eq(palermo_generic_cache_record_id),
    [
        "review_status",
        "review_notes",
    ],
] = [
    "reviewed_no_results",
    (
        "Generic English venue query returned no provider "
        "results; the jurisdiction-specific query was used."
    ),
]

# Record the manually selected racecourse result from the accented query.
geocoding_cache.loc[
    geocodi
…
```

### Cell 57

Matched: `external`

```text
# Identify the existing timezone-related notebook objects.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify project files;
# - it does not alter either geocoding cache.
#
# A frozen copy of globals is used because directly iterating over the live
# notebook namespace can raise "dictionary changed size during iteration".

timezone_name_keywords = (
    "timezone",
    "time_zone",
    "tz",
)

possible_timezone_objects = []

for variable_name, variable_value in list(globals().items()):
    if not any(
        keyword in variable_name.lower()
        for keyword in timezone_name_keywords
    ):
        continue

    possible_timezone_objects.append(
        {
            "variable_name": variable_name,
            "object_type": type(variable_value).__name__,
            "shape": (
                str(variable_value.shape)
                if hasattr(variable_value, "shape")
                else pd.NA
            ),
        }
    )

possible_timezone_objects = (
    pd.DataFrame(possible_timezone_objects)
    .sort_values("variable_name")
    .reset_index(drop=True)
)

display(possible_timezone_objects)
               variable_name     object_type shape
0             TimezoneFinder         ABCMeta  <NA>
1  possible_timezone_objects            list  <NA>
2     selected_iana_timezone             str  <NA>
3              test_timezone             str  <NA>
4                   timezone            type  <NA>
5            timezone_finder  TimezoneFinder  <NA>
6          timezone_is_valid            bool  <NA>
7     timezone_name_keywords           tuple  <NA>
8  timezone_validation_error        NoneType  <NA>
9             timezonefinder          module  <NA>
```

### Cell 58

Matched: `external`

```text
# Derive and validate the IANA timezone for the selected Palermo racecourse.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache;
# - it does not write to course_locations.csv.
#
# It uses the already selected Palermo coordinates and the existing
# TimezoneFinder instance created earlier in the notebook.

palermo_selected_latitude = float(
    palermo_selected_result["lat"]
)

palermo_selected_longitude = float(
    palermo_selected_result["lon"]
)

palermo_iana_timezone = timezone_finder.timezone_at(
    lat=palermo_selected_latitude,
    lng=palermo_selected_longitude,
)

if palermo_iana_timezone is None:
    raise RuntimeError(
        "No IANA timezone could be derived for the selected "
        "Palermo coordinates."
    )

# Validate that Python's timezone database recognises the returned name.
try:
    ZoneInfo(palermo_iana_timezone)
    palermo_timezone_is_valid = True
except Exception as exc:
    palermo_timezone_is_valid = False
    raise RuntimeError(
        "The derived Palermo timezone is not a valid IANA timezone: "
        f"{palermo_iana_timezone}"
    ) from exc

print("Selected venue: Hipódromo Argentino de Palermo")
print("Latitude:", palermo_selected_latitude)
print("Longitude:", palermo_selected_longitude)
print("Derived IANA timezone:", palermo_iana_timezone)
print("Timezone valid:", palermo_timezone_is_valid)

Selected venue: Hipódromo Argentino de Palermo
Latitude: -34.5663978
Longitude: -58.4257272
Derived IANA timezone: America/Argentina/Buenos_Aires
Timezone valid: True
```

### Cell 59

Matched: `manual`, `manually`, `external`, `validation_status`, `nominatim`

```text
# Inspect the permanent course-location reference schema.
#
# This is the final structural inspection before the reusable batch function.
# It:
# - makes no external requests;
# - writes no files;
# - shows the actual column names;
# - shows the existing validated La Plata row as the model for Palermo and
#   subsequent automated writes.

print("course_locations columns:")
print(list(course_locations.columns))

print()
print("Existing validated La Plata row:")

display(
    course_locations.loc[
        course_locations["candidate_course_label"].eq("La Plata")
        & course_locations["candidate_jurisdiction"].eq("Argentina")
    ].T
)

course_locations columns:
['candidate_course_label', 'candidate_jurisdiction', 'physical_venue_name', 'locality', 'region', 'country', 'latitude', 'longitude', 'iana_timezone', 'location_evidence', 'location_validation_status', 'raw_course_labels', 'provisional_races', 'meeting_dates', 'earliest_date', 'latest_date', 'has_reusable_location', 'address_line', 'suburb', 'postcode', 'provider_place_id', 'provider_display_name']

Existing validated La Plata row:

                                                                            0
candidate_course_label                                               La Plata
candidate_jurisdiction                                              Argentina
physical_venue_name                                     Hipódromo de La Plata
locality                                                             La Plata
region                                                           Buenos Aires
country                                                             Argentina
latitude                                                           -34.901267
longitude
…
```

### Cell 60

Matched: `manual`, `manually`, `validation_status`, `nominatim`

```text
# Write the validated Palermo location to the permanent course reference.
#
# This cell:
# - updates exactly one existing Palermo, Argentina row;
# - preserves the source-derived race and date fields already present;
# - writes the completed reference back to course_locations.csv;
# - recalculates the derived reusable-location flag;
# - validates the saved values after writing.
#
# It is safe to rerun:
# - the same validated values are assigned each time;
# - no duplicate row is created;
# - a second run should report zero changed rows.

palermo_reference_mask = (
    course_locations["candidate_course_label"].eq("Palermo")
    & course_locations["candidate_jurisdiction"].eq("Argentina")
)

if int(palermo_reference_mask.sum()) != 1:
    raise RuntimeError(
        "Expected exactly one Palermo, Argentina reference row, "
        f"found {int(palermo_reference_mask.sum())}."
    )

palermo_reference_values = {
    "physical_venue_name": "Hipódromo Argentino de Palermo",
    "locality": "Buenos Aires",
    "region": "Autonomous City of Buenos Aires",
    "country": "Argentina",
    "latitude": palermo_selected_latitude,
    "longitude": palermo_selected_longitude,
    "iana_timezone": palermo_iana_timezone,
    "location_evidence": (
        "Nominatim manual selection from query "
        "'Palermo hipódromo, Argentina'; selected result index 0, "
        "Hipódromo Argentino de Palermo."
    ),
    "location_validation_status": "manually_validated",
}

palermo_before = (
    course_locations.loc[
        palermo_reference_mask,
        list(palermo_reference_values),
    ]
    .copy()
)

for column_name, column_value in palermo_reference_values.items():
    course_locations.loc[
        palermo_reference_mask,
        column_name,
    ] = column_value

# Recalculate the
…
```

### Cell 61

Matched: `external`, `nominatim`

```text
# Inspect the complete address fields returned for the selected Palermo venue.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify either cache;
# - it does not write to course_locations.csv.
#
# It shows every address component supplied by Nominatim so we can decide
# which fields belong in the permanent course-location reference.

palermo_selected_address = (
    palermo_selected_result.get("address") or {}
)

palermo_address_components = pd.DataFrame(
    [
        {
            "address_component": key,
            "value": value,
        }
        for key, value in palermo_selected_address.items()
    ]
).sort_values("address_component")

print("Provider display name:")
print(
    palermo_selected_result.get("display_name")
)

print()
print("Provider place ID:")
print(
    palermo_selected_provider_place_id
)

print()
print("Returned address components:")

display(palermo_address_components)

Provider display name:
Hipódromo Argentino de Palermo, 4101, Avenida Del Libertador, Palermo Pacífico, Palermo, Buenos Aires, Comuna 14, Autonomous City of Buenos Aires, C1426BSD, Argentina

Provider place ID:
way:18772836

Returned address components:

   address_component                            value
8     ISO3166-2-lvl4                             AR-C
5               city                     Buenos Aires
10           country                        Argentina
11      country_code                               ar
1       house_number                             4101
0            leisure   Hipódromo Argentino de Palermo
3      neighbourhood                 Palermo Pacífico
9           postcode                         C1426BSD
2               road           Avenida Del Libertador
7              state  Autonomous City of Buenos Aires
6     s
…
```

### Cell 62

Matched: `manual`, `manually`, `validation_status`

```text
# Add practical address and provider-lineage fields to the permanent
# course-location reference, then backfill the validated Palermo record.
#
# New permanent fields:
# - address_line: street address without repeating locality/region/country;
# - suburb: useful local district within a city;
# - postcode: venue postcode where supplied;
# - provider_place_id: stable provider object identifier;
# - provider_display_name: complete provider-returned address for audit.
#
# This cell:
# - adds missing columns without removing existing data;
# - fills the existing Palermo row from the selected provider result;
# - writes course_locations.csv;
# - reloads and validates the saved values.
#
# It is safe to rerun:
# - existing columns are reused;
# - the same Palermo values are assigned;
# - no duplicate course row is created.

location_enrichment_columns = [
    "address_line",
    "suburb",
    "postcode",
    "provider_place_id",
    "provider_display_name",
]

for column_name in location_enrichment_columns:
    if column_name not in course_locations.columns:
        course_locations[column_name] = pd.NA

palermo_reference_mask = (
    course_locations["candidate_course_label"].eq("Palermo")
    & course_locations["candidate_jurisdiction"].eq("Argentina")
)

if int(palermo_reference_mask.sum()) != 1:
    raise RuntimeError(
        "Expected exactly one Palermo, Argentina reference row, "
        f"found {int(palermo_reference_mask.sum())}."
    )

palermo_enrichment_values = {
    "address_line": "4101 Avenida Del Libertador",
    "suburb": "Palermo",
    "postcode": "C1426BSD",
    "provider_place_id": palermo_selected_provider_place_id,
    "provider_display_name": (
        palermo_selected_result.get("display_name")
    ),
}

palermo_enrichment_before = (
    course_locati
…
```

### Cell 63

Matched: `manual`, `external`

```text
## Production geocoding pipeline

The exploratory La Plata and Palermo work above established the safe operating rules:

- preserve every external request in a deterministic cache;
- remove source-only suffixes such as `(AW)` from provider queries;
- accept only named racecourse venue objects in the expected jurisdiction;
- reject roads, neighbourhoods, accommodation, casinos, parking and nearby facilities;
- write only unambiguous high-confidence matches;
- export every unresolved or ambiguous course to a manual-review queue.

The cells below replace the development batches with one rerunnable production workflow. A complete rerun reuses cached requests and does not duplicate cache records.
```

### Cell 64

Matched: `manual`, `nominatim`

```text
# Define the permanent reference enrichment columns and processing controls.
#
# Set RUN_FULL_GEOCODING to False when validating notebook structure without
# contacting Nominatim. With it set to True, every unresolved course is
# processed. Cached exact requests are reused, so later reruns are much faster.

LOCATION_ENRICHMENT_COLUMNS = [
    "address_line",
    "suburb",
    "postcode",
    "provider_place_id",
    "provider_display_name",
]

for column_name in LOCATION_ENRICHMENT_COLUMNS:
    if column_name not in course_locations.columns:
        course_locations[column_name] = pd.NA

RUN_FULL_GEOCODING = True
MAX_UNRESOLVED_COURSES = None  # Use an integer for a deliberately smaller run.

manual_review_path = course_locations_path.with_name(
    "course_location_manual_review.csv"
)
geocoding_run_summary_path = course_locations_path.with_name(
    "course_location_geocoding_run_summary.csv"
)

print("Production controls prepared.")
print("Run full geocoding:", RUN_FULL_GEOCODING)
print("Course limit:", MAX_UNRESOLVED_COURSES)

Production controls prepared.
Run full geocoding: True
Course limit: None
```

### Cell 66

Matched: `nominatim`

```text
# Define ordered query planning and deterministic cache lookup.

def build_course_geocoding_queries(course_label, jurisdiction):
    if jurisdiction not in JURISDICTION_GEOCODING_RULES:
        raise KeyError(
            f"No geocoding rule exists for jurisdiction {jurisdiction!r}."
        )

    if jurisdiction not in JURISDICTION_VENUE_TERMS:
        raise KeyError(
            f"No venue-term rule exists for jurisdiction {jurisdiction!r}."
        )

    jurisdiction_rule = JURISDICTION_GEOCODING_RULES[jurisdiction]
    query_country = jurisdiction_rule["query_country"]
    country_codes = sorted(jurisdiction_rule["country_codes"])

    if len(country_codes) != 1:
        raise RuntimeError(
            f"Expected one country code for {jurisdiction!r}; "
            f"found {country_codes}."
        )

    country_code = country_codes[0]
    query_label = clean_course_label_for_geocoding(course_label)

    query_rows = []

    for query_order, venue_term in enumerate(
        JURISDICTION_VENUE_TERMS[jurisdiction],
        start=1,
    ):
        exact_query = f"{query_label} {venue_term}, {query_country}"

        cache_record_id = build_geocoding_cache_record_id(
            provider=NOMINATIM_PROVIDER,
            candidate_course_label=course_label,
            candidate_jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code,
            result_limit=NOMINATIM_RESULT_LIMIT,
        )

        query_rows.append(
            {
                "query_order": query_order,
                "venue_term": venue_term,
                "exact_query": exact_query,
                "country_code_filter": country_code,
                "cache_record_id": cache_record_id,
            }
        )

    return pd.DataFrame(quer
…
```

### Cell 67

Matched: `nominatim`

```text
# Define the cache-aware request function.
#
# Every exact query is sent at most once. Errors and zero-result responses are
# cached as outcomes rather than silently retried on every notebook run.

def request_or_reuse_geocoding_query(
    *,
    course_label,
    jurisdiction,
    exact_query,
    country_code_filter,
    cache_record_id,
):
    global geocoding_cache

    manifest_row = get_cache_manifest_row(cache_record_id)

    if manifest_row is not None:
        raw_record = get_raw_response_record(cache_record_id)

        if raw_record is None:
            raise RuntimeError(
                "Manifest row exists without a raw response for "
                f"{cache_record_id!r}."
            )

        return {
            "request_action": "reused_cached_result",
            "request_status": manifest_row["request_status"],
            "results": raw_record.get("results", []),
        }

    requested_at_utc = datetime.now(timezone.utc).isoformat()
    request_status = "pending"
    raw_results = []
    error_type = None
    error_message = None

    try:
        locations = rate_limited_geocode(
            exact_query,
            country_codes=country_code_filter,
            **NOMINATIM_REQUEST_OPTIONS,
        )

        if locations is None:
            locations = []

        raw_results = [location.raw for location in locations]
        request_status = (
            "success_with_results"
            if raw_results
            else "success_no_results"
        )

    except Exception as exc:
        request_status = "request_error"
        error_type = type(exc).__name__
        error_message = str(exc)

    raw_record = {
        "raw_response_record_id": cache_record_id,
        "cache_record_id": cache_record_id,
        "provider": NOMINATIM_PROVI
…
```

### Cell 68

Matched: `manual`

```text
# Define one complete course decision.
#
# All jurisdiction-specific queries are considered. Automatic selection occurs
# only when they collectively identify exactly one eligible provider object.
# Multiple eligible objects, weak objects, errors and zero results go to review.

def process_course_geocoding(course_label, jurisdiction):
    query_plan = build_course_geocoding_queries(
        course_label,
        jurisdiction,
    )

    request_rows = []
    review_rows = []
    eligible_candidates = {}

    for query_row in query_plan.itertuples(index=False):
        outcome = request_or_reuse_geocoding_query(
            course_label=course_label,
            jurisdiction=jurisdiction,
            exact_query=query_row.exact_query,
            country_code_filter=query_row.country_code_filter,
            cache_record_id=query_row.cache_record_id,
        )

        request_rows.append(
            {
                "query_order": query_row.query_order,
                "exact_query": query_row.exact_query,
                "cache_record_id": query_row.cache_record_id,
                "request_action": outcome["request_action"],
                "request_status": outcome["request_status"],
                "result_count": len(outcome["results"]),
            }
        )

        for result_index, result in enumerate(outcome["results"]):
            assessment = automatic_candidate_assessment(
                course_label=course_label,
                expected_country_code=query_row.country_code_filter,
                result=result,
            )

            place_id = result_provider_place_id(result)
            review_row = {
                "candidate_course_label": course_label,
                "candidate_jurisdiction": jurisdiction,
                "exact_query": qu
…
```

### Cell 69

Matched: `manual`, `manually`, `validation_status`, `nominatim`

```text
# Define automatic writing and manifest review updates.

def recalculate_reusable_location(reference):
    return (
        reference["latitude"].notna()
        & reference["longitude"].notna()
        & reference["iana_timezone"].notna()
        & reference["location_validation_status"].isin(
            {"manually_validated", "automatically_validated"}
        )
    )

def write_automatic_course_location(processor_result):
    global course_locations
    global geocoding_cache

    if processor_result["decision"] != "single_strong_match":
        raise ValueError(
            "Only single_strong_match results may be written automatically."
        )

    course_label = processor_result["course_label"]
    jurisdiction = processor_result["jurisdiction"]
    candidate = processor_result["selected_candidate"]
    selected_fields = processor_result["selected_fields"]

    reference_mask = (
        course_locations["candidate_course_label"].eq(course_label)
        & course_locations["candidate_jurisdiction"].eq(jurisdiction)
    )

    if int(reference_mask.sum()) != 1:
        raise RuntimeError(
            f"Expected one reference row for {course_label!r}, "
            f"{jurisdiction!r}; found {int(reference_mask.sum())}."
        )

    permanent_values = {
        **selected_fields,
        "location_evidence": (
            "Nominatim conservative automatic selection from query "
            f"{candidate['query']!r}; selected result index "
            f"{candidate['result_index']}."
        ),
        "location_validation_status": "automatically_validated",
    }

    for column_name, column_value in permanent_values.items():
        course_locations.loc[
            reference_mask,
            column_name,
        ] = column_value

    course_locations["has_re
…
```

### Cell 70

Matched: `manual`

```text
# Process every currently unresolved course and checkpoint after each decision.
#
# The final review CSV contains one row per provider alternative. Courses with
# no alternatives still receive a summary row in the run-summary CSV.

def run_production_geocoding(
    *,
    max_courses=None,
):
    global course_locations

    course_locations["has_reusable_location"] = (
        recalculate_reusable_location(course_locations)
    )

    unresolved = (
        course_locations.loc[
            ~course_locations["has_reusable_location"]
        ]
        .sort_values(
            [
                "provisional_races",
                "candidate_jurisdiction",
                "candidate_course_label",
            ],
            ascending=[False, True, True],
        )
        .copy()
    )

    if max_courses is not None:
        unresolved = unresolved.head(int(max_courses))

    summary_rows = []
    review_frames = []

    for course_row in unresolved.itertuples(index=False):
        result = process_course_geocoding(
            course_row.candidate_course_label,
            course_row.candidate_jurisdiction,
        )

        if result["decision"] == "single_strong_match":
            write_automatic_course_location(result)

        request_summary = result["request_summary"]

        summary_rows.append(
            {
                "candidate_course_label": course_row.candidate_course_label,
                "candidate_jurisdiction": course_row.candidate_jurisdiction,
                "provisional_races": course_row.provisional_races,
                "decision": result["decision"],
                "decision_reason": result["decision_reason"],
                "physical_venue_name": (
                    result["selected_fields"]["physical_venue_name"]
…
```

### Cell 71

Matched: `manual`

```text
## Final validation and outputs

The permanent reference is considered complete for analysis when every accepted row has a valid coordinate pair and IANA timezone, while every unaccepted row is explicitly available in the manual-review output. “Complete” therefore does not mean guessing every venue: ambiguous cases remain unresolved by design.
```

### Cell 72

Matched: `manual`, `manually`, `validation_status`

```text
# Validate permanent outputs and report final coverage.

course_locations = pd.read_csv(course_locations_path)
course_locations["has_reusable_location"] = (
    recalculate_reusable_location(course_locations)
)

duplicate_course_keys = (
    course_locations.groupby(
        [
            "candidate_course_label",
            "candidate_jurisdiction",
        ],
        dropna=False,
    )
    .size()
    .loc[lambda counts: counts > 1]
)

if not duplicate_course_keys.empty:
    raise RuntimeError(
        "Duplicate course-location identity rows remain in the reference."
    )

accepted_rows = course_locations.loc[
    course_locations["has_reusable_location"]
].copy()

invalid_accepted_rows = accepted_rows.loc[
    accepted_rows[
        [
            "physical_venue_name",
            "latitude",
            "longitude",
            "iana_timezone",
            "location_validation_status",
        ]
    ].isna().any(axis=1)
]

if not invalid_accepted_rows.empty:
    raise RuntimeError(
        "At least one accepted course-location row is incomplete."
    )

invalid_timezone_rows = []

for row in accepted_rows.itertuples(index=False):
    try:
        ZoneInfo(row.iana_timezone)
    except Exception:
        invalid_timezone_rows.append(
            {
                "candidate_course_label": row.candidate_course_label,
                "candidate_jurisdiction": row.candidate_jurisdiction,
                "iana_timezone": row.iana_timezone,
            }
        )

if invalid_timezone_rows:
    raise RuntimeError(
        "At least one accepted row has an invalid IANA timezone."
    )

final_status = pd.DataFrame(
    [
        {
            "measure": "Permanent course identities",
            "value": len(course_locations),
        },
        {
            "measure
…
```

### Cell 74

Matched: `external`

```text
# Profile timezone coverage by jurisdiction.
#
# This cell is read-only:
# - it sends no external requests;
# - it does not modify course_locations.csv;
# - it does not assign any new timezones.
#
# The purpose is to identify:
# - jurisdictions where every validated course uses one timezone;
# - jurisdictions with multiple observed timezones;
# - jurisdictions with no validated timezone evidence yet;
# - the number of provisional races affected by unresolved timezones.
#
# We will use this evidence to separate safe jurisdiction-level defaults from
# jurisdictions that still require course-level resolution.

timezone_jurisdiction_profile = (
    course_locations
    .groupby(
        "candidate_jurisdiction",
        dropna=False,
    )
    .agg(
        course_identities=(
            "candidate_course_label",
            "size",
        ),
        provisional_races=(
            "provisional_races",
            "sum",
        ),
        courses_with_timezone=(
            "iana_timezone",
            lambda values: values.notna().sum(),
        ),
        resolved_provisional_races=(
            "provisional_races",
            lambda values: values[
                course_locations.loc[
                    values.index,
                    "iana_timezone",
                ].notna()
            ].sum(),
        ),
        distinct_validated_timezones=(
            "iana_timezone",
            lambda values: values.dropna().nunique(),
        ),
        observed_timezones=(
            "iana_timezone",
            lambda values: ", ".join(
                sorted(
                    values.dropna().astype(str).unique()
                )
            ),
        ),
    )
    .reset_index()
)

timezone_jurisdiction_profile[
    "unresolved_courses"
] = (
    timezone_jurisd
…
```

### Cell 76

Matched: `manual`

```text
# Define an explicit timezone-resolution policy by racing jurisdiction.
#
# This is deliberately manual and reviewable. We are not inferring that a
# jurisdiction is safe merely because the currently validated sample contains
# one observed timezone.
#
# Policy classes:
# - jurisdiction_default:
#     All unresolved courses represented by this racing jurisdiction may use
#     the stated IANA timezone for off-time interpretation.
# - course_level_required:
#     The jurisdiction spans multiple relevant timezones, so each unresolved
#     course must be resolved separately.
#
# This cell does not modify course_locations.csv.

jurisdiction_timezone_policy = {
    "Great Britain": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Europe/London",
        "reason": "British racecourses use UK civil time.",
    },
    "Ireland": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Europe/Dublin",
        "reason": "Irish racecourses use Irish civil time.",
    },
    "Hong Kong": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Asia/Hong_Kong",
        "reason": "Both represented Hong Kong racecourses use Hong Kong time.",
    },
    "France": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Europe/Paris",
        "reason": "The dataset represents mainland French racing.",
    },
    "United Arab Emirates": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Asia/Dubai",
        "reason": "Represented UAE racecourses use Gulf Standard Time.",
    },
    "Japan": {
        "policy": "jurisdiction_default",
        "iana_timezone": "Asia/Tokyo",
        "reason": "Japan uses one civil timezone.",
    },
    "Germany": {
        "policy": "jurisdiction_default",
        "iana_timezon
…
```

### Cell 83

Matched: `nominatim`

```text
# Test the timezone-only workflow on the five highest-volume unresolved courses.
#
# This cell:
# - uses the existing cache-aware Nominatim request helper;
# - stops for a course after the first query producing one-timezone consensus;
# - preserves every request in the existing cache;
# - does not update course_locations.csv.

TIMEZONE_COUNTRY_CODE_FILTERS = {
    "United States": "us",
    "Australia": "au",
    "Canada": "ca",
    "Brazil": "br",
}

timezone_test_rows = []

for course_row in (
    timezone_query_plan
    .head(5)
    .itertuples(index=False)
):
    course_label = course_row.candidate_course_label
    jurisdiction = course_row.candidate_jurisdiction
    country_code_filter = TIMEZONE_COUNTRY_CODE_FILTERS[jurisdiction]

    final_decision = "all_queries_exhausted"
    resolved_timezone = pd.NA
    accepted_review = None
    queries_attempted = 0
    requests_sent = 0
    requests_reused = 0

    for exact_query in course_row.planned_queries:
        queries_attempted += 1

        cache_record_id = build_geocoding_cache_record_id(
            provider=NOMINATIM_PROVIDER,
            candidate_course_label=course_label,
            candidate_jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            result_limit=NOMINATIM_RESULT_LIMIT,
        )

        outcome = request_or_reuse_geocoding_query(
            course_label=course_label,
            jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            cache_record_id=cache_record_id,
        )

        if outcome["request_action"] == "sent_and_cached":
            requests_sent += 1
        else:
            requests_reused += 1

        review = review_timezone_
…
```

### Cell 84

Matched: `nominatim`

```text
# Expand the reviewed provider results from the five-course test.
#
# This lets us distinguish:
# - a genuine racecourse result mixed with irrelevant same-name places;
# - results referring only to unrelated towns, roads or neighbourhoods;
# - queries that need additional state or city qualification.
#
# No requests are sent and no files are written.

timezone_test_detail_rows = []

for course_row in (
    timezone_query_plan
    .head(5)
    .itertuples(index=False)
):
    course_label = course_row.candidate_course_label
    jurisdiction = course_row.candidate_jurisdiction
    country_code_filter = TIMEZONE_COUNTRY_CODE_FILTERS[jurisdiction]

    for exact_query in course_row.planned_queries:
        cache_record_id = build_geocoding_cache_record_id(
            provider=NOMINATIM_PROVIDER,
            candidate_course_label=course_label,
            candidate_jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            result_limit=NOMINATIM_RESULT_LIMIT,
        )

        outcome = request_or_reuse_geocoding_query(
            course_label=course_label,
            jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            cache_record_id=cache_record_id,
        )

        review = review_timezone_query_results(
            raw_results=outcome["results"],
            jurisdiction=jurisdiction,
        )

        for reviewed_result in review["reviewed_results"]:
            timezone_test_detail_rows.append(
                {
                    "candidate_course_label": course_label,
                    "candidate_jurisdiction": jurisdiction,
                    "exact_query": exact_query,
                    "result_index": revi
…
```

### Cell 85

Matched: `nominatim`

```text
# Inspect provider object types for the five-course test.
#
# This will show whether relevant results are classified as leisure,
# stadium, sports venue, neighbourhood, park, administrative area, etc.
# No new requests should be sent because all outcomes are cached.

timezone_test_provider_rows = []

for course_row in timezone_query_plan.head(5).itertuples(index=False):
    course_label = course_row.candidate_course_label
    jurisdiction = course_row.candidate_jurisdiction
    country_code_filter = TIMEZONE_COUNTRY_CODE_FILTERS[jurisdiction]

    for exact_query in course_row.planned_queries:
        cache_record_id = build_geocoding_cache_record_id(
            provider=NOMINATIM_PROVIDER,
            candidate_course_label=course_label,
            candidate_jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            result_limit=NOMINATIM_RESULT_LIMIT,
        )

        outcome = request_or_reuse_geocoding_query(
            course_label=course_label,
            jurisdiction=jurisdiction,
            exact_query=exact_query,
            country_code_filter=country_code_filter,
            cache_record_id=cache_record_id,
        )

        for result_index, result in enumerate(outcome["results"]):
            address = result.get("address") or {}

            try:
                latitude = float(result["lat"])
                longitude = float(result["lon"])
                derived_timezone = timezone_finder.timezone_at(
                    lat=latitude,
                    lng=longitude,
                )
            except (KeyError, TypeError, ValueError):
                latitude = pd.NA
                longitude = pd.NA
                derived_timezone = pd.NA

            timezone_test_pro
…
```

### Cell 86

Matched: `manual`, `manually`

```text
# Record manually reviewed timezone decisions from the five-course test.
#
# Approved:
# - Gulfstream Park -> America/New_York
# - Randwick -> Australia/Sydney
# - Caulfield -> Australia/Melbourne
# - Belmont Park -> America/New_York
#
# Saratoga remains unresolved.
#
# This cell does not write to course_locations.csv.

manual_timezone_decisions = pd.DataFrame(
    [
        {
            "candidate_course_label": "Gulfstream Park",
            "candidate_jurisdiction": "United States",
            "resolved_iana_timezone": "America/New_York",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Manual review identified the Hallandale Beach, Florida "
                "sports-centre result as the relevant course; Texas results "
                "were unrelated namesakes."
            ),
        },
        {
            "candidate_course_label": "Randwick",
            "candidate_jurisdiction": "Australia",
            "resolved_iana_timezone": "Australia/Sydney",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Exact Randwick Racecourse result in Sydney, New South Wales."
            ),
        },
        {
            "candidate_course_label": "Caulfield",
            "candidate_jurisdiction": "Australia",
            "resolved_iana_timezone": "Australia/Melbourne",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Two exact Caulfield Racecourse results in Melbourne, Victoria, "
                "both derived the same timezone."
            ),
        },
        {
            "candidate_course_label": "Belmont Park",
            "candidate_
…
```

### Cell 87

Matched: `manual`, `nominatim`

```text
# Run timezone-only candidate generation for the remaining 81 courses.
#
# Important:
# - the five test courses are excluded;
# - no timezone is automatically accepted;
# - no permanent reference data is modified;
# - all provider responses use the existing cache;
# - plausible sporting/racing objects are ranked for manual inspection.
#
# The output is a compact candidate table rather than a final decision table.

RACE_LIKE_CLASSIFICATIONS = {
    ("leisure", "sports_centre"),
    ("leisure", "track"),
    ("leisure", "stadium"),
    ("sport", "horse_racing"),
    ("landuse", "recreation_ground"),
}

EXCLUDED_TEST_COURSES = {
    ("Gulfstream Park", "United States"),
    ("Randwick", "Australia"),
    ("Caulfield", "Australia"),
    ("Saratoga", "United States"),
    ("Belmont Park", "United States"),
}

def normalise_candidate_text(value):
    if pd.isna(value):
        return ""

    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())

def candidate_name_similarity(course_label, provider_name):
    course_tokens = set(
        normalise_candidate_text(course_label).split()
    )
    provider_tokens = set(
        normalise_candidate_text(provider_name).split()
    )

    if not course_tokens or not provider_tokens:
        return 0.0

    return len(course_tokens & provider_tokens) / len(course_tokens)

remaining_timezone_query_plan = timezone_query_plan.loc[
    ~timezone_query_plan.apply(
        lambda row: (
            row["candidate_course_label"],
            row["candidate_jurisdiction"],
        ) in EXCLUDED_TEST_COURSES,
        axis=1,
…
```

### Cell 88

Matched: `manual`, `manually`

```text
# Add the 18 manually approved candidates from the full candidate run.
#
# This extends the existing manual_timezone_decisions table.
# Duplicated provider objects were reviewed as supporting evidence, but each
# course receives only one timezone decision.
#
# No permanent files are written in this cell.

additional_manual_timezone_decisions = pd.DataFrame(
    [
        {
            "candidate_course_label": "Churchill Downs",
            "candidate_jurisdiction": "United States",
            "resolved_iana_timezone": "America/Kentucky/Louisville",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Exact Churchill Downs stadium result in Louisville, Kentucky."
            ),
        },
        {
            "candidate_course_label": "Woodbine",
            "candidate_jurisdiction": "Canada",
            "resolved_iana_timezone": "America/Toronto",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Exact Woodbine Racetrack result in Toronto, Ontario."
            ),
        },
        {
            "candidate_course_label": "Morphettville",
            "candidate_jurisdiction": "Australia",
            "resolved_iana_timezone": "Australia/Adelaide",
            "timezone_resolution_method": "manual_timezone_review",
            "timezone_resolution_reason": (
                "Exact Morphettville Racecourse sporting and track objects "
                "in Adelaide, South Australia agreed on timezone."
            ),
        },
        {
            "candidate_course_label": "Arlington Park",
            "candidate_jurisdiction": "United States",
            "resolved_iana_timezone": "America/Chicago",
            "ti
…
```

### Cell 89

Matched: `manual`

```text
# Generate a compact unresolved-course list for manual lookup.
#
# This prints one course per line in a format that can be pasted directly
# back into ChatGPT. No files are written.

manual_lookup_list = (
    remaining_timezone_courses[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "provisional_races",
        ]
    ]
    .sort_values(
        [
            "provisional_races",
            "candidate_jurisdiction",
            "candidate_course_label",
        ],
        ascending=[False, True, True],
    )
    .reset_index(drop=True)
)

print(
    "\n".join(
        f"{row.candidate_course_label} | "
        f"{row.candidate_jurisdiction} | "
        f"{int(row.provisional_races)} races"
        for row in manual_lookup_list.itertuples(index=False)
    )
)

Saratoga | United States | 528 races
Rosehill | Australia | 472 races
Keeneland | United States | 409 races
Will Rogers Downs | United States | 178 races
Eagle Farm | Australia | 166 races
Oaklawn Park | United States | 157 races
Gavea | Brazil | 136 races
Fair Grounds | United States | 112 races
Tampa Bay Downs | United States | 107 races
Pimlico | United States | 100 races
Kentucky Downs | United States | 86 races
Parx | United States | 85 races
Newcastle | Australia | 77 races
Laurel Park | United States | 71 races
Fonner Park | United States | 68 races
Golden Gate Fields | United States | 54 races
Delaware Park | United States | 49 races
Los Alamitos | United States | 48 races
Indiana Grand | United States | 40 races
Kembla Grange | Australia | 38 races
Hawkesbury | Australia | 33 races
Remington Park | United States | 25 races
Charles town | United States | 24 races
Far Hills | United States | 23 races
Hobart | Australia | 22 races
Prairie Meadows | United St
…
```

### Cell 90

Matched: `manual`, `manually`

```text
# Load and validate the 64 manually researched course resolutions.
#
# This cell reads only. It does not yet update course_locations.csv.

from pathlib import Path

MANUAL_TIMEZONE_RESOLUTION_PATH = Path(
    "/home/rob/Documents/inside-rails-horse-racing/"
    "data/reference/course_location_manual_timezone_resolution.csv"
)

manual_course_resolutions = pd.read_csv(
    MANUAL_TIMEZONE_RESOLUTION_PATH,
    dtype={
        "candidate_course_label": "string",
        "candidate_jurisdiction": "string",
        "official_venue_name": "string",
        "street_address": "string",
        "locality": "string",
        "region": "string",
        "postal_code": "string",
        "country": "string",
        "latitude": "Float64",
        "longitude": "Float64",
        "iana_timezone": "string",
        "venue_status": "string",
        "former_or_alternative_name": "string",
        "manual_review_confidence": "string",
        "manual_review_note": "string",
        "source_urls": "string",
    },
)

manual_course_resolutions["provisional_races"] = pd.to_numeric(
    manual_course_resolutions["provisional_races"],
    errors="raise",
).astype("int64")

assert len(manual_course_resolutions) == 64

assert not manual_course_resolutions.duplicated(
    subset=[
        "candidate_course_label",
        "candidate_jurisdiction",
    ]
).any()

assert manual_course_resolutions[
    [
        "candidate_course_label",
        "candidate_jurisdiction",
        "official_venue_name",
        "locality",
        "region",
        "country",
        "iana_timezone",
        "manual_review_confidence",
    ]
].notna().all().all()

for timezone_name in manual_course_resolutions["iana_timezone"]:
    ZoneInfo(timezone_name)

expected_unresolved_keys = set(
    zip(
        remaining_tim
…
```

### Cell 91

Matched: `manual`

```text
# Build a complete timezone assignment preview for all course identities.
#
# This still does not write to course_locations.csv.

manual_csv_timezone_assignments = (
    manual_course_resolutions[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "iana_timezone",
            "manual_review_confidence",
            "manual_review_note",
        ]
    ]
    .rename(
        columns={
            "iana_timezone": "resolved_iana_timezone",
        }
    )
    .assign(
        timezone_resolution_method="manual_reference_csv",
        timezone_resolution_reason=lambda df: (
            df["manual_review_note"]
        ),
    )
)

manual_csv_timezone_assignments = (
    manual_csv_timezone_assignments[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "resolved_iana_timezone",
            "timezone_resolution_method",
            "timezone_resolution_reason",
            "manual_review_confidence",
        ]
    ]
)

all_manual_timezone_assignments = pd.concat(
    [
        manual_timezone_decisions.assign(
            manual_review_confidence="high"
        )[
            [
                "candidate_course_label",
                "candidate_jurisdiction",
                "resolved_iana_timezone",
                "timezone_resolution_method",
                "timezone_resolution_reason",
                "manual_review_confidence",
            ]
        ],
        manual_csv_timezone_assignments,
    ],
    ignore_index=True,
)

assert len(all_manual_timezone_assignments) == 86

assert not all_manual_timezone_assignments.duplicated(
    subset=[
        "candidate_course_label",
        "candidate_jurisdiction",
    ]
).any()

complete_timezone_preview = (
    course_locations
…
```

### Cell 93

Matched: `manual`, `manually`

```text
# Build a complete timezone assignment preview for all course identities.
#
# Sources:
# - existing timezone on course_locations;
# - jurisdiction defaults;
# - 22 manually reviewed course assignments;
# - 64 manual CSV assignments.
#
# This cell still does not write to course_locations.csv.

manual_csv_timezone_assignments = (
    manual_course_resolutions[
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "iana_timezone",
            "manual_review_confidence",
            "manual_review_note",
        ]
    ]
    .rename(
        columns={
            "iana_timezone": "resolved_iana_timezone",
        }
    )
    .assign(
        timezone_resolution_method="manual_reference_csv",
        timezone_resolution_reason=lambda df: (
            df["manual_review_note"]
        ),
    )
    [
        [
            "candidate_course_label",
            "candidate_jurisdiction",
            "resolved_iana_timezone",
            "timezone_resolution_method",
            "timezone_resolution_reason",
            "manual_review_confidence",
        ]
    ]
)

all_manual_timezone_assignments = pd.concat(
    [
        manual_timezone_decisions.assign(
            manual_review_confidence="high"
        )[
            [
                "candidate_course_label",
                "candidate_jurisdiction",
                "resolved_iana_timezone",
                "timezone_resolution_method",
                "timezone_resolution_reason",
                "manual_review_confidence",
            ]
        ],
        manual_csv_timezone_assignments,
    ],
    ignore_index=True,
)

assert len(all_manual_timezone_assignments) == 86

assert not all_manual_timezone_assignments.duplicated(
    subset=[
        "candidate_course_label",
        "
…
```

### Cell 94

Matched: `manual`

```text
### Complete timezone coverage achieved

All 394 permanent course identities now have a valid IANA timezone assignment.

Assignments were derived from three evidence paths:

- 126 courses retained a timezone derived from an already resolved course location;
- 182 courses used a documented jurisdiction-level timezone policy where one civil timezone safely applies;
- 86 courses in multi-timezone jurisdictions were resolved individually through manual course-level review.

No course identities remain unresolved. The next step is to persist the final timezone, resolution method, and resolution reason into the permanent course-location reference.
```

### Cell 95

Matched: `manual`

```text
# Persist complete timezone coverage into course_locations.csv.
#
# This updates only the final timezone and its resolution metadata.
# Existing course identity and location fields are preserved.
from pathlib import Path

COURSE_LOCATION_REFERENCE_PATH = Path(
    "/home/rob/Documents/inside-rails-horse-racing/"
    "data/reference/course_locations.csv"
)
course_locations_updated = complete_timezone_preview.copy()

course_locations_updated["iana_timezone"] = (
    course_locations_updated["final_iana_timezone"]
)

course_locations_updated["timezone_resolution_method"] = (
    course_locations_updated[
        "final_timezone_resolution_method"
    ]
)

course_locations_updated["timezone_resolution_reason"] = (
    course_locations_updated[
        "final_timezone_resolution_reason"
    ]
)

# Remove preview-only merge columns before writing.
preview_only_columns = [
    "timezone_policy",
    "jurisdiction_default_iana_timezone",
    "jurisdiction_timezone_reason",
    "resolved_iana_timezone",
    "manual_review_confidence",
    "final_iana_timezone",
    "final_timezone_resolution_method",
    "final_timezone_resolution_reason",
]

course_locations_updated = course_locations_updated.drop(
    columns=[
        column
        for column in preview_only_columns
        if column in course_locations_updated.columns
    ]
)

assert len(course_locations_updated) == 394
assert course_locations_updated["iana_timezone"].notna().all()

for timezone_name in course_locations_updated["iana_timezone"]:
    ZoneInfo(timezone_name)

course_locations_updated.to_csv(
    COURSE_LOCATION_REFERENCE_PATH,
    index=False,
)

# Reload from disk to confirm the persisted file is valid.
course_locations_reloaded = pd.read_csv(
    COURSE_LOCATION_REFERENCE_PATH,
    dtype={
        "candidat
…
```

## `notebooks/13_prize_money_semantics_and_availability.ipynb`

### Cell 26

Matched: `external`

```text
# Inspect race-level prize totals and winner amounts across major jurisdictions.
#
# Several foreign values resemble currency conversions into pounds rather than
# natural local-currency prize schedules. For example, repeated thirds such as
# 333333.33 and 111111.11 may result from dividing round local amounts by an
# exchange rate.
#
# This cell selects a small set of high-value races from major jurisdictions
# and reports:
# - the winner's raw prize;
# - the sum of all populated runner prizes;
# - the number of paid runners; and
# - the race description.
#
# The results will provide candidate cases for external validation. No currency
# or conversion interpretation is assigned in this cell.

with sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True) as conn:
    race_prize_amounts = pd.read_sql_query(
        f"""
        SELECT
            date,
            course,
            off,
            MIN(race_name) AS race_name,
            MIN(type) AS type,
            MAX(
                CASE
                    WHEN CAST(pos AS TEXT) = '1'
                    THEN CAST(
                        REPLACE(
                            REPLACE(CAST(prize AS TEXT), '€', ''),
                            ',',
                            ''
                        ) AS REAL
                    )
                END
            ) AS winner_raw_prize,
            SUM(
                CASE
                    WHEN TRIM(CAST(prize AS TEXT)) <> ''
                    THEN CAST(
                        REPLACE(
                            REPLACE(CAST(prize AS TEXT), '€', ''),
                            ',',
                            ''
                        ) AS REAL
                    )
                    ELSE 0
                END
            ) AS summed_runner_priz
…
```

### Cell 27

Matched: `external`

```text
## Interim structural findings

The source field is named `prize` and is declared as `INTEGER`, but SQLite actually stores a mixture of text, real and integer values.

Effective availability is:

- 1,011,570 populated runner rows out of 1,851,285;
- 189,031 provisional races with at least one populated value out of 189,043;
- 12 races with no populated value.

The field behaves primarily as a **runner-level prize allocation**, not as a race-level purse:

- populated values normally occur on placed runners;
- several runners within the same race usually receive different amounts;
- lower placings may receive identical minimum payments;
- blanks generally indicate runners receiving no recorded prize.

A small number of non-finishers also carry values. These occur across several jurisdictions and must be retained as valid source observations pending jurisdiction-specific validation.

Raw formatting is jurisdiction-dependent:

- Irish populated values are consistently stored as euro-prefixed text;
- all other populated values are stored numerically;
- numeric storage as `INTEGER` or `REAL` reflects whether the resulting value contains a fractional component, not a stable semantic distinction;
- no populated numeric value requires more than two decimal places.

High-value foreign examples contain conspicuous conversion-like decimals. The current candidate interpretation is therefore:

1. Great Britain — runner prize recorded in pounds;
2. Ireland — runner prize recorded in euros with an explicit `€` symbol;
3. at least some other jurisdictions — runner prize apparently converted into pounds by the source.

The apparent foreign-currency conversion remains a candidate interpretation and must be tested against external historical results before being confirmed.
```

### Cell 28

Matched: `external`, `racecard`

```text
# Build a small external-validation sample of prominent foreign races.
#
# These races are useful because their official prize schedules should be
# recoverable from historical racecards or governing-body results.
#
# We retain every paid runner so that any inferred exchange rate can be tested
# across the complete placing schedule, not just against the winner.
#
# No reverse conversion is attempted yet.

validation_name_patterns = [
    "Pegasus World Cup",
    "Breeders Cup Classic",
    "Prix de lArc de Triomphe",
    "The TAB Everest",
]

with sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True) as conn:
    external_validation_candidates = pd.read_sql_query(
        f"""
        SELECT
            date,
            course,
            off,
            race_name,
            pos,
            horse,
            prize,
            typeof(prize) AS prize_storage_class
        FROM data
        WHERE {DATA_ROW_PREDICATE}
          AND TRIM(CAST(prize AS TEXT)) <> ''
          AND (
              race_name LIKE '%Pegasus World Cup%'
              OR race_name LIKE '%Breeders Cup Classic%'
              OR race_name LIKE '%Prix de lArc de Triomphe%'
              OR race_name LIKE '%The TAB Everest%'
          )
        ORDER BY
            date,
            course,
            off,
            CASE
                WHEN typeof(pos) IN ('integer', 'real') THEN pos
                ELSE 999
            END,
            rowid
        """,
        conn,
    )

external_validation_candidates[
    [
        "date",
        "course",
        "off",
        "race_name",
    ]
].drop_duplicates().reset_index(drop=True)
          date                 course    off  \
0   2015-10-04         Longchamp (FR)   2:55   
1   2015-10-31        Keeneland (USA)   9:35   
2   2016-10
…
```

### Cell 29

Matched: `external`

```text
# Select a small, controlled set of races for external validation.
#
# The broad name search found one false positive: a Chelmsford handicap whose
# title merely referred to the Breeders' Cup broadcast. We therefore identify
# validation races by exact date + course + off, using the established
# provisional race identity.
#
# The sample covers three foreign-currency jurisdictions and several years:
# - United States;
# - France; and
# - Australia.
#
# Every runner row is retained so an inferred exchange rate can later be tested
# against the complete official prize schedule, not just the winner's amount.

validation_race_keys = pd.DataFrame(
    [
        {
            "date": "2018-01-27",
            "course": "Gulfstream Park (USA)",
            "off": "10:35",
            "validation_label": "2018 Pegasus World Cup",
        },
        {
            "date": "2025-11-01",
            "course": "Del Mar",
            "off": "22:25",
            "validation_label": "2025 Breeders Cup Classic",
        },
        {
            "date": "2019-10-06",
            "course": "Longchamp (FR)",
            "off": "3:05",
            "validation_label": "2019 Prix de lArc de Triomphe",
        },
        {
            "date": "2023-10-14",
            "course": "Randwick (AUS)",
            "off": "6:15",
            "validation_label": "2023 The Everest",
        },
    ]
)

controlled_validation_sample = (
    external_validation_candidates
    .merge(
        validation_race_keys,
        on=["date", "course", "off"],
        how="inner",
        validate="many_to_one",
    )
    .sort_values(
        ["date", "course", "off", "pos"],
        key=lambda series: pd.to_numeric(series, errors="coerce"),
        na_position="last",
    )
    .reset_index(drop=True)
)

controlle
…
```

### Cell 30

Matched: `external`

```text
# Compare the stored 2018 Pegasus World Cup values with the externally
# reported official US-dollar prize schedule.
#
# External evidence:
# - winner: $7,000,000
# - second: $1,600,000
# - third: $1,300,000
# - fourth: $1,000,000
# - fifth: $850,000
# - positions 6–12: $650,000 each
#
# Sources consulted:
# - Bleacher Report, 27 January 2018, citing NBC Sports for the allocations
# - America's Best Racing race page, reporting a $16.3 million purse
#
# For each placing, the implied conversion rate is:
#
#     official USD prize / stored source prize
#
# A stable rate across every placing would confirm that the source stored
# converted sterling amounts rather than the original US-dollar awards.

pegasus_2018_official = pd.DataFrame(
    {
        "pos": list(range(1, 13)),
        "official_local_prize": [
            7_000_000,
            1_600_000,
            1_300_000,
            1_000_000,
            850_000,
            650_000,
            650_000,
            650_000,
            650_000,
            650_000,
            650_000,
            650_000,
        ],
        "official_currency": "USD",
    }
)

pegasus_2018_source = (
    controlled_validation_sample.loc[
        controlled_validation_sample["validation_label"]
        == "2018 Pegasus World Cup",
        ["pos", "horse", "prize"],
    ]
    .copy()
)

pegasus_2018_source["pos"] = pd.to_numeric(
    pegasus_2018_source["pos"],
    errors="raise",
).astype(int)

pegasus_2018_validation = pegasus_2018_source.merge(
    pegasus_2018_official,
    on="pos",
    how="left",
    validate="one_to_one",
)

pegasus_2018_validation["implied_usd_per_stored_unit"] = (
    pegasus_2018_validation["official_local_prize"]
    / pegasus_2018_validation["prize"].astype(float)
)

pegasus_2018_validation["reconstruct
…
```

### Cell 31

Matched: `external`

```text
# Test the 2019 Prix de l'Arc de Triomphe against its apparent official
# euro-denominated placing schedule.
#
# The source contains five paid runners whose stored values appear to reconstruct
# round or half-round euro amounts under one common conversion rate.
#
# These candidate official allocations sum to the advertised €5 million purse:
# - first:  €2,857,000
# - second: €1,143,000
# - third:    €571,500
# - fourth:   €285,500
# - fifth:    €143,000
#
# This cell calculates the implied euro-per-stored-unit rate for each placing.
# A stable rate would confirm race-level conversion, although the exact official
# allocation schedule should still be retained as externally validated evidence.

arc_2019_official = pd.DataFrame(
    {
        "pos": [1, 2, 3, 4, 5],
        "official_local_prize": [
            2_857_000,
            1_143_000,
            571_500,
            285_500,
            143_000,
        ],
        "official_currency": "EUR",
    }
)

arc_2019_source = (
    controlled_validation_sample.loc[
        controlled_validation_sample["validation_label"]
        == "2019 Prix de lArc de Triomphe",
        ["pos", "horse", "prize"],
    ]
    .copy()
)

arc_2019_source["pos"] = pd.to_numeric(
    arc_2019_source["pos"],
    errors="raise",
).astype(int)

arc_2019_validation = arc_2019_source.merge(
    arc_2019_official,
    on="pos",
    how="left",
    validate="one_to_one",
)

arc_2019_validation["implied_eur_per_stored_unit"] = (
    arc_2019_validation["official_local_prize"]
    / arc_2019_validation["prize"].astype(float)
)

arc_2019_validation
   pos           horse       prize  official_local_prize official_currency  \
0    1  Waldgeist (GB)  2573873.87               2857000               EUR   
1    2     Enable (GB)  1029729.73               1
…
```

### Cell 35

Matched: `racecard`

```text
# Check whether the same inferred USD conversion rate applies to other US
# meetings on the same calendar date.
#
# If 1.35 reconstructs plausible whole-dollar amounts at other US courses on
# 27 January 2018, that would suggest a date-wide source exchange rate.
# If it works only at Gulfstream Park, the rate may instead be attached to a
# meeting, feed, or separately processed racecard.
#
# We therefore load every populated US prize row on that date and measure how
# closely multiplication by 1.35 lands on whole-dollar amounts by course.

with sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True) as conn:
    same_date_us_prizes = pd.read_sql_query(
        f"""
        SELECT
            date,
            course,
            off,
            race_name,
            pos,
            CAST(prize AS REAL) AS stored_prize
        FROM data
        WHERE {DATA_ROW_PREDICATE}
          AND date = '2018-01-27'
          AND course LIKE '%(USA)%'
          AND TRIM(CAST(prize AS TEXT)) <> ''
        """,
        conn,
    )

same_date_us_prizes["reconstructed_usd"] = (
    same_date_us_prizes["stored_prize"] * 1.35
)

same_date_us_prizes["distance_from_nearest_dollar"] = (
    same_date_us_prizes["reconstructed_usd"]
    - same_date_us_prizes["reconstructed_usd"].round()
).abs()

same_date_us_rate_profile = (
    same_date_us_prizes
    .groupby("course", dropna=False)
    .agg(
        provisional_races=("off", "nunique"),
        populated_prize_rows=("stored_prize", "size"),
        rows_within_one_cent_of_whole_dollar=(
            "distance_from_nearest_dollar",
            lambda values: (values <= 0.01).sum(),
        ),
        maximum_distance_from_whole_dollar=(
            "distance_from_nearest_dollar",
            "max",
        ),
    )
    .reset_index()
…
```

### Cell 37

Matched: `verified`

```text
# Test the apparent USD conversion regime across January 2018.
#
# For each race date containing US prize data, we compare candidate exchange
# rates from 1.20 to 1.50 in increments of 0.01.
#
# The best candidate is the rate that makes the largest number of stored prize
# values reconstruct to within one cent of a whole US-dollar amount.
#
# This will show whether 1.35 was:
# - specific to the Pegasus weekend;
# - stable across a longer period; or
# - replaced by different rounded rates during the month.
#
# The inferred rates remain source-transformation candidates rather than
# independently verified historical market exchange rates.

with sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True) as conn:
    january_2018_us_prizes = pd.read_sql_query(
        f"""
        SELECT
            date,
            course,
            off,
            CAST(prize AS REAL) AS stored_prize
        FROM data
        WHERE {DATA_ROW_PREDICATE}
          AND date >= '2018-01-01'
          AND date < '2018-02-01'
          AND course LIKE '%(USA)%'
          AND TRIM(CAST(prize AS TEXT)) <> ''
        """,
        conn,
    )

candidate_rates = np.round(np.arange(1.20, 1.5001, 0.01), 2)

daily_best_rate_rows = []

for race_date, group in january_2018_us_prizes.groupby("date"):
    stored_values = group["stored_prize"].to_numpy(dtype=float)
    candidate_results = []

    for candidate_rate in candidate_rates:
        reconstructed = stored_values * candidate_rate
        residuals = np.abs(reconstructed - np.round(reconstructed))

        candidate_results.append(
            {
                "candidate_rate": candidate_rate,
                "matching_rows": int((residuals <= 0.01).sum()),
                "mean_residual": residuals.mean(),
                "maximum_residual"
…
```

### Cell 48

Matched: `external`

```text
## Reverse-engineering feasibility

External validation confirms that foreign prize schedules were converted into stored sterling amounts using a fixed multiplier applied consistently across every paid runner in a race.

For the 2018 United States population:

- 4,598 prize rows across 587 provisional races reconstruct to whole-dollar awards under a `1.35` multiplier;
- 16 prize rows across two Santa Anita races on 6 January reconstruct under `1.23`;
- one runner row remains unresolved.

The dominant `1.35` transformation covers 99.6316% of populated 2018 United States prize rows.

This demonstrates that the original local-currency amounts are potentially recoverable where:

1. the original currency can be assigned confidently;
2. one source multiplier applies consistently to a race, meeting, date or identifiable source batch;
3. reconstructed amounts satisfy strong monetary-rounding tests; and
4. exceptions are retained rather than forced.

However, Notebook 13 will not attempt to reconstruct every historical foreign amount. That would require a governed currency reference, inference rules across all jurisdictions and periods, and independent validation. It should be isolated as a later dependency rather than allowed to dominate the prize-field semantic audit.
```

### Cell 61

Matched: `external`

```text
## Findings summary

The `prize` field is usable, but only after separating three distinct cases.

### Confirmed direct values

- Great Britain values are runner-level prize amounts in GBP.
- Ireland values are runner-level prize amounts in EUR.
- Both can be converted exactly into integer minor units.
- No populated British or Irish value requires precision smaller than one penny or cent.

### Foreign source-presented values

Values from other jurisdictions are not safe to interpret directly as local currency.

External checks show that at least some foreign prize schedules were converted before storage. For example, selected United States and French races reconstruct to official local-currency prize schedules only after applying a source multiplier.

These multipliers appear to describe the source transformation, not necessarily the historical market exchange rate.

Foreign values must therefore remain preserved as source-presented amounts until the relevant jurisdiction and period have been validated.

### Missing values

Blank runner values are common and usually indicate that no prize amount was recorded for that runner.

They must remain null and must not be replaced with zero.

### Structural variation

The number of runners with recorded prize money varies by race, year and jurisdiction.

It must be treated as observed source data rather than inferred from finishing position, race type or a fixed number of paid places.

### Overall recommendation

The field should be retained with:

- the unchanged raw source value;
- a confirmed currency only where supported;
- an exact minor-unit amount only where safe;
- an explicit interpretation status; and
- preserved evidence for any later foreign-currency reconstruction.
```

### Cell 63

Matched: `external`

```text
# Create a compact decision table for the final notebook output.
#
# This turns the narrative findings into explicit modelling rules that can be
# reused when the staging schema is designed.
#
# The table deliberately separates:
# - what the source field means;
# - what can be parsed safely now;
# - what must remain unresolved; and
# - what must never be inferred automatically.

prize_field_decisions = pd.DataFrame(
    [
        {
            "area": "Field meaning",
            "decision": "Interpret as runner-level recorded prize money",
            "status": "Confirmed",
            "reason": (
                "Values vary between runners within the same race and usually "
                "follow finishing position or jurisdiction-specific payments."
            ),
        },
        {
            "area": "Great Britain",
            "decision": "Parse directly into integer pence with currency GBP",
            "status": "Confirmed",
            "reason": (
                "All 17,335 distinct populated British values convert exactly "
                "to integer pence."
            ),
        },
        {
            "area": "Ireland",
            "decision": "Parse euro-prefixed values into integer cents with currency EUR",
            "status": "Confirmed",
            "reason": (
                "All 1,624 distinct populated Irish values match the expected "
                "format and convert exactly to integer cents."
            ),
        },
        {
            "area": "Other jurisdictions",
            "decision": "Preserve as source-presented amount without assigning currency",
            "status": "Required",
            "reason": (
                "At least some foreign values were converted before storage, "
                "and the source multiplier
…
```

## `notebooks/14_runner_counts_numbers_and_entries.ipynb`

### Cell 14

Matched: `external`, `published result`, `checked against`, `verified`

```text
### External verification of the five exceptions

Because only five provisional races have fewer source rows than `ran`, each was
checked against a published result.

The exceptions do not share one universal explanation.

| Date | Course | Source `ran` | Stored rows | Published runners | External finding |
|---|---|---:|---:|---:|---|
| 2024-06-18 | Nantes (FR) | 8 | 7 | 8 | The missing starter, Saucats, fell. The seven stored rows are the seven finishers. |
| 2024-06-26 | Ohi (JPN) | 5 | 4 | 13 | The source stores only positions 1–4 and understates the actual field by eight runners. |
| 2024-09-03 | Morioka (JPN) | 5 | 4 | 12 | The source stores only positions 1–4 and understates the actual field by seven runners. |
| 2024-09-26 | Funabashi (JPN) | 6 | 2 | 6 | `ran` matches the published field, but positions 3–6 are absent. |
| 2025-10-09 | Ohi (JPN) | 16 | 15 | 16 | The missing runner, Tosen Thunder, failed to finish. |

This changes the interpretation of the source-wide equality result.

The agreement between source row count and `ran` in 189,038 races establishes
strong **internal consistency**, but it does not independently establish
complete runner coverage or prove that `ran` always means actual starters.

At least two races contain a repeated `ran` value that is demonstrably lower
than the published number of runners. Other races can therefore have equal
source row counts and `ran` while both omit part of the actual field.

Safe provisional interpretation:

- preserve `ran` as the source-presented race count;
- do not rename it `starter_count` without independent validation;
- distinguish internal row-count agreement from externally verified
  completeness;
- treat `source_rows = ran` as a consistency check, not proof of full coverage;
- retain explicit anomaly
…
```

### Cell 15

Matched: `external`

```text
## Stage 3 — Search for concealed partial-field races

The five visible exceptions show that internal agreement between source row
count and `ran` is not sufficient evidence of complete race coverage.

Two Japanese races are particularly important:

- their stored rows contain only the leading finishers;
- `ran` understates the externally published field size; and
- retained positive runner numbers exceed `ran`.

A similar race could be concealed among the 189,038 cases where source row
count equals `ran`: the source could store a truncated subset and repeat the
subset size in `ran`.

This stage searches for internally complete-looking races with warning signals.

The first warning pattern is:

- source row count equals `ran`;
- all stored positions are distinct positive integers;
- the positions form a complete sequence from 1 through `ran`;
- at least one positive `num` exceeds `ran`.

This is a candidate-warning rule, not proof of an incomplete field. Runner
numbers can exceed the final field size after withdrawals or other numbering
conventions. Any resulting group must be profiled by jurisdiction and inspected
before it is classified.
```

### Cell 17

Matched: `external`

```text
### Warning screen rejected

The proposed warning rule produced 58,336 races across 423 courses.

This is not a meaningful partial-field detector.

Runner numbers are card identifiers, not a sequence bounded by the final number
of starters. Withdrawals and non-runners routinely leave gaps, so a race with
`ran = 7` can legitimately retain runner numbers considerably above 7.

The output includes ordinary British, Irish, Australian, American and French
races where this explanation is sufficient. Consequently:

- `maximum num > ran` must not be treated as evidence of missing source rows;
- the candidate set must not be persisted as an anomaly table;
- this rule must not appear in a validator; and
- runner-number magnitude cannot independently establish field completeness.

The exercise nevertheless confirms an important semantic point: `num` is not an
ordinal position within the final field and cannot be validated against `ran`
using a simple upper bound.

The two externally contradicted Japanese races demonstrate that concealed
partial fields can exist, but the current source fields do not provide a
universal internal method for detecting them. Coverage equality must therefore
remain an internal-consistency measure rather than proof of external
completeness.
```

### Cell 23

Matched: `manual`, `manually`, `validation_status`, `nominatim`

```text
# Load the governed course-location reference created by Notebook 12.
#
# Notebook 14 should reuse this durable mapping rather than introduce another
# course-to-jurisdiction derivation. We first inspect its columns so that the
# subsequent join uses the documented reference structure correctly.

COURSE_LOCATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "course_locations.csv"
)

assert COURSE_LOCATIONS_PATH.exists(), (
    f"Course-location reference not found: {COURSE_LOCATIONS_PATH}"
)

course_locations = pd.read_csv(COURSE_LOCATIONS_PATH)

print(f"Reference rows: {len(course_locations):,}")
display(course_locations.head())
display(
    pd.DataFrame(
        {
            "column": course_locations.columns,
            "dtype": [
                str(course_locations[column].dtype)
                for column in course_locations.columns
            ],
        }
    )
)

Reference rows: 395

  candidate_course_label candidate_jurisdiction  \
0               La Plata              Argentina   
1                Palermo              Argentina   
2             San Isidro              Argentina   
3                 Albury              Australia   
4          Alice springs              Australia   

              physical_venue_name      locality  \
0           Hipódromo de La Plata      La Plata   
1  Hipódromo Argentino de Palermo  Buenos Aires   
2                             NaN           NaN   
3                             NaN           NaN   
4                             NaN           NaN   

                            region    country   latitude  longitude  \
0                     Buenos Aires  Argentina -34.901267 -57.943804   
1  Autonomous City of Buenos Aires  Argentina -34.566398 -58.425727   
2                              NaN        NaN
…
```

### Cell 29

Matched: `verified`

```text
### Rare duplicate-number cases

Individual inspection shows that duplicated positive `num` values outside the
main coupling jurisdictions do not all share one explanation.

Several French, Hong Kong and United Arab Emirates examples contain horses with
the same `num` but different:

- owners;
- trainers;
- starting prices; and
- draws.

These do not resemble the confirmed coupled-entry examples and are better
treated as ambiguous source-number collisions.

The Bahrain example is different. The two horses sharing `num = 5` also share
draw 1 and the same owner, which is consistent with a coupled or bracketed
entry. However, `Bahrain` did not join to the governed course-location
reference and therefore also exposes a separate reference-maintenance issue.

Governed conclusion:

- duplicated positive `num` is compatible with legitimate coupled entries;
- duplicated positive `num` does not by itself prove coupling;
- no universal uniqueness constraint is safe;
- no universal coupled-entry classification can be derived from `num` alone;
- duplicate-number groups outside known convention patterns should carry an
  ambiguous status unless independently verified;
- the Bahrain course identity requires reconciliation with the Notebook 12
  reference.
```

### Cell 39

Matched: `external`

```text
## Stage 8 — Safe staging representation

The investigation supports a conservative staging design.

### `ran`

`ran` is structurally clean and internally consistent:

- every stored value is an integer from 1 to 40;
- every runner row within a provisional race carries the same value;
- 189,038 races have source row count equal to `ran`;
- five races have fewer source rows than `ran`;
- no race has more source rows than `ran`.

However, external checks showed that internal agreement does not prove complete
field coverage. At least two Japanese races have a source `ran` value that is
lower than the published number of runners.

The field should therefore be stored as a source-presented race count rather
than renamed as an unqualified starter count.

### `num`

`num` has three raw representations:

- positive integer;
- integer zero;
- blank text.

Positive integers are not universally unique within a race. In several
jurisdictions they can represent coupled betting interests shared by multiple
horses. Elsewhere, duplicate positive values can be ambiguous source
collisions.

Blank text and integer zero are usually race-wide source states, but mixed
races also exist. Neither state should be interpreted as runner number zero or
used to reconstruct a missing number.

### Proposed staging fields

Race-level fields:

- `source_reported_ran`
- `source_runner_row_count`
- `source_ran_consistency_status`
- `source_row_count_vs_ran_status`
- `source_field_coverage_status`

Runner-level fields:

- `source_num_raw`
- `source_num_storage_class`
- `source_positive_runner_number`
- `source_num_state`
- `source_num_within_race_multiplicity`
- `source_num_uniqueness_status`

These are staging and governance fields. They do not redesign the final race or
runner keys.
```

### Cell 40

Matched: `external`, `verified`

```text
# Record the provisional governance decisions reached by Notebook 14.
#
# This table separates:
#
# - the raw source field;
# - the safe canonical or staging representation;
# - the status needed to preserve uncertainty; and
# - rules that must not be imposed.
#
# The table is still an analytical notebook output. It will later guide the
# reusable module, tests, validator and database-integration document.

runner_entry_governance = pd.DataFrame(
    [
        {
            "area": "reported race count",
            "source_field": "ran",
            "safe_representation": "source_reported_ran",
            "status_or_rule": "preserve integer source value",
            "provisional_constraint": "integer between 1 and 40",
            "must_not_assume": "unqualified starter count or complete field size",
        },
        {
            "area": "within-race ran consistency",
            "source_field": "ran",
            "safe_representation": "source_ran_consistency_status",
            "status_or_rule": (
                "consistent when every stored runner row in the provisional "
                "race carries one ran value"
            ),
            "provisional_constraint": (
                "current full-source baseline: all 189,043 races consistent"
            ),
            "must_not_assume": (
                "consistency proves external correctness"
            ),
        },
        {
            "area": "source row coverage",
            "source_field": "ran",
            "safe_representation": "source_row_count_vs_ran_status",
            "status_or_rule": (
                "equal, below, above, or not comparable because ran conflicts"
            ),
            "provisional_constraint": (
                "current baseline: 189,038 equal; 5 below; 0 above"
…
```

### Cell 41

Matched: `external`, `verified`

```text
### Refinement of external-status fields

External checking revealed that runner-row completeness and the correctness of
`ran` are related but separate questions.

For example:

- a race may have missing runner rows while `ran` remains externally correct;
- a race may have missing runner rows and an externally contradicted `ran`;
- a race may be externally verified as complete; or
- no external verification may have been performed.

One combined field would obscure these distinctions.

The staging model should therefore use:

#### `source_runner_coverage_status`

- `unverified`
- `internally_equal_to_ran`
- `known_partial`
- `externally_verified_complete`

#### `source_ran_external_status`

- `unverified`
- `externally_verified`
- `externally_contradicted`

`internally_equal_to_ran` remains an internal source observation. It does not
mean externally verified completeness.
```

### Cell 42

Matched: `external`, `verified`

```text
# Replace the combined external-coverage decision with two independent status
# fields: one for stored runner coverage and one for external validation of
# `ran`.

runner_entry_governance = runner_entry_governance.loc[
    runner_entry_governance["area"] != "external field coverage"
].copy()

external_governance_rows = pd.DataFrame(
    [
        {
            "area": "stored runner coverage",
            "source_field": "ran and source row count",
            "safe_representation": "source_runner_coverage_status",
            "status_or_rule": (
                "unverified, internally_equal_to_ran, known_partial, "
                "or externally_verified_complete"
            ),
            "provisional_constraint": (
                "internal equality is not external proof of completeness"
            ),
            "must_not_assume": (
                "source rows equal to ran means the full published field "
                "is present"
            ),
        },
        {
            "area": "external validation of ran",
            "source_field": "ran",
            "safe_representation": "source_ran_external_status",
            "status_or_rule": (
                "unverified, externally_verified, or externally_contradicted"
            ),
            "provisional_constraint": (
                "populate only from recorded external evidence"
            ),
            "must_not_assume": (
                "a structurally valid and repeated ran value is externally "
                "correct"
            ),
        },
    ]
)

runner_entry_governance = (
    pd.concat(
        [
            runner_entry_governance,
            external_governance_rows,
        ],
        ignore_index=True,
    )
)

display(runner_entry_governance)
                          area
…
```

### Cell 43

Matched: `external`

```text
## Stage 9 — Conclusions and limitations

### Conclusions

#### `ran`

The source field `ran` is structurally clean:

- all 1,851,285 stored values are integers;
- observed values range from 1 to 40;
- every provisional race carries one consistent `ran` value across its stored
  runner rows.

For 189,038 of 189,043 provisional races, the stored runner-row count equals
`ran`.

Five races contain fewer stored runner rows than `ran`. These are known partial
source records.

However, external checks also showed that internal equality does not prove that
the published field is complete. Some races can have:

- internally consistent `ran`;
- stored rows equal to `ran`; and
- an externally contradicted field size.

The safe interpretation is therefore:

> `ran` is a source-presented race-level count.

It must not be renamed or treated as an unqualified starter count without
external validation.

#### `num`

The source field `num` has three observed raw states:

- positive integer;
- integer zero;
- blank text.

A canonical positive runner number can be derived only when `num` is an integer
greater than zero.

Positive `num` is not universally unique within a race:

- 523 duplicated positive-number groups occur;
- 362 provisional races are affected;
- 1,084 runner rows are involved;
- up to four horses can share one positive `num`.

Some duplicated values are consistent with coupled or bracketed betting
interests. Others appear to be ambiguous source-number collisions. Duplicate
`num` alone therefore cannot establish coupling, duplication or error.

Blank and zero values are overwhelmingly race-wide source states:

- 863 races have all rows blank;
- 174 races have all rows zero;
- only 18 races mix states.

Blank text and integer zero must remain distinct raw states. Neither sh
…
```

### Cell 44

Matched: `external`

```text
# Record the final Notebook 14 decisions in a compact closeout table.
#
# These decisions are intended to drive the reusable module, unit tests,
# independent validator and database-integration documentation.

runner_counts_numbers_decisions = pd.DataFrame(
    [
        {
            "area": "ran meaning",
            "decision": "Preserve as source_reported_ran",
            "status": "Confirmed",
            "reason": (
                "Structurally consistent but not proven to equal complete "
                "published starter count"
            ),
        },
        {
            "area": "ran consistency",
            "decision": (
                "Derive within-race consistency and row-count comparison "
                "statuses"
            ),
            "status": "Confirmed",
            "reason": (
                "All races have one ran value; five have fewer stored rows "
                "than ran"
            ),
        },
        {
            "area": "external coverage",
            "decision": (
                "Keep runner coverage and ran external validation as separate "
                "statuses"
            ),
            "status": "Required",
            "reason": (
                "Internal equality does not prove external completeness or "
                "correctness"
            ),
        },
        {
            "area": "positive num",
            "decision": (
                "Derive source_positive_runner_number only for integers > 0"
            ),
            "status": "Confirmed",
            "reason": (
                "Positive values are structurally valid but not universally "
                "unique within race"
            ),
        },
        {
            "area": "blank num",
            "decision": (
                "Preserve
…
```

## `notebooks/15_beaten_distance_semantics.ipynb`

### Cell 20

Matched: `official result`

```text
# Reload every positive-distance winner row with the source comment included.
#
# Input grain:
#   One governed source runner row.
#
# Intermediate output grain:
#   One runner row where:
#       raw `pos = 1`
#       and (`ovr_btn > 0` or `btn > 0`).
#
# Final output grain:
#   One summary row per exploratory comment-evidence state.
#
# Purpose:
#   The four unequal winner rows were explained by amended-result comments.
#   This cell tests how much of the complete positive-winner population contains
#   similar explicit source evidence.
#
# Important:
#   - Raw `pos`, `ovr_btn`, `btn` and `comment` are preserved unchanged.
#   - The keyword classification is exploratory notebook logic only.
#   - A blank comment does not prove that no amendment occurred.
#   - No result is labelled erroneous.

positive_winner_comment_query = f"""
SELECT
    rowid AS source_rowid,
    date,
    course,
    off,
    race_id,
    race_name,
    type,
    horse,
    pos AS raw_pos,
    ovr_btn AS raw_ovr_btn,
    btn AS raw_btn,
    comment AS raw_comment
FROM {SOURCE_TABLE}
WHERE {DATA_ROW_PREDICATE}
  AND typeof(pos) IN ('integer', 'real')
  AND pos = 1
  AND (
      (
          typeof(ovr_btn) IN ('integer', 'real')
          AND ovr_btn > 0
      )
      OR
      (
          typeof(btn) IN ('integer', 'real')
          AND btn > 0
      )
  )
ORDER BY
    date,
    course,
    off,
    source_rowid
"""

# Execute through SQLite's read-only URI.
with sqlite3.connect(SOURCE_DATABASE_URI, uri=True) as connection:
    positive_winner_comment_profile = pd.read_sql_query(
        positive_winner_comment_query,
        connection,
    )

# Confirm that the reloaded population matches the earlier 500-row result.
if len(positive_winner_comment_profile) != 500:
    raise ValueError(
        "Pos
…
```

### Cell 22

Matched: `official result`

```text
# Inspect every positive-distance winner row without explicit amendment wording.
#
# Input grain:
#   One positive-distance winner runner row from
#   `positive_winner_comment_profile`.
#
# Output grain:
#   One residual runner row classified as either:
#       - `blank_comment`; or
#       - `no_explicit_amendment_evidence`.
#
# Purpose:
#   Explicit amendment wording explains 480 of the 500 positive winner rows.
#   This table exposes the remaining 20 rows so they are not silently treated
#   as equivalent to the explained population.
#
# Important:
#   - Raw source comments and distance values remain unchanged.
#   - The absence of a keyword match is not treated as evidence that the
#     official result was unchanged.
#   - No row is labelled as a source error.
#   - Physical source row order remains lineage only.

positive_winner_residual_rows = (
    positive_winner_comment_profile.loc[
        positive_winner_comment_profile["comment_evidence_state"]
        != "explicit_amended_result"
    ]
    .sort_values(
        ["date", "course", "off", "source_rowid"],
        kind="stable",
    )
    .reset_index(drop=True)
)

# Validate the residual count against the preceding summary:
# 17 blank comments plus 3 comments without an explicit amendment keyword.
if len(positive_winner_residual_rows) != 20:
    raise ValueError(
        "Expected 20 residual positive winner rows, "
        f"but found {len(positive_winner_residual_rows)}."
    )

display(
    positive_winner_residual_rows[
        [
            "source_rowid",
            "date",
            "course",
            "off",
            "race_id",
            "race_name",
            "type",
            "horse",
            "raw_pos",
            "raw_ovr_btn",
            "raw_btn",
            "comment_evidenc
…
```

### Cell 26

Matched: `manual`, `external`

```text
### Positive winner values and original finishing order

Complete race context explains 19 of the 20 positive-winner residual races.

In each of those 19 races:

* the official winner has a positive `ovr_btn` and `btn`;
* another runner carries zero in both fields; and
* the remaining distance sequence is consistent with the zero-valued runner occupying the original physical winning position.

The zero-valued runner may later appear as:

* second;
* third; or
* `DSQ`.

This establishes that explicit amendment wording in `comment` is not required for the distance fields to retain an original physical result.

Across the positive-winner population, the defensible interpretation is therefore:

> Positive distance values on a runner with official `pos = 1` ordinarily indicate that the horse was promoted to first after the physical finish, while `ovr_btn` and `btn` retained the original finishing-distance sequence.

The source fields can consequently describe different result stages:

* `pos` can represent the amended official placing;
* `ovr_btn` can remain anchored to the original physical winner;
* `btn` can remain anchored to the original physical finishing sequence.

This means that sorting solely by official `pos` will produce false arithmetic contradictions in amended-result races.

One residual race remains unresolved:

`2023-12-23 + Gulfstream Park (USA) + 9:36`

In that race:

* no runner carries zero in either distance field;
* the official winner has `ovr_btn = 4.25` and `btn = 4.25`;
* the official second has `ovr_btn = 4` and `btn = 4`;
* raw positions omit position 5;
* a runner has raw position 9 despite `ran = 8`.

The observed rows are compatible with an omitted or removed original winner, but the source alone does not prove that explanation. The race must
…
```

### Cell 27

Matched: `manual`, `manually`, `external`, `checked against`, `verified`

```text
### Manual verification: Gulfstream Park, 23 December 2023

The unresolved race was checked against external result evidence.

Race identity:

`2023-12-23 + Gulfstream Park (USA) + 9:36`

Race:

`Mr. Prospector Stakes`

The external result establishes that:

* nine runners competed;
* Sibelius finished first;
* Gilmore finished second;
* Dreaming Of Kona finished third;
* Long Range Toddy finished fourth;
* Great Navigator finished fifth; and
* the source extract omitted Great Navigator.

The source contains eight runner rows even though retained finishing positions extend to ninth place. The missing fifth-place runner explains the discontinuity in the supplied result population.

This is not an amended-winner case. Sibelius was the physical and official winner.

The positive distance values on the retained winner row cannot be interpreted safely from the incomplete source rows alone. The supplied distance sequence is misaligned because at least one result row is absent.

### Governance decision

The immutable raw source must remain unchanged.

The manually verified missing runner should be captured separately as governed supplementary result data and included during future database processing.

The supplementary record must preserve:

* candidate race identity;
* supplied `race_id`;
* missing horse identity;
* verified finishing position;
* external evidence and locator;
* access date;
* verification status;
* confidence;
* supplementation method; and
* a clear distinction between source-present and externally supplemented data.

The database build should therefore:

1. load all immutable source runner rows;
2. add the governed supplementary runner record;
3. retain a provenance flag showing that the row was absent from the source;
4. process the completed race populat
…
```

### Cell 33

Matched: `official result`

```text
### Complete-context review of multiple-zero races

The selected race contexts establish two distinct uses of `ovr_btn = 0` and `btn = 0`.

#### Race-wide zero distance coverage

Four reviewed races contain zero in both fields for every numeric finisher:

* Haydock, 17 December 2016;
* St Moritz, 6 February 2022;
* San Isidro, 25 May 2026 at 19:22;
* San Isidro, 25 May 2026 at 22:25.

Their finishing positions remain differentiated, but the distance fields contain no usable margin information.

These races must not be interpreted as mass dead heats. They represent unavailable or failed beaten-distance capture encoded as numeric zero.

#### Isolated zero-holder after an amended result

The 2019 Kentucky Derby contains one later-placed runner with zero in both fields:

* Maximum Security physically finished first;
* the official result placed him seventeenth;
* Country House became the official winner;
* the distance sequence remained anchored to Maximum Security as the physical winner.

This is consistent with the positive-winner examples reviewed earlier.

### Provisional rule

A later numeric finisher carrying `0 / 0` has no single source-wide meaning.

Interpretation requires race context:

* where all numeric finishers carry `0 / 0`, beaten-distance coverage is unavailable;
* where one runner carries `0 / 0` within an otherwise populated sequence, that runner may be the original physical winner in an amended result;
* other structures remain to be classified separately.

No zero value should be interpreted independently of the surrounding race.
```

### Cell 36

Matched: `manual`, `racecard`

```text
# Retrieve complete runner context for all 15 races classified as having
# multiple partial zero-holders.
#
# Input grain:
#   One governed source runner row.
#
# Output grain:
#   One source runner row from one of the 15 selected provisional races.
#
# Purpose:
#   Each selected race contains exactly two numeric finishers with zero in
#   both distance fields: normally the official winner and one later finisher.
#   Complete context is required to distinguish dead heats, amended results,
#   source defects and any other repeated convention.
#
# Important:
#   - Candidate race identity remains `date + course + off`.
#   - Raw source values and comments remain unchanged.
#   - Source row order is preserved for lineage only.
#   - No semantic classification is assigned in this cell.
#   - The complete bounded population of 15 races is displayed, not sampled.
# Show complete comment text in notebook tables.

#
# Purpose:
#   Pandas truncates long text columns by default, which hides the evidence
#   needed for manual race-level review.
#
# Effect:
#   Display only. No source values or dataframe contents are changed.

pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)

# Extract the 15 provisional race identities identified by the source-wide
# coverage classification.
partial_zero_race_keys = (
    both_zero_coverage_profile.loc[
        both_zero_coverage_profile[
            "both_zero_coverage_state"
        ].eq("multiple_partial_zero_holders"),
        ["date", "course", "off"],
    ]
    .drop_duplicates()
    .sort_values(
        ["date", "course", "off"],
        kind="stable",
    )
    .reset_index(drop=True)
)

# Validate the bounded population before querying complete race context.
if len(partial_zero_race_keys) != 15:
    raise V
…
```

### Cell 37

Matched: `manual`, `external`, `verified`, `official result`

```text
### Multiple partial zero-holders

Complete review resolved all 15 races containing exactly two numeric finishers with `ovr_btn = 0` and `btn = 0`.

#### Amended dead-heat results

Fourteen races represent a physical dead heat for first followed by an amended official result.

In these races:

* the two physical first-place finishers both retain `ovr_btn = 0` and `btn = 0`;
* one runner is recorded as official `pos = 1`;
* the other is recorded as official `pos = 2`; and
* the official separation arose through disqualification, demotion, interference or an award of the race.

Twelve races state this directly in the source comments.

The blank-comment Ascot and Deauville examples were confirmed through governed manual verification:

* `NB15-BTN-0002`;
* `NB15-BTN-0003`.

These races show that the distance fields may preserve a physical dead heat while `pos` records the amended official result.

#### Source-distance contradiction

One race does not follow that convention:

`2025-04-06 + Gavea (BRZ) + 7:35`

The source stores both Naturalizada and Gevrey-Chambertain at `0 / 0`. External results establish that Naturalizada won and Gevrey-Chambertain finished second, with a published winning margin of 16½ lengths.

This is therefore a defective source-distance sequence rather than a dead heat.

The contradiction is governed by:

`NB15-BTN-0004`

The immutable raw values must remain unchanged. The verified winning margin may be applied only through a governed downstream reconciliation layer.

### Resulting interpretation

The `multiple_partial_zero_holders` structure is highly diagnostic but not infallible:

* 14 of 15 races are amended physical dead heats;
* 1 of 15 is a verified source defect.

A pair of zero-distance finishers must therefore be interpreted using comments o
…
```

### Cell 38

Matched: `manual`, `official result`

```text
### Single zero-holder races

The largest `both_zero` group contains 322 races with exactly one numeric zero-holder.

In these races:

* one runner carries `ovr_btn = 0` and `btn = 0`;
* the remaining numeric finishers have populated nonzero distance values; and
* the zero-holder may occupy an official position later than first.

The reviewed Kentucky Derby example showed that this structure can preserve the original physical winner after an amended official result.

The next step measures how often the source comments explicitly explain the official placing change and identifies the residual cases that may require manual verification.
```

### Cell 40

Matched: `manual`, `external`

```text
# Retrieve complete context for the seven single-zero-holder races whose
# comments are populated but contain no amendment wording matched by the
# current regular expression.
#
# Input grain:
#   One governed source runner row.
#
# Output grain:
#   One source runner row from one of the seven selected provisional races.
#
# Purpose:
#   These races may contain explanatory wording that the bounded amendment
#   pattern failed to recognise. Complete comments must be reviewed before
#   deciding whether external manual verification is necessary.
#
# Important:
#   - Candidate race identity remains `date + course + off`.
#   - Raw comments and distance values remain unchanged.
#   - The seven-race population is complete, not sampled.
#   - No race is classified automatically in this cell.

# Select the complete bounded population of populated-comment residual races.
populated_single_zero_residual_keys = (
    single_zero_comment_profile.loc[
        single_zero_comment_profile[
            "comment_evidence_state"
        ].eq("populated_without_explicit_amendment"),
        ["date", "course", "off"],
    ]
    .drop_duplicates()
    .sort_values(
        ["date", "course", "off"],
        kind="stable",
    )
    .reset_index(drop=True)
)

# Validate the expected bounded population before retrieving full context.
if len(populated_single_zero_residual_keys) != 7:
    raise ValueError(
        "Expected seven populated-comment residual races, "
        f"but found {len(populated_single_zero_residual_keys)}."
    )

# Build a parameterised SQLite condition for the seven candidate race keys.
populated_single_zero_condition = " OR ".join(
    ["(date = ? AND course = ? AND off = ?)"]
    * len(populated_single_zero_residual_keys)
)

populated_single_zero_parameters = [
    val
…
```

### Cell 41

Matched: `manual`, `external`, `official result`

```text
### Populated-comment single-zero residuals

All seven single-zero-holder races with populated comments but no initially matched amendment phrase were resolved.

Five races contain sufficient explanation within the source comments:

* Ayr, 20 June 2015;
* Flemington, 12 March 2016;
* Laurel Park, 18 September 2021;
* Happy Valley, 20 November 2024;
* Sha Tin, 9 February 2025.

In each race:

* the runner carrying `ovr_btn = 0` and `btn = 0` passed the post first;
* that runner was subsequently placed second;
* the official winner was promoted from second; and
* the promoted official winner retains a positive distance from the original physical winner.

The original pattern did not match these races because the comments used wording such as:

* `finished first - placed second`; and
* `finished second - placed first`.

Two further races required governed manual verification:

* `NB15-BTN-0005` — Gulfstream Park, 11 April 2020;
* `NB15-BTN-0006` — Saratoga, 1 August 2025.

Both external checks confirm the same result-stage convention:

* the zero-holder crossed the line first;
* the official result later demoted that runner;
* the promoted winner retains a positive source distance.

All seven populated-comment residuals therefore support the interpretation that `pos` may represent the amended official result while `ovr_btn` and `btn` remain anchored to the physical finishing order.
```

### Cell 42

Matched: `manual`, `external`

```text
# Build a compact manual-verification queue for the 11 single-zero-holder
# races whose source comments are entirely blank.
#
# Input grain:
#   One governed source runner row from a single-zero-holder race.
#
# Output grain:
#   One summary row per provisional race requiring external verification.
#
# Purpose:
#   Manual research must use exact source identities rather than relying on
#   memory or shortened notebook prose. This table identifies:
#
#   - the candidate race identity;
#   - the supplied race name;
#   - the later-positioned zero-holder;
#   - the official source winner;
#   - the relevant raw positions and distances; and
#   - the source runner count.
#
# Important:
#   - Candidate race identity remains `date + course + off`.
#   - Raw source values remain unchanged.
#   - `zero_holder_horse` is an observed source role, not yet a confirmed
#     physical-winner classification.
#   - Each external lookup must later be recorded separately in the governed
#     manual-verification register.

# Select the complete bounded population of all-comments-blank residual races.
blank_single_zero_race_keys = (
    single_zero_comment_profile.loc[
        single_zero_comment_profile[
            "comment_evidence_state"
        ].eq("all_comments_blank"),
        ["date", "course", "off"],
    ]
    .drop_duplicates()
    .sort_values(
        ["date", "course", "off"],
        kind="stable",
    )
    .reset_index(drop=True)
)

# Validate the expected residual population.
if len(blank_single_zero_race_keys) != 11:
    raise ValueError(
        "Expected 11 all-comments-blank residual races, "
        f"but found {len(blank_single_zero_race_keys)}."
    )

# Build a parameterised SQLite condition for the 11 race identities.
blank_single_zero_condition = " OR ".join(
…
```

### Cell 43

Matched: `manual`, `manually`, `external`, `published result`, `verified`, `official result`

```text
### Blank-comment single-zero-holder races

All 11 single-zero-holder races with entirely blank source comments were manually verified and captured in the governed manual-verification register.

The checks produced two distinct outcomes.

#### Amended official results

Eight races confirm the established result-stage convention:

* the runner carrying `ovr_btn = 0` and `btn = 0` passed the post first;
* that runner was subsequently disqualified or demoted;
* another runner became the official winner; and
* the promoted official winner retains a positive source distance from the physical winner.

The governed verification identifiers are:

* `NB15-BTN-0008`;
* `NB15-BTN-0009`;
* `NB15-BTN-0011`;
* `NB15-BTN-0012`;
* `NB15-BTN-0014`;
* `NB15-BTN-0015`;
* `NB15-BTN-0016`;
* `NB15-BTN-0017`.

These races provide external confirmation that official `pos` and the finishing stage represented by the distance fields may differ.

#### Source-distance defects

Three races do not contain an identified amended result:

* Saint-Cloud, 11 April 2017;
* Gulfstream Park, 9 April 2020;
* Longchamp, 31 August 2023.

Their published results show ordinary finishing orders incompatible with the later-positioned runner carrying the zero-distance reference.

The governed verification identifiers are:

* `NB15-BTN-0007`;
* `NB15-BTN-0010`;
* `NB15-BTN-0013`.

These cases must be preserved as raw source contradictions and corrected only through a governed downstream reconciliation layer.

### Completed single-zero-holder finding

Across the 322 single-zero-holder races:

* 304 are explained by explicit source-comment evidence;
* five additional populated-comment races were resolved through broader comment review;
* two populated-comment races required external verification;
* eight blank-comment
…
```

### Cell 47

Matched: `racing post`

```text
# Retrieve complete race context for every `btn_zero_only` row whose official
# position is unique within its provisional race.
#
# Input grain:
#   One governed source runner row.
#
# Output grain:
#   One source runner row from a provisional race containing at least one
#   unique-position `btn_zero_only` runner.
#
# Purpose:
#   Repeated official positions explain 2,702 of the 2,750 rows. The remaining
#   48 runner rows are structurally exceptional and require complete race
#   context before any general semantic rule is assigned.
#
# Important:
#   - Candidate race identity remains `date + course + off`.
#   - Raw source values and comments remain unchanged.
#   - The selected 48 rows may occur in fewer than 48 races.
#   - Complete runner context is returned for every affected race.
#   - This cell performs evidence retrieval only; it does not automatically
#     classify the exceptional rows.

unique_btn_zero_query = f"""
WITH governed_rows AS (
    SELECT
        rowid AS source_rowid,
        date,
        course,
        off,
        race_id,
        race_name,
        type,
        horse,
        pos AS raw_pos,
        ovr_btn AS raw_ovr_btn,
        btn AS raw_btn,
        ran AS raw_ran,
        num AS raw_num,
        comment AS raw_comment
    FROM {SOURCE_TABLE}
    WHERE {DATA_ROW_PREDICATE}
),
numeric_position_counts AS (
    SELECT
        date,
        course,
        off,
        raw_pos,
        COUNT(*) AS rows_at_position
    FROM governed_rows
    WHERE typeof(raw_pos) IN ('integer', 'real')
      AND raw_pos > 0
    GROUP BY
        date,
        course,
        off,
        raw_pos
),
selected_races AS (
    SELECT DISTINCT
        rows.date,
        rows.course,
        rows.off
    FROM governed_rows AS rows
    INNER JOIN numeric_position_
…
```

### Cell 50

Matched: `official result`

```text
### Same-distance counterpart result

All 48 unique-position `btn = 0` rows have at least one other runner in the same race with the identical stored `ovr_btn`.

The observed structures are:

* 31 rows with one numeric same-distance counterpart;
* 13 rows with multiple same-distance counterparts;
* four rows with a nonnumeric same-distance counterpart such as `DSQ`.

No selected row lacks an exact same-distance counterpart.

This establishes that `btn = 0` is not an isolated missing value in this population. It records membership of a same-distance group, even where the official `pos` values no longer show a repeated placing.

The next step determines how those same-distance counterparts relate to the selected runner in the official result order.
```

### Cell 51

Matched: `official result`

```text
# Classify the official-position relationship between each of the 48 selected
# unique-position `btn = 0` runners and its same-distance counterparts.
#
# Input grain:
#   One selected exceptional runner joined to one same-distance counterpart.
#
# Output grain:
#   One summary row per observed counterpart-position relationship.
#
# Purpose:
#   We have established that every exceptional zero adjacent margin belongs
#   to an exact same-distance group. This cell determines whether the matching
#   runner is adjacent in the official result, separated by amended placings,
#   nonnumeric, or part of a larger grouped-distance tail.
#
# Important:
#   - Raw source values remain unchanged.
#   - Numeric position differences describe official source positions only.
#   - A difference of -1 means the counterpart is one official place ahead.
#   - A difference of +1 means the counterpart is one official place behind.
#   - Nonnumeric counterparts remain a separate structural category.
#   - These structures are descriptive and do not themselves prove why the
#     distance was shared.

# Start from the same-distance counterpart join already produced.
counterpart_relationships = same_distance_counterparts.copy()

# Derive the official numeric position difference where both positions are
# numeric. Positive means the counterpart is officially behind the selected
# runner; negative means it is officially ahead.
counterpart_relationships["official_position_difference"] = (
    counterpart_relationships["counterpart_numeric_pos"]
    - counterpart_relationships["selected_numeric_pos"]
)

# Assign one descriptive relationship per selected-counterpart pair.
counterpart_relationships["position_relationship"] = (
    "nonadjacent_numeric_counterpart"
)

counterpart_relationships.loc[
…
```

### Cell 53

Matched: `external`

```text
# Assign one mutually exclusive same-distance structure to each of the 48
# unique-position runners with positive `ovr_btn` and zero `btn`.
#
# Input grain:
#   One selected exceptional runner with all same-distance counterparts.
#
# Output grain:
#   One analytical row per selected runner, followed by a summary of the
#   mutually exclusive structures.
#
# Purpose:
#   Pair-level relationship counts include several counterparts for runners
#   belonging to larger same-distance groups. This cell reduces the evidence
#   to one structural classification per selected runner.
#
# Classification precedence:
#   1. A nonnumeric counterpart indicates that a matching runner has been
#      removed from the numeric official sequence, commonly through DSQ.
#   2. More than one counterpart indicates a multi-runner distance plateau.
#   3. A sole immediately preceding counterpart represents an adjacent
#      same-distance pair.
#   4. Any remaining sole numeric counterpart is a separated same-distance
#      pair whose official positions are nonadjacent.
#
# Important:
#   - These are structural descriptions, not final sporting interpretations.
#   - Raw source values remain unchanged.
#   - Comment evidence is attached separately and does not override structure.

# Aggregate the pair-level relationships to one row per selected runner.
selected_distance_group_structure = (
    counterpart_relationships
    .groupby(
        [
            "selected_source_rowid",
            "date",
            "course",
            "off",
            "selected_horse",
            "selected_raw_pos",
            "numeric_ovr_btn",
        ],
        as_index=False,
        dropna=False,
    )
    .agg(
        counterpart_count=(
            "counterpart_source_rowid",
            "size",
…
```

### Cell 54

Matched: `external`

```text
### Residual separated same-distance pair

Only one of the 48 unique-position zero-margin rows remains without explicit tie or amendment evidence:

* Morphettville, 16 May 2015;
* Mighty Maher, stored position 12;
* Cinnamon Carter, stored position 10;
* both stored at `ovr_btn = 8.75`.

The race’s supplied position sequence is itself irregular:

* position 10 occurs twice;
* positions 8 and 13 are absent;
* the position-11 runner is stored at a different overall distance.

The available source and external evidence do not establish whether Mighty Maher physically tied with Cinnamon Carter, whether later amendments disrupted the position sequence, or whether the supplied position or distance values are defective.

This race should therefore remain an unresolved source-structure exception rather than being forced into the amended-tie interpretation.
```

### Cell 55

Matched: `manual`, `external`, `verified`, `official result`

```text
## Conclusion

The source fields `ovr_btn` and `btn` both contain beaten-distance information, but they operate at different levels.

### `ovr_btn`

`ovr_btn` records the runner’s cumulative distance from the physical first-place reference used by the source result.

For ordinary results:

* the physical winner carries `ovr_btn = 0`;
* later finishers carry positive cumulative distances; and
* nonfinishers use the text sentinel `-`.

The field does not always align with the final official placing stored in `pos`.

Where a result is amended after the finish:

* `pos` may record the official revised order;
* `ovr_btn` may continue to reflect the physical finishing order; and
* the official winner may therefore carry a positive `ovr_btn`.

A later-positioned runner carrying `ovr_btn = 0` is highly diagnostic of a physical winner or dead-heat participant subsequently demoted, disqualified or separated by an amended result. It is not infallible because a small number of verified source defects also produce this structure.

### `btn`

`btn` records the margin from the preceding physical finisher or preceding stored distance group rather than the cumulative distance from the winner.

For ordinary sequential finishers:

* `btn` is positive;
* cumulative `ovr_btn` generally increases through the finishing order; and
* `btn` represents the incremental separation contributing to that cumulative distance.

A numeric `btn = 0` indicates that the runner has no recorded separation from at least one other runner carrying the same stored `ovr_btn`.

This commonly represents:

* an official dead heat;
* a physical dead heat later separated by an amended result;
* a multi-runner same-distance plateau; or
* grouped, rounded or capped distance presentation.

It does not, by itself, prove th
…
```

### Cell 57

Matched: `manual`, `external`

```text
## Closeout evidence and persisted outputs

**Manual-verification decision: `captured`.**

Notebook 15 used bounded external verification to distinguish amended results,
physical dead heats, omitted runners and confirmed source-distance defects.
Reusable provenance is preserved in `data/reference/manual_verifications.csv`
under verification IDs `NB15-BTN-0001` through `NB15-BTN-0017`.

The immutable source remains unchanged. External evidence permits only governed
downstream reconciliation, review classification or documented exception
handling.

The following cell persists a compact notebook decision table. This is not a
copy of bulk source data. It records the field-level conclusions, exception
rules and closeout evidence required by downstream implementation.

`NOTEBOOK_15_CLOSEOUT_PERSISTENCE_V1`
```

### Cell 58

Matched: `verified`

```text
# Persist the compact governed decision output for Notebook 15.
#
# Input grain:
#   One final notebook decision assembled from the completed investigation.
#
# Output grain:
#   One row per beaten-distance interpretation or governed exception rule.
#
# Raw versus derived:
#   This cell does not rewrite any source runner row. It persists only the
#   notebook's derived semantic decisions and their implementation status.
#
# Assumptions deliberately not made:
#   - `btn = 0` is not treated as proof of an official dead heat.
#   - positive winner distance is not automatically corrected.
#   - later zero overall distance is not automatically corrected.
#   - the text sentinel `-` is not converted to numeric zero.

from pathlib import Path

import pandas as pd

NOTEBOOK_15_OUTPUT_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "derived" / "notebook_15_beaten_distance_semantics"
)
NOTEBOOK_15_DECISIONS_PATH = (
    NOTEBOOK_15_OUTPUT_DIRECTORY / "beaten_distance_field_decisions.csv"
)

NOTEBOOK_15_OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

beaten_distance_field_decisions = pd.DataFrame(
    [
        {
            "decision_id": "NB15-DIST-001",
            "raw_field": "ovr_btn",
            "interpreted_meaning": (
                "cumulative distance from the source physical-finish "
                "first-place reference"
            ),
            "status": "confirmed",
            "implementation_action": "parse numeric values and preserve raw value",
            "limitation": (
                "official pos can reflect an amended result while distance "
                "continues to reflect the physical finish"
            ),
        },
        {
            "decision_id": "NB15-DIST-002",
            "raw_field": "btn",
            "interpreted_meaning": (
…
```

### Cell 59

Matched: `verified`

```text
# Reload and validate the persisted Notebook 15 decision output.
#
# Purpose:
#   The notebook wrap-up procedure requires every written file to be reloaded
#   and validated rather than trusting the in-memory dataframe.
#
# Output grain:
#   One persisted decision row per governed beaten-distance rule.

reloaded_beaten_distance_field_decisions = pd.read_csv(
    NOTEBOOK_15_DECISIONS_PATH,
    keep_default_na=False,
)

if len(reloaded_beaten_distance_field_decisions) != 7:
    raise ValueError(
        "Expected seven persisted Notebook 15 decisions, "
        f"found {len(reloaded_beaten_distance_field_decisions)}."
    )

if set(reloaded_beaten_distance_field_decisions.columns) != required_decision_columns:
    raise ValueError("Reloaded Notebook 15 decision schema is invalid.")

if reloaded_beaten_distance_field_decisions["decision_id"].duplicated().any():
    raise ValueError("Reloaded Notebook 15 decision IDs are not unique.")

expected_statuses = {
    "confirmed",
    "confirmed_with_limitation",
    "governed_exception",
    "required",
}
observed_statuses = set(reloaded_beaten_distance_field_decisions["status"])

if not observed_statuses <= expected_statuses:
    raise ValueError(
        "Reloaded Notebook 15 decisions contain an invalid status: "
        f"{sorted(observed_statuses - expected_statuses)}"
    )

display(reloaded_beaten_distance_field_decisions)

     decision_id    raw_field  \
0  NB15-DIST-001      ovr_btn   
1  NB15-DIST-002          btn   
2  NB15-DIST-003  ovr_btn|btn   
3  NB15-DIST-004      ovr_btn   
4  NB15-DIST-005      ovr_btn   
5  NB15-DIST-006          btn   
6  NB15-DIST-007  ovr_btn|btn   

                                                                                                  interpreted_meaning  \
0
…
```

## `notebooks/16_race_classification_and_eligibility.ipynb`

### Cell 7

Matched: `manual`

```text
# Input grain:
#   Governed source runner rows from SQLite table `data`, restricted by
#   DATA_ROW_PREDICATE = "rowid <> 1".
#
#   Race-level classification values come from `jurisdiction_frame`, where
#   governed course identity and jurisdiction have already been attached.
#
# Output grain:
#   1. One parser-status row per exact raw age_band value.
#   2. One age-consistency summary row per raw age_band value.
#   3. One detailed row per runner whose recorded age falls outside the parsed
#      age-band limits.
#   4. One sex-rest consistency summary row per raw sex_rest value.
#   5. One detailed row per runner whose raw sex value is not admitted by the
#      provisional sex-rest token mapping.
#
# Purpose:
#   Test whether `age_band` and `sex_rest` behave like eligibility conditions
#   by comparing them with the actual recorded characteristics of runners in
#   the same race.
#
# Raw versus derived values:
#   Raw race and runner values remain unchanged.
#
#   Derived age-band components are limited to exact observed formats:
#   - `Nyo`       -> minimum age N and maximum age N;
#   - `Nyo+`      -> minimum age N and no stated maximum;
#   - `N-Myo`     -> minimum age N and maximum age M.
#
#   Derived sex-rest membership is provisional and based only on the observed
#   source abbreviations:
#   - F     -> F;
#   - M     -> M;
#   - F & M -> F or M;
#   - C & G -> C or G;
#   - C & F -> C or F.
#
# Assumptions deliberately not made:
#   - blank age_band is not parsed or inferred from race_name;
#   - runner age zero or malformed age is not silently corrected;
#   - an out-of-band runner is not automatically declared ineligible;
#   - amendments, substitutions and source errors remain possible;
#   - blank sex_rest is not interpreted as unrestricted in this cell;
…
```

### Cell 9

Matched: `external`

```text
# Input grain:
#   Runner-level `runner_eligibility` rows produced by the age and sex-rest
#   consistency stage.
#
# Output grain:
#   1. One row per age-band contradiction direction and signed age difference.
#   2. One row per jurisdiction, calendar month and signed age difference.
#   3. One row per contradictory provisional race with its dominant difference.
#   4. One detailed row for contradictions whose difference is greater than
#      one year in either direction.
#
# Purpose:
#   Distinguish likely calendar or jurisdictional age-convention differences
#   from isolated source defects.
#
#   A systematic difference of exactly one year across every runner in a race
#   may indicate that the race eligibility age and stored runner age use
#   different birthday conventions. Larger or internally mixed differences
#   require separate review.
#
# Raw versus derived values:
#   Raw runner age and raw age_band remain unchanged.
#
#   Derived values are limited to:
#   - the signed distance from the relevant permitted age boundary;
#   - calendar month extracted from the raw race date;
#   - per-race counts and dominant difference values;
#   - flags distinguishing uniform and mixed contradiction patterns.
#
# Assumptions deliberately not made:
#   - a one-year difference is not automatically corrected;
#   - Southern Hemisphere or jurisdictional birthday rules are not assigned
#     without external verification;
#   - the race date is not used to recompute horse age;
#   - large differences are not automatically treated as horse-age errors;
#   - an internally uniform race is not automatically treated as valid.
#
# Validation and failure behaviour:
#   The cell fails if:
#   - `runner_eligibility` is unavailable;
#   - the contradiction population differs from 958 r
…
```

### Cell 10

Matched: `external`

```text
# Input grain:
#   Runner-level `runner_eligibility` rows produced by the age and sex-rest
#   consistency stage.
#
# Output grain:
#   1. One row per age-band contradiction direction and signed age difference.
#   2. One row per jurisdiction, calendar month and signed age difference.
#   3. One row per contradictory provisional race with its dominant difference.
#   4. One detailed row for contradictions whose difference is greater than
#      one year in either direction.
#
# Purpose:
#   Distinguish likely calendar or jurisdictional age-convention differences
#   from isolated source defects.
#
#   A systematic difference of exactly one year across every runner in a race
#   may indicate that the race eligibility age and stored runner age use
#   different birthday conventions. Larger or internally mixed differences
#   require separate review.
#
# Raw versus derived values:
#   Raw runner age and raw age_band remain unchanged.
#
#   Derived values are limited to:
#   - the signed distance from the relevant permitted age boundary;
#   - calendar month extracted from the raw race date;
#   - per-race counts and dominant difference values;
#   - flags distinguishing uniform and mixed contradiction patterns.
#
# Assumptions deliberately not made:
#   - a one-year difference is not automatically corrected;
#   - Southern Hemisphere or jurisdictional birthday rules are not assigned
#     without external verification;
#   - the race date is not used to recompute horse age;
#   - large differences are not automatically treated as horse-age errors;
#   - an internally uniform race is not automatically treated as valid.
#
# Validation and failure behaviour:
#   The cell fails if:
#   - `runner_eligibility` is unavailable;
#   - the contradiction population differs from 958 r
…
```

### Cell 12

Matched: `external`

```text
## Age-band semantics and runner-age consistency

The source `age_band` field is structurally consistent and fully parseable across the current extract.

Observed forms are limited to:

- exact ages such as `2yo`, `3yo`, `4yo`;
- open-ended minimum ages such as `3yo+`, `4yo+`, `5yo+`;
- closed ranges such as `3-5yo`, `4-6yo`, `5-7yo`;
- 13 blank race values.

All 27 populated raw forms matched one of these syntactic families without requiring correction.

The field can therefore be parsed safely into:

- raw source value;
- syntax type;
- minimum stated age;
- maximum stated age where explicitly present;
- whether the source explicitly includes a `+`.

However, a literal comparison with the runner-level source `age` field produced 958 apparent contradictions across 183 provisional races.

These contradictions are not uniform:

- some runners are one year outside the stated band;
- some races contain several older ages despite an exact-age label such as `3yo` or `4yo`;
- some contradictions are concentrated by jurisdiction and race;
- one runner has an obviously implausible recorded age of `31`;
- only one contradictory race showed a visible disagreement between structured `age_band` and age text in `race_name`:
  - Compiegne, 16 May 2017, 13:35;
  - structured `age_band`: `5yo`;
  - race name: `Prix du Morbihan (Hurdle) (Claimer) (5yo+) (Turf)`.

The race-name comparison otherwise showed that the structured field usually repeats the source-presented age expression exactly. The apparent contradictions therefore cannot be explained simply as widespread extraction errors from `race_name`.

### Analytical conclusion

`age_band` is safe to treat as a structured representation of the source-presented race age condition.

It is not yet safe to treat every parsed value as a uni
…
```

### Cell 14

Matched: `manual`, `external`, `published result`, `verified`

```text
## Age-band semantics and runner-age consistency

The source `age_band` field is structurally consistent and fully parseable across the current extract.

Observed forms are limited to:

- exact ages such as `2yo`, `3yo`, `4yo`;
- open-ended minimum ages such as `3yo+`, `4yo+`, `5yo+`;
- closed ranges such as `3-5yo`, `4-6yo`, `5-7yo`;
- 13 blank race values.

All 27 populated raw forms matched one of these syntactic families without requiring correction.

The field can therefore be parsed safely into:

- raw source value;
- syntax type;
- minimum stated age;
- maximum stated age where explicitly present;
- whether the source explicitly includes a `+`.

However, a literal comparison with the runner-level source `age` field produced 958 apparent contradictions across 183 provisional races.

These contradictions are not uniform:

- some runners are one year outside the stated band;
- some races contain several older ages despite an exact-age label such as `3yo` or `4yo`;
- some contradictions are concentrated by jurisdiction and race;
- some runner ages are individually implausible;
- one race showed a visible disagreement between structured `age_band` and the age expression embedded in `race_name`.

The race-name comparison otherwise showed that the structured field usually repeats the source-presented age expression exactly. The apparent contradictions therefore cannot be explained as one general extraction failure.

## Manual and external verification decision

Manual-verification status for this notebook: `captured`.

Four bounded checks have been preserved in `data/reference/manual_verifications.csv`.

### `NB16-AGE-0001` — Compiegne age-band defect

Race:

- date: 16 May 2017;
- course: Compiegne (FR);
- off: 13:35;
- race: Prix du Morbihan.

Observed source values:
…
```

### Cell 16

Matched: `manual`

```text
# Input grain:
#   Runner-level rows from `runner_eligibility`, with one row per retained
#   source runner.
#
# Output grain:
#   1. One row per raw `sex_rest` and raw runner `sex` combination.
#   2. One row per `sex_rest`, jurisdiction, race type and runner-sex value.
#   3. One row per `sex_rest`, runner age and runner-sex value.
#   4. Sample races for rare or apparently contradictory combinations.
#
# Purpose:
#   Investigate what the race-level `sex_rest` field appears to represent,
#   without assuming that its letters can be compared literally with the
#   runner-level `sex` field.
#
# Important semantic caution:
#   The two source fields use different vocabularies:
#
#   - runner `sex` contains horse sex codes such as C, F, G, H, M and R;
#   - race `sex_rest` contains labels such as F, M, F & M, C & F and C & G.
#
#   In racing terminology, labels such as F, M, C and G may represent words
#   such as filly, mare, colt and gelding. Their relationship to a runner's
#   stored code can also depend on age, jurisdiction and source convention.
#
#   This cell therefore profiles combinations descriptively. It does not
#   classify a runner as eligible or ineligible.
#
# Raw versus derived values:
#   Raw `sex_rest`, runner `sex`, runner `age`, jurisdiction and race type are
#   preserved unchanged.
#
#   Display columns are derived only to make blank values visible.
#
# Assumptions deliberately not made:
#   - `sex_rest = F` is not treated as requiring runner `sex = F`;
#   - `sex_rest = M` is not treated as requiring runner `sex = M`;
#   - fillies and mares are not distinguished solely from the stored sex code;
#   - colts and horses are not distinguished solely from age;
#   - rare combinations are not automatically classified as source errors;
#   - blank `sex_r
…
```

### Cell 17

Matched: `manual`

```text
# Input grain:
#   Runner-level rows from `runner_eligibility`, with one row per retained
#   source runner.
#
# Output grain:
#   1. One row per raw `sex_rest` and raw runner `sex` combination.
#   2. One row per `sex_rest`, jurisdiction, race type and runner-sex value.
#   3. One row per `sex_rest`, runner age and runner-sex value.
#   4. Sample races for rare or apparently contradictory combinations.
#
# Purpose:
#   Investigate what the race-level `sex_rest` field appears to represent,
#   without assuming that its letters can be compared literally with the
#   runner-level `sex` field.
#
# Important semantic caution:
#   The two source fields use different vocabularies:
#
#   - runner `sex` contains horse sex codes such as C, F, G, H, M and R;
#   - race `sex_rest` contains labels such as F, M, F & M, C & F and C & G.
#
#   In racing terminology, labels such as F, M, C and G may represent words
#   such as filly, mare, colt and gelding. Their relationship to a runner's
#   stored code can also depend on age, jurisdiction and source convention.
#
#   This cell therefore profiles combinations descriptively. It does not
#   classify a runner as eligible or ineligible.
#
# Raw versus derived values:
#   Raw `sex_rest`, runner `sex`, runner `age`, jurisdiction and race type are
#   preserved unchanged.
#
#   Display columns are derived only to make blank values visible.
#
# Assumptions deliberately not made:
#   - `sex_rest = F` is not treated as requiring runner `sex = F`;
#   - `sex_rest = M` is not treated as requiring runner `sex = M`;
#   - fillies and mares are not distinguished solely from the stored sex code;
#   - colts and horses are not distinguished solely from age;
#   - rare combinations are not automatically classified as source errors;
#   - blank `sex_r
…
```

### Cell 18

Matched: `external`, `verified`

```text
# Input grain:
#   One row per provisional race from `jurisdiction_frame`.
#
# Output grain:
#   1. One row per race with a populated `sex_rest`.
#   2. One row per structured `sex_rest` and detected race-name sex phrase.
#   3. One row per race where the structured field and race-name wording
#      appear inconsistent.
#
# Purpose:
#   Test whether the structured `sex_rest` field reproduces the sex-restriction
#   wording embedded in `race_name`, and identify bounded source anomalies for
#   later external verification.
#
# Interpretation boundary:
#   This comparison concerns two race-level source representations.
#   It does not determine individual runner eligibility and does not compare
#   `sex_rest` literally with the runner-level `sex` code.
#
# No source or reference data is written or modified.

required_prior_names = [
    "jurisdiction_frame",
    "sex_restriction_runner_frame",
]

missing_prior_names = [
    name
    for name in required_prior_names
    if name not in globals()
]

if missing_prior_names:
    raise RuntimeError(
        "Run the preceding jurisdiction and sex-restriction stages first. "
        f"Missing variables: {missing_prior_names}"
    )

required_race_columns = {
    "date",
    "course",
    "off",
    "race_name",
    "type",
    "sex_rest",
    "jurisdiction",
}

missing_race_columns = sorted(
    required_race_columns
    - set(jurisdiction_frame.columns)
)

if missing_race_columns:
    raise RuntimeError(
        "`jurisdiction_frame` is missing required columns: "
        f"{missing_race_columns}"
    )

sex_restricted_races = (
    jurisdiction_frame.loc[
        jurisdiction_frame[
            "sex_rest"
        ].astype("string").str.strip().ne(""),
        [
            "date",
            "course",
            "off",
…
```

### Cell 21

Matched: `external`

```text
## Sex-restriction semantics

The source fields `sex_rest` and runner `sex` use related racing terminology but operate at different grains.

Runner `sex` records a runner-level category, including:

- `C` — colt;
- `F` — filly;
- `G` — gelding;
- `H` — horse or older entire male;
- `M` — mare;
- `R` — rig.

Rare values such as `B` and `BB` remain unresolved source codes and must not be interpreted without separate evidence.

The race-level `sex_rest` field contains:

- `F`;
- `M`;
- `F & M`;
- `C & G`;
- `C & F`;
- blank.

### Runner composition

The dominant runner compositions support several straightforward source meanings:

- `C & G` predominantly contains colts and geldings;
- `F & M` predominantly contains fillies and mares;
- `C & F` contains runners coded as colts in the five observed races;
- `F` predominantly contains fillies, with mares and some male-coded runners;
- `M` predominantly contains mares, with some younger runners coded as fillies.

Runner `sex` must not be compared literally with `sex_rest`.

A filly can later be recorded as a mare, and a colt can later be recorded as a horse. The race-condition wording and runner-level category therefore need not use the same age-specific term.

Rare incompatible-looking combinations remain review candidates rather than automatic eligibility failures.

### Structured field versus race-name wording

Race-name comparison showed that the explicit combined values generally reproduce the visible race wording:

- all five `C & F` races explicitly say Colts & Fillies;
- 2,163 `C & G` races explicitly say Colts & Geldings;
- 3,797 `F & M` races explicitly say Fillies & Mares.

However, the raw value `F` is overloaded.

Among races stored as `F`:

- 221 race names explicitly say Colts & Fillies;
- 16 race names explicitl
…
```

### Cell 23

Matched: `manual`, `external`

```text
## Overall conclusion and governed field decisions

Notebook 16 investigated the source fields used to describe race classification and eligibility:

- `race_name`;
- `type`;
- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`.

The bounded question was:

> What do these fields represent, how do they relate to one another, and which values can be interpreted or derived safely?

The source supports reliable structural parsing for several fields, but it does not support one universal classification or eligibility model across every jurisdiction.

## Final field decisions

| Field | Safe source meaning | Safe derived treatment | Unsafe treatment | Status |
|---|---|---|---|---|
| `race_name` | Source-presented race title and embedded descriptive wording | Preserve unchanged; use narrowly for supporting phrase extraction and anomaly review | Treat every detected word or phrase as an official condition | Confirmed raw source field |
| `type` | Source race-type category | Preserve canonical observed values: `Flat`, `Hurdle`, `Chase`, `NH Flat` | Infer deeper code or regulatory equivalence without jurisdiction context | Confirmed source category |
| `class` | Source-presented broad race class | Preserve raw value; parse the integer from canonical `Class N` forms | Derive from `rating_band`; assume international Class 1 equals British Class 1 | Confirmed structure; contextual meaning |
| `pattern` | Source-presented Listed, Group or Grade status | Preserve raw value and separate Listed, Group and Grade families | Collapse all Group and Grade labels into one universal hierarchy | Confirmed structure; jurisdiction-dependent meaning |
| `rating_band` | Source-presented rating restriction where populated | Parse exact `N-N` forms into stated lower and upper bounds |
…
```

## `notebooks/17_runner_characteristics_and_equipment.ipynb`

### Cell 9

Matched: `external`, `racing post`, `racecard`

```text
## Stage 5 — Establish the documented code system before testing exceptions

The raw vocabularies are consistent with a structured racecard code system rather than unrestricted text.

Published Racing Post racecard guidance documents the common runner-sex codes:

- `C` — colt;
- `F` — filly;
- `G` — gelding;
- `H` — horse;
- `M` — mare;
- `R` — rig.

It also documents the principal headgear codes:

- `b` — blinkers;
- `p` — cheekpieces;
- `t` — tongue-tie;
- `v` — visor;
- `h` — hood;
- `e` — eye hood;
- `e/c` — eyecover;
- `e/s` — eyeshield.

The same guidance states that a following `1` or `2` can indicate first- or second-time use for applicable headgear. :contentReference[oaicite:0]{index=0}

This is external interpretive evidence, not proof that every value in this database follows the guidance universally. The next stage will therefore test the complete source vocabulary against the documented codes while preserving:

- original case;
- original token order;
- combined codes;
- numeric suffixes;
- undocumented or jurisdiction-specific values;
- blank values as unresolved until their source meaning is demonstrated.

The rare `B` and `BB` runner-sex values will not be labelled erroneous merely because they are absent from this initial reference. They require source-context and, if necessary, separately governed verification.
```

### Cell 10

Matched: `external`, `racing post`, `racecard`

```text
## Stage 6 — Preserve external code-reference evidence

The interpretation of the `sex` and `hg` vocabularies now depends partly on published racecard guidance rather than source-internal profiling alone.

The project procedure therefore requires the external evidence to be captured while it is open, with permanent verification identifiers and explicit downstream authority.

Two bounded claims will be registered:

- `NB17-SEX-0001` — published Racing Post guidance defines the common runner-sex abbreviations `C`, `F`, `G`, `H`, `M` and `R`;
- `NB17-HG-0001` — published racecard guidance defines the principal headgear codes and identifies a trailing `1` as first-time use under that code.

These verification records support construction of a governed code reference. They do not establish that every observed source value is covered, universally applicable across all jurisdictions, or safe to normalise without further source-wide testing.

The immutable source values will remain unchanged.
```

### Cell 11

Matched: `manual`, `external`, `verified`

```text
# Reload the already-persisted Notebook 17 external code evidence.
#
# These records were written successfully before the kernel restart.
# This cell does not append, overwrite or reconstruct them.
MANUAL_VERIFICATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "manual_verifications.csv"
)

manual_verifications = pd.read_csv(
    MANUAL_VERIFICATIONS_PATH,
    dtype=str,
    keep_default_na=False,
)

external_code_verification_ids = {
    "NB17-SEX-0001",
    "NB17-HG-0001",
}

reloaded_external_code_verifications = (
    manual_verifications.loc[
        manual_verifications["verification_id"].isin(
            external_code_verification_ids
        )
    ]
    .sort_values("verification_id")
    .reset_index(drop=True)
)

# Confirm that both permanent records exist exactly once.
assert len(reloaded_external_code_verifications) == 2
assert set(
    reloaded_external_code_verifications["verification_id"]
) == external_code_verification_ids
assert set(
    reloaded_external_code_verifications["verification_status"]
) == {"confirmed"}
assert set(
    reloaded_external_code_verifications["database_action"]
) == {"reference_enrichment"}

print(
    "Notebook 17 external code evidence "
    "already persisted and successfully reloaded"
)

display(
    reloaded_external_code_verifications[
        [
            "verification_id",
            "source_field",
            "raw_source_value",
            "verified_value",
            "verification_status",
            "confidence",
            "database_action",
        ]
    ]
)

Notebook 17 external code evidence already persisted and successfully reloaded

  verification_id source_field              raw_source_value  \
0    NB17-HG-0001           hg  h|b|p|t|v|e|ht|e/c|e/s|b1|b2   
1   NB17-SEX-0001
…
```

### Cell 12

Matched: `verified`

```text
## Stage 7 — Test the runner-sex vocabulary against the verified reference

The source contains eight runner-sex codes:

- six codes covered by `NB17-SEX-0001`: `C`, `F`, `G`, `H`, `M`, `R`;
- two codes not covered by that reference: `B`, `BB`.

This stage will separate:

- values supported by the verified common-code mapping;
- values that remain unresolved;
- the row and race coverage of each state;
- the jurisdiction, period and runner context of the unresolved residue.

Absence from the initial reference does not make `B` or `BB` erroneous. They will remain raw, explicit and unresolved until source context or additional evidence establishes their meaning.
```

### Cell 13

Matched: `external`, `verified`

```text
# Define only the six runner-sex mappings supported by NB17-SEX-0001.
#
# B and BB are deliberately excluded rather than guessed from their spelling.
verified_sex_code_map = {
    "C": "colt",
    "F": "filly",
    "G": "gelding",
    "H": "horse",
    "M": "mare",
    "R": "rig",
}

# Classify the complete observed sex vocabulary against the verified mapping.
sex_vocabulary_governance = sex_vocabulary.copy()

sex_vocabulary_governance["normalised_sex"] = (
    sex_vocabulary_governance["raw_sex"].map(verified_sex_code_map)
)

sex_vocabulary_governance["interpretation_status"] = (
    sex_vocabulary_governance["normalised_sex"]
    .notna()
    .map(
        {
            True: "verified_common_code",
            False: "unresolved_source_code",
        }
    )
)

sex_vocabulary_governance["verification_id"] = (
    sex_vocabulary_governance["interpretation_status"]
    .map(
        {
            "verified_common_code": "NB17-SEX-0001",
            "unresolved_source_code": "",
        }
    )
)

# Confirm that all eight observed values are partitioned exactly once.
assert len(sex_vocabulary_governance) == 8
assert set(sex_vocabulary_governance["raw_sex"]) == {
    "C",
    "F",
    "G",
    "H",
    "M",
    "R",
    "B",
    "BB",
}
assert (
    sex_vocabulary_governance["runner_rows"].sum()
    == EXPECTED_RUNNER_ROWS
)

print("Runner-sex vocabulary governance")
display(
    sex_vocabulary_governance[
        [
            "raw_sex",
            "runner_rows",
            "normalised_sex",
            "interpretation_status",
            "verification_id",
        ]
    ]
)

# Summarise how much of the governed runner population is covered by the
# externally verified common-code mapping.
sex_coverage_summary = (
    sex_vocabulary_governance
    .groupby("interpret
…
```

### Cell 14

Matched: `external`, `verified`

```text
## Stage 8 — Test unresolved sex codes against repeated horse histories

The two unresolved sex codes occur in different jurisdictions:

- `BB` — Par Coeur (GER), Cologne, 15 October 2017;
- `B` — La Venezolana (VEN), Gulfstream Park, 29 November 2019.

Before consulting another external reference, this stage tests whether the same source horse labels appear elsewhere with one of the six verified runner-sex codes.

Repeated-horse evidence can reveal whether:

- the unresolved code is stable for that horse;
- another source record supplies a verified sex code;
- the value appears to be a one-row source inconsistency;
- the horse label itself is ambiguous or reused.

A different code on another row will not automatically authorise correction. Horse labels are source-presented identities rather than proven permanent entity keys, and any conclusion must retain the exact race and row lineage.
```

### Cell 16

Matched: `external`

```text
## Stage 9 — Inspect unresolved codes within their complete race context

Neither unresolved horse label appears elsewhere in the source, and the initial external search did not establish the meanings of `B` or `BB`.

The next source-internal check therefore examines every runner in the two affected races.

This can show whether:

- the unresolved values are isolated within otherwise standard sex-code vocabularies;
- the race-level `sex_rest` value supplies relevant context;
- the race name describes a sex restriction;
- neighbouring runner rows reveal a jurisdiction-specific coding pattern;
- the values look more like isolated source substitutions than stable additional categories.

Race-level restrictions will be treated as contextual evidence only. They cannot, by themselves, define the runner-level code or prove an official eligibility fact.
```

### Cell 18

Matched: `external`, `published result`, `verified`, `racing post`

```text
## Stage 10 — Verify the two unresolved runner-sex values externally

The two unresolved source values are isolated one-row cases, and neither horse has another appearance in the source from which its sex can be established independently.

External evidence resolves both cases:

- `NB17-SEX-0002` — Par Coeur (GER) is recorded by Deutscher Galopp as a gelding. A published result additionally describes the horse as `b/br g`, meaning bay/brown gelding. The source value `BB` is therefore inconsistent with the verified runner sex and is consistent with colour information entering the `sex` field.
- `NB17-SEX-0003` — La Venezolana (VEN) is independently described as a bay mare, and the affected source race was restricted to two-year-old fillies. The source value `B` is therefore inconsistent with the verified runner sex and is consistent with the bay-colour code entering the `sex` field.

Published Racing Post guidance separately defines:

- `b` — bay;
- `br` — brown;
- `g` — gelding;
- `f` — filly;
- `m` — mare.

The evidence supports treating `B` and `BB` as two source-field contamination cases rather than additional runner-sex categories.

The immutable values must remain preserved. Any corrected sex values must be applied only through a governed downstream correction layer with the permanent verification identifiers.
```

### Cell 19

Matched: `manual`, `verified`

```text
# Reload the already-persisted Notebook 17 runner-sex exception evidence.
#
# These records were written successfully before the kernel restart.
# This cell does not append, overwrite or reconstruct them.
MANUAL_VERIFICATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "manual_verifications.csv"
)

manual_verifications = pd.read_csv(
    MANUAL_VERIFICATIONS_PATH,
    dtype=str,
    keep_default_na=False,
)

sex_exception_verification_ids = {
    "NB17-SEX-0002",
    "NB17-SEX-0003",
}

reloaded_sex_exception_verifications = (
    manual_verifications.loc[
        manual_verifications["verification_id"].isin(
            sex_exception_verification_ids
        )
    ]
    .sort_values("verification_id")
    .reset_index(drop=True)
)

# Confirm that both permanent exception records exist exactly once.
assert len(reloaded_sex_exception_verifications) == 2
assert set(
    reloaded_sex_exception_verifications["verification_id"]
) == sex_exception_verification_ids
assert set(
    reloaded_sex_exception_verifications["verification_status"]
) == {"contradicted"}
assert set(
    reloaded_sex_exception_verifications["database_action"]
) == {"source_correction_candidate"}
assert set(
    reloaded_sex_exception_verifications["verified_value"]
) == {"G=gelding", "F=filly"}

print(
    "Notebook 17 runner-sex exceptions "
    "already persisted and successfully reloaded"
)

display(
    reloaded_sex_exception_verifications[
        [
            "verification_id",
            "source_date",
            "source_course",
            "source_horse",
            "raw_source_value",
            "verified_value",
            "verification_status",
            "confidence",
            "database_action",
        ]
    ]
)

Notebook 17 runner-sex exceptions already persist
…
```

### Cell 22

Matched: `external`

```text
## Stage 12 — Locate age-band exceptions by governed jurisdiction and race pattern

The initial relationship check classifies 958 runner rows outside canonical parsed `age_band` bounds:

- 118 below a source-stated minimum;
- 840 above a source-stated maximum.

These flags do not yet establish that runner `age` is wrong. Some patterns involve many differently aged runners within the same race, which may instead indicate:

- an inaccurate or incomplete race-level `age_band`;
- a source extraction or classification defect;
- a jurisdiction-specific convention;
- a race condition not fully represented by the shorthand;
- an isolated runner-age error.

This stage joins the permanent governed course reference rather than deriving jurisdiction from course-text suffixes.

It will establish:

- complete course-reference join coverage;
- exception counts by governed jurisdiction;
- whether each affected race contains one exceptional runner or many;
- whether all runners in a race contradict the stated band;
- the most material affected race identities.

No correction or external verification will be authorised from this profiling alone.
```

### Cell 24

Matched: `racing post`

```text
## Stage 13 — Decompose the headgear field without over-interpreting it

The `hg` field is blank on 1,122,490 runner rows and populated on 728,795 rows with 60 distinct raw values.

Published Racing Post guidance verifies the principal component codes:

- `h` — hood;
- `b` — blinkers;
- `p` — cheekpieces;
- `t` — tongue-tie;
- `v` — visor;
- `e` — eye hood;
- `e/c` — eyecover;
- `e/s` — eyeshield.

It also explicitly documents `b1` and `b2` as first- and second-time blinkers.

The source additionally contains:

- concatenated combinations such as `tp`, `ht`, `tb` and `htp`;
- slash-bearing components such as `e/s`;
- trailing `1` values on several different combinations;
- rare components or combinations not covered by the initial reference.

This stage will decompose each raw value into observable components while preserving:

- the original raw string;
- component order;
- slash-bearing tokens;
- any trailing numeral;
- unresolved residue.

A successful decomposition does not by itself prove the semantic meaning of every combination or suffix.
```

### Cell 25

Matched: `external`, `verified`

```text
# Decompose the complete populated headgear vocabulary while preserving each
# raw value exactly.
#
# The parser recognises only externally verified component codes. Any
# character sequence that cannot be consumed by those codes remains explicit
# unresolved residue rather than being guessed.

verified_headgear_components = [
    "e/c",
    "e/s",
    "h",
    "b",
    "p",
    "t",
    "v",
    "e",
]

def decompose_headgear_value(raw_value):
    """Parse verified headgear components, suffix and unresolved residue."""

    remaining = raw_value
    components = []

    # Preserve a single trailing numeral separately.
    use_suffix = ""

    if remaining.endswith(("1", "2")):
        use_suffix = remaining[-1]
        remaining = remaining[:-1]

    # Consume the remaining text from left to right, preferring slash-bearing
    # multi-character codes before one-character codes.
    while remaining:
        matched_component = None

        for component in verified_headgear_components:
            if remaining.startswith(component):
                matched_component = component
                break

        if matched_component is None:
            break

        components.append(matched_component)
        remaining = remaining[len(matched_component):]

    return pd.Series(
        {
            "parsed_components": "|".join(components),
            "component_count": len(components),
            "use_suffix": use_suffix,
            "unresolved_residue": remaining,
            "fully_decomposed": remaining == "",
        }
    )

headgear_decomposition = hg_vocabulary.copy()

parsed_headgear = headgear_decomposition["raw_hg"].apply(
    decompose_headgear_value
)

headgear_decomposition = pd.concat(
    [
        headgear_decomposition,
        parsed_headgear,
…
```

### Cell 26

Matched: `external`, `racing post`

```text
## Stage 14 — Inspect the nine headgear values containing unresolved `c`

Only three populated raw `hg` values fail decomposition:

- `hc` — five runner rows;
- `cvp` — two runner rows;
- `hct` — two runner rows.

All three contain `c`, which is not defined as headgear in the initial Racing Post reference.

This stage retrieves every affected runner and attaches governed jurisdiction context. It will test whether the values:

- occur within one jurisdiction or source period;
- recur for the same horse;
- coexist with otherwise standard equipment codes;
- appear to represent a jurisdiction-specific equipment code;
- are isolated transcription or field-contamination cases.

The raw values will remain unresolved until source repetition or external evidence establishes what `c` means.
```

### Cell 28

Matched: `racing post`, `racecard`

```text
## Stage 15 — Establish `c` as the source-specific eyecover component

The source does not contain the published Racing Post eyecover form `e/c`. Instead, nine runner rows contain `c` within:

- `hc`;
- `hct`;
- `cvp`.

The runner context provides direct supporting evidence. Humble Spark’s source comment states that the horse wore an eyeshield instead of the declared eye cover, while the row’s raw `hg` value is `hc`.

Interpreting `c` as the source-specific eyecover component makes all three forms coherent:

- `hc` — hood and eyecover;
- `hct` — hood, eyecover and tongue-tie;
- `cvp` — eyecover, visor and cheekpieces.

This is a source-specific normalisation rule rather than a claim that published racecards universally use standalone `c` for eyecover.

The immutable raw values remain preserved. A downstream equipment model may expose `c` as `eyecover` with explicit source lineage.
```

### Cell 30

Matched: `racing post`

```text
## Stage 16 — Test the observed trailing `1` against runner equipment histories

The source contains 22 suffixed raw `hg` values, all ending in `1`. No populated value ends in `2`.

Published Racing Post guidance explicitly verifies:

- `b1` — first-time blinkers;
- `b2` — second-time blinkers.

The source also applies `1` to other equipment and combinations, including:

- `p1`;
- `t1`;
- `h1`;
- `v1`;
- `tp1`;
- `e/s1`;
- multi-component combinations.

It would be unsafe to assume from `b1` alone that every trailing `1` universally means first-time use.

This stage tests the source behaviour directly by comparing every suffixed runner row with earlier appearances of the same source horse label.

The test can establish whether:

- the exact unsuffixed equipment combination appeared previously;
- any component in the suffixed combination appeared previously;
- the suffix usually marks the first recorded source appearance of the equipment;
- incomplete horse histories prevent a definitive conclusion.

A first appearance in this database is not automatically the horse’s first official use. The result will therefore be described as source-recorded history rather than universal equipment history.
```

### Cell 36

Matched: `racecard`

```text
## Stage 18 — Define the safe headgear interpretation boundary

The complete `hg` investigation supports the following governed interpretation.

### Blank values

A blank `hg` value means that no headgear code was supplied in this field.

It must not automatically be converted into a universal claim that the horse wore no equipment. The field may omit equipment outside the source coding scheme or reflect incomplete historical reporting.

### Equipment components

All 60 populated raw values can be decomposed into an ordered combination of:

- blinkers;
- cheekpieces;
- tongue-tie;
- hood;
- visor;
- eye hood;
- eyeshield;
- eyecover.

The raw source value and component order must remain preserved.

The source-specific component `c` can be normalised to `eyecover`, supported by the nine affected rows and the explicit Humble Spark comment. This does not imply that standalone `c` is a universal published racecard abbreviation.

### Trailing `1`

A trailing `1` is a source-presented first-time equipment declaration.

However:

- it appears only from 15 October 2025;
- it is not available consistently across the full historical period;
- no trailing `2` occurs in this source;
- database history cannot independently validate every declaration;
- the suffix may apply to one component within a combination.

Therefore a downstream model may preserve:

- the raw trailing suffix;
- a boolean source-declared-first-time flag;
- the equipment component combination.

It must not derive first-time status for earlier rows from absence of the suffix, nor claim that the source contains a complete lifetime equipment history.
```

### Cell 37

Matched: `verified`

```text
# Build the final governed interpretation table for every observed raw hg
# value, including the blank source value.
#
# This table records what can be normalised safely while preserving the
# limitations established by the investigation.

headgear_governance_rows = []

# Represent the blank source value explicitly rather than silently treating it
# as equivalent to a fully verified "no equipment" declaration.
headgear_governance_rows.append(
    {
        "raw_hg": "",
        "runner_rows": 1_122_490,
        "normalised_components": "",
        "component_count": 0,
        "source_declared_first_time": False,
        "suffix_interpretation_status": "not_applicable",
        "interpretation_status": "blank_field_not_supplied",
        "normalisation_action": "preserve_blank",
        "evidence_basis": "source_profile",
    }
)

for row in governed_headgear_vocabulary.itertuples(index=False):
    has_trailing_1 = row.use_suffix == "1"

    headgear_governance_rows.append(
        {
            "raw_hg": row.raw_hg,
            "runner_rows": int(row.runner_rows),
            "normalised_components": row.normalised_components,
            "component_count": int(row.component_count),
            "source_declared_first_time": has_trailing_1,
            "suffix_interpretation_status": (
                "source_declared_first_time_from_2025_10_15"
                if has_trailing_1
                else "no_source_first_time_suffix"
            ),
            "interpretation_status": "fully_decomposed_source_code",
            "normalisation_action": (
                "preserve_raw_and_expose_components"
            ),
            "evidence_basis": (
                "NB17-HG-0001_and_source_context"
                if row.contains_source_eyecover_code
                else "
…
```

### Cell 38

Matched: `racecard`

```text
## Stage 19 — Preserve the source-specific eyecover evidence

The published reference defines eyecover as `e/c`, but the source contains no populated literal `e/c` value.

Instead, nine runner rows contain `c` within `hc`, `hct` and `cvp`. Their source context supports interpreting `c` as the source-specific eyecover component, most directly through Humble Spark’s comment that an eyeshield was worn instead of the declared eye cover.

This evidence authorises a downstream normalisation from source component `c` to `eyecover`.

It does not alter the immutable raw values and does not claim that standalone `c` is a universal racecard abbreviation.
```

### Cell 39

Matched: `manual`, `verified`

```text
# Persist the source-specific c-to-eyecover interpretation.
#
# This cell is restart-safe:
# - it appends the verification record when absent;
# - it accepts the already-persisted row when present;
# - it refuses to overwrite a permanent ID containing different evidence.

manual_verification_columns = [
    "verification_id",
    "subject_type",
    "source_date",
    "source_course",
    "source_off",
    "source_horse",
    "source_field",
    "raw_source_value",
    "verification_question",
    "verified_value",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "governing_notebook",
    "confidence",
    "notes",
    "database_action",
]

MANUAL_VERIFICATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "manual_verifications.csv"
)

eyecover_verification = pd.DataFrame(
    [
        {
            "verification_id": "NB17-HG-0002",
            "subject_type": "source_value",
            "source_date": "2023-05-30",
            "source_course": "Redcar",
            "source_off": "4:20",
            "source_horse": "Humble Spark (IRE)",
            "source_field": "hg",
            "raw_source_value": "c",
            "verification_question": (
                "What does the source-specific headgear component c mean "
                "within hc, hct and cvp?"
            ),
            "verified_value": "c=eyecover",
            "verification_status": "confirmed",
            "evidence_type": "source_context",
            "evidence_locator": (
                "source rowid 1347987; Humble Spark comment states "
                "'Wore eye shield instead of declared eye cover'"
            ),
            "evidence_accessed_date": "2026-07-31",
            "governing_notebook": "17",
            "c
…
```

### Cell 40

Matched: `verified`

```text
## Stage 20 — Field-level analytical decisions

### `age`

- Stored as an integer on all 1,851,285 governed runner rows.
- Nineteen distinct values are observed, ranging from `1` to `31`.
- The field is usable as the source-recorded runner age.
- Apparent conflicts with race-level `age_band` inherit Notebook 16’s limitations and must not be used here to overwrite runner age automatically.
- Extreme or contradictory values require targeted verification rather than global range clipping.

### `sex`

- Stored as text and populated on every governed runner row.
- Six common codes are verified and safely normalised:

  - `C` — colt;
  - `F` — filly;
  - `G` — gelding;
  - `H` — horse;
  - `M` — mare;
  - `R` — rig.

- Two isolated values were verified as source-field contamination:

  - `BB` for Par Coeur (GER) should reconcile to `G`;
  - `B` for La Venezolana (VEN) should reconcile to `F`.

- The immutable raw values must remain preserved, with corrections applied only through the governed verification layer.

### `hg`

- Blank on 1,122,490 rows and populated on 728,795 rows.
- All 60 populated raw values can be decomposed into ordered equipment components.
- Safe component normalisations are:

  - `b` — blinkers;
  - `p` — cheekpieces;
  - `t` — tongue-tie;
  - `h` — hood;
  - `v` — visor;
  - `e` — eye hood;
  - `e/s` — eyeshield;
  - source-specific `c` — eyecover.

- Raw combinations and component order must remain preserved.
- A trailing `1` may be retained as a source-declared first-time flag from 15 October 2025 onward.
- Absence of a suffix, especially before that date, must not be interpreted as a negative first-time declaration.
- Blank `hg` means no value was supplied in this field, not proven absence of all equipment.
```

### Cell 41

Matched: `verified`

```text
# Consolidate the Notebook 17 field-level decisions into one auditable table.
#
# This table records the permitted downstream interpretation and the main
# limitations without altering the immutable source.

runner_characteristics_decisions = pd.DataFrame(
    [
        {
            "source_field": "age",
            "source_population": EXPECTED_RUNNER_ROWS,
            "distinct_raw_values": 19,
            "safe_interpretation": "source_recorded_runner_age",
            "normalisation_action": "preserve_integer_value",
            "correction_layer_required": False,
            "verification_ids": "",
            "main_limitation": (
                "Do not overwrite from age_band conflicts or clip extreme "
                "values without targeted verification."
            ),
        },
        {
            "source_field": "sex",
            "source_population": EXPECTED_RUNNER_ROWS,
            "distinct_raw_values": 8,
            "safe_interpretation": (
                "normalise C, F, G, H, M and R; reconcile two verified "
                "source-field contamination cases"
            ),
            "normalisation_action": (
                "preserve_raw_and_expose_verified_normalised_value"
            ),
            "correction_layer_required": True,
            "verification_ids": (
                "NB17-SEX-0001|NB17-SEX-0002|NB17-SEX-0003"
            ),
            "main_limitation": (
                "Raw B and BB must not be treated as additional sex "
                "categories; corrections require exact row lineage."
            ),
        },
        {
            "source_field": "hg",
            "source_population": EXPECTED_RUNNER_ROWS,
            "distinct_raw_values": 61,
            "safe_interpretation": (
                "preserve blank
…
```

### Cell 43

Matched: `manual`, `verified`

```text
# Persist the compact governed outputs produced by Notebook 17.
#
# A notebook-specific processed directory keeps these analytical artifacts
# separate from the immutable source and permanent manual-verification register.
NOTEBOOK_17_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "notebook_17_runner_characteristics"
)

NOTEBOOK_17_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SEX_VOCABULARY_OUTPUT_PATH = (
    NOTEBOOK_17_OUTPUT_DIR
    / "runner_sex_governance.csv"
)

HEADGEAR_VOCABULARY_OUTPUT_PATH = (
    NOTEBOOK_17_OUTPUT_DIR
    / "runner_headgear_governance.csv"
)

FIELD_DECISIONS_OUTPUT_PATH = (
    NOTEBOOK_17_OUTPUT_DIR
    / "runner_characteristics_decisions.csv"
)

# Build the final governed sex vocabulary.
#
# The two contaminated raw values remain explicit and carry exact permanent
# verification identifiers for downstream reconciliation.
sex_correction_map = {
    "B": {
        "normalised_sex": "filly",
        "interpretation_status": "verified_source_correction",
        "verification_id": "NB17-SEX-0003",
    },
    "BB": {
        "normalised_sex": "gelding",
        "interpretation_status": "verified_source_correction",
        "verification_id": "NB17-SEX-0002",
    },
}

runner_sex_governance = (
    sex_vocabulary_governance.copy()
)

for raw_sex, correction in sex_correction_map.items():
    correction_mask = (
        runner_sex_governance["raw_sex"].eq(raw_sex)
    )

    runner_sex_governance.loc[
        correction_mask,
        "normalised_sex",
    ] = correction["normalised_sex"]

    runner_sex_governance.loc[
        correction_mask,
        "interpretation_status",
    ] = correction["interpretation_status"]

    runner_sex_governance.loc[
        correction_mask,
        "verification_id",
    ] = co
…
```

### Cell 44

Matched: `manual`, `external`, `verified`

```text
## Analytical conclusion and limitations

### Bounded question

What do the runner-level `age`, `sex` and `hg` fields represent in the source, how consistently are they populated, and which values can be normalised or derived safely without inventing runner identity, eligibility or equipment facts?

### Executive conclusion

The three fields are useful, but they require different treatment.

- `age` is a fully populated runner-level integer and can be retained as the source-recorded runner age. It must not be overwritten automatically from race-level `age_band` values or clipped merely because a value looks unusual.
- `sex` is fully populated and almost entirely governed by six standard codes. Two isolated rows contain colour information in the sex field and require exact, verification-backed corrections.
- `hg` is blank on most rows but every populated raw value can be decomposed into an ordered equipment combination. The field is suitable for component-level analysis provided that blanks, source-specific notation and the late introduction of first-time suffixes remain explicit.

### `age`

All 1,851,285 governed runner rows contain an integer `age` value.

Nineteen distinct values are observed, ranging from `1` to `31`. The field should be preserved as the source-recorded runner age rather than treated as independently verified biological or official eligibility evidence.

Notebook 16 already investigated race-level age conditions. Apparent conflicts between `age` and `age_band` do not justify automatic runner-age correction because they may reflect:

- incomplete or misleading race-level shorthand;
- jurisdiction-specific age conventions;
- extraction defects;
- isolated source errors.

Extreme values require targeted verification if they become material to a later a
…
```

## `notebooks/18_ratings_semantics_and_availability.ipynb`

### Cell 11

Matched: `external`, `published result`

```text
## Stage 6 — Govern the isolated invalid RPR value

The source contains one isolated `rpr` value of `775`:

- source rowid: `1619851`;
- date: 3 January 2025;
- course: Deauville (FR);
- off time: 4:27;
- horse: Si Capo Si (FR).

This value is not treated as a valid RPR.

The source-internal evidence is decisive:

- it is the only `rpr` above 184 in 1,851,285 governed runner rows;
- the next-highest observed `rpr` is 184;
- the remaining runners in the same race have RPR values between 30 and 71;
- the value is inconsistent with the observed RPR scale and distribution.

External representations of the exact published result also contradict `775`, although they do not currently provide sufficiently consistent evidence to establish whether the intended value was `75` or unavailable.

The governed decision is therefore:

- preserve the immutable raw value `775`;
- do not expose `775` as a usable parsed RPR;
- set the analytical RPR to null for this exact source row;
- classify the row as `invalid_source_value`;
- leave the replacement value unresolved;
- apply the rule only through exact physical source lineage.

The downstream representation is:

- `raw_rpr = 775`
- `parsed_rpr = null`
- `availability_status = invalid_source_value`
- `replacement_status = unresolved`
- `source_rowid = 1619851`

This is not a general rule that all unusually high ratings should be removed. It is an exact exclusion rule for one uniquely identified source defect.

All other physically numeric values remain rating candidates until later jurisdiction, race-type, temporal and cross-field analysis establishes their analytical limitations.
```

### Cell 17

Matched: `racing post`

```text
## Stage 7 conclusion — Ratings must remain independent fields

The cross-field table confirms that rating availability is not one shared all-or-nothing condition.

This is expected because the fields have different producers and purposes:

- `or` is an official handicap mark assigned by the relevant racing authority;
- `rpr` is a proprietary Racing Post assessment of an individual performance;
- `ts` is a proprietary Racing Post speed figure.

A horse may therefore have any one of these fields without necessarily having the others.

The database must:

- preserve separate nullable columns for `or`, `rpr` and `ts`;
- preserve the source en dash as an unavailable state;
- exclude the exact invalid `rpr = 775` value from the analytical RPR;
- avoid requiring all three fields for a runner record to be usable;
- avoid creating one generic `rating_available` field.

No further cross-field combination analysis is required.
```

### Cell 18

Matched: `racing post`

```text
## Stage 8 — Establish field meaning and timing

The three rating fields represent different kinds of information and must not be treated as interchangeable.

### `or`

`or` is the official handicap rating applicable to the horse for that race.

For British racing, official ratings are produced by the British Horseracing Authority and are used to allocate weights in handicap races.

This is therefore a pre-race or current-state field: it records the official mark the horse was running from, not a retrospective assessment of how it performed in that race.

### `rpr`

`rpr` is the Racing Post Rating awarded to the horse for its performance in that completed race.

Racing Post describes RPR as a measure of performance and explains that races are usually rated after the event, normally the following morning. The result rating shows how much better or worse the horse performed relative to the other runners.

This is therefore a retrospective performance rating.

RPRs are not necessarily permanently fixed. Racing Post states that past result ratings may later be raised or lowered as subsequent form changes the overall assessment.

### `ts`

`ts` is Racing Post's retrospective speed figure for the horse's performance in that completed race.

Speed ratings estimate how fast a horse ran on a particular day. They are derived from the completed race time, standard times, ground conditions, race distance and beaten distances.

This is therefore a retrospective performance figure rather than a pre-race prediction.

### Governed interpretation

The database should interpret the fields as:

- `or`: official pre-race handicap mark;
- `rpr`: retrospective and potentially revisable Racing Post performance rating;
- `ts`: retrospective Racing Post speed figure.

The fields must remain sep
…
```

### Cell 19

Matched: `racing post`

```text
## Final conclusion

Notebook 18 investigated the meaning, storage, availability and analytical treatment of the source fields `or`, `rpr` and `ts`.

### Executive conclusion

The three fields are valid rating fields, but they do not represent the same kind of information and must remain separate in the future database.

- `or` is the official handicap mark applicable to the horse for that race.
- `rpr` is Racing Post's retrospective assessment of the horse's performance in that completed race.
- `ts` is Racing Post's retrospective speed figure for that completed performance.

The Racing Post handbook confirms that RPRs are normally compiled after the race and that speed ratings estimate how fast a horse ran on a particular day. It also states that past RPRs can later be revised as subsequent form changes the overall assessment. 

### Source representation

Across the governed population of 1,851,285 runner rows:

- all three fields are physically populated;
- available ratings are stored as integers;
- unavailable ratings are stored as the Unicode en dash `–`;
- no blanks, nulls, ASCII hyphens or other text tokens were observed.

The unavailable token must therefore be interpreted as:

- raw value: `–`;
- parsed analytical value: `NULL`;
- status: `unavailable`.

It must never be converted to zero.

### Numeric candidate ranges

After applying the governed exception described below, the observed numeric candidate ranges are:

- `or`: 1 to 181;
- `rpr`: 1 to 184;
- `ts`: 1 to 178.

These are observed source ranges, not universal validity rules for all future data.

### Isolated invalid RPR value

One runner row stores `rpr = 775`:

- source rowid: `1619851`;
- date: 3 January 2025;
- course: Deauville (FR);
- off time: 4:27;
- horse: Si Capo Si (FR).

This is the only R
…
```

### Cell 20

Matched: `manual`, `external`

```text
### Manual-verification decision

Status: `captured`

Notebook 18 used external publisher evidence to establish the meaning and timing of `or`, `rpr` and `ts`.

The permanent verification records are:

- `NB18-OR-0001`
- `NB18-RPR-0001`
- `NB18-TS-0001`

The isolated source value `rpr = 775` was not externally corrected. Its raw value remains preserved, its parsed analytical value is `NULL`, its status is `invalid_source_value`, and the intended replacement remains unresolved.

Focused validation completed successfully:

- `tests/test_manual_verifications.py`: 10 passed
- `scripts/validate_manual_verifications.py`: 36 governed rows passed
```

## `notebooks/19_horse_and_pedigree_identity.ipynb`

### Cell 0

Matched: `verified`

```text
# Notebook 19 — Horse and Pedigree Identity

## Bounded question

> What do the runner-level `horse`, `sire`, `dam` and `damsire` fields represent in the source, how stable and complete are their labels, and which identity or pedigree relationships can be preserved safely without inventing entity equivalence from names alone?

## Initial governed scope

This notebook investigates four runner-level source-text fields:

- `horse`
- `sire`
- `dam`
- `damsire`

The source-field governance register assigns all four to the `horse_and_pedigree_identity` family, requires their raw values to be preserved and leaves their semantics pending.

The investigation begins with source lineage and physical profiling only. At this stage, no assumption is made that:

- a source string is a stable real-world entity identifier;
- identical strings always refer to the same horse;
- different strings always refer to different horses;
- a terminal country suffix is authoritative nationality evidence;
- stripping a suffix creates a globally unique name;
- `horse + country suffix` is a permanent natural key;
- repeated pedigree labels are complete, correct or internally consistent.

Raw source labels, parsed display names, embedded suffixes, source-level label identity, provisional entity candidates, verified real-world entities and pedigree assertions will remain separate concepts. Any future normalization must be reversible and must preserve physical source lineage, confidence and review status.

## Stage 1 — Source lineage and governed population

This stage establishes the immutable source, read-only controls, complete governed runner population and provisional race key before interpreting any horse or pedigree label.

The source is:

- database: `data/raw/form_2015-present/form_2015-present/
…
```

### Cell 28

Matched: `verified`

```text
### Stage 5c — Recalculate pedigree contradictions after reversible dam parsing

The raw comparison overstated pedigree instability because two source formats were used for many dam labels:

- bare suffix: `China Cherub GB`;
- parenthesised suffix: `China Cherub (GB)`.

A reversible parser reduced 5,515 raw dam contradictions to 307 structured dam contradictions.

This stage recalculates repeated-horse pedigree consistency using:

- exact raw sire labels;
- structured dam keys where suffix syntax is supported;
- exact raw damsire labels;
- missing values kept separate from competing populated assertions.

The structured dam key is used only to compare source assertions. It does not replace the raw label or establish verified real-world entity identity.
```

### Cell 34

Matched: `external`, `verified`

```text
### Interim interpretation — Horse names are labels, not permanent identities

The temporal structure provides strong evidence that an exact source `horse` label is not a permanent identifier for one real-world horse.

Of the 368 exact horse labels associated with competing structured pedigrees:

* 350 have pedigree groups that are completely separate in time;
* 363 have exactly two pedigree groups;
* only 18 have any overlap between competing groups.

The non-overlapping cases commonly show a later appearance period with a different pedigree, reset age sequence and sometimes a different sex. Examples such as `Yukon River (IRE)` and `Zangar (FR)` are consistent with the same registered name being used for different horses in different periods.

This interpretation is compatible with international naming rules. Racing authorities generally prevent duplication within their own relevant registers rather than enforcing permanent global uniqueness. When required for international distinction, a bracketed suffix showing the country of foaling is added and forms part of the registered name. Non-protected names may later become available for reuse after authority-defined protection periods.

The source evidence therefore supports the following provisional governance conclusions:

* the complete raw `horse` label must be preserved;
* the terminal bracketed token may be parsed separately as an embedded country-of-foaling suffix where the syntax is clear;
* the suffix remains part of the source label and must not be discarded;
* the parsed display name alone is not unique;
* the complete `horse + suffix` label is not permanently unique across time;
* one exact source horse label may legitimately map to multiple coherent pedigree groups;
* an exact horse label must not be used as a
…
```

### Cell 37

Matched: `verified`

```text
### Stage 5g — Classify overlapping pedigree-label variants

The eighteen temporally overlapping cases do not generally resemble separate horses sharing one source label.

Most retain a coherent horse chronology while one pedigree component changes through a small textual variant. Recurrent examples include:

- `Almutawakel`, `AlmutawakelI` and `Almutawakel I`;
- `Voiladenuo (FR)` and `Ut*voiladenuo (FR)`;
- spacing, capitalisation or trailing-`I` variation in dam labels.

These patterns are consistent with source transcription or formatting variation, but source-internal similarity alone does not prove real-world equivalence.

This stage therefore classifies exact competing labels by reversible textual comparisons. It tests:

- case-only differences;
- whitespace-only differences;
- removal of a leading `Ut*` marker;
- attachment or separation of a terminal capital `I`;
- combinations of those transformations.

The original labels remain unchanged. A matched comparison creates only a provisional label-variant candidate and not a verified pedigree correction.
```

### Cell 39

Matched: `manual`, `external`

```text
### Stage 5h — Recurrence of unresolved pedigree-label pairs

The bounded comparison identified several safe textual relationships but left nineteen materially different label pairs unresolved.

Most unresolved damsire comparisons involve:

- `Almutawakel`;
- `AlmutawakelI`;
- `Almutawakel I`.

A recurring pair across many unrelated horse labels is more consistent with a systematic source-label variant than with independent pedigree changes. However, recurrence alone does not prove that the labels identify the same real stallion.

This stage counts each exact competing label pair across the overlapping cases and records:

- the affected pedigree component;
- number of horse labels;
- number of runner rows associated with each label;
- first and last source dates;
- representative affected horses.

No normalization rule is applied. The result determines whether a small number of bounded claims should be considered for manual or external verification.
```

### Cell 41

Matched: `external`

```text
### Stage 5i — Source-wide recurrence of the Almutawakel label family

The overlapping-case analysis found the same damsire-label pair across many unrelated horses:

- `Almutawakel`;
- `AlmutawakelI`;
- `Almutawakel I`.

This recurrence is consistent with a systematic source-label variation, but the prior counts were restricted to horse labels already known to have overlapping pedigree groups.

This stage profiles the three exact labels across the complete governed runner population.

It establishes:

- total runner-row and horse-label coverage;
- first and last appearance dates;
- jurisdictions and courses;
- whether the forms occur against the same dam labels;
- whether individual dam labels are associated with more than one form.

The raw labels remain separate. Source-wide recurrence may justify a provisional equivalence candidate, but authoritative equivalence still requires bounded external verification.
```

### Cell 43

Matched: `manual`, `external`, `verified`

```text
### Interim conclusion — Systematic damsire-label variation

The source-wide profile confirms that `Almutawakel`, `AlmutawakelI` and `Almutawakel I` are not isolated one-row anomalies.

Across the governed source they occur in:

- 423 runner rows;
- 41 distinct horse labels;
- 19 distinct dam labels;
- 14 dam labels associated with more than one exact form.

Several dam labels are associated with all three forms, including:

- `Salsa Brava (IRE)`;
- `Sensible GB`;
- `Senetosa (FR)`;
- `Boo Boo Bear (IRE)`;
- `An Realt Beag (IRE)`;
- `Almutamore (IRE)`;
- `Dilag (IRE)`.

The three forms overlap across horses, courses and periods. This rules out a simple one-time format transition and strongly supports a systematic source-label variation affecting the same apparent damsire identity.

The source-internal evidence therefore supports the following provisional rule:

- preserve every raw `damsire` label unchanged;
- treat `Almutawakel`, `AlmutawakelI` and `Almutawakel I` as members of one provisional label-variant family;
- do not silently replace any form with another;
- retain the exact transformation or matching method;
- classify the relationship as a provisional equivalence candidate rather than a verified real-world entity match;
- flag any use of the grouped form with confidence and review status.

This bounded equivalence candidate removes a large share of the remaining overlapping pedigree contradictions, but authoritative equivalence still requires external verification.

The other unresolved overlapping cases remain separate:

- `Moon Light Shadow I GB` versus `Moonlight Shadow GB`;
- `Summer Holiday (IRE)` versus `Summer Holiday I (IRE)`;
- `Paradise Lost (IRE)` versus `Paradise Lost I (IRE)`;
- `Compton Place` versus `Fountain Of Youth`.

Those differences must n
…
```

### Cell 44

Matched: `manual`, `external`, `verified`

```text
### Stage 5j — External verification of the Almutawakel label family

The source-internal analysis identified three recurring `damsire` labels:

* `Almutawakel`;
* `AlmutawakelI`;
* `Almutawakel I`.

The source alone strongly suggested that these labels refer to one real-world horse, but that equivalence required external verification.

Godolphin’s official profile provides direct evidence. The page identifies the horse as `Almutawakel (GB)` in its title and profile, while the pedigree section on the same page identifies that horse as `Almutawakel I (GB)`. Both references describe the bay horse foaled on 19 January 1995, by Machiavellian out of Elfaslah.

This directly confirms that:

* `Almutawakel` and `Almutawakel I` are alternative labels for the same real-world horse;
* the terminal `I` does not identify a different sire in this bounded case.

The source form `AlmutawakelI` differs from the externally verified `Almutawakel I` only by the absence of a space. Its repeated source-wide use against the same dam labels supports treating it as a source formatting variant of the same verified label.

The bounded verified conclusion is therefore:

> `Almutawakel`, `AlmutawakelI` and `Almutawakel I` may be assigned to one governed pedigree-label equivalence group representing the 1995 British-bred stallion Almutawakel, while every raw source label remains preserved.

This conclusion does not justify removing a terminal `I`, an attached `I` or any other apparent suffix from unrelated horse or pedigree labels. The rule applies only to this explicitly verified label family.

The permitted database action is:

* preserve the exact raw `damsire` label;
* assign the three labels to one verified label-equivalence group;
* expose `Almutawakel (GB)` as the verified display label;
* p
…
```

### Cell 45

Matched: `external`, `verified`

```text
### Stage 5k — Analytical consequence of verification `NB19-HORSE-0001`

Verification `NB19-HORSE-0001` confirms that one recurring source-label family represents a single real-world sire under multiple textual forms:

* `Almutawakel`;
* `AlmutawakelI`;
* `Almutawakel I`.

This establishes an important but deliberately narrow rule.

A repeated pedigree-label difference is not automatically evidence of a different real-world entity. Some source labels vary through spacing, legacy naming conventions or publisher-specific formatting while referring to the same horse.

The verified rule is specific to this label family:

* all three raw labels must remain preserved;
* all three may be linked to one verified pedigree-label equivalence group;
* the preferred verified display label is `Almutawakel (GB)`;
* the relationship must retain verification ID `NB19-HORSE-0001`;
* the relationship carries high confidence;
* the source rows must not be overwritten;
* the rule must not be generalized to other labels merely because they contain an attached or separated terminal `I`.

This verification reduces the number of unresolved overlapping pedigree cases, but it does not resolve the broader horse-identity problem.

The source evidence now supports three distinct classes of repeated-label behaviour:

1. **Reversible source-format variation**

   Example:

   * `China Cherub GB`;
   * `China Cherub (GB)`.

   These retain the same parsed display name and country token under different source formats.

2. **Externally verified label equivalence**

   Example:

   * `Almutawakel`;
   * `AlmutawakelI`;
   * `Almutawakel I`.

   These may be grouped only because the source-wide evidence and external verification support one bounded real-world identity.

3. **Unresolved competing assertions*
…
```

### Cell 46

Matched: `verified`

```text
### Stage 5l — Chronology of the remaining unresolved overlapping cases

After applying reversible dam parsing and the verified `Almutawakel` label equivalence, three exact horse labels retain materially different overlapping pedigree assertions:

* `Attention All (IRE)`;
* `Calivigny (IRE)`;
* `Turf Brilliant (AUS)`.

These cases cannot yet be classified safely from textual similarity alone.

This stage profiles each complete pedigree assertion by:

* exact horse label;
* sire, structured dam and damsire labels;
* number of runner rows;
* first and last source dates;
* minimum and maximum recorded age;
* observed sex values;
* number of courses;
* representative course names.

The purpose is to determine whether each difference resembles:

* an isolated source error;
* a temporary correction or reversal;
* a persistent competing assertion;
* or evidence that the same exact horse label has been reused for different real-world horses.

No additional normalization or entity merge is performed.
```

### Cell 50

Matched: `external`, `verified`

```text
### Interim interpretation — Repeated switching distinguishes label variation from pedigree conflict

The row-level chronology separates the remaining cases into two different source behaviours.

#### Persistent switching between dam-label forms

`Calivigny (IRE)` switches eight times between:

* `Summer Holiday (IRE)`;
* `Summer Holiday I (IRE)`.

The switching occurs between 2015 and 2020 while the following attributes remain stable:

* sire: `Gold Well (GB)`;
* damsire: `Kambalda`;
* sex: `G`;
* continuous recorded age progression;
* one coherent racing history.

`Turf Brilliant (AUS)` switches twice between:

* `Paradise Lost (IRE)`;
* `Paradise Lost I (IRE)`.

The switching occurs between 2020 and 2022 while the following attributes remain stable:

* sire: `Manhattan Rain (AUS)`;
* damsire: `Sadlers Wells`;
* sex: `G`;
* continuous recorded age progression;
* the same two Hong Kong courses.

Repeated reversals make a simple one-time correction or clean format transition unlikely. They are more consistent with persistent source-level variation in the dam label attached to one coherent horse history.

The evidence supports classifying both pairs as **provisional label-equivalence candidates**, but not as verified real-world equivalences. The terminal `I` must remain intact until bounded external evidence confirms its meaning in each case.

#### Isolated full-pedigree conflict

`Attention All (IRE)` shows a different pattern.

Seven rows use:

* dam: `Moon Light Shadow I GB`;
* damsire: `Compton Place`.

One Newcastle row dated 6 January 2024 instead uses:

* dam: `Moonlight Shadow GB`;
* damsire: `Fountain Of Youth`.

At the following recorded run on 3 February 2024, the original dam and damsire return.

Because both pedigree components change together for one isolat
…
```

### Cell 51

Matched: `verified`

```text
# Recalculate contradiction status after bounded classifications.
#
# Verified equivalence:
#   Almutawakel / AlmutawakelI / Almutawakel I
#
# Provisional label-variant candidates:
#   Summer Holiday (IRE) / Summer Holiday I (IRE)
#   Paradise Lost (IRE) / Paradise Lost I (IRE)
#
# Attention All remains unresolved.

VERIFIED_PEDIGREE_LABEL_GROUPS = {
    "almutawakel_verified": {
        "Almutawakel",
        "AlmutawakelI",
        "Almutawakel I",
    },
}

PROVISIONAL_DAM_LABEL_GROUPS = {
    "summer_holiday_terminal_i_candidate": {
        "Summer Holiday (IRE)",
        "Summer Holiday I (IRE)",
    },
    "paradise_lost_terminal_i_candidate": {
        "Paradise Lost (IRE)",
        "Paradise Lost I (IRE)",
    },
}

def map_label_group(
    value: object,
    groups: dict[str, set[str]],
) -> object:
    if pd.isna(value):
        return value

    for group_id, labels in groups.items():
        if value in labels:
            return group_id

    return value

reclassified_overlap_rows = overlap_rows.copy()

reclassified_overlap_rows["reclassified_dam"] = (
    reclassified_overlap_rows["dam"].map(
        lambda value: map_label_group(
            value,
            PROVISIONAL_DAM_LABEL_GROUPS,
        )
    )
)

reclassified_overlap_rows["reclassified_damsire"] = (
    reclassified_overlap_rows["damsire"].map(
        lambda value: map_label_group(
            value,
            VERIFIED_PEDIGREE_LABEL_GROUPS,
        )
    )
)

reclassified_horse_contradictions = (
    reclassified_overlap_rows
    .groupby("horse", as_index=False)
    .agg(
        sire_forms=("sire", "nunique"),
        dam_forms=("reclassified_dam", "nunique"),
        damsire_forms=("reclassified_damsire", "nunique"),
        runner_rows=("horse", "size"),
        first_date=("date", "m
…
```

### Cell 52

Matched: `verified`

```text
### Stage 5n — Chronology of the remaining bounded textual variants

After the verified `Almutawakel` grouping and the two provisional terminal-`I` dam groups, three exact horse labels remain contradictory:

* `Shielas Well (IRE)`;
* `Holly (FR)`;
* `Attention All (IRE)`.

The first two differ through narrowly bounded textual transformations already identified by the comparison stage:

* `AmcHitka (IRE)` versus `Amchitka (IRE)` differ only by letter case;
* `Ut*voiladenuo (FR)` versus `Voiladenuo (FR)` differ only by the leading source token `Ut*`.

These textual relationships are much narrower than the competing dam and damsire assertion for `Attention All (IRE)`, but similarity alone still does not establish real-world entity equivalence.

This stage profiles the chronology of `Shielas Well (IRE)` and `Holly (FR)` to determine whether each difference:

* occurs within one continuous horse history;
* preserves the surrounding pedigree;
* appears once or repeatedly;
* reverses between forms;
* or separates into distinct periods consistent with reused horse labels.

No additional equivalence group is applied at this stage.
```

### Cell 55

Matched: `verified`

```text
# Apply the two bounded textual-variant groups and recalculate the residue.
PROVISIONAL_SIRE_LABEL_GROUPS = {
    "voiladenuo_ut_prefix_candidate": {
        "Voiladenuo (FR)",
        "Ut*voiladenuo (FR)",
    },
}

PROVISIONAL_CASE_DAM_GROUPS = {
    "amchitka_case_candidate": {
        "AmcHitka (IRE)",
        "Amchitka (IRE)",
    },
}

final_overlap_classification_rows = overlap_rows.copy()

final_overlap_classification_rows["classified_sire"] = (
    final_overlap_classification_rows["sire"].map(
        lambda value: map_label_group(
            value,
            PROVISIONAL_SIRE_LABEL_GROUPS,
        )
    )
)

final_overlap_classification_rows["classified_dam"] = (
    final_overlap_classification_rows["dam"].map(
        lambda value: map_label_group(
            map_label_group(
                value,
                PROVISIONAL_DAM_LABEL_GROUPS,
            ),
            PROVISIONAL_CASE_DAM_GROUPS,
        )
    )
)

final_overlap_classification_rows["classified_damsire"] = (
    final_overlap_classification_rows["damsire"].map(
        lambda value: map_label_group(
            value,
            VERIFIED_PEDIGREE_LABEL_GROUPS,
        )
    )
)

final_overlap_contradictions = (
    final_overlap_classification_rows
    .groupby("horse", as_index=False)
    .agg(
        sire_forms=("classified_sire", "nunique"),
        dam_forms=("classified_dam", "nunique"),
        damsire_forms=("classified_damsire", "nunique"),
        runner_rows=("horse", "size"),
        first_date=("date", "min"),
        last_date=("date", "max"),
    )
)

final_overlap_contradictions["has_contradiction"] = (
    final_overlap_contradictions[
        ["sire_forms", "dam_forms", "damsire_forms"]
    ]
    .gt(1)
    .any(axis=1)
)

final_overlap_summary = pd.DataFrame(
    [
…
```

### Cell 56

Matched: `external`, `published result`, `verified`

```text
### Conclusion — Temporally overlapping pedigree contradictions

The structured contradiction analysis identified eighteen exact horse labels whose competing pedigree assertions overlapped in time.

After applying bounded source-internal classifications and captured external verification:

* thirteen labels were resolved by the verified `Almutawakel` damsire-equivalence group;
* two labels were resolved by provisional terminal-`I` dam-variant groups;
* one label was resolved by a provisional case-only dam group;
* one label was resolved by the bounded `Ut*` sire-prefix group;
* the final apparent conflict, `Attention All (IRE)`, was resolved through external verification.

#### `Attention All (IRE)`

Seven source rows identify the pedigree as:

* sire: `Westerner (GB)`;
* dam: `Moon Light Shadow I GB`;
* damsire: `Compton Place`.

One source row, recorded at Newcastle on 6 January 2024, instead identifies:

* sire: `Westerner (GB)`;
* dam: `Moonlight Shadow GB`;
* damsire: `Fountain Of Youth`.

The published result for that same Newcastle race identifies the pedigree as:

* sire: `Westerner`;
* dam: `Moon Light Shadow I`;
* damsire: `Compton Place`.

The following source appearance on 3 February 2024 also returns to that pedigree.

The Newcastle source row is therefore not evidence of a second horse identity or a legitimate competing pedigree. It is an isolated source pedigree defect affecting both the dam and damsire fields.

The governed interpretation for `Attention All (IRE)` is:

* sire: `Westerner`;
* dam: `Moon Light Shadow I`;
* damsire: `Compton Place`.

The raw Newcastle values must remain preserved for lineage, but:

* `Moonlight Shadow GB` must not be treated as a verified alternative dam;
* `Fountain Of Youth` must not be retained as a competing damsire;
*
…
```

### Cell 61

Matched: `external`

```text
### Interim interpretation — Exact horse labels are reused across real-world horses

The temporally separated pedigree analysis provides direct source-wide evidence that an exact `horse` label cannot serve as a permanent natural key.

Across 350 exact horse labels:

* 703 structured pedigree groups were observed;
* 353 transitions occurred between consecutive groups;
* 259 transitions changed sire, structured dam and damsire together;
* 205 transitions restarted at a younger recorded age;
* 204 transitions combined a complete pedigree change with an age reset;
* the median gap between groups was 2,443 days;
* the maximum gap was 4,095 days.

The strongest cases cannot represent pedigree corrections within one horse’s life.

Examples include:

* `OGorman (GB)`;
* `Hanohano (JPN)`;
* `Police Gazette (USA)`;
* `Seedling (GB)`;
* `Fireball (AUS)`;
* `Australia Day (IRE)`;
* `Chamonix (IRE)`.

In these cases, the later group has:

* a different sire;
* a different dam;
* a different damsire;
* a younger recorded age;
* and often a different sex category.

The evidence therefore supports the conclusion that the source reuses identical complete horse labels, including the country suffix, for different real-world horses at different periods.

The governed identity rule must consequently be:

> An exact raw horse label identifies a source-reported name, not a permanently unique horse entity.

Neither of the following is safe as a permanent horse key:

* parsed display name alone;
* complete raw label including country suffix.

A source-level horse occurrence must instead be distinguished using a coherent evidence bundle that includes:

* raw horse label;
* structured pedigree assertion;
* observed date range;
* age progression;
* sex history where consistent;
* race and source-r
…
```

### Cell 67

Matched: `external`

```text
### Conclusion — Full-pedigree transitions and exact-label reuse

The 259 temporally separated transitions in which sire, structured dam and damsire all changed were tested against recorded-age continuity.

Using a deliberately generous two-year tolerance:

* 257 transitions had age progression incompatible with one continuous horse identity;
* the median age-continuity shortfall was approximately 9.5 years;
* only `Forest King (AUS)` and `Felix Felicis (FR)` required external resolution.

#### `Forest King (AUS)`

The source contains:

1. a three-year-old gelding by `Rubick (AUS)`, out of `Lady Of War (AUS)`, by `Charge Forward`, observed at Sha Tin on 26 October 2025; and
2. a two-year-old gelding by `Tiger Of Malay (AUS)`, out of `Tibrogargan Miss (AUS)`, by `Monashee Mountain`, observed at Rosehill on 14 March 2026.

External authority evidence confirms that these are two different real-world horses:

* the Hong Kong Jockey Club identifies its `FOREST KING` as the Australian gelding by Rubick out of Lady Of War;
* Racing Australia identifies the later `FOREST KING` as the Australian two-year-old by Tiger Of Malay out of Tibrogargan Miss.

This is a confirmed exact-label collision. The two source occurrence groups must remain separate and must not share a permanent horse identifier merely because their complete raw `horse` labels are identical.

#### `Felix Felicis (FR)`

The source initially appears to contain two pedigree groups separated by eighteen days:

1. three 2024 rows carrying `Affinisea (IRE) — Just Eile (IRE) — Presenting`;
2. subsequent rows carrying `Olympic Glory (IRE) — Sorina (FR) — Le Havre`.

External form and profile evidence identifies one gelding, foaled on 13 April 2020, by Olympic Glory out of Sorina, and includes the same October, November an
…
```

### Cell 74

Matched: `manual`, `external`

```text
### Interim classification — Material partial-pedigree transitions

Row-level chronology distinguishes three broad classes among the thirteen material partial-pedigree transitions.

#### Strong exact-label reuse candidates

Three labels show long temporal separation, coherent but materially different pedigree groups and age histories consistent with separate horses:

* `Lyneham (FR)`;
* `Marakan (IRE)`;
* `What A Whopper (IRE)`.

Although one pedigree component happens to match in each case, the remaining evidence indicates distinct provisional horse occurrences sharing the same exact source label.

#### Bounded source-label or metadata variants

Five transitions are consistent with one continuous horse history and a narrowly identifiable source-label difference:

* `Alderley Charlie (GB)`: `Ut*windsor Heights` / `Windsor Heights`;
* `Hangry (IRE)`: `Galileo (FR)` / `Galileo (IRE)`;
* `LAziza Des Places (FR)`: `Alandi` / `Alanadi`;
* `Almavillalobas (GB)`: `Nation` / `Nation II`;
* `Bonny Ezra (NZ)`: dam country suffix `AUS` / `NZ`.

These remain provisional equivalence or correction candidates. The source-internal chronology supports continuity, but the correct governed form requires either a narrowly bounded rule or external verification.

#### Likely isolated pedigree defects

Five labels retain a materially different pedigree assertion within an otherwise continuous age and race chronology:

* `Diamond Tipp (IRE)`;
* `Colwyn Bay (FR)`;
* `New President (FR)`;
* `Runninsonofagun (IRE)`;
* `Herbert (NZ)`.

For these labels, the changed assertion may be:

* an isolated incorrect damsire;
* an incomplete pedigree;
* an incorrect sire;
* or a source correction introduced between appearances.

The source alone does not establish which assertion is correct. These cases sho
…
```

### Cell 75

Matched: `manual`

```text
material_partial_classification = pd.DataFrame(
    [
        {
            "horse": "Lyneham (FR)",
            "classification": "strong_exact_label_reuse_candidate",
            "reason": "long gap, different dam and damsire, age restart",
        },
        {
            "horse": "Marakan (IRE)",
            "classification": "strong_exact_label_reuse_candidate",
            "reason": "long gap, different dam and damsire, distinct sex history",
        },
        {
            "horse": "What A Whopper (IRE)",
            "classification": "strong_exact_label_reuse_candidate",
            "reason": "long gap, different sire, age restart and sex difference",
        },
        {
            "horse": "Alderley Charlie (GB)",
            "classification": "bounded_label_variant_candidate",
            "reason": "exact Ut-prefix pair with continuous age chronology",
        },
        {
            "horse": "Hangry (IRE)",
            "classification": "bounded_metadata_correction_candidate",
            "reason": "same pedigree except sire country suffix; continuous age chronology",
        },
        {
            "horse": "LAziza Des Places (FR)",
            "classification": "bounded_spelling_variant_candidate",
            "reason": "Alandi and Alanadi differ by one internal letter; all other evidence stable",
        },
        {
            "horse": "Almavillalobas (GB)",
            "classification": "bounded_terminal_numeral_candidate",
            "reason": "Nation and Nation II with otherwise continuous pedigree and age",
        },
        {
            "horse": "Bonny Ezra (NZ)",
            "classification": "dam_country_suffix_correction_candidate",
            "reason": "same dam name, sire and damsire; only dam country suffix changes",
        },
…
```

### Cell 76

Matched: `manual`, `external`, `verified`

```text
### Conclusion — Temporally separated partial-pedigree transitions

The 94 temporally separated transitions affecting only one or two pedigree components were classified using reversible structural comparison, chronology and age evidence.

They divide into the following groups.

#### Narrow source-label variation

Seventy-seven transitions are explained by bounded textual differences:

* 34 dam terminal-`I` variants;
* 20 damsire terminal-`I` variants;
* 16 damsire punctuation or spacing variants;
* four sire punctuation or spacing variants;
* two dam punctuation or spacing variants;
* one dam case or whitespace variant.

These transitions do not support separate horse identities.

They remain provisional label-equivalence candidates because the relationship is supported by:

* unchanged surrounding pedigree components;
* coherent age progression;
* non-overlapping but continuous chronology;
* and a narrowly reversible text transformation.

The raw labels must remain preserved, and no unrestricted global normalization rule is authorised.

#### Bounded `Ut*` variants

Three additional transitions are covered by exact observed `Ut*` pairs:

* `Ut*mangarose` / `Mangarose`;
* `Ut*voiladenuo (FR)` / `Voiladenuo (FR)`;
* `Ut*windsor Heights` / `Windsor Heights`.

These may be governed only as explicitly enumerated pairs. The evidence does not support removing `Ut*` from arbitrary pedigree labels.

#### Strong exact-label reuse candidates

Three labels retain materially different pedigree evidence and long separated histories consistent with distinct horses:

* `Lyneham (FR)`;
* `Marakan (IRE)`;
* `What A Whopper (IRE)`.

They should be represented as separate provisional horse occurrences sharing the same exact raw horse label.

#### Bounded metadata or spelling candidates

F
…
```

### Cell 77

Matched: `external`

```text
### External verification — `New President (FR)`

The source contains three dam-label forms for `New President (FR)`:

* `Sun Song`;
* `Sun Song I`;
* `Sun Song II`.

The final `Sun Song II` assertion also omits the damsire, while earlier rows identify `Dr Fong`.

Official France Galop records resolve the apparent contradiction.

France Galop’s published official racing bulletins identify `New President` as:

* sire: `Sinndar`;
* dam: `Sun Song`;
* damsire: `Dr Fong`.

The same registered pedigree appears in official records across multiple seasons.

The governed interpretation is therefore:

* horse: `New President (FR)`;
* sire: `Sinndar (IRE)`;
* dam: `Sun Song (FR)`;
* damsire: `Dr Fong`;
* `Sun Song I` and `Sun Song II`: source-label variants of `Sun Song` for this exact pedigree family;
* blank damsire on 15 November 2025: incomplete source pedigree assertion.

This is not evidence of multiple real-world horses or competing registered pedigrees.

All raw labels and the blank damsire must remain preserved for lineage. A governed downstream layer may expose the France Galop-supported pedigree with explicit official provenance.

This verification is bounded to `New President (FR)` and does not authorise general removal of terminal Roman numerals from arbitrary dam labels.
```

### Cell 78

Matched: `external`, `verified`

```text
### External verification — `Herbert (NZ)`

The source contains two sire labels for `Herbert (NZ)`:

* `Warning Flag (USA)`;
* `Sweet Orange (USA)`.

All other pedigree components remain stable:

* dam: `Ze One (AUS)`;
* damsire: `All American`.

The official New Zealand Stud Book resolves the apparent contradiction.

Its registered record for `Herbert (NZ)`, foaled on 18 October 2020 with life number `NZ00423062`, identifies the horse as:

* sire: `Sweet Orange (USA)`;
* dam: `Ze One (AUS)`;
* damsire: `All American (AUS)`.

The official Stud Book record for `Sweet Orange (USA)` separately records `Warning Flag (USA)` as another name used by the same stallion.

The two source sire values therefore refer to one real-world sire:

* registered breeding name: `Sweet Orange (USA)`;
* alternative racing name: `Warning Flag (USA)`.

This is not a pedigree correction, source defect or horse-identity split. It is a verified sire-alias relationship.

The governed interpretation for `Herbert (NZ)` is:

* horse: `Herbert (NZ)`;
* sire entity: `Sweet Orange (USA)`;
* equivalent source sire label: `Warning Flag (USA)`;
* dam: `Ze One (AUS)`;
* damsire: `All American (AUS)`.

Both raw sire labels must remain preserved for lineage. A governed identity layer may link them to the same verified sire entity using the official New Zealand Stud Book evidence.

This verification is specific to `Sweet Orange (USA)` and `Warning Flag (USA)` and does not authorise general alias matching from names alone.
```

### Cell 80

Matched: `verified`

```text
### Stage 7 — From source labels to provisional horse occurrences

The contradiction analysis establishes that the source `horse` field is a reported label rather than a permanent horse identifier.

An identical complete label may represent:

* one horse with stable pedigree reporting;
* one horse whose pedigree labels change through punctuation, spacing, aliases or metadata corrections;
* one horse with one or more defective pedigree rows;
* or multiple real-world horses whose identical names and breeding-country suffixes are reused across time or jurisdictions.

The database therefore requires an intermediate identity layer between immutable source rows and any later authoritative horse entity.

#### Raw source label

The exact `horse` value stored on each runner row.

It must remain unchanged and traceable to the original row.

#### Structured pedigree assertion

The source-reported combination of:

* sire;
* reversibly parsed dam label and country suffix;
* damsire.

This is evidence attached to a runner appearance. It is not automatically a verified pedigree.

#### Provisional horse occurrence

A source-internal grouping of runner rows that appear to describe one continuous horse history.

A provisional occurrence may use:

* exact raw horse label;
* coherent structured pedigree assertion;
* non-contradictory chronology;
* plausible age progression;
* compatible sex history;
* and explicit bounded label-equivalence rules.

It must split where the evidence strongly indicates label reuse, including:

* materially different complete pedigrees;
* incompatible age continuity;
* distinct registry identities;
* or captured official verification.

#### Verified horse entity

A real-world horse identity supported by an authoritative identifier or governing registration reco
…
```

### Cell 81

Matched: `external`, `verified`

```text
### Conclusion — Transition-level identity governance

The 353 temporally separated pedigree transitions now have explicit source-governance decisions.

They divide into:

| transition decision           | transitions | exact horse labels |
| ----------------------------- | ----------: | -----------------: |
| split provisional occurrence  |         261 |                261 |
| retain single occurrence      |          89 |                 86 |
| pending official confirmation |           3 |                  3 |
| **total**                     |     **353** |                  — |

#### Split provisional occurrence

Two hundred and sixty-one transitions require a new provisional horse occurrence.

These include:

* 258 genuine complete-pedigree identity transitions;
* three strong partial-pedigree label-reuse candidates.

The evidence supporting a split includes:

* materially different pedigree assertions;
* temporally separated histories;
* incompatible age continuity;
* sex-history differences where present;
* and, in some cases, external confirmation of distinct registered horses.

A split does not by itself create two verified real-world horse entities. It records that the source evidence cannot safely be represented as one continuous horse occurrence.

#### Retain single occurrence

Eighty-nine transitions across 86 exact horse labels remain within one provisional occurrence.

These include:

* punctuation, spacing and case variants;
* terminal-Roman-numeral variants;
* bounded `Ut*` label pairs;
* verified sire aliases;
* metadata corrections;
* incomplete pedigree assertions;
* and externally confirmed source pedigree defects.

Retaining one occurrence does not mean overwriting the raw assertion. Every source value remains attached to its original runner row, whil
…
```

### Cell 82

Matched: `external`

```text
### External verification — `Hangry (IRE)`

The source contains two sire-label forms for `Hangry (IRE)`:

* `Galileo (FR)`;
* `Galileo (IRE)`.

The remaining pedigree and horse history are stable:

* dam: `Magic Tree (UAE)`;
* damsire: `Timber Country`;
* coherent age progression;
* continuous sex and racing history.

Published Irish form records consistently identify `Hangry (IRE)` as:

* sire: `Galileo (IRE)`;
* dam: `Magic Tree (UAE)`;
* damsire: `Timber Country (USA)`.

International racing-authority records also identify the relevant stallion as `Galileo (IRE)`.

The `(FR)` suffix is therefore an incorrect country suffix attached to the same sire identity. It is not evidence of:

* a second sire;
* a pedigree change;
* or a separate horse occurrence.

The governed interpretation is:

* horse: `Hangry (IRE)`;
* sire: `Galileo (IRE)`;
* dam: `Magic Tree (UAE)`;
* damsire: `Timber Country (USA)`.

The raw `Galileo (FR)` value must remain preserved on its original rows for lineage. A governed downstream layer may expose `Galileo (IRE)` and classify the earlier suffix as a source metadata defect.

This decision is bounded to this identified sire relationship and does not authorise country-suffix replacement based on name similarity alone.
```

### Cell 83

Matched: `external`

```text
### External verification — `Bonny Ezra (NZ)`

The source contains two dam-label forms for `Bonny Ezra (NZ)`:

* `Ascolini (AUS)`;
* `Ascolini (NZ)`.

The remaining pedigree is stable:

* sire: `Road To Rock (AUS)`;
* damsire: `Bertolini (USA)`;
* continuous horse history.

New Zealand Stud Book material identifies the broodmare as:

* `Ascolini (NZ)`;
* foaled in 2006;
* by `Bertolini (USA)`;
* out of `Ascona (NZ)`.

Independent breeding records also identify Bonny Ezra’s dam as `Ascolini (NZ)`.

The governed interpretation is therefore:

* horse: `Bonny Ezra (NZ)`;
* sire: `Road To Rock (AUS)`;
* dam: `Ascolini (NZ)`;
* damsire: `Bertolini (USA)`.

The `(AUS)` form is an incorrect breeding-country suffix attached to the same dam identity. It is not evidence of:

* a different mare;
* a pedigree change;
* or a separate horse occurrence.

The raw `Ascolini (AUS)` value must remain preserved on its original rows. A governed downstream layer may expose `Ascolini (NZ)` and classify the alternative suffix as a source metadata defect.
```

### Cell 84

Matched: `external`, `verified`

```text
### External verification — `Alderley Charlie (GB)`

The source contains two damsire-label forms for `Alderley Charlie (GB)`:

* `Windsor Heights`;
* `Ut*Windsor Heights`.

The surrounding pedigree remains stable:

* sire: `Ask`;
* dam: `Alderley Heights`;
* continuous age, sex and racing history.

`Windsor Heights` is an identifiable registered stallion. Published pedigree records consistently identify Alderley Charlie as:

* `Ask`;
* out of `Alderley Heights`;
* by `Windsor Heights`.

No evidence was found for a separate stallion registered as `Ut*Windsor Heights`.

The `Ut*` prefix is therefore treated as a source-system or registry marker attached to the underlying name. Its precise internal expansion is not established and must not be invented.

The governed interpretation is:

* verified damsire label: `Windsor Heights`;
* raw source variant: `Ut*Windsor Heights`;
* decision: `label_equivalence`;
* identity split: no.

Both raw forms remain preserved on their original runner rows. The governed layer may expose `Windsor Heights` while recording the prefixed form as a bounded source-label variant.
```

### Cell 85

Matched: `manual`, `external`, `verified`

```text
# Build explicit governance decisions for temporally separated pedigree transitions.

transition_governance = separated_transitions.copy()

transition_governance["transition_decision"] = "review_required"
transition_governance["decision_basis"] = "not_yet_classified"
transition_governance["identity_split"] = pd.NA
transition_governance["governing_verification_id"] = pd.NA

# Complete-pedigree changes generally represent exact-label reuse.
full_pedigree_mask = (
    transition_governance["pedigree_components_changed"].eq(3)
)

transition_governance.loc[
    full_pedigree_mask,
    [
        "transition_decision",
        "decision_basis",
        "identity_split",
    ],
] = [
    "split_provisional_occurrence",
    "complete_pedigree_change_with_separated_chronology",
    True,
]

# Felix Felicis is one horse with defective early pedigree rows.
felix_mask = transition_governance["horse"].eq(
    "Felix Felicis (FR)"
)

transition_governance.loc[
    felix_mask,
    [
        "transition_decision",
        "decision_basis",
        "identity_split",
    ],
] = [
    "retain_single_occurrence",
    "externally_verified_source_pedigree_defect",
    False,
]

# Forest King is a confirmed exact-label collision.
forest_king_mask = transition_governance["horse"].eq(
    "Forest King (AUS)"
)

transition_governance.loc[
    forest_king_mask,
    [
        "transition_decision",
        "decision_basis",
        "identity_split",
    ],
] = [
    "split_provisional_occurrence",
    "externally_confirmed_exact_label_collision",
    True,
]

# Apply classifications from the material partial-pedigree review.
partial_classification_lookup = (
    material_partial_classification
    .set_index("horse")["classification"]
    .to_dict()
)

partial_reason_lookup = (
    material_partial
…
```

### Cell 86

Matched: `external`, `verified`

```text
### Updated conclusion — Transition-level identity governance

The 353 temporally separated pedigree transitions now have explicit governance decisions.

| transition decision           | transitions | exact horse labels |
| ----------------------------- | ----------: | -----------------: |
| split provisional occurrence  |         261 |                261 |
| retain single occurrence      |          87 |                 84 |
| pending official confirmation |           5 |                  5 |
| **total**                     |     **353** |                  — |

#### Split provisional occurrence

Two hundred and sixty-one transitions are treated as boundaries between distinct horse occurrences sharing the same raw horse label.

These are cases where the evidence indicates that the same displayed horse name and breeding-country suffix have been used for different real horses.

The raw source label remains unchanged, but the histories must not be merged into one analytical horse record.

#### Retain single occurrence

Eighty-seven transitions across 84 horse labels remain within one horse occurrence.

These include:

* punctuation, spacing and case variants;
* terminal-Roman-numeral variants;
* bounded `Ut*` source markers;
* verified aliases;
* incorrect country suffixes;
* incomplete pedigree rows;
* and externally supported source defects.

The raw assertions remain preserved, while the governed layer records the supported pedigree relationship or label equivalence.

#### Pending official confirmation

Five transitions remain unresolved:

* `Almavillalobas (GB)` — `Nation (USA)` versus `Nation II (USA)`;
* `Colwyn Bay (FR)` — disagreement affecting dam and damsire;
* `Diamond Tipp (IRE)` — `Great Palm` versus `Oscar`;
* `L’Aziza des Places (FR)` — `Alandi (IRE)` versus
…
```

### Cell 87

Matched: `verified`

```text
### Stage 8 — Governed pedigree reconciliation

Where the evidence identifies one continuous horse, competing pedigree labels should not remain as unresolved alternatives merely because they appeared in the source.

The governed layer should distinguish between:

* the immutable raw assertion recorded on each runner row;
* the verified or best-supported pedigree relationship;
* the type of source discrepancy;
* and the authority supporting the reconciliation.

A governed reconciliation may classify a discrepancy as:

* `label_equivalence` — two labels refer to the same registered horse;
* `country_suffix_defect` — the underlying name is correct but the breeding-country suffix is wrong;
* `publisher_disambiguation` — a numeral or marker was added by a publication rather than forming part of the registered name;
* `source_prefix_variant` — a bounded source-system marker is attached to the underlying name;
* `incorrect_entity_assignment` — the source selected a different real sire, dam or damsire;
* `incomplete_pedigree_assertion` — a source row omits a relationship confirmed elsewhere;
* or `pending_official_confirmation`.

The raw values must never be overwritten. Instead, each reconciliation should record:

* horse label;
* pedigree role affected;
* raw competing labels;
* governed label where established;
* reconciliation type;
* evidence status;
* verification identifier or authority;
* whether the discrepancy implies another horse identity;
* and whether database correction is permitted.

This separates identity governance from source correction:

> A horse may remain one identity while one or more of its source pedigree assertions are corrected, normalized or explicitly rejected in the governed layer.

Only genuine same-label collisions should require separate horse
…
```

### Cell 88

Matched: `external`, `verified`

```text
# Record pedigree reconciliations established during Notebook 19.

pedigree_reconciliations = pd.DataFrame(
    [
        {
            "horse": "Felix Felicis (FR)",
            "pedigree_role": "complete_pedigree",
            "raw_competing_labels": (
                "Olympic Glory — Sorina — Le Havre | "
                "Affinisea — Just Eile — Presenting"
            ),
            "governed_label": (
                "Olympic Glory — Sorina — Le Havre"
            ),
            "reconciliation_type": "incorrect_entity_assignment",
            "evidence_status": "externally_verified",
            "verification_id": pd.NA,
            "authority_or_source": (
                "external pedigree verification"
            ),
            "implies_distinct_horse": False,
            "database_correction_permitted": True,
            "notes": (
                "Three early rows contain a pedigree belonging "
                "to a different horse."
            ),
        },
        {
            "horse": "New President (FR)",
            "pedigree_role": "damsire",
            "raw_competing_labels": (
                "Sun Song | Sun Song I | Sun Song II | blank"
            ),
            "governed_label": "Dr Fong",
            "reconciliation_type": (
                "label_equivalence_and_incomplete_pedigree_assertion"
            ),
            "evidence_status": "officially_verified",
            "verification_id": "NB19-HORSE-0002",
            "authority_or_source": "France Galop",
            "implies_distinct_horse": False,
            "database_correction_permitted": True,
            "notes": (
                "The raw variants apply to the dam label; "
                "official pedigree confirms Dr Fong as damsire."
            ),
        },
        {
…
```

### Cell 89

Matched: `external`, `verified`

```text
### Conclusion — Governed pedigree reconciliation

Eleven material pedigree discrepancies have been converted into explicit governed reconciliation records.

Six cases currently permit downstream correction or normalization:

| horse                   | governed outcome                                                       |
| ----------------------- | ---------------------------------------------------------------------- |
| `Felix Felicis (FR)`    | reject the incorrect early complete pedigree                           |
| `New President (FR)`    | retain one dam identity and restore `Dr Fong` as damsire               |
| `Herbert (NZ)`          | treat `Warning Flag` and `Sweet Orange` as verified sire aliases       |
| `Bonny Ezra (NZ)`       | correct the dam suffix to `Ascolini (NZ)`                              |
| `Alderley Charlie (GB)` | remove the bounded `Ut*` source prefix from the governed damsire label |
| `Hangry (IRE)`          | correct the sire suffix to `Galileo (IRE)`                             |

These reconciliations do not overwrite the source rows. They establish a governed interpretation alongside the immutable raw assertions.

Five cases remain pending official confirmation:

* `Almavillalobas (GB)`;
* `Colwyn Bay (FR)`;
* `Diamond Tipp (IRE)`;
* `L’Aziza des Places (FR)`;
* `Runninsonofagun (IRE)`.

For those cases:

* no canonical pedigree value is assigned;
* database correction remains prohibited;
* competing raw assertions remain visible;
* and the enquiry authority is recorded.

The reconciliation register demonstrates that pedigree disagreement and horse-identity disagreement are separate problems.

A source row may contain:

* the correct horse but an incorrect country suffix;
* the correct horse but a publisher-added numeral;
* a leg
…
```

### Cell 90

Matched: `verified`

```text
### Stage 9 — Assigning provisional horse occurrences

The pedigree discrepancies that can currently be reconciled have now been separated from genuine same-label horse collisions.

A provisional occurrence may therefore be assigned using the governed transition decisions.

For each exact raw horse label:

* the first structured pedigree group begins occurrence `1`;
* `split_provisional_occurrence` starts a new occurrence because the same label represents a different horse history;
* `retain_single_occurrence` keeps the adjoining groups together because the discrepancy has been classified as a label variant, metadata defect, alias, incomplete assertion or incorrect source pedigree;
* `pending_official_confirmation` remains within one occurrence provisionally, but the unresolved boundary must remain visible.

The resulting identifier is source-internal and provisional. It does not replace an official registration or life number.

Its purpose is to prevent histories belonging to different horses from being merged merely because they share:

* the same displayed name;
* and the same breeding-country suffix.

At the same time, it avoids splitting one real horse because of:

* spelling or punctuation;
* Roman numerals;
* source prefixes;
* aliases;
* incorrect country suffixes;
* missing pedigree fields;
* or known source defects.

Each occurrence must retain:

* the raw horse label;
* occurrence sequence within that label;
* included structured pedigree groups;
* first and last observed dates;
* observed age and sex history;
* runner-row lineage;
* the governed boundaries that created the occurrence;
* pending official-confirmation boundaries;
* and any verification identifiers.

A provisional occurrence must not be presented as a verified real-world horse entity unless it
…
```

### Cell 95

Matched: `manual`, `manually`

```text
### Reader-facing conclusion — Horse and pedigree identity

The raw `horse` label is not a safe permanent horse identifier.

The analysis found three practical outcomes.

#### Corrected

Where reliable evidence establishes the right horse or pedigree, the clean analytical layer should use that corrected result.

The original source value remains available only for audit and provenance.

#### Different horse

Where the same displayed name and breeding-country suffix have been reused for genuinely different horses, the histories must be split.

These records must not be merged merely because the raw label matches.

#### Unresolved

Where the correct horse or pedigree cannot yet be established confidently, the next question is whether manual verification is practical.

Manual checking is worthwhile where:

* the number of affected horses is small;
* an official Stud Book or racing authority can be contacted;
* the result would materially affect later analysis;
* and the verification effort is proportionate.

Where practical, the case should be investigated and converted to either:

* `Corrected`; or
* `Different horse`.

Only cases that cannot be resolved at reasonable cost should remain unresolved.

Those records should then be flagged or excluded from horse- or pedigree-dependent analysis rather than guessed.

The practical database rule is therefore:

> Use the corrected horse and pedigree where known, split genuine same-name collisions, manually verify unresolved cases where practical, and exclude rather than guess where uncertainty remains.

This produces a clean analytical identity layer without discarding the raw source evidence needed to verify how each decision was reached.
```

### Cell 96

Matched: `manual`, `manually`, `verified`

```text
## Final conclusion

### Bounded question

This notebook investigated what the runner-level `horse`, `sire`, `dam` and `damsire` fields represent, whether those labels are stable enough to support horse- and pedigree-level analysis, and what identity rules are required before the fields can be used safely.

### Conclusion

The raw `horse` field is a source-presented label, not a permanent horse identifier.

The same displayed horse name and breeding-country suffix can be reused for different real horses. Conversely, one real horse can appear beside incorrect or inconsistent pedigree assertions.

Horse identity and pedigree therefore require a governed analytical layer rather than direct use of the raw strings.

The 353 material transitions between structured pedigree histories produced three practical outcomes:

| analytical outcome | transitions | exact horse labels |
| ------------------ | ----------: | -----------------: |
| Corrected          |          87 |                 84 |
| Different horse    |         261 |                261 |
| Unresolved         |           5 |                  5 |
| **Total**          |     **353** |                  — |

### Corrected

Eighty-seven transitions across 84 exact horse labels belong to one continuous horse history.

Where the correct pedigree has been established, the analytical layer should use the corrected result rather than preserving competing values as equally valid.

Examples include:

* verified aliases;
* incorrect country suffixes;
* source prefixes;
* missing pedigree fields;
* and rows carrying a pedigree belonging to another horse.

The original source values must remain unchanged for lineage and audit, but they should not remain active alternatives in analysis once the correct interpretation is governed.

###
…
```

## `notebooks/20_connections_and_ownership_identity.ipynb`

### Cell 0

Matched: `external`, `verified`

```text
# Notebook 20 — Connections and Ownership Identity

## Bounded question

> What do the runner-level `jockey`, `trainer` and `owner` fields represent in the source, how stable and complete are their labels, and which source-internal identity relationships can be preserved safely without inventing equivalence between people, partnerships, syndicates or organisations?

## Initial governed scope

This notebook investigates three runner-level source-text fields:

- `jockey`
- `trainer`
- `owner`

The source-field governance register assigns all three to the `connections_and_ownership` family, requires their raw values to be preserved and leaves their semantics pending.

The investigation begins with source lineage and inherited governance only. At this stage, no assumption is made that:

- a raw label is a stable real-world entity identifier;
- identical strings always identify the same person, organisation or ownership account;
- different strings always identify different entities;
- initials uniquely identify a person;
- punctuation, spacing or title differences imply equivalence;
- trainer and jockey names follow the same identity rules;
- owner partnership or syndicate labels can be decomposed safely;
- a person, organisation, ownership account, partnership and syndicate can share one undifferentiated entity model;
- name similarity alone justifies merging.

Raw source labels, display-name parsing, exact-label identity, provisional source-internal identity, externally verified identity, role assertions and ownership-entity type will remain separate concepts.

## Stage 1 — Source lineage and governed population

This stage establishes the immutable source, read-only controls, complete governed runner population and provisional race key before interpreting any connection
…
```

### Cell 35

Matched: `manual`

```text
# Inspect the committed reference directory before choosing a governed course
# or jurisdiction source.
#
# This cell deliberately does not guess a filename or column name. It lists
# the available reference files and shows the schema of CSVs whose names or
# columns mention course, jurisdiction, country, authority, location or
# timezone.
REFERENCE_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "reference"
)

if not REFERENCE_DIRECTORY.exists():
    raise FileNotFoundError(
        f"Reference directory not found: {REFERENCE_DIRECTORY}"
    )

reference_files = sorted(
    path
    for path in REFERENCE_DIRECTORY.iterdir()
    if path.is_file()
)

reference_inventory_rows = []

for path in reference_files:
    inventory_row = {
        "reference_file": path.name,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
    }

    # Read only CSV headers at this stage. We are inspecting repository
    # structure, not loading or interpreting reference contents yet.
    if path.suffix.lower() == ".csv":
        try:
            columns = pd.read_csv(
                path,
                nrows=0,
            ).columns.tolist()

            inventory_row["columns"] = ", ".join(columns)

        except Exception as error:
            inventory_row["columns"] = (
                f"<header read failed: {type(error).__name__}: {error}>"
            )

    else:
        inventory_row["columns"] = ""

    reference_inventory_rows.append(inventory_row)

reference_inventory = pd.DataFrame(
    reference_inventory_rows
)

# Retain files whose filename or CSV schema contains terminology relevant to
# governed course, jurisdiction, location or timezone context.
relevant_terms = [
    "course",
    "jurisdiction",
    "country",
    "authority",
    "loca
…
```

### Cell 36

Matched: `validation_status`

```text
# Load the existing governed course-location reference using its actual
# repository filename and actual committed schema.
#
# This cell still does not join the source data. It first establishes whether
# `raw_course_labels` can safely act as the source-course lookup column or
# whether it contains composite or non-unique values requiring a separate
# mapping step.
COURSE_LOCATION_REFERENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "course_locations.csv"
)

if not COURSE_LOCATION_REFERENCE_PATH.exists():
    raise FileNotFoundError(
        "Governed course-location reference not found: "
        f"{COURSE_LOCATION_REFERENCE_PATH}"
    )

course_location_reference = pd.read_csv(
    COURSE_LOCATION_REFERENCE_PATH
)

# These names come from the committed file schema rather than an inferred or
# newly invented course model.
REQUIRED_COURSE_LOCATION_COLUMNS = [
    "candidate_course_label",
    "candidate_jurisdiction",
    "country",
    "iana_timezone",
    "raw_course_labels",
    "provisional_races",
    "meeting_dates",
    "earliest_date",
    "latest_date",
]

missing_course_location_columns = [
    column
    for column in REQUIRED_COURSE_LOCATION_COLUMNS
    if column not in course_location_reference.columns
]

if missing_course_location_columns:
    raise AssertionError(
        "Governed course-location reference is missing required columns: "
        f"{missing_course_location_columns}"
    )

# Profile the possible source-course lookup column before using it.
#
# We must establish whether each row contains exactly one raw source label and
# whether those labels are unique. A plural column name alone is not enough
# evidence to assume its storage convention.
raw_course_label_profile = pd.DataFrame(
    [
        {
            "reference_row
…
```

### Cell 55

Matched: `external`

```text
## Stage 25 — Conclusions from trainer ampersand structure

The trainer field contains 305 exact labels with at least one ampersand, covering 53,656 runner rows.

The source uses ampersands across several different text structures:

- full-name joint labels, such as `Ciaron Maher & David Eustace`;
- shared-surname compression, such as `John & Thady Gosden`;
- initial-based compression, such as `D & P ProdHomme`;
- labels containing more than one ampersand.

Literal splitting is not a safe general rule.

Of the 297 labels containing exactly one ampersand:

- 29 had both literal sides independently observed as exact trainer labels;
- 111 had only one side independently observed;
- 157 had neither side independently observed.

Many unmatched components are incomplete strings created by shared-surname compression rather than meaningful standalone trainer labels.

The 29 strongest literal full-name cases produced 58 joint-label/component relationships:

- 40 had at least one shared exact horse label;
- 18 had no shared exact horse evidence.

Continuity was often asymmetric.

A joint label could share many horses with one component but few or none with the other. Component chronology also varied between:

- standalone activity before the joint label;
- standalone activity after the joint label;
- overlapping periods;
- activity spanning the whole joint-label period.

These results support the following governance position:

1. The complete raw trainer label is the source assertion and must be preserved atomically.
2. An ampersand must not trigger automatic trainer decomposition.
3. Literal component strings may be retained only as analytical relationship candidates.
4. Shared exact horses and chronology can strengthen a candidate relationship but do not establish entity equiv
…
```

### Cell 57

Matched: `manual`, `external`

```text
## Stage 26 — Trainer labels containing multiple ampersands

Eight exact trainer labels contain two ampersands, covering 1,149 runner rows.

These labels were excluded from the earlier left/right component analysis because splitting once around `&` would not represent their complete structure.

This stage inspects the finite population directly.

For each label, it records:

- the complete raw trainer label;
- runner-row volume;
- first and last observed dates;
- the number of ampersands;
- the literal trimmed segments produced by splitting at every ampersand;
- the number of resulting segments;
- whether each literal segment occurs as a standalone exact trainer label.

The resulting segments are diagnostic only.

They must not be treated as trainer identities because multiple-ampersand labels may contain:

- three named trainers;
- compressed shared surnames;
- initials that depend on a later surname;
- stable partnership or organisational wording;
- punctuation whose exact structure cannot be inferred internally.

The complete raw trainer label remains the governed source assertion.

Any component relationship must be established separately through manual or external verification.
```

### Cell 59

Matched: `external`, `verified`

```text
## Stage 27 — Boundary between source semantics and connection identity resolution

The trainer ampersand investigation demonstrates that connection-label semantics and entity resolution are separate problems.

The source provides complete runner-level trainer assertions such as:

- `John & Thady Gosden`;
- `Michael & David Easterby`;
- `Ciaron Maher & David Eustace`;
- `David A & B Hayes & Tom Dabernig`.

These labels contain several structures:

- complete names joined by ampersands;
- compressed shared surnames;
- initial-based compressed names;
- labels involving three apparent participants;
- standalone components with strong horse continuity;
- standalone components with weak or no continuity;
- independently observed strings that may be namesakes.

The source does not provide enough information to reconstruct every participant safely.

Therefore this notebook establishes the following boundary:

### In scope here

- preserve the complete raw `trainer` value;
- describe punctuation and structural vocabularies;
- identify candidate relationships supported by exact-label and horse-history evidence;
- document why automatic splitting or canonicalisation is unsafe;
- define the raw-field database treatment.

### Deferred to later identity-resolution work

- reconstructing omitted shared surnames;
- verifying formal joint-training arrangements;
- assigning canonical person identifiers;
- distinguishing namesakes;
- establishing partnership start and end dates;
- resolving trainer organisations or licences externally;
- linking joint labels to verified individual trainer entities.

The same boundary will apply to complex owner labels, where partnerships, syndicates, companies and named co-owners may be represented within one source string.

The current notebook should n
…
```

### Cell 70

Matched: `manual`, `external`

```text
## Stage 34 — Consolidated source-field governance

The preceding stages established the safe treatment of the runner-level connection fields.

This stage records one consolidated decision for each field across:

- source meaning;
- blank handling;
- exact-label identity;
- within-race cardinality;
- punctuation and compound labels;
- cross-role equality;
- normalisation;
- database storage;
- deferred identity resolution.

The table is a notebook-level governance output.

It does not create canonical connection entities.

Therefore empty connection strings should initially be interpreted as source values not supplied.

They must:

- be converted to database nulls in the uncorrected source representation;
- not be interpreted as evidence that no connection existed;
- not be filled from companion runners or inferred from repeated histories;
- be reviewed as a finite manual-repair population;
- be corrected only where an independent authoritative or reputable source identifies the missing value;
- retain repair provenance and the original source value;
- remain null where external verification is unavailable or conflicting.
```

### Cell 71

Matched: `manual`

```text
# Consolidate the notebook's source-semantic findings into one governed table.
#
# These decisions describe safe source handling. They do not claim that exact
# labels are globally unique people, partnerships, organisations or licences.
#
# Blank source values remain preserved in the raw source layer. They may be
# repaired in a separate governed correction layer only where independent
# evidence supplies the missing value and complete provenance is retained.

connection_field_governance = pd.DataFrame(
    [
        {
            "source_field": "jockey",
            "source_level_meaning": (
                "runner-level source-presented jockey label"
            ),
            "blank_treatment": (
                "preserve original empty string in raw source; "
                "represent as null analytically; permit provenance-backed "
                "manual repair from independent evidence"
            ),
            "exact_label_treatment": (
                "preserve exactly as supplied"
            ),
            "within_race_cardinality": (
                "maximum one populated exact label occurrence "
                "per provisional race"
            ),
            "compound_label_treatment": (
                "preserve punctuation and complete raw label"
            ),
            "cross_role_equality": (
                "exact equality with trainer or owner is not "
                "proof of shared identity"
            ),
            "normalisation_policy": (
                "no automatic canonicalisation beyond explicit "
                "missing-value handling"
            ),
            "database_storage": (
                "raw source text plus nullable governed value; "
                "repairs require separate provenance"
            ),
…
```

### Cell 72

Matched: `manual`, `verified`

```text
## Stage 35 — Manual verification queue for blank connection values

The source contains 46 blank field occurrences across 43 runner rows:

- 2 missing jockey values;
- 9 missing trainer values;
- 35 missing owner values.

Two rows are blank for both trainer and owner.

Because this is a small finite population, each missing field occurrence can be reviewed against independent race records.

The verification queue preserves one row per missing field occurrence rather than one row per runner. This allows trainer and owner repairs on the same runner to be researched, evidenced and decided separately.

Each queue row records:

- source row and race identifiers;
- race and runner context;
- the missing source field;
- the original source value;
- the companion connection labels;
- fields for the proposed repaired value;
- evidence source and locator;
- verification date;
- decision and confidence;
- reviewer notes.

Permitted decisions are:

- `pending`;
- `verified_repair`;
- `verified_unavailable`;
- `conflicting_evidence`;
- `not_researched`.

No repaired value should enter the governed database unless its decision is `verified_repair` and its provenance fields are populated.
```

### Cell 73

Matched: `manual`

```text
# Create one manual-verification record per blank field occurrence.
#
# There are 43 affected runner rows but 46 missing field occurrences because
# two rows are blank for both trainer and owner.

manual_connection_repair_rows = []

for _, source_row in blank_connection_rows.iterrows():
    for field in CONNECTION_IDENTITY_FIELDS:
        if not source_row[f"{field}_is_blank"]:
            continue

        manual_connection_repair_rows.append(
            {
                "source_rowid": int(
                    source_row["source_rowid"]
                ),
                "race_id": source_row["race_id"],
                "date": source_row["date"],
                "course": source_row["course"],
                "off": source_row["off"],
                "race_name": source_row["race_name"],
                "race_type": source_row["type"],
                "horse": source_row["horse"],
                "position": source_row["pos"],
                "declared_runners": source_row["ran"],
                "missing_source_field": field,
                "original_source_value": source_row[field],
                "source_jockey": source_row["jockey"],
                "source_trainer": source_row["trainer"],
                "source_owner": source_row["owner"],
                "proposed_repaired_value": pd.NA,
                "evidence_source_name": pd.NA,
                "evidence_source_type": pd.NA,
                "evidence_locator": pd.NA,
                "evidence_accessed_date": pd.NA,
                "verification_decision": "pending",
                "verification_confidence": pd.NA,
                "reviewer_notes": pd.NA,
            }
        )

manual_connection_repair_queue = pd.DataFrame(
    manual_connection_repair_rows
)

manual_string_columns = [
    "proposed
…
```

### Cell 74

Matched: `manual`, `external`

```text
## Stage 36 — Persist and reload the manual connection-repair queue

The manual verification queue is a reusable notebook output.

It must be persisted before external research begins so that:

- the original 46-record pending population is preserved;
- research decisions can be edited outside the notebook if necessary;
- the queue can be reloaded in a fresh kernel;
- later database repairs can be traced to a stable evidence record;
- completed and unresolved cases remain distinguishable.

The persisted file contains source context and verification fields only.

It does not modify the raw source database.
```

### Cell 75

Matched: `manual`, `verified`

```text
# Persist the complete manual connection-repair queue.
#
# Keep this output separate from the immutable raw source database.
connection_repair_output_directory = (
    PROJECT_ROOT
    / "data"
    / "derived"
    / "connection_identity"
)

connection_repair_output_directory.mkdir(
    parents=True,
    exist_ok=True,
)

manual_connection_repair_queue_path = (
    connection_repair_output_directory
    / "manual_connection_repair_queue.csv"
)

manual_connection_repair_queue.to_csv(
    manual_connection_repair_queue_path,
    index=False,
)

# Reload immediately to verify that the persisted artifact is usable.
reloaded_manual_connection_repair_queue = (
    pd.read_csv(
        manual_connection_repair_queue_path,
        dtype={
            "repair_record_id": "string",
            "missing_source_field": "string",
            "original_source_value": "string",
            "source_jockey": "string",
            "source_trainer": "string",
            "source_owner": "string",
            "proposed_repaired_value": "string",
            "evidence_source_name": "string",
            "evidence_source_type": "string",
            "evidence_locator": "string",
            "evidence_accessed_date": "string",
            "verification_decision": "string",
            "verification_confidence": "string",
            "reviewer_notes": "string",
        },
        keep_default_na=True,
    )
)

# Confirm the persisted and reloaded queue retains its governing structure.
assert len(
    reloaded_manual_connection_repair_queue
) == 46

assert reloaded_manual_connection_repair_queue[
    "repair_record_id"
].is_unique

assert set(
    reloaded_manual_connection_repair_queue[
        "repair_record_id"
    ]
) == set(
    manual_connection_repair_queue[
        "repair_record_id"
…
```

### Cell 76

Matched: `external`, `checked against`, `verified`, `racing post`

```text
## Stage 37 — External verification batch 1: missing jockey values

The two missing jockey values were checked against independent historical race records.

### `connection_blank_001`

- horse: `Ahzana (FR)`;
- race: Prix Guy Hunault, Auteuil, 2016-04-08;
- verified jockey: `T. Viel`;
- evidence: two independent historical race sources identify T. Viel as Ahzana's jockey in this race.

The abbreviated source presentation is retained rather than expanding the name to a canonical person identity.

### `connection_blank_002`

- horse: `Millebosc (FR)`;
- race: 149th Wettstar Grosser Preis von Baden, Baden-Baden, 2021-09-05;
- verified jockey: `Adrie de Vries`;
- evidence: the complete historical Racing Post result identifies Adrie de Vries as the jockey.

Both records qualify as provenance-backed repairs.

The original empty strings remain preserved in the raw source layer.
```

### Cell 77

Matched: `https://`, `manual`, `external`, `verified`, `racing post`, `racecard`

```text
# Apply the first externally verified repair batch to the persisted manual
# queue.
#
# These updates affect the governed repair artifact only. They do not overwrite
# the original source database or remove the original empty-string evidence.

from datetime import date

verification_date = date.today().isoformat()

jockey_repair_updates = {
    "connection_blank_001": {
        "proposed_repaired_value": "T. Viel",
        "evidence_source_name": (
            "Canalturf and Coin-Turf"
        ),
        "evidence_source_type": (
            "independent historical horse record and racecard"
        ),
        "evidence_locator": (
            "https://www.canalturf.com/courses_fiche_cheval.php"
            "?idcheval=176640 | "
            "https://www.coin-turf.fr/programmes-courses/"
            "08042016/3080_auteuil/prix-guy-hunault"
        ),
        "evidence_accessed_date": verification_date,
        "verification_decision": "verified_repair",
        "verification_confidence": "high",
        "reviewer_notes": (
            "Both sources identify T. Viel as Ahzana's jockey in "
            "the Prix Guy Hunault on 2016-04-08. Preserve the "
            "source-style abbreviated label; no canonical person "
            "identity is asserted."
        ),
    },
    "connection_blank_002": {
        "proposed_repaired_value": "Adrie de Vries",
        "evidence_source_name": "Racing Post",
        "evidence_source_type": (
            "complete historical race result"
        ),
        "evidence_locator": (
            "https://www.racingpost.com/results/207/"
            "baden-baden/2021-09-05/792961"
        ),
        "evidence_accessed_date": verification_date,
        "verification_decision": "verified_repair",
        "verification_confidence": "high",
…
```

### Cell 78

Matched: `external`, `verified`

```text
## Stage 38 — Complete external review of blank connection values

The remaining 44 missing connection values were reviewed as one finite external-verification population.

The review produced:

- 26 additional `verified_repair` decisions;
- 5 `conflicting_evidence` decisions;
- 13 `insufficient_evidence` decisions;
- no records left `pending`.

Together with the two previously verified jockey repairs, the complete 46-record queue contains:

- 28 provenance-backed repairs;
- 5 records where exact-date sources disagree;
- 13 records where the available evidence does not establish the missing value at the target race date.

A `conflicting_evidence` decision means that two or more apparently relevant sources provide materially different connection labels for the same horse and race.

An `insufficient_evidence` decision does not mean that the value is permanently unknowable. It means that the sources reviewed did not support a race-date repair strongly enough to enter the governed database.

Neither category receives a proposed repaired value.

The raw source database remains unchanged.

Only records classified as `verified_repair`, with a populated repaired value and complete provenance, are eligible for a governed correction layer.
```

### Cell 79

Matched: `https://`, `manual`, `external`, `verified`, `racing post`, `racecard`

```text
# Complete the external-evidence review for all 44 records that remained after
# the two verified jockey repairs.
#
# The raw source database is not modified. This cell updates only the governed
# repair queue and persists the completed evidence log.

from datetime import date

verification_date = date.today().isoformat()

# Reload the latest persisted queue so this cell remains reproducible after a
# fresh-kernel restart.
manual_connection_repair_queue = pd.read_csv(
    manual_connection_repair_queue_path,
    dtype={
        "repair_record_id": "string",
        "missing_source_field": "string",
        "original_source_value": "string",
        "source_jockey": "string",
        "source_trainer": "string",
        "source_owner": "string",
        "proposed_repaired_value": "string",
        "evidence_source_name": "string",
        "evidence_source_type": "string",
        "evidence_locator": "string",
        "evidence_accessed_date": "string",
        "verification_decision": "string",
        "verification_confidence": "string",
        "reviewer_notes": "string",
    },
    keep_default_na=True,
)

assert len(manual_connection_repair_queue) == 46

assert manual_connection_repair_queue[
    "repair_record_id"
].is_unique

# The two jockey repairs must already be present.
existing_jockey_decisions = (
    manual_connection_repair_queue.loc[
        manual_connection_repair_queue[
            "repair_record_id"
        ].isin(
            [
                "connection_blank_001",
                "connection_blank_002",
            ]
        ),
        "verification_decision",
    ]
)

assert existing_jockey_decisions.eq(
    "verified_repair"
).all()

def verified_repair(
    value: str,
    source_name: str,
    source_type: str,
    locator: str,
    notes: str,
…
```

### Cell 80

Matched: `manual`, `verified`

```text
## Stage 39 — Provenance-quality audit of manual connection repairs

The completed evidence log contains a decision for every blank connection occurrence.

Before verified values are promoted into a governed correction artifact, this stage audits whether each decision is structurally reproducible.

The audit checks:

- every repair record has one permitted decision;
- verified repairs contain a nonblank proposed value;
- conflicting and insufficient-evidence records contain no proposed value;
- every decision contains source name, source type, evidence locator, access date, confidence and reviewer notes;
- access dates are parseable;
- verified-repair evidence locators contain a direct web address or require additional locator strengthening.

A descriptive locator may still identify the evidence used, but it is weaker than a direct URL, archived document path or stable publication identifier.

Records requiring stronger locators remain verified at the analytical level, but should not enter the final governed correction artifact until their evidence can be reproduced independently.
```

### Cell 81

Matched: `manual`, `verified`, `racecard`

```text
# Audit the completed manual evidence log before deriving a governed repair
# artifact.
#
# This stage does not alter any decisions or repaired values.

connection_repair_provenance_audit = (
    reloaded_manual_connection_repair_queue.copy()
)

permitted_verification_decisions = {
    "verified_repair",
    "conflicting_evidence",
    "insufficient_evidence",
}

# ----------------------------------------------------------------------
# Structural decision checks
# ----------------------------------------------------------------------

connection_repair_provenance_audit[
    "decision_is_permitted"
] = (
    connection_repair_provenance_audit[
        "verification_decision"
    ].isin(permitted_verification_decisions)
)

connection_repair_provenance_audit[
    "has_proposed_repaired_value"
] = (
    connection_repair_provenance_audit[
        "proposed_repaired_value"
    ]
    .fillna("")
    .str.strip()
    .ne("")
)

connection_repair_provenance_audit[
    "value_decision_is_consistent"
] = (
    (
        connection_repair_provenance_audit[
            "verification_decision"
        ].eq("verified_repair")
        & connection_repair_provenance_audit[
            "has_proposed_repaired_value"
        ]
    )
    |
    (
        connection_repair_provenance_audit[
            "verification_decision"
        ].isin(
            [
                "conflicting_evidence",
                "insufficient_evidence",
            ]
        )
        & ~connection_repair_provenance_audit[
            "has_proposed_repaired_value"
        ]
    )
)

# ----------------------------------------------------------------------
# Required provenance-field checks
# ----------------------------------------------------------------------

required_provenance_columns = [
    "evidence_so
…
```

### Cell 82

Matched: `verified`, `racecard`

```text
## Stage 40 — Strengthening verified-repair evidence locators

The provenance audit identified six verified repairs whose evidence locators were descriptive references rather than direct URLs.

Direct target-race evidence has now been recorded for all six:

- two Funabashi owner records;
- one Ohi owner record;
- two Morioka owner records;
- one further Funabashi owner record.

The strengthened evidence uses:

- official NAR racecards;
- an exact JBIS historical result;
- direct Rakuten Keiba racecards;
- a direct bilingual Mercury Cup listing where Romanised owner presentation was retained.

This stage changes only the evidence-source metadata.

It does not alter:

- the original source values;
- proposed repaired values;
- verification decisions;
- confidence classifications;
- reviewer conclusions.

The Giga King records also demonstrate why ownership must be verified at the individual race date:

- the 2022-07-18 Mercury Cup card lists `尾崎智大`;
- the 2022-09-28 Nippon TV Hai card lists `（株）Ｈｅｒｏレーシング`.

A later or general horse profile would therefore not be a safe substitute for exact-date evidence.
```

### Cell 83

Matched: `https://`, `manual`, `verified`, `racecard`

```text
# Strengthen the six verified repairs whose evidence locators were previously
# descriptive rather than directly reproducible.
#
# Only provenance metadata is changed. The proposed repaired values,
# verification decisions and original source values remain untouched.

manual_connection_repair_queue = pd.read_csv(
    manual_connection_repair_queue_path,
    dtype="string",
    keep_default_na=True,
)

assert len(manual_connection_repair_queue) == 46

assert manual_connection_repair_queue[
    "repair_record_id"
].is_unique

# Record direct target-race locators for the six repairs isolated by the
# provenance audit.
verified_repair_locator_updates = {
    "connection_blank_025": {
        "evidence_source_name": (
            "NAR Local Racing Information Site and Rakuten Keiba"
        ),
        "evidence_source_type": (
            "official and independent exact-date racecards"
        ),
        "evidence_locator": (
            "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/"
            "DebaTable?k_babaCode=19&k_raceDate=2021%2F04%2F07"
            "&k_raceNo=11"
            " | "
            "https://keiba.rakuten.co.jp/race_card/list/"
            "RACEID/202104071900000011"
        ),
    },
    "connection_blank_027": {
        "evidence_source_name": (
            "NAR Local Racing Information Site and Rakuten Keiba"
        ),
        "evidence_source_type": (
            "official and independent exact-date racecards"
        ),
        "evidence_locator": (
            "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/"
            "DebaTable?k_babaCode=19&k_raceDate=2021%2F12%2F01"
            "&k_raceNo=11"
            " | "
            "https://keiba.rakuten.co.jp/race_card/list/"
            "RACEID/202112011914090311"
        ),
    },
    "connection
…
```

### Cell 84

Matched: `verified`

```text
## Stage 41 — Governed connection-value correction artifact

The completed evidence review contains:

- 28 verified repairs;
- 5 conflicting-evidence records;
- 13 insufficient-evidence records.

Only the 28 verified repairs satisfy the requirements for promotion into a governed correction layer.

The correction artifact uses a long structure with one row per:

- source runner row;
- repaired source field.

Each correction record retains:

- the immutable source-row identifier;
- race and runner context;
- the original source value;
- the governed repaired value;
- evidence source and locator;
- evidence-access date;
- confidence;
- reviewer notes;
- repair-record identifier.

The artifact does not overwrite the raw source database.

Downstream database construction may apply it by joining on:

- `source_rowid`;
- `source_field`.

The five conflicting records and thirteen insufficient-evidence records remain null in the governed connection fields.
```

### Cell 85

Matched: `https://`, `manual`, `external`, `verified`, `racing post`, `racecard`

```text
# Derive the governed connection-value correction artifact from the completed
# and provenance-audited manual evidence log.
#
# Only verified repairs that passed every eligibility check are included.

governed_connection_repairs = (
    connection_repair_provenance_audit.loc[
        connection_repair_provenance_audit[
            "eligible_for_governed_repair_artifact"
        ],
        [
            "repair_record_id",
            "source_rowid",
            "race_id",
            "date",
            "course",
            "off",
            "race_name",
            "race_type",
            "horse",
            "missing_source_field",
            "original_source_value",
            "proposed_repaired_value",
            "evidence_source_name",
            "evidence_source_type",
            "evidence_locator",
            "evidence_accessed_date",
            "verification_confidence",
            "reviewer_notes",
        ],
    ]
    .rename(
        columns={
            "missing_source_field": "source_field",
            "proposed_repaired_value": "governed_repaired_value",
        }
    )
    .copy()
)

# Record the correction policy explicitly in every artifact row.
governed_connection_repairs[
    "correction_method"
] = "manual_external_verification"

governed_connection_repairs[
    "correction_status"
] = "approved"

# Stable column order for database ingestion and review.
governed_connection_repairs = (
    governed_connection_repairs[
        [
            "repair_record_id",
            "source_rowid",
            "race_id",
            "date",
            "course",
            "off",
            "race_name",
            "race_type",
            "horse",
            "source_field",
            "original_source_value",
            "governed_repaired_value
…
```

### Cell 86

Matched: `verified`

```text
## Stage 42 — Validate application of governed connection repairs

The governed repair artifact contains one approved correction for each verified missing connection value.

Before database integration, this stage applies the artifact to the corresponding source rows in memory and verifies that:

- every repair matches exactly one source runner row;
- the targeted raw field is blank;
- the governed value is populated;
- no populated source value is overwritten;
- fields not targeted by a repair remain unchanged;
- all 28 approved repairs are applied exactly once;
- unresolved and conflicting records remain blank.

This is an application test only.

The raw source database is opened read-only and is not modified.
```

### Cell 89

Matched: `external`, `verified`

```text
## Stage 44 — Analytical conclusion

The runner-level `jockey`, `trainer` and `owner` fields are source-presented connection labels.

They are highly complete, but they are not globally stable entity identifiers.

### Jockey

The `jockey` field behaves as a runner-level riding assertion:

- 1,851,283 of 1,851,285 runner rows are populated;
- 7,917 exact populated labels occur;
- no exact jockey label appears on more than one runner in the same provisional race;
- two blank values were independently verified and repaired;
- exact equality with trainer or owner labels does not establish shared identity.

The field can be stored safely as nullable raw text.

It cannot support canonical person identity without later namesake and identity-resolution work.

### Trainer

The `trainer` field behaves as a runner-level training-connection assertion:

- 1,851,276 runner rows are populated;
- 10,708 exact populated labels occur;
- one exact trainer label may relate to multiple runners in the same race;
- 120,906 repeated same-race trainer groups contain distinct exact horse labels on every row;
- the largest observed same-race trainer group contains 14 runners.

Trainer labels include individual-looking names, initials, hyphenated forms and compound ampersand structures.

Ampersand labels cannot be split safely by punctuation alone.

They may represent:

- complete individual names;
- compressed shared surnames;
- formal joint-training arrangements;
- stable or licence presentations;
- three or more apparent participants;
- structures that require external verification.

Four missing trainer values were verified and repaired.

Five further missing trainer values produced materially conflicting exact-date evidence and remain null.

The complete raw trainer label must therefore remai
…
```

### Cell 91

Matched: `manual`, `external`, `verified`

```text
## Stage 44 — Analytical conclusion

### Bounded question

What do the runner-level `jockey`, `trainer` and `owner` fields represent in the source, how stable and complete are their labels, and which source-internal identity relationships can be preserved safely without inventing equivalence between people, partnerships, syndicates or organisations?

### Executive conclusion

The three fields are reliable as **runner-level source-presented connection labels**.

They are not reliable as canonical identifiers for people, partnerships, licences, syndicates or organisations.

The database should therefore preserve:

- each original source value exactly;
- analytical nulls for empty strings;
- approved provenance-backed repairs in a separate correction layer;
- complete compound labels as atomic source assertions;
- unresolved and conflicting cases without forced resolution.

### Jockey

The `jockey` field behaves as a runner-level riding assertion.

- 1,851,283 of 1,851,285 runner rows are populated.
- 7,917 exact populated labels occur.
- No exact jockey label appears on more than one runner in the same provisional race.
- The two blank values were independently verified and repaired.
- Exact equality with a trainer or owner label does not establish that the same real person is represented.

The field can safely be stored as nullable raw text.

It cannot support canonical person identity without later namesake and identity-resolution work.

### Trainer

The `trainer` field behaves as a runner-level training-connection assertion.

- 1,851,276 runner rows are populated.
- 10,708 exact populated labels occur.
- One exact trainer label may relate to multiple runners in the same race.
- 120,906 repeated same-race trainer groups contain distinct exact horse labels on every row.
…
```

### Cell 92

Matched: `manual`, `external`, `verified`

```text
## Stage 45 — Notebook closure classification and manual-verification decision

### Closure route

This notebook is classified as a:

> non-rerunnable archival construction record

The notebook preserves the completed investigation, executed outputs, reasoning, anomalies, repair decisions and source lineage.

It is not intended to remain the durable production workflow.

A fresh-kernel top-to-bottom rerun is not required because:

- the analytical investigation is complete;
- governed outputs have been persisted and reloaded;
- the repair artifact has been application-tested against the immutable source;
- external evidence has already been captured with access dates and direct locators;
- rerunning the research cells would repeat finite manual-review work without improving reliability;
- reusable implementation, focused tests and independent validation will live outside the notebook.

Any material cell that performs external verification or overwrites the persisted repair queue should therefore be treated as construction history rather than a routine rerun step.

### Durable notebook outputs

The notebook created and reloaded:

- `data/derived/connection_identity/manual_connection_repair_queue.csv`;
- `data/derived/connection_identity/manual_connection_repair_evidence_log.csv`;
- `data/derived/connection_identity/governed_connection_repairs.csv`.

The governed repair artifact contains:

- 28 approved repairs;
- 2 jockey repairs;
- 4 trainer repairs;
- 22 owner repairs.

The full evidence log retains:

- 28 `verified_repair` decisions;
- 5 `conflicting_evidence` decisions;
- 13 `insufficient_evidence` decisions;
- no pending records.

### Manual-verification decision

Manual-verification status:

> `specialist_reference`

External evidence was used to verify missing joc
…
```

## `notebooks/21_comment_and_embedded_information.ipynb`

### Cell 7

Matched: `external`

```text
## 3. Investigate short values and probable placeholders

The shortest populated comments contain values that may not represent ordinary in-running narratives.

External research indicates that the field is generally a runner-level close-up comment: compressed chronological prose describing a particular performance. However, no standard close-up-comment convention has been identified that explains standalone values such as `"A"`, `"B"`, `"."` or `" -"`.

These values must therefore be investigated from the source rather than assigned meanings from unrelated racing abbreviations.

This stage will examine:

* every distinct populated comment of ten characters or fewer;
* frequency by exact value;
* first and last occurrence;
* course and jurisdiction distribution;
* whether values are concentrated within particular races or source periods;
* the surrounding comments from affected races;
* whether `"."`, `" -"`, isolated letters and symbols behave like missing-value placeholders;
* whether any short values are legitimate compressed racing descriptions.

The following distinctions will be preserved:

* empty source string;
* punctuation-only value;
* whitespace-and-punctuation value;
* isolated letter;
* short word or abbreviation;
* ordinary short narrative.

A familiar abbreviation used elsewhere in racing must not automatically be transferred into this field. For example, `"B"` can have a documented meaning in result or form notation, but that does not establish the same meaning when it appears as the complete `comment` value.

No short value will be converted to null, expanded into a meaning or otherwise normalised until its source distribution and surrounding race context have been inspected.
```

### Cell 9

Matched: `racing post`

```text
### Short-value findings

The **304 populated comments of ten characters or fewer** divide into three materially different groups rather than one general anomaly class.

#### 1. Probable placeholders or unresolved source codes

There are **238 rows** containing punctuation-only, numeric-only or isolated-letter values:

* `"."`: **225 rows**, across 49 provisional races and 21 courses;
* `"B"`: **4 rows**, each in a different race, course and jurisdiction;
* `"A"`: **2 rows**, in two French races;
* `"/"`: **2 rows**, both from one Bahrain race;
* `"-"`: **1 row**;
* `"1"`: **1 row**;
* `"V"`: **1 row**;
* `" -"`: **1 row**;
* `".."`: **1 row**.

These values account for approximately **78.3%** of all comments containing ten characters or fewer, but only about **0.0158%** of all populated comments.

The dominant anomaly is `"."`. It occurs across multiple jurisdictions and years and can affect several runners within the same race. The Racing Post result display reproduces the dots directly beneath affected runners, confirming that they are not introduced by this database extraction. Their repeated placement where an ordinary close-up comment would appear strongly suggests a published placeholder for unavailable commentary, although the exact upstream convention remains undocumented.

The isolated letters are exceptionally rare:

* `"B"` occurs four times between 2015 and 2020 in Japan, Australia, the United States and Argentina;
* `"A"` occurs twice, in France in 2016 and 2021;
* `"V"` occurs once in Argentina.

Original Racing Post result pages also reproduce at least the inspected `"A"` and `"B"` values. They are therefore source-presented values rather than database corruption. However, no reliable published convention has yet been found that establishes their meaning
…
```

### Cell 10

Matched: `external`, `racing post`

```text
## 4. Test the equipment-change hypothesis

A specialist form reader suggested that the isolated letters may indicate a gear change, such as blinkers or a visor.

He did not recognise the letters as an established Raceform or Racing Post close-up-comment convention, so this remains a hypothesis rather than external validation.

This stage will test the idea directly against the source by examining:

- the structured `hg` value on every runner whose complete comment is `A`, `B` or `V`;
- the same horse’s immediately preceding and following source appearances;
- whether headgear is present on the coded run;
- whether the coded run coincides with a change in the recorded equipment value;
- whether one letter consistently corresponds to one equipment state.

The test is deliberately bounded. It will not reopen the full semantics of the `hg` field or attempt to reconstruct equipment history beyond the adjacent source appearances needed to evaluate this hypothesis.

Possible outcomes are:

- **supported**: a stable and repeated relationship is visible;
- **partially supported**: some coded rows coincide with equipment changes but the pattern is inconsistent;
- **not supported**: the letters do not align with recorded equipment;
- **unresolved**: source coverage is insufficient to test the idea safely.

The raw `comment` and `hg` values will remain unchanged regardless of the result.
```

### Cell 12

Matched: `racing post`

```text
### Equipment-change hypothesis result

The source does not support the suggestion that standalone `A`, `B` or `V` comments indicate a recorded headgear change.

Across all seven coded rows:

- the current `hg` value is empty in every case;
- no coded run has a populated equipment value;
- every available previous and next appearance also has an empty `hg` value;
- no coded run differs from the preceding or following `hg` state.

By code:

- `A`: 2 rows, no populated current or adjacent `hg`;
- `B`: 4 rows, no populated current or adjacent `hg`;
- `V`: 1 row, no populated current or adjacent `hg`.

The specialist suggestion was useful because it produced a direct falsifiable test. On the evidence available in this source, that hypothesis is **not supported**.

This does not prove that the letters cannot refer to equipment in the upstream publication, because the `hg` field may itself be incomplete or use jurisdiction-specific conventions. However, there is no positive source evidence linking these letters to headgear, and no stable correspondence can be inferred.

The correct treatment remains:

- preserve the raw letter unchanged;
- classify it as an `unresolved_source_code`;
- do not expand it into blinkers, visor or another equipment meaning;
- do not treat it as a standard Racing Post or Raceform convention without further evidence.
```

### Cell 13

Matched: `external`, `verified`

```text
## 5. Profile embedded market and attributed-report markers

The field is not purely an in-running narrative. External research and the short-value evidence show that it can also contain:

- opening-price markers such as `op`;
- touched-price markers such as `tchd`;
- jockey, trainer or veterinary explanations;
- post-race findings or other attributed reports.

This stage will measure how often those structures occur and whether they appear:

- alone;
- appended to an ordinary close-up;
- in different capitalisation or punctuation forms;
- in particular periods, jurisdictions or courses;
- together within the same comment.

The analysis will remain marker-based rather than semantic. Detecting the exact text `op`, `tchd`, `jockey said`, `trainer said` or similar wording does not prove that every surrounding parenthetical has one uniform structure.

The purpose is to establish whether the field contains stable, recurring subfamilies that may justify later deterministic span extraction.

No parenthetical text will yet be removed from the narrative, parsed into canonical values or treated as independently verified fact.
```

### Cell 38

Matched: `manual`

```text
## 12. Provisional semantic and database decisions

The source-wide profiling, manual inspection and jurisdiction comparison now support a bounded interpretation of `comment`.

This stage records the decisions reached so far without implementing a parser or replacing the raw field.

The register distinguishes:

- confirmed field meaning;
- source-coverage limitations;
- unresolved short codes and placeholders;
- embedded terminal material;
- permitted database treatment;
- work explicitly deferred to a later study.

These are governance decisions for preserving and using the source field, not claims that every comment can already be parsed reliably.
```

### Cell 39

Matched: `manual`, `external`

```text
# Record the field-level conclusions reached from Notebook 21 evidence.
# This table governs preservation and analytical use without authorising a
# speculative parser or destructive cleaning rule.
comment_semantic_decisions = pd.DataFrame(
    [
        {
            "decision_area": "Field meaning",
            "decision": (
                "Interpret populated substantive values as runner-level "
                "English-language descriptions of race position and performance."
            ),
            "status": "Confirmed",
            "evidence": (
                "Manual inspection across British, Irish and selected overseas "
                "jurisdictions showed consistent in-running narrative content."
            ),
        },
        {
            "decision_area": "Jurisdiction consistency",
            "decision": (
                "Use the same broad field meaning across jurisdictions when "
                "substantive text is present."
            ),
            "status": "Confirmed",
            "evidence": (
                "France, Germany, Australia, Italy, Hong Kong, the United States "
                "and the UAE contained recognisably comparable performance prose."
            ),
        },
        {
            "decision_area": "Coverage",
            "decision": (
                "Treat comment availability as jurisdiction- and feed-dependent "
                "rather than as a source-wide random missingness process."
            ),
            "status": "Confirmed",
            "evidence": (
                "Great Britain and Ireland were complete while several overseas "
                "feeds were sparse or selective."
            ),
        },
        {
            "decision_area": "Empty values",
            "decision": (
                "
…
```

## `notebooks/22_jockey_and_trainer_identity.ipynb`

### Cell 0

Matched: `manual`

```text
# Notebook 22 — Jockey and Trainer Identity

## Bounded question

Can raw `jockey` and `trainer` labels be mapped safely to stable source-internal and, where evidence permits, real-world participant identities without merging different people or splitting the same person unnecessarily?

## Purpose

This notebook investigates the source semantics, physical behaviour and identity risks of the runner-level `jockey` and `trainer` fields.

It is an identity study, not a participant-performance ranking exercise. Raw-label aggregates remain source-label analysis unless and until an identity mapping is supported by evidence.

The investigation will begin with source-wide profiling. It will not assume that punctuation removal, case folding, initial expansion, title removal, whitespace normalisation or fuzzy matching is safe.

The study will distinguish between:

* immutable raw source labels;
* exploratory candidate-match text;
* source-internal participant occurrences;
* governed equivalence decisions;
* governed split decisions;
* unresolved relationships;
* authority- or evidence-backed real-world identities.

No broad name normalisation or cross-role merge is authorised in advance.

## Source and grain

* **Source database:** `data/raw/form_2015-present/form_2015-present/raceform.db`
* **Source table:** `data`
* **Governed data-row predicate:** `rowid <> 1`
* **Fields under investigation:** `jockey`, `trainer`
* **Declared source type:** to be confirmed from SQLite
* **Provisional grain:** runner-level source assertions about race participants
* **Raw preservation:** required
* **Current analytical status:** identity semantics pending
* **Notebook 20 relationship:** existing blank supplementation remains governed and must not be silently replaced or reinterpreted here
* **No
…
```

### Cell 11

Matched: `external`

```text
### Structural residue findings

Direct inspection confirms that unusual jockey-label structures are not one homogeneous problem.

The only single-token populated label is `Reserve`, occurring twice in 2026. This appears structurally unlike a personal name and must be investigated as a possible source placeholder rather than assigned a participant identity.

Long labels include several legitimate naming structures:

* multi-part surnames;
* Arabic patronymic or family-name conventions;
* embedded initials;
* compound surnames;
* amateur or social titles such as `Mr`, `Ms`, `Mlle`, `Mme` and `Frau`;
* suffixes such as `Jr`.

The source therefore mixes personal-name content with presentation metadata. A title cannot safely remain part of the eventual identity key without first testing whether the same person appears under another title or without one.

The displayed residue also contains possible variation candidates, including:

* `Mr S J P Baragry` and `Mr S J P Bargary`;
* `Mlle Anna Van Den Troost` and `Mme Anna Van Den Troost`.

These examples do not yet justify correction or equivalence. Similar strings may represent source defects, title changes, or different people. They require chronology, jurisdiction, race context and external evidence before any governed merge.

The next step measures title and prefix conventions source-wide. No title is removed from the raw label and no person-level identity is inferred.
```

### Cell 13

Matched: `external`, `checked against`

```text
## 3. Candidate duplicate and variant jockey labels

The source contains 7,917 distinct raw jockey labels. A distinct label is not yet assumed to represent either:

* one unique real-world individual; or
* a unique presentation of that individual.

The first candidate-generation stage tests only a narrow presentation difference already observed in the source: a leading title such as `Mr`, `Miss`, `Mlle`, `Mme`, `Ms`, `Mrs` or `Frau`.

For comparison only, the leading title is removed and whitespace is standardised. Raw labels remain unchanged.

A shared comparison key identifies labels requiring investigation; it does not establish that the labels belong to the same person. Every resulting candidate group must later be checked against source context and authoritative external evidence before any merge or split decision is recorded.

No fuzzy matching, spelling correction, initial expansion or identity resolution is performed in this stage.
```

### Cell 17

Matched: `external`

```text
### Same-race collision test

Observed date overlap does not establish that two labels represent different people. One jockey may be recorded under competing presentation conventions during the same period.

A stronger test is whether both labels occur within the same provisional race.

The provisional race key is:

`date + course + off`

Where two candidate labels occur on separate runner rows within the same provisional race, they cannot ordinarily represent one jockey riding both runners. Such a result is therefore evidence against merging the labels automatically.

However, same-race occurrence is not by itself proof of two correctly recorded people. The underlying rows may still contain a source error, duplicated record or incorrect jockey attribution. Every detected collision remains subject to source-row inspection and external verification.

Labels without a same-race collision also remain unresolved. Absence of collision does not prove that they represent the same person.
```

### Cell 19

Matched: `external`, `published result`

```text
### Same-race collision finding

The same-race test found one collision among the 216 strict candidate pairs.

On 11 November 2017 at Naas, the 4:05 race contains:

* `Miss B ONeill` riding `Hawthorn Echo (IRE)` for Peter McCreery;
* `Mr B ONeill` riding `Chisholm Trail (IRE)` for Paul Nolan.

The two labels occur on separate source rows and separate runners within the same provisional race.

Published result evidence independently confirms both riders. Horse Racing Ireland identifies `Mr B ONeill` as Barry O'Neill. The complete identity of `Miss B ONeill` remains unresolved from the evidence inspected so far, but the simultaneous race occurrence proves that she is a different person.

Decision:

* `Miss B ONeill` and `Mr B ONeill` must not be merged;
* the shared title-stripped comparison key `b oneill` is a genuine real-world identity collision;
* title removal is suitable only for candidate generation and cannot be used as an automatic identity key;
* the immutable raw labels and both source-row lineages must remain preserved.

This decision depends on external evidence and must be captured with reusable provenance before Notebook 22 closes.
```

### Cell 20

Matched: `external`, `checked against`

```text
# Compare the source context of the 215 strict candidate pairs that never
# occur together in one provisional race.
#
# Shared horses can provide strong candidate evidence that two raw labels may
# describe the same rider under different presentation conventions. Shared
# trainers are weaker evidence because many jockeys ride for the same trainer.
#
# Neither measure resolves identity. The output only ranks the finite set that
# must later be checked against authoritative external evidence.

collision_free_strict_pairs = (
    jockey_strict_candidate_pairs.loc[
        jockey_strict_candidate_pairs[
            "same_race_collisions"
        ].eq(0)
    ]
    .copy()
    .reset_index(drop=True)
)

# Reduce the already-loaded candidate occurrences to distinct label/context
# combinations. Raw horse and trainer labels remain unchanged.
jockey_label_horse_context = (
    jockey_strict_candidate_occurrences[
        [
            "raw_jockey_label",
            "horse",
        ]
    ]
    .dropna(subset=["horse"])
    .drop_duplicates()
)

jockey_label_trainer_context = (
    jockey_strict_candidate_occurrences[
        [
            "raw_jockey_label",
            "trainer",
        ]
    ]
    .dropna(subset=["trainer"])
    .drop_duplicates()
)

pair_context_rows = []

for pair_record in collision_free_strict_pairs.to_dict("records"):
    left_label = pair_record["left_raw_jockey_label"]
    right_label = pair_record["right_raw_jockey_label"]

    # Build exact raw-label sets separately for each candidate label. No horse
    # or trainer identity normalisation is introduced at this stage.
    left_horses = set(
        jockey_label_horse_context.loc[
            jockey_label_horse_context[
                "raw_jockey_label"
            ].eq(left_label),
            "hor
…
```

### Cell 21

Matched: `manual`, `external`

```text
### Strict candidate manual-review queue

The 215 collision-free strict pairs show materially different levels of source-internal support.

Pairs sharing exact horse labels are the strongest alias candidates because the same horses appear under both jockey labels. Shared trainers provide weaker support, while pairs with no shared source context rely only on title-stripped name equivalence.

This evidence is used only to order manual research. It does not resolve identity.

The review queue therefore records:

* the known same-race collision as a confirmed split candidate;
* shared-horse pairs as the highest-priority alias candidates;
* shared-trainer-only pairs as secondary candidates;
* pairs with no shared context as lower-evidence candidates that still require review.

Every pair remains unresolved until authoritative external evidence supports a merge, split or unresolved decision.
```

### Cell 22

Matched: `manual`, `external`

```text
# Build one complete strict-candidate review queue containing the confirmed
# same-race collision and all 215 collision-free candidate pairs.
#
# Review priority reflects the strength of source-internal evidence only. It is
# not an identity confidence score and does not authorise any automatic merge.

strict_candidate_review_queue = (
    jockey_strict_candidate_pairs[
        [
            "strict_comparison_key",
            "left_raw_jockey_label",
            "right_raw_jockey_label",
            "pair_label_structure",
            "temporal_relationship",
            "overlap_days",
            "gap_days",
            "left_runner_rows",
            "right_runner_rows",
            "combined_runner_rows",
            "same_race_collisions",
        ]
    ]
    .merge(
        jockey_strict_pair_context[
            [
                "strict_comparison_key",
                "left_raw_jockey_label",
                "right_raw_jockey_label",
                "shared_horse_count",
                "shared_horses",
                "shared_trainer_count",
                "shared_trainers",
                "context_candidate_status",
            ]
        ],
        how="left",
        on=[
            "strict_comparison_key",
            "left_raw_jockey_label",
            "right_raw_jockey_label",
        ],
        validate="one_to_one",
    )
)

# The same-race collision was excluded from the earlier context table, so its
# context fields remain blank. This is deliberate: its collision evidence
# already places it in the strongest do-not-merge review category.
strict_candidate_review_queue[
    "context_candidate_status"
] = strict_candidate_review_queue[
    "context_candidate_status"
].fillna("same_race_collision")

strict_candidate_review_queue[
    [
        "shar
…
```

### Cell 23

Matched: `external`

```text
### Persist the strict jockey-identity review queue

The strict candidate analysis has produced a finite review population of 216 jockey-label pairs:

* 1 same-race collision;
* 114 pairs sharing exact horse labels;
* 46 pairs sharing trainers but no exact horse labels;
* 55 pairs supported only by title-stripped label equivalence.

This population should not remain only in notebook memory. It will be persisted as a review queue at:

`data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv`

The file is an analytical working output, not yet the final governed identity reference.

Each row represents one candidate relationship between two immutable raw jockey labels. It preserves:

* the candidate-generation method;
* source-internal supporting or contradictory evidence;
* chronology;
* review priority;
* unresolved identity and verification states;
* fields for later external evidence and decisions.

The raw labels remain unchanged. A comparison key or shared-horse pattern does not authorise a merge.

After external verification, confirmed relationships will be transferred into a separately validated participant-identity reference with stable entity identifiers and permanent provenance. Unresolved cases will remain explicitly unresolved rather than being guessed.
```

### Cell 24

Matched: `manual`, `external`, `verified`

```text
from pathlib import Path

# Persist the complete strict candidate population as a working review queue.
#
# This is written under data/processed rather than data/reference because the
# 216 relationships have not yet been externally verified. The file records
# the review workload and its source-internal evidence; it is not a completed
# participant-identity authority.
JOCKEY_IDENTITY_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jockey_identity"
)

JOCKEY_STRICT_REVIEW_QUEUE_PATH = (
    JOCKEY_IDENTITY_OUTPUT_DIR
    / "jockey_strict_candidate_review_queue.csv"
)

JOCKEY_IDENTITY_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# Create the persisted schema explicitly rather than writing every temporary
# notebook column. The review fields begin unresolved and will be populated
# only when external evidence has actually been inspected.
jockey_strict_candidate_review_output = (
    strict_candidate_review_queue[
        [
            "candidate_pair_id",
            "strict_comparison_key",
            "left_raw_jockey_label",
            "right_raw_jockey_label",
            "pair_label_structure",
            "temporal_relationship",
            "gap_days",
            "overlap_days",
            "left_runner_rows",
            "right_runner_rows",
            "combined_runner_rows",
            "same_race_collisions",
            "shared_horse_count",
            "shared_horses",
            "shared_trainer_count",
            "shared_trainers",
            "context_candidate_status",
            "review_priority",
            "review_reason",
        ]
    ]
    .copy()
)

# Record how each pair entered the queue. At this stage all 216 rows were
# generated through exact case-folded equivalence after removal of only the
# observed l
…
```

### Cell 25

Matched: `external`, `published result`, `verified`

```text
### Refine the review schema before recording decisions

The persisted review queue requires one schema correction before external decisions are entered.

A single `verified_person_name` field is insufficient for relationships classified as `different_people`, because each raw label may resolve to a different named individual. The review artifact will therefore store:

* `left_verified_person_name`;
* `right_verified_person_name`.

Either field may remain blank where the relationship is established but the person's complete name has not been verified.

The relationship vocabulary is:

* `same_person`;
* `different_people`;
* `unresolved`.

A `different_people` decision does not require both complete names where separate identity is independently established, such as two labels occurring on different runners in the same race. It does require the evidence and reasoning to be preserved.

The first candidate, `Miss B ONeill` versus `Mr B ONeill`, is therefore resolvable as `different_people`. Published results independently list both labels on separate horses in the same Naas race on 11 November 2017. The complete name represented by `Miss B ONeill` remains unresolved and will not be invented.
```

### Cell 26

Matched: `https://`, `manual`, `external`, `published result`, `verified`

```text
# Refine the persisted review schema before recording external decisions.
#
# A single verified_person_name field cannot safely represent a split
# relationship. Replace it with one verified-name field for each raw label.
reloaded_jockey_strict_review_queue = pd.read_csv(
    JOCKEY_STRICT_REVIEW_QUEUE_PATH,
    keep_default_na=False,
)

verified_person_name_position = (
    reloaded_jockey_strict_review_queue.columns.get_loc(
        "verified_person_name"
    )
)

reloaded_jockey_strict_review_queue = (
    reloaded_jockey_strict_review_queue.drop(
        columns="verified_person_name"
    )
)

reloaded_jockey_strict_review_queue.insert(
    verified_person_name_position,
    "left_verified_person_name",
    "",
)

reloaded_jockey_strict_review_queue.insert(
    verified_person_name_position + 1,
    "right_verified_person_name",
    "",
)

# Record the first externally supported relationship.
#
# The published result confirms that both labels occur on different runners
# in the same race. This establishes separate people even though the complete
# name represented by the female rider's source label remains unresolved.
b_oneill_mask = reloaded_jockey_strict_review_queue[
    "candidate_pair_id"
].eq("JOCKEY-STRICT-0001")

assert b_oneill_mask.sum() == 1

reloaded_jockey_strict_review_queue.loc[
    b_oneill_mask,
    "identity_relationship",
] = "different_people"

# Barry O'Neill is retained only on the right-hand label. The left-hand full
# name remains blank because it has not yet been established sufficiently.
reloaded_jockey_strict_review_queue.loc[
    b_oneill_mask,
    "left_verified_person_name",
] = ""

reloaded_jockey_strict_review_queue.loc[
    b_oneill_mask,
    "right_verified_person_name",
] = "Barry O'Neill"

reloaded_jockey_strict_review_queue.loc[
…
```

### Cell 27

Matched: `external`, `verified`, `racing post`

```text
### Verified alias: Marie Velon

`Mlle Marie Velon` and `Mme Marie Velon` are confirmed as two source-label presentations of the same jockey, Marie Vélon.

Source-internal evidence includes:

* 80 shared exact horse labels;
* 116 shared trainer labels;
* 2,449 combined runner rows;
* no same-race collision;
* only 20 days between the source-observed label periods.

External evidence provides a stable real-world identity:

* France Galop records one jockey, Marie Vélon, with a continuous professional career;
* Racing Post assigns Marie Velon one jockey profile, identifier `95747`;
* historical and current results associated with that profile use the presentation `Mme Marie Velon`.

The external result presentation does not support treating `Mlle` and `Mme` as reliable chronological status markers. Historical races may currently be displayed with a later or standardised title.

Decision:

* relationship: `same_person`;
* verified name: `Marie Vélon`;
* both immutable raw labels remain preserved;
* both labels may map to one future jockey participant identity;
* the title itself must not be used as an effective-dated identity attribute without separate evidence.
```

### Cell 28

Matched: `https://`, `external`, `verified`, `racing post`

```text
# Record the second externally verified strict relationship.
#
# France Galop records one continuous jockey identity for Marie Vélon, while
# Racing Post uses the single jockey profile identifier 95747. Together with
# the extensive shared-horse evidence, this supports a same-person decision.
#
# The source titles remain preserved exactly. The decision does not interpret
# Mlle-to-Mme as a verified marital or chronological transition.

verified_jockey_strict_review_queue = pd.read_csv(
    JOCKEY_STRICT_REVIEW_QUEUE_PATH,
    keep_default_na=False,
)

marie_velon_mask = verified_jockey_strict_review_queue[
    "candidate_pair_id"
].eq("JOCKEY-STRICT-0002")

assert marie_velon_mask.sum() == 1

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "identity_relationship",
] = "same_person"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "left_verified_person_name",
] = "Marie Vélon"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "right_verified_person_name",
] = "Marie Vélon"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "verification_status",
] = "confirmed"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "verification_id",
] = "NB22-JOCKEY-0002"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "evidence_type",
] = "governing_body_profile; published_jockey_profile"

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "evidence_locator",
] = (
    "https://www.france-galop.com/fr/content/"
    "la-jockey-marie-velon-signe-une-annee-2022-exceptionnelle"
    "; "
    "https://www.racingpost.com/profile/jockey/95747/"
    "mme-marie-velon"
)

verified_jockey_strict_review_queue.loc[
    marie_velon_mask,
    "evidence_accessed_date",
] = "2026-08-
…
```

### Cell 29

Matched: `external`, `verified`

```text
### Prepare the first batch of unresolved jockey relationships

Two strict candidate relationships have now been verified:

* `JOCKEY-STRICT-0001` — different people;
* `JOCKEY-STRICT-0002` — same person.

The remaining 214 relationships will not be handled through one bespoke notebook cell per pair.

Instead, external verification will use bounded review batches. The first batch contains the 25 highest-ranked unresolved pairs supported by shared exact horse labels.

The batch file is a temporary research worksheet. It preserves the permanent candidate identifiers from the complete review queue and provides empty fields for evidence and decisions.

After the batch has been researched:

1. completed decisions will be validated;
2. the matching rows in the complete 216-row review queue will be updated;
3. the batch file will remain as review provenance;
4. unresolved members will remain unresolved rather than being forced into a decision.
```

### Cell 30

Matched: `external`, `verified`

```text
# Prepare the first reusable external-verification batch rather than creating
# one bespoke notebook cell for every candidate pair.

JOCKEY_VERIFICATION_BATCH_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jockey_identity"
    / "verification_batches"
)

JOCKEY_VERIFICATION_BATCH_01_PATH = (
    JOCKEY_VERIFICATION_BATCH_DIR
    / "jockey_strict_verification_batch_01.csv"
)

JOCKEY_VERIFICATION_BATCH_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

verified_jockey_strict_review_queue = pd.read_csv(
    JOCKEY_STRICT_REVIEW_QUEUE_PATH,
    keep_default_na=False,
)

# Select the 25 strongest unresolved shared-horse candidates.
#
# Existing review order already ranks candidates by:
# - source-evidence category;
# - shared-horse count;
# - shared-trainer count;
# - combined runner volume.
jockey_verification_batch_01 = (
    verified_jockey_strict_review_queue.loc[
        verified_jockey_strict_review_queue[
            "verification_status"
        ].eq("not_started")
        & verified_jockey_strict_review_queue[
            "context_candidate_status"
        ].eq("shared_horse")
    ]
    .head(25)
    .copy()
    .reset_index(drop=True)
)

# Keep only the evidence needed for efficient external review.
jockey_verification_batch_01 = (
    jockey_verification_batch_01[
        [
            "candidate_pair_id",
            "left_raw_jockey_label",
            "right_raw_jockey_label",
            "temporal_relationship",
            "gap_days",
            "overlap_days",
            "left_runner_rows",
            "right_runner_rows",
            "combined_runner_rows",
            "shared_horse_count",
            "shared_horses",
            "shared_trainer_count",
            "shared_trainers",
        ]
    ]
)

# Add explicit review-result fields.
…
```

### Cell 31

Matched: `external`

```text
### Authority-first external verification schema

The 25-pair verification batch will use the relevant racing authority as its primary identity source wherever public evidence is available.

Authority evidence differs by jurisdiction:

* the BHA and HRI may provide a public participant profile or stable identifier;
* France Galop may publish an official name in results, rankings, articles or licensing material without exposing a public participant identifier;
* some historical or lower-profile riders may not have a sufficiently complete public authority record.

The review schema must therefore permit an authority-confirmed name without requiring an authority participant ID.

For each candidate pair, the review will record separately:

* the governing authority;
* the authority-published name;
* any public authority participant identifier;
* the authority evidence type and locator;
* any secondary provider identifier used as corroboration;
* the final relationship decision.

The evidence hierarchy is:

1. public governing-authority identity evidence;
2. authority-published rides, results or licensing records;
3. stable secondary participant identifiers;
4. source-internal shared horses, trainers and chronology.

Secondary providers may corroborate an identity but do not replace authority evidence where authority evidence is publicly available.

No candidate is automatically merged because the two labels differ only by a title. Where public evidence remains insufficient, the relationship remains unresolved.
```

### Cell 32

Matched: `external`, `verified`

```text
# Refine the first verification batch around authority-first identity evidence.
#
# Public authority systems are not uniform. An authority may expose:
# - a registered name and stable participant identifier;
# - a published name without a public identifier;
# - only result, ranking or licensing evidence;
# - no sufficient public evidence.
#
# The schema therefore keeps authority name, identifier and evidence method
# separate and allows identifiers to remain blank.

jockey_verification_batch_01 = pd.read_csv(
    JOCKEY_VERIFICATION_BATCH_01_PATH,
    keep_default_na=False,
)

authority_review_columns = {
    "governing_jurisdiction": "",
    "governing_authority": "",
    "authority_registered_name": "",
    "authority_participant_id": "",
    "authority_evidence_type": "",
    "authority_evidence_locator": "",
    "authority_evidence_accessed_date": "",
    "authority_lookup_status": "not_checked",
    "secondary_provider": "",
    "secondary_participant_id": "",
    "secondary_display_name": "",
    "secondary_evidence_locator": "",
    "secondary_lookup_status": "not_checked",
}

for column_name, default_value in authority_review_columns.items():
    if column_name not in jockey_verification_batch_01.columns:
        jockey_verification_batch_01[column_name] = default_value

# Reorder the worksheet so authority evidence sits immediately before the
# final decision fields. Existing candidate evidence and prior decisions remain
# unchanged.
decision_columns = [
    "identity_relationship",
    "left_verified_person_name",
    "right_verified_person_name",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "review_notes",
    "database_action",
]

authority_columns = list(authority_review_columns)
…
```

### Cell 35

Matched: `manual`, `external`

```text
### Proportionate stopping rule for strict jockey candidates

Strict title removal identified 216 candidate relationships between raw jockey labels. It did not establish 216 real-world identity relationships.

The investigation confirmed:

* one same-race collision that must remain split;
* one externally supported same-person relationship;
* 214 relationships that remain unresolved;
* shared horses, trainers, courses and active periods can strengthen a candidate but cannot prove identity;
* comprehensive historical verification would require disproportionate manual reconstruction across several racing authorities and publication systems.

The database exists to support analysis and writing. It is not intended to become a complete international jockey registry.

The stopping rule is therefore:

1. preserve every immutable raw jockey label and its source-row lineage;
2. preserve every generated candidate relationship;
3. apply only externally supported merge or split decisions;
4. leave all other candidate relationships unresolved;
5. revisit an unresolved relationship only when a specific analysis, article or materially important participant requires it;
6. never aggregate unresolved raw labels as one definitive real-world jockey.

The 25-pair authority-review batch is retained as evidence of the proposed verification method, but its remaining research is deferred until an analytical need justifies it.

This is an intentional governed unresolved state, not incomplete automatic cleaning.
```

### Cell 36

Matched: `external`, `published result`, `verified`

```text
# Apply the proportionate stopping rule without changing any unresolved
# relationship into a merge or split.
#
# The complete candidate queue remains available for future targeted review.
# Confirmed decisions remain active. All other relationships are explicitly
# deferred until a specific analytical use makes their resolution material.

jockey_strict_review_queue = pd.read_csv(
    JOCKEY_STRICT_REVIEW_QUEUE_PATH,
    keep_default_na=False,
)

jockey_verification_batch_01 = pd.read_csv(
    JOCKEY_VERIFICATION_BATCH_01_PATH,
    keep_default_na=False,
)

assert len(jockey_strict_review_queue) == 216
assert jockey_strict_review_queue[
    "candidate_pair_id"
].is_unique

assert len(jockey_verification_batch_01) == 25
assert jockey_verification_batch_01[
    "candidate_pair_id"
].is_unique

# Remove the unsupported full-name enrichment from the B O'Neill split.
#
# The published result proves that Miss B O'Neill and Mr B O'Neill rode in the
# same race and therefore represent different people. That result does not by
# itself establish that Mr B O'Neill's full registered name was Barry O'Neill.
b_oneill_mask = jockey_strict_review_queue[
    "candidate_pair_id"
].eq("JOCKEY-STRICT-0001")

assert b_oneill_mask.sum() == 1

jockey_strict_review_queue.loc[
    b_oneill_mask,
    "left_verified_person_name",
] = ""

jockey_strict_review_queue.loc[
    b_oneill_mask,
    "right_verified_person_name",
] = ""

jockey_strict_review_queue.loc[
    b_oneill_mask,
    "review_notes",
] = (
    "The published 4:05 Naas result on 2017-11-11 lists "
    "Miss B O'Neill and Mr B O'Neill as separate riders in the "
    "same race. This confirms that the two raw labels represent "
    "different people. The evidence does not establish either "
    "rider's full registered name, so both
…
```

### Cell 40

Matched: `manual`, `verified`

```text
# Reconcile the nine immutable raw trainer blanks with Notebook 20.
#
# Notebook 20 stores the blank marker together with source locators in
# raw_source_value, for example:
# "blank; source_rowid=...; race_id=...; repair_record_id=..."

MANUAL_VERIFICATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "manual_verifications.csv"
)

CONNECTION_IDENTITY_REPAIRS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "connection_identity_repairs.csv"
)

manual_verifications = pd.read_csv(
    MANUAL_VERIFICATIONS_PATH,
    keep_default_na=False,
)

connection_identity_repairs = pd.read_csv(
    CONNECTION_IDENTITY_REPAIRS_PATH,
    keep_default_na=False,
)

nb20_trainer_blank_verifications = (
    manual_verifications.loc[
        manual_verifications[
            "verification_id"
        ].str.startswith("NB20-CONNECTION-")
        & manual_verifications[
            "source_field"
        ].eq("trainer")
        & manual_verifications[
            "raw_source_value"
        ].str.startswith("blank;")
    ]
    .copy()
    .sort_values("verification_id")
    .reset_index(drop=True)
)

nb20_trainer_repairs = (
    connection_identity_repairs.loc[
        connection_identity_repairs[
            "source_field"
        ].eq("trainer")
    ]
    .copy()
    .sort_values("verification_id")
    .reset_index(drop=True)
)

raw_empty_trainer_rows = int(
    trainer_source_profile_summary.loc[
        0,
        "empty_string_trainer_rows",
    ]
)

confirmed_trainer_supplementations = int(
    nb20_trainer_blank_verifications[
        "database_action"
    ].eq("source_supplementation").sum()
)

preserved_unresolved_trainer_blanks = int(
    nb20_trainer_blank_verifications[
        "database_action"
    ].eq("preserve_raw_unresolved").sum()
)

assert raw
…
```

### Cell 47

Matched: `verified`

```text
# Apply the bounded trainer-title decision.
#
# Only exact-name, non-overlapping Mlle -> Mme pairs are accepted as
# source-label transitions. This does not assert independently verified
# real-world identity.

trainer_title_decisions = (
    trainer_candidate_chronology.copy()
)

trainer_title_decisions[
    "identity_relationship"
] = "unresolved"

trainer_title_decisions[
    "decision_basis"
] = (
    "strict title-removal candidate only"
)

trainer_title_decisions[
    "confidence"
] = "low"

trainer_title_decisions[
    "database_action"
] = "preserve_raw_unresolved"

confirmed_transition_mask = (
    trainer_title_decisions[
        "title_structure"
    ].eq("two_titled_labels")
    & trainer_title_decisions[
        "title_sequence"
    ].eq("mlle_then_mme")
    & trainer_title_decisions[
        "chronology_status"
    ].eq("separate_active_periods")
)

trainer_title_decisions.loc[
    confirmed_transition_mask,
    "identity_relationship",
] = "same_provisional_trainer"

trainer_title_decisions.loc[
    confirmed_transition_mask,
    "decision_basis",
] = (
    "exact post-title name with non-overlapping Mlle-to-Mme "
    "source transition, supported by the source-wide January 2024 "
    "presentation discontinuity"
)

trainer_title_decisions.loc[
    confirmed_transition_mask,
    "confidence",
] = "high_source_label_equivalence"

trainer_title_decisions.loc[
    confirmed_transition_mask,
    "database_action",
] = (
    "map_both_labels_to_same_provisional_trainer_identity"
)

trainer_title_decisions[
    "mapping_method"
] = ""

trainer_title_decisions.loc[
    confirmed_transition_mask,
    "mapping_method",
] = "exact_mlle_to_mme_source_transition"

trainer_title_decisions[
    "review_scope_status"
] = "deferred_until_material_use"

trainer_title_deci
…
```

### Cell 49

Matched: `verified`

```text
### Trainer identity stopping point

The trainer investigation produced a narrower usable result than the jockey investigation.

The immutable source contains 10,708 distinct populated trainer labels. Strict removal of one recognised leading title generated 53 candidate groups involving 106 raw labels.

A source-wide discontinuity occurs around January 2024:

* `Mlle` usage falls from 935 runner rows in 2023 to 30 in 2024;
* `Mme` usage rises from 789 runner rows in 2023 to 1,939 in 2024;
* multiple exact post-title names change from `Mlle` to `Mme` at approximately the same time.

A bounded rule therefore accepts 26 exact-name, non-overlapping `Mlle → Mme` transitions whose earlier label remained active in the second half of 2023 and whose later label began in the first half of 2024.

These mappings cover 6,350 runner rows.

The rule establishes high-confidence source-label equivalence, not independently verified legal or licensing identity. Both immutable raw labels must remain preserved and the relationship must be recorded as provisional.

The remaining 27 candidate groups are unresolved. They include:

* overlapping titled and untitled labels;
* the overlapping `Mlle L Pontoir` and `Mme L Pontoir` pair;
* English and German title variants;
* exact-name recurrences separated by periods too distant from the observed 2024 source transition.

No general title-stripping rule is authorised.

The practical database consequence is:

1. preserve every raw trainer label;
2. map the 26 governed pairs to shared provisional trainer identities;
3. record the method as `bounded_2024_mlle_to_mme_source_transition`;
4. retain all other title-derived relationships as unresolved candidates;
5. revisit unresolved labels only when they materially affect a specific analysis, article or
…
```

### Cell 52

Matched: `validation_status`

```text
# Validate the provisional trainer mapping against the immutable source rows.
#
# This confirms only coverage and join behaviour. It does not add any further
# trainer identities or reinterpret unresolved labels.

mapped_trainer_labels = (
    trainer_provisional_identity_mapping_reloaded[
        "raw_trainer_label"
    ].tolist()
)

mapped_trainer_placeholders = ", ".join(
    ["?"] * len(mapped_trainer_labels)
)

mapped_trainer_source_rows = pd.read_sql_query(
    f"""
    SELECT
        rowid AS source_rowid,
        race_id AS source_race_id,
        date,
        course,
        off,
        horse,
        trainer AS raw_trainer_label
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND trainer IN (
          {mapped_trainer_placeholders}
      )
    """,
    connection,
    params=mapped_trainer_labels,
)

assert not mapped_trainer_source_rows.empty

mapped_trainer_source_rows = (
    mapped_trainer_source_rows.merge(
        trainer_provisional_identity_mapping_reloaded[
            [
                "provisional_trainer_id",
                "raw_trainer_label",
                "label_role",
                "mapping_method",
                "confidence",
            ]
        ],
        on="raw_trainer_label",
        how="left",
        validate="many_to_one",
    )
)

assert mapped_trainer_source_rows[
    "provisional_trainer_id"
].notna().all()

assert mapped_trainer_source_rows[
    "source_rowid"
].is_unique

assert len(mapped_trainer_source_rows) == 6350

assert (
    mapped_trainer_source_rows[
        "provisional_trainer_id"
    ].nunique()
    == 26
)

assert (
    mapped_trainer_source_rows[
        "raw_trainer_label"
    ].nunique()
    == 52
)

trainer_mapping_coverage = (
    mapped_trainer_source_rows.groupby(
        [
            "provisiona
…
```

### Cell 55

Matched: `external`

```text
# Create and persist the final trainer-identity governance summary.
#
# This provides a compact audit record of what was mapped, what remains
# unresolved, and what the governed outputs cover.

trainer_identity_governance_summary = pd.DataFrame(
    [
        {
            "metric": "distinct_populated_raw_trainer_labels",
            "value": 10708,
            "status": "profiled",
            "governance_meaning": (
                "Immutable populated trainer labels observed in the source"
            ),
        },
        {
            "metric": "raw_blank_trainer_rows",
            "value": 9,
            "status": "reconciled_with_notebook_20",
            "governance_meaning": (
                "Four externally supplemented and five preserved unresolved"
            ),
        },
        {
            "metric": "strict_title_candidate_groups",
            "value": len(trainer_title_decisions_reloaded),
            "status": "reviewed",
            "governance_meaning": (
                "Candidates generated by removing one recognised leading title"
            ),
        },
        {
            "metric": "accepted_provisional_trainer_identities",
            "value": int(
                trainer_provisional_identity_mapping_reloaded[
                    "provisional_trainer_id"
                ].nunique()
            ),
            "status": "governed",
            "governance_meaning": (
                "Bounded 2024 Mlle-to-Mme source-label transitions"
            ),
        },
        {
            "metric": "accepted_raw_trainer_labels",
            "value": len(
                trainer_provisional_identity_mapping_reloaded
            ),
            "status": "mapped",
            "governance_meaning": (
                "Two immutable raw labels per prov
…
```

### Cell 56

Matched: `verified`

```text
### Trainer identity conclusion

The trainer field is materially more usable than the jockey field, but it still does not support unrestricted name normalisation.

The source contains:

* 10,708 distinct populated raw trainer labels;
* nine blank trainer rows already governed through Notebook 20;
* 53 strict title-derived candidate groups;
* 106 raw labels involved in those candidate groups.

The investigation identified one narrow, defensible source-level rule.

A marked presentation change occurred around January 2024, when `Mlle` usage collapsed and `Mme` usage increased sharply. Twenty-six exact-name, non-overlapping `Mlle → Mme` pairs align with that transition window.

Those 26 pairs:

* create 26 provisional trainer identities;
* govern 52 immutable raw labels;
* cover 6,350 source runner rows;
* contain no duplicate source-row joins;
* contain no unmatched mapping rows.

The accepted relationship is **source-label equivalence**, not independently verified legal or licensing identity.

The remaining 27 candidate groups, containing 54 raw labels, remain unresolved. They include overlapping labels, English and German title variants, and `Mlle/Mme` recurrences outside the bounded 2024 transition window.

Therefore:

1. raw trainer labels remain immutable;
2. only the 26 governed pairs may share provisional trainer identities;
3. the mapping method is `bounded_2024_mlle_to_mme_source_transition`;
4. all other title-derived candidates remain explicitly unresolved;
5. no general trainer title-stripping or automatic identity-merging rule is authorised;
6. unresolved cases should be revisited only when they materially affect a specific article, analysis or participant.

This is the analytical stopping point for trainer identity in Notebook 22.
```

### Cell 59

Matched: `manual`

```text
### Owner blanks

The owner field contains 35 empty-string rows and no SQL-null rows.

Before investigating populated owner labels, these blank rows must be reconciled with any earlier manual verification or supplementation work. A blank owner cannot be interpreted as “no owner”; it means that no usable owner label was retained in this source row.
```

### Cell 61

Matched: `manual`, `verified`

```text
# Reconcile the 35 blank owner rows against the permanent governed
# manual-verification register used by Notebook 20.
#
# The register does not have a dedicated source_rowid column. Notebook 20
# preserves the physical source row identifier inside raw_source_value.

MANUAL_VERIFICATIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "manual_verifications.csv"
)

assert MANUAL_VERIFICATIONS_PATH.exists()

manual_verifications = pd.read_csv(
    MANUAL_VERIFICATIONS_PATH,
    keep_default_na=False,
)

required_manual_verification_columns = {
    "verification_id",
    "source_field",
    "raw_source_value",
    "verified_value",
    "verification_status",
    "governing_notebook",
    "confidence",
    "notes",
    "database_action",
}

assert required_manual_verification_columns.issubset(
    manual_verifications.columns
)

notebook_20_owner_verifications = (
    manual_verifications.loc[
        manual_verifications[
            "governing_notebook"
        ].astype(str).eq("20")
        & manual_verifications[
            "source_field"
        ].eq("owner")
    ]
    .copy()
    .reset_index(drop=True)
)

notebook_20_owner_verifications[
    "source_rowid"
] = pd.to_numeric(
    notebook_20_owner_verifications[
        "raw_source_value"
    ].str.extract(
        r"source_rowid=(\d+)"
    )[0],
    errors="raise",
).astype(int)

assert notebook_20_owner_verifications[
    "verification_id"
].is_unique

assert notebook_20_owner_verifications[
    "source_rowid"
].is_unique

blank_owner_reconciliation = (
    blank_owner_rows.merge(
        notebook_20_owner_verifications[
            [
                "source_rowid",
                "verification_id",
                "verified_value",
                "verification_status",
                "confidence"
…
```

### Cell 62

Matched: `manual`, `external`, `verified`

```text
### Owner blank-field reconciliation

All 35 empty-string owner rows were previously governed through Notebook 20.

The permanent manual-verification register contains one matching record for every blank source row:

* 22 rows have confirmed externally verified owners and are authorised for `source_supplementation`;
* 13 rows remain unresolved and are authorised only for `preserve_raw_unresolved`;
* no blank owner row remains outside the existing governance record.

Notebook 23 therefore inherits these decisions without repeating the external research.

The immutable raw owner value remains blank. Any verified owner must be added only through the governed supplementation layer with its Notebook 20 verification identifier, evidence method and confidence preserved.
```

### Cell 67

Matched: `verified`

```text
# Test whether reordered owner-label variants occur within the same race.
#
# Same-race use of two or more raw labels with the exact same token multiset
# is strong source-internal evidence that token order is presentation noise.
#
# This still establishes ownership-composition equivalence, not verified
# legal identity for every named person or organisation inside the label.

owner_candidate_source_rows = pd.read_sql_query(
    f"""
    SELECT
        rowid AS source_rowid,
        race_id AS source_race_id,
        date,
        course,
        off,
        horse,
        owner AS raw_owner_label
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND owner IS NOT NULL
      AND TRIM(owner) <> ''
    """,
    connection,
)

owner_candidate_source_rows = (
    owner_candidate_source_rows.merge(
        owner_token_collision_labels[
            [
                "raw_owner_label",
                "token_multiset_key",
                "candidate_structure",
            ]
        ],
        on="raw_owner_label",
        how="inner",
        validate="many_to_one",
    )
)

assert owner_candidate_source_rows[
    "source_rowid"
].is_unique

owner_same_race_variant_profile = (
    owner_candidate_source_rows.groupby(
        [
            "date",
            "course",
            "off",
            "token_multiset_key",
        ],
        as_index=False,
    )
    .agg(
        raw_label_count=(
            "raw_owner_label",
            "nunique",
        ),
        runner_rows=(
            "source_rowid",
            "size",
        ),
        raw_labels=(
            "raw_owner_label",
            lambda values: " || ".join(
                sorted(set(values))
            ),
        ),
        horses=(
            "horse",
            lambda values: " || ".join(
…
```

### Cell 68

Matched: `verified`

```text
### Bounded owner token-order rule

Exact token-multiset comparison generated 936 candidate groups containing owner labels with the same words in different orders.

All 936 groups represent genuine order changes rather than punctuation-only differences.

A same-race test found direct source-internal evidence for 41 groups. Within those groups, two or more differently ordered labels occur in the same reconstructed race while retaining exactly the same token multiset.

This demonstrates that, for those 41 groups, token order is source-presentation variation rather than a meaningful difference in the named ownership composition.

The rule is deliberately bounded:

1. preserve every immutable raw owner label;
2. accept only token-multiset groups with same-race variant evidence;
3. map those labels to one provisional ownership-composition identity;
4. record the method as `same_race_exact_owner_token_multiset`;
5. treat the result as composition equivalence, not verified legal identity of every named person or organisation;
6. preserve the remaining 895 token-multiset groups as unresolved candidates.

No general owner token-sorting or automatic word-order normalisation rule is authorised.
```

### Cell 72

Matched: `validation_status`

```text
# Validate the provisional owner-composition mapping against the immutable
# source rows.
#
# This confirms source coverage and join cardinality only. It does not infer
# individual legal ownership identities inside a compressed owner label.

mapped_owner_labels = (
    owner_provisional_composition_mapping_reloaded[
        "raw_owner_label"
    ].tolist()
)

mapped_owner_placeholders = ", ".join(
    ["?"] * len(mapped_owner_labels)
)

mapped_owner_source_rows = pd.read_sql_query(
    f"""
    SELECT
        rowid AS source_rowid,
        race_id AS source_race_id,
        date,
        course,
        off,
        horse,
        owner AS raw_owner_label
    FROM data
    WHERE {DATA_ROW_PREDICATE}
      AND owner IN (
          {mapped_owner_placeholders}
      )
    """,
    connection,
    params=mapped_owner_labels,
)

assert not mapped_owner_source_rows.empty

mapped_owner_source_rows = (
    mapped_owner_source_rows.merge(
        owner_provisional_composition_mapping_reloaded[
            [
                "provisional_owner_composition_id",
                "raw_owner_label",
                "token_multiset_key",
                "mapping_method",
                "confidence",
            ]
        ],
        on="raw_owner_label",
        how="left",
        validate="many_to_one",
    )
)

assert mapped_owner_source_rows[
    "provisional_owner_composition_id"
].notna().all()

assert mapped_owner_source_rows[
    "source_rowid"
].is_unique

assert len(mapped_owner_source_rows) == 9788

assert (
    mapped_owner_source_rows[
        "provisional_owner_composition_id"
    ].nunique()
    == 41
)

assert (
    mapped_owner_source_rows[
        "raw_owner_label"
    ].nunique()
    == 95
)

owner_mapping_coverage = (
    mapped_owner_source_rows.groupby(
        [
…
```

### Cell 76

Matched: `verified`

```text
### Owner identity conclusion and limitations

The governed source contains 1,851,285 runner rows and 98,234 distinct populated raw owner labels. A further 35 raw owner blanks were already governed through Notebook 20: 22 have evidence-backed supplementations and 13 remain unresolved.

Owner labels are structurally mixed. They can describe individuals, partnerships, syndicates, companies, studs, clubs and compressed groups of several named parties. Broad owner-name normalisation would therefore create unacceptable false equivalences.

Exact token-multiset comparison identified 936 groups in which two or more raw labels contained precisely the same tokens in different orders. These were treated as candidates only.

A bounded source-internal rule accepted 41 groups where differently ordered variants occurred within the same reconstructed race. This provides strong evidence that token order was presentation noise for those particular ownership compositions.

The accepted rule produced:

- 41 provisional ownership-composition identities;
- 95 mapped raw owner labels;
- 9,788 mapped runner rows;
- no duplicate source-row joins;
- no unmatched mapped labels.

The remaining 895 token-multiset groups, covering 1,822 raw labels and 24,406 runner rows, remain unresolved because they lacked direct same-race variant evidence.

These mappings establish high-confidence source-label equivalence for the complete named ownership composition. They do not independently verify the legal identity, ownership share or continuing membership of every person or organisation named within a compressed label.

No general token sorting, title removal, punctuation removal, partnership decomposition or owner-entity reconstruction is authorised. Immutable raw labels remain preserved, unresolved candida
…
```

### Cell 77

Matched: `external`, `verified`

```text
## Notebook conclusion

This notebook investigated whether participant labels could be converted into governed identity relationships without silently overwriting the immutable source.

### Jockeys

The source contained 7,917 distinct populated jockey labels.

Strict comparison after removing only recognised personal titles produced 212 candidate groups containing 426 labels and 216 candidate relationships.

Only one relationship was confirmed as the same jockey:

- `Mlle Marie Velon`
- `Mme Marie Velon`

One relationship was confirmed as different because both labels occurred in the same race:

- `Miss B ONeill`
- `Mr B ONeill`

The remaining 214 relationships remain unresolved. No general jockey-title removal or broad identity reconstruction is authorised.

### Trainers

The source contained 10,708 distinct populated trainer labels and nine blank trainer rows. Those blanks were already governed through Notebook 20, with four evidence-backed supplementations and five unresolved rows.

Strict title comparison produced 53 candidate groups. A bounded chronology rule accepted 26 `Mlle` to `Mme` transitions where:

- the post-title name matched exactly;
- the `Mlle` label ended between July and December 2023;
- the `Mme` label began between January and June 2024;
- the two labels had separate active periods.

Those decisions created:

- 26 provisional trainer identities;
- 52 mapped raw labels;
- 6,350 mapped runner rows;
- 27 preserved unresolved candidate groups.

The result represents high-confidence source-label equivalence, not independently verified legal or licensing identity. No general trainer-title removal is authorised.

### Owners

The source contained 98,234 distinct populated owner labels and 35 blank owner rows. Notebook 20 already governed all 35 blanks, pro
…
```

## `notebooks/23_comment_rendering_diagnostic.ipynb`

### Cell 5

Matched: `manual`, `external`

```text
## Conclusion

The apparent `Walkover<br><br><br>` value was **not stored in either Source Version 1 or the accepted Inside Rails database**.

A source-wide check found zero admitted comments containing a literal `<` character. The accepted database row for Queensbury Boy at Hereford on 12 May 2026 stores the comment exactly as `Walkover`, with character length 8 and UTF-8 hexadecimal `57616C6B6F766572`.

The apparent `<br>` markup was introduced after the stored value during rendered-output / copy-paste transport. This was confirmed when copied notebook output also merged material from a separate diagnostic cell into the same pasted representation.

Therefore no comment-cleaning transformation is justified. Existing Notebook 21 comment governance remains unchanged.

**Confidence:** high.

**Manual/external verification:** `not_applicable`.

The separate race-time question is outside this diagnostic.
```

## `notebooks/24_race_time_database_extension.ipynb`

### Cell 12

Matched: `verified`

```text
### Design decision — one race-time record per structural race occurrence

The evidence supports a single governed temporal extension at race grain.

Its logical grain is:

> exactly one temporal record for each `core_source_race_occurrence`.

The extension must preserve:

- the existing structural race identifier and raw `date + course + off`;
- the governed IANA racecourse timezone;
- both pre-boundary candidate UK civil timestamps;
- candidate UTC and course-local timestamps where civil-time conversion is valid;
- intentional null candidate conversions at governed DST edges;
- the selected UK, UTC and course-local advertised start where resolved;
- selected branch;
- decision method;
- decision confidence;
- temporal resolution status.

The temporal extension does not alter race identity and does not overwrite raw `off`.

Because accepted Database v1 is immutable, implementation must occur through a new candidate/release boundary rather than by modifying `inside_rails_v1.sqlite3` in place.

Before physical DDL is written, the proposed cross-field constraints must be verified against all 189,043 governed temporal rows.

The next bounded question is:

> Does every governed race-time row satisfy the complete set of constraints we intend the database itself to enforce?
```

## `notebooks/25_database_v2_governed_integration_inventory.ipynb`

### Cell 0

Matched: `external`

```text
# Notebook 25 — Database v2 Governed Integration Inventory

## Purpose

Accepted Inside Rails Database v1 deliberately implemented only the minimum structural core.

That design preserved the immutable source, reconstructed Source Version 1 race occurrences and runner participations, and recorded database governance and validation evidence. However, many reusable governed outputs established by the preceding source-field notebooks were deliberately left outside the physical SQLite database.

Reader-facing studies now require a study-ready database containing those governed representations directly.

This notebook therefore asks:

> Which reusable governed outputs established by Notebooks 04–22 should be physically integrated into Inside Rails Database v2?

The investigation will review every Notebook 04–22 individually and classify its database consequence as one of:

1. **Integrate into Database v2** — reusable governed information required by studies or downstream analysis.
2. **Remain external governed evidence** — important project evidence that should not become a database field or relation.
3. **Remain deliberately unresolved/raw-only** — the notebook established that no defensible canonical replacement is available.
4. **No additional integration required** — the relevant result is already represented by the accepted structural database.

No Database v2 schema or database write is authorised until all nineteen notebooks have an explicit disposition.

The completed race-time investigation in abandoned Notebook 24 may be reused as supporting evidence when Notebook 11 is assessed, but Notebook 24 itself is not the Database v2 design notebook.
```

### Cell 1

Matched: `external`

```text
# Notebook 25 — Database v2 Governed Integration Inventory

## Purpose

Accepted Inside Rails Database v1 deliberately implemented only the minimum structural core.

That design preserved the immutable source, reconstructed Source Version 1 race occurrences and runner participations, and recorded database governance and validation evidence. However, many reusable governed outputs established by the preceding source-field notebooks were deliberately left outside the physical SQLite database.

Reader-facing studies now require a study-ready database containing those governed representations directly.

This notebook therefore asks:

> Which reusable governed outputs established by Notebooks 04–22 should be physically integrated into Inside Rails Database v2?

The investigation will review every Notebook 04–22 individually and classify its database consequence as one of:

1. **Integrate into Database v2** — reusable governed information required by studies or downstream analysis.
2. **Remain external governed evidence** — important project evidence that should not become a database field or relation.
3. **Remain deliberately unresolved/raw-only** — the notebook established that no defensible canonical replacement is available.
4. **No additional integration required** — the relevant result is already represented by the accepted structural database.

No Database v2 schema or database write is authorised until all nineteen notebooks have an explicit disposition.

The completed race-time investigation in abandoned Notebook 24 may be reused as supporting evidence when Notebook 11 is assessed, but Notebook 24 itself is not the Database v2 design notebook.
```

### Cell 4

Matched: `external`

```text
### Notebook 04 disposition

**Database v2 classification: partial integration, with later-notebook supersession.**

#### Integrate

Notebook 04's source-supported race-surface derivation belongs in Database v2 at `core_source_race_occurrence` grain.

Required governed values:

- `candidate_surface`;
- `surface_evidence`.

Accepted rule:

- raw course contains `(AW)` -> `all_weather_unspecified` with explicit-course-marker evidence;
- otherwise -> `unresolved` with no source-supported surface evidence.

Validated Source Version 1 population:

- 189,043 races;
- 33,023 `all_weather_unspecified`;
- 156,020 `unresolved`.

Absence of `(AW)` must not be interpreted as turf, dirt or any other surface. Any later external surface enrichment must remain a separate governed assertion and must not overwrite the source-supported value.

#### Defer to later notebook authority

Notebook 04's candidate course-label and jurisdiction reconstruction is reusable supporting logic, but it is not the final Database v2 semantic authority.

- Notebook 09 became the semantic owner of jurisdiction interpretation.
- Notebook 12 created the permanent governed course-location/timezone reference.

Notebook 04's 395 provisional venue/configuration identities must therefore not be promoted directly as permanent course identities.

The eight NH Flat/type conflicts are also outside the surface representation and remain for the later race-classification disposition.

**Notebook 04 v2 disposition: COMPLETE.**
```

### Cell 8

Matched: `verified`

```text
## Notebook 06 — Race distance parsing

### Database v2 disposition

**Classification: integrate into Database v2.**

Notebook 06 establishes a reusable governed race-distance representation at `core_source_race_occurrence` grain.

Validated Source Version 1 state:

- 189,043 races;
- exactly one raw distance value per race;
- 63 distinct governed raw distance expressions;
- 189,043 parsed races;
- 0 unresolved races in the current source snapshot;
- source-implied distances between 880 and 8,030 yards;
- 0 races independently verified against an official-distance authority.

Database v2 should materialise:

- `distance_miles_component`;
- `distance_whole_furlongs_component`;
- `distance_has_half_furlong`;
- `distance_total_furlongs`;
- `distance_source_implied_yards`;
- `distance_source_implied_metres`;
- `distance_official_verified`;
- `distance_parse_status`;
- parser/governance version provenance.

The immutable raw `dist` value remains authoritative source evidence and must not be overwritten.

The derived yard and metre values describe the literal source notation only. They must not be presented as independently verified official race distances.

Only the 63 exact raw forms governed by Notebook 06 are currently authorised. Previously unseen forms must remain unresolved until separately investigated, even when a generic parser could interpret them.

**Notebook 06 v2 disposition: COMPLETE.**
```

### Cell 10

Matched: `verified`

```text
## Notebook 07 — Carried weight parsing

### Database v2 disposition

**Classification: integrate into Database v2.**

Notebook 07 establishes a reusable governed carried-weight representation at `core_runner_participation` grain.

Validated Source Version 1 state:

- 1,851,285 runner records;
- 79 distinct raw `wgt` values;
- all current values stored as SQLite text;
- all current values use governed stones-and-pounds notation;
- all current runner values parse successfully;
- source-implied total weights range from 96 to 179 lb;
- 0 current unresolved runner records;
- 0 independently verified official-weight records.

Database v2 should materialise:

- `weight_notation_family`;
- `carried_weight_stones`;
- `carried_weight_remainder_pounds`;
- `carried_weight_total_pounds`;
- `carried_weight_implied_kg`;
- `weight_parse_status`;
- `weight_ambiguity_flag`;
- `weight_anomaly_flags`;
- `official_weight_verified`;
- parser/governance version provenance.

The immutable raw `wgt` remains source evidence and must not be overwritten or duplicated as replacement truth.

`carried_weight_implied_kg` is only the mathematical SI conversion of the source stones-and-pounds expression. It must not be presented as an independently verified official metric declaration.

Unsupported notation, unexpected storage types and malformed values must remain explicitly unresolved rather than being trimmed, normalised or guessed.

**Notebook 07 v2 disposition: COMPLETE.**
```

### Cell 12

Matched: `external`

```text
## Notebook 08 — Starting price parsing

### Database v2 disposition

**Classification: integrate into Database v2, including governed corrections with explicit provenance.**

Notebook 08 establishes reusable starting-price arithmetic at `core_runner_participation` grain.

Database v2 should materialise the governed parser outputs:

* `starting_price_kind`;
* `starting_price_numerator`;
* `starting_price_denominator`;
* exact fractional-odds representation;
* exact decimal-odds representation;
* exact implied-probability representation;
* `starting_price_favourite_marker`;
* `starting_price_favourite_status`;
* `starting_price_market_context_status`;
* parser/governance version provenance.

The immutable raw `sp` value must remain permanently recoverable.

### Corrections and enrichments

Database v2 is allowed to contain corrected or externally enriched values where the project has sufficient governed evidence.

A correction must never silently replace the immutable raw source assertion.

Instead, the database must preserve both:

1. the exact raw source value; and
2. the governed corrected or enriched value, together with its provenance.

For a governed correction or enrichment the database must retain enough metadata to establish:

* the exact affected source/runner record;
* the raw source value;
* the corrected or enriched value;
* the evidence source or locator;
* evidence access date;
* verification status;
* confidence;
* governing notebook or decision;
* correction/enrichment method;
* applicable governance/build version.

### Governed `F` anomaly

Source Version 1 contains exactly one raw `sp` value equal to `F` without an attached numerical price.

The affected record is the governed Almendares (GB) occurrence.

The raw source assertion remains:

`sp = 'F'`
…
```

### Cell 19

Matched: `manual`

```text
from pathlib import Path
import subprocess

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

# Identify the actual Notebook 12 file rather than reconstructing its filename.
notebook_matches = sorted(
    path
    for path in (PROJECT_ROOT / "notebooks").glob("12_*.ipynb")
    if path.is_file()
)

assert len(notebook_matches) == 1, (
    "Expected exactly one Notebook 12; "
    f"found {[path.name for path in notebook_matches]}"
)

notebook_path = notebook_matches[0]
print(f"Notebook 12: {notebook_path.relative_to(PROJECT_ROOT)}")

# Locate the durable course-identity, location, timezone and provenance artifacts
# before deciding how the permanent course reference enters Database v2.
result = subprocess.run(
    [
        "git",
        "-C",
        str(PROJECT_ROOT),
        "grep",
        "-l",
        "-E",
        r"Notebook 12",
        "--",
        "docs",
        "src",
        "scripts",
        "tests",
    ],
    capture_output=True,
    text=True,
    check=False,
)

if result.returncode not in (0, 1):
    raise RuntimeError(result.stderr)

references = sorted(
    line.strip()
    for line in result.stdout.splitlines()
    if line.strip()
)

print("\nTracked Notebook 12 references:")
for path in references:
    print(f"  - {path}")

Notebook 12: notebooks/12_course_timezone_resolution_completed_archive.ipynb

Tracked Notebook 12 references:
  - docs/COURSE_LOCATIONS_DATABASE_INTEGRATION.md
  - docs/CROSS_NOTEBOOK_IMPLEMENTATION_COMPLETENESS_AUDIT.md
  - docs/MANUAL_VERIFICATION_BACKFILL.md
  - docs/NOTEBOOK_04_IMPLEMENTATION_RECONCILIATION.md
  - docs/NOTEBOOK_14_CLOSEOUT.json
  - docs/PHASE_3_EVIDENCE_STATUS_MATRIX.md
  - docs/REPORT_12_COURSE_LOCATION_AND_TIMEZONE_MAPPING.md
  - docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.m
…
```

### Cell 20

Matched: `manual`

```text
## Notebook 12 — Course location and timezone resolution

### Database v2 disposition

**Classification: integrate into Database v2 as the permanent governed course reference.**

Notebook 12 establishes the authoritative course-identity, location and timezone enrichment required by downstream studies and by Notebook 11 temporal reconstruction.

### Permanent course identity

The governed course-reference key is:

* `candidate_course_label`;
* `candidate_jurisdiction`.

Database v2 should materialise a permanent course-reference relation keyed uniquely by that pair.

The reference should retain:

* `candidate_course_label`;
* `candidate_jurisdiction`;
* physical venue name;
* locality;
* region;
* country;
* latitude;
* longitude;
* IANA timezone;
* location evidence;
* location resolution/validation status;
* applicable reference/governance version.

Coordinates may remain nullable because exact geospatial resolution and sufficient timezone resolution are different requirements.

### Current authoritative baseline

The durable permanent reference contains:

* 395 unique governed course identities;
* 395 assigned IANA timezones;
* 0 unresolved timezone assignments;
* 51 distinct valid IANA timezone names.

The earlier archived Notebook 12 count of 394 identities is superseded by the durable validated reference.

Database v2 must therefore use the current governed total of 395.

### Source-facing attachment

Raw `course` text must remain unchanged.

A source race is attached to the permanent reference by first deriving:

* `candidate_course_label`;
* `candidate_jurisdiction`;
* jurisdiction derivation evidence;

and then joining the governed identity pair to the course reference.

The raw source label itself is not a reliable permanent venue key.

Current Source Version 1
…
```

### Cell 23

Matched: `manual`

```text
from pathlib import Path
import subprocess

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

# Identify the actual Notebook 14 file rather than reconstructing its filename.
notebook_matches = sorted(
    path
    for path in (PROJECT_ROOT / "notebooks").glob("14_*.ipynb")
    if path.is_file()
)

assert len(notebook_matches) == 1, (
    "Expected exactly one Notebook 14; "
    f"found {[path.name for path in notebook_matches]}"
)

notebook_path = notebook_matches[0]
print(f"Notebook 14: {notebook_path.relative_to(PROJECT_ROOT)}")

# Locate the durable runner-count, runner-number and entry-semantics artifacts
# before deciding their Database v2 consequence.
result = subprocess.run(
    [
        "git",
        "-C",
        str(PROJECT_ROOT),
        "grep",
        "-l",
        "-E",
        r"Notebook 14",
        "--",
        "docs",
        "src",
        "scripts",
        "tests",
    ],
    capture_output=True,
    text=True,
    check=False,
)

if result.returncode not in (0, 1):
    raise RuntimeError(result.stderr)

references = sorted(
    line.strip()
    for line in result.stdout.splitlines()
    if line.strip()
)

print("\nTracked Notebook 14 references:")
for path in references:
    print(f"  - {path}")

Notebook 14: notebooks/14_runner_counts_numbers_and_entries.ipynb

Tracked Notebook 14 references:
  - docs/COURSE_LOCATIONS_DATABASE_INTEGRATION.md
  - docs/CROSS_NOTEBOOK_IMPLEMENTATION_COMPLETENESS_AUDIT.md
  - docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md
  - docs/MANUAL_VERIFICATION_BACKFILL.md
  - docs/MANUAL_VERIFICATION_REGISTER.md
  - docs/NOTEBOOK_12_CLOSEOUT.json
  - docs/NOTEBOOK_14_CLOSEOUT.json
  - docs/PHASE_3_EVIDENCE_STATUS_MATRIX.md
  - docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md
  - docs/RUNNER_ENTRIES_
…
```

### Cell 24

Matched: `external`, `verified`, `racecard`

```text
## Notebook 14 — Runner counts, numbers and entries

### Database v2 disposition

**Classification: integrate into Database v2, including governed missing-runner supplementations and external verification evidence.**

Notebook 14 establishes separate governed meanings for:

* source-reported race count `ran`;
* stored source runner-row count;
* source runner number `num`;
* externally verified missing-runner supplementations;
* external confirmations or contradictions affecting selected exceptional races.

These concepts must not be collapsed into one generic `field_size` or `runner_number` representation.

### Race-level `ran` representation

At `core_source_race_occurrence` grain, Database v2 should materialise:

* `source_reported_ran`;
* `source_runner_row_count`;
* `source_ran_distinct_value_count`;
* `source_ran_consistency_status`;
* `source_row_count_vs_ran_status`;
* `source_runner_coverage_status`;
* `source_ran_external_status`;
* applicable governance/version provenance.

`source_reported_ran` remains a source-presented count.

It must not automatically be described as:

* verified starters;
* declarations;
* complete published-result runners;
* expected racecard entries.

Current Source Version 1 baseline:

* 189,043 races;
* 37 distinct `ran` values;
* minimum `ran` = 1;
* maximum `ran` = 40;
* 189,043 races internally consistent for `ran`;
* 189,038 races where stored runner rows equal `ran`;
* 5 races where stored runner rows are below `ran`;
* 0 races where stored rows exceed `ran`.

Internal equality does not prove external completeness.

### Runner-level `num` representation

At `core_runner_participation` grain, Database v2 should materialise:

* raw `num` through immutable source lineage;
* `source_num_storage_class`;
* `source_positive_runner_numbe
…
```

### Cell 25

Matched: `manual`

```text
from pathlib import Path
import subprocess

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

# Identify the actual Notebook 15 file rather than reconstructing its filename.
notebook_matches = sorted(
    path
    for path in (PROJECT_ROOT / "notebooks").glob("15_*.ipynb")
    if path.is_file()
)

assert len(notebook_matches) == 1, (
    "Expected exactly one Notebook 15; "
    f"found {[path.name for path in notebook_matches]}"
)

notebook_path = notebook_matches[0]
print(f"Notebook 15: {notebook_path.relative_to(PROJECT_ROOT)}")

# Locate the durable beaten-distance implementation, manual evidence,
# supplementation and database-integration artifacts before deciding v2 scope.
result = subprocess.run(
    [
        "git",
        "-C",
        str(PROJECT_ROOT),
        "grep",
        "-l",
        "-E",
        r"Notebook 15",
        "--",
        "docs",
        "src",
        "scripts",
        "tests",
    ],
    capture_output=True,
    text=True,
    check=False,
)

if result.returncode not in (0, 1):
    raise RuntimeError(result.stderr)

references = sorted(
    line.strip()
    for line in result.stdout.splitlines()
    if line.strip()
)

print("\nTracked Notebook 15 references:")
for path in references:
    print(f"  - {path}")

Notebook 15: notebooks/15_beaten_distance_semantics.ipynb

Tracked Notebook 15 references:
  - docs/BEATEN_DISTANCE_INTEGRATION.md
  - docs/NOTEBOOK_15_CLOSEOUT.json
  - docs/NOTEBOOK_15_FIELD_GOVERNANCE.md
  - docs/NOTEBOOK_15_LESSONS_LEARNED.md
  - docs/PHASE_3_EVIDENCE_STATUS_MATRIX.md
  - docs/RUNNER_RECORD_SUPPLEMENTATION_INTEGRATION.md
  - scripts/validate_beaten_distances.py
  - scripts/validate_runner_record_supplementations.py
  - src/inside_rails/beaten_distance.py
```

### Cell 26

Matched: `external`, `verified`, `official result`

```text
## Notebook 15 — Beaten-distance semantics

### Database v2 disposition

**Classification: integrate into Database v2, with separate governed verification, supplementation and correction layers.**

Notebook 15 establishes the reusable interpretation of source runner fields:

* `ovr_btn`;
* `btn`.

These fields describe physical-finish distance structure and must remain semantically separate from the final official placing represented by `pos`.

### Governed source semantics

`ovr_btn` is the cumulative distance from the source physical-finish first-place reference.

`btn` is the incremental margin from the preceding physical finisher or stored distance group.

The text sentinel:

`-`

means that a numeric beaten distance is unavailable.

It must never become zero.

### Runner-level Database v2 representation

At `core_runner_participation` grain, Database v2 should materialise:

* `ovr_btn_numeric`;
* `ovr_btn_status`;
* `btn_numeric`;
* `btn_status`;
* `positive_official_winner_distance`;
* `later_position_zero_overall`;
* `same_distance_group`;
* `beaten_distance_requires_review`;
* applicable parser/governance version.

Raw `ovr_btn` and `btn` remain permanently recoverable through immutable source lineage.

### Validated Source Version 1 population

Across 1,851,285 runner rows:

* 93,992 `ovr_btn` text-sentinel rows;
* 93,992 `btn` text-sentinel rows;
* 0 unexpected populated text values in either field;
* 500 rows where official position 1 has positive `ovr_btn`;
* 371 rows where a later official position has zero `ovr_btn`;
* 2,750 rows where positive `ovr_btn` is accompanied by zero `btn`.

These populations are governed structural states rather than automatic data errors.

### Physical finish versus official result

A positive `ovr_btn` on official position 1 m
…
```

### Cell 28

Matched: `external`

```text
## Notebook 16 — Race classification and eligibility

### Database v2 disposition

**Classification: integrate into Database v2, with `going` deferred for final contextual reconciliation.**

Notebook 16 establishes bounded structural interpretation for seven race-level source fields:

- `race_name`;
- `type`;
- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`.

All seven fields are constant within each of the 189,043 governed source race occurrences.

Their raw source values remain authoritative evidence. Derived values are additive structural interpretations rather than universal international classification or eligibility truth.

### Race-level Database v2 representation

At `core_source_race_occurrence` grain, Database v2 should make the exact governed race-level source values directly available together with the following derived fields.

#### Class

- `class_number`;
- `class_parse_status`.

Only canonical `Class N` syntax is structurally parsed.

A class number must not be treated as internationally equivalent across jurisdictions.

#### Pattern

- `pattern_family`;
- `pattern_level_raw`;
- `pattern_parse_status`.

`Listed`, `Group` and `Grade` remain distinct families.

Group and Grade must not be collapsed into one universal hierarchy.

#### Rating band

- `rating_lower_bound`;
- `rating_upper_bound`;
- `rating_band_parse_status`.

Only exact closed integer `N-N` ranges are canonical.

The currently observed forms:

- `--`;
- `(75-100)`;

remain explicitly unresolved source forms.

#### Age band

- `stated_minimum_age`;
- `stated_maximum_age`;
- `age_band_open_ended`;
- `age_band_syntax`;
- `age_band_interpretation_status`.

These represent the bounds stated by the source syntax.

They are not universal eligibility constraints and must not autom
…
```

### Cell 30

Matched: `verified`

```text
## Notebook 17 — Runner characteristics and equipment

### Database v2 disposition

**Classification: integrate into Database v2, including exact-lineage governed sex corrections.**

Notebook 17 establishes reusable governed interpretations for runner-level source fields:

* `age`;
* `sex`;
* `hg`.

The immutable raw source values remain permanently recoverable.

### Runner age

At `core_runner_participation` grain, Database v2 should materialise:

* `age_recorded`;
* `age_interpretation_status`;
* applicable governance/version provenance.

Current Source Version 1 contains:

* 1,851,285 runner rows with integer source ages;
* 19 distinct age values;
* minimum source age 1;
* maximum source age 31.

`age_recorded` means exactly that: the age recorded by the source.

It must not automatically be interpreted as:

* independently verified age;
* proof of race eligibility;
* a value safe to clip to an expected range.

Race-level `age_band` from Notebook 16 must not automatically overwrite or constrain runner age.

The separately evidenced Ecstasy (USA) `31 → 3` case remains governed by its Notebook 16 correction decision rather than by Notebook 17's generic age normalisation.

### Runner sex

Database v2 should materialise:

* `sex_normalised`;
* `sex_interpretation_status`;
* `sex_verification_id`;
* applicable governance/version provenance.

The common source codes have governed interpretations:

* `C` → `colt`;
* `F` → `filly`;
* `G` → `gelding`;
* `H` → `horse`;
* `M` → `mare`;
* `R` → `rig`.

These are governed reference mappings.

### Exact governed sex corrections

Source Version 1 also contains exactly one `B` and one `BB`.

These are not globally valid additional sex codes.

The durable Notebook 17 implementation accepts two exact-lineage corrections:

1. **Par Coe
…
```

### Cell 32

Matched: `racing post`

```text
## Notebook 18 — Ratings semantics and availability

### Database v2 disposition

**Classification: integrate into Database v2.**

Notebook 18 establishes separate governed runner-level representations for:

- `or`;
- `rpr`;
- `ts`.

These three ratings have different meanings, producers and timing and must remain independently represented throughout Database v2.

### Governed meanings

`or` represents:

`official_pre_race_handicap_mark`

applicable to the runner for the race.

`rpr` represents:

`retrospective_racing_post_performance_rating`

and may subsequently be revised by its publisher.

`ts` represents:

`retrospective_racing_post_speed_figure`

for the completed performance.

Database v2 must not collapse these fields into a single generic rating.

### Runner-level representation

At `core_runner_participation` grain, Database v2 should materialise:

- analytical `or`;
- `or_status`;
- analytical `rpr`;
- `rpr_status`;
- analytical `ts`;
- `ts_status`;
- applicable semantic/parser/governance version.

The immutable raw values remain directly recoverable through source lineage.

Permitted interpretation states are:

- `available`;
- `unavailable`;
- `invalid_source_value`;
- `unresolved_source_value`.

The exact Unicode en dash `–` represents unavailable data and must produce a null analytical rating rather than zero.

Unexpected future source forms must remain unresolved rather than being permissively coerced.

### Validated Source Version 1 availability

Across 1,851,285 runner rows:

#### Official rating (`or`)

- 1,116,633 available;
- 734,652 unavailable;
- 0 invalid;
- current observed analytical range 1–181.

#### Racing Post Rating (`rpr`)

- 1,644,175 available;
- 207,109 unavailable;
- 1 invalid;
- current observed analytical range after exclusion of th
…
```

### Cell 36

Matched: `manual`, `external`, `verified`

```text
## Notebook 20 — Connections and ownership identity

### What the notebook established

Notebook 20 investigated the runner-level source fields:

- `jockey`;
- `trainer`;
- `owner`.

Its principal reusable result is **not participant identity resolution**.

The raw fields are source-presented connection labels. Exact text may support bounded source-label analysis, but it must not automatically be treated as a canonical person, licence, partnership, syndicate or organisation identifier.

Notebook 22 subsequently owns the separate participant-identity problem.

Notebook 20 instead established a governed supplementation layer for otherwise blank connection fields.

### Governed blank-field population

Across the 1,851,285 admitted runner rows, the immutable source contains:

- 2 blank `jockey` occurrences;
- 9 blank `trainer` occurrences;
- 35 blank `owner` occurrences;
- **46 blank field occurrences** across **44 source rows**.

Every one of those 46 exact `(source_rowid, source_field)` occurrences has a permanent governed decision.

The decision partition is:

- **28 verified repairs**;
- **5 conflicting-evidence cases**;
- **13 insufficient-evidence cases**.

The 28 usable supplementations comprise:

- 2 jockey values;
- 4 trainer values;
- 22 owner values.

The remaining **18 blanks remain deliberately unresolved**:

- 5 trainer;
- 13 owner.

Confirmed decisions authorise only `source_supplementation`.

Conflicting or insufficient decisions authorise only `preserve_raw_unresolved`.

### Durable governed evidence

The permanent decision population is stored in:

`data/reference/manual_verifications.csv`

with permanent identifiers:

`NB20-CONNECTION-0001` through `NB20-CONNECTION-0046`.

The 28 usable supplementations are separately exposed in:

`data/reference/connecti
…
```

### Cell 40

Matched: `external`, `verified`

```text
## Notebook 22 — Jockey, trainer and owner participant identity

### What the notebook established

Notebook 22 investigated whether source-presented `jockey`, `trainer` and `owner` labels could safely be converted into reusable participant identities.

The central conclusion is that **broad string normalisation is unsafe**.

Raw labels may vary because of titles, formatting, ordering and source presentation, while superficially similar labels may also refer to different real-world participants.

Notebook 22 therefore creates only bounded **provisional source-label identities** where the evidence supports them.

These identities do not claim universal legal, licensing or provider-independent identity.

### Jockey identity

The source contains:

- **7,917 populated jockey labels**;
- **216 strict title-removal candidate relationships**.

The governed decision population is:

- **1 accepted same-person relationship**;
- **1 externally confirmed distinct-person relationship**;
- **214 unresolved relationships**.

The accepted relationship is:

- `Mlle Marie Velon`;
- `Mme Marie Velon`.

Both labels map to:

`JOCKEY-PROVISIONAL-0001`

The relationship was externally verified and is represented by two directly usable governed label mappings.

The confirmed distinct relationship is:

- `Miss B ONeill`;
- `Mr B ONeill`.

Those labels occur within the same reconstructed race and external evidence confirms that they represent different people. They must remain separate identities.

No general title-stripping rule is authorised.

### Trainer identity

Notebook 22 accepts only a tightly bounded source-presentation transition:

- earlier label title `Mlle`;
- later label title `Mme`;
- no overlapping active periods;
- earlier `Mlle` label ending between 1 July and 31 December 2023;
…
```

### Cell 41

Matched: `manual`, `manually`, `verified`

```text
## Database v2 physical-design reconciliation — governing rule

The Notebook 04–22 inventory is now complete.

Database v2 is not a redesign of the accepted structural core.

It is a new immutable database release that retains the Database v1 structural model and adds the governed analytical and identity structures that the completed notebook programme now authorises.

### Stable core carried forward

The following concepts retain their existing meaning, grain and key boundaries:

- immutable physical source record;
- Source Version 1 race occurrence;
- runner participation;
- source/provider/version/relation provenance;
- structural governance release;
- import/build/validation evidence.

In particular:

- one admitted source row continues to support exactly one runner participation;
- each runner participation belongs to exactly one Source Version 1 race occurrence;
- `date + course + off` remains only the Source Version 1 race-grouping rule;
- raw horse, jockey, trainer and owner labels remain source assertions rather than permanent identities;
- supplied `race_id`, runner number and other descriptive source fields do not become project-wide natural keys.

Database v2 must not change those meanings merely because richer governed information is now available.

### Additive extension rule

Notebook 04–22 outputs should be integrated through **additive governed structures attached to the stable core**, rather than by rewriting the structural core tables.

The normal attachment grains are:

1. **race occurrence**
   - governed race-level interpretations and context;

2. **runner participation**
   - governed runner-level interpretations, corrections and supplementations;

3. **source record**
   - exact correction or verification decisions where physical source-row linea
…
```

### Cell 42

Matched: `external`, `verified`

```text
## Database v2 physical-structure matrix — Notebooks 04–22

The completed Notebook 04–22 inventory can now be reconciled by **physical attachment grain**.

This matrix is deliberately conceptual.

It identifies where each governed output belongs in Database v2 before table names, columns, indexes or DDL are fixed.

| Notebook | Governed subject | Primary v2 grain | Integration treatment | Physical structure family |
|---|---|---|---|---|
| 04 | Course jurisdiction / surface observations | race occurrence + evidence | Partial integration | race context / governed observation |
| 05 | Result position and non-finish semantics | runner participation | Integrate | governed runner result |
| 06 | Distance parsing and interpretation | race occurrence | Integrate | governed race distance |
| 07 | Carried weight | runner participation | Integrate | governed runner weight |
| 08 | Starting price arithmetic and bounded corrections | runner participation + correction evidence | Integrate | governed runner starting price + correction provenance |
| 09 | Jurisdiction / race context | race occurrence + versioned reference | Integrate | governed race jurisdiction/context |
| 10 | Source-field governance | governance release | Integrate as metadata/control | versioned field-governance reference |
| 11 | Race time | race occurrence | Integrate | governed temporal representation |
| 12 | Course location and timezone | reference entity + race occurrence | Integrate | course reference + race-to-course link |
| 13 | Prize-money semantics | runner participation | Integrate | governed runner prize |
| 14 | Runner counts, numbers and entries | race occurrence + runner participation + evidence | Integrate | governed field-size / entry semantics + supplementation evidence |
| 15 | Beaten distance
…
```

### Cell 44

Matched: `manual`, `manually`, `external`, `verified`

```text
## Proposed Database v2 table inventory

Inspection of the accepted Database v1 confirms that its physical schema already provides the stable attachment points required for Database v2:

- `source_raceform_v1_record`;
- `core_source_race_occurrence`;
- `core_runner_participation`;
- the existing source, governance and import-control structures.

Review of the durable Notebook 04–22 integration contracts also confirms that several governed concepts require their own relational grains rather than being flattened into the two general race/runner extension tables.

Database v2 therefore does **not** redesign the accepted structural core.

The physical strategy is:

> Carry the accepted Database v1 structures forward unchanged in meaning, then add only the governed extensions, reusable references, evidence structures, supplementations and provisional identity structures established by Notebooks 04–22.

### Naming extensions

Database v1 currently uses:

- `source_*`;
- `core_*`;
- `governance_*`;
- `import_*`;
- `view_*`.

Database v2 introduces two additional prefixes for concepts now supported by governed evidence:

- `reference_*` — reusable governed reference entities;
- `identity_*` — explicitly provisional or source-internal identity structures.

These prefixes apply only to evidenced Database v2 concepts. They do not authorise speculative future reference or identity models.

---

## A. Existing Database v1 tables carried forward

| Table | Grain | Database v2 treatment |
|---|---|---|
| `source_provider` | one governed source provider | carry forward |
| `source_product` | one governed source product | carry forward |
| `source_version` | one immutable source delivery | carry forward |
| `source_relation` | one relation within one source version | carry forward |
| `
…
```

### Cell 45

Matched: `manual`

```text
from pathlib import Path
import subprocess

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

# These are the notebooks whose governed outputs feed the proposed
# one-row-per-race extension. We inspect their tracked references together so
# the column design is based on the durable contracts, not remembered names.
RACE_LEVEL_NOTEBOOKS = ("04", "06", "09", "11", "12", "14", "16")

for notebook_number in RACE_LEVEL_NOTEBOOKS:
    print(f"\nNotebook {notebook_number}")
    print("-" * 40)

    # Search only tracked implementation/governance areas. This deliberately
    # excludes notebook prose itself because the durable integration contracts,
    # modules and validators are the authority for Database v2 design.
    result = subprocess.run(
        [
            "git",
            "-C",
            str(PROJECT_ROOT),
            "grep",
            "-l",
            "-E",
            rf"Notebook {notebook_number}",
            "--",
            "docs",
            "src",
            "scripts",
            "tests",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # git grep returns 1 when there are simply no matches; any other non-zero
    # result means the discovery command itself failed and should stop the stage.
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)

    references = sorted(
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    )

    # Show the complete tracked reference set so we can identify the precise
    # integration contract, reusable implementation and validator for each
    # race-level subject before proposing physical columns.
    if references:
        for path in references:
            print(f"
…
```

### Cell 46

Matched: `external`, `verified`

```text
## `core_source_race_occurrence_governed` — proposed exact field design

The durable Notebook 04, 06, 09, 12, 14 and 16 integration contracts now provide enough evidence to define the general race-level governed extension.

Notebook 11 race time remains outside this table in the separately proposed `core_source_race_occurrence_time` structure.

The governing principle is:

> one governed extension row for every existing `core_source_race_occurrence`, containing race-level interpretations that are reproducible from the governed source and accepted reference/evidence inputs.

The table does not create a new race identity.

Its one-to-one parent remains:

`core_source_race_occurrence`

---

### 1. Structural linkage and governance

| Column | Proposed type | Null? | Meaning |
|---|---|---:|---|
| `source_race_occurrence_id` | INTEGER | no | Primary key and foreign key to `core_source_race_occurrence` |
| `governance_release_id` | INTEGER | no | Governance release under which this integrated race representation was built |

`source_race_occurrence_id` should serve as both:

- the primary key of this extension table; and
- the foreign key to the existing structural race occurrence.

No additional race surrogate identifier is required.

This enforces the intended cardinality:

> one structural race occurrence → exactly one general governed race row.

---

## 2. Course and jurisdiction derivation

Notebook 04 established reusable source-to-candidate course/jurisdiction derivation.

Notebook 09 became the semantic authority for bounded jurisdiction context.

Notebook 12 established the permanent governed course reference.

The following columns should therefore be stored:

| Column | Proposed type | Null? | Meaning |
|---|---|---:|---|
| `candidate_course_label` | TEXT | no | G
…
```

### Cell 48

Matched: `manual`

```text
from pathlib import Path
import subprocess

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

# These notebooks contribute governed runner-level values to the proposed
# one-row-per-source-backed-runner extension. Notebook 20 is included because
# its exact connection-field supplementation feeds the governed runner values,
# while its evidence remains in a separate governance table.
RUNNER_LEVEL_NOTEBOOKS = (
    "05",
    "07",
    "08",
    "13",
    "14",
    "15",
    "17",
    "18",
    "20",
    "21",
)

for notebook_number in RUNNER_LEVEL_NOTEBOOKS:
    print(f"\nNotebook {notebook_number}")
    print("-" * 40)

    # Search only tracked durable implementation/governance areas. The goal is
    # to identify the integration contract, reusable implementation and
    # validator that should govern Database v2 rather than relying on notebook
    # memory or historical intermediate outputs.
    result = subprocess.run(
        [
            "git",
            "-C",
            str(PROJECT_ROOT),
            "grep",
            "-l",
            "-E",
            rf"Notebook {notebook_number}",
            "--",
            "docs",
            "src",
            "scripts",
            "tests",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # git grep returns 1 when there are simply no matches. Any other non-zero
    # result means discovery itself failed, so stop rather than silently
    # designing the runner schema from an incomplete reference set.
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)

    references = sorted(
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    )

    # Display the full tracked referenc
…
```

### Cell 49

Matched: `external`, `verified`

```text
## `core_runner_participation_governed` — proposed exact field design

The durable Notebook 05, 07, 08, 13, 14, 15, 17, 18, 20 and 21 integration contracts now provide enough evidence to define the general source-backed runner extension.

The governing grain is:

> exactly one governed row for every existing `core_runner_participation`.

The current Source Version 1 population is therefore:

- **1,851,285 source-backed runner participations**.

Externally verified runners absent from the immutable source do **not** belong in this table. They remain in the separately proposed:

`governance_runner_record_supplementation`

The governing principle is:

> preserve immutable source assertions, derive only governed interpretations, make accepted corrections or supplementations analytically usable where authorised, and retain explicit lineage whenever the governed analytical value differs from the source.

---

## 1. Structural linkage and governance

| Column | Proposed type | Null? | Meaning |
|---|---|---:|---|
| `runner_participation_id` | INTEGER | no | Primary key and foreign key to `core_runner_participation` |
| `governance_release_id` | INTEGER | no | Governance release under which the integrated runner representation was built |

`runner_participation_id` serves as both:

- the primary key of this extension table; and
- the foreign key to the existing structural runner participation.

No second source-backed runner identifier is required.

The intended cardinality is:

> one `core_runner_participation` → exactly one `core_runner_participation_governed`.

---

## 2. Result position and outcome

Notebook 05 established that source `pos` contains several structurally different states and must not be collapsed into a nullable finishing-position integer.

Proposed columns:
…
```

### Cell 50

Matched: `manual`, `external`, `verified`, `validation_status`

```text
## Reference and governance tables — proposed exact field design

The next Database v2 structures cover governed reference data, field-treatment metadata, permanent external verification and the two supplementation mechanisms already authorised by the Notebook 04–22 programme.

These tables have different grains from race and runner facts and therefore should not be flattened into `core_source_race_occurrence_governed` or `core_runner_participation_governed`.

The six structures covered here are:

1. `reference_course`;
2. `reference_jurisdiction_context`;
3. `governance_source_field_treatment`;
4. `governance_manual_verification`;
5. `governance_connection_value_decision`;
6. `governance_runner_record_supplementation`.

No DDL is authorised yet.

---

# 1. `reference_course`

Notebook 12 established a permanent governed course-location and timezone reference.

The current governed population is:

- **395 unique course identities**;
- **395 assigned IANA timezones**;
- **51 distinct IANA timezone names**;
- **zero unresolved timezone assignments**.

The governed course identity is:

> `candidate_course_label + candidate_jurisdiction`

This is not the same thing as raw source `course` text.

### Proposed fields

| Column | Proposed type | Null? | Meaning |
|---|---|---:|---|
| `reference_course_id` | INTEGER | no | Internal primary key |
| `candidate_course_label` | TEXT | no | Governed candidate course label |
| `candidate_jurisdiction` | TEXT | no | Governed candidate jurisdiction |
| `physical_venue_name` | TEXT | yes | Verified physical venue name where established |
| `locality` | TEXT | yes | Locality where established |
| `region` | TEXT | yes | Region/state/province where established |
| `country` | TEXT | yes | Governed country text |
| `latitude` | REAL | yes |
…
```

### Cell 51

Matched: `manual`, `external`

```text
## Notebook 19 horse and pedigree identity — proposed exact field design

Notebook 19 requires three Database v2 structures because it established three distinct relational grains:

1. a governed provisional horse occurrence;
2. the assignment of applicable source-backed runner rows to those occurrences;
3. the governed pedigree/identity decisions that determine whether adjacent histories remain one horse or split into different horses.

The three physical tables are:

- `identity_horse_occurrence`;
- `identity_runner_horse_occurrence`;
- `identity_horse_pedigree_decision`.

The governing principle remains:

> raw `horse`, `sire`, `dam` and `damsire` are immutable source assertions; provisional identity and governed pedigree decisions are additive analytical structures.

A provisional horse occurrence is source-internal only.

It is **not**:

- an official registration number;
- a life number;
- a provider-independent horse identity;
- evidence that the same label is unique outside Source Version 1.

---

# 1. Current governed Notebook 19 baseline

The current durable implementation and regenerated processed outputs establish:

- **5,573 raw contradiction labels**;
- **368 structured contradiction labels**;
- **96,404 structured pedigree rows**;
- **741 structured pedigree groups**;
- **350 temporally separated exact horse labels**;
- **703 separated pedigree groups**;
- **353 governed transitions**;
- **92 `Corrected` transitions**;
- **261 `Different horse` transitions**;
- **0 `Unresolved` transitions**;
- **611 provisional horse occurrences**.

The 8 August 2026 Weatherbys confirmation for `Runninsonofagun (IRE)` changed the final transition partition from:

- 91 `Corrected`;
- 261 `Different horse`;
- 1 `Unresolved`;

to:

- 92 `Corrected`;
- 261 `Different horse`;
…
```

### Cell 52

Matched: `manual`, `external`

```text
## Notebook 22 participant identity — proposed exact field design

Notebook 22 established that broad normalisation of jockey, trainer and owner labels is unsafe.

Database v2 therefore requires five participant-identity structures:

1. `identity_participant_source_label`;
2. `identity_participant`;
3. `identity_participant_label_map`;
4. `identity_participant_candidate`;
5. `identity_participant_candidate_label`.

The governing principle is:

> preserve source-presented labels exactly, create provisional identities only from accepted governed relationships, and preserve unresolved or confirmed-distinct candidates without allowing them to become analytical identities.

Notebook 20 remains responsible for blank connection-field supplementation.

Notebook 22 does not overwrite or reinterpret those immutable blank source values.

---

# 1. Current governed Notebook 22 baseline

### Jockey

Current source-wide population:

- **7,917 populated raw labels**;
- **212 strict comparison groups**;
- **216 candidate relationships**;
- **1 accepted same-person relationship**;
- **1 confirmed distinct-person relationship**;
- **214 unresolved relationships**.

The single accepted relationship is:

- `Mlle Marie Velon`;
- `Mme Marie Velon`;

mapped to:

`JOCKEY-PROVISIONAL-0001`

under verification:

`NB22-JOCKEY-0002`.

The confirmed distinct relationship is:

- `Miss B ONeill`;
- `Mr B ONeill`;

under verification:

`NB22-JOCKEY-0001`.

Those labels must remain separate.

### Trainer

Current governed population:

- **10,708 populated raw labels**;
- **26 accepted provisional trainer identities**;
- **52 accepted mapped raw labels**;
- **6,350 mapped runner rows**;
- **27 unresolved candidate groups**.

Accepted trainer identity is limited to the bounded:

`Mlle` → `Mme`

source-pr
…
```

### Cell 53

Matched: `manual`, `external`

```text
## Database v2 cross-table reconciliation — keys, cardinalities and duplication boundaries

The proposed Database v2 structures have now been reviewed together rather than notebook by notebook.

This reconciliation checks:

- physical grain;
- parent key;
- foreign-key direction;
- one-to-one and one-to-many cardinalities;
- source-value duplication;
- governance-release lineage;
- correction and supplementation provenance;
- unresolved-state preservation;
- whether any governed artifact has been forced into a table with the wrong grain.

This stage intentionally occurs **before DDL**.

The governing rule is:

> A physical table should exist because it has a distinct governed relational grain, not because a notebook happened to produce an output.

---

# 1. Reconciliation result

The previous proposed inventory contained:

- 13 carried-forward Database v1 tables;
- 17 proposed Database v2 tables;
- 30 physical tables total.

Cross-table reconciliation identifies **one missing governed grain**:

`data/reference/horse_pedigree_identity_governance.csv`

contains **16 specialist Notebook 19 decisions**.

Those decisions are not the same grain as the:

- 353 derived horse-pedigree transition decisions.

The earlier design attempted to place specialist decision/evidence fields directly inside `identity_horse_pedigree_decision`.

That would mix:

- one row per source-derived pedigree transition;
- one row per bounded externally/specialist-governed horse decision.

It could also repeat the same specialist evidence across multiple transition rows.

That is not the correct relational model.

Database v2 therefore requires one additional table:

`governance_horse_pedigree_specialist_decision`

The reconciled Database v2 inventory is now:

- **13 carried-forward Database v1 tables*
…
```
