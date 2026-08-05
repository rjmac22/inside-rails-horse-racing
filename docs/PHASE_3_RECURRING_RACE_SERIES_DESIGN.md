# Phase 3 Recurring Race Series Identity Design

## Purpose

This document records the accepted conceptual design for recurring race identity in Phase 3.

It is deliberately conceptual. It does not define SQL tables, physical key types, indexes or database technology.

The design separates:

- the exact race name supplied for one source race occurrence;
- the individual running of a race;
- an optional governed recurring race series;
- the governed relationship between an individual running and a series;
- unresolved or competing continuity candidates.

The central rule is:

> Similar or identical race names do not establish recurring-race identity. A race series is an optional governed continuity claim supported by evidence, while every individual running and raw source name remains preserved.

## Accepted design principles

1. Every source race occurrence remains an independent race occurrence.
2. The exact raw `race_name` remains immutable source evidence.
3. Identical, similar or normalised race names do not automatically create one recurring series.
4. Generic titles must not be merged merely because their wording matches.
5. A recurring race series is created only after a bounded study supports historical continuity.
6. Each accepted running remains a separate series edition with its own date, venue, site, configuration, distance, class, conditions and other race context.
7. Sponsorship, naming, scheduling, venue, distance, class or condition changes do not automatically preserve or terminate series continuity.
8. Continuity decisions must retain their evidence, effective scope, status, confidence and governance release.
9. Uncertain continuity remains a candidate relationship rather than being forced into an accepted series assignment.
10. Raw source records and names are never overwritten when a governed series link is accepted or amended.

## Candidate entities and governed relationships

### 1. Raw race-name assertion

**Grain:** The exact source-presented `race_name` attached to one source race occurrence through its supporting source records.

**Status:** Immutable source assertion.

**Candidate identifier:** Source version, source race occurrence and source field; no recurring-race identity is derived directly from the text.

**Identifier scope:** Source-race-occurrence-scoped.

**Required lineage and evidence:**

- source version;
- source relation and supporting source records;
- source race occurrence;
- exact raw `race_name` value;
- original punctuation, capitalisation and source storage state;
- raw date, course and off-time grouping context.

**Known uncertainty:**

- sponsorship text may be inserted, removed or reordered;
- the same recurring race may use materially different names over time;
- generic or promotional titles may be reused for unrelated races;
- one title may be used for several races on the same card, season or jurisdiction;
- historical spellings and abbreviations may vary.

**Expected relationships:**

- every source race occurrence preserves its exact raw race-name assertion;
- many source race occurrences may share the same text without sharing one series identity;
- one raw race-name assertion may support an optional governed series-edition assignment;
- unresolved or blank names do not prevent preservation of the source race occurrence.

**Accepted rules:**

- raw race-name text is evidence, not a natural key;
- text normalisation may support investigation but cannot authorise a merge;
- generic titles such as maiden, novice, handicap or conditions descriptions are not series identities without separate evidence.

### 2. Governed recurring race series

**Grain:** One governed historical race continuity recognised across two or more individual runnings where evidence supports treating them as editions of the same continuing race.

**Status:** Optional governed real-world continuity entity.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Project-wide, subject to governed historical amendment.

**Required lineage and evidence:**

- accepted series display name;
- known historical, sponsored or abbreviated names;
- jurisdiction and organising context where established;
- evidence supporting continuity between editions;
- recognised predecessor, successor, replacement or disputed relationships;
- expected scheduling or meeting context where relevant;
- governance release, decision status, confidence and review provenance.

**Known uncertainty:**

- a race may change sponsor, title, venue, date, distance, class, eligibility or conditions;
- an old title may be revived for a different race;
- two series may be merged administratively or one series may divide;
- historical sources may disagree about continuity;
- marketing continuity may not match sporting or regulatory continuity.

**Expected relationships:**

- one recurring race series may contain many governed editions;
- one source race occurrence may belong to zero or one accepted recurring race series within one governance release;
- a series may have predecessor, successor, replacement or disputed-continuity relationships to other series;
- candidate editions remain separate until accepted.

**Accepted rules:**

- series identity represents governed historical continuity, not text similarity;
- a series may survive a verified sponsorship or title change;
- a series may survive changes in venue, schedule, distance, class or conditions where the evidence supports continuity;
- those changes remain visible at edition level and must never be normalised away;
- an apparent continuation may instead require predecessor and successor series rather than one unconditional merge.

**Unresolved design questions:**

- the evidence threshold for distinguishing continuous series, replacement race, revived title and genuinely new race;
- whether some formal competition structures require a parent series and named sub-series;
- how official identifiers from future authorities should relate to governed series identities.

### 3. Recurring race series edition

**Grain:** One individual running treated as an edition of one governed recurring race series.

**Status:** Governed edition context linked to an independent source race occurrence.

**Candidate identifier:** Independent project-assigned technical identifier or a governed relationship identity derived from series plus source race occurrence; physical choice deferred.

**Identifier scope:** Series-and-governance-release-scoped.

**Required lineage and evidence:**

- governed recurring race series;
- source race occurrence;
- exact raw race-name assertion;
- race date and governed time status;
- source meeting occurrence where resolved;
- venue, physical site and course configuration context where resolved;
- race distance, class, type, eligibility and conditions as separately governed attributes;
- edition sequence or year label only where supported;
- assignment evidence, status, confidence and governance release.

