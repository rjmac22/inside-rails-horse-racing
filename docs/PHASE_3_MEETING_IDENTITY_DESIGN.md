# Phase 3 Meeting Identity Design

## Purpose

This document records the accepted conceptual design for meeting identity within Phase 3.

It supplements `docs/PHASE_3_ENTITY_AND_KEY_DESIGN_INVENTORY.md` and remains conceptual. It does not define SQL tables, physical key types, indexes or database technology.

The design preserves the distinction between:

- raw source race evidence;
- one meeting as represented inside one exact source version;
- governed membership of races within that meeting;
- optional meeting sessions or card sections where required;
- later provider-independent or cross-version meeting identity.

## Accepted governing rule

Races sharing a raw course label and raw date are candidate members of one source meeting, but meeting membership is a governed structural decision rather than an unquestioned natural key.

The combination:

`source version + raw date + raw course`

is therefore grouping evidence for the current source. It is not a permanent technical meeting identifier and does not prove one real-world meeting across source versions or providers.

## Why date and course are not enough

A single raw date-and-course grouping can conceal materially different structures, including:

- separate cards or sessions staged at the same venue on the same date;
- a card split into afternoon and evening sessions;
- partial abandonment after some races were run;
- races transferred from another advertised meeting;
- resumed or rearranged races;
- duplicate or corrected source representations;
- inconsistent source course labels within what external evidence later establishes was one meeting;
- a temporary or replacement site used under the identity of another venue.

Conversely, races that belong to one continuing meeting may not always share one unchanged source label, advertised venue or temporal representation.

The model must therefore preserve the source grouping evidence without allowing that evidence to decide meeting identity automatically.

## Candidate entity inventory

### 1. Source meeting occurrence

**Grain:** One meeting or race card as represented within one exact source version under one accepted meeting-governance release.

**Status:** Structural governed interpretation derived from source race occurrences and their source evidence.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Source-version-and-governance-release-scoped. It is not a provider-independent real-world meeting identifier.

**Candidate grouping evidence for the current source:**

- exact source version;
- raw race date;
- raw course label;
- race sequence and raw off values;
- race names;
- supplied race identifiers as supporting evidence only;
- runner populations;
- governed course context where available;
- neighbouring races on the apparent card.

**Required lineage and evidence:**

- exact source version;
- every member source race occurrence;
- raw date and course assertions used during reconstruction;
- reconstruction method and governance release;
- meeting status where established;
- evidence for any split, transfer, resumption, rearrangement or partial abandonment;
- assigned venue, physical site or configuration context only where separately governed;
- unresolved or competing meeting candidates;
- review status and confidence where applicable.

**Known uncertainty:**

- the current source is primarily race-and-runner evidence rather than an independently verified meeting register;
- races sharing date and course may represent more than one card or session;
- a meeting may be advertised for one venue but partly or wholly staged elsewhere;
- incomplete or abandoned meetings may not be fully visible in a results-led source;
- future source versions may add, remove, reorder or relabel races.

**Expected relationships:**

- one source meeting occurrence may contain one or more source race occurrences;
- one source race occurrence has zero or one accepted meeting assignment within one governance release;
- unresolved race membership remains explicit rather than being forced;
- one meeting may contain one or more meeting-session occurrences where a verified session distinction is analytically or operationally material;
- one meeting may relate to an advertised venue context and a staged venue or site context without assuming they are identical;
- cross-version or cross-provider equivalence remains a separate later reconciliation decision.

**Accepted rules:**

- a source meeting occurrence receives its own technical identity;
- `raw date + raw course` is matching evidence, not its permanent natural key;
- a meeting is not inferred solely because races share text fields;
- source race evidence is never overwritten after a meeting assignment;
- uncertainty about meeting boundaries must remain explicit;
- meeting reconstruction must be repeatable from the accepted governance release and retained evidence.

**Unresolved design questions:**

- the exact evidence threshold for splitting same-date, same-course races into separate meetings;
- whether current source-wide validation can identify all genuine multi-session cases;
- how advertised, scheduled, staged and completed meeting states should be related when richer sources are introduced.

### 2. Source-race-to-meeting assignment

**Grain:** One governed assignment of one source race occurrence to one source meeting occurrence under one accepted meeting-governance release.

**Status:** Governed relationship, not immutable source fact.

**Candidate identifier:** Source race occurrence plus governance release, supported by an independent relationship identifier if required by the later physical design.

**Identifier scope:** Governance-release-scoped.

**Required lineage and evidence:**

- source race occurrence;
- source meeting occurrence where accepted;
- candidate raw date-and-course grouping;
- assignment method;
- supporting race sequence, off-time, race-name and runner evidence;
- course-context evidence where applicable;
- status, confidence and review state;
- unresolved or competing meeting candidates;
- governing output and reference-data versions.

