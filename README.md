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

### Notebooks 00–14

**Status:** complete and retrospectively implemented.

These notebooks established source immutability, grain and lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price parsing, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and runner-number governance, and complete governance of all 37 source fields.

Notebook 08 retains one deliberate governed source failure: the malformed standalone starting-price value `F` remains unresolved rather than being silently normalised.

### Notebook 15 — Beaten-distance semantics

**Status:** durable implementation complete; focused local validation pending.

Notebook 15 established that:

- `ovr_btn` is cumulative distance from the source physical-finish first-place reference;
- `btn` is the incremental margin from the preceding physical finisher or stored distance group;
- the text sentinel `-` means distance unavailable and must not become zero;
- official positions can reflect amendments while distance fields preserve the physical finish;
- positive winner distance and later-position zero overall distance are review flags, not automatic corrections;
- `btn = 0` with positive `ovr_btn` identifies a same-stored-distance group but does not prove an official dead heat.

The notebook passed a fresh-kernel run, persisted and reloaded its governed decision table, and captured bounded external verification under IDs `NB15-BTN-0001` through `NB15-BTN-0017`.

Durable outputs:

- `src/inside_rails/beaten_distance.py`
- `tests/test_beaten_distance.py`
- `scripts/validate_beaten_distances.py`
- `docs/BEATEN_DISTANCE_INTEGRATION.md`
- `docs/NOTEBOOK_15_FIELD_GOVERNANCE.md`
- `docs/NOTEBOOK_15_LESSONS_LEARNED.md`
- `reports/notebook_15_beaten_distance_semantics.md`
- `data/derived/notebook_15_beaten_distance_semantics/beaten_distance_field_decisions.csv`

Notebook 15 becomes fully closed when its focused tests and independent source-wide validator pass locally and the results are recorded. The complete repository test suite remains deferred until the end of the source-field series or repair branch.

## Retrospective implementation audit

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch `audit/retrospective-implementation-closeout` remains open while the remaining source-field studies continue. The complete test suite and all applicable validators will run again before final merge.

## Next bounded action

After Notebook 15 focused validation, continue the remaining source-field sequence with race classification and eligibility. Permanent entity design and the physical target schema remain deferred until the source-field studies required for structural reconstruction are complete or explicitly deferred.

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
