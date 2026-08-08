# Database v2 Governed Integration Design

## Status

Canonical Database v2 design specification for the governed integration of Notebook 04–22 outputs.

This document supersedes Notebook 25 as the working design authority. Notebook 25 may remain as an archival scratchpad, but further Database v2 physical-design decisions should be recorded here rather than expanded through Markdown-only notebook cells.

Database v2 is a bounded integration release. It carries forward the accepted Database v1 structural core and adds only governed structures justified by the completed Notebook 04–22 investigations.

The accepted Database v1 remains the last-known-good database until a complete Database v2 candidate passes the governed import and validation gate and is explicitly promoted.

## Governing sources

Database v2 must remain consistent with the accepted project controls, including:

- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/PHASE_4_SQLITE_ARCHITECTURE_DECISION_RECORD.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/NOTEBOOK_CODE_COMMENTING_STANDARD.md`;
- the individual Notebook 04–22 database-integration contracts;
- the durable reusable modules, governed reference files and source-wide validators produced by those notebooks.

Where older notebook closeout prose conflicts with a later durable governed reference or validator baseline, the later governed implementation/reference is authoritative.

## Source and accepted-release boundaries

### Immutable Source Version 1

Source Version 1 remains third-party source evidence and must never be modified in place.

Current governed source facts:

- physical source rows: **1,851,286**;
- admitted runner-bearing rows under `rowid <> 1`: **1,851,285**;
- Source Version 1 race occurrences: **189,043**;
- physical source fields: **37**;
- authorised source-scoped race grouping: exact raw `date + course + off`.

The original source filename remains provenance only. Database v2 code and documentation should refer to it as Source Version 1 rather than treating the source file as the Inside Rails database.

### Accepted Database v1

Database v1 is an immutable accepted release. It intentionally contains the minimum structural core rather than the full governed Notebook 04–22 semantic programme.

Database v2 therefore extends Database v1. It does not mutate Database v1 in place.

## General Database v2 rules

1. **Raw assertions are immutable.**
2. **Defensible corrections are permitted and should be analytically usable when explicitly authorised.**
3. **Every correction or supplementation must remain transparent and traceable to raw evidence and governance provenance.**
4. **Candidate corrections are not automatically accepted corrections.**
5. **Unresolved states remain first-class states.** Nulls must not be eliminated through guessing.
6. **Provisional identities remain explicitly provisional.**
7. **No universal EAV correction framework is introduced.** Use bounded structures at the natural governed grain.
8. **One table is not created merely because one notebook existed.** A table requires a distinct relational grain.
9. **Study-facing views may prefer accepted governed values, but raw lineage and unresolved status must remain recoverable.**
10. **No hidden analytical population filters are permitted in normal study-facing interfaces.**

## Notebook 04–22 integration dispositions

| Notebook | Subject | Database v2 disposition |
|---|---|---|
| 04 | course jurisdiction and surface | partial integration: source-supported surface plus course/jurisdiction derivation; later jurisdiction/course authority comes from 09/12 |
| 05 | result position and non-finish states | runner-governed extension |
| 06 | source distance notation | race-governed extension; literal source interpretation only, not independently verified official distance |
| 07 | carried weight | runner-governed extension |
| 08 | starting price | runner-governed arithmetic plus bounded external correction provenance |
| 09 | jurisdiction/context | race jurisdiction plus effective-dated context reference |
| 10 | field governance | versioned source-field treatment metadata/build control |
| 11 | advertised start time | dedicated one-row-per-race temporal table |
| 12 | course location/timezone | reusable course reference plus race link |
| 13 | prize | runner-level recorded-prize semantics |
| 14 | runner counts/numbers/entries | race and runner semantics plus separate missing-runner supplementation |
| 15 | beaten distance | runner structural semantics plus verification/candidate evidence |
| 16 | classification/eligibility source fields | race-governed source and structural interpretations |
| 17 | runner characteristics/equipment | runner-governed interpretation plus exact accepted sex corrections |
| 18 | ratings | runner-governed independent nullable rating states; exact invalid-RPR handling |
| 19 | horse/pedigree identity | specialist governance, transition decisions, provisional occurrences and runner assignments |
| 20 | connections/ownership blanks | exact source-record/field supplementation decisions; identity remains Notebook 22 |
| 21 | comment information | raw comment remains source evidence; conservative state classification integrated |
| 22 | participant identity | role-specific provisional identities, accepted mappings and unresolved candidate governance |

## Reconciled physical model

Cross-table reconciliation establishes **31 physical tables**:

- **13 carried forward from Database v1**;
- **18 new Database v2 structures**.

### Carried-forward Database v1 tables

1. `source_provider`
2. `source_product`
3. `source_version`
4. `source_relation`
5. `source_relation_field`
6. `source_raceform_v1_record`
7. `core_source_race_occurrence`
8. `core_runner_participation`
9. `governance_method`
10. `governance_release`
11. `governance_release_evidence`
12. `import_manifest`
13. `import_validation_result`

These retain their existing meanings. Existing structural rows retain their original structural governance lineage; Database v2 does not rewrite historical v1 governance simply because those rows are carried into a v2 file.

### New Database v2 tables

14. `core_source_race_occurrence_governed`
15. `core_source_race_occurrence_time`
16. `core_runner_participation_governed`
17. `reference_course`
18. `reference_jurisdiction_context`
19. `governance_source_field_treatment`
20. `governance_manual_verification`
21. `governance_connection_value_decision`
22. `governance_runner_record_supplementation`
23. `governance_horse_pedigree_specialist_decision`
24. `identity_horse_occurrence`
25. `identity_runner_horse_occurrence`
26. `identity_horse_pedigree_decision`
27. `identity_participant_source_label`
28. `identity_participant`
29. `identity_participant_label_map`
30. `identity_participant_candidate`
31. `identity_participant_candidate_label`

The 31-table count supersedes the earlier provisional 30-table inventory. The additional table is required because the 16-row Notebook 19 specialist governance reference has a different grain from the 353 source-wide horse-pedigree transition decisions.

---

# New table specifications

## `core_source_race_occurrence_governed`

### Grain

Exactly one row per `core_source_race_occurrence`.

Expected current population: **189,043**.

`source_race_occurrence_id` is both primary key and foreign key to `core_source_race_occurrence`.

### Columns

Structural/governance:

- `source_race_occurrence_id INTEGER NOT NULL` — PK/FK;
- `governance_release_id INTEGER NOT NULL`.

Course/jurisdiction:

- `candidate_course_label TEXT NOT NULL`;
- `candidate_jurisdiction TEXT NOT NULL`;
- `jurisdiction_evidence TEXT NOT NULL`;
- `reference_course_id INTEGER NOT NULL`;
- `jurisdiction_context_id INTEGER NULL`;
- `jurisdiction_context_status TEXT NOT NULL` — `matched` or `unresearched`.

Surface:

- `candidate_surface TEXT NOT NULL` — current domain `all_weather_unspecified`, `unresolved`;
- `surface_evidence TEXT NOT NULL` — current domain `explicit_course_all_weather_marker`, `no_source_surface_evidence`.

Distance:

- `raw_dist TEXT NOT NULL`;
- `distance_miles_component INTEGER NULL`;
- `distance_whole_furlongs_component INTEGER NULL`;
- `distance_has_half_furlong INTEGER NULL`;
- `distance_total_furlongs REAL NULL`;
- `distance_source_implied_yards INTEGER NULL`;
- `distance_source_implied_metres REAL NULL`;
- `distance_official_verified INTEGER NOT NULL`;
- `distance_parse_status TEXT NOT NULL` — `parsed`, `unresolved`;
- `distance_parser_version TEXT NOT NULL`.

Runner-count/coverage semantics:

- `source_reported_ran INTEGER NULL`;
- `source_runner_row_count INTEGER NOT NULL`;
- `source_ran_distinct_value_count INTEGER NOT NULL`;
- `source_ran_consistency_status TEXT NOT NULL` — `consistent`, `conflicting`, `invalid`, `missing`;
- `source_row_count_vs_ran_status TEXT NOT NULL` — `equal`, `below`, `above`, `not_comparable`;
- `source_runner_coverage_status TEXT NOT NULL` — `unverified`, `internally_equal_to_ran`, `known_partial`, `externally_verified_complete`;
- `source_ran_external_status TEXT NOT NULL` — `unverified`, `externally_verified`, `externally_contradicted`;
- `source_ran_verification_id TEXT NULL`.

Race-level source assertions promoted only after source-wide within-race constancy validation:

- `race_name_raw TEXT NULL`;
- `race_type_raw TEXT NULL`;
- `class_raw TEXT NULL`;
- `pattern_raw TEXT NULL`;
- `rating_band_raw TEXT NULL`;
- `age_band_raw TEXT NULL`;
- `sex_rest_raw TEXT NULL`.

Class interpretation:

- `class_number INTEGER NULL`;
- `class_parse_status TEXT NOT NULL` — `blank`, `canonical`, `unrecognised`.

Pattern interpretation:

- `pattern_family TEXT NULL` — recognised `Listed`, `Group`, `Grade`;
- `pattern_level_raw TEXT NULL`;
- `pattern_parse_status TEXT NOT NULL` — `blank`, `canonical`, `unrecognised`.

Rating-band interpretation:

- `rating_lower_bound INTEGER NULL`;
- `rating_upper_bound INTEGER NULL`;
- `rating_band_parse_status TEXT NOT NULL` — `blank`, `canonical`, `unrecognised_source_form`, `invalid_range_order`.

Age-band interpretation:

- `stated_minimum_age INTEGER NULL`;
- `stated_maximum_age INTEGER NULL`;
- `age_band_open_ended INTEGER NULL`;
- `age_band_syntax TEXT NOT NULL` — `blank`, `exact_age`, `open_ended_minimum`, `closed_age_range`, `invalid_range_order`, `unrecognised`;
- `age_band_interpretation_status TEXT NOT NULL` — `blank`, `source_stated_bounds_only`, `unresolved`.

Sex-restriction interpretation:

- `sex_rest_category TEXT NULL`;
- `sex_rest_interpretation_status TEXT NOT NULL` — `blank`, `explicit_source_category`, `overloaded_source_category`, `unrecognised_source_category`.

### Boundaries

- Surface inference is limited to explicit `(AW)` course markers; other surfaces remain unresolved from Notebook 04 source evidence.
- Source-implied distance is not an independently verified official distance.
- Internal equality between source row count and `ran` is not external proof of complete field coverage.
- Regulatory/administrative context text is not repeated per race; the race stores only an optional context reference.
- Notebook 11 temporal fields are excluded and stored separately.
- No new normalised `going` value is introduced by Database v2; raw `going` remains source evidence pending a separately governed study.

## `core_source_race_occurrence_time`

### Grain

Exactly one row per `core_source_race_occurrence`.

Expected population:

- total: **189,043**;
- pre-boundary: **178,691**;
- post-boundary: **10,352**;
- resolved: **169,465**;
- unresolved: **19,578**.

The source-encoding boundary is **15 October 2025**.

The table attaches directly to `core_source_race_occurrence`, not to the governed race extension. The build separately validates that the governed course/timezone context exists for every temporal row.

### Columns

- `source_race_occurrence_id INTEGER NOT NULL` — PK/FK;
- `governance_release_id INTEGER NOT NULL`;
- `candidate_a_uk_naive TEXT NULL`;
- `candidate_b_uk_naive TEXT NULL`;
- `candidate_a_utc TEXT NULL`;
- `candidate_b_utc TEXT NULL`;
- `candidate_a_course_local TEXT NULL`;
- `candidate_b_course_local TEXT NULL`;
- `advertised_start_uk TEXT NULL`;
- `advertised_start_utc TEXT NULL`;
- `advertised_start_course_local TEXT NULL`;
- `selected_branch TEXT NULL` — `candidate_a`, `candidate_b`, `explicit_24h`;
- `decision_method TEXT NOT NULL` — `course_local_dead_of_night_rejection`, `stable_post_boundary_course_profile`, `explicit_post_boundary_time`, `unresolved`;
- `decision_confidence TEXT NOT NULL` — `high`, `supported`, `source_explicit`, `unresolved`;
- `temporal_resolution_status TEXT NOT NULL` — `resolved`, `unresolved`.

### Current decision baseline

- `course_local_dead_of_night_rejection`: **111,871**;
- `stable_post_boundary_course_profile`: **47,242**;
- `explicit_post_boundary_time`: **10,352**;
- `unresolved`: **19,578**.

Pre-boundary unresolved races retain both candidate branches and no selected canonical advertised-start timestamp. Post-boundary races retain no pre-boundary candidates.

Source `off` is a UK-facing advertised/scheduled clock representation. Database v2 must not describe reconstructed timestamps automatically as exact actual-off times.

## `core_runner_participation_governed`

### Grain

Exactly one row per `core_runner_participation`.

Expected population: **1,851,285**.

`runner_participation_id` is both primary key and FK.

### Raw duplication boundary

The immutable source mirror already provides a one-to-one raw source record through `core_runner_participation.source_record_id`. Database v2 therefore does **not** physically duplicate every raw runner field in this extension. Study-facing views join raw values from `source_raceform_v1_record` to the governed analytical values below.

### Result

- `result_kind TEXT NOT NULL` — `finish_position`, `zero_sentinel`, `disqualified`, `non_finish_outcome`, `missing`;
- `finish_position INTEGER NULL`;
- `outcome_code TEXT NULL`.

### Carried weight

- `weight_notation_family TEXT NOT NULL`;
- `carried_weight_stones INTEGER NULL`;
- `carried_weight_remainder_pounds INTEGER NULL`;
- `carried_weight_total_pounds INTEGER NULL`;
- `carried_weight_implied_kg REAL NULL`;
- `weight_parse_status TEXT NOT NULL`;
- `weight_ambiguity_flag INTEGER NOT NULL`;
- `weight_anomaly_flags_json TEXT NOT NULL`;
- `official_weight_verified INTEGER NOT NULL`.

### Source starting-price interpretation

- `starting_price_kind TEXT NOT NULL` — `fractional`, `evens`, `missing`, `unresolved`;
- `starting_price_numerator INTEGER NULL`;
- `starting_price_denominator INTEGER NULL`;
- `starting_price_fractional_odds TEXT NULL`;
- `starting_price_decimal_odds TEXT NULL`;
- `starting_price_implied_probability TEXT NULL`;
- `starting_price_favourite_marker TEXT NULL`;
- `starting_price_favourite_status TEXT NULL`;
- `starting_price_market_context_status TEXT NOT NULL`.

Governed analytical SP:

- `starting_price_analytical_numerator INTEGER NULL`;
- `starting_price_analytical_denominator INTEGER NULL`;
- `starting_price_analytical_favourite_status TEXT NULL`;
- `starting_price_value_status TEXT NOT NULL` — `source_parsed`, `externally_corrected`, `missing`, `unresolved`;
- `starting_price_verification_id TEXT NULL`.

The known standalone `F` anomaly for Almendares remains source-unresolved while the governed analytical layer may use verified `5/2 favourite` through exact provenance. No global rule maps standalone `F` to `5/2`.

### Prize

- `prize_source_presented_amount TEXT NULL`;
- `prize_canonical_minor_units INTEGER NULL`;
- `prize_currency TEXT NULL`;
- `prize_interpretation_status TEXT NOT NULL`;
- `prize_interpretation_method TEXT NOT NULL`;
- `prize_conversion_multiplier TEXT NULL`;
- `prize_confidence TEXT NOT NULL`.

Only governed GBP/EUR cases receive canonical minor units. A populated source amount with unresolved currency remains source-presented only.

### Runner number

- `source_num_storage_class TEXT NOT NULL`;
- `source_positive_runner_number INTEGER NULL`;
- `source_num_state TEXT NOT NULL` — `positive_integer`, `integer_zero`, `blank_text`, `null`, `invalid`;
- `source_num_within_race_multiplicity INTEGER NULL`;
- `source_num_uniqueness_status TEXT NOT NULL` — `unassessed`, `unique_within_race`, `shared_positive_num`, `nonpositive_state`.

Source `num` is not a natural runner key.

### Beaten distance

- `ovr_btn_numeric REAL NULL`;
- `ovr_btn_status TEXT NOT NULL`;
- `btn_numeric REAL NULL`;
- `btn_status TEXT NOT NULL`;
- `positive_official_winner_distance INTEGER NOT NULL`;
- `later_position_zero_overall INTEGER NOT NULL`;
- `same_distance_group INTEGER NOT NULL`;
- `beaten_distance_requires_review INTEGER NOT NULL`.

The source sentinel `-` means numeric beaten distance unavailable, not zero. Zero `btn` with positive `ovr_btn` supports a same stored-distance group but does not alone prove an official dead heat.

### Age

- `age_recorded INTEGER NULL`;
- `age_interpretation_status TEXT NOT NULL` — `source_recorded_integer`, `unresolved`.

### Sex

- `sex_normalised TEXT NULL`;
- `sex_interpretation_status TEXT NOT NULL`;
- `sex_verification_id TEXT NULL`.

Common codes map conservatively to colt/filly/gelding/horse/mare/rig. Exact accepted corrections are lineage-bound:

- `BB` → `gelding` for Par Coeur (GER), Cologne, 2017-10-15 1:35 under `NB17-SEX-0002`;
- `B` → `filly` for La Venezolana (VEN), Gulfstream Park, 2019-11-29 8:30 under `NB17-SEX-0003`.

No global B/BB replacement is authorised.

### Headgear

- `headgear_raw_components_json TEXT NOT NULL`;
- `headgear_components_json TEXT NOT NULL`;
- `headgear_component_count INTEGER NOT NULL`;
- `headgear_use_suffix TEXT NULL`;
- `headgear_source_declared_first_time INTEGER NOT NULL`;
- `headgear_interpretation_status TEXT NOT NULL`.

Canonical JSON arrays retain ordered decomposed tokens without requiring a separate child table for this bounded vocabulary.

### Ratings

- `or INTEGER NULL`;
- `or_status TEXT NOT NULL`;
- `rpr INTEGER NULL`;
- `rpr_status TEXT NOT NULL`;
- `ts INTEGER NULL`;
- `ts_status TEXT NOT NULL`.

Allowed states: `available`, `unavailable`, `invalid_source_value`, `unresolved_source_value`.

The exact invalid RPR case is source rowid `1619851`, raw `rpr = 775`: governed `rpr` is null with `rpr_status = 'invalid_source_value'`. No replacement value is authorised and no global `775` rule is permitted.

### Governed connection labels

For each of jockey, trainer and owner:

- `<role>_governed TEXT NULL`;
- `<role>_value_status TEXT NOT NULL` — `source_present`, `externally_supplemented`, `source_blank_unresolved`;
- `<role>_verification_id TEXT NULL`;
- `<role>_confidence TEXT NULL`.

Current Notebook 20 baseline:

- 46 blank field decisions;
- 28 confirmed supplementations: 2 jockey, 4 trainer, 22 owner;
- 18 unresolved: 5 trainer, 13 owner.

These are governed labels, not participant identities.

### Comment state

- `comment_state TEXT NOT NULL` — `empty_string`, `probable_placeholder`, `unresolved_source_code`, `substantive_text`, `unexpected_null`;
- `comment_analytically_available INTEGER NOT NULL`.

Exact probable placeholders: `.`, `..`, `-`, ` -`, `/`, `1`.

Exact unresolved source codes: `A`, `B`, `V`.

All other current non-empty values remain unchanged substantive text. No general narrative parser or HTML-cleaning field is authorised.

## `reference_course`

### Grain

One governed course identity keyed by `candidate_course_label + candidate_jurisdiction`.

Current baseline:

- **395 course identities**;
- **395 timezones**;
- **51 distinct valid IANA timezones**;
- **zero unresolved timezone assignments**.

### Columns

- `reference_course_id INTEGER NOT NULL` — PK;
- `candidate_course_label TEXT NOT NULL`;
- `candidate_jurisdiction TEXT NOT NULL`;
- `physical_venue_name TEXT NULL`;
- `locality TEXT NULL`;
- `region TEXT NULL`;
- `country TEXT NULL`;
- `latitude REAL NULL`;
- `longitude REAL NULL`;
- `iana_timezone TEXT NOT NULL`;
- `location_evidence TEXT NULL`;
- `location_validation_status TEXT NOT NULL`;
- `raw_course_labels TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

