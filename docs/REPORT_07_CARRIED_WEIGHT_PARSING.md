# Notebook 07 Report — Carried Weight Parsing

## Conclusion

The source `wgt` field is complete, internally consistent and reproducibly parseable for the current extract.

All 1,851,285 data-like runner records use one of 79 canonical stones-and-pounds expressions. Each current value can be converted exactly into source-implied total pounds and deterministically into source-implied kilograms.

Those conversions describe the stored source expression. For jurisdictions that ordinarily publish carried weight in kilograms, the converted SI value must not be treated as a recovered or independently verified official metric declaration.

## Supporting evidence

- All 1,851,285 source runner records store `wgt` as non-blank SQLite text.
- The source contains 79 distinct raw weight values.
- Every current value uses canonical integer-hyphen-integer notation.
- The left component ranges from 6 to 12 stones.
- The right component covers 0 through 13 pounds and never exceeds 13.
- All 79 current values map one-to-one onto 79 source-implied total-pound values.
- All 1,851,285 current runner records parse successfully.
- Zero current-source records remain unresolved.
- Independent Python and SQLite calculations agree for every current value.
- The standalone validation script passes across the complete runner-record population.
- All parser results explicitly retain `official_weight_verified = False`.

## Interpretation

The raw `wgt` field is reliable evidence of how this source represented carried weight.

`source_implied_total_pounds` is the exact interpretation of the stored stones-and-pounds expression:

    source_implied_total_pounds = (parsed_stones × 14) + parsed_pounds

`source_implied_kilograms` is a literal SI conversion:

    source_implied_kilograms = source_implied_total_pounds × 0.45359237

The converted kilograms are suitable as a consistent analytical variable. They do not prove that an international race's original official weight was declared at that exact decimal value. An upstream conversion from kilograms to whole pounds may have introduced rounding before the value entered this extract.

Unusual extreme values and large within-race spreads were inspected. They remained structurally valid and generally coherent within their race contexts. Contextual anomalies in other source fields must therefore remain separate from weight parse validity.

## Database consequence

A later staging implementation should preserve:

- exact raw `wgt`;
- detected notation family;
- parsed stones;
- parsed pounds;
- source-implied total pounds;
- source-implied kilograms;
- parse status;
- ambiguity flag;
- anomaly flags;
- official-weight verification status;
- separately enriched official carried weight and original unit when available.

The parser should accept only canonical stones-and-pounds notation with a pounds component from 0 through 13.

Previously unseen values may parse when they use that unambiguous canonical structure. Unsupported values must remain unresolved rather than being trimmed, normalised or guessed. This includes metric unit text, pounds-only values, decimal or fractional notation, leading-zero variants, whitespace variants, non-text values and invalid pounds components.

## Confidence

**High** for parsing and literal conversion of the current source representation.

**High** for using source-implied kilograms as a consistent analytical conversion of the stored value.

**Low or unknown** for treating reconverted kilograms as the exact original official declaration in jurisdictions whose native publication convention is metric.

## Next action

Notebook 07 has passed a clean-kernel Run All and independent complete-source validation. Close out the notebook and begin Notebook 08 as a bounded study of starting-price parsing.