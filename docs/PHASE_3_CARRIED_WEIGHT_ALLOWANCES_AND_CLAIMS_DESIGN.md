# Phase 3 Carried Weight, Allowances, and Claims Design

## Status

Accepted conceptual design for Phase 3 entity and key work.

This document defines the governed identity and evidence model for runner weights, allowances, claims, penalties, overweight, and related adjustments.

It deliberately does **not** define physical tables, SQL, indexes, migrations, or ingestion code.

Field-specific implementation must wait for a dedicated source-field audit of the available weight-related columns and their observed values.

---

## 1. Purpose

Weight information is easy to flatten into one apparently simple number even though racing records may refer to several different facts:

- the weight assigned by the race conditions or handicapper;
- the weight declared before the race;
- the weight intended after an allowance or claim;
- the weight actually carried;
- additional overweight;
- penalties applied for previous performances;
- allowances arising from age, sex, apprentice status, conditional status, amateur status, or race conditions;
- a source-presented value whose exact stage is unresolved.

These are related facts, but they are not interchangeable.

The design must preserve the original evidence while allowing governed interpretations, reconciliation, and later jurisdiction-specific extensions without forcing every source value into one universal weight concept.

The central rule is:

> A runner's handicap mark, allotted weight, declared weight, and actual carried weight are related but distinct facts.

---

## 2. Core conceptual separation

The model must keep the following concepts separate.

### 2.1 Raw weight assertion

The exact weight-related text or number supplied by an immutable source record.

This may include:

- stones and pounds;
- pounds only;
- kilograms;
- textual claims or allowances;
- overweight markers;
- penalty markers;
- footnotes;
- blanks or nulls;
- malformed values;
- a source-presented number whose precise semantic stage is unresolved.

The raw assertion remains supplier evidence even after successful parsing or later correction.

### 2.2 Governed weight observation

A project interpretation that a defined runner was associated with a defined weight concept in a defined race context.

A governed observation must be able to carry:

- the linked runner record;
- weight concept;
- original value and unit;
- governed normalised value where justified;
- effective stage or timing;
- interpretation method;
- evidence status;
- confidence or review status;
- jurisdiction and rule context where relevant;
- governance release.

### 2.3 Weight adjustment

A separately evidenced addition to or subtraction from a runner's base or assigned weight.

Potential adjustment types include:

- jockey claim;
- apprentice or conditional allowance;
- age allowance;
- sex allowance;
- race-condition allowance;
- penalty;
- statutory extra weight;
- overweight;
- underweight or failure to draw weight;
- equipment-related allowance where a jurisdiction explicitly provides one;
- manual or official correction.

An adjustment is not the same thing as the final carried weight.

### 2.4 Derived weight measure

A value calculated from one or more governed observations and adjustments.

Examples include:

- pounds carried;
- kilograms carried;
- weight relative to top weight;
- weight above or below the race mean;
- weight-for-age adjusted load;
- weight relative to official rating;
- change in carried weight from a previous run;
- reconstructed expected carried weight;
- discrepancy between expected and observed carried weight.

Derived measures are analytical outputs, not original source evidence.

---

## 3. Relationship to existing Phase 3 entities

### 3.1 Runner record

Weight evidence attaches to a runner in one specific race.

It must not attach permanently to the provisional horse occurrence because:

- the same horse carries different weights in different races;
- the same horse may receive different allowances or penalties over time;
- jockey claims are specific to a rider assignment and race context;
- declared and actual carried weights can differ within one runner occurrence.

A governed weight observation therefore links to a runner record while retaining its own independent technical identity.

### 3.2 Raw participant assertion and governed jockey assignment

A jockey claim or allowance may depend on the jockey assigned to the runner.

The weight model must not assume that a raw jockey label has already been reconciled to a verified person.

Where a claim is source-presented, it can still be preserved against the runner even if participant identity remains unresolved.

Where a study requires jockey-level claim history, admission should require the appropriate governed participant identity or an explicitly source-scoped alternative.

### 3.3 Race conditions and classification

Allowances and penalties may derive from the race conditions, classification system, jurisdiction, date, or eligibility rules.

The weight model should therefore preserve links to the governed race-condition interpretation where available.

Matching numeric weights do not prove matching race conditions.

### 3.4 Ratings and performance measures

Official handicap marks, private ratings, speed figures, and carried weights remain separate concepts.

A rating may help explain why a weight was assigned, but it is not itself a weight.

A carried weight must never be stored in the ratings layer merely because the same numeric scale appears plausible.

### 3.5 Race result state

