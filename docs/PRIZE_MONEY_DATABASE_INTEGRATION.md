# Prize-money database integration contract

## Status

This contract implements the governed treatment established in Notebook 13.
The reusable parser is `src/inside_rails/prize_money.py` and the independent
immutable-source validator is `scripts/validate_prize_money.py`.

The source `prize` field is runner-level recorded prize money. It is not the
advertised race purse, total race value, or a guaranteed payment schedule.

## Required runner-level columns

The database build should preserve the following fields separately:

| Column | Suggested type | Meaning |
|---|---:|---|
| `prize_raw` | source-preserving text or typed staging value | Exact source value before interpretation |
| `prize_source_presented_amount` | decimal-compatible staging value | Numeric amount represented by the source, without asserting currency |
| `prize_canonical_minor_units` | nullable integer | Exact pence or cents only when currency is confirmed |
| `prize_currency` | nullable text | ISO 4217 code; currently `GBP` or `EUR` only |
| `prize_interpretation_status` | text | `blank`, `canonical`, `currency_unresolved`, or `invalid` |
| `prize_interpretation_method` | text | Named rule used for the interpretation |
| `prize_conversion_multiplier` | nullable decimal | Reserved for later evidenced reconstruction; currently always null |
| `prize_confidence` | text | `confirmed` or `unresolved` |

`Decimal` values returned by the Python parser should be serialised through a
lossless database adapter or as exact text during staging. Canonical money must
be stored as integer minor units, not floating-point currency.

## Current governed rules

### Great Britain

A non-Boolean numeric source value is interpreted directly as GBP only when:

- the jurisdiction is confirmed as Great Britain;
- the value is finite;
- the value is non-negative;
- it has no precision below one penny.

The method is `direct_gb_numeric_gbp`.

### Ireland

A euro-prefixed text source value is interpreted directly as EUR only when:

- the jurisdiction is confirmed as Ireland;
- the string begins with `€`;
- commas are only presentation separators;
- the remaining value is finite and non-negative;
- it has no precision below one cent.

The method is `direct_ireland_euro_text`.

### Other jurisdictions

A populated numeric-looking value is preserved as a source-presented amount,
but no currency or canonical minor-unit value is assigned. The status is
`currency_unresolved` and the method is
`source_presented_amount_currency_unresolved`.

No currency should be inferred from magnitude, course, race name, date, or an
assumed exchange rate.

### Blanks and invalid values

Blank values remain null with status `blank`; they must never become zero.
Values that do not match a governed rule receive status `invalid` and remain
available through `prize_raw` for review.

## Validated source population

The independent validator opens the immutable SQLite source read-only, derives
the governed candidate jurisdiction for all 189,043 provisional races, and
parses all 1,851,285 runner rows.

The expected current-source partition is:

| Status or method | Runner rows |
|---|---:|
| source blank preserved | 839,715 |
| direct Great Britain GBP parsing | 561,852 |
| direct Ireland EUR parsing | 168,466 |
| source-presented amount with currency unresolved | 281,252 |
| invalid current source rows | 0 |

The source contains 47,215 distinct raw prize values. SQLite storage classes
must remain exactly 225,078 integer rows, 618,026 real rows and 1,008,181 text
rows. Any new status, method, storage-class population or unresolved
jurisdiction is a review event, not a reason to update the baselines blindly.

The validator also enforces:

- exact preservation of every raw value;
- complete partitioning of the governed runner population;
- canonical minor units only for GBP and EUR rows;
- no canonical minor units on blank, unresolved or invalid rows;
- no currency-conversion multiplier on any current row;
- no foreign-exchange reconstruction.

## Race-level aggregation

Any race-level sum derived from runner records must be named explicitly as a
**recorded runner prize total**. It must not be named or described as:

- advertised purse;
- race prize fund;
- total race value;
- guaranteed distributed prize money.

The number of runners with populated prize values is an observed property of
each race and should be stored or calculated alongside any aggregation.

## Build integration pattern

For each source runner row:

```python
from inside_rails.prize_money import parse_prize_money

parsed = parse_prize_money(
    raw_prize=row["prize"],
    candidate_jurisdiction=row["candidate_jurisdiction"],
)
```

Persist the returned fields without replacing the original source value.
Jurisdiction must come from the governed course/jurisdiction mapping rather
than being inferred inside the prize parser.

## Future jurisdiction updates

Later jurisdiction studies may add evidenced rules. Updates must follow this
sequence:

1. preserve the existing raw and source-presented values;
2. add a narrowly scoped jurisdiction-and-period rule;
3. record the interpretation or conversion method by name;
4. retain any multiplier and supporting evidence separately;
5. add tests using confirmed source examples and known exceptions;
6. rerun the focused tests and independent source-wide validator;
7. reprocess affected rows without altering unrelated jurisdictions;
8. compare the complete status, method, currency and storage partitions with the previous version.

Historical transformations must not be represented as direct source currency.
A reconstructed canonical value requires explicit provenance and confidence.

## Validation commands

From the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_prize_money.py
PYTHONPATH=src .venv/bin/python scripts/validate_prize_money.py
```

Both must pass before the parser is used in the database build.
