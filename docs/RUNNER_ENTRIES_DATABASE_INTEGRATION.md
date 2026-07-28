# Runner Counts, Numbers and Entries — Database Integration

## Purpose

This document defines how the governed findings from Notebook 14 should be carried into the eventual Inside Rails database build.

The source fields `ran` and `num` are not interchangeable with clean starter counts or unique runner identifiers. Their raw states, internal consistency and unresolved meaning must remain explicit.

## Source scope

Source database:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Source rows exclude the physical header-like row where `rowid = 1`.

Candidate race identity:

`date + course + off`

Candidate runner identity:

`date + course + off + horse`

The supplied `race_id` and `num` values remain source lineage attributes and must not be used as independent natural keys.

## Race-level storage

The race table or race staging table should preserve the following fields.

### `source_reported_ran`

Integer source-presented race count where one valid value is consistent across the provisional race.

This is not automatically a verified number of starters, declarations, runners in the published result, or rows expected from an external racecard.

### `source_runner_row_count`

Count of stored source runner rows assigned to the provisional race.

This is a physical source count, not a sporting field-size measure.

### `source_ran_distinct_value_count`

Count of distinct valid `ran` values observed within the provisional race.

### `source_ran_consistency_status`

Allowed governed values:

- `consistent`
- `conflicting`
- `invalid`
- `missing`

### `source_row_count_vs_ran_status`

Allowed governed values:

- `equal`
- `below`
- `above`
- `not_comparable`

### `source_runner_coverage_status`

Allowed governed values:

- `unverified`
- `internally_equal_to_ran`
- `known_partial`
- `externally_verified_complete`

Internal equality must never be promoted automatically to external completeness.

### `source_ran_external_status`

Allowed governed values:

- `unverified`
- `externally_verified`
- `externally_contradicted`

This status records evidence about the source-presented count itself and remains separate from stored-row coverage.

## Runner-level storage

The runner table or runner staging table should preserve the following fields.

### `source_num_raw`

The exact source-presented `num` value, including blank text and integer zero.

Do not trim, coerce or replace the raw value before storage.

### `source_num_storage_class`

Python-side staging equivalent of the SQLite storage class:

- `integer`
- `text`
- `null`
- another explicit invalid class where encountered

### `source_positive_runner_number`

Canonical positive integer derived only when the source value is an integer greater than zero.

Blank text, integer zero, null and invalid values produce null here.

### `source_num_state`

Allowed governed values:

- `positive_integer`
- `integer_zero`
- `blank_text`
- `null`
- `invalid`

Blank text and integer zero must remain distinct.

### `source_num_within_race_multiplicity`

For positive integers only, the number of runner rows in the provisional race sharing that same positive value.

Null for nonpositive or invalid states.

### `source_num_uniqueness_status`

Allowed governed values:

- `unassessed`
- `unique_within_race`
- `shared_positive_num`
- `nonpositive_state`

A shared positive number must not automatically be interpreted as a duplicate runner or a confirmed coupled entry.

## Transformation sequence

1. Reconstruct the provisional race identity from `date + course + off`.
2. Group source rows by provisional race.
3. Profile all raw `ran` values with `profile_reported_ran()`.
4. Count positive integer `num` multiplicity within each provisional race.
5. Parse each raw `num` value with `parse_runner_number()` and the supplied multiplicity.
6. Persist the raw fields and all governed derived fields together.
7. Preserve source database, table, row ID and supplied `race_id` for lineage.
8. Do not create runner identity from `num`.

## Prohibited transformations

The database build must not:

- replace blank `num` with zero;
- treat zero as runner number zero;
- accept text such as `1A` as a recoverable canonical number;
- invent coupled-entry suffixes;
- assume every duplicated positive number is a coupled betting interest;
- use race plus `num` as a runner key;
- infer external completeness because stored row count equals `ran`;
- create missing runner records to make row count equal `ran`;
- overwrite raw values with canonical values.

## Update path

For a new source delivery:

1. run the independent source validator;
2. confirm that the observed `ran` domain and `num` storage states remain supported;
3. fail the load on new conflicting, invalid or out-of-policy states unless explicitly reviewed;
4. calculate and persist governed fields using `src/inside_rails/runner_entries.py`;
5. compare source-wide counts with the approved validation baseline;
6. retain new anomalies for review rather than silently coercing them.

## Upstream dependency

Jurisdiction-level summaries depend on the governed course reference resolving every raw source course label through the intended production join.

Notebook 14 exposed seven unresolved course labels. That defect belongs to the course-reference implementation and must be repaired separately. Runner-number parsing must not hard-code jurisdiction aliases to compensate for an incomplete course join.

## Validation assets

Reusable implementation:

`src/inside_rails/runner_entries.py`

Governed unit tests:

`tests/test_runner_entries.py`

Independent validator:

`scripts/validate_runner_entries.py`

Analytical closeout record:

`docs/NOTEBOOK_14_CLOSEOUT.json`
