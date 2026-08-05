# Phase 3 Equipment and Medication Assertions Design

## Status

Accepted conceptual design for Phase 3 entity and key work.

This document defines the governed identity and evidence model for race-specific equipment, aids, medication, treatment, and related declarations.

It deliberately does **not** define physical tables, SQL, indexes, migrations, ingestion code, or a complete international terminology dictionary.

Field-specific implementation must wait for a dedicated source audit of the available equipment and medication columns, abbreviations, combinations, blanks, and jurisdictional meanings.

---

## 1. Purpose

Equipment and medication fields are easy to flatten into permanent horse attributes even though they normally describe a runner in one particular race under one particular rules regime.

A source value may represent:

- equipment declared before the race;
- equipment confirmed as used;
- a change from the horse's previous run;
- medication permitted under local rules;
- a historical abbreviation whose exact meaning is uncertain;
- a combination of several items;
- a source-presented value derived from another provider;
- a blank whose meaning is unknown.

The design must preserve the original evidence while allowing governed interpretations to be added later without overwriting the source or inventing certainty.

The central rule is:

> Equipment and medication are race-specific, effective-dated assertions, not permanent attributes of the horse.

---

## 2. Core conceptual separation

The model must keep the following concepts separate.

### 2.1 Raw equipment or medication assertion

The exact source value attached to an immutable source record.

This may include:

- one abbreviation;
- several concatenated abbreviations;
- punctuation or spacing;
- first-time markers;
- removed, reapplied, or retained markers;
- medication codes;
- source-specific terminology;
- blank text;
- null values;
- malformed or unfamiliar text.

The raw assertion is immutable supplier evidence.

### 2.2 Governed runner-use assertion

A project interpretation that a particular runner was declared, expected, confirmed, reported, or subsequently corrected as using one or more defined items in one race.

A governed assertion may carry:

- runner record;
- source race occurrence;
- governed item or unresolved item label;
- assertion stage;
- use status;
- change status;
- jurisdiction and rules regime where known;
- interpretation method;
- evidence status;
- confidence or review status;
- governance release.

### 2.3 Equipment or medication item

A governed concept representing one item or treatment category only where the source semantics and external evidence support that interpretation.

Examples might eventually include:

- blinkers;
- visor;
- cheekpieces;
- hood;
- tongue-tie;
- eye shield;
- sheepskin noseband;
- pacifiers;
- approved race-day medication categories in jurisdictions where those are relevant.

The conceptual model must not imply that every example occurs in Source Version 1.

### 2.4 Composite declaration

A source assertion may describe a combination of items.

The combination must be preserved as a source-level whole even where it is also decomposed into governed constituent items.

For example, a source label interpreted as blinkers plus tongue-tie must not be flattened into one invented equipment category, and the original combined text must remain available.

### 2.5 Derived equipment history

Statements such as:

- first time in blinkers;
- reapplied after an interval;
- retained from previous run;
- equipment removed;
- first run without an item

are historical or comparative interpretations.

They require an ordered admitted runner history and cannot be inferred safely from one isolated source row unless the source explicitly asserts the change.

Derived history is analytical output, not the immutable source assertion.

---

## 3. Relationship to existing Phase 3 entities

### 3.1 Runner record

Equipment and medication normally attach to the runner record for one race.

This matters because:

- the same horse may use different equipment in different races;
- a declaration may change between entry and race time;
- a horse may be withdrawn after equipment was declared;
- equipment evidence belongs to the participation context rather than permanent horse identity.

### 3.2 Provisional horse occurrence

A provisional horse occurrence may support chronological history across runner records, but it must not store equipment as a permanent attribute.

A later horse-identity correction must not alter the immutable runner-level assertion.

Historical change derivations should identify the horse-governance release used.

### 3.3 Source record

Every raw assertion remains linked to the immutable source record that supplied it.

The presence of text on a source row does not by itself establish:

- that the equipment was actually used;
- that the value was final;
- that every abbreviation has been interpreted correctly;
- that a blank means no equipment;
- that medication terminology matches another jurisdiction.

### 3.4 Source race occurrence and result state

Equipment declarations relate to a race occurrence, while later result or steward evidence may confirm or correct actual use.

A result correction must not overwrite the historical declaration.

A runner who becomes a non-runner may retain a valid pre-race declaration without a confirmed race-use assertion.

### 3.5 Participant identity

Some equipment changes may be reported alongside trainer or jockey information, but equipment identity must not be embedded in participant identity.

The horse, runner, trainer, jockey, equipment item, and assertion are separate concepts.

---

## 4. Raw value preservation

Every raw equipment or medication value must be retained exactly as supplied.

Preservation includes:

- original characters;
- case;
- punctuation;
- whitespace;
- source ordering of combined items;
- suffixes and prefixes;
- first-time or change markers;
- blanks and nulls;
- malformed text;
- unknown abbreviations.

Normalisation, tokenisation, decomposition, and correction must never replace the raw value.

A governed interpretation is an additional evidence layer.

---

## 5. Assertion identity

Each governed equipment or medication assertion requires its own project-wide technical identity.

It must not use:

- raw text;
- item code;
- horse name;
- runner number;
- source rowid alone

as permanent identity.

One source record may support:

- one composite raw assertion;
- several constituent governed item assertions;
- one or more unresolved tokens;
- a later correction or superseding interpretation.

One runner may therefore have several valid governed assertions for the same race.

---

## 6. Assertion stage must be explicit

The model must distinguish, where evidence supports it:

- entry-stage declaration;
- overnight or final-declaration stage;
- pre-race expected use;
- confirmed use in the race;
- post-race reported use;
- steward-corrected use;
- historical source reconstruction;
- stage unresolved.

A declaration is not automatically proof of actual use.

A source field whose timing is unknown must remain stage-unresolved until a dedicated audit establishes its semantics.

---

## 7. Use status must be explicit

Potential governed statuses include:

- declared to be used;
- confirmed used;
- expected but unconfirmed;
- declared then withdrawn;
- reported not used;
- removed before race;
- source conflict;
- unresolved;
- not applicable.

The initial implementation should support only statuses justified by actual evidence.

A blank source value must not be converted automatically into `not used`.

---

## 8. Equipment identity and classification

An equipment item should have a governed identity only where its meaning is established.

The governed item may carry:

- canonical project label;
- source-specific aliases;
- broad category;
- jurisdictional scope;
- effective dates where terminology changes;
- rules references where available;
- evidence status;
- governance release.

Potential broad categories may include:

- vision restriction or focus aids;
- hearing or noise aids;
- tongue or breathing-related equipment;
- headgear;
- nosebands;
- footwear or traction equipment;
- safety equipment;
- medication or treatment declaration;
- other governed category;
- unresolved category.

These categories are analytical aids and must not replace the specific item identity.

---

## 9. Composite values and tokenisation

A source value may contain several items or modifiers.

The project must preserve both:

1. the exact composite source assertion; and
2. any governed decomposition into constituent items.

Tokenisation must be:

- source-specific;
- versioned;
- deterministic;
- validated against observed values;
- reversible back to the original raw assertion;
- capable of leaving uncertain tokens unresolved.

Punctuation or character position must not be assumed to have universal meaning across providers or jurisdictions.

A failed or partial parse must not discard the original value.

---

## 10. First-time, reapplied, retained, and removed status

Change status is separate from equipment identity.

Potential statuses include:

- first declared use;
- source-marked first time;
- first confirmed use in admitted history;
- retained;
- reapplied;
- removed;
- first run without;
- change status unresolved.

The system must distinguish:

- a source explicitly saying `first time`;
- the project deriving first observed use within incomplete data;
- the project establishing first known career use from sufficiently complete history.

