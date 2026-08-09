# Inside Rails Study Database Reference

## Purpose

This is the canonical database reference for reader-facing Inside Rails studies.

Read this document before beginning every study, alongside:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Its purpose is to stop study notebooks from rediscovering or guessing database names, paths, release state, table grain, identifiers, source-admission rules or safe analytical interfaces.

When the database schema, release status, canonical paths or study-facing analytical structures change, update this document as part of that database work.

---

## 1. Immutable third-party Source Version 1

Original filename:

`raceform.db`

Canonical local path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Role:

- immutable third-party source evidence;
- never an Inside Rails database name;
- opened read-only;
- never renamed or modified because its original identity is part of lineage.

Source Version 1 admission rule:

`rowid <> 1`

Governed source population:

- physical source records: **1,851,286**;
- admitted runner-bearing records: **1,851,285**;
- retained excluded physical records: **1**;
- source race occurrences: **189,043**;
- source columns: **37**;
- minimum source date: `2015-01-01`;
- maximum source date: `2026-05-27`.

Authorised Source Version 1 race identity:

`exact raw date + course + off`

Source Version 1 SHA-256:

`77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7`

---

## 2. Current accepted Inside Rails database

### Database v3 — current study database

Accepted and promoted on **9 August 2026**.

Canonical release path:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Accepted release SHA-256:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Release size:

`3,137,081,344 bytes`

SQLite identity:

- `application_id`: **1230130259**;
- `user_version`: **3**;
- manifest status: **`release_accepted`**;
- validation-result rows: **7**;
- `PRAGMA quick_check`: **`ok`**;
- `PRAGMA foreign_key_check`: **0 rows**.

Promotion verification:

- all **1,851,286** raw-record rows were compared back to accepted Database v2;
- **189,043** structural race rows were compared back to Database v2;
- **1,851,285** structural source-runner rows were compared back to Database v2;
- candidate hash remained unchanged during promotion;
- accepted Database v2 remained unchanged and available for rollback.

Promotion implementation commit:

`0b535cb5bfdcb22b7693e8a26a82acfcb025529d`

Reader-facing studies should use Database v3 read-only by default.

There is no silent fallback to Database v2, Database v1, the validated candidate or the raw third-party source if Database v3 is missing.

### Preserved validated Database v3 candidate

Path:

`data/processed/database/candidates/inside_rails_v3_candidate.sqlite3`

SHA-256:

`0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b`

Manifest status:

`validated`

The candidate is immutable pre-release evidence. Normal studies must not use it as the analytical database.

### Retained Database v2 release

Path:

`data/processed/database/releases/inside_rails_v2.sqlite3`

SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Database v2 remains retained as the prior accepted release and rollback material. It is no longer the default study database.

### Retained Database v1 release

Path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v1 remains historical accepted-release evidence and is not the default study database.

---

## 3. Release evidence boundary

Database v3 was accepted only after:

- the exact Database v3 candidate had been built from a verified copy of accepted Database v2;
- standalone independent v3 candidate validation passed;
- focused promotion-boundary tests passed;
- the complete repository suite passed at the final promotion implementation head: **412 passed in 18.64s**;
- the canonical applicable independent-validator sweep passed: **31 validators**;
- the standalone Database v3 validator was rerun immediately before promotion;
- the release staging copy was independently validated again after acceptance evidence was written;
- promotion proved the candidate hash was unchanged and Database v2 was preserved.

The accepted database contains seven required import-validation records and must now be treated as immutable.

The permanent applicable-validator procedure is documented in `docs/APPLICABLE_VALIDATOR_GATE.md` and executed by `scripts/run_applicable_validators.py`.

---

## 4. Current consumer contract

The current study-facing consumer contract is the exact immutable Database v3 release path documented above.

Do not invent or infer an `active_database.json` file, symbolic link or mutable `inside_rails.db` alias. Until an active-release resolver is deliberately implemented and documented, studies must take the accepted release path from this file rather than reconstructing it from memory.

Normal accepted-release connections must be read-only and should enforce:

```text
PRAGMA query_only = ON;
PRAGMA foreign_keys = ON;
PRAGMA trusted_schema = OFF;
```

---

## 5. Database v3 physical model

Database v3 is a bounded successor to Database v2. It preserves the complete Database v2 source/core/governed model and adds one typed external-verification reconciliation table.

Database v3 contains **32 physical tables**:

- **31** carried through from Database v2;
- **1** new Database v3 reconciliation table.

New Database v3 table:

- `governance_external_value_resolution`

Current reconciliation evidence populations:

- manual-verification rows: **104**;
- typed external-value resolutions: **37**.

The typed resolution kinds are:

- `correction`;
- `enrichment`;
- `invalidation`.

