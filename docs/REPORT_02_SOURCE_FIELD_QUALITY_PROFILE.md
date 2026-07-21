# Report 02 — Source Field Quality Profile

## Executive conclusion

The supplied `raceform.db` can support a professional analytical database, but its fields cannot be cleaned safely through generic type conversion or blanket missing-value replacement.

Across the 37 source columns, missingness is represented through field-specific conventions including blank strings, hyphens, en dashes, zeroes and racing outcome codes. Several columns also contain mixed SQLite storage classes despite being declared as numeric.

The correct approach is to preserve every raw value and introduce explicit, tested parsing rules in later domain-specific studies.

## Source examined

`data/raw/form_2015-present/form_2015-present/raceform.db`

Table: `data`

Profiling excluded the imported header row using `rowid <> 1`, leaving:

- 1,851,285 data-like runner rows;
- 189,043 provisional apparent races.

No raw values were changed.

## Overall quality pattern

The source makes no meaningful use of SQL `NULL`. Apparent missingness is instead represented through:

- blank text;
- `-`;
- `–`;
- zeroes;
- racing-specific status codes;
- field-specific conventions.

A generic rule that converts every blank, dash or zero to missing would therefore be unsafe.

Several fields declared as `INTEGER` contain a mixture of integers, real numbers, formatted text and sentinel text. The raw database must consequently be treated as loosely typed source data.

## Race and runner description fields

The provisional combination of `date`, `course`, `off` and `race_name` remains useful for analytical grouping, but it is not yet accepted as a permanent race identifier.

The source contains broad international coverage and jurisdiction-specific formatting. Course, distance, class, going and race-description fields must remain unchanged until dedicated interpretation work is complete.

## Runner identity and demographics

Horse, jockey, trainer, owner, sire, dam and damsire are stored as descriptive text rather than stable entity identifiers.

Pedigree coverage is strong:

- `sire` is fully populated;
- `dam` has 5 blank rows;
- `damsire` has 21 blank rows.

Ownership coverage is also strong, with only 35 blank `owner` rows.

Names should not be treated as durable identity keys because punctuation, abbreviations, spelling variants and collisions may occur.

## Finishing position and outcome fields

`pos` contains both numeric official placings and text status codes.

Observed status codes include `PU`, `F`, `UR`, `BD`, `RR`, `DSQ`, `RO`, `SU`, `REF`, `CO` and `LFT`.

Numeric positions are not guaranteed to be contiguous and can exceed the declared `ran` value where official placings have been revised or gaps remain. Validation rules must therefore not assume `pos <= ran` or contiguous numeric placings.

## Finishing margins

`btn` and `ovr_btn` are numeric for most rows, with `-` used where no distance value is available.

The two fields are generally consistent, although a small number of rows contain minor rounding differences or larger inconsistencies among abnormal and tailed-off performances.

Disqualified runners may retain numeric finishing distances. The fields appear to preserve aspects of the physical finish even where official placings have later changed.

## Race time

`time` is a runner-level elapsed-time field rather than a single race-level winning time.

Findings include:

- 1,756,877 parseable time values;
- 94,408 `-` values;
- a consistent `minutes:seconds.hundredths` format among populated values;
- numeric finishers almost always having parseable times;
- some disqualified runners retaining times.

Runner time is extremely closely related to `ovr_btn`, indicating that it is derived from, or tightly linked to, recorded finishing margins rather than always representing independently measured stopwatch data for each horse.

The raw text should be preserved and later parsed into numeric seconds, but it should not automatically be treated as independent timing evidence.

## Draw, weight and headgear

### `draw`

- 592,778 blank rows;
- otherwise integer values from 1 to 37;
- no invalid populated values identified.

Blank draw values appear to represent races where a draw is not applicable.

### `wgt`

- fully populated;
- stored as stone-pound text;
- stones range from 6 to 12;
- pounds range from 0 to 13.

A later transformation can derive total pounds while retaining the raw value.

### `hg`

- 1,122,490 blank rows;
- compact headgear codes and combinations;
- first-use suffixes such as `1` occur.

This field requires a controlled code dictionary rather than free-form cleaning.

## Starting price

`sp` is mostly fractional-odds text with optional favourite and joint-favourite suffixes, plus even-money variants.

There are 9,097 blank values. One isolated row contains only `F`, which should be retained raw and flagged as malformed or incomplete.

Starting-price parsing should therefore preserve the original string, derive a numeric odds value only where valid, and separately retain favourite markers.

## Prize and rating fields

### `prize`

Prize values use three storage conventions:

- blank text for missing values;
- numeric SQLite values for non-euro amounts;
- euro-prefixed text for euro-denominated amounts.

Euro values may contain decimals and thousands separators. No other non-blank text currency format was identified.

A later transformation should derive separate amount and currency fields while preserving the original value.

### `or`, `rpr` and `ts`

These fields use the en dash `–` as their missing-value marker.

Observed numeric ranges are:

- `or`: 1 to 181;
- `rpr`: 1 to 775;
- `ts`: 1 to 178.

The isolated `rpr = 775` value is an obvious anomaly and should be retained raw but flagged during transformation. The maximum `or = 181` appears twice for the same high-class hurdle horse and is not treated as an obvious source error.

## Pedigree, ownership and comments

All remaining narrative fields are stored consistently as text.

`comment` has 340,394 blank rows. Populated comments range from 1 to 2,206 characters.

The longest comments are legitimate steward-enquiry and running-and-riding notes rather than corrupted text. The full raw comment must therefore be preserved without truncation.

## Decisions made

- Preserve every original raw field.
- Convert known blanks and sentinels only through field-specific rules.
- Use nullable numeric types in later transformed layers.
- Add parsed values alongside raw values rather than replacing source text.
- Add anomaly flags instead of silently correcting questionable values.
- Do not impose assumptions such as contiguous placings or `pos <= ran`.
- Do not treat names as stable entity identifiers.
- Do not truncate long comments.
- Do not begin final target-schema design until race and runner identity are studied directly.

## Confidence

**High confidence** in:

- field-specific missing-value conventions;
- mixed storage classes;
- position and outcome-code behaviour;
- weight, prize, ratings and comment formats;
- the need to preserve raw values.

**Medium confidence** in:

- the exact derivation of runner-level time values;
- the meaning of some jurisdiction-specific headgear and starting-price variants;
- whether all extreme domain values are genuine rather than source errors.

## Practical implication

The next bounded study should examine race identity and source-key reconstruction.

That study should test how races and runner records can be identified across jurisdictions without prematurely designing the final relational schema.
