# Inside Rails Project Plan

## Objective

Build a documented, reproducible and professionally structured horse-racing analytical database from supplied third-party source products, then use that governed foundation for evidence-led racing studies and reader-facing work.

Profiling and domain interpretation come before cleaning, schema design or predictive modelling. Immutable source evidence is never overwritten merely because a governed correction or enrichment exists.

## Standing method

For each substantive investigation:

1. state one bounded question;
2. declare the source/database and grain under investigation;
3. separate profiling evidence from interpretation;
4. avoid irreversible cleaning decisions inside exploratory work;
5. extract stable reusable plumbing only after it works;
6. add focused tests and independent validation where reusable governed implementation is created;
7. document the database consequence where one exists;
8. preserve uncertainty and unresolved states explicitly;
9. close the study/release with only the documentation needed to prevent future mistakes;
10. commit and verify the completed state.

For reader-facing studies, the mandatory pre-study references are:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Reader-study closure state is tracked in `docs/STUDY_CLOSEOUT_REGISTER.md`. Post-v4 source/correctness investigations are tracked in `docs/POST_V4_SOURCE_INVESTIGATION_REGISTER.md`.

## Immutable Source Version 1

Canonical path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Standing identity:

```text
SHA-256: 77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
physical records: 1,851,286
admitted runner records: 1,851,285
source race occurrences: 189,043
source columns: 37
race identity: exact raw date + course + off
```

Source Version 1 is immutable and read-only. Admission uses `rowid <> 1`.

## Database admission gate

Every staging, core or analytical database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

> No validated output, no database write. No partial success. The last known-good database remains intact.

The canonical independent-validator runner is:

```bash
python scripts/run_applicable_validators.py
```

Do not replace it with ad-hoc shell loops.

## Completed database programme

### Source understanding / field governance / participant identity

**Status: fully closed.**

Notebooks 00–22 established immutable source lineage, race and runner reconstruction, field semantics, governed corrections/supplementations and conservative identity layers.

### Database v1 — minimum structural release

**Accepted 8 August 2026.**

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
user_version: 1
```

### Database v2 — governed Notebook 04–22 integration

**Accepted 9 August 2026.**

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
user_version: 2
```

### Database v3 — external-verification reconciliation

