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

This matching rule is a current-source validation rule. It is not the runner record's permanent technical identifier and does not establish permanent horse identity across races.

**Identifier scope:** Current source-version-scoped unless later cross-version reconciliation establishes otherwise.

**Required lineage:** Direct reference to the supporting source record, source race occurrence, raw horse label, supplied `race_id`, supplied `num` and all governed derivation statuses required by downstream fields.

**Known uncertainty:** A future source may omit runners, duplicate versions, split one runner across several records or provide corrections separately.

**Expected relationships:**

- every current source record produces exactly one current runner record;
- every current runner record is supported by exactly one current source record;
- many runner records belong to one source race occurrence;
- a runner record preserves exactly one raw horse label from its supporting source record;
- a runner record may link to at most one governed provisional horse occurrence under the accepted current governance release;
- governed jockey, trainer and owner relationships remain separate from horse occurrence identity.

**Accepted rules:**

- source record and runner record receive separate technical identities even though they currently reconcile one-to-one;
- the runner record identifies participation in a race, not the permanent identity of the horse;
- the raw horse label remains immutable source evidence and must never be replaced by a provisional horse identifier.

**Unresolved design questions:** How later supplementary runner records and cross-source runner equivalence should be represented.

## Runner record and horse identity distinction

### 7. Raw horse-label assertion

**Grain:** The exact source-presented horse label carried by one source record and inherited by its current runner record.

**Status:** Immutable source assertion.

**Candidate identifier:** The supporting source record and source field identify the assertion; no separate permanent real-world horse identifier is derived from the text.

**Identifier scope:** Source-record-scoped.

**Required lineage:** Source version, source relation, source record, raw `horse` value and original storage state.

**Known uncertainty:** The same displayed horse label can represent different real horses, and one real horse can appear with inconsistent or incorrect supporting pedigree assertions.

**Expected relationships:**

- one current runner record preserves one raw horse-label assertion;
- many runner records may share the same raw text without thereby sharing one verified horse identity;
- the assertion may support a governed provisional horse occurrence assignment.

**Accepted rule:** Raw horse text is evidence and a current-source matching attribute. It is not a permanent natural key for a horse.

**Unresolved design questions:** None at this grain; cross-source label reconciliation remains deferred.

### 8. Provisional horse occurrence

**Grain:** One governed source-internal horse-history occurrence created by Notebook 19's bounded correction, split and unresolved rules.

**Status:** Governed provisional identity used for analysis within the current source programme.

**Candidate identifier:** The existing governed `provisional_horse_occurrence_id`, treated as an independent source-internal analytical identifier.

**Identifier scope:** Current governed source population and governing identity release. It is not an official registration number, life number or provider-independent horse identifier.

**Required lineage and evidence:**

- every assigned runner record and its supporting source record;
- exact raw horse label;
- structured pedigree history used by the governed derivation;
- occurrence sequence;
- identity outcome and decision basis;
- relevant transition decision identifiers;
- governed pedigree fields where established;
- verification identifier, confidence and review status where applicable;
- explicit unresolved state where the evidence does not permit a correction or split.

**Known uncertainty:** The occurrence model prevents unsafe same-label merging inside the current source, but it does not prove official horse identity across providers. `Runninsonofagun (IRE)` remains a governed unresolved pedigree relationship.

**Expected relationships:**

- one provisional horse occurrence may be linked from many runner records across races;
- one runner record may link to at most one provisional horse occurrence under one accepted governance release;
- a raw horse label may correspond to more than one provisional horse occurrence where governed different-horse split boundaries exist;
- unresolved relationships remain explicit and must not be converted into an unsupported identity merge or split.

**Accepted rules:**

- runner participation identity and horse-history identity remain separate;
- provisional occurrence links may be used for governed horse-level analysis while their source-internal status is stated;
- raw horse and pedigree values remain unchanged even when a governed correction or split is applied;
- analyses that do not require horse continuity may use runner records without implying permanent horse identity;
- no provisional occurrence may be presented as an official or globally verified horse identity.

**Unresolved design questions:**