**Known uncertainty:**

- official edition numbering may be absent, inconsistent or retrospectively assigned;
- a race may be postponed, abandoned, rerun, transferred or divided;
- two divisions on one day may or may not both count as editions;
- a replacement race may be advertised as carrying on a tradition without representing the same sporting continuity.

**Expected relationships:**

- one accepted edition links exactly one source race occurrence to one recurring race series within one governance release;
- one source race occurrence has zero or one accepted series-edition assignment within that release;
- a series may have many editions across dates, meetings, venues and configurations;
- later evidence may amend the assignment while preserving earlier accepted states.

**Accepted rules:**

- the edition retains all occurrence-level facts and does not inherit timeless race conditions from the series;
- edition numbering is optional and evidence-based;
- transferred, postponed, divided or rerun races require explicit treatment rather than automatic numbering;
- series-level analysis must be reproducible from the edition assignments and their governance release.

### 4. Source-race-to-series assignment

**Grain:** One governed decision about whether one source race occurrence is an accepted edition of one recurring race series under one governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Source race occurrence plus governance release, supported by an independent relationship identifier if required by later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:**

- source race occurrence;
- raw race-name assertion;
- recurring race series where accepted;
- assignment status;
- decision method and evidence;
- confidence and review status;
- effective scope and relevant dates;
- accepted, rejected and competing candidate series where required;
- governing output and reference-data version.

**Expected statuses:**

- accepted;
- unresolved;
- rejected candidate;
- not investigated;
- not applicable because no recurring series is claimed.

**Known uncertainty:** Later research may show that an accepted edition belongs to another series, represents a successor race or is unrelated despite similar naming.

**Accepted rules:**

- no automatic assignment is created merely because a name resembles a known series;
- unresolved cases do not create placeholder or generic series identities;
- rejected candidate links remain available as evidence where useful;
- historical accepted decisions must remain reconstructable rather than being silently overwritten.

### 5. Race-series continuity relationship

**Grain:** One governed historical relationship between two recurring race series.

**Status:** Optional governed relationship.

**Candidate identifier:** Independent relationship identifier or series pair plus relationship type and governance release; physical choice deferred.

**Identifier scope:** Governance-release-scoped.

**Possible relationship types:**

- predecessor;
- successor;
- replacement;
- renamed continuation;
- revived title;
- split into;
- merged from;
- disputed continuity;
- no supported continuity.

**Required lineage and evidence:** Both series identities, relationship type, effective dates or bounded period, evidence, decision status, confidence, review provenance and governance release.

**Accepted rule:** Historical complexity is represented through typed relationships rather than forcing every related race into one timeless series identity.

## Evidence expected in a recurring-race study

A governed study may use evidence such as:

- official race histories or authority records;
- race conditions and eligibility continuity;
- prize structure or sponsor documentation;
- meeting and calendar position;
- venue and scheduling continuity;
- contemporary reports describing renaming, replacement or transfer;
- recognised historical lists of winners;
- explicit edition numbering;
- predecessor and successor statements;
- race-name changes through time;
- evidence that an apparently identical title was reused independently.

No single item is automatically decisive. The study must state the reasoning and limitations.

## Analysis rules

A study using recurring race series must:

1. identify the governance release used for series and edition assignments;
2. state whether unresolved candidate editions are excluded, retained separately or sensitivity-tested;
3. preserve edition-level changes in venue, physical site, configuration, date, distance, class, conditions and eligibility;
4. avoid substituting the latest series name for historical raw race names without disclosure;
5. state whether predecessor, successor, replacement or revived-title relationships are included;
6. avoid treating generic title matches as recurring-race continuity;
7. report any material changes in series definition across the study period.

## Examples of accepted treatment

- A verified sponsorship rename may remain one series while each edition preserves its exact source name.
- A recognised race moving to another venue may remain one series where historical evidence supports continuity, while venue and configuration changes remain visible by edition.
- A generic `Maiden Stakes` title appearing repeatedly does not create a recurring race series.
- A historic title revived decades later may be a new series with a `revived title` relationship rather than an automatic continuation.
- A former race replaced by a newly constituted event may require predecessor and successor identities rather than one merged series.
- Two divisions staged on the same day remain separate race occurrences and require explicit evidence before either or both are treated as editions of the series.

## Deferred cross-source identity

The current design does not assume that recurring series or editions from another provider are automatically equivalent.

When another source version or provider becomes available, reconciliation may use:

- governed source race occurrence matching;
- official or provider identifiers as supporting evidence;
- series histories;
- meeting, venue and date context;
- conditions, distance, class and participant evidence;
- explicit predecessor, successor or renaming documentation.

Cross-source equivalence must be governed and evidenced rather than inferred solely from race-name text.

## Current design boundary

This document establishes:

- immutable raw race-name assertions;
- optional governed recurring race series;
- separately preserved series editions;
- governed source-race-to-series assignments;
- typed continuity relationships between series;
- explicit unresolved and rejected candidate states;
- analysis disclosure requirements.

It does not define:

- SQL tables;
- physical key types;
- automated race-name matching rules;
- a complete catalogue of recurring races;
- official edition numbering;
- cross-provider series identity;
- amendment-history implementation;
- import-manifest structure;
- physical database technology.
