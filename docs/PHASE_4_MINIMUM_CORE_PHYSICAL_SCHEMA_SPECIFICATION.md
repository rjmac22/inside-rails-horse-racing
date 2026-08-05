# Phase 4 Minimum-Core Physical Schema Specification

## Status

**Accepted physical schema contract for the authorised minimum stable core.**

Accepted on 5 August 2026.

This specification is governed by:

- `docs/PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`;
- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

It defines the exact first-release physical boundary before executable DDL or database-builder code is written.

It authorises implementation of the tables, constraints, indexes, triggers, views and external release manifests defined here. It does not authorise any governed field extension, provisional horse or participant identity, meeting, race-series, weather, sectional, betting-feed or analytical structure.

The governing rule is:

> The first SQLite release preserves the exact source, reconstructs only the accepted Source Version 1 race and runner structure, and records enough build and validation evidence to reproduce and audit the release.

---

## 1. Database-level contract

### 1.1 Engine and minimum version

The first release uses SQLite.

The implementation must require SQLite 3.37.0 or later because the structural tables use `STRICT` mode and the `ANY` type.

A builder must stop before creating a candidate when the runtime SQLite version is below the supported minimum.

### 1.2 One immutable file per release

One accepted database release is one complete SQLite file containing all authorised source, core, governance and import-evidence tables.

The original `raceform.db` remains separate, immutable and read-only.

No accepted database release may be modified in place after its final file hash is calculated.

### 1.3 SQLite header values

The first schema version must set:

```text
PRAGMA application_id = 1230130259;  -- hexadecimal 0x49524C53, ASCII-like marker IRLS
PRAGMA user_version = 1;
```

The independent validator must check both values.

### 1.4 Required connection settings

Every builder and validator connection must execute and verify:

```text
PRAGMA foreign_keys = ON;
PRAGMA trusted_schema = OFF;
```

The builder must use a single-file journal lifecycle. The first implementation should use `journal_mode=DELETE` rather than retaining WAL sidecar files in an accepted release.

The builder must use durable transaction settings, with `synchronous=FULL` unless a separately measured and documented decision changes it.

Normal consumer connections resolved through the active-release manifest must additionally set:

```text
PRAGMA query_only = ON;
```

Direct write access to an accepted release is prohibited.

### 1.5 Integrity checks before release acceptance

The complete persisted candidate must pass:

- `PRAGMA quick_check` returning exactly `ok`, or the stronger `integrity_check` where selected by the implementation plan;
- `PRAGMA foreign_key_check` returning zero rows;
- the independent project source-wide database validator;
- persisted readback and manifest reconciliation.

---

## 2. Naming and data-type conventions

### 2.1 Logical prefixes

- `source_*` — immutable source metadata and raw evidence;
- `core_*` — Source Version 1 race occurrences and runner participations;
- `governance_*` — structural methods, releases and evidence references;
- `import_*` — build manifests and validation results;
- `view_*` — documented evidence and structural read interfaces.

No `analysis_*` object is authorised in the first release.

### 2.2 Primary keys

Every physical entity table uses an explicitly populated `INTEGER PRIMARY KEY`.

`AUTOINCREMENT` is prohibited.

Internal integer keys are scoped to one built database release and are not stable external references.

### 2.3 Stable textual codes

Stable textual codes are stored as `TEXT NOT NULL UNIQUE`.

The builder must generate them using the algorithms in Section 4 and the independent validator must recompute them.

### 2.4 Hashes

SHA-256 values are stored internally as 32-byte `BLOB` values with:

```text
CHECK(typeof(value) = 'blob' AND length(value) = 32)
```

Views or reports may expose lowercase hexadecimal with `lower(hex(value))`.

### 2.5 Booleans

Boolean states are stored as `INTEGER NOT NULL` with:

```text
CHECK(value IN (0, 1))
```

### 2.6 UTC timestamps

Timestamps are stored as UTC ISO-8601 text in the form:

