# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

The wider purpose is not database construction for its own sake. The project is intended to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The downloaded raw source files are intentionally excluded from Git because of size, licensing and reproducibility considerations.

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

Established raw-source immutability, notebook-led evidence, conceptual raw/staging/core/analytical layers and deferral of premature schema or platform decisions.

### Notebook 01 — Source database structure profile

**Status:** complete

Established the source grain, population, broad international coverage, loose typing and structural limitations.

Reusable outputs:

- `src/inside_rails/source_sqlite.py`
- `scripts/validate_source_profile.py`

### Notebook 02 — Source field quality profile

**Status:** complete

Established field-specific missingness and sentinel conventions, mixed SQLite storage classes and the need to preserve raw values before interpretation.

### Notebook 03 — Race identity and source-key reconstruction

**Status:** complete; clean-kernel Run All passed

Established that supplied `race_id` is reused, `date + race_id` still collides, `date + course + off` identifies all 189,043 provisional races in the current extract, candidate race identity plus `horse` identifies each source runner record, and later staging tables require independent surrogate identifiers.

### Notebook 04 — Course jurisdiction and surface mapping

**Status:** complete; clean-kernel Run All passed

Established candidate jurisdiction for every provisional race, reduced 528 raw course values to jurisdiction-qualified candidate venue/configuration identities, and separated direct surface evidence from unresolved enrichment.

### Notebook 05 — Finishing position and non-finish outcomes

**Status:** complete; clean-kernel Run All passed

Established complete result representation, textual non-finish outcomes, disqualification handling, supported dead heats and explicitly retained anomalies. It also showed that `btn` and `ovr_btn` cannot be forced into one universal exact-addition rule.

### Notebook 06 — Race distance parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established complete deterministic parsing of all observed raw distance values into source-implied component and total measures while keeping official metric-distance enrichment separate.

Reusable outputs:

- `src/inside_rails/race_distance.py`
- `scripts/validate_race_distance.py`

### Notebook 07 — Carried weight parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established complete deterministic parsing of all observed canonical stones-and-pounds values into total pounds and source-implied kilograms while preserving the distinction from exact official metric declarations.

Reusable outputs:

- `src/inside_rails/carried_weight.py`
- `scripts/validate_carried_weight.py`

### Notebook 08 — Starting price parsing

**Status:** complete; notebook validation and clean-kernel Run All passed

Established bounded arithmetic parsing of the source `sp` field while demonstrating that market meaning, blank coverage and cross-jurisdiction comparability remain contextual rather than universal.

### Notebook 09 — Course jurisdiction, racing authority and betting-market context

**Status:** complete; independent validation and clean-kernel Run All passed

Established reproducible candidate jurisdiction for all provisional races, separate source, structural-derivation and research-interpretation layers, and preservation of raw `type` and `sp` without treating them as universally equivalent.

Reusable outputs:

- `src/inside_rails/course_jurisdiction.py`
- `scripts/validate_course_jurisdiction.py`

### Notebook 10 — Remaining source-field inventory and triage

**Status:** complete; notebook assertions and clean-kernel Run All passed

Established a complete inventory of all 37 source columns, one provisional treatment for every field, and a bounded sequence for the remaining semantic investigations.

### Notebook 11 — Off-time and temporal semantics

**Status:** in progress; timezone dependency resolved

- `notebooks/11_off_time_and_temporal_semantics.ipynb`

The study profiles the exact source `off` formats, race-level consistency, jurisdiction and date-period coverage, 12-hour and 24-hour behaviour, midnight risks and the distinction between deterministic clock parsing and timezone interpretation.

Notebook 11 identified that safe temporal interpretation required a governed course-timezone reference, which was resolved in Notebook 12.

### Notebook 12 — Course location and timezone mapping

**Status:** complete; archived executed research record; independent validation passed

Outputs:

- `notebooks/12_course_timezone_resolution_completed_archive.ipynb`
- `docs/REPORT_12_COURSE_LOCATION_AND_TIMEZONE_MAPPING.md`
- `docs/NOTEBOOK_12_CLOSEOUT.json`
- `data/reference/course_locations.csv`
- `data/reference/course_location_manual_review.csv`
- `data/reference/course_location_manual_timezone_resolution.csv`
- `data/reference/course_location_geocoding_run_summary.csv`
- `src/inside_rails/course_locations.py`
- `scripts/validate_course_locations.py`

Established:

- 394 permanent jurisdiction-qualified course identities;
- 394 valid IANA timezone assignments;
- 0 unresolved timezone assignments;
- 51 distinct IANA timezones;
- explicit separation of course identity, exact venue enrichment and timezone sufficiency;
- safe jurisdiction defaults only where one timezone applies;
- course-level manual resolution for multi-timezone jurisdictions;
- governed reference loading, validation and many-to-one merging.

The executed notebook is preserved as the historical construction record. It is not intended to be rerun against the completed permanent reference because persisting the reference changed the notebook's future input state. Reusable validation is provided independently.

## Next bounded action

Resume Notebook 11 using `data/reference/course_locations.csv` as the governed timezone reference.

The remaining question is:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?

Notebook 11 should complete deterministic clock parsing, timezone-aware interpretation, date-rollover assessment and the resulting database consequence without redesigning the final race key or physical staging schema prematurely.

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
11. discuss and record lessons learned;
12. update project entry documentation before starting the next notebook;
13. commit and verify the completed closeout.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.

See:

- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/REUSABLE_CODE_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`

## Validation

Course-location reference validation:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_course_locations.py
```

The validator checks required columns, identity uniqueness, complete timezone coverage, valid IANA timezone names, coordinate bounds and the expected current reference totals.
