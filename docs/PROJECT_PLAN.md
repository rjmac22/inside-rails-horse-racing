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

**Status:** next

Purpose:

- profile every source field systematically;
- distinguish blanks, placeholders, codes and valid values;
- document formats and jurisdiction-specific conventions;
- prioritise fields for dedicated parsing studies.

Expected outputs:

- field-level completeness and storage-class profile;
- controlled value dictionaries for categorical fields;
- representative examples for mixed-format fields;
- investigation register refined into notebook sequence.

## Phase 2 — Domain interpretation and parsing

Provisional notebook sequence, subject to Notebook 02 evidence:

- race identity and source-key reconstruction;
- course, jurisdiction and surface mapping;
- finishing position and non-finish outcomes;
- distance parsing;
- carried-weight parsing;
- starting-price parsing;
- prize and currency parsing;
- race-time parsing;
- ratings semantics and availability;
- horse, trainer, jockey and owner identity risks.

Each study should produce tested parsing or mapping utilities only when the evidence supports them.

## Phase 3 — Entity and key design

Questions:

- What constitutes one race across jurisdictions and source editions?
- What constitutes one runner record?
- Which source identifiers can be retained as attributes?
- Which surrogate identifiers are required?
- How should amended or repeated source records be versioned?
- How should names and jurisdiction-qualified entities be represented?

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

Create Notebook 02 as a systematic field and domain-value profile. Do not begin target-schema design yet.
