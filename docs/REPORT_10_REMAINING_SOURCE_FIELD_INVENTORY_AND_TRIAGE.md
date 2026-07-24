# Report 10 — Remaining Source-Field Inventory and Triage

## Executive summary

Notebook 10 inventoried all source fields in the Raceform `data` table and determined which fields have already received sufficient investigation, which can currently be preserved without deeper semantic work, and which require bounded profiling before database reconstruction.

The source table contains 37 columns.

Current study coverage is:

- 9 fields with substantive prior study;
- 1 field used as supporting context;
- 27 fields requiring further investigation.

Every source field has now been assigned:

- an analytical family;
- a provisional reconstruction treatment;
- a treatment rationale;
- where further work is required, a bounded investigation group.

The remaining 27 fields have been organised into 11 investigation groups. This does not imply that 11 full-length notebooks must be produced. Some groups may require only a short profile, may be combined with a closely related subject, or may result in a preservation-only decision.

The first remaining priority is the source `off` field because the candidate race key currently uses `date + course + off`, while the temporal meaning of `off` has not yet been independently established.

## Bounded question

Notebook 10 asked:

> Which source fields have already been sufficiently investigated, which can be preserved without further semantic work, and which require dedicated profiling before database reconstruction?

The notebook was an inventory and triage study.

It did not:

- deeply analyse every unresolved field;
- define the final staging schema;
- resolve jurisdiction-specific meanings;
- create parsers before stable rules had been established.

The raw SQLite database remained read-only throughout.

All source-data queries applied:

`DATA_ROW_PREDICATE = "rowid <> 1"`

## Source population

The established source population remains:

- 1,851,285 data-like runner rows;
- 189,043 provisional races;
- candidate provisional race key: `date + course + off`.

The source table contains 37 columns.

No source column contains SQL `NULL` values within the data-like population.

This does not mean that all fields are complete. Several text fields use blank strings as missing, unavailable or inapplicable values.

Notable blank-text rates include:

- `sex_rest`: 87.10%;
- `pattern`: 85.77%;
- `hg`: 60.63%;
- `rating_band`: 58.42%;
- `class`: 41.51%;
- `comment`: 18.39%;
- `sp`: 0.49%.

Blank strings and SQL `NULL` must therefore remain distinct concepts during reconstruction.

## Existing study coverage

Nine fields have received substantive prior study:

- `date`;
- `course`;
- `race_id`;
- `type`;
- `dist`;
- `pos`;
- `draw`;
- `wgt`;
- `sp`.

The `race_name` field has been used as supporting context for race identity and jurisdiction validation but has not required an independent semantic study.

The remaining 27 fields were treated as requiring triage.

Prior study does not imply that every possible analytical interpretation has been resolved. It means that enough source behaviour has been established to support the current reconstruction treatment.

## Analytical field families

The 37 columns were grouped into eight broad analytical families.

### Race identity and timing

- `date`
- `course`
- `race_id`
- `off`
- `race_name`

### Race classification and conditions

- `type`
- `class`
- `pattern`
- `rating_band`
- `age_band`
- `sex_rest`
- `going`

### Race structure and result

- `ran`
- `num`
- `pos`
- `draw`
- `ovr_btn`
- `btn`

### Runner identity and characteristics

- `horse`
- `age`
- `sex`
- `wgt`
- `hg`

### Performance, market and value

- `dist`
- `time`
- `sp`
- `prize`
- `or`
- `rpr`
- `ts`

### Connections and ownership

- `jockey`
- `trainer`
- `owner`

### Pedigree

- `sire`
- `dam`
- `damsire`

### Free text

- `comment`

These families describe subject matter only.

Fields within one family do not necessarily share the same reconstruction risk, semantic meaning or required depth of study.

## Provisional treatment categories

Each source field received one provisional treatment category.

### Deterministic parsing

The raw source value is preserved while a stable, reproducible derivation is also produced.

Assigned fields:

- `date`;
- `course`;
- `dist`;
- `pos`;
- `wgt`;
- `sp`.

All six fields in this category have already received substantive study.

### Raw preservation

The source value can currently be retained substantially as supplied.

