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

**Status: completed and fully closed on 5 August 2026.**

The audit found a finite set of implementation and status-document defects. Every finding was repaired as a bounded review unit, reviewed individually, integrated on `audit/retrospective-implementation-integration`, and then subjected to the complete repository test suite and every current independent validator.

Final integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

No genuine integration defect was found by the final gate. The analytical conclusions did not need to be reopened.

## Findings and completed repairs

### Clean under the initial audit

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

| Notebook | Finding | Completed repair |
|---|---|---|
| 02 | Stale closeout status and missing reusable-implementation details. | Reconciled the closeout record with the governed 37-field reference, loader, tests, validators and correct integration document path. |
| 10 | Stale closeout status, missing reusable output and obsolete future sequence. | Reconciled the closeout with the completed 37-field governance programme and current validator. |

### Provenance and governed-decision validation repairs

| Notebook | Finding | Completed repair |
|---|---|---|
| 08 | Almendares `5/2 favourite` evidence existed outside permanent parser governance. | Preserved the bounded external claim separately, retained raw `F` as parser-unresolved and enforced the exact one-record enrichment. |
| 09 | Authority and Irish regulatory-transition evidence was not governed independently. | Added exact four-record provenance and source-context agreement validation. |
| 12 | Two Argentina course-location records lacked enforced access dates and exact reference agreement. | Recovered the `2026-07-26` dates and enforced exact two-record evidence-to-reference agreement. |
| 16 | The validator did not enforce the exact persisted field and external decisions. | Enforced seven field decisions and four external decisions without authorising automatic corrections. |
| 18 | Three ratings semantic decisions were not enforced from the permanent manual-verification register. | Strengthened the ratings validator to require exact closure of the three existing records without creating a duplicate evidence store. |

### Missing usable output or incomplete validator repairs

| Notebook | Finding | Completed repair |
|---|---|---|
| 11 | No repeatable complete canonical race-time output path or mandatory persisted-output validation. | Added the source-to-output builder, atomic persistence, typed reload and mandatory independent validation across all 189,043 races. |
| 13 | Prize-money validation was only a synthetic smoke test. | Replaced it with complete immutable-source parsing and partition validation. |
| 14 | Saucats and Tosen Thunder supplementations were not machine-usable. | Added the governed runner-supplementation layer and exact five-decision validation. |
| 15 | Great Navigator supplementation and exact 17-decision closure were not enforced. | Added the supplementation to the shared governed layer and exact decision validation. |
| 17 | Validator depended on ignored outputs and correction application was insufficiently lineage-bound. | Removed false clean-checkout dependencies, enforced exact evidence closure and exact source-row correction lineage. |
| 20 | The earlier validator did not prove exact closure of all 46 raw blank occurrences. | Enforced exact IDs, raw-blank closure, decision partition, repair agreement and unresolved exclusion. |
| 20 | The completed promotion utility depended on an ignored construction file and was not part of the future build. | Retired the utility while retaining its Git history and documenting the permanent governed inputs. |

## Repair discipline applied

Each substantive finding was repaired under these constraints:

- immutable source values and unresolved states remained preserved;
- no unsupported automatic correction was added;
- external evidence was captured in governed permanent references;
- focused tests were added where reusable behaviour changed;
- independent validators protect the exact decision, output or provenance claimed;
- database consequences and validation commands were documented;
- the complete suite and validator sweep were deferred until integration.

The larger Notebook 11 output was generated only from the user's immutable local SQLite source. Generated source-derived output was not invented through the GitHub connector.

## Review order completed

The review proceeded in this order:

1. Notebook 20 exact decision closure;
2. Notebook 02 and 10 status reconciliation;
3. Notebook 08 and 09 provenance;
4. Notebook 12 provenance and source-reference agreement;
5. Notebook 13 source-wide validation;
6. Notebook 14 and 15 runner supplementations;
7. Notebook 16 decision validation;
8. Notebook 17 clean-checkout and lineage repair;
9. Notebook 18 semantic provenance validation;
10. Notebook 20 obsolete promotion-utility retirement;
11. Notebook 11 canonical temporal output and regeneration;
12. final audit-register, README and project-plan reconciliation;
13. final complete test suite and all-validator sweep.

All thirteen stages are complete.

## Final consequence

The targeted audit no longer blocks physical database design.

All future ingestion is subject to `docs/DATABASE_IMPORT_VALIDATION_GATE.md`: no validated output, no database write; no partial success; the last known-good database remains intact.

The next project stage is Phase 3 entity and key design.
