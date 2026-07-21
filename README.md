# Inside Rails: Horse-Racing Database

A notebook-led data-engineering and database-design portfolio project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The downloaded source files are intentionally excluded from Git because of size, licensing and reproducibility considerations.

Notebook 01 established that the supplied `raceform.db` has broader geographical and date coverage than the dataset title suggests, including substantial international racing and records through 27 May 2026.

## Current status

Notebook 00 — project scope and methodology — is complete:

- `notebooks/00_project_scope_and_methodology.ipynb`
- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/NOTEBOOK_00_CLOSEOUT.json`

Notebook 01 — source database structure profile — is complete:

- `notebooks/01_source_database_structure_profile.ipynb`
- `docs/REPORT_01_SOURCE_DATABASE_STRUCTURE_PROFILE.md`
- `docs/NOTEBOOK_01_CLOSEOUT.json`
- `src/inside_rails/source_sqlite.py`
- `scripts/validate_source_profile.py`

Notebook 02 — source field quality profile — is complete locally and has passed a clean-kernel Run All. Its report and closeout record are published; the notebook file itself remains to be committed from the local checkout:

- `notebooks/02_source_field_quality_profile.ipynb`
- `docs/REPORT_02_SOURCE_FIELD_QUALITY_PROFILE.md`
- `docs/NOTEBOOK_02_CLOSEOUT.json`

The source contains one denormalised runner-grain table with 1,851,285 data-like rows and 189,043 apparent races. It has no declared primary key, foreign keys, indexes or uniqueness constraints. The supplied `race_id` is reused across different races and cannot serve as a reliable standalone key.

Notebook 02 established that missingness and special values are field-specific rather than SQL-`NULL` based. Several declared numeric fields contain mixed storage classes, official placings can differ from the physical finish, prize values mix numeric and euro-formatted text, and raw values must be preserved alongside later parsed fields.

The next analytical stage is race identity and source-key reconstruction before target-schema design.

## Working method

The project follows the same evidence-led closeout discipline used in the Coral 2NL analysis project:

1. develop and verify new analytical logic visibly in a notebook;
2. keep observation separate from interpretation and design decisions;
3. extract only stable, reusable plumbing into `src/inside_rails/`;
4. add a validation script or test for extracted code;
5. produce a concise report and machine-readable closeout record;
6. update project entry documentation before starting the next notebook.

See `docs/REUSABLE_CODE_ARCHITECTURE.md`.

## Planned workflow

1. Record source provenance and inventory.
2. Profile the supplied database and fields.
3. Audit data quality and racing-domain meaning.
4. Identify entities and business keys.
5. Design the target relational schema.
6. Build staging, core and analysis layers.
7. Apply constraints, indexes and validation tests.
8. Publish the notebooks and supporting documentation.

## Validation

From the project root:

```bash
PYTHONPATH=src python scripts/validate_source_profile.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

The validation script opens the raw database in read-only mode and checks the stable structural findings from Notebook 01.
