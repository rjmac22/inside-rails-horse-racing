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
7. validate extracted code and governed references independently;
8. document the database and update consequence;
9. produce a concise Minto-style report;
10. record decisions, uncertainty and lessons learned;
11. update the audit register, field governance, this plan and the README;
12. commit and verify the complete closeout.

The full procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The raw SQLite database remains read-only. All source-data queries use `rowid <> 1`.

Established source population:

- 1,851,285 governed runner rows;
- 189,043 provisional races;
- 37 source columns;
- candidate provisional race key: `date + course + off`.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status: fully closed.**

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and source-field governance

### Notebooks 04–21

**Status: fully closed on the retrospective implementation branch.**

The completed programme governs course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree labels, connection-field blanks and comment-field states.

Retained governed limits:

- Notebook 08 preserves one unresolved raw starting-price value `F`;
- Notebook 19 preserves five unresolved authority-dependent horse/pedigree transitions;
- Notebook 20 preserves 18 unresolved connection blanks;
- Notebook 21 does not authorise a general narrative parser.

## End-of-series validation — completed 4 August 2026

The complete repository test suite and every discovered independent validator were run after Notebook 21.

Final evidence:

```text
256 passed in 0.96s
ALL VALIDATORS PASSED
```

The validator sweep covered 26 scripts, including source-wide checks over the immutable 1,851,285-row source population.

The sweep found and repaired:

1. a prize-money minor-unit fall-through defect;
2. a source-field status-loader compatibility defect.

The final field-governance reconciliation passed with:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 source fields require raw preservation and match the SQLite schema names, order and declared types.

## Mandatory pre-database authority gate

**Status: next operational gate.**

Before physical database construction begins:

1. check all responses from studbooks and racing authorities contacted during Notebook 19;
2. revisit the five unresolved horse/pedigree cases;
3. update specialist governance and manual-verification records where new evidence changes a decision;
4. rerun focused horse-identity tests and the independent validator;
5. regenerate, reload and recommit governed transition and occurrence outputs;
6. preserve unanswered cases as unresolved rather than guessing;
7. record completion of this gate in project documentation.

Database construction must not proceed until this check has been completed and recorded.

## Mandatory participant identity programme

This is the next bounded analytical programme and must be completed before physical participant schema design, participant-level retrospective analysis, publication or modelling.

### Notebook 22 — Jockey and trainer identity

Resolve people, aliases, initials, punctuation variants, spelling changes, same-name collisions, jurisdiction and active-period boundaries while preserving unresolved mappings.

### Notebook 23 — Owner identity and ownership structures

Distinguish individuals, partnerships, syndicates, clubs, companies and other ownership entities, including compressed and changing ownership labels.

Both studies must:

- preserve immutable raw labels and row lineage;
- create separate entity identifiers;
- test alias and collision risk;
- record every merge, split and unresolved relationship with provenance;
- prevent unsupported automatic cross-role merging.

Until this programme is complete:

- raw-label summaries may be used only when explicitly labelled as source-label analysis;
- normalised-text summaries may be used only for exploratory candidate matching;
- no output may describe raw-label aggregates as an individual's definitive career performance;
- trainer, jockey and owner comparisons intended for publication or modelling remain blocked.

## Phase 3 — Entity and key design

After the authority gate and participant identity studies:

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
