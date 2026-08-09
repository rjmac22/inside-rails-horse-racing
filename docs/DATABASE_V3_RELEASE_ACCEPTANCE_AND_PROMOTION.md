# Database v3 Release Acceptance and Promotion

## Status

**Validated candidate complete; release promotion pending final acceptance gate.**

Validated candidate:

`data/processed/database/candidates/inside_rails_v3_candidate.sqlite3`

Validated candidate SHA-256:

`0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b`

Candidate build commit:

`96d82413c86169698113896938479027ecda81ab`

Candidate manifest:

- import manifest code: `imp:20260809T132557790891Z:77d44696`;
- database release code: `db:20260809T132557790891Z:84258cbc`;
- schema version: `3`;
- governance release id: `3`;
- prior accepted release: Database v2;
- manifest status: `validated`;
- validation-result rows: `5`.

The candidate is not yet an accepted release and must not be used as the canonical study database.

## Candidate validation evidence

The successful build and independent validator established:

- physical source rows: `1,851,286`;
- admitted source rows: `1,851,285`;
- race rows: `189,043`;
- source-backed runner rows: `1,851,285`;
- reconciled combined runner rows: `1,851,288`;
- manual-verification rows: `104`;
- typed external-value resolutions: `37`;
- raw source rows compared against accepted Database v2: `1,851,286`;
- structural race rows compared: `189,043`;
- structural runner rows compared: `1,851,285`;
- `PRAGMA quick_check = ok`;
- foreign-key-check rows: `0`.

The build preserved the accepted Database v2 SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

## Required final acceptance gate

Before promotion, the project must pass:

1. promotion-specific focused tests;
2. the complete repository test suite;
3. all applicable independent validators through the canonical governed runner;
4. a final standalone Database v3 validator run against the exact candidate and accepted Database v2 base.

Canonical commands:

```bash
pytest -q
python scripts/run_applicable_validators.py
python scripts/validate_inside_rails_v3.py
```

The validator inventory, exact positional-argument mapping and three historical Database v1 construction-only exclusions are permanently governed by `docs/APPLICABLE_VALIDATOR_GATE.md` and `scripts/run_applicable_validators.py`. Do not replace this with an ad-hoc shell loop.

Historical Database v1 construction-only validators remain outside the acceptance dependency because they require disposable v1 construction artefacts that no longer exist.

## Required promotion behaviour

The fail-closed v3 promotion implementation must:

1. require the exact validated candidate SHA-256;
2. require the exact candidate manifest identity and build/reference commit;
3. require the five existing passing candidate-stage validation records;
4. preserve the candidate byte-for-byte;
5. preserve accepted Database v2 byte-for-byte;
6. create a separate staging copy in the release directory;
7. write release-boundary evidence only to that staging copy;
8. add `focused_unit_tests` and `project_acceptance_gate` validation rows;
9. advance only the staging copy from `validated` to `release_accepted`;
10. independently validate the accepted staging copy against Database v2;
11. refuse to overwrite any existing v3 release;
12. publish only after all checks pass;
13. make the published release read-only;
14. revalidate candidate and Database v2 hashes after publication;
15. delete staging/release output on failure without deleting the validated candidate or Database v2.

## Promotion command

After the final acceptance gate passes:

`python scripts/promote_inside_rails_v3.py`

Canonical release target:

`data/processed/database/releases/inside_rails_v3.sqlite3`

## Post-promotion closure

After successful promotion, this document must be updated with the accepted release SHA-256, size, promotion commit, test/validator evidence and observed promotion result. Study-facing database documentation must then point to immutable Database v3, and Study 01 can resume against that accepted release.
