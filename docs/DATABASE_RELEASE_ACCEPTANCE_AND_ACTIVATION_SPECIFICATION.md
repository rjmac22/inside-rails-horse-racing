# Database Release Acceptance and Activation Specification

## Status

**Accepted implementation contract on 7 August 2026.**

This specification defines how a completely built and independently validated SQLite candidate becomes:

1. an immutable accepted database release; and
2. optionally, the active database used by downstream consumers.

It is governed by:

- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`;
- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_LESSONS_LEARNED.md`.

The governing decision is:

> Preserve the tested candidate unchanged. Create a separate acceptance copy, verify and mark that copy accepted, place it at an immutable versioned release path, and make activation or rollback consist only of atomically replacing one small verified JSON pointer.

This specification authorises implementation and synthetic testing of that workflow. It does **not** itself promote, activate or mutate the real Source Version 1 candidate.

---

## 1. Plain-language outcome

The project will not overwrite the tested candidate and will not maintain one mutable database file.

Instead:

- the disposable candidate remains exactly as built, with `build_status = 'built'`;
- acceptance creates a separate database file;
- the accepted file contains the complete acceptance evidence and has `build_status = 'release_accepted'`;
- the accepted file is hashed after its final database mutation;
- the accepted file and its release manifest are never modified in place;
- a small `active_database.json` file says which accepted release downstream code should open;
- switching or rolling back means replacing only that pointer after verifying the target release.

The first accepted release has no earlier active release. Later accepted releases retain every earlier release file and manifest.

---

## 2. Separation of states

The implementation must keep these states distinct.

### 2.1 Disposable candidate

The candidate is generated under:

```text
data/processed/database/candidates/
```

It remains reproducible and disposable.

For the current Source Version 1 candidate:

```text
path: data/processed/database/candidates/raceform_v1_minimum_core_candidate.sqlite3
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
size: 1,730,048,000 bytes
build_status: built
release_accepted: false
```

The acceptance workflow must verify the candidate hash before and after processing and must never update this file.

### 2.2 Accepted immutable release

An accepted release is a separate complete SQLite file under:

```text
data/processed/database/releases/
```

It contains a single `import_manifest` row at `release_accepted`, all required validation evidence, and the exact accepted structural core.

No accepted release may be modified in place after its final SHA-256 is calculated.

### 2.3 Active release pointer

The active release is selected only through:

```text
data/processed/database/active_database.json
```

The active pointer is mutable. Accepted SQLite files and immutable release manifests are not.

A release may be accepted without being active. Acceptance and activation are separate commands and separate decisions.

---

## 3. Exact release paths

Database release codes contain colons and are audit identities, not portable filenames. Filesystem names must therefore use a deterministic safe slug.

For a database release code of:

```text
db:20260806T110355286543Z:c427ca06
```

the safe release slug is:

```text
db_20260806T110355286543Z_c427ca06
```

Only lowercase ASCII letters, digits and underscores are permitted in the slug.

Final paths are:

```text
data/processed/database/releases/inside_rails_<safe_release_slug>.sqlite3
data/processed/database/releases/inside_rails_<safe_release_slug>.manifest.json
```

Temporary acceptance artifacts must be created on the same filesystem under:

```text
data/processed/database/releases/.staging/
```

Example temporary paths:

```text
inside_rails_<safe_release_slug>.sqlite3.tmp
inside_rails_<safe_release_slug>.manifest.json.tmp
```

The implementation must refuse to overwrite any final release database, final release manifest or conflicting temporary artifact.

SQLite journal, WAL and shared-memory sidecars are prohibited beside candidates, staging files and accepted releases.

---

## 4. Required acceptance inputs

The release-acceptance command must receive or resolve explicitly:

- candidate database path;
- expected candidate SHA-256;
- exact 40-character code commit tested by the project gate;
- exact 40-character reference-data commit;
- final repository-gate evidence path;
- full-suite command and result summary;
- all-validator command or governed runner description and result summary;
- acceptance timestamp;
- releases directory.

For the first real Source Version 1 acceptance, the final project-gate evidence currently records:

```text
repository test suite: 354 passed in 18.28s
independent validators: ALL 31 VALIDATORS PASSED
final gate evidence: docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md
```

