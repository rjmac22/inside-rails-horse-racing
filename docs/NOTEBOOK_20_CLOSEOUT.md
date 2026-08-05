# Notebook 20 Closeout — Connections and Ownership Identity

## Status

**Fully closed with exact decision validation and clean-checkout promotion retirement.**

Notebook 20 investigated runner-level `jockey`, `trainer` and `owner` fields as source-presented connection labels. It does not treat those labels as canonical person, partnership, syndicate, licence or organisation identifiers.

## Governing conclusion

The three raw fields are suitable for preservation as atomic source text. Exact text equality may support bounded source-label analysis, but it must not be promoted automatically to real-world entity identity.

The immutable source population contains:

- 1,851,285 governed runner rows under `rowid <> 1`;
- 2 blank `jockey` occurrences;
- 9 blank `trainer` occurrences;
- 35 blank `owner` occurrences;
- 46 blank connection-field occurrences across 44 source rows.

## Manual-verification outcome

The exact Notebook 20 decision population is:

- 28 verified repairs;
- 5 conflicting-evidence cases;
- 13 insufficient-evidence cases.

Verified repairs comprise:

- 2 jockey supplementations;
- 4 trainer supplementations;
- 22 owner supplementations.

The remaining 18 blanks stay unresolved:

- 5 trainer blanks;
- 13 owner blanks.

Permanent IDs are `NB20-CONNECTION-0001` through `NB20-CONNECTION-0046` in `data/reference/manual_verifications.csv`.

Confirmed records authorise only `source_supplementation`. Conflicting and insufficient records authorise only `preserve_raw_unresolved`.

## Durable artifacts

- archival notebook: `notebooks/20_connections_and_ownership_identity.ipynb`;
- permanent evidence: `data/reference/manual_verifications.csv`;
- usable repair reference: `data/reference/connection_identity_repairs.csv`;
- reusable module: `src/inside_rails/connection_identity.py`;
- focused tests: `tests/test_connection_identity.py` and `tests/test_manual_verifications.py`;
- independent validators: `scripts/validate_connection_identity.py` and `scripts/validate_manual_verifications.py`;
- integration contract: `docs/CONNECTION_IDENTITY_INTEGRATION.md`;
- this closeout record.

## Promotion-utility retirement

The original one-time promotion utility depended on an ignored local construction file:

`data/derived/connection_identity/manual_connection_repair_evidence_log.csv`

That local evidence queue had already been promoted into the permanent manual register and repair reference, but it was not present in a clean checkout. Continuing to list the promotion utility as a durable validation artifact was therefore incorrect.

The one-time script has been removed. The repository history preserves it as construction provenance. Current validation begins from the two permanent governed references and does not attempt to replay a completed notebook promotion.

## Exact validator closure

The strengthened source-wide validator now enforces:

1. every verification ID from `0001` to `0046` exactly once;
2. the exact 28 verified / 5 conflicting / 13 insufficient partition;
3. exact one-to-one coverage of all 46 raw blank `(source_rowid, source_field)` occurrences;
4. exact source race and runner locators for every decision;
5. exact agreement between all 28 confirmed decisions and usable repair rows;
6. complete exclusion of unresolved decisions from the repair reference;
7. no repair against a populated source field;
8. exact supplementation counts by field.

This protects the governed decisions rather than merely reproducing totals.

## Database consequence

Raw `jockey`, `trainer` and `owner` remain immutable.

A clean runner layer may expose a governed value only when an exact `(source_rowid, source_field)` repair exists and the raw field remains blank. Populated source values must never be overwritten.

Unresolved blanks remain null and must not be replaced with guesses derived from adjacent fields, repeated labels, trainer-owner relationships or name similarity.

Any later entity-resolution model remains a separate governed programme.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_connection_identity.py \
  tests/test_manual_verifications.py

PYTHONPATH=src .venv/bin/python scripts/validate_manual_verifications.py
PYTHONPATH=src .venv/bin/python scripts/validate_connection_identity.py
```

## Limitations

- source labels are not canonical identities;
- exact text can refer to different real-world entities;
- one entity can appear under multiple labels;
- owner labels may represent people, organisations, partnerships or syndicates;
- 18 blank fields remain deliberately unresolved.

The complete repository test suite and all-validator sweep remain deferred until the final repair-series gate.
