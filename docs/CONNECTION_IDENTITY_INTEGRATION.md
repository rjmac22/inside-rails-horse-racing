# Connections and Ownership Identity Integration

## Purpose

This document records the database consequence of Notebook 20 for the runner-level source fields:

- `jockey`;
- `trainer`;
- `owner`.

The fields are source-presented connection labels. They are not canonical identifiers for people, partnerships, syndicates, licences or organisations.

## Governed population

The immutable source population is:

- source table: `data`;
- governed predicate: `rowid <> 1`;
- runner rows: 1,851,285.

Observed raw blank counts are:

- `jockey`: 2;
- `trainer`: 9;
- `owner`: 35;
- total blank field occurrences: 46;
- affected runner rows: 43.

Manual review produced:

- 28 confirmed source supplementations;
- 5 conflicting-evidence trainer records;
- 13 insufficient-evidence owner records.

The unresolved 18 fields remain null in the governed layer.

## Immutable raw fields

The future database must preserve, without rewriting:

- source database identifier;
- source table identifier;
- `source_rowid`;
- supplied `race_id`;
- raw `jockey`;
- raw `trainer`;
- raw `owner`.

Empty strings may be represented as analytical nulls, but the immutable raw value and its original blank state must remain recoverable.

## Governed reference data

### Manual-verification register

The 46 external checks are recorded in:

`data/reference/manual_verifications.csv`

Permanent identifiers use:

`NB20-CONNECTION-0001` through `NB20-CONNECTION-0046`.

Confirmed rows authorise `source_supplementation`. Conflicting or insufficient rows authorise only `preserve_raw_unresolved`.

### Connection repair reference

The 28 confirmed blank-field supplementations are recorded in:

`data/reference/connection_identity_repairs.csv`

The reference grain is one row per:

- exact immutable `source_rowid`;
- exact `source_field`.

The pair `(source_rowid, source_field)` must be unique.

A repair row must retain:

- permanent `verification_id`;
- original Notebook 20 `repair_record_id`;
- source race and runner locators;
- blank raw source value;
- governed supplemented value;
- evidence type and locator;
- evidence-access date;
- confidence;
- notes;
- authorised database action.

## Clean-layer fields

For each source connection field, the clean runner layer should expose:

- `<field>_raw` — immutable source-present value;
- `<field>_governed` — source value when present, otherwise an approved supplemented value, otherwise null;
- `<field>_value_status` — one of:
  - `source_present`;
  - `externally_supplemented`;
  - `source_blank_unresolved`;
- `<field>_verification_id` — populated only for external supplementation;
- `<field>_confidence` — populated only for external supplementation.

The clean layer must not describe an externally supplied value as source-original.

## Application rule

A governed supplementation may be applied only when all of the following match:

1. `source_rowid`;
2. `source_field`;
3. the immutable source field is null, empty or whitespace-only;
4. the reference verification status is `confirmed`;
5. the authorised action is `source_supplementation`.

If the source field has become populated, processing must fail rather than overwrite it.

The implementation is provided by:

`src/inside_rails/connection_identity.py`

## Atomic label treatment

Raw and governed connection labels remain atomic text assertions.

Do not automatically:

- split trainer labels on `&`;
- expand compressed shared surnames;
- split owner labels into people or organisations;
- sort owner tokens;
- merge punctuation, case or spacing variants;
- share a canonical entity identifier merely because exact text appears in more than one role;
- infer that a no-keyword owner label represents one person.

Any later person, partnership, syndicate, organisation or licence model requires a separate governed identity-resolution programme.

## Data types and null treatment

Recommended logical types are:

- raw and governed connection labels: nullable text;
- value status: constrained text enumeration;
- verification identifier: nullable text foreign key to the manual-verification register;
- confidence: nullable constrained text (`high`, `medium`, `low`).

Unresolved blanks remain null. They must not be converted to empty organisations, unknown-person entities or trainer/owner guesses derived from adjacent fields.

## Cardinality and constraints

The database build must enforce:

- one raw runner record per immutable `source_rowid`;
- at most one governed repair per `(source_rowid, source_field)`;
- `source_field` limited to `jockey`, `trainer`, `owner`;
- a nonblank governed value for every repair;
- a direct evidence URL for every confirmed repair;
- no repair against a populated raw source value;
- every repair `verification_id` present as a confirmed Notebook 20 manual-verification row;
- every unresolved Notebook 20 verification excluded from the repair reference.

## Rebuild consequence

Any existing derived runner table that converts source blanks directly to final nulls must be rebuilt after the connection repair reference is introduced.

No table should group or join connection histories on raw labels as though they were canonical real-world identities.

## Source-update procedure

When a new source extract arrives:

1. run the independent connection validator before changing any baseline;
2. identify new or changed blank `jockey`, `trainer` and `owner` fields;
3. confirm whether an existing `(source_rowid, source_field)` repair still points to the same immutable runner;
4. fail if a repair target has become populated or its race/runner locators have changed;
5. research only the new or changed residue;
6. add one permanent manual-verification row per bounded external check;
7. add only confirmed blank-field supplementations to the repair reference;
8. preserve conflicting and insufficient cases as unresolved;
9. run focused unit tests;
10. run the manual-verification validator;
11. run the independent source-wide connection validator;
12. rebuild dependent clean runner tables;
13. compare raw blanks, supplemented values and unresolved counts with the previous version;
14. commit the evidence register and repair reference together.

Expected counts must never be changed merely to make a new extract pass. Establish the reason for every population change first.

## Validation commands

Promotion from the completed local Notebook 20 evidence log:

```bash
PYTHONPATH=src .venv/bin/python scripts/promote_connection_identity_verifications.py
```

Focused tests:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_connection_identity.py \
  tests/test_manual_verifications.py
```

Register validation:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_manual_verifications.py
```

Independent source-wide validation:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_connection_identity.py
```
