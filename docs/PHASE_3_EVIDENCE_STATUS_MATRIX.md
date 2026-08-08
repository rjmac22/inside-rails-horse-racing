# Phase 3 Evidence Status Matrix

## Status

Accepted Phase 3 evidence, design and implementation-status register.

This document applies the maturity states and physical-implementation gate defined in:

- `docs/PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`;
- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

It separates four questions that must not be collapsed:

1. Has the actual source evidence been inspected?
2. Has its meaning and limitation been established?
3. Has a governed conceptual model been accepted?
4. Has physical database implementation been explicitly authorised?

The current answer to question 4 is:

- **yes for the minimum stable structural core defined in `PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;**
- **no for every governed extension, higher racing abstraction and deferred enrichment unless a later accepted brief states otherwise.**

No table, column, parser, relationship, migration or ingestion process is authorised merely because a notebook is closed or a conceptual design document exists.

---

## 1. Status vocabulary

### Evidence maturity

- **Uninspected** — no adequate source or enrichment study exists.
- **Profiled** — distributions and examples are known, but semantic meaning is incomplete.
- **Semantically investigated** — a focused study established the supported meaning, limitations and unresolved cases.
- **Analytically justified** — a defined accepted use requires the concept and the evidence is adequate.
- **Conceptually designed** — governed distinctions and identity boundaries have been accepted.
- **Implementation authorised** — an accepted bounded implementation brief permits physical work.
- **Implemented and validated** — reusable implementation, tests, source-wide validation, provenance and limitations are complete.

A topic may have reusable notebook-era parsing or governed outputs at **implemented and validated** maturity while its physical database representation remains unauthorised.

### Physical database status

- **Implementation authorised** — physical work may proceed only within the accepted brief.
- **Eligible for bounded extension brief** — evidence appears sufficient to draft a proposal, but no physical extension is yet authorised.
- **Further focused study required** — evidence, analytical need or minimum representation is insufficient.
- **Deferred enrichment** — the project does not hold the required dataset and must not create speculative structures.
- **Not authorised** — no physical work may begin.

---

## 2. Authorised stable core

The following concepts are authorised for physical architecture selection, schema design, implementation and Source Version 1 database construction under `PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`.

The authorisation does not extend beyond the boundary stated in the final column.

| Topic | Principal evidence | Evidence maturity | Physical database status | Authorised boundary |
|---|---|---|---|---|
| Source provider and source product | Notebooks 00–02; project methodology; source-lineage decisions | Analytically justified and conceptually designed | **Implementation authorised** | Minimum Source Version 1 metadata only; no speculative provider-role or product-history model. |
| Exact source version | Notebooks 01–02; immutable-file controls; database import gate | Implemented and validated as source-governance practice | **Implementation authorised** | Independent identifier, file hash, size, retrieval metadata, schema fingerprint, integrity and population baselines. |
| Source relation | Notebooks 01–02; governed `data` relation and 37-field schema | Implemented and validated as source-governance practice | **Implementation authorised** | The actual Source Version 1 SQLite `data` relation only. |
| Immutable physical source record | Notebooks 01–03; 1,851,286 physical rows; 37-field preservation | Implemented and validated at source-governance level | **Implementation authorised** | Preserve every physical row and all 37 raw values; retain `rowid = 1` as explicitly excluded evidence. |
| Source-record admission state | Governed predicate `rowid <> 1`; complete source baseline | Implemented and validated | **Implementation authorised** | Exactly 1,851,285 admitted runner-bearing records and one retained excluded physical record. |
| Source race occurrence | Notebook 03; 189,043 reconciled source races; grouping `date + course + off` | Implemented and validated for Source Version 1 | **Implementation authorised** | Source-version-scoped race occurrence only; no real-world race, meeting or series identity. |
| Runner participation | Notebooks 01–03 and 14; one admitted source row per runner | Implemented and validated for Source Version 1 | **Implementation authorised** | Independent runner identity linked one-to-one to an admitted source record and to one source race occurrence. |
| Raw-value recoverability | Notebooks 02 and 10; 37-field governance register and schema validation | Implemented and validated | **Implementation authorised** | Exact raw round trip; no cleaning, correction or semantic promotion in the stable core. |
| Governance release and structural provenance | Closed notebooks; governed outputs; final integrated validation | Analytically justified and conceptually designed | **Implementation authorised** | Minimum release, code, method and evidence references needed to reproduce structural derivations. |
| Import manifest and validation evidence | `DATABASE_IMPORT_VALIDATION_GATE.md`; complete test and validator evidence | Analytically justified and conceptually required | **Implementation authorised** | Candidate-build identity, source fingerprint, validation results, transactional status and last-known-good protection. |

### Stable-core consequence

Phase 4 may now:

- compare and select the physical database technology;
- define the stable-core schema and constraints;
- implement a complete deterministic Source Version 1 builder;
- implement candidate-build, readback, post-load and atomic-activation controls;
- build and validate the first database.

The accepted boundary remains:

- source lineage;
- immutable physical source records;
- explicit admission state;
- source race occurrences;
- runner participations;
- exact raw-value recoverability;
- structural governance;
- import and validation evidence.

Nothing else is authorised by this section.

---

## 3. Strongly evidenced governed extensions

The source fields and governed outputs below have completed investigations and reusable validation. Their database representations remain unauthorised until a defined analysis or operational requirement justifies a separate bounded extension brief.

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Course label, jurisdiction and surface context | Notebooks 04 and 09 | Implemented and validated as governed references | Conceptually designed within course identity work | **Eligible for bounded extension brief** | Define the first analytical use and implement only evidenced current-source distinctions. |
| Course location and timezone | Notebook 12; complete 395-identity timezone reference and provenance validation | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Decide whether an accepted analysis requires them. |
| Governed race time | Notebook 11; 189,043-race output; 169,465 resolved and 19,578 unresolved | Implemented and validated | Conceptually designed as an attribute, not identity | **Eligible for bounded extension brief** | Specify the accepted use and required local, UTC and unresolved states. |
| Finishing positions and non-finish outcomes | Notebook 05 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Restrict implementation to source-supported result states. |
| Beaten distance | Notebook 15 | Implemented and validated | Covered by result safeguards | **Eligible for bounded extension brief** | Define exact analytical use and preserve source-specific semantics and supplementation provenance. |
| Race distance | Notebook 06 | Implemented and validated | Covered by race-conditions safeguards | **Eligible for bounded extension brief** | Implement only confirmed raw and governed representations and failure states. |
| Carried weight | Notebook 07 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Implement only the actual established Source Version 1 meaning. |
| Prize money | Notebook 13 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Restrict scope to evidenced runner-level values, currency and unresolved cases. |
| Runner counts, numbers and entries | Notebook 14 | Implemented and validated | Partly covered by runner and race design | **Eligible for bounded extension brief** | Distinguish stored facts, reconciliations and derived counts. |
| Race classification and eligibility | Notebook 16 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Implement only accepted field and external decisions; retain non-automatic candidates. |
| Runner characteristics and source equipment fields | Notebook 17 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Limit scope to investigated fields and confirmed abbreviations. |
| Ratings fields | Notebook 18 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Implement only systems, timings and meanings established by the study. |
| Connection-field blank governance | Notebook 20; 28 supplementations and 18 unresolved blanks | Implemented and validated | Supports participant and ownership evidence layers | **Eligible for bounded extension brief** | Define whether an accepted product requires governed supplements. |
| Comment-field states | Notebook 21 | Implemented and validated for bounded classification | No broad narrative model authorised | **Further analytical justification required** | Identify a specific study; a general narrative parser remains prohibited. |

Completed notebook work proves that these interpretations are reproducible. It does not prove that every result belongs in the first physical database.

---

## 4. Identity extensions

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Provisional horse occurrence | Notebook 19; 91 corrected, 261 different horse, one unresolved; 611 occurrences | Implemented and validated as source-internal identity | Conceptually designed | **Eligible for bounded extension brief** | Define the immediate horse-level analysis and preserve release-scoped provisional status. |
| Runner-to-horse-occurrence assignment | Notebook 19 governed outputs and validators | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define append-only release handling without implying official identity. |
| Jockey provisional identity | Notebook 22; exact `1 / 1 / 214` decision partition and two-row mapping | Implemented and validated for bounded decisions | Conceptually designed | **Eligible for bounded extension brief** | Demonstrate a product need and preserve unresolved candidates. |
| Trainer provisional transitions | Notebook 22; 26 transitions covering 52 labels and 6,350 rows | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define the analysis and retain role-, evidence- and release-scoped status. |
| Ownership compositions | Notebook 22; 41 supported compositions and 895 unresolved groups | Implemented and validated for the bounded supported set | Conceptually designed | **Eligible for bounded extension brief** | Implement only for an accepted owner-level analysis; constituent splitting needs another study. |
| Official/global horse, jockey, trainer or owner identity | No official registry dataset held | Uninspected enrichment | Deferred relationship safeguards only | **Deferred enrichment** | Inspect an obtainable official or licensed identity dataset. |
| Cross-provider identity reconciliation | Only one governed primary source version is in scope | Uninspected | Conceptual safeguards only | **Deferred until another source exists** | Inspect the actual second source before designing reconciliation. |

The stable core runner identifier is the future attachment point for these layers. No identity extension is part of the first implementation.

---

## 5. Race, meeting and course abstractions

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Source meeting occurrence | Race grouping and course/date evidence exist; no dedicated meeting reconstruction study | Profiled indirectly | Conceptually designed | **Further focused study required** | Test grouping, sessions, transfers, abandonments and actual-versus-advertised sites. |
| Recurring race series and editions | Raw race names exist; continuity has not been governed source-wide | Profiled | Conceptually designed | **Further focused study required** | Conduct a bounded continuity study with accepted, rejected and unresolved relationships. |
| Racecourse venue identity | Notebooks 04, 09 and 12 provide context | Semantically investigated | Conceptually designed | **Further analytical justification required** | Define an analysis that needs institutional venue identity rather than raw course labels. |
| Physical racecourse site | Notebook 12 provides locations but not full site-history governance | Profiled to semantically investigated | Conceptually designed | **Further focused study required** | Investigate relocations and temporary transfers only when needed. |
| Course configuration era | No complete governed layout or configuration history | Uninspected to partially profiled | Conceptual safeguards only | **Further enrichment study required** | Inspect actual layout, rail-movement or specialist evidence. |

---

## 6. Betting-market evidence

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Source starting-price arithmetic | Notebook 08; parser and validator; one unresolved `F` | Implemented and validated for bounded arithmetic | Conceptually designed | **Further semantic and analytical gate required** | Confirm analyses that do not assume homogeneous market semantics. |
| Jurisdiction and betting-market context | Notebook 09 | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define the minimum context needed for an accepted analysis. |
| British SP methodology regimes | External evidence and interpretation-regime addendum | Semantically investigated at regime level | Conceptually designed | **Further source-linkage study required** | Verify exact effective-date assignment and Source Version 1 relationship. |
| Foreign Tote or pari-mutuel values and source conversions | Meanings remain incomplete by jurisdiction | Profiled with unresolved semantics | Conceptual safeguards accepted | **Further jurisdiction studies required** | Investigate only jurisdictions used in an accepted analysis. |
| General market observations and price movement | No multi-snapshot operator dataset held | Uninspected or absent | Conceptual safeguards only | **Deferred enrichment** | Inspect the actual bookmaker, exchange or feed dataset if acquired. |

---

## 7. Deferred enrichments

| Topic | Current evidence | Evidence maturity | Physical database status | Required first step |
|---|---|---|---|---|
| Historical weather and going reconciliation | Going exists; no accepted weather dataset has been studied | **Uninspected enrichment** | **Deferred enrichment** | Conduct a provider, location, coverage, interval, rainfall-window and representativeness study. |
| Sectional timing | No sectional dataset held | **Uninspected enrichment** | **Deferred enrichment** | Inspect an obtainable provider's methodology, checkpoints, coverage, precision and linkage. |
| GPS and runner tracking | No dataset held | **Uninspected enrichment** | **Deferred enrichment** | Inspect the actual dataset if acquired. |
| Irrigation and drainage evidence | No governed dataset held | **Uninspected enrichment** | **Deferred enrichment** | Investigate within a weather-and-going study. |
| Exchange order books and liquidity | No dataset held | **Uninspected enrichment** | **Deferred enrichment** | Inspect actual timestamps, sides, volume, matching and commission data. |
| Specialist course-layout and rail-movement data | No complete governed dataset held | **Uninspected enrichment** | **Deferred enrichment** | Inspect actual provider coverage and effective-date semantics. |

The absence of an enrichment from the current database means only:

> Not available in the admitted source evidence.

It is not proof that the real-world event or measurement did not exist.

---

## 8. Document authority

The following remain accepted conceptual safeguards rather than independent implementation authority:

- `PHASE_3_ENTITY_AND_KEY_DESIGN_INVENTORY.md`;
- `PHASE_3_MEETING_IDENTITY_DESIGN.md`;
- `PHASE_3_RECURRING_RACE_SERIES_DESIGN.md`;
- `PHASE_3_RACE_CONDITIONS_AND_CLASSIFICATION_DESIGN.md`;
- `PHASE_3_RACE_RESULTS_AND_FINISHING_OUTCOMES_DESIGN.md`;
- `PHASE_3_PRIZE_MONEY_AND_MONETARY_AMOUNTS_DESIGN.md`;
- `PHASE_3_BETTING_PRICES_AND_MARKET_OBSERVATIONS_DESIGN.md`;
- `PHASE_3_BETTING_PRICE_INTERPRETATION_REGIMES_ADDENDUM.md`;
- `PHASE_3_RATINGS_AND_PERFORMANCE_MEASURES_DESIGN.md`;
- `PHASE_3_CARRIED_WEIGHT_ALLOWANCES_AND_CLAIMS_DESIGN.md`;
- `PHASE_3_EQUIPMENT_AND_MEDICATION_ASSERTIONS_DESIGN.md`.

They define distinctions, failure modes and future study questions. They are not a table list.

Physical authority for the stable core comes only from:

- `PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- the evidence-first gate;
- the database import validation gate.

