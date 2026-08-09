# Database v2 Release Acceptance and Promotion

## Status

**Completed release-boundary record for Inside Rails Database v2.**

Database v2 was release-accepted and promoted successfully on **9 August 2026**.

Canonical accepted release:

`data/processed/database/releases/inside_rails_v2.sqlite3`

Accepted release SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Release size:

`3,137,044,480 bytes`

The release was created only after the validated candidate, retained Database v1 release, repository tests and applicable independent validators passed the required gates.

Promotion was a release-lifecycle operation only. It did not add data scope, change parser semantics, introduce a new correction, alter an identity decision or rebuild Source Version 1.

---

## 1. Validated candidate identity

Canonical preserved candidate:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

Candidate SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

Candidate size:

`3,137,044,480 bytes`

Candidate build identity:

- repository commit: `68ac0364c4af2a104ea76c8765fd0e220aaf8e84`;
- reference-data commit: `68ac0364c4af2a104ea76c8765fd0e220aaf8e84`;
- import manifest code: `imp:20260809T081402956098Z:878ceaa5`;
- database release code: `db:20260809T081402956098Z:5b29ea51`;
- schema version: `2`;
- manifest status before promotion: `validated`.

Promotion proved that this candidate remained byte-for-byte unchanged.

---

## 2. Retained prior release

Accepted Database v1 remains immutable and available for rollback:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Promotion proved `prior_release_preserved = true`.

Database v1 was not modified, renamed or removed.

---

## 3. Candidate validation evidence

The complete Database v2 candidate build completed successfully from the accepted Database v1 base.

Validated candidate state included:

- 31 physical tables;
- 189,043 race rows;
- 1,851,285 source-backed runner rows;
- 189,043 temporal rows;
- 85 manual-verification rows;
- 611 provisional horse occurrences;
- 353 horse/pedigree transition decisions;
- 1,205 participant candidates;
- 68 participant identities;
- 149 accepted participant label mappings;
- `PRAGMA quick_check = ok`;
- zero foreign-key-check rows.

The standalone Database v2 validator revalidated the exact final candidate SHA-256 and:

- recomputed all **1,851,286** raw-record fingerprints;
- compared **2,040,328** carried structural rows to the accepted Database v1 release.

Focused Database v2 tests passed:

`26 passed in 1.52s`

The candidate-era complete repository suite passed:

`386 passed in 17.04s`

All applicable independent validators for the Notebook 01–22 governance chain and Database v2 passed on 9 August 2026.

Three historical Database v1 construction-stage validators were intentionally excluded because they depend on disposable v1 construction artefacts that no longer exist and are not Database v2 acceptance dependencies:

- `validate_core_structure_prototype.py`;
- `validate_raw_mirror_candidate.py`;
- `validate_minimum_core_candidate.py`.

---

## 4. Promotion implementation gate

A dedicated fail-closed Database v2 promotion implementation was then added.

Promotion implementation commit:

`78087b0ae1985809d63ee2feacd71423ac18c727`

Promotion-specific focused tests passed:

`6 passed in 0.51s`

Because those six tests were added after the earlier 386-test candidate-era gate, the complete repository suite was run again at the actual promotion implementation commit:

`392 passed in 16.93s`

This 392-test run is the final repository corroboration for the promotion implementation.

The accepted database contains seven required import-validation rows. Its embedded `project_acceptance_gate` row records the earlier 386-test candidate-era repository gate plus the applicable independent-validator sweep, exactly as the promotion contract was implemented. The subsequent 392-test run at the promotion commit is recorded in this durable release record and the study-facing database documentation.

---

## 5. Required promotion behaviour

The promotion implementation was required to fail closed and to:

1. verify the exact validated candidate SHA-256;
2. verify candidate schema/header, manifest identity, counts, validation flags and the five candidate-stage validation records already present;
3. verify the accepted Database v1 base remained the exact retained prior release;
4. copy the candidate to temporary staging in the release directory;
5. write acceptance evidence only to the staging copy;
6. add the two release-boundary validation stages absent from the candidate:
   - `focused_unit_tests`;
   - `project_acceptance_gate`;
7. retain the existing Database v2 `source_wide_validation` record rather than duplicate it;
8. advance only the staging copy from `validated` to `release_accepted`;
9. attach this release contract to the current Database v2 governance release;
10. run SQLite integrity and foreign-key checks on the staging copy;
11. run the full independent Database v2 validator against the release copy and accepted Database v1 base;
12. prove the original validated candidate hash did not change;
13. publish the release without overwriting any existing release file;
14. re-read and re-hash the published release;
15. remove staging/release output on failure while leaving the candidate and Database v1 intact.

The successful promotion result demonstrates that these controls passed.

---

## 6. Successful promotion result

Command:

`python scripts/promote_inside_rails_v2.py`

Observed successful result:

```text
application_id: 1230130259
candidate_sha256_hex: 5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe
candidate_hash_unchanged: true
candidate_size_bytes: 3137044480
release_sha256_hex: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
release_size_bytes: 3137044480
manifest_status: release_accepted
release_validator_manifest_status: release_accepted
validation_result_count: 7
quick_check: ok
foreign_key_check_rows: 0
raw_record_fingerprints_recomputed: 1851286
structural_rows_compared: 2040328
prior_release_preserved: true
release_accepted: true
user_version: 2
promotion_repository_commit: 78087b0ae1985809d63ee2feacd71423ac18c727
```

The release file has a different SHA-256 from the validated candidate because acceptance evidence and the manifest status were written only to the release copy. This is expected.

---

## 7. Release immutability

The accepted Database v2 release is now immutable.

Do not modify it in place.

The validated candidate remains unchanged as pre-release evidence.

Database v1 remains unchanged as the prior accepted release and rollback point.

Any future database correction that changes accepted database content must use a new candidate/release lifecycle rather than editing this release.

---

## 8. Study-facing integration

After promotion, the required study-facing documents were updated so reader-facing studies use Database v2 read-only by default:

- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/DATABASE_USER_GUIDE.md`;
- `docs/DATABASE_V2_GOVERNED_INTEGRATION_DESIGN.md`.

The canonical study database is now:

`data/processed/database/releases/inside_rails_v2.sqlite3`

There is no silent fallback to Database v1, the v2 candidate or Source Version 1.

The current implemented consumer contract is the documented immutable release path. The active-manifest mechanism described in the older SQLite architecture ADR is not currently the implemented study resolver and must not be invented ad hoc.

---

## 9. Closure condition

Database v2 work is closed when:

- the release exists locally at the canonical path;
- the accepted release hash is recorded;
- candidate and v1 preservation are confirmed;
- post-promotion study documentation is committed;
- the local checkout is synchronised to the documentation commits;
- the remote branch is verified;
- unrelated untracked Notebook 24, Notebook 25 and `studies/` work remains untouched.

After those checks, Study 01 should resume immediately against accepted Database v2.
