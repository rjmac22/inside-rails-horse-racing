# Retrospective Notebook Implementation Audit

## Purpose

This register audits completed notebook investigations against `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`. Analytical completion is not treated as implementation completion.

A notebook is fully closed only when its conclusion, reproducibility or archival classification, persisted outputs, reusable implementation, focused tests, independent validation, database consequence, manual-verification decision, report, lessons and project-status updates are complete.

## Classification register

| Notebook | Investigation | Audit classification | Principal evidence or retained limit |
|---|---|---|---|
| 00 | Project scope and methodology | **No reusable artifact required** | Durable methodology and closure rules are documented. |
| 01 | Source database structure profile | **Fully closed** | Reusable profile module, tests, validator and integration documentation. |
| 02 | Source field quality profile | **Fully closed** | Governed 37-field reference, loader, tests, validator, corrected integration path and lineage policy. |
| 03 | Race identity and source-key reconstruction | **Fully closed** | Reusable identity profiling, tests and source-wide reconciliation. |
| 04 | Course jurisdiction and surface mapping | **Fully closed** | Reconciled jurisdiction and bounded surface governance. |
| 05 | Finishing positions and non-finish outcomes | **Fully closed** | Complete governed result partition. |
| 06 | Race distance parsing | **Fully closed** | Parser, tests, validator and integration contract. |
| 07 | Carried weight parsing | **Fully closed** | Parser, tests, validator and integration contract. |
| 08 | Starting price parsing | **Fully closed with governed anomaly** | The lone raw `F` remains unresolved; the bounded Almendares external claim is separately governed and validated. |
| 09 | Jurisdiction, authority and betting-market context | **Fully closed** | Exact four-record context provenance and source-context agreement. |
| 10 | Remaining source-field inventory and triage | **Fully closed** | Reconciled closeout record, 37-field governance register and immutable-source schema validation. |
| 11 | Off-time and temporal semantics | **Fully closed — archival route** | Complete 189,043-race builder, atomic persistence, typed reload and independent source reconciliation; 169,465 resolved and 19,578 unresolved. |
| 12 | Course location and timezone mapping | **Fully closed** | Complete 395-identity timezone reference, two governed provenance records and exact evidence-to-reference validation. |
| 13 | Prize-money semantics and availability | **Fully closed** | Complete immutable-source parsing and partition validator; no foreign-exchange conversion. |
| 14 | Runner counts, numbers and entries | **Fully closed** | Exact five-decision validation and governed Saucats and Tosen Thunder supplementations. |
| 15 | Beaten-distance semantics | **Fully closed** | Exact 17-decision validation and governed Great Navigator supplementation. |
| 16 | Race classification and eligibility | **Fully closed** | Exact seven field decisions and four external decisions; correction candidates remain non-automatic. |
| 17 | Runner characteristics and equipment | **Fully closed — archival route** | Direct source-wide validation, exact evidence closure and exact correction lineage. |
| 18 | Ratings semantics and availability | **Fully closed** | Exact source-wide ratings partition plus three permanent semantic-provenance decisions. |
| 19 | Horse and pedigree identity | **Fully closed — archival route** | 353 governed transitions: 91 corrected, 261 different horse and one unresolved; 611 provisional occurrences. |
| 20 | Connections and ownership identity | **Fully closed** | Exact closure of 46 raw blank occurrences: 28 supplementations and 18 preserved unresolved; obsolete promotion utility retired. |
| 21 | Comment and embedded information | **Fully closed** | Persisted profiles, conservative classifier, tests and independent validation; no general narrative parser. |
| 22 | Jockey, trainer and owner participant identity | **Fully closed — archival route** | Direct jockey mapping, exact decision closure, decisive provenance and source-wide validation. |

## Targeted cross-notebook audit result

The targeted implementation-completeness audit found a finite set of bounded defects without reopening the analytical investigations.

The completed repairs include:

- Notebook 20 exact one-to-one closure of all 46 raw blank field occurrences;
- Notebook 02 and 10 status-document reconciliation;
- Notebook 08 governed external anomaly evidence;
- Notebook 09 exact context-provenance enforcement;
- Notebook 12 recovered provenance dates and exact reference agreement;
- Notebook 13 complete source-wide prize-money validation;
- Notebook 14 and 15 machine-usable missing-runner supplementations and exact decision partitions;
- Notebook 16 exact field and external-decision validation;
- Notebook 17 removal of false clean-checkout dependencies and exact correction lineage;
- Notebook 18 exact closure of the three existing permanent semantic-evidence records;
- retirement of the completed Notebook 20 promotion utility;
- Notebook 11 complete canonical-output regeneration, persistence and independent validation.

Every individual repair unit was reviewed and accepted before integration. The repair history remains visible in the dedicated review branches; the accepted content is consolidated on `audit/retrospective-implementation-integration`.

## Notebook 11 acceptance evidence

Local execution on 5 August 2026 established:

- race-time pipeline and DST regression tests: **5 passed**;
- raw off-time tests: **9 passed**;
- raw off-time validator: **1,851,285 rows**, **1,380 distinct raw values**, **189,043 races**, **0 unresolved raw values**;
- canonical source build: **passed**;
- atomic persisted-output write and typed reload: **passed**;
- independent source-wide validator: **passed**;
- exact source-race, timezone and UTC/local conversion reconciliation: **passed**;
- exact method totals: **111,871 dead-of-night**, **47,242 stable profile**, **10,352 explicit post-boundary**, **19,578 unresolved**.

The repaired pipeline restores the original notebook's exclusion of 93 DST-edge meetings comprising 515 races from profile-based selection. Unsupported future inputs fail closed rather than being silently selected or imported.

## Notebook 21 evidence

Established baselines:

- governed runner rows: **1,851,285**;
- provisional races: **189,043**;
- SQL null comments: **0**;
- empty-string comments: **340,394**;
- probable-placeholder or unresolved-code rows: **238**;
- substantive-text rows: **1,510,653**;
- candidate jurisdictions: **36**;
- unresolved candidate-jurisdiction races: **0**.

Manual-verification decision: `not_applicable`.

## Notebook 22 evidence

Established baselines:

- jockey labels: **7,917**;
- jockey candidate relationships: **216**;
- confirmed same-person relationships: **1**;
- confirmed different-person relationships: **1**;
- unresolved jockey relationships: **214**;
- directly mapped jockey labels: **2**;
- trainer labels: **10,708**;
- accepted trainer groups: **26** covering **6,350** source rows;
- owner labels: **98,234**;
- accepted owner groups: **41** covering **9,788** source rows;
- unresolved owner groups: **895**.

Manual-verification decision: `specialist_reference`.

Focused local tests passed with **14 passed in 0.61s**. The strengthened validator enforces exact candidate closure, decisive external provenance, unresolved preservation and the exact direct jockey mapping.

## Historical end-of-source-field-series evidence

The complete repository test run after Notebook 21 found and repaired two integration defects:

1. a Great Britain sub-minor-unit prize value incorrectly fell through to `currency_unresolved`;
2. the source-field loader did not allow the explicit later-notebook pending-validation status.

Final local evidence on 4 August 2026 was:

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

Final field-governance totals were:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 fields require raw preservation and match the SQLite field names, order and declared types.

## Database consequence

All future database ingestion is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

No source-derived output may enter staging, core or analytical structures until it has passed its applicable unit tests, source-wide validators, persisted-output readback and source reconciliation. Candidate database structures must be built and validated transactionally or as a complete replacement before the last known-good database is changed.

Unknown, changed or unmatched data must fail closed, remain explicitly unresolved or be quarantined. Partial success and silent coercion are prohibited.

## Current position

All individual notebook and cross-notebook repair units are accepted and integrated.

The remaining closure gate is:

1. run the complete repository test suite from the integration branch;
2. run every applicable independent validator;
3. repair any genuine integration defect found;
4. record the final integrated evidence in this register, `README.md` and `docs/PROJECT_PLAN.md`;
5. merge only after the integrated branch is clean and the complete gate passes.

After that, proceed to Phase 3 entity and key design. No further source-field notebook investigation is required unless a new source snapshot or failed validator produces concrete new evidence.
