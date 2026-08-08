# Phase 4 Release Acceptance Evidence

## Status

**Inside Rails Database Version 1 was release-accepted and promoted on 8 August 2026.**

This closes the release-management boundary left open after the independently validated minimum-core candidate and Phase 4 repository-wide technical gate.

No Source Version 1 rows were rebuilt or reinterpreted during promotion.

---

## 1. Release contract

Promotion was performed under:

`docs/PHASE_4_RELEASE_ACCEPTANCE_AND_PROMOTION_CONTRACT.md`

The contract requires the validated candidate to remain unchanged, promotion to operate on a copy, manifest transition to follow `built -> validated -> release_accepted`, final publication to use an atomic same-directory rename, and any failure to leave the candidate intact.

---

## 2. Preserved validated candidate

Candidate path:

`data/processed/database/candidates/inside_rails_v1_candidate.sqlite3`

Candidate size:

`1,730,048,000 bytes`

Candidate SHA-256 before and after promotion:

`7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2`

Promotion result:

```text
candidate_hash_unchanged: true
```

The candidate therefore remains the exact pre-release artifact previously bound to the complete source-wide validation evidence.

---

## 3. Release-boundary implementation validation

Focused promotion tests were run before release:

```bash
.venv/bin/python -m pytest -q tests/test_database_release_v1.py
```

Observed result:

```text
6 passed in 0.64s
```

The complete repository test suite was then run against the release-boundary implementation:

```bash
.venv/bin/python -m pytest -q
```

Observed result:

```text
360 passed in 15.36s
```

The earlier Phase 4 repository-wide technical gate remains the source of the all-validator acceptance evidence:

```text
repository commit: bf1d7f7b253edaf7232351e33ada92b039ca97ba
354 tests passed
ALL 31 VALIDATORS PASSED
```

Those 31 validators were not represented as newly rerun during promotion. Their already-recorded evidence was durably associated with the accepted release as required by the release contract.

---

## 4. Promotion command

The accepted release was created with:

```bash
.venv/bin/python scripts/promote_inside_rails_v1.py
```

Observed promotion summary:

```text
application_id: 1230130259
candidate_hash_unchanged: true
candidate_sha256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
candidate_size_bytes: 1730048000
foreign_key_check_rows: 0
manifest_status: release_accepted
quick_check: ok
release_accepted: true
release_sha256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
release_size_bytes: 1730048000
user_version: 1
validation_result_count: 7
```

---

## 5. Accepted database identity

Canonical accepted release path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Accepted release SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Accepted release size:

`1,730,048,000 bytes`

Manifest status:

`release_accepted`

Validation-result rows:

`7`

SQLite identity:

```text
application_id: 1230130259
user_version: 1
```

Post-promotion integrity:

```text
PRAGMA quick_check: ok
PRAGMA foreign_key_check: 0 rows
```

---

## 6. Release conclusion

The first Inside Rails database release is now active for reader-facing analytical work.

The analytical default is:

`data/processed/database/releases/inside_rails_v1.sqlite3`

The immutable third-party source remains separate at its original `raceform.db` path. The validated candidate remains preserved in the candidate directory and is not the normal study database.

Reader-facing studies must consume the accepted release read-only and continue to respect existing field-governance decisions, table grains, stable identifiers and the evidence-led study process.

---

## 7. Next bounded action

Return to the reader-facing study programme using accepted Database v1, beginning with the already-defined Study 01 question unless a later project decision supersedes it.
