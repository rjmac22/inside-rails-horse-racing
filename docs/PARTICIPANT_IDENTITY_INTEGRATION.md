# Participant Identity Integration Contract

## Scope

This document governs the database consequence of Notebook 22 for jockey, trainer and owner labels.

The immutable source remains the authority for raw values and lineage. Participant identity is represented separately because broad string normalisation is not safe.

## Raw fields to preserve

Every governed runner row must retain:

- source database and table;
- source `rowid`;
- supplied `race_id`;
- reconstructed provisional race key (`date + course + off`);
- raw `jockey` label;
- raw `trainer` label;
- raw `owner` label.

Raw labels must never be overwritten by a canonical or provisional identity label.

## Jockey consequence

Notebook 22 produced 216 strict title-removal candidate relationships from 7,917 populated raw labels.

Only one relationship is accepted as the same provisional jockey label identity:

- `Mlle Marie Velon`;
- `Mme Marie Velon`.

The decision was externally verified through the governed record `NB22-JOCKEY-0002`. Its two directly usable label mappings are persisted in:

- `data/processed/jockey_identity/jockey_provisional_identity_mapping.csv`.

Both raw labels map to `JOCKEY-PROVISIONAL-0001`. The mapping retains the verification identifier and a reference back to `JOCKEY-STRICT-0002` in the governed jockey review queue.

`Miss B ONeill` and `Mr B ONeill` are explicitly different because both occur within the same reconstructed race and the distinction was confirmed through the governed published-result record `NB22-JOCKEY-0001`. They must remain separate participant identities. The remaining 214 relationships remain unresolved.

No general jockey-title stripping or automatic alias merge is authorised.

## Trainer consequence

The accepted trainer rule is limited to exact post-title labels where:

- the earlier title is `Mlle`;
- the later title is `Mme`;
- active periods do not overlap;
- the `Mlle` label ends between 1 July and 31 December 2023;
- the `Mme` label begins between 1 January and 30 June 2024.

This produces:

- 26 provisional trainer identities;
- 52 mapped raw labels;
- 6,350 mapped runner rows;
- 27 unresolved candidate groups.

The mapping represents high-confidence source-label equivalence, not independently verified legal or licensing identity.

## Owner consequence

Owner labels may represent people, partnerships, syndicates, clubs, companies, studs, farms or compressed multi-party compositions.

Exact token-multiset matching is candidate generation only. A provisional ownership-composition identity is authorised only when differently ordered variants of the same exact token multiset occur within one reconstructed race.

This produces:

- 41 provisional ownership-composition identities;
- 95 mapped raw labels;
- 9,788 mapped runner rows;
- 895 unresolved candidate groups;
- 1,822 unresolved candidate labels;
- 24,406 unresolved candidate runner rows.

The result establishes equivalence of the complete named composition only. It does not establish legal identity, ownership shares or continuing membership.

## Proposed relational structures

### `participant_source_label`

One row per distinct source-presented participant label and role.

Required columns:

- `participant_source_label_id` surrogate key;
- `participant_role` constrained to `jockey`, `trainer` or `owner`;
- `raw_label`;
- `first_source_date`;
- `last_source_date`;
- `source_runner_rows`;
- unique constraint on (`participant_role`, `raw_label`).

### `participant_provisional_identity`

One row per governed provisional identity.

Required columns:

- `participant_provisional_identity_id`;
- `participant_role`;
- `identity_scope` such as `person_label_identity` or `ownership_composition`;
- `identity_status`;
- `method`;
- `confidence`;
- `review_status`;
- `created_by_notebook`.

### `participant_identity_label_map`

Many source labels may map to one provisional identity.

Required columns:

- `participant_provisional_identity_id`;
- `participant_source_label_id`;
- `relationship_status`;
- `method`;
- `confidence`;
- `evidence_reference`;
- `effective_start_date` nullable;
- `effective_end_date` nullable;
- unique constraint on (`participant_role`, `raw_label`) for active accepted mappings.

The jockey mapping file, trainer mapping file and owner-composition mapping file are the governed inputs for this structure. Review queues and unresolved files must not be treated as accepted label maps.

### `participant_identity_candidate`

Unresolved candidate relationships remain separate from accepted mappings.

Required columns:

- candidate identifier;
- role;
- candidate key or comparison label;
- participating raw labels;
- candidate method;
- evidence status;
- decision status;
- review notes.

Candidate records must never be joined as if they were accepted identities.

## Blank-field supplementation

Notebook 20 remains the governing source for blank connection fields.

Downstream views may expose a verified supplementation only by joining through `data/reference/manual_verifications.csv` and retaining:

- permanent `verification_id`;
- evidence locator;
- confidence;
- permitted database action;
- raw blank value and source row lineage.

The immutable raw field remains blank.

## Join and cardinality requirements

- A source row may join to at most one accepted provisional identity per role.
- A raw label may map to at most one active accepted provisional identity within the same role and governed method scope.
- Unresolved candidates must not create participant identifiers in analytical facts.
- Owner composition identities must not be decomposed into individual owners without a separate governed study.
- Cross-role merges are prohibited unless separately verified.

## Validation requirements

Database builds must fail when:

- a governed mapping file contains duplicate raw labels;
- an accepted mapping does not join to the immutable source;
- one source row duplicates after a mapping join;
- accepted and unresolved populations overlap;
- expected unresolved cases disappear without a governed decision;
- the jockey review queue does not close exactly over all 216 source candidate relationships;
- the jockey decision population is not exactly one accepted same-person relationship, one confirmed distinct-person relationship and 214 unresolved relationships;
- either decisive jockey record loses its verification identifier, evidence locator, access date, confidence or database action;
- the direct jockey mapping differs from the two labels governed by `NB22-JOCKEY-0002`;
- a new title or token-order population falls outside the established rules;
- a blank-field supplementation lacks permanent verification provenance.

Run:

```text
pytest -q tests/test_participant_identity.py
python scripts/validate_participant_identity.py
```

## Update procedure

For future source updates:

1. retain all historical raw labels;
2. regenerate candidate populations using the reusable helper functions;
3. compare new candidates with the governed mapping and unresolved files;
4. investigate only the new or changed residue;
5. preserve external evidence in the permanent manual-verification register or the governed role-specific decision table, whichever is the documented evidence authority for that decision;
6. update accepted mappings and unresolved candidates together;
7. rerun focused tests and the independent validator;
8. rebuild dependent participant dimensions and analytical views;
9. compare mapping, unresolved and unmatched counts with the previous release.

Expected counts must never be changed merely to make validation pass.
