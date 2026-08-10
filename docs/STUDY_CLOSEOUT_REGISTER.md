# Inside Rails Reader Study Closeout Register

## Purpose

This register is the reader-study successor to the database-focused retrospective implementation audit for tracking study closure state.

It records whether a reader-facing study is analytically complete, reproducible, externally evidenced where required, and fully closed under `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The register does not replace the detailed closeout record for each study. It provides the concise project-level status needed by the README and project plan.

## Status vocabulary

- `in_progress` — analytical work is active;
- `analytically_complete` — the bounded question has been answered, but closeout work remains;
- `closeout_validation_pending` — analytical and documentation closeout is complete but required local validation evidence has not yet been recorded;
- `fully_closed` — every applicable closeout item is complete and validation evidence is recorded;
- `revisit_required` — a later finding materially affects a previously closed study and the revisit register governs the next action.

## Studies

| Study | Notebook | Analytical status | Reproducibility | External evidence | Implementation / validator consequence | Closeout status | Next action |
|---|---|---|---|---|---|---|---|
| Great Britain 01 — Governance and structure | `studies/jurisdictions/great_britain/01_governance_and_structure.ipynb` | complete | fresh-kernel execution passed 2026-08-10 | captured: `ST01-GOV-0001`, `ST01-GOV-0002`; race-type specialist evidence retained separately | no new main-study production transform or validator; existing study overlay used for governed post-v3 corrections | `closeout_validation_pending` | run focused manual-verification tests and register validator, record exact results, then mark `fully_closed` |

## Governing closeout record

Great Britain Study 01:

`docs/studies/GB_01_GOVERNANCE_AND_STRUCTURE_CLOSEOUT.md`

## Next planned reader study

Great Britain Study 02 — **Types of British racing**.

The study should establish the authoritative Flat/Jump structure before using governed analytical race-type values. Racecourse identity and physical-venue semantics remain a later bounded study.
