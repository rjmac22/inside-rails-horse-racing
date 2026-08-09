-- Final pre-population enforcement corrections discovered during implementation
-- review of the study-facing governed-pedigree join.

BEGIN IMMEDIATE;

-- The durable Notebook 19 implementation indexes its specialist governance by
-- exact source horse label and therefore requires at most one specialist row per
-- label in the current release. Enforce that contract so joining the specialist
-- decision into runner views cannot duplicate source-backed runner rows.
CREATE UNIQUE INDEX ux_horse_pedigree_specialist_decision_source_horse
    ON governance_horse_pedigree_specialist_decision(source_horse_label);

COMMIT;
