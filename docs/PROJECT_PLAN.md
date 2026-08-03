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

Established course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, complete field governance, and race classification and eligibility.

Notebook 08 retains one deliberate governed validator failure for the malformed standalone source value `F`.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed age, sex and headgear rules, including exact verification-backed contamination corrections and source-specific eyecover normalisation.

### Notebook 18 — Ratings semantics and availability

**Status:** fully closed.

Governed separate nullable meanings for `or`, `rpr` and `ts`, exact unavailable-value treatment and the isolated invalid `rpr = 775` source row.

### Notebook 19 — Horse and pedigree identity

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed rules:

- preserve raw `horse`, `sire`, `dam` and `damsire` values;
- do not use raw `horse` as a permanent natural key;
- treat exact-label reuse and inconsistent pedigree assertions separately;
- apply only bounded evidence-backed pedigree corrections;
- split 261 confirmed same-label histories into provisional source-internal occurrences;
- preserve five unresolved boundaries without guessing;
- persist governed transitions and provisional occurrences outside the notebook.

Recorded closeout validation:

- focused horse-identity tests passed;
- manual-verification register passed across 39 governed rows before Notebook 20 promotion;
- independent validator matched all Notebook 19 population baselines;
- 353 governed transitions partitioned into 87 `Corrected`, 261 `Different horse` and 5 `Unresolved`;
- 611 provisional source-internal horse occurrences were written, reloaded and committed.

### Notebook 20 — Connections and ownership identity

**Status:** fully closed for source-field semantics, blank governance and bounded supplementation. Global participant entity resolution remains a separate mandatory downstream study.

Governed rules:

- preserve raw `jockey`, `trainer` and `owner` labels as source assertions rather than canonical entities;
- do not split partnerships, syndicates or shared surnames automatically;
- supplement only an exact blank `(source_rowid, source_field)` target backed by confirmed external evidence;
- preserve conflicting and insufficient-evidence blanks as unresolved;
- fail rather than overwrite a populated source value;
- retain verification identifiers, evidence locators, confidence and database action for every governed decision.

Recorded closeout validation:

- 46 raw blank field occurrences across 44 source rows;
- 28 confirmed source supplementations;
- 18 unresolved blanks preserved;
- focused tests passed: 18;
- manual-verification register passed across 85 governed rows;
- independent source-wide connection validator passed;
- permanent reference data and the Notebook 20 closeout record are committed.

Notebook 20 does **not** establish that equal labels identify the same real participant, or that different labels identify different participants. Direct career aggregation by raw or merely normalised connection label is therefore not authorised.

The complete repository suite remains deferred until the end of the source-field series or repair branch.

## Remaining source-field study

Only one bounded study remains:

1. comments and embedded information — `comment`.

This is a planning unit rather than a commitment to a predetermined notebook shape. The study should remain bounded around field meaning, embedded structured information, preservation rules and any safely extractable derived features.

## Current next action

### Begin comments and embedded information

Bound the final source-field study around `comment`.

Establish:

- field coverage, blanks and exact-text repetition;
- whether comments are runner-level, race-level or mixed assertions;
- punctuation, abbreviations, symbols and source-specific templates;
- embedded finishing, positional, equipment, incident, pace or performance information;
- which elements duplicate structured fields and which add genuinely new information;
- whether any extraction can be deterministic, reversible and independently validated;
- what must remain preserved as free text;
- what licensing or publication constraints apply to derived examples.

Do not run the complete repository suite until this final study is closed.

## End-of-series closeout

After the final `comment` study:

1. close that notebook under the standard procedure;
2. update the complete field-governance register;
3. run the complete repository test suite;
4. run the all-validator sweep, preserving Notebook 08's deliberate governed failure as expected evidence;
5. repair any cross-notebook integration defects;
6. reconcile README, project plan, audit and lessons learned;
7. verify a clean local tree and synchronized remote branch;
8. begin the participant identity studies as the first Phase 3 work.

## Mandatory pre-database authority gate

Before physical database construction begins:

1. check all responses from studbooks and racing authorities contacted during Notebook 19;
2. revisit the five unresolved horse/pedigree cases;
3. update the specialist governance and manual-verification records where new evidence changes a decision;
4. rerun the focused horse-identity tests and independent validator;
5. regenerate, reload and recommit the governed transition and occurrence outputs;
6. preserve any unanswered case as unresolved rather than guessing;
7. record completion of this gate in the project documentation.

Database construction must not proceed until this check has been completed and recorded.

## Mandatory participant identity gate

This gate begins **immediately after Notebook 21 and the end-of-series repository-wide validation sweep**. It is the first Phase 3 programme and must be completed before physical participant schema design, retrospective participant performance analysis, publication or modelling.

The planned bounded studies are:

1. **Notebook 22 — Jockey and trainer identity**: resolve individual people, aliases, initials, punctuation variants, spelling changes, same-name collisions, jurisdiction and active-period boundaries, while preserving unresolved mappings;
2. **Notebook 23 — Owner identity and ownership structures**: distinguish individuals, partnerships, syndicates, clubs, companies and other ownership entities, including compressed and changing ownership labels.

The numbering is provisional only if the final `comment` study requires a different notebook number, but the sequence is mandatory: comments closeout, repository-wide validation, jockey/trainer identity, owner identity, then physical database entity design.

Before any retrospective jockey, trainer or owner performance analysis, and before final participant tables are treated as analytical entities, complete the governed participant identity-resolution studies.

The studies must:

1. preserve every immutable raw connection label and its runner-level lineage;
2. create separate participant and ownership-entity identifiers rather than using display text as a natural key;
3. distinguish people, partnerships, syndicates, clubs, companies and other ownership forms;
4. profile exact-label reuse, punctuation variants, initials, titles, suffixes, spelling changes and compressed shared-name formats;
5. test both alias risk — one entity represented by several labels — and collision risk — several entities represented by one label;
6. use jurisdiction, role, active dates, associated horses and external authority evidence where available;
7. record every merge, split and unresolved relationship with provenance, confidence and effective scope;
8. prevent automatic cross-role merging merely because jockey, trainer or owner text matches;
9. validate that governed mappings do not overwrite source labels or conceal unresolved ambiguity;
10. produce identity-aware analytical views that can separate confirmed entity totals from unresolved label-level totals.

Until this gate is complete:

- raw-label summaries may be used only when explicitly labelled as source-label analysis;
- normalised-text summaries may be used only for exploratory candidate matching;
- no output may describe raw-label aggregates as an individual's definitive career performance;
- trainer, jockey and owner comparisons intended for publication or modelling remain blocked.

## Phase 3 — Entity and key design

Phase 3 begins with the participant identity gate, not with physical schema design.

After the source-field series, end-of-series validation, authority gate and participant identity studies:

- consolidate identity and reconstruction requirements;
- define race, runner, horse-occurrence, participant and ownership entities;
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

Potential outputs after the database is validated include research views, form-history datasets, trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Participant-level trainer, jockey and owner summaries require completion of the mandatory participant identity gate. Predictive work remains downstream of reliable source interpretation, governed identity resolution and database design.