```text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

Application code must validate and normalise timestamps before insertion. Database checks must at least require non-empty text ending in `Z`.

### 2.7 Foreign-key actions

All stable-core foreign keys use:

```text
ON UPDATE RESTRICT ON DELETE RESTRICT
```

No cascade delete is permitted in immutable evidence or accepted release data.

### 2.8 `STRICT` and raw-table exception

Metadata, core, governance and import tables are `STRICT`.

`source_raceform_v1_record` is deliberately not `STRICT`. Its 37 raw source columns have **no declared type**, giving them SQLite BLOB affinity and preventing destination-column affinity from coercing valid source storage classes.

The raw table's metadata columns retain explicit declared types and constraints.

---

## 3. Authorised table inventory

The first release contains exactly these twelve physical tables:

1. `source_provider`
2. `source_product`
3. `source_version`
4. `source_relation`
5. `source_relation_field`
6. `source_raceform_v1_record`
7. `governance_method`
8. `governance_release`
9. `governance_release_evidence`
10. `core_source_race_occurrence`
11. `core_runner_participation`
12. `import_manifest`
13. `import_validation_result`

The numbered list contains thirteen tables; the authoritative count is therefore **thirteen**. This explicit correction is intentional and prevents a stale twelve-table count from entering implementation.

No additional physical table may be introduced without either:

- a correction to this specification for an omitted requirement already inside the authorised core; or
- a separately accepted evidence-led extension brief.

---

## 4. Identifier formats and canonical ordering

### 4.1 Controlled metadata codes

Provider and product codes are controlled, immutable project identifiers chosen once in the seed metadata.

Initial intended namespaces are:

```text
provider:<stable-provider-slug>
product:<stable-product-slug>
```

The label may later change without changing the code.

### 4.2 Source-version code

```text
sv:<first-24-lowercase-hex-characters-of-full-source-file-sha256>
```

The complete 32-byte hash remains stored separately. A code collision on the 24-character prefix must fail closed and require a longer code before admission.

### 4.3 Source-relation code

```text
rel:<source-version-hash-prefix>:<relation-slug>
```

For the first source relation, the relation slug is `data`.

### 4.4 Source-record code

```text
rec:<source-version-hash-prefix>:data:<source-rowid-zero-padded-to-10-digits>
```

The original source `rowid` remains a separate integer attribute.

### 4.5 Source-race-occurrence code

```text
race:<source-version-hash-prefix>:<race-sequence-zero-padded-to-9-digits>
```

Race sequence is assigned by ascending minimum supporting admitted source `rowid` for each accepted `date + course + off` group.

This ordering is deterministic within one exact source version and avoids depending on locale-sensitive text ordering.

### 4.6 Runner-participation code

```text
run:<source-version-hash-prefix>:data:<source-rowid-zero-padded-to-10-digits>
```

The runner code is in a separate namespace from the source-record code even though Source Version 1 has one runner participation per admitted source record.

### 4.7 Governance codes

Governance methods and releases use controlled, versioned codes:

```text
gm:<method-slug>:v<positive-integer>
gr:<source-version-hash-prefix>:<release-slug>:v<positive-integer>
```

### 4.8 Build and database-release codes

A build attempt is an event, not a logical source entity. It must not reuse a deterministic core-entity code.

Build and database-release codes therefore use a UTC timestamp and random suffix generated before the build starts:

```text
imp:<YYYYMMDDTHHMMSSffffffZ>:<8-lowercase-hex-random-characters>
db:<YYYYMMDDTHHMMSSffffffZ>:<8-lowercase-hex-random-characters>
```

A repeated clean build has different event codes but must reproduce the same logical source, race and runner codes.

### 4.9 Canonical integer-key insertion order

The builder explicitly inserts deterministic integer primary keys in these orders:

- provider and product: seed-manifest order;
- source version: source-version-code order;
- source relation: source-relation-code order;
- source relation fields: relation code then ordinal position;
- source records: relation code then source `rowid`;
- governance method and release: textual code order;
- race occurrences: race sequence defined in 4.5;
- runner participations: supporting source `rowid` ascending;
- governance evidence: release code, evidence type, evidence reference;
- validation results: validation stage, validator name, validator version.

Import-event integer keys need only be unique inside the release because the stable import code is the audit reference.

---

## 5. Source metadata tables

## 5.1 `source_provider`

**Grain:** one admitted source provider.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_provider_id` | INTEGER | no | Primary key; explicitly populated. |
| `source_provider_code` | TEXT | no | Unique controlled project code. |
| `provider_label` | TEXT | no | Governed display label. |
| `provenance_note` | TEXT | no | Acquisition and role uncertainty note. |
| `created_at_utc` | TEXT | no | Governance metadata creation timestamp. |

Additional checks:

- code, label and provenance note must not be empty;
- table is `STRICT`.

No provider-role taxonomy is included.

## 5.2 `source_product`