- how a future official horse identifier would be related to existing provisional occurrences;
- how occurrence assignments are versioned if later authority evidence changes a governed boundary;
- how provisional occurrences from another provider would be reconciled with this source-internal occurrence layer.

### 9. Runner-to-horse-occurrence assignment

**Grain:** One governed assignment of one runner record to one provisional horse occurrence under one accepted identity-governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Runner record plus governance release, supported by an independent relationship identifier if required by the later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:** Runner record, provisional horse occurrence, assignment method, governing output/reference version, decision basis, status, confidence where applicable and any supporting transition or verification identifier.

**Known uncertainty:** Later authority evidence may amend an occurrence boundary or assignment. Historical accepted assignments must remain reconstructable rather than being silently overwritten.

**Expected relationships:**

- a runner record has zero or one accepted provisional horse occurrence assignment within one governance release;
- a provisional horse occurrence may receive many runner-record assignments;
- unresolved identity evidence must remain represented without creating multiple active accepted assignments.

**Accepted rule:** The relationship must carry its governed status and release context so that a provisional horse occurrence is not mistaken for a raw source fact or eternal identity.

**Unresolved design questions:** The detailed amendment and effective-version mechanism is deferred to the later Phase 3 history-design task.

## Runner record and participant identity distinction

### 10. Raw participant-label assertion

**Grain:** One exact source-presented label in one participant-role field on one source record and inherited by its runner record.

**Status:** Immutable source assertion.

**Candidate identifier:** The supporting source record plus the exact source field; no real-world participant identifier is derived directly from the text.

**Identifier scope:** Source-record-and-role-scoped.

**Required lineage and evidence:** Source version, source relation, source record, participant role, exact raw value and original storage state.

The current participant roles in scope are jockey and trainer. The raw owner field is governed separately as an ownership-composition assertion because it may represent more than one person or organisation.

**Known uncertainty:** Participant labels may contain initials, titles, abbreviations, spelling variants, punctuation variants or errors. The same displayed label may represent different people, while one person may appear under several labels.

**Expected relationships:**

- one runner record preserves the source-presented jockey and trainer assertions where populated;
- many assertions may share identical raw text without thereby identifying one verified person;
- one assertion may support an optional governed provisional participant assignment;
- blank or unresolved values remain preserved through the source record and do not create artificial participant entities.

**Accepted rules:**

- raw participant labels are source facts, not verified people;
- textual normalisation alone does not authorise identity merging;
- an unresolved label remains unresolved rather than being attached to a generic `unknown` participant.

**Unresolved design questions:** Source-specific handling for future roles such as breeder, agent or stable representative will be considered only when those fields are introduced.

### 11. Provisional participant identity

**Grain:** One governed source-internal identity for a jockey or trainer where available evidence supports the link.

**Status:** Optional governed interpretation.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Current governed source population and participant-governance release. Identity remains role-scoped unless explicit evidence supports a cross-role equivalence.

**Required lineage and evidence:**

- every linked raw participant-label assertion and runner record;
- participant role;
- accepted display label and known source-presented variants;
- decision method and evidence;
- governance release;
- resolution status;
- confidence and review status where applicable;
- external identifiers only where independently verified and recorded with provenance.

**Known uncertainty:** The project has not confirmed the real-world identity behind many jockey and trainer labels. A provisional participant identity is not automatically an official licensing identity or a provider-independent person record.

**Expected relationships:**

- one provisional participant identity may receive many governed label assignments;
- a raw participant-label assertion may have zero or one accepted provisional identity assignment within one governance release;
- unresolved or competing candidate relationships remain separate from accepted assignments;
- the same normalised label may remain split across provisional identities where evidence does not support a merge.

**Accepted rules:**

- provisional participant identities are created only where the governed evidence supports them;
- no participant identity is created merely to eliminate a null or unresolved label;
- provisional identities must not be presented as official or globally verified people;
- raw labels remain unchanged after a provisional assignment is made.

**Unresolved design questions:**