Post-race official evidence may clarify:

- actual carried weight;
- overweight;
- failure to draw the correct weight;
- a disqualification or inquiry relating to weighing in;
- a corrected jockey claim;
- an amended result caused by a weight breach.

The result state may affect settlement or official classification but must not overwrite the original weight assertion.

---

## 4. Raw evidence preservation

Every raw weight-related value must be retained exactly as supplied.

Preservation includes:

- original characters;
- punctuation;
- spacing;
- separators;
- unit notation;
- abbreviations;
- superscripts or suffixes where represented as text;
- claim and allowance markers;
- overweight indicators;
- penalty indicators;
- blanks and nulls;
- malformed or unparseable values.

Parsing or unit conversion must never replace the raw source value.

A parsed value is a governed interpretation of the raw assertion, not a corrected version of the source record.

---

## 5. Weight observation identity

Every governed weight observation requires its own project-wide technical identifier.

The observation identifier must remain independent of:

- source-record identity;
- runner identity;
- horse occurrence identity;
- jockey identity;
- race identity;
- numeric weight value.

A runner may legitimately have multiple weight observations because the evidence may include:

- assigned weight;
- declared weight;
- expected carried weight after claim;
- actual carried weight;
- source correction;
- official post-race amendment;
- multiple providers;
- multiple governance releases.

The model must not assume one weight value per runner.

---

## 6. Weight concepts must be explicit

The following concepts are distinct and should remain separately representable.

### 6.1 Base or conditions weight

The starting weight defined by race conditions before runner-specific adjustments.

This may be relevant in non-handicaps, weight-for-age races, penalties-and-allowances races, or other condition structures.

### 6.2 Allotted or assigned weight

The weight assigned to the runner under the handicap or race conditions before some later rider-specific or declaration-stage adjustments.

The exact meaning may vary by jurisdiction and source.

### 6.3 Declared weight

The weight declared for the runner at a defined pre-race stage.

A source value must not be labelled declared weight unless the field semantics establish that meaning.

### 6.4 Expected carried weight

A governed reconstruction of the weight expected to be carried after known claims, allowances, penalties, and overweight are applied.

This is derived unless explicitly supplied by the source.

### 6.5 Actual carried weight

The weight officially recorded as carried by the runner.

This may only be known from a result source or post-race evidence.

### 6.6 Weighed-in value

A post-race measurement or official weighing outcome where separately recorded.

This must remain distinct from a pre-race declared or assigned value.

### 6.7 Source-presented unresolved weight

A value that parses as a weight but whose semantic stage is not yet established.

It remains usable as source evidence but must not be admitted to analyses requiring a specific weight concept.

---

## 7. Unit systems and exact conversion

The original unit system must be preserved.

Potential source units include:

- stones and pounds;
- pounds;
- kilograms;
- another jurisdiction-specific unit;
- textual values with implied units;
- unresolved units.

A governed normalised value may be added only when the source unit is established.

For exact conversions:

- one stone equals 14 pounds;
- one international avoirdupois pound equals exactly 0.45359237 kilograms.

Where a value is expressed in stones and pounds, the governed pound total is:

`(stones × 14) + pounds`

The system must retain sufficient precision to reproduce the original value and conversion.

A converted display rounded to a preferred number of decimals must remain separate from the exact governed conversion.

The database must not infer a unit solely from a plausible numeric range if the jurisdiction or field semantics remain uncertain.

---

## 8. Claims and rider allowances

A jockey claim or rider allowance is a distinct adjustment, not a replacement for the assigned or carried weight.

A governed claim observation may require:

- linked runner;
- linked jockey assignment where resolved;
- claim amount;
- original and governed units;
- claim type;
- claim eligibility category;
- effective date or race date;
- source assertion;
- rule regime or jurisdiction;
- whether the claim was declared, expected, or officially applied;
- confidence and governance release.

The system must not assume that:

- every apprentice or conditional jockey claimed an allowance;
- the maximum eligible allowance was actually claimed;
- the claim amount can be inferred from the rider's name or status alone;
- a displayed carried weight excludes or includes the claim;
- the same rider had the same claim entitlement throughout the dataset.

Eligibility and claim amounts can change through experience, wins, jurisdiction, code, race type, age, or rule changes.

A rider identity study and an effective-dated rules study may therefore be required before claim histories are analysed across time.

---

## 9. Other allowances

Non-rider allowances must remain separately typed.

Potential examples include:

- age allowance;
- sex allowance;
- weight-for-age allowance;
- novice or maiden allowance;
- race-condition allowance;
- breeding or sales-condition allowance;
- jurisdiction-specific statutory allowance;
- another governed allowance established by evidence.

