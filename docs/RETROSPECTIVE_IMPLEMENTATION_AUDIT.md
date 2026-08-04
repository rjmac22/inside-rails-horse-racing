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
| 15 | Beaten-distance semantics | Reusable conservative parser and structural review flags | **Fully closed on this audit branch** | Fresh-kernel notebook run passed; persisted decisions and manual-verification provenance exist. The reusable module, focused tests, independent source validator, integration contract, field governance, Minto report and lessons learned are committed. |
| 16 | Race classification and eligibility | Reusable structural parsers with unresolved-state preservation | **Fully closed on this audit branch** | Fresh-kernel notebook execution passed; persisted decisions, focused tests, classification validator and manual-verification validator passed. |
| 17 | Runner characteristics and equipment | Governed age/sex/headgear interpretation with exact anomaly lineage | **Fully closed on this audit branch** | Notebook is explicitly archived as non-rerunnable. Persisted outputs, reusable module, focused tests, independent source validation, integration document, report, lessons and committed manual-verification provenance passed closure. |
| 18 | Ratings semantics and availability | Governed `or`/`rpr`/`ts` transformation with exact invalid-value lineage | **Fully closed on this audit branch** | Fresh-kernel notebook execution passed. Reusable module, focused tests, independent source-wide validator, integration document, report, lessons and three permanent verification records are committed. |
| 19 | Horse and pedigree identity | Governed pedigree reconciliation and provisional horse-occurrence identity | **Fully closed on this audit branch** | Explicit archival classification, specialist governance, reusable implementation, focused tests, manual-verification validation, independent source-wide validator, database integration documentation and persisted/reloaded outputs are committed. Five authority-dependent cases remain governed as unresolved rather than blocking closure. |
| 20 | Connections and ownership identity | Governed blank-field supplementation without unsupported entity resolution | **Fully closed on this audit branch** | Notebook conclusions, 46 permanent verification records, 28 governed repair rows, reusable implementation, focused tests, manual-register validation, independent source-wide validation, integration documentation and closeout record are committed. Eighteen blanks remain deliberately unresolved. |
| 21 | Comment and embedded information | Conservative raw-text state governance without speculative parsing | **Implemented pending local validation** | Executed notebook, persisted source profile and decisions, reusable classifier, focused tests, independent validator, integration contract, report, lessons and closeout record are committed. Focused local validation and the end-of-series repository sweep remain outstanding. |

## Notebook 19 closure evidence

Durable artifacts:

- `notebooks/19_horse_and_pedigree_identity.ipynb`;
- `data/reference/horse_pedigree_identity_governance.csv`;
- Notebook 19 records in `data/reference/manual_verifications.csv`;
- `src/inside_rails/horse_pedigree_identity.py`;
- `src/inside_rails/horse_pedigree_identity_counts.py`;
- focused tests in `tests/test_horse_pedigree_identity.py` and `tests/test_horse_pedigree_identity_counts.py`;
- `scripts/validate_horse_pedigree_identity.py`;
- `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`;
- `docs/NOTEBOOK_19_CLOSEOUT.md`;
- persisted outputs under `data/processed/horse_pedigree_identity/`.

Recorded validation evidence includes 353 governed transitions partitioned into 87 `Corrected`, 261 `Different horse` and 5 `Unresolved`, plus 611 provisional source-internal horse occurrences. The five unresolved cases remain subject to the mandatory pre-database authority-response gate recorded in `docs/PROJECT_PLAN.md`.

## Notebook 20 closure evidence

Durable artifacts:

- `notebooks/20_connections_and_ownership_identity.ipynb`;
- Notebook 20 records in `data/reference/manual_verifications.csv`;
- `data/reference/connection_identity_repairs.csv`;
- `src/inside_rails/connection_identity.py`;
- `tests/test_connection_identity.py`;
- `scripts/validate_connection_identity.py`;
- `docs/CONNECTION_IDENTITY_INTEGRATION.md`;
- `docs/NOTEBOOK_20_CLOSEOUT.md`.

Recorded validation evidence: 46 raw blank field occurrences across 44 source rows, 28 confirmed source supplementations and 18 unresolved preserved blanks. Raw connection labels remain source-presented text rather than canonical person or organisation identifiers.

## Notebook 21 implementation evidence

Durable artifacts:

- `notebooks/21_comment_and_embedded_information.ipynb`;
- `data/processed/comment_information/comment_source_profile.csv`;
- `data/processed/comment_information/comment_semantic_decisions.csv`;
- `src/inside_rails/comment_information.py`;
- `tests/test_comment_information.py`;
- `scripts/validate_comment_information.py`;
- `docs/COMMENT_INFORMATION_INTEGRATION.md`;
- `docs/REPORT_21_COMMENT_AND_EMBEDDED_INFORMATION.md`;
- `docs/NOTEBOOK_21_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_21_CLOSEOUT.md`.

Established baselines:

- governed runner rows: **1,851,285**;
- provisional races: **189,043**;
- SQL null comments: **0**;
- empty-string comments: **340,394**;
- probable-placeholder or unresolved-code rows: **238**;
- substantive-text rows: **1,510,653**;
- candidate jurisdictions: **36**;
- unresolved candidate-jurisdiction races: **0**.

Manual-verification decision: `not_applicable`. Final conclusions depend on source-internal evidence; the informal equipment-code hypothesis was not accepted as validation and was not supported by source testing.

## Current position

The analytical source-field series is complete through Notebook 21. Notebook 21 remains **implemented pending local validation** until its focused test and validator results are recorded.

The next branch-level action is the end-of-series complete repository test suite and all-validator sweep, followed by repair of any cross-notebook integration defects. Notebook 08's deliberate lone `F` failure remains governed evidence rather than a defect to normalise away.

After the sweep, complete the mandatory authority-response gate and begin the participant identity studies before physical participant schema design or participant-level analysis.