- how future official licence or registration identifiers should relate to provisional participant identities;
- whether and when cross-role person identity should be governed;
- how participant identities from another provider should be reconciled.

### 12. Runner-to-participant-role assignment

**Grain:** One governed assignment of one runner record's participant-role assertion to one provisional participant identity under one accepted governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Runner record plus participant role plus governance release, supported by an independent relationship identifier if required by the later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:** Runner record, raw participant-label assertion, participant role, provisional participant identity where accepted, assignment method, evidence, status, confidence where applicable and governing output/reference version.

**Known uncertainty:** Later authoritative evidence may change an assignment. Previous accepted states must remain reconstructable and must not be silently overwritten.

**Expected relationships:**

- a runner record has zero or one accepted provisional identity assignment for each participant role within one governance release;
- one provisional participant identity may be assigned to many runner records;
- unresolved candidate relationships may be retained without becoming accepted assignments;
- analyses may use raw participant labels where identity continuity is unnecessary.

**Accepted rule:** The governed link is optional. Absence of a verified or provisional identity must not prevent preservation or use of the runner record.

**Unresolved design questions:** The detailed amendment and effective-version mechanism remains deferred to the later Phase 3 history-design task.

## Runner record and ownership-composition distinction

### 13. Raw ownership-composition assertion

**Grain:** The exact complete owner label supplied for one source record and inherited by its runner record.

**Status:** Immutable source assertion.

**Candidate identifier:** The supporting source record plus the raw owner field; no individual owner identity is derived directly from the text.

**Identifier scope:** Source-record-scoped.

**Required lineage and evidence:** Source version, source relation, source record, exact raw owner value, punctuation, ordering, separators and original storage state.

**Known uncertainty:** An owner label may represent one person, several people, a partnership, syndicate, company, stud, club or another organisation. Apparent separators and ordering do not reliably prove component membership or legal identity.

**Expected relationships:**

- one runner record preserves the complete source-presented owner assertion where populated;
- many runner records may share identical raw owner text without thereby establishing a verified owner or ownership group;
- the complete assertion may support an optional provisional ownership-composition assignment;
- any later component-level identities remain separate governed interpretations.

**Accepted rules:**

- the whole source-presented ownership composition is the primary assertion;
- raw owner text must not be automatically split into individual people or organisations;
- reordering, punctuation changes or normalisation alone do not prove composition equivalence;
- unresolved owner labels remain unresolved rather than creating artificial owner entities.

**Unresolved design questions:** Whether particular source syntaxes can later support governed component parsing after separate validation.

### 14. Provisional ownership composition

**Grain:** One governed source-internal ownership composition, treated as a complete composition, where evidence supports linking source-presented owner assertions.

**Status:** Optional governed interpretation.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Current governed source population and ownership-governance release. It is not automatically an official registered ownership entity.

**Required lineage and evidence:**

- every linked raw ownership-composition assertion and runner record;
- accepted display label and source-presented variants;
- composition decision method;
- governance release;
- resolution status;
- evidence, confidence and review status where applicable;
- constituent participant or organisation identities only where separately confirmed and governed.

**Known uncertainty:** Ownership can change over time, and labels that look similar may represent different compositions. A syndicate or partnership name may itself be the ownership entity rather than a list of underlying members.

**Expected relationships:**

- one provisional ownership composition may be assigned to many runner records;
- one raw ownership-composition assertion may have zero or one accepted composition assignment within one governance release;
- one composition may later relate to zero or more separately governed constituent identities;
- unresolved or competing composition candidates remain separate from accepted assignments.

**Accepted rules:**

- ownership-composition identity applies to the complete composition, not automatically to each apparent name within it;
- no individual owner person or organisation is created from unverified string parsing;
- raw owner labels remain unchanged after a governed composition assignment;
- provisional compositions must not be presented as official or globally verified ownership registrations.

**Unresolved design questions:**

- whether and how constituent ownership members should later be represented;
- how ownership changes and effective periods should be modelled;
- how official registered-owner evidence should relate to provisional compositions;
- how compositions from another provider should be reconciled.