An allowance must identify the base to which it applies where known.

The project must not collapse all negative adjustments into one generic claim field if the underlying reasons are materially different.

For initial implementation, only allowance types established by source evidence or a dedicated rule study should be populated.

Unknown allowance semantics remain unresolved.

---

## 10. Penalties and extra weight

Penalties must remain distinct from base weights and allowances.

Potential penalty evidence may include:

- fixed penalties for wins within a defined period;
- cumulative penalties;
- penalties under race conditions;
- handicap reassessment effects;
- statutory extra weight;
- post-entry penalties;
- jurisdiction-specific penalties;
- source-presented penalty markers whose exact basis is unresolved.

A penalty observation should retain:

- amount and unit;
- reason or type where known;
- effective race context;
- source evidence;
- rule regime where established;
- whether the amount was declared, expected, or officially applied;
- confidence and governance release.

A penalty must not be inferred solely from the difference between two weight values unless a governed reconstruction establishes all other adjustments.

---

## 11. Overweight and underweight

Overweight is conceptually separate from an allotted or declared weight.

A governed overweight observation may represent:

- declared overweight before the race;
- officially recorded overweight in the result;
- source-presented overweight marker;
- a later official correction;
- an unresolved discrepancy.

The system must preserve both:

- the target or expected weight where supported; and
- the additional overweight amount.

Actual carried weight may then be supplied directly or derived only under a documented rule.

Underweight, failure to draw weight, or weighing-in discrepancies must not be represented as negative overweight without evidence that the governing rules use that interpretation.

Such events may require typed incident or result-state evidence.

---

## 12. Do not assume arithmetic composition

The project must not assume that every source follows a universal equation such as:

`actual carried weight = allotted weight - claim + penalties + overweight`

That equation may be useful as a validation hypothesis, but only after the meanings and inclusion rules of the individual fields are established.

A displayed weight may already incorporate:

- a claim;
- an allowance;
- a penalty;
- overweight;
- some but not all adjustments;
- a post-race correction.

Field-level audits must establish whether each source column is gross, net, pre-adjustment, or post-adjustment.

Until then, arithmetic discrepancies remain evidence requiring investigation rather than automatic error correction.

---

## 13. Timing and stage

Weight evidence should be represented with the strongest supported temporal stage.

Potential stages include:

- race-entry stage;
- handicap publication;
- declaration stage;
- final declaration;
- rider booking stage;
- pre-race weighing out;
- official result publication;
- weighing in;
- later correction or appeal.

The race date alone does not establish the stage at which the value was observed.

Where the exact stage is unresolved, the observation must remain explicitly unresolved rather than being labelled actual carried weight.

---

## 14. Jurisdiction and rule regimes

Weight rules can vary by:

- jurisdiction;
- racing code;
- race type;
- date;
- rider category;
- age and sex conditions;
- amateur or professional status;
- specific race conditions;
- regulator;
- historical rule version.

The model should permit an optional governed weight-rule regime to describe established context.

A regime may define:

- effective dates;
- jurisdiction and code;
- permitted units;
- claim categories;
- allowance rules;
- penalty rules;
- overweight treatment;
- weighing procedures;
- evidence and confidence.

The initial database need not encode every historical rule worldwide.

It should store only evidenced core facts and add regime detail when a focused investigation or analysis justifies it.

---

## 15. Relationship to horse age and sex

Age and sex can influence race-condition allowances and weight-for-age structures.

The weight model must not derive an age or sex allowance solely from a horse label or generic assumption.

Any derived allowance should depend on governed evidence for:

- the runner's age and sex at the relevant date;
- the race conditions;
- the jurisdiction and code;
- the applicable rule regime;
- the exact allowance schedule.

Where any component is unresolved, the derived allowance remains unresolved.

---

## 16. Relationship to official handicap marks

Official handicap marks and carried weights are different measures.

A higher official mark may influence an allotted weight, but the relationship depends on:

- race conditions;
- handicap structure;
- top-weight limits;
- minimum weights;
- weight compression;
- penalties;
- allowances;
- jurisdictional rules;
- declarations and withdrawals.

The project must not derive one directly from the other without a documented model and full race context.

Studies of rating-to-weight relationships must state:

- which rating system and version are used;
- which weight concept is used;
- whether claims and allowances are included;
- whether the race was a handicap;
- how compressed or limited weight ranges are treated.

---

## 17. Multiple source versions and providers

