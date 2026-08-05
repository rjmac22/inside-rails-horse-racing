# Phase 3 Ratings and Performance Measures Design

## Status

Accepted conceptual design for Phase 3 entity and key work.

This document defines the governed identity, evidence, timing, revision, and comparability model for ratings and performance measures.

It deliberately does **not** define physical tables, SQL, indexes, migrations, parsers, or ingestion code.

Field-specific implementation must wait for a dedicated audit of the available rating and performance-measure columns, their observed values, and their documented source semantics.

---

## 1. Purpose

A rating can look like a simple numeric property of a horse while actually being an assessment produced:

- by a particular authority, publisher, analyst, or model;
- under a particular rating system;
- on a particular scale;
- using information available at a particular time;
- for a particular code, jurisdiction, surface, race type, or analytical purpose;
- before or after a particular race;
- under a particular methodology version;
- and sometimes subject to later revision.

The same horse can therefore have several valid but non-equivalent ratings at the same time.

A rating is not an intrinsic permanent property of a horse, runner, race, jockey, trainer, owner, course, or recurring race series.

The central rule is:

> A rating is a system-specific, time-specific assessment, not an intrinsic numeric property of the horse.

---

## 2. Core conceptual separation

The model must keep the following concepts separate.

### 2.1 Raw rating assertion

The exact rating or performance-measure value supplied by a source record.

This is immutable supplier evidence.

It may contain:

- an integer;
- a decimal;
- a signed value;
- text or symbols;
- a blank or null;
- a provisional marker;
- an official or unofficial marker;
- a value whose system or meaning is unresolved;
- a source-normalised representation of another published measure.

The raw assertion must remain available even after parsing, interpretation, correction, or external reconciliation.

### 2.2 Governed rating observation

A project interpretation that a defined rating value was assigned to a defined subject under a defined rating system and temporal context.

A governed rating observation should be able to carry:

- the linked subject;
- the linked source evidence;
- rating category;
- rating system;
- publisher or authority;
- numeric value where valid;
- original text;
- scale definition or scale version;
- effective date or time;
- publication date or time where known;
- information cutoff where known;
- pre-race or post-race status;
- provisional, final, revised, or superseded status;
- methodology version where known;
- interpretation method;
- evidence status;
- confidence or review status;
- governance release.

### 2.3 Rating system

A named framework under which ratings are produced and interpreted.

A rating system is not identified merely by a column name or numeric range.

It may require:

- system name;
- publisher or governing authority;
- intended purpose;
- subject type;
- scale direction;
- scale range or usual range;
- unit interpretation;
- code, jurisdiction, surface, or discipline scope;
- methodology version;
- effective dates;
- publication and revision practices;
- comparability limitations.

### 2.4 Rating revision state

A rating may be revised after initial publication.

The project must represent revisions as later governed states rather than overwriting earlier observations.

A revision may reflect:

- correction of a source error;
- re-handicapping;
- reassessment after later form;
- methodology change;
- retrospective recalculation;
- provisional-to-final transition;
- changed jurisdictional authority decision;
- project correction of an earlier interpretation.

### 2.5 Derived performance measure

A calculated output produced by the project or another analytical system.

Examples include:

- project speed figures;
- pace-adjusted ratings;
- class-adjusted performance measures;
- standardised ratings;
- percentile ranks;
- rolling form scores;
- model probabilities;
- residual performance measures;
- transformed official marks;
- composite ratings.

Derived measures are analytical outputs, not original source evidence.

---

## 3. Relationship to existing Phase 3 entities

### 3.1 Horse identity

Some ratings describe a horse at a point in time independently of one specific race.

Examples may include:

- an official handicap mark effective before a race;
- a published current rating;
- a project rolling-form rating;
- a current world ranking assessment.

Such ratings may attach to a governed horse identity or provisional horse occurrence only where the identity evidence supports that link.

A raw horse label alone must not establish durable rating continuity across records.

### 3.2 Runner record

Many rating observations belong to a runner in a specific race context.

Examples include:

