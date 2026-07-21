# Report 01 — Source Database Structure Profile

## Executive conclusion

The supplied `raceform.db` is structurally readable and internally consistent as a SQLite file, but it is not ready to serve directly as a professional analytical schema.

It contains one denormalised table named `data`, with race-level attributes repeated across runner rows. The evidence strongly supports a grain of one horse participating in one race.

The source should therefore be ingested through a controlled staging process rather than copied directly into a final relational model.

## Source examined

`data/raw/form_2015-present/form_2015-present/raceform.db`

The file:

- is a valid SQLite 3 database;
- is approximately 730 MiB;
- opens successfully in read-only mode;
- returns `ok` from `PRAGMA quick_check`.

No raw values were changed during profiling.

## Structural evidence

The database contains one user-defined schema object:

- table: `data`;

The table contains:

- 37 declared columns;
- 1,851,286 physical rows;
- one imported CSV header row at `rowid = 1`;
- 1,851,285 data-like rows;
- no declared primary key;
- no foreign keys;
- no indexes;
- no uniqueness constraints;
- no `NOT NULL` constraints;
- no default values.

It is a normal SQLite rowid table rather than a strict or `WITHOUT ROWID` table.

## Likely grain

The evidence strongly indicates the source grain is:

> one row per horse participating in one race.

A provisional composite of:

- `date`;
- `course`;
- `off`;
- `race_name`;
- `horse`;

produces 1,851,285 distinct values across 1,851,285 data-like rows.

This is strong profiling evidence, but not a final key decision. It depends on descriptive text fields that may change across source editions.

## Apparent race structure

Using `date`, `course`, `off` and `race_name` as a provisional race description produces:

- 189,043 apparent races;
- a mean of approximately 9.79 runner rows per apparent race.

For all apparent races, the following fields are constant within the race:

- `type`;
- `class`;
- `dist`;
- `going`;
- `ran`.

The following usually vary within the race:

- `horse`;
- `jockey`;
- `trainer`;
- `pos`;
- `sp`.

This confirms that race-level and runner-level attributes are stored together in a denormalised table.

## Identifier findings

### `race_id`

`race_id` repeats across runner rows within a race, as expected, but it is also reused across genuinely different races on different dates and at different courses.

It therefore fails as a globally reliable standalone race key.

### `num`

Runner number is usually unique within a race, but not universally:

- zero is sometimes used across an entire field;
- positive numbers can be shared by multiple horses;
- shared positive values are concentrated in international racing and appear consistent with coupled or bracketed betting entries.

`num` is therefore a source racing or betting attribute, not a universal runner identifier.

### Named entities

Horse, trainer, jockey and owner are stored as text labels rather than declared entity identifiers.

Repeated values behave plausibly as recurring real-world entities, but names alone cannot safely resolve identity because of spelling variants, punctuation, abbreviations, collisions and jurisdiction-specific formatting.

## Date and geographical scope

The data-like rows cover:

- minimum date: `2015-01-01`;
- maximum date: `2026-05-27`.

The database therefore extends beyond the 2015–2025 range in the Kaggle title.

It also contains substantial international coverage, including racing from France, Hong Kong, the United States, Australia, Japan, the UAE and many other jurisdictions.

The source is not restricted to UK and Irish racing.

## Type and missing-value findings

SQLite storage classes do not consistently follow the declared column types.

Examples include:

- numeric-looking fields containing text placeholders;
- `pos` containing numeric placings and non-finish codes;
- `prize` containing blanks, integers, decimals and currency-formatted text;
- `or`, `rpr` and `ts` containing integers and dash placeholders;
- `num` and `draw` containing blank text;
- no SQLite `NULL` storage values despite extensive apparent missingness.

Missingness and special outcomes are represented through field-specific conventions such as:

- blank strings;
- hyphens or dashes;
- zeroes;
- racing outcome codes.

These meanings must be profiled field by field. A generic missing-value replacement would be unsafe.

## Data completeness signal

For 189,038 of 189,043 apparent races, the stored runner-row count matches the repeated `ran` field.

Five apparent international races contain fewer stored rows than the declared field size.

This is strong support for the inferred grain while also identifying a small number of apparently incomplete race records.

## Decisions made

- Treat the table as a runner-grain denormalised source.
- Preserve the raw database unchanged.
- Exclude the imported header row only through explicit, documented staging logic.
- Do not accept `race_id`, `num`, rowid or name strings automatically as durable business keys.
- Do not infer missing values from SQLite `NULL` checks alone.
- Preserve original course labels and other source text until parsing rules are proven.
- Keep provisional composite keys as profiling aids, not final schema decisions.

## Confidence

**High confidence** in:

- the one-runner-per-race-row grain;
- the denormalised source structure;
- the physical row and apparent-race counts;
- the failure of `race_id` as a global standalone key;
- the broader-than-advertised geographical and date scope.

**Medium confidence** in:

- the interpretation of shared positive runner numbers as coupled or bracketed entries;
- the exact causes of the five incomplete apparent races.

These interpretations require targeted domain investigation before transformation rules are adopted.

## Practical implication

The next stage should profile individual fields and domain conventions before designing the target relational schema.

Priority areas are:

- race identity;
- course, jurisdiction and surface;
- runner numbering;
- finishing positions and non-finish codes;
- official ratings, Racing Post Ratings and Topspeed;
- prize money and currency;
- starting prices;
- distance;
- carried weight;
- race time.

## Reusable code extracted

Notebook-independent technical logic now lives in:

- `src/inside_rails/source_sqlite.py`;
- `scripts/validate_source_profile.py`.

The module provides read-only source access, identifier quoting, schema inventory, declared-column inspection and reproduction of the core structural profile.

Racing interpretations and unresolved transformation choices remain visible in the notebook and report rather than being hidden inside utility code.