Some bounded validation may still be useful, but no immediate parser or semantic reinterpretation is required.

Assigned fields:

- `draw`;
- `age`;
- `sex`.

### Lineage or free text

The field primarily supports traceability, description, validation or unstructured information.

Assigned fields:

- `race_id`;
- `race_name`;
- `comment`.

The source `race_id` must be preserved as lineage but must not be treated as a globally unique race identifier.

### Later jurisdictional enrichment

The source value can be preserved now, while native meaning or cross-jurisdiction interpretation remains part of a separate enrichment layer.

Assigned fields:

- `type`;
- `going`;
- `prize`.

The source `type` must remain preserved even where later native racing-code interpretation differs.

The numeric `prize` value cannot be compared internationally without establishing currency and prize-component meaning.

### Semantic risk

The field cannot safely be interpreted from its name or SQLite type alone.

Its meaning, scope, missing-value convention, identity behaviour or relationship to other fields requires profiling.

Assigned fields:

- `off`;
- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`;
- `ran`;
- `num`;
- `ovr_btn`;
- `btn`;
- `horse`;
- `hg`;
- `time`;
- `or`;
- `rpr`;
- `ts`;
- `jockey`;
- `trainer`;
- `owner`;
- `sire`;
- `dam`;
- `damsire`.

The semantic-risk category is deliberately broad.

It does not mean that each field requires its own notebook.

## Provisional treatment totals

The completed triage assigns:

- 6 fields to deterministic parsing;
- 3 fields to raw preservation;
- 3 fields to lineage or free text;
- 3 fields to later jurisdictional enrichment;
- 22 fields to semantic risk.

All six deterministic-parsing fields have already been studied.

The remaining work is concentrated in the semantic-risk fields, together with limited validation of:

- two raw-preservation fields;
- one free-text field;
- two later-enrichment fields.

## Bounded investigation groups

The 27 fields requiring further work were organised into 11 bounded investigation groups.

### 1. Off-time and temporal semantics

Fields:

- `off`

Question:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?

This is the first priority because the current candidate race identity uses `date + course + off`.

### 2. Runner counts, numbers and entries

Fields:

- `ran`;
- `num`.

This study should establish:

- whether `ran` represents declared runners, actual starters or another race-level count;
- how it relates to the number of source rows;
- the meaning of zero or exceptional runner numbers;
- whether coupled entries or jurisdiction-specific numbering practices occur.

### 3. Beaten-distance semantics

Fields:

- `ovr_btn`;
- `btn`.

This study should determine:

- whether `btn` is incremental distance from the immediately preceding finisher;
- whether `ovr_btn` is cumulative distance from the winner;
- how dead heats, disqualifications and non-finishers are represented;
- whether sentinel values or rounding behaviour occur.

### 4. Race classification and eligibility

Fields:

- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`;
- `going`.

This study should distinguish:

- source classification labels;
- eligibility restrictions;
- sparse or inapplicable values;
- fields that can be parsed structurally;
- fields whose native meaning is jurisdiction-specific.

### 5. Runner characteristics and equipment

Fields:

- `age`;
- `sex`;
- `hg`.

The likely scope is bounded validation of:

- age ranges and exceptional values;
- sex-code inventory;
- equipment or headgear-code inventory;
- blank-value behaviour.

### 6. Prize and currency semantics

Fields:

- `prize`.

The numeric source value must not be assumed to represent a universally comparable currency amount.

The study should establish:

- whether the field records winner’s prize, total purse or another component;
- unit scaling;
- jurisdictional currencies;
- period-specific currency behaviour;
- whether values can be enriched without altering the raw source field.

### 7. Race-time semantics

Fields:

- `time`.

This study should determine:

- observed formats;
- missing or sentinel values;
- whether the field represents winning time;
- precision;
- jurisdiction-specific measurement conventions;
- whether deterministic duration parsing is possible.

The source `time` field is distinct from scheduled `off` time and must not be confused with it.

### 8. Ratings semantics and availability

Fields:

- `or`;
- `rpr`;
- `ts`.

This study should jointly profile:

- coverage;
- zero or sentinel conventions;
- valid ranges;
- relationships among the three fields;
- provider-specific meaning;
- jurisdiction and race-type availability.