The implementation must not infer a passing result merely because the evidence document exists. The exact governed values passed to acceptance must be validated and recorded.

---

## 5. Required acceptance sequence

The real acceptance operation must execute in this order.

### Step 1 — Preflight

Before copying any bytes, the command must:

1. validate all arguments;
2. require a clean candidate with no SQLite sidecars;
3. verify the exact candidate SHA-256 and file size;
4. open the candidate read-only;
5. verify `PRAGMA application_id`, `PRAGMA user_version`, `PRAGMA quick_check` and `PRAGMA foreign_key_check`;
6. verify exactly one import manifest at `build_status = 'built'`;
7. verify zero manifests at `release_accepted`;
8. verify the expected database release code, source version, governance release and complete structural counts;
9. verify the four builder validation-result rows already present and passed;
10. verify that the final release and temporary paths do not exist.

Any difference stops the operation before a staging database is created.

### Step 2 — Durable copy to staging

The command must copy the complete candidate to a staging file without altering the source candidate.

The copy must:

- use bounded chunks;
- flush and `fsync` the staging file;
- verify copied byte count;
- verify that the staging copy initially has the same SHA-256 as the candidate;
- verify that the candidate hash remains unchanged.

A normal SQLite backup API is not sufficient as the sole copy proof because the acceptance boundary requires exact initial byte identity.

### Step 3 — Record project acceptance evidence

The staging copy may then be opened for the only authorised database mutation in the acceptance workflow.

Inside one `BEGIN IMMEDIATE` transaction, the implementation must:

1. enable and verify governed writable-connection PRAGMAs;
2. recheck that the manifest is still `built`;
3. insert the missing required acceptance results;
4. update the manifest from `built` to `validated`;
5. set prior-release fields correctly;
6. update the manifest from `validated` to `release_accepted`;
7. commit only if all schema checks and acceptance triggers pass.

The transaction must insert exactly these three additional required rows:

#### Focused/unit and complete repository tests

```text
validation_stage: focused_unit_tests
validator_name: complete-repository-test-suite
required_for_acceptance: 1
outcome: passed
```

The result summary must record the exact passing count and elapsed time.

#### Independent source-wide validation

```text
validation_stage: source_wide_validation
validator_name: complete-independent-validator-sweep
required_for_acceptance: 1
outcome: passed
```

The result summary must record the exact number of validators passed.

#### Final project acceptance gate

```text
validation_stage: project_acceptance_gate
validator_name: phase-4-final-repository-gate
required_for_acceptance: 1
outcome: passed
```

The details artifact must be:

```text
docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md
```

After insertion, the accepted copy must contain one passed required result for every required stage:

1. `focused_unit_tests`;
2. `source_wide_validation`;
3. `persisted_readback`;
4. `sqlite_integrity`;
5. `foreign_key_validation`;
6. `post_load_validation`;
7. `project_acceptance_gate`.

No required failed result may exist.

### Step 4 — Prior-release preservation

Before setting `release_accepted`, the command must inspect the current active pointer.

For the first release:

```text
prior_database_release_code: null
prior_release_preserved: true
```

This means there was no prior active release to preserve.

For a later release:

- the current active pointer must be valid;
- its accepted database and immutable manifest must verify successfully;
- `prior_database_release_code` must equal that active release code;
- the prior database and manifest must remain present and unchanged;
- `prior_release_preserved` may be set true only after those checks pass.

Acceptance must not modify the active pointer.

### Step 5 — Close and independently verify the accepted staging copy

After the transaction commits, the connection must close completely.

A separate read-only accepted-release validator must then verify from persisted state:

- no SQLite sidecars;
- exactly one `release_accepted` import manifest;
- zero `building`, `built` or `validated` manifests;
- exact source, race and runner populations;
- all seven required validation stages present and passed;
- no required failed result;
- manifest commit and evidence agreement;
- prior-release fields;
- SQLite application ID and user version;
- `quick_check = ok`;
- zero foreign-key-check rows;
- exact authorised schema inventory;
- query-only consumer opening;
- unchanged original candidate hash.

This validator must not trust the acceptance command's in-memory summary.

### Step 6 — Final hash and immutable placement

Only after accepted-copy validation passes may the command:

1. calculate the final accepted SQLite SHA-256 and file size;
2. atomically rename the staging database to its final release path;
3. `fsync` the releases directory where supported;
4. verify the final file again at its final path;
5. write the immutable release manifest to a temporary JSON file;
6. flush and `fsync` it;
7. atomically rename it to its final manifest path;
8. verify database-to-manifest agreement;
9. make the database and immutable manifest read-only on POSIX systems.

A failure before the final database rename must remove all staging artifacts.

A failure after the database rename but before a valid immutable manifest exists must leave no active-pointer change and must report the incomplete release artifact explicitly for investigation. It must never silently activate the database.

---

## 6. Immutable release manifest

The immutable JSON manifest uses:

```text
manifest_schema_version: 1
```

It must contain at least:

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
required_validation_count
release_gate_evidence_path
prior_database_release_code
prior_release_preserved
```

`required_validation_status` must equal `passed` and `required_validation_count` must equal `7` for schema version 1.

JSON output must be deterministic:

- UTF-8;
- sorted keys;
- two-space indentation;
- one trailing newline;
- no non-finite numbers.

The manifest itself may be hashed in command output and documentary evidence, but its hash is not recursively embedded inside itself.

---

## 7. Activation contract

Activation is a separate command. It must never accept or mutate a database release.

The activation command receives an immutable release-manifest path or release code and must:

1. validate the target release manifest;
2. verify the target database exists at the governed path;
3. verify database size and SHA-256;
4. open the database read-only and query-only;
5. reconcile release code, import manifest, source version, code commit and acceptance state;
6. verify `quick_check` and foreign keys;
7. read and verify the existing active pointer where one exists;
8. write a complete new active pointer to a temporary file;
9. flush and `fsync` it;
10. atomically replace `active_database.json`;
11. reopen the new pointer and resolve the active database through the production resolver.

Activation does not rename, overwrite or delete any accepted database.

The active JSON schema uses:

```text
active_manifest_schema_version: 1
```

It must contain at least:

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
previous_active_database_release_code
```

For first activation, `previous_active_database_release_code` is null.

---

## 8. Resolver contract

A single repository resolver is the only supported way for notebooks and applications to open the active database.

It must:

1. locate `active_database.json` relative to a supplied project root;
2. reject symlinks for the active pointer, immutable release manifest and database file;
3. reject absolute paths in manifests;
4. reject `..` and any path escaping the governed project database directory;
5. require the database beneath `data/processed/database/releases/`;
6. load and validate the immutable release manifest;
7. reconcile all duplicated active and release fields;
8. verify file existence, size and SHA-256;
9. open SQLite using a read-only URI;
10. set and verify `foreign_keys = ON`, `trusted_schema = OFF` and `query_only = ON`;
11. verify application ID and schema version;
12. verify the in-database accepted release and manifest codes;
13. return the query-only connection.

No notebook or application may hard-code an individual accepted release filename.

The resolver must fail closed if any manifest, hash, path, SQLite header, accepted state or in-database identity differs.

---

## 9. Rollback contract

Rollback does not alter an accepted database.

Where a previous accepted release exists, rollback is implemented by running the same activation command against that previous immutable release manifest.

Before pointer replacement, the previous release must pass the complete resolver and release validation.

The currently active release remains retained as an accepted release; rollback changes only which release is active.

For the first release, there is no earlier release to roll back to. A failed first activation must leave no active pointer or leave the previously valid absent state unchanged.

No automated cleanup may delete old accepted releases. Retention or archival is a separately governed operation.

---

## 10. Failure and cleanup rules

The implementation must fail closed.

### Before staging copy exists

No cleanup beyond temporary command state is required.

### While staging exists

On failure, remove:

- staging database;
- SQLite journal, WAL and shared-memory sidecars;
- temporary release manifest.

The original candidate and all accepted releases must remain unchanged.

### After final accepted paths exist

Never overwrite them automatically.

If an incomplete accepted artifact exists because a process stopped between final atomic operations, the next run must stop and identify the exact conflict. It must not guess whether to delete or reuse the artifact.

### During activation

Any failure before `os.replace` leaves the old active pointer unchanged.

Any failure after `os.replace` must be detected by reopening through the production resolver. If post-replacement resolution fails, the command may restore the previously verified pointer atomically from its in-memory bytes, then verify the restored state. It must report both the failed activation and rollback outcome.

---

## 11. Implementation units

The first implementation should create bounded modules similar to:

```text
src/inside_rails/database/release_model.py
src/inside_rails/database/release_paths.py
src/inside_rails/database/release_manifest.py
src/inside_rails/database/release_acceptance.py
src/inside_rails/database/release_validator.py
src/inside_rails/database/active_release.py
src/inside_rails/database/active_resolver.py
scripts/accept_minimum_core_release.py
scripts/validate_database_release.py
scripts/activate_database_release.py
scripts/validate_active_database.py
```

The exact split may change to keep modules cohesive, but acceptance, independent validation, activation and consumer resolution must remain separate code paths.

The real candidate must not be used while basic lifecycle behaviour is still being developed. Implementation starts with synthetic databases generated by the existing schema and candidate test helpers.

---

## 12. Required focused tests

Tests must cover at least:

### Acceptance success

- candidate remains byte-for-byte unchanged;
- accepted copy reaches `release_accepted` through `built -> validated -> release_accepted`;
- all seven required validation stages are present and passed;
- immutable database and release manifest agree;
- accepted release opens read-only and query-only;
- first release records no prior release and preservation true.

### Refusal and cleanup

- wrong candidate hash;
- candidate already release accepted;
- candidate manifest not at `built`;
- missing or failed required project evidence;
- changed candidate during copying;
- pre-existing final release path;
- pre-existing staging or SQLite sidecar;
- failure while recording acceptance evidence;
- failed independent accepted-release validation;
- staging cleanup after every pre-publication failure.

### Activation

- first activation succeeds;
- activation leaves accepted files unchanged;
- switching to a later release preserves the earlier release;
- rollback reactivates the earlier release;
- invalid target hash, manifest or database identity leaves the old pointer unchanged;
- a post-replacement resolver failure restores the prior pointer.

### Resolver security

- absolute paths rejected;
- traversal paths rejected;
- paths outside the releases directory rejected;
- symlinks rejected;
- missing files rejected;
- size and hash mismatches rejected;
- inconsistent active/release manifests rejected;
- non-accepted database rejected;
- wrong SQLite application ID or schema version rejected;
- returned connection is query-only.

### Immutability

- acceptance refuses overwrite;
- activation never mutates an accepted database;
- accepted database hash remains stable across resolution and queries;
- old releases remain present after later activation and rollback.

---

## 13. Independent validators

Two new validators are required.

### 13.1 Accepted release validator

This validator receives an immutable release manifest and independently verifies the accepted SQLite file and all release-manifest agreement.

It must not call the acceptance implementation to derive expected values.

### 13.2 Active database validator

This validator reads `active_database.json`, independently verifies the active pointer and immutable release manifest, resolves the database query-only, and checks accepted in-database identity.

It must not rewrite any file.

Both validators must be included in the repository-wide validator sweep once implemented.

---

## 14. Real Source Version 1 gate

After implementation and synthetic tests, the real Source Version 1 candidate may be accepted only after:

1. focused release-lifecycle tests pass;
2. all existing database tests pass;
3. the complete repository test suite passes;
4. all independent validators, including the two new release validators where applicable, pass;
5. the implementation and evidence are reviewed;
6. the user explicitly authorises the real acceptance command;
7. the candidate hash is rechecked immediately before acceptance.

Acceptance must initially create the immutable release and release manifest **without activating it**.

The accepted release must then be validated independently at its final path.

Activation requires a second explicit user decision after reviewing the accepted-release evidence.

---

## 15. Current bounded conclusion

The selected release model is intentionally simple:

- never overwrite the tested candidate;
- never edit an accepted release;
- copy, validate and accept a separate file;
- retain every accepted release;
- select the live release with one atomic JSON pointer;
- use the same verified activation mechanism for rollback;
- require all consumers to resolve the pointer rather than hard-code a database filename.

This provides a clear official database, exact evidence of what was accepted, no silent replacement, and a practical rollback path.

The next bounded implementation step is to build the lifecycle against synthetic data and prove its failure behaviour. No real database acceptance or activation is authorised by this document alone.
