-- Database v2 pre-population schema corrections discovered while reconciling the
-- physical schema against the durable Notebook 13 parser contract.
--
-- This script runs immediately after v002_governed_integration.sql while the
-- governed runner extension is still empty. It exists separately so the
-- original migration history remains inspectable.

BEGIN IMMEDIATE;

DROP INDEX IF EXISTS ix_core_runner_participation_governed_result;
DROP INDEX IF EXISTS ix_core_runner_participation_governed_sp;

-- The table has just been created by the preceding v2 migration resource and
-- cannot contain governed runner rows yet. Dropping/recreating it avoids SQLite
-- rename-side effects on the already-created import acceptance trigger.
DROP TABLE core_runner_participation_governed;

CREATE TABLE core_runner_participation_governed (
    runner_participation_id INTEGER PRIMARY KEY,
    governance_release_id INTEGER NOT NULL,
    result_kind TEXT NOT NULL,
    finish_position INTEGER,
    outcome_code TEXT,
    weight_notation_family TEXT NOT NULL,
    carried_weight_stones INTEGER,
    carried_weight_remainder_pounds INTEGER,
    carried_weight_total_pounds INTEGER,
    carried_weight_implied_kg REAL,
    weight_parse_status TEXT NOT NULL,
    weight_ambiguity_flag INTEGER NOT NULL,
    weight_anomaly_flags_json TEXT NOT NULL,
    official_weight_verified INTEGER NOT NULL,
    starting_price_kind TEXT NOT NULL,
    starting_price_numerator INTEGER,
    starting_price_denominator INTEGER,
    starting_price_fractional_odds TEXT,
    starting_price_decimal_odds TEXT,
    starting_price_implied_probability TEXT,
    starting_price_favourite_marker TEXT,
    starting_price_favourite_status TEXT,
    starting_price_market_context_status TEXT NOT NULL,
    starting_price_analytical_numerator INTEGER,
    starting_price_analytical_denominator INTEGER,
    starting_price_analytical_favourite_status TEXT,
    starting_price_value_status TEXT NOT NULL,
    starting_price_manual_verification_id INTEGER,
    prize_source_presented_amount TEXT,
    prize_canonical_minor_units INTEGER,
    prize_currency TEXT,
    prize_interpretation_status TEXT NOT NULL,
    prize_interpretation_method TEXT NOT NULL,
    prize_conversion_multiplier TEXT,
    prize_confidence TEXT NOT NULL,
    source_num_storage_class TEXT NOT NULL,
    source_positive_runner_number INTEGER,
    source_num_state TEXT NOT NULL,
    source_num_within_race_multiplicity INTEGER,
    source_num_uniqueness_status TEXT NOT NULL,
    ovr_btn_numeric REAL,
    ovr_btn_status TEXT NOT NULL,
    btn_numeric REAL,
    btn_status TEXT NOT NULL,
    positive_official_winner_distance INTEGER NOT NULL,
    later_position_zero_overall INTEGER NOT NULL,
    same_distance_group INTEGER NOT NULL,
    beaten_distance_requires_review INTEGER NOT NULL,
    age_recorded INTEGER,
    age_interpretation_status TEXT NOT NULL,
    sex_normalised TEXT,
    sex_interpretation_status TEXT NOT NULL,
    sex_manual_verification_id INTEGER,
    headgear_raw_components_json TEXT NOT NULL,
    headgear_components_json TEXT NOT NULL,
    headgear_component_count INTEGER NOT NULL,
    headgear_use_suffix TEXT,
    headgear_source_declared_first_time INTEGER NOT NULL,
    headgear_interpretation_status TEXT NOT NULL,
    or_governed INTEGER,
    or_status TEXT NOT NULL,
    rpr_governed INTEGER,
    rpr_status TEXT NOT NULL,
    ts_governed INTEGER,
    ts_status TEXT NOT NULL,
    jockey_governed TEXT,
    jockey_value_status TEXT NOT NULL,
    jockey_connection_value_decision_id INTEGER,
    trainer_governed TEXT,
    trainer_value_status TEXT NOT NULL,
    trainer_connection_value_decision_id INTEGER,
    owner_governed TEXT,
    owner_value_status TEXT NOT NULL,
    owner_connection_value_decision_id INTEGER,
    comment_state TEXT NOT NULL,
    comment_analytically_available INTEGER NOT NULL,
    CHECK(result_kind IN ('finish_position', 'zero_sentinel', 'disqualified', 'non_finish_outcome', 'missing')),
    CHECK(finish_position IS NULL OR finish_position > 0),
    CHECK(
        (result_kind = 'finish_position' AND finish_position IS NOT NULL AND outcome_code IS NULL)
        OR
        (result_kind IN ('zero_sentinel', 'disqualified', 'non_finish_outcome') AND finish_position IS NULL AND outcome_code IS NOT NULL)
        OR
        (result_kind = 'missing' AND finish_position IS NULL AND outcome_code IS NULL)
    ),
    CHECK(carried_weight_remainder_pounds IS NULL OR (carried_weight_remainder_pounds >= 0 AND carried_weight_remainder_pounds <= 13)),
    CHECK(weight_ambiguity_flag IN (0, 1)),
    CHECK(length(weight_anomaly_flags_json) > 0),
    CHECK(official_weight_verified IN (0, 1)),
    CHECK(starting_price_kind IN ('fractional', 'evens', 'missing', 'unresolved')),
    CHECK(starting_price_numerator IS NULL OR starting_price_numerator >= 0),
    CHECK(starting_price_denominator IS NULL OR starting_price_denominator > 0),
    CHECK(starting_price_value_status IN ('source_parsed', 'externally_corrected', 'missing', 'unresolved')),
    CHECK(prize_canonical_minor_units IS NULL OR prize_canonical_minor_units >= 0),
    CHECK(prize_currency IS NULL OR prize_currency IN ('GBP', 'EUR')),
    CHECK(prize_interpretation_status IN ('blank', 'canonical', 'currency_unresolved', 'invalid')),
    CHECK(length(trim(prize_interpretation_method)) > 0),
    CHECK(prize_confidence IN ('confirmed', 'unresolved')),
    CHECK(source_positive_runner_number IS NULL OR source_positive_runner_number > 0),
    CHECK(source_num_state IN ('positive_integer', 'integer_zero', 'blank_text', 'null', 'invalid')),
    CHECK(source_num_within_race_multiplicity IS NULL OR source_num_within_race_multiplicity > 0),
    CHECK(source_num_uniqueness_status IN ('unassessed', 'unique_within_race', 'shared_positive_num', 'nonpositive_state')),
    CHECK(ovr_btn_status IN ('available', 'unavailable', 'unresolved')),
    CHECK(btn_status IN ('available', 'unavailable', 'unresolved')),
    CHECK(positive_official_winner_distance IN (0, 1)),
    CHECK(later_position_zero_overall IN (0, 1)),
    CHECK(same_distance_group IN (0, 1)),
    CHECK(beaten_distance_requires_review IN (0, 1)),
    CHECK(age_recorded IS NULL OR age_recorded >= 0),
    CHECK(age_interpretation_status IN ('source_recorded_integer', 'unresolved')),
    CHECK(sex_interpretation_status IN ('verified_common_code', 'verified_source_correction', 'unresolved')),
    CHECK(length(headgear_raw_components_json) > 0),
    CHECK(length(headgear_components_json) > 0),
    CHECK(headgear_component_count >= 0),
    CHECK(headgear_use_suffix IS NULL OR headgear_use_suffix = '1'),
    CHECK(headgear_source_declared_first_time IN (0, 1)),
    CHECK(headgear_interpretation_status IN ('blank_field_not_supplied', 'fully_decomposed_source_code', 'unresolved')),
    CHECK(or_status IN ('available', 'unavailable', 'invalid_source_value', 'unresolved_source_value')),
    CHECK(rpr_status IN ('available', 'unavailable', 'invalid_source_value', 'unresolved_source_value')),
    CHECK(ts_status IN ('available', 'unavailable', 'invalid_source_value', 'unresolved_source_value')),
    CHECK(jockey_value_status IN ('source_present', 'externally_supplemented', 'source_blank_unresolved')),
    CHECK(trainer_value_status IN ('source_present', 'externally_supplemented', 'source_blank_unresolved')),
    CHECK(owner_value_status IN ('source_present', 'externally_supplemented', 'source_blank_unresolved')),
    CHECK(comment_state IN ('empty_string', 'probable_placeholder', 'unresolved_source_code', 'substantive_text', 'unexpected_null')),
    CHECK(comment_analytically_available IN (0, 1)),
    FOREIGN KEY(runner_participation_id) REFERENCES core_runner_participation(runner_participation_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(starting_price_manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(sex_manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(jockey_connection_value_decision_id) REFERENCES governance_connection_value_decision(connection_value_decision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(trainer_connection_value_decision_id) REFERENCES governance_connection_value_decision(connection_value_decision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(owner_connection_value_decision_id) REFERENCES governance_connection_value_decision(connection_value_decision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_core_runner_participation_governed_result
    ON core_runner_participation_governed(result_kind, finish_position);
CREATE INDEX ix_core_runner_participation_governed_sp
    ON core_runner_participation_governed(starting_price_value_status, starting_price_kind);

COMMIT;