**Grain:** one continuing source product or dataset family.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_product_id` | INTEGER | no | Primary key. |
| `source_product_code` | TEXT | no | Unique controlled code. |
| `source_provider_id` | INTEGER | no | FK to `source_provider`. |
| `product_label` | TEXT | no | Governed product label. |
| `product_description` | TEXT | no | Bounded description of the admitted product. |
| `acquisition_usage_note` | TEXT | no | Current acquisition and usage context. |
| `created_at_utc` | TEXT | no | Metadata creation timestamp. |

Additional constraints:

- `UNIQUE(source_provider_id, source_product_code)`;
- table is `STRICT`.

## 5.3 `source_version`

**Grain:** one exact immutable source-file delivery.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_version_id` | INTEGER | no | Primary key. |
| `source_version_code` | TEXT | no | Unique deterministic code. |
| `source_product_id` | INTEGER | no | FK to `source_product`. |
| `original_filename` | TEXT | no | Original supplied filename. |
| `acquisition_description` | TEXT | no | Exact acquisition or receipt description. |
| `file_sha256` | BLOB | no | Unique 32-byte complete-file SHA-256. |
| `file_size_bytes` | INTEGER | no | `CHECK(file_size_bytes > 0)`. |
| `received_date` | TEXT | yes | Calendar date where known. |
| `source_schema_sha256` | BLOB | no | 32-byte canonical source-schema signature. |
| `physical_record_count` | INTEGER | no | First baseline: 1,851,286. |
| `admitted_record_count` | INTEGER | no | First baseline: 1,851,285. |
| `excluded_record_count` | INTEGER | no | First baseline: 1. |
| `admission_predicate` | TEXT | no | Exact governed predicate `rowid <> 1`. |
| `minimum_source_date` | TEXT | no | `2015-01-01`. |
| `maximum_source_date` | TEXT | no | `2026-05-27`. |
| `source_integrity_result` | TEXT | no | Must equal `ok` for accepted Source Version 1. |
| `version_status` | TEXT | no | First allowed value: `accepted_exact_source`. |
| `notes` | TEXT | no | Includes retained `rowid = 1` treatment. |
| `created_at_utc` | TEXT | no | Metadata creation timestamp. |

Checks:

- both SHA values are 32-byte blobs;
- counts are non-negative;
- `physical_record_count = admitted_record_count + excluded_record_count`;
- first importer independently enforces the exact accepted baseline;
- `file_sha256` is unique;
- table is `STRICT`.

A later delivery is a new source version even if the filename is unchanged.

## 5.4 `source_relation`

**Grain:** one physical relation within one source version.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_relation_id` | INTEGER | no | Primary key. |
| `source_relation_code` | TEXT | no | Unique deterministic code. |
| `source_version_id` | INTEGER | no | FK to `source_version`. |
| `relation_name` | TEXT | no | Exact raw relation name; first value `data`. |
| `relation_schema_sha256` | BLOB | no | 32-byte ordered-field signature. |
| `column_count` | INTEGER | no | First value exactly 37. |
| `physical_record_count` | INTEGER | no | First value 1,851,286. |
| `admitted_record_count` | INTEGER | no | First value 1,851,285. |
| `admission_predicate` | TEXT | no | Exact relation predicate. |

Constraints:

- `UNIQUE(source_version_id, relation_name)`;
- `UNIQUE(source_relation_id, source_version_id)` to support composite lineage FKs;
- counts are positive and admitted count cannot exceed physical count;
- table is `STRICT`.

## 5.5 `source_relation_field`

**Grain:** one declared source field at one ordinal position in one source relation.

This is schema metadata, not a row-per-value source-claim system.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_relation_field_id` | INTEGER | no | Primary key. |
| `source_relation_id` | INTEGER | no | FK to `source_relation`. |
| `ordinal_position` | INTEGER | no | Zero-based source ordinal, 0 through 36. |
| `field_name` | TEXT | no | Exact SQLite source column name. |
| `declared_type` | TEXT | no | Exact declared source type. |
| `source_not_null` | INTEGER | no | Source `PRAGMA table_info` flag, boolean. |
| `source_default_sql` | TEXT | yes | Exact default SQL where present. |
| `source_primary_key_ordinal` | INTEGER | no | Source PK ordinal; zero for all current fields. |

Constraints:

- `UNIQUE(source_relation_id, ordinal_position)`;
- `UNIQUE(source_relation_id, field_name)`;
- ordinal must be non-negative;
- boolean checks;
- table is `STRICT`.

The source relation schema signature is SHA-256 over a canonical encoding of these rows in ordinal order.

---

## 6. Immutable raw Source Version 1 table

## 6.1 `source_raceform_v1_record`

**Grain:** one physical row exactly as stored in the Source Version 1 `data` relation.

The table contains all 1,851,286 physical rows.

### Metadata columns

