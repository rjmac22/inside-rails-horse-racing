# Phase 4 Complete Raw-Mirror Candidate Evidence

## Status

**Complete disposable Source Version 1 raw mirror built and independently validated on 6 August 2026.**

This evidence closes the source-wide raw-preservation step only.

It does **not** accept a database release, populate the authorised core race or runner tables, create governance-release records, populate import manifests, or promote any file for analytical use.

The candidate remains an ignored generated artifact and may be deleted and rebuilt.

---

## 1. Governing boundary

The step was governed by:

- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_4_RAW_MIRROR_PROTOTYPE_EVIDENCE.md`.

The bounded question was:

> Can every physical Source Version 1 row be copied into the authorised untyped raw table, with exact values, SQLite storage classes, deterministic lineage codes and canonical row fingerprints preserved and independently reconciled after persistence?

The answer is **yes for the complete disposable raw-mirror candidate described here**.

---

## 2. Implementation

Builder:

- `src/inside_rails/database/raw_mirror_candidate.py`
- `scripts/build_raw_mirror_candidate.py`

Independent validator:

- `src/inside_rails/database/raw_mirror_validator.py`
- `scripts/validate_raw_mirror_candidate.py`

Focused tests:

- `tests/test_database_raw_mirror_candidate.py`
- `tests/test_database_raw_mirror_validator.py`

The implementation and validator were present at repository commit:

```text
df692738fabf5cfc21400c2cbd6404c3009213cb
```

The builder and validator are separate code paths. The validator does not trust builder counters or the builder summary. It reopens both files read-only and derives its own reconciliation evidence.

---

## 3. Accepted source identity

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

Accepted ordered source-schema SHA-256:

```text
991d95b497256c1fe6063efd422cc26c6d74e78c19f92daa4556164be3a88dba
```

Accepted source population:

```text
physical records: 1851286
admitted records: 1851285
excluded records: 1
admission predicate: rowid <> 1
minimum admitted date: 2015-01-01
maximum admitted date: 2026-05-27
```

The source hash was checked before and after both the build and validation runs. It remained unchanged.

---

## 4. Candidate artifact

Generated path:

```text
data/processed/database/candidates/raceform_v1_raw_mirror_candidate.sqlite3
```

The path and SQLite file extension are ignored by Git.

Candidate file size:

```text
1356701696 bytes
```

Candidate SHA-256 after the successful build and before/after independent validation:

```text
cbc7ac16c0a66f50002e2cf9b17d3bc77795640b7a340537f3cd83d202543f3a
```

SQLite header values:

```text
application_id: 1230130259
user_version: 1
```

The candidate had no retained journal, WAL or shared-memory sidecars.

The candidate is not an accepted release. Its hash identifies this one disposable generated artifact only.

---

## 5. Focused automated gate

Before the real source-wide build, the complete focused Phase 4 raw-mirror test set was run:

```bash
pytest -q \
  tests/test_database_schema_v001.py \
  tests/test_database_schema_v001_review.py \
  tests/test_database_identifiers.py \
  tests/test_database_fingerprints.py \
  tests/test_database_accepted_source.py \
  tests/test_database_raw_mirror_prototype.py \
  tests/test_database_raw_mirror_candidate.py \
  tests/test_database_raw_mirror_validator.py
