# Race Result Database Integration

## Scope

This document implements the durable database consequence of Notebook 05.

The source `pos` field carries several different kinds of information:

- positive numeric finishing positions;
- a zero sentinel;
- disqualification;
- textual non-finish outcomes;
- missing values.

These must not be collapsed into one nullable integer.

## Governed transformation

`src/inside_rails/race_results.py` returns:

- `raw_pos` — exact source value;
- `result_kind` — governed representation category;
- `finish_position` — populated only for positive numeric positions;
- `outcome_code` — populated for zero, disqualification and textual outcomes.

Textual codes are upper-cased for comparison while the exact raw value remains retained.

Unknown future textual codes are preserved as `non_finish_outcome`. They are not rejected or assigned a guessed meaning.

## Recommended staging fields

A runner-result staging record should include:

- `raw_pos`;
- `result_kind`;
- `finish_position`;
- `outcome_code`;
- raw `ran`;
- raw `btn`;
- raw `ovr_btn`;
- source lineage and runner-record surrogate identifier.

Suggested constraints:

- `finish_position` is positive when populated;
- `finish_position` is populated only when `result_kind = 'finish_position'`;
- `outcome_code` is null for numeric finishing positions and missing values;
- `raw_pos` is always retained.

## Dead heats

Equal positive finishing positions within a race are valid and must not be forced into a unique sequence. A race-level uniqueness constraint on finishing position would therefore be incorrect.

## Disqualification

`DSQ` is represented separately from other textual outcomes because it is an amended or governed result status rather than simply failure to complete.

No attempt is made here to reconstruct an earlier placing before disqualification.

## Zero values

The eight observed zero values are preserved as `zero_sentinel`. They are not accepted as finishing position zero and are not silently converted to missing.

## Beaten-distance fields

Notebook 05 established that `btn` and `ovr_btn` cannot be forced into one universal exact-addition rule. This parser therefore does not derive or overwrite either value.

Both raw fields remain available for a later bounded implementation and anomaly reconciliation.

## Source replacement and updates

For every replacement or extended source snapshot:

1. preserve the new raw `pos` values unchanged;
2. run unit tests;
3. run `scripts/validate_race_results.py`;
4. compare category totals and distinct textual codes with the previous snapshot;
5. inspect new textual codes before adding semantic descriptions;
6. do not change historical meanings merely to make a new snapshot pass.

## Validation

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_race_results.py

PYTHONPATH=src .venv/bin/python scripts/validate_race_results.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

The source-wide validator requires every data row to fall into exactly one governed representation category.
