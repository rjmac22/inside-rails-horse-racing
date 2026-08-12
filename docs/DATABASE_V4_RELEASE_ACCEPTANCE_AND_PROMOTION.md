# Database v4 Release Acceptance and Promotion

## Status

**Database v4 was release-accepted on 12 August 2026.**

It is now the current immutable Inside Rails study database.

Canonical release:

`data/processed/database/releases/inside_rails_v4.sqlite3`

Accepted release SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

Accepted release size:

`3,137,249,280 bytes`

SQLite / manifest state:

- `application_id`: `1230130259`;
- `user_version`: `4`;
- manifest status: `release_accepted`;
- validation-result rows: `7`;
- `PRAGMA quick_check`: `ok`;
- `PRAGMA foreign_key_check`: `0` rows.

## Exact promoted candidate

The accepted release was promoted from the exact candidate:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

Candidate SHA-256:

`04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`

Candidate build/reference commit:

`dc84089aa858d45ec64c6bfe087b0cf6b763dbc2`

Candidate manifest code:

`imp:20260811T215904471424Z:80905d2d`

Database release code:

`db:20260811T215904471424Z:928240a8`

The candidate remained byte-for-byte unchanged during promotion and retains its pre-release `built` state as immutable evidence.

## Immutable prior release

Database v4 was built from and promoted against accepted Database v3:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Database v3 SHA-256 before and after promotion:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Database v3 size:

`3,137,081,344 bytes`

A separate read-only pre-v4-promotion backup was also created locally and verified byte-for-byte against the accepted v3 hash before promotion.

Database v3 remains retained as an immutable historical release and rollback point.

## Study 03 population integrated by v4

Database v4 integrates the corrected completed Great Britain Study 03 racecourse/course identity model:

- 61 Study 03 racecourse notebooks;
- 65 Great Britain source-label mappings;
- 61 governed racecourse identities;
- 90 course/track inventory rows;
- 86 stable course/track identities;
- 7 unresolved governance rows;
- 111,634 Great Britain race rows;
- 111,634 distinct Great Britain race IDs.

The release preserves the corrected Newmarket split:

- `Newmarket` → `Newmarket — Rowley Mile`;
- `Newmarket (July)` → `Newmarket — July Course`.

Database v4 does not fabricate race-occurrence → physical-track assignment. Study 03 establishes racecourse-level identity and a reusable course/track reference layer while preserving unresolved lower-level assignment questions.

## Release-boundary implementation

Promotion implementation commit:

`27b8ac8aba3b22809c4da4f603b2302e47e9fa6d`

Implementation:

- `src/inside_rails/database/release_v4.py`;
- `scripts/promote_inside_rails_v4.py`;
- `data/tests/test_database_v4_release_promotion.py`.

The promotion path is fail-closed. It binds promotion to the exact candidate identity, verifies immutable v3, copies to a private staging database, writes acceptance evidence only to staging, independently validates staging, publishes without overwriting an existing release, makes the release read-only, then re-reads and independently validates the published release. Candidate and prior-release hashes are rechecked during and after promotion.

## Final acceptance evidence

Focused v4/release tests at the final promotion-code state:

```text
13 passed in 1.11s
```

Complete repository suite at the same state:

```text
435 passed in 15.47s
```

Canonical applicable independent-validator gate:

```text
Applicable validator sweep PASSED: 32 validators
```

Final standalone v4 validation immediately before promotion returned:

```text
candidate_sha256_hex: 04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e
manifest_status: built
quick_check: ok
foreign_key_check_rows: 0
notebook_rows: 61
source_label_rows: 65
racecourse_rows: 61
inventory_rows: 90
stable_course_rows: 86
unresolved_rows: 7
gb_race_rows: 111634
gb_distinct_race_rows: 111634
raw_record_rows_compared: 1851286
structural_race_rows_compared: 189043
structural_runner_rows_compared: 1851285
reference_course_rows_compared: 395
```

Promotion then returned:

```text
release_accepted: true
manifest_status: release_accepted
release_validator_manifest_status: release_accepted
candidate_hash_unchanged: true
prior_release_preserved: true
quick_check: ok
foreign_key_check_rows: 0
validation_result_count: 7
```

Published release SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

A final filesystem readback confirmed both accepted releases are read-only and have the expected hashes:

```text
v3: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
v4: 45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7
```

## Study database consequence

Database v4 supersedes Database v3 for normal reader-facing analytical work.

Normal studies must now use the exact accepted v4 release read-only. Database v3, v2 and v1 remain immutable historical releases; the v4 candidate remains immutable pre-release evidence.

The new Study 04-facing racecourse interface is:

`view_gb_reconciled_race_occurrences_with_racecourse`

It preserves one row per Great Britain race occurrence while adding governed racecourse identity. The existing reconciled race/runner views remain available unchanged for questions that do not require racecourse identity.

## Process lesson for v5+

Database v4 required substantial one-off release infrastructure work: full pytest discovery was corrected, historical validators were made reproducible, the canonical applicable-validator gate was established, an independent v4 validator was added, and a fail-closed v4 promotion implementation was created.

Future releases should reuse this infrastructure rather than reconstructing it. The intended normal sequence is:

1. freeze completed study evidence;
2. build the smallest governed candidate;
3. add/update its independent validator;
4. run focused tests;
5. run the complete repository suite once at the final implementation state;
6. run the canonical applicable-validator sweep once;
7. run the new-version standalone validator once at the release boundary;
8. promote through the established fail-closed release pattern;
9. perform cheap post-publication identity/readback checks;
10. update study-facing release documentation.

The project should make future database releases routine rather than rebuilding release governance for every study.