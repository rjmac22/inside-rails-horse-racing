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

### Database v2 — current study database

Accepted and promoted on **9 August 2026**.

Canonical release path:

`data/processed/database/releases/inside_rails_v2.sqlite3`

Accepted release SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Release size:

`3,137,044,480 bytes`

SQLite identity:

- `application_id`: **1230130259**;
- `user_version`: **2**;
- manifest status: **`release_accepted`**;
- validation-result rows: **7**;
- `PRAGMA quick_check`: **`ok`**;
- `PRAGMA foreign_key_check`: **0 rows**.

Promotion verification:

- all **1,851,286** raw-record fingerprints were recomputed;
- **2,040,328** carried structural rows were compared back to accepted Database v1;
- candidate hash remained unchanged during promotion;
- Database v1 remained unchanged and available for rollback.

Promotion implementation commit:

`78087b0ae1985809d63ee2feacd71423ac18c727`

Reader-facing studies should use Database v2 read-only by default.

There is no silent fallback to Database v1, the validated candidate or the raw third-party source if Database v2 is missing.

### Preserved validated Database v2 candidate

Path:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

Manifest status:

`validated`

The candidate is immutable pre-release evidence. Normal studies must not use it as the analytical database.

### Retained Database v1 release

Path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v1 remains retained as the prior accepted release and rollback material. It is no longer the default study database.

---

## 3. Release evidence boundary

Database v2 was accepted only after:

- the full Database v2 build completed successfully;
- standalone independent v2 validation passed;
- focused Database v2 tests passed;
- the complete applicable independent-validator sweep passed;
- the repository suite passed at the final promotion implementation commit: **392 passed in 16.93s**;
- the six promotion-specific tests separately passed: **6 passed in 0.51s**;
- the release copy was independently validated again after acceptance evidence was written.

The accepted database contains seven required import-validation records. The embedded `project_acceptance_gate` record preserves the earlier 386-test candidate-era repository gate plus the applicable-validator sweep; the later 392-test run at the promotion commit is the final repository corroboration recorded here and in the release documentation.

The accepted release must now be treated as immutable.

---

## 4. Current consumer contract

The current study-facing consumer contract is the exact immutable Database v2 release path documented above.

Do not invent or infer an `active_database.json` file, symbolic link or mutable `inside_rails.db` alias. The older architecture decision record describes an active-manifest mechanism as an intended lifecycle pattern, but no active-manifest resolver is currently the implemented study interface.

Until that mechanism is deliberately implemented and documented, studies must take the accepted release path from this file rather than reconstructing it from memory.

Normal accepted-release connections must be read-only and should enforce:

```text
PRAGMA query_only = ON;
PRAGMA foreign_keys = ON;
PRAGMA trusted_schema = OFF;
```

---

## 5. Database v2 physical model

Database v2 contains **31 physical tables**:

- **13** carried forward from Database v1;
- **18** Database v2 governed-integration tables.

### Carried structural/source tables

- `source_provider`
- `source_product`
- `source_version`
- `source_relation`
- `source_relation_field`
- `source_raceform_v1_record`
- `core_source_race_occurrence`
- `core_runner_participation`
- `governance_method`
- `governance_release`
- `governance_release_evidence`
- `import_manifest`
- `import_validation_result`

### Database v2 governed tables

- `core_source_race_occurrence_governed`
- `core_source_race_occurrence_time`
- `core_runner_participation_governed`
- `reference_course`
- `reference_jurisdiction_context`
- `governance_source_field_treatment`
- `governance_manual_verification`
- `governance_connection_value_decision`
- `governance_runner_record_supplementation`
- `governance_horse_pedigree_specialist_decision`
- `identity_horse_occurrence`
- `identity_runner_horse_occurrence`
- `identity_horse_pedigree_decision`
- `identity_participant_source_label`
- `identity_participant`
- `identity_participant_label_map`
- `identity_participant_candidate`
- `identity_participant_candidate_label`

---

## 6. Recommended study-facing views

For normal analytical work prefer the documented views rather than rebuilding governance joins in every notebook.

### `view_governed_race_occurrences`

Grain:

> one governed Source Version 1 race occurrence.

Expected rows:

**189,043**

Use for race-level analysis, including course/jurisdiction context, source-supported surface, literal source-distance interpretation, runner-count semantics, race classification and governed advertised-start-time fields.

### `view_governed_source_runner_participations`

Grain:

> one source-backed runner participation.

Expected rows:

**1,851,285**

Use when the analysis must remain exactly on the admitted physical source-runner population while benefiting from governed result, price, weight, prize, rating, characteristic, connection and comment semantics.

### `view_governed_runner_records`

Grain:

> one governed runner record, including approved externally supplemented missing runners.

Expected rows:

**1,851,288**

This is the normal combined runner view when the study question should include the three verified missing-runner supplementations.

It contains:

- all **1,851,285** source-backed runners; plus
- **3** externally supplemented missing runners.

The supplemented rows do not acquire fabricated source-record IDs or unsupported attributes.

### `view_governed_horse_occurrence_assignments`

Use when Notebook 19 provisional horse/pedigree occurrence identity is material to the question.

Current governed identity baseline:

- provisional horse occurrences: **611**;
- transition decisions: **353**;
- corrected transitions: **92**;
- different-horse transitions: **261**;
- unresolved transitions: **0**.

### `view_governed_participant_label_identities`

Use when accepted Notebook 22 jockey/trainer/owner label mappings are material.

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

Database v2 makes Notebook 04–22 governed work directly usable while retaining raw lineage.

Important examples:

- explicit `(AW)` evidence supports only `all_weather_unspecified`; other surface values remain unresolved under that rule;
- distance is a governed parse of the literal source notation, not independently verified official distance;
- the lone raw starting-price value `F` remains unresolved and receives no invented odds;
- exact Notebook 17 `B` / `BB` sex anomalies have bounded accepted corrections;
- exact raw `rpr = 775` anomaly is analytically null as `invalid_source_value`, with no replacement rating;
- **28** blank connection labels have verified external supplementations and **18** remain unresolved;
- comment values are conservatively classified rather than narratively parsed;
- participant and horse identities remain provisional where governance says they are provisional.

Raw source values remain recoverable. Study-facing governed values must not be described as if the source itself contained them.

---

## 9. Race-time boundary

Database v2 integrates Notebook 11 advertised/scheduled start-time governance.

Rows:

**189,043**

Current status:

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

These values represent reconstructed advertised/scheduled start times, not automatically exact actual-off times.

---

## 10. Runner-count population choice

Study 01 and later field-size work must state which population is being measured.

Possible concepts are deliberately distinct:

1. admitted physical source runner rows;
2. source-reported `ran`;
3. governed source-runner coverage state;
4. the combined governed runner view including three verified external supplementations.

Do not silently substitute one for another.

For a question about what the accepted physical source contains, use the source-backed population. For a question intended to use all currently governed runner evidence, consider `view_governed_runner_records` and state that the three supplementation rows are included.

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
3. the current accepted database is Database v2;
4. the exact path is `data/processed/database/releases/inside_rails_v2.sqlite3`;
5. the database is opened read-only;
6. the study's unit of observation is declared;
7. the relevant governed view/table and population are declared;
8. every required field has sufficient governance for the proposed use;
9. unresolved states and supplementations relevant to the question are understood;
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
