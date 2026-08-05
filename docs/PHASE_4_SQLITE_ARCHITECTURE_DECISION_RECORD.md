# Phase 4 SQLite Architecture Decision Record

## Status

Accepted technical architecture decision record for the first governed Inside Rails database.

This document records the technical decisions made after acceptance of:

- `docs/PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`;
- `docs/PHASE_3_EVIDENCE_STATUS_MATRIX.md`;
- `docs/PHASE_3_MINIMUM_STABLE_CORE_IMPLEMENTATION_BRIEF.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

It authorises architectural design and later bounded implementation only for the already authorised minimum stable core.

It does not authorise any deferred field, identity, meeting, race-series, weather, sectional, market-feed, or analytical extension.

---

## 1. Decision-making rule

The user has delegated low-level technical architecture judgement where specialist database knowledge is required, subject to complete audit documentation.

The project will therefore distinguish:

### Technical implementation decisions

Examples include database engine, key representation, file lifecycle, hashing, table naming, view structure, and transactional activation.

These may be selected on engineering grounds when they remain inside an already accepted scope.

Each decision must record:

- the requirement being satisfied;
- the selected approach;
- credible alternatives;
- why the alternatives were not selected now;
- assumptions and limitations;
- validation requirements;
- concrete review triggers.

### Material scope and semantic decisions

Examples include admitting a new source, interpreting a field, creating a new governed identity, changing unresolved treatment, or adding an analytical extension.

These remain subject to evidence-led study and explicit user acceptance.

Technical delegation does not permit the implementation to expand the authorised database scope.

---

## 2. Current workload and constraints

The architecture is selected for the evidenced first-release workload:

- one primary operator and developer;
- one immutable Source Version 1 SQLite file;
- 1,851,286 physical source records;
- 1,851,285 admitted runner-bearing records;
- 189,043 Source Version 1 race occurrences;
- batch construction rather than continuous transactional updates;
- complete candidate-database builds outside the active release;
- fail-closed validation before activation;
- predominantly read-only analytical use after activation;
- no demonstrated need for simultaneous writers;
- no current public application writing directly to the governed database;
- no current requirement for a database server, remote authentication, replication, or high availability.

The architecture must favour reproducibility, auditability, exact source preservation, simple rollback, and low operational complexity.

---

## ADR-01 — Database engine

### Decision

Use SQLite for the first authoritative governed database.

### Rationale

SQLite satisfies the current requirements with the least unnecessary machinery:

- embedded and serverless;
- transactional;
- supports primary keys, unique constraints, checks, foreign keys, indexes, and views;
- one complete database file can be built and validated independently;
- simple local Python integration;
- simple backup, retention, and rollback;
- sufficient scale for the current source population;
- the single-writer constraint matches the intended controlled batch-build process.

### Required safeguards

The implementation must:

- use `STRICT` tables for metadata, structural core, governance, and import-control tables where compatible with the required data types;
- enable `PRAGMA foreign_keys = ON` on every governed connection;
- verify that foreign-key enforcement is active rather than assuming it;
- use explicit `NOT NULL`, `UNIQUE`, and `CHECK` constraints;
- run SQLite integrity and foreign-key checks after persistence;
- avoid relying on permissive SQLite type coercion;
- prohibit direct modification of an active accepted release.

### Alternatives considered

#### PostgreSQL

Not selected now because its principal advantages—multiple concurrent writers, remote services, database users and permissions, replication, and server operations—solve requirements the project does not currently have.

PostgreSQL remains the preferred server-database candidate if those requirements appear.

#### DuckDB

Not selected as the authoritative core because its clearest advantage is analytical scanning and aggregation rather than relational source-governance lifecycle and controlled evidence storage.

DuckDB may later be used as an analytical companion or to query exported Parquet datasets.

#### MySQL or MariaDB

Not selected because they introduce server administration without a demonstrated project-specific advantage over PostgreSQL.

#### Parquet

Not selected as the canonical database because it is an analytical storage format and does not itself enforce relational keys, foreign keys, transactions, or multi-table activation.

#### CSV

Not selected because it cannot safely enforce types, null states, uniqueness, relationships, or transactional releases.

### Review triggers

Reconsider SQLite when any of the following becomes real rather than hypothetical:

- multiple processes need concurrent writes;
- a public or internal application must write continuously;
- remote database access and role-based permissions are required;
- the database must remain online while frequent incremental updates occur;
- replication, high availability, or point-in-time recovery becomes necessary;
- measured workloads show SQLite cannot meet accepted performance requirements after appropriate indexing and query design.

---

## ADR-02 — Database-file boundary

### Decision

Use one complete governed SQLite database file per accepted database release.

Keep the original third-party `raceform.db` source file separate, immutable, and read-only.

### Rationale

One governed file provides:

- enforceable foreign keys across the complete model;
- one transaction boundary;
- one candidate artefact to validate;
- one immutable release artefact to retain;
- simple release hashing;
- simple rollback;
- no possibility of combining mismatched source, core, governance, or import-control database files.

### Alternative considered: attached SQLite databases

Rejected for the first release because ordinary foreign keys cannot enforce relationships across attached database files, and separate files create avoidable release-matching, backup, deployment, and reconciliation risks.

### Review triggers

Reconsider only if a measured operational need requires independent distribution, access control, or lifecycle management that cannot be achieved safely through tables and views in one file.

---

## ADR-03 — Logical layers

### Decision

Represent logical layers through explicit table-name prefixes inside the single SQLite file.

Initial prefixes are:

- `source_*` — source provider, product, version, relation, and immutable raw records;
- `core_*` — Source Version 1 race occurrences and runner participations;
- `governance_*` — structural releases, methods, and provenance references;
- `import_*` — manifests, validation results, build status, and activation evidence;
- `view_*` — documented read interfaces;
- `analysis_*` — reserved for separately authorised derived outputs only.

### Rationale

SQLite does not provide PostgreSQL-style schemas. Prefixes preserve understandable boundaries without weakening foreign keys or splitting the release across files.

### Naming rule

Names must state grain precisely.

Prefer:

- `core_source_race_occurrence`;
- `core_runner_participation`;
- `import_validation_result`.

Avoid ambiguous names such as `races`, `horses`, `data`, or `results` where they could imply broader real-world identity or semantics than the evidence supports.

---

## ADR-04 — Internal and external identifiers

### Decision

Use both:

1. compact integer surrogate primary keys for relationships inside one built database release; and
2. deterministic stored textual identifiers for audit, exports, logs, validation reports, and cross-release references.

### Internal integer keys

Use SQLite `INTEGER PRIMARY KEY` without `AUTOINCREMENT`.

Integer keys:

- remain meaningless;
- support compact indexes and efficient joins;
- are scoped to one built database release;
- must not be treated as stable external identifiers.

### Stable textual identifiers

Store a unique deterministic textual code on each core entity.

The code must:

- identify its entity namespace;
- derive from governed source provenance or canonical release construction;
- be reproducible from accepted inputs;
- remain separate from descriptive source values;
- be independently recomputed by validation.

Examples of intended namespaces include:

- source version;
- source relation;
- source record;
- source race occurrence;
- runner participation;
- governance release;
- import manifest;
- database release.

Exact syntax will be fixed in the physical schema specification.

### Prohibited natural keys

The following must not become permanent primary keys:

- supplied `race_id`;
- `date + course + off` outside its accepted source-version-scoped grouping role;
- raw horse label;
- supplied runner number;
- SQLite `rowid` without exact source-version and relation context;
- descriptive names.

---

## ADR-05 — Deterministic rebuilds

### Decision

A complete build must regenerate internal integer identifiers from documented canonical ordering.

Persistent allocation sequences are not required.

### Rationale

The database must be reproducible from governed inputs without depending on a previous active database or historical sequence state.

The same source, code, reference data, and canonical ordering should generate the same identifiers and database content.

A later source version may change internal integer assignments. This is acceptable because external dependencies must use stable textual identifiers.

### Validation

The implementation must prove deterministic regeneration through focused tests using fixed fixtures and at least one repeated clean build comparison.

---

## ADR-06 — Raw Source Version 1 representation

### Decision

Use a source-specific wide raw mirror with one ordinary column for each of the exact 37 Source Version 1 fields.

Do not use JSON or an entity–attribute–value model for the fixed Source Version 1 relation.

### Required records

Copy all 1,851,286 physical source records, including retained excluded `rowid = 1`.

Record an explicit structural status distinguishing:

- 1,851,285 admitted runner-bearing records; and
- one retained excluded physical record.

### Rationale

The source schema is known, fixed, and already investigated. Ordinary columns provide direct inspection, clear reconciliation, efficient filtering, and exact source-field boundaries.

JSON would obscure known structure and complicate validation. An entity–attribute–value model would expand the source into approximately 68.5 million value rows without a corresponding analytical or governance benefit.

### Future sources

A future provider or structurally different source version receives its own evidence-led raw representation after inspection. It must not be forced into the Source Version 1 raw table.

---

## ADR-07 — Raw value and storage-class preservation

### Decision

Preserve every raw value and its SQLite storage class through exact copy and source-wide round-trip validation.

Do not add 37 duplicated storage-class columns.

### Required validation

For every physical source row and all 37 fields, validate:

- copied value equality;
- `typeof()` equality;
- column order;
- null versus empty-text distinction;
- persisted readback equality;
- row-fingerprint equality.

### Raw-table typing

The raw table must use a tested declaration strategy that does not coerce valid source storage classes.

The final declaration approach must be proven through a representative prototype before the complete build.

Metadata, core, governance, and import tables should remain `STRICT` where possible.

---

## ADR-08 — Row fingerprints

### Decision

Store a SHA-256 fingerprint for each physical source record.

The digest is calculated over a canonical binary encoding of all 37 values in fixed source-column order.

Each encoded value must include:

- column ordinal;
- SQLite storage-class marker;
- explicit null treatment;
- unambiguous byte length;
- canonical value bytes.

### Canonical value representation

- `NULL`: explicit null marker and no value bytes;
- integer: signed 64-bit representation;
- real: IEEE-754 64-bit representation;
- text: exact UTF-8 bytes;
- blob: exact bytes.

### Storage

Prefer the 32-byte digest as a `BLOB` internally. Audit views and reports may expose lowercase hexadecimal.

### Limits

The fingerprint supports integrity and reconciliation. It does not replace value-by-value and `typeof()` comparison, and it does not establish real-world identity.

The exact source file must separately retain a complete-file SHA-256 hash.

---

## ADR-09 — Core-table denormalisation boundary

### Decision

Repeat only the raw attributes required to define and independently validate the structural grain.

### Source race occurrence

The race-occurrence table may store:

- source version reference;
- exact raw `date`;
- exact raw `course`;
- exact raw `off`;
- stable race-occurrence code;
- internal key;
- admitted runner count;
- structural governance release.

These three raw grouping fields are stored because they define the accepted Source Version 1 race grouping.

Do not automatically promote race name, class, distance, going, supplied `race_id`, or other apparently race-level values into the structural race table.

### Runner participation

The runner-participation table should initially store only:

- stable runner-participation code;
- internal key;
- source race occurrence reference;
- source record reference;
- structural governance release.

Horse, jockey, trainer, owner, result, price, weight, rating, number, and other raw fields remain available through the one-to-one source-record relationship until separately authorised.

### Rationale

This preserves one authoritative raw value, prevents drift, and avoids embedding unauthorised semantic interpretations into the structural core.

---

## ADR-10 — Stored textual identifiers

### Decision

Physically store stable textual identifiers rather than generating them only through views.

Store their defining component fields separately and validate that the code can be recomputed exactly.

### Rationale

Stored identifiers survive exports, logs, validation reports, and historical release inspection. A view-only identifier could change silently if formatting logic changed.

Internal foreign keys should continue to use integer keys.

---

## ADR-11 — Read interface

### Decision

Use documented views as the normal query interface for notebooks, reports, and later applications.

Physical tables remain available for controlled ingestion, validation, and specialist audit work.

### First-release views

The first release should contain only evidence and structural-core views, such as:

- source-record lineage;
- Source Version 1 raw records;
- source race occurrences;
- runner participations joined to source lineage;
- active import release;
- import validation evidence.

### Prohibited first-release views

Do not add horse histories, trainer statistics, betting measures, result aggregates, feature datasets, or other analytical convenience views before their governing studies and extension briefs are accepted.

### View transparency

Views must not silently:

- replace raw values with corrections;
- suppress unresolved cases;
- merge provisional identities;
- present source occurrences as provider-independent real-world identities;
- conceal the retained excluded source record;
- apply hidden analytical population filters.

---

## ADR-12 — Database-release lifecycle

### Decision

Retain every accepted governed database as an immutable versioned release file.

Use a small atomic active-release manifest rather than a mutable duplicate database file or platform-dependent symbolic link.

### Intended layout

The exact paths may be refined during implementation, but the intended lifecycle is:

```text
data/processed/database/candidates/
    inside_rails_<database_release_code>.sqlite3.tmp

