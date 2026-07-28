# Carried-Weight Database Integration

## Scope

This document closes Notebook 07 by defining how `src/inside_rails/carried_weight.py` is used in a later staging build.

The source database remains immutable. The exact raw `wgt` value must be retained alongside every derived field.

## Governed interpretation

Current source values are stored as canonical stones-and-pounds text:

`<stones>-<pounds>`

The pounds component must be between 0 and 13. The parser deliberately rejects whitespace, leading zeros, alternative separators, unit suffixes, metric notation and non-text storage.

A parsed value yields:

- `parsed_stones`;
- `parsed_pounds`;
- `source_implied_total_pounds`;
- `source_implied_kilograms`;
- `notation_family`;
- `parse_status`;
- `ambiguity_flag`;
- `anomaly_flags`;
- `official_weight_verified`.

The kilogram value is only the exact SI conversion of the stored stones-and-pounds expression. It is not evidence that the original racing authority published or verified that metric value.

## Suggested staging fields

A runner staging table should retain:

```text
raw_wgt                         TEXT NOT NULL
weight_notation_family          TEXT NOT NULL
carried_weight_stones           INTEGER
carried_weight_remainder_pounds INTEGER
carried_weight_total_pounds     INTEGER
carried_weight_implied_kg       REAL
weight_parse_status              TEXT NOT NULL
weight_ambiguity_flag            INTEGER NOT NULL
weight_anomaly_flags              TEXT NOT NULL
official_weight_verified          INTEGER NOT NULL
```

`weight_anomaly_flags` may be stored as JSON text or normalised into a child table. Raw `wgt` must never be overwritten by derived values.

## Build rule

For each runner row:

1. preserve `wgt` exactly as `raw_wgt`;
2. call `parse_carried_weight(raw_wgt)`;
3. store every returned derived field;
4. do not coerce unresolved values;
5. retain source database, table and original `rowid` lineage.

## Validation expectations for the current snapshot

The independent validator confirms:

- 1,851,285 runner records;
- 79 distinct raw values;
- all values stored as SQLite text;
- all current values parsed as canonical stones and pounds;
- observed source-implied total weights from 96 to 179 lb;
- no current unresolved records;
- no official source weight independently verified.

## Replacement or extended snapshots

Every replacement snapshot must be validated before rebuilding staging data.

A new raw value is not automatically trusted merely because the parser can interpret its grammar. Review should establish:

- whether the notation still means stones and pounds;
- whether a provider has begun storing kilograms or decimal values;
- whether jurisdiction-specific source semantics changed;
- whether storage types changed;
- whether the pounds remainder remains bounded by 13.

New canonical stones-and-pounds values can be parsed without changing code, but their appearance should still be recorded in snapshot validation. New notation families require a separately reviewed parser change, tests and migration note.

## Migration policy

Parser changes must not silently rewrite historical staging records. Record a transformation version or build version so previously derived values can be reproduced. Rebuild derived fields from retained raw values and lineage when the governed interpretation changes.

## Tests and independent validation

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_carried_weight.py
PYTHONPATH=src .venv/bin/python scripts/validate_carried_weight.py
```

Unit tests cover canonical values, limits, malformed text, missing and non-text values, and the distinction between literal metric conversion and official verification. The validator reconciles the implementation against the immutable full source database.