### 9. Horse and pedigree identity

Fields:

- `horse`;
- `sire`;
- `dam`;
- `damsire`.

The raw names must be preserved.

The study should assess:

- country suffixes;
- repeated names;
- punctuation and formatting variants;
- whether pedigree fields help distinguish horses;
- the limits of text-only identity reconstruction.

The source `horse` value identifies a source runner record but must not yet be treated as a permanent global horse identifier.

### 10. Connections and owner identity

Fields:

- `jockey`;
- `trainer`;
- `owner`.

The study should assess:

- spelling and punctuation variants;
- initials and abbreviated forms;
- duplicate names;
- trainer partnerships or shared licences;
- owners represented as people, partnerships, syndicates or organisations;
- the limits of text-only entity matching.

Raw source names should remain preserved even if later identity-resolution tables are introduced.

### 11. Comments and embedded information

Fields:

- `comment`.

The comment field is unstructured source text and can be preserved without blocking reconstruction.

A later bounded study may examine:

- coverage by jurisdiction and period;
- repeated formulaic phrases;
- embedded starting-price text;
- equipment, incident or positional information not represented elsewhere;
- whether any extraction is sufficiently stable to justify structured derivations.

No automated extraction should be treated as authoritative without preserving the original comment.

## Provisional sequence

The current order is:

1. off-time and temporal semantics;
2. runner counts, runner numbers and entries;
3. beaten-distance semantics;
4. race classification and eligibility;
5. runner characteristics and equipment;
6. prize and currency semantics;
7. race-time semantics;
8. ratings semantics and availability;
9. horse and pedigree identity;
10. connections and owner identity;
11. comments and embedded information.

The order prioritises fields that affect race identity, runner structure and result reconstruction before descriptive enrichment and entity-resolution work.

Notebook numbers 11–21 are provisional planning labels only.

A group may become:

- one short notebook;
- part of a combined notebook with an adjacent subject;
- a preservation-only decision after a small profile;
- a deferred enrichment study that does not block reconstruction.

## Reconstruction implications

Notebook 10 supports several immediate reconstruction principles.

### Preserve raw values first

Every source field should remain available in its original form.

A parsed or enriched value must not replace the source value from which it was derived.

### Keep blank strings distinct from SQL NULL

The source uses blank text extensively while providing no SQL `NULL` values in the data-like population.

Reconstruction must not silently collapse these states before field-specific meaning has been established.

### Separate source, derivation and research interpretation

The future database should continue to distinguish:

- raw source attributes;
- deterministic structural derivations;
- research-backed semantic or jurisdictional enrichment.

### Do not infer semantics from SQLite types

The declared type establishes storage affinity, not business meaning.

Fields such as `prize`, `or`, `rpr`, `ts`, `ran` and `num` require semantic profiling despite being stored as integers.

### Do not force premature entity resolution

Horse, jockey, trainer, owner and pedigree strings can be preserved before permanent entity identities are resolved.

Text equality alone must not be assumed to represent stable global identity.

### Defer physical schema design

The notebook establishes work priorities and treatment categories only.

It does not determine final tables, keys, constraints or indexes.

## Validation

Notebook 10 completed with the following validation summary:

- source columns retained: 37;
- studied fields: 9;
- supporting-context fields: 1;
- fields requiring investigation: 27;
- bounded investigation groups: 11;
- provisional sequenced studies: 11.

The notebook passed:

- all internal assertions;
- Restart Kernel and Run All without errors.

## Conclusion

Notebook 10 has answered its bounded inventory and triage question.

All 37 source fields now have a documented current status, analytical family and provisional treatment. All 27 fields needing further work have been assigned to one of 11 bounded investigation groups.

The project does not need to analyse every remaining field at equal depth before proceeding. Structural risks should be resolved first, while raw-preservable, identity-resolution and enrichment fields can be deferred where they do not block reconstruction.

The next notebook should study `off` because it participates directly in the current candidate race key.

Notebook 11 should ask:

> What does the source `off` field represent, how consistently is it formatted, and what temporal assumptions can safely be made during race reconstruction?
