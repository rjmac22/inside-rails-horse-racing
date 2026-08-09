-- Database v2 governed-integration migration.
--
-- This script upgrades a disposable/candidate copy of the accepted Database v1
-- schema. The accepted v1 release itself must never be opened writable.
-- Python migration code disables foreign-key enforcement before executing this
-- transaction because the v1 import-manifest tables are deliberately rebuilt.
-- Foreign keys are re-enabled and checked immediately after the transaction.

BEGIN IMMEDIATE;

-- Database v2 records its own build evidence. The separately retained accepted
-- Database v1 file remains the immutable authority for the v1 release manifest.
DROP VIEW IF EXISTS view_import_validation_evidence;
DROP VIEW IF EXISTS view_database_release_evidence;

DROP TRIGGER IF EXISTS trg_import_manifest_acceptance_insert;
DROP TRIGGER IF EXISTS trg_import_manifest_acceptance_structural_recheck;
DROP TRIGGER IF EXISTS trg_import_manifest_acceptance_update;
DROP TRIGGER IF EXISTS trg_import_manifest_initial_status;
DROP TRIGGER IF EXISTS trg_import_manifest_state_transition;
DROP TRIGGER IF EXISTS trg_manifest_governance_compatible_insert;
DROP TRIGGER IF EXISTS trg_manifest_governance_compatible_update;

DROP INDEX IF EXISTS ix_import_validation_result_manifest_stage_outcome;
DROP INDEX IF EXISTS ux_import_manifest_one_release_accepted;

DROP TABLE import_validation_result;
DROP TABLE import_manifest;

