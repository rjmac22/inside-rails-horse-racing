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
- blank strings and sentinel values instead of SQL `NULL`;
- mixed SQLite storage classes in several declared numeric fields;
- finishing positions combining numeric placings and non-finisher codes;
- official placings that can differ from physical finishing order;
- runner-level time values closely linked to finishing margins;
- weights, starting prices, headgear and prize values requiring dedicated study;
- prize values combining numeric amounts and euro-prefixed text;
- `or`, `rpr` and `ts` using an en dash for missing values;
- one isolated `rpr = 775` anomaly retained raw and flagged;
- nearly complete pedigree and ownership fields;
- legitimate long steward-enquiry comments that must not be truncated.

### Notebook 03 — Race identity and source-key reconstruction

**Status:** complete

Established:

- 188,782 distinct supplied `race_id` values across 189,043 reconstructed races;
- 206 `race_id` values occurring on multiple dates;
- eight `date + race_id` pairs each identifying two different races;
- `date + course + off` producing 189,043 unique race groups;
- `race_name` remaining a required descriptive validation field;
- candidate race identity plus `horse` identifying every source runner row uniquely;
- `num` containing sentinel and jurisdiction-dependent betting-entry behaviour;
- no exact duplicate source records;
- original SQLite `rowid` retained as source lineage;
- physical adjacency unsuitable for reconstructing race membership;
- future staging race and runner-record surrogate identifiers required;
- no final target schema designed.

Candidate matching rules:

- race: `date + course + off`;
- conservative race grouping: `date + course + off + race_name`;
- runner record: candidate race identity plus `horse`.

## Phase 2 — Domain interpretation and parsing

### Notebook 04 — Course, jurisdiction and surface mapping

**Status:** complete

Established:

- candidate jurisdiction for all 189,043 provisional races;
- 528 raw course values and 395 jurisdiction-qualified candidate venue/configuration identities;
- 135 candidate identities represented by multiple raw forms;
- no same-date collisions among those forms;
- direct all-weather evidence for 33,023 races from explicit `(AW)` markers;
- 156,020 races whose surface remains unresolved from the source alone;
- eight explicit NH Flat/type conflicts requiring later validation;
- no derivation of canonical surface from race-name wording.

### Notebook 05 — Finishing position and non-finish outcomes

**Status:** complete; clean-kernel Run All passed

Established:

- complete candidate result representation for all 1,851,285 source runner rows;
- 1,756,666 positive numeric finishing-position rows;
- 94,611 textual-position rows using 11 validated codes;
- separate treatment of `DSQ` rows retaining numeric margins;
- 3,006 supported candidate dead-heat groups covering 6,020 runners;
- eight unresolved `pos = 0` rows;
- ten numeric positions above `ran`;
- five incomplete provisional race extracts;
- two duplicated-position rows with conflicting cumulative distances;
- one externally verified Morphettville source anomaly retained separately;
- no universal exact-addition rule for `btn` and `ovr_btn`;
- raw and candidate result attributes remaining separate;
- no final target schema designed.

### Notebook 06 — Race distance parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established:

- complete non-blank text `dist` coverage;
- one internally consistent raw distance per provisional race;
- 63 exact raw values covering all 189,043 provisional races;
- complete parsing into miles, furlongs and optional half-furlongs;
- source-implied yards and metres for every race;
- unsupported future values remaining unresolved;
- source-implied distance not necessarily equalling official scheduled distance;
- official 1,600-metre races represented as `1m` in the source;
- official metric distances requiring later race-level enrichment;
- initial analytical priority for UK and Irish racing.

### Notebook 07 — Carried weight parsing

**Status:** complete; independent validation and clean-kernel Run All passed

Established:

- complete non-blank text `wgt` coverage;
- 79 distinct raw values;
- one canonical stones-and-pounds notation family;
- complete parsing into stones, pounds, total pounds and source-implied kilograms;
- observed range of 96–179 source-implied pounds;
- independent Python and SQLite agreement;
- unsupported future values remaining unresolved;
- metric jurisdictions also represented in source stones-and-pounds notation;
- exact official metric declarations requiring later runner-level enrichment.

### Notebook 08 — Starting price parsing

