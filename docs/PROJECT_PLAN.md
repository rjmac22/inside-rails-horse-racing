# Inside Rails Project Plan

## Objective

Build a documented, reproducible and professionally structured horse-racing analytical database from the supplied third-party source products.

The project is evidence-led. Profiling and domain interpretation come before cleaning, schema design or predictive modelling.

## Standing method

For each substantive notebook:

1. state one bounded question;
2. declare the source and grain under investigation;
3. separate profiling evidence from interpretation;
4. avoid irreversible cleaning decisions inside exploratory work;
5. extract stable reusable plumbing only after it works;
6. validate extracted code independently where justified;
7. produce a concise Minto-style report;
8. record decisions, uncertainty, database consequences and next actions;
9. discuss lessons learned and capture reusable changes;
10. update this plan and the project README;
11. commit and verify the complete closeout.

The raw SQLite database remains read-only.

All source-data queries use:

`DATA_ROW_PREDICATE = "rowid <> 1"`

The established source population is:

- 1,851,285 data-like runner rows;
- 189,043 provisional races;
- 37 source columns;
- candidate provisional race key: `date + course + off`.

## Phase 1 — Source understanding

### Notebook 00 — Project scope and methodology

**Status:** complete

Established raw-source immutability, notebook-led evidence, conceptual raw/staging/core/analytical layers and deferral of premature schema or platform decisions.

### Notebook 01 — Source database structure profile

**Status:** complete

Established one denormalised runner-grain table, the source population, broad international and 2015–2026 coverage, loose typing and structural limitations.

### Notebook 02 — Field and domain-value profile

**Status:** complete

Established field-specific missingness, blank and sentinel conventions, mixed SQLite storage classes, unusual result values, prize and rating anomalies, and preservation requirements for long text and raw values.

### Notebook 03 — Race identity and source-key reconstruction

**Status:** complete

Established that supplied `race_id` is not unique, `date + race_id` still collides, `date + course + off` produces 189,043 unique provisional race groups, candidate race identity plus `horse` identifies each source runner row, and later staging race and runner-record surrogate identifiers are required.

## Phase 2 — Domain interpretation and parsing

### Notebook 04 — Course, jurisdiction and surface mapping

**Status:** complete

Established candidate jurisdiction for all provisional races, jurisdiction-qualified candidate venue/configuration identities, direct all-weather evidence and explicit unresolved surface cases.

### Notebook 05 — Finishing position and non-finish outcomes

**Status:** complete; clean-kernel Run All passed

Established complete result representation, textual non-finish outcomes, disqualification handling, supported dead heats and explicitly retained anomalies. Demonstrated that `btn` and `ovr_btn` are related but cannot be forced into one universal exact-addition rule.

### Notebook 06 — Race distance parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established complete deterministic parsing of all observed raw distance values into source-implied measures while keeping official metric-distance enrichment separate.

### Notebook 07 — Carried weight parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established complete deterministic parsing of all observed canonical stones-and-pounds values into total pounds and source-implied kilograms while preserving the distinction from exact official metric declarations.

### Notebook 08 — Starting price parsing

**Status:** complete; notebook validation and clean-kernel Run All passed

Established bounded arithmetic parsing of `sp`, five race-level coverage patterns and the requirement to separate arithmetic price representation from jurisdictional market interpretation.

### Notebook 09 — Course jurisdiction, racing authority and betting-market context

**Status:** complete; independent validation and clean-kernel Run All passed

Established reproducible candidate jurisdiction, reusable course and jurisdiction logic, separate source/structural/research layers, racing-code and effective-period escalation where required, and preservation of raw `type` and `sp` without universal reinterpretation.

### Notebook 10 — Remaining source-field inventory and triage

**Status:** complete; notebook assertions and clean-kernel Run All passed

Established the complete 37-field inventory, provisional treatment for every field and the bounded sequence for remaining source-field studies.

### Notebook 11 — Off-time and temporal semantics

**Status:** in progress; timezone dependency resolved

Field:

- `off`

Bounded question:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?

The study profiles exact raw formats, leading-zero and spacing behaviour, race-level consistency, jurisdiction and date-period coverage, apparent 12-hour or 24-hour conventions, midnight and date-rollover risks, and the separation of deterministic parsing from timezone enrichment.

Notebook 11 identified a dependency on governed course-timezone data. That dependency was resolved in Notebook 12.

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
- identity based on `candidate_course_label + candidate_jurisdiction`;
- safe jurisdiction defaults only where one timezone applies;
- course-level manual resolution for multi-timezone jurisdictions;
- separation of exact venue enrichment from timezone sufficiency;
- reusable loading, reference validation and many-to-one merge logic.

The notebook is retained as an executed historical construction record. It is not treated as a permanent rerunnable pipeline because persisting the completed reference changed the notebook's future input state. Independent reusable validation now protects the permanent reference.

## Remaining source-field studies

The provisional sequence remains:

1. complete Notebook 11 — off-time and temporal semantics;
2. runner counts, numbers and entries (`ran`, `num`);
3. beaten-distance semantics (`ovr_btn`, `btn`);
4. race classification and eligibility;
5. runner characteristics and equipment;
6. prize and currency semantics;
7. race-time semantics;
8. ratings semantics and availability;
9. horse and pedigree identity;
10. connections and owner identity;
11. comments and embedded information.

These are planning units rather than a commitment to one full-length notebook per group. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Phase 3 — Entity and key design

Notebook 03 established candidate source-record matching rules, but permanent entity and key design remains deferred.

Questions still to resolve include:

- stability of descriptive race fields across replacement snapshots;
- permanent representation of jurisdiction-qualified courses;
- entity-resolution requirements for horse and participant names;
- versioning of amended or repeated source records;
- coupled-entry representation;
- staging surrogate identifiers and reconciliation controls.

This phase begins only after the source-field studies required for structural reconstruction have been completed or explicitly deferred.

## Phase 4 — Target architecture

Only after the evidence base is sufficient:

- consolidate reconstruction requirements;
- define a conceptual staging model;
- select the physical database technology;
- define staging, core and analytical schemas;
- create tables, constraints and indexes;
- implement repeatable ingestion;
- preserve raw source values and technical lineage;
- add automated reconciliation and integrity tests.

## Phase 5 — Analytical products and writing

Potential outputs after the database is validated:

- race and runner research views;
- form-history datasets;
- trainer, jockey, course and horse summaries;
- reproducible feature datasets;
- claim-testing investigations;
- reader-facing stories about hidden data assumptions;
- later modelling studies where justified.

Predictive work is downstream of reliable source interpretation and database design.

## Current next action

Resume Notebook 11 using:

`data/reference/course_locations.csv`

as the governed timezone reference.

Complete:

- deterministic parsing of source `off` values;
- local civil-time interpretation;
- timezone-aware timestamp construction where defensible;
- midnight and date-rollover assessment;
- exception preservation;
- database consequence;
- reusable code and validation where justified;
- full notebook closeout procedure.

Do not redesign the final race key or physical staging schema inside Notebook 11 unless the evidence creates a direct and unavoidable requirement.
