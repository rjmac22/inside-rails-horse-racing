# Phase 4 Complete Minimum-Core Candidate Evidence

## Status

**Complete disposable Source Version 1 minimum-core candidate built and independently validated on 6 August 2026.**

This evidence closes the source-wide minimum-core construction step only.

It establishes that the accepted raw mirror can be transformed into the authorised structural race and runner tables across the complete Source Version 1 population, with exact lineage, deterministic identifiers, persisted reconciliation and independent source-wide validation.

It does **not** accept a database release, promote an active database, replace a prior accepted release, complete the project acceptance gate, authorise analytical field extensions, or permit bulk redistribution of the source data.

The generated candidate remains an ignored, disposable artifact. Its persisted import manifest remains at `built`, and `release_accepted` remains false.

---

## 1. Governing boundary

The step was governed by:

- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md`.

The bounded question was:

> Can the complete accepted Source Version 1 raw mirror be transformed into exactly one canonical race occurrence per authorised raw `date + course + off` group and exactly one runner participation per admitted source record, while retaining the complete raw evidence, deterministic lineage, durable build provenance and independent persisted validation?

The answer is **yes for the complete disposable candidate described here**.

---

## 2. Implementation

Complete candidate builder:

- `src/inside_rails/database/minimum_core_candidate.py`
- `src/inside_rails/database/minimum_core_candidate_io.py`
- `src/inside_rails/database/minimum_core_candidate_manifest.py`
- `src/inside_rails/database/minimum_core_candidate_model.py`
- `src/inside_rails/database/minimum_core_candidate_population.py`
- `src/inside_rails/database/minimum_core_candidate_readback.py`
- `src/inside_rails/database/minimum_core_candidate_seed.py`
- `scripts/build_minimum_core_candidate.py`

Independent complete-candidate validator:

- `src/inside_rails/database/minimum_core_validator.py`
- `scripts/validate_minimum_core_candidate.py`

Focused tests:

- `tests/test_database_minimum_core_candidate.py`
- `tests/test_database_minimum_core_validator.py`

The real complete candidate was built from repository commit:

```text
732fa63bf5ec927e3215b9f55c296beebaf4d974
```

The independent validator and its focused tests were present at repository commit:

```text
f930b00030955b295f72a87dc196d2c50abd11ba
```

The builder and independent validator are separate code paths. The validator does not trust the builder's JSON summary, in-memory counters or persisted self-description. It independently opens the accepted source, complete raw mirror and complete minimum-core candidate read-only and derives its own reconciliation evidence.

---

## 3. Accepted immutable inputs

### 3.1 Source Version 1

Source path used locally:

```text
data/raw/form_2015-present/form_2015-present/raceform.db
```

Accepted complete SHA-256:

```text
77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
```

Source file size:

```text
765825024 bytes
```

Accepted source population:

```text
physical records: 1851286
admitted records: 1851285
excluded records: 1
admission predicate: rowid <> 1
```

### 3.2 Complete raw-mirror candidate

Raw-mirror path used locally:

```text
data/processed/database/candidates/raceform_v1_raw_mirror_candidate.sqlite3
```

Accepted candidate SHA-256:

```text
cbc7ac16c0a66f50002e2cf9b17d3bc77795640b7a340537f3cd83d202543f3a
```

Raw-mirror file size:

```text
1356701696 bytes
```

Both input hashes were checked before and after the complete build and before and after the independent validation. Both inputs remained unchanged.

---

## 4. Complete minimum-core candidate artifact

Generated path:

```text
data/processed/database/candidates/raceform_v1_minimum_core_candidate.sqlite3
```

Candidate file size:

```text
1730048000 bytes
```

Candidate SHA-256 after the successful build and before/after independent validation:

```text
7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
```

SQLite header values:

```text
application_id: 1230130259
user_version: 1
```

Persisted build identifiers:

```text
import_manifest_code: imp:20260806T110355286543Z:989756fa
database_release_code: db:20260806T110355286543Z:c427ca06
```

Persisted candidate state:

```text
build_status: built
release_accepted: false
validation-result rows written by builder: 4
```

The candidate is not an accepted database release. The `database_release_code` is a durable identity for this build attempt, not evidence of promotion or acceptance.

---

## 5. Builder-focused automated tests

The complete candidate builder was first exercised against controlled synthetic data:

```bash
pytest -q tests/test_database_minimum_core_candidate.py
```

Initial result:

```text
1 failed, 5 passed in 2.42s
```

The sole failure was a brittle test expectation. The database correctly rejected an invalid transition from `built` to `release_accepted`, but a different authorised integrity trigger produced the rejection message before the trigger named by the test.

No production code changed. The test was corrected to assert the required invariant:

- an invalid release-acceptance transition raises `sqlite3.IntegrityError`;
- after rollback, the manifest remains at `built`.

Rerun result:

```text
6 passed in 2.24s
```

The focused builder tests covered:

- complete race and runner population on synthetic source data;
- deterministic race and runner identities;
- durable import-manifest construction;
- persisted final-state reconciliation;
- refusal of an incorrect raw-mirror hash;
- refusal of incomplete raw-mirror population;
- refusal to overwrite an existing output;
- early rejection of invalid arguments;
- removal of the generated database and SQLite sidecars after forced readback failure;
- refusal to treat a completed disposable build as release accepted.

---

## 6. Pre-build database-focused gate

Before the real complete source-wide build, the bounded database-focused test set was run:

```bash
pytest -q \
  tests/test_database_schema_v001.py \
  tests/test_database_schema_v001_review.py \
  tests/test_database_identifiers.py \
  tests/test_database_fingerprints.py \
  tests/test_database_accepted_source.py \
  tests/test_database_raw_mirror_prototype.py \
  tests/test_database_raw_mirror_candidate.py \
  tests/test_database_raw_mirror_validator.py \
  tests/test_database_core_structure_prototype.py \
  tests/test_database_core_structure_validator.py \
  tests/test_database_minimum_core_candidate.py
