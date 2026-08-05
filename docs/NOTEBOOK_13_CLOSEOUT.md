# Notebook 13 Closeout — Prize-Money Semantics and Availability

## Status

**Implementation repaired and prepared for focused local validation.**

Notebook 13 established the meaning and limits of the runner-level `prize` field. The analytical investigation remains closed. This repair replaces the former synthetic smoke validator with an independent immutable-source validator; it does not reopen the notebook or change the governed parsing policy.

## Bounded conclusion

The source field records runner-level prize amounts where supplied. It is not a reliable advertised race purse, total race value or guaranteed payment schedule.

Only two current source conventions are canonicalised:

- Great Britain numeric values become exact GBP minor units;
- Ireland euro-prefixed text values become exact EUR minor units.

Other populated amounts remain source-presented values with currency unresolved. Blank values remain null, never zero. No foreign-exchange reconstruction is authorised.

## Governed source baselines

- governed runner rows: **1,851,285**;
- provisional races: **189,043**;
- blank prize rows: **839,715**;
- populated prize rows: **1,011,570**;
- distinct raw prize values: **47,215**;
- direct Great Britain GBP rows: **561,852**;
- direct Ireland EUR rows: **168,466**;
- currency-unresolved populated rows: **281,252**;
- invalid current-source rows: **0**.

SQLite storage-class baselines are:

- integer: **225,078**;
- real: **618,026**;
- text: **1,008,181**.

## Durable implementation

- parser: `src/inside_rails/prize_money.py`;
- focused tests: `tests/test_prize_money.py`;
- independent validator: `scripts/validate_prize_money.py`;
- integration contract: `docs/PRIZE_MONEY_DATABASE_INTEGRATION.md`.

## Audit defect and repair

The previous validator exercised only four synthetic examples and never opened the immutable source database. It could not support the repository claim of source-wide independent validation.

The replacement validator now:

1. opens the source read-only;
2. reconstructs all 189,043 provisional race jurisdictions through the governed course mapping;
3. parses all 1,851,285 runner rows;
4. checks the exact storage-class, status, method and currency partitions;
5. verifies raw-value preservation;
6. rejects canonical minor units outside governed GBP and EUR rows;
7. enforces zero current invalid rows and zero conversion multipliers;
8. fails on any unresolved race jurisdiction or population drift.

## Manual-verification decision

`not_applicable`

The implemented parsing rules and current source-wide counts are supported by the completed source investigation and governed jurisdiction mapping. No row-level external correction is applied by this notebook.

## Database consequence

Preserve the raw source value and store parsed amount, canonical minor units, currency, status, method and confidence separately. Any race-level sum must be labelled as a **recorded runner prize total**, not a race purse or total race value.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_prize_money.py
PYTHONPATH=src .venv/bin/python scripts/validate_prize_money.py
```

The new source-wide validator must be run against the user's immutable local SQLite database before this review unit is accepted. A complete repository test run remains deferred until the final repair-series gate.