### 15. Runner-to-ownership-composition assignment

**Grain:** One governed assignment of one runner record's raw ownership-composition assertion to one provisional ownership composition under one accepted governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Runner record plus governance release, supported by an independent relationship identifier if required by the later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:** Runner record, raw ownership-composition assertion, provisional ownership composition where accepted, assignment method, evidence, status, confidence where applicable and governing output/reference version.

**Known uncertainty:** Later evidence may change whether two owner labels represent the same composition. Previous accepted states must remain reconstructable rather than being silently overwritten.

**Expected relationships:**

- a runner record has zero or one accepted provisional ownership-composition assignment within one governance release;
- one provisional ownership composition may receive many runner-record assignments;
- unresolved candidate relationships may be retained without becoming accepted assignments;
- analyses that do not require ownership continuity may use raw owner labels without implying verified ownership identity.

**Accepted rule:** Ownership identity remains optional and composition-level. Failure to resolve it must not prevent preservation or analysis of the runner record.

**Unresolved design questions:** The detailed amendment and effective-version mechanism remains deferred to the later Phase 3 history-design task.

## Source course assertion and racecourse context distinction

### 16. Raw course-label assertion

**Grain:** The exact source-presented `course` value attached to one source race occurrence through its supporting source records.

**Status:** Immutable source assertion.

**Candidate identifier:** Source version, source race occurrence and source field; no permanent racecourse identity is derived directly from the label.

**Identifier scope:** Source-race-occurrence-scoped.

**Required lineage and evidence:** Source version, supporting source records, exact raw `course` value, source-presented jurisdiction context where available, race date and original storage state.

**Known uncertainty:** A course may change name, use sponsorship naming, reuse an historical name, relocate, close, reopen or be confused with a same-named course in another jurisdiction.

**Expected relationships:**

- every current source race occurrence preserves exactly one raw course-label assertion;
- many source race occurrences may share the same raw label without thereby proving one venue, site or configuration;
- a raw course-label assertion may support an optional governed course-context assignment;
- same-named labels in different jurisdictions remain separate candidates unless explicit evidence establishes another relationship.

**Accepted rules:**

- the raw course label remains immutable source evidence;
- `course label + jurisdiction + relevant date` is matching evidence, not a permanent natural key;
- textual normalisation, abbreviation expansion or sponsorship-name removal alone does not authorise a merge.

**Unresolved design questions:** Source-specific handling where jurisdiction must itself be inferred rather than supplied.

### 17. Governed racecourse venue

**Grain:** One continuing real-world racing venue or institutional course identity whose continuity may span verified name changes and, in exceptional cases, changes of physical site.

**Status:** Governed real-world entity with explicitly bounded continuity.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Project-wide, subject to governed historical amendment rather than source-label scope.

**Required lineage and evidence:**

- accepted venue name and verified historical or sponsored names;
- jurisdiction and relevant racing authority;
- evidence supporting continuity through each name or status change;
- operational dates where known;
- relationships to physical sites and course configurations;
- closure, reopening, relocation, predecessor or successor evidence where applicable;
- governance release, decision status and confidence.

**Known uncertainty:** Institutional continuity is not always the same as physical continuity. A named racing organisation may move, rebuild or temporarily stage racing elsewhere.

**Expected relationships:**

- one racecourse venue may have many verified name assertions over time;
- one venue may use one or more physical sites over its history;
- one physical site may host more than one institutional venue in exceptional cases;
- one venue may have many course configurations or configuration eras;
- predecessor, successor or temporary-host relationships remain explicit rather than being represented as unconditional identity merges.

**Accepted rules:**

- a verified naming or sponsorship change may remain the same venue;
- a change of physical site does not automatically preserve or end venue identity; the continuity decision must be explicit and evidenced;
- same-named courses in different jurisdictions are never merged automatically;
- the venue identifier answers an institutional-continuity question, not every course-equivalence question.

**Unresolved design questions:** The exact evidence threshold for treating a relocated institution as the same venue rather than a predecessor and successor pair.

### 18. Racecourse physical site

