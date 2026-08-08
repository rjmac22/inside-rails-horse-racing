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

**Status: fully closed, with one post-closeout authority amendment awaiting focused output regeneration.**

The completed programme governs course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree labels, connection-field blanks and comment-field states.

Retained governed limits:

- Notebook 08 preserves one unresolved raw starting-price value `F`;
- Notebook 19 has no remaining unresolved pedigree transition after the 8 August 2026 Weatherbys Ireland confirmation for `Runninsonofagun (IRE)`; the competing raw damsire assertions remain preserved and the governed analytical damsire is `Society Rock (IRE)`;
- Notebook 20 preserves 18 unresolved connection blanks;
- Notebook 21 does not authorise a general narrative parser.

The Notebook 19 authority amendment changes the expected transition partition from the historical 5 August state `91 corrected / 261 different horse / 1 unresolved` to `92 / 261 / 0`. The two validator-generated Notebook 19 processed outputs must be regenerated and reloaded locally before that amended state is accepted as fully validated.

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

## Mandatory pre-database authority gate — completed 5 August 2026; final follow-up resolved 8 August 2026

**Status: authority evidence complete; Notebook 19 post-authority output regeneration pending.**

The 5 August authority gate confirmed four bounded pedigree corrections and left `Runninsonofagun (IRE)` explicitly unresolved.

On 8 August 2026 Weatherbys Ireland Senior Pedigree Researcher Georgina Doherty confirmed that `High Society Lady (IRE)` is by `Society Rock (IRE)`. Notebook 19 decision `NB19-ID-0013` is therefore now a high-confidence bounded correction:

- raw horse: `Runninsonofagun (IRE)`;
- source sire history: `Inns Of Court (IRE)`;
- source dam history: `High Society Lady (IRE)`;
- competing raw damsire assertions: `General Monash` and `Society Rock`;
- governed damsire: `Society Rock (IRE)`;
- identity split: no.

The specialist governance reference, reusable implementation, focused tests and validator contract have been updated. The source-derived transition and occurrence outputs still require local regeneration and readback before this amendment is accepted.

## Targeted cross-notebook implementation-completeness audit — completed 5 August 2026

**Status: fully closed for its 5 August evidence state.**

The audit repaired stale closeout records, missing governed outputs, incomplete provenance enforcement, weak source-wide validation, correction-lineage gaps, an obsolete construction utility and the missing canonical race-time regeneration path.

Historical integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

The later 8 August Notebook 19 authority amendment is a new governed evidence update and does not invalidate that historical gate. It receives its own focused validation rather than rewriting the 5 August evidence.

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

## Phase 4 — Physical target architecture, candidate validation and Database v1 release

**Status: fully closed with Version 1 release accepted and promoted on 8 August 2026.**

The selected physical technology is SQLite schema version 1. The implementation includes:

- exact source-file identity enforcement;
- a complete immutable raw mirror;
- deterministic source, race and runner identifiers;
- complete core race and runner population;
- governance, import-manifest and validation-evidence tables;
- STRICT tables, foreign keys, indexes and protective triggers;
- durable candidate construction with complete cleanup after failure;
- builder persisted readback;
- a separate source-wide validator that does not trust builder counters;
- explicit separation between `built`, `validated` and `release_accepted` states;
- a tested release-copy, atomic-promotion and rollback boundary.

Preserved candidate identity:

```text
path: data/processed/database/candidates/inside_rails_v1_candidate.sqlite3
physical source records: 1,851,286
admitted runner records: 1,851,285
source race occurrences: 189,043
runner participations: 1,851,285
candidate size: 1,730,048,000 bytes
candidate SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
manifest status: built
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

Final Phase 4 repository-wide technical gate at commit `bf1d7f7b253edaf7232351e33ada92b039ca97ba`:

```text
354 passed in 18.28s
ALL 31 VALIDATORS PASSED
```

Release-boundary implementation gate on 8 August 2026:

```text
focused promotion tests: 6 passed in 0.64s
complete repository tests: 360 passed in 15.36s
```

Accepted Version 1 release:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
size: 1,730,048,000 bytes
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
manifest status: release_accepted
validation-result rows: 7
quick_check: ok
foreign_key_check rows: 0
SQLite application_id: 1230130259
SQLite user_version: 1
candidate hash unchanged during promotion: true
```

Evidence:

- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_LESSONS_LEARNED.md`;
- `docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`;
- `docs/PHASE_4_RELEASE_ACCEPTANCE_AND_PROMOTION_CONTRACT.md`;
- `docs/PHASE_4_RELEASE_ACCEPTANCE_EVIDENCE.md`.

The accepted release is the default read-only analytical database for reader-facing studies. The validated candidate remains unchanged as evidence and rollback material.

## Phase 5 — Analytical products and writing

**Status: in progress using accepted Database v1, with a bounded Database v2 governed-integration inventory underway where studies require previously external governed outputs.**

### Study 01 — field size and race predictability

The first reader-facing study asks:

> What relationship, if any, exists between field size and the predictability of British horse races?

Established so far:

- 111,634 British races in the accepted study population before the walkover exclusion;
- field-size mode 8 and median 9;
- approximately 74.0% of British races have 6–12 runners;
- approximately 89.8% have 5–14 runners;
- 21 one-runner British races were inspected and confirmed as genuine walkovers;
- the competitive British population is therefore 111,613 races.

A temporary diagnostic branch was opened after copied notebook output appeared to contain `Walkover<br><br><br>`. That branch is closed:

- Source Version 1 contains zero admitted comments with a literal `<` character;
- the accepted Database v1 value is exactly `Walkover`;
- the apparent markup came from rendered-output / copy-paste transport;
- no comment parser, HTML cleaner, `comment_plain_text` field or comment database migration is required.

This field consequence is recorded in `docs/COMMENT_INFORMATION_INTEGRATION.md`, and the workflow safeguard is recorded in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The study exposed that Database v1 deliberately materialised only the minimum structural core while many reusable governed Notebook 04–22 outputs remained external. Notebook 25 therefore inventories those outputs before one coherent Database v2 design. Database v1 remains immutable and no v2 schema or write is authorised until that inventory is complete.

Potential later outputs include research views, form-history datasets, identity-aware trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

The immediate study programme remains question-led rather than schema-led. A study-specific derivation does not automatically belong in the database; only reusable or correctness-critical infrastructure should trigger a database-governance escalation.

Comment-derived features remain future bounded studies. Predictive work remains downstream of reliable source interpretation, governed identity resolution and accepted database infrastructure.
