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

## Database admission gate

Every future staging, core or analytical database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

The standing rule is:

> No validated output, no database write. No partial success. The last known-good database remains intact.

Candidate outputs must be built outside the live database, validated source-wide, persisted and read back, loaded transactionally into temporary or replacement structures, and validated again after load. Unknown or changed data must fail closed for investigation, remain explicitly unresolved or be quarantined; it must never be silently guessed, discarded or partially loaded.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status: fully closed.**

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and source-field governance

### Notebooks 04–21

**Status: fully closed.**

The completed programme governs course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree labels, connection-field blanks and comment-field states.

Retained governed limits:

- Notebook 08 preserves one unresolved raw starting-price value `F`;
- Notebook 19 preserves one unresolved authority-dependent horse/pedigree transition for `Runninsonofagun (IRE)`;
- Notebook 20 preserves 18 unresolved connection blanks;
- Notebook 21 does not authorise a general narrative parser.

## End-of-source-field-series validation — completed 4 August 2026

The complete repository test suite and every then-discovered independent validator were run after Notebook 21.

Final evidence:

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

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

**Status: fully closed.**

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

The closeout repair added `data/processed/jockey_identity/jockey_provisional_identity_mapping.csv` and strengthened `scripts/validate_participant_identity.py` to enforce all 216 candidate pairs, the exact `1 / 1 / 214` decision partition, both decisive verification records, unresolved preservation actions and the exact two-row mapping.

Retained controls:

- raw-label summaries must remain explicitly labelled as source-label analysis;
- normalised text is a candidate-generation aid, not a definitive identity key;
- unresolved relationships remain preserved rather than guessed;
- unsupported automatic cross-role merging is prohibited;
- participant-level publication or modelling must use the governed identity layer and state its limits.

## Mandatory pre-database authority gate — completed 5 August 2026

**Status: completed.**

All available responses from studbooks and racing authorities contacted during Notebook 19 were checked before physical database construction.

Authority evidence confirmed bounded pedigree corrections for:

- `Almavillalobas (GB)`;
- `Colwyn Bay (FR)`;
- `Diamond Tipp (IRE)`;
- `LAziza Des Places (FR)`.

Weatherbys Ireland had not replied about `Runninsonofagun (IRE)` by the gate date. That case remains explicitly `Unresolved`; its competing raw assertions are preserved and no governed pedigree is guessed.

Final governed transition results are:

```text
Corrected: 91
Different horse: 261
Unresolved: 1
provisional occurrences: 611
```

Focused tests and independent source-wide validation passed against the immutable source and wrote and reloaded both governed outputs.

## Targeted cross-notebook implementation-completeness audit — completed 5 August 2026

**Status: fully closed.**

The audit reviewed the existing notebook implementations without reopening their analytical investigations. It repaired stale closeout records, missing governed outputs, incomplete provenance enforcement, weak source-wide validation, correction-lineage gaps, an obsolete construction utility and the missing canonical race-time regeneration path.

Notebook 11 was accepted after the full 189,043-race output built, wrote, reloaded and independently reconciled to the source with the exact settled totals of 169,465 resolved and 19,578 unresolved races.

Every repair unit was reviewed individually before integration. The accepted content was consolidated on `audit/retrospective-implementation-integration`.

Final integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

The 28-validator sweep covered every current `scripts/validate_*.py` file. No genuine integration defect was found.

## Phase 3 — Entity and key design

**Status: next active phase.**

The next bounded work is to:

- consolidate race, runner, horse-occurrence, participant and ownership identity requirements;
- distinguish source labels, source-internal occurrence identifiers and verified real-world identities;
- define amended-record versioning and reconciliation controls;
- decide which unresolved relationships remain nullable or quarantined;
- define the import manifest and validation-evidence record required by the database admission gate;
- produce the conceptual entity and key design before selecting a physical database technology.

## Phase 4 — Target architecture

Only after the entity and key design is accepted:

- select the physical database technology;
- define staging, core and analytical schemas;
- create tables, constraints and indexes;
- implement repeatable fail-closed ingestion;
- preserve raw source values and technical lineage;
- build into temporary or versioned structures;
- add automated source-to-output, cross-table and post-load reconciliation;
- commit or atomically swap the new database only after every gate passes.

## Phase 5 — Analytical products and writing

Potential outputs after the database is validated include research views, form-history datasets, identity-aware trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Comment-derived features remain future bounded studies. Predictive work remains downstream of reliable source interpretation, governed identity resolution and database design.
