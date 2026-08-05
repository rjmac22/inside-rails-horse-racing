# Phase 3 Entity and Key Design Inventory

## Purpose

This document records the reviewed conceptual entities, grains, identifier scopes, lineage requirements, uncertainty rules and unresolved design questions for Phase 3.

It is deliberately conceptual. It does not define SQL tables, physical data types, indexes or database technology.

The governing principles are:

- preserve immutable source evidence;
- distinguish source records from governed interpretations and real-world entities;
- preserve unresolved cases explicitly;
- assign independent technical identifiers rather than deriving permanent keys from descriptive text;
- avoid designing for hypothetical future sources beyond the flexibility required to admit them safely later.

## Accepted terminology

### Source provider

One organisation, publisher or originating party that supplies data or evidence.

Examples may later include the current historical racing-data publisher, an official racing authority, a weather-data provider or another results archive.

### Source product

One dataset, database, feed, website, reference product or other identifiable information product supplied by a provider.

A source product identifies the continuing product family. It does not identify one exact file delivery, download or retrieval.

### Source version

One exact immutable delivery, file, download, API response or captured edition of a source product.

`source snapshot` may be used as the technical term, but `source version` is preferred in reader-facing documentation.

A later updated `raceform.db` file is a new source version even when it has the same filename.

Each source version must retain enough evidence to distinguish the exact delivered content, including a project-assigned technical identifier and a full-file cryptographic hash where a complete file exists.

### Source relation

One table, relation, file section or equivalent record collection within one source version.

For the current source, this is the `data` table inside the exact governed `raceform.db` source version.

### Source record

One physical record exactly as supplied within one source relation and source version.

For the current source, one source record is identified within its source version by the `data` table and SQLite `rowid`.

### Source claim

One individual value or assertion contained in a source record or external evidence item.

The database will not create a separate claim record for every ordinary raw field value. The immutable raw source record is the evidence for ordinary source-present values.

Separate field-level evidence records are required only when a value is corrected, supplemented, disputed, unresolved or externally enriched.

## Accepted source-evidence rules

1. Every imported source record must retain a route back to its source provider, source product, exact source version and source relation.
2. Every complete source version should have an independent immutable technical identifier.
3. A descriptive filename or version label is not sufficient evidence that two files are identical.
4. A complete source file should retain a cryptographic content hash, file size and other governed structural checks.
5. Reprocessing the same exact immutable source version must not create duplicate source records.
6. A record supplied in a later source version is a new source assertion even when all its displayed values match an earlier version.
7. Cross-version or cross-provider equivalence is a later governed reconciliation decision. It must not be assumed during raw ingestion.
8. New source products will receive their own bounded investigation and validation before admission. Their source-specific record locators will be designed when their actual structure is known.

## Candidate entity inventory

### 1. Source provider

**Grain:** One organisation, publisher or originating party.

**Status:** Source metadata.

**Candidate identifier:** Independent immutable technical identifier assigned by the project.

**Identifier scope:** Project-wide.

**Required lineage and metadata:** Provider name, source notes and any relevant acquisition or licensing context.

**Known uncertainty:** The publisher, data compiler and original sporting authority may be different parties. Those roles must not be assumed identical.

**Expected relationships:** One provider may supply multiple source products.

**Unresolved design questions:** Whether provider roles require a later typed relationship model.

### 2. Source product

**Grain:** One continuing dataset, database, feed, website or reference product.

**Status:** Source metadata.

**Candidate identifier:** Independent immutable technical identifier assigned by the project.

**Identifier scope:** Project-wide.

**Required lineage and metadata:** Provider, product title, acquisition context, source description and relevant licence or usage notes.

**Known uncertainty:** Product branding or ownership may change over time.

**Expected relationships:** One source product may have many source versions.

**Unresolved design questions:** How product renames or provider transfers should be represented if encountered.

### 3. Source version

**Grain:** One exact immutable delivery, file, download, API response or captured edition of a source product.

**Status:** Immutable source evidence.

**Candidate identifier:** Independent project-assigned technical identifier, supported by a cryptographic content hash where applicable.

**Identifier scope:** Project-wide and immutable.

**Required lineage and metadata:**

- source product;
- original filename or retrieval description;
- full-file cryptographic hash where a complete file exists;
- file size where applicable;
- received or retrieved date;
- structural schema signature;
- physical and governed record counts;
- observed minimum and maximum source dates where applicable;
- repository commit and reference-data version used for processing;
- notes on unusual delivery characteristics.

**Known uncertainty:** Some future sources may be API responses or webpages rather than complete files. Their version evidence may require request parameters, retrieval timestamps and retained response hashes instead.

**Expected relationships:** One source version contains one or more source relations and participates in one or more import manifests.

**Unresolved design questions:** The exact required fingerprint and retrieval metadata for non-file sources.

### 4. Source relation

**Grain:** One table, relation, file section or equivalent record collection within one source version.

**Status:** Immutable source structure.

**Candidate identifier:** Source version plus relation identity, supported by an independent technical identifier.

**Identifier scope:** Source-version-scoped.

**Required lineage and metadata:** Source version, raw relation name or locator and governed schema signature.

**Known uncertainty:** Future sources may not expose conventional tables.

**Expected relationships:** One source relation contains many source records.

**Unresolved design questions:** How file sections, API endpoints and nested response collections should map to this concept when introduced.

### 5. Source record

**Grain:** One physical record exactly as supplied within one source relation and source version.

**Status:** Immutable source evidence.

**Candidate identifier:** Independent technical identifier plus the exact source-local locator.

For the current source, the exact source-local locator is:

`source version + data relation + SQLite rowid`

