# Cross-Notebook Implementation-Completeness Audit

## Purpose

This audit applies the targeted pre-database review required by `docs/PROJECT_PLAN.md`.

It does not reopen the analytical investigations or rerun archival notebooks. It checks whether the repository implementation actually supports each notebook's claimed database consequence, with particular attention to:

1. accepted decisions stranded in review tables without a usable governed output;
2. validators that prove only counts, syntax or file existence rather than exact governed closure;
3. external evidence without durable identifiers, locators, access dates, confidence and permitted actions;
4. documentation claiming closure where required implementation artifacts are absent or stale;
5. accepted, rejected and unresolved populations that could overlap downstream.

## Overall result

The analytical conclusions remain usable. The audit found a finite set of implementation and status-document defects. No result below justifies reopening the completed source-field investigations or manufacturing new analytical work.

### Clean under this audit

| Notebook | Result | Evidence |
|---|---|---|
| 00 | Clean | Methodology notebook; no reusable transformation was required. |
| 01 | Clean | Reusable source profiler and exact source-wide validator. |
| 03 | Clean | Race and runner-record identity implementation and exact source-wide reconciliation. |
| 04 | Clean | Candidate jurisdiction and bounded surface outputs are independently source-validated. |
| 05 | Clean | Result representation forms a complete validated source partition. |
| 06 | Clean | Distance parser covers the complete observed race vocabulary and preserves limits. |
| 07 | Clean | Carried-weight parser covers the complete observed vocabulary and rejects unsupported forms. |
| 19 | Clean after authority-gate repair | Exact `91 / 261 / 1` decision partition, usable occurrence output, focused tests and independent validator pass. |
| 21 | Clean | Source-wide comment partition plus tests that reload both persisted governed outputs. |
| 22 | Clean after closeout repair | Direct participant mapping, exact decision closure and decisive provenance enforced. |

### Documentation-only repairs

| Notebook | Defect | Required bounded repair |
|---|---|---|
| 02 | `NOTEBOOK_02_CLOSEOUT.json` still says `complete_locally_pending_notebook_commit`, has no completed commit, and lists no reusable implementation despite the current reference, loader, tests and validator. | Reconcile the closeout record with the existing implementation and validation evidence. |
| 10 | `NOTEBOOK_10_CLOSEOUT.json` still lists no reusable output or validator and retains the original provisional future sequence after the field-governance programme was implemented and completed. | Reconcile the closeout record with the current governed 37-field inventory and validator. |

### Provenance and governed-decision validation repairs

| Notebook | Defect | Required bounded repair |
|---|---|---|
| 08 | The standalone `F` anomaly is source-validated, but the separately researched Almendares `5/2 favourite` evidence is mentioned only in the notebook/report. The closeout also still says no module or validator exists. | Preserve the external claim in a small governed specialist reference, validate it separately from parser output, and update stale closeout metadata. |
| 09 | Authority names and the Irish 2018 regulatory transition are hard-coded in `jurisdiction_context.py`; evidence URLs remain only inside the archived notebook. | Add a governed context-evidence reference and enforce exact agreement between it and the reusable context rows. |
| 12 | The two permanent Argentina course-location verifications have blank access dates, although the archived request log preserves both request dates. Existing validators do not enforce exact evidence-to-reference agreement. | Add/repair governed provenance with the recovered `2026-07-26` access date and validate the exact La Plata and Palermo reference values. |
| 16 | The source-wide parser validator does not enforce the exact four external age/eligibility decisions or the seven-row persisted field-decision output. | Strengthen validation without converting correction candidates into automatic repairs. |
| 18 | Ratings coverage and the exact RPR anomaly are source-validated, but the three publisher-reference decisions defining `or`, `rpr` and `ts` semantics are not enforced. | Add a governed semantic-evidence reference and validate its exact three-record closure. |

### Missing usable output or incomplete validator repairs

| Notebook | Defect | Required bounded repair |
|---|---|---|
| 11 | The repository claims 169,465 resolved and 19,578 unresolved canonical race times, but no persisted race-time decision/output file exists. The reusable module contains building blocks but no default source-wide regeneration path; full canonical validation is optional and requires an externally supplied file. | Add a repeatable source-to-output build path, persist/reload the governed race-time output locally, and make exact full-population validation mandatory. |
| 13 | `validate_prize_money.py` is a four-case synthetic smoke test and never reads the immutable source, despite closure claims of independent validation. | Replace or strengthen it with complete source-wide parsing and partition checks using governed jurisdiction context. |
| 14 | Two confirmed `source_supplementation` decisions—Saucats and Tosen Thunder—exist only in the manual register. No machine-usable missing-runner supplementation output exists, and the validator does not enforce the exact five-decision partition. | Add a bounded supplementation reference and validate all five decisions, source locators and non-overlap. |
| 15 | Great Navigator's confirmed missing-runner/fifth-place supplementation exists only in the manual register. The validator does not enforce the exact 17 external decisions or the persisted field-decision table. | Add the bounded supplementation to the same governed runner-supplementation layer and strengthen exact decision validation. |
| 17 | `validate_runner_characteristics.py` requires three ignored `data/processed/...` CSVs that are absent from a clean checkout. It also cites verification IDs without validating the five corresponding evidence decisions, and correction application is not sufficiently lineage-bound. | Remove the false clean-checkout dependency or restore governed outputs, validate exact evidence, and enforce exact runner lineage for `B` and `BB` corrections. |
| 20 | The earlier validator proved totals and the 28 repairs but not exact one-to-one closure of all 46 raw blank `(source_rowid, source_field)` occurrences. | Repaired in commit `3270c6d`: exact IDs, decision partition, raw-blank closure, locators, repair agreement and unresolved exclusion are now enforced. |

## Repair discipline

Each substantive finding will be repaired as a bounded review unit. A repair must:

- preserve immutable source values and unresolved states;
- add no unsupported automatic correction;
- use a small governed specialist reference where external evidence is required;
- include focused tests where reusable behaviour changes;
- strengthen the independent validator to protect the exact decision or output claimed;
- record the database consequence and validation command;
- avoid a complete repository test or all-validator sweep until the repair series reaches its final gate.

The larger Notebook 11 output repair and any generated source-wide files must be built and validated against the user's immutable local SQLite source before they can be accepted. Generated source-derived outputs will not be invented through the GitHub connector.

## Review order

The intended review order is:

1. Notebook 20 exact decision closure;
2. Notebook 02 and 10 status reconciliation;
3. Notebook 08 and 09 provenance;
4. Notebook 12 provenance and source-reference agreement;
5. Notebook 13 source-wide validation;
6. Notebook 14 and 15 runner supplementations;
7. Notebook 16 decision validation;
8. Notebook 17 clean-checkout and lineage repair;
9. Notebook 18 semantic provenance validation;
10. Notebook 11 canonical temporal output and regeneration;
11. final audit-register, README and project-plan reconciliation;
12. final complete test suite and all-validator sweep.
