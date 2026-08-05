PRAGMA application_id = 1230130259;
PRAGMA user_version = 1;

CREATE TABLE source_provider (
    source_provider_id INTEGER PRIMARY KEY,
    source_provider_code TEXT NOT NULL UNIQUE,
    provider_label TEXT NOT NULL,
    provenance_note TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    CHECK(length(trim(source_provider_code)) > 0),
    CHECK(length(trim(provider_label)) > 0),
    CHECK(length(trim(provenance_note)) > 0),
    CHECK(length(created_at_utc) > 1 AND substr(created_at_utc, -1) = 'Z')
) STRICT;

CREATE TABLE source_product (
    source_product_id INTEGER PRIMARY KEY,
    source_product_code TEXT NOT NULL UNIQUE,
    source_provider_id INTEGER NOT NULL,
    product_label TEXT NOT NULL,
    product_description TEXT NOT NULL,
    acquisition_usage_note TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE(source_provider_id, source_product_code),
    CHECK(length(trim(source_product_code)) > 0),
    CHECK(length(trim(product_label)) > 0),
    CHECK(length(trim(product_description)) > 0),
    CHECK(length(trim(acquisition_usage_note)) > 0),
    CHECK(length(created_at_utc) > 1 AND substr(created_at_utc, -1) = 'Z'),
    FOREIGN KEY(source_provider_id) REFERENCES source_provider(source_provider_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE source_version (
    source_version_id INTEGER PRIMARY KEY,
    source_version_code TEXT NOT NULL UNIQUE,
    source_product_id INTEGER NOT NULL,
    original_filename TEXT NOT NULL,
    acquisition_description TEXT NOT NULL,
    file_sha256 BLOB NOT NULL UNIQUE,
    file_size_bytes INTEGER NOT NULL,
    received_date TEXT,
    source_schema_sha256 BLOB NOT NULL,
    physical_record_count INTEGER NOT NULL,
    admitted_record_count INTEGER NOT NULL,
    excluded_record_count INTEGER NOT NULL,
    admission_predicate TEXT NOT NULL,
    minimum_source_date TEXT NOT NULL,
    maximum_source_date TEXT NOT NULL,
    source_integrity_result TEXT NOT NULL,
    version_status TEXT NOT NULL,
    notes TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    CHECK(length(trim(source_version_code)) > 0),
    CHECK(length(trim(original_filename)) > 0),
    CHECK(length(trim(acquisition_description)) > 0),
    CHECK(typeof(file_sha256) = 'blob' AND length(file_sha256) = 32),
    CHECK(file_size_bytes > 0),
    CHECK(received_date IS NULL OR length(trim(received_date)) > 0),
    CHECK(typeof(source_schema_sha256) = 'blob' AND length(source_schema_sha256) = 32),
    CHECK(physical_record_count >= 0),
    CHECK(admitted_record_count >= 0),
    CHECK(excluded_record_count >= 0),
    CHECK(physical_record_count = admitted_record_count + excluded_record_count),
    CHECK(admission_predicate = 'rowid <> 1'),
    CHECK(length(trim(minimum_source_date)) > 0),
    CHECK(length(trim(maximum_source_date)) > 0),
    CHECK(source_integrity_result = 'ok'),
    CHECK(version_status = 'accepted_exact_source'),
    CHECK(length(trim(notes)) > 0),
    CHECK(length(created_at_utc) > 1 AND substr(created_at_utc, -1) = 'Z'),
    FOREIGN KEY(source_product_id) REFERENCES source_product(source_product_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE source_relation (
    source_relation_id INTEGER PRIMARY KEY,
    source_relation_code TEXT NOT NULL UNIQUE,
    source_version_id INTEGER NOT NULL,
    relation_name TEXT NOT NULL,
    relation_schema_sha256 BLOB NOT NULL,
    column_count INTEGER NOT NULL,
    physical_record_count INTEGER NOT NULL,
    admitted_record_count INTEGER NOT NULL,
    admission_predicate TEXT NOT NULL,
    UNIQUE(source_version_id, relation_name),
    UNIQUE(source_relation_id, source_version_id),
    CHECK(length(trim(source_relation_code)) > 0),
    CHECK(length(trim(relation_name)) > 0),
    CHECK(typeof(relation_schema_sha256) = 'blob' AND length(relation_schema_sha256) = 32),
    CHECK(column_count > 0),
    CHECK(physical_record_count > 0),
    CHECK(admitted_record_count >= 0 AND admitted_record_count <= physical_record_count),
    CHECK(length(trim(admission_predicate)) > 0),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE source_relation_field (
    source_relation_field_id INTEGER PRIMARY KEY,
    source_relation_id INTEGER NOT NULL,
    ordinal_position INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    declared_type TEXT NOT NULL,
    source_not_null INTEGER NOT NULL,
    source_default_sql TEXT,
    source_primary_key_ordinal INTEGER NOT NULL,
    UNIQUE(source_relation_id, ordinal_position),
    UNIQUE(source_relation_id, field_name),
    CHECK(ordinal_position >= 0),
    CHECK(length(field_name) > 0),
    CHECK(source_not_null IN (0, 1)),
    CHECK(source_primary_key_ordinal >= 0),
    FOREIGN KEY(source_relation_id) REFERENCES source_relation(source_relation_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE source_raceform_v1_record (
    source_record_id INTEGER PRIMARY KEY,
    source_record_code TEXT NOT NULL UNIQUE,
    source_version_id INTEGER NOT NULL,
    source_relation_id INTEGER NOT NULL,
    source_rowid INTEGER NOT NULL,
    structural_status TEXT NOT NULL,
    exclusion_reason TEXT,
    row_sha256 BLOB NOT NULL,
    "date",
    "course",
    "race_id",
    "off",
    "race_name",
    "type",
    "class",
    "pattern",
    "rating_band",
    "age_band",
    "sex_rest",
    "dist",
    "going",
    "ran",
    "num",
    "pos",
    "draw",
    "ovr_btn",
    "btn",
    "horse",
    "age",
    "sex",
    "wgt",
    "hg",
    "time",
    "sp",
    "jockey",
    "trainer",
    "prize",
    "or",
    "rpr",
    "ts",
    "sire",
    "dam",
    "damsire",
    "owner",
    "comment",
    UNIQUE(source_version_id, source_relation_id, source_rowid),
    UNIQUE(source_record_id, structural_status),
    CHECK(length(trim(source_record_code)) > 0),
    CHECK(source_rowid > 0),
    CHECK(structural_status IN ('admitted_runner_record', 'retained_excluded_record')),
    CHECK(typeof(row_sha256) = 'blob' AND length(row_sha256) = 32),
    CHECK(
        (
            source_rowid = 1
            AND structural_status = 'retained_excluded_record'
            AND exclusion_reason IS NOT NULL
            AND length(trim(exclusion_reason)) > 0
        )
        OR
        (
            source_rowid <> 1
            AND structural_status = 'admitted_runner_record'
            AND exclusion_reason IS NULL
        )
    ),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_relation_id, source_version_id)
        REFERENCES source_relation(source_relation_id, source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE governance_method (
    governance_method_id INTEGER PRIMARY KEY,
    governance_method_code TEXT NOT NULL UNIQUE,
    method_name TEXT NOT NULL,
    method_version INTEGER NOT NULL,
    repository_commit TEXT NOT NULL,
    method_description TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    CHECK(length(trim(governance_method_code)) > 0),
    CHECK(length(trim(method_name)) > 0),
    CHECK(method_version > 0),
    CHECK(length(repository_commit) = 40 AND repository_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(trim(method_description)) > 0),
    CHECK(length(created_at_utc) > 1 AND substr(created_at_utc, -1) = 'Z')
) STRICT;

CREATE TABLE governance_release (
    governance_release_id INTEGER PRIMARY KEY,
    governance_release_code TEXT NOT NULL UNIQUE,
    source_version_id INTEGER NOT NULL,
    governance_method_id INTEGER NOT NULL,
    release_status TEXT NOT NULL,
    accepted_date TEXT NOT NULL,
    repository_commit TEXT NOT NULL,
    population_predicate TEXT NOT NULL,
    release_description TEXT NOT NULL,
    superseded_by_release_id INTEGER,
    created_at_utc TEXT NOT NULL,
    UNIQUE(source_version_id, governance_release_code),
    CHECK(length(trim(governance_release_code)) > 0),
    CHECK(release_status IN ('accepted', 'superseded')),
    CHECK(length(trim(accepted_date)) > 0),
    CHECK(length(repository_commit) = 40 AND repository_commit NOT GLOB '*[^0-9a-f]*'),
    CHECK(length(trim(population_predicate)) > 0),
    CHECK(length(trim(release_description)) > 0),
    CHECK(
        (release_status = 'accepted' AND superseded_by_release_id IS NULL)
        OR
        (
            release_status = 'superseded'
            AND superseded_by_release_id IS NOT NULL
            AND superseded_by_release_id <> governance_release_id
        )
    ),
    CHECK(length(created_at_utc) > 1 AND substr(created_at_utc, -1) = 'Z'),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_method_id) REFERENCES governance_method(governance_method_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(superseded_by_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE governance_release_evidence (
    governance_release_evidence_id INTEGER PRIMARY KEY,
    governance_release_id INTEGER NOT NULL,
    evidence_type TEXT NOT NULL,
    evidence_reference TEXT NOT NULL,
    evidence_sha256 BLOB,
    evidence_description TEXT NOT NULL,
    UNIQUE(governance_release_id, evidence_type, evidence_reference),
    CHECK(evidence_type IN ('document', 'repository_artifact', 'validator', 'governed_output')),
    CHECK(length(trim(evidence_reference)) > 0),
    CHECK(evidence_sha256 IS NULL OR (typeof(evidence_sha256) = 'blob' AND length(evidence_sha256) = 32)),
    CHECK(length(trim(evidence_description)) > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE core_source_race_occurrence (
    source_race_occurrence_id INTEGER PRIMARY KEY,
    source_race_occurrence_code TEXT NOT NULL UNIQUE,
    source_version_id INTEGER NOT NULL,
    raw_date ANY NOT NULL,
    raw_course ANY NOT NULL,
    raw_off ANY NOT NULL,
    admitted_runner_count INTEGER NOT NULL,
    governance_release_id INTEGER NOT NULL,
    UNIQUE(source_version_id, raw_date, raw_course, raw_off),
    CHECK(length(trim(source_race_occurrence_code)) > 0),
    CHECK(admitted_runner_count > 0),
    FOREIGN KEY(source_version_id) REFERENCES source_version(source_version_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE core_runner_participation (
    runner_participation_id INTEGER PRIMARY KEY,
    runner_participation_code TEXT NOT NULL UNIQUE,
    source_race_occurrence_id INTEGER NOT NULL,
    source_record_id INTEGER NOT NULL UNIQUE,
    source_record_status TEXT NOT NULL,
    governance_release_id INTEGER NOT NULL,
    CHECK(length(trim(runner_participation_code)) > 0),
    CHECK(source_record_status = 'admitted_runner_record'),
    FOREIGN KEY(source_race_occurrence_id)
        REFERENCES core_source_race_occurrence(source_race_occurrence_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(source_record_id, source_record_status)
        REFERENCES source_raceform_v1_record(source_record_id, structural_status)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

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
    CHECK(schema_version = 1),
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

CREATE INDEX ix_source_raceform_v1_record_structural_status
    ON source_raceform_v1_record(structural_status);
CREATE INDEX ix_source_raceform_v1_record_admitted_race_group
    ON source_raceform_v1_record(source_version_id, source_relation_id, "date", "course", "off")
    WHERE structural_status = 'admitted_runner_record';
CREATE UNIQUE INDEX ux_governance_release_one_accepted_per_source_version
    ON governance_release(source_version_id)
    WHERE release_status = 'accepted';
CREATE INDEX ix_governance_release_source_version_status
    ON governance_release(source_version_id, release_status);
CREATE INDEX ix_governance_release_evidence_release
    ON governance_release_evidence(governance_release_id);
CREATE INDEX ix_core_runner_participation_race
    ON core_runner_participation(source_race_occurrence_id);
CREATE INDEX ix_core_runner_participation_governance_release
    ON core_runner_participation(governance_release_id);
CREATE INDEX ix_import_validation_result_manifest_stage_outcome
    ON import_validation_result(import_manifest_id, validation_stage, outcome);
CREATE UNIQUE INDEX ux_import_manifest_one_release_accepted
    ON import_manifest(build_status)
    WHERE build_status = 'release_accepted';

CREATE TRIGGER trg_race_governance_compatible_insert
BEFORE INSERT ON core_source_race_occurrence
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'race governance release is incompatible with source version');
END;

CREATE TRIGGER trg_race_governance_compatible_update
BEFORE UPDATE OF source_version_id, governance_release_id ON core_source_race_occurrence
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'race governance release is incompatible with source version');
END;

CREATE TRIGGER trg_runner_structural_compatible_insert
BEFORE INSERT ON core_runner_participation
WHEN NOT EXISTS (
    SELECT 1
    FROM source_raceform_v1_record AS sr
    JOIN core_source_race_occurrence AS race
      ON race.source_race_occurrence_id = NEW.source_race_occurrence_id
    JOIN governance_release AS gr
      ON gr.governance_release_id = NEW.governance_release_id
    WHERE sr.source_record_id = NEW.source_record_id
      AND sr.structural_status = 'admitted_runner_record'
      AND NEW.source_record_status = 'admitted_runner_record'
      AND sr.source_version_id = race.source_version_id
      AND sr."date" IS race.raw_date
      AND sr."course" IS race.raw_course
      AND sr."off" IS race.raw_off
      AND race.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = race.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'runner participation is structurally incompatible');
END;

CREATE TRIGGER trg_runner_structural_compatible_update
BEFORE UPDATE OF source_race_occurrence_id, source_record_id, source_record_status, governance_release_id
ON core_runner_participation
WHEN NOT EXISTS (
    SELECT 1
    FROM source_raceform_v1_record AS sr
    JOIN core_source_race_occurrence AS race
      ON race.source_race_occurrence_id = NEW.source_race_occurrence_id
    JOIN governance_release AS gr
      ON gr.governance_release_id = NEW.governance_release_id
    WHERE sr.source_record_id = NEW.source_record_id
      AND sr.structural_status = 'admitted_runner_record'
      AND NEW.source_record_status = 'admitted_runner_record'
      AND sr.source_version_id = race.source_version_id
      AND sr."date" IS race.raw_date
      AND sr."course" IS race.raw_course
      AND sr."off" IS race.raw_off
      AND race.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = race.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'runner participation is structurally incompatible');
END;

CREATE TRIGGER trg_manifest_governance_compatible_insert
BEFORE INSERT ON import_manifest
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'import manifest governance release is incompatible with source version');
END;

CREATE TRIGGER trg_manifest_governance_compatible_update
BEFORE UPDATE OF source_version_id, governance_release_id ON import_manifest
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
)
BEGIN
    SELECT RAISE(ABORT, 'import manifest governance release is incompatible with source version');
END;

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

CREATE TRIGGER trg_import_manifest_acceptance_update
BEFORE UPDATE OF build_status ON import_manifest
WHEN NEW.build_status = 'release_accepted' AND (
    NEW.physical_record_count <> 1851286
    OR NEW.admitted_record_count <> 1851285
    OR NEW.excluded_record_count <> 1
    OR NEW.race_occurrence_count <> 189043
    OR NEW.runner_participation_count <> 1851285
    OR NOT EXISTS (
        SELECT 1 FROM source_version AS sv
        WHERE sv.source_version_id = NEW.source_version_id
          AND sv.physical_record_count = NEW.physical_record_count
          AND sv.admitted_record_count = NEW.admitted_record_count
          AND sv.excluded_record_count = NEW.excluded_record_count
    )
    OR (SELECT COUNT(*) FROM source_raceform_v1_record AS sr
        WHERE sr.source_version_id = NEW.source_version_id) <> NEW.physical_record_count
    OR (SELECT COUNT(*) FROM source_raceform_v1_record AS sr
        WHERE sr.source_version_id = NEW.source_version_id
          AND sr.structural_status = 'admitted_runner_record') <> NEW.admitted_record_count
    OR (SELECT COUNT(*) FROM source_raceform_v1_record AS sr
        WHERE sr.source_version_id = NEW.source_version_id
          AND sr.structural_status = 'retained_excluded_record') <> NEW.excluded_record_count
    OR (SELECT COUNT(*) FROM core_source_race_occurrence AS race
        WHERE race.source_version_id = NEW.source_version_id) <> NEW.race_occurrence_count
    OR (SELECT COUNT(*)
        FROM core_runner_participation AS runner
        JOIN core_source_race_occurrence AS race
          ON race.source_race_occurrence_id = runner.source_race_occurrence_id
        WHERE race.source_version_id = NEW.source_version_id) <> NEW.runner_participation_count
    OR EXISTS (
        SELECT 1
        FROM core_source_race_occurrence AS race
        LEFT JOIN core_runner_participation AS runner
          ON runner.source_race_occurrence_id = race.source_race_occurrence_id
        WHERE race.source_version_id = NEW.source_version_id
        GROUP BY race.source_race_occurrence_id, race.admitted_runner_count
        HAVING COUNT(runner.runner_participation_id) <> race.admitted_runner_count
    )
    OR EXISTS (
        SELECT 1 FROM import_validation_result AS result
        WHERE result.import_manifest_id = NEW.import_manifest_id
          AND result.required_for_acceptance = 1
          AND result.outcome <> 'passed'
    )
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'focused_unit_tests' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'source_wide_validation' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'persisted_readback' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'sqlite_integrity' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'foreign_key_validation' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'post_load_validation' AND required_for_acceptance = 1 AND outcome = 'passed')
    OR NOT EXISTS (SELECT 1 FROM import_validation_result WHERE import_manifest_id = NEW.import_manifest_id AND validation_stage = 'project_acceptance_gate' AND required_for_acceptance = 1 AND outcome = 'passed')
)
BEGIN
    SELECT RAISE(ABORT, 'release_accepted manifest is incomplete or inconsistent');
END;

CREATE VIEW view_source_record_lineage AS
SELECT
    provider.source_provider_code,
    product.source_product_code,
    version.source_version_code,
    relation.source_relation_code,
    record.source_record_id,
    record.source_record_code,
    record.source_rowid,
    record.structural_status,
    record.exclusion_reason,
    lower(hex(record.row_sha256)) AS row_sha256_hex
FROM source_raceform_v1_record AS record
JOIN source_relation AS relation
  ON relation.source_relation_id = record.source_relation_id
 AND relation.source_version_id = record.source_version_id
JOIN source_version AS version
  ON version.source_version_id = record.source_version_id
JOIN source_product AS product
  ON product.source_product_id = version.source_product_id
JOIN source_provider AS provider
  ON provider.source_provider_id = product.source_provider_id;

CREATE VIEW view_source_raceform_v1_records AS
SELECT
    lineage.*,
    record."date",
    record."course",
    record."race_id",
    record."off",
    record."race_name",
    record."type",
    record."class",
    record."pattern",
    record."rating_band",
    record."age_band",
    record."sex_rest",
    record."dist",
    record."going",
    record."ran",
    record."num",
    record."pos",
    record."draw",
    record."ovr_btn",
    record."btn",
    record."horse",
    record."age",
    record."sex",
    record."wgt",
    record."hg",
    record."time",
    record."sp",
    record."jockey",
    record."trainer",
    record."prize",
    record."or",
    record."rpr",
    record."ts",
    record."sire",
    record."dam",
    record."damsire",
    record."owner",
    record."comment"
FROM view_source_record_lineage AS lineage
JOIN source_raceform_v1_record AS record
  ON record.source_record_id = lineage.source_record_id;

CREATE VIEW view_core_source_race_occurrences AS
SELECT
    race.source_race_occurrence_id,
    race.source_race_occurrence_code,
    version.source_version_code,
    race.raw_date,
    race.raw_course,
    race.raw_off,
    race.admitted_runner_count,
    release.governance_release_code,
    method.governance_method_code
FROM core_source_race_occurrence AS race
JOIN source_version AS version
  ON version.source_version_id = race.source_version_id
JOIN governance_release AS release
  ON release.governance_release_id = race.governance_release_id
JOIN governance_method AS method
  ON method.governance_method_id = release.governance_method_id;

CREATE VIEW view_core_runner_participations AS
SELECT
    runner.runner_participation_id,
    runner.runner_participation_code,
    race.source_race_occurrence_code,
    raw.source_record_code,
    raw.source_rowid,
    release.governance_release_code,
    raw.source_provider_code,
    raw.source_product_code,
    raw.source_version_code,
    raw.source_relation_code,
    raw.row_sha256_hex,
    raw."date",
    raw."course",
    raw."race_id",
    raw."off",
    raw."race_name",
    raw."type",
    raw."class",
    raw."pattern",
    raw."rating_band",
    raw."age_band",
    raw."sex_rest",
    raw."dist",
    raw."going",
    raw."ran",
    raw."num",
    raw."pos",
    raw."draw",
    raw."ovr_btn",
    raw."btn",
    raw."horse",
    raw."age",
    raw."sex",
    raw."wgt",
    raw."hg",
    raw."time",
    raw."sp",
    raw."jockey",
    raw."trainer",
    raw."prize",
    raw."or",
    raw."rpr",
    raw."ts",
    raw."sire",
    raw."dam",
    raw."damsire",
    raw."owner",
    raw."comment"
FROM core_runner_participation AS runner
JOIN core_source_race_occurrence AS race
  ON race.source_race_occurrence_id = runner.source_race_occurrence_id
JOIN governance_release AS release
  ON release.governance_release_id = runner.governance_release_id
JOIN view_source_raceform_v1_records AS raw
  ON raw.source_record_id = runner.source_record_id
WHERE raw.structural_status = 'admitted_runner_record';

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
