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

The complete repository test suite remains deferred until the end of the source-field series or repair branch.

### Notebook 17 — Runner characteristics and equipment

**Status:** implemented pending local validation.

Notebook 17 established that:

- `age` is complete and usable as the source-recorded runner age without automatic clipping or correction from `age_band`;
- the standard sex codes `C`, `F`, `G`, `H`, `M` and `R` are governed;
- two isolated sex-field contamination rows require exact verification-backed corrections;
- `hg` is blank on 1,122,490 rows and populated on 728,795 rows;
- all 60 populated headgear values can be decomposed into ordered governed components;
- source-specific `c` is interpreted as eyecover with preserved provenance;
- 5,932 trailing-`1` rows begin on 15 October 2025 and represent a source declaration rather than a complete lifetime equipment history.

Notebook 17 is classified as a non-rerunnable archival construction record. Durable replacement validation is provided outside the notebook.

Durable outputs:

- `src/inside_rails/runner_characteristics.py`;
- `tests/test_runner_characteristics.py`;
- `scripts/validate_runner_characteristics.py`;
- `docs/NOTEBOOK_17_DATABASE_INTEGRATION.md`;
- `docs/NOTEBOOK_17_RUNNER_CHARACTERISTICS_REPORT.md`;
- `docs/NOTEBOOK_17_LESSONS_LEARNED.md`;
- `data/processed/notebook_17_runner_characteristics/runner_sex_governance.csv`;
- `data/processed/notebook_17_runner_characteristics/runner_headgear_governance.csv`;
- `data/processed/notebook_17_runner_characteristics/runner_characteristics_decisions.csv`.

Focused tests, the runner-characteristics validator and manual-verification validation must still be run locally against the source database before the status changes to fully closed.

## Retrospective implementation audit

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch `audit/retrospective-implementation-closeout` remains open while the remaining source-field studies continue. The complete test suite and all applicable validators will run again before final merge.

## Next bounded action

Begin ratings semantics and availability, bounded around `or`, `rpr` and `ts`. Permanent entity design and the physical target schema remain deferred until the source-field studies required for structural reconstruction are complete or explicitly deferred.

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
