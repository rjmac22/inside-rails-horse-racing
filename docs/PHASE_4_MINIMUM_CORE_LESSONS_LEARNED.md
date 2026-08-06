# Phase 4 Minimum-Core Lessons Learned

## Purpose

This document records reusable lessons from designing, building and independently validating the complete Source Version 1 minimum-core database candidate.

It supplements `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md` without reopening the completed notebook investigations.

---

## 1. Prove the smallest real structure before scaling

The three-race prototype was not redundant. It exposed the exact structural contract on real data before a 1.85-million-runner build was attempted.

The useful sequence was:

1. prove the complete raw boundary;
2. select a deterministic small set of complete real races;
3. create race and runner rows;
4. close and reopen the file;
5. independently reconstruct the same result;
6. only then scale to the complete source.

A synthetic test can prove code behaviour. A small real-data rehearsal proves that the code and source semantics meet at the intended boundary.

---

## 2. Builder checks and independent validation are different evidence

A builder must check its own output, but that is not independent evidence.

The complete builder verified persisted counts, race grouping, runner lineage, SQLite integrity, foreign keys and manifest state. A separate validator then reopened the fixed candidate and independently repeated the reconstruction.

The reusable rule is:

> A builder may prove that it followed its own plan; a separate validator must prove that the persisted result agrees with the governed source contract.

The validator should not import builder counters, accept builder summaries or rely on temporary in-memory state.

---

## 3. Bind every large validation to exact artifact hashes

Counts and filenames are not sufficient identity.

The complete validation was bound to:

- the exact immutable source SHA-256;
- the exact independently validated raw-mirror SHA-256;
- the exact complete minimum-core candidate SHA-256.

Hashes were checked before and after validation. This made the result evidence about one exact set of bytes rather than about whatever happened to exist at a familiar path.

---

## 4. Separate structural governance from database-release acceptance

An accepted method is not the same as an accepted database release.

The candidate legitimately contains an accepted governance release describing the authorised Source Version 1 structural method. Its import manifest nevertheless remains only `built`.

The reusable distinction is:

- **method accepted**: the transformation rule is authorised;
- **candidate built**: the database file was constructed and passed builder checks;
- **candidate independently validated**: separate code reconciled the persisted file;
- **release accepted**: a further explicit project gate approved promotion or active use.

These states must not be collapsed into one Boolean called “valid.”

---

## 5. Keep release acceptance impossible by accident

The schema should not depend on developer restraint alone.

Protective constraints and triggers ensure that:

- incompatible governance cannot be attached to races, runners or manifests;
- invalid manifest state transitions fail;
- a structurally inconsistent candidate cannot enter `release_accepted`;
- only one release-accepted manifest can exist where the schema requires it.

Tests should verify the invariant rather than depend on which valid protective trigger produces the first error message.

---

## 6. Copying the proved raw mirror reduced risk

The complete minimum-core builder copied the already validated raw-mirror candidate rather than repeating source extraction and fingerprint generation inside the same operation.

That created a cleaner boundary:

- raw preservation had already been proved independently;
- the core builder only had to add governance, race, runner and manifest structures;
- the copied raw bytes could be hashed against the fixed raw-mirror candidate;
- failure in core population could not damage the previously proved raw artifact.

Layered candidates can be safer than one enormous all-purpose import, provided each boundary has exact identity and reconciliation evidence.

---

## 7. Refuse overwrite and delete every failed artifact

A disposable candidate should still be handled carefully.

The builder refuses to overwrite an existing database or SQLite sidecar. On failure it removes:

- the candidate database;
- `-journal`;
- `-wal`;
- `-shm`.

This prevents an incomplete file from looking like a usable candidate and preserves the previous known-good artifacts unchanged.

The rule is:

> Failure should leave evidence in logs and tests, not a plausible-looking half-built database.

---

## 8. Close and reopen before claiming persistence

Successful SQL execution is not persisted-readback evidence.

