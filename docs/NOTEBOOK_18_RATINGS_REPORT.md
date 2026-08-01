# Notebook 18 — Ratings Semantics and Availability

## Executive conclusion

The source contains three useful runner-level rating fields, but they describe different things and cannot safely be collapsed into one rating.

- `or` is the official handicap mark applicable before the race.
- `rpr` is Racing Post's retrospective assessment of the completed performance.
- `ts` is Racing Post's retrospective speed figure for that performance.

The database should retain all three as separate nullable fields with their own raw values and availability statuses.

## What the source actually stores

Across 1,851,285 governed runner rows, every physical cell in `or`, `rpr` and `ts` contains either an integer or the Unicode en dash `–`.

The en dash means the rating is unavailable. It is not zero and should become a null analytical value while the raw token remains preserved.

After excluding one exact invalid source value, the observed numeric candidate ranges are:

- `or`: 1–181;
- `rpr`: 1–184;
- `ts`: 1–178.

These are descriptions of the current source, not permanent universal limits.

## The isolated RPR defect

One row stores `rpr = 775` for Si Capo Si (FR) at Deauville on 3 January 2025.

It is the only RPR above 184 in the complete governed source. Other runners in the race and the horse's surrounding performances remain on the normal scale. The value is therefore unsuitable for analysis.

The safe treatment is to preserve `775` as the raw value, return a null analytical RPR, mark the row `invalid_source_value`, and leave the intended replacement unresolved. Guessing that it means 75 would create unsupported data.

## Availability is structured

Only 847,923 runner rows, or 45.80%, have usable candidates in all three rating fields.

This is not a data failure by itself. The fields have different producers, purposes and timing, so one can be present while another is absent.

The practical consequences are:

- missingness must remain field-specific;
- analyses requiring all three ratings use a selected minority of the source;
- no generic `rating_available` flag should replace the three statuses;
- a runner record remains usable when only one or two ratings are present.

## Database decision

The governed model should preserve:

- immutable `raw_or`, `raw_rpr` and `raw_ts`;
- nullable analytical `or`, `rpr` and `ts`;
- independent status columns;
- exact source lineage;
- the lineage-bound invalid-RPR exception.

The model should not:

- convert unavailable ratings to zero;
- overwrite the raw source;
- treat official ratings, performance ratings and speed figures as interchangeable;
- infer a replacement for the invalid RPR;
- require all three fields for analytical use.

## Limitations

Notebook 18 establishes source semantics and governance. It does not establish predictive value, betting profitability, jurisdiction-specific coverage, race-type coverage, historical revision behaviour, or incremental information between the three ratings.

Those are later analytical questions. The present result is the controlled foundation needed to study them without corrupting the source meaning.