**Known uncertainty:** Later evidence may show that races assigned together were separate cards, or that races assigned separately belonged to one rearranged or transferred meeting.

**Expected relationships:**

- one source race occurrence has zero or one accepted source-meeting assignment within one governance release;
- one source meeting occurrence may receive many source-race assignments;
- an unresolved race may remain without an accepted meeting assignment;
- historical accepted assignments must remain reconstructable when later evidence changes the current decision.

**Accepted rules:**

- meeting membership is an explicit governed relationship;
- no source race occurrence is silently reassigned or overwritten;
- absence of a resolved meeting assignment must not prevent race-level or runner-level analysis;
- analyses using meeting-level aggregates must state how unresolved or split assignments were handled.

**Unresolved design questions:** The detailed amendment and effective-version mechanism remains deferred to the later Phase 3 history-design task.

### 3. Meeting-session occurrence

**Grain:** One verified operational or card section within one source meeting occurrence where a session distinction is required.

**Status:** Optional governed structural interpretation.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Source-meeting-and-governance-release-scoped.

**Possible reasons for creating a session occurrence:**

- separately advertised afternoon and evening cards;
- a formally split meeting;
- a resumed section after interruption;
- a transferred or rearranged section that retains a governed relationship to the broader meeting;
- another independently evidenced division that is material to analysis.

**Required lineage and evidence:**

- parent source meeting occurrence;
- assigned source race occurrences;
- session label where supplied or governed;
- temporal ordering and time evidence;
- advertised and staged venue or site context where relevant;
- reason for the session distinction;
- evidence, status, confidence and governance release.

**Known uncertainty:** A long gap between races or an apparent morning/evening pattern does not by itself prove separate sessions.

**Expected relationships:**

- one source meeting occurrence may contain zero, one or many session occurrences;
- one source race occurrence may belong to zero or one accepted session occurrence within a governance release;
- a meeting does not require a session layer where the distinction adds no supported meaning;
- session identity does not replace meeting identity or race identity.

**Accepted rules:**

- session entities are created only where evidence or analytical need supports the distinction;
- sessions are not manufactured merely to make every meeting structurally uniform;
- raw race date, course and off values remain unchanged;
- analyses must not interpret an inferred time gap as a verified session boundary without supporting evidence.

**Unresolved design questions:** The first implementation may defer session construction until a dedicated meeting-structure study establishes reliable rules.

## Meeting status and exceptional structures

The meeting model must be able to retain, where evidence later becomes available:

- scheduled;
- staged;
- completed;
- partly completed;
- abandoned before racing;
- abandoned after one or more races;
- transferred;
- rearranged;
- resumed;
- split into sessions;
- cancelled or duplicated in the source.

These statuses are governed descriptions of what happened. They must not overwrite the source evidence or be inferred solely from a missing race count.

A transferred or temporarily relocated card may require several separate facts:

- the advertised meeting or venue;
- the source-presented meeting and course labels;
- the physical site at which each race was staged;
- the continuing institutional venue relationship, where any;
- the meeting, session and race membership decisions.

The database must not force those distinct questions into one `course` or `meeting` identifier.

## Meeting-level analysis rule

A study using meeting-level aggregates must state:

- the meeting-governance release used;
- whether meeting sessions were combined or separated;
- how transferred, rearranged and partially abandoned cards were handled;
- whether venue, physical-site or configuration continuity was required;
- how unresolved meeting assignments were treated.

Meeting-level analysis must not simply group by raw `date + course` and present the result as verified meeting identity unless the study explicitly states that it is using a source-level approximation.

## Deferred provider-independent meeting identity

A source meeting occurrence is not yet a verified cross-version or provider-independent real-world meeting entity.

When another source version or provider is introduced, possible equivalence may be assessed using evidence such as:

- advertised and actual dates;
- venue and physical-site context;
- race membership and ordering;
- race names and official identifiers;
- scheduled and actual times;
- card or session descriptions;
- abandonment, transfer or rearrangement notices;
- official meeting identifiers where available.

No cross-version merge is authorised merely because two source meeting occurrences share a date and course label.

## Current accepted boundary

This document establishes:

- source meeting occurrence;
- governed source-race-to-meeting assignment;
- optional meeting-session occurrence;
- explicit handling of split cards, transferred races, resumptions and partial abandonments;
- analysis rules for meeting-level aggregation;
- deferral of provider-independent meeting identity.

It does not yet define:

- SQL tables;
- physical key types;
- a complete meeting-reconstruction algorithm;
- source-wide validated session boundaries;
- amendment-history implementation;
- cross-version or cross-provider meeting reconciliation;
- physical database technology.
