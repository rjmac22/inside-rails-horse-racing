-- Database v4 Study 03 British racecourse/course identity migration.
--
-- Applied only to a verified disposable copy of accepted Database v3.
-- The v3 release and Source Version 1 remain immutable.

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
    CHECK(length(trim(import_manifest_code)) > 0),
    CHECK(length(trim(database_release_code)) > 0),
    CHECK(schema_version = 4),
    CHECK(length(code_commit) = 40 AND code_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(reference_data_commit) = 40 AND reference_data_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(trim(build_command)) > 0),
    CHECK(length(build_started_at_utc) > 1 AND substr(build_started_at_utc, -1) = 'Z'),
    CHECK(build_completed_at_utc IS NULL OR (length(build_completed_at_utc) > 1 AND substr(build_completed_at_utc, -1) = 'Z')),
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

CREATE TABLE governance_study03_racecourse_notebook (
    racecourse_notebook_id INTEGER PRIMARY KEY,
    source_notebook TEXT NOT NULL UNIQUE,
    notebook_sha256 BLOB NOT NULL,
    study_evidence_commit TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(source_notebook)) > 0),
    CHECK(typeof(notebook_sha256) = 'blob' AND length(notebook_sha256) = 32),
    CHECK(length(study_evidence_commit) = 40 AND study_evidence_commit NOT GLOB '*[^0-9a-f]*'),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE reference_racecourse_identity (
    racecourse_identity_id INTEGER PRIMARY KEY,
    racecourse_identity_code TEXT NOT NULL UNIQUE,
    racecourse_name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    identity_kind TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(jurisdiction, racecourse_name),
    CHECK(length(trim(racecourse_identity_code)) > 0),
    CHECK(length(trim(racecourse_name)) > 0),
    CHECK(jurisdiction = 'Great Britain'),
    CHECK(identity_kind IN ('venue','analytical_grouping')),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE reference_course_racecourse_map (
    reference_course_id INTEGER PRIMARY KEY,
    racecourse_identity_id INTEGER NOT NULL,
    racecourse_notebook_id INTEGER NOT NULL,
    study03_grouping_name TEXT NOT NULL DEFAULT 'pending_build_resolution',
    racecourse_resolution_method TEXT NOT NULL DEFAULT 'pending_build_resolution',
    racecourse_resolution_evidence TEXT NOT NULL DEFAULT 'pending_build_resolution',
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(study03_grouping_name)) > 0),
    CHECK(racecourse_resolution_method IN (
        'pending_build_resolution',
        'study03_identity_direct',
        'explicit_source_label',
        'source_label_convention'
    )),
    CHECK(length(trim(racecourse_resolution_evidence)) > 0),
    FOREIGN KEY(reference_course_id) REFERENCES reference_course(reference_course_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(racecourse_identity_id) REFERENCES reference_racecourse_identity(racecourse_identity_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(racecourse_notebook_id) REFERENCES governance_study03_racecourse_notebook(racecourse_notebook_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_reference_course_racecourse_map_identity
    ON reference_course_racecourse_map(racecourse_identity_id);

CREATE TABLE reference_racecourse_course_identity (
    course_identity_id INTEGER PRIMARY KEY,
    course_identity_code TEXT NOT NULL UNIQUE,
    racecourse_identity_id INTEGER NOT NULL,
    course_name TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(racecourse_identity_id, course_name),
    CHECK(length(trim(course_identity_code)) > 0),
    CHECK(length(trim(course_name)) > 0),
    FOREIGN KEY(racecourse_identity_id) REFERENCES reference_racecourse_identity(racecourse_identity_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_reference_racecourse_course_identity_parent
    ON reference_racecourse_course_identity(racecourse_identity_id);

CREATE TABLE reference_racecourse_course_inventory (
    course_inventory_id INTEGER PRIMARY KEY,
    course_identity_id INTEGER NOT NULL,
    racecourse_notebook_id INTEGER NOT NULL,
    source_row_number INTEGER NOT NULL,
    source_course_or_track_name TEXT NOT NULL,
    surface TEXT,
    inventory_payload_json TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(racecourse_notebook_id, source_row_number),
    CHECK(source_row_number > 0),
    CHECK(length(trim(source_course_or_track_name)) > 0),
    CHECK(surface IS NULL OR length(trim(surface)) > 0),
    FOREIGN KEY(course_identity_id) REFERENCES reference_racecourse_course_identity(course_identity_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(racecourse_notebook_id) REFERENCES governance_study03_racecourse_notebook(racecourse_notebook_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_reference_racecourse_course_inventory_identity
    ON reference_racecourse_course_inventory(course_identity_id);

CREATE TABLE governance_racecourse_unresolved_question (
    unresolved_question_id INTEGER PRIMARY KEY,
    racecourse_identity_id INTEGER NOT NULL,
    racecourse_notebook_id INTEGER NOT NULL,
    source_row_number INTEGER NOT NULL,
    question TEXT NOT NULL,
    impact TEXT,
    unresolved_class TEXT,
    verification_status TEXT,
    unresolved_payload_json TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(racecourse_notebook_id, source_row_number),
    CHECK(source_row_number > 0),
    CHECK(length(trim(question)) > 0),
    CHECK(impact IS NULL OR length(trim(impact)) > 0),
    CHECK(unresolved_class IS NULL OR length(trim(unresolved_class)) > 0),
    CHECK(verification_status IS NULL OR length(trim(verification_status)) > 0),
    FOREIGN KEY(racecourse_identity_id) REFERENCES reference_racecourse_identity(racecourse_identity_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(racecourse_notebook_id) REFERENCES governance_study03_racecourse_notebook(racecourse_notebook_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

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

CREATE VIEW view_gb_racecourse_identity_reference AS
SELECT
    course.reference_course_id,
    course.candidate_course_label,
    course.candidate_jurisdiction,
    racecourse.racecourse_identity_id,
    racecourse.racecourse_identity_code,
    racecourse.racecourse_name,
    racecourse.identity_kind,
    map.study03_grouping_name,
    map.racecourse_resolution_method,
    map.racecourse_resolution_evidence,
    notebook.source_notebook,
    hex(notebook.notebook_sha256) AS notebook_sha256_hex
FROM reference_course AS course
JOIN reference_course_racecourse_map AS map
  ON map.reference_course_id = course.reference_course_id
JOIN reference_racecourse_identity AS racecourse
  ON racecourse.racecourse_identity_id = map.racecourse_identity_id
JOIN governance_study03_racecourse_notebook AS notebook
  ON notebook.racecourse_notebook_id = map.racecourse_notebook_id
WHERE course.candidate_jurisdiction = 'Great Britain';

CREATE VIEW view_gb_course_track_identities AS
SELECT
    racecourse.racecourse_identity_code,
    racecourse.racecourse_name,
    racecourse.identity_kind,
    course.course_identity_id,
    course.course_identity_code,
    course.course_name,
    COUNT(inventory.course_inventory_id) AS inventory_state_rows
FROM reference_racecourse_course_identity AS course
JOIN reference_racecourse_identity AS racecourse
  ON racecourse.racecourse_identity_id = course.racecourse_identity_id
LEFT JOIN reference_racecourse_course_inventory AS inventory
  ON inventory.course_identity_id = course.course_identity_id
GROUP BY
    racecourse.racecourse_identity_code,
    racecourse.racecourse_name,
    racecourse.identity_kind,
    course.course_identity_id,
    course.course_identity_code,
    course.course_name;

CREATE VIEW view_gb_reconciled_race_occurrences_with_racecourse AS
SELECT
    race.*,
    racecourse.racecourse_identity_id,
    racecourse.racecourse_identity_code,
    racecourse.racecourse_name AS governed_racecourse_name,
    racecourse.identity_kind AS racecourse_identity_kind,
    map.study03_grouping_name,
    map.racecourse_resolution_method,
    map.racecourse_resolution_evidence
FROM view_reconciled_race_occurrences AS race
JOIN reference_course AS course
  ON course.candidate_course_label = race.candidate_course_label
 AND course.candidate_jurisdiction = race.candidate_jurisdiction
JOIN reference_course_racecourse_map AS map
  ON map.reference_course_id = course.reference_course_id
JOIN reference_racecourse_identity AS racecourse
  ON racecourse.racecourse_identity_id = map.racecourse_identity_id
WHERE race.candidate_jurisdiction = 'Great Britain';

PRAGMA user_version = 4;

COMMIT;
