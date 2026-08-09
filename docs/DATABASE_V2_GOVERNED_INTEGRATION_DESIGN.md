# Database v2 Governed Integration Design

## Status

**Canonical Database v2 design, implementation and accepted-release specification.**

This document supersedes Notebook 25 as the working authority for Database v2. Notebook 25 may remain as an archival construction/scratch record, but Database v2 design and release decisions belong here.

Database v2 is a bounded integration release. It carries forward the accepted Database v1 structural core and integrates only the governed semantic, correction, supplementation, reference and provisional-identity work established by Notebooks 04–22.

Database v2 was successfully built, independently validated, release-accepted and promoted on **9 August 2026**.

Accepted release:

`data/processed/database/releases/inside_rails_v2.sqlite3`

Accepted release SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Release size:

`3,137,044,480 bytes`

Accepted SQLite identity:

- `application_id`: **1230130259**;
- `user_version`: **2**;
- manifest status: **`release_accepted`**;
- validation-result rows: **7**;
- `PRAGMA quick_check`: **`ok`**;
- foreign-key-check rows: **0**.

The exact validated candidate remains preserved unchanged:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

Candidate SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

The accepted Database v1 release also remains unchanged and available for rollback:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Database v1 SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

---

## 1. Governing rule

The general Database v2 rule is:

> **Raw assertions are immutable; defensible corrections are permitted and should be analytically usable when explicitly authorised, but every correction must remain transparent and traceable.**

A `source_correction_candidate` is not automatically an accepted correction.

Database v2 remains subordinate to:

- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- the Notebook 04–22 integration contracts;
- their durable reusable modules, references and validators.

Where an older notebook closeout conflicts with a later durable governed reference, reusable implementation or source-wide validator baseline, the later durable governance is authoritative.

---

## 2. Immutable Source Version 1

Source Version 1 is third-party source evidence, not the Inside Rails database.

Canonical path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Identity:

- physical source rows: **1,851,286**;
- admitted rows under `rowid <> 1`: **1,851,285**;
- race occurrences: **189,043**;
- physical fields: **37**;
- authorised race grouping: exact raw `date + course + off`;
- SHA-256: `77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7`.

The source is always read-only.

---

## 3. Database v1 base-release contract

Database v2 begins from an exact copy of accepted Database v1 rather than rebuilding the structural core from scratch.

Accepted Database v1:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v1 remains immutable. Database v2 promotion proved that v1 remained preserved.

Carried-forward v1 structural rows retain v1 structural-governance lineage. Database v2 does not rewrite those rows as though they had been created by the v2 semantic release.

---

## 4. Architectural rules

1. Source Version 1 remains immutable.
2. Accepted Database v1 remains immutable and retained for rollback.
3. Database v2 is built as a disposable candidate outside the release directory.
4. Carried-forward v1 structural rows retain v1 governance lineage.
5. New semantic/reference/evidence/identity structures use the Database v2 governance release.
6. Raw runner values are not duplicated unnecessarily in one-to-one governed extensions.
7. Source fields established as race-constant may be promoted to race grain only after source-wide constancy validation.
8. Unresolved states remain explicit; nulls are not eliminated by guessing.
9. Provisional horse and participant identities remain explicitly provisional.
10. No universal EAV correction framework is introduced.
11. Candidate identity relationships never become accepted identities merely because they were generated.
12. No destructive FK cascades are used.
13. Study-facing views may prefer accepted governed values only while raw lineage remains recoverable.
14. No hidden study population filters are permitted.
15. Missing runners verified outside the source remain outside the source-backed core-runner table.

---

## 5. Notebook 04–22 integration dispositions

