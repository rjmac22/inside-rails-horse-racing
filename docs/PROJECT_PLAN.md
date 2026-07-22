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

Current notebook sequence, refined by Notebooks 02–06:

1. course, jurisdiction and surface mapping — complete;
2. finishing position and non-finish outcomes — complete;
3. distance parsing — analytical reconciliation complete; clean-kernel Run All pending;
4. carried-weight parsing;
5. starting-price parsing;
6. prize and currency parsing;
7. race-time parsing;
8. ratings semantics and availability;
9. horse, trainer, jockey and owner identity risks;
10. coupled-entry interpretation where justified.

Each study should produce tested parsing or mapping utilities only when the evidence supports them.

### Notebook 04 — Course, jurisdiction and surface mapping

**Status:** complete

Established:

- candidate jurisdiction for all 189,043 provisional races;
- 528 raw course values and 395 jurisdiction-qualified candidate venue/configuration identities;
- 135 candidate identities represented by multiple raw source forms;
- no same-date collisions among those multiple raw forms;
- direct all-weather evidence for 33,023 races from explicit `(AW)` course markers;
- 156,020 races whose surface remains unresolved from the source alone;
- eight explicit NH Flat/type conflicts requiring later validation;
- no derivation of canonical surface from race-name wording.

### Notebook 05 — Finishing position and non-finish outcomes

**Status:** complete; clean-kernel Run All passed

Established:

- complete candidate result representation for all 1,851,285 source runner rows;
- 1,756,666 positive numeric finishing-position rows;
- 94,611 textual-position rows using 11 validated source codes;
- one-to-one semantic mappings for `BD`, `CO`, `DSQ`, `F`, `LFT`, `PU`, `REF`, `RO`, `RR`, `SU` and `UR`;
- 619 `DSQ` rows retaining numeric `btn` and `ovr_btn` values;
- 3,006 supported candidate dead-heat race-position groups covering 6,020 runner records;
- eight unresolved numeric `pos = 0` rows;
- ten numeric positions above `ran`;
- five incomplete provisional race extracts containing 32 observed runner rows;
- two duplicated-position rows with conflicting cumulative distances;
- one externally verified Morphettville source anomaly retained as a separate audit record;
- evidence that amended official positions can coexist with beaten distances anchored to the original on-course order;
- no universal exact-addition rule for `btn` and `ovr_btn`;
- raw and candidate result attributes must remain separate;
- no final target schema was designed.

Candidate result attributes supported:

- positive numeric finishing position;
- raw textual outcome code;
- mapped candidate outcome and broad result category;
- candidate result representation;
- candidate dead-heat flag;
- numeric-distance-availability flag;
- separate runner-level and race-level validation flags.

### Notebook 06 — Race distance parsing

**Status:** analytical reconciliation complete; independent validation passed; clean-kernel Run All pending

Established:

- complete non-blank text `dist` coverage across all 1,851,285 runner records;
- one internally consistent raw distance per provisional race;
- 63 exact raw distance values covering all 189,043 provisional races;
- one observed miles-and-furlongs notation family with optional half-furlongs represented by `½`;
- complete parsing of all current source races;
- exact integer source-implied yards and deterministic source-implied metres for every provisional race;
- a conservative validated-domain parser that leaves unseen values unresolved;
- independent validation across all 189,043 provisional races;
- evidence that source-implied distances are not necessarily exact official scheduled distances for metric jurisdictions;
- external examples of official 1,600-metre races represented by the source as `1m`;
- separation of raw source distance, source-implied conversions and later official-distance enrichment;
- initial analytical priority for UK and Irish racing while international official distances remain a deferred enrichment workstream.

Candidate distance attributes supported:

- exact raw `dist`;
- parsed miles;
- parsed whole furlongs;
- half-furlong indicator;
- total furlongs;
- source-implied yards;
- source-implied metres;
- parse status;
- official-distance verification status;
- separately enriched official distance and original unit when available.

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

Run Notebook 06 from a clean kernel and confirm that Restart and Run All completes without error.

After that validation is recorded, begin Notebook 07 as a bounded study of carried-weight parsing.

Notebook 07 should determine:

- how the source `wgt` field represents stones, pounds and any jurisdiction-specific alternatives;
- which SQLite storage classes, missing values and sentinels occur;
- whether weight values are consistent within their runner context;
- which values can be parsed reproducibly without concealing source ambiguity;
- whether candidate total pounds and kilograms can be justified;
- which raw, parsed, source-implied and validation attributes later staging work must preserve.

The study must remain observational and must not begin final target-schema design.
