# Notebook 08 Report — Starting Price Parsing

## Conclusion

The source `sp` column cannot be interpreted globally as a conventional runner-level starting-price field.

Its text notation is reproducibly parseable, but its racing and wagering meaning varies by race, course, jurisdiction and market context. The field can contain conventional fixed-odds starting prices, fractionalised tote or pari-mutuel returns, winner-only returns, limited leading-finisher returns and favourite markers without a numeric price.

A parsed fraction therefore establishes the arithmetic meaning of the stored source expression. It does not independently establish the original market type or make prices directly comparable across jurisdictions.

## Supporting evidence

- All 1,851,285 data-like runner records store `sp` as SQLite text.
- The source contains 843 distinct raw values.
- There are no SQL `NULL` values.
- There are 9,097 explicit empty strings.
- There are no whitespace-only values or values with outer whitespace.
- 1,842,187 runner records contain a reproducibly parsed numeric fraction.
- One runner record contains a standalone favourite marker, `F`, without a numeric source value.
- Zero current records contain an unsupported notation structure.
- 77,468 records contain valid fractions that are not in lowest terms.
- Textual even-money values occur as `Evs`, `EvensF` and `EvsJ`.
- Terminal favourite markers occur as `F`, `J` and `C`.
- Marker-count behaviour is not perfectly uniform across races or jurisdictions.
- Independent notebook assertions pass across the complete runner-record population.
- The notebook passed Restart Kernel and Run All Cells without error.

## Reproducible representation rule

The current fractional notation has the form:

    <numerator>/<denominator>[optional marker]

where:

- numerator and denominator are positive integers;
- the optional terminal marker is `F`, `J` or `C`;
- fractions are not required to be in lowest terms.

Textual even-money expressions map arithmetically to `1/1`, while their exact raw notation and marker remain preserved.

The parser retains:

- exact raw `sp`;
- notation family;
- raw numerator;
- raw denominator;
- literal favourite marker;
- parse status;
- anomaly flags.

Unsupported future values remain unresolved rather than being trimmed, normalised or guessed.

## Mixed field semantics

Race-context and external inspection established that `sp` may represent:

- a conventional fixed-odds starting price;
- a fractional representation of a tote or pari-mutuel dividend;
- a return supplied only for the winner;
- returns supplied for a limited group of leading finishers;
- a favourite marker without a numeric source value;
- no value because the runner was excluded from wagering;
- no supplied race-level price or return;
- an unexplained source omission.

The field name `sp` therefore overstates the uniformity of the underlying information.

## Race-level coverage

Across 189,043 provisional races:

- 188,148 have complete nonblank coverage;
- 701 have all runners blank;
- 122 have a nonblank value for the winner only;
- 53 have nonblank values for a contiguous group of leading finishers;
- 19 have irregular partial coverage.

These patterns occur overwhelmingly in complete race extracts and are geographically concentrated. They are genuine source behaviour rather than merely missing physical runner rows.

Winner-only coverage is concentrated particularly at Monterrico, several French regional courses and St Moritz.

Leading-finisher coverage is concentrated particularly at San Isidro, with smaller clusters across France, Japan, Hong Kong, North America, Australia and Germany.

## Known exception

The one standalone `F` value belongs to Almendares in the 2025 Wickerr Stakes at Del Mar.

The raw source string contains favourite status but no numeric price. External verification established a returned price of `5/2 favourite`.

That evidence must be retained as a separate external correction or enrichment record. The parser must not infer that a standalone `F` generally means `5/2`.

## Database consequence

Later processing must preserve:

- exact raw `sp`;
- parsed arithmetic components;
- exact unreduced numerator and denominator;
- literal favourite marker;
- parse status and anomaly flags;
- race-level price-coverage pattern;
- market or return type when independently supported;
- wagering applicability when independently supported;
- external corrections as separate audit records;
- evidence source and confidence.

Empty strings must not be collapsed into one undifferentiated missing-value category.

No final target schema was designed in this notebook.

## Confidence

**High** for parsing the arithmetic structure of all current nonblank numeric expressions.

**High** for identifying the current notation families, favourite markers and race-level coverage patterns.

**High** that the field has mixed semantics and is not globally a conventional starting-price field.

**Low or unknown** for assigning a market type solely from the stored fraction without jurisdictional and race-level context.

## Next action

Create Notebook 09 as a bounded study of:

    Course Jurisdiction, Racing Authority and Betting-Market Context

That study should classify the context required to interpret international distance, carried weight and source price-or-return fields. It must precede treating those values as directly comparable across jurisdictions.
