# Phase 4 Release Acceptance and Promotion Contract

## Status

**Accepted implementation contract for the first Inside Rails Version 1 database release.**

Accepted for implementation on 8 August 2026 after explicit user instruction to complete the already-validated database release.

This contract closes the release-management boundary left deliberately open after the Phase 4 candidate build and final repository-wide technical gate.

It does not rebuild Source Version 1 and does not change any source-derived race, runner or raw-evidence row.

---

## 1. Governing evidence

The release decision is bound to the exact validated candidate already evidenced by:

- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_4_MINIMUM_CORE_PHYSICAL_SCHEMA_SPECIFICATION.md`.

Validated candidate identity before release mutation:

```text
filename: inside_rails_v1_candidate.sqlite3
size: 1,730,048,000 bytes
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
manifest status: built
```

The candidate was previously stored under the legacy generated filename `raceform_v1_minimum_core_candidate.sqlite3`. Renaming the file did not change its bytes or evidence identity.

Existing technical evidence includes:

```text
bounded database gate: 72 passed in 14.54s
independent source-wide validation: passed
final repository gate: 354 passed in 18.28s
all independent validators at that gate: 31 passed
repository gate commit: bf1d7f7b253edaf7232351e33ada92b039ca97ba
```

The release procedure durably associates these already-completed evidence stages with the accepted release. It does not pretend they were rerun at promotion time.

---

## 2. Canonical paths and names

Immutable third-party source:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Validated unreleased candidate:

`data/processed/database/candidates/inside_rails_v1_candidate.sqlite3`

Canonical accepted Version 1 release:

`data/processed/database/releases/inside_rails_v1.sqlite3`

The source filename `raceform.db` is retained only for immutable source lineage. Inside Rails-generated database artifacts use Inside Rails-owned names.

---

## 3. Release-copy rule

The validated candidate is not mutated in place.

Promotion must:

1. verify the candidate path, exact file size and exact pre-release SHA-256;
2. refuse candidate SQLite sidecars;
3. refuse to overwrite an existing accepted Version 1 release;
4. copy the exact candidate to a temporary file inside the release directory;
5. verify that the temporary copy has the same SHA-256 as the candidate before any mutation;
6. apply release-evidence and manifest-state changes only to the temporary copy;
7. close and reopen the temporary copy and validate it read-only;
8. confirm the original candidate hash is unchanged;
9. atomically rename the validated temporary release to the canonical release path;
10. reopen and validate the final canonical path;
11. on any failure before successful completion, remove the temporary or failed release and leave the candidate unchanged.

The candidate therefore remains the rollback and forensic reference for the exact bytes that passed the Phase 4 source-wide validation.

---

## 4. Acceptance evidence recorded inside the release

The original candidate contains four builder validation-result rows:

- `persisted_readback`;
- `sqlite_integrity`;
- `foreign_key_validation`;
- `post_load_validation`.

The release copy must durably add the three acceptance stages required by schema version 1:

- `focused_unit_tests` — records the bounded database gate from `PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `source_wide_validation` — records the independent complete candidate validation from the same evidence document;
- `project_acceptance_gate` — records the complete repository test and all-validator result from `PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`.

These rows are evidence associations. Their command and result-summary text must state that they are recording prior evidence and identify the governing evidence document rather than claiming a new execution at promotion time.

The release copy must also add a `governance_release_evidence` document reference to this release contract.

---

## 5. Manifest transition

The existing schema enforces the authorised state path:

```text
built -> validated -> release_accepted
```

Promotion must use that exact transition.

It must not update `built` directly to `release_accepted` and must not weaken or remove any schema trigger to make promotion pass.

The final `release_accepted` transition remains subject to all existing schema checks for:

- Source Version 1 physical/admitted/excluded counts;
- 189,043 race occurrences;
- 1,851,285 runner participations;
- race-level admitted-runner reconciliation;
- accepted compatible governance;
- all seven required validation stages being present and passed;
- persisted readback, SQLite integrity, foreign keys and post-load validation flags.

---

## 6. Active-release resolution

For Version 1 the active database is resolved by one fixed canonical path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Downstream study code must consume that path read-only after release acceptance.

There is no fallback from the canonical release path to a candidate or to the raw third-party source. If the accepted release is absent, consumers must fail closed rather than silently changing data source.

---

## 7. Prior-release preservation and replacement

This is the first accepted Version 1 release.

The first-release promotion procedure therefore refuses to overwrite any pre-existing `inside_rails_v1.sqlite3`.

A later replacement or Version 2 release must define its own supersession and prior-release preservation procedure. It must not silently reuse the first-release command as an overwrite mechanism.

---

## 8. Atomicity and rollback

The canonical release path is created only by an atomic same-directory rename after the complete temporary release has passed persisted validation.

Before that rename, failure deletes the temporary release and any SQLite sidecars.

If final-path readback fails after the rename, the failed final release is removed and the unchanged validated candidate remains available for investigation and retry.

No operation may delete or mutate the validated candidate as part of rollback.

---

## 9. Post-promotion validation

Before and after the atomic rename, the release procedure must verify at minimum:

- `build_status = 'release_accepted'`;
- exactly the required validation evidence is present and passed;
- the expected Source Version 1 population counts remain unchanged;
- `PRAGMA quick_check` returns `ok`;
- `PRAGMA foreign_key_check` returns zero rows;
- SQLite `application_id = 1230130259`;
- SQLite `user_version = 1`;
- no SQLite sidecars remain;
- the original candidate SHA-256 remains `7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2`.

The accepted release obtains a new SHA-256 because release-evidence rows and manifest state are intentionally added to the copied file. That final release hash must be recorded in the release evidence and study database reference after promotion.

---

## 10. User acceptance

The project owner explicitly instructed the assistant on 8 August 2026 to complete the release acceptance/promotion after the remaining distinction between technical validation and formal release status was explained.

That instruction authorises implementation and first-release promotion under this contract.

It does not authorise branch merge or unrelated database extension.

---

## 11. Stop rule

The release boundary is complete only when:

- the promotion implementation exists;
- the validated candidate is still unchanged;
- `data/processed/database/releases/inside_rails_v1.sqlite3` exists;
- its manifest is `release_accepted`;
- post-promotion validation passes;
- the final release SHA-256 is recorded;
- `README.md`, `PROJECT_PLAN.md`, `DATABASE_USER_GUIDE.md`, `STUDY_DATABASE_REFERENCE.md` and `STUDY_DATA_ACCESS.md` identify the accepted release correctly.

Only then should reader-facing studies use the Inside Rails Version 1 database as their default analytical database.
