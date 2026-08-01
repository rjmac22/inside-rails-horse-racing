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
6. add focused unit tests including failure behaviour;
7. validate extracted code and governed references independently where justified;
8. document the database and update consequence;
9. produce a concise Minto-style report;
10. record decisions, uncertainty, lessons learned and next actions;
11. update the audit register, field governance, this plan and the project README;
12. commit and verify the complete closeout.

The full procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The raw SQLite database remains read-only. All source-data queries use `DATA_ROW_PREDICATE = "rowid <> 1"`.

Established source population:

- 1,851,285 governed runner rows;
- 189,043 provisional races;
- 37 source columns;
- candidate provisional race key: `date + course + off`.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status:** complete and retrospectively implemented.

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and parsing

### Notebooks 04–16

**Status:** complete and retrospectively implemented or fully closed.

Established course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, complete field governance, and race classification and eligibility.

Notebook 08 retains one deliberate governed validator failure for the malformed standalone source value `F`.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed age, sex and headgear rules, including exact verification-backed contamination corrections and source-specific eyecover normalisation.

### Notebook 18 — Ratings semantics and availability

**Status:** fully closed.

Governed rules:

- preserve raw `or`, `rpr` and `ts` values separately;
- parse the exact Unicode en dash `–` as unavailable/null, never zero;
- interpret `or` as a pre-race official handicap mark;
- interpret `rpr` as a retrospective and potentially revisable performance rating;
- interpret `ts` as a retrospective speed figure;
- keep independent nullable analytical values and statuses for all three fields;
- exclude only source `rowid = 1619851`, `rpr = 775` as an exact lineage-backed invalid value;
- preserve its raw value and leave its intended replacement unresolved;
- treat observed ranges as validation baselines rather than universal business rules.

Durable outputs:

- `notebooks/18_ratings_semantics_and_availability.ipynb`;
- `src/inside_rails/ratings.py`;
- `tests/test_ratings.py`;
- `scripts/validate_ratings.py`;
- `docs/NOTEBOOK_18_RATINGS_DATABASE_INTEGRATION.md`;
- `docs/NOTEBOOK_18_RATINGS_REPORT.md`;
- `docs/NOTEBOOK_18_LESSONS_LEARNED.md`;
- three permanent Notebook 18 records in `data/reference/manual_verifications.csv`.

Recorded closeout validation:

- `22 passed in 0.06s` across focused ratings and manual-verification tests;
- independent ratings validation passed across 1,851,285 governed runner rows;
- `or`: 1,116,633 available, 734,652 unavailable, 0 invalid, range 1–181;
- `rpr`: 1,644,175 available, 207,109 unavailable, 1 invalid, range 1–184;
- `ts`: 1,227,384 available, 623,901 unavailable, 0 invalid, range 1–178;
- manual-verification validation passed across 36 governed rows.

The complete repository suite remains deferred until the end of the source-field series or repair branch.

## Remaining source-field studies

The provisional sequence is now:

1. horse and pedigree identity;
2. connections and owner identity;
3. comments and embedded information.

These are planning units rather than a commitment to one full-length notebook per group. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Current next action

### Begin horse and pedigree identity

Bound the next study around `horse`, `sire`, `dam` and `damsire`. Establish raw-name stability, country-suffix behaviour, missingness, collisions, lineage requirements and which identity rules can be implemented safely without premature entity resolution.

Do not run the complete repository suite yet.

## Phase 3 — Entity and key design

Permanent entity and key design remains deferred until the source-field studies required for structural reconstruction are completed or explicitly deferred.

Questions still to resolve include descriptive-field stability across replacement snapshots, entity resolution for horses and participants, amended-record versioning, coupled-entry representation, staging surrogate identifiers and reconciliation controls.

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

Potential outputs after the database is validated include research views, form-history datasets, trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Predictive work remains downstream of reliable source interpretation and database design.
