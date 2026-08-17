# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible analytical database from third-party racing data, then use that governed foundation for evidence-led racing studies and reader-facing work.

Source evidence remains immutable. Governed corrections, enrichments and identity decisions are layered on top with explicit provenance and validation.

## Immutable Source Version 1

Original source file:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Accepted identity:

```text
SHA-256: 77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
size: 765,825,024 bytes
physical records: 1,851,286
admitted runner records: 1,851,285
retained excluded records: 1
source race occurrences: 189,043
source columns: 37
```

Source Version 1 is always read-only. The admitted source population uses `rowid <> 1`. The authorised Source Version 1 race identity is exact raw `date + course + off`.

## Current accepted analytical database

### Database v4 — accepted 12 August 2026

Canonical study database:

```text
path: data/processed/database/releases/inside_rails_v4.sqlite3
size: 3,137,249,280 bytes
SHA-256: 45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7
manifest status: release_accepted
validation-result rows: 7
quick_check: ok
foreign_key_check rows: 0
SQLite application_id: 1230130259
SQLite user_version: 4
```

Database v4 is the current read-only analytical source for reader-facing studies.

It preserves the complete Database v3 reconciliation layer and adds the corrected completed Great Britain Study 03 racecourse/course identity model.

Study 03 population integrated in v4:

```text
racecourse evidence notebooks: 61
Great Britain source-label mappings: 65
governed racecourses: 61
course/track inventory rows: 90
stable course/track identities: 86
unresolved governance rows: 7
Great Britain race rows: 111,634
```

The corrected Newmarket model contains two separate racecourses:

- `Newmarket — Rowley Mile`;
- `Newmarket — July Course`.

There is no synthetic combined Newmarket racecourse identity in v4.

Database v4 deliberately does not fabricate a physical-track assignment for each race. The Study 03 modelling conclusion is:

> `racecourse -> course/track -> time-bounded characteristics`

A British racecourse is a venue and is not necessarily a single racing course.

### Recommended current study interfaces

General race-level work:

- `view_reconciled_race_occurrences` — 189,043 races.

Great Britain racecourse-aware race work:

- `view_gb_reconciled_race_occurrences_with_racecourse` — 111,634 GB races, one row per race occurrence.

Racecourse/course reference work:

- `view_gb_racecourse_identity_reference` — 65 source-label mappings;
- `view_gb_course_track_identities` — 86 stable course/track identities.

Runner work:

- `view_reconciled_source_runner_participations` — 1,851,285 source-backed runners;
- `view_reconciled_runner_records` — 1,851,288 combined governed runners including three verified supplementations.

Exact usage rules are governed by `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.

## Preserved earlier releases

Database v3:

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
```

Database v2:

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
```

Database v1:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
```

They remain immutable historical release/rollback evidence, not the normal study database.

The exact v4 candidate is also retained as immutable pre-release evidence:

```text
path: data/processed/database/candidates/inside_rails_v4_candidate.sqlite3
SHA-256: 04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e
manifest status: built
```

## Database release programme

- Database v1: minimum structural core, accepted 8 August 2026;
- Database v2: Notebook 04–22 governed integration, accepted 9 August 2026;
- Database v3: external-verification reconciliation, accepted 9 August 2026;
- Database v4: corrected Great Britain Study 03 racecourse/course identity integration, accepted 12 August 2026.

### Final Database v4 acceptance evidence

Promotion implementation commit:

`27b8ac8aba3b22809c4da4f603b2302e47e9fa6d`

Final release-boundary evidence:

```text
focused v4/release tests: 13 passed in 1.11s
complete repository suite: 435 passed in 15.47s
applicable independent validators: 32 passed
standalone Database v4 validator: passed
promotion: release_accepted=true
candidate hash unchanged: true
prior v3 preserved: true
quick_check: ok
foreign_key_check rows: 0
```

Accepted v4 SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

Full release record:

`docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md`

## Completed database/source investigation programme

The source-field investigation series and participant-identity programme are closed. They established source immutability, structural race/runner identity, jurisdiction/surface context, results, distance, weight, starting price, temporal handling, prize money, runner counts, beaten distance, race classification, runner characteristics, ratings, horse/pedigree identity, connection governance, conservative comment handling and participant-label identity.

Database v3 made externally verified corrections/enrichments analytically usable without rewriting raw evidence. Database v4 carries all of that work forward unchanged.

## Great Britain reader-study programme

### Study 01 — governance and structure

**Status: fully closed.**

Notebook:

`studies/jurisdictions/great_britain/01_governance_and_structure.ipynb`

It established the scale/calendar structure of the observed British racing programme and used an explicitly analytical course-date grouping without claiming that grouping was the official definition of a meeting or racecourse.

### Study 02 — types of British racing

**Status: completed before Study 03.**

Notebook:

`studies/jurisdictions/great_britain/02_types_of_british_racing.ipynb`

The study establishes the authoritative Flat/Jump structure before using governed analytical race-type classifications. Known verified post-v3 race-type corrections remain handled through the governed read-only study overlay where they are not yet native to the accepted database.

### Study 03 — what is a British racecourse?

**Status: completed and integrated into Database v4.**

National notebook:

`studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`

Evidence base:

- 61 per-racecourse notebooks under `studies/jurisdictions/great_britain/racecourses/`;
- corrected frozen evidence commit `01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b`.

Study 03 established the distinction between source labels, actual racecourse identity, constituent course/track identity and time-bounded course characteristics. Seven governance questions remain explicitly unresolved rather than guessed.

