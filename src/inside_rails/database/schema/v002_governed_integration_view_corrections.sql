-- Pre-release correction to the combined runner view: a supplemented runner with
-- a verified positive finish position follows the same result model as a
-- source-backed finisher, so outcome_code remains null. The supplementation
-- evidence table still preserves verified_outcome='finished'.

BEGIN IMMEDIATE;

DROP VIEW view_governed_runner_records;

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
    CASE
        WHEN supplement.verified_finish_position IS NOT NULL THEN NULL
        ELSE supplement.verified_outcome
    END AS outcome_code,
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
