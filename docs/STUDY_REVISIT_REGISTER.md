# Inside Rails Study Revisit Register

## Purpose

This register records completed or published studies that may need reassessment because later work has changed, corrected or materially qualified the evidence on which they depended.

Use this register whenever:

- a database defect is corrected;
- field semantics or governance changes;
- a canonical transformation changes;
- new source limitations are discovered;
- a methodological lesson exposes a weakness in an earlier study;
- new external evidence materially affects an earlier conclusion;
- a study discovers information that may invalidate or qualify previous work.

The register exists so potential impacts are captured immediately rather than left to memory.

A new upstream change does not automatically require a complete rerun of every dependent study. Record the possible impact first, assess materiality, then take proportionate action.

---

## Status vocabulary

Use one of the following statuses.

### `review_required`

A later change may materially affect the study and impact has not yet been assessed.

### `review_in_progress`

The earlier study is currently being reassessed.

### `reviewed_no_change`

The later change was assessed and does not materially alter the study's analytical conclusion or published work.

### `revision_required`

The study remains usable but its analysis, conclusion, figures or publication requires material revision.

### `superseded`

The earlier study should no longer be treated as the current analytical result because a replacement study or analysis has taken its place.

### `withdrawal_required`

The original conclusion is no longer defensible and published work should be withdrawn or clearly marked as invalid.

---

## Severity vocabulary

### `low`

Potential impact is narrow and unlikely to change the main conclusion, but should be checked for completeness.

### `medium`

Potential impact could change a supporting result, limitation, subgroup conclusion, figure or wording.

### `high`

Potential impact could change the principal conclusion, invalidate the population or measure, or materially affect published claims.

---

## Revisit register

| revisit_id | study_id | study_path | trigger_date | trigger_type | trigger_summary | affected_evidence | severity | publication_impact_possible | status | resolution_summary | resolved_date | resolving_commit_or_artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

No study revisit entries have been recorded yet.

---

## Entry rules

Create an entry as soon as there is a reasonable possibility that later work could materially affect an earlier study.

Do not wait until the impact has been proved.

Each entry should identify:

- the affected study;
- the later event that triggered the concern;
- the field, transformation, population, method or claim potentially affected;
- severity;
- whether published material could be affected;
- current review status.

When the review is completed, record:

- whether the original result changed;
- whether tables or figures changed;
- whether the principal conclusion changed;
- whether published work requires correction;
- the commit, notebook, database release or other durable artifact supporting the resolution.

---

## Mandatory impact checks

### Database and governance work

At closeout ask:

> Could this change affect any completed study?

If yes or reasonably possibly, add a register entry before declaring the database or governance work closed.

### Study work

At closeout ask:

> Has anything discovered in this study created a reason to revisit an earlier study?

If yes or reasonably possibly, add a register entry.

### Publication correction

Where reassessment materially affects published work, follow the correction rules in `docs/STUDY_RESEARCH_PLAYBOOK.md`.

Do not silently replace a material historical analytical conclusion without preserving what changed and why.