| Notebook | Subject | Database v2 disposition |
|---|---|---|
| 04 | course jurisdiction/surface | race-level source-supported surface and course/jurisdiction derivation |
| 05 | result | runner-level governed result representation |
| 06 | distance | race-level literal source-distance parse; not independently verified official distance |
| 07 | carried weight | runner-level governed parse |
| 08 | starting price | runner arithmetic/status; lone raw `F` remains unresolved |
| 09 | jurisdiction/context | race jurisdiction plus effective-dated bounded context reference |
| 10 | field governance | versioned source-field treatment metadata |
| 11 | advertised start time | one temporal row per race |
| 12 | course location/timezone | 395-row governed course reference |
| 13 | prize | runner-level recorded-prize semantics |
| 14 | runner counts/numbers | race/runner semantics plus missing-runner supplementation |
| 15 | beaten distance | runner structural semantics plus evidence |
| 16 | classification/eligibility | race-level structural interpretations; no normalised going field |
| 17 | age/sex/headgear | runner extension plus two exact accepted sex corrections |
| 18 | ratings | runner OR/RPR/TS states; exact invalid RPR handling |
| 19 | horse/pedigree | specialist governance, transitions, provisional occurrences and assignments |
| 20 | connections | exact source-row/field supplementation/unresolved decisions |
| 21 | comments | conservative state classification; raw text remains atomic |
| 22 | participant identity | role-specific labels, candidates, accepted provisional identities and mappings |

### Notebook 08 clarification

The standalone raw `sp = 'F'` case is not promoted to corrected odds.

Database v2 preserves:

- raw source `F`;
- `starting_price_kind = 'unresolved'`;
- no analytical numerator/denominator;
- no invented correction.

### Going clarification

Database v2 deliberately does **not** introduce a normalised going field. The raw source value remains available, but the field was not promoted into a new governed normalisation merely for convenience.

---

## 6. Physical inventory

Database v2 contains **31 physical tables**:

- **13** carried from Database v1;
- **18** new v2 tables.

### Carried v1 tables

1. `source_provider`
2. `source_product`
3. `source_version`
4. `source_relation`
5. `source_relation_field`
6. `source_raceform_v1_record`
7. `core_source_race_occurrence`
8. `core_runner_participation`
9. `governance_method`
10. `governance_release`
11. `governance_release_evidence`
12. `import_manifest`
13. `import_validation_result`

### New v2 tables

14. `core_source_race_occurrence_governed`
15. `core_source_race_occurrence_time`
16. `core_runner_participation_governed`
17. `reference_course`
18. `reference_jurisdiction_context`
19. `governance_source_field_treatment`
20. `governance_manual_verification`
21. `governance_connection_value_decision`
22. `governance_runner_record_supplementation`
23. `governance_horse_pedigree_specialist_decision`
24. `identity_horse_occurrence`
25. `identity_runner_horse_occurrence`
26. `identity_horse_pedigree_decision`
27. `identity_participant_source_label`
28. `identity_participant`
29. `identity_participant_label_map`
30. `identity_participant_candidate`
31. `identity_participant_candidate_label`

The specialist Notebook 19 table remains separate from transition decisions because the grains are different.

---

## 7. Race-level governed extension

### `core_source_race_occurrence_governed`

Grain:

> exactly one row per structural `core_source_race_occurrence`.

Expected population:

**189,043**

It stores governed race-grain values covering:

- course/jurisdiction derivation;
- required course reference;
- optional bounded jurisdiction-context reference;
- source-supported surface;
- literal source-distance interpretation;
- runner-count / `ran` / coverage semantics;
- race classification and structural interpretations.

Important boundaries:

- explicit `(AW)` supports only `all_weather_unspecified`;
- source-implied distance is not independently verified official distance;
- equality between physical runner rows and `ran` is not external proof of complete published-field coverage;
- no normalised going field is introduced.

---

## 8. Advertised start time

### `core_source_race_occurrence_time`

Grain:

> exactly one temporal row per structural race occurrence.

It attaches directly to `core_source_race_occurrence` rather than depending on the general race-governed extension.

Baseline:

- total: **189,043**;
- pre-boundary: **178,691**;
- explicit post-boundary: **10,352**;
- resolved: **169,465**;
- unresolved: **19,578**.

Methods:

- `course_local_dead_of_night_rejection`: **111,871**;
- `stable_post_boundary_course_profile`: **47,242**;
- `explicit_post_boundary_time`: **10,352**;
- `unresolved`: **19,578**.

Format boundary:

`2025-10-15`

Unresolved pre-boundary races retain both candidate branches and no selected canonical timestamp.

These values represent reconstructed advertised/scheduled start time, not automatically exact actual-off time.

---

## 9. Runner-level governed extension

### `core_runner_participation_governed`

Grain:

> exactly one row per source-backed `core_runner_participation`.

Expected population:

**1,851,285**

It stores governed derivatives/status/provenance for:

- result position/outcome;
- carried weight;
- starting price;
- recorded prize;
- source runner number;
- beaten distance;
- age;
- sex;
- headgear;
- OR/RPR/TS;
- jockey/trainer/owner governed labels;
- comment state.

Raw runner values are not duplicated physically where they remain available through:

`core_runner_participation → source_raceform_v1_record`.

### Accepted exact sex corrections

Notebook 17:

- Par Coeur (GER), Cologne, 2017-10-15 1:35: raw `BB` → governed `gelding`;
- La Venezolana (VEN), Gulfstream Park, 2019-11-29 8:30: raw `B` → governed `filly`.

These are exact-record corrections, not global code rules.

### Invalid RPR handling

Notebook 18:

- source rowid `1619851`, raw `rpr = 775` → governed RPR null with `invalid_source_value`;
- no replacement rating is authorised.

---

## 10. Course and jurisdiction references

### `reference_course`

Governed identity:

`candidate_course_label + candidate_jurisdiction`

Baseline:

- course identities: **395**;
- timezone assignments: **395**;
- distinct IANA timezones: **51**;
- unresolved timezone assignments: **0**.

### `reference_jurisdiction_context`

Grain:

> one jurisdiction + source type + effective period.

Current rows:

**16**

The reference is bounded to researched Great Britain, Ireland and France contexts.

Effective periods for one jurisdiction/type may not overlap. Zero matches means unresearched, not proof that no authority/context exists.

---

## 11. Evidence, corrections and supplementations

### Source-field treatment

`governance_source_field_treatment` contains exactly **37** rows, one per Source Version 1 physical field under the v2 governance release.

### Permanent verification evidence

`governance_manual_verification` contains **85** governed rows.

Permitted actions include:

- `evidence_only`;
- `label_equivalence`;
- `reference_enrichment`;
- `source_supplementation`;
- `source_correction_candidate`;
- `preserve_raw_unresolved`.

A correction candidate does not become an accepted correction without an explicit integration contract.

### Connection decisions

Notebook 20 baseline:

- exact blank field decisions: **46**;
- externally supplemented values: **28**;
- unresolved blanks preserved: **18**.

By field:

- jockey: 2 supplemented, 0 unresolved;
- trainer: 4 supplemented, 5 unresolved;
- owner: 22 supplemented, 13 unresolved.

### Missing-runner supplementations

Exactly **3** verified missing runners are stored outside the source-backed core-runner table:

1. Saucats — Nantes 2024-06-18 2:14, outcome `F`;
2. Tosen Thunder (JPN) — Ohi 2025-10-09 11:07, did not finish;
3. Great Navigator (USA) — Gulfstream Park 2023-12-23 9:36, verified fifth.

They do not receive fabricated source-record IDs or unsupported attributes.

---

## 12. Horse/pedigree identity

### Specialist decisions

`governance_horse_pedigree_specialist_decision` contains **16** bounded Notebook 19 specialist decisions.

### Transition decisions

`identity_horse_pedigree_decision` contains **353** adjacent structured-pedigree transition decisions:

- `Corrected`: **92**;
- `Different horse`: **261**;
- `Unresolved`: **0**.

### Provisional occurrences

`identity_horse_occurrence` contains **611** provisional horse occurrences.

The identity model is deliberately provisional and source-governed. It is not a universal external horse registry.

---

## 13. Participant identity

