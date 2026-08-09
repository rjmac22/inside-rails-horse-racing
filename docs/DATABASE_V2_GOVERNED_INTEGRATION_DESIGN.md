# Database v2 Governed Integration Design

## Status

**Canonical Database v2 design and implementation specification.**

This document supersedes Notebook 25 as the working authority for Database v2 design. Notebook 25 may remain as an archival construction/scratch record, but further Database v2 decisions belong here rather than in Markdown-only notebook cells.

Database v2 is a bounded integration release. It carries forward the accepted Database v1 structural core and adds only the governed semantic, correction, supplementation, reference and provisional-identity structures established by Notebooks 04–22.

The accepted Database v1 remains the last-known-good database until a complete Database v2 candidate passes all required validation and is explicitly promoted. Nothing in this document authorises modifying Database v1 or Source Version 1 in place.

### Current implementation state

The repository now contains an implementation path for:

- Database v1 → Database v2 candidate migration;
- the reconciled 31-table physical schema;
- governed reference/evidence loading;
- race and runner semantic population;
- Notebook 11 temporal population;
- Notebook 19 horse/pedigree identity population;
- Notebook 22 participant identity population;
- transparent study-facing views;
- an independent read-only Database v2 validator;
- an end-to-end candidate-build command.

These new Database v2 files have **not yet been executed against the local full source during this implementation session**. They therefore remain implementation work pending focused local execution and validation. No Database v2 release has been accepted or promoted.

---

## 1. Governing controls

Database v2 remains subordinate to the existing project controls, principally:

- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- the individual Notebook 04–22 integration contracts;
- their durable reusable modules, reference files and independent validators.

Where an older notebook closeout conflicts with a later durable governed reference, reusable implementation or source-wide validator baseline, the later durable governance is authoritative.

The general Database v2 rule is:

> **Raw assertions are immutable; defensible corrections are permitted and should be analytically usable when explicitly authorised, but every correction must remain transparent and traceable.**

A `source_correction_candidate` is not automatically an accepted correction.

---

## 2. Immutable Source Version 1

Source Version 1 is third-party source evidence, not the Inside Rails database.

Current governed source facts:

- path: `data/raw/form_2015-present/form_2015-present/raceform.db`;
- physical source rows: **1,851,286**;
- admitted runner-bearing rows under `rowid <> 1`: **1,851,285**;
- Source Version 1 race occurrences: **189,043**;
- source fields: **37**;
- authorised source-scoped race grouping: exact raw `date + course + off`.

The source is always read-only.

---

## 3. Accepted Database v1

Accepted release:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Current accepted identity:

- size: **1,730,048,000 bytes**;
- SHA-256: `2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`;
- SQLite `application_id`: **1230130259**;
- SQLite `user_version`: **1**;
- validation rows: **7**;
- `quick_check`: `ok`;
- foreign-key violations: **0**.

Database v1 intentionally contains the minimum stable structural core rather than the complete Notebook 04–22 governed semantic programme.

Database v2 therefore begins from an **exact copied candidate of the accepted Database v1 file**. The accepted v1 release itself remains untouched and is hash-checked before and after candidate preparation/validation.

This copy-first strategy preserves the already accepted raw mirror and structural core byte-for-byte at row/value level while allowing the disposable copy to be migrated and extended.

---

## 4. Database v2 architectural rules

1. Source Version 1 remains immutable.
2. Accepted Database v1 remains immutable and retained for rollback.
3. Database v2 is built only as a disposable candidate outside the accepted-release path.
4. Carried-forward v1 structural rows retain their v1 structural governance lineage.
5. The new Database v2 governance release governs the new semantic/reference/evidence/identity structures.
6. Raw runner values are not physically duplicated in the one-to-one governed runner extension; they remain available through the immutable source-record FK.
7. Source fields explicitly established as race-constant may be promoted once to race grain after source-wide constancy validation.
8. Unresolved states remain explicit; nulls are not eliminated by guessing.
9. Provisional horse/participant identities remain explicitly provisional.
10. No universal EAV correction framework is introduced.
11. Candidate identity relationships never become accepted identities merely because they were generated.
12. No destructive FK cascades are used.
13. Study-facing views may prefer accepted governed values only while raw lineage and governance status remain recoverable.
14. No hidden study population filters are permitted.

