# Source Field Governance and Database Integration

## Purpose

Notebook 02 established that the 37 source columns do not share one universal missing-value or typing convention. Blank text, dashes, zeroes and mixed SQLite storage classes must be interpreted field by field. The raw source value must therefore survive every later transformation.

The durable implementation is:

- `data/reference/source_field_governance.csv` — one governed row for every source column;
- `src/inside_rails/source_fields.py` — loader, structural validation and source-schema comparison;
- `tests/test_source_fields.py` — governed-rule and failure-case tests;
- `scripts/validate_source_fields.py` — independent reconciliation against `raceform.db`.

## What the reference governs

The reference fixes:

- the exact 37-column source schema and column order;
- the declared SQLite type observed in the source;
- the provisional race-level or runner-level grain of each field;
- the field family used to route later investigations;
- mandatory preservation of the raw value;
- whether blank, dash and zero values may be treated as missing, valid or context-dependent;
- the notebook responsible for later semantic interpretation;
- whether that interpretation is pending or implemented elsewhere.

It does **not** claim that Notebook 02 solved the final semantics of every field. Values marked contextual or unresolved must remain unresolved until their owning notebook supplies a tested rule.

## Raw and staging schema consequence

A staging build must retain physical source lineage and the untouched source value. A practical pattern is:

```text
source_database_id
source_table_name
source_rowid
source_field_name
raw_value
raw_storage_class
normalised_value
normalisation_status
normalisation_rule_version
```

A wider staging table may retain the 37 raw columns directly, but interpreted columns must be additional columns rather than replacements. For example, `raw_pos` must survive alongside any later `finish_position` and `outcome_code` fields.

## Missing-value rule

No global operation such as replacing all blanks, dashes or zeroes with SQL `NULL` is permitted.

The sequence is:

1. preserve the raw value and SQLite storage class;
2. look up the field's governed policy;
3. apply only the parser owned by the responsible notebook;
4. store interpreted value and status separately;
5. leave unresolved values explicit rather than coercing them.

A dash in `or`, `rpr` or `ts` can express rating unavailability. A textual code in `pos` can express a genuine race outcome. Zero can be a valid measure, a sentinel or an anomaly depending on the field. These cases must never be collapsed by a source-wide cleaning rule.

## Validation

Unit tests:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_source_fields.py
```

Independent source reconciliation:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_source_fields.py \
  data/raw/raceform.db
```

Supply the actual immutable source path where it differs.

The validator fails if:

- the reference does not contain exactly the governed 37 fields in source order;
- required policy fields are absent;
- a source field is duplicated;
- raw preservation is not mandatory;
- the live SQLite column names, order or declared types drift from the reference.

## Update path

When a new source database is received:

1. retain the previous database unchanged;
2. run `validate_source_profile.py` and `validate_source_fields.py` against the new file;
3. treat schema drift as a new source-version event, not an automatic reference edit;
4. inspect added, removed, renamed or retyped columns;
5. update the governed reference only through a reviewed change with tests;
6. assign every new field to a semantic owner before ingestion;
7. version any changed transformation rules independently from the raw source version.

Observed value-frequency changes do not by themselves alter the governance reference. A policy changes only when evidence supports a different semantic rule.

## Closure decision

Notebook 02 is implementation-closed when:

- this reference loads successfully;
- its unit tests pass;
- the independent validator matches the immutable source schema;
- later notebooks use the reference rather than recreating a private field inventory.
