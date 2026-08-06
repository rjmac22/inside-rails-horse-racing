# Inside Rails Project Plan

## Objective

Build a documented, reproducible and professionally structured horse-racing analytical database from the supplied third-party source products.

The project is evidence-led. Profiling and domain interpretation come before cleaning, schema design or predictive modelling.

## Standing method

For each substantive investigation:

1. state one bounded question;
2. declare the source and grain under investigation;
3. separate profiling evidence from interpretation;
4. avoid irreversible cleaning decisions inside exploratory work;
5. extract stable reusable plumbing only after it works;
6. add focused unit tests including failure behaviour;
7. validate extracted code and governed references independently;
8. document the database consequence;
9. produce a concise reader-facing report where applicable;
10. record decisions, uncertainty and lessons learned;
11. update the audit record, project plan and README;
12. commit and verify the complete closeout.

The full notebook procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The raw SQLite database remains read-only. All source-data queries use `rowid <> 1`.

Established Source Version 1 population:

- 1,851,286 physical source records;
- 1,851,285 admitted runner records;
- one retained excluded physical row;
- 189,043 reconstructed source race occurrences;
- 37 source columns;
- authorised Source Version 1 race key: exact raw `date + course + off`.

## Database admission gate

Every staging, core or analytical database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

The standing rule is:

> No validated output, no database write. No partial success. The last known-good database remains intact.

Candidates must be built away from any live database, validated source-wide, persisted and read back, and accepted through a separate explicit gate. Unknown or changed data must fail closed, remain explicitly unresolved or be quarantined; it must never be silently guessed, discarded or partially loaded.

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

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

The sweep found and repaired a prize-money minor-unit fall-through defect and a source-field status-loader compatibility defect.

Final field-governance reconciliation:

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

Established governed results include:

- 7,917 jockey labels;
- 212 jockey candidate groups and 216 candidate relationships;
- one confirmed provisional jockey label identity;
- one confirmed distinct-person jockey relationship;
- 214 jockey relationships retained unresolved;
- 26 bounded provisional trainer transitions;
- 41 same-race-supported provisional ownership compositions;
- 895 owner groups retained unresolved.

The owner-identity scope originally scheduled as Notebook 23 was completed inside Notebook 22. A separate Notebook 23 is not required.

## Mandatory pre-database authority gate — completed 5 August 2026

**Status: completed.**

Available authority responses were checked before physical database construction. Four bounded pedigree corrections were confirmed. `Runninsonofagun (IRE)` remains explicitly unresolved; its competing raw assertions are preserved and no governed pedigree is guessed.

## Targeted cross-notebook implementation-completeness audit — completed 5 August 2026

**Status: fully closed.**

The audit repaired stale closeout records, missing governed outputs, incomplete provenance enforcement, weak source-wide validation, correction-lineage gaps, an obsolete construction utility and the missing canonical race-time regeneration path.

Final integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

## Phase 3 — Minimum stable entity and key design

**Status: completed and evidenced on 6 August 2026.**

Phase 3 established the bounded minimum stable core needed before field-level analytical extensions:

- immutable physical source lineage;
- deterministic source-version, relation, record, race and runner codes;
- source race occurrences grouped by exact raw `date + course + off`;
- one runner participation for each admitted source record;
- explicit governance method and release records;
- import-manifest and validation-result structures;
- fail-closed lifecycle and acceptance-state constraints;
- preservation of unresolved identity and semantic work outside the minimum structural core.

Primary governing documents:

- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`.

## Phase 4 — Physical target architecture and complete disposable candidate

**Status: complete through independently validated disposable candidate and final repository-wide technical gate; no database release accepted.**

The selected physical technology is SQLite schema version 1. The implementation now includes:

- exact source-file identity enforcement;
- a complete immutable raw mirror;
- deterministic source, race and runner identifiers;
- complete core race and runner population;
- governance, import-manifest and validation-evidence tables;
- STRICT tables, foreign keys, indexes and protective triggers;
- durable candidate construction with complete cleanup after failure;
- builder persisted readback;
- a separate source-wide validator that does not trust builder counters;
- explicit separation between `built`, `validated` and `release_accepted` states.

Complete candidate results:

```text
physical source records: 1,851,286
admitted runner records: 1,851,285
source race occurrences: 189,043
runner participations: 1,851,285
candidate size: 1,730,048,000 bytes
candidate SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
manifest status: built
release accepted: false
```

Independent validation reconciled:

```text
raw records: 1,851,286
raw values: 68,497,582
SQLite storage classes: 68,497,582
race codes, groupings and runner counts: 189,043 each
runner codes and source lineage: 1,851,285 each
```

Final bounded database gate:

```text
72 passed in 14.54s
```

Final repository-wide technical gate at commit `bf1d7f7b253edaf7232351e33ada92b039ca97ba`:

```text
354 passed in 18.28s
ALL 31 VALIDATORS PASSED
```

Evidence:

- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_LESSONS_LEARNED.md`;
- `docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`.

The generated database remains an ignored, disposable candidate. It has not been promoted, installed as an active database or marked `release_accepted`.

## Next bounded stage — release acceptance and analytical extension planning

The final repository-wide technical gate is complete for the current candidate and repository commit. It is evidence for a future release decision, not the release decision itself.

Before any promotion or active-database replacement, the project must separately define and execute the release-acceptance boundary. That stage must cover, at minimum:

- how independent and repository-wide validation evidence is durably associated with the candidate;
- active-release resolution and atomic promotion or replacement;
- prior-release preservation and rollback behaviour;
- the location and naming of the accepted analytical database;
- the exact authorised transition from `built` to any later manifest state;
- explicit user review and acceptance before branch movement, merge or promotion.

Any code or governed-reference change made while implementing that boundary must trigger the appropriate focused tests and a fresh final repository-wide technical gate before release acceptance.

Only after that boundary is accepted should governed field-level and identity-aware analytical structures be added to the minimum core.

## Phase 5 — Analytical products and writing

Potential outputs after database release acceptance include research views, form-history datasets, identity-aware trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Comment-derived features remain future bounded studies. Predictive work remains downstream of reliable source interpretation, governed identity resolution and accepted database infrastructure.