| Column | Declared type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_record_id` | INTEGER | no | Primary key; independent project technical identity. |
| `source_record_code` | TEXT | no | Unique deterministic audit code. |
| `source_version_id` | INTEGER | no | Exact source version. |
| `source_relation_id` | INTEGER | no | Exact source relation. |
| `source_rowid` | INTEGER | no | Original SQLite `rowid`; positive. |
| `structural_status` | TEXT | no | `admitted_runner_record` or `retained_excluded_record`. |
| `exclusion_reason` | TEXT | yes | Required only for the retained excluded record. |
| `row_sha256` | BLOB | no | 32-byte typed-value fingerprint of the 37 raw fields. |

Lineage constraints:

- `UNIQUE(source_record_code)`;
- `UNIQUE(source_version_id, source_relation_id, source_rowid)`;
- composite FK `(source_relation_id, source_version_id)` to `source_relation`;
- `UNIQUE(source_record_id, structural_status)` supports admitted-record enforcement;
- `CHECK(source_rowid > 0)`;
- status domain check;
- source-specific status check:
  - `source_rowid = 1` requires `retained_excluded_record` and a non-empty exclusion reason;
  - every other row requires `admitted_runner_record` and a null exclusion reason.

### Exact 37 raw columns

The raw columns are declared with **no type name** in the governed mirror.

Their exact source order and source-declared types are:

| Ordinal | Raw column | Source declared type |
|---:|---|---|
| 0 | `date` | NUMERIC |
| 1 | `course` | TEXT |
| 2 | `race_id` | INTEGER |
| 3 | `off` | TEXT |
| 4 | `race_name` | TEXT |
| 5 | `type` | TEXT |
| 6 | `class` | TEXT |
| 7 | `pattern` | TEXT |
| 8 | `rating_band` | TEXT |
| 9 | `age_band` | TEXT |
| 10 | `sex_rest` | TEXT |
| 11 | `dist` | TEXT |
| 12 | `going` | TEXT |
| 13 | `ran` | INTEGER |
| 14 | `num` | INTEGER |
| 15 | `pos` | INTEGER |
| 16 | `draw` | INTEGER |
| 17 | `ovr_btn` | NUMERIC |
| 18 | `btn` | NUMERIC |
| 19 | `horse` | TEXT |
| 20 | `age` | INTEGER |
| 21 | `sex` | TEXT |
| 22 | `wgt` | TEXT |
| 23 | `hg` | TEXT |
| 24 | `time` | TEXT |
| 25 | `sp` | TEXT |
| 26 | `jockey` | TEXT |
| 27 | `trainer` | TEXT |
| 28 | `prize` | INTEGER |
| 29 | `or` | INTEGER |
| 30 | `rpr` | INTEGER |
| 31 | `ts` | INTEGER |
| 32 | `sire` | TEXT |
| 33 | `dam` | TEXT |
| 34 | `damsire` | TEXT |
| 35 | `owner` | TEXT |
| 36 | `comment` | TEXT |

The executable DDL must quote every raw source column name. In particular, `or` must never be emitted unquoted.

The source-declared type metadata belongs in `source_relation_field`; it must not be applied as destination affinity to the raw mirror columns.

### Raw-value requirements

For every physical row and raw field, the builder and independent validator must compare:

- logical value equality;
- SQLite `typeof()` equality;
- null versus empty-text distinction;
- fixed ordinal placement;
- persisted readback equality;
- row SHA-256 equality.

No trimming, normalisation, parsing, replacement or supplementation occurs in this table.

### Raw-table indexes

Required:

```text
UNIQUE(source_version_id, source_relation_id, source_rowid)
INDEX(structural_status)
INDEX(source_version_id, source_relation_id, date, course, off)
```

The race-grouping index should be partial to admitted rows where supported cleanly by the executable DDL:

```text
WHERE structural_status = 'admitted_runner_record'
```

The candidate uniqueness of race group plus raw horse label remains an independently reconstructed validation invariant rather than a raw-table uniqueness constraint. The raw mirror must be capable of preserving a changed or invalid candidate source completely before that candidate fails admission.

---

## 7. Row-fingerprint contract

The raw row fingerprint uses SHA-256 over a canonical binary message.

### 7.1 Domain prefix

The message begins with the fixed ASCII domain separator:

```text
inside-rails:raceform-v1-row:v1\0
```

### 7.2 Per-field encoding

Each of the 37 fields is appended in ordinal order as:

1. unsigned 16-bit big-endian ordinal;
2. one-byte storage-class marker;
3. unsigned 64-bit big-endian byte length;
4. canonical value bytes.

Storage-class markers:

- `0x00` — NULL;
- `0x01` — INTEGER;
- `0x02` — REAL;
- `0x03` — TEXT;
- `0x04` — BLOB.

Canonical values:

- NULL: zero length and no value bytes;
- INTEGER: signed 64-bit big-endian two's-complement bytes;
- REAL: IEEE-754 binary64 big-endian bytes, retaining negative zero and infinities where present;
- TEXT: canonical UTF-8 encoding of the SQLite logical text value;
- BLOB: exact blob bytes.

An unsupported Python or SQLite value type must fail closed.

The full-file source hash remains separate from row fingerprints.

---

## 8. Governance tables

## 8.1 `governance_method`

**Grain:** one versioned structural derivation method.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `governance_method_id` | INTEGER | no | Primary key. |
| `governance_method_code` | TEXT | no | Unique controlled versioned code. |
| `method_name` | TEXT | no | Reader-facing name. |
| `method_version` | INTEGER | no | Positive integer. |
| `repository_commit` | TEXT | no | Exact lowercase 40-character Git commit. |
| `method_description` | TEXT | no | Bounded structural method description. |
| `created_at_utc` | TEXT | no | Creation timestamp. |

Checks:

- positive method version;
- valid non-empty strings;
- repository commit length and lowercase hexadecimal form;
- table is `STRICT`.

## 8.2 `governance_release`

**Grain:** one accepted structural-governance release for one exact source version.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `governance_release_id` | INTEGER | no | Primary key. |
| `governance_release_code` | TEXT | no | Unique controlled release code. |
| `source_version_id` | INTEGER | no | FK to exact source version. |
| `governance_method_id` | INTEGER | no | FK to method. |
| `release_status` | TEXT | no | `accepted` or `superseded`. |
| `accepted_date` | TEXT | no | Calendar acceptance date. |
| `repository_commit` | TEXT | no | Exact accepted repository commit. |
| `population_predicate` | TEXT | no | Exact `rowid <> 1` for first release. |
| `release_description` | TEXT | no | Structural scope and limitations. |
| `superseded_by_release_id` | INTEGER | yes | Self-FK when superseded. |
| `created_at_utc` | TEXT | no | Metadata creation timestamp. |

Checks:

- status domain;
- accepted releases have null `superseded_by_release_id`;
- superseded releases require a different successor;
- valid commit form;
- `UNIQUE(source_version_id, governance_release_code)`;
- table is `STRICT`.

Only one release may be active for the same structural release family and source version. The first implementation enforces this through builder validation and a suitable partial unique index where the final family representation supports it.

## 8.3 `governance_release_evidence`

**Grain:** one structural evidence reference supporting one governance release.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `governance_release_evidence_id` | INTEGER | no | Primary key. |
| `governance_release_id` | INTEGER | no | FK to release. |
| `evidence_type` | TEXT | no | `document`, `repository_artifact`, `validator`, or `governed_output`. |
| `evidence_reference` | TEXT | no | Repository path, validator name or durable reference. |
| `evidence_sha256` | BLOB | yes | 32-byte hash where a fixed artifact is hashed. |
| `evidence_description` | TEXT | no | What the item proves. |

Constraints:

- evidence-type domain;
- `UNIQUE(governance_release_id, evidence_type, evidence_reference)`;
- optional hash shape check;
- table is `STRICT`.

This table records structural evidence only. It is not a universal source-claim or correction framework.

---

## 9. Structural core tables

## 9.1 `core_source_race_occurrence`

**Grain:** one Source Version 1 race occurrence reconstructed from admitted records.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `source_race_occurrence_id` | INTEGER | no | Primary key. |
| `source_race_occurrence_code` | TEXT | no | Unique deterministic audit code. |
| `source_version_id` | INTEGER | no | FK to exact source version. |
| `raw_date` | ANY | no | Exact raw grouping value. |
| `raw_course` | ANY | no | Exact raw grouping value. |
| `raw_off` | ANY | no | Exact raw grouping value. |
| `admitted_runner_count` | INTEGER | no | Positive derived structural count. |
| `governance_release_id` | INTEGER | no | FK to accepted structural release. |

Constraints:

- `UNIQUE(source_version_id, raw_date, raw_course, raw_off)`;
- `CHECK(admitted_runner_count > 0)`;
- table is `STRICT`;
- `ANY` is deliberate: it preserves exact SQLite value and storage class without coercion.

A trigger must reject insertion or update where the governance release belongs to a different source version.

Exactly 189,043 rows are required for the first accepted release.

The supplied raw `race_id`, race name, distance, class and other fields remain only on supporting source records.

## 9.2 `core_runner_participation`

**Grain:** one governed runner participation supported by one admitted physical source record in one Source Version 1 race occurrence.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `runner_participation_id` | INTEGER | no | Primary key. |
| `runner_participation_code` | TEXT | no | Unique deterministic audit code. |
| `source_race_occurrence_id` | INTEGER | no | FK to `core_source_race_occurrence`. |
| `source_record_id` | INTEGER | no | Unique FK to supporting raw source record. |
| `source_record_status` | TEXT | no | Constant `admitted_runner_record`, used in composite FK enforcement. |
| `governance_release_id` | INTEGER | no | FK to structural governance release. |

Constraints:

- `UNIQUE(source_record_id)`;
- `UNIQUE(runner_participation_code)`;
- `CHECK(source_record_status = 'admitted_runner_record')`;
- composite FK `(source_record_id, source_record_status)` to the raw record's `(source_record_id, structural_status)`;
- table is `STRICT`.

A trigger must reject insertion or update unless all of the following are true:

1. the source record is admitted;
2. the source record and race occurrence have the same source version;
3. source raw `date`, `course` and `off` are identical by SQLite `IS` semantics to the race's stored grouping values;
4. the runner and race refer to the same governance release;
5. the governance release belongs to that source version.

Exactly 1,851,285 rows are required for the first accepted release.

No horse, participant, result, weight, price, rating or runner-number column is copied into this table.

---

## 10. Import and validation tables

## 10.1 `import_manifest`

**Grain:** one complete candidate build attempt represented inside its resulting candidate database.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `import_manifest_id` | INTEGER | no | Primary key. |
| `import_manifest_code` | TEXT | no | Unique event code. |
| `database_release_code` | TEXT | no | Unique immutable release code if accepted. |
| `source_version_id` | INTEGER | no | FK to exact source version. |
| `governance_release_id` | INTEGER | no | FK to structural release. |
| `schema_version` | INTEGER | no | First value 1. |
| `code_commit` | TEXT | no | Exact builder Git commit. |
| `reference_data_commit` | TEXT | no | Exact reference-data Git commit; may equal code commit. |
| `build_command` | TEXT | no | Reproducible entry point and arguments. |
| `build_started_at_utc` | TEXT | no | Build start timestamp. |
| `build_completed_at_utc` | TEXT | yes | Set before final acceptance. |
| `physical_record_count` | INTEGER | no | Built count. |
| `admitted_record_count` | INTEGER | no | Built count. |
| `excluded_record_count` | INTEGER | no | Built count. |
| `race_occurrence_count` | INTEGER | no | Built count. |
| `runner_participation_count` | INTEGER | no | Built count. |
| `persisted_readback_passed` | INTEGER | no | Boolean. |
| `sqlite_integrity_passed` | INTEGER | no | Boolean. |
| `foreign_key_check_passed` | INTEGER | no | Boolean. |
| `post_load_validation_passed` | INTEGER | no | Boolean. |
| `prior_database_release_code` | TEXT | yes | Previous active release where one exists. |
| `prior_release_preserved` | INTEGER | no | Boolean. |
| `build_status` | TEXT | no | Domain below. |
| `failure_reason` | TEXT | yes | Required for failed or rolled-back candidates. |

Allowed `build_status` values:

- `building`;
- `built`;
- `validated`;
- `release_accepted`;
- `failed`;
- `rolled_back`.

Checks:

- all counts non-negative;
- physical count equals admitted plus excluded;
- boolean domains;
- accepted status requires completion timestamp, all four validation booleans true, prior release preservation true, and null failure reason;
- failed or rolled-back status requires a non-empty failure reason;
- commit fields are lowercase 40-character hexadecimal;
- table is `STRICT`.

The final database-file SHA-256 is **not stored inside the database**. Storing a file's final digest inside itself would create a recursive hash dependency. The final file hash belongs in the immutable external release manifest described in Section 13.

The database file records that it passed the release gate; the external active manifest records whether that immutable release is currently active.

## 10.2 `import_validation_result`

**Grain:** one named validation execution for one import manifest.

| Column | Type | Null | Constraint / meaning |
|---|---|---:|---|
| `import_validation_result_id` | INTEGER | no | Primary key. |
| `import_manifest_id` | INTEGER | no | FK to `import_manifest`. |
| `validation_stage` | TEXT | no | Domain below. |
| `validator_name` | TEXT | no | Stable test, validator or check name. |
| `validator_version` | TEXT | no | Commit, version or implementation identifier. |
| `required_for_acceptance` | INTEGER | no | Boolean. |
| `outcome` | TEXT | no | `passed` or `failed`. |
| `executed_at_utc` | TEXT | no | Execution timestamp. |
| `command` | TEXT | no | Exact or reproducible command. |
| `result_summary` | TEXT | no | Concise result and counts. |
| `details_artifact_path` | TEXT | yes | Repository or generated-artifact reference. |

Allowed stages:

- `focused_unit_tests`;
- `source_wide_validation`;
- `persisted_readback`;
- `sqlite_integrity`;
- `foreign_key_validation`;
- `post_load_validation`;
- `project_acceptance_gate`.

Constraints:

- stage and outcome domains;
- boolean check;
- `UNIQUE(import_manifest_id, validation_stage, validator_name, validator_version)`;
- table is `STRICT`.

An accepted release may contain failed results only when `required_for_acceptance = 0` and the failure is explicitly explained. Every required result must be present and passed.

---

## 11. Required cross-table triggers

Executable DDL must define insertion and update triggers for conditions SQLite cannot express through ordinary checks or foreign keys alone.

### 11.1 Race-governance compatibility

Reject a `core_source_race_occurrence` insert or update when its governance release references a different source version.

### 11.2 Runner structural compatibility

Reject a `core_runner_participation` insert or update when any condition in Section 9.2 is false.

### 11.3 Manifest-governance compatibility

Reject an `import_manifest` insert or update when its governance release belongs to a different source version.

### 11.4 Accepted-manifest completeness

Reject transition to `release_accepted` unless:

- required counts agree with `source_version` and the physical core tables;
- all required validation results are present and passed;
- no required failed result exists;
- the accepted structural counts equal the first baseline;
- the manifest's governance and source versions match.

The builder must not rely only on these triggers. The independent validator reconstructs the same rules separately.

### 11.5 Immutability boundary

The first release does not add triggers that permanently prevent candidate-build inserts or updates. Immutability is enforced operationally after release acceptance through:

- final database-file hashing;
- immutable release-path policy;
- consumer `query_only=ON`;
- file permissions where supported;
- active-manifest verification;
- independent hash checks.

---

## 12. Required indexes

Unique constraints create their ordinary backing indexes.

Additional required indexes are:

### Source evidence

- admitted/excluded status on `source_raceform_v1_record`;
- partial admitted race-group lookup on source version, relation, raw `date`, raw `course`, raw `off`;
- source-record row fingerprint where measured validation shows it is useful; this is optional initially because source-row lookup is already unique by locator.

### Core structure

- `core_source_race_occurrence(source_version_id, raw_date, raw_course, raw_off)` — unique;
- `core_runner_participation(source_race_occurrence_id)`;
- `core_runner_participation(governance_release_id)`;
- unique `core_runner_participation(source_record_id)`.

### Governance and import

- `governance_release(source_version_id, release_status)`;
- `governance_release_evidence(governance_release_id)`;
- `import_validation_result(import_manifest_id, validation_stage, outcome)`.

No index is authorised merely because a future analytical query might use it.

Additional indexes require measured query or validation evidence and must be documented.

---

## 13. External immutable release manifests

The SQLite file cannot safely contain its own final file SHA-256. Two external JSON manifests are therefore part of the physical release contract.

### 13.1 Immutable release manifest

Path pattern:

```text
data/processed/database/releases/inside_rails_<database_release_code>.manifest.json
```

Minimum fields:

```text
manifest_schema_version
database_release_code
database_relative_path
database_file_sha256_hex
database_file_size_bytes
sqlite_application_id
sqlite_user_version
source_version_code
source_file_sha256_hex
import_manifest_code
governance_release_code
code_commit
reference_data_commit
release_accepted_at_utc
physical_record_count
admitted_record_count
excluded_record_count
race_occurrence_count
runner_participation_count
required_validation_status
```

This file is written only after the database has been closed, hashed and moved to its immutable release path.

It is itself written atomically and then treated as immutable.

### 13.2 Active database manifest

Path:

```text
data/processed/database/active_database.json
```

Minimum fields:

```text
active_manifest_schema_version
database_release_code
database_relative_path
release_manifest_relative_path
database_file_sha256_hex
source_version_code
import_manifest_code
code_commit
activated_at_utc
post_load_validation_passed
```

Activation consists only of atomically replacing this small JSON file after verifying the immutable database and release manifest.

The active manifest is the only mutable release pointer.

### 13.3 Resolver obligations

One repository helper must:

1. read and validate `active_database.json`;
2. prevent path traversal and require a path beneath the releases directory;
3. read and reconcile the immutable release manifest;
4. verify database file existence, size and SHA-256;
5. open SQLite through a read-only URI;
6. enable and verify required PRAGMAs;
7. confirm application ID, schema version, release code and import manifest agreement;
8. return a query-only connection.

No notebook or application may hard-code an individual release filename.

---

## 14. First-release views

Views are read interfaces, not additional evidence.

The first release contains exactly these six views.

## 14.1 `view_source_record_lineage`

Exposes:

- provider, product, source-version and relation codes;
- source-record integer ID and code;
- original source `rowid`;
- structural status and exclusion reason;
- lowercase hexadecimal row fingerprint.

It includes both admitted and retained excluded records.

## 14.2 `view_source_raceform_v1_records`

Exposes all columns from `view_source_record_lineage` plus the exact 37 raw values.

It applies no population filter.

## 14.3 `view_core_source_race_occurrences`

Exposes:

- race integer ID and stable code;
- source-version code;
- exact raw date, course and off;
- admitted runner count;
- governance release and method codes.

It does not expose or infer meeting, real-world race or recurring-series identity.

## 14.4 `view_core_runner_participations`

Exposes:

- runner integer ID and stable code;
- race code;
- source-record code and source `rowid`;
- governance release code;
- source lineage;
- all 37 raw values through the one-to-one source-record relationship.

It contains exactly the admitted runner population and does not expose the retained excluded record as a runner.

## 14.5 `view_database_release_evidence`

Exposes this database file's:

- database release code;
- import manifest code and status;
- source and governance release codes;
- schema version and commits;
- build timestamps;
- structural counts;
- validation booleans;
- prior-release preservation evidence.

It deliberately does not claim that the file is currently active. Active status exists only in the external active manifest.

## 14.6 `view_import_validation_evidence`

Exposes every named validation result joined to its import and database-release codes.

No analytical convenience view is authorised.

---

## 15. Source-wide structural invariants

The accepted first database must satisfy all of the following simultaneously.

### 15.1 Physical source

- exactly 1,851,286 raw physical records;
- exactly 1,851,285 admitted raw records;
- exactly one retained excluded raw record;
- excluded record is exactly source `rowid = 1`;
- every source `rowid` is represented exactly once;
- all 37 raw values and `typeof()` results reconcile exactly.

### 15.2 Race occurrences

- exactly 189,043 race occurrences;
- each admitted source record belongs to exactly one race;
- every race has at least one runner;
- stored runner count equals actual linked runner count;
- race grouping is exactly source version plus raw `date + course + off`;
- no excluded source record participates.

### 15.3 Runner participations

- exactly 1,851,285 runner participations;
- one and only one runner per admitted source record;
- no runner for an excluded source record;
- every runner references exactly one race;
- source race plus raw horse label remains unique across the accepted population;
- zero orphan relationships.

### 15.4 Governance and import evidence

- every race and runner resolves to one accepted compatible structural governance release;
- exactly one accepted import manifest describes the immutable database release;
- every required validator is present and passed;
- all in-database counts match source, core and external release manifests;
- active-manifest values reconcile when the release is active.

---

## 16. Schema creation and migration rules

### 16.1 Executable schema location

The next implementation step should create a versioned SQL definition under a path such as:

```text
src/inside_rails/database/schema/v001_minimum_core.sql
```

The exact package path may follow established repository structure, but the schema version and purpose must remain explicit.

### 16.2 No in-place migration of accepted releases

An accepted SQLite release is never migrated in place.

A schema change creates:

1. a new schema version;
2. a complete new candidate database;
3. full source and post-load validation;
4. a new immutable release file and release manifest;
5. optional activation through the active manifest.

### 16.3 Schema changes inside the authorised core

A correction to table shape, constraint or index strategy requires:

- identified defect or measured requirement;
- specification update;
- compatibility analysis;
- focused schema tests;
- independent validator update;
- full candidate rebuild.

### 16.4 Domain extensions

A new racing concept cannot enter through an ordinary schema migration. It requires its own evidence-led extension brief before schema design.

---

## 17. Required focused tests before full build

Before loading 1.85 million rows, implementation must pass small-fixture tests for:

- SQLite minimum-version rejection;
- application ID and user version;
- foreign-key enforcement on every connection;
- `STRICT ANY` preservation of null, integer, real, text and blob values;
- untyped raw-column preservation without affinity coercion;
- exact quoted handling of the raw `or` field;
- row-fingerprint canonical encoding, including null, empty text, negative integer, negative zero, real, Unicode text and blob;
- deterministic source-record, race and runner codes;
- race ordering by minimum source `rowid`;
- retained excluded-record checks;
- race-governance and runner compatibility triggers;
- accepted-manifest completeness trigger;
- release-manifest and active-manifest atomic writes;
- resolver path and hash verification;
- failed candidate leaving the prior active manifest untouched.

A representative source prototype must include fields with mixed observed SQLite storage classes. Failure to preserve either value or `typeof()` stops the full build.

---

## 18. Explicit exclusions

This schema contains no physical table or view for:

- governed result, beaten distance, parsed distance, weight, price, rating, prize money, equipment or comments;
- race-time reconstruction or timezone;
- horse, jockey, trainer or ownership identity;
- meeting or session identity;
- provider-independent race identity;
- recurring race series;
- racecourse venue, site or configuration history;
- weather, irrigation or drainage;
- sectional timing or tracking;
- betting-market snapshots or exchange data;
- analytical aggregates, features or models;
- future sources not yet inspected.

Their raw Source Version 1 values remain available where present. Their governed outputs remain external until separately authorised.

---

## 19. Implementation stop conditions

DDL or builder work must stop and return to review when:

- the exact 37-field names, order or declared source types differ;
- raw values or storage classes cannot be copied exactly;
- runtime SQLite cannot support the required strict tables and `ANY` semantics;
- a required invariant cannot be expressed through constraint, trigger or independent validation;
- the design would require storing final database hash inside the database;
- the builder would modify an accepted database release;
- external manifest activation could leave a partial or mismatched state;
- any additional domain concept is needed to make the core function;
- the implementation begins copying descriptive raw fields into core tables for convenience;
- expected baseline counts need to be changed merely to pass.

---

## 20. Decision summary

The accepted physical contract is:

1. SQLite 3.37.0 or later, schema version 1.
2. Thirteen physical tables in one immutable release file.
3. `STRICT` metadata, core, governance and import tables.
4. One deliberately non-strict source-specific raw mirror with 37 untyped raw columns.
5. All 1,851,286 physical source rows retained, including excluded `rowid = 1`.
6. Exact raw value and SQLite storage-class reconciliation.
7. SHA-256 typed row fingerprints and a separate full source-file hash.
8. Exactly 189,043 Source Version 1 race occurrences.
9. Exactly 1,851,285 runner participations.
10. Integer internal keys and stored deterministic audit codes for logical entities.
11. Event-specific import and database-release codes for build attempts.
12. Explicit governance-method, release and evidence records.
13. In-database import and validation evidence without a recursive self-file hash.
14. Immutable external release manifests containing the final database-file hash.
15. One atomic active-release JSON pointer and one verified read-only resolver.
16. Six evidence and structural views only.
17. Cross-table triggers for source-version, governance, race and admitted-runner compatibility.
18. No in-place migration of accepted releases.
19. No unauthorised field, identity, enrichment or analytical structures.
20. Full independent source-wide validation before activation.

The next bounded step is executable schema DDL and focused schema tests—not the full 1.85-million-row build.