**Identifier scope:** Source-version-and-relation-scoped for the source-local locator; project-wide for the independent technical identifier.

**Required lineage and metadata:**

- source version;
- source relation;
- original SQLite `rowid` for the current source;
- every one of the 37 raw values unchanged;
- original source storage state where required for governed interpretation.

**Known uncertainty:** SQLite `rowid` may change if the provider rebuilds the source database. It is not a cross-version identity.

**Expected relationships:** A current governed source record supports exactly one current runner record. A source record may also be the subject of zero or more field-level evidence, correction, supplementation or dispute records.

**Unresolved design questions:** Source-specific locators for future providers.

## Source record and runner record distinction

### 6. Runner record

**Grain:** One governed representation of one horse's recorded participation in one source race occurrence.

**Status:** Structural governed interpretation derived from source evidence.

**Candidate identifier:** Independent immutable technical identifier.

Within the current source version, the validated candidate matching rule is:

`source race occurrence + raw horse label`

**Identifier scope:** Current source-version-scoped unless later cross-version reconciliation establishes otherwise.

**Required lineage:** Direct reference to the supporting source record, source race occurrence, raw horse label, supplied `race_id`, supplied `num` and all governed derivation statuses required by downstream fields.

**Known uncertainty:** A future source may omit runners, duplicate versions, split one runner across several records or provide corrections separately.

**Expected relationships:**

- every current source record produces exactly one current runner record;
- every current runner record is supported by exactly one current source record;
- many runner records belong to one source race occurrence;
- a runner record may link to a provisional horse occurrence and governed participant labels separately.

**Accepted rule:** Source record and runner record receive separate technical identities even though they currently reconcile one-to-one.

**Unresolved design questions:** How later supplementary runner records and cross-source runner equivalence should be represented.

## Source race occurrence and race-time distinction

### 7. Source race occurrence

**Grain:** One race as represented within one exact source version.

**Status:** Structural governed interpretation derived from the source version's raw race fields.

**Candidate identifier:** Independent immutable technical identifier.

Within the current source version, the validated grouping rule uses the exact raw values:

`raw date + raw course + raw off`

Raw `race_name` remains a required validation attribute.

**Identifier scope:** Source-version-scoped.

**Required lineage:** Source version, all supporting source records, raw `date`, raw `course`, raw `off`, raw `race_name`, supplied non-unique `race_id` values and the reconstruction method.

**Known uncertainty:** A future source version may alter the raw course label, advertised off-time or race name. Such a change must not automatically create a new real-world race or overwrite the earlier source race occurrence.

**Expected relationships:**

- one source race occurrence contains one or more runner records;
- every current runner record belongs to exactly one source race occurrence;
- one source race occurrence may have one governed race-time decision containing resolved or unresolved interpretations;
- possible cross-version or cross-provider real-world race links are deferred.

**Accepted rule:** The raw `off` value is part of current source-version grouping only. It is not treated as a confirmed real-world timestamp.

**Unresolved design questions:** Cross-version and cross-provider race reconciliation when another actual source version or provider becomes available.

### 8. Governed race-time decision

**Grain:** One governed temporal interpretation for one source race occurrence.

**Status:** Governed interpretation, not source identity.

**Candidate identifier:** Independent technical identifier or one-to-one dependent identity attached to the source race occurrence; physical choice deferred.

**Identifier scope:** Source-race-occurrence-scoped and versioned by governing method/reference release where required.

**Required lineage and evidence:**

- raw source `date` and `off`;
- source-facing timezone assumption;
- candidate AM/PM branches where applicable;
- UTC and course-local candidates;
- selected values where resolved;
- decision method;
- confidence;
- resolution status;
- course and timezone reference versions;
- preserved unresolved candidates.

**Known uncertainty:** The current validated output resolves 169,465 source race occurrences and preserves 19,578 unresolved. A resolved value remains a governed interpretation rather than a component of immutable race identity.

**Expected relationships:** Exactly one current governed decision state per source race occurrence for a given accepted governance release.

**Accepted rule:** Canonical UTC or course-local time is an attribute of the source race occurrence and may remain unresolved. It is never substituted into the immutable raw race grouping key.

**Unresolved design questions:** The detailed amendment/version-history mechanism for later changes to governed temporal decisions.

## Deferred real-world race identity

A source race occurrence is not yet a verified provider-independent real-world race entity.

When a later source version or another provider becomes available, possible equivalence may be assessed using evidence such as:

- race date;
- governed course identity;
- race name;
- runners or horse labels;
- supplied provider identifiers as supporting evidence only;
- neighbouring races at the meeting;
- official identifiers where available;
- raw and governed time evidence.

No cross-version or cross-provider race merge is authorised in the current phase inventory merely because descriptive fields appear similar.

## Claim-level evidence rule

Every ordinary raw field remains preserved inside its immutable source record. The project will not create a separate stored claim row for all 37 fields across all 1,851,285 governed runner rows.

A separate claim-level or field-level governed record is required when a value is:

- corrected;
- supplemented;
- disputed;
- unresolved through external review;
- externally enriched;
- reconciled across source versions or providers.

Such a record must identify the exact source record and field, preserve the raw value, retain the governed value where established, record the evidence and confidence, and state the permitted database action.

## Current accepted design boundary

The inventory currently establishes only the source-evidence foundation, source-record and runner-record distinction, source race occurrence, and governed race-time separation.

It does not yet define:

- SQL tables;
- physical key types;
- cross-version race reconciliation;
- governed horse identity structure beyond its existing occurrence contract;
- participant or ownership entity detail;
- amendment-history implementation;
- import-manifest structure;
- validation-evidence record structure;
- physical database technology.

These will be added through later bounded Phase 3 design questions after review.