These are not equivalent claims.

A study must disclose which definition it uses.

---

## 11. Absence, blanks, and missingness

The system must distinguish at least:

- explicit source assertion of no equipment;
- blank source text;
- source null;
- field not supplied;
- field not applicable;
- item unresolved;
- parser failure;
- race-stage information unavailable;
- confirmed absence;
- absence not established.

A blank must not automatically mean:

- no equipment;
- unchanged equipment;
- no medication;
- missing runner;
- not applicable.

Those meanings require source-field evidence.

---

## 12. Declared use versus confirmed actual use

Declared equipment and actual use must remain separate where later evidence is available.

Possible evidence sources include:

- declarations;
- racecards;
- official results;
- steward reports;
- veterinary reports;
- source corrections;
- video or image review where appropriate and documented.

The design must support cases where:

- the declaration was correct;
- the item was removed before the start;
- the item was added after initial declaration;
- the source was corrected later;
- sources conflict;
- actual use remains unresolved.

No silent overwrite is permitted.

---

## 13. Medication and treatment semantics

Medication terminology is especially jurisdiction- and date-sensitive.

A value may describe:

- permitted race-day medication;
- an equipment code that resembles a medication code;
- treatment status;
- a regulatory declaration;
- a source conversion from another jurisdiction;
- a historical rule no longer in force.

Medication interpretation should therefore retain, where known:

- race jurisdiction;
- governing authority;
- effective rules period;
- treatment or medication category;
- declaration stage;
- permitted, prohibited, restricted, or unresolved status;
- source terminology;
- interpretation evidence.

The project must not infer clinical details, dosage, diagnosis, or treatment effect unless explicit evidence supports them.

---

## 14. Jurisdiction and effective-dated rules regimes

Equipment and medication rules can change over time.

The model must allow optional governed regimes describing:

- jurisdiction;
- governing authority;
- effective start and end dates;
- terminology and abbreviation meanings;
- declaration requirements;
- permitted or restricted equipment;
- medication rules;
- change-reporting requirements;
- evidence references;
- governance release.

The initial database should store only regimes needed by established evidence and current studies.

It should remain extensible rather than attempting to encode every international historical rule in advance.

---

## 15. Source-specific terminology

The same abbreviation may mean different things across:

- providers;
- products;
- jurisdictions;
- periods;
- racing codes.

Conversely, different abbreviations may represent the same governed item.

Therefore:

- aliases must be source- and context-scoped;
- text normalisation alone does not establish equivalence;
- an abbreviation dictionary must be versioned;
- uncertain mappings remain unresolved;
- cross-provider equivalence requires explicit evidence.

---

## 16. Racing code and configuration context

Some equipment or medication meanings may depend on:

- Flat racing;
- hurdles;
- chases;
- National Hunt Flat racing;
- harness racing;
- other codes;
- local rules or course configuration.

The design must allow context without assuming that one item has identical regulatory meaning across all codes.

---

## 17. Corrections, conflicts, and supersession

Later evidence may establish that a source assertion was:

- misparsed;
- mapped to the wrong item;
- incomplete;
- attached to the wrong runner;
- a declaration rather than confirmed use;
- superseded before the race;
- corrected by an official source;
- inconsistent with another provider.

The original source assertion remains immutable.

A correction should carry:

- prior interpretation;
- corrected interpretation;
- correction type;
- evidence reference;
- decision status;
- confidence or review status;
- effective governance release.

Conflicting evidence may remain unresolved rather than forcing one answer.

---

## 18. Historical sequence and horse-level derivations

Equipment-history studies require an admitted ordered sequence of runner records.

They must identify:

- horse identity or provisional occurrence release;
- race ordering rule;
- treatment of unresolved off-times;
- treatment of foreign and incomplete history;
- source coverage boundaries;
- equipment parser and governance release;
- handling of non-runners;
- whether declarations or confirmed use are analysed.