```

Result:

```text
66 passed in 12.79s
```

This was a bounded database gate, not the complete repository test suite or final all-validator sweep.

---

## 7. Complete source-wide build evidence

Command:

```bash
python scripts/build_minimum_core_candidate.py
```

### 7.1 Population result

```text
physical_record_count: 1851286
admitted_record_count: 1851285
excluded_record_count: 1
race_occurrence_count: 189043
runner_participation_count: 1851285
```

The exact expected complete population was produced:

- one retained excluded raw record for Source Version 1 `rowid = 1`;
- one runner participation for each of the 1,851,285 admitted source records;
- 189,043 canonical race occurrences ordered by ascending minimum supporting source rowid.

### 7.2 Batch and performance result

```text
batch_size: 5000
race_batch_count: 38
runner_batch_count: 371
copied_bytes: 1356701696
copy_elapsed_seconds: 4.274955792003311
core_population_elapsed_seconds: 36.818536445032805
build_elapsed_seconds: 76.16271843307186
core_rows_per_second: 55415.78229341218
```

The performance figures are observational evidence from this machine and build. They are not a guaranteed service level or cross-machine benchmark.

### 7.3 Builder persisted readback

```text
race_readback_comparisons: 189043
runner_readback_comparisons: 1851285
persisted_readback_passed: true
quick_check: ok
foreign_key_check_rows: 0
application_id: 1230130259
user_version: 1
source_hash_unchanged: true
raw_mirror_candidate_hash_unchanged: true
manifest_status: built
release_accepted: false
```

The builder:

1. verified the exact accepted source and raw-mirror hashes before creating the output;
2. refused any pre-existing output database or SQLite sidecar;
3. durably copied the complete independently validated raw mirror to a new candidate;
4. verified the copied raw-mirror hash before structural population;
5. verified the exact raw-only schema boundary and population;
6. inserted the accepted structural governance method and evidence references;
7. inserted an import manifest at `building` before core population;
8. created all canonical race occurrences in deterministic order;
9. created one runner participation for every admitted source record;
10. committed the complete core population only after exact expected counts were reached;
11. closed and reopened the database read-only;
12. reconciled every race and every runner against persisted raw evidence;
13. ran SQLite `quick_check` and `foreign_key_check`;
14. finalised the manifest at `built`, never `release_accepted`;
15. deleted the generated database and all known SQLite sidecars on any failure.

The builder's complete persisted readback was necessary but was not treated as independent validation.

---

## 8. Independent validator-focused tests

Before applying the independent validator to the complete candidate, its synthetic focused tests were run:

```bash
pytest -q tests/test_database_minimum_core_validator.py
```

Result:

```text
6 passed in 2.94s
```

The validator tests covered:

- successful independent reconciliation of a complete controlled candidate;
- detection of altered raw evidence;
- detection of altered race identity;
- detection of altered runner identity;
- detection of inconsistent manifest state;
- detection of unauthorised schema inventory changes;
- refusal to validate when SQLite journal, WAL or shared-memory sidecars are present.

---

## 9. Complete independent source-wide validation evidence

Command:

```bash
python scripts/validate_minimum_core_candidate.py
```

Validation elapsed time:

```text
199.25864554394502 seconds
```

Observed validation throughput:

```text
9290.86913617363 raw records per second
```

The throughput figure is observational only and does not imply that all validation work is reducible to one comparison per raw record.

### 9.1 Raw evidence reconciliation

```text
raw_record_comparisons: 1851286
raw_value_comparisons: 68497582
storage_class_comparisons: 68497582
source_record_code_comparisons: 1851286
structural_status_comparisons: 1851286
stored_fingerprint_comparisons: 1851286
recomputed_fingerprint_comparisons: 1851286
```

The validator independently compared every retained raw record between the complete raw mirror and complete minimum-core candidate.

For all 1,851,286 raw records it checked:

- exact source-row identity;
- deterministic source-record code;
- structural admission or exclusion status;
- exclusion reason;
- stored row fingerprint;
- independently recomputed row fingerprint.

Across the 37 raw source fields it performed:

- 68,497,582 exact value comparisons;
- 68,497,582 SQLite storage-class comparisons.

### 9.2 Race reconciliation

```text
race_code_comparisons: 189043
race_grouping_comparisons: 189043
race_runner_count_comparisons: 189043
```

For every canonical race occurrence, the validator independently reconstructed the expected group from admitted raw rows and checked:

- canonical integer ordering by minimum supporting source rowid;
- deterministic race code;
- exact raw `date`, `course` and `off` group identity;
- exact admitted-runner count;
- compatible accepted structural governance.

### 9.3 Runner reconciliation

```text
runner_code_comparisons: 1851285
runner_lineage_comparisons: 1851285
```

For every admitted source record, the validator independently checked:

- exactly one runner participation exists;
- deterministic runner code;
- exact source-record linkage;
- linkage to the correct race occurrence;
- exact admitted source-record status;
- compatible accepted structural governance.

### 9.4 Metadata, governance, manifest and SQLite reconciliation

```text
metadata_row_comparisons: 41
metadata_reconciliation_passed: true
governance_reconciliation_passed: true
manifest_reconciliation_passed: true
manifest_validation_result_count: 4
schema_inventory_matched: true
quick_check: ok
foreign_key_check_rows: 0
application_id: 1230130259
user_version: 1
persisted_readback_passed: true
release_accepted: false
```

The independent validator also checked:

- exact authorised schema inventory;
- source-provider, product, version, relation and all 37 ordered field records;
- accepted structural governance method and release metadata;
- required governance evidence references;
- manifest counts, commits, build command, timestamps and state;
- the four builder validation-result records;
- absence of any `release_accepted` import manifest;
- absence of SQLite sidecars;
- unchanged source, raw-mirror and candidate hashes before and after validation.

The validator was read-only. It did not alter the candidate manifest from `built` to `validated` and did not insert its own result into the database.

---

## 10. Final bounded database-focused gate

After the real complete build and independent source-wide validation, the database-focused test set was rerun with the complete validator tests included:

```bash
pytest -q \
  tests/test_database_schema_v001.py \
  tests/test_database_schema_v001_review.py \
  tests/test_database_identifiers.py \
  tests/test_database_fingerprints.py \
  tests/test_database_accepted_source.py \
  tests/test_database_raw_mirror_prototype.py \
  tests/test_database_raw_mirror_candidate.py \
  tests/test_database_raw_mirror_validator.py \
  tests/test_database_core_structure_prototype.py \
  tests/test_database_core_structure_validator.py \
  tests/test_database_minimum_core_candidate.py \
  tests/test_database_minimum_core_validator.py