### Study 04 — what is a race meeting/fixture?

**Status: fully closed.**

Notebook:

`studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`

Closeout:

`docs/studies/GB_04_RACE_MEETINGS_AND_FIXTURES_CLOSEOUT.md`

Study 04 established that a BHA **fixture** is an administrative scheduling object whose venue, date, times and programme may change, while **meeting** is context-dependent and can refer either to one fixture/day or to a wider multi-day event.

Database v4 completed results do not contain enough administrative history to reconstruct persistent BHA fixture identity reliably.

For realised source analysis, use the explicitly descriptive **source racecourse-date group** rather than claiming `date + racecourse` is a verified fixture or meeting.

No fixture, meeting or session entity was added to Database v4.

## Post-v4 source investigations

Status register:

`docs/POST_V4_SOURCE_INVESTIGATION_REGISTER.md`

### Notebook 26 — Great Britain race-population completeness

**Status: fully closed.**

Notebook:

`notebooks/26_gb_race_population_completeness.ipynb`

The audit proved that Source Version 1 / Database v4 is materially incomplete for Great Britain in 2020. The defect is already present in immutable Source Version 1; Database v4 inherited it.

The missing pattern is dominated by **whole missing fixtures**, not races selectively disappearing from otherwise retained fixtures. Database v4 has not been rewritten to hide the defect.

### Notebook 27 — BHA official-source feasibility

**Status: feasibility inventory closed.**

Notebook/report:

- `notebooks/27_bha_official_source_feasibility.ipynb`;
- `reports/notebook_27_bha_official_source_feasibility.md`.

The BHA public estate exposes multiple official source families covering fixture/race/results information, going/weather/watering, officials, participant/ratings histories, Stewards material and statistical publications. It is not treated as one homogeneous replacement feed and no Database v5 adoption decision was made.

### Notebook 28 — BHA historical race-data depth

**Status: fully closed — archival construction record.**

Evidence/report/closeout:

- `notebooks/28_bha_historical_race_data_depth.ipynb`;
- `reports/notebook_28_bha_historical_race_data_depth.md`;
- `docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md`.

Notebook 28 established:

- fixture discovery observed on a controlled 1995 racing date, with a controlled 1994 racing date empty;
- a sampled fixture-detail and fixture-race-list lower-edge split between 1999 and 2000;
- race-detail/result/runner resources demonstrated from sampled 2000 races without claiming a direct pre-2000 endpoint boundary;
- fixture-search `resultsAvailable=true` is not a safe completed-racing predicate.

The correct evidence hierarchy for “did this programmed race go ahead?” is now explicit:

> **race list = programmed race; race-level state/result = candidate realised-race evidence; fixture state = administrative context.**

Notebook 26 had already exposed race-level `abandonedReasonCode`, `winnersDetails` and result-group material on the individual BHA race object. The exact race-level realised-race predicate still requires population-wide validation before it can govern a repair.

Source-use contract:

`docs/BHA_STRUCTURED_SOURCE_USAGE.md`

## Database admission rule

Every database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

> No validated output, no database write. No partial success. The last known-good database remains intact.

The permanent canonical independent-validator runner is:

```bash
python scripts/run_applicable_validators.py
```

Do not reconstruct an ad-hoc shell loop for the validator gate.

## Study database rules

Before every reader-facing study, read:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Normal studies must use accepted Database v4 read-only. There is no silent fallback to an older release, a candidate or Source Version 1.

## Durable project controls

Core current controls:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`;
- `docs/STUDY_CLOSEOUT_REGISTER.md`;
- `docs/POST_V4_SOURCE_INVESTIGATION_REGISTER.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/BHA_STRUCTURED_SOURCE_USAGE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/APPLICABLE_VALIDATOR_GATE.md`;
- `docs/DATABASE_USER_GUIDE.md`;
- `docs/DATABASE_V4_GB_RACECOURSE_IDENTITY_INTEGRATION.md`;
- `docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md`;
- `docs/PROJECT_PLAN.md`.

Historical v1/v2/v3 evidence documents remain historical records and should not be rewritten to pretend they described v4 at the time.

## Release-process lesson

Database v4 required one-off infrastructure work that should not be repeated for every future study: complete pytest discovery was fixed, historical validators were made reproducible, the canonical validator gate was established, and a fail-closed promotion pattern was implemented.

Future database releases should reuse that infrastructure so the normal path is mechanical: freeze evidence, build candidate, validate, run the final test/validator gates once, promote, perform cheap readback checks, update the current-release docs.

## Next bounded action

Validate the **race-level** realised-race candidate before any Database v5 population repair is designed:

> **Does the BHA race-level execution/result state (`abandonedReasonCode` plus official winner/result/runner evidence) provide a complete and stable realised-race predicate across all addressable Great Britain races in 2015-present?**

Use fixture state as administrative context and fixture race lists as programme evidence. Do not use fixture-search `resultsAvailable=true` as the completed-race predicate.

## Working method

The project follows an evidence-led investigation-to-implementation cycle:

1. state one bounded question;
2. profile the relevant governed data without altering immutable evidence;
3. test coverage, uniqueness, exceptions and failure modes;
4. preserve unresolved cases explicitly;
5. separate observation, interpretation, confidence and design decision;
6. implement only correctness-critical reusable findings;
7. retain raw values and lineage;
8. add focused tests/independent validation where warranted;
9. record evidence, limitations and lessons learned;
10. update current project/release state only when it materially changes;
11. commit and verify the closeout.
