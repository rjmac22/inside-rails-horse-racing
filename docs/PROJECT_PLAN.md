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

### Notebooks 04–10

**Status:** complete and retrospectively implemented.

Established course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, and governance of all 37 source fields.

Notebook 08 retains one deliberate governed validator failure for the malformed standalone source value `F`.

### Notebook 11 — Off-time and temporal semantics

**Status:** fully closed.

Established deterministic parsing of observed source `off` values, explicit preservation of 12-hour ambiguity and timezone-aware timestamp construction only after an evidence-backed branch and governed course timezone are supplied.

### Notebook 12 — Course location and timezone mapping

**Status:** fully closed as an archived construction record with durable reference validation and source-facing join repair.

The permanent reference contains 395 jurisdiction-qualified course identities, complete valid IANA timezone coverage and zero unresolved assignments.

### Notebook 13 — Prize-money semantics and availability

**Status:** fully closed.

Established runner-level recorded prize-money semantics, governed GBP and EUR parsing for Great Britain and Ireland, integer minor-unit storage, null preservation and unresolved treatment for unsupported foreign values.

### Notebook 14 — Runner counts, numbers and entries

**Status:** fully closed.

Established that `ran` is a source-presented race count rather than guaranteed external starter completeness, and that `num` must preserve positive integer, zero and blank states separately. Shared positive numbers are permitted and `num` does not participate in runner identity.

### Notebook 15 — Beaten-distance semantics

**Status:** durable implementation complete; focused local validation pending.

Established that `ovr_btn` describes cumulative distance from the source physical-finish first-place reference and `btn` describes incremental separation from the preceding physical finisher or stored distance group.

Governed rules:

- preserve raw values;
- derive numeric values only from numeric storage;
- treat `-` as unavailable rather than zero;
- flag positive official-winner distance and later-position zero overall distance for review;
- treat zero incremental distance with positive overall distance as same-distance-group evidence, not automatic proof of an official dead heat;
- permit downstream correction only through governed reconciliation with verification provenance.

Durable outputs:

- `src/inside_rails/beaten_distance.py`;
- `tests/test_beaten_distance.py`;
- `scripts/validate_beaten_distances.py`;
- `docs/BEATEN_DISTANCE_INTEGRATION.md`;
- `docs/NOTEBOOK_15_FIELD_GOVERNANCE.md`;
- `docs/NOTEBOOK_15_LESSONS_LEARNED.md`;
- `reports/notebook_15_beaten_distance_semantics.md`.

Notebook 15 becomes fully closed after focused local tests and the independent source-wide validator pass and are recorded. The complete repository suite remains deferred until the end of the source-field series or repair branch.

## Remaining source-field studies

The provisional sequence is now:

1. race classification and eligibility;
2. runner characteristics and equipment;
3. ratings semantics and availability;
4. horse and pedigree identity;
5. connections and owner identity;
6. comments and embedded information.

These are planning units rather than a commitment to one full-length notebook per group. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Current next action

### Validate and close Notebook 15 implementation

Run only the focused Notebook 15 checks:

```bash
pytest -q tests/test_beaten_distance.py
python scripts/validate_beaten_distances.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

Record the results in the audit register and closeout record. Do not run the complete repository suite yet.

### Then begin race classification and eligibility

Bound the next study around `class`, `pattern`, `rating_band`, `age_band`, `sex_rest` and related eligibility fields. Profile storage, coverage, jurisdiction dependence, internal contradictions and safe preservation rules before extracting reusable logic.

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