---

## 5. Notebook 04–22 integration dispositions

| Notebook | Subject | Database v2 disposition |
|---|---|---|
| 04 | course jurisdiction/surface | source-supported surface and course/jurisdiction derivation; final context authority supplied by 09/12 |
| 05 | result | runner extension |
| 06 | distance | race extension; literal source notation only, not independently verified official distance |
| 07 | carried weight | runner extension |
| 08 | starting price | runner arithmetic/status; the one standalone raw `F` remains unresolved |
| 09 | jurisdiction/context | race jurisdiction plus effective-dated context reference |
| 10 | field governance | source-field treatment metadata |
| 11 | advertised start time | dedicated one-row-per-race temporal table |
| 12 | course location/timezone | reusable 395-row course reference |
| 13 | prize | runner-level recorded-prize semantics |
| 14 | runner counts/numbers | race/runner semantics plus missing-runner supplementation |
| 15 | beaten distance | runner semantics plus verification/candidate evidence |
| 16 | classification | race-level raw-preserved structural interpretations |
| 17 | age/sex/headgear | runner extension plus exact accepted sex corrections |
| 18 | ratings | independent nullable OR/RPR/TS states; exact invalid RPR handling |
| 19 | horse/pedigree identity | specialist governance, transition decisions, provisional occurrences and runner assignments |
| 20 | connection blanks | exact jockey/trainer/owner field supplementations/unresolved decisions |
| 21 | comments | conservative comment-state classification only |
| 22 | participant identity | role-specific labels, candidates, accepted provisional identities and mappings |

### Notebook 08 clarification

The historical standalone `sp = 'F'` case must **not** be promoted to an externally corrected Database v2 price.

The durable starting-price integration/backfill authority records it as one unresolved source anomaly. Database v2 therefore preserves:

- raw source `F`;
- `starting_price_kind = 'unresolved'`;
- no analytical numerator/denominator;
- no correction verification FK.

No global standalone-`F` price rule is authorised.

---

## 6. Reconciled physical inventory

Database v2 contains **31 physical tables**:

- **13 carried forward from Database v1**;
- **18 new Database v2 tables**.

### Carried-forward v1 tables

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

The v2 migration rebuilds the **import build-evidence tables** so the Database v2 file has one Database v2 build manifest rather than incorrectly carrying Database v1 build status forward as though it described v2. Database v1's release evidence remains intact in the separately retained accepted v1 file.

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

The 31-table design supersedes the earlier provisional 30-table inventory. The extra table is required because Notebook 19's 16 specialist governance decisions have a different grain from the 353 source-derived transition decisions.

Exact DDL is implemented in:

- `src/inside_rails/database/schema/v002_governed_integration.sql`;
- `src/inside_rails/database/schema/v002_governed_integration_corrections.sql`;
- `src/inside_rails/database/schema/v002_governed_integration_enforcement.sql`;
- `src/inside_rails/database/schema/v002_governed_integration_views.sql`;
- `src/inside_rails/database/schema/v002_governed_integration_view_corrections.sql`.

`src/inside_rails/database/schema.py` applies those resources in order.

---

## 7. Core race extension

### `core_source_race_occurrence_governed`

Grain:

> exactly one row per `core_source_race_occurrence`.

Expected population: **189,043**.

It stores governed race-grain values covering:

- candidate course label/jurisdiction and evidence;
- required `reference_course_id`;
- optional bounded Notebook 09 jurisdiction-context FK;
- Notebook 04 source-supported surface;
- Notebook 06 literal source-distance parsing;
- Notebook 14 `ran`/row-count/coverage semantics;
- Notebook 16 race classification fields and structural interpretations.

Important boundaries:

- explicit `(AW)` course marker supports only `all_weather_unspecified`; other surfaces remain unresolved from this source rule;
- source-implied distance is not independently verified official distance;
- row-count equality with `ran` is not external proof of complete field coverage;
- Notebook 09 context is bounded to researched jurisdictions and periods;
- no new normalised `going` field is introduced in Database v2.

Raw race-level values promoted here are inserted only after every supporting source runner row is proved consistent at race grain.

---

## 8. Race time

### `core_source_race_occurrence_time`

Grain:

> exactly one temporal row per structural race occurrence.

It attaches directly to `core_source_race_occurrence`, independently of the general governed race extension.