- the mark carried into that race;
- a source-displayed pre-race rating;
- a post-race performance figure;
- a speed figure earned in that race;
- a project model input or output for that runner.

A runner-level rating observation must retain its independent technical identity because one runner may have multiple ratings from different systems, publishers, stages, or revisions.

### 3.3 Source race occurrence

Post-race performance measures must be scoped to the race occurrence in which the performance happened.

Pre-race assessments may also be linked to the race occurrence where they were displayed or used.

Two equal rating values in different races are not the same observation.

### 3.4 Race result state

Post-race performance measures may depend on the accepted result state.

A later disqualification, amended placing, corrected distance, or changed result may affect a derived performance figure without changing the immutable original source assertion.

Every result-dependent rating should identify the result state or result evidence used where material.

### 3.5 Race conditions and course configuration

A rating may depend on:

- race code;
- surface;
- distance;
- going;
- course configuration;
- class or grade;
- handicap conditions;
- weight carried;
- pace or sectional information.

These dependencies do not make those facts part of rating identity, but they may be required to interpret or reproduce the rating.

### 3.6 Recurring race series

Ratings attach to horses, runners, or performances in individual editions, not permanently to a recurring race series.

Series-level rating analysis must aggregate edition-level observations under explicit comparability rules.

---

## 4. Raw rating preservation

Every raw rating value must be retained exactly as supplied.

Preservation includes:

- original characters;
- punctuation;
- spacing;
- signs;
- decimal precision;
- suffixes;
- provisional or official markers;
- blanks and nulls;
- malformed or unparseable values.

Parsing must never replace the raw value.

A successfully parsed rating is a governed interpretation of the raw assertion, not a corrected version of the source text.

---

## 5. Rating observation identity

A governed rating observation requires its own project-wide technical identifier.

It must not use the numeric rating value as an identifier.

It must not assume one rating per horse or one rating per runner.

A subject may legitimately have multiple observations because of:

- different systems;
- different publishers;
- official and private ratings;
- different publication times;
- pre-race and post-race stages;
- provisional and final states;
- revisions;
- different methodology versions;
- different jurisdictions or racing codes;
- multiple source deliveries;
- project-derived measures.

The rating observation identity must therefore remain independent of horse, runner, race, and source-record identity.

---

## 6. Rating subject must be explicit

A rating must identify what is being assessed.

Potential subjects include:

- horse at a defined point in time;
- runner before a particular race;
- performance by a runner in a particular race;
- jockey;
- trainer;
- sire or dam;
- race strength;
- field strength;
- course or configuration;
- stable or ownership entity;
- betting market;
- model prediction.

The initial implementation should support only subject types established by evidence in the available source and by approved analytical outputs.

A number must not be attached to a horse merely because the source field occurs on a runner row.

---

## 7. Rating category must be explicit

Conceptually distinct categories include:

- official handicap mark;
- official international rating;
- private handicap rating;
- pre-race form rating;
- post-race performance rating;
- speed figure;
- pace figure;
- sectional rating;
- class or race-strength measure;
- projected rating;
- model score;
- project-derived composite;
- unresolved numeric measure.

The project must not treat these categories as interchangeable.

A rating category should be assigned only where source documentation, field investigation, or external evidence supports it.

---

## 8. Pre-race and post-race separation

Pre-race assessments and post-race performance measures are different facts.

### 8.1 Pre-race rating

A pre-race rating reflects information available before the race or at a defined pre-race cutoff.

Examples may include:

- official handicap mark carried into the race;
- current published rating;
- private form rating;
- tissue or model score;
- project prediction generated before the race.

### 8.2 Post-race performance measure

A post-race measure evaluates the performance after the race using some or all of:

- finishing outcome;
- beaten distances;
- time;
- pace;
- weight;
- going;
- course configuration;
- field strength;
- later interpretation.

### 8.3 Anti-leakage rule

A pre-race study must not use a rating that was calculated or revised after the race unless it is explicitly conducting retrospective analysis.

The information cutoff must therefore be part of the analytical admission rule.

The central temporal distinction is:

> A rating available before a race and a rating assigned after that race may share a number but are not the same evidence.