**Accepted 9 August 2026.**

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
user_version: 3
```

Database v3 made externally established corrections/enrichments analytically usable without altering raw evidence.

### Database v4 — Study 03 British racecourse/course identity

**Accepted 12 August 2026; current study database.**

```text
path: data/processed/database/releases/inside_rails_v4.sqlite3
size: 3,137,249,280 bytes
SHA-256: 45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7
manifest status: release_accepted
validation-result rows: 7
application_id: 1230130259
user_version: 4
quick_check: ok
foreign_key_check rows: 0
```

Study 03 reference population:

```text
racecourse notebooks: 61
GB source-label mappings: 65
governed racecourses: 61
course/track inventory rows: 90
stable course/track identities: 86
unresolved governance rows: 7
GB race rows with racecourse identity: 111,634
```

Corrected Newmarket model:

- `Newmarket` → `Newmarket — Rowley Mile`;
- `Newmarket (July)` → `Newmarket — July Course`.

Database v4 deliberately stops short of fabricating race-occurrence → physical-track assignment.

Final v4 release-boundary evidence:

```text
focused tests: 13 passed in 1.11s
complete repository suite: 435 passed in 15.47s
applicable independent validators: 32 passed
standalone v4 validator: passed
promotion repository commit: 27b8ac8aba3b22809c4da4f603b2302e47e9fa6d
candidate hash unchanged: true
prior v3 preserved: true
```

Full release record:

`docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md`

## Reader-facing Great Britain study programme

### Study 01 — governance and structure

**Status: fully closed.**

Notebook:

`studies/jurisdictions/great_britain/01_governance_and_structure.ipynb`

Established the scale/calendar structure of the observed British racing programme while keeping its course-date grouping explicitly analytical rather than treating it as the official definition of a meeting or racecourse.

### Study 02 — types of British racing

**Status: completed before Study 03.**

Notebook:

`studies/jurisdictions/great_britain/02_types_of_british_racing.ipynb`

Established the authoritative Flat/Jump structure before descriptive use of governed broad race-type classifications.

Known verified post-v3 race-type corrections remain available through the governed read-only study overlay where they are not native to the accepted release.

### Study 03 — what is a British racecourse?

**Status: completed and integrated into Database v4.**

National notebook:

`studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`

Evidence base:

- 61 per-racecourse notebooks;
- corrected frozen Study 03 evidence commit `01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b`.

Study 03 established four distinct layers:

1. source-facing course label;
2. governed racecourse identity;
3. stable constituent course/track identity;
4. time-bounded inventory/characteristics.

The key modelling conclusion is:

> `racecourse -> course/track -> time-bounded characteristics`

A British racecourse is a venue and is not necessarily a single racing course.

### Study 04 — what is a race meeting/fixture?

**Status: fully closed.**

Notebook:

`studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`

Closeout:

`docs/studies/GB_04_RACE_MEETINGS_AND_FIXTURES_CLOSEOUT.md`

Study 04 established that fixture and meeting are not reliably the same technical unit.

A BHA fixture is the more precise administrative scheduling object. Meeting is context-dependent and may refer to one fixture/day or to a wider multi-day event.

Database v4 cannot reconstruct persistent BHA fixture identity from completed results alone, so no fixture, meeting or session entity was implemented.

The accepted realised-racing grouping is the explicitly analytical **source racecourse-date group**.

Study 04 also identified BHA fixture/results evidence as a potentially high-value external source for validating Great Britain race-population completeness.

## Post-v4 source/correctness investigation programme

Governing register:

`docs/POST_V4_SOURCE_INVESTIGATION_REGISTER.md`

### Notebook 26 — Great Britain race-population completeness

**Status: fully closed.**

The audit established that Source Version 1 / Database v4 is materially incomplete for Great Britain in 2020. The omission exists in immutable Source Version 1 and is dominated by complete missing fixtures rather than partial race loss within retained fixtures.

The accepted Database v4 remains unchanged; the defect is evidence that future population work needs an official external population rule.

### Notebook 27 — BHA official-source feasibility

**Status: feasibility inventory closed.**

The BHA public estate is sufficiently rich to support official fixture/race/result reconciliation and multiple additional information families, but it is not one homogeneous replacement feed. Source semantics and historical depth must be governed family by family.

### Notebook 28 — BHA historical race-data depth

**Status: fully closed — archival construction record.**

Notebook 28 established a controlled fixture-discovery lower edge around 1995, a sampled fixture-detail/race-list lower-edge split between 1999 and 2000, and populated race/result/runner resources from sampled 2000 races without overclaiming a direct result-endpoint start date.

It also established that fixture-search `resultsAvailable=true` is not a completed-racing predicate.

The source-use contract is now:

`docs/BHA_STRUCTURED_SOURCE_USAGE.md`

Crucially, Notebook 26 had already exposed **race-level** `abandonedReasonCode`, `winnersDetails` and result-group material on individual BHA race objects. The next correctness question is therefore a population-wide validation of that candidate race-level execution evidence, not another fixture-level definition exercise.

## Current study-start rule

Before beginning or resuming a reader-facing study:

1. read `docs/STUDY_RESEARCH_PLAYBOOK.md`;
2. read `docs/STUDY_DATABASE_REFERENCE.md`;
3. read `docs/STUDY_DATA_ACCESS.md`;
4. read `docs/STUDY_REVISIT_REGISTER.md`;
5. use the exact accepted Database v4 release read-only;
6. declare the observation grain and chosen population;
7. use current governed/reconciled interfaces rather than rebuilding known corrections;
8. check the pending post-release overlay where material;
9. escalate correctness-critical database defects out of the study;
10. record the exact database release and repository commit at closeout.

Current accepted study database:

`data/processed/database/releases/inside_rails_v4.sqlite3`

## Release-process improvement for v5+

Database v4 took substantially longer than the domain integration itself because several pieces of release infrastructure had to be repaired or created for the first time.

That work is now reusable. Future database releases should follow the established path rather than reconstructing governance each time:

1. freeze the completed study evidence;
2. implement the smallest governed candidate change;
3. add/update the independent validator;
4. build the disposable candidate;
5. run focused tests;
6. run the complete repository suite once at the final implementation state;
7. run the canonical applicable-validator sweep once;
8. run the new-version standalone validator once at the release boundary;
9. promote through the established fail-closed pattern;
10. perform cheap final hash/readback checks;
11. update the current-release docs.

Avoid repeating expensive validation after documentation-only changes. Promotion infrastructure should be prepared as reusable plumbing rather than rebuilt from scratch for each study.

After roughly three to five fully closed reader-facing studies, review the study-document burden and consolidate overlapping start/closeout guidance if the completed-study evidence supports doing so.

## Next bounded action

Validate the candidate **race-level realised-race predicate**:

> **Does the BHA race-level execution/result state (`abandonedReasonCode` plus official winner/result/runner evidence) provide a complete and stable realised-race predicate across all addressable Great Britain races in 2015-present?**

This is a source-correctness investigation, not a Database v5 design exercise.

Required discipline:

- start at individual race grain;
- include completed and known non-realised/abandoned race cases;
- treat fixture race lists as programme evidence;
- treat fixture status as administrative context;
- do not use fixture-search `resultsAvailable=true` as a completed-racing predicate;
- govern the realised-race rule before designing any population repair.
