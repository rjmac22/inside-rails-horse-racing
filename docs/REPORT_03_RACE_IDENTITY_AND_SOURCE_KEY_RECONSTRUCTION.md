# Report 03 — Race Identity and Source-Key Reconstruction

## Executive conclusion

The supplied `race_id` cannot be used as a globally unique race identifier.

It is reused across dates and, in eight cases, identifies two genuinely different races on the same date. The strongest race-matching rule in the current source is:

`date + course + off`

This combination produces 189,043 distinct race groups with no observed collisions. For conservative reconstruction, `race_name` should remain attached as a descriptive validation field.

A runner record can be identified within a reconstructed race by adding `horse`. This produces one unique group for every one of the 1,851,285 data-like source rows.

These are candidate natural matching rules, not permanent database identifiers. A later staging layer should assign surrogate race and runner-record identifiers while preserving the supplied identifiers, descriptive fields and exact source lineage.

## Source examined

`data/raw/form_2015-present/form_2015-present/raceform.db`

Table: `data`

Profiling excluded the imported header row using `rowid <> 1`, leaving:

- 1,851,285 data-like runner rows;
- 189,043 provisional races;
- 4,130 distinct race dates.

The raw database was opened through SQLite read-only mode. No raw values were changed.

## Supplied `race_id` behaviour

The source contains:

- 188,782 distinct `race_id` values;
- 189,035 distinct `date + race_id` combinations;
- 206 identifiers used on more than one date;
- one identifier used on five dates.

Reuse is not limited to repeated versions of one race. The same identifiers are attached to unrelated races across different dates, courses and jurisdictions.

Adding the date does not resolve the problem completely. Eight `date + race_id` combinations each contain two distinct races, including different courses on the same date and two separate races at the same course.

The supplied `race_id` must therefore be retained as a source reference without a uniqueness constraint.

## Candidate race identity

The conservative descriptive grouping:

`date + course + off + race_name`

produces 189,043 race groups.

No group contains more than one supplied `race_id`, and no `date + course + off` combination contains multiple race names. Therefore:

`date + course + off`

also produces exactly 189,043 groups in the current extract.

All candidate identity components are fully populated. Trimming outer whitespace and ignoring case does not merge any race groups.

The leading candidate natural race identity is therefore `date + course + off`, with `race_name` retained as a required descriptive validation attribute.

## Importance of off-time

Off-time is essential to race identity.

Removing `off` and grouping by `date + course + race_name` creates:

- 451 colliding reduced-key groups;
- 967 actual races inside those groups;
- 516 races lost through merging;
- 10,410 affected runner rows;
- as many as six same-named races at one meeting.

Generic and repeated race names cannot distinguish separate races at one meeting.

## Candidate runner identity

Within the provisional race grouping, adding `horse` produces 1,851,285 distinct groups, equal to the full data-row count.

No horse appears twice within one provisional race, and no horse appears in more than one provisional race at the same course on the same date.

The leading candidate runner-record identity is therefore:

`candidate race identity + horse`

This identifies a source runner record in the current extract. It does not establish durable horse-entity identity across races.

## Runner-number behaviour

The supplied `num` field cannot identify an individual runner.

There are 700 provisional race-and-number groups containing multiple horses:

- 177 groups use `num = 0`, covering 1,170 rows;
- 523 groups use non-zero values, covering 1,084 rows.

Zero frequently behaves as an unavailable-number sentinel. Many non-zero duplicate values appear to represent coupled betting entries, but 20 duplicate-number groups contain multiple recorded starting prices and the field is not consistent enough for one universal interpretation.

`num` should be preserved as a source racecard or betting-entry attribute, not used as a runner key.

## Repeated and amended source records

No exact duplicate source records were found.

Grouping by every supplied source column, excluding SQLite `rowid`, produced zero exact duplicate groups. No provisional race-and-horse group contains multiple source rows.

There is therefore no evidence of straightforward copied runner records or repeated versions retaining the same current identity fields. This does not rule out revisions that changed descriptive identity fields.

## Physical source order

SQLite `rowid` is unique across all data-like rows. The data rows occupy the uninterrupted range `2` to `1,851,286`; `rowid = 1` is the imported header row.

All 4,130 dates occupy one contiguous physical block and progress strictly forwards chronologically.

Race rows are not always contiguous within a date:

- 71,960 races occupy one physical segment;
- 117,083 occupy two or more segments;
- some races are split across as many as 11 segments.

Physical adjacency cannot therefore be used to reconstruct race membership. Original `rowid` remains valuable as exact source lineage within this immutable extract.

## Candidate identity rules

### Race matching

Leading candidate:

`date + course + off`

Conservative reconstruction grouping:

`date + course + off + race_name`

### Runner-record matching

Leading candidate:

`candidate race identity + horse`

## Source-lineage requirements

A later staging process should preserve:

- source product or database identity;
- source database or file path;
- source table name;
- original SQLite `rowid`;
- supplied `race_id`;
- supplied `num`;
- original `date`, `course`, `off`, `race_name` and `horse` values.

Canonical or parsed values should be added alongside these raw values rather than replacing them.

## Surrogate identifiers required later

A later staging layer will require:

1. an independent surrogate race identifier;
2. an independent surrogate runner-record identifier;
3. a relationship from each runner record to its reconstructed race;
4. retained natural-key fields for matching and validation;
5. retained source-lineage fields for audit and reprocessing.

No final target schema is designed in this notebook.

## Decisions made

- Do not use `race_id` as a unique race key.
- Do not assume `date + race_id` is unique.
- Use `date + course + off` as the leading candidate natural race identity.
- Retain `race_name` as a required descriptive validation field.
- Use candidate race identity plus `horse` as the leading candidate runner-record identity.
- Do not use `num` as an individual-runner identifier.
- Preserve `race_id`, `num` and original `rowid` for distinct lineage purposes.
- Preserve all original descriptive identity text.
- Assign surrogate race and runner-record identifiers in a later staging layer.
- Re-run collision and uniqueness tests for every replacement or extended source snapshot.
- Do not begin permanent horse-entity resolution yet.
- Do not design the final target schema in this phase.

## Confidence

**High confidence** in the failure of `race_id` and `date + race_id`, the current-extract uniqueness of `date + course + off`, the uniqueness of race identity plus `horse`, the failure of `num` as an individual-runner key, the absence of exact duplicates, and the value of original `rowid` as lineage.

**Medium confidence** in the stability of the descriptive identity across future snapshots, interpreting most shared non-zero numbers as coupled entries, and the absence of amended records whose identity fields changed.

## Unresolved risks

- Advertised off-times may be corrected in later snapshots.
- Course and race-name text may be reformatted or renamed.
- Future data may contain two races sharing the same descriptive meeting slot.
- Horse-name spelling may change across snapshots or providers.
- Coupled-entry structure cannot be reconstructed reliably from `num` alone.
- SQLite `rowid` may change if the source database is rebuilt.

## Practical implication

The project can now reconstruct provisional races and runner records without relying on the defective supplied identifiers.

These findings will later support a controlled staging layer that assigns surrogate identifiers while preserving raw values and exact lineage. Final staging and target-schema design remain deferred.

The next bounded study should examine course, jurisdiction and surface mapping.