---

## 9. Official handicap marks

Official handicap marks require separate treatment from private or analytical ratings.

Where supported by evidence, an official mark observation should retain:

- governing authority;
- jurisdiction;
- racing code or discipline;
- effective date;
- publication date where known;
- mark value;
- whether the mark was carried into a specific race;
- whether the horse raced from out of the handicap;
- any applicable ceiling, floor, band, or eligibility context;
- provisional, revised, or final status;
- source evidence;
- governance release.

An official mark is not automatically comparable across:

- jurisdictions;
- Flat and Jump racing;
- historical periods;
- different official scales;
- codes with different handicapping practices.

A mark displayed on a race record may represent the mark applicable to that race rather than a timeless current mark.

---

## 10. Private ratings and publisher identity

Private ratings must retain their publisher or producing system.

A private rating should not be labelled merely as `rating` where the publisher or system is known.

Relevant context may include:

- publisher;
- product;
- edition or release;
- methodology version;
- publication date;
- intended use;
- rating category;
- scale definition;
- revision practice;
- jurisdiction and code coverage.

Two publishers may both use a 0–150-looking scale without their numbers being equivalent.

---

## 11. Speed and performance figures

Speed figures and performance figures require an explicit system definition.

Potential dependencies include:

- race time;
- sectional times;
- distance;
- course configuration;
- surface;
- going allowance;
- wind or weather adjustment;
- weight carried;
- age or sex allowances;
- pace adjustment;
- track variant;
- class or par time;
- treatment of non-completions;
- methodology version.

A source-displayed speed figure must not be reverse-engineered into a different system without evidence.

A project-derived figure must preserve:

- input dataset version;
- code or method version;
- parameters;
- admission rules;
- dependencies;
- calculation timestamp;
- governance release.

---

## 12. Rating system identity and versioning

A rating system requires independent governed identity.

The system identity should remain separate from a particular rating observation.

A system may have multiple methodology versions over time.

A methodology change may alter:

- scale calibration;
- treatment of weight;
- going adjustments;
- time standards;
- age allowances;
- field-strength calculation;
- retrospective revision policy;
- jurisdiction coverage;
- rounding;
- publication timing.

Where a material methodology change occurs, the effective-dated version must be preserved.

The project must not assume one named rating product has used an unchanged methodology throughout the full 2015–2026 source period.

---

## 13. Scale definition

A numeric rating is interpretable only within its scale.

A governed scale definition may require:

- direction, such as higher-is-better or lower-is-better;
- numeric type;
- permitted or usual range;
- unit meaning where one exists;
- zero point;
- interval interpretation;
- whether differences have stable meaning;
- rounding convention;
- missing-value convention;
- caps or floors;
- population scope;
- calibration period;
- methodology version.

The project must not assume that a ten-point difference has the same meaning across systems.

It must also not assume that rating values are interval-scaled merely because they are numeric.

---

## 14. Effective time, publication time, and information cutoff

The system must distinguish where supported:

- effective date or time;
- publication date or time;
- source capture date or time;
- race date;
- information cutoff;
- revision date;
- project interpretation date.

These are not interchangeable.

An official mark may be published before it becomes effective.

A post-race rating may be calculated shortly after the race and revised weeks later.

A historical database delivery date does not establish when a rating first became available to bettors or analysts.

If the exact timing is unknown, the uncertainty must remain explicit.

---

## 15. Multiple ratings for one subject

Multiple valid ratings may coexist for the same subject and effective date.

Examples include:

- an official mark and a private rating;
- two private publishers;
- pre-race and post-race values;
- provisional and final values;
- Flat and Jump ratings;
- turf and all-weather ratings;
- domestic and international assessments;
- raw source and project-derived measures.

The model must not collapse these into one canonical number unless a specific governed selection rule is created for a defined analytical purpose.

A project display may nominate a preferred rating for convenience, but that preference is a derived presentation decision, not identity truth.

---

## 16. Missingness and unresolved values

The system must distinguish at least:

- valid rating;
- true source null;
- blank source text;
- rating not published;
- horse not eligible for that system;
- rating system not applicable;
- source value malformed;
- rating withheld;
- rating not yet available;
- rating category unresolved;
- rating system unresolved;
- scale unresolved;
- effective date unresolved.

A blank or zero must not automatically mean unrated.

Zero may be a valid value in some systems and a sentinel in others.

A dedicated field study must establish the meaning before zero is interpreted.

---

## 17. Revisions, corrections, and supersession

Later evidence may establish that a rating was:

- provisional;
- revised by the publisher;
- corrected for a data error;
- recalculated under a later method;
- attached to the wrong horse or runner;
- mislabelled as pre-race or post-race;
- sourced from the wrong rating system;
- parsed incorrectly;
- retrospectively reassessed.

The original source assertion must remain immutable.

A revision or correction should be represented through governed evidence with:

- prior observation;
- later observation;
- relationship type;
- reason;
- evidence reference;
- publication or revision date where known;
- decision status;
- governance release.

The design should support append-only interpretive history rather than silent replacement.

---

## 18. Cross-system comparability

Two ratings must not be compared numerically merely because both are numbers.

Direct comparison requires evidence that the systems are compatible for the intended use.

Compatibility may depend on:

- same publisher and system;
- same methodology version;
- same scale;
- same code or discipline;
- same jurisdiction;
- same surface or race type;
- same temporal regime;
- same subject type;
- same pre-race or post-race stage;
- comparable population and calibration.

Possible governed compatibility outcomes include:

- directly comparable;
- comparable after documented transformation;
- comparable only within restricted scope;
- directionally comparable but not numerically equivalent;
- incompatible;
- unresolved.

A crosswalk is an analytical model, not an inherent identity relationship.

---

## 19. Transformations and standardisation

A project may transform ratings for analysis, but the transformed value must remain separate from the original rating observation.

Potential transformations include:

- rescaling;
- centring;
- z-scores;
- percentile ranks;
- within-season standardisation;
- age-adjustment;
- code-specific calibration;
- mapping between documented scales;
- monotonic transformations;
- model-based crosswalks.

Every transformation must identify:

- input rating system and version;
- admitted observations;
- reference population;
- date range;
- formula or model;
- parameters;
- output scale;
- validation evidence;
- version;
- governance release.

A transformed rating must not be presented as though it were the publisher's original value.

---

## 20. Project-derived ratings

Project-derived ratings require full analytical provenance.

At minimum, a reproducible project rating should identify:

- subject;
- calculation method;
- input source versions;
- governance releases;
- feature definitions;
- result state used;
- course and race-condition interpretations;
- treatment of missing data;
- training or calibration period where applicable;
- parameters or fitted model version;
- calculation timestamp;
- release status;
- limitations.

A project-derived rating may be useful without being comparable to an official or private published rating.

The project must not imply official status.

---

## 21. Data leakage and hindsight control

Ratings are especially vulnerable to hindsight leakage.

A predictive study must define the latest information time permitted for every rating input.

Potential leakage includes:

- using a post-race figure as a pre-race predictor;
- using a revised official mark published after the target race;
- using retrospective ratings recalculated with later form;
- using a source snapshot compiled after the event without preserving original availability;
- selecting a preferred rating based on the known result;
- normalising against a population containing future observations.

Where contemporaneous availability cannot be established, the rating may still support retrospective descriptive analysis but must not be represented as a live predictive input.

---

## 22. Jurisdiction, code, and discipline scope

Rating interpretation may require explicit scope for:

- jurisdiction;
- governing authority;
- Flat, Hurdle, Chase, National Hunt Flat, harness, or other code;
- turf, dirt, synthetic, or mixed surface;
- age group;
- sex restriction;
- handicap or non-handicap context;
- domestic or international comparison.

A horse may have separate valid ratings across codes or surfaces.

The project must not merge them merely because they apply to the same horse.

Jurisdiction-specific investigation may later add richer details without changing the identity of existing raw assertions.

---

## 23. Historical regimes and methodology changes

Rating systems and official handicapping practices may change during the source period.

The design must support effective-dated regimes where evidence establishes changes in:

- methodology;
- scale calibration;
- publication practice;
- eligibility;
- code coverage;
- international coordination;
- rounding;
- reassessment policy;
- timing of revisions.

The database should store only evidenced regime details required by current investigations.

It should remain extensible rather than attempting to model every historical rating rule in advance.

The governing principle is:

> Store what is evidenced now, preserve unresolved meaning, and extend the interpretation only when a focused investigation justifies it.

---

## 24. Source and external evidence

A rating observation may be supported by:

- immutable source record evidence;
- official authority publication;
- publisher documentation;
- archived racecard or result publication;
- methodology document;
- project calculation output;
- correction notice;
- manual verification with provenance.

The supplier of the database may differ from the publisher of the rating.

The model must allow the source provider, rating publisher, and governing authority to remain distinct.

External evidence may supplement or correct source interpretation without overwriting the raw source value.

---

## 25. Reconciliation across source versions and providers

Cross-version or cross-provider matching must be explicit.

Two rating observations should not be treated as duplicates merely because they share:

- horse label;
- race;
- numeric value;
- date;
- apparent rating category.

Potential reconciliation evidence may include:

- governed horse or runner identity;
- rating system;
- publisher;
- category;
- effective date;
- publication date;
- methodology version;
- raw value;
- source lineage;
- revision notice.

The relationship may be:

- same published observation represented twice;
- distinct observations with equal values;
- revision or supersession;
- conflicting evidence;
- unresolved.

No cross-source equivalence should be assumed at ingestion.

---

## 26. Validation requirements

Future implementation should support validation of at least the following invariants.

### 26.1 Evidence preservation

- Every governed rating interpretation links to immutable source evidence or documented external/project evidence.
- Raw rating text remains unchanged.
- A failed parse does not destroy or replace the raw value.

### 26.2 Observation integrity

- Every governed observation has one defined subject.
- Every observation has a rating category or explicit unresolved status.
- Every observation has a rating system or explicit unresolved status.
- Valid numeric values satisfy the known scale constraints.
- Invalid, blank, or unresolved values are not stored as valid ratings.

### 26.3 Temporal integrity

- Pre-race and post-race states are not silently mixed.
- Exact timestamps include timezone or explicit unresolved timezone status where timestamps are used.
- Revision dates do not overwrite original publication or effective dates.
- Predictive studies respect the declared information cutoff.

### 26.4 System integrity

- Methodology versions are effective-dated where known.
- Scale direction and interpretation remain attached to the system version.
- Official and private ratings remain distinguishable.
- Project-derived measures remain distinguishable from published ratings.

### 26.5 Comparability integrity

- Cross-system comparison requires an explicit compatibility decision or transformation.
- A transformation identifies its input and output systems.
- Ratings from incompatible codes, jurisdictions, stages, or versions are not silently pooled.

### 26.6 Version integrity

- Interpretive changes create a new governed state or release.
- Prior accepted interpretations remain traceable.
- Source-version and rating-system lineage are retained.

---

## 27. Admission rules for analytical studies

Every rating study must state its admission rules.

At minimum, it should define:

- source version or versions;
- governance release;
- jurisdiction and date range;
- race universe;
- subject type;
- rating category;
- rating system and methodology version;
- publisher or authority;
- pre-race or post-race status;
- effective-time or publication-time rule;
- handling of revisions;
- handling of missing and malformed values;
- scale and direction;
- comparability or transformation rule;
- treatment of multiple ratings per subject;
- result state where relevant;
- information cutoff for predictive work.

A study must not describe an unidentified numeric field as an official mark, speed figure, or performance rating unless that semantic interpretation has been established.

---

## 28. Required disclosures for common analyses

### 28.1 Official-rating performance

Disclose:

- governing authority;
- code and jurisdiction;
- effective date rule;
- whether the mark was the one carried into the race;
- treatment of out-of-handicap runners;
- handling of later mark revisions;
- race and result admission rules.

### 28.2 Private-rating comparison

Disclose:

- publisher and system;
- methodology version where known;
- publication timing;
- scale direction;
- multiple-rating selection rule;
- compatibility limitations.