**Grain:** One geographically distinct real-world location at which racing is staged during a defined period.

**Status:** Governed geographical entity.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Project-wide and location-specific.

**Required lineage and evidence:**

- verified coordinates or bounded location description;
- jurisdiction, locality and timezone evidence;
- effective dates where use of the site changed;
- source and confidence for location attributes;
- related venue or venues;
- temporary, replacement or relocated-use status where applicable.

**Known uncertainty:** Coordinates, boundaries and published addresses can vary in precision. A course may occupy the same broad site while its racing surface or layout changes materially.

**Expected relationships:**

- one racecourse venue may be associated with several physical sites over time;
- one physical site may support several course configurations, including simultaneous straight, round, inner, outer, hurdle or chase layouts;
- weather, altitude, geography and travel analysis should normally resolve at physical-site level rather than venue-name level;
- a temporary relocation links the race to the temporary physical site even where institutional venue continuity is retained.

**Accepted rules:**

- physical location is separate from venue name and institutional continuity;
- a genuine move to another site creates a distinct physical-site identity;
- site-level analysis must not assume that all races under one venue name occurred at one unchanged location;
- location and timezone attributes require provenance and effective periods where they can change.

**Unresolved design questions:** The precision standard required for coordinates and site boundaries in later geographical and weather studies.

### 19. Course configuration era

**Grain:** One materially consistent racing layout, surface or course configuration at one physical site during a defined effective period.

**Status:** Governed analysis context.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Physical-site-and-effective-period-scoped, with separate identities where simultaneous materially different layouts exist.

**Required lineage and evidence:**

- physical site and related venue;
- configuration or layout label where available;
- racing code and surface where relevant;
- geometry, direction, turns, straight length, obstacles, rails, drainage or other material design attributes where established;
- effective start and end dates or bounded uncertainty;
- evidence for openings, closures, redesigns, resurfacing or material alterations;
- governance release, status and confidence.

**Known uncertainty:** Not every alteration is analytically material, and the threshold depends on the study. Some changes affect draw, pace, going or distance comparability while others do not.

**Expected relationships:**

- one physical site may have many successive configuration eras;
- one physical site may have several simultaneous configurations or named layouts;
- one venue may therefore relate to several configurations at the same time;
- a material redesign may end one configuration era and begin another without creating a new venue or physical site;
- configuration-level evidence may remain unresolved even when venue and site are known.

**Accepted rules:**

- a major redesign can remain the same venue and site while becoming a different configuration era;
- straight, round, inner, outer, hurdle, chase or other materially distinct layouts may be treated separately where the evidence and analysis require it;
- minor changes are not forced into new configuration identities unless a governed study establishes material analytical impact;
- configuration identity must carry effective-period evidence rather than being treated as timeless.

**Unresolved design questions:** The field-specific materiality rules that determine when rails, drainage, obstacle, surface or geometry changes require a new configuration era.

### 20. Source-race-to-course-context assignment

**Grain:** One governed assignment of one source race occurrence to its best-supported venue, physical site and course configuration context under one accepted governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Source race occurrence plus governance release, supported by an independent relationship identifier if required by the later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:**

- source race occurrence and raw course-label assertion;
- race date and jurisdiction evidence;
- assigned venue where resolved;
- assigned physical site where resolved;
- assigned configuration era where resolved;
- assignment method, evidence, confidence and review status;
- unresolved or competing candidates;
- governing reference-data version.

**Known uncertainty:** Resolution may be partial. A venue may be confidently known while the physical site or exact configuration remains unresolved.

**Expected relationships:**

- each source race occurrence has zero or one accepted venue assignment within one governance release;
- each source race occurrence has zero or one accepted physical-site assignment within one governance release;
- each source race occurrence has zero or one accepted configuration-era assignment within one governance release;
- unresolved finer-grained context does not invalidate a supported broader assignment;
- later evidence may amend an assignment while retaining the historical accepted state.

**Accepted rules:**

