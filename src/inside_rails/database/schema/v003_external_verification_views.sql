-- Study-facing Database v3 views.
--
-- V2 views remain available for historical comparison. These v3 views add typed
-- external corrections/enrichments while retaining every raw/v2 value.

BEGIN IMMEDIATE;

CREATE VIEW view_reconciled_race_occurrences AS
SELECT
    base.*,
    CASE
        WHEN ran.external_value_resolution_id IS NOT NULL THEN ran.governed_integer_value
        WHEN base.source_reported_ran IS NOT NULL THEN base.source_reported_ran
        ELSE base.source_runner_row_count
    END AS governed_runner_count,
    CASE
        WHEN ran.external_value_resolution_id IS NOT NULL THEN 'externally_corrected'
        WHEN base.source_reported_ran IS NOT NULL THEN 'source_reported'
        ELSE 'source_rows_fallback'
    END AS governed_runner_count_status,
    ran.resolution_code AS runner_count_resolution_code,
    dist.governed_real_value AS external_official_distance_metres,
    CASE WHEN dist.external_value_resolution_id IS NULL THEN NULL ELSE 'externally_verified' END AS external_official_distance_status,
    dist.resolution_code AS official_distance_resolution_code,
    COALESCE(age_band.governed_text_value, base.age_band_raw) AS governed_age_band,
    CASE WHEN age_band.external_value_resolution_id IS NULL THEN base.stated_minimum_age ELSE 5 END AS governed_stated_minimum_age,
    CASE WHEN age_band.external_value_resolution_id IS NULL THEN base.stated_maximum_age ELSE NULL END AS governed_stated_maximum_age,
    CASE WHEN age_band.external_value_resolution_id IS NULL THEN base.age_band_open_ended ELSE 1 END AS governed_age_band_open_ended,
    CASE WHEN age_band.external_value_resolution_id IS NULL THEN base.age_band_interpretation_status ELSE 'externally_corrected' END AS governed_age_band_status,
    age_band.resolution_code AS age_band_resolution_code,
    actual_off.governed_text_value AS external_actual_off_time_uk_text,
    actual_off.resolution_code AS actual_off_resolution_code
FROM view_governed_race_occurrences AS base
LEFT JOIN governance_external_value_resolution AS ran
  ON ran.source_race_occurrence_id = base.source_race_occurrence_id
 AND ran.source_record_id IS NULL
 AND ran.source_field = 'ran'
LEFT JOIN governance_external_value_resolution AS dist
  ON dist.source_race_occurrence_id = base.source_race_occurrence_id
 AND dist.source_record_id IS NULL
 AND dist.source_field = 'dist'
LEFT JOIN governance_external_value_resolution AS age_band
  ON age_band.source_race_occurrence_id = base.source_race_occurrence_id
 AND age_band.source_record_id IS NULL
 AND age_band.source_field = 'age_band'
LEFT JOIN governance_external_value_resolution AS actual_off
  ON actual_off.source_race_occurrence_id = base.source_race_occurrence_id
 AND actual_off.source_record_id IS NULL
 AND actual_off.source_field = 'actual_off_time';

CREATE VIEW view_reconciled_source_runner_participations AS
SELECT
    base.*,
    CASE WHEN pos.external_value_resolution_id IS NOT NULL
         THEN pos.governed_integer_value ELSE base.finish_position END
        AS governed_finish_position,
    CASE WHEN pos.external_value_resolution_id IS NOT NULL
         THEN 'externally_corrected' ELSE base.result_kind END
        AS governed_result_status,
    pos.governed_text_value AS external_result_context,
    pos.resolution_code AS result_resolution_code,
    CASE WHEN sp.external_value_resolution_id IS NOT NULL
         THEN sp.governed_numerator ELSE base.starting_price_analytical_numerator END
        AS governed_starting_price_numerator,
    CASE WHEN sp.external_value_resolution_id IS NOT NULL
         THEN sp.governed_denominator ELSE base.starting_price_analytical_denominator END
        AS governed_starting_price_denominator,
    CASE
        WHEN sp.external_value_resolution_id IS NOT NULL
        THEN 1.0 + (1.0 * sp.governed_numerator / sp.governed_denominator)
        WHEN base.starting_price_decimal_odds IS NOT NULL
        THEN CAST(base.starting_price_decimal_odds AS REAL)
        ELSE NULL
    END AS governed_starting_price_decimal_odds,
    CASE
        WHEN sp.external_value_resolution_id IS NOT NULL
        THEN 1.0 / (1.0 + (1.0 * sp.governed_numerator / sp.governed_denominator))
        WHEN base.starting_price_implied_probability IS NOT NULL
        THEN CAST(base.starting_price_implied_probability AS REAL)
        ELSE NULL
    END AS governed_starting_price_implied_probability,
    CASE WHEN sp.external_value_resolution_id IS NOT NULL
         THEN sp.governed_marker ELSE base.starting_price_analytical_favourite_status END
        AS governed_starting_price_favourite_status,
    CASE WHEN sp.external_value_resolution_id IS NOT NULL
         THEN 'externally_corrected' ELSE base.starting_price_value_status END
        AS governed_starting_price_value_status,
    sp.resolution_code AS starting_price_resolution_code,
    CASE
        WHEN ovr.analytical_action = 'null_known_wrong' THEN NULL
        WHEN ovr.external_value_resolution_id IS NOT NULL THEN ovr.governed_real_value
        ELSE base.ovr_btn_numeric
    END AS governed_ovr_btn_numeric,
    CASE
        WHEN ovr.analytical_action = 'null_known_wrong' THEN 'verified_source_error_unresolved_replacement'
        WHEN ovr.external_value_resolution_id IS NOT NULL THEN 'externally_corrected'
        ELSE base.ovr_btn_status
    END AS governed_ovr_btn_status,
    ovr.governed_text_value AS external_ovr_btn_text,
    ovr.resolution_code AS ovr_btn_resolution_code,
    CASE
        WHEN btn.analytical_action IN ('null_known_wrong','replace_text_null_numeric') THEN NULL
        WHEN btn.external_value_resolution_id IS NOT NULL THEN btn.governed_real_value
        ELSE base.btn_numeric
    END AS governed_btn_numeric,
    CASE
        WHEN btn.analytical_action = 'null_known_wrong' THEN 'verified_source_error_unresolved_replacement'
        WHEN btn.analytical_action = 'replace_text_null_numeric' THEN 'externally_corrected_text_only'
        WHEN btn.external_value_resolution_id IS NOT NULL THEN 'externally_corrected'
        ELSE base.btn_status
    END AS governed_btn_status,
    btn.governed_text_value AS external_btn_text,
    btn.resolution_code AS btn_resolution_code,
    CASE WHEN age.external_value_resolution_id IS NOT NULL
         THEN age.governed_integer_value ELSE base.age_recorded END AS governed_age,
    CASE WHEN age.external_value_resolution_id IS NOT NULL
         THEN 'externally_corrected' ELSE base.age_interpretation_status END AS governed_age_status,
    age.resolution_code AS age_resolution_code,
    prize.governed_real_value AS external_official_prize_amount,
    prize.governed_currency AS external_official_prize_currency,
    prize.resolution_code AS official_prize_resolution_code