Notebook 22 remains role-specific.

Current baseline:

- jockey source labels: **7,917**;
- trainer source labels: **10,708**;
- owner source labels: **98,234**;
- total source labels: **116,859**;
- participant candidates: **1,205**;
- accepted provisional identities: **68**;
- accepted label mappings: **149**.

Candidate counts:

- jockey: **216**;
- trainer: **53**;
- owner: **936**.

Unresolved candidate confidence may remain blank where Notebook 22 deliberately deferred assessment. Accepted/confirmed candidate decisions require a nonblank confidence.

No cross-role identity is inferred from identical text.

Notebook 20 supplemental label text does not automatically create a Notebook 22 participant identity.

---

## 14. Study-facing views

Database v2 provides transparent study-facing views:

- `view_governed_race_occurrences`;
- `view_governed_source_runner_participations`;
- `view_governed_runner_records`;
- `view_governed_horse_occurrence_assignments`;
- `view_governed_participant_label_identities`.

Together with the carried v1 evidence/core views, the accepted database exposes **11** documented views.

Normal combined runner view population:

**1,851,288**

This equals:

- **1,851,285** source-backed runners; plus
- **3** verified missing-runner supplementations.

Views must not conceal raw lineage, silently remove unresolved cases or turn provisional identity candidates into accepted identities.

---

## 15. Validation and acceptance evidence

### Candidate build

The complete Database v2 candidate build completed successfully in approximately 23 minutes.

Final validated candidate SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

### Independent candidate validation

The standalone v2 validator passed and verified:

- schema tables: **31**;
- raw-record fingerprints recomputed: **1,851,286**;
- carried structural rows compared: **2,040,328**;
- races: **189,043**;
- source-backed runners: **1,851,285**;
- temporal rows: **189,043**;
- manual verifications: **85**;
- horse occurrences: **611**;
- horse transitions: **353**;
- participant candidates: **1,205**;
- participant identities: **68**;
- participant mappings: **149**;
- `quick_check`: `ok`;
- foreign-key violations: `0`.

### Repository and validator gates

Before promotion:

- focused Database v2 suite: **26 passed**;
- complete applicable validator sweep: **passed**;
- candidate-era complete repository suite: **386 passed**.

After the six promotion tests were added:

- promotion-specific tests: **6 passed in 0.51s**;
- complete repository suite at promotion implementation commit: **392 passed in 16.93s**.

### Promotion

Promotion command:

`python scripts/promote_inside_rails_v2.py`

Promotion implementation commit:

`78087b0ae1985809d63ee2feacd71423ac18c727`

Promotion succeeded and independently revalidated the release copy against Database v1 before publishing it.

Promotion output proved:

- candidate hash unchanged: **true**;
- prior v1 release preserved: **true**;
- raw fingerprints recomputed: **1,851,286**;
- structural rows compared: **2,040,328**;
- release manifest status: **`release_accepted`**;
- release validator manifest status: **`release_accepted`**;
- release `quick_check`: **`ok`**;
- foreign-key-check rows: **0**.

---

## 16. Release lifecycle

Accepted Database v2 is immutable.

The validated candidate remains preserved as pre-release evidence.

Database v1 remains preserved as the prior accepted release and rollback point.

The current study consumer contract is the exact release path documented in `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.

The older architecture ADR describes an `active_database.json` mechanism as an intended lifecycle pattern. That resolver is not currently the implemented study interface and must not be invented ad hoc. If an active-manifest mechanism is implemented later, it requires its own tested integration and documentation update.

---

## 17. Current analytical consequence

Database v2 closes the integration gap that paused Study 01.

Reader-facing studies can now use the governed database directly rather than joining Notebook 04–22 CSVs and ad hoc notebook outputs into Database v1.

Study 01 should therefore resume against accepted Database v2, with explicit choice among:

- source-backed runner population;
- raw source-reported `ran`;
- governed coverage status;
- combined governed runner records including the three verified supplementations.

The evidence should determine which population is appropriate for each specific field-size question.
