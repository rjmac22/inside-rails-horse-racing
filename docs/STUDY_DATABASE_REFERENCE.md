# Inside Rails Study Database Reference

## Purpose

This is the canonical database reference for reader-facing Inside Rails studies.

Read it before beginning every study, alongside:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Its purpose is to stop study notebooks from rediscovering or guessing database names, paths, release state, table grain, identifiers, source-admission rules or safe analytical interfaces.

When the accepted release, schema or study-facing structures change, this document must change with them.

---

## 1. Immutable third-party Source Version 1

Original filename:

`raceform.db`

Canonical local path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Role:

- immutable third-party source evidence;
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

### Database v4 — current study database

Accepted and promoted on **12 August 2026**.

Canonical release path:

`data/processed/database/releases/inside_rails_v4.sqlite3`

Accepted release SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

Release size:

`3,137,249,280 bytes`

SQLite identity:

- `application_id`: **1230130259**;
- `user_version`: **4**;
- manifest status: **`release_accepted`**;
- validation-result rows: **7**;
- `PRAGMA quick_check`: **`ok`**;
- `PRAGMA foreign_key_check`: **0 rows**.

Promotion implementation commit:

`27b8ac8aba3b22809c4da4f603b2302e47e9fa6d`

Reader-facing studies must use Database v4 read-only by default.

There is no silent fallback to Database v3, Database v2, Database v1, the v4 candidate or Source Version 1 if Database v4 is missing.

### Preserved Database v4 candidate

Path:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

SHA-256:

`04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`

Manifest status:

`built`

The candidate is immutable pre-release evidence. Normal studies must not use it as the analytical database.

### Retained earlier releases

Database v3:

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
user_version: 3
```

Database v2:

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
user_version: 2
```

