# Retrospective Notebook Implementation Audit

## Purpose

This register audits completed notebook investigations against the project closeout standard. Analytical completion is not treated as implementation completion.

A notebook is fully closed only when, as applicable:

1. it runs from a fresh kernel, or is explicitly archived as a non-rerunnable construction record with durable replacement validation;
2. conclusions and limitations are recorded;
3. reusable transformation logic or governed reference data is extracted;
4. tests cover governed rules and edge cases;
5. an independent validator exists where appropriate;
6. the database consequence and update path are documented.

This audit covers committed repository artifacts. Local uncommitted files are outside its evidence base.

## Classification register

| Notebook | Investigation | Required durable artifact | Audit classification | Evidence and principal gap |
|---|---|---|---|---|
| 00 | Project scope and methodology | No reusable field transformation required | **No reusable artifact required** | Methodology and closeout rules belong in durable documentation rather than a parser. Confirm the report and machine-readable closeout remain current, but no field module is justified. |
| 01 | Source database structure profile | Reusable source-access/profile module | **Fully closed on this audit branch** | Existing `source_sqlite.py` and `validate_source_profile.py` were missing governed tests and an explicit database/update path. Added `tests/test_source_sqlite.py` and `docs/SOURCE_PROFILE_DATABASE_INTEGRATION.md`. |
| 02 | Source field quality profile | Reusable source-field inventory, sentinel/missingness policy and lineage specification | **Reusable reference required** | Conclusions exist, but no durable machine-readable field inventory or governed raw-value/sentinel policy is identified. A later notebook must not silently become the only record of these rules. |
| 03 | Race identity and source-key reconstruction | Reusable race/runner identity transformation and reconciliation validator | **Reusable transformation module required** | Candidate race identity, source race-reference treatment, runner identity and surrogate-key requirements affect every later database build. No dedicated reusable implementation, tests, validator or integration document is currently identified. |
| 04 | Course jurisdiction and surface mapping | Governed course mapping reference | **Implementation exists but tests/validation/integration are incomplete** | Later course-jurisdiction and course-location artifacts appear to supersede part of this notebook. The remaining surface/configuration mapping must be reconciled explicitly so Notebook 04 is either retired into later governed references or given its own durable artifact. |
| 05 | Finishing positions and non-finish outcomes | Reusable result/outcome parser and governed outcome-code reference | **Reusable transformation module required** | Numeric positions, dead heats, disqualifications and non-finish codes are core database semantics. Notebook assertions alone are insufficient; module, tests, validator and database integration are required. |
| 06 | Race distance parsing | Reusable transformation module | **Implementation exists but tests/validation/integration are incomplete** | `race_distance.py` and `validate_race_distance.py` exist. The audit must verify unit tests for grammar and edge cases plus a documented schema/update path before declaring full closure. |
| 07 | Carried weight parsing | Reusable transformation module | **Implementation exists but tests/validation/integration are incomplete** | `carried_weight.py` and `validate_carried_weight.py` are listed in project documentation, but governed unit tests and database integration/update documentation are not identified. |
| 08 | Starting price parsing | Reusable transformation module plus contextual market metadata | **Reusable transformation module required** | Arithmetic parsing is deterministic even though market meaning is contextual. Parsing, blank handling, fractional/decimal representation and unresolved values require durable code and tests; jurisdictional comparability must remain separate metadata. |
| 09 | Jurisdiction, authority and betting-market context | Governed jurisdiction/context reference and loader | **Implementation exists but tests/validation/integration are incomplete** | `course_jurisdiction.py` and `validate_course_jurisdiction.py` exist. The audit must verify governed reference data, unit tests, merge cardinality rules, provenance and update documentation. |
| 10 | Remaining source-field inventory and triage | Reusable field-governance register | **Reusable reference required** | The notebook's one-treatment-per-field decision is operational project state. It must be exported into a durable machine-readable register that records owner notebook, treatment, status and dependencies. |
| 11 | Off-time and temporal semantics | Reusable clock parser/time reconstruction module | **Implementation exists but tests/validation/integration are incomplete** | `race_times.py` exists, but a conventional test file was not identified at `tests/test_race_times.py`. Verify actual tests, independent validation, rollover rules, timezone joins and database integration before closure. |
| 12 | Course location and timezone mapping | Governed reference data, loader and validator | **Implementation exists but tests/validation/integration are incomplete** | Strong closeout artifacts exist: permanent CSV references, report, closeout JSON, loader and independent validator. Add or verify unit tests for schema, uniqueness, merge cardinality, IANA validation and failure cases; document database update/migration handling if not already explicit. |
| 13 | Prize-money semantics and availability | Reusable transformation module | **Fully closed** | `prize_money.py`, `tests/test_prize_money.py`, `scripts/validate_prize_money.py` and `docs/PRIZE_MONEY_DATABASE_INTEGRATION.md` establish the model closeout pattern. |

## Gap register and repair order

The repair order is chronological unless a later artifact explicitly supersedes an earlier notebook. This avoids building new field investigations on undefined foundations.

| Priority | Notebook | Missing work | Closure evidence required |
|---:|---:|---|---|
| 1 | 01 | Tests and database/update documentation | **Completed on this branch.** Run the new unit tests locally and retain the existing independent source validator. |
| 2 | 02 | Export governed source-field inventory and raw sentinel/missingness policy | Machine-readable reference, loader if needed, tests for completeness/uniqueness, lineage integration document and validator. |
| 3 | 03 | Implement race and runner identity reconstruction | Module, synthetic edge-case tests, source-wide reconciliation validator, schema/key migration document. |
| 4 | 04 | Reconcile Notebook 04 with Notebooks 09 and 12 | Explicit supersession map; durable unresolved surface/configuration reference or documented retirement. |
| 5 | 05 | Implement finishing-position and outcome semantics | Parser/reference, tests for numeric/text/dead-heat/DSQ/anomaly cases, validator and schema integration. |
| 6 | 06 | Verify/add tests and integration document | Unit-test suite, update policy and database field mapping. |
| 7 | 07 | Verify/add tests and integration document | Unit-test suite, update policy and database field mapping. |
| 8 | 08 | Implement starting-price parsing | Parser, tests, validator and separation of arithmetic value from market context. |
| 9 | 09 | Verify governed reference and integration completeness | Tests, provenance/update path and database merge rules. |
| 10 | 10 | Export the field-treatment register | Machine-readable project governance artifact with completeness validation. |
| 11 | 11 | Verify/add temporal tests, validator and integration | Clock grammar, AM/PM interpretation, rollover, timezone and unresolved-case coverage. |
| 12 | 12 | Verify/add reference-loader tests and migration path | Synthetic failure tests and explicit reference version/update procedure. |
| 13 | 13 | No implementation gap identified | Keep as the reference closeout pattern. |

## Immediate stopping rule

No new source-field investigation should begin until every row above has either:

- reached **fully closed**; or
- been formally classified **no reusable artifact required** with the reason recorded.

A notebook marked complete in the README is not sufficient evidence of closure.

## Next notebook to repair

Notebook 02 is next. Its closeout should extract the source-field inventory and sentinel/missingness decisions into a durable reference before any race-identity implementation is built on top of them.
