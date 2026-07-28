# Course Location and Timezone Database Integration

## Scope

Notebook 12 produced a governed course-location reference at `data/reference/course_locations.csv`. Its minimum operational purpose is to assign an IANA timezone to each jurisdiction-qualified candidate course identity.

The reference is enrichment. It must not replace the source `course`, `date` or `off` values.

## Identity and merge grain

Join using exactly:

- `candidate_course_label`
- `candidate_jurisdiction`

The reference must contain no duplicate identity pairs. Race and runner populations may join many rows to one course-reference row. Unmatched source identities must remain visible as unresolved enrichment rather than being dropped or guessed.

## Required preservation

Retain separately:

- raw source course text;
- candidate course label and jurisdiction;
- IANA timezone;
- resolution method and evidence;
- validation status;
- optional venue name, locality, region, country and coordinates.

Coordinates are nullable because timezone sufficiency and exact geospatial completeness are different requirements.

## Current governed baseline

The current validator expects:

- 395 unique course identities;
- 395 assigned timezones;
- zero unresolved timezone assignments;
- 51 distinct valid IANA timezone names.

The earlier Notebook 12 closeout record reported 394 identities. The durable validator reflects the later permanent reference and is the current baseline. Any count change must be explained by a reviewed reference update rather than silently accepted.

## Reference update procedure

For a replacement source extract or newly observed course identity:

1. derive the candidate course label and jurisdiction using the governed course-jurisdiction logic;
2. compare the resulting identity set with `course_locations.csv`;
3. retain all unmatched identities in an explicit review list;
4. research the minimum defensible timezone assignment;
5. record the evidence, resolution method and validation status;
6. append or amend the permanent reference without altering raw source values;
7. run `tests/test_course_locations.py`;
8. run `scripts/validate_course_locations.py`;
9. review any identity-count or timezone-count change before rebuilding downstream timestamps.

Do not rerun the historical global geocoding exercise merely because one new identity appears. Resolve the finite unmatched residue and preserve the evidence.

## Failure policy

The load or validation step must fail for:

- missing required columns;
- duplicate identity pairs;
- invalid IANA timezone names;
- latitude outside -90 to 90;
- longitude outside -180 to 180;
- unexpected current identity or timezone counts;
- unresolved timezone assignments in the governed permanent reference.

A future historical venue change may require effective-period rows. It must not be represented by duplicate undated identity rows.
