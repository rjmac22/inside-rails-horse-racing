# Database Import Validation Gate

## Purpose

This document defines the project-wide rule for admitting source-derived data into any staging, core or analytical database.

The governing principle is:

> No validated output, no database write. No partial success. The last known-good database remains intact.

This rule applies to every field, reference, supplementation, correction, identity mapping and derived output—not only race-time reconstruction.

## Scope

The gate applies whenever the project:

- ingests a new source snapshot;
- rebuilds governed source-derived outputs;
- adds or changes reference data;
- applies a supplementation or correction;
- changes a parser, identity rule or interpretation;
- migrates or rebuilds staging, core or analytical tables.

The immutable source remains read-only. Raw values and physical lineage must always be preserved.

## Required admission sequence

A database load must proceed through these stages:

1. **Build outside the live database.** Create the candidate output in memory, a generated file, a temporary table or a temporary database.
2. **Validate the source population.** Confirm the governed source-row predicate, expected grain, required identities and complete source partition.
3. **Validate the candidate output.** Enforce schema, types, required columns, key uniqueness, cardinality, domains, null and unresolved rules, provenance, lineage and notebook-specific invariants.
4. **Reconcile source to output.** Prove that every admitted, rejected, unresolved and quarantined source item is accounted for exactly once where the governing rule requires a complete partition.
5. **Persist and read back.** Write the candidate atomically, reload it using production types and repeat integrity checks against the persisted representation.
6. **Load transactionally.** Populate temporary or replacement database structures inside a transaction without altering the last known-good production structures.
7. **Validate after load.** Recheck row counts, keys, foreign keys, constraints, source lineage, governed totals and representative round trips from the loaded database.
8. **Commit or swap only after every check passes.** Any failure must roll back the complete load.

## Mandatory controls

Every applicable load must enforce:

- immutable raw-value preservation;
- source database, table and row lineage;
- exact target grain;
- primary, natural and surrogate key uniqueness as designed;
- foreign-key and relationship cardinality rules;
- governed type and unit interpretation;
- permitted null, blank and unresolved states;
- reference-data key uniqueness and effective-period rules;
- exact supplementation and correction lineage;
- non-overlap between accepted, rejected, unresolved and quarantined populations;
- provenance, confidence, method and permitted-action requirements;
- independent source-wide validation in addition to unit tests;
- persisted-output readback and reconciliation;
- atomic or transactional replacement of the prior database state.

## Fail-closed behaviour

The workflow must stop for investigation when it encounters:

- an unfamiliar raw value or format;
- a new or unmatched source identity;
- a missing governed reference;
- a duplicate key or changed cardinality;
- an invalid timezone, currency, unit or status;
- a changed source population or governed baseline that has not been explained;
- a source-to-output reconciliation difference;
- an unsupported automatic correction;
- missing provenance for a decision that depends on external evidence;
- a failed persisted-output or post-load readback check.

Expected counts may not be changed merely to make a new snapshot pass. The population change must first be explained and the governing decision updated deliberately.

## Unknown and unresolved data

Unknown cases must be handled explicitly by one of the governed outcomes:

- preserved unresolved;
- quarantined from the admitted analytical layer;
- rejected with a recorded reason;
- researched and added to a governed reference;
- accepted only after a bounded rule and validation are implemented.

Unknown values must never be silently guessed, discarded, coerced into a nearby category or loaded through a partial-success path.

## Database safety

The import process must not modify the last known-good database until the complete candidate database has passed validation.

Preferred implementation patterns are:

- build a complete temporary database and atomically replace the prior file;
- load replacement tables in a transaction and swap them only after validation;
- use versioned schemas or tables and advance the active version only after validation.

A failed run must leave the prior database usable and unchanged. Recovery must not depend on manually reversing a partially completed load.

## Validation ownership

Notebook-specific modules and validators define the field-level rules. The future database ingestion layer must orchestrate those validators and add cross-table integrity checks; it must not weaken or bypass them.

The complete repository test suite and all applicable independent validators form the minimum project-level gate before a new ingestion implementation or governed source snapshot is accepted.

## Evidence record

Each accepted load must record:

- source snapshot identity and date;
- code and reference-data commit;
- build command;
- test and validator results;
- source and target row counts;
- unresolved and quarantined counts;
- database version or output identifier;
- confirmation that post-load validation passed;
- confirmation that the prior database remained available until commit or swap.
