# Retrospective Notebook Implementation Audit

## Purpose

This register audits completed notebook investigations against the project closeout standard. Analytical completion is not treated as implementation completion.

The permanent standard is recorded in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

A notebook is fully closed only when, as applicable:

1. it runs from a fresh kernel, or is explicitly archived with durable replacement validation;
2. conclusions and limitations are recorded;
3. reusable transformation logic or governed reference data is extracted;
4. tests cover governed rules and edge cases;
5. an independent validator exists where appropriate;
6. the database consequence and update path are documented;
7. local test and validator results are recorded.

This audit covers committed repository artifacts. Local uncommitted files are outside its evidence base.

## Classification register

| Notebook | Investigation | Required durable artifact | Audit classification | Evidence and principal gap |
|---|---|---|---|---|
| 00 | Project scope and methodology | No reusable field transformation required | **No reusable artifact required** | Methodology and closeout rules belong in durable documentation rather than a parser. |
| 01 | Source database structure profile | Reusable source-access/profile module | **Fully closed on this audit branch** | Existing module and validator supplemented by governed tests and integration documentation; local tests passed. |
| 02 | Source field quality profile | Reusable field inventory, sentinel policy and lineage specification | **Fully closed on this audit branch** | Governed 37-field reference, loader, tests, validator and integration documentation exist; local tests and source-wide validation passed. |
| 03 | Race identity and source-key reconstruction | Reusable race/runner identity transformation and reconciliation validator | **Fully closed on this audit branch** | Identity module, tests, source-wide reconciliation validator and database integration documentation passed locally. |
| 04 | Course jurisdiction and surface mapping | Reconciled jurisdiction ownership plus bounded surface transformation | **Fully closed on this audit branch** | Reconciliation document, surface module, tests and independent source validation passed locally. |
| 05 | Finishing positions and non-finish outcomes | Reusable result/outcome parser and governed representation categories | **Fully closed on this audit branch** | Result parser, tests, complete source partition validator and database integration documentation passed locally. |
| 06 | Race distance parsing | Reusable transformation module | **Fully closed on this audit branch** | Parser, tests, validator and database integration documentation passed locally. |
| 07 | Carried weight parsing | Reusable transformation module | **Fully closed on this audit branch** | Parser, tests, validator and database integration documentation passed locally. |
| 08 | Starting price parsing | Reusable arithmetic parser plus separate contextual market metadata | **Implemented with deliberate governed validator failure** | Parser and tests pass. Source validator deliberately fails on the exact known unresolved source anomaly `{'F': 1}`. |
| 09 | Jurisdiction, authority and betting-market context | Governed jurisdiction/context reference and loader | **Fully closed on this audit branch** | Tests and bounded-context source validation passed. |
| 10 | Remaining source-field inventory and triage | Reusable field-governance register | **Fully closed on this audit branch** | Tests and immutable-source schema validation passed. |
| 11 | Off-time and temporal semantics | Reusable clock parser/time reconstruction module | **Fully closed on this audit branch** | Tests and immutable-source clock validation passed. |
| 12 | Course location and timezone mapping | Governed reference data, loader and validator | **Fully closed on this audit branch** | Permanent-reference validation confirmed complete governed timezone coverage. |
| 13 | Prize-money semantics and availability | Reusable transformation module | **Fully closed** | Module, tests, independent validator and database integration document establish the model closeout pattern. |
| 14 | Runner counts, numbers and entries | Reusable `ran` profile and `num` interpretation module | **Fully closed on this audit branch** | Module, tests, independent validators, source-wide validation and integration documentation passed locally. |
| 15 | Beaten-distance semantics | Reusable conservative parser and structural review flags | **Fully closed on this audit branch** | Fresh-kernel notebook run passed; persisted decisions and manual-verification provenance exist. The reusable module, 15 focused tests, independent source validator, integration contract, field governance, Minto report and lessons learned are committed. Source-wide validation passed across 1,851,285 runner rows. |
| 16 | Race classification and eligibility | Reusable structural parsers with unresolved-state preservation | **Fully closed on this audit branch** | Fresh-kernel notebook execution passed and the executed notebook is committed at `ffd4344`. Persisted decisions reloaded successfully; 25 focused tests passed; classification and manual-verification validators passed. |

## Notebook 16 closure evidence

Durable artifacts:

- `notebooks/16_race_classification_and_eligibility.ipynb`
- `data/derived/notebook_16_race_classification_and_eligibility/race_classification_field_decisions.csv`
- `data/reference/manual_verifications.csv` (`NB16-AGE-0001` through `NB16-AGE-0004`)
- `src/inside_rails/race_classification.py`
- `tests/test_race_classification.py`
- `scripts/validate_race_classification.py`
- `docs/RACE_CLASSIFICATION_DATABASE_INTEGRATION.md`
- `docs/NOTEBOOK_16_FIELD_GOVERNANCE.md`
- `docs/NOTEBOOK_16_LESSONS_LEARNED.md`
- `reports/notebook_16_race_classification_and_eligibility.md`

Recorded focused validation:

- fresh-kernel notebook execution: **passed**;
- executed notebook commit: `ffd4344`;
- persisted decision table reload: **7 governed fields passed**;
- `pytest -q tests/test_race_classification.py tests/test_manual_verifications.py`: **25 passed in 0.03s**;
- race-classification source validator: **passed**;
- runner rows checked: **1,851,285**;
- provisional races checked: **189,043**;
- unresolved rating-band vocabulary: exactly `--` and `(75-100)`;
- manual-verification validator: **28 governed rows passed**;
- verification statuses: 19 confirmed, 8 contradicted, 1 partially confirmed;
- database actions: 13 evidence-only, 1 preserve-raw-unresolved, 2 reference-enrichment, 9 source-correction-candidate, 3 source-supplementation.

Manual-verification decision: **captured**.

## Current position

Notebook 16 is fully closed. The next source-field study is runner characteristics and equipment, bounded around runner `age`, `sex`, `hg` and related characteristic or equipment fields.

The complete repository test suite and all-validator sweep remain deferred until the end of the source-field series or repair branch. Notebook 08's deliberate lone `F` failure remains governed evidence rather than a defect to normalise away.