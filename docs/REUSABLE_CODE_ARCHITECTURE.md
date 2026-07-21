# Reusable Code Architecture

## Purpose

Inside Rails is notebook-led, but it is not notebook-only.

Finished notebooks should explain:

- the analytical question;
- the source evidence;
- the interpretation;
- the conclusions and uncertainty.

Reusable technical plumbing should live outside notebooks so it can be tested, reused and reviewed independently.

## Project rule

New logic should normally be developed visibly in the notebook first.

Once the logic:

- has run successfully;
- is stable;
- is not specific to one displayed result;
- will be reused by another notebook or validation script;

it should be extracted into `src/inside_rails/`.

The finished notebook should retain the analytical intent and results rather than low-level implementation noise.

## Current package structure

### `src/inside_rails/source_sqlite.py`

Responsible for source-database plumbing that is independent of a particular notebook display:

- opening SQLite files in read-only mode;
- safely quoting SQLite identifiers;
- inventorying schema objects;
- reading declared table-column metadata;
- constructing null-safe provisional composite-key expressions;
- reproducing the stable structural assertions established by Notebook 01.

It does not:

- clean source values;
- alter the raw database;
- decide the final relational schema;
- convert racing-domain codes;
- resolve real-world entity identity.

### `scripts/validate_source_profile.py`

Provides a command-line regression check for the specific `raceform.db` source profiled in Notebook 01.

It checks:

- row counts;
- apparent-race count;
- provisional runner-key uniqueness;
- date coverage;
- schema-object count;
- declared-column count;
- SQLite quick-check result.

Run from the project root with the package on `PYTHONPATH`:

```bash
PYTHONPATH=src python scripts/validate_source_profile.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

## Layer boundaries

The project should develop reusable code in layers.

### Generic technical layer

Code that could work with another SQLite source or another racing dataset:

- filesystem and project paths;
- read-only database connections;
- schema inspection;
- validation helpers;
- deterministic reporting utilities.

### Inside Rails source-adapter layer

Code that understands the supplied source product without yet imposing a final domain model:

- header-row exclusion rules;
- source-table names;
- provisional race and runner descriptions;
- source-specific profile assertions;
- source lineage.

### Racing-domain layer

Code added only after the relevant meanings have been established:

- distance parsing;
- weight parsing;
- finishing-outcome interpretation;
- going classification;
- starting-price parsing;
- jurisdiction and course mapping;
- race, horse and participant identity rules.

### Database-build layer

Code added after the target architecture is justified:

- staging loads;
- transformations;
- core-table creation;
- constraints and indexes;
- reconciliation tests;
- analytical views.

## Validation rule

Every extracted reusable module should have a corresponding validation route.

Validation may be:

- a focused script under `scripts/`;
- automated tests;
- database reconciliation queries;
- schema or constraint assertions.

Notebook output alone is not sufficient validation for code intended to support later project stages.

## Raw-data rule

Reusable utilities must never silently modify files under `data/raw/`.

Source access should default to read-only operation. Any later ingestion process must write to separate staging or build locations and preserve source lineage.

## Documentation rule

Each completed notebook should normally produce:

- the finished notebook;
- a concise Minto-style report in `docs/`;
- a machine-readable closeout record;
- reusable code where justified;
- a validation script or test where reusable code was extracted;
- updates to the README and project plan.

This mirrors the working method established in the Coral 2NL analysis project while adapting it to data engineering and horse-racing domain analysis.
