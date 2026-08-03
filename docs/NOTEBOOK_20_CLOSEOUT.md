# Notebook 20 Closeout — Connections and Ownership Identity

## Status

Notebook 20 is fully closed on branch `audit/retrospective-implementation-closeout`.

The notebook investigated the runner-level `jockey`, `trainer` and `owner` fields as source-presented connection labels. The work does not treat those labels as canonical person, partnership, syndicate, licence or organisation identifiers.

## Governing conclusion

The three fields are suitable for preservation as atomic source text. Exact text equality may support bounded source-label analysis, but it must not be promoted automatically to real-world entity identity.

The immutable source population contains:

- 1,851,285 governed runner rows under `rowid <> 1`;
- 2 blank `jockey` occurrences;
- 9 blank `trainer` occurrences;
- 35 blank `owner` occurrences;
- 46 blank connection-field occurrences across 44 runner rows.

Two runners each contain both a blank trainer and a blank owner, explaining the difference between blank occurrences and affected rows.

## Manual verification outcome

The completed Notebook 20 review queue contains 46 bounded records:

- 28 verified repairs;
- 5 conflicting-evidence cases;
- 13 insufficient-evidence cases.

The verified repairs comprise:

- 2 jockey supplementations;
- 4 trainer supplementations;
- 22 owner supplementations.

The remaining 18 blanks are preserved as unresolved:

- 5 trainer blanks;
- 13 owner blanks.

Permanent verification identifiers are `NB20-CONNECTION-0001` through `NB20-CONNECTION-0046` in `data/reference/manual_verifications.csv`.

Confirmed records authorise only `source_supplementation`. Conflicting and insufficient records authorise only `preserve_raw_unresolved`.

## Durable artifacts

- `notebooks/20_connections_and_ownership_identity.ipynb`;
- `data/reference/manual_verifications.csv`;
- `data/reference/connection_identity_repairs.csv`;
- `src/inside_rails/connection_identity.py`;
- `tests/test_connection_identity.py`;
- `tests/test_manual_verifications.py`;
- `scripts/promote_connection_identity_verifications.py`;
- `scripts/validate_connection_identity.py`;
- `scripts/validate_manual_verifications.py`;
- `docs/CONNECTION_IDENTITY_INTEGRATION.md`;
- this closeout record.

## Database consequence

The raw `jockey`, `trainer` and `owner` fields remain immutable.

A clean runner layer may expose a governed value only when an exact `(source_rowid, source_field)` repair exists and the raw source field remains blank. A populated source value must never be overwritten.

Unresolved blanks remain null. They must not be replaced with guesses derived from adjacent fields, repeated labels, trainer-owner relationships or external name similarity.

Any later entity-resolution model must be a separate governed programme with explicit authority and provenance.

## Validation evidence

Focused tests:

- `tests/test_connection_identity.py`;
- `tests/test_manual_verifications.py`;
- result: **18 passed**.

Manual-verification register:

- governed rows: **85**;
- confirmed: **56**;
- contradicted: **10**;
- partially confirmed: **1**;
- unresolved: **18**.

Independent source-wide connection validation:

- governed runner rows: **1,851,285**;
- raw blank occurrences: **46**;
- affected source rows: **44**;
- permanent Notebook 20 verification records: **46**;
- governed source supplementations: **28**;
- unresolved preserved blanks: **18**;
- jockey: 2 raw blanks, 2 supplemented, 0 unresolved;
- trainer: 9 raw blanks, 4 supplemented, 5 unresolved;
- owner: 35 raw blanks, 22 supplemented, 13 unresolved.

Both governed reference files were written, reloaded, committed and pushed. The local working tree was clean after the push.

## Limitations

- Source labels are not canonical identities.
- Exact text can refer to different real-world entities.
- One real-world entity can appear under multiple labels.
- Shared surnames, initials, punctuation and partnership formatting cannot be resolved safely from source text alone.
- Owner labels may represent people, organisations, partnerships, syndicates or other arrangements without a reliable source-level type marker.
- The 18 unresolved blanks remain deliberately unresolved.

## Deferred work

Canonical identity resolution for jockeys, trainers, owners, partnerships, syndicates and organisations is deferred until after the source-field series and target database architecture are complete.

The complete repository test suite and all-validator sweep remain deferred until the source-field series or repair branch reaches its end, in accordance with project procedure.
