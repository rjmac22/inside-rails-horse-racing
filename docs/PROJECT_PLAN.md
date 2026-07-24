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
7. produce a concise report;
8. record decisions, uncertainty and next actions;
9. update this plan and the project README.

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

Established:

- supplied `race_id` is not unique;
- `date + race_id` still collides for eight pairs of distinct races;
- `date + course + off` produces 189,043 unique provisional race groups;
- `race_name` remains descriptive validation context;
- candidate race identity plus `horse` identifies each source runner row;
- `num` contains sentinels and shared betting-entry behaviour;
- SQLite `rowid` is source lineage;
- later staging race and runner-record surrogate identifiers are required.

## Phase 2 — Domain interpretation and parsing

### Notebook 04 — Course, jurisdiction and surface mapping

**Status:** complete

Established candidate jurisdiction for all provisional races, 395 jurisdiction-qualified candidate venue/configuration identities, direct all-weather evidence and explicit unresolved surface cases.

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

Established:

- candidate jurisdiction for all 189,043 provisional races;
- 36 candidate jurisdictions;
- 395 candidate venue/configuration identities;
- reusable course and jurisdiction logic in `src/inside_rails/course_jurisdiction.py`;
- independent validation in `scripts/validate_course_jurisdiction.py`;
- separate source, structural-derivation and research-interpretation layers;
- racing-code and effective-period escalation where required;
- preservation of raw `type` and `sp` without universal reinterpretation;
- deferral of worldwide authority and wagering research until required by a bounded analytical study.

### Notebook 10 — Remaining source-field inventory and triage

**Status:** complete; notebook assertions and clean-kernel Run All passed

Outputs:

- `notebooks/10_remaining_source_field_inventory_and_triage.ipynb`
- `docs/REPORT_10_REMAINING_SOURCE_FIELD_INVENTORY_AND_TRIAGE.md`
- `docs/NOTEBOOK_10_CLOSEOUT.json`

Established:

- complete inventory of all 37 source columns;
- 9 fields with substantive prior study;
- 1 supporting-context field;
- 27 fields requiring some form of investigation;
- eight analytical field families;
- a provisional treatment and rationale for every source field;
- 6 deterministic-parsing fields;
- 3 raw-preservation fields;
- 3 lineage or free-text fields;
- 3 later-jurisdictional-enrichment fields;
- 22 semantic-risk fields;
- 11 bounded investigation groups covering all 27 unresolved fields;
- continued deferral of physical staging-schema design.

The 11 groups are planning units rather than a commitment to 11 full-length notebooks. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Remaining source-field studies

Notebook 10 established the following provisional order.

### Notebook 11 — Off-time and temporal semantics

**Status:** next

Field:

- `off`

Bounded question:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?

Priority reason:

The candidate race key uses `date + course + off`, so the source format and temporal meaning of `off` should be established before reconstruction.

The study should profile:

- exact raw formats;
- leading-zero and spacing behaviour;
- race-level consistency;
- jurisdiction and date-period coverage;
- apparent 12-hour or 24-hour conventions;
- midnight and date-rollover risks;
- whether timezone interpretation is source-supplied, inferable or unavailable;
- whether deterministic parsing can be separated from timezone enrichment.

It must not yet redesign the race key or staging schema.

### Provisional Notebook 12 — Runner counts, numbers and entries

Fields:

- `ran`;
- `num`.

Questions include declared versus actual runner counts, source-row reconciliation, zero sentinels, duplicate numbers and coupled-entry behaviour.

### Provisional Notebook 13 — Beaten-distance semantics

Fields:

- `ovr_btn`;
- `btn`.

Questions include cumulative versus incremental meaning, dead heats, amended results, disqualifications, non-finishers, sentinels and rounding.

### Provisional Notebook 14 — Race classification and eligibility

Fields:

- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`;
- `going`.

The study must distinguish source labels, deterministic structure, blank or inapplicable values and later jurisdictional enrichment.

### Provisional Notebook 15 — Runner characteristics and equipment

Fields:

- `age`;
- `sex`;
- `hg`.

Likely scope is bounded validation of ranges, compact code inventories and blank-value behaviour.

### Provisional Notebook 16 — Prize and currency semantics

Field:

- `prize`.

Questions include winner’s prize versus total purse, unit scaling, source storage behaviour, currency by jurisdiction and effective period, and preservation of the raw numeric or textual source value.

### Provisional Notebook 17 — Race-time semantics

Field:

- `time`.

Questions include winning-time meaning, observed formats, precision, missingness, duration parsing and jurisdiction-specific conventions. This field must remain distinct from scheduled `off` time.

### Provisional Notebook 18 — Ratings semantics and availability

Fields:

- `or`;
- `rpr`;
- `ts`.

The study should profile coverage, sentinels, valid ranges, provider meaning, jurisdiction and race-type availability, and relationships among the three ratings.

### Provisional Notebook 19 — Horse and pedigree identity

Fields:

- `horse`;
- `sire`;
- `dam`;
- `damsire`.

Questions include country suffixes, repeated names, punctuation variants, pedigree-assisted distinction and the limits of text-only identity resolution.

### Provisional Notebook 20 — Connections and owner identity

Fields:

- `jockey`;
- `trainer`;
- `owner`.

Questions include name variants, people versus organisations, partnerships, syndicates and the limits of source-text identity.

### Provisional Notebook 21 — Comments and embedded information

Field:

- `comment`.

Raw comments can be preserved without blocking reconstruction. Later work may inventory structured information embedded in comments without treating free text as a replacement for source fields.

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

## Phase 5 — Analytical products

Potential outputs after the database is validated:

- race and runner research views;
- form-history datasets;
- trainer, jockey, course and horse summaries;
- reproducible feature datasets;
- later modelling studies where justified.

Predictive work is downstream of reliable source interpretation and database design.

## Current next action

Create Notebook 11:

> Off-time and temporal semantics

Begin with a bounded inventory of the exact `off` values and their race-level consistency. Preserve the raw field, distinguish deterministic clock parsing from timezone interpretation, and do not alter the candidate race key or design the staging schema inside the notebook.
