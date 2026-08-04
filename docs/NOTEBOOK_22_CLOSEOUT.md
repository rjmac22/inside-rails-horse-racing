# Notebook 22 Closeout — Participant Identity

## Status

**Implementation pending local validation and governed-output commit.**

The analytical investigation is complete. Durable implementation, tests, validator and documentation have been added to the branch. The notebook-generated governed CSV outputs must be committed and the focused checks must pass before the notebook can be marked fully closed.

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

## Persisted outputs

### Jockey

- `data/processed/jockey_identity/jockey_strict_candidate_review_queue.csv`
- `data/processed/jockey_identity/verification_batches/jockey_strict_verification_batch_01.csv`

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

## Reusable implementation

- `src/inside_rails/participant_identity.py`

The module contains strict title separation, bounded trainer transition logic, exact owner token-multiset helpers and same-race owner evidence detection.

## Focused tests

- `tests/test_participant_identity.py`

The tests cover recognised and unknown titles, blanks, duplicate owner tokens, missing members, genuine token reordering, trainer date boundaries, overlap rejection and same-race evidence scope.

## Independent validation

- `scripts/validate_participant_identity.py`

The validator opens the immutable SQLite source read-only, applies `rowid <> 1`, reconstructs the source-wide jockey, trainer and owner populations, checks the exact accepted and unresolved baselines, and validates the governed CSV row counts.

## Database integration

- `docs/PARTICIPANT_IDENTITY_INTEGRATION.md`

The integration contract preserves raw labels, separates provisional identities from candidates, prohibits unsupported cross-role merging and defines cardinality and update controls.

## Manual-verification decision

**specialist_reference**

Notebook 22 did not add new external claims. Blank jockey, trainer and owner fields inherit the permanent Notebook 20 evidence recorded in `data/reference/manual_verifications.csv`. The participant identity acceptance rules themselves are source-internal.

## Reader-facing report

- `docs/REPORT_22_PARTICIPANT_IDENTITY.md`

## Lessons learned

- `docs/NOTEBOOK_22_LESSONS_LEARNED.md`

## Field-governance decision

No source field changes status in the source-field governance register. Jockey, trainer and owner raw-field semantics and blank governance were already closed through Notebook 20. Notebook 22 adds a separate participant identity layer rather than changing raw-field interpretation.

## Required local validation

Run only the focused checks at this stage:

```text
pytest -q tests/test_participant_identity.py
python scripts/validate_participant_identity.py
```

The complete repository test suite and all-validator sweep remain deferred until the end of the participant identity series or repair branch, in accordance with the project procedure.

## Completion gate

Notebook 22 may be marked fully closed only after:

1. all listed governed CSV outputs are committed;
2. focused unit tests pass;
3. the independent validator passes;
4. exact results are recorded here and in the audit register;
5. README and project plan status updates are reconciled;
6. the branch is synchronized and clean.