```

Result:

```text
72 passed in 14.54s
```

This confirms that the complete builder and validator did not regress the accepted schema, identity, fingerprint, raw-mirror or three-race prototype contracts.

It remains a bounded database-focused gate. The complete repository test suite and final all-validator sweep have not yet been run for release acceptance.

---

## 11. Bounded conclusion

The authorised minimum physical core has now been demonstrated across the complete accepted Source Version 1 population.

The evidence establishes that:

- all 1,851,286 physical source records remain present in the candidate raw layer;
- all 1,851,285 admitted source records have exactly one runner participation;
- all admitted records are assigned to exactly one of 189,043 canonical race occurrences;
- race identities are deterministic and reproducible from the accepted structural method;
- runner identities and source lineage are deterministic and reproducible;
- all copied raw values, SQLite storage classes and row fingerprints remain exact;
- the schema, source metadata, governance metadata and build manifest reconcile;
- the source file and complete raw mirror remain immutable;
- the complete candidate survives close-and-reopen validation;
- an independent read-only validator reproduces the source-wide result;
- the candidate cannot silently declare itself release accepted.

This removes the remaining source-wide structural uncertainty from the minimum-core build.

---

## 12. Remaining limitations

This evidence does not establish complete database-release acceptance or operational promotion.

The following remain outside this bounded step:

- recording the independent source-wide validator as durable acceptance evidence through an authorised procedure;
- transition of the import manifest from `built` to any later governed state;
- complete repository test-suite evidence;
- final all-validator sweep evidence;
- prior accepted-release preservation against a real prior release;
- atomic promotion and rollback of an active database;
- active-release resolution for downstream consumers;
- final project acceptance and sign-off;
- database integration documentation for downstream analytical code;
- governed analytical field extensions beyond the minimum structural core;
- publication or redistribution rights for the underlying source data.

The candidate file remains disposable generated output and may be deleted and reproduced from the accepted immutable inputs and recorded code commit.

---

## 13. Next bounded step

The next implementation unit should define and evidence the **database-release acceptance and promotion boundary** without retroactively weakening the candidate safeguards proved here.

That unit should decide, before any promotion:

- how independent validator evidence is durably recorded;
- whether acceptance occurs by controlled mutation, immutable copy, or a separate release registry;
- how `built`, `validated` and `release_accepted` states are authorised and separated;
- how the complete repository suite and final all-validator sweep are attached to the release decision;
- how a prior accepted release is preserved;
- how active-release replacement is atomic and reversible;
- how downstream code resolves the active accepted database;
- how failure leaves the previously accepted release untouched.

No candidate should be promoted or marked `release_accepted` until that boundary is explicitly specified, implemented, tested and reviewed.