### 28.3 Speed-figure analysis

Disclose:

- producing system;
- time and distance inputs;
- going or track-variant treatment;
- weight and pace adjustments;
- course-configuration scope;
- post-race revision policy;
- missing-time treatment.

### 28.4 Predictive modelling

Disclose:

- information cutoff;
- whether each rating was contemporaneously available;
- handling of retrospective revisions;
- transformation and normalisation;
- leakage controls;
- training and validation periods;
- governance and model versions.

### 28.5 Cross-system or cross-jurisdiction comparison

Disclose:

- systems compared;
- evidence for compatibility;
- transformation or crosswalk;
- calibration population;
- effective periods;
- remaining limitations.

---

## 29. Known limitations before implementation

The current Phase 3 design does not yet establish:

- which Source Version 1 fields contain ratings or performance measures;
- the precise semantics of those fields;
- whether values are pre-race or post-race;
- whether values are official, private, or source-derived;
- the publisher or authority;
- the applicable scale;
- the methodology version;
- the effective or publication timing;
- whether values are revised retrospectively;
- whether zero or blank values have special meanings;
- whether systems vary by jurisdiction, code, or period;
- whether source-presented values were transformed before delivery.

These are field-governance questions for dedicated source audits and notebooks.

The model intentionally leaves them unresolved rather than inventing certainty.

---

## 30. Deferred extensions

The following are valid later extensions but are not required for the first implementation:

- detailed official handicapping histories;
- international rating reconciliation;
- jurisdiction-specific scale crosswalks;
- high-frequency rating publication histories;
- publisher-specific methodology archives;
- sectional and pace rating systems;
- Bayesian rating uncertainty;
- confidence intervals for model-derived ratings;
- latent-class or state-space ratings;
- ratings for jockeys, trainers, sires, and courses;
- real-time model ratings;
- proprietary commercial rating feeds;
- user-defined rating systems;
- formal rating-system ontologies.

These should be added as governed extensions when a focused investigation or product requirement justifies them.

---

## 31. Implementation implications for later schema work

Without prescribing SQL, the eventual schema will need to support independent identities or governed records for:

- raw rating assertion;
- rating subject;
- rating category;
- rating system;
- rating-system methodology version;
- scale definition;
- rating observation;
- rating revision or supersession;
- comparability decision;
- transformation or crosswalk;
- project-derived rating release;
- governance release.

The schema must support multiple ratings per horse, runner, race, system, and date.

It must also support unresolved semantics without fabricating a false publisher, system, category, scale, or numeric interpretation.

---

## 32. Decision summary

The accepted Phase 3 ratings and performance-measures design is:

1. Preserve every raw rating value exactly as supplied.
2. Treat ratings as system-specific, time-specific observations.
3. Give rating observations independent technical identity.
4. Identify the rating subject explicitly.
5. Keep official handicap marks, private ratings, speed figures, post-race figures, and project-derived measures distinct.
6. Keep pre-race and post-race ratings distinct.
7. Preserve publisher, authority, system, scale, methodology version, and effective timing where evidenced.
8. Allow multiple valid ratings for the same subject and date.
9. Preserve revisions and corrections append-only.
10. Do not compare numeric ratings across systems without an explicit compatibility decision or governed transformation.
11. Keep transformed and standardised values separate from original observations.
12. Require full provenance for project-derived ratings.
13. Enforce information cutoffs and leakage controls in predictive analysis.
14. Retain missing, malformed, inapplicable, withheld, and unresolved states separately.
15. Support effective-dated jurisdictional and methodology regimes only where investigation establishes them.
16. Defer field-specific implementation until source audits establish actual rating-field semantics.

---

## 33. Boundary with the next design topics

This document resolves the conceptual identity and governance boundary for ratings and performance measures.

It does not yet resolve:

- carried weight, allowances, penalties, and claims;
- draw, stalls, and starting position;
- equipment, headgear, medication, and declarations;
- sectional timing and in-race position observations;
- weather observations and going reconciliation;
- physical table design.

Those remain separate bounded design questions.
