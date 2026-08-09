-- Transparent study-facing views for Database v2.
--
-- These views do not hide unresolved states or replace immutable source values.
-- They expose governed values alongside their source lineage and keep externally
-- supplemented missing runners visibly separate from source-backed records.

BEGIN IMMEDIATE;

CREATE VIEW view_governed_race_occurrences AS
SELECT
    race.source_race_occurrence_id,
    race.source_race_occurrence_code,
    race.raw_date,
    race.raw_course,
    race.raw_off,
    race.admitted_runner_count,
    governed.candidate_course_label,
    governed.candidate_jurisdiction,
    governed.jurisdiction_evidence,
    governed.candidate_surface,
    governed.surface_evidence,
    governed.raw_dist,
    governed.distance_miles_component,
    governed.distance_whole_furlongs_component,
    governed.distance_has_half_furlong,
    governed.distance_total_furlongs,
    governed.distance_source_implied_yards,
    governed.distance_source_implied_metres,
    governed.distance_official_verified,
    governed.distance_parse_status,
    governed.source_reported_ran,
    governed.source_runner_row_count,
    governed.source_ran_consistency_status,
    governed.source_row_count_vs_ran_status,
    governed.source_runner_coverage_status,
    governed.source_ran_external_status,
    governed.race_name_raw,
    governed.race_type_raw,
    governed.class_raw,
    governed.class_number,
    governed.class_parse_status,
    governed.pattern_raw,
    governed.pattern_family,
    governed.pattern_level_raw,
    governed.pattern_parse_status,
    governed.rating_band_raw,
    governed.rating_lower_bound,
    governed.rating_upper_bound,
    governed.rating_band_parse_status,
    governed.age_band_raw,
    governed.stated_minimum_age,
    governed.stated_maximum_age,
    governed.age_band_open_ended,
    governed.age_band_syntax,
    governed.age_band_interpretation_status,
    governed.sex_rest_raw,
    governed.sex_rest_category,
    governed.sex_rest_interpretation_status,
    course.physical_venue_name,
    course.locality AS course_locality,
    course.region AS course_region,
    course.country AS course_country,
    course.latitude AS course_latitude,
    course.longitude AS course_longitude,
    course.iana_timezone,
    governed.jurisdiction_context_status,
    context.regulatory_authority,
    context.administrative_body,
    context.native_code_status,
    context.wagering_context_status,
    context.evidence_scope AS jurisdiction_context_evidence_scope,
    time.candidate_a_uk_naive,
    time.candidate_b_uk_naive,
    time.candidate_a_utc,
    time.candidate_b_utc,
    time.candidate_a_course_local,
    time.candidate_b_course_local,
    time.advertised_start_uk,
    time.advertised_start_utc,
    time.advertised_start_course_local,
    time.selected_branch,
    time.decision_method AS temporal_decision_method,
    time.decision_confidence AS temporal_decision_confidence,
    time.temporal_resolution_status
FROM core_source_race_occurrence AS race
JOIN core_source_race_occurrence_governed AS governed
  ON governed.source_race_occurrence_id = race.source_race_occurrence_id
JOIN reference_course AS course
  ON course.reference_course_id = governed.reference_course_id
LEFT JOIN reference_jurisdiction_context AS context
  ON context.jurisdiction_context_id = governed.jurisdiction_context_id
LEFT JOIN core_source_race_occurrence_time AS time
  ON time.source_race_occurrence_id = race.source_race_occurrence_id;

CREATE VIEW view_governed_horse_occurrence_assignments AS
SELECT
    runner.runner_participation_id,
    runner.runner_participation_code,
    source.source_record_id,
    source.source_record_code,
    source.source_rowid,
    source.horse AS raw_horse,
    assignment.pedigree_group_number,
    occurrence.horse_occurrence_id,
    occurrence.provisional_occurrence_code,
    occurrence.occurrence_sequence,
    occurrence.first_source_date,
    occurrence.last_source_date
FROM identity_runner_horse_occurrence AS assignment
JOIN core_runner_participation AS runner
  ON runner.runner_participation_id = assignment.runner_participation_id
JOIN source_raceform_v1_record AS source
  ON source.source_record_id = runner.source_record_id
JOIN identity_horse_occurrence AS occurrence
  ON occurrence.horse_occurrence_id = assignment.horse_occurrence_id;

