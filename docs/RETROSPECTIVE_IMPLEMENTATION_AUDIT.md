# Retrospective Notebook Implementation Audit

## Purpose

This register audits completed notebook investigations against `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`. Analytical completion is not treated as implementation completion.

A notebook is fully closed only when its conclusion, reproducibility or archival classification, persisted outputs, reusable implementation, focused tests, independent validation, database consequence, manual-verification decision, report, lessons and project-status updates are complete.

## Classification register

| Notebook | Investigation | Audit classification | Principal evidence or retained limit |
|---|---|---|---|
| 00 | Project scope and methodology | **No reusable artifact required** | Durable methodology and closure rules are documented. |
| 01 | Source database structure profile | **Fully closed** | Reusable profile module, tests, validator and integration documentation. |
| 02 | Source field quality profile | **Fully closed** | Governed 37-field reference, loader, tests, validator and lineage policy. |
| 03 | Race identity and source-key reconstruction | **Fully closed** | Reusable identity profiling, tests and source-wide reconciliation. |
| 04 | Course jurisdiction and surface mapping | **Fully closed** | Reconciled jurisdiction and bounded surface governance. |
| 05 | Finishing positions and non-finish outcomes | **Fully closed** | Complete governed result partition. |
| 06 | Race distance parsing | **Fully closed** | Parser, tests, validator and integration contract. |
| 07 | Carried weight parsing | **Fully closed** | Parser, tests, validator and integration contract. |
| 08 | Starting price parsing | **Fully closed with governed anomaly** | The lone raw `F` remains preserved as unresolved; the validator passes only when the exact anomaly remains `{'F': 1}`. |
| 09 | Jurisdiction, authority and betting-market context | **Fully closed** | Governed bounded context and source validation. |
| 10 | Remaining source-field inventory and triage | **Fully closed** | Field-governance register and immutable-source schema validation. |
| 11 | Off-time and temporal semantics | **Fully closed** | Clock parsing and temporal helper validation. |
| 12 | Course location and timezone mapping | **Fully closed** | Complete 395-identity timezone reference and source join. |
| 13 | Prize-money semantics and availability | **Fully closed** | Reusable governed parser, tests and validator; minor-unit fall-through defect repaired during final sweep. |
| 14 | Runner counts, numbers and entries | **Fully closed** | Reusable interpretation and source-wide validation. |
| 15 | Beaten-distance semantics | **Fully closed** | Conservative parsing, structural flags and independent validation. |
| 16 | Race classification and eligibility | **Fully closed** | Structural parsers, unresolved preservation and source-wide validation. |
| 17 | Runner characteristics and equipment | **Fully closed — archival route** | Persisted outputs, reusable implementation, manual evidence and source validation. |
| 18 | Ratings semantics and availability | **Fully closed** | Exact unavailable and invalid-value governance across `or`, `rpr` and `ts`. |
| 19 | Horse and pedigree identity | **Fully closed — archival route** | 353 governed transitions and 611 provisional occurrences; five cases remain deliberately unresolved pending authority responses. |
| 20 | Connections and ownership identity | **Fully closed** | 46 permanent verifications, 28 supplementations and 18 preserved unresolved blanks. |
| 21 | Comment and embedded information | **Fully closed** | Persisted profiles, conservative classifier, focused tests, independent validator, integration contract, report, lessons and successful branch-wide sweep. |
| 22 | Jockey, trainer and owner participant identity | **Fully closed — archival route** | 212 jockey candidate groups, 26 bounded trainer transitions and 41 same-race-supported ownership compositions; broad normalisation remains prohibited and 895 owner groups remain unresolved. |

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

Focused validation on 4 August 2026:

- `pytest -q tests/test_comment_information.py`: **8 passed in 0.46s**;
- `python scripts/validate_comment_information.py`: **PASS**.

## Notebook 22 evidence

The consolidated archival investigation covers jockey, trainer and owner participant identity. The owner programme originally scheduled separately as Notebook 23 was completed inside Notebook 22; no separate Notebook 23 is required.

Established baselines:

- jockey labels: **7,917**;
- jockey candidate groups: **212**;
- jockey candidate relationships: **216**;
- confirmed provisional jockey identity groups: **1**;
- trainer labels: **10,708**;
- accepted bounded trainer groups: **26**;
- accepted trainer labels: **52**;
- trainer mapped rows: **6,350**;
- owner labels: **98,234**;
- owner candidate groups: **936**;
- same-race-supported ownership compositions: **41**;
- accepted owner labels: **95**;
- owner mapped rows: **9,788**;
- unresolved owner groups: **895**.

Manual-verification decision: `specialist_reference`.

Durable artifacts:

- `notebooks/22_jockey_and_trainer_identity.ipynb`;
- 12 governed CSV outputs under `data/processed/jockey_identity/`, `data/processed/trainer_identity/` and `data/processed/owner_identity/`;
- `src/inside_rails/participant_identity.py`;
- `tests/test_participant_identity.py`;
- `scripts/validate_participant_identity.py`;
- `docs/PARTICIPANT_IDENTITY_INTEGRATION.md`;
- `docs/REPORT_22_PARTICIPANT_IDENTITY.md`;
- `docs/NOTEBOOK_22_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_22_CLOSEOUT.md`.

Focused local validation on 4 August 2026:

```text
14 passed in 0.61s

jockeys: 7,917 labels; 212 groups; 216 candidate relationships
trainers: 10,708 labels; 26 accepted groups; 6,350 mapped rows
owners: 98,234 labels; 41 accepted groups; 9,788 mapped rows; 895 unresolved groups
participant identity validation: PASS
```

The governed outputs were committed in `d60ac32`.

## End-of-series validation evidence

The first complete repository test run after Notebook 21 found two genuine integration defects:

1. a sub-minor-unit Great Britain prize value was incorrectly relabelled `currency_unresolved` after failing canonicalisation;
2. the source-field loader did not permit the explicit later-notebook status `implemented_pending_validation`.

Both were repaired and tested. The governance registers were then reconciled so completed source-field studies no longer remained falsely open or pending.

Final local evidence for the source-field series on 4 August 2026:

```text
256 passed in 0.96s
```

All 26 then-discovered independent validator scripts passed. This included the complete immutable-source validators and confirmation that Notebook 08's lone `F` anomaly remained exactly preserved.

Final field-governance totals:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

The source-field governance reference contains all 37 fields, requires raw preservation for all 37, and matches the SQLite field names, order and declared types.

Notebook 22 was subsequently closed with focused tests and its independent source-wide validator. A new full repository suite and all-validator sweep remain deferred until the next appropriate end-of-series or repair-branch gate.

## Current position

The retrospective source-field implementation programme is fully closed through Notebook 21. The consolidated participant identity programme is fully closed through Notebook 22.

Before physical database construction, complete the Notebook 19 authority-response gate. After that gate, proceed to entity and key design using the governed race, runner, horse, jockey, trainer and ownership identity requirements.