Raw Source Version 1 values and Database v2 governed values remain retained alongside the new reconciled analytical values.

---

## 6. Recommended study-facing views

For normal analytical work prefer the Database v3 reconciled views rather than rebuilding external-correction joins in every notebook.

### `view_reconciled_race_occurrences`

Grain:

> one reconciled Source Version 1 race occurrence.

Expected rows:

**189,043**

Use this as the normal race-level analytical interface.

It carries the Database v2 governed race semantics and additionally exposes externally reconciled race-level facts where established, including:

- corrected governed runner count where exact external evidence exists;
- externally verified official metric distance where available, without overwriting the literal source-distance parse;
- exact corrected age-band condition where established;
- externally reported actual-off text where available, kept distinct from advertised/scheduled time.

### `view_reconciled_source_runner_participations`

Grain:

> one reconciled source-backed runner participation.

Expected rows:

**1,851,285**

Use when the analysis must remain exactly on the admitted physical source-runner population while applying governed v2 semantics plus typed Database v3 external corrections, enrichments and invalidations.

Important v3 behaviour includes:

- corrected finishing position where externally established;
- corrected starting-price numerator/denominator, decimal odds, implied probability and favourite status where externally established;
- known-wrong beaten-distance numeric values becoming analytical null where no defensible numeric replacement exists;
- externally established text-only distance relation retained without inventing a numeric conversion;
- corrected runner age where externally established;
- externally established official local prize amount/currency as a distinct enrichment where available.

Raw source fields remain visible for lineage.

### `view_reconciled_runner_records`

Grain:

> one reconciled governed runner record, including approved externally supplemented missing runners.

Expected rows:

**1,851,288**

This is the normal combined runner view when the study question should include the three verified missing-runner supplementations.

It contains:

- all **1,851,285** source-backed runners; plus
- **3** externally supplemented missing runners.

The supplemented rows do not acquire fabricated source-record IDs or unsupported attributes.

### Carried Database v2 governed views

Database v3 still contains the Database v2 governed views for lineage, comparison and specialised use, including:

- `view_governed_race_occurrences`;
- `view_governed_source_runner_participations`;
- `view_governed_runner_records`;
- `view_governed_horse_occurrence_assignments`;
- `view_governed_participant_label_identities`.

For new general studies, prefer the `view_reconciled_*` interfaces so exact externally resolved facts are not accidentally ignored.

Use `view_governed_horse_occurrence_assignments` when Notebook 19 provisional horse/pedigree occurrence identity is material to the question.

Current governed identity baseline:

- provisional horse occurrences: **611**;
- transition decisions: **353**;
- corrected transitions: **92**;
- different-horse transitions: **261**;
- unresolved transitions: **0**.

Use `view_governed_participant_label_identities` when accepted Notebook 22 jockey/trainer/owner label mappings are material.

Current baseline:

- source labels: **116,859**;
- accepted provisional participant identities: **68**;
- accepted label mappings: **149**;
- participant candidates: **1,205**.

Do not convert unresolved candidates into identities in a study.

---

## 7. Structural grains and identifiers

### `source_raceform_v1_record`

Grain:

> one physical Source Version 1 record exactly as retained in the Inside Rails raw mirror.

Contains all **1,851,286** physical records, including the retained excluded row.

### `core_source_race_occurrence`

Grain:

> one admitted Source Version 1 race occurrence reconstructed from exact raw `date + course + off`.

Rows:

**189,043**

### `core_runner_participation`

Grain:

> one admitted physical source runner linked to one structural race occurrence.

Rows:

**1,851,285**

Do not use raw `race_id` as a unique Inside Rails race identifier.

Prefer stable project-owned textual codes such as:

- source version: `sv:...`;
- source record: `rec:...`;
- source race occurrence: `race:...`;
- runner participation: `run:...`.

Internal integer primary keys are release-local implementation identifiers, not durable external references.

---

## 8. Important governed semantics now integrated

Database v3 carries Database v2 Notebook 04–22 governance and reconciles the externally established facts found during the retrospective evidence audit.

The governing rule is:

> Raw source assertions remain immutable. When external evidence establishes an exact fact, the study-facing database exposes that fact as usable analytical data with provenance. When external evidence proves a raw analytical value wrong but does not establish a defensible replacement, the raw value remains visible but the study-facing analytical value is not silently left usable as if correct.

Important examples include:

- Almendares (GB), Del Mar 20 July 2025: raw `sp='F'`; reconciled analytical SP **5/2 favourite**;
- Cinnamon Carter (AUS), Morphettville 16 May 2015: raw position `10`; reconciled finish position **12**, with dead-heat context;
- Sha Tin 25 January 2015 and Kyoto 4 January 2015: raw distance `1m`; external official distance **1600m** exposed separately;
- Ohi 26 June 2024: raw `ran=5`; reconciled externally verified runner count **13**;
- Morioka 3 September 2024: raw `ran=5`; reconciled externally verified runner count **12**;
- Gulfstream Park 23 December 2023: raw `ran=8`; reconciled externally verified runner count **9**;
- Gavea 6 April 2025 position-2 runner: externally established beaten distances **16.5** lengths;
- Nardo, Red Fog and Cabernet Franc: known-wrong zero beaten-distance values are not left analytically usable; unresolved numeric replacements remain null where evidence does not establish one;
- Compiegne 16 May 2017: raw age band `5yo`; reconciled condition **5yo+**;
- Ecstasy (USA), Woodbine 27 July 2024: raw age `31`; reconciled age **3**;
- three externally reported actual-off observations are exposed as enrichments, distinct from advertised/scheduled time;
- externally checked Pegasus 2018 USD and Arc 2019 EUR prize schedules are exposed as distinct official/local-currency enrichment rather than overwriting source-presented prize values.

Database v2 integrations remain in force, including:

- explicit `(AW)` evidence supports only `all_weather_unspecified`; other surface values remain unresolved under that source-only rule;
- literal source-distance parsing remains distinct from official distance enrichment;
- exact Notebook 17 `B` / `BB` sex anomalies have bounded accepted corrections;
- exact raw `rpr = 775` anomaly is analytically null as `invalid_source_value`, with no replacement rating;
- **28** blank connection labels have verified external supplementations and **18** remain unresolved;
- comment values are conservatively classified rather than narratively parsed;
- participant and horse identities remain provisional where governance says they are provisional.

Raw source values remain recoverable. Reconciled study-facing values must not be described as if the source itself contained them.

---

## 9. Race-time boundary

Database v3 carries Notebook 11 advertised/scheduled start-time governance from Database v2 and adds separately typed actual-off enrichment for three externally observed cases.

Advertised/scheduled rows:

**189,043**

Current advertised/scheduled status:

- resolved: **169,465**;
- unresolved: **19,578**;
- pre-format-boundary races: **178,691**;
- explicit post-boundary races: **10,352**.

Methods:

- `course_local_dead_of_night_rejection`: **111,871**;
- `stable_post_boundary_course_profile`: **47,242**;
- `explicit_post_boundary_time`: **10,352**;
- `unresolved`: **19,578**.

Boundary date:

`2025-10-15`

Advertised/scheduled values and externally reported actual-off observations are different concepts and must not be conflated.

---

## 10. Runner-count population choice

Study 01 and later field-size work must state which population is being measured.

Possible concepts are deliberately distinct:

1. admitted physical source runner rows;
2. raw/source-reported `ran`;
3. reconciled externally verified runner count where available;
4. governed source-runner coverage state;
5. the combined reconciled runner view including three verified external supplementations.

Do not silently substitute one for another.

For a race-level field-size question intended to use the best currently governed evidence, prefer `view_reconciled_race_occurrences` and its reconciled runner-count field rather than raw `ran` alone.

For a question about what the accepted physical source contains, use the source-backed population and state that choice explicitly.

For a runner-level question intended to include all currently governed runner evidence, consider `view_reconciled_runner_records` and state that the three supplementation rows are included.

---

## 11. Efficient analytical use

Do not load all 1.85 million runner rows into pandas unless the question genuinely requires it.

Preferred workflow:

1. filter in SQLite;
2. aggregate in SQLite where practical;
3. load the smaller result into pandas;
4. use pandas for presentation, modelling or charts.

Start exploration with explicit columns and `LIMIT`, not `SELECT *` over the full runner view.

---

## 12. Study-start checklist

Before the first analytical cell of every study, confirm:

1. this document has been read;
2. `docs/STUDY_DATA_ACCESS.md` has been read;
3. the current accepted database is Database v3;
4. the exact path is `data/processed/database/releases/inside_rails_v3.sqlite3`;
5. the database is opened read-only;
6. the study's unit of observation is declared;
7. the relevant reconciled/governed view and population are declared;
8. every required field has sufficient governance for the proposed use;
9. unresolved states, invalidations and supplementations relevant to the question are understood;
10. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work;
11. any newly discovered database defect or reusable transformation is escalated rather than quietly buried inside the study notebook.

---

## 13. Update rule

Update this document whenever any of the following changes:

- canonical source path;
- candidate or accepted database filename/path;
- release status or release hash;
- database schema version;
- study-facing table/view inventory;
- table grain;
- stable identifier rules;
- analytical access conventions;
- field-governance consequences that materially change study queries.

A database change is not fully integrated into the study workflow until this reference reflects it.
