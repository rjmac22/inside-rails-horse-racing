# Phase 4 Source Version 1 Raw-Mirror Prototype Evidence

## Status

**Accepted bounded persistence prototype. Not an accepted database release.**

Completed and independently reviewed on 6 August 2026.

This evidence record is governed by:

- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`;
- `docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

The prototype answers one bounded question:

> Can the authorised non-`STRICT`, untyped Source Version 1 raw-mirror table preserve exact SQLite values, storage classes, row lineage and canonical row fingerprints after a real disk write, close and readback from the accepted immutable source file?

The answer is **yes for the reviewed representative sample and fail-closed execution path described below**.

It does not yet prove a complete Source Version 1 load or authorise release acceptance.

---

## 1. Accepted source identity

The prototype uses the exact accepted Source Version 1 file at the repository-local default path:

```text
data/raw/form_2015-present/form_2015-present/raceform.db
```

Observed and enforced source evidence:

```text
original filename: raceform.db
file size: 765,825,024 bytes
file SHA-256: 77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
schema SHA-256: 991d95b497256c1fe6063efd422cc26c6d74e78c19f92daa4556164be3a88dba
physical rows: 1,851,286
admitted rows: 1,851,285
retained excluded rows: 1
minimum admitted source date: 2015-01-01
maximum admitted source date: 2026-05-27
admission predicate: rowid <> 1
```

The source is opened in SQLite read-only URI mode. The complete file SHA-256 is checked before the prototype starts and again after the candidate has been built and validated.

A file with matching schema and headline counts but a different full SHA-256 fails before candidate creation.

---

## 2. Implemented prototype boundary

The bounded implementation consists of:

- `src/inside_rails/database/raw_mirror_prototype.py`;
- `src/inside_rails/database/accepted_source.py`;
- `scripts/prototype_raw_mirror.py`;
- `tests/test_database_raw_mirror_prototype.py`;
- `tests/test_database_accepted_source.py`.

It uses the accepted Phase 4 schema and identifier/fingerprint implementations:

- `src/inside_rails/database/schema.py`;
- `src/inside_rails/database/schema/v001_minimum_core.sql`;
- `src/inside_rails/database/schema/v001_minimum_core_enforcement.sql`;
- `src/inside_rails/database/identifiers.py`;
- `src/inside_rails/database/fingerprints.py`.

The command is:

```bash
python scripts/prototype_raw_mirror.py
```

The output is a disposable ignored candidate at:

```text
data/processed/database/prototypes/raceform_v1_raw_mirror_prototype.sqlite3
```

The command refuses to overwrite an existing candidate.

---

## 3. Exact schema and source-population gate

Before candidate creation, the prototype requires:

- the exact accepted 37 source fields;
- the exact field order;
- the exact declared source types;
- no unexpected source `NOT NULL`, default or primary-key declarations;
- the accepted physical, admitted and excluded row counts;
- the accepted minimum and maximum admitted source dates;
- `PRAGMA quick_check` returning exactly `ok`;
- the full accepted Source Version 1 file SHA-256.

A schema, population, date-boundary, integrity or identity difference fails closed.

---

## 4. Representative source-backed sample

The real-source run selected these seven deterministic physical source rows:

```text
1, 2, 3, 4, 5, 153, 160
```

Together they cover the required prototype evidence:

- retained excluded source `rowid = 1`;
- the first admitted source record;
- `prize` represented as empty `TEXT`;
- `prize` represented as `INTEGER`;
- `prize` represented as `REAL`;
- `prize` represented as non-empty `TEXT`;
- `num` represented as `INTEGER` and `TEXT`;
- `ovr_btn` represented as `REAL`.

Several requirements are satisfied by the same physical row, leaving seven unique rows.

A source lacking one of the required observed examples fails before candidate creation.

---

## 5. Storage-class finding

The real Source Version 1 profiling established that admitted raw values use exactly these SQLite storage classes:

```text
integer
real
text
```

No admitted value in any of the 37 source fields is stored as SQLite `NULL` or `BLOB`.

Blank values are source-presented values, commonly empty `TEXT`, rather than inferred SQL nulls. The prototype preserves that distinction exactly and does not normalise blanks during raw mirroring.

This finding corrected the first synthetic prototype assumption, which had incorrectly required a `prize` value stored as SQLite `NULL`. The tests and selector were changed to represent the real source convention rather than forcing a fabricated storage class.

---

## 6. Persisted readback evidence