data/processed/database/releases/
    inside_rails_<database_release_code>.sqlite3

data/processed/database/active_database.json
```

Large generated database artefacts should remain outside ordinary Git history unless a later explicit artefact-distribution decision states otherwise.

### Candidate lifecycle

1. Build a complete candidate outside the releases directory.
2. Run unit tests, applicable source-wide validators, reconciliation, persisted readback, SQLite integrity checks, and post-load validation.
3. Calculate the complete candidate-file SHA-256 hash.
4. Move the validated candidate into the immutable releases directory under its release code.
5. Verify the moved file and hash.
6. Atomically replace `active_database.json` with a manifest naming the new immutable release.
7. Leave the prior release file unchanged and available for rollback.

### Active manifest contents

At minimum, record:

- database release code;
- relative release-file path;
- full database-file SHA-256;
- source version code and hash;
- import manifest code;
- code commit;
- reference-data release or commit;
- activation timestamp;
- confirmation that post-load validation passed.

### Why not a fixed mutable `inside_rails.db` copy?

A duplicated active file could drift from the retained versioned release, wastes storage, and requires another large-file replacement operation.

### Why not a symbolic link?

A symbolic link would be workable on the current Ubuntu environment but is less portable across Windows, packaging, archive, and connector workflows. A small JSON manifest is explicit, hashable, portable, and easy to replace atomically.

### Consumer rule

Repository code must use one resolver function to locate and verify the active database through the manifest. Consumers must not hard-code a release filename.

---

## ADR-13 — Atomicity and last-known-good protection

### Decision

The active release changes only by atomically replacing the small active manifest after the complete immutable database file has passed every gate.

A failed build or validation must leave both:

- the previous active manifest; and
- the previous accepted release file

unchanged and usable.

The candidate database must never overwrite an accepted release in place.

---

## 3. First implementation validation obligations

The physical implementation must include, at minimum:

- schema tests for every authorised table and view;
- connection tests proving foreign keys are enabled;
- uniqueness and relationship-cardinality tests;
- complete physical-source row reconciliation;
- exact `1,851,286 / 1,851,285 / 189,043 / 1,851,285` structural totals;
- all 37-field value and `typeof()` reconciliation;
- retained-excluded-row validation;
- deterministic identifier tests;
- deterministic repeated-build evidence;
- source-file and row-fingerprint checks;
- SQLite `quick_check` or `integrity_check` as accepted in the implementation plan;
- `foreign_key_check`;
- persisted-file readback;
- complete active-manifest validation;
- rollback demonstration or equivalent automated test;
- confirmation that the original source file was opened read-only and remained unchanged.

No expected total may be changed merely to make a build pass. A changed source or population requires investigation and a new governed decision.

---

## 4. Explicit non-goals

This decision record does not authorise:

- governed result, distance, weight, price, rating, prize-money, equipment, or comment tables;
- horse, jockey, trainer, or ownership identity tables;
- meeting identity;
- recurring race series;
- racecourse site or configuration history;
- weather;
- sectional timing or tracking;
- general betting-market observations;
- analytical aggregates or feature stores;
- web-application infrastructure;
- PostgreSQL deployment;
- DuckDB analytical replicas;
- cloud storage or orchestration.

Each remains subject to its own evidence and implementation gate.

---

## 5. Audit and change control

Every later architecture change must record:

- the observed requirement or defect prompting review;
- measurements or evidence;
- affected decision number;
- alternatives considered;
- compatibility and migration consequences;
- validation changes;
- user acceptance where the change affects scope, semantics, unresolved treatment, or analytical meaning.

A technical preference alone is not enough to overturn an accepted decision.

---

## 6. Decision summary

The accepted first-release architecture is:

1. SQLite as the authoritative governed database engine.
2. One complete immutable SQLite file per accepted release.
3. One portable active-release JSON manifest pointing to the accepted file.
4. One-file logical layers expressed through precise table prefixes.
5. Integer surrogate keys inside each release.
6. Deterministic stored textual identifiers for audit and cross-release use.
7. Deterministic complete rebuilds without `AUTOINCREMENT` sequence dependence.
8. A fixed 37-column Source Version 1 raw mirror containing all 1,851,286 physical records.
9. Exact raw-value and SQLite storage-class preservation verified source-wide.
10. SHA-256 file and row fingerprints using canonical typed binary encoding.
11. Minimal structural core tables with no premature field interpretation.
12. Evidence and structural views only in the first release.
13. Complete candidate validation before immutable release retention and atomic activation.
14. PostgreSQL and DuckDB retained as future options triggered by demonstrated operational or analytical need.
15. Every decision and future revision retained with explicit evidence, rationale, and review triggers.

The governing architecture principle is:

> Use the simplest system that fully enforces the authorised evidence model, and preserve enough audit evidence to explain and reproduce every technical decision.