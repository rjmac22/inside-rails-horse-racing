-- Database v3 external-verification reconciliation migration.
--
-- Applied only to a verified copy of the accepted Database v2 release.
-- Source Version 1 and the accepted v2 release remain immutable.

BEGIN IMMEDIATE;

DROP VIEW IF EXISTS view_import_validation_evidence;
DROP VIEW IF EXISTS view_database_release_evidence;
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
    prior_database_release_code TEXT NOT NULL,
    prior_release_preserved INTEGER NOT NULL,
    build_status TEXT NOT NULL,
    failure_reason TEXT,
    CHECK(schema_version = 3),
    CHECK(length(code_commit) = 40 AND code_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(reference_data_commit) = 40 AND reference_data_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(physical_record_count = admitted_record_count + excluded_record_count),
    CHECK(persisted_readback_passed IN (0,1)),
    CHECK(sqlite_integrity_passed IN (0,1)),
    CHECK(foreign_key_check_passed IN (0,1)),
    CHECK(post_load_validation_passed IN (0,1)),
    CHECK(prior_release_preserved = 1),
    CHECK(build_status IN ('building','built','validated','release_accepted','failed','rolled_back')),
    CHECK((build_status IN ('failed','rolled_back') AND failure_reason IS NOT NULL) OR (build_status NOT IN ('failed','rolled_back') AND failure_reason IS NULL)),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id) ON UPDATE RESTRICT ON DELETE RESTRICT
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
    CHECK(validation_stage IN ('focused_unit_tests','source_wide_validation','persisted_readback','sqlite_integrity','foreign_key_validation','post_load_validation','project_acceptance_gate')),
    CHECK(required_for_acceptance IN (0,1)),
    CHECK(outcome IN ('passed','failed')),
    FOREIGN KEY(import_manifest_id) REFERENCES import_manifest(import_manifest_id) ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_import_validation_result_manifest_stage_outcome
    ON import_validation_result(import_manifest_id, validation_stage, outcome);
CREATE UNIQUE INDEX ux_import_manifest_one_release_accepted
    ON import_manifest(build_status) WHERE build_status = 'release_accepted';

CREATE TABLE governance_external_value_resolution (
    external_value_resolution_id INTEGER PRIMARY KEY,
    resolution_code TEXT NOT NULL UNIQUE,
    manual_verification_id INTEGER NOT NULL,
    source_record_id INTEGER,
    source_race_occurrence_id INTEGER NOT NULL,
    source_field TEXT NOT NULL,
    resolution_kind TEXT NOT NULL,
    governed_text_value TEXT,
    governed_integer_value INTEGER,
    governed_real_value REAL,
    governed_numerator INTEGER,
    governed_denominator INTEGER,
    governed_marker TEXT,
    governed_currency TEXT,
    governed_unit TEXT,
    analytical_action TEXT NOT NULL,
    notes TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(manual_verification_id, source_record_id, source_race_occurrence_id, source_field),
    CHECK(length(trim(resolution_code)) > 0),
    CHECK(length(trim(source_field)) > 0),
    CHECK(resolution_kind IN ('correction','enrichment','invalidation')),
    CHECK(governed_denominator IS NULL OR governed_denominator > 0),
    CHECK(governed_numerator IS NULL OR governed_numerator >= 0),
    CHECK((governed_numerator IS NULL) = (governed_denominator IS NULL)),
    CHECK(governed_currency IS NULL OR governed_currency IN ('USD','EUR','GBP')),
    CHECK(analytical_action IN ('replace','enrich','enrich_official_value','enrich_official_local_prize','null_known_wrong','replace_text_null_numeric')),
    CHECK(length(trim(notes)) > 0),
    CHECK(
        resolution_kind = 'invalidation'
        OR governed_text_value IS NOT NULL
        OR governed_integer_value IS NOT NULL
        OR governed_real_value IS NOT NULL
        OR governed_numerator IS NOT NULL
    ),
    FOREIGN KEY(manual_verification_id) REFERENCES governance_manual_verification(manual_verification_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_record_id) REFERENCES source_raceform_v1_record(source_record_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_race_occurrence_id) REFERENCES core_source_race_occurrence(source_race_occurrence_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id) ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_external_resolution_race_field
    ON governance_external_value_resolution(source_race_occurrence_id, source_field);
CREATE INDEX ix_external_resolution_record_field
    ON governance_external_value_resolution(source_record_id, source_field);

PRAGMA user_version = 3;

COMMIT;
