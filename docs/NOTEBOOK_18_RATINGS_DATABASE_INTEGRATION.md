# Notebook 18 — Ratings Database Integration

## Decision

The source fields `or`, `rpr` and `ts` are runner-level ratings with distinct meanings, producers and timing. They must remain separate throughout ingestion, storage and analysis.

- `or`: official pre-race handicap mark applicable to the runner for the race.
- `rpr`: retrospective and potentially revisable Racing Post performance rating.
- `ts`: retrospective Racing Post speed figure for the completed performance.

## Required columns

The governed runner model should expose, for each field:

- `raw_or`, `raw_rpr`, `raw_ts`: immutable source representations;
- `or`, `rpr`, `ts`: nullable analytical integers;
- `or_status`, `rpr_status`, `ts_status`: independent interpretation states;
- physical source lineage, including source rowid while this source remains in use.

Permitted statuses established by Notebook 18 are:

- `available`;
- `unavailable`;
- `invalid_source_value`;
- `unresolved_source_value` for unexpected future representations.

## Parsing contract

Use `inside_rails.ratings.parse_rating` or `parse_rating_triplet`.

1. Preserve the raw source value without normalisation.
2. Interpret the exact Unicode en dash `–` as unavailable and return a null analytical value.
3. Preserve integer source values as analytical candidates.
4. Do not convert unavailable values to zero.
5. Do not silently coerce numeric text, ASCII hyphens, blanks, booleans or fractional values.
6. Preserve unexpected future representations with `unresolved_source_value` rather than guessing.

## Exact RPR exception

Source rowid `1619851` stores `rpr = 775` for Si Capo Si (FR), Deauville (FR), 3 January 2025, 4:27.

This is the only RPR above 184 in the 1,851,285-row governed population. The downstream rule is deliberately tied to both exact physical lineage and exact raw value:

- `raw_rpr = 775`;
- analytical `rpr = NULL`;
- `rpr_status = invalid_source_value`;
- replacement status remains unresolved.

Do not globally reject every future value of 775 and do not replace this value with 75 or any other inferred figure.

## Availability and joins

Availability is field-specific. Only 847,923 rows, or 45.80% of the governed source, have usable candidates in all three fields.

Therefore:

- no generic `rating_available` field should replace the three statuses;
- runner usability must not require all three ratings;
- analyses requiring all three fields must disclose the resulting selected population;
- joins and feature views must preserve nullability independently.

## Observed source baselines

After the exact invalid-RPR exclusion:

| Field | Available | Unavailable | Invalid | Observed candidate range |
|---|---:|---:|---:|---:|
| `or` | 1,116,633 | 734,652 | 0 | 1–181 |
| `rpr` | 1,644,175 | 207,109 | 1 | 1–184 |
| `ts` | 1,227,384 | 623,901 | 0 | 1–178 |

These ranges are regression baselines for this immutable source, not universal validity limits for future feeds.

## Evidence and validation

Permanent publisher-reference records:

- `NB18-OR-0001`;
- `NB18-RPR-0001`;
- `NB18-TS-0001`.

Focused implementation tests:

- `tests/test_ratings.py`.

Independent source-wide validation:

- `scripts/validate_ratings.py`.

The manual-verification register remains independently governed by:

- `tests/test_manual_verifications.py`;
- `scripts/validate_manual_verifications.py`.
