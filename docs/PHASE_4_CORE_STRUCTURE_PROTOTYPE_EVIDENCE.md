# Phase 4 Core Structure Prototype Evidence

## Status

**Bounded prototype proved on 6 August 2026.**

This document records the completed rehearsal for converting the validated Source Version 1 raw mirror into the authorised race-and-runner core structure.

The result proves a deliberately small persisted population only:

- the first three complete Source Version 1 race groups under the accepted deterministic ordering;
- all 26 admitted runner records supporting those groups;
- the retained excluded physical source row at `source_rowid = 1`;
- the accepted structural-governance method, release and evidence references.

It does **not** authorise or claim:

- the complete 189,043-race core load;
- an accepted database release;
- import-manifest completion;
- release promotion or active-database replacement;
- governed field extensions beyond the minimum structural core.

---

## 1. Governing contracts

The prototype implements only the bounded structure authorised by:

- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`;
- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

The structural rule remains:

- one Source Version 1 race occurrence per accepted raw `date + course + off` group;
- race sequence assigned by ascending minimum supporting admitted source `rowid`;
- one runner participation per admitted physical source record;
- every core row retains direct lineage to immutable raw evidence;
- supplied `race_id`, horse text and runner number remain raw values rather than permanent keys.

---

## 2. Exact input identities

### Accepted source

Path:

```text
data/raw/form_2015-present/form_2015-present/raceform.db
```

SHA-256:

```text
77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
```

File size:

```text
765825024 bytes
```

### Independently validated raw-mirror candidate

Path:

```text
data/processed/database/candidates/raceform_v1_raw_mirror_candidate.sqlite3
```

SHA-256:

```text
cbc7ac16c0a66f50002e2cf9b17d3bc77795640b7a340537f3cd83d202543f3a
```

File size:

```text
1356701696 bytes
```

The builder and independent validator both required the exact hashes above and confirmed that both files remained unchanged throughout the prototype work.

---

## 3. Durable implementation

Builder module:

```text
src/inside_rails/database/core_structure_prototype.py
```

Builder CLI:

```text
scripts/build_core_structure_prototype.py
```

Independent validator module:

```text
src/inside_rails/database/core_structure_validator.py
```

Independent validator CLI:

```text
scripts/validate_core_structure_prototype.py
```

Focused tests:

```text
tests/test_database_core_structure_prototype.py
tests/test_database_core_structure_validator.py
```

Implementation commits:

```text
521d6010ad173564160f817f1a3eabb38df46020  bounded builder and focused tests
5a65f3e9040bcdb6344cb6d1b383c333ba633557  independent validator and focused tests
```

---

## 4. Builder behaviour

The builder:

1. validates the exact accepted source identity;
2. validates the exact independently approved raw-mirror candidate identity;
3. requires the raw mirror to remain at the raw-only boundary;
4. selects the first complete race groups by ascending minimum admitted source `rowid`;
5. copies every admitted record in each selected group rather than sampling runners;
6. also copies retained excluded `source_rowid = 1`;
7. preserves all 37 raw values and their SQLite storage classes;
8. preserves deterministic source-record codes and row fingerprints;
9. seeds the accepted structural-governance method, release and evidence references;
10. creates deterministic race and runner identifiers using the accepted algorithms;
11. writes to a separate disposable SQLite file;
12. closes and reopens the file for persisted readback;
13. reconciles races, runners, raw values, storage classes and fingerprints;
14. checks SQLite integrity and foreign keys;
15. rechecks both input hashes;
16. removes the database and all SQLite sidecars after any failure.

It refuses to overwrite an existing prototype artifact.

---

## 5. Focused test evidence

### Builder tests

Command:

```bash
pytest -q tests/test_database_core_structure_prototype.py
```

Result:

```text
6 passed in 4.68s
```

The tests covered:

- complete first-race selection and runner lineage;
- deterministic race and runner codes;
- raw-value and storage-class persistence;
- governance seeding;
- exact raw-mirror hash gating;
- altered candidate values and fingerprints;
- incomplete candidate population;
- overwrite refusal and argument validation;
- deletion of the prototype and sidecars after forced persisted-readback failure.

### Independent-validator tests

Command:

```bash
pytest -q tests/test_database_core_structure_validator.py
```

Result:

```text
6 passed in 4.41s
```

The validator tests included a correct end-to-end prototype plus deliberate failures for:

- raw-value corruption;
- race-structure corruption;
- governance corruption;
- schema-inventory expansion;
- unexpected SQLite sidecars.

---

## 6. Real prototype build

Command:

```bash
python scripts/build_core_structure_prototype.py
```

Generated file:

```text
data/processed/database/prototypes/raceform_v1_core_structure_prototype.sqlite3
```

Generated-file SHA-256:

```text
7fd9ac19f1822b3f0437344053212c35981069688c476f2969b3240c86a29ace
```

Selected race minimum source rowids:

```text
2, 3, 4
```

Persisted population:

| Measure | Result |
|---|---:|
| Selected complete races | 3 |
| Admitted runner records | 26 |
| Retained excluded records | 1 |
| Total copied raw records | 27 |
| Core race occurrences | 3 |
| Core runner participations | 26 |

Builder persisted-readback evidence:

| Check | Result |
|---|---:|
| Raw-value comparisons | 999 |
| SQLite storage-class comparisons | 999 |
| Stored fingerprint comparisons | 27 |
| Recomputed fingerprint comparisons | 27 |
| Race reconciliations | 3 |
| Runner reconciliations | 26 |
| `PRAGMA quick_check` | `ok` |
| Foreign-key-check rows | 0 |
| Source hash unchanged | yes |
| Raw-mirror hash unchanged | yes |
| Persisted readback | passed |

---

## 7. Independent real-prototype validation

Command:

```bash
python scripts/validate_core_structure_prototype.py
```

The independent validator began from the persisted prototype and independently reconstructed the expected bounded population from the complete raw mirror.

Result:

| Check | Result |
|---|---:|
| Compared raw records | 27 |
| Compared admitted records | 26 |
| Compared excluded records | 1 |
| Raw-value comparisons | 999 |
| Storage-class comparisons | 999 |
| Source-record-code comparisons | 27 |
| Structural-status comparisons | 27 |
| Stored-fingerprint comparisons | 27 |
| Recomputed-fingerprint comparisons | 27 |
| Race-grouping comparisons | 3 |
| Race-code comparisons | 3 |
| Race/runner-count comparisons | 3 |
| Runner-code comparisons | 26 |
| Runner-lineage comparisons | 26 |
| Schema inventory | matched |
| Source metadata | reconciled |
| Governance metadata | reconciled |
| `PRAGMA quick_check` | `ok` |
| Foreign-key-check rows | 0 |
| `application_id` | 1230130259 |
| `user_version` | 1 |
| Persisted readback | passed |
| Validation elapsed time | 22.00316964101512 seconds |

The validator also proved that the source, raw-mirror candidate and prototype hashes remained unchanged during validation.

---

## 8. Bounded conclusion

The minimum physical schema can represent real Source Version 1 race groups and runner participations without losing or coercing raw evidence.

For the first three deterministic race groups:

- every admitted raw record created exactly one runner participation;
- every runner participation attached to the correct race group;
- runner counts agreed with the supporting raw records;
- all stable codes were reproducible;
- all copied values and SQLite storage classes survived persistence exactly;
- all stored fingerprints and independently recomputed fingerprints matched;
- governance references were structurally compatible;
- no import manifest or database-release acceptance was fabricated;
- the immutable source and complete raw mirror remained unchanged.

This removes the main structural uncertainty before a complete core builder is attempted.

---

## 9. Remaining limitations

This evidence does not establish source-wide core performance, source-wide transaction behaviour or complete-release acceptance.

The prototype deliberately omits:

- the remaining 189,040 Source Version 1 race groups;
- the remaining admitted runner records;
- a full import manifest and validation-result population;
- complete candidate build timings and throughput;
- prior-release preservation and atomic promotion;
- active-release resolution;
- final repository-wide acceptance gates;
- all governed analytical field extensions.

The prototype file is disposable generated output and is not an accepted release.

---

## 10. Next bounded step

The next implementation unit may design and build a **complete disposable Source Version 1 minimum-core candidate** using the now-proved structural method.

That next unit must still remain separate from release acceptance. It must add, at minimum:

- batched source-wide core population;
- exact reconciliation to 189,043 races and 1,851,285 runner participations;
- a durable import manifest for the build attempt;
- source-wide persisted readback;
- an independent complete-core validator;
- measured build evidence;
- complete cleanup after failure.

Promotion, active-release replacement and final database-release acceptance remain separately gated.