---

## 9. Current project sequence

### Completed — evidence and conceptual boundary

- Notebooks 00–22 and the targeted implementation audit are closed and validated.
- The evidence-first gate is accepted.
- The evidence-status matrix is accepted.
- The minimum stable-core boundary is accepted.
- The minimum stable-core implementation brief is accepted.

### Next — physical architecture selection

Select the database technology and physical architecture that best implement the authorised core without expanding it.

The decision must cover:

- technical identifier representation;
- exact raw-value storage and round trip;
- constraints and indexes;
- database versioning;
- candidate-build and atomic-activation strategy;
- generated-artifact location and retention;
- query-performance needs for source, race and runner access.

### Then — bounded stable-core implementation

Implement, review and validate the core in focused units. Run the complete project-level test and validator gate at final integration rather than after every small step.

### Later — extensions one at a time

Each governed extension requires an accepted use and a separate bounded brief.

### Later — enrichments only when evidence exists

Weather, sectionals, official identifiers and market feeds remain deferred until an obtainable dataset and analytical question exist.

---

## 10. Decision summary

The accepted evidence-status position is:

1. Notebooks 00–22 and the targeted cross-notebook audit are closed and validated.
2. Closed notebook evidence does not automatically authorise physical database representation.
3. Existing conceptual documents remain safeguards rather than schema promises.
4. The minimum stable structural core is now explicitly authorised by `PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`.
5. That authority is limited to source lineage, immutable physical records, admission state, Source Version 1 race occurrences, runner participations, raw recoverability, structural governance and import evidence.
6. All governed source-field and provisional identity layers remain unauthorised extensions.
7. Meetings, recurring race series, course configurations and incomplete betting regimes need further focused studies.
8. Weather, sectionals, tracking, official registries and similar unavailable datasets remain deferred enrichments.
9. The database must remain extension-friendly without containing empty speculative structures.
10. The next decision is physical database technology and architecture for the authorised core.

The governing rule remains:

> Understand the evidence first, authorise a bounded representation, and build nothing beyond that accepted boundary.
