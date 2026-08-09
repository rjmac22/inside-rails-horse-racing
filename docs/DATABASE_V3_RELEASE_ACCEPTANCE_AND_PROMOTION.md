# Database v3 Release Acceptance and Promotion

## Status

**Database v3 accepted and promoted on 9 August 2026.**

Canonical accepted release:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Accepted release SHA-256:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Accepted release size:

`3,137,081,344 bytes`

Promotion repository commit:

`0b535cb5bfdcb22b7693e8a26a82acfcb025529d`

SQLite/release identity:

- `application_id`: `1230130259`;
- `user_version`: `3`;
- manifest status: `release_accepted`;
- validation-result rows: `7`;
- `PRAGMA quick_check`: `ok`;
- foreign-key-check rows: `0`.

The accepted release is immutable and is now the canonical study database.

## Validated candidate preserved

Validated candidate:

`data/processed/database/candidates/inside_rails_v3_candidate.sqlite3`

Candidate SHA-256:

`0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b`

Candidate size:

`3,137,081,344 bytes`

Candidate build commit:

`96d82413c86169698113896938479027ecda81ab`

Candidate manifest identity:

- import manifest code: `imp:20260809T132557790891Z:77d44696`;
- database release code: `db:20260809T132557790891Z:84258cbc`;
- schema version: `3`;
- governance release id: `3`;
- prior accepted release: Database v2;
- candidate manifest status: `validated`;
- candidate validation-result rows: `5`.

Promotion confirmed `candidate_hash_unchanged = true`.

## Prior accepted release preserved

Database v2 remains immutable at:

`data/processed/database/releases/inside_rails_v2.sqlite3`

Database v2 SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Promotion confirmed `prior_release_preserved = true`.

## Final acceptance gate evidence

At the final promotion implementation head, the complete repository suite passed:

```text
412 passed in 18.64s
```

The canonical applicable-validator runner then passed every applicable independent validator:

```text
Applicable validator sweep PASSED: 31 validators
```

The three historical Database v1 construction-only validators remained explicitly outside the release dependency as documented in `docs/APPLICABLE_VALIDATOR_GATE.md`.

A final standalone Database v3 validation immediately before promotion returned:

- physical source rows: `1,851,286`;
- admitted source rows: `1,851,285`;
- race rows: `189,043`;
- source-backed runner rows: `1,851,285`;
- reconciled combined runner rows: `1,851,288`;
- manual-verification rows: `104`;
- typed external-value resolutions: `37`;
- raw source rows compared against Database v2: `1,851,286`;
- structural race rows compared: `189,043`;
- structural runner rows compared: `1,851,285`;
- `PRAGMA quick_check = ok`;
- foreign-key-check rows: `0`;
- candidate manifest status: `validated`.

The promotion itself revalidated the accepted release and reported:

- release manifest status: `release_accepted`;
- release validator manifest status: `release_accepted`;
- candidate hash unchanged: `true`;
- prior release preserved: `true`;
- raw rows compared: `1,851,286`;
- structural race rows compared: `189,043`;
- structural runner rows compared: `1,851,285`;
- `quick_check = ok`;
- foreign-key-check rows: `0`.

## Release purpose

Database v3 is the bounded external-verification reconciliation release specified in `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`.

It preserves Source Version 1 and Database v2 unchanged while making all externally established exact facts from the audited notebook evidence analytically usable where the evidence supports that action. It also nulls known-wrong analytical values where no defensible replacement exists, while keeping the raw source assertion visible for lineage.

The release contains:

- `104` durable manual-verification records;
- `37` typed external-value resolutions;
- the new `governance_external_value_resolution` table;
- reconciled race, source-runner and combined-runner study views.

## Promotion behaviour proved

The fail-closed promotion:

1. required the exact validated candidate SHA-256;
2. required the exact candidate manifest identity and build/reference commit;
3. required the five existing passing candidate-stage validation records;
4. preserved the candidate byte-for-byte;
5. preserved accepted Database v2 byte-for-byte;
6. created a separate staging copy in the release directory;
7. wrote release-boundary evidence only to that staging copy;
8. added `focused_unit_tests` and `project_acceptance_gate` validation rows;
9. advanced only the staging copy from `validated` to `release_accepted`;
10. independently validated the accepted staging copy against Database v2;
11. published without overwriting an existing release;
12. made the published release read-only;
13. revalidated candidate and Database v2 hashes after publication.

## Canonical promotion command

The accepted release was produced with:

```bash
python scripts/promote_inside_rails_v3.py
```

No further promotion is required for this release.
