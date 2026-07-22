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

Notebook 02 — source field quality profile — is complete:

- `notebooks/02_source_field_quality_profile.ipynb`
- `docs/REPORT_02_SOURCE_FIELD_QUALITY_PROFILE.md`
- `docs/NOTEBOOK_02_CLOSEOUT.json`

Notebook 03 — race identity and source-key reconstruction — is complete and has passed a clean-kernel Run All:

- `notebooks/03_race_identity_and_source_key_reconstruction.ipynb`
- `docs/REPORT_03_RACE_IDENTITY_AND_SOURCE_KEY_RECONSTRUCTION.md`
- `docs/NOTEBOOK_03_CLOSEOUT.json`

Notebook 04 — course jurisdiction and surface mapping — is complete and has passed a clean-kernel Run All:

- `notebooks/04_course_jurisdiction_and_surface_mapping.ipynb`
- `docs/NOTEBOOK_04_CLOSEOUT.json`

Notebook 05 — finishing position and non-finish outcomes — is complete and has passed a clean-kernel Run All:

- `notebooks/05_finishing_position_and_non_finish_outcomes.ipynb`
- `docs/NOTEBOOK_05_CLOSEOUT.json`

Notebook 06 — race distance parsing — has completed analytical reconciliation and independent validation; clean-kernel Run All remains pending:

- `notebooks/06_race_distance_parsing.ipynb`
- `docs/REPORT_06_RACE_DISTANCE_PARSING.md`
- `docs/NOTEBOOK_06_CLOSEOUT.json`
- `src/inside_rails/race_distance.py`
- `scripts/validate_race_distance.py`

The source contains one denormalised runner-grain table with 1,851,285 data-like rows and 189,043 reconstructed provisional races. It has no declared primary key, foreign keys, indexes or uniqueness constraints.

Notebook 02 established that missingness and special values are field-specific rather than SQL-`NULL` based. Several declared numeric fields contain mixed storage classes, official placings can differ from the physical finish, prize values mix numeric and euro-formatted text, and raw values must be preserved alongside later parsed fields.

Notebook 03 established that:

- the supplied `race_id` is reused and cannot serve as a unique race key;
- even `date + race_id` collides for eight pairs of genuinely different races;
- `date + course + off` is unique across the current extract and is the leading candidate natural race identity;
- `race_name` should remain attached as a descriptive validation field;
- adding `horse` identifies one unique runner record within every reconstructed race;
- `num` cannot identify an individual runner because it includes zero sentinels and shared betting-entry numbers;
- original SQLite `rowid` should be preserved as source lineage, not business identity;
- later staging tables will require independent surrogate race and runner-record identifiers.

Notebook 04 established that:

- all 189,043 provisional races can receive a candidate jurisdiction;
- 528 raw course values reduce to 395 jurisdiction-qualified candidate venue/configuration identities;
- recognised terminal jurisdiction suffixes can be removed while retaining meaningful markers such as `(AW)`, `(July)`, `(RH)` and `(Perth)`;
- the 135 candidate identities represented by multiple raw forms have no same-date form collisions;
- 33,023 races have direct all-weather evidence from an explicit `(AW)` course marker;
- `race_name` is not reliable for surface derivation;
- the remaining 156,020 surface values require later external race-level enrichment;
- eight reproducible explicit NH Flat/type conflicts require separate validation.

Notebook 05 established that:

- all 1,851,285 source runner records can be represented without replacing raw `ran`, `pos`, `btn` or `ovr_btn`;
- 1,756,666 rows contain positive numeric finishing positions;
- 94,611 rows contain one of 11 validated textual result codes;
- 619 `DSQ` rows retain numeric beaten-distance values and must remain separate from ordinary non-finish outcomes;
- 3,006 duplicated race-position groups covering 6,020 runners are supported candidate dead heats;
- eight `pos = 0` rows remain unresolved;
- ten rows have numeric `pos > ran`;
- five provisional races contain fewer source rows than recorded `ran`;
- two duplicated-position rows have conflicting cumulative distances;
- one Morphettville row was externally verified as a source anomaly and is retained as an audit record rather than overwritten;
- `btn` and `ovr_btn` are related but cannot be forced into a universally additive sequence, especially after amended results.

Notebook 06 established that:

- all 1,851,285 runner records contain a non-blank text `dist` value;
- every provisional race contains one internally consistent raw distance;
- 63 exact raw values cover all 189,043 provisional races;
- all current values parse reproducibly into miles, furlongs and optional half-furlongs;
- exact integer source-implied yards and deterministic source-implied metres are available for every race;
- previously unseen values must remain unresolved rather than be interpreted automatically;
- source-implied distances describe the source expression, not necessarily the independently verified official scheduled distance;
- official 1,600-metre races were externally verified in the source as `1m`, demonstrating international approximation;
- official metric-jurisdiction distances require separate race-level enrichment;
- early analytical work will prioritise UK and Irish racing while preserving international records and their provenance limitation.

The next bounded study is carried-weight parsing. Final target-schema design remains deferred.

## Working method

The project follows an evidence-led investigation-to-implementation cycle:

1. profile the raw source without altering it;
2. state one bounded candidate rule or database-design question;
3. test coverage, uniqueness, exceptions and failure modes;
4. inspect material exceptions and preserve unresolved cases explicitly;
5. separate observation, interpretation, confidence and design decision;
6. translate the conclusion into a practical database consequence;
7. implement the rule reversibly while retaining raw values and lineage;
8. extract only stable, reusable plumbing into `src/inside_rails/`;
9. add an independent validation script, test, constraint or reconciliation check;
10. produce a concise report and machine-readable closeout record;
11. update project entry documentation before starting the next notebook.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.

The project does not require every source oddity to be completely explained before implementation proceeds. Each notebook must resolve a design, transformation or validation question rather than merely describe a field. Stable bounded rules should move incrementally into staging so that the emerging architecture is tested in practice.

AI may accelerate query writing, debugging and documentation, but generated work remains untrusted until checked against actual source outputs and the same validation standards as manually written code.

See:

- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/REUSABLE_CODE_ARCHITECTURE.md`

## Planned workflow

1. Record source provenance and inventory.
2. Profile the supplied database and fields.
3. Audit data quality and racing-domain meaning.
4. Identify entities and business keys.
5. Design the target relational schema incrementally from supported decisions.
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

Notebook-specific analytical assertions are retained inside each completed profiling notebook and run during clean-kernel validation.