Database v1:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
user_version: 1
```

They remain immutable historical release/rollback evidence, not the normal study database.

---

## 3. Database v4 acceptance boundary

Database v4 was accepted only after the final promotion-code state passed:

```text
focused v4/release tests: 13 passed in 1.11s
complete repository suite: 435 passed in 15.47s
applicable independent-validator gate: 32 validators passed
final standalone Database v4 validator: passed
```

The final standalone validator reconfirmed the exact v4 candidate immediately before promotion, including:

- candidate SHA-256 `04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`;
- 1,851,286 raw records compared against accepted v3;
- 189,043 structural race rows compared;
- 1,851,285 structural runner rows compared;
- 395 `reference_course` rows compared;
- `quick_check=ok`;
- zero foreign-key errors.

Promotion then independently validated staging and the published release, proved the candidate hash remained unchanged, and proved accepted v3 remained unchanged.

Published v4 SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

Full release record:

`docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md`

---

## 4. Current consumer contract

The study-facing consumer contract is the exact immutable Database v4 release path documented above.

Do not invent or infer an `active_database.json` file, symbolic link or mutable `inside_rails.db` alias. Until an active-release resolver is deliberately implemented and documented, studies take the accepted release path from this file.

Normal accepted-release connections must be read-only and should enforce:

```text
PRAGMA query_only = ON;
PRAGMA foreign_keys = ON;
PRAGMA trusted_schema = OFF;
```

---

## 5. What Database v4 contains

Database v4 is a bounded successor to Database v3.

It preserves the full v3 source/core/governed/external-reconciliation layer and adds the corrected completed Great Britain Study 03 racecourse/course identity layer.

### Carried Database v3 reconciliation layer

Important current baselines remain:

- manual-verification rows: **104**;
- typed external-value resolutions: **37**;
- source race occurrences: **189,043**;
- source-backed runner rows: **1,851,285**;
- combined governed runner rows: **1,851,288**.

The typed resolution kinds remain:

- `correction`;
- `enrichment`;
- `invalidation`.

Raw Source Version 1 values remain visible alongside governed/reconciled analytical values.

### New Database v4 Study 03 layer

Current national Study 03 baseline:

- racecourse evidence notebooks: **61**;
- Great Britain source-label mappings: **65**;
- governed racecourse identities: **61**;
- course/track inventory rows: **90**;
- stable course/track identities: **86**;
- unresolved governance rows: **7**.

The corrected Newmarket identities are separate racecourses:

- `Newmarket` → `Newmarket — Rowley Mile`;
- `Newmarket (July)` → `Newmarket — July Course`.

There is no synthetic combined Newmarket analytical racecourse identity in v4.

The Study 03 modelling rule is:

> `racecourse -> course/track -> time-bounded characteristics`

A British racecourse is a venue and is not necessarily a single racing course.

Database v4 deliberately does **not** assign every race occurrence to one physical course/track. Source Version 1 often does not identify which peer track, route, configuration, rail position or temporary layout was used, so v4 stops at the governed racecourse identity where the evidence stops.

---

## 6. Recommended study-facing views

### `view_reconciled_race_occurrences`

Grain:

> one reconciled Source Version 1 race occurrence.

Expected rows:

**189,043**

Use this as the normal general race-level analytical interface when racecourse identity is not required.

It carries governed runner counts, distance/age-band corrections and enrichments, actual-off enrichments and the rest of the accepted v3 reconciliation layer.

### `view_gb_reconciled_race_occurrences_with_racecourse`

Grain:

> one reconciled Great Britain race occurrence with governed racecourse identity.

Expected rows:

**111,634**

Distinct race IDs:

**111,634**

This is the Study 04-facing race-level interface.

It adds:

- `racecourse_identity_id`;
- `racecourse_identity_code`;
- `governed_racecourse_name`;
- `racecourse_identity_kind`;
- `study03_grouping_name`;
- `racecourse_resolution_method`;
- `racecourse_resolution_evidence`.

It must not be interpreted as assigning a physical course/track below racecourse level.

### `view_gb_racecourse_identity_reference`

Grain:

> one Great Britain Source Version 1 course label mapped to one governed racecourse identity.

Expected rows:

**65**

Use this when the source-label-to-racecourse bridge itself is material.

### `view_gb_course_track_identities`

Grain:

> one stable Study 03 course/track identity.

Expected rows:

**86**

Use this to describe the constituent course/track reference layer, not to infer which track a race used.

### `view_reconciled_source_runner_participations`

Grain:

> one reconciled source-backed runner participation.

Expected rows:

**1,851,285**

Use when the analysis must remain exactly on the admitted physical source-runner population while applying governed corrections/enrichments/invalidations.

### `view_reconciled_runner_records`

Grain:

> one reconciled governed runner record, including approved externally supplemented missing runners.

Expected rows:

**1,851,288**

This contains all **1,851,285** source-backed runners plus **3** externally supplemented missing runners.

### Carried governed identity views

Use `view_governed_horse_occurrence_assignments` when Notebook 19 provisional horse/pedigree identity is material.

Current baseline:

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

Rows:

**1,851,286**

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

Prefer project-owned textual codes such as:

- source version: `sv:...`;
- source record: `rec:...`;
- source race occurrence: `race:...`;
- runner participation: `run:...`;
- racecourse identity: `rc:gb:...`;
- stable course/track identity: `trk:gb:...`.

Internal integer primary keys are release-local implementation identifiers, not durable external references.

---

## 8. Important governed semantics carried into v4

Database v4 preserves Database v3's central rule:

> Raw source assertions remain immutable. When external evidence establishes an exact fact, the study-facing database exposes that fact as usable analytical data with provenance. When external evidence proves a raw analytical value wrong but does not establish a defensible replacement, the raw value remains visible but the analytical value is not silently left usable as if correct.

Examples carried into v4 include:

- Almendares raw `sp='F'` with reconciled analytical SP **5/2 favourite**;
- Cinnamon Carter raw finish `10` with reconciled finish position **12**;
- official **1600m** enrichments for the verified Sha Tin and Kyoto cases;
- exact externally verified runner-count corrections for Ohi, Morioka and Gulfstream Park;
- governed beaten-distance correction/invalidation cases;
- Compiegne `5yo+` and Ecstasy age `3`;
- three actual-off-time enrichments;
- Pegasus 2018 and Arc 2019 official/local-currency prize enrichments.

Database v2 integrations also remain in force, including:

- explicit `(AW)` evidence supports only `all_weather_unspecified` under the source-only surface rule;
- literal source-distance parsing remains distinct from official distance enrichment;
- exact Notebook 17 `B` / `BB` sex corrections;
- exact raw `rpr = 775` anomaly treated as analytically invalid without inventing a replacement;
- **28** blank connection labels externally supplemented and **18** preserved unresolved;
- conservative comment classification;
- provisional participant and horse identities where governance remains provisional.

Raw values remain recoverable. Reconciled values must not be described as if the source itself contained them.

---

## 9. Race-time boundary

Database v4 carries the accepted advertised/scheduled start-time governance and the distinct actual-off enrichments.

Advertised/scheduled rows:

**189,043**

Current advertised/scheduled status:

- resolved: **169,465**;
- unresolved: **19,578**;
- pre-format-boundary races: **178,691**;
- explicit post-boundary races: **10,352**.

Boundary date:

`2025-10-15`

Advertised/scheduled values and externally reported actual-off observations are different concepts and must not be conflated.

---

## 10. Runner-count population choice

A study must state which population is being measured.

Distinct concepts include:

1. admitted physical source runner rows;
2. raw/source-reported `ran`;
3. reconciled externally verified runner count where available;
4. governed source-runner coverage state;
5. the combined reconciled runner view including three verified external supplementations.

Do not silently substitute one for another.

For a race-level field-size question intended to use the best currently governed evidence, prefer `view_reconciled_race_occurrences` and its reconciled runner-count field rather than raw `ran` alone.

For a runner-level question intended to include all currently governed runner evidence, consider `view_reconciled_runner_records` and state that the three supplementation rows are included.

---

## 11. Pending post-release overlay

Database v4 does not automatically integrate every governed resolution created after Database v3.

The historical pending registers remain:

- `data/reference/post_v3_external_verification_candidates.csv`;
- `data/reference/post_v3_external_value_resolutions.csv`.

Their filenames reflect when the register was created, not the current accepted release number.

Before applying a pending resolution, check whether the specific fact is already native to Database v4. Apply the read-only overlay only where the accepted release does not yet contain that governed resolution.

Reusable helper:

```python
from inside_rails.study_overlay import build_race_overlay_query
```

Do not knowingly analyse a value already established as wrong merely because the accepted release is immutable.

---

## 12. Efficient analytical use

Do not load all 1.85 million runner rows into pandas unless the question genuinely requires it.

Preferred workflow:

1. filter in SQLite;
2. aggregate in SQLite where practical;
3. load the smaller result into pandas;
4. use pandas for presentation, modelling or charts.

Start exploration with explicit columns and `LIMIT`, not `SELECT *` over the full runner view.

---

## 13. Study-start checklist

Before the first analytical cell of every study, confirm:

1. this document has been read;
2. `docs/STUDY_DATA_ACCESS.md` has been read;
3. the current accepted database is Database v4;
4. the exact path is `data/processed/database/releases/inside_rails_v4.sqlite3`;
5. the database is opened read-only;
6. the study's unit of observation is declared;
7. the relevant reconciled/governed view and population are declared;
8. every required field/identity has sufficient governance for the proposed use;
9. unresolved states, invalidations and supplementations relevant to the question are understood;
10. the pending post-release resolution register has been checked where material;
11. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work;
12. any newly discovered database defect or reusable transformation is escalated rather than quietly buried inside the study notebook.

For Study 04 specifically, start from `view_gb_reconciled_race_occurrences_with_racecourse`; do **not** assume `date + racecourse = meeting/fixture` until Study 04 establishes the sporting concept and its analytical representation.

---

## 14. Update rule

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