```

Result:

```text
48 passed in 4.21s
```

The focused set covered:

- exact Phase 4 schema creation and object inventory;
- independent schema and trigger enforcement review;
- deterministic source identifiers;
- canonical typed row fingerprints;
- exact accepted-source hash enforcement;
- the seven-row persisted prototype;
- complete batched raw-mirror construction on synthetic data;
- wrong-source and overwrite rejection;
- rollback and generated-file cleanup after forced failure;
- independent validation success and deliberate corruption detection.

No complete repository test suite or all-validator sweep was run for this bounded Phase 4 step.

---

## 6. Source-wide build evidence

Command:

```bash
python scripts/build_raw_mirror_candidate.py
```

Observed result:

```text
physical_record_count: 1851286
admitted_record_count: 1851285
excluded_record_count: 1
copied_record_count: 1851286
copied_admitted_record_count: 1851285
copied_excluded_record_count: 1
row_fingerprint_count: 1851286
batch_size: 1000
batch_count: 1852
build_elapsed_seconds: 140.6863697260851
rows_per_second: 13158.957783930558
output_file_size_bytes: 1356701696
quick_check: ok
foreign_key_check_rows: 0
application_id: 1230130259
user_version: 1
source_hash_unchanged: true
persisted_structural_checks_passed: true
```

The builder:

1. verified the complete accepted source SHA-256 before opening the candidate;
2. validated the exact 37-field source declaration and accepted source baseline;
3. created the authorised minimum-core schema in a new disposable SQLite file;
4. inserted source metadata and all 37 ordered source-field declarations;
5. streamed all physical source rows in ascending `rowid` batches;
6. generated one deterministic source-record code and one canonical SHA-256 fingerprint per physical row;
7. retained Source Version 1 `rowid = 1` with explicit excluded status and reason;
8. classified every other physical row as an admitted runner record;
9. committed only after exact physical/admitted/excluded reconciliation;
10. closed and reopened the candidate for structural checks;
11. reran source identity validation after the build;
12. deleted the candidate and any SQLite sidecars on any failure.

The builder's post-close checks were deliberately described as structural checks, not independent persisted readback.

---

## 7. Independent source-wide validation evidence

Command:

```bash
python scripts/validate_raw_mirror_candidate.py
```

Observed result:

```text
physical_record_count: 1851286
admitted_record_count: 1851285
excluded_record_count: 1
compared_record_count: 1851286
raw_value_comparisons: 68497582
storage_class_comparisons: 68497582
source_record_code_comparisons: 1851286
structural_status_comparisons: 1851286
stored_fingerprint_comparisons: 1851286
recomputed_fingerprint_comparisons: 1851286
batch_size: 1000
batch_count: 1852
validation_elapsed_seconds: 290.53532930405345
rows_per_second: 6371.982383122077
quick_check: ok
foreign_key_check_rows: 0
schema_inventory_matched: true
metadata_reconciliation_passed: true
raw_population_reconciliation_passed: true
persisted_readback_passed: true
source_hash_unchanged: true
candidate_hash_unchanged: true
```

The arithmetic is exact:

```text
1851286 records × 37 raw fields = 68497582 comparisons
```

The independent validator proved for every physical source row that:

- the candidate contains exactly one corresponding row;
- source rows and candidate rows remain in identical ascending source-`rowid` order;
- the candidate internal record sequence is complete and one-based;
- `source_version_id` and `source_relation_id` match the accepted fixed lineage;
- the source `rowid` matches exactly;
- the deterministic source-record code recomputes exactly;
- structural status and exclusion reason match the accepted `rowid = 1` rule;
- all 37 logical values compare exactly;
- all 37 SQLite `typeof()` storage classes compare exactly;
- the stored row fingerprint matches a fresh fingerprint calculated from the source values;
- a fresh fingerprint calculated from persisted candidate values matches the same expected digest.

The validator also independently checked:

- exact candidate schema inventory;
- absence of unauthorised populated core, governance and import rows;
- source-version, relation and field metadata;
- complete physical/admitted/excluded population counts;
- SQLite `quick_check`;
- SQLite foreign-key integrity;
- application and schema version header values;
- absence of SQLite sidecars before and after validation;
- source and candidate file hashes before and after validation.

---

## 8. Storage-class conclusion

The complete validation confirms that the authorised raw-table design prevents SQLite affinity coercion.

Across the accepted source population, the observed source storage classes are the source's actual classes, including mixed `integer`, `real` and `text` representations in columns whose declarations might otherwise coerce them.

The raw columns in `source_raceform_v1_record` therefore remain deliberately untyped. This preserves both the source value and its physical SQLite storage class.

A typed or `STRICT` declaration for those 37 raw columns would weaken the evidence layer and remains prohibited by the accepted physical specification.

---

## 9. Fail-closed behaviour retained

The complete builder and validator stop for investigation when they encounter, among other controls:

- a source hash different from the accepted complete Source Version 1 SHA-256;
- an exact source-schema mismatch;
- a changed physical/admitted/excluded baseline;
- an invalid batch size;
- an existing candidate file or SQLite sidecar;
- non-increasing source `rowid` ordering;
- incomplete or excessive source population;
- any failed database write or constraint;
- a persisted candidate count mismatch;
- an unexpected schema object;
- populated unauthorised core, governance or import structures;
- metadata disagreement;
- a missing, duplicate or reordered raw record;
- a raw value or storage-class difference;
- a deterministic-code, status or fingerprint difference;
- a failed SQLite integrity or foreign-key check;
- source or candidate mutation during validation.

Builder failure removes the candidate database and any known SQLite sidecars. Validation failure does not modify the candidate; it reports the first detected divergence.

---

## 10. What this step proves

This step proves that the project can reproducibly build a complete raw evidence layer for the accepted immutable Source Version 1 file and independently verify it source-wide after persistence.

Specifically, it proves:

- exact source identity;
- exact ordered source schema;
- complete physical-row coverage;
- exact admitted/excluded partitioning;
- complete technical lineage;
- exact preservation of every raw value;
- exact preservation of every SQLite storage class;
- one canonical fingerprint per source row;
- deterministic persisted source-record identifiers;
- database structural integrity;
- independent persisted readback;
- no mutation of source or candidate during validation.

This is a meaningful implementation milestone: the full raw evidence layer is no longer only a schema design or representative prototype.

---

## 11. Limitations and prohibited interpretations

This step does **not** prove or provide:

- reconstructed `core_source_race_occurrence` rows;
- reconstructed `core_runner_participation` rows;
- source-to-core race or runner reconciliation;
- populated governance methods or governance releases;
- governance evidence records;
- an import manifest or import-validation result population;
- code-commit and build-command evidence stored inside the candidate;
- a final accepted database-file hash recorded in an external manifest;
- a stable release filename or immutable release location;
- atomic promotion or active-release switching;
- a consumer-facing query-only release resolver;
- an accepted analytical database release.

The raw candidate contains the complete source evidence layer but deliberately leaves all downstream authorised structures empty.

The source-version metadata describes the accepted source snapshot. It must not be interpreted as accepting this generated candidate as a database release.

The candidate must not be published, distributed as a data product, or used as though core racing entities have already been reconstructed.

---

## 12. Decision and next bounded action

The complete raw-mirror implementation is accepted as the reusable source-preservation basis for the remaining Phase 4 work.

The next bounded implementation should be a **small source-backed core race-and-runner reconstruction prototype** that:

- reads only admitted raw-mirror records from the persisted candidate;
- reconstructs a deliberately small deterministic set of provisional race occurrences using the accepted `date + course + off` structure;
- creates deterministic race and runner-participation codes using the authorised ordering rules;
- preserves direct lineage from every core runner participation to its raw source record;
- proves race-to-runner cardinality and source-row partitioning for the selected sample;
- closes and independently validates the persisted prototype;
- remains disposable and stops before a source-wide core load, governance release, import manifest or database-release acceptance.

A full source-wide core population is not yet authorised.