The builder committed, closed the connection, reopened the file read-only and reconciled the persisted result. The validator independently reopened all relevant files again.

This caught a different class of possible failure from in-transaction assertions: journalling, finalisation, schema persistence, wrong output paths and accidental reliance on connection state.

---

## 9. Preserve SQLite storage classes, not just displayed values

SQLite's dynamic typing means equal-looking values can have different physical representations.

The independent validator compared both:

- all 68,497,582 raw values;
- all 68,497,582 SQLite storage classes.

This matters because text `"1"`, integer `1`, real `1.0`, blank text and null are not interchangeable evidence even when downstream software might coerce them into similar-looking values.

Raw preservation must include physical type as well as apparent content.

---

## 10. Deterministic identifiers make rebuilds auditable

Source, race and runner codes are derived from fixed source identity and deterministic sequence or row lineage.

Race sequence is based on ascending minimum supporting source `rowid`. Runner codes are tied directly to admitted source `rowid`.

This ensures the same source and method produce the same structural identities across rebuilds. Random identifiers are useful for build-attempt and database-release codes, but not for stable source-derived entities.

---

## 11. Performance should be measured after correctness is fixed

The complete build finished in about 76 seconds and populated core rows at roughly 55,416 rows per second. Independent validation took about 199 seconds and compared about 9,291 raw records per second while also checking 37 values and storage classes per row.

Those measurements are useful for operational planning, but performance optimisation came after the structural method and failure behaviour were proved.

The right order is:

1. correct bounded method;
2. deterministic output;
3. failure cleanup;
4. independent validation;
5. measured performance;
6. optimisation only where evidence shows a material need.

---

## 12. Split large implementation modules by responsibility

The complete builder was easier to review when separated into:

- shared model and validation contracts;
- file-copy and artifact-lifecycle controls;
- governance and manifest seeding;
- source-wide core population;
- persisted readback;
- manifest finalisation;
- command-line entry point.

The validator remained a separate implementation path.

Module splitting should follow meaningful evidence boundaries, not arbitrary line counts.

---

## 13. Focused gates should grow with the implementation boundary

The database-focused gate expanded from schema tests to raw-mirror tests, structural-prototype tests, full-builder tests and full-validator tests.

The final bounded gate was:

```text
72 passed in 14.54s
```

This was appropriate before source-wide validation. It was not treated as a substitute for the complete repository test suite and every project validator at a later release or series boundary.

The lesson is to run the smallest gate that fully covers the current change, then reserve broad expensive gates for the agreed integration boundary.

---

## 14. Evidence documents should state what remains unproved

Each evidence record explicitly distinguishes its achieved conclusion from later work.

For the complete candidate, remaining unproved items include:

- live release acceptance;
- active database path and discovery;
- atomic promotion or replacement;
- rollback against a prior accepted release;
- complete project acceptance evidence inside the candidate;
- governed analytical-field extensions.

A good evidence document prevents a later reader from turning “this candidate passed” into “the whole database programme is finished.”

---

## 15. Documentation drift is a real project defect

After the complete candidate passed, `PROJECT_PLAN.md`, `README.md` and the historical audit still described Phase 3 as future work.

Technical completion without status-document reconciliation creates the wrong next action and can cause settled work to be repeated or skipped.

Closeout should therefore include an explicit documentation check:

- what was just proved;
- what stage is now complete;
- what remains deliberately unaccepted;
- what the next bounded action actually is.

---

## 16. Next behavioural change

The next stage should not immediately add analytical fields merely because the structural candidate exists.

First define the separate release-acceptance and promotion contract, including:

- required project acceptance evidence;
- active database path and naming;
- atomic replacement;
- prior-release preservation;
- rollback;
- post-promotion validation;
- explicit user acceptance.

The reusable stop rule is:

> Do not promote a candidate because construction succeeded. Promote only after the promotion and rollback mechanism itself has been designed, tested and accepted.
