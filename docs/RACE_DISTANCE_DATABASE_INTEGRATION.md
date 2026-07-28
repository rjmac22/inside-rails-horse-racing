# Race Distance Database Integration

## Purpose

This document governs how the Notebook 06 race-distance parser is used in a later staging database.

The raw `dist` value is always preserved. Derived values describe the literal distance expression supplied by the source; they are not independently verified official race distances.

## Governed implementation

- Parser: `src/inside_rails/race_distance.py`
- Unit tests: `tests/test_race_distance.py`
- Independent validator: `scripts/validate_race_distance.py`
- Source investigation: `notebooks/06_race_distance_parsing.ipynb`

## Staging fields

A race-level staging table should retain or derive the following fields:

| Field | Type | Rule |
|---|---|---|
| `raw_dist` | text | Exact source value, unchanged. |
| `distance_miles_component` | integer, nullable | Parsed whole-mile component. |
| `distance_whole_furlongs_component` | integer, nullable | Parsed whole-furlong remainder. |
| `distance_has_half_furlong` | boolean, nullable | Whether the source expression includes a half furlong. |
| `distance_total_furlongs` | numeric, nullable | Literal source expression converted to furlongs. |
| `distance_source_implied_yards` | integer, nullable | `total_furlongs × 220`. |
| `distance_source_implied_metres` | numeric, nullable | `source_implied_yards × 0.9144`. |
| `distance_official_verified` | boolean | Always false for this parser. |
| `distance_parse_status` | text | `parsed` or `unresolved`. |
| `distance_parser_version` | text | Version or commit of the parser used. |

These attributes belong at race grain and should be joined to runner records through the staging race surrogate identifier.

## Interpretation boundary

`source_implied_yards` and `source_implied_metres` are deterministic conversions of the supplied notation only.

They must not be described as official measured distances because:

- some jurisdictions publish metric distances;
- the upstream provider may have rounded or standardised those values into miles-and-furlongs notation;
- Notebook 06 did not independently reconcile every race to an official authority record.

`distance_official_verified` therefore remains false unless a separate documented enrichment process verifies an official race-level distance.

## Accepted values

The implementation converts only the 63 exact raw values validated in Notebook 06.

The parser intentionally does not normalise case, whitespace, alternative fractions or metric expressions. A previously unseen value remains unresolved and must trigger review rather than silently acquire a guessed interpretation.

## Database constraints

Recommended constraints:

- preserve `raw_dist` even when parsing fails;
- require `distance_parse_status`;
- when status is `parsed`, require all component and converted fields;
- when status is `unresolved`, require those derived fields to be null;
- do not require uniqueness of `raw_dist`;
- do not store derived distance only on runner rows as independent duplicated truth.

## Replacement snapshot procedure

For every replacement or extended source database:

1. run `scripts/validate_race_distance.py`;
2. inventory distinct raw `dist` values;
3. compare them with `VALIDATED_COMPONENTS`;
4. leave new values unresolved;
5. investigate each new form before adding it;
6. add tests for every newly governed grammar or exact value;
7. record the parser version used for the rebuild;
8. rebuild derived staging fields rather than patching the immutable raw source.

A new source value must never be accepted merely because a general regular expression can parse it. Its source meaning and jurisdictional implications must first be reviewed.

## Existing-source validation target

The current immutable source is expected to contain:

- 189,043 provisional races;
- one distance value within every candidate race;
- 63 distinct raw distance values;
- complete parser coverage for all current races;
- source-implied values between 880 and 8,030 yards;
- zero rows marked as independently official-distance verified.