`raw_course_labels` is provenance, not a production join key. Snapshot construction fields such as provisional race counts and earliest/latest dates remain in the reference artifact/validator rather than the reusable course entity.

## `reference_jurisdiction_context`

### Grain

One `jurisdiction + source_type + effective_period` context row.

Current governed reference contains **16 rows** covering only Great Britain, Ireland and France.

### Columns

- `jurisdiction_context_id INTEGER NOT NULL` — PK;
- `jurisdiction TEXT NOT NULL`;
- `source_type TEXT NOT NULL`;
- `effective_from TEXT NOT NULL`;
- `effective_to TEXT NULL`;
- `regulatory_authority TEXT NOT NULL`;
- `administrative_body TEXT NULL`;
- `native_code_status TEXT NOT NULL`;
- `wagering_context_status TEXT NOT NULL`;
- `evidence_scope TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Effective periods for the same jurisdiction/type may not overlap. Zero race-context matches mean `unresearched`; more than one match is a validation failure. Current wagering context remains unresolved.

## `governance_source_field_treatment`

### Grain

One governed treatment of one `source_relation_field` under one governance release.

### Columns

- `source_field_treatment_id INTEGER NOT NULL` — PK;
- `source_relation_field_id INTEGER NOT NULL` — FK;
- `analytical_family TEXT NOT NULL`;
- `investigation_group TEXT NOT NULL`;
- `treatment TEXT NOT NULL`;
- `governing_notebook TEXT NOT NULL`;
- `audit_status TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Unique key: `source_relation_field_id + governance_release_id`.

