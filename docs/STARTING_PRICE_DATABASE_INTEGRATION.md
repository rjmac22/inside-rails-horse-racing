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
- `starting_price_favourite_marker`
- `starting_price_favourite_status`
- `starting_price_market_context_status`

Exact rational values should be retained as numerator and denominator pairs where practical. Floating-point columns may be added for analysis but must not replace exact components.

## Governed interpretation

- Exact positive-integer fractions such as `7/2` are arithmetic fractional odds.
- `EVS` and `EVENS` are arithmetic evens.
- `F`, `J` and `C` suffixes are preserved separately as favourite-status metadata.
- Blank values are missing, not zero-priced runners.
- Unseen or reformatted text remains unresolved.
- The parser does not infer market provenance, pool type, bookmaker source, overround treatment or comparability between jurisdictions.

## Governed source anomaly

The immutable source contains exactly one raw `sp` value equal to `F` with no numeric price attached.

This row is deliberately left unresolved because:

- `F` identifies favourite status but does not encode odds;
- the actual price was checked manually outside the raw field;
- inserting that researched price into the parser would silently rewrite source data;
- any corrected value belongs in a separate provenance-bearing corrections layer.

The source validator therefore expects exactly one unresolved current value: `{'F': 1}`. Any additional unresolved value, disappearance of this anomaly, or change in its count causes validation to fail and requires investigation.

## Database grain

Starting price belongs to the staged runner record identified by the Notebook 03 runner-record surrogate. It is not a race-level attribute.

## Update path

For every replacement or extended source snapshot:

1. run the unit tests;
2. run `scripts/validate_starting_price.py` against the immutable source;
3. inspect every unresolved current value;
4. require the unresolved set to match the governed anomaly register exactly;
5. extend parsing only after a new representation has been investigated;
6. version any manually researched correction separately from raw parsing;
7. version market-context enrichment separately from arithmetic parsing;
8. rebuild derived fields without altering raw `sp` values.

A newly parseable string must not be accepted merely because it resembles a price. Its source representation and meaning must first be documented.