A first observed use within Source Version 1 is not automatically the horse's first career use.

---

## 19. Non-runners, abandonments, and void races

A runner may have a valid equipment declaration but not participate.

The model must preserve:

- declaration evidence;
- non-runner outcome;
- any later withdrawal-stage correction;
- absence of confirmed race use.

For abandoned or void races, declarations may remain historically valid while performance analysis excludes the race.

---

## 20. Equipment combinations

Analyses may need to distinguish:

- one individual item;
- any item within a category;
- an exact combination;
- a combination plus change status;
- an item added to an existing combination;
- an item removed while others remain.

The model must not collapse an exact combination into a binary `equipment yes/no` attribute unless a study deliberately derives that broader category and states its rules.

---

## 21. Analytical derivations

Potential derived measures include:

- first observed use;
- first confirmed use;
- change since previous admitted run;
- retained-equipment run count;
- runs since removal;
- performance with and without an item;
- performance after adding or removing an item;
- trainer-level equipment patterns;
- jurisdiction-specific medication comparisons.

All are analytical outputs requiring explicit admission rules.

They are not source facts.

---

## 22. Causal interpretation warning

Equipment changes are not randomly assigned.

They may coincide with:

- a decline or improvement in form;
- a change in trip;
- a change in surface or going;
- a trainer switch;
- a layoff;
- a change in class;
- a different jockey;
- a behavioural issue;
- selective reporting.

Therefore observed performance differences must not be presented automatically as the causal effect of equipment or medication.

Studies should distinguish descriptive association from causal inference.

---

## 23. Versioning and governance releases

Interpretations must be reproducible under a named governance release.

A release may define:

- accepted source fields;
- tokenisation rules;
- abbreviation mappings;
- item identities;
- composite decomposition rules;
- assertion-stage mappings;
- change-status rules;
- missingness interpretation;
- known defects;
- source exclusions;
- jurisdiction regimes.

Later releases may improve interpretation without changing the immutable source evidence.

---

## 24. Validation requirements

Future implementation should support validation of at least the following invariants.

### 24.1 Evidence preservation

- Every governed assertion links to immutable source evidence or documented external evidence.
- Raw text remains unchanged.
- Parsing failure does not remove the source value.

### 24.2 Runner scope

- Every race-specific assertion links to one runner record.
- Assertions are not stored as permanent horse attributes.
- A non-runner may retain declarations without confirmed race use.

### 24.3 Item integrity

- Every resolved item maps to one governed item identity.
- Unresolved tokens remain explicit.
- Composite assertions can retain several constituent items.
- Constituent decomposition remains traceable to the original composite assertion.

### 24.4 Stage and status integrity

- Declaration and confirmed-use stages are not silently merged.
- Blank values are not treated as confirmed absence without evidence.
- First-time claims identify whether they are source-marked or project-derived.

### 24.5 Temporal and regime integrity

- Effective-dated rules do not overlap incompatibly without an explicit relationship.
- Jurisdiction-specific interpretations identify their applicable context.
- Historical terminology changes remain traceable.

### 24.6 Version integrity

- Interpretive changes create a new governed state or governance release.
- Prior decisions remain traceable.
- Source-version lineage is retained.

---

## 25. Admission rules for analytical studies

Every equipment or medication study must state:

- source version or versions;
- jurisdiction and date range;
- racing code;
- race and runner universe;
- horse-identity or occurrence release;
- source fields used;
- parser and terminology version;
- whether declarations or confirmed use are analysed;
- handling of blanks and unresolved values;
- handling of non-runners;
- definition of first-time, reapplied, retained, or removed;
- treatment of combinations;
- relevant rules regime;
- governance release.

A study must not call a blank `no equipment` unless that semantic has been established for the field and source context.

---

## 26. Required disclosures for common analyses

### 26.1 First-time equipment performance

Disclose:

- whether first time is source-marked or project-derived;
- completeness of prior runner history;
- treatment of foreign runs and unresolved horse identity;
- item and combination rules;
- declaration versus confirmed-use basis;
- comparator population.

### 26.2 Equipment added or removed

Disclose:

- previous-run ordering rule;
- minimum history requirements;
- treatment of gaps and non-runners;
- whether other equipment in the combination changed simultaneously;
- relevant changes in race class, distance, surface, trainer, and jockey.

### 26.3 Medication comparisons

Disclose:

- jurisdiction;
- effective rules period;
- medication category;
- source terminology;
- whether the data represents declaration, permitted status, treatment, or confirmed administration;
- unresolved and excluded records.

### 26.4 Trainer equipment patterns

Disclose:

- trainer identity release;
- equipment parsing rules;
- minimum runner thresholds;
- repeated horses and clustered observations;
- whether outcomes are descriptive or model-adjusted.

---

## 27. Known limitations before implementation

The current Phase 3 design does not yet establish:

- which Source Version 1 fields contain equipment or medication values;
- the precise semantics of those fields;
- whether values are declarations or confirmed use;
- the full abbreviation dictionary;
- how combinations are encoded;
- whether first-time markers are present;
- whether blanks mean none, unchanged, or unknown;
- whether terminology varies by jurisdiction or period;
- whether medication fields exist independently of equipment fields;
- whether source corrections are present.

These remain field-governance questions for dedicated audits and notebooks.

The model leaves them unresolved rather than inventing certainty.

---

## 28. Deferred extensions

Valid later extensions include:

- detailed equipment taxonomies;
- jurisdiction-specific historical abbreviation dictionaries;
- official declaration feeds;
- steward-confirmed race-use evidence;
- veterinary treatment records where lawfully and appropriately available;
- dosage and timing evidence where explicitly supported;
- image- or video-supported equipment verification;
- richer safety-equipment modelling;
- code-specific equipment regimes;
- causal research designs.

These should be added only when evidence and a focused study require them.

---

## 29. Implementation implications for later schema work

Without prescribing SQL, the eventual schema will need to support independent identities or governed records for:

- raw equipment or medication assertion;
- governed item;
- source-specific alias or token mapping;
- composite assertion;
- constituent item assignment;
- runner-use assertion;
- assertion stage;
- change status;
- rules regime;
- correction or supersession;
- governance release.

The schema must support several items per runner and several interpretations of one raw composite assertion while preserving unresolved meaning.

---

## 30. Decision summary

The accepted Phase 3 equipment and medication design is:

1. Preserve every raw value exactly as supplied.
2. Attach assertions to the runner in one specific race.
3. Keep declarations separate from confirmed actual use.
4. Give governed assertions independent technical identity.
5. Represent individual items only where source semantics support them.
6. Preserve composite source labels alongside any constituent decomposition.
7. Keep first-time, retained, reapplied, and removed status separate from item identity.
8. Distinguish source-marked change claims from project-derived historical claims.
9. Do not interpret blanks as no equipment or no medication without evidence.
10. Treat medication and regulatory terminology as jurisdiction- and date-specific.
11. Use optional effective-dated rules regimes only when required by evidence.
12. Preserve corrections, conflicts, and interpretive history append-only.
13. Leave unfamiliar abbreviations and ambiguous values explicitly unresolved.
14. Require studies to disclose source, stage, item, history, missingness, and governance rules.
15. Treat performance comparisons as descriptive unless a valid causal design supports stronger claims.
16. Defer physical implementation until dedicated field audits establish actual Source Version 1 semantics.

---

## 31. Boundary with the next design topics

This document resolves the conceptual identity and governance boundary for equipment and medication assertions.

It does not yet resolve:

- sectional timing and in-race position observations;
- weather observations and going reconciliation;
- draw, stall, and starting-position context;
- detailed veterinary records;
- physical table design.

Those remain separate bounded design questions.
