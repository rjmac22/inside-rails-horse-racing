# Notebook 22 Closeout — Participant Identity

## Status

**Fully closed on 4 August 2026.**

The analytical investigation, governed outputs, reusable implementation, focused tests, strengthened independent source-wide validation, integration documentation and project-status reconciliation are complete.

A final closeout audit found that the jockey review queue had been persisted but the accepted same-person decision lacked a directly usable mapping file, and that the earlier validator checked only the queue row count rather than exact decision closure. Both defects were repaired and the strengthened validator passed locally against the immutable source on 4 August 2026.

## Bounded question

Which jockey, trainer and owner source labels can be linked through conservative, evidence-backed identity rules without overwriting raw values or forcing uncertain matches?

## Analytical conclusion

Broad participant string normalisation is unsafe.

Notebook 22 accepts only:

- `Mlle Marie Velon` and `Mme Marie Velon` as one provisional jockey label identity;
- 26 bounded `Mlle` to `Mme` trainer transitions around the 2023–2024 source presentation change;
- 41 owner token-order groups with direct same-race evidence, represented as provisional ownership compositions.

All other candidates remain unresolved.

## Reproducibility classification

The notebook is a **non-rerunnable archival construction record**.

Its executed outputs preserve the investigation, evidence and decisions. Durable reproducibility is provided through persisted governed outputs, reusable code, focused tests and an independent source-wide validator.

Because the archival notebook is not the repeatable execution path, it is not required to be rerun or to demonstrate notebook-level save-and-reload reproducibility. It should not be rerun piecemeal: the reusable module and source-wide validator are the governed route for repeating the implemented behaviour without relying on historical notebook state or risking governed output replacement.

## Persisted outputs

### Jockey

- `data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv`
- `data/processed/jockey_identity/verification_batches/jockey_strict_verification_batch_01.csv`
- `data/processed/jockey_identity/jockey_provisional_identity_mapping.csv`

### Trainer

- `data/processed/trainer_identity/trainer_strict_title_decisions.csv`
- `data/processed/trainer_identity/trainer_provisional_identity_mapping.csv`
- `data/processed/trainer_identity/trainer_provisional_identity_coverage.csv`
- `data/processed/trainer_identity/trainer_unresolved_identity_candidates.csv`
- `data/processed/trainer_identity/trainer_identity_governance_summary.csv`

### Owner

- `data/processed/owner_identity/owner_token_multiset_decisions.csv`
- `data/processed/owner_identity/owner_provisional_composition_mapping.csv`
- `data/processed/owner_identity/owner_provisional_composition_coverage.csv`
- `data/processed/owner_identity/owner_unresolved_token_multiset_candidates.csv`
- `data/processed/owner_identity/owner_identity_governance_summary.csv`

The original 12 governed outputs were committed in `d60ac32`. The direct two-row jockey mapping was added during the final closeout audit in `20296cd`.

## Reusable implementation

- `src/inside_rails/participant_identity.py`

The module contains strict title separation, bounded trainer transition logic, exact owner token-multiset helpers and same-race owner evidence detection.

## Focused tests

- `tests/test_participant_identity.py`

The tests cover recognised and unknown titles, blanks, duplicate owner tokens, missing members, genuine token reordering, trainer date boundaries, overlap rejection and same-race evidence scope.

Local evidence on 4 August 2026:

```text
14 passed in 0.61s
```

## Independent validation

- `scripts/validate_participant_identity.py`

The validator opens the immutable SQLite source read-only, applies `rowid <> 1`, reconstructs the source-wide jockey, trainer and owner populations, checks accepted and unresolved baselines, closes exactly over all governed jockey decisions, verifies decisive external provenance and validates the governed mappings and CSV counts.

Final strengthened local evidence on 4 August 2026:

```text
jockeys: 7,917 labels; 212 groups; 216 candidate relationships; 1 accepted; 1 distinct; 214 unresolved
trainers: 10,708 labels; 26 accepted groups; 6,350 mapped rows
owners: 98,234 labels; 41 accepted groups; 9,788 mapped rows; 895 unresolved groups
participant identity validation: PASS
```

The strengthened jockey section validates:

- exact closure over all 216 source candidate relationships;
- exactly one accepted same-person relationship, one confirmed distinct-person relationship and 214 unresolved relationships;
- the full governed fields and external provenance for `JOCKEY-STRICT-0001` and `JOCKEY-STRICT-0002`;
- unresolved preservation actions and deferred-review status;
- the exact two-row direct jockey mapping.

## Database integration

- `docs/PARTICIPANT_IDENTITY_INTEGRATION.md`

The integration contract preserves raw labels, separates provisional identities from candidates, prohibits unsupported cross-role merging and defines cardinality and update controls. It identifies the direct jockey mapping as a governed input alongside the trainer and owner mappings.

## Manual and external verification

**specialist_reference**

Two decisive jockey candidate decisions were externally verified, with their provenance preserved in `data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv`:

- `JOCKEY-STRICT-0001`: `Miss B ONeill` and `Mr B ONeill` were confirmed as different people using the source same-race collision and a published result, accessed on 4 August 2026;
- `JOCKEY-STRICT-0002`: `Mlle Marie Velon` and `Mme Marie Velon` were accepted as the same provisional source-label identity using a France Galop governing-body profile and a published jockey profile, accessed on 4 August 2026.

The governed candidate queue records the candidate IDs, evidence types and locators, access dates, confidence, review notes and database actions. It is the specific verification register for these participant decisions, so duplicating the records in `data/reference/manual_verifications.csv` is unnecessary.

These checks govern source-label equivalence within this dataset; they are not broader legal-identity claims. Trainer and owner acceptances remain source-internal structural equivalence decisions. Blank jockey, trainer and owner fields inherit the permanent Notebook 20 evidence recorded in `data/reference/manual_verifications.csv`. No raw source value was overwritten.

## Reader-facing report

- `docs/REPORT_22_PARTICIPANT_IDENTITY.md`

## Lessons learned

- `docs/NOTEBOOK_22_LESSONS_LEARNED.md`

## Field-governance decision

No source field changes status in the source-field governance register. Jockey, trainer and owner raw-field semantics and blank governance were already closed through Notebook 20. Notebook 22 adds a separate participant identity layer rather than changing raw-field interpretation.

## Programme reconciliation

The owner-identity and ownership-structure work originally scheduled as Notebook 23 was completed inside the consolidated Notebook 22 archival investigation. A separate Notebook 23 is therefore not required for this programme.

## Completion evidence

Notebook 22 is fully closed because:

1. all 13 governed CSV outputs are committed;
2. focused unit tests passed;
3. the strengthened independent validator passed over the immutable 1,851,285-row source population;
4. exact analytical results and decision closure are recorded here and in the audit register;
5. the direct accepted jockey mapping and decisive external provenance are validated;
6. README and project plan status are reconciled;
7. raw labels, lineage and unresolved candidates remain preserved.

The complete repository test suite and all-validator sweep remain deferred until the next appropriate end-of-series or repair-branch gate, in accordance with the project procedure.
