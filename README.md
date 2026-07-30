# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

The wider purpose is not database construction for its own sake. The project is intended to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The raw files are excluded from Git because of size, licensing and reproducibility considerations. The supplied `raceform.db` has broader geographical and date coverage than the title suggests, including substantial international racing and records through 27 May 2026.

The source contains:

- 1,851,285 governed runner rows;
- 189,043 reconstructed provisional races;
- 37 source columns;
- no declared primary key, foreign keys, indexes or uniqueness constraints.

The candidate provisional race key is `date + course + off`. The raw SQLite database remains read-only, and source queries use `DATA_ROW_PREDICATE = "rowid <> 1"`.

## Current status

### Notebooks 00–15

**Status:** complete and retrospectively implemented or fully closed as recorded in the audit register.

These notebooks established source immutability, grain and lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price parsing, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and runner-number governance, beaten-distance semantics, and complete governance of all 37 source fields.

Notebook 08 retains one deliberate governed source failure: the malformed standalone starting-price value `F` remains unresolved rather than being silently normalised.

### Notebook 16 — Race classification and eligibility

**Status:** fully closed.

Notebook 16 established that:

- `class`, `pattern` and `rating_band` are complementary source fields rather than one interchangeable hierarchy;
- canonical `Class N`, Listed/Group/Grade and exact `N-N` rating syntax can be parsed safely while preserving raw values;
- `--` and `(75-100)` remain explicit unresolved rating-band forms;
- `age_band` syntax can be parsed into source-stated bounds, but those bounds cannot be enforced universally against source runner ages;
- `sex_rest` is source shorthand rather than a complete official eligibility condition;
- the value `F` is overloaded and cannot be treated globally as fillies-only;
- authoritative sex-condition reconstruction is deferred to a future jurisdiction-specific study using official race-condition evidence.

Closeout validation passed with:

- fresh-kernel notebook execution and committed executed notebook (`ffd4344`);
- persisted decision-table reload across 7 governed fields;
- 25 focused classification and manual-verification tests in 0.03s;
- 1,851,285 source runner rows checked;
- 189,043 provisional races checked;
- complete partitioning of the observed parser vocabularies;
- exact unresolved rating-band vocabulary of `--` and `(75-100)`;
- manual-verification validation across 28 governed rows.

Manual evidence is captured under `NB16-AGE-0001` through `NB16-AGE-0004`.

Durable outputs:

- `src/inside_rails/race_classification.py`
- `tests/test_race_classification.py`
- `scripts/validate_race_classification.py`
- `docs/RACE_CLASSIFICATION_DATABASE_INTEGRATION.md`
- `docs/NOTEBOOK_16_FIELD_GOVERNANCE.md`
- `docs/NOTEBOOK_16_LESSONS_LEARNED.md`
- `reports/notebook_16_race_classification_and_eligibility.md`
- `data/derived/notebook_16_race_classification_and_eligibility/race_classification_field_decisions.csv`

The complete repository test suite remains deferred until the end of the source-field series or repair branch.

## Retrospective implementation audit

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch `audit/retrospective-implementation-closeout` remains open while the remaining source-field studies continue. The complete test suite and all applicable validators will run again before final merge.

## Next bounded action

Begin runner characteristics and equipment, bounded around runner `age`, `sex`, `hg` and related characteristic or equipment fields. Permanent entity design and the physical target schema remain deferred until the source-field studies required for structural reconstruction are complete or explicitly deferred.

## Working method

The project follows an evidence-led investigation-to-implementation cycle:

1. profile the raw source without altering it;
2. state one bounded question;
3. test coverage, uniqueness, exceptions and failure modes;
4. inspect material exceptions and preserve unresolved cases explicitly;
5. separate observation, interpretation, confidence and design decision;
6. translate the conclusion into a practical database consequence;
7. implement the rule reversibly while retaining raw values and lineage;
8. extract stable reusable logic into `src/inside_rails/`;
9. add focused tests and independent validation where justified;
10. produce the report and lessons learned;
11. update the audit register, field governance, README and project plan;
12. commit and verify the complete closeout.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.

See:

- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/REUSABLE_CODE_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`