Current Source Version 1 release must contain exactly **37** treatment rows.

## `governance_manual_verification`

### Grain

One bounded manual/external verification claim.

### Columns

- `manual_verification_id INTEGER NOT NULL` — PK;
- `verification_code TEXT NOT NULL` — unique permanent governed identifier;
- `subject_type TEXT NOT NULL`;
- `source_record_id INTEGER NULL`;
- `source_race_occurrence_id INTEGER NULL`;
- `reference_course_id INTEGER NULL`;
- `source_relation_field_id INTEGER NULL`;
- `source_date TEXT NULL`;
- `source_course TEXT NULL`;
- `source_off TEXT NULL`;
- `source_horse TEXT NULL`;
- `source_field TEXT NULL`;
- `raw_source_value TEXT NULL`;
- `verification_question TEXT NOT NULL`;
- `verified_value TEXT NULL`;
- `verification_status TEXT NOT NULL` — `confirmed`, `contradicted`, `partially_confirmed`, `unresolved`;
- `evidence_type TEXT NOT NULL`;
- `evidence_locator TEXT NOT NULL`;
- `evidence_accessed_date TEXT NULL`;
- `governing_notebook TEXT NOT NULL`;
- `confidence TEXT NOT NULL` — `high`, `medium`, `low`;
- `notes TEXT NOT NULL`;
- `database_action TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Current allowed database actions include:

- `evidence_only`;
- `label_equivalence`;
- `reference_enrichment`;
- `source_supplementation`;
- `source_correction_candidate`;
- `preserve_raw_unresolved`.

The older `MV-####` convention is obsolete; current governed identifiers such as `NB14-RAN-0001`, `NB17-SEX-0002` and `NB20-CONNECTION-0001` remain valid. Physical validation requires permanent, nonblank, unique verification codes rather than one obsolete prefix.