Current baseline:

- total: **189,043**;
- pre-boundary: **178,691**;
- explicit post-boundary: **10,352**;
- resolved: **169,465**;
- unresolved: **19,578**.

Decision methods:

- `course_local_dead_of_night_rejection`: **111,871**;
- `stable_post_boundary_course_profile`: **47,242**;
- `explicit_post_boundary_time`: **10,352**;
- `unresolved`: **19,578**.

Boundary: **15 October 2025**.

Unresolved pre-boundary races retain both candidate branches and no selected canonical timestamp.

The stored governed values represent reconstructed **advertised/scheduled start time**, not automatically exact actual-off time.

---

## 9. Core runner extension

### `core_runner_participation_governed`

Grain:

> exactly one row per source-backed `core_runner_participation`.

Expected population: **1,851,285**.

The table stores governed derivatives/status/provenance for:

- result position/outcome;
- carried weight;
- starting price;
- recorded prize;
- source runner number;
- beaten distance;
- runner age;
- runner sex;
- headgear;
- OR/RPR/TS ratings;
- jockey/trainer/owner governed labels;
- comment state.

Raw source runner fields are not duplicated physically. They remain available through:

`core_runner_participation → source_raceform_v1_record`.

### Accepted exact corrections

Notebook 17:

- `BB` → `gelding` only for Par Coeur (GER), Cologne, 2017-10-15 1:35, `NB17-SEX-0002`;
- `B` → `filly` only for La Venezolana (VEN), Gulfstream Park, 2019-11-29 8:30, `NB17-SEX-0003`.

Notebook 18:

- source rowid `1619851`, raw `rpr = 775` → governed RPR null with `invalid_source_value`;
- no replacement value is authorised.

### Prize confidence

Notebook 13's durable parser uses:

- `confirmed`;
- `unresolved`.

Database v2 follows that exact confidence domain. Monetary canonical values use integer minor units only where currency is governed.

### Connection values

Notebook 20 produces exactly:

- **46** blank field decisions;
- **28** externally supplemented labels: 2 jockey, 4 trainer, 22 owner;
- **18** unresolved blanks: 5 trainer, 13 owner.

The raw source field remains blank. The governed label is not a participant identity.

---

## 10. Course and jurisdiction references

### `reference_course`

Governed identity:

`candidate_course_label + candidate_jurisdiction`

Current baseline:

- **395** course identities;
- **395** IANA timezone assignments;
- **51** distinct valid IANA timezone names;
- **0** unresolved timezone assignments.

The source-course label remains raw provenance rather than a permanent production join key.

### `reference_jurisdiction_context`

Grain:

> one jurisdiction + source type + effective period.

Current reference: **16 rows**, bounded to Great Britain, Ireland and France.

Effective periods for one jurisdiction/type may not overlap. More than one context match for a race is a validation failure. Zero means `unresearched`, not “no authority exists”. Current wagering context remains unresolved.

---

## 11. Evidence and supplementation

### `governance_source_field_treatment`

Exactly **37** current rows, one per Source Version 1 physical field under the v2 governance release.

It records authorised treatment, not field values.

### `governance_manual_verification`

Generic bounded evidence table carrying permanent verification code, source locator, question, result, evidence, confidence and authorised database action.

Current permitted actions remain:

- `evidence_only`;
- `label_equivalence`;
- `reference_enrichment`;
- `source_supplementation`;
- `source_correction_candidate`;
- `preserve_raw_unresolved`.

The older `MV-####` convention is not enforced; current governed `NB...` identifiers are preserved.

### `governance_connection_value_decision`

Exactly one operational decision per exact Notebook 20 `(source record, source field)` blank.

The field is relationally linked through `source_relation_field_id`, and schema enforcement restricts it to jockey/trainer/owner and requires compatible permanent verification evidence.

### `governance_runner_record_supplementation`

Exactly **3** current externally verified missing runners:

1. Saucats — Nantes 2024-06-18 2:14, outcome `F`;
2. Tosen Thunder (JPN) — Ohi 2025-10-09 11:07, did not finish;
3. Great Navigator (USA) — Gulfstream Park 2023-12-23 9:36, verified fifth.

They do not receive artificial source-record or core-runner IDs. Unsupported runner attributes remain null.

---

## 12. Horse/pedigree identity

