# Database v2 Release Acceptance and Promotion

## Status

**Release-boundary contract for Inside Rails Database v2.**

This document governs promotion of the exact validated Database v2 candidate built from the accepted Database v1 release. It does not authorise any additional data scope, parser change, correction, identity decision or analytical extension.

Promotion is a release-lifecycle operation only: copy the exact validated candidate, record the already-completed acceptance evidence on the copy, validate that copy, publish it as a new immutable release, and leave both the validated candidate and accepted Database v1 unchanged.

The project owner explicitly accepts Database v2 by running the promotion command after the gates below have passed. Until that command succeeds, Database v1 remains the accepted study database.

---

## 1. Candidate identity

Canonical validated candidate:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

Candidate SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

Candidate build identity:

- repository commit: `68ac0364c4af2a104ea76c8765fd0e220aaf8e84`;
- reference-data commit: `68ac0364c4af2a104ea76c8765fd0e220aaf8e84`;
- import manifest code: `imp:20260809T081402956098Z:878ceaa5`;
- database release code: `db:20260809T081402956098Z:5b29ea51`;
- schema version: `2`;
- manifest status before promotion: `validated`.

The candidate must remain byte-for-byte unchanged during promotion.

---

## 2. Retained prior release

Accepted Database v1 remains immutable and available for rollback:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v2 promotion must not modify, rename or remove Database v1.

---

## 3. Acceptance evidence completed on 9 August 2026

### Database v2 build and independent validation

The full Database v2 candidate build completed successfully from the accepted Database v1 base.

Final candidate state included:

- manifest status: `validated`;
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

The standalone independent Database v2 validator then revalidated the final candidate SHA-256 above and recomputed all **1,851,286** raw-record fingerprints while comparing **2,040,328** carried structural rows to the accepted Database v1 release.

### Focused Database v2 tests

After the final participant-confidence correction, the focused Database v2 test set passed:

`26 passed in 1.52s`

### Complete repository suite

At the final release boundary, the complete repository suite passed:

`386 passed in 17.04s`

### Applicable independent-validator sweep

All applicable independent validators for the current Notebook 01–22 governance chain and Database v2 passed on 9 August 2026.

Three historical Database v1 construction-stage validators were intentionally excluded because they require disposable v1 raw-mirror/candidate artefacts that no longer exist and are not acceptance dependencies for Database v2:

- `validate_core_structure_prototype.py`;
- `validate_raw_mirror_candidate.py`;
- `validate_minimum_core_candidate.py`.

The applicable sweep included the Database v2 implementation preflight and the full read-only Database v2 validator, together with the source-wide field, identity, temporal, reference, supplementation and semantic validators.

---

## 4. Required promotion behaviour

The promotion implementation must fail closed and must:

1. verify the exact validated candidate SHA-256;
2. verify candidate schema/header, manifest identity, counts, validation flags and the five candidate-stage validation records already present;
3. verify the accepted Database v1 base remains the exact retained prior release;
4. copy the candidate to a temporary staging file in the release directory;
5. write acceptance evidence only to the staging copy;
6. add exactly two release-boundary validation records:
   - `focused_unit_tests` for the completed Database v2 focused test evidence;
   - `project_acceptance_gate` for the complete 386-test repository suite and applicable-validator sweep;
7. retain the existing Database v2 `source_wide_validation` record rather than duplicating it;
8. advance only the staging copy from `validated` to `release_accepted`;
9. attach this release contract to the current Database v2 governance release;
10. run SQLite integrity and foreign-key checks on the staging copy;
11. run the full independent Database v2 validator against the release copy and accepted Database v1 base;
12. prove the original validated candidate hash did not change;
13. publish the release without overwriting any existing release file;
14. re-read and re-hash the published release;
15. remove staging/release output on failure while leaving the candidate and Database v1 intact.

---

## 5. Canonical release path

On successful promotion, Database v2 is published as:

`data/processed/database/releases/inside_rails_v2.sqlite3`

The release copy will have a different SHA-256 from the validated candidate because release acceptance adds validation/provenance rows and changes the import-manifest status to `release_accepted`. This is expected.

The validated candidate remains preserved unchanged as pre-release evidence.

---

## 6. Post-promotion integration

After successful local promotion and final release hash capture, update the study-facing database documentation so reader-facing studies use Database v2 read-only by default.

At minimum update:

- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/DATABASE_USER_GUIDE.md`;
- `docs/DATABASE_V2_GOVERNED_INTEGRATION_DESIGN.md`.

Do not switch study documentation before the promotion command succeeds.

Once those release-state updates are committed and remote-verified, Database v2 work is closed and Study 01 should resume immediately.