-- Database v2 participant-candidate confidence correction.
--
-- Notebook 22 intentionally leaves confidence blank for unresolved jockey
-- candidates whose external review was deferred until a concrete analytical
-- need exists. That blank is part of the durable governance artifact and must
-- not be converted into invented confidence. Accepted/confirmed decisions must
-- still carry a non-blank confidence value.

BEGIN IMMEDIATE;

-- The table is still empty when schema resources are applied. Foreign-key
-- enforcement is deliberately off for the v1-to-v2 migration, so rebuilding
-- this table here preserves the dependent table definitions while correcting
-- only the confidence-domain constraint.
DROP TABLE identity_participant_candidate;

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
    CHECK(
        length(trim(confidence)) > 0
        OR (decision_status = 'unresolved' AND confidence = '')
    ),
    CHECK(length(trim(review_status)) > 0),
    CHECK(length(trim(database_action)) > 0),
    FOREIGN KEY(governance_release_id) REFERENCES governance_release(governance_release_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_identity_participant_candidate_role_status
    ON identity_participant_candidate(participant_role, decision_status);

COMMIT;
