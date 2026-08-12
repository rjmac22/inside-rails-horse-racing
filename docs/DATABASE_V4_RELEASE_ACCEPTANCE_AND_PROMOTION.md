# Database v4 Release Acceptance and Promotion

## Status

**Promotion implementation prepared; Database v4 is not yet release-accepted.**

Database v3 remains the current accepted, immutable study database until the final gates below pass and the owner deliberately executes the v4 promotion command.

The exact Database v4 candidate already built and independently validated is:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

Candidate SHA-256:

`04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`

Candidate build/reference commit:

`dc84089aa858d45ec64c6bfe087b0cf6b763dbc2`

Candidate manifest code:

`imp:20260811T215904471424Z:80905d2d`

Database release code carried by the candidate:

`db:20260811T215904471424Z:928240a8`

The candidate remains intentionally at:

`import_manifest.build_status = 'built'`

It must remain byte-for-byte unchanged during promotion.

## Immutable prior release

Database v4 is based on the accepted Database v3 release:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Required Database v3 SHA-256:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Required size:

`3,137,081,344 bytes`

Required prior database release code:

`db:20260809T132557790891Z:84258cbc`

Promotion must prove Database v3 is unchanged before, during and after publication.

## Candidate evidence already established

Before the promotion implementation was added, the v4 candidate passed:

- independent reconstruction of the frozen Study 03 evidence;
- exact preservation checks against Database v3;
- `PRAGMA quick_check = ok`;
- zero foreign-key-check rows;
- 61 notebook records;
- 65 source-label mappings;
- 61 governed racecourses;
- 90 course/track inventory rows;
- 86 stable course/track identities;
- seven unresolved governance rows;
- exactly 111,634 GB race rows and 111,634 distinct GB race IDs;
- the exact Newmarket Rowley Mile / July Course mapping and race counts.

The complete repository suite also reached 429 passing tests, and the canonical applicable-validator runner passed all 32 applicable independent validators.

Those results establish the candidate itself. Because the repository changes when the promotion implementation and its tests are added, they are **not by themselves the final release gate**. The final gate must be rerun at the promotion implementation commit.

## Release-boundary evidence model

The built v4 candidate contains four builder-stage validation records:

1. `persisted_readback`;
2. `sqlite_integrity`;
3. `foreign_key_validation`;
4. `post_load_validation`.

Unlike Database v3, Database v4 deliberately left independent source-wide validation outside the builder and therefore stopped at `built` rather than `validated`.

The release staging copy adds exactly three acceptance records:

5. `source_wide_validation`;
6. `focused_unit_tests`;
7. `project_acceptance_gate`.

Only the staging copy may then advance to:

`import_manifest.build_status = 'release_accepted'`

The original candidate remains `built` and unchanged.

## Fail-closed promotion implementation

The implementation is:

- `src/inside_rails/database/release_v4.py`;
- `scripts/promote_inside_rails_v4.py`;
- `data/tests/test_database_v4_release_promotion.py`.

It is required to:

1. bind promotion to the exact candidate SHA-256, build/reference commit, manifest code and database release code above;
2. verify the accepted Database v3 hash and size;
3. independently validate the exact v4 candidate before any release write;
4. refuse candidate/release/base path aliasing;
5. refuse to overwrite an existing release or stale release sidecar;
6. copy the candidate to a private staging path;
7. write the three release-boundary evidence rows only to staging;
8. attach this release contract to governance release 4;
9. advance only staging from `built` to `release_accepted`;
10. run integrity, foreign-key and independent v4 validation against staging;
11. prove candidate and v3 hashes remain unchanged;
12. publish without overwriting an existing release;
13. make the published release read-only;
14. re-read, re-hash and independently revalidate the published release;
15. remove staging and any newly published release if promotion fails.

Canonical output path:

`data/processed/database/releases/inside_rails_v4.sqlite3`

## Final gate before promotion

Because the promotion implementation changes the repository after the earlier candidate gate, run the following sequence from the repository root after pulling the final implementation commit:

```bash
pytest -q \
  data/tests/test_database_v4_release_promotion.py \
  tests/test_racecourse_identity_database.py \
  tests/test_racecourse_identity_governance_handover.py \
  data/tests/test_racecourse_identity_validator.py

pytest -q

python scripts/run_applicable_validators.py

python scripts/validate_inside_rails_v4.py
```

All four commands must pass at the same repository state.

Only then run:

```bash
python scripts/promote_inside_rails_v4.py
```

The promotion command itself independently validates the exact candidate again before staging and validates both staging and the published release. It does not modify the candidate or Database v3.

## Post-promotion closeout

After a successful promotion, this document must be updated with:

- promotion implementation commit;
- observed focused-test result;
- observed complete repository-test result;
- observed 32-validator result;
- final standalone v4 validator result;
- published v4 SHA-256 and size;
- confirmation that the candidate hash remained unchanged;
- confirmation that Database v3 remained unchanged;
- final `release_accepted` status.

Only after that release exists and is independently verified should study-facing database defaults be moved from Database v3 to Database v4.
