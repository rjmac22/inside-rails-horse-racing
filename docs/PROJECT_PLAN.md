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

## End-of-source-field-series validation — completed 4 August 2026

The complete repository test suite and every then-discovered independent validator were run after Notebook 21.

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

## Participant identity programme

### Consolidated Notebook 22 — jockey, trainer and owner identity

**Status: fully closed on 4 August 2026.**

The programme preserves immutable raw labels and row lineage while adding a separate conservative participant-identity layer.

Established governed results:

- 7,917 jockey labels profiled;
- 212 jockey candidate groups and 216 candidate relationships retained for review;
- one confirmed provisional jockey label identity: `Mlle Marie Velon` / `Mme Marie Velon`;
- one confirmed distinct-person jockey relationship: `Miss B ONeill` / `Mr B ONeill`;
- 214 jockey relationships retained unresolved;
- two direct jockey label mappings to `JOCKEY-PROVISIONAL-0001`;
- 26 bounded provisional trainer transitions covering 52 labels and 6,350 source rows;
- 936 owner token-multiset candidate groups;
- 41 same-race-supported provisional ownership compositions covering 95 labels and 9,788 source rows;
- 895 owner groups retained unresolved.

The owner-identity and ownership-structure work originally scheduled as Notebook 23 was completed inside the consolidated Notebook 22 archival investigation. A separate Notebook 23 is not required.

Focused test evidence:

```text
14 passed in 0.61s
```

The final closeout audit found two implementation gaps:

1. the accepted Marie Velon decision was persisted in the review queue but lacked a directly usable label-to-identity mapping file;
2. the jockey validator checked the source baseline and queue length but did not enforce exact accepted, distinct and unresolved decision closure or decisive external provenance.

The repair added `data/processed/jockey_identity/jockey_provisional_identity_mapping.csv` and strengthened `scripts/validate_participant_identity.py` to enforce all 216 candidate pairs, the exact `1 / 1 / 214` decision partition, both decisive verification records, unresolved preservation actions and the exact two-row mapping.

Final strengthened validator evidence on 4 August 2026:

```text
jockeys: 7,917 labels; 212 groups; 216 candidate relationships; 1 accepted; 1 distinct; 214 unresolved
trainers: 10,708 labels; 26 accepted groups; 6,350 mapped rows
owners: 98,234 labels; 41 accepted groups; 9,788 mapped rows; 895 unresolved groups
participant identity validation: PASS
```

Retained controls:

- raw-label summaries must remain explicitly labelled as source-label analysis;
- normalised text is a candidate-generation aid, not a definitive identity key;
- unresolved relationships remain preserved rather than guessed;
- unsupported automatic cross-role merging is prohibited;
- participant-level publication or modelling must use the governed identity layer and state its limits.

The complete repository test suite and all-validator sweep remain deferred until the next appropriate end-of-series or repair-branch gate.

## Targeted cross-notebook implementation-completeness audit

**Status: queued before physical database construction.**

This is a repository-level review of the existing notebook implementations, not a reopening or rerun of every notebook.

The audit must check for the specific closure defects exposed by Notebook 22:

1. accepted decisions that exist only in review or decision tables without a directly usable governed mapping or output;
2. validators that prove only file existence or row counts without checking the governed decisions, partitions, exceptions and provenance they claim to protect;
3. external evidence mentioned in notebooks or reports but not preserved with identifiers, locators, access dates, confidence and permitted actions;
4. documentation claiming full closure where the implementation artifacts do not support the stated database consequence;
5. accepted, unresolved and rejected populations that are not explicitly separated or could overlap in downstream joins.

The audit should begin from the existing closeout documents, integration contracts, governed outputs, tests and validators. It must not rerun archival notebooks or recreate completed implementations unless a concrete defect is found.

Any defect found should be repaired through one bounded change, focused validation and documented evidence. A clean audit should be recorded without manufacturing additional work.

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

## Phase 3 — Entity and key design

After the Notebook 19 authority gate and targeted cross-notebook implementation-completeness audit:

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
