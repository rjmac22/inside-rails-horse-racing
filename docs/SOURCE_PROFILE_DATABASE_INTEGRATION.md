# Source Profile Database Integration

## Scope

This document closes the implementation path from Notebook 01, `01_source_database_structure_profile.ipynb`, into later ingestion and database-building work.

Notebook 01 governs how the immutable third-party SQLite source is opened, identified and structurally reconciled. It does not clean source values or define the final analytical schema.

## Durable implementation

The reusable implementation is:

- `src/inside_rails/source_sqlite.py`
- `tests/test_source_sqlite.py`
- `scripts/validate_source_profile.py`

The module owns stable technical rules only:

1. open the supplied SQLite file in read-only URI mode;
2. exclude the imported header at physical `rowid = 1` from data counts;
3. quote SQLite identifiers safely;
4. inspect declared schema objects and columns;
5. calculate the structural reconciliation established by Notebook 01;
6. report candidate race and runner-key uniqueness without promoting either key into a permanent database identifier.

## Database-layer consequence

### Raw source layer

The supplied SQLite database remains external and immutable. No migration should modify it in place.

Every ingested row must retain enough physical lineage to return to the original record. At minimum, staging ingestion should retain:

- source database identity or version;
- source table name;
- source `rowid`;
- ingestion run identifier;
- ingestion timestamp;
- all 37 raw source values without destructive replacement.

The imported header row must be excluded deliberately rather than removed from the source file.

### Staging layer

Staging should assign an independent surrogate runner-record identifier. Candidate descriptive keys remain validation attributes, not primary keys.

Notebook 01 used `date + course + off + race_name` for an early apparent-race count and added `horse` for an early runner-grain uniqueness check. Later Notebook 03 refined provisional race reconstruction to `date + course + off`. Code consuming this module must therefore treat the Notebook 01 constants as structural-profile definitions, not as the final race-identity contract.

### Core layer

Core race and runner tables must use independent surrogate identifiers. Source `race_id`, runner number and descriptive text values must be retained as source attributes and lineage, not trusted as universal keys.

## Validation path

### Unit tests

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_source_sqlite.py
```

The tests cover:

- identifier quoting;
- null-safe composite expressions;
- missing-file rejection;
- enforcement of read-only access;
- schema and column inspection;
- header-row exclusion;
- candidate race counting;
- candidate runner-key uniqueness and duplicate detection.

The test database is synthetic and does not require the excluded raw dataset.

### Independent source reconciliation

Run:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_source_profile.py /path/to/raceform.db
```

This validator independently checks the committed source extract against the Notebook 01 totals and date bounds. It is intentionally dataset-specific and should fail when a different source version is supplied.

## Update path

When a new source extract arrives:

1. preserve the old file and record the new source identity;
2. run the structural validator against the new file and expect the current fixed totals to fail;
3. rerun Notebook 01 from a fresh kernel against the new extract;
4. investigate every structural difference rather than replacing expected values automatically;
5. update governed totals in `scripts/validate_source_profile.py` only after review;
6. add or amend unit tests if a stable technical rule changes;
7. record the source-version change and migration consequence before ingestion.

A changed row count is not itself an error. An unexplained change is.

## Known limitation

`profile_source_database()` reproduces the structural definitions established by Notebook 01. It does not replace the later race-identity rules from Notebook 03, and its provisional key constants must not be imported as the permanent core database key.