**Status:** complete; notebook validation and clean-kernel Run All passed

Established:

- complete text storage coverage across all runner records;
- 843 distinct raw `sp` values;
- reproducible fraction parsing for 1,842,187 runner records;
- 9,097 explicit empty strings;
- one standalone favourite marker without a numeric value;
- zero unsupported current notation structures;
- 77,468 valid fractions not stored in lowest terms;
- textual even-money notation and terminal `F`, `J` and `C` markers;
- arithmetic representation separate from market semantics;
- possible fixed-odds, tote, pari-mutuel, winner-only and selective-finisher meanings;
- five race-level coverage patterns;
- geographical concentration of selective coverage;
- requirement to retain race-level coverage and wagering applicability context;
- external verification of the standalone Almendares `F` record;
- no justification for globally comparable implied probabilities;
- no final target schema designed.

### Notebook 09 — Course jurisdiction, racing authority and betting-market context

**Status:** complete; independent validation and clean-kernel Run All passed

Established:

- candidate jurisdiction for all 189,043 provisional races;
- 36 candidate jurisdictions;
- 395 jurisdiction-qualified candidate venue/configuration identities;
- 135 multi-form candidate identities with no same-date collisions;
- reusable course and jurisdiction mapping in `src/inside_rails/course_jurisdiction.py`;
- independent validation in `scripts/validate_course_jurisdiction.py`;
- Great Britain requiring racing-code context beneath one principal regulator;
- Ireland requiring racing-code and historical-period context;
- separation of the 2015–2017 and 2018-onward Irish regulatory periods;
- France Galop as the principal authority context for the French worked example;
- 23 French AQPS races labelled `NH Flat` by the source;
- the French AQPS native-code interpretation remaining unresolved rather than overwritten;
- source, structural-derivation and research-interpretation layers remaining distinct;
- detailed jurisdiction research deferred until a country-specific or analytical study requires it;
- worldwide regulatory research not being a prerequisite for core reconstruction;
- no final target schema designed.

Required before reconstruction:

- preserve source `type` exactly as supplied;
- store candidate jurisdiction separately;
- preserve raw `sp` while keeping market interpretation separate.

Deferred research enrichment:

- native racing-code mappings;
- authority and rules records with effective periods;
- jurisdiction-specific wagering context;
- unresolved interpretation questions and later resolutions.

## Remaining source-field studies

The next stage is to inventory and triage every source field that has not yet received a bounded study.

Likely later studies may include:

- prize and currency parsing;
- race-time and temporal semantics;
- runner number, declared runners and field-size semantics;
- beaten-distance semantics where further work is required;
- ratings semantics and availability;
- horse, trainer, jockey and owner identity risks;
- comments and embedded source information;
- headgear and other compact categorical fields;
- coupled-entry interpretation where justified.

The exact sequence will be set by Notebook 10 rather than assumed in advance.

### Notebook 10 — Remaining source-field inventory and triage

**Status:** next

Bounded purpose:

- list every source column;
- mark fields already investigated;
- identify fields that can be preserved without additional semantic study;
- identify fields requiring a dedicated profiling notebook;
- identify fields requiring later jurisdiction-specific research;
- establish the remaining notebook sequence.

Notebook 10 is a triage checkpoint, not a combined analysis of every remaining field.

## Phase 3 — Entity and key design

Notebook 03 established candidate source-record matching rules, but permanent entity and key design remains deferred.

Questions still to resolve include:

- stability of descriptive race fields across replacement snapshots;
- permanent representation of jurisdiction-qualified courses;
- entity-resolution requirements for horse and participant names;
- versioning of amended or repeated source records;
- coupled-entry representation;
- staging surrogate identifiers and reconciliation controls.

Outputs:

- candidate entity model;
- tested business-key analysis;
- lineage and source-record strategy;
- reconciliation rules.

This phase begins only after the remaining source-field studies have been completed or explicitly deferred.

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

Create Notebook 10:

> Remaining source-field inventory and triage

The notebook should inventory all 37 source columns, link completed fields to their existing notebook evidence, classify the remaining fields by semantic and reconstruction risk, and define the bounded sequence of later field studies.

Do not begin conceptual or physical staging-schema design until this triage and the resulting required field studies are complete.