FROM view_governed_source_runner_participations AS base
LEFT JOIN governance_external_value_resolution AS pos
  ON pos.source_record_id = base.source_record_id AND pos.source_field = 'pos'
LEFT JOIN governance_external_value_resolution AS sp
  ON sp.source_record_id = base.source_record_id AND sp.source_field = 'sp'
LEFT JOIN governance_external_value_resolution AS ovr
  ON ovr.source_record_id = base.source_record_id AND ovr.source_field = 'ovr_btn'
LEFT JOIN governance_external_value_resolution AS btn
  ON btn.source_record_id = base.source_record_id AND btn.source_field = 'btn'
LEFT JOIN governance_external_value_resolution AS age
  ON age.source_record_id = base.source_record_id AND age.source_field = 'age'
LEFT JOIN governance_external_value_resolution AS prize
  ON prize.source_record_id = base.source_record_id AND prize.source_field = 'prize';

CREATE VIEW view_reconciled_runner_records AS
SELECT
    'source_record' AS record_origin,
    source.source_race_occurrence_id,
    source.source_race_occurrence_code,
    source.runner_participation_id,
    source.runner_participation_code,
    source.source_record_id,
    source.source_record_code,
    source.source_rowid,
    source.raw_horse AS horse_label,
    source.result_kind,
    source.governed_finish_position AS finish_position,
    source.outcome_code,
    source.source_positive_runner_number,
    source.governed_starting_price_numerator AS starting_price_analytical_numerator,
    source.governed_starting_price_denominator AS starting_price_analytical_denominator,
    source.governed_starting_price_favourite_status AS starting_price_analytical_favourite_status,
    source.governed_starting_price_value_status AS starting_price_value_status,
    source.jockey_governed,
    source.trainer_governed,
    source.owner_governed,
    source.provisional_horse_occurrence_code,
    source.jockey_provisional_identity_code,
    source.trainer_provisional_identity_code,
    source.owner_provisional_identity_code,
    source.external_official_prize_amount,
    source.external_official_prize_currency
FROM view_reconciled_source_runner_participations AS source
UNION ALL
SELECT
    legacy.record_origin,
    legacy.source_race_occurrence_id,
    legacy.source_race_occurrence_code,
    legacy.runner_participation_id,
    legacy.runner_participation_code,
    legacy.source_record_id,
    legacy.source_record_code,
    legacy.source_rowid,
    legacy.horse_label,
    legacy.result_kind,
    legacy.finish_position,
    legacy.outcome_code,
    legacy.source_positive_runner_number,
    legacy.starting_price_analytical_numerator,
    legacy.starting_price_analytical_denominator,
    legacy.starting_price_analytical_favourite_status,
    legacy.starting_price_value_status,
    legacy.jockey_governed,
    legacy.trainer_governed,
    legacy.owner_governed,
    legacy.provisional_horse_occurrence_code,
    legacy.jockey_provisional_identity_code,
    legacy.trainer_provisional_identity_code,
    legacy.owner_provisional_identity_code,
    NULL AS external_official_prize_amount,
    NULL AS external_official_prize_currency
FROM view_governed_runner_records AS legacy
WHERE legacy.record_origin = 'externally_supplemented';

COMMIT;