Two weight observations should not be treated as duplicates merely because they share:

- runner label;
- race label;
- numeric weight;
- unit;
- source date.

Cross-version or cross-provider reconciliation should consider:

- reconciled race identity;
- runner identity within the race;
- weight concept;
- stage or timing;
- exact raw value;
- unit;
- adjustment context;
- source lineage;
- correction evidence.

Possible reconciliation outcomes include:

- duplicate representation of the same observation;
- distinct observations at different stages;
- source correction;
- conflicting evidence;
- unresolved relationship.

No cross-source equivalence should be assumed at ingestion.

---

## 18. Corrections and supersession

Later evidence may establish that a source weight was:

- malformed;
- expressed in a different unit;
- attached to the wrong runner;
- assigned the wrong semantic stage;
- missing a claim or penalty marker;
- corrected by an official source;
- inconsistent with the result;
- invalidated by a source-version defect.

The original source assertion remains immutable.

A correction should be represented through governed evidence with:

- correction type;
- prior interpretation;
- corrected interpretation;
- evidence reference;
- decision status;
- effective governance release;
- reviewer or method where applicable.

Interpretive history should remain append-only rather than silently replacing prior governed states.

---

## 19. Missingness and unresolved states

The system must distinguish at least:

- valid weight supplied;
- source null;
- blank source text;
- unit unresolved;
- semantic stage unresolved;
- malformed value;
- claim not supplied;
- no claim applicable;
- claim eligibility unresolved;
- allowance not supplied;
- no allowance applicable;
- penalty not supplied;
- no penalty applicable;
- actual carried weight unavailable;
- source conflict;
- official correction pending or unresolved.

A blank claim field must not automatically mean a zero claim.

A blank actual-weight field must not automatically mean the declared weight was carried.

Unknown and zero are different facts.

---

## 20. Derived weight calculations

Derived calculations must use named, versioned methods.

Potential derived measures include:

- total pounds;
- exact kilograms;
- nominal carried weight;
- expected carried weight after adjustments;
- discrepancy between expected and reported actual weight;
- relative weight within a race;
- difference from top weight;
- change from previous run;
- weight per unit of official rating;
- weight-for-age adjusted comparison;
- standardised weight within a jurisdiction and rule regime.

Every derived value should retain:

- input observations;
- transformation formula;
- unit rules;
- missing-value handling;
- adjustment inclusion rules;
- method version;
- governance release.

Derived measures must not overwrite source or governed observations.

---

## 21. Validation requirements

Future implementation should support validation of at least the following invariants.

### 21.1 Evidence preservation

- Every governed weight interpretation links to immutable source or documented external evidence.
- Raw weight text remains unchanged.
- Failed parsing does not destroy or replace the raw value.

### 21.2 Observation integrity

- Every weight observation links to one runner record.
- Every observation has a defined weight concept or explicit unresolved status.
- Every valid normalised value has a resolved source unit.
- Invalid or unavailable states are not stored as valid weights.

### 21.3 Unit integrity

- Stones-and-pounds values reconcile exactly to governed pounds.
- Exact pound-to-kilogram conversions are reproducible.
- Rounded display values remain separate from exact governed conversions.
- Unit inference is not accepted without evidence.

### 21.4 Adjustment integrity

- Claims, allowances, penalties, and overweight remain separately typed.
- No adjustment is applied twice in a governed reconstruction.
- A derived actual or expected weight identifies all included adjustments.
- Zero adjustments remain distinct from unknown adjustments.

### 21.5 Temporal integrity

- Observations identify their stage where known.
- Pre-race and post-race weight facts are not silently merged.
- Later corrections retain their effective governance release.

### 21.6 Cross-field integrity

- Official ratings are not stored as weights.
- A jockey claim does not require fabricated participant identity.
- Result amendments do not overwrite historical weight evidence.
- Weight observations remain scoped to the correct runner and race.

---

## 22. Admission rules for analytical studies

Every weight-related study must state its admission rules.

At minimum, it should define:

- source version or versions;
- jurisdiction and date range;
- racing code and race universe;
- weight field or governed weight concept;
- unit-conversion method;
- treatment of claims;
- treatment of allowances;
- treatment of penalties;
- treatment of overweight;
- treatment of missing and unresolved values;
- whether actual or expected weight is used;
- rating system where ratings are involved;
- result-state version where post-race outcomes are involved;
- governance release.

A study must not refer generically to "weight carried" unless the field semantics establish actual carried weight or the study clearly defines a governed proxy.

---

## 23. Required disclosures for common analyses

### 23.1 Weight and performance

