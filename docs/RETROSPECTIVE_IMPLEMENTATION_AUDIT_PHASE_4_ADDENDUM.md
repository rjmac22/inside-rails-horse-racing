# Retrospective Implementation Audit — Phase 4 Addendum

## Status

**Phase 3 minimum stable core design and the Phase 4 complete disposable minimum-core candidate were completed and independently validated on 6 August 2026.**

This addendum extends `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`, whose notebook and cross-notebook classifications remain unchanged.

It records the subsequent entity/key and physical-database work without rewriting the historical notebook audit.

The result is a validated disposable candidate, not an accepted or promoted database release.

---

## 1. Bounded scope

The completed work answered four successive questions:

1. Can the accepted Source Version 1 file be identified exactly and mirrored without changing any physical value or SQLite storage class?
2. Can the authorised minimum core represent real race groups and runner participations without losing lineage?
3. Can the method scale to all 189,043 race occurrences and 1,851,285 admitted runner records?
4. Can separate code independently reconstruct and reconcile the complete candidate rather than trusting builder counters?

All four questions were answered **yes** for the exact source and candidate hashes recorded below.

The work did not accept a live database release, promote an artifact, replace a prior release or add governed analytical fields beyond the minimum structural core.

---

## 2. Accepted source boundary

Source path used locally:

```text
data/raw/form_2015-present/form_2015-present/raceform.db
```

Exact Source Version 1 identity:

```text
SHA-256: 77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
size: 765,825,024 bytes
physical records: 1,851,286
admitted records: 1,851,285
retained excluded records: 1
source race occurrences: 189,043
source columns: 37
admission predicate: rowid <> 1
```

The source remained read-only and its hash stayed unchanged across construction and validation.

---

## 3. Minimum stable core design result

The authorised minimum core now distinguishes:

- immutable source-version identity;
- source relation and ordered field declarations;
- one physical source record for every source `rowid`;
- retained excluded source evidence;
- deterministic source-record identity;
- deterministic source race occurrence identity;
- one runner participation per admitted source record;
- governance method and release identity;
- import-manifest identity and lifecycle state;
- validation evidence required before acceptance.

The Source Version 1 structural race key is exact raw:

```text
date + course + off
```

Race sequences are assigned by ascending minimum supporting source `rowid`. Runner identity remains tied to exact physical source lineage rather than horse label, runner number or supplied `race_id`.

---

## 4. Physical architecture result

SQLite schema version 1 implements:

- complete raw preservation;
- STRICT governed tables where appropriate;
- deterministic textual identifiers;
- foreign keys and uniqueness constraints;
- governance compatibility triggers;
- release-state transition controls;
- schema inventory checks;
- SQLite application and user-version headers;
- durable candidate construction;
- refusal to overwrite existing outputs;
- deletion of candidate and journal/WAL/SHM sidecars after failure.

The builder copied the independently validated complete raw mirror and added the minimum race and runner core without modifying the source or raw-mirror candidate.

---

## 5. Complete candidate build evidence

Command:

```bash
python scripts/build_minimum_core_candidate.py
```

Generated candidate:

```text
path: data/processed/database/candidates/raceform_v1_minimum_core_candidate.sqlite3
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
size: 1,730,048,000 bytes
manifest code: imp:20260806T110355286543Z:989756fa
database release code: db:20260806T110355286543Z:c427ca06
manifest status: built
release accepted: false
```

Population and performance:

```text
physical raw records: 1,851,286
admitted raw records: 1,851,285
retained excluded records: 1
race occurrences: 189,043
runner participations: 1,851,285
race batches: 38
runner batches: 371
batch size: 5,000
copy elapsed: 4.274955792003311 seconds
core population elapsed: 36.818536445032805 seconds
complete build elapsed: 76.16271843307186 seconds
core rows per second: 55,415.78229341218
```

Builder persisted readback compared all 189,043 races and 1,851,285 runner participations. `PRAGMA quick_check` returned `ok`; `PRAGMA foreign_key_check` returned zero rows.

---

## 6. Independent source-wide validation evidence

Command:

```bash
python scripts/validate_minimum_core_candidate.py
```

The independent validator was bound to the exact source, raw-mirror and candidate hashes. It reopened all artifacts read-only and did not trust builder counters.

Observed reconciliation:

```text
raw records compared: 1,851,286
raw values compared: 68,497,582
SQLite storage classes compared: 68,497,582
stored fingerprints compared: 1,851,286
recomputed fingerprints compared: 1,851,286
source-record codes compared: 1,851,286
structural statuses compared: 1,851,286
race codes compared: 189,043
race groupings compared: 189,043
race runner counts compared: 189,043
runner codes compared: 1,851,285
runner lineage relationships compared: 1,851,285
metadata rows compared: 41
validation elapsed: 199.25864554394502 seconds
rows per second: 9,290.86913617363
```

It also proved:

- exact schema inventory;
- source metadata reconciliation;
- governance reconciliation;
- import-manifest reconciliation;
- four builder validation-result rows;
- no release-accepted manifest;
- SQLite application and schema versions;
- `quick_check = ok`;
- zero foreign-key failures;
- unchanged source, raw-mirror and candidate hashes.

---

## 7. Focused automated gate

The final bounded database gate covered schema creation and review, identifiers, fingerprints, source identity, raw-mirror prototype and complete candidate, core-structure prototype, both independent validators and the complete minimum-core builder.

Result:

```text
72 passed in 14.54s
```

This was intentionally a database-focused gate rather than the complete repository test suite or every project validator. Those broader gates remain reserved for the appropriate series or release-acceptance boundary.

---

## 8. Audit classification

| Unit | Classification | Evidence |
|---|---|---|
| Source identity gate | **Fully closed** | Exact accepted file hash and baseline enforced before construction. |
| Complete raw mirror | **Fully closed as disposable candidate** | Complete build, persisted checks and independent 68.5-million-value reconciliation. |
| Minimum stable core design | **Fully closed for authorised structural scope** | Entity, key, lineage, governance and manifest contracts implemented and tested. |
| Three-race structural rehearsal | **Fully closed** | Real-data prototype independently validated before source-wide construction. |
| Complete minimum-core builder | **Fully closed as disposable candidate builder** | Full population, durable cleanup, manifest and persisted readback. |
| Complete minimum-core validator | **Fully closed** | Separate source-wide reconstruction and corruption tests. |
| Database release acceptance | **Not started / separately gated** | Candidate remains `built`; no promotion or active-release replacement. |
| Governed analytical-field integration | **Future bounded work** | Minimum core deliberately contains structural lineage only. |

---

## 9. Remaining limits

The completed evidence does not establish:

- an accepted live database release;
- active-release discovery or replacement;
- atomic promotion into a production location;
- rollback against an existing accepted database;
- prior-release preservation under a real replacement scenario;
- project-wide acceptance evidence stored inside the candidate;
- governed field-level analytical tables;
- identity-aware horse, participant or ownership analytical structures;
- complete repository and all-validator release gates at a final acceptance boundary.

The candidate is an ignored generated artifact and may be deleted and reproduced from the immutable source and committed code.

---

## 10. Next bounded action

Define the release-acceptance and promotion contract before changing the candidate manifest or installing an active database.

That contract must explicitly govern:

- required project-acceptance evidence;
- candidate-to-accepted state transition;
- active database path and naming;
- atomic promotion or replacement;
- preservation of a prior accepted release;
- rollback after failed promotion;
- independent post-promotion validation;
- final complete test and validator gates;
- explicit user review before promotion, branch movement or merge.

No implementation should mark this candidate `release_accepted` merely because its build and independent validation passed.
