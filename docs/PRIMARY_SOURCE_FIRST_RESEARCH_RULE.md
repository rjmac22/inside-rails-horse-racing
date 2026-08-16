# Primary-source-first research rule

## Status

**Standing project-wide research-governance rule.**

Effective: 16 August 2026.

This rule applies to all Inside Rails research, including reader-facing studies, source-field investigations, database-governance work, validation, reconciliation and publication drafting.

It supplements the existing study playbook, data-access rules, source register and provenance requirements. Where older workflow wording implies that the accepted Inside Rails database is the normal starting point for discovering what British racing means, this rule takes precedence.

---

## Core rule

> **For a question about what a racing jurisdiction is, means, permits, requires, schedules, classifies or officially records, establish the concept from the best available primary official source before using Inside Rails or another third-party dataset to define it.**

For Great Britain, the British Horseracing Authority is normally the primary authority for regulatory, administrative, programme, race-condition, result and handicapping concepts. Depending on the question, another primary authority may be more specific, for example an official racecourse/operator source for the identity or physical configuration of its own racecourse.

Inside Rails databases are analytical representations. They are not authorities on the meaning of the sport.

Commercial form providers, media sites and other third-party datasets are secondary evidence unless the research question is specifically about what that source itself publishes or represents.

---

## Required evidence order

For conceptual and semantic questions, use this order unless the question itself requires a different source object:

1. **Primary official terminology / rules**
   - rules and regulations;
   - official glossaries and guides;
   - official programme or fixture instructions;
   - official race conditions;
   - official technical or administrative publications.

2. **Primary official structured data / records**
   - official API or structured race data;
   - official racecards/results;
   - stewarding records;
   - official ratings or programme records;
   - other official record systems.

3. **Inside Rails governed data**
   - test whether the project represents the official concept;
   - measure the historical population;
   - identify disagreements, missingness and source-specific conventions;
   - perform analytical relationships once field semantics are established.

4. **Secondary/commercial sources**
   - independent corroboration;
   - historical context where primary archives are unavailable;
   - bounded triangulation;
   - investigation of source/publication conventions.

A lower-ranked source must not silently define a concept when a suitable higher-ranked primary source exists.

---

## Important distinction: authority versus analytical population

This rule does **not** mean every numerical database query must first be reproduced from an official source.

A statement such as:

> Database v4 contains 111,634 governed Great Britain race occurrences.

is a statement about the Inside Rails database and can be established from the database itself.

A statement such as:

> Great Britain staged exactly 111,634 races over the period.

is a claim about the real official racing population and requires evidence that the Inside Rails population is complete against an authoritative official source.

Likewise:

- the database can establish which values occur in `race_type_raw`;
- it cannot by itself establish what British racing officially means by Flat, Jump, Hurdle, Chase or National Hunt Flat;
- the database can establish the distribution of `age_band_raw`;
- it cannot by itself establish the complete official eligibility rule represented by an age condition;
- the database can show `rating_band_raw = 0-75`;
- it cannot by itself prove that `0-75` is the BHA's formal programmed rating band.

Always label database observations as database/source observations until official equivalence has been established.

---

## Source-specific questions are the exception

If the bounded question is specifically about a source or project artifact, that object is the primary thing being studied.

Examples:

- What does Source Version 1 contain?
- Does Database v4 reproduce BHA `ageLimit` correctly?
- How does Racing Post display a formal BHA rating band?
- Which Source Version 1 race occurrences are missing from a governed view?

In those cases it is legitimate to inspect the relevant source first, but claims about the underlying sport must still be checked against the appropriate official authority.

---

## Great Britain working pattern

For current Great Britain conceptual studies, the default workflow is:

> **BHA meaning → BHA structured representation → Inside Rails representation → population analysis → exceptions → primary verification of exceptions.**

For example, when studying sex restriction:

1. establish from BHA material what sex restrictions mean and what eligibility they govern;
2. inspect BHA structured `sexLimit` values and concrete official races;
3. only then compare with Inside Rails `sex_rest_raw` / governed equivalents;
4. test population-wide runner compliance;
5. investigate exceptions using primary official race conditions/results before treating them as sporting anomalies or source errors.

---

## Primary-source choice

"Primary source" means the source with first-hand authority for the fact being established, not simply any official-looking website.

Prefer, where relevant:

- BHA for British Rules of Racing, race programming, fixture administration, official results, ratings, handicapping and regulatory concepts;
- the official racecourse/operator for its own physical racecourse/course configuration when it is the direct authority and BHA material is less specific;
- official stewarding or disciplinary records for incidents;
- the responsible jurisdiction authority for non-British racing.

If the best primary source is unavailable, record that limitation explicitly and use the strongest available alternative without upgrading it to primary status.

---

## Structured official data is evidence, not self-interpreting truth

An official API field name does not remove the need to understand the governing concept.

Use rules/terminology to determine what the field is intended to represent, then use official structured data to see how that concept is encoded in actual records.

Example:

- BHA rules/conditions establish the age-eligibility concept;
- BHA `ageLimit` shows the structured race-level representation;
- runner eligibility may still depend on contextual rules such as Southern Hemisphere age treatment;
- Inside Rails can then be tested against that official structure.

---

## Audit rule for existing work

All previously completed substantive studies must be retrospectively classified against this rule before their conclusions are treated as publication-ready.

Use four audit statuses:

1. **primary-grounded** — sporting/administrative meaning was established from suitable primary official evidence first;
2. **primary-grounded before conclusion** — exploration may have started elsewhere, but the material conclusion was independently established from primary evidence before closeout;
3. **targeted revalidation required** — numerical/database findings remain usable, but one or more semantic or real-world claims need primary-source confirmation or tighter wording;
4. **reopen** — a material conclusion depends on a third-party/database interpretation that has not been established from suitable primary evidence.

Do not rerun a study merely to make its historical discovery order look cleaner. The purpose of the audit is to determine whether the final conclusion is adequately grounded and, where necessary, add the missing primary evidence or qualify the claim.

---

## Publication rule

No reader-facing statement about what British racing officially means, requires or permits should rely solely on:

- a Source Version 1 field name;
- an Inside Rails governed column;
- a commercial racing publication;
- a source-derived pattern;
- an inferred relationship between columns.

The publication evidence chain should make clear which layer supports which claim:

> official concept → official record/representation → Inside Rails observation/analysis.

This does not require publishing reproduction instructions, API mechanics or the full internal research workflow. It requires the published claim to be defensible from authoritative evidence.

---

## Relationship to database governance

Primary-source-first does not mean "put all BHA data in the database".

Use official information in the smallest correct way:

- bounded verification;
- study-specific official dataset/API call;
- governed integration only when correctness-critical or clearly reusable.

The accepted database remains immutable. Discovering a better official source does not automatically trigger a new database release.

---

## Stop condition

If an analysis reaches a sporting or administrative concept whose official meaning has not been established, stop interpreting the database field and establish the primary-source meaning first.

Do not fill the semantic gap by guessing from column names, observed values or commercial presentation.
