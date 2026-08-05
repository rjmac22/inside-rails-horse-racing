# Connections and Ownership Identity Integration

## Purpose

This document records the database consequence of Notebook 20 for the runner-level source fields `jockey`, `trainer` and `owner`.

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
- affected runner rows: 44.

The 46 blank occurrences occupy 44 rows because source rows `203870` and `203991` each contain both a blank trainer and a blank owner.

Manual review produced:

- 28 confirmed source supplementations;
- 5 conflicting-evidence cases;
- 13 insufficient-evidence cases.

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

Empty strings may be represented as analytical nulls, but the immutable raw value and original blank state must remain recoverable.

## Governed reference data

### Manual-verification register

The 46 external checks are permanently recorded in:

`data/reference/manual_verifications.csv`

Permanent identifiers are `NB20-CONNECTION-0001` through `NB20-CONNECTION-0046`.

Confirmed rows authorise only `source_supplementation`. Conflicting or insufficient rows authorise only `preserve_raw_unresolved`.

### Connection repair reference

The 28 confirmed blank-field supplementations are recorded in:

`data/reference/connection_identity_repairs.csv`

The reference grain is one row per exact `(source_rowid, source_field)` pair. A repair row retains:

- permanent `verification_id`;
- original Notebook 20 `repair_record_id`;
- source race and runner locators;
- blank raw source value;
- governed supplemented value;
- evidence type and locator;
- evidence access date;
- confidence;
- notes;
- authorised database action.

## Promotion history

The original notebook evidence queue was promoted once into the two permanent governed references above. The local construction log lived under ignored `data/derived/` storage and is not present in a clean checkout.

The completed one-time promotion utility has therefore been retired. Current validation must start from the permanent register and repair reference; it must not depend on reconstructing already-promoted rows from an absent local notebook file.

Future source changes follow the governed update procedure below and require explicit new evidence. They are not handled by replaying the historical Notebook 20 promotion.

## Clean-layer fields

For each source connection field, expose:

- `<field>_raw` — immutable source-present value;
- `<field>_governed` — source value when present, otherwise an approved supplementation, otherwise null;
- `<field>_value_status` — `source_present`, `externally_supplemented`, or `source_blank_unresolved`;
- `<field>_verification_id` — populated only for external supplementation;
- `<field>_confidence` — populated only for external supplementation.

The clean layer must not describe an externally supplied value as source-original.

## Application rule

A governed supplementation may be applied only when all of the following match:

1. exact `source_rowid`;
2. exact `source_field`;
3. the immutable source field is null, empty or whitespace-only;
4. the reference verification status is `confirmed`;
5. the authorised action is `source_supplementation`.

If the source field has become populated, processing must fail rather than overwrite it.

The implementation is provided by `src/inside_rails/connection_identity.py`.

## Exact decision-closure contract

`scripts/validate_connection_identity.py` must prove:

- the exact 46 verification IDs;
- the exact 28 verified / 5 conflicting / 13 insufficient decision partition;
- one and only one governed decision for every raw blank `(source_rowid, source_field)` occurrence;
- exact race and runner locator agreement for all 46 cases;
- exact agreement between all 28 confirmed manual decisions and usable repair rows;
- exclusion of every unresolved decision from the repair reference;
- no repair against a populated raw field;
- exact field totals of 2 jockey, 4 trainer and 22 owner supplementations.

Counts alone are insufficient if any raw blank is omitted, duplicated or assigned to the wrong decision.

## Atomic label treatment

Raw and governed connection labels remain atomic text assertions. Do not automatically:

- split trainer labels on `&`;
- expand compressed shared surnames;
- split owner labels into people or organisations;
- sort owner tokens;
- merge punctuation, case or spacing variants;
- share a canonical identity merely because exact text appears in more than one role;
- infer that a no-keyword owner label represents one person.

Any later person, partnership, syndicate, organisation or licence model requires a separate governed identity-resolution programme.

## Data types and null treatment

Recommended logical types are:

- raw and governed labels: nullable text;
- value status: constrained text enumeration;
- verification ID: nullable foreign key to the manual-verification register;
- confidence: nullable constrained text (`high`, `medium`, `low`).

Unresolved blanks remain null. They must not become unknown-person entities or guesses derived from adjacent fields.

## Cardinality and constraints

The database build must enforce:

- one raw runner record per immutable `source_rowid`;
- at most one governed repair per `(source_rowid, source_field)`;
- `source_field` limited to `jockey`, `trainer`, `owner`;
- a nonblank governed value for every repair;
- a direct evidence URL for every confirmed repair;
- no repair against a populated raw source value;
- every repair verification ID present as a confirmed Notebook 20 manual record;
- every unresolved Notebook 20 verification excluded from the repair reference.

## Rebuild consequence

Any derived runner table that converts source blanks directly to final nulls must be rebuilt after introducing the repair reference.

No table should group or join connection histories on raw labels as though they were canonical real-world identities.

## Source-update procedure

When a new source extract arrives:

1. run the independent connection validator before changing a baseline;
2. identify new or changed blank connection fields;
3. confirm whether each existing repair still points to the same immutable runner;
4. fail if a repair target has become populated or its locators changed;
5. research only the new or changed residue;
6. add one permanent manual-verification row per bounded external check;
7. add only confirmed blank-field supplementations to the repair reference;
8. preserve conflicting and insufficient cases as unresolved;
9. run focused tests and both independent validators;
10. rebuild dependent clean runner tables;
11. compare raw blanks, supplementations and unresolved counts with the previous version;
12. commit the evidence register and repair reference together.

Expected counts must never be changed merely to make validation pass.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_connection_identity.py \
  tests/test_manual_verifications.py

PYTHONPATH=src .venv/bin/python scripts/validate_manual_verifications.py
PYTHONPATH=src .venv/bin/python scripts/validate_connection_identity.py
```

No historical promotion command is part of clean-checkout validation.