## `governance_connection_value_decision`

### Grain

One governed Notebook 20 decision per exact blank source record/connection-field occurrence.

Current population: **46**.

### Columns

- `connection_value_decision_id INTEGER NOT NULL` — PK;
- `connection_decision_code TEXT NOT NULL` — unique stable decision code;
- `source_record_id INTEGER NOT NULL`;
- `source_relation_field_id INTEGER NOT NULL`;
- `manual_verification_id INTEGER NOT NULL`;
- `governed_value TEXT NULL`;
- `value_status TEXT NOT NULL` — `externally_supplemented`, `source_blank_unresolved`;
- `confidence TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Unique operational key: `source_record_id + source_relation_field_id`.

The field FK must resolve only to jockey, trainer or owner.

## `governance_runner_record_supplementation`

### Grain

One externally verified missing runner per source race occurrence and horse label.

Current population: **3**.

### Columns

- `runner_record_supplementation_id INTEGER NOT NULL` — PK;
- `supplementation_code TEXT NOT NULL` — unique;
- `manual_verification_id INTEGER NOT NULL`;
- `source_race_occurrence_id INTEGER NOT NULL`;
- `source_horse TEXT NOT NULL`;
- `source_runner_rows INTEGER NOT NULL`;
- `source_reported_ran INTEGER NOT NULL`;
- `published_runner_count INTEGER NOT NULL`;
- `verified_finish_position INTEGER NULL`;
- `verified_outcome TEXT NULL`;
- `record_origin TEXT NOT NULL` — current only `externally_supplemented`;
- `governance_release_id INTEGER NOT NULL`.

Unique key: `source_race_occurrence_id + source_horse`.

Current exact supplementations:

- `RUNNER-SUPPLEMENT-0001` — Saucats, Nantes 2024-06-18 2:14, outcome F;
- `RUNNER-SUPPLEMENT-0002` — Tosen Thunder (JPN), Ohi 2025-10-09 11:07, did not finish;
- `RUNNER-SUPPLEMENT-0003` — Great Navigator (USA), Gulfstream Park 2023-12-23 9:36, verified fifth.

No fake source record or runner-participation ID may be generated for these rows. Unsupported runner attributes remain null.

## `governance_horse_pedigree_specialist_decision`

### Grain

One bounded Notebook 19 specialist horse/pedigree governance decision.

Current population: **16**.

### Columns

- `horse_pedigree_specialist_decision_id INTEGER NOT NULL` — PK;
- `specialist_decision_code TEXT NOT NULL` — unique, current `NB19-ID-0001` … `NB19-ID-0016`;
- `source_horse_label TEXT NOT NULL`;
- `decision_scope TEXT NOT NULL`;
- `analytical_outcome TEXT NOT NULL` — `Corrected`, `Different horse`, `Unresolved`;
- `raw_sire TEXT NULL`;
- `raw_dam TEXT NULL`;
- `raw_damsire TEXT NULL`;
- `governed_sire TEXT NULL`;
- `governed_dam TEXT NULL`;
- `governed_damsire TEXT NULL`;
- `verification_status TEXT NOT NULL`;
- `verification_code TEXT NOT NULL`;
- `evidence_locator TEXT NOT NULL`;
- `confidence TEXT NOT NULL`;
- `notes TEXT NOT NULL`;
- `manual_verification_id INTEGER NULL`;
- `governance_release_id INTEGER NOT NULL`.

This table is distinct from the 353 transition decisions. It is the specialist authority for bounded manually/external researched cases and prevents evidence/provenance text from being repeated across transition rows.

Current `Runninsonofagun (IRE)` specialist decision is `NB19-ID-0013`, outcome `Corrected`, governed damsire `Society Rock (IRE)`, confirmed high confidence, with no identity split. Raw General Monash/Society Rock assertions remain source evidence.

## `identity_horse_occurrence`

### Grain

One governed provisional source-internal horse occurrence.

Current population: **611**.

### Columns

- `horse_occurrence_id INTEGER NOT NULL` — PK;
- `provisional_occurrence_code TEXT NOT NULL` — unique;
- `source_horse_label TEXT NOT NULL`;
- `occurrence_sequence INTEGER NOT NULL`;
- `pedigree_group_count INTEGER NOT NULL`;
- `runner_row_count INTEGER NOT NULL`;
- `first_source_date TEXT NOT NULL`;
- `last_source_date TEXT NOT NULL`;
- `minimum_recorded_age INTEGER NULL`;
- `maximum_recorded_age INTEGER NULL`;
- `sex_values TEXT NOT NULL`;
- `unresolved_boundary_count INTEGER NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Unique key: `source_horse_label + occurrence_sequence`.