CREATE VIEW view_governed_participant_label_identities AS
SELECT
    label.participant_source_label_id,
    label.participant_source_label_code,
    label.participant_role,
    label.raw_label,
    label.first_source_date,
    label.last_source_date,
    label.source_runner_rows,
    map.relationship_status,
    map.mapping_method,
    map.confidence AS mapping_confidence,
    map.evidence_reference,
    identity.participant_identity_id,
    identity.participant_identity_code,
    identity.identity_scope,
    identity.identity_status,
    identity.identity_method,
    identity.confidence AS identity_confidence,
    identity.review_status
FROM identity_participant_source_label AS label
LEFT JOIN identity_participant_label_map AS map
  ON map.participant_source_label_id = label.participant_source_label_id
LEFT JOIN identity_participant AS identity
  ON identity.participant_identity_id = map.participant_identity_id;

CREATE VIEW view_governed_source_runner_participations AS
SELECT
    runner.runner_participation_id,
    runner.runner_participation_code,
    race.source_race_occurrence_id,
    race.source_race_occurrence_code,
    source.source_record_id,
    source.source_record_code,
    source.source_rowid,
    source.date AS raw_date,
    source.course AS raw_course,
    source.off AS raw_off,
    source.race_id AS raw_race_id,
    source.horse AS raw_horse,
    source.sire AS raw_sire,
    source.dam AS raw_dam,
    source.damsire AS raw_damsire,
    source.pos AS raw_pos,
    governed.result_kind,
    governed.finish_position,
    governed.outcome_code,
    source.wgt AS raw_wgt,
    governed.weight_notation_family,
    governed.carried_weight_stones,
    governed.carried_weight_remainder_pounds,
    governed.carried_weight_total_pounds,
    governed.carried_weight_implied_kg,
    governed.weight_parse_status,
    source.sp AS raw_sp,
    governed.starting_price_kind,
    governed.starting_price_numerator,
    governed.starting_price_denominator,
    governed.starting_price_fractional_odds,
    governed.starting_price_decimal_odds,
    governed.starting_price_implied_probability,
    governed.starting_price_favourite_marker,
    governed.starting_price_favourite_status,
    governed.starting_price_market_context_status,
    governed.starting_price_analytical_numerator,
    governed.starting_price_analytical_denominator,
    governed.starting_price_analytical_favourite_status,
    governed.starting_price_value_status,
    source.prize AS raw_prize,
    governed.prize_source_presented_amount,
    governed.prize_canonical_minor_units,
    governed.prize_currency,
    governed.prize_interpretation_status,
    governed.prize_interpretation_method,
    governed.prize_confidence,
    source.num AS raw_num,
    governed.source_num_storage_class,
    governed.source_positive_runner_number,
    governed.source_num_state,
    governed.source_num_within_race_multiplicity,
    governed.source_num_uniqueness_status,
    source.ovr_btn AS raw_ovr_btn,
    governed.ovr_btn_numeric,
    governed.ovr_btn_status,
    source.btn AS raw_btn,
    governed.btn_numeric,
    governed.btn_status,
    governed.positive_official_winner_distance,
    governed.later_position_zero_overall,
    governed.same_distance_group,
    governed.beaten_distance_requires_review,
    source.age AS raw_age,
    governed.age_recorded,
    governed.age_interpretation_status,
    source.sex AS raw_sex,
    governed.sex_normalised,
    governed.sex_interpretation_status,
    sex_verification.verification_code AS sex_verification_code,
    source.hg AS raw_hg,
    governed.headgear_raw_components_json,
    governed.headgear_components_json,
    governed.headgear_component_count,
    governed.headgear_use_suffix,
    governed.headgear_source_declared_first_time,
    governed.headgear_interpretation_status,
    source.or AS raw_or,
    governed.or_governed,
    governed.or_status,
    source.rpr AS raw_rpr,
    governed.rpr_governed,
    governed.rpr_status,
    source.ts AS raw_ts,
    governed.ts_governed,
    governed.ts_status,
    source.jockey AS raw_jockey,
    governed.jockey_governed,
    governed.jockey_value_status,
    jockey_identity.participant_identity_code AS jockey_provisional_identity_code,
    source.trainer AS raw_trainer,
    governed.trainer_governed,
    governed.trainer_value_status,
    trainer_identity.participant_identity_code AS trainer_provisional_identity_code,
    source.owner AS raw_owner,
    governed.owner_governed,
    governed.owner_value_status,
    owner_identity.participant_identity_code AS owner_provisional_identity_code,
    source.comment AS raw_comment,
    governed.comment_state,
    governed.comment_analytically_available,
    horse_occurrence.provisional_occurrence_code AS provisional_horse_occurrence_code
FROM core_runner_participation AS runner
JOIN core_source_race_occurrence AS race
  ON race.source_race_occurrence_id = runner.source_race_occurrence_id