The reviewed accepted-source run produced:

```text
copied records: 7
raw-value comparisons after reopen: 259
SQLite typeof() comparisons after reopen: 259
row-fingerprint comparisons after reopen: 7
observed storage classes: integer, real, text
PRAGMA quick_check: ok
PRAGMA foreign_key_check rows: 0
source hash unchanged: true
persisted readback passed: true
```

The 259 value comparisons and 259 storage-class comparisons equal:

```text
7 records × 37 raw fields
```

For every copied source row, the readback validation proves:

- deterministic `source_record_code` equality;
- exact source `rowid` lineage;
- the required admitted or retained-excluded structural status;
- correct exclusion-reason state;
- Python value type and value equality for every raw field;
- bit-exact equality for floating-point values;
- exact SQLite `typeof()` equality for every raw field;
- equality of the stored canonical SHA-256 row fingerprint;
- equality of a newly recomputed fingerprint from persisted target values.

Both source and target files are closed and reopened for the readback phase.

---

## 7. Independent review and repair

The independent review found one material fail-closed gap in the first version:

- it proved that the source file hash did not change during one run;
- it did not prove that the starting file was the accepted exact Source Version 1 file.

That would have allowed a different file with the same schema and headline population to be recorded as `accepted_exact_source`.

The repair added `src/inside_rails/database/accepted_source.py`, which:

1. checks the complete accepted source SHA-256 before invoking the prototype builder;
2. confirms that the builder recorded the same complete source SHA-256;
3. checks the complete accepted source SHA-256 again after the build;
4. deletes the candidate if the source changes or the builder reports a different identity.

The command-line entry point now routes through this accepted-source gate.

---

## 8. Fail-closed behaviour proved by tests

The focused tests prove failure before or cleanup after candidate creation for:

- missing source file;
- wrong accepted source SHA-256;
- malformed expected SHA-256 length;
- exact source-schema mismatch;
- source population or date-boundary mismatch;
- missing required representative storage-class example;
- an already-existing output path;
- a source change after candidate construction;
- a builder recording a different source hash;
- candidate write, constraint or persisted-readback failure.

The raw prototype deletes a newly created candidate on any build or validation exception. The accepted-source wrapper also deletes a candidate when its post-build identity checks fail.

It never modifies or deletes the immutable source.

---

## 9. Focused validation evidence

After the independent review repair, the complete bounded Phase 4 test set passed:

```text
35 passed in 1.39s
```

The focused set covered:

- Phase 4 schema creation and exact object inventory;
- independent schema enforcement and trigger review;
- deterministic identifiers;
- canonical raw-row fingerprints;
- synthetic raw-mirror persistence and failure behaviour;
- accepted exact-source identity enforcement.

The reviewed real-source prototype then passed with the evidence recorded in Section 6.

No complete repository test suite or all-validator sweep was run for this bounded prototype step.

---

## 10. Limitations

This prototype deliberately does **not** yet provide:

- a source-wide copy of all 1,851,286 physical rows;
- source-wide row-fingerprint reconciliation;
- batching, restart or measured full-load performance;
- a populated accepted governance method or governance release;
- governance evidence records;
- reconstructed core race occurrences;
- core runner participations;
- an import manifest or import-validation results;
- complete source-to-core population reconciliation;
- a final database-file hash and external release manifest;
- atomic promotion or active-release switching;
- an accepted immutable database release.

The candidate contains source metadata and seven representative raw records only. Counts recorded in `source_version` and `source_relation` describe the accepted source snapshot, not the number of raw rows copied into this prototype.

The output must therefore remain clearly labelled as a prototype and must not be used as a complete analytical database.

---

## 11. Decision and next bounded action

The prototype provides sufficient evidence to retain the authorised untyped raw-column design:

- source values survive the target write without affinity coercion;
- SQLite storage classes survive exactly;
- deterministic lineage codes survive;
- canonical row fingerprints survive and recompute after readback;
- the accepted source file can be bound fail-closed to its complete SHA-256.

The next bounded implementation should extend this reviewed pattern to a **complete disposable Source Version 1 raw-mirror candidate** with:

- batched loading of all 1,851,286 physical rows;
- exact physical/admitted/excluded reconciliation;
- source-wide deterministic code and row-fingerprint validation;
- persisted readback through an independent validator;
- measured build evidence and complete failure cleanup.

That next step must still stop before core race/runner population, release acceptance or atomic promotion unless those separately pass their own bounded implementation and validation gates.
