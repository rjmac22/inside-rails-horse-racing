# Phase 3 Evidence-First Design and Implementation Gate

## Status

Accepted governing rule for all Phase 3 entity, key, field-governance, enrichment, and physical-schema work.

This document applies to every existing and future Phase 3 conceptual design document.

Where another Phase 3 document appears to imply that a table, field, relationship, parser, classification, or enrichment must be implemented, this document takes precedence.

The central rule is:

> No physical model is authorised until a focused evidence study confirms that the relevant concepts exist in the available evidence, can be distinguished reliably, and are analytically necessary.

---

## 1. Purpose

The project must not build a theoretically comprehensive horse-racing database before it understands the evidence it actually possesses.

Racing data contains many concepts that may exist in the wider domain but may be:

- absent from the current source;
- represented differently by jurisdiction or period;
- encoded ambiguously;
- transformed by a supplier;
- unavailable historically;
- analytically unnecessary for the first implementation;
- obtainable only from a later provider;
- impossible to interpret reliably without a dedicated investigation.

Conceptual awareness of a complication is useful.

It does not, by itself, justify a physical table, field, relationship, parser, or ingestion process.

The project must therefore proceed from evidence to design, not from imagined completeness to schema.

---

## 2. Mandatory sequence

Every non-foundational data concept must pass through the following sequence.

### Stage 1: inspect the actual evidence

The project must establish what is physically present in the source or proposed enrichment.

This includes, where relevant:

- source provider;
- source product;
- exact source version or retrieval;
- relation and field;
- raw data type;
- populated and blank counts;
- distinct-value patterns;
- jurisdiction and date coverage;
- malformed values;
- internal contradictions;
- changes in encoding through time;
- supplier transformations;
- examples linked back to immutable source records.

No field meaning should be inferred from its name alone.

### Stage 2: establish meaning and limitations

A focused study must determine what the evidence represents and what it does not represent.

The study must identify:

- the strongest supported semantic interpretation;
- unresolved cases;
- jurisdiction-specific meanings;
- effective-date or methodology changes;
- source-version limitations;
- whether blanks mean none, unknown, unavailable, not applicable, or something else;
- whether the field is raw evidence, a supplier-derived value, or a converted representation;
- whether multiple concepts have been collapsed into one source field.

Where meaning cannot be established, the value remains unresolved evidence.

### Stage 3: define the analytical need

The project must identify the real analytical questions the data is intended to answer.

The study must explain:

- which analyses require the concept;
- what precision is needed;
- what distinctions materially affect conclusions;
- which cases can be excluded safely;
- whether the source has enough coverage to justify implementation;
- whether the same result can be obtained more simply;
- whether the concept belongs in the core database, an extension, or a derived analytical output.

A concept should not be implemented merely because it is interesting or exists somewhere in racing.

### Stage 4: design the governed model

Only after Stages 1 to 3 may the project define the governed representation.

The design should include only distinctions that are:

- evidenced;
- analytically necessary;
- reproducible;
- supportable by provenance;
- testable;
- proportionate to the available data.

The design may preserve a route for later extension without implementing speculative detail.

### Stage 5: authorise physical implementation

A physical table, column, relationship, parser, migration, or ingestion process requires an explicit implementation decision.

That decision must identify:

- the accepted evidence study;
- the governed concepts being implemented;
- what remains unresolved;
- the intended analytical use;
- the minimum physical structure required;
- validation rules;
- source-wide checks;
- migration and compatibility implications;
- what has deliberately been deferred.

### Stage 6: implement and validate

Implementation must include, where applicable:

- immutable raw evidence preservation;
- reproducible transformation logic;
- focused unit tests;
- source-wide validation;
- persisted and reloaded outputs;
- documented provenance;
- explicit handling of unresolved cases;
- analytical admission rules;
- reader-facing limitations.

---

## 3. Conceptual design documents are safeguards, not schema promises

Existing Phase 3 documents describe:

- distinctions that may matter;
- failure modes to avoid;
- identity boundaries;
- provenance requirements;
- questions a future study must answer;
- ways the database may need to expand later.

They do **not** automatically authorise:

- one table per conceptual entity;
- one column per listed attribute;
- implementation of every possible status;
- speculative jurisdiction rules;
- ingestion of data not currently held;
- parsing of fields whose semantics remain unaudited;
- worldwide modelling of every racing or betting regime;
- premature normalisation of unresolved text.

A conceptual document may remain valuable even when none of its optional entities is implemented in the first physical schema.

---

## 4. Minimum viable governed core

The first physical implementation should contain only the smallest structure needed to preserve evidence and support accepted analyses.

The likely stable core includes concepts such as:

- source provider, product, version, relation, and immutable source record;
- source-record provenance;
- governed source race occurrence where supported by accepted grouping evidence;
- runner participation where supported by accepted source-row evidence;
- raw values or source-record linkage sufficient to recover them;
- governance release and decision provenance;
- explicit unresolved states where interpretation is required.

Even these concepts require an implementation brief before physical schema work begins.

Everything beyond the stable core should be justified separately.

---

## 5. Evidence maturity states

Each proposed concept or field should have an explicit maturity state.

### 5.1 Uninspected

The source or enrichment has not been profiled sufficiently.

No governed semantic claim is authorised.

### 5.2 Profiled

Basic distributions and examples are known, but meaning is not yet established.

The field remains raw evidence only.

### 5.3 Semantically investigated

A focused study has established a supported interpretation, limitations, and unresolved cases.

This does not yet authorise physical implementation.

### 5.4 Analytically justified

A defined analysis requires the concept, and the evidence has adequate coverage and quality.

A governed model may now be designed.

### 5.5 Conceptually designed

The governed distinctions and identity boundaries have been accepted.

This is the status of many current Phase 3 documents.

It still does not authorise physical implementation.

### 5.6 Implementation authorised

A bounded implementation brief has been accepted.

Only this state permits schema, parser, migration, and ingestion work.

### 5.7 Implemented and validated

The concept has reusable implementation, focused tests, source-wide validation, provenance, documentation, and accepted limitations.

---

## 6. Required evidence package before implementation

Before implementation authorisation, the project should normally possess:

1. a focused notebook or equivalent study;
2. exact source-version provenance;
3. source-wide field profiling;
4. representative examples and edge cases;
5. semantic conclusion;
6. explicit limitations and unresolved cases;
7. jurisdiction and effective-date treatment where relevant;
8. proposed analytical uses;
9. admission and exclusion rules;
10. a minimal governed design;
11. validation requirements;
12. a decision on whether the concept belongs in core, extension, or derived output.

The depth of the package should be proportionate to the risk and complexity of the field.

---

## 7. Physical design must remain extension-friendly

Evidence-first design does not mean designing the database into a corner.

The core should preserve stable identities and provenance so later evidence can be attached without rewriting history.

Later extensions may add:

- another source version;
- another provider;
- a jurisdiction-specific interpretation regime;
- official identifiers;
- weather observations;
- sectional timing;
- detailed betting-pool semantics;
- course configuration evidence;
- richer ownership structures;
- corrected or superseding governed interpretations.

The correct response to a future enrichment is:

1. inspect the actual dataset;
2. understand its methodology and coverage;
3. determine how it links to existing stable identities;
4. design the smallest justified extension;
5. validate it independently.

The project must not create empty speculative structures merely to show that expansion is theoretically possible.

---

## 8. Raw evidence remains the fallback

Where meaning is unresolved, the database should preserve:

- the immutable source record;
- the exact raw value;
- source lineage;
- the unresolved status;
- any candidate interpretations and their evidence, if useful.

Unresolved evidence must not be forced into a misleading governed category.

It may be excluded from a specific analysis without being deleted or treated as useless.

---

## 9. Effective-dated and jurisdiction-specific concepts

Some meanings change by jurisdiction, date, provider, or methodology regime.

Examples include:

- starting-price construction;
- Tote and pari-mutuel dividends;
- classification systems;
- medication rules;
- allowances and claims;
- course layouts;
- official result amendments;
- weather-provider coverage;
- sectional-timing methodology.

The existence of these complications does not require the first schema to model every regime.

A regime should be implemented only when:

- the relevant evidence exists;
- the study requires it;
- the effective boundaries are supported;
- the distinction materially affects interpretation.

Until then, the source value remains preserved with unresolved or limited semantics.

---

## 10. Core, extension, and derived layers

Every implemented concept should be classified deliberately.

### 10.1 Core evidence layer

Use for stable provenance and identities required across many studies.

### 10.2 Governed extension layer

Use for source-, provider-, jurisdiction-, or study-specific evidence that can attach to the core without becoming universal.

### 10.3 Derived analytical layer

Use for calculated measures, classifications, aggregates, model outputs, and study-specific features.

Derived values should not be promoted into core source facts.

---

## 11. Treatment of current Phase 3 documents

The existing Phase 3 documents remain accepted as conceptual safeguards.

Their default status is:

> Conceptually designed; physical implementation not yet authorised.

This includes, unless a later implementation brief explicitly states otherwise:

