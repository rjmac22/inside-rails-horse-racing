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

The raw SQLite database remains read-only.

All source-data queries use:

`DATA_ROW_PREDICATE = "rowid <> 1"`

The established source population is:

- 1,851,285 data-like runner rows;
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

**Status:** fully closed; 9 tests and immutable-source validation passed.

Established deterministic parsing of all observed source `off` values, explicit preservation of 12-hour ambiguity and timezone-aware timestamp construction only after an evidence-backed branch and governed course timezone are supplied.

Validation covered 1,851,285 source rows, 1,380 distinct raw values and 189,043 provisional races with zero unresolved clock representations.

### Notebook 12 — Course location and timezone mapping

**Status:** fully closed; archived executed construction record, 13 tests and permanent-reference validation passed.

The current permanent reference contains:

- 395 jurisdiction-qualified course identities;
- 395 valid IANA timezone assignments;
- 0 unresolved timezone assignments;
- 51 distinct IANA timezones.

The notebook remains an archived historical construction record because persisting the completed reference changed its own future input state. Reusable loading, tests and independent validation now protect the permanent reference.

### Notebook 13 — Prize-money semantics and availability

**Status:** fully closed.

Established runner-level recorded prize-money semantics, direct governed GBP and EUR parsing for Great Britain and Ireland, integer minor-unit storage, null preservation, precise aggregation labels and explicit unresolved treatment for foreign source-presented values.

## Retrospective implementation closeout

The implementation audit for Notebooks 00–13 is complete on branch `audit/retrospective-implementation-closeout`.

No notebook in the 00–13 sequence has an outstanding repair target. Notebook 08's deliberate source anomaly remains documented and unresolved by design.

The branch remains open while the remaining source-field and database work continues. The complete test suite and all applicable validators will be run before final merge.

## Remaining source-field studies

The provisional sequence is now:

1. Notebook 14 — runner counts, numbers and entries (`ran`, `num`);
2. beaten-distance semantics (`ovr_btn`, `btn`);
3. race classification and eligibility;
4. runner characteristics and equipment;
5. ratings semantics and availability;
6. horse and pedigree identity;
7. connections and owner identity;
8. comments and embedded information.

Prize-money and race-time semantics have already been completed in Notebooks 13 and 11 respectively and are no longer future studies.

These are planning units rather than a commitment to one full-length notebook per group. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Current next action

### Notebook 14 — Runner counts, numbers and entries

Fields:

- `ran`
- `num`

Bounded question:

> What do `ran` and `num` represent across jurisdictions, how reliably do they describe runners and entries, and what can safely be stored in the future database?

Required investigation:

- profile `ran` and `num` values, storage, blanks, zeroes and ranges;
- compare source runner rows with `ran` for every provisional race;
- inspect the known races where source rows fall below `ran`;
- distinguish starters, entries, finishers and source rows;
- inspect duplicate runner numbers and coupled-entry conventions by jurisdiction;
- determine whether `num` can serve any identity role;
- define raw, canonical, interpreted and unresolved staging fields;
- establish constraints and source-wide validation rules;
- complete the permanent notebook wrap-up procedure.

Do not redesign the final race key or physical staging schema inside Notebook 14 unless the evidence creates a direct and unavoidable requirement.

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
