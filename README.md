# Inside Rails: Horse-Racing Database

A notebook-led data-engineering and database-design portfolio project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The downloaded source files are intentionally excluded from Git because of size, licensing and reproducibility considerations.

Notebook 01 established that the supplied `raceform.db` has broader geographical and date coverage than the dataset title suggests, including substantial international racing and records through 27 May 2026.

The source contains one denormalised runner-grain table with:

- 1,851,285 data-like runner rows;
- 189,043 reconstructed provisional races;
- 37 source columns;
- no declared primary key, foreign keys, indexes or uniqueness constraints.

The established candidate provisional race key is:

`date + course + off`

The raw SQLite database remains read-only, and source queries use:

`DATA_ROW_PREDICATE = "rowid <> 1"`

## Current status

### Notebook 00 — Project scope and methodology

**Status:** complete

- `notebooks/00_project_scope_and_methodology.ipynb`
- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/NOTEBOOK_00_CLOSEOUT.json`

Established raw-source immutability, notebook-led evidence, conceptual raw/staging/core/analytical layers and deferral of premature schema or platform decisions.

### Notebook 01 — Source database structure profile

**Status:** complete

- `notebooks/01_source_database_structure_profile.ipynb`
- `docs/REPORT_01_SOURCE_DATABASE_STRUCTURE_PROFILE.md`
- `docs/NOTEBOOK_01_CLOSEOUT.json`
- `src/inside_rails/source_sqlite.py`
- `scripts/validate_source_profile.py`

Established the source grain, population, broad international coverage, loose typing and structural limitations.

### Notebook 02 — Source field quality profile

**Status:** complete

- `notebooks/02_source_field_quality_profile.ipynb`
- `docs/REPORT_02_SOURCE_FIELD_QUALITY_PROFILE.md`
- `docs/NOTEBOOK_02_CLOSEOUT.json`

Established field-specific missingness and sentinel conventions, mixed SQLite storage classes and the need to preserve raw values before interpretation.

### Notebook 03 — Race identity and source-key reconstruction

**Status:** complete; clean-kernel Run All passed

- `notebooks/03_race_identity_and_source_key_reconstruction.ipynb`
- `docs/REPORT_03_RACE_IDENTITY_AND_SOURCE_KEY_RECONSTRUCTION.md`
- `docs/NOTEBOOK_03_CLOSEOUT.json`

Established that:

- supplied `race_id` is reused and cannot serve as a unique race key;
- `date + race_id` still collides for eight pairs of distinct races;
- `date + course + off` identifies all 189,043 provisional races uniquely in the current extract;
- candidate race identity plus `horse` identifies each source runner record;
- `num` contains sentinels and shared betting-entry numbers;
- SQLite `rowid` is source lineage rather than business identity;
- later staging tables require independent surrogate race and runner-record identifiers.

### Notebook 04 — Course jurisdiction and surface mapping

**Status:** complete; clean-kernel Run All passed

- `notebooks/04_course_jurisdiction_and_surface_mapping.ipynb`
- `docs/NOTEBOOK_04_CLOSEOUT.json`

Established candidate jurisdiction for every provisional race, reduced 528 raw course values to 395 jurisdiction-qualified candidate venue/configuration identities, and separated direct surface evidence from unresolved enrichment.

### Notebook 05 — Finishing position and non-finish outcomes

**Status:** complete; clean-kernel Run All passed

- `notebooks/05_finishing_position_and_non_finish_outcomes.ipynb`
- `docs/NOTEBOOK_05_CLOSEOUT.json`

Established complete result representation for all source rows, including positive placings, 11 textual outcome codes, disqualifications, supported dead heats and explicitly retained anomalies. It also showed that `btn` and `ovr_btn` cannot be forced into one universal exact-addition rule.

### Notebook 06 — Race distance parsing

**Status:** complete; independent validation and clean-kernel Run All passed

- `notebooks/06_race_distance_parsing.ipynb`
- `docs/REPORT_06_RACE_DISTANCE_PARSING.md`
- `docs/NOTEBOOK_06_CLOSEOUT.json`
- `src/inside_rails/race_distance.py`
- `scripts/validate_race_distance.py`

Established complete deterministic parsing of all 63 observed raw distance values into source-implied component and total measures while keeping official metric-distance enrichment separate.

### Notebook 07 — Carried weight parsing

**Status:** complete; independent validation and clean-kernel Run All passed

- `notebooks/07_carried_weight_parsing.ipynb`
- `docs/REPORT_07_CARRIED_WEIGHT_PARSING.md`
- `docs/NOTEBOOK_07_CLOSEOUT.json`
- `src/inside_rails/carried_weight.py`
- `scripts/validate_carried_weight.py`

Established complete deterministic parsing of all 79 observed canonical stones-and-pounds values into total pounds and source-implied kilograms while preserving the distinction from exact official metric declarations.

### Notebook 08 — Starting price parsing

**Status:** complete; notebook validation and clean-kernel Run All passed

- `notebooks/08_starting_price_parsing.ipynb`
- `docs/REPORT_08_STARTING_PRICE_PARSING.md`
- `docs/NOTEBOOK_08_CLOSEOUT.json`

Established bounded arithmetic parsing of the source `sp` field while demonstrating that market meaning, blank coverage and cross-jurisdiction comparability remain contextual rather than universal.

### Notebook 09 — Course jurisdiction, racing authority and betting-market context

**Status:** complete; independent validation and clean-kernel Run All passed

- `notebooks/09_course_jurisdiction_racing_authority_and_betting_market_context.ipynb`
- `docs/REPORT_09_COURSE_JURISDICTION_RACING_AUTHORITY_AND_BETTING_MARKET_CONTEXT.md`
- `docs/NOTEBOOK_09_CLOSEOUT.json`
- `src/inside_rails/course_jurisdiction.py`
- `scripts/validate_course_jurisdiction.py`

Established:

- reproducible candidate jurisdiction for all 189,043 provisional races;
- 36 candidate jurisdictions and 395 candidate venue/configuration identities;
- separate source, structural-derivation and research-interpretation layers;
- the need for racing-code and effective-period context where justified;
- preservation of raw `type` and `sp` without treating them as universally equivalent;
- deferral of worldwide authority and wagering research until an analytical study requires it.

### Notebook 10 — Remaining source-field inventory and triage

**Status:** complete; notebook assertions and clean-kernel Run All passed

- `notebooks/10_remaining_source_field_inventory_and_triage.ipynb`
- `docs/REPORT_10_REMAINING_SOURCE_FIELD_INVENTORY_AND_TRIAGE.md`
- `docs/NOTEBOOK_10_CLOSEOUT.json`

Established:

- a complete inventory of all 37 source columns;
- 9 fields with substantive prior study;
- 1 field used as supporting context;
- 27 fields still requiring some form of investigation;
- eight broad analytical field families;
- one provisional treatment and rationale for every source field;
- 6 deterministic-parsing fields;
- 3 raw-preservation fields;
- 3 lineage or free-text fields;
- 3 later-jurisdictional-enrichment fields;
- 22 semantic-risk fields;
- 11 bounded investigation groups covering all 27 unresolved fields;
- continued deferral of physical staging-schema design.

The provisional investigation sequence is:

1. off-time and temporal semantics;
2. runner counts, numbers and entries;
3. beaten-distance semantics;
4. race classification and eligibility;
5. runner characteristics and equipment;
6. prize and currency semantics;
7. race-time semantics;
8. ratings semantics and availability;
9. horse and pedigree identity;
10. connections and owner identity;
11. comments and embedded information.

These are planning groups, not a commitment to eleven full-length notebooks. Closely related subjects may be combined where one bounded study can resolve them cleanly.

## Next bounded study

Notebook 11 — off-time and temporal semantics.

Bounded question:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?

This is the first priority because the current candidate race identity depends on `date + course + off`.

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
9. add an independent validation script, test, constraint or reconciliation check where justified;
10. produce a concise report and machine-readable closeout record;
11. update project entry documentation before starting the next notebook.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.

The project does not require every source oddity to be completely explained before implementation proceeds. Each notebook must resolve a design, transformation or validation question rather than merely describe a field.

AI may accelerate query writing, debugging and documentation, but generated work remains untrusted until checked against actual source outputs and the same validation standards as manually written code.

See:

- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/REUSABLE_CODE_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`

## Planned workflow

1. Record source provenance and inventory.
2. Profile the supplied database and fields.
3. Audit data quality and racing-domain meaning.
4. Identify entities and business keys.
5. Design the target relational schema incrementally from supported decisions.
6. Build staging, core and analysis layers.
7. Apply constraints, indexes and validation tests.
8. Publish notebooks and supporting documentation.

## Validation

From the project root:

```bash
PYTHONPATH=src python scripts/validate_source_profile.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

The validation script opens the raw database in read-only mode and checks the stable structural findings from Notebook 01.

Notebook-specific analytical assertions are retained inside each completed profiling notebook and run during clean-kernel validation.