Disclose:

- exact weight concept used;
- whether the value is assigned, declared, expected, or actual;
- unit conversion;
- claims and allowances included;
- treatment of penalties and overweight;
- race-type and jurisdiction restrictions;
- handling of missing values.

### 23.2 Change in weight between runs

Disclose:

- horse-occurrence identity version;
- weight concept used at both runs;
- unit normalisation;
- treatment of code and jurisdiction changes;
- treatment of different claims or riders;
- whether race-condition effects are controlled.

### 23.3 Jockey claims

Disclose:

- claim field semantics;
- rider identity or source-scoped label treatment;
- claim-rule regime;
- whether eligibility or actual claimed amount is analysed;
- handling of unknown and zero claims;
- race types included.

### 23.4 Handicap mark versus weight

Disclose:

- official-mark system and effective date;
- carried-weight concept;
- handicap-only admission rule;
- treatment of weight compression and minimum weights;
- claims, penalties, and allowances;
- any transformation or normalisation.

### 23.5 Cross-jurisdiction comparisons

Disclose:

- source units;
- exact conversions;
- weight-rule regimes;
- race-condition differences;
- unresolved jurisdictions excluded;
- whether values represent equivalent stages.

---

## 24. Known limitations before implementation

The current Phase 3 design does not yet establish:

- which Source Version 1 fields contain runner weights;
- whether the displayed value is allotted, declared, or actual carried weight;
- whether claims are embedded in the displayed weight;
- whether claim amounts appear in separate fields;
- whether penalties or allowances are encoded separately;
- whether overweight is recorded;
- which unit systems occur by jurisdiction;
- whether unit conventions change across the source period;
- whether result-stage corrections are represented;
- whether blanks mean unknown, not applicable, or zero;
- whether foreign jurisdictions use source conversions;
- whether source values are internally arithmetically consistent.

These are field-governance questions for a dedicated source audit and notebook.

The model intentionally leaves them unresolved rather than inventing certainty.

---

## 25. Deferred extensions

The following are valid later extensions but are not required for the first implementation:

- complete jurisdiction-specific claim-rule histories;
- apprentice win thresholds and changing entitlements;
- official weighing-out and weighing-in records;
- saddle and equipment weight components;
- minimum riding weights;
- weight-for-age scale histories;
- full penalties-and-allowances rule engines;
- automatic expected-weight reconstruction;
- steward inquiry linkage for weight breaches;
- equipment-specific allowances;
- high-precision weight sensor evidence;
- live declaration and rider-change histories;
- cross-provider weight reconciliation services.

These should be added as governed extension layers when evidence and analytical need justify them.

---

## 26. Implementation implications for later schema work

Without prescribing SQL, the eventual schema will need to support independent identities or governed records for:

- raw weight assertion;
- governed weight observation;
- weight concept;
- unit and conversion rule;
- weight adjustment;
- adjustment type;
- optional effective-dated rule regime;
- correction or supersession;
- derived weight measure;
- governance release.

The schema must support multiple weight observations and multiple adjustments per runner.

It must also support unresolved semantics without fabricating a final carried weight.

---

## 27. Decision summary

The accepted Phase 3 carried-weight design is:

1. Preserve every raw weight-related value exactly as supplied.
2. Attach weight evidence to the runner in one specific race.
3. Give governed weight observations independent technical identity.
4. Keep allotted, declared, expected, actual carried, and weighed-in values distinct.
5. Retain original units and add governed conversions only when units are established.
6. Keep official handicap marks separate from weight observations.
7. Represent jockey claims, other allowances, penalties, and overweight as separate adjustments.
8. Do not assume a displayed weight includes or excludes any adjustment without evidence.
9. Do not infer a universal arithmetic composition before field semantics are audited.
10. Distinguish zero, unknown, not applicable, malformed, and unavailable states.
11. Preserve pre-race and post-race observations separately.
12. Permit effective-dated jurisdiction and rule regimes as optional extensions.
13. Preserve corrections and interpretive changes append-only through governance releases.
14. Require every study to name the exact governed weight concept and adjustment treatment used.
15. Defer field-specific implementation until a dedicated audit establishes Source Version 1 semantics.

---

## 28. Boundary with the next design topics

This document resolves the conceptual identity and governance boundary for carried weight, allowances, claims, penalties, and overweight.

It does not yet resolve:

- equipment and medication assertions;
- draw, stalls, and starting-position evidence;
- sectional timing and in-race position observations;
- weather observations and going reconciliation;
- physical table design.

Those remain separate bounded design questions.
