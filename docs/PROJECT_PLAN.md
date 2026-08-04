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
6. add focused unit tests including failure behaviour;
7. validate extracted code and governed references independently where justified;
8. document the database and update consequence;
9. produce a concise Minto-style report;
10. record decisions, uncertainty, lessons learned and next actions;
11. update the audit register, field governance, this plan and the project README;
12. commit and verify the complete closeout.

The full procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The raw SQLite database remains read-only. All source-data queries use `DATA_ROW_PREDICATE = "rowid <> 1"`.

Established source population:

- 1,851,285 governed runner rows;
- 189,043 provisional races;
- 37 source columns;
- candidate provisional race key: `date + course + off`.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status:** complete and retrospectively implemented.

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and parsing

### Notebooks 04–16

**Status:** complete and retrospectively implemented or fully closed.

Established course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, field governance, and race classification and eligibility.

Notebook 08 retains one deliberate governed validator failure for the malformed standalone source value `F`.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed age, sex and headgear rules, including exact verification-backed contamination corrections and source-specific eyecover normalisation.

### Notebook 18 — Ratings semantics and availability

**Status:** fully closed.

Governed separate nullable meanings for `or`, `rpr` and `ts`, exact unavailable-value treatment and the isolated invalid `rpr = 775` source row.

### Notebook 19 — Horse and pedigree identity

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed raw horse and pedigree labels, reversible contradiction treatment, 353 transition decisions and 611 provisional source-internal horse occurrences. Five authority-dependent cases remain governed as unresolved and subject to the pre-database authority gate.

### Notebook 20 — Connections and ownership identity

**Status:** fully closed for source-field semantics, blank governance and bounded supplementation. Global participant entity resolution remains a separate mandatory downstream study.

Governed rules preserve raw `jockey`, `trainer` and `owner` labels as source assertions, permit supplementation only for exact blank source targets backed by confirmed evidence, and preserve conflicting or insufficient-evidence blanks unresolved.

Recorded closeout result: 46 raw blank field occurrences, 28 confirmed supplementations and 18 unresolved blanks.

### Notebook 21 — Comment and embedded information

**Status:** implemented pending focused local validation and the end-of-series repository sweep.

Notebook 21 established that substantive comments are generally runner-level English-language descriptions of race position and performance. The broad meaning is consistent across inspected jurisdictions, but availability is strongly jurisdiction- and feed-dependent.

Governed rules:

- preserve the exact raw comment and physical lineage;
- preserve empty strings as source absence;
- preserve rare placeholder-like values and `A`, `B`, `V` as unresolved source states;
- permit only conservative state classification;
- do not implement a general narrative, incident, market or parenthetical parser;
- store any later extracted assertion separately with method, version, confidence and source linkage;
- report or control for jurisdiction-specific coverage before comment-derived comparison.

Recorded baselines:

- 340,394 empty-string comments;
- 238 probable-placeholder or unresolved-code rows;
- 1,510,653 substantive-text rows;
- 0 SQL nulls;
- 36 candidate jurisdictions and 0 unresolved jurisdiction assignments.

Durable implementation, focused tests, an independent source validator, persisted outputs, integration documentation, report, lessons and closeout record are committed.

## Source-field series position

The bounded source-field investigation series is analytically complete through Notebook 21.

The immediate work is no longer another source-field notebook. It is the end-of-series validation and reconciliation sweep.

## Current next action — End-of-series validation sweep

1. run Notebook 21 focused tests;
2. run `scripts/validate_comment_information.py`;
3. record exact results in `docs/NOTEBOOK_21_CLOSEOUT.md`;
4. run the complete repository test suite;
5. run every applicable independent validator;
6. preserve Notebook 08's lone governed `F` failure as expected evidence;
7. repair any cross-notebook integration defects;
8. reconcile README, project plan, audit, field governance, closeout records and lessons learned;
9. verify a clean local tree and synchronized remote branch;
10. mark Notebook 21 fully closed only after the recorded sweep passes.

## Mandatory pre-database authority gate

Before physical database construction begins:

1. check all responses from studbooks and racing authorities contacted during Notebook 19;
2. revisit the five unresolved horse/pedigree cases;
3. update specialist governance and manual-verification records where new evidence changes a decision;
4. rerun focused horse-identity tests and the independent validator;
5. regenerate, reload and recommit governed transition and occurrence outputs;
6. preserve unanswered cases as unresolved rather than guessing;
7. record completion of this gate in project documentation.

Database construction must not proceed until this check has been completed and recorded.

## Mandatory participant identity gate

This gate begins immediately after the end-of-series repository-wide validation sweep. It is the first Phase 3 programme and must be completed before physical participant schema design, retrospective participant performance analysis, publication or modelling.

Planned bounded studies:

1. **Notebook 22 — Jockey and trainer identity**: resolve people, aliases, initials, punctuation variants, spelling changes, same-name collisions, jurisdiction and active-period boundaries while preserving unresolved mappings;
2. **Notebook 23 — Owner identity and ownership structures**: distinguish individuals, partnerships, syndicates, clubs, companies and other ownership entities, including compressed and changing ownership labels.

The studies must preserve immutable raw labels and lineage, create separate entity identifiers, test alias and collision risk, record every merge/split/unresolved relationship with provenance, and prevent automatic cross-role merging.

Until this gate is complete:

- raw-label summaries may be used only when explicitly labelled as source-label analysis;
- normalised-text summaries may be used only for exploratory candidate matching;
- no output may describe raw-label aggregates as an individual's definitive career performance;
- trainer, jockey and owner comparisons intended for publication or modelling remain blocked.

## Phase 3 — Entity and key design

Phase 3 begins with participant identity, not physical schema design.

After the validation sweep, authority gate and participant identity studies:

- consolidate race, runner, horse-occurrence, participant and ownership identity requirements;
- distinguish source labels, source-internal occurrence identifiers and verified real-world identities;
- define amended-record versioning and reconciliation controls;
- decide which unresolved relationships remain nullable or quarantined.

## Phase 4 — Target architecture

Only after the evidence base is sufficient:

- define a conceptual staging model;
- select the physical database technology;
- define staging, core and analytical schemas;
- create tables, constraints and indexes;
- implement repeatable ingestion;
- preserve raw source values and technical lineage;
- add automated reconciliation and integrity tests.

## Phase 5 — Analytical products and writing

Potential outputs after the database is validated include research views, form-history datasets, identity-aware trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Comment-derived features remain future bounded studies. Predictive work remains downstream of reliable source interpretation, governed identity resolution and database design.
