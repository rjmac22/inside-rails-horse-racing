# Off-Time Database Integration

## Scope

Notebook 11 established that `off` is a UK-facing advertised or scheduled clock representation, not a guaranteed exact actual-off timestamp.

The source text is fully parseable as clock-shaped data, but values from `1:00` through `12:59` may represent either of two 12-hour branches. The parser must therefore separate deterministic clock parsing from researched branch selection.

## Preserve raw data

Keep source `off` unchanged on the staged race record. Add derived fields rather than replacing it.

Recommended fields:

- `raw_off`
- `off_time_kind`
- `candidate_uk_time_a`
- `candidate_uk_time_b`
- `selected_branch`
- `decision_method`
- `decision_confidence`
- `advertised_start_uk`
- `advertised_start_utc`
- `advertised_start_course_local`
- `course_timezone`
- `temporal_resolution_status`

## Governed rules

- Accept only exact `H:MM` or `HH:MM` text with a valid clock hour and minute.
- Values `00:00`–`00:59` and `13:00`–`23:59` are explicit 24-hour clocks.
- Values `1:00`–`12:59` produce two candidates separated by 12 hours.
- Never select candidate A or B from the raw value alone.
- A branch decision must be supplied by a governed reconstruction rule or evidence record.
- Timezone conversion requires an explicit IANA timezone from the course-location reference.
- Daylight-saving offsets come from the timezone database, not hand-coded offsets.
- Course-local conversion may change the calendar date; this is a derived local-date consequence, not a change to source `date`.
- Unresolved races retain both candidates and no selected canonical timestamp.

## Notebook 11 reconstruction result

The notebook reconstructed 169,465 of 189,043 provisional races and retained 19,578 as unresolved. Those decisions were produced through course-local plausibility, stable post-boundary profiles, explicit 24-hour values and external validation.

The reusable module does not embed those meeting-level decisions as universal rules. It provides the deterministic parser and the timestamp constructor used after a branch and timezone have been governed elsewhere.

## Database grain and joins

`off` belongs to the provisional race grain identified by source `date + course + off`. Temporal enrichment should join one-to-one to the staged race surrogate.

Course timezone must join through the governed candidate course identity and effective course-location reference. Missing or ambiguous course-location joins must leave temporal reconstruction unresolved.

## Update path

For every new source snapshot:

1. preserve the raw `off` value;
2. run `tests/test_off_time.py`;
3. run `scripts/validate_off_time.py` against the immutable source;
4. inspect every newly unresolved clock representation;
5. regenerate candidate branches;
6. rerun the governed course/timezone join;
7. apply only versioned branch-decision rules or evidence records;
8. retain unresolved races rather than guessing;
9. rebuild UK, UTC and course-local timestamps using the current timezone database.

A change in source formatting, course identity, timezone reference or branch-decision evidence must be versioned and revalidated separately.