- meeting identity;
- recurring race series and editions;
- race conditions and classification;
- race results and finishing outcomes;
- prize money and monetary amounts;
- betting prices and market observations;
- betting-price interpretation regimes;
- ratings and performance measures;
- carried weight, allowances, and claims;
- equipment and medication assertions;
- course configuration extensions;
- participant and ownership identity extensions.

Some of these topics already have stronger evidence than others.

That difference should determine the order and depth of future studies, not create blanket implementation authority.

---

## 12. Deferred enrichments

Data not present in Source Version 1 should normally remain a deferred enrichment until an obtainable dataset has been inspected.

Examples include:

- sectional timing;
- runner tracking;
- GPS positions;
- detailed weather observations;
- irrigation records;
- exchange order books;
- official identity registries;
- specialist course-layout data.

The project should not design detailed physical structures for these merely because they may be useful one day.

A brief note identifying the future linkage requirement is sufficient until evidence exists.

---

## 13. Study-first examples

### 13.1 Weather and going

Do not preselect weather variables and windows from intuition alone.

First investigate:

- obtainable providers;
- course-location accuracy;
- station or grid representativeness;
- historical coverage;
- observation intervals;
- rainfall accumulation conventions;
- missingness;
- relationships with going;
- useful pre-race windows;
- limitations from irrigation and drainage.

Only then design the weather evidence layer.

### 13.2 Sectional timing

Do not build sectional tables while no sectional dataset is held.

First inspect the actual provider, methodology, checkpoint definitions, coverage, precision, and race linkage.

### 13.3 Betting prices

Do not treat every familiar-looking numeric price as comparable fixed odds.

First establish field semantics, jurisdiction, effective methodology regime, and any source conversion.

### 13.4 Ratings

Do not create a universal rating column.

First establish the rating system, publisher, timing, scale, and whether the value is pre-race, post-race, official, private, or derived.

---

## 14. Implementation gate checklist

A concept may move to physical implementation only when every applicable answer is satisfactory.

### Evidence

- Is the exact source or enrichment identified?
- Has the field or relation been profiled source-wide?
- Are raw examples and edge cases preserved?
- Is the semantic interpretation supported rather than guessed?
- Are unresolved cases explicit?

### Analytical need

- Is there a defined study or operational requirement?
- Does the distinction materially affect analysis?
- Is coverage sufficient?
- Is implementation preferable to a simpler derived treatment?

### Design

- Is the proposed model minimal?
- Does it preserve provenance?
- Does it avoid overwriting raw evidence?
- Can it represent uncertainty?
- Can later evidence extend it safely?

### Validation

- Are deterministic rules documented?
- Are focused tests defined?
- Is a source-wide validator possible?
- Are reconciliation rules defined?
- Are limitations and disclosure requirements clear?

### Governance

- Is the implementation decision recorded?
- Is the governance release identified?
- Are deferred items explicit?
- Has the user accepted the bounded implementation scope?

If any material answer is no, implementation remains unauthorised.

---

## 15. Stop conditions

Work should stop and return to investigation when:

- field values contradict the assumed meaning;
- multiple jurisdictions use materially different semantics;
- a methodology breakpoint is discovered;
- blanks or zeros cannot be interpreted safely;
- supplier conversion is suspected but undocumented;
- source coverage is too sparse for the intended analysis;
- the proposed schema requires speculative entities;
- validation cannot distinguish valid from invalid records;
- implementation scope grows beyond the evidence package.

Stopping is not failure.

It is the required response to insufficient evidence.

---

## 16. Documentation wording rule

Future Phase 3 conceptual documents should state clearly:

> This document defines conceptual safeguards and questions for evidence-led investigation. It does not authorise physical schema or implementation. Implementation requires a focused source study and an accepted implementation brief under `PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`.

Existing documents are governed by this rule even where they do not yet contain that wording individually.

---

## 17. Decision summary

The accepted Phase 3 method is:

1. Inspect actual evidence before modelling it.
2. Establish meaning, limitations, jurisdiction, period, and supplier transformations.
3. Define the analytical need before designing the governed representation.
4. Treat conceptual documents as safeguards, not schema promises.
5. Require explicit implementation authorisation for every non-foundational concept.
6. Build the smallest useful governed core.
7. Preserve unresolved raw evidence instead of forcing false certainty.
8. Keep later providers and enrichments as evidence-led extensions.
9. Do not create space for data the project does not hold and may never obtain.
10. Validate every implemented interpretation independently and source-wide.

The governing principle is:

> Understand it first. Design it second. Build only what the evidence and analysis justify.