### `governance_horse_pedigree_specialist_decision`

Current population: **16** bounded Notebook 19 specialist decisions.

This is separate from transition decisions because the relational grain is different.

### `identity_horse_pedigree_decision`

Current population: **353** adjacent structured-pedigree transition decisions:

- **92 `Corrected`**;
- **261 `Different horse`**;
- **0 `Unresolved`**.

The schema continues to support future unresolved boundaries.

### `identity_horse_occurrence`

Current population: **611** provisional source-internal horse occurrences.

These are not official registration/life numbers or globally unique horse identities.

### `identity_runner_horse_occurrence`

Maps exact applicable source-backed runner participations to provisional horse occurrences.

Runner assignment is reconstructed from Notebook 19's governed structured pedigree groups and split boundaries, never by raw horse label alone.

### Current Runninsonofagun authority

`Runninsonofagun (IRE)` is now:

- specialist decision `NB19-ID-0013`;
- outcome `Corrected`;
- governed damsire `Society Rock (IRE)`;
- confirmed/high confidence;
- no identity split.

Competing raw source assertions remain unchanged.

---

## 13. Participant identity

### `identity_participant_source_label`

One exact populated raw label per role.

Current counts:

- jockey: **7,917**;
- trainer: **10,708**;
- owner: **98,234**;
- total: **116,859**.

Blank connection fields do not create source-label entities.

### `identity_participant_candidate`

Current candidate populations:

Jockey:

- **216** relationships;
- 1 accepted;
- 1 confirmed distinct;
- 214 unresolved.

Trainer:

- **53** groups;
- 26 accepted;
- 27 unresolved.

Owner:

- **936** groups;
- 41 accepted;
- 895 unresolved.

Total candidates: **1,205**.

Candidate membership is stored relationally in `identity_participant_candidate_label` and never implies accepted identity.

### `identity_participant`

Current accepted provisional identities:

- jockey: **1**;
- trainer: **26**;
- owner composition: **41**;
- total: **68**.

### `identity_participant_label_map`

Current accepted mappings:

- jockey: **2**;
- trainer: **52**;
- owner: **95**;
- total: **149**.

A source label may have at most one accepted current identity mapping in its role.

Marie Velon remains the sole accepted jockey relationship:

`Mlle Marie Velon` + `Mme Marie Velon` → `JOCKEY-PROVISIONAL-0001`.

`Miss B ONeill` and `Mr B ONeill` are confirmed distinct and must not be merged.

Cross-role automatic merging is prohibited. Owner composition identity does not decompose into individual owners.

---

## 14. Study-facing views

Database v2 defines transparent views rather than requiring studies to reconstruct governance joins manually:

- `view_governed_race_occurrences`;
- `view_governed_horse_occurrence_assignments`;
- `view_governed_participant_label_identities`;
- `view_governed_source_runner_participations`;
- `view_governed_runner_records`.

`view_governed_runner_records` is the broad study-facing runner population and unions:

- **1,851,285** source-backed governed runner participations;
- **3** externally supplemented missing runners;

for an expected **1,851,288 records**.

`record_origin` remains explicit so the three externally supplemented records cannot masquerade as immutable source rows.

Unsupported fields on supplemented runners remain null.

---

## 15. Build implementation

### Candidate preparation

`src/inside_rails/database/governed_integration_candidate.py`

Responsibilities:

- verify accepted Database v1 exact size/hash/header/manifest/validation baseline;
- copy v1 to a new candidate path;
- prove copied bytes match v1 before migration;
- migrate the disposable copy to schema version 2;
- create the new v2 governance release while preserving v1 structural governance on carried core rows;
- create a fresh v2 `building` manifest;
- prove accepted v1 did not change during preparation.

### Finite reference/evidence population

`src/inside_rails/database/governed_integration_references.py`

Loads and reconciles:

- 395 course references;
- 16 jurisdiction contexts;
- 37 field treatments;
- permanent manual verifications;
- 46 connection decisions;
- 3 missing runners;
- 16 horse specialist decisions.

### Race/runner population

`src/inside_rails/database/governed_integration_population.py`

Uses bounded race batches so the builder does not require a 1.85-million-row pandas working set on the current 8 GB development machine.

Each batch is fully fetched before writes occur. Partial batches never become accepted because the candidate remains `building` and the outer build deletes a failed candidate.

### Temporal population

`src/inside_rails/database/governed_integration_time.py`

Uses the durable Notebook 11 pipeline and validates exact totals/conversions before persistence.

### Horse identity population

`src/inside_rails/database/governed_integration_horse_identity.py`

Rebuilds Notebook 19 under the populated-value contradiction rule and materialises transitions, occurrences and exact runner assignments.

### Participant identity population

`src/inside_rails/database/governed_integration_participant_identity.py`

Materialises source labels, complete candidate decision populations, candidate memberships, 68 accepted provisional identities and 149 accepted mappings.

### Orchestrator

`src/inside_rails/database/governed_integration_build.py`

Command:

```bash
python scripts/build_inside_rails_v2.py
```

Default candidate:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

The builder does **not** promote a release. A successful build ends in `validated`, not `release_accepted`.

---

## 16. Independent validation

Independent validator:

`src/inside_rails/database/governed_integration_validator.py`

Command:

```bash
python scripts/validate_inside_rails_v2.py
```

The validator opens Database v1 and the v2 candidate read-only and verifies, among other controls:

- candidate schema inventory and schema version;
- SQLite `quick_check` and FK check;
- accepted v1 exact hash/size;
- carried metadata/core preservation;
- all **1,851,286 raw-row fingerprints recomputed** from candidate raw values;
- race/runner/temporal exact populations;
- reference/evidence populations;
- Notebook 20 exact supplementation partition;
- standalone Notebook 08 `F` remains unresolved;
- Notebook 17 exact two sex corrections;
- Notebook 18 exact invalid RPR row;
- Notebook 19 transition/occurrence partition and Runninsonofagun authority result;
- Notebook 22 label/candidate/identity/mapping populations;
- exact Marie Velon mapping and absence of a B ONeill merge;
- candidate and accepted v1 files do not change while validated read-only.

The builder records only checks it actually performs. The independent validator records its own source-wide validation evidence after it returns successfully.

---

## 17. Acceptance baseline

Database v2 acceptance must fail on an unexplained change to the governed baselines.

Key expected populations:

### Source/core

- source physical rows: 1,851,286;
- source-backed runners: 1,851,285;
- races: 189,043;
- source fields: 37.

### Course/time

- course identities: 395;
- jurisdiction contexts: 16;
- temporal rows: 189,043;
- resolved temporal rows: 169,465;
- unresolved temporal rows: 19,578.

### Supplementation

- connection decisions: 46 = 28 supplemented + 18 unresolved;
- missing runners: 3.

### Horse identity

- specialist decisions: 16;
- transitions: 353 = 92 corrected + 261 different horse + 0 unresolved;
- provisional occurrences: 611.

### Participant identity

- source labels: 116,859;
- candidates: 1,205;
- accepted identities: 68;
- accepted label mappings: 149.

Expected baselines must not be changed merely to make a future build pass.

---

## 18. Release lifecycle

A complete Database v2 candidate must progress only through:

`building → built → validated`

during normal candidate construction/independent validation.

Promotion to:

`release_accepted`

is a separate final acceptance action and must occur only after the required project-level acceptance evidence exists.

The acceptance gate must still include the complete final test/validator boundary required by project procedure. The full repository suite/all-validator sweep is intentionally **not** run after each implementation step.

No promotion implementation should be used until the candidate has been executed locally and its evidence reviewed.

---

## 19. Notebook 25 disposition

`notebooks/25_database_v2_governed_integration_inventory.ipynb` is now an archival design-construction record rather than the canonical specification.

It should not be manually maintained in parallel with this document. Doing so would create two competing design authorities and force needless large Markdown edits inside Jupyter.

This document is the canonical Database v2 design record going forward.

---

## 20. Next gate

The next bounded gate is **local focused execution** of the new Database v2 implementation:

1. run focused Database v2 schema tests;
2. correct any syntax/constraint failures;
3. build one disposable full Database v2 candidate;
4. run the independent v2 validator;
5. inspect any mismatch rather than changing expected baselines automatically;
6. only after that evidence exists, add/perform the final release-acceptance step;
7. update the normal Database user guide/active release documentation;
8. return immediately to Study 01.

Until that local execution occurs, Database v2 is **implemented in the repository but not yet validated or accepted**.