- course context may be resolved at different levels rather than forced into one all-purpose course identity;
- raw course labels are never overwritten by governed venue, site or configuration assignments;
- analyses must use the narrowest supported course level needed for their question and must not silently substitute venue equivalence for site or configuration equivalence;
- failure to resolve a configuration must not prevent valid venue-level or site-level analysis.

**Unresolved design questions:** The detailed amendment and effective-version mechanism remains deferred to the later Phase 3 history-design task.

## Analysis-dependent course equivalence

The phrase `same course` is not treated as one universal database fact. It is a study-level equivalence decision made from separately preserved course entities.

The expected analytical levels are:

- **venue continuity:** use when the question concerns the continuing institution, long-run operation or published course identity;
- **physical-site continuity:** use for geography, weather, altitude, travel and other location-dependent analysis;
- **configuration-era continuity:** use for draw, pace, distance, going, surface, obstacle or layout-sensitive analysis;
- **exact supported layout:** use where a study has evidence that a more specific simultaneous layout distinction is material.

A study must declare the course-equivalence level it uses and the unresolved cases it excludes or retains. The database must not collapse venue, site and configuration history into one permanent course label merely for convenience.

Examples of accepted treatment are:

- a verified sponsorship rename may be the same venue, site and configuration;
- a major redesign may be the same venue and site but a new configuration era;
- a move to a different location creates a new physical site and requires an explicit decision on institutional venue continuity;
- a temporary relocation may retain institutional continuity while assigning affected races to a different physical site;
- simultaneous straight, round, inner, outer or code-specific layouts may be different configurations without being different venues.

## Source race occurrence and race-time distinction

### 21. Source race occurrence

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
- one source race occurrence may have one governed course-context assignment resolved at venue, physical-site and configuration levels;
- one source race occurrence may have one governed race-time decision containing resolved or unresolved interpretations;
- possible cross-version or cross-provider real-world race links are deferred.

**Accepted rule:** The raw `off` value is part of current source-version grouping only. It is not treated as a confirmed real-world timestamp.

**Unresolved design questions:** Cross-version and cross-provider race reconciliation when another actual source version or provider becomes available.

### 22. Governed race-time decision

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
- course, physical-site and timezone reference versions;
- preserved unresolved candidates.

**Known uncertainty:** The current validated output resolves 169,465 source race occurrences and preserves 19,578 unresolved. A resolved value remains a governed interpretation rather than a component of immutable race identity.

**Expected relationships:** Exactly one current governed decision state per source race occurrence for a given accepted governance release.

**Accepted rule:** Canonical UTC or course-local time is an attribute of the source race occurrence and may remain unresolved. It is never substituted into the immutable raw race grouping key.

**Unresolved design questions:** The detailed amendment/version-history mechanism for later changes to governed temporal decisions.

## Deferred real-world race identity

A source race occurrence is not yet a verified provider-independent real-world race entity.

When a later source version or another provider becomes available, possible equivalence may be assessed using evidence such as:

- race date;
- governed venue, physical-site and course-configuration context;
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

The inventory currently establishes:

- the source-evidence foundation;
- source-record and runner-record separation;
- raw horse-label assertions;
- provisional horse occurrences;
- governed runner-to-horse-occurrence assignments;
- raw jockey and trainer label assertions;
- optional provisional participant identities;
- governed runner-to-participant-role assignments;
- raw ownership-composition assertions;
- optional provisional ownership compositions;
- governed runner-to-ownership-composition assignments;
- raw course-label assertions;
- governed racecourse venues;
- physical racecourse sites;
- course configuration eras;
- governed source-race-to-course-context assignments;
- analysis-dependent course equivalence;
- source race occurrences;
- governed race-time separation.

It does not yet define:

- SQL tables;
- physical key types;
- cross-version race reconciliation;
- official or provider-independent horse identity;
- official or provider-independent participant identity;
- verified constituent owner identities;
- complete historical course-reference coverage;
- field-specific configuration-change materiality rules;
- amendment-history implementation;
- import-manifest structure;
- validation-evidence record structure;
- physical database technology.

These will be added through later bounded Phase 3 design questions after review.