Current codes follow `<exact source horse label>::<two-digit occurrence sequence>`.

## `identity_runner_horse_occurrence`

### Grain

One assignment of one applicable source-backed runner participation to one provisional horse occurrence.

### Columns

- `runner_participation_id INTEGER NOT NULL` — PK/FK;
- `horse_occurrence_id INTEGER NOT NULL`;
- `pedigree_group_number INTEGER NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Many applicable runner participations may map to one horse occurrence. A source-backed runner may map to at most one occurrence. Rows outside the governed Notebook 19 occurrence population remain unmapped rather than receiving invented identities.

## `identity_horse_pedigree_decision`

### Grain

One governed transition between adjacent temporally separated structured pedigree groups.

Current population: **353**.

Current accepted partition:

- **92 `Corrected`**;
- **261 `Different horse`**;
- **0 `Unresolved`**.

Older closeout prose containing 87/5 or 91/1 partitions is historical. The current durable implementation/reference baseline above is authoritative. The schema continues to support future unresolved transitions.

### Columns

- `horse_pedigree_decision_id INTEGER NOT NULL` — PK;
- `horse_pedigree_decision_code TEXT NOT NULL` — unique deterministic boundary code;
- `source_horse_label TEXT NOT NULL`;
- `from_pedigree_group_number INTEGER NOT NULL`;
- `to_pedigree_group_number INTEGER NOT NULL`;
- `from_sire TEXT NULL`;
- `from_dam_key_kind TEXT NOT NULL`;
- `from_dam_name TEXT NULL`;
- `from_dam_country TEXT NULL`;
- `from_damsire TEXT NULL`;
- `from_first_date TEXT NOT NULL`;
- `from_last_date TEXT NOT NULL`;
- `from_minimum_age INTEGER NULL`;
- `from_maximum_age INTEGER NULL`;
- `from_runner_rows INTEGER NOT NULL`;
- `from_provisional_races INTEGER NOT NULL`;
- `to_sire TEXT NULL`;
- `to_dam_key_kind TEXT NOT NULL`;
- `to_dam_name TEXT NULL`;
- `to_dam_country TEXT NULL`;
- `to_damsire TEXT NULL`;
- `to_first_date TEXT NOT NULL`;
- `to_minimum_age INTEGER NULL`;
- `gap_days INTEGER NOT NULL`;
- `sire_changed INTEGER NOT NULL`;
- `dam_changed INTEGER NOT NULL`;
- `damsire_changed INTEGER NOT NULL`;
- `pedigree_components_changed INTEGER NOT NULL`;
- `analytical_outcome TEXT NOT NULL` — `Corrected`, `Different horse`, `Unresolved`;
- `decision_basis TEXT NOT NULL`;
- `identity_split INTEGER NULL`;
- `horse_pedigree_specialist_decision_id INTEGER NULL`;
- `governance_release_id INTEGER NOT NULL`.

`identity_split = 1` only for `Different horse`, `0` for `Corrected`, null for `Unresolved`.

The reversible structured dam key is stored relationally as kind/name/country rather than serialised Python tuple text.

## `identity_participant_source_label`

### Grain

One distinct populated source-presented participant label within one role.

Roles: `jockey`, `trainer`, `owner`.

Current populations:

- jockey: **7,917**;
- trainer: **10,708**;
- owner: **98,234**.

### Columns

- `participant_source_label_id INTEGER NOT NULL` — PK;
- `participant_source_label_code TEXT NOT NULL` — unique deterministic code;
- `participant_role TEXT NOT NULL`;
- `raw_label TEXT NOT NULL`;
- `first_source_date TEXT NOT NULL`;
- `last_source_date TEXT NOT NULL`;
- `source_runner_rows INTEGER NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Unique key: `participant_role + raw_label`.

