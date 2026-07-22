# Notebook 06 Report — Race Distance Parsing

## Conclusion

The source `dist` field is complete, internally consistent and reproducibly parseable for the current extract.

All 189,043 provisional races use one of 63 validated miles-and-furlongs expressions. These values can be converted exactly into source-implied yards and deterministically into source-implied metres.

Those conversions describe the source expression. They do not necessarily reproduce the original official scheduled distance for international races from jurisdictions that commonly publish distances metrically.

## Supporting evidence

- All 1,851,285 source runner records contain a non-blank text `dist` value.
- Every provisional race contains one consistent raw distance.
- The source contains 63 distinct raw distance values.
- All 63 values parse successfully.
- All 189,043 provisional races receive source-implied yards and metres.
- Zero current-source races remain unresolved.
- The standalone validation script passes across the complete race population.
- All parser results explicitly retain `official_distance_verified = False`.
- External checks confirmed examples of official 1,600-metre races represented by the source as `1m`.

## Interpretation

The raw `dist` field is reliable evidence of how this source represented the scheduled race distance.

`source_implied_yards` is an exact conversion of that source expression.

`source_implied_metres` is a literal SI conversion of the source expression, not an independently verified official measurement.

The source representation is suitable for early UK and Irish analytical work, provided the raw value and provenance warning remain visible.

Exact official distances for metric jurisdictions require a separate later enrichment process.

## Database consequence

A later staging implementation should preserve:

- exact raw `dist`;
- parsed miles;
- parsed whole furlongs;
- half-furlong indicator;
- total furlongs;
- source-implied yards;
- source-implied metres;
- parse status;
- official-distance verification status;
- separately enriched official distance and original unit when available.

Previously unseen values must remain unresolved until reviewed.

An official distance must never be populated merely by converting the source expression.

## Confidence

**High** for parsing and literal conversion of the current source representation.

**Low or unknown** for treating source-implied values as exact official distances outside jurisdictions where the source convention has been independently validated.

## Next action

Run Notebook 06 from a clean kernel and confirm the notebook and independent validation complete without error. Then mark the closeout record complete and begin the carried-weight parsing study.
