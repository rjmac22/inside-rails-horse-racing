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
6. validate extracted code independently;
7. produce a concise report;
8. record decisions, uncertainty and next actions;
9. update this plan and the project README.

## Phase 1 — Source understanding

### Notebook 00 — Project scope and methodology

**Status:** complete

Established:

- raw-source immutability;
- notebook-led evidence process;
- conceptual raw, staging, core and analytical layers;
- no premature target-platform or schema decision.

### Notebook 01 — Source database structure profile

**Status:** complete

Established:

- one SQLite table named `data`;
- 1,851,285 data-like runner rows;
- 189,043 apparent races;
- likely grain of one horse participating in one race;
- denormalised race and runner attributes;
- unreliable standalone `race_id`;
- broad international and 2015–2026 coverage;
- loose typing and field-specific missing-value conventions.

### Notebook 02 — Field and domain-value profile

**Status:** complete

Established:

- field-specific missing-value conventions across all 37 source columns;
- blank strings and sentinel values are used instead of SQL `NULL`;
- mixed SQLite storage classes occur in several declared numeric fields;
- finishing positions combine numeric placings with non-finisher codes;
- official placings can differ from the physical finishing order;
- runner-level time values are closely linked to recorded finishing margins;
- weights, starting prices, headgear and prize values require dedicated parsing;
- prize values combine numeric amounts with euro-prefixed text;
- `or`, `rpr` and `ts` use an en dash for missing values;
- one isolated `rpr = 775` anomaly should be retained raw and flagged;
- pedigree and ownership fields are nearly complete;
- long comments contain legitimate steward-enquiry text and must not be truncated.

### Notebook 03 — Race identity and source-key reconstruction

**Status:** complete

Established:

- 188,782 distinct supplied `race_id` values across 189,043 reconstructed races;
- 206 `race_id` values occur on multiple dates;
- eight `date + race_id` pairs each identify two different races;
- `date + course + off` produces 189,043 unique race groups;
- `race_name` adds no groups in this extract but remains a required descriptive validation field;
- omitting `off` would merge 516 races and affect 10,410 runner rows;
- race identity plus `horse` is unique across all 1,851,285 data-like rows;
- 700 race-and-number groups contain multiple horses;
- `num` has sentinel and jurisdiction-dependent betting-entry behaviour;
- no exact duplicate source records were found;
- original SQLite `rowid` is unique and should be retained as source lineage;
- physical source adjacency cannot be used to reconstruct race membership;
- later staging tables will require surrogate race and runner-record identifiers;
- no final target schema was designed.

Candidate matching rules:

- race: `date + course + off`;
- conservative race grouping: `date + course + off + race_name`;
- runner record: candidate race identity plus `horse`.

## Phase 2 — Domain interpretation and parsing

Current notebook sequence, refined by Notebooks 02 and 03:

1. course, jurisdiction and surface mapping;
2. finishing position and non-finish outcomes;
3. distance parsing;
4. carried-weight parsing;
5. starting-price parsing;
6. prize and currency parsing;
7. race-time parsing;
8. ratings semantics and availability;
9. horse, trainer, jockey and owner identity risks;
10. coupled-entry interpretation where justified.

Each study should produce tested parsing or mapping utilities only when the evidence supports them.

## Phase 3 — Entity and key design

Notebook 03 has established candidate source-record matching rules, but permanent entity and key design remains deferred.

Questions still to resolve:

- How stable are descriptive race fields across replacement source snapshots?
- How should jurisdiction-qualified courses be represented?
- Which names require entity-resolution rules rather than exact matching?
- How should amended or repeated source records be versioned?
- How should coupled entries be represented?
- Which surrogate identifiers and reconciliation controls should the staging layer use?

Outputs:

- candidate entity model;
- tested business-key analysis;
- lineage and source-record strategy;
- reconciliation rules.

## Phase 4 — Target architecture

Only after the earlier evidence is complete:

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

Create Notebook 04 as a bounded study of course, jurisdiction and surface mapping.

The notebook should determine:

- how course names encode jurisdiction and course variants;
- whether jurisdiction can be parsed reliably from course text;
- how all-weather, turf and other surface information is represented;
- where course naming varies across time or source jurisdictions;
- which raw and canonical course attributes a later staging layer must preserve.

The study must remain observational and must not begin final target-schema design.
