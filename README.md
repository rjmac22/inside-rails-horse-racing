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

### Notebooks 00–16

**Status:** complete and retrospectively implemented or fully closed as recorded in the audit register.

These notebooks established source immutability, grain and lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price parsing, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and runner-number governance, beaten-distance semantics, race classification and eligibility, and complete governance of all 37 source fields.

Notebook 08 retains one deliberate governed source failure: the malformed standalone starting-price value `F` remains unresolved rather than being silently normalised.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Notebook 17 governed runner age, sex and headgear, including exact verification-backed corrections for two contaminated sex values and source-specific eyecover normalisation.

### Notebook 18 — Ratings semantics and availability

**Status:** fully closed.

Notebook 18 established that:

- `or` is the official pre-race handicap mark applicable to the runner;
- `rpr` is a retrospective and potentially revisable Racing Post performance rating;
- `ts` is a retrospective Racing Post speed figure;
- the exact Unicode en dash `–` means unavailable and must parse to null rather than zero;
- the three ratings require independent nullable analytical values and statuses;
- the isolated source row `rowid = 1619851`, `rpr = 775` is an invalid source value whose raw value remains preserved and whose replacement remains unresolved;
- observed candidate ranges are regression baselines, not universal future validity rules.

Durable outputs:

- `notebooks/18_ratings_semantics_and_availability.ipynb`;
- `src/inside_rails/ratings.py`;
- `tests/test_ratings.py`;
- `scripts/validate_ratings.py`;
- `docs/NOTEBOOK_18_RATINGS_DATABASE_INTEGRATION.md`;
- `docs/NOTEBOOK_18_RATINGS_REPORT.md`;
- `docs/NOTEBOOK_18_LESSONS_LEARNED.md`;
- three Notebook 18 records in `data/reference/manual_verifications.csv`.

Closeout validation passed with:

- `22 passed in 0.06s` across ratings and manual-verification focused tests;
- ratings validation across all 1,851,285 governed runner rows;
- `or`: 1,116,633 available and 734,652 unavailable, range 1–181;
- `rpr`: 1,644,175 available, 207,109 unavailable and one invalid, range 1–184;
- `ts`: 1,227,384 available and 623,901 unavailable, range 1–178;
- manual-verification validation across 36 governed rows.

## Retrospective implementation audit

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch `audit/retrospective-implementation-closeout` remains open while the remaining source-field studies continue. The complete test suite and all applicable validators will run again before final merge.

## Next bounded action

Begin horse and pedigree identity, bounded around `horse`, `sire`, `dam` and `damsire`. Permanent entity design and the physical target schema remain deferred until the remaining source-field studies required for structural reconstruction are complete or explicitly deferred.

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