Blank source fields do not create label entities.

## `identity_participant`

### Grain

One accepted governed provisional participant identity.

Current accepted population:

- 1 jockey provisional person-label identity;
- 26 trainer provisional person-label identities;
- 41 provisional ownership-composition identities;
- **68 total**.

### Columns

- `participant_identity_id INTEGER NOT NULL` — PK;
- `participant_identity_code TEXT NOT NULL` — unique existing governed code;
- `participant_role TEXT NOT NULL`;
- `identity_scope TEXT NOT NULL` — current `person_label_identity`, `ownership_composition`;
- `identity_status TEXT NOT NULL`;
- `identity_method TEXT NOT NULL`;
- `confidence TEXT NOT NULL`;
- `review_status TEXT NOT NULL`;
- `created_by_notebook TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Existing codes such as `JOCKEY-PROVISIONAL-0001`, `TRAINER-PROVISIONAL-0001` and `OWNER-COMPOSITION-PROVISIONAL-0001` are preserved.

## `identity_participant_candidate`

### Grain

One governed participant-identity candidate relationship/group.

### Columns

- `participant_candidate_id INTEGER NOT NULL` — PK;
- `participant_candidate_code TEXT NOT NULL` — unique deterministic code;
- `participant_role TEXT NOT NULL`;
- `candidate_key TEXT NOT NULL`;
- `candidate_method TEXT NOT NULL`;
- `candidate_structure TEXT NULL`;
- `evidence_status TEXT NULL`;
- `identity_relationship TEXT NOT NULL`;
- `decision_status TEXT NOT NULL` — `accepted`, `confirmed_distinct`, `unresolved`;
- `decision_basis TEXT NOT NULL`;
- `confidence TEXT NOT NULL`;
- `verification_code TEXT NULL`;
- `evidence_type TEXT NULL`;
- `evidence_locator TEXT NULL`;
- `evidence_accessed_date TEXT NULL`;
- `review_status TEXT NOT NULL`;
- `review_notes TEXT NULL`;
- `database_action TEXT NOT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Current candidate baselines:

- jockey: **216** relationships = 1 accepted, 1 confirmed distinct, 214 unresolved;
- trainer: **53** groups = 26 accepted, 27 unresolved;
- owner: **936** groups = 41 accepted, 895 unresolved.

Jockey codes `JOCKEY-STRICT-####` are preserved. Trainer and owner candidate codes must be deterministic from governed role/key rather than insertion order.

## `identity_participant_candidate_label`

### Grain

One source-label membership in one participant candidate.

### Columns

- `participant_candidate_id INTEGER NOT NULL`;
- `participant_source_label_id INTEGER NOT NULL`;
- `candidate_label_role TEXT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Composite primary key: `participant_candidate_id + participant_source_label_id`.

Candidate membership never implies accepted identity equivalence.

## `identity_participant_label_map`

### Grain

One accepted source-label mapping to one accepted provisional participant identity.

Current accepted mappings:

- jockey: **2**;
- trainer: **52**;
- owner: **95**;
- **149 total**.

### Columns

- `participant_identity_label_map_id INTEGER NOT NULL` — PK;
- `participant_identity_id INTEGER NOT NULL`;
- `participant_source_label_id INTEGER NOT NULL`;
- `participant_candidate_id INTEGER NOT NULL`;
- `label_role TEXT NULL`;
- `relationship_status TEXT NOT NULL` — current accepted population uses `accepted`;
- `mapping_method TEXT NOT NULL`;
- `confidence TEXT NOT NULL`;
- `evidence_reference TEXT NULL`;
- `database_action TEXT NOT NULL`;
- `effective_start_date TEXT NULL`;
- `effective_end_date TEXT NULL`;
- `governance_release_id INTEGER NOT NULL`.

Only accepted candidates may create mapping rows. Unresolved and confirmed-distinct candidates may not.

Current accepted methods:

- jockey: `targeted_external_profile_verification` for `Mlle Marie Velon` / `Mme Marie Velon` → `JOCKEY-PROVISIONAL-0001` under `NB22-JOCKEY-0002`;
- trainer: `bounded_2024_mlle_to_mme_source_transition`;
- owner: `same_race_exact_owner_token_multiset`.

Marie Velon mapping dates remain null because source/published title presentation must not be treated as reliable legal/social-title effective dating.

---

# Cross-table cardinality and FK rules

## Race extensions

- `core_source_race_occurrence_governed.source_race_occurrence_id` → `core_source_race_occurrence` one-to-one.
- `core_source_race_occurrence_time.source_race_occurrence_id` → `core_source_race_occurrence` one-to-one.
- Both extensions independently attach to the structural parent; neither is the parent of the other.
- `core_source_race_occurrence_governed.reference_course_id` → `reference_course` many-to-one and required.
- `core_source_race_occurrence_governed.jurisdiction_context_id` → `reference_jurisdiction_context` many-to-one and optional.

## Runner extension

- `core_runner_participation_governed.runner_participation_id` → `core_runner_participation` one-to-one.
- Raw source values remain reached through `core_runner_participation.source_record_id` rather than duplicated in the governed runner table.

## Governance

- `governance_source_field_treatment.source_relation_field_id` → `source_relation_field`.
- `governance_connection_value_decision.source_record_id` → exact `source_raceform_v1_record`.
- `governance_connection_value_decision.source_relation_field_id` → exact jockey/trainer/owner physical field.
- `governance_connection_value_decision.manual_verification_id` → `governance_manual_verification`.
- `governance_runner_record_supplementation.source_race_occurrence_id` → `core_source_race_occurrence`.
- `governance_runner_record_supplementation.manual_verification_id` → `governance_manual_verification`.
- `identity_horse_pedigree_decision.horse_pedigree_specialist_decision_id` → optional `governance_horse_pedigree_specialist_decision`.

## Horse identity

- `identity_runner_horse_occurrence.runner_participation_id` → `core_runner_participation` one-to-one on the governed Notebook 19 population.
- Many assignments may reference one `identity_horse_occurrence`.
- Raw horse label alone is never the join key for assigning runner history to an occurrence.

## Participant identity

- `identity_participant_source_label` is role-specific; cross-role merges are prohibited.
- `identity_participant_candidate_label` relates source labels to candidates.
- Only `identity_participant_candidate.decision_status = 'accepted'` may support `identity_participant_label_map`.
- A source label may map to at most one active accepted provisional identity within the same role and governed method scope.
- Owner compositions are not decomposed into individual owner identities.

## Delete/update behaviour

Accepted releases are immutable. New governed foreign keys should fail closed and should not use cascading destructive behaviour to remove source lineage or governance evidence automatically.

---

# Correction and supplementation policy

## Accepted corrections

Accepted governed corrections may become preferred analytical values while the raw source assertion remains immutable and recoverable.

Examples include:

- exact Notebook 17 B/BB sex corrections;
- exact Notebook 18 invalid RPR nulling at source rowid 1619851;
- bounded Notebook 19 pedigree corrections, including Runninsonofagun;
- Notebook 08 Almendares externally corrected analytical SP once its permanent verification is represented.

## Candidate corrections

`source_correction_candidate` does not itself authorise canonical replacement.

Current candidate/evidence populations from Notebooks 14, 15 and 16 remain raw-plus-evidence unless a durable integration contract explicitly promotes a reconciled value.

## Supplementations

A supplementation is not a recovered raw source fact.

- Notebook 20 supplements exact blank connection fields while preserving the blank source value.
- Notebook 14/15 missing-runner supplementations exist outside the source-backed runner table and expose `record_origin = externally_supplemented`.

---

# Study-facing views

Physical tables are not the normal study interface.

Database v2 should later provide a small documented set of transparent views, principally:

- governed race-level view;
- governed runner-level view;
- governed horse-occurrence/runner-assignment views;
- governed participant-identity views;
- governance/evidence audit views.

The governed runner view may union:

- source-backed runner participations;
- the three externally supplemented missing runners;

but must expose origin explicitly.

Views may prefer accepted corrected/supplemented values only when:

- the raw source value is still accessible;
- correction/supplementation status is exposed;
- verification/evidence lineage remains reachable;
- unresolved cases remain visible;
- provisional identities remain labelled as provisional.

Views must not describe:

- source-implied distance as independently verified official distance;
- advertised reconstructed start time automatically as actual off time;
- Notebook 09 bounded jurisdiction context as worldwide coverage;
- owner composition as an individual owner;
- raw horse label as a permanent horse identity;
- internal row-count equality with `ran` as external proof of field completeness.

---

# Current high-value validation baselines

A Database v2 candidate must fail rather than silently update expected baselines when these governed populations change unexpectedly.

### Structural source

- physical source rows: 1,851,286;
- admitted source-backed runners: 1,851,285;
- race occurrences: 189,043;
- source fields: 37.

### Course

- course identities: 395;
- assigned timezones: 395;
- distinct valid IANA timezones: 51;
- unresolved timezone assignments: 0.

### Time

- total: 189,043;
- resolved: 169,465;
- unresolved: 19,578;
- dead-of-night method: 111,871;
- stable post-boundary profile: 47,242;
- explicit post-boundary: 10,352.

### Missing runners

- accepted supplementations: 3.

### Connections

- blank-field decisions: 46;
- supplemented: 28;
- unresolved: 18.

### Horse identity

- raw contradiction labels: 5,573;
- structured contradiction labels: 368;
- structured pedigree rows: 96,404;
- structured pedigree groups: 741;
- separated labels: 350;
- separated pedigree groups: 703;
- transitions: 353;
- corrected: 92;
- different horse: 261;
- unresolved: 0;
- provisional occurrences: 611;
- specialist governance decisions: 16.

### Participant identity

Jockey:

- labels: 7,917;
- candidate relationships: 216;
- accepted: 1;
- confirmed distinct: 1;
- unresolved: 214;
- accepted label mappings: 2.

Trainer:

- labels: 10,708;
- accepted groups: 26;
- accepted mapped labels: 52;
- accepted mapped runner rows: 6,350;
- unresolved groups: 27.

Owner:

- labels: 98,234;
- accepted groups: 41;
- accepted mapped labels: 95;
- accepted mapped runner rows: 9,788;
- unresolved groups: 895;
- unresolved labels: 1,822;
- unresolved candidate runner rows: 24,406.

Accepted provisional participant identities: 68.
Accepted participant label mappings: 149.

---

# Build and acceptance obligations

Database v2 must follow the existing fail-closed release lifecycle:

1. preserve the accepted Database v1 release unchanged;
2. build a complete Database v2 candidate outside the accepted releases path;
3. copy/reconstruct the Database v1 structural core deterministically rather than mutating the accepted file in place;
4. load only governed v2 reference/evidence/semantic structures;
5. validate source populations and exact source round-trip preservation;
6. validate schema, types, domains, keys, uniqueness and foreign keys;
7. validate every expected notebook-derived population independently;
8. persist and reload the candidate;
9. run SQLite `quick_check`/integrity and foreign-key checks;
10. run post-load reconciliation through study-facing/audit views;
11. calculate candidate SHA-256;
12. promote only after the complete acceptance gate passes;
13. keep the prior accepted release and active manifest unchanged after any failed candidate build.

The complete repository test suite and all-validator sweep remain deferred until the appropriate final acceptance boundary. Focused implementation tests and bounded validators should be used during construction.

---

# Implementation sequence

The recommended bounded implementation order is:

1. encode the 18 new table definitions and constraints in one Database v2 schema specification;
2. add focused schema tests for keys, domains and FK structure;
3. extend the governed candidate builder from the existing Database v1 build path rather than creating an unrelated parallel database system;
4. load reusable reference/governance tables first;
5. build race extension and race-time tables;
6. build runner extension and missing-runner supplementations;
7. build horse specialist/transition/occurrence/assignment structures;
8. build participant label/candidate/identity/mapping structures;
9. add transparent study-facing views;
10. add one Database v2 source-wide validator that reconciles the complete integrated population without replacing the individual notebook validators;
11. build a local candidate against immutable Source Version 1;
12. run focused tests and individual required validators;
13. inspect any population or key mismatch rather than altering expected baselines automatically;
14. at final acceptance only, run the complete project test suite/all-validator gate and release-promotion checks.

## Current status

The semantic and relational design is sufficiently reconciled to begin schema/implementation work.

No unresolved user-level scope decision currently blocks the design. Remaining low-level choices such as exact deterministic codes, indexes and CHECK syntax are technical implementation decisions and may be selected under the existing architecture delegation, provided they preserve the governed semantics documented here.
