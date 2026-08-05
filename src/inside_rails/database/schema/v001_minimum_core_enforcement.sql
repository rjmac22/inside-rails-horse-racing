-- Independent-review enforcement for schema version 1.
-- This script is applied immediately after v001_minimum_core.sql when a clean
-- candidate schema is created. It replaces compatibility triggers with the
-- complete accepted-governance rule and adds a final structural reconciliation
-- before an import manifest can enter release_accepted.

DROP TRIGGER trg_race_governance_compatible_insert;
DROP TRIGGER trg_race_governance_compatible_update;
DROP TRIGGER trg_runner_structural_compatible_insert;
DROP TRIGGER trg_runner_structural_compatible_update;
DROP TRIGGER trg_manifest_governance_compatible_insert;
DROP TRIGGER trg_manifest_governance_compatible_update;

CREATE TRIGGER trg_race_governance_compatible_insert
BEFORE INSERT ON core_source_race_occurrence
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
      AND gr.release_status = 'accepted'
)
BEGIN
    SELECT RAISE(ABORT, 'race governance release is not accepted and compatible');
END;

CREATE TRIGGER trg_race_governance_compatible_update
BEFORE UPDATE OF source_version_id, governance_release_id ON core_source_race_occurrence
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_release AS gr
    WHERE gr.governance_release_id = NEW.governance_release_id
      AND gr.source_version_id = NEW.source_version_id
      AND gr.release_status = 'accepted'
)
BEGIN
    SELECT RAISE(ABORT, 'race governance release is not accepted and compatible');
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
      AND gr.release_status = 'accepted'
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
      AND gr.release_status = 'accepted'
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
    OR EXISTS (
        SELECT 1
        FROM core_source_race_occurrence AS race
        WHERE race.source_version_id = NEW.source_version_id
          AND race.governance_release_id <> NEW.governance_release_id
    )
    OR EXISTS (
        SELECT 1
        FROM core_runner_participation AS runner
        JOIN core_source_race_occurrence AS race
          ON race.source_race_occurrence_id = runner.source_race_occurrence_id
        JOIN source_raceform_v1_record AS sr
          ON sr.source_record_id = runner.source_record_id
        WHERE race.source_version_id = NEW.source_version_id
          AND (
              runner.governance_release_id <> NEW.governance_release_id
              OR race.governance_release_id <> NEW.governance_release_id
              OR sr.structural_status <> 'admitted_runner_record'
              OR runner.source_record_status <> 'admitted_runner_record'
              OR sr.source_version_id <> race.source_version_id
              OR NOT (sr."date" IS race.raw_date)
              OR NOT (sr."course" IS race.raw_course)
              OR NOT (sr."off" IS race.raw_off)
          )
    )
)
BEGIN
    SELECT RAISE(ABORT, 'release_accepted manifest has incompatible structural governance');
END;
