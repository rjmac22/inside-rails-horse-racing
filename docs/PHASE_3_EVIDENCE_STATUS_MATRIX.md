# Phase 3 Evidence Status Matrix

## Status

Accepted Phase 3 evidence, design and implementation-status register.

This document applies the maturity states and physical-implementation gate defined in:

- `docs/PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

It separates four questions that must not be collapsed:

1. Has the actual source evidence been inspected?
2. Has its meaning and limitation been established?
3. Has a governed conceptual model been accepted?
4. Has physical database implementation been explicitly authorised?

The current answer to question 4 is **no for every Phase 3 topic**.

No table, column, parser, relationship, migration or ingestion process is authorised merely because a notebook is closed or a conceptual design document exists.

---

## 1. Status vocabulary

### Evidence maturity

The matrix uses the maturity states established by the evidence-first gate:

- **Uninspected** — no adequate source or enrichment study exists.
- **Profiled** — distributions and examples are known, but semantic meaning is incomplete.
- **Semantically investigated** — a focused study established the supported meaning, limitations and unresolved cases.
- **Analytically justified** — a defined accepted use requires the concept and the evidence is adequate.
- **Conceptually designed** — governed distinctions and identity boundaries have been accepted.
- **Implementation authorised** — an accepted bounded implementation brief permits physical work.
- **Implemented and validated** — reusable implementation, tests, source-wide validation, provenance and limitations are complete.

A topic may have reusable notebook-era parsing or governed outputs at **implemented and validated** maturity while its physical database representation remains **not authorised**.

### Physical database status

- **Not authorised** — no physical work may begin.
- **Eligible for bounded implementation brief** — the evidence appears sufficient to draft a minimal implementation proposal, but the proposal still requires explicit acceptance.
- **Further focused study required** — the evidence, analytical need or minimum representation is not yet sufficiently established.
- **Deferred enrichment** — the project does not currently hold the required dataset and should not design speculative structures.

---

## 2. Stable core candidates

These are the strongest candidates for the first physical implementation. They still require one accepted bounded implementation brief.

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Source provider and source product | Notebooks 00–02; project methodology; source-lineage decisions | Analytically justified | Conceptually designed in `PHASE_3_ENTITY_AND_KEY_DESIGN_INVENTORY.md` | **Eligible for bounded implementation brief** | Define the minimum provider/product metadata required for Source Version 1 without speculative role modelling. |
| Exact source version | Notebooks 01–02; immutable-file controls; database import gate | Implemented and validated as source-governance practice | Conceptually designed | **Eligible for bounded implementation brief** | Specify immutable identifier, cryptographic hash, file size, retrieval metadata and schema fingerprint. |
| Source relation | Notebooks 01–02; governed `data` relation and 37-field schema | Implemented and validated as source-governance practice | Conceptually designed | **Eligible for bounded implementation brief** | Limit the first implementation to the actual SQLite `data` relation; defer generic non-tabular source abstractions. |
| Immutable source record | Notebooks 01–03; exact 1,851,285-row governed population; `rowid <> 1`; 37-field preservation | Implemented and validated | Conceptually designed | **Eligible for bounded implementation brief** | Define project technical identity and the exact Source Version 1 locator: source version + relation + SQLite `rowid`. |
| Raw source-field preservation | Notebooks 02 and 10; 37-field governance register; source schema validation | Implemented and validated | Conceptually designed as immutable evidence | **Eligible for bounded implementation brief** | Decide whether first implementation stores all raw values directly or preserves an equally reliable immutable route to them. |
| Source race occurrence | Notebook 03; 189,043 reconciled source races; current candidate grouping `date + course + off` | Implemented and validated for Source Version 1 | Conceptually designed | **Eligible for bounded implementation brief** | Preserve the grouping as source-version-scoped evidence, not permanent real-world race identity. |
| Runner participation record | Notebooks 01–03 and 14; current one-row-per-runner evidence; candidate validation by source race occurrence + raw horse label | Implemented and validated for Source Version 1 | Conceptually designed | **Eligible for bounded implementation brief** | Define independent runner identity while retaining the direct source-record relationship and all raw labels. |
| Governance release and decision provenance | All closed notebooks; governed outputs; 282 tests and 28 validators; database admission gate | Analytically justified and repeatedly used | Conceptually designed at policy level | **Eligible for bounded implementation brief** | Define the smallest release, method, decision and evidence references needed to reproduce accepted interpretations. |
| Import manifest and validation evidence | `DATABASE_IMPORT_VALIDATION_GATE.md`; complete test and validator evidence | Analytically justified | Required conceptually but not yet physically specified | **Eligible for bounded implementation brief** | Define source fingerprint, candidate-output identity, validator results, transaction status and last-known-good protection. |

### Stable-core conclusion

The first implementation brief should be restricted to:

- source provider;
- source product;
- exact source version;
- source relation;
- immutable source record;
- source race occurrence;
- runner participation;
- raw-value recoverability;
- governance release and decision provenance;
- import and validation evidence.

This conclusion does not yet authorise physical schema work.

---

## 3. Strongly evidenced governed extensions

The source fields and governed outputs below have completed investigations and reusable validation. Their database representations should be admitted only when a defined analysis or operational requirement justifies them.

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Course label, jurisdiction and surface context | Notebooks 04 and 09 | Implemented and validated as governed references | Conceptually designed within course identity work | **Eligible for bounded extension brief** | Define the first analytical use and implement only the evidenced current-source distinctions. |
| Course location and timezone | Notebook 12; complete 395-identity timezone reference and provenance validation | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Decide whether Phase 4 needs these values immediately for accepted race-time analysis. |
| Governed race time | Notebook 11; 189,043-race output; 169,465 resolved and 19,578 unresolved | Implemented and validated | Conceptually designed as an attribute, not identity | **Eligible for bounded extension brief** | Specify which local/UTC values and unresolved statuses are needed in the first database release. |
| Finishing positions and non-finish outcomes | Notebook 05 | Implemented and validated | Conceptually designed in `PHASE_3_RACE_RESULTS_AND_FINISHING_OUTCOMES_DESIGN.md` | **Eligible for bounded extension brief** | Restrict implementation to source-supported result states; do not prebuild unsupported amendment machinery. |
| Beaten distance | Notebook 15 | Implemented and validated | Covered by result design safeguards | **Eligible for bounded extension brief** | Define exact analytical use and preserve source-specific semantics and supplemented evidence. |
| Race distance | Notebook 06 | Implemented and validated | Covered by race-conditions design safeguards | **Eligible for bounded extension brief** | Implement only confirmed raw and governed distance representations and documented failure states. |
| Carried weight | Notebook 07 | Implemented and validated | Conceptually designed in `PHASE_3_CARRIED_WEIGHT_ALLOWANCES_AND_CLAIMS_DESIGN.md` | **Eligible for bounded extension brief** | Implement only the actual established Source Version 1 meaning; claims and adjustment detail require evidence that those concepts are separately encoded. |
| Prize money | Notebook 13 | Implemented and validated | Conceptually designed in `PHASE_3_PRIZE_MONEY_AND_MONETARY_AMOUNTS_DESIGN.md` | **Eligible for bounded extension brief** | Restrict first implementation to evidenced runner-level recorded values, currency/scale decisions and unresolved foreign cases. |
| Runner counts, numbers and entries | Notebook 14 | Implemented and validated | Partly covered by runner and race design | **Eligible for bounded extension brief** | Define which counts are stored facts, reconciliations or derived outputs; retain supplementations with provenance. |
| Race classification and eligibility | Notebook 16 | Implemented and validated | Conceptually designed in `PHASE_3_RACE_CONDITIONS_AND_CLASSIFICATION_DESIGN.md` | **Eligible for bounded extension brief** | Implement only the seven accepted field decisions and supported external decisions; retain correction candidates as non-automatic. |
| Runner characteristics and source equipment fields | Notebook 17 | Implemented and validated | Conceptually designed in `PHASE_3_EQUIPMENT_AND_MEDICATION_ASSERTIONS_DESIGN.md` | **Eligible for bounded extension brief** | Limit the implementation to the actual investigated fields and confirmed abbreviations; do not create worldwide medication structures. |
| Ratings fields | Notebook 18 | Implemented and validated | Conceptually designed in `PHASE_3_RATINGS_AND_PERFORMANCE_MEASURES_DESIGN.md` | **Eligible for bounded extension brief** | Implement only systems, timings and meanings established by Notebook 18; do not create a universal rating entity without need. |
| Connection-field blank governance | Notebook 20; exact 46-blank closure with 28 supplementations and 18 unresolved | Implemented and validated | Supports participant and ownership evidence layers | **Eligible for bounded extension brief** | Decide whether the first database needs governed supplements or can initially preserve raw fields plus separate evidence outputs. |
| Comment-field states | Notebook 21 | Implemented and validated for bounded classification | No broad narrative model authorised | **Further focused analytical justification required** | Identify a specific study that needs the conservative classes; a general narrative parser remains prohibited. |

### Governed-extension conclusion

Completed notebook work proves that the interpretations are reproducible. It does not prove that every result belongs in the first physical database.

Each extension requires a brief that states:

- the accepted analysis or operational need;
- the minimum fields or relationships required;
- the governed output and release used;
- unresolved-case treatment;
- validation and reconciliation rules;
- deliberately deferred conceptual detail.

---

## 4. Identity extensions

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Provisional horse occurrence | Notebook 19; 353 governed transitions; 91 corrected, 261 different horse, one unresolved; 611 provisional occurrences | Implemented and validated as source-internal identity | Conceptually designed | **Eligible for bounded extension brief** | Define the immediate horse-level analyses requiring continuity and preserve the provisional, release-scoped status. |
| Runner-to-horse-occurrence assignment | Notebook 19 governed outputs and validators | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define append-only release/version handling without pretending the occurrence is an official horse identity. |
| Jockey provisional identity | Consolidated Notebook 22; exact `1 / 1 / 214` decision partition and two-row direct mapping | Implemented and validated for the accepted bounded decisions | Conceptually designed | **Eligible for bounded extension brief** | Decide whether the first analytical products require participant identity; preserve all unresolved candidates. |
| Trainer provisional transitions | Consolidated Notebook 22; 26 transitions covering 52 labels and 6,350 rows | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define the analysis requiring them and retain role-, evidence- and release-scoped status. |
| Ownership compositions | Consolidated Notebook 22; 41 supported compositions covering 95 labels and 9,788 rows; 895 groups unresolved | Implemented and validated for the bounded supported set | Conceptually designed | **Eligible for bounded extension brief** | Implement compositions only if an accepted owner-level analysis needs them; do not split constituents without another study. |
| Official/global horse, jockey, trainer or owner identity | No official registry dataset held; current identities are explicitly provisional | Uninspected as a new enrichment | Deferred relationship safeguards only | **Deferred enrichment** | Inspect an obtainable official or licensed identity dataset before modelling provider-independent identities. |
| Cross-provider identity reconciliation | Only one governed primary source version is currently in scope | Uninspected | Conceptual safeguards only | **Deferred until another source exists** | Design reconciliation only after inspecting the actual second provider or source version. |

---

## 5. Race, meeting and course abstractions

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Source meeting occurrence | Race grouping and course/date evidence exist, but no dedicated meeting reconstruction study has been accepted | Profiled indirectly | Conceptually designed in `PHASE_3_MEETING_IDENTITY_DESIGN.md` | **Further focused study required** | Test `date + course` grouping, split sessions, transfers, abandonments and actual-versus-advertised sites before implementation. |
| Recurring race series and editions | Raw race names and individual race occurrences exist; recurring continuity has not been source-wide governed | Profiled | Conceptually designed in `PHASE_3_RECURRING_RACE_SERIES_DESIGN.md` | **Further focused study required** | Conduct a bounded recurring-race continuity study with explicit accepted, rejected and unresolved relationships. |
| Racecourse venue identity | Notebooks 04, 09 and 12 provide course context and location evidence | Semantically investigated | Conceptually designed | **Further analytical justification required** | Define which analyses need institutional venue identity rather than current source course labels. |
| Physical racecourse site | Notebook 12 provides locations but does not establish full relocation and site-history governance | Profiled to semantically investigated | Conceptually designed | **Further focused study required** | Investigate relocations, temporary transfers and historical site continuity only where an accepted study needs them. |
| Course configuration era | Source Version 1 does not provide a governed complete layout/configuration history | Uninspected to partially profiled | Conceptual safeguards only | **Further focused enrichment study required** | Inspect actual course-layout, rail-movement or specialist reference evidence before modelling configuration eras. |

---

## 6. Betting-market evidence

| Topic | Principal evidence | Evidence maturity | Conceptual status | Physical database status | Remaining gate before implementation |
|---|---|---|---|---|---|
| Source starting-price arithmetic | Notebook 08; parser and source-wide validator; one unresolved raw `F` | Implemented and validated for bounded arithmetic | Conceptually designed within betting-price work | **Further semantic and analytical gate required** | Confirm which analyses can safely use the parsed values without assuming homogeneous market semantics. |
| Jurisdiction and betting-market context | Notebook 09; exact context provenance | Implemented and validated | Conceptually designed | **Eligible for bounded extension brief** | Define the minimum context required to prevent incompatible comparisons. |
| British SP methodology regimes | External methodology evidence and `PHASE_3_BETTING_PRICE_INTERPRETATION_REGIMES_ADDENDUM.md` | Semantically investigated at regime level | Conceptually designed | **Further focused source-linkage study required** | Verify exact effective-date assignment and how Source Version 1 values relate to each regime before implementation. |
| Foreign Tote or pari-mutuel values and source conversions | Supplier conversion is known or suspected in foreign jurisdictions, but jurisdiction-level meanings remain incomplete | Profiled with unresolved semantics | Conceptual safeguards accepted | **Further jurisdiction-level studies required** | Investigate actual market mechanism, stake/return convention, pool operator and supplier conversion only for jurisdictions used in an accepted analysis. |
| General market observations, snapshots and price movement | Source Version 1 does not establish multiple timestamped operator observations | Uninspected or absent | Conceptually designed as safeguards | **Deferred unless a suitable market dataset is obtained** | Inspect the actual bookmaker, exchange or feed dataset before physical modelling. |

---

## 7. Deferred enrichments

| Topic | Current evidence | Evidence maturity | Conceptual status | Physical database status | Required first step |
|---|---|---|---|---|---|
| Historical weather and going reconciliation | Going exists in Source Version 1; no accepted historical weather dataset has been studied | **Uninspected enrichment** | No detailed model authorised | **Deferred enrichment** | Conduct a provider, location, coverage, interval, rainfall-window and representativeness study before design. |
| Sectional timing | No sectional dataset is held in the current project | **Uninspected enrichment** | Linkage safeguards only | **Deferred enrichment** | Inspect an obtainable provider's methodology, checkpoint definitions, coverage, precision and race/runner linkage. |
| GPS and runner tracking | No dataset held | **Uninspected enrichment** | None required now | **Deferred enrichment** | Inspect the actual dataset if acquired. |
| Irrigation and drainage evidence | No governed dataset held | **Uninspected enrichment** | None required now | **Deferred enrichment** | Investigate availability and analytical relevance as part of a weather/going study. |
| Exchange order books and liquidity | No dataset held | **Uninspected enrichment** | Betting design contains safeguards only | **Deferred enrichment** | Inspect actual timestamps, sides, volume, matching and commission data if acquired. |
| Specialist course-layout and rail-movement data | No complete governed dataset held | **Uninspected enrichment** | Course design contains safeguards only | **Deferred enrichment** | Inspect actual provider coverage and effective-date semantics. |

The absence of an enrichment from the current database must mean only:

> Not available in the admitted source evidence.

It must not be presented as proof that the real-world event or measurement did not exist.

---

## 8. Conceptual documents and their current authority

The following Phase 3 documents are accepted as conceptual safeguards but do not authorise physical implementation:

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

They define distinctions to preserve, failure modes to avoid and questions for future evidence-led work.

They are not a table list.

---

## 9. Recommended Phase 3 sequence from this matrix

### Step 1 — accept the minimum stable core boundary

Review whether the first database needs only:

- source lineage;
- immutable source records;
- source race occurrences;
- runner participation;
- raw-value recoverability;
- governance and import-validation evidence.

### Step 2 — write one bounded core implementation brief

The brief must define:

- exact included concepts;
- explicit exclusions;
- minimum physical requirements;
- identifiers and uniqueness scopes;
- raw evidence preservation;
- unresolved-state handling;
- ingestion and reconciliation rules;
- tests and validators;
- migration or replacement approach;
- last-known-good database protection.

Acceptance of this matrix does not constitute acceptance of that future brief.

### Step 3 — select physical database technology only after the core brief is accepted

Technology selection must follow the evidenced model rather than determine it in advance.

### Step 4 — admit extensions one at a time

Each extension should be justified by an accepted analysis and should attach to stable core identities without rewriting source history.

### Step 5 — investigate enrichments only when obtainable evidence and an analytical question exist

Weather, sectionals, official identifiers and market feeds should remain deferred until then.

---

## 10. Decision summary

The accepted evidence-status position is:

1. Notebooks 00–22 and the targeted cross-notebook audit are closed and validated.
2. Closed notebook evidence does not automatically authorise physical database representation.
3. All current Phase 3 conceptual documents remain safeguards rather than schema promises.
4. No Phase 3 physical implementation is currently authorised.
5. The source-lineage, source-record, source-race and runner-participation core is sufficiently evidenced to draft a bounded implementation brief.
6. Source-field outputs and provisional identity layers are potential governed extensions, admitted only when an accepted use justifies them.
7. Meetings, recurring race series, course configurations and incomplete betting regimes need further focused studies before implementation.
8. Weather, sectionals, tracking, official registries and similar unavailable datasets remain deferred enrichments.
9. The database must be extension-friendly without containing empty speculative structures.
10. The next decision is the scope of the minimum stable-core implementation brief, not another broad conceptual entity design.

The governing rule remains:

> Understand the evidence first, design only the necessary representation, and build nothing until its bounded implementation has been explicitly authorised.