JOIN source_raceform_v1_record AS source
  ON source.source_record_id = runner.source_record_id
JOIN core_runner_participation_governed AS governed
  ON governed.runner_participation_id = runner.runner_participation_id
LEFT JOIN governance_manual_verification AS sex_verification
  ON sex_verification.manual_verification_id = governed.sex_manual_verification_id
LEFT JOIN identity_runner_horse_occurrence AS horse_assignment
  ON horse_assignment.runner_participation_id = runner.runner_participation_id
LEFT JOIN identity_horse_occurrence AS horse_occurrence
  ON horse_occurrence.horse_occurrence_id = horse_assignment.horse_occurrence_id
LEFT JOIN identity_participant_source_label AS jockey_label
  ON jockey_label.participant_role = 'jockey'
 AND jockey_label.raw_label = source.jockey
LEFT JOIN identity_participant_label_map AS jockey_map
  ON jockey_map.participant_source_label_id = jockey_label.participant_source_label_id
LEFT JOIN identity_participant AS jockey_identity
  ON jockey_identity.participant_identity_id = jockey_map.participant_identity_id
LEFT JOIN identity_participant_source_label AS trainer_label
  ON trainer_label.participant_role = 'trainer'
 AND trainer_label.raw_label = source.trainer
LEFT JOIN identity_participant_label_map AS trainer_map
  ON trainer_map.participant_source_label_id = trainer_label.participant_source_label_id
LEFT JOIN identity_participant AS trainer_identity
  ON trainer_identity.participant_identity_id = trainer_map.participant_identity_id
LEFT JOIN identity_participant_source_label AS owner_label
  ON owner_label.participant_role = 'owner'
 AND owner_label.raw_label = source.owner
LEFT JOIN identity_participant_label_map AS owner_map
  ON owner_map.participant_source_label_id = owner_label.participant_source_label_id
LEFT JOIN identity_participant AS owner_identity
  ON owner_identity.participant_identity_id = owner_map.participant_identity_id;

-- Normal study-facing runner population. The union includes only facts actually
-- established for the three externally supplemented missing runners; unsupported
-- runner attributes stay null and record_origin remains explicit.
CREATE VIEW view_governed_runner_records AS
SELECT
    'source_record' AS record_origin,
    source_runner.source_race_occurrence_id,
    source_runner.source_race_occurrence_code,
    source_runner.runner_participation_id,
    source_runner.runner_participation_code,
    source_runner.source_record_id,
    source_runner.source_record_code,
    source_runner.source_rowid,
    source_runner.raw_horse AS horse_label,
    source_runner.result_kind,
    source_runner.finish_position,
    source_runner.outcome_code,
    source_runner.source_positive_runner_number,
    source_runner.starting_price_analytical_numerator,
    source_runner.starting_price_analytical_denominator,
    source_runner.starting_price_analytical_favourite_status,
    source_runner.starting_price_value_status,
    source_runner.jockey_governed,
    source_runner.trainer_governed,
    source_runner.owner_governed,
    source_runner.provisional_horse_occurrence_code,
    source_runner.jockey_provisional_identity_code,
    source_runner.trainer_provisional_identity_code,
    source_runner.owner_provisional_identity_code
FROM view_governed_source_runner_participations AS source_runner
UNION ALL
SELECT
    supplement.record_origin,
    race.source_race_occurrence_id,
    race.source_race_occurrence_code,
    NULL AS runner_participation_id,
    NULL AS runner_participation_code,
    NULL AS source_record_id,
    NULL AS source_record_code,
    NULL AS source_rowid,
    supplement.source_horse AS horse_label,
    CASE
        WHEN supplement.verified_finish_position IS NOT NULL THEN 'finish_position'
        ELSE 'non_finish_outcome'
    END AS result_kind,
    supplement.verified_finish_position AS finish_position,
    supplement.verified_outcome AS outcome_code,
    NULL AS source_positive_runner_number,
    NULL AS starting_price_analytical_numerator,
    NULL AS starting_price_analytical_denominator,
    NULL AS starting_price_analytical_favourite_status,
    'unresolved' AS starting_price_value_status,
    NULL AS jockey_governed,
    NULL AS trainer_governed,
    NULL AS owner_governed,
    NULL AS provisional_horse_occurrence_code,
    NULL AS jockey_provisional_identity_code,
    NULL AS trainer_provisional_identity_code,
    NULL AS owner_provisional_identity_code
FROM governance_runner_record_supplementation AS supplement
JOIN core_source_race_occurrence AS race
  ON race.source_race_occurrence_id = supplement.source_race_occurrence_id;

COMMIT;