CREATE TABLE import_manifest (
    import_manifest_id INTEGER PRIMARY KEY,
    import_manifest_code TEXT NOT NULL UNIQUE,
    database_release_code TEXT NOT NULL UNIQUE,
    source_version_id INTEGER NOT NULL,
    governance_release_id INTEGER NOT NULL,
    schema_version INTEGER NOT NULL,
    code_commit TEXT NOT NULL,
    reference_data_commit TEXT NOT NULL,
    build_command TEXT NOT NULL,
    build_started_at_utc TEXT NOT NULL,
    build_completed_at_utc TEXT,
    physical_record_count INTEGER NOT NULL,
    admitted_record_count INTEGER NOT NULL,
    excluded_record_count INTEGER NOT NULL,
    race_occurrence_count INTEGER NOT NULL,
    runner_participation_count INTEGER NOT NULL,
    persisted_readback_passed INTEGER NOT NULL,
    sqlite_integrity_passed INTEGER NOT NULL,
    foreign_key_check_passed INTEGER NOT NULL,
    post_load_validation_passed INTEGER NOT NULL,
    prior_database_release_code TEXT,
    prior_release_preserved INTEGER NOT NULL,
    build_status TEXT NOT NULL,
    failure_reason TEXT,
    CHECK(length(trim(import_manifest_code)) > 0),
    CHECK(length(trim(database_release_code)) > 0),
    CHECK(schema_version = 2),
    CHECK(length(code_commit) = 40 AND code_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(reference_data_commit) = 40 AND reference_data_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(trim(build_command)) > 0),
    CHECK(length(build_started_at_utc) > 1 AND substr(build_started_at_utc, -1) = 'Z'),
    CHECK(build_completed_at_utc IS NULL OR (length(build_completed_at_utc) > 1 AND substr(build_completed_at_utc, -1) = 'Z')),
    CHECK(physical_record_count >= 0),
    CHECK(admitted_record_count >= 0),
    CHECK(excluded_record_count >= 0),
    CHECK(race_occurrence_count >= 0),
    CHECK(runner_participation_count >= 0),
    CHECK(physical_record_count = admitted_record_count + excluded_record_count),
    CHECK(persisted_readback_passed IN (0, 1)),
    CHECK(sqlite_integrity_passed IN (0, 1)),
    CHECK(foreign_key_check_passed IN (0, 1)),
    CHECK(post_load_validation_passed IN (0, 1)),
    CHECK(prior_release_preserved IN (0, 1)),
    CHECK(build_status IN ('building', 'built', 'validated', 'release_accepted', 'failed', 'rolled_back')),
    CHECK(
        (build_status IN ('failed', 'rolled_back') AND failure_reason IS NOT NULL AND length(trim(failure_reason)) > 0)
        OR
        (build_status NOT IN ('failed', 'rolled_back') AND failure_reason IS NULL)
    ),
    CHECK(
        build_status <> 'release_accepted'
        OR
        (
            build_completed_at_utc IS NOT NULL
            AND persisted_readback_passed = 1
            AND sqlite_integrity_passed = 1
            AND foreign_key_check_passed = 1
            AND post_load_validation_passed = 1
            AND prior_database_release_code IS NOT NULL
            AND length(trim(prior_database_release_code)) > 0
            AND prior_release_preserved = 1
            AND failure_reason IS NULL
        )
    ),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE import_validation_result (
    import_validation_result_id INTEGER PRIMARY KEY,
    import_manifest_id INTEGER NOT NULL,
    validation_stage TEXT NOT NULL,
    validator_name TEXT NOT NULL,
    validator_version TEXT NOT NULL,
    required_for_acceptance INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    executed_at_utc TEXT NOT NULL,
    command TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    details_artifact_path TEXT,
    UNIQUE(import_manifest_id, validation_stage, validator_name, validator_version),
    CHECK(validation_stage IN (
        'focused_unit_tests',
        'source_wide_validation',
        'persisted_readback',
        'sqlite_integrity',
        'foreign_key_validation',
        'post_load_validation',
        'project_acceptance_gate'
    )),
    CHECK(length(trim(validator_name)) > 0),
    CHECK(length(trim(validator_version)) > 0),
    CHECK(required_for_acceptance IN (0, 1)),
    CHECK(outcome IN ('passed', 'failed')),
    CHECK(length(executed_at_utc) > 1 AND substr(executed_at_utc, -1) = 'Z'),
    CHECK(length(trim(command)) > 0),
    CHECK(length(trim(result_summary)) > 0),
    CHECK(details_artifact_path IS NULL OR length(trim(details_artifact_path)) > 0),
    FOREIGN KEY(import_manifest_id) REFERENCES import_manifest(import_manifest_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_import_validation_result_manifest_stage_outcome
    ON import_validation_result(import_manifest_id, validation_stage, outcome);
CREATE UNIQUE INDEX ux_import_manifest_one_release_accepted
    ON import_manifest(build_status)
    WHERE build_status = 'release_accepted';

-- Reusable governed course identity established by Notebook 12.
CREATE TABLE reference_course (
    reference_course_id INTEGER PRIMARY KEY,
    candidate_course_label TEXT NOT NULL,
    candidate_jurisdiction TEXT NOT NULL,
    physical_venue_name TEXT,
    locality TEXT,
    region TEXT,
    country TEXT,
    latitude REAL,
    longitude REAL,
    iana_timezone TEXT NOT NULL,
    location_evidence TEXT,
    location_validation_status TEXT NOT NULL,
    raw_course_labels TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(candidate_course_label, candidate_jurisdiction),
    CHECK(length(trim(candidate_course_label)) > 0),
    CHECK(length(trim(candidate_jurisdiction)) > 0),
    CHECK(latitude IS NULL OR (latitude >= -90.0 AND latitude <= 90.0)),
    CHECK(longitude IS NULL OR (longitude >= -180.0 AND longitude <= 180.0)),
    CHECK(length(trim(iana_timezone)) > 0),
    CHECK(length(trim(location_validation_status)) > 0),
    CHECK(length(trim(raw_course_labels)) > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- Bounded Notebook 09 regulatory/administrative context reference.
CREATE TABLE reference_jurisdiction_context (
    jurisdiction_context_id INTEGER PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    source_type TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    regulatory_authority TEXT NOT NULL,
    administrative_body TEXT,
    native_code_status TEXT NOT NULL,
    wagering_context_status TEXT NOT NULL,
    evidence_scope TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(jurisdiction)) > 0),
    CHECK(length(trim(source_type)) > 0),
    CHECK(length(trim(effective_from)) > 0),
    CHECK(effective_to IS NULL OR effective_to >= effective_from),
    CHECK(length(trim(regulatory_authority)) > 0),
    CHECK(administrative_body IS NULL OR length(trim(administrative_body)) > 0),
    CHECK(length(trim(native_code_status)) > 0),
    CHECK(length(trim(wagering_context_status)) > 0),
    CHECK(length(trim(evidence_scope)) > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_reference_jurisdiction_context_lookup
    ON reference_jurisdiction_context(jurisdiction, source_type, effective_from, effective_to);

-- Notebook 10 field-treatment metadata. This records authorised processing, not values.
CREATE TABLE governance_source_field_treatment (
    source_field_treatment_id INTEGER PRIMARY KEY,
    source_relation_field_id INTEGER NOT NULL,
    analytical_family TEXT NOT NULL,
    investigation_group TEXT NOT NULL,
    treatment TEXT NOT NULL,
    governing_notebook TEXT NOT NULL,
    audit_status TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_relation_field_id, governance_release_id),
    CHECK(length(trim(analytical_family)) > 0),
    CHECK(length(trim(investigation_group)) > 0),
    CHECK(length(trim(treatment)) > 0),
    CHECK(length(trim(governing_notebook)) > 0),
    CHECK(length(trim(audit_status)) > 0),
    FOREIGN KEY(source_relation_field_id) REFERENCES source_relation_field(source_relation_field_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- Generic bounded manual/external verification evidence.
CREATE TABLE governance_manual_verification (
    manual_verification_id INTEGER PRIMARY KEY,
    verification_code TEXT NOT NULL UNIQUE,
    subject_type TEXT NOT NULL,
    source_record_id INTEGER,
    source_race_occurrence_id INTEGER,
    reference_course_id INTEGER,
    source_relation_field_id INTEGER,
    source_date TEXT,
    source_course TEXT,
    source_off TEXT,
    source_horse TEXT,
    source_field TEXT,
    raw_source_value TEXT,
    verification_question TEXT NOT NULL,
    verified_value TEXT,
    verification_status TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    evidence_locator TEXT NOT NULL,
    evidence_accessed_date TEXT,
    governing_notebook TEXT NOT NULL,
    confidence TEXT NOT NULL,
    notes TEXT NOT NULL,
    database_action TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(verification_code)) > 0),
    CHECK(length(trim(subject_type)) > 0),
    CHECK(
        source_record_id IS NOT NULL
        OR source_race_occurrence_id IS NOT NULL
        OR reference_course_id IS NOT NULL
        OR source_relation_field_id IS NOT NULL
        OR source_date IS NOT NULL
        OR source_course IS NOT NULL
        OR source_off IS NOT NULL
        OR source_horse IS NOT NULL
        OR source_field IS NOT NULL
        OR raw_source_value IS NOT NULL
    ),
    CHECK(length(trim(verification_question)) > 0),
    CHECK(verification_status IN ('confirmed', 'contradicted', 'partially_confirmed', 'unresolved')),
    CHECK(length(trim(evidence_type)) > 0),
    CHECK(length(trim(evidence_locator)) > 0),
    CHECK(length(trim(governing_notebook)) > 0),
    CHECK(confidence IN ('high', 'medium', 'low')),
    CHECK(length(trim(notes)) > 0),
    CHECK(database_action IN (
        'evidence_only',
        'label_equivalence',
        'reference_enrichment',
        'source_supplementation',
        'source_correction_candidate',
        'preserve_raw_unresolved'
    )),
    CHECK(verification_status <> 'confirmed' OR (verified_value IS NOT NULL AND length(trim(verified_value)) > 0)),
    FOREIGN KEY(source_record_id) REFERENCES source_raceform_v1_record(source_record_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_race_occurrence_id) REFERENCES core_source_race_occurrence(source_race_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(reference_course_id) REFERENCES reference_course(reference_course_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_relation_field_id) REFERENCES source_relation_field(source_relation_field_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_governance_manual_verification_subject
    ON governance_manual_verification(subject_type, source_race_occurrence_id, source_record_id);

-- Exact Notebook 20 blank connection-field decisions.
CREATE TABLE governance_connection_value_decision (
    connection_value_decision_id INTEGER PRIMARY KEY,
    connection_decision_code TEXT NOT NULL UNIQUE,
    source_record_id INTEGER NOT NULL,
    source_relation_field_id INTEGER NOT NULL,
    manual_verification_id INTEGER NOT NULL,
    governed_value TEXT,
    value_status TEXT NOT NULL,
    confidence TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_record_id, source_relation_field_id),
    CHECK(length(trim(connection_decision_code)) > 0),
    CHECK(value_status IN ('externally_supplemented', 'source_blank_unresolved')),
    CHECK(confidence IN ('high', 'medium', 'low')),
    CHECK(
        (value_status = 'externally_supplemented' AND governed_value IS NOT NULL AND length(trim(governed_value)) > 0)
        OR
        (value_status = 'source_blank_unresolved' AND governed_value IS NULL)
    ),
    FOREIGN KEY(source_record_id) REFERENCES source_raceform_v1_record(source_record_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_relation_field_id) REFERENCES source_relation_field(source_relation_field_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- Three externally verified runners absent from immutable source rows.
CREATE TABLE governance_runner_record_supplementation (
    runner_record_supplementation_id INTEGER PRIMARY KEY,
    supplementation_code TEXT NOT NULL UNIQUE,
    manual_verification_id INTEGER NOT NULL,
    source_race_occurrence_id INTEGER NOT NULL,
    source_horse TEXT NOT NULL,
    source_runner_rows INTEGER NOT NULL,
    source_reported_ran INTEGER NOT NULL,
    published_runner_count INTEGER NOT NULL,
    verified_finish_position INTEGER,
    verified_outcome TEXT,
    record_origin TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_race_occurrence_id, source_horse),
    CHECK(length(trim(source_horse)) > 0),
    CHECK(source_runner_rows > 0),
    CHECK(source_reported_ran > 0),
    CHECK(published_runner_count > 0),
    CHECK(verified_finish_position IS NULL OR verified_finish_position > 0),
    CHECK(verified_outcome IS NULL OR length(trim(verified_outcome)) > 0),
    CHECK(record_origin = 'externally_supplemented'),
    FOREIGN KEY(manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_race_occurrence_id) REFERENCES core_source_race_occurrence(source_race_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- Notebook 19 specialist governance reference. This is deliberately separate
-- from the complete 353-row source-derived transition population.
CREATE TABLE governance_horse_pedigree_specialist_decision (
    horse_pedigree_specialist_decision_id INTEGER PRIMARY KEY,
    specialist_decision_code TEXT NOT NULL UNIQUE,
    source_horse_label TEXT NOT NULL,
    decision_scope TEXT NOT NULL,
    analytical_outcome TEXT NOT NULL,
    raw_sire TEXT,
    raw_dam TEXT,
    raw_damsire TEXT,
    governed_sire TEXT,
    governed_dam TEXT,
    governed_damsire TEXT,
    verification_status TEXT NOT NULL,
    verification_code TEXT NOT NULL,
    evidence_locator TEXT NOT NULL,
    confidence TEXT NOT NULL,
    notes TEXT NOT NULL,
    manual_verification_id INTEGER,
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(specialist_decision_code)) > 0),
    CHECK(length(trim(source_horse_label)) > 0),
    CHECK(length(trim(decision_scope)) > 0),
    CHECK(analytical_outcome IN ('Corrected', 'Different horse', 'Unresolved')),
    CHECK(verification_status IN ('confirmed', 'unresolved')),
    CHECK(length(trim(verification_code)) > 0),
    CHECK(length(trim(evidence_locator)) > 0),
    CHECK(confidence IN ('high', 'medium', 'low')),
    CHECK(length(trim(notes)) > 0),
    CHECK(
        analytical_outcome <> 'Unresolved'
        OR (governed_sire IS NULL AND governed_dam IS NULL AND governed_damsire IS NULL)
    ),
    FOREIGN KEY(manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- General one-row-per-race governed semantic extension.
CREATE TABLE core_source_race_occurrence_governed (
    source_race_occurrence_id INTEGER PRIMARY KEY,
    governance_release_id INTEGER NOT NULL,
    candidate_course_label TEXT NOT NULL,
    candidate_jurisdiction TEXT NOT NULL,
    jurisdiction_evidence TEXT NOT NULL,
    reference_course_id INTEGER NOT NULL,
    jurisdiction_context_id INTEGER,
    jurisdiction_context_status TEXT NOT NULL,
    candidate_surface TEXT NOT NULL,
    surface_evidence TEXT NOT NULL,
    raw_dist TEXT NOT NULL,
    distance_miles_component INTEGER,
    distance_whole_furlongs_component INTEGER,
    distance_has_half_furlong INTEGER,
    distance_total_furlongs REAL,
    distance_source_implied_yards INTEGER,
    distance_source_implied_metres REAL,
    distance_official_verified INTEGER NOT NULL,
    distance_parse_status TEXT NOT NULL,
    distance_parser_version TEXT NOT NULL,
    source_reported_ran INTEGER,
    source_runner_row_count INTEGER NOT NULL,
    source_ran_distinct_value_count INTEGER NOT NULL,
    source_ran_consistency_status TEXT NOT NULL,
    source_row_count_vs_ran_status TEXT NOT NULL,
    source_runner_coverage_status TEXT NOT NULL,
    source_ran_external_status TEXT NOT NULL,
    source_ran_manual_verification_id INTEGER,
    race_name_raw TEXT,
    race_type_raw TEXT,
    class_raw TEXT,
    pattern_raw TEXT,
    rating_band_raw TEXT,
    age_band_raw TEXT,
    sex_rest_raw TEXT,
    class_number INTEGER,
    class_parse_status TEXT NOT NULL,
    pattern_family TEXT,
    pattern_level_raw TEXT,
    pattern_parse_status TEXT NOT NULL,
    rating_lower_bound INTEGER,
    rating_upper_bound INTEGER,
    rating_band_parse_status TEXT NOT NULL,
    stated_minimum_age INTEGER,
    stated_maximum_age INTEGER,
    age_band_open_ended INTEGER,
    age_band_syntax TEXT NOT NULL,
    age_band_interpretation_status TEXT NOT NULL,
    sex_rest_category TEXT,
    sex_rest_interpretation_status TEXT NOT NULL,
    CHECK(length(trim(candidate_course_label)) > 0),
    CHECK(length(trim(candidate_jurisdiction)) > 0),
    CHECK(length(trim(jurisdiction_evidence)) > 0),
    CHECK(jurisdiction_context_status IN ('matched', 'unresearched')),
    CHECK(candidate_surface IN ('all_weather_unspecified', 'unresolved')),
    CHECK(surface_evidence IN ('explicit_course_all_weather_marker', 'no_source_surface_evidence')),
    CHECK(distance_has_half_furlong IS NULL OR distance_has_half_furlong IN (0, 1)),
    CHECK(distance_official_verified IN (0, 1)),
    CHECK(distance_parse_status IN ('parsed', 'unresolved')),
    CHECK(length(trim(distance_parser_version)) > 0),
    CHECK(source_reported_ran IS NULL OR source_reported_ran > 0),
    CHECK(source_runner_row_count > 0),
    CHECK(source_ran_distinct_value_count >= 0),
    CHECK(source_ran_consistency_status IN ('consistent', 'conflicting', 'invalid', 'missing')),
    CHECK(source_row_count_vs_ran_status IN ('equal', 'below', 'above', 'not_comparable')),
    CHECK(source_runner_coverage_status IN ('unverified', 'internally_equal_to_ran', 'known_partial', 'externally_verified_complete')),
    CHECK(source_ran_external_status IN ('unverified', 'externally_verified', 'externally_contradicted')),
    CHECK(class_parse_status IN ('blank', 'canonical', 'unrecognised')),
    CHECK(pattern_family IS NULL OR pattern_family IN ('Listed', 'Group', 'Grade')),
    CHECK(pattern_parse_status IN ('blank', 'canonical', 'unrecognised')),
    CHECK(rating_band_parse_status IN ('blank', 'canonical', 'unrecognised_source_form', 'invalid_range_order')),
    CHECK(age_band_open_ended IS NULL OR age_band_open_ended IN (0, 1)),
    CHECK(age_band_syntax IN ('blank', 'exact_age', 'open_ended_minimum', 'closed_age_range', 'invalid_range_order', 'unrecognised')),
    CHECK(age_band_interpretation_status IN ('blank', 'source_stated_bounds_only', 'unresolved')),
    CHECK(sex_rest_interpretation_status IN ('blank', 'explicit_source_category', 'overloaded_source_category', 'unrecognised_source_category')),
    CHECK(
        distance_parse_status <> 'parsed'
        OR (
            distance_miles_component IS NOT NULL
            AND distance_whole_furlongs_component IS NOT NULL
            AND distance_has_half_furlong IS NOT NULL
            AND distance_total_furlongs IS NOT NULL
            AND distance_source_implied_yards IS NOT NULL
            AND distance_source_implied_metres IS NOT NULL
        )
    ),
    CHECK(
        distance_parse_status <> 'unresolved'
        OR (
            distance_miles_component IS NULL
            AND distance_whole_furlongs_component IS NULL
            AND distance_has_half_furlong IS NULL
            AND distance_total_furlongs IS NULL
            AND distance_source_implied_yards IS NULL
            AND distance_source_implied_metres IS NULL
        )
    ),
    FOREIGN KEY(source_race_occurrence_id) REFERENCES core_source_race_occurrence(source_race_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(reference_course_id) REFERENCES reference_course(reference_course_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(jurisdiction_context_id) REFERENCES reference_jurisdiction_context(jurisdiction_context_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_ran_manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_core_source_race_occurrence_governed_course
    ON core_source_race_occurrence_governed(reference_course_id);
CREATE INDEX ix_core_source_race_occurrence_governed_context
    ON core_source_race_occurrence_governed(jurisdiction_context_id);
CREATE INDEX ix_core_source_race_occurrence_governed_surface
    ON core_source_race_occurrence_governed(candidate_jurisdiction, candidate_surface);

-- Complete Notebook 11 advertised-start representation.
CREATE TABLE core_source_race_occurrence_time (
    source_race_occurrence_id INTEGER PRIMARY KEY,
    governance_release_id INTEGER NOT NULL,
    candidate_a_uk_naive TEXT,
    candidate_b_uk_naive TEXT,
    candidate_a_utc TEXT,
    candidate_b_utc TEXT,
    candidate_a_course_local TEXT,
    candidate_b_course_local TEXT,
    advertised_start_uk TEXT,
    advertised_start_utc TEXT,
    advertised_start_course_local TEXT,
    selected_branch TEXT,
    decision_method TEXT NOT NULL,
    decision_confidence TEXT NOT NULL,
    temporal_resolution_status TEXT NOT NULL,
    CHECK(selected_branch IS NULL OR selected_branch IN ('candidate_a', 'candidate_b', 'explicit_24h')),
    CHECK(decision_method IN ('course_local_dead_of_night_rejection', 'stable_post_boundary_course_profile', 'explicit_post_boundary_time', 'unresolved')),
    CHECK(decision_confidence IN ('high', 'supported', 'source_explicit', 'unresolved')),
    CHECK(temporal_resolution_status IN ('resolved', 'unresolved')),
    CHECK(
        temporal_resolution_status <> 'resolved'
        OR (
            advertised_start_uk IS NOT NULL
            AND advertised_start_utc IS NOT NULL
            AND advertised_start_course_local IS NOT NULL
            AND selected_branch IS NOT NULL
        )
    ),
    CHECK(
        temporal_resolution_status <> 'unresolved'
        OR (
            advertised_start_uk IS NULL
            AND advertised_start_utc IS NULL
            AND advertised_start_course_local IS NULL
            AND selected_branch IS NULL
            AND decision_method = 'unresolved'
            AND decision_confidence = 'unresolved'
        )
    ),
    FOREIGN KEY(source_race_occurrence_id) REFERENCES core_source_race_occurrence(source_race_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_core_source_race_occurrence_time_resolution
    ON core_source_race_occurrence_time(temporal_resolution_status, decision_method);
CREATE INDEX ix_core_source_race_occurrence_time_utc
    ON core_source_race_occurrence_time(advertised_start_utc)
    WHERE advertised_start_utc IS NOT NULL;

-- One-to-one governed analytical extension for source-backed runner participations.
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
    CHECK(length(trim(prize_interpretation_status)) > 0),
    CHECK(length(trim(prize_interpretation_method)) > 0),
    CHECK(prize_confidence IN ('high', 'medium', 'low')),
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
    CHECK(headgear_source_declared_first_time IN (0, 1)),
    CHECK(length(trim(headgear_interpretation_status)) > 0),
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

-- Notebook 19 provisional occurrence identity.
CREATE TABLE identity_horse_occurrence (
    horse_occurrence_id INTEGER PRIMARY KEY,
    provisional_occurrence_code TEXT NOT NULL UNIQUE,
    source_horse_label TEXT NOT NULL,
    occurrence_sequence INTEGER NOT NULL,
    pedigree_group_count INTEGER NOT NULL,
    runner_row_count INTEGER NOT NULL,
    first_source_date TEXT NOT NULL,
    last_source_date TEXT NOT NULL,
    minimum_recorded_age INTEGER,
    maximum_recorded_age INTEGER,
    sex_values TEXT NOT NULL,
    unresolved_boundary_count INTEGER NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_horse_label, occurrence_sequence),
    CHECK(length(trim(provisional_occurrence_code)) > 0),
    CHECK(length(trim(source_horse_label)) > 0),
    CHECK(occurrence_sequence > 0),
    CHECK(pedigree_group_count > 0),
    CHECK(runner_row_count > 0),
    CHECK(length(trim(first_source_date)) > 0),
    CHECK(length(trim(last_source_date)) > 0),
    CHECK(last_source_date >= first_source_date),
    CHECK(unresolved_boundary_count >= 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE identity_runner_horse_occurrence (
    runner_participation_id INTEGER PRIMARY KEY,
    horse_occurrence_id INTEGER NOT NULL,
    pedigree_group_number INTEGER NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(pedigree_group_number > 0),
    FOREIGN KEY(runner_participation_id) REFERENCES core_runner_participation(runner_participation_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(horse_occurrence_id) REFERENCES identity_horse_occurrence(horse_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_runner_horse_occurrence_occurrence
    ON identity_runner_horse_occurrence(horse_occurrence_id);

CREATE TABLE identity_horse_pedigree_decision (
    horse_pedigree_decision_id INTEGER PRIMARY KEY,
    horse_pedigree_decision_code TEXT NOT NULL UNIQUE,
    source_horse_label TEXT NOT NULL,
    from_pedigree_group_number INTEGER NOT NULL,
    to_pedigree_group_number INTEGER NOT NULL,
    from_sire TEXT,
    from_dam_key_kind TEXT NOT NULL,
    from_dam_name TEXT,
    from_dam_country TEXT,
    from_damsire TEXT,
    from_first_date TEXT NOT NULL,
    from_last_date TEXT NOT NULL,
    from_minimum_age INTEGER,
    from_maximum_age INTEGER,
    from_runner_rows INTEGER NOT NULL,
    from_provisional_races INTEGER NOT NULL,
    to_sire TEXT,
    to_dam_key_kind TEXT NOT NULL,
    to_dam_name TEXT,
    to_dam_country TEXT,
    to_damsire TEXT,
    to_first_date TEXT NOT NULL,
    to_minimum_age INTEGER,
    gap_days INTEGER NOT NULL,
    sire_changed INTEGER NOT NULL,
    dam_changed INTEGER NOT NULL,
    damsire_changed INTEGER NOT NULL,
    pedigree_components_changed INTEGER NOT NULL,
    analytical_outcome TEXT NOT NULL,
    decision_basis TEXT NOT NULL,
    identity_split INTEGER,
    horse_pedigree_specialist_decision_id INTEGER,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_horse_label, from_pedigree_group_number, to_pedigree_group_number),
    CHECK(length(trim(horse_pedigree_decision_code)) > 0),
    CHECK(length(trim(source_horse_label)) > 0),
    CHECK(from_pedigree_group_number > 0),
    CHECK(to_pedigree_group_number = from_pedigree_group_number + 1),
    CHECK(from_dam_key_kind IN ('blank', 'parsed_suffix', 'raw_unsuffixed')),
    CHECK(to_dam_key_kind IN ('blank', 'parsed_suffix', 'raw_unsuffixed')),
    CHECK(from_runner_rows > 0),
    CHECK(from_provisional_races > 0),
    CHECK(gap_days > 0),
    CHECK(sire_changed IN (0, 1)),
    CHECK(dam_changed IN (0, 1)),
    CHECK(damsire_changed IN (0, 1)),
    CHECK(pedigree_components_changed = sire_changed + dam_changed + damsire_changed),
    CHECK(pedigree_components_changed BETWEEN 1 AND 3),
    CHECK(analytical_outcome IN ('Corrected', 'Different horse', 'Unresolved')),
    CHECK(length(trim(decision_basis)) > 0),
    CHECK(
        (analytical_outcome = 'Corrected' AND identity_split = 0)
        OR (analytical_outcome = 'Different horse' AND identity_split = 1)
        OR (analytical_outcome = 'Unresolved' AND identity_split IS NULL)
    ),
    FOREIGN KEY(horse_pedigree_specialist_decision_id)
        REFERENCES governance_horse_pedigree_specialist_decision(horse_pedigree_specialist_decision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_horse_pedigree_decision_horse
    ON identity_horse_pedigree_decision(source_horse_label, from_pedigree_group_number);

-- Notebook 22 role-specific source labels and provisional identities.
CREATE TABLE identity_participant_source_label (
    participant_source_label_id INTEGER PRIMARY KEY,
    participant_source_label_code TEXT NOT NULL UNIQUE,
    participant_role TEXT NOT NULL,
    raw_label TEXT NOT NULL,
    first_source_date TEXT NOT NULL,
    last_source_date TEXT NOT NULL,
    source_runner_rows INTEGER NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(participant_role, raw_label),
    CHECK(participant_role IN ('jockey', 'trainer', 'owner')),
    CHECK(length(raw_label) > 0),
    CHECK(length(trim(first_source_date)) > 0),
    CHECK(length(trim(last_source_date)) > 0),
    CHECK(last_source_date >= first_source_date),
    CHECK(source_runner_rows > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE identity_participant (
    participant_identity_id INTEGER PRIMARY KEY,
    participant_identity_code TEXT NOT NULL UNIQUE,
    participant_role TEXT NOT NULL,
    identity_scope TEXT NOT NULL,
    identity_status TEXT NOT NULL,
    identity_method TEXT NOT NULL,
    confidence TEXT NOT NULL,
    review_status TEXT NOT NULL,
    created_by_notebook TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(participant_role IN ('jockey', 'trainer', 'owner')),
    CHECK(identity_scope IN ('person_label_identity', 'ownership_composition')),
    CHECK(length(trim(identity_status)) > 0),
    CHECK(length(trim(identity_method)) > 0),
    CHECK(length(trim(confidence)) > 0),
    CHECK(length(trim(review_status)) > 0),
    CHECK(length(trim(created_by_notebook)) > 0),
    CHECK((participant_role = 'owner' AND identity_scope = 'ownership_composition') OR (participant_role IN ('jockey', 'trainer') AND identity_scope = 'person_label_identity')),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE identity_participant_candidate (
    participant_candidate_id INTEGER PRIMARY KEY,
    participant_candidate_code TEXT NOT NULL UNIQUE,
    participant_role TEXT NOT NULL,
    candidate_key TEXT NOT NULL,
    candidate_method TEXT NOT NULL,
    candidate_structure TEXT,
    evidence_status TEXT,
    identity_relationship TEXT NOT NULL,
    decision_status TEXT NOT NULL,
    decision_basis TEXT NOT NULL,
    confidence TEXT NOT NULL,
    verification_code TEXT,
    evidence_type TEXT,
    evidence_locator TEXT,
    evidence_accessed_date TEXT,
    review_status TEXT NOT NULL,
    review_notes TEXT,
    database_action TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(participant_role IN ('jockey', 'trainer', 'owner')),
    CHECK(length(trim(candidate_key)) > 0),
    CHECK(length(trim(candidate_method)) > 0),
    CHECK(length(trim(identity_relationship)) > 0),
    CHECK(decision_status IN ('accepted', 'confirmed_distinct', 'unresolved')),
    CHECK(length(trim(decision_basis)) > 0),
    CHECK(length(trim(confidence)) > 0),
    CHECK(length(trim(review_status)) > 0),
    CHECK(length(trim(database_action)) > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_participant_candidate_role_status
    ON identity_participant_candidate(participant_role, decision_status);

CREATE TABLE identity_participant_candidate_label (
    participant_candidate_id INTEGER NOT NULL,
    participant_source_label_id INTEGER NOT NULL,
    candidate_label_role TEXT,
    governance_release_id INTEGER NOT NULL,
    PRIMARY KEY(participant_candidate_id, participant_source_label_id),
    FOREIGN KEY(participant_candidate_id) REFERENCES identity_participant_candidate(participant_candidate_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(participant_source_label_id) REFERENCES identity_participant_source_label(participant_source_label_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_participant_candidate_label_source
    ON identity_participant_candidate_label(participant_source_label_id);

CREATE TABLE identity_participant_label_map (
    participant_identity_label_map_id INTEGER PRIMARY KEY,
    participant_identity_id INTEGER NOT NULL,
    participant_source_label_id INTEGER NOT NULL,
    participant_candidate_id INTEGER NOT NULL,
    label_role TEXT,
    relationship_status TEXT NOT NULL,
    mapping_method TEXT NOT NULL,
    confidence TEXT NOT NULL,
    evidence_reference TEXT,
    database_action TEXT NOT NULL,
    effective_start_date TEXT,
    effective_end_date TEXT,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(participant_identity_id, participant_source_label_id),
    CHECK(relationship_status = 'accepted'),
    CHECK(length(trim(mapping_method)) > 0),
    CHECK(length(trim(confidence)) > 0),
    CHECK(length(trim(database_action)) > 0),
    CHECK(effective_end_date IS NULL OR effective_start_date IS NOT NULL),
    CHECK(effective_start_date IS NULL OR effective_end_date IS NULL OR effective_end_date >= effective_start_date),
    FOREIGN KEY(participant_identity_id) REFERENCES identity_participant(participant_identity_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(participant_source_label_id) REFERENCES identity_participant_source_label(participant_source_label_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(participant_candidate_id) REFERENCES identity_participant_candidate(participant_candidate_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_participant_label_map_source
    ON identity_participant_label_map(participant_source_label_id);
CREATE INDEX ix_identity_participant_label_map_identity
    ON identity_participant_label_map(participant_identity_id);

-- Connection decisions may only govern the three Notebook 20 connection fields.
CREATE TRIGGER trg_connection_value_decision_field_insert
BEFORE INSERT ON governance_connection_value_decision
WHEN NOT EXISTS (
    SELECT 1
    FROM source_relation_field AS field
    WHERE field.source_relation_field_id = NEW.source_relation_field_id
      AND field.field_name IN ('jockey', 'trainer', 'owner')
)
BEGIN
    SELECT RAISE(ABORT, 'connection decision field must be jockey, trainer or owner');
END;

CREATE TRIGGER trg_connection_value_decision_field_update
BEFORE UPDATE OF source_relation_field_id ON governance_connection_value_decision
WHEN NOT EXISTS (
    SELECT 1
    FROM source_relation_field AS field
    WHERE field.source_relation_field_id = NEW.source_relation_field_id
      AND field.field_name IN ('jockey', 'trainer', 'owner')
)
BEGIN
    SELECT RAISE(ABORT, 'connection decision field must be jockey, trainer or owner');
END;

-- An accepted participant map must be role-compatible and backed by an accepted candidate.
CREATE TRIGGER trg_participant_label_map_compatible_insert
BEFORE INSERT ON identity_participant_label_map
WHEN NOT EXISTS (
    SELECT 1
    FROM identity_participant AS identity
    JOIN identity_participant_source_label AS label
      ON label.participant_source_label_id = NEW.participant_source_label_id
    JOIN identity_participant_candidate AS candidate
      ON candidate.participant_candidate_id = NEW.participant_candidate_id
    WHERE identity.participant_identity_id = NEW.participant_identity_id
      AND identity.participant_role = label.participant_role
      AND candidate.participant_role = identity.participant_role
      AND candidate.decision_status = 'accepted'
      AND EXISTS (
          SELECT 1
          FROM identity_participant_candidate_label AS member
          WHERE member.participant_candidate_id = candidate.participant_candidate_id
            AND member.participant_source_label_id = label.participant_source_label_id
      )
)
BEGIN
    SELECT RAISE(ABORT, 'participant mapping is not backed by an accepted compatible candidate');
END;

-- Database v2 import-manifest lifecycle and compatibility controls.
CREATE TRIGGER trg_import_manifest_initial_status
BEFORE INSERT ON import_manifest
WHEN NEW.build_status <> 'building'
BEGIN
    SELECT RAISE(ABORT, 'import manifest must begin in building status');
END;

CREATE TRIGGER trg_import_manifest_state_transition
BEFORE UPDATE OF build_status ON import_manifest
WHEN NOT (
    NEW.build_status = OLD.build_status
    OR (OLD.build_status = 'building' AND NEW.build_status IN ('built', 'failed', 'rolled_back'))
    OR (OLD.build_status = 'built' AND NEW.build_status IN ('validated', 'failed', 'rolled_back'))
    OR (OLD.build_status = 'validated' AND NEW.build_status IN ('release_accepted', 'failed', 'rolled_back'))
    OR (OLD.build_status = 'failed' AND NEW.build_status = 'rolled_back')
)
BEGIN
    SELECT RAISE(ABORT, 'invalid import manifest state transition');
END;

CREATE TRIGGER trg_import_manifest_acceptance_insert
BEFORE INSERT ON import_manifest
WHEN NEW.build_status = 'release_accepted'
BEGIN
    SELECT RAISE(ABORT, 'release_accepted cannot be the initial import manifest state');
END;

CREATE TRIGGER trg_manifest_governance_compatible_insert
BEFORE INSERT ON import_manifest
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
      AND gr.release_status = 'accepted'
)
BEGIN
    SELECT RAISE(ABORT, 'import manifest governance release is not accepted and compatible');
END;

CREATE TRIGGER trg_manifest_governance_compatible_update
BEFORE UPDATE OF source_version_id, governance_release_id ON import_manifest
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
      AND gr.release_status = 'accepted'
)
BEGIN
    SELECT RAISE(ABORT, 'import manifest governance release is not accepted and compatible');
END;

CREATE TRIGGER trg_import_manifest_acceptance_update
BEFORE UPDATE OF build_status ON import_manifest
WHEN NEW.build_status = 'release_accepted' AND (
    NEW.physical_record_count <> 1851286
    OR NEW.admitted_record_count <> 1851285
    OR NEW.excluded_record_count <> 1
    OR NEW.race_occurrence_count <> 189043
    OR NEW.runner_participation_count <> 1851285
    OR NEW.schema_version <> 2
    OR NEW.prior_database_release_code IS NULL
    OR length(trim(NEW.prior_database_release_code)) = 0
    OR NEW.prior_release_preserved <> 1
)
BEGIN
    SELECT RAISE(ABORT, 'release_accepted manifest does not match Database v2 structural baseline');
END;

CREATE TRIGGER trg_import_manifest_acceptance_structural_recheck
BEFORE UPDATE OF build_status ON import_manifest
WHEN NEW.build_status = 'release_accepted' AND (
    NOT EXISTS (
        SELECT 1
        FROM governance_release AS gr
        WHERE gr.governance_release_id = NEW.governance_release_id
          AND gr.source_version_id = NEW.source_version_id
          AND gr.release_status = 'accepted'
    )
    OR (SELECT COUNT(*) FROM core_source_race_occurrence) <> 189043
    OR (SELECT COUNT(*) FROM core_runner_participation) <> 1851285
    OR EXISTS (
        SELECT 1
        FROM core_source_race_occurrence AS race
        LEFT JOIN governance_release AS gr
          ON gr.governance_release_id = race.governance_release_id
        WHERE gr.governance_release_id IS NULL
           OR gr.source_version_id <> race.source_version_id
           OR gr.release_status NOT IN ('accepted', 'superseded')
    )
    OR EXISTS (
        SELECT 1
        FROM core_runner_participation AS runner
        JOIN core_source_race_occurrence AS race
          ON race.source_race_occurrence_id = runner.source_race_occurrence_id
        JOIN source_raceform_v1_record AS sr
          ON sr.source_record_id = runner.source_record_id
        LEFT JOIN governance_release AS gr
          ON gr.governance_release_id = runner.governance_release_id
        WHERE sr.structural_status <> 'admitted_runner_record'
           OR runner.source_record_status <> 'admitted_runner_record'
           OR sr.source_version_id <> race.source_version_id
           OR NOT (sr."date" IS race.raw_date)
           OR NOT (sr."course" IS race.raw_course)
           OR NOT (sr."off" IS race.raw_off)
           OR runner.governance_release_id <> race.governance_release_id
           OR gr.governance_release_id IS NULL
           OR gr.source_version_id <> race.source_version_id
           OR gr.release_status NOT IN ('accepted', 'superseded')
    )
    OR (SELECT COUNT(*) FROM core_source_race_occurrence_governed) <> 189043
    OR EXISTS (SELECT 1 FROM core_source_race_occurrence_governed WHERE governance_release_id <> NEW.governance_release_id)
    OR (SELECT COUNT(*) FROM core_source_race_occurrence_time) <> 189043
    OR EXISTS (SELECT 1 FROM core_source_race_occurrence_time WHERE governance_release_id <> NEW.governance_release_id)
    OR (SELECT COUNT(*) FROM core_runner_participation_governed) <> 1851285
    OR EXISTS (SELECT 1 FROM core_runner_participation_governed WHERE governance_release_id <> NEW.governance_release_id)
    OR (SELECT COUNT(*) FROM reference_course) <> 395
    OR (SELECT COUNT(*) FROM reference_jurisdiction_context) <> 16
    OR (SELECT COUNT(*) FROM governance_source_field_treatment) <> 37
    OR (SELECT COUNT(*) FROM governance_connection_value_decision) <> 46
    OR (SELECT COUNT(*) FROM governance_runner_record_supplementation) <> 3
    OR (SELECT COUNT(*) FROM governance_horse_pedigree_specialist_decision) <> 16
    OR (SELECT COUNT(*) FROM identity_horse_occurrence) <> 611
    OR (SELECT COUNT(*) FROM identity_horse_pedigree_decision) <> 353
    OR (SELECT COUNT(*) FROM identity_participant_source_label) <> 116859
    OR (SELECT COUNT(*) FROM identity_participant) <> 68
    OR (SELECT COUNT(*) FROM identity_participant_label_map) <> 149
    OR (SELECT COUNT(*) FROM identity_participant_candidate) <> 1205
)
BEGIN
    SELECT RAISE(ABORT, 'release_accepted manifest failed Database v2 integrated structural recheck');
END;

-- Existing v1 audit views are recreated over the v2 build-evidence tables.
CREATE VIEW view_database_release_evidence AS
SELECT
    manifest.database_release_code,
    manifest.import_manifest_code,
    manifest.build_status,
    version.source_version_code,
    release.governance_release_code,
    manifest.schema_version,
    manifest.code_commit,
    manifest.reference_data_commit,
    manifest.build_started_at_utc,
    manifest.build_completed_at_utc,
    manifest.physical_record_count,
    manifest.admitted_record_count,
    manifest.excluded_record_count,
    manifest.race_occurrence_count,
    manifest.runner_participation_count,
    manifest.persisted_readback_passed,
    manifest.sqlite_integrity_passed,
    manifest.foreign_key_check_passed,
    manifest.post_load_validation_passed,
    manifest.prior_database_release_code,
    manifest.prior_release_preserved
FROM import_manifest AS manifest
JOIN source_version AS version
  ON version.source_version_id = manifest.source_version_id
JOIN governance_release AS release
  ON release.governance_release_id = manifest.governance_release_id;

CREATE VIEW view_import_validation_evidence AS
SELECT
    manifest.import_manifest_code,
    manifest.database_release_code,
    result.validation_stage,
    result.validator_name,
    result.validator_version,
    result.required_for_acceptance,
    result.outcome,
    result.executed_at_utc,
    result.command,
    result.result_summary,
    result.details_artifact_path
FROM import_validation_result AS result
JOIN import_manifest AS manifest
  ON manifest.import_manifest_id = result.import_manifest_id;

PRAGMA user_version = 2;

COMMIT;
