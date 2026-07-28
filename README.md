# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

The wider purpose is not database construction for its own sake. The project is intended to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The downloaded raw source files are intentionally excluded from Git because of size, licensing and reproducibility considerations.

Notebook 01 established that the supplied `raceform.db` has broader geographical and date coverage than the dataset title suggests, including substantial international racing and records through 27 May 2026.

The source contains one denormalised runner-grain table with:

- 1,851,285 data-like runner rows;
- 189,043 reconstructed provisional races;
- 37 source columns;
- no declared primary key, foreign keys, indexes or uniqueness constraints.

The established candidate provisional race key is:

`date + course + off`

The raw SQLite database remains read-only, and source queries use:

`DATA_ROW_PREDICATE = "rowid <> 1"`

## Current status

### Notebooks 00–10 — Source understanding and core parsing

**Status:** complete and retrospectively implemented.

These notebooks established source immutability, source grain and quality, race and runner reconstruction, jurisdiction and surface context, result semantics, distance and carried-weight parsing, bounded starting-price parsing, and complete governance of all 37 source fields.

Reusable implementations, tests, validators and database-integration documents now exist for the governed rules established in these notebooks.

Notebook 08 retains one deliberate governed source failure: the malformed standalone starting-price value `F` remains unresolved rather than being silently normalised.

### Notebook 11 — Off-time and temporal semantics

**Status:** fully closed; 9 tests and immutable-source validation passed.

Established strict parsing of all observed source `off` values, explicit treatment of 12-hour ambiguity, and timezone-aware reconstruction only where an evidence-backed branch and course timezone are supplied.

Validation covered:

- 1,851,285 source rows;
- 1,380 distinct raw `off` values;
- 189,043 provisional races;
- 0 unresolved clock representations.

Reusable outputs:

- `src/inside_rails/off_time.py`
- `tests/test_off_time.py`
- `scripts/validate_off_time.py`
- `docs/OFF_TIME_DATABASE_INTEGRATION.md`

### Notebook 12 — Course location and timezone mapping

**Status:** fully closed; archived executed construction record, 13 tests and permanent-reference validation passed.

The governed reference now contains:

- 395 permanent jurisdiction-qualified course identities;
- 395 valid IANA timezone assignments;
- 0 unresolved timezone assignments;
- 51 distinct IANA timezones.

It preserves the distinction between course identity, exact venue enrichment and timezone sufficiency, using safe jurisdiction defaults only where defensible and course-level review in multi-timezone jurisdictions.

Reusable outputs include:

- `data/reference/course_locations.csv`
- `src/inside_rails/course_locations.py`
- `tests/test_course_locations.py`
- `scripts/validate_course_locations.py`
- `docs/COURSE_LOCATIONS_DATABASE_INTEGRATION.md`

### Notebook 13 — Prize-money semantics and availability

**Status:** fully closed.

Established that `prize` is runner-level recorded prize money rather than the advertised race purse. Great Britain and Ireland support direct governed GBP and EUR parsing, blank values remain null, and foreign source-presented values remain unresolved unless a jurisdiction-specific reconstruction is separately validated.

Reusable implementation, tests, source validation and database-integration documentation establish the current notebook closeout pattern.

## Retrospective implementation audit

The retrospective closeout of Notebooks 00–13 is complete on branch `audit/retrospective-implementation-closeout`.

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch should remain open while the remaining source-field and database work continues. The complete test suite and all applicable validators will be run again before final merge.

## Next bounded action

### Notebook 14 — Runner counts, numbers and entries

Fields:

- `ran`
- `num`

Bounded question:

> What do `ran` and `num` represent across jurisdictions, how reliably do they describe runners and entries, and what can safely be stored in the future database?

The study should establish:

- whether `ran` represents declared starters, source rows, finishers or another count;
- the known races where source rows fall below `ran`;
- blank, zero, duplicate and unusual `num` values;
- jurisdiction-dependent numbering and coupled entries;
- why `num` must not be used as a universal runner key;
- safe staging fields, statuses, constraints and validation rules.

Permanent entity design and the physical target schema remain deferred until the source-field studies required for structural reconstruction are complete or explicitly deferred.

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
