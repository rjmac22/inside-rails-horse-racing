-- Additional fail-closed relational enforcement for Database v2.
--
-- These rules govern relationships that cannot be expressed by a simple
-- single-row CHECK constraint. They are applied before any Database v2 semantic
-- population is inserted.

BEGIN IMMEDIATE;

-- A role-specific source label can have at most one accepted active mapping in
-- the current Database v2 model. Historical/effective-dated multi-mapping is not
-- currently governed; any future requirement must revisit this constraint.
CREATE UNIQUE INDEX ux_identity_participant_label_map_one_identity_per_source_label
    ON identity_participant_label_map(participant_source_label_id);

-- Candidate membership must remain role-compatible. Candidate generation is
-- deliberately role-scoped; a jockey label cannot become an owner/trainer
-- candidate member merely because the text is identical.
CREATE TRIGGER trg_participant_candidate_label_role_insert
BEFORE INSERT ON identity_participant_candidate_label
WHEN NOT EXISTS (
    SELECT 1
    FROM identity_participant_candidate AS candidate
    JOIN identity_participant_source_label AS label
      ON label.participant_source_label_id = NEW.participant_source_label_id
    WHERE candidate.participant_candidate_id = NEW.participant_candidate_id
      AND candidate.participant_role = label.participant_role
)
BEGIN
    SELECT RAISE(ABORT, 'participant candidate member role is incompatible');
END;

CREATE TRIGGER trg_participant_candidate_label_role_update
BEFORE UPDATE OF participant_candidate_id, participant_source_label_id
ON identity_participant_candidate_label
WHEN NOT EXISTS (
    SELECT 1
    FROM identity_participant_candidate AS candidate
    JOIN identity_participant_source_label AS label
      ON label.participant_source_label_id = NEW.participant_source_label_id
    WHERE candidate.participant_candidate_id = NEW.participant_candidate_id
      AND candidate.participant_role = label.participant_role
)
BEGIN
    SELECT RAISE(ABORT, 'participant candidate member role is incompatible');
END;

-- Effective-dated jurisdiction-context rows may not overlap for the same
-- jurisdiction/source-type pair. Zero or one context row may match a race date;
-- two matches would make the race-context relationship ambiguous.
CREATE TRIGGER trg_jurisdiction_context_no_overlap_insert
BEFORE INSERT ON reference_jurisdiction_context
WHEN EXISTS (
    SELECT 1
    FROM reference_jurisdiction_context AS existing
    WHERE existing.jurisdiction = NEW.jurisdiction
      AND existing.source_type = NEW.source_type
      AND COALESCE(existing.effective_to, '9999-12-31') >= NEW.effective_from
      AND COALESCE(NEW.effective_to, '9999-12-31') >= existing.effective_from
)
BEGIN
    SELECT RAISE(ABORT, 'jurisdiction context effective periods overlap');
END;

CREATE TRIGGER trg_jurisdiction_context_no_overlap_update
BEFORE UPDATE OF jurisdiction, source_type, effective_from, effective_to
ON reference_jurisdiction_context
WHEN EXISTS (
    SELECT 1
    FROM reference_jurisdiction_context AS existing
    WHERE existing.jurisdiction_context_id <> NEW.jurisdiction_context_id
      AND existing.jurisdiction = NEW.jurisdiction
      AND existing.source_type = NEW.source_type
      AND COALESCE(existing.effective_to, '9999-12-31') >= NEW.effective_from
      AND COALESCE(NEW.effective_to, '9999-12-31') >= existing.effective_from
)
BEGIN
    SELECT RAISE(ABORT, 'jurisdiction context effective periods overlap');
END;

-- Notebook 20 decisions are intentionally limited to the three connection
-- fields reviewed in that notebook. Reject any other physical source field.
CREATE TRIGGER trg_connection_decision_field_insert
BEFORE INSERT ON governance_connection_value_decision
WHEN NOT EXISTS (
    SELECT 1
    FROM source_relation_field AS field
    WHERE field.source_relation_field_id = NEW.source_relation_field_id
      AND field.field_name IN ('jockey', 'trainer', 'owner')
)
BEGIN
    SELECT RAISE(ABORT, 'connection decision source field must be jockey, trainer or owner');
END;

CREATE TRIGGER trg_connection_decision_field_update
BEFORE UPDATE OF source_relation_field_id ON governance_connection_value_decision
WHEN NOT EXISTS (
    SELECT 1
    FROM source_relation_field AS field
    WHERE field.source_relation_field_id = NEW.source_relation_field_id
      AND field.field_name IN ('jockey', 'trainer', 'owner')
)
BEGIN
    SELECT RAISE(ABORT, 'connection decision source field must be jockey, trainer or owner');
END;

-- A Notebook 20 operational decision must point to the same permanent
-- verification subject: exact source record, exact physical source field and an
-- action compatible with the operational status. The first EXISTS restricts
-- this trigger to valid connection fields so the dedicated field-boundary
-- trigger remains the deterministic failure for any out-of-scope field.
CREATE TRIGGER trg_connection_decision_verification_compatible_insert
BEFORE INSERT ON governance_connection_value_decision
WHEN EXISTS (
    SELECT 1
    FROM source_relation_field AS field
    WHERE field.source_relation_field_id = NEW.source_relation_field_id
      AND field.field_name IN ('jockey', 'trainer', 'owner')
)
AND NOT EXISTS (
    SELECT 1
    FROM governance_manual_verification AS verification
    JOIN source_raceform_v1_record AS source
      ON source.source_record_id = NEW.source_record_id
    JOIN source_relation_field AS field
      ON field.source_relation_field_id = NEW.source_relation_field_id
    WHERE verification.manual_verification_id = NEW.manual_verification_id
      AND verification.source_record_id = NEW.source_record_id
      AND verification.source_relation_field_id = NEW.source_relation_field_id
      AND verification.source_field = field.field_name
      AND (
          (NEW.value_status = 'externally_supplemented'
           AND verification.verification_status = 'confirmed'
           AND verification.database_action = 'source_supplementation'
           AND verification.verified_value = NEW.governed_value)
          OR
          (NEW.value_status = 'source_blank_unresolved'
           AND verification.database_action = 'preserve_raw_unresolved'
           AND NEW.governed_value IS NULL)
      )
)
BEGIN
    SELECT RAISE(ABORT, 'connection decision verification is incompatible');
END;

-- A missing-runner supplementation must be backed by a confirmed permanent
-- source-supplementation verification for the same race/horse and must not have
-- acquired a physical source row since the governed decision was made.
CREATE TRIGGER trg_runner_supplementation_verification_insert
BEFORE INSERT ON governance_runner_record_supplementation
WHEN NOT EXISTS (
    SELECT 1
    FROM governance_manual_verification AS verification
    WHERE verification.manual_verification_id = NEW.manual_verification_id
      AND verification.source_race_occurrence_id = NEW.source_race_occurrence_id
      AND verification.source_horse = NEW.source_horse
      AND verification.verification_status = 'confirmed'
      AND verification.database_action = 'source_supplementation'
) OR EXISTS (
    SELECT 1
    FROM core_runner_participation AS runner
    JOIN source_raceform_v1_record AS source
      ON source.source_record_id = runner.source_record_id
    WHERE runner.source_race_occurrence_id = NEW.source_race_occurrence_id
      AND source.horse IS NEW.source_horse
)
BEGIN
    SELECT RAISE(ABORT, 'runner supplementation verification/absence check failed');
END;

COMMIT;
