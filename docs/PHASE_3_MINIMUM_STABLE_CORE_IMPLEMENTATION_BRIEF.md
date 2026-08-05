# Phase 3 Minimum Stable Core Implementation Brief

## Status

**Accepted bounded implementation authorisation for the first physical database core.**

Accepted on 5 August 2026.

This brief is governed by:

- `docs/PHASE_3_EVIDENCE_FIRST_DESIGN_AND_IMPLEMENTATION_GATE.md`;
- `docs/PHASE_3_EVIDENCE_STATUS_MATRIX.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PHASE_3_ENTITY_AND_KEY_DESIGN_INVENTORY.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

This is the first Phase 3 document that explicitly authorises bounded physical database work.

The authorisation applies only to the stable structural core defined below. It does not authorise any governed field extension, provisional real-world identity layer, analytical feature, or future enrichment.

The central decision is:

> Build the smallest physical core that preserves the exact source, reconstructs Source Version 1 race occurrences and runner participations, records governance and import evidence, and provides stable attachment points for later evidence-led extensions.

---

## 1. Purpose

The first database implementation needs a reliable structural foundation before it needs a comprehensive racing model.

The foundation must answer five questions exactly:

1. Which provider, product, exact source version and relation supplied this record?
2. What did the source physically contain, without cleaning or replacement?
3. Which Source Version 1 race occurrence was reconstructed from each admitted runner-bearing record?
4. Which runner participation was created from that admitted source record?
5. Which code, governance release, tests, validators and transactional load admitted the resulting database?

The first implementation is not intended to answer every domain question already investigated in Notebooks 04–22.

Those outputs remain available as validated governed evidence and may be admitted later through separate bounded extension briefs.

---

## 2. Authorised source boundary

The first implementation is restricted to the exact governed `raceform.db` Source Version 1 already investigated and validated by the project.

Established baseline:

- one exact SQLite source file;
- one governed `data` relation;
- 37 source columns;
- 1,851,286 physical rows;
- 1,851,285 admitted runner-bearing rows under `rowid <> 1`;
- one retained non-governed physical row at `rowid = 1`;
- 189,043 Source Version 1 race occurrences;
- source date range from 2015-01-01 to 2026-05-27;
- source `PRAGMA quick_check` result of `ok`.

A later delivery, replacement file, API feed or second provider is outside this authorisation even when it appears to contain the same racing records.

It must enter through a new source-version study and admission decision.

---

## 3. Authorised concepts

The physical architecture may implement only the concepts in this section as the first stable core.

The final physical design may combine closely related metadata where doing so preserves every required constraint. This brief does not require one SQL table per conceptual item.

### 3.1 Source provider

The originating or supplying organisation recorded for the admitted source product.

Minimum required evidence:

- project-assigned technical identifier;
- governed provider label;
- acquisition or provenance note sufficient for Source Version 1;
- explicit uncertainty where publisher, compiler and original racing authority are not known to be the same organisation.

No generic provider-role taxonomy is authorised.

### 3.2 Source product

The continuing product or dataset family from which Source Version 1 was obtained.

Minimum required evidence:

- project-assigned technical identifier;
- source-provider relationship;
- governed product label or description;
- acquisition and usage notes already supported by project evidence.

Product renaming and provider-transfer history are deferred until encountered.

### 3.3 Exact source version

One immutable source delivery.

Minimum required evidence:

- independent project technical identifier;
- source-product relationship;
- original filename or acquisition description;
- cryptographic full-file hash;
- file size;
- retrieval or receipt date where known;
- SQLite structural signature;
- physical row count;
- admitted row count and governing predicate;
- source date range;
- source integrity result;
- notes identifying the retained `rowid = 1` exclusion;
- exact source-version status.

The filename is not the identity.

The cryptographic hash is evidence of exact content, not a substitute for the project identifier.

### 3.4 Source relation

The actual `data` relation in Source Version 1.

Minimum required evidence:

- project-assigned technical identifier;
- exact source-version relationship;
- raw relation name;
- ordered 37-field schema signature;
- physical and admitted record counts;
- governed admission predicate.

No generic abstraction for webpages, APIs, nested responses or non-tabular sources is authorised.

### 3.5 Immutable physical source record

One physical row exactly as supplied in the Source Version 1 `data` relation.

The first implementation must preserve all 1,851,286 physical rows, including `rowid = 1`.

Minimum required evidence for each physical record:

- independent project technical identifier;
- exact source-version relationship;
- source-relation relationship;
- original SQLite `rowid`;
- all 37 raw values without correction, replacement or normalisation;
- null, blank and storage distinctions needed for exact round-trip verification;
- admission status;
- exclusion reason where not admitted to the governed runner population.

The Source Version 1 source-local locator is:

`source version + source relation + SQLite rowid`

`rowid` alone is never a project-wide or cross-version identity.

The single physical record at `rowid = 1` must remain recoverable and must be recorded as excluded from the governed runner-bearing population. It must not disappear through the use of `rowid <> 1`.

### 3.6 Source race occurrence

One race as represented in Source Version 1.

The accepted Source Version 1 grouping evidence is:

`raw date + raw course + raw off`

Minimum required evidence:

- independent project technical identifier;
- exact source-version relationship;
- exact raw grouping values;
- structural-governance release or method reference;
- runner count derived from admitted records;
- direct reconciliation to supporting source records.

Required boundary:

- the grouping is unique and accepted for Source Version 1;
- it is not a provider-independent real-world race identity;
- governed local or UTC race time is not part of the identity;
- supplied `race_id` is retained as raw evidence and is not promoted to a key;
- race name, class, distance and other descriptive fields are not identity components.

### 3.7 Runner participation

One governed structural representation of one horse's recorded participation in one Source Version 1 race occurrence.

Minimum required evidence:

- independent project technical identifier;
- exactly one admitted supporting physical source record;
- exactly one Source Version 1 race occurrence;
- structural-governance release or method reference;
- direct access to every raw source value through the supporting source record.

Required boundary:

- every admitted physical source record produces exactly one runner participation;
- every runner participation is supported by exactly one admitted physical source record;
- raw horse text is a source label, not permanent horse identity;
- supplied `num` is retained as raw evidence and is not a runner key;
- `source race occurrence + raw horse label` remains a Source Version 1 validation rule, not the permanent technical identifier.

### 3.8 Governance release and structural-method provenance

The first core requires enough provenance to reconstruct why source records were admitted and how race occurrences and runner participations were derived.

Minimum required evidence:

- governance-release identifier;
- release status;
- creation or acceptance date;
- repository commit;
- method or builder identifier and version;
- source-version relationship;
- applicable governed population predicate;
- references to the accepted evidence and validation outputs;
- supersession status where a later accepted release replaces the structural derivation.

No universal field-level claim, correction, dispute or event-sourcing framework is authorised.

The implementation should use the smallest representation that preserves structural reproducibility.

### 3.9 Import manifest and validation evidence

Every candidate build and accepted database load must have a durable manifest.

Minimum required evidence:

- import or build identifier;
- exact source-version identifier and hash;
- code commit;
- governance-release identifier;
- reference-data versions actually used;
- build command or reproducible entry point;
- candidate database or output identifier;
- build start and completion timestamps;
- source physical, admitted, excluded, race and runner counts;
- test and validator names and outcomes;
- persisted-readback result;
- post-load integrity result;
- transaction or atomic-swap result;
- accepted, failed or rolled-back status;
- prior last-known-good database identifier;
- confirmation that the prior database remained available until acceptance.

A failed build manifest may be retained for diagnosis, but a failed candidate must never become the active database.

---

## 4. Explicitly unauthorised concepts

The first physical implementation must not introduce structures whose only justification is possible future usefulness.

The following are excluded from this authorisation.

### 4.1 Governed source-field extensions

Do not yet load separate governed representations for:

- course jurisdiction or surface;
- course location or timezone;
- resolved race time;
- result positions or non-finish outcomes;
- beaten distance;
- governed race distance;
- carried weight;
- starting-price arithmetic;
- betting-market context;
- prize-money amounts;
- race classification or eligibility;
- ratings;
- runner characteristics or equipment;
- connection-field supplementations;
- comment classifications.

Their raw source values remain available through the immutable physical source record.

Their existing validated outputs remain separate governed artifacts until an accepted analysis or operational need justifies an extension brief.

### 4.2 Provisional identity extensions

Do not yet load:

- provisional horse occurrences;
- runner-to-horse-occurrence assignments;
- jockey provisional identities;
- trainer provisional transitions;
- ownership compositions;
- official or provider-independent participant identities.

The stable runner identifier created by this core will provide the later attachment point.

### 4.3 Higher racing abstractions

Do not implement:

- meeting occurrences;
- meeting sessions;
- provider-independent real-world race identity;
- recurring race series or editions;
- institutional racecourse venue identity;
- historical physical racecourse sites;
- course-configuration eras;
- generic official-result amendment history.

### 4.4 Unavailable or unstudied enrichments

Do not implement empty or speculative structures for:

- weather;
- irrigation or drainage;
- sectional timing;
- GPS or runner tracking;
- specialist course-layout data;
- exchange order books;
- official identity registries;
- future source providers or APIs.

### 4.5 Generic infrastructure without an evidenced need

Do not create:

- a row-per-field source-claim system for all 37 values;
- a generic entity-attribute-value model;
- universal effective-dated regime machinery;
- a generic graph of every possible racing relationship;
- a global `unknown` entity used to eliminate nulls;
- speculative correction, amendment or supersession tables with no admitted records;
- analytical aggregates or model features presented as core facts.

---

## 5. Identifier and uniqueness requirements

The physical design may select integer, UUID, content-derived namespace or another suitable technical identifier strategy only after the database technology is selected.

Whatever strategy is selected must satisfy all of the following.

### 5.1 General rules

- Technical identifiers must not encode mutable descriptive meaning.
- Raw names, dates, times, supplied identifiers and runner numbers must not become permanent project-wide identities.
- Rebuilding the same exact source version under the same accepted structural release must not create duplicate logical records.
- Identifiers and relationships must be reproducible or durably mapped so downstream governed extensions can attach safely.
- Identifier scope must be documented explicitly.

### 5.2 Required uniqueness constraints

The implementation must enforce or independently validate:

- source version: project identifier unique;
- complete-file hash unique within the admitted exact-source-version register unless a deliberate duplicate-content relationship is recorded;
- source relation: unique within source version by exact relation identity;
- physical source record: unique by source version + relation + SQLite `rowid`;
- Source Version 1 race occurrence: unique by source version + raw date + raw course + raw off;
- runner participation: exactly one per admitted physical source record;
- Source Version 1 validation candidate: source race occurrence + raw horse label unique across admitted runner participations;
- import manifest: unique build or import identifier;
- one active accepted database version at a time.

The candidate validation combinations are not promoted to provider-independent natural keys.

---

## 6. Required cardinality and reconciliation rules

The first build must prove all applicable relationships source-wide.

### 6.1 Physical source population

- 1,851,286 physical source records are preserved.
- 1,851,285 are admitted to the runner-bearing governed population.
- exactly one physical source record, `rowid = 1`, is retained as excluded with an explicit reason.
- no physical source record is silently dropped.

### 6.2 Race occurrences

- exactly 189,043 Source Version 1 race occurrences are created.
- every admitted physical source record belongs to exactly one race occurrence.
- every race occurrence has at least one runner participation.
- no excluded physical source record creates a runner or race membership.
- grouping values reconcile exactly to the immutable raw source values.

### 6.3 Runner participations

- exactly 1,851,285 runner participations are created.
- every runner participation references exactly one admitted physical source record.
- every admitted physical source record supports exactly one runner participation.
- every runner participation references exactly one Source Version 1 race occurrence.
- there are no orphan source records, runner participations or race occurrences.

### 6.4 Source-field preservation

- the 37 raw fields match the governed source schema names, order and declared types;
- exact null and blank counts reconcile to Source Version 1;
- representative and source-wide round trips demonstrate that raw values were not normalised, trimmed, corrected or replaced;
- supplied `race_id`, `num`, horse, course, date and off values remain exactly recoverable.

---

## 7. Unresolved, excluded and changed evidence

The stable core should contain almost no semantic resolution. Its primary responsibility is faithful preservation and structural linkage.

Required treatment:

- `rowid = 1` is retained and explicitly excluded, not deleted;
- unfamiliar future rows, fields, schemas or cardinalities fail closed;
- a changed source file is a new source-version candidate, not a silent replacement;
- a changed 37-field schema fails the Source Version 1 importer;
- changed baseline counts require investigation and a new accepted decision;
- duplicate candidate race or runner groupings fail closed;
- missing raw values remain raw nulls or blanks and are not converted to `unknown`, zero or empty text;
- no raw correction is applied inside the stable core.

Quarantine may be implemented only as part of the import workflow for a failed or changed candidate. It must not become a partial-success path into the active database.

---

## 8. Required import behaviour

The implementation must comply with the complete sequence in `DATABASE_IMPORT_VALIDATION_GATE.md`.

For this core, the required operational behaviour is:

1. fingerprint and validate the immutable source file;
2. build the complete candidate database outside the active database;
3. load all physical records without modifying raw values;
4. classify admitted and excluded source records;
5. create race occurrences and runner participations from the admitted population;
6. run focused unit tests and structural validation;
7. reconcile every physical, admitted, excluded, race and runner record;
8. persist and reload the candidate database;
9. run database constraints and independent post-load validators;
10. record the complete import manifest;
11. atomically accept or swap the candidate only after every check passes;
12. leave the previous active database unchanged after any failure.

Incremental partial admission of Source Version 1 is not authorised for the first implementation.

The first build should be a complete deterministic rebuild from the immutable source.

---

## 9. Required validation layers

### 9.1 Focused unit tests

At minimum, tests must cover:

- source fingerprint handling;
- source-version duplicate protection;
- exact 37-field schema validation;
- admission predicate handling;
- preservation of `rowid = 1` as excluded evidence;
- race grouping;
- runner creation;
- duplicate and orphan rejection;
- raw-value round trips;
- manifest state transitions;
- failed-build rollback or non-activation;
- idempotent rebuild behaviour.

### 9.2 Independent source-wide validator

A separate validator must independently reconstruct and verify:

- source-file hash and integrity;
- physical, admitted and excluded counts;
- ordered 37-field schema;
- source date range;
- 189,043 race groups;
- 1,851,285 runner participations;
- race-group uniqueness;
- runner candidate uniqueness;
- one-to-one admitted source-record-to-runner relationship;
- complete admitted source-record-to-race assignment;
- zero orphan relationships;
- exact raw-value recoverability;
- import-manifest agreement;
- active-database acceptance status.

The independent validator must not merely call the builder's internal assertions.

### 9.3 Project-level acceptance gate

Before the first active database is accepted:

- the complete repository test suite must pass;
- every applicable independent validator must pass;
- the candidate database must pass persisted-readback validation;
- the post-load structural validator must pass;
- the import manifest must record the accepted evidence;
- the prior database or absence of a prior database must be handled explicitly.

Broad project-level runs are required at final integration, not after every small implementation step.

---

## 10. Physical architecture decisions still required

This brief authorises physical work but deliberately does not predetermine the database technology.

The next Phase 4 decision must select and justify:

- database technology;
- database-file, server or warehouse deployment model;
- technical identifier representation;
- raw-value storage types and exact round-trip strategy;
- schema namespaces or layer separation;
- index strategy;
- constraint enforcement;
- migration and database-version strategy;
- candidate-build and atomic-activation approach;
- generated-database artifact location and retention policy;
- query-performance requirements for race and runner access.

Technology must follow this brief.

The technology decision must not expand the authorised domain scope.

---

## 11. Minimum implementation deliverables

The authorised core implementation is complete only when the repository contains, where applicable:

1. an accepted physical-architecture decision;
2. explicit schema or DDL definitions;
3. repeatable source-fingerprint and import code;
4. complete candidate-database build orchestration;
5. immutable raw-record loading;
6. race-occurrence and runner-participation builders;
7. focused unit tests;
8. an independent source-wide database validator;
9. persisted-readback and post-load validation;
10. atomic activation or replacement handling;
11. an import-manifest artifact;
12. a database data dictionary;
13. operator instructions for build, validation, failure and recovery;
14. documented exact baseline results;
15. project-plan, audit, README and lessons-learned updates;
16. local final test and validator evidence.

No governed extension is required to declare the stable core complete.

---

## 12. Stop conditions

Implementation must stop and return to review if:

- the source fingerprint does not match the accepted Source Version 1 file;
- the physical or admitted population differs from the accepted baseline;
- the schema differs from the governed 37-field signature;
- `rowid = 1` cannot be preserved and explicitly accounted for;
- race grouping is no longer unique;
- runner candidate validation fails;
- raw values cannot be round-tripped exactly;
- the proposed technology cannot enforce or validate required constraints;
- the design begins adding unauthorised governed extensions;
- the build requires speculative entities to function;
- an incremental or partial-success path would alter the active database;
- the independent validator cannot reproduce the key counts and relationships;
- the active database could be left partially modified after failure.

A stop condition requires investigation and a new bounded decision. It does not authorise weakening the baseline.

---

## 13. Authorisation decision

This brief authorises Phase 4 to:

- compare and select a physical database technology;
- define the minimum physical schema for the authorised stable core;
- implement the complete Source Version 1 core builder;
- implement the import manifest and validation evidence;
- build and validate the first candidate database;
- activate the database only after the complete admission gate passes.

This brief does not authorise Phase 4 to add any excluded field, identity, meeting, course-history, betting-regime, weather, sectional or analytical structure.

Any such addition requires its own evidence-led extension brief and explicit acceptance.

The accepted first-core boundary is therefore:

> Exact source evidence, Source Version 1 race occurrences, runner participations, structural governance, and fail-closed import evidence—nothing more until a real analytical need justifies it.
