# Notebook 16 — Race classification and eligibility

## Executive conclusion

The source fields `class`, `pattern`, `rating_band`, `age_band` and `sex_rest` contain useful structured information, but they do not form one universal official classification or eligibility system.

The correct database treatment is to preserve every raw value, parse only stable observed syntax, retain unresolved forms explicitly, and require jurisdiction-specific evidence before making stronger semantic or eligibility claims.

## Core evidence

The study covered 1,851,285 governed runner rows grouped into 189,043 provisional races by `date + course + off`.

All investigated race-level fields were internally constant within those provisional race groups.

Availability differed materially:

- `race_name` and `type`: 189,043 races;
- `class`: 119,836 races;
- `pattern`: 27,191 races;
- `rating_band`: 81,403 races;
- `age_band`: 189,030 races, with 13 blank;
- `sex_rest`: 25,585 races.

Observed structural vocabularies were bounded:

- `type`: Flat, Hurdle, Chase and NH Flat;
- `class`: Class 1 through Class 7;
- `pattern`: Listed, Group 1–3, Grade 1–3 and Grade A–C;
- `rating_band`: 381 canonical `N-N` ranges plus `--` and `(75-100)`;
- `age_band`: exact ages, open-ended minimum ages and closed age ranges;
- `sex_rest`: `F`, `M`, `F & M`, `C & G` and `C & F`.

There were 6,387 races with both `class` and `pattern`, showing that those fields describe different properties. Rating bands overlapped across classes and were absent for many races, including NH Flat races, so they cannot be used as a substitute for class.

## Interpretation

### Classification

`class`, `pattern` and `rating_band` are complementary source fields. Their syntax can be parsed, but their deeper meaning depends on jurisdiction, race type, authority and period.

Group and Grade labels remain distinct. International Class 1 values are not assumed equivalent to British Class 1.

### Age conditions

The source age-band syntax is stable enough to parse into stated bounds. It is not safe to enforce those bounds universally against source runner ages.

The study found 958 apparent runner-age disagreements across 183 races. External verification established multiple causes rather than one universal defect:

- a dropped plus sign (`NB16-AGE-0001`);
- an implausible source runner age (`NB16-AGE-0002`);
- contextual age-condition semantics alongside older runners (`NB16-AGE-0003`);
- an unresolved feed or jurisdiction discrepancy (`NB16-AGE-0004`).

### Sex restrictions

`sex_rest` is source shorthand for an official sex-related condition, not the complete official condition itself.

The value `F` is overloaded. It appears on races described as fillies, fillies and mares, and colts and fillies. Literal `C & F` appears only from 26 October 2025 and is used selectively rather than as a complete historical coding change.

Raw-category analysis remains possible, but authoritative global sex-eligibility reconstruction is not supported by this field alone.

## Confidence

Confidence is high in source coverage, observed vocabularies, race-level consistency, canonical syntax parsing and the recorded anomalies with governed evidence.

Confidence is moderate in broader semantic interpretation because classification and eligibility systems vary by jurisdiction and source convention.

Confidence remains low or unresolved for unusual international forms and any attempt to reconstruct complete official eligibility from shorthand alone.

## Limitations

The source does not provide full governing-authority race conditions in a standard structured form. Race-name wording can support review but can also contain sponsorship or title phrases unrelated to conditions.

The source runner `age` field can itself be wrong. Therefore, a disagreement between `age` and `age_band` does not identify which side is wrong without external evidence.

Blank `sex_rest` must not automatically be interpreted as unrestricted.

## Database consequence

The processed database should preserve raw values and add separately named parser outputs and statuses. It should not overwrite source values or present derived values as source-original.

The reusable implementation is in `src/inside_rails/race_classification.py`, with focused tests, a full-source validator and the integration contract in `docs/RACE_CLASSIFICATION_DATABASE_INTEGRATION.md`.

Any external correction must retain verification ID, method, confidence and source-versus-reconciled status.

## Practical implication

These fields can support descriptive work and carefully bounded jurisdiction-specific studies. They cannot, by themselves, justify a global quality ranking, automatic eligibility decisions or betting conclusions based on labels alone.

A future authoritative sex-condition study should use official race-condition text and governing-authority provenance for one jurisdiction and period at a time.

## Next action

Complete the fresh-kernel Notebook 16 execution and persisted-output reload check, then begin the next bounded source-field study: runner characteristics and equipment.
