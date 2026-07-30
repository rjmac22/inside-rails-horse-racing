# Course Location and Timezone Database Integration

## Scope

Notebook 12 produced a governed course-location reference at `data/reference/course_locations.csv`. Its minimum operational purpose is to assign an IANA timezone to each jurisdiction-qualified candidate course identity.

The reference is enrichment. It must not replace the source `course`, `date` or `off` values.

## Canonical identity and source-facing join

The governed reference identity is exactly:

- `candidate_course_label`
- `candidate_jurisdiction`

Canonical venue identity and raw source course text are separate concepts. `raw_course_labels` is retained as construction provenance; it is not a production join key.

A source-facing join must:

1. preserve raw `course` unchanged;
2. derive `candidate_course_label` with `derive_candidate_course_label()`;
3. derive `candidate_jurisdiction` and its evidence with `derive_candidate_race_jurisdiction()` using the available race context;
4. join the canonical pair to `course_locations.csv` with many-to-one validation;
5. retain an explicit unmatched residue for review;
6. fail in strict validation contexts when any source identity has zero matches.

Use `merge_source_course_locations()` for raw source rows. Use `merge_course_locations()` only for rows that already contain the governed canonical identity.

The reference must contain no duplicate identity pairs. Duplicate reference matches fail through the many-to-one merge contract.

## Required source context

Source-facing derivation requires:

- `course`
- `date`
- `type`
- `race_name`

The context is required because some unsuffixed labels are resolved through historical or race-context rules rather than terminal jurisdiction suffixes.

## Required preservation

Retain separately:

- raw source course text;
- candidate course label and jurisdiction;
- jurisdiction derivation evidence;
- IANA timezone;
- location resolution method and evidence;
- validation status;
- optional venue name, locality, region, country and coordinates.

Coordinates are nullable because timezone sufficiency and exact geospatial completeness are different requirements.

## Unmatched residue

`merge_source_course_locations()` adds `course_location_match_status`. `unmatched_source_course_locations()` returns the distinct raw labels and derived identities that did not match.

A new source extract may legitimately introduce unmatched identities. They must remain visible for governed review and must never be dropped, guessed or converted into nulls without an explicit residue.

Strict validators set `require_all_matches=True` or fail after inspecting the residue.

## Current governed baseline

The permanent reference validator expects:

- 395 unique course identities;
- 395 assigned timezones;
- zero unresolved timezone assignments;
- 51 distinct valid IANA timezone names.

The source-wide join baseline expects:

- 528 distinct raw course labels in the current extract;
- zero unmatched raw labels;
- zero raw labels mapping to multiple governed identities.

The earlier Notebook 12 closeout record reported 394 identities. The durable validator reflects the later permanent reference and is the current baseline. Any count change must be explained by a reviewed reference or source update rather than silently accepted.

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
9. run `scripts/validate_course_locations_source.py`;
10. review any identity-count, raw-label-count or timezone-count change before rebuilding downstream timestamps.

Do not rerun the historical global geocoding exercise merely because one new identity appears. Resolve the finite unmatched residue and preserve the evidence.

## Failure policy

The load or validation step must fail for:

- missing required columns;
- duplicate identity pairs;
- invalid IANA timezone names;
- latitude outside -90 to 90;
- longitude outside -180 to 180;
- unexpected current identity, raw-label or timezone counts;
- unresolved timezone assignments in the governed permanent reference;
- zero source matches in strict mode;
- one raw source label mapping to multiple governed identities.

A future historical venue change may require effective-period rows. It must not be represented by duplicate undated identity rows.

## Notebook 14 correction

The archived Notebook 14 construction record joined raw `course` directly to the provenance column `raw_course_labels`. That produced seven false unmatched labels: Bordeaux Le Bouscat, Chukyo, Cidade Jardim, Hipodromo Chile, Les Landes, Monterrico and Nakayama.

Those labels already resolve through the governed course-jurisdiction rules and canonical identity reference. The archived notebook is not being represented as freshly rerun; its direct-join conclusion is superseded by the reusable source-facing join and source-wide validator.
