# Inside Rails Study Database Reference

## Purpose

This is the canonical database reference for reader-facing Inside Rails studies.

Read this document before beginning every study, alongside:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Its purpose is to stop study notebooks from rediscovering or guessing database names, paths, release state, table grain, identifiers, source-admission rules or safe analytical interfaces.

When the database schema, release status, canonical paths or study-facing analytical structures change, update this document as part of that database work.

---

## 1. Database identities

### Immutable third-party Source Version 1

Original filename:

`raceform.db`

Canonical local path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Role:

- immutable third-party source evidence;
- never an Inside Rails database name;
- opened read-only;
- never renamed or modified because its original identity is part of lineage.

Source Version 1 admission rule:

`rowid <> 1`

Accepted population:

- 1,851,286 physical source records;
- 1,851,285 admitted runner records;
- 1 retained excluded physical row;
- 189,043 source race occurrences;
- 37 source columns.

Authorised Source Version 1 race identity:

`exact raw date + course + off`

Minimum source date:

`2015-01-01`

Maximum source date:

`2026-05-27`

---

## 2. Inside Rails database naming

Inside Rails-built databases use project-owned names and must not inherit the third-party source filename.

Approved naming convention:

- validated Version 1 candidate: `inside_rails_v1_candidate.sqlite3`;
- accepted/promoted Version 1 release: `inside_rails_v1.sqlite3`.

Future releases should follow the same Inside Rails-owned naming pattern.

### Current implementation

Preserved validated candidate:

`data/processed/database/candidates/inside_rails_v1_candidate.sqlite3`

Candidate SHA-256:

`7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2`

Canonical accepted Version 1 release:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Accepted-release SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

The candidate is retained unchanged as pre-release evidence and rollback material. Reader-facing studies should not use it as the normal analytical database.

---

## 3. Current release state

Inside Rails Version 1 was explicitly release-accepted and promoted on 8 August 2026.

Current state:

- minimum-core SQLite schema version 1: implemented;
- complete candidate: built and independently validated;
- repository-wide release implementation gate: 360 tests passed;
- manifest transition: `built -> validated -> release_accepted`;
- release accepted: **true**;
- active/promoted Inside Rails database: `data/processed/database/releases/inside_rails_v1.sqlite3`;
- release SHA-256: `2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`;
- release size: 1,730,048,000 bytes;
- validation-result rows: 7;
- `PRAGMA quick_check`: `ok`;
- `PRAGMA foreign_key_check`: zero rows;
- SQLite `application_id`: 1230130259;
- SQLite `user_version`: 1;
- preserved candidate hash unchanged during promotion: **true**.

Reader-facing studies should use this accepted release as the default analytical database and consume it read-only.

There is no silent fallback to the candidate or raw third-party source if the accepted release is missing.

---

## 4. Engine and database contract

Inside Rails Version 1 uses SQLite.

Minimum supported SQLite version:

`3.37.0`

The minimum core uses `STRICT` tables except for the raw mirrored source table, which deliberately preserves original SQLite storage classes.

Accepted database releases are immutable after final hashing and must be consumed read-only.

Normal accepted-release consumer connections must use:

```text
PRAGMA query_only = ON;
PRAGMA foreign_keys = ON;
PRAGMA trusted_schema = OFF;
```

The original source database remains physically separate from Inside Rails-built releases.

---

## 5. Minimum-core table inventory

The authorised first-release minimum core contains thirteen physical tables:

### Source metadata and raw evidence

- `source_provider`
- `source_product`
- `source_version`
- `source_relation`
- `source_relation_field`
- `source_raceform_v1_record`

### Governance

- `governance_method`
- `governance_release`
- `governance_release_evidence`

### Structural racing core

- `core_source_race_occurrence`
- `core_runner_participation`

### Build and validation evidence

- `import_manifest`
- `import_validation_result`

No analytical field-extension tables were authorised in the minimum-core release.

---

## 6. Important table grains

### `source_raceform_v1_record`

Grain:

> one physical row exactly as stored in Source Version 1.

Contains all 1,851,286 physical source rows, including the retained excluded row.

It preserves original raw values and source lineage. It is evidence, not a cleaned analytical table.

### `core_source_race_occurrence`

Grain:

> one admitted Source Version 1 race occurrence reconstructed from the authorised exact raw `date + course + off` grouping.

Expected population:

`189,043` race occurrences.

This is the structural race-level unit for Inside Rails Version 1.

### `core_runner_participation`

Grain:

> one admitted runner participation linked to one source record and one source race occurrence.

Expected population:

`1,851,285` runner participations.

For race-level research questions, do not casually use runner rows as independent race observations.

---

## 7. Identifier rules studies must respect

Do not use the supplied raw `race_id` as a unique Inside Rails race identifier.

The structural core uses deterministic project-owned codes.

Relevant namespaces include:

- source version: `sv:...`;
- source record: `rec:...`;
- source race occurrence: `race:...`;
- runner participation: `run:...`.

Internal integer primary keys are scoped to one built database release and are not stable external references.

Stable study outputs should prefer project-owned textual codes or another explicitly governed stable identifier where appropriate.

---

## 8. Raw, structural and analytical data are different layers

Studies must distinguish:

### Raw evidence

Exact third-party values and physical lineage.

### Structural core

Governed source version, race occurrence and runner participation identities.

### Governed field interpretations

Canonical or interpreted values established by the source-field investigation programme and its governed references/implementations.

### Study-specific derivations

Calculations created to answer one study question.

A study-specific derivation does not automatically belong in the database.

If a study discovers a missing transformation, defect or reusable analytical structure that materially affects correctness or repeatability, pause the study and handle it through database governance as required by `docs/STUDY_RESEARCH_PLAYBOOK.md`.

---

## 9. Field governance remains authoritative

The minimum structural core does not by itself make every raw field analytically safe.

Before using a field, consult the existing field-governance work and reusable implementation/reference outputs for that field.

Important standing examples include:

- supplied `race_id` is not accepted as a unique race key;
- result semantics require governed interpretation;
- starting-price arithmetic has a retained unresolved raw value `F`;
- course/jurisdiction context matters;
- runner counts and numbers have governed semantics;
- raw comment text is preserved without a general narrative parser.

Do not infer meaning from a column name merely because the structural database contains it.

---

## 10. Study-start database checklist

Before the first analytical cell of every study, confirm:

1. this document has been read;
2. `docs/STUDY_DATA_ACCESS.md` has been read;
3. the current database release state is known;
4. the exact accepted database path is taken from documentation rather than memory;
5. the study's unit of observation is declared;
6. every required field has sufficient governance for the proposed use;
7. source/candidate/accepted-release status is not being conflated;
8. relevant stable identifiers and join cardinalities are understood;
9. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work;
10. any database enhancement discovered during the study will be escalated rather than quietly implemented as notebook-only infrastructure when correctness or reuse requires database work.

---

## 11. Update rule

This document is a living study-facing database reference.

Update it whenever any of the following changes:

- canonical source path;
- candidate or accepted database filename/path;
- release status;
- database schema version;
- study-facing table/view inventory;
- table grain;
- stable identifier rules;
- analytical access conventions;
- field-governance consequence that materially changes how studies should query the database.

A database change is not fully integrated into the study workflow until this reference reflects it.
