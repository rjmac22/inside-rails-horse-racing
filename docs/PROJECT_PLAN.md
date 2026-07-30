# Inside Rails Project Plan

## Objective

Build a documented, reproducible and professionally structured horse-racing analytical database from the supplied third-party source products.

The project is evidence-led. Profiling and domain interpretation come before cleaning, schema design or predictive modelling.

## Standing method

For each substantive notebook:

1. state one bounded question;
2. declare the source and grain under investigation;
3. separate profiling evidence from interpretation;
4. avoid irreversible cleaning decisions inside exploratory work;
5. extract stable reusable plumbing only after it works;
6. add focused unit tests including failure behaviour;
7. validate extracted code and governed references independently where justified;
8. document the database and update consequence;
9. produce a concise Minto-style report;
10. record decisions, uncertainty, lessons learned and next actions;
11. update the audit register, field governance, this plan and the project README;
12. commit and verify the complete closeout.

The full procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

The raw SQLite database remains read-only. All source-data queries use `DATA_ROW_PREDICATE = "rowid <> 1"`.

Established source population:

- 1,851,285 governed runner rows;
- 189,043 provisional races;
- 37 source columns;
- candidate provisional race key: `date + course + off`.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status:** complete and retrospectively implemented.

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and parsing

### Notebooks 04–15

**Status:** complete and retrospectively implemented or fully closed.

Established course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, and governance of all 37 source fields.

Notebook 08 retains one deliberate governed validator failure for the malformed standalone source value `F`.

### Notebook 16 — Race classification and eligibility

**Status:** fully closed.

Established complementary, jurisdiction-sensitive interpretation of `class`, `pattern`, `rating_band`, `age_band` and `sex_rest`, with raw and unresolved states preserved.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Governed rules:

- preserve integer `age` as the source-recorded runner age;
- do not overwrite age from race-level `age_band` or clip unusual values automatically;
- normalise the six standard sex codes;
- apply the two sex contamination corrections only through exact verification-backed lineage;
- preserve blank `hg` as field not supplied;
- decompose all populated headgear values into ordered governed components;
- normalise source-specific `c` to eyecover while preserving the raw token;
- retain trailing `1` only as a source-declared first-time flag from 15 October 2025 onward;
- do not reconstruct historical lifetime first use from suffix absence or local source history.

Durable outputs:

- `notebooks/17_runner_characteristics_and_equipment.ipynb`;
- `src/inside_rails/runner_characteristics.py`;
- `tests/test_runner_characteristics.py`;
- `scripts/validate_runner_characteristics.py`;
- `docs/NOTEBOOK_17_DATABASE_INTEGRATION.md`;
- `docs/NOTEBOOK_17_RUNNER_CHARACTERISTICS_REPORT.md`;
- `docs/NOTEBOOK_17_LESSONS_LEARNED.md`;
- three persisted governed CSV outputs under `data/processed/notebook_17_runner_characteristics/`;
- five permanent Notebook 17 records in `data/reference/manual_verifications.csv`.

Recorded closeout validation:

- `20 passed in 0.04s` across focused runner-characteristics and manual-verification tests;
- independent source validation passed across 1,851,285 runner rows;
- 8 sex values governed, including 2 exact corrections;
- 1,122,490 blank and 728,795 populated headgear rows reconciled;
- 5,932 trailing-`1` rows confirmed, first observed on 15 October 2025;
- manual-verification validation passed across 33 governed rows;
- notebook and verification evidence committed at `699375d`.

The complete repository suite remains deferred until the end of the source-field series or repair branch.

## Remaining source-field studies

The provisional sequence is now:

1. ratings semantics and availability;
2. horse and pedigree identity;
3. connections and owner identity;
4. comments and embedded information.

These are planning units rather than a commitment to one full-length notebook per group. Adjacent subjects may be combined where one bounded study resolves them cleanly.

## Current next action

### Begin ratings semantics and availability

Bound the next study around runner `or`, `rpr` and `ts`. Profile storage, blank and dash behaviour, temporal and jurisdiction coverage, cross-rating relationships, impossible or sentinel values, and which ratings can be compared safely without inventing official scale equivalence.

Do not run the complete repository suite yet.

## Phase 3 — Entity and key design

Permanent entity and key design remains deferred until the source-field studies required for structural reconstruction are completed or explicitly deferred.

Questions still to resolve include descriptive-field stability across replacement snapshots, entity resolution for horses and participants, amended-record versioning, coupled-entry representation, staging surrogate identifiers and reconciliation controls.

## Phase 4 — Target architecture

Only after the evidence base is sufficient:

- consolidate reconstruction requirements;
- define a conceptual staging model;
- select the physical database technology;
- define staging, core and analytical schemas;
- create tables, constraints and indexes;
- implement repeatable ingestion;
- preserve raw source values and technical lineage;
- add automated reconciliation and integrity tests.

## Phase 5 — Analytical products and writing

Potential outputs after the database is validated include research views, form-history datasets, trainer/jockey/course/horse summaries, reproducible feature datasets, claim-testing investigations and reader-facing stories about hidden data assumptions.

Predictive work remains downstream of reliable source interpretation and database design.
