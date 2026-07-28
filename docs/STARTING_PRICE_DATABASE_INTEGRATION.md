# Starting Price Database Integration

## Scope

Notebook 08 supports arithmetic parsing of the stored `sp` expression. It does not establish which bookmaker, tote pool, exchange, consensus feed or settlement convention produced the value.

## Preserve raw data

Keep the original `sp` value unchanged on every staged runner record. Derived fields are additive and reproducible.

Recommended derived columns:

- `starting_price_kind`
- `starting_price_numerator`
- `starting_price_denominator`
- `starting_price_fractional_odds`
- `starting_price_decimal_odds`
- `starting_price_implied_probability`
- `starting_price_market_context_status`

Exact rational values should be retained as numerator and denominator pairs where practical. Floating-point columns may be added for analysis but must not replace exact components.

## Governed interpretation

- Exact positive-integer fractions such as `7/2` are arithmetic fractional odds.
- `EVS` and `EVENS` are arithmetic evens.
- Blank values are missing, not zero-priced runners.
- Unseen or reformatted text remains unresolved.
- The parser does not infer market provenance, pool type, bookmaker source, overround treatment or comparability between jurisdictions.

## Database grain

Starting price belongs to the staged runner record identified by the Notebook 03 runner-record surrogate. It is not a race-level attribute.

## Update path

For every replacement or extended source snapshot:

1. run the unit tests;
2. run `scripts/validate_starting_price.py` against the immutable source;
3. inspect every unresolved current value;
4. extend parsing only after the new representation has been investigated;
5. version any market-context enrichment separately from arithmetic parsing;
6. rebuild derived fields without altering raw `sp` values.

A newly parseable string must not be accepted merely because it resembles a price. Its source representation and meaning must first be documented.
