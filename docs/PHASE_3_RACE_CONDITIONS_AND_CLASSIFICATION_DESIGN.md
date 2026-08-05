# Phase 3 Race Conditions and Classification Design

## Purpose

This document records the reviewed conceptual design for race conditions, classification and going in Phase 3.

It is deliberately conceptual. It does not define SQL tables, physical key types, indexes, database technology or implementation order.

The design separates four questions that must not be collapsed:

1. What did the source say about this individual race?
2. What governed interpretation can the project support for that race?
3. Which races are materially comparable for a stated analytical purpose?
4. Is the race an edition of a recurring race series?

A positive answer to one question does not determine the others.

## Governing principle

> Race identity, recurring-series identity and race-conditions equivalence are separate governed questions.

Two unrelated races may have materially equivalent conditions. Two editions of the same recurring race series may have materially different conditions.

## 1. Raw race-condition assertions

### Grain

One exact source-presented race-level value or condition-bearing text attached to one source race occurrence through its supporting source records.

### Status

Immutable source evidence.

### Scope

The current source includes race-level fields and text that may bear on conditions or classification, including where populated:

- race type or code;
- class or grade-style labels;
- source-presented distance;
- going;
- race name and condition-bearing title text;
- handicap or non-handicap indicators where supplied or inferable only through later governed interpretation;
- age, sex, novice, maiden, claiming, selling, amateur, apprentice or other eligibility wording where present;
- obstacle, surface or course-code implications where present;
- any other source field later shown by a dedicated study to encode race conditions.

This list describes the conceptual scope. It does not authorise assumptions about fields that have not yet been investigated.

### Required lineage

Every raw condition assertion must retain a route to:

- source provider;
- source product;
- exact source version;
- source relation;
- source record or supporting source records;
- source race occurrence;
- exact field name or text location;
- exact raw value and original storage state.

### Accepted rules

- Raw race-condition values remain unchanged.
- Textual normalisation must not replace the source value.
- Blank, malformed, conflicting and unparsed values remain explicit.
- Repeated race-level values across runner rows remain source evidence even where the governed race occurrence stores one reconciled interpretation.
- A raw condition value is not automatically a governed classification.

## 2. Governed race-condition interpretation

### Grain

One governed interpretation of the material race conditions attached to one source race occurrence under one accepted governance release.

### Status

Governed interpretation, not immutable source fact.

### Candidate identity

Source race occurrence plus governance release, supported by an independent technical identifier if required by the later physical design.

### Required content

A governed interpretation may include only attributes supported by completed investigations and accepted evidence, such as:

- racing code or broad race type;
- surface or obstacle context;
- governed distance and distance unit;
- class, grade, group or level interpretation;
- handicap status;
- eligibility restrictions;
- age restrictions;
- sex restrictions;
- novice, maiden, claiming, selling, amateur, apprentice or similar status;
- weight or rating-band conditions where established;
- field-size or entry-condition context where established;
- other material conditions supported by a dedicated source-field study;
- resolution status, confidence and evidence for each governed attribute.

### Partial resolution

Resolution is field-specific.

A race may have:

- resolved racing code but unresolved class;
- resolved distance but ambiguous eligibility wording;
- resolved handicap status but incomplete weight-condition detail;
- resolved venue and surface but unresolved exact configuration;
- resolved going label but uncertain observation time or spatial scope.

The model must not require all condition attributes to be known before any supported attribute can be used.

### Accepted rules

- Governed interpretations attach to the individual source race occurrence.
- Each interpreted attribute retains its method, evidence, status and governance release.
- Unsupported detail remains unresolved rather than being inferred for convenience.
- Later corrections must preserve earlier accepted states rather than silently overwriting them.
- Recurring race-series membership does not supply missing edition-level conditions automatically.

## 3. Race-conditions profile

### Grain

One governed analytical profile representing a defined set of materially comparable race conditions for a stated purpose.

### Status

Optional governed analytical construct.

### Candidate identity

Independent project-assigned technical identifier.

### Purpose

A race-conditions profile allows races to be grouped for comparison without claiming that they are the same race or the same recurring series.

Examples of possible profile purposes include:

- broad class-and-code comparison;
- handicap versus non-handicap analysis;
- novice or maiden comparison;
- age-restricted race comparison;
- distance-band analysis;
- surface-and-obstacle comparison;
- a deliberately narrow eligibility-and-weight-condition study.

The exact profile dimensions must be declared by the study that creates or uses the profile.

### Required metadata

Each profile must state:

- analytical purpose;
- included condition dimensions;
- excluded dimensions;
- permitted tolerances or bins;
- treatment of unresolved attributes;
- effective governance release;
- evidence and rule version;
- whether the profile is broad, narrow or study-specific.

### Accepted rules

- Matching profiles do not establish race identity.
- Matching profiles do not establish recurring-series continuity.
- Different profiles may group the same races differently because materiality depends on the analytical question.
- Profiles must not conceal unresolved condition attributes.
- A profile may be retired or superseded while remaining historically reconstructable.

## 4. Source-race-to-conditions-profile assignment

### Grain

One governed assignment of one source race occurrence to one race-conditions profile under one accepted governance release and analytical purpose.

### Status

Governed relationship, not immutable source fact.

### Candidate identity

Source race occurrence plus profile plus governance release, supported by an independent relationship identifier if required by the later physical design.

### Required lineage

The assignment must retain:

- source race occurrence;
- governed race-condition interpretation;
- target conditions profile;
- analytical purpose;
- assignment method;
- included and excluded attributes;
- status and confidence;
- unresolved conditions;
- governance and rule versions.

### Accepted rules

- A source race occurrence may belong to several profiles for different analytical purposes.
- A source race occurrence may remain unassigned where evidence is insufficient.
- Profile assignment must not overwrite edition-level conditions.
- Profile assignment must not imply that two assigned races are the same race.

## 5. Recurring race series and edition conditions

A recurring race series and the conditions of each running remain separate.

### Accepted treatment

- Every edition preserves its own source-presented and governed conditions.
- Series membership does not imply unchanged distance, class, eligibility, handicap status, venue, surface or configuration.
- A sponsorship or title change may leave series identity unchanged while edition conditions remain separately recorded.
- A material conditions change does not automatically end series continuity.
- A continuing title does not automatically preserve series continuity.
- Series-level analysis must report material condition changes across editions.

### Example structure

```text
Recurring race series
  ├── edition A: conditions interpretation A
  ├── edition B: conditions interpretation B
  └── edition C: conditions interpretation C
```

The series groups historical editions only where continuity has been governed. It does not replace their individual conditions.

## 6. Going as time-specific condition evidence

### Grain

One source-presented or externally observed description of ground or surface condition applying to a stated race, meeting, course area and time context.

### Status

Raw going is source evidence. Any harmonised, corrected, spatially assigned or temporally interpreted going is a governed interpretation.

### Accepted rules

- Going is not a permanent property of a racecourse venue.
- Going is not a permanent property of a physical site.
- Going is not a permanent property of a course configuration.
- Going is not a permanent property of a recurring race series.
- Going may vary within a meeting, between course areas, during the day and after weather or maintenance changes.
- One meeting-level label must not automatically be assumed to describe every race or every course section equally.
- Raw going labels remain unchanged even where a governed category or comparison scale is later applied.

### Required context for later governed going work

Where evidence exists, a governed going interpretation should retain:

- exact raw label;
- source and source version;
- applicable race or meeting;
- venue, physical site and configuration context;
- observation or publication time where known;
- effective period where known;
- spatial scope where known;
- weather and maintenance evidence where later introduced;
- harmonisation method;
- resolution status and confidence.

### Weather comparison boundary

Future weather-versus-going studies must compare weather observations to the relevant physical site, course area and time window. They must not assume that a course name alone provides sufficient spatial or temporal identity.

## 7. Classification systems and historical change

Class, grade, group and related systems may vary by:

- jurisdiction;
- racing code;
- authority;
- historical period;
- source product;
- race type;
- later rule changes.

### Accepted rules

- Raw classification labels remain preserved.
- A governed classification must identify its jurisdictional and temporal reference system.
- Identical numeric or textual class labels across jurisdictions or eras are not automatically equivalent.
- Conversion into a common analytical scale requires a separate validated study.
- A common scale, if created, remains an analytical interpretation rather than a replacement for the original classification.
- Unknown historical rule changes must be represented as uncertainty, not silently normalised away.

## 8. Distance and material comparability

Distance is an edition-level condition and may require separate governed treatment.

### Accepted rules

- Raw distance remains immutable source evidence.
- Parsed or standardised distance retains the original value, unit, method and confidence.
- Advertised distance, measured distance and effective racing distance must not be assumed identical.
- Rail movements, configuration changes or jurisdictional conventions may affect comparability.
- Distance bands are analytical profiles, not race identities.
- Two editions of one race series may remain linked despite distance changes.

## 9. Eligibility and restriction parsing

Eligibility rules may be encoded in structured fields, title text or abbreviations.

### Accepted rules

- No condition-bearing title text is discarded merely because structured parsing is available.
- Automated parsing may propose candidate interpretations but does not become accepted without validation.
- Age, sex, novice, maiden, claiming, selling, amateur, apprentice and related restrictions remain separate attributes where evidence supports them.
- Composite or unusual conditions may remain as preserved governed text where safe decomposition is not yet possible.
- Absence of a parsed restriction does not prove that no restriction existed.

## 10. Analysis disclosure requirements

Any analysis using race conditions or classification must state:

- the source version and governed release used;
- the condition dimensions included;
- the dimensions excluded or unavailable;
- how unresolved values were handled;
- whether raw labels, governed interpretations or conditions profiles were used;
- the jurisdictional and historical scope of any class or grade comparisons;
- the distance treatment;
- the going treatment and its temporal or spatial limitations;
- whether recurring race editions were pooled despite condition changes.

## 11. Admission rules for future condition studies

A new governed condition attribute or profile may enter the database only after:

- source meaning has been investigated;
- raw evidence remains preserved;
- parsing and interpretation rules are documented;
- edge cases and unresolved values are explicit;
- focused tests exist where reusable implementation is introduced;
- a source-wide validator exists where appropriate;
- persisted outputs are reloaded and checked;
- counts reconcile to the governed source population;
- provenance and governance release are recorded;
- the permitted database action is stated.

Partial or failed processing must not create partially accepted condition assignments.

## 12. Current design boundary

This document establishes:

- immutable raw race-condition assertions;
- governed per-race condition interpretations;
- optional analytical race-conditions profiles;
- governed race-to-profile assignments;
- separation of series identity from edition conditions;
- going as time-specific and spatially bounded evidence;
- jurisdictional and historical classification safeguards;
- disclosure requirements for conditions-based analysis.

It does not yet define:

- SQL tables;
- physical key types;
- the final list of governed condition attributes;
- a universal class or grade conversion scale;
- a universal going scale;
- complete historical eligibility-rule parsing;
- measured or effective race-distance reconstruction;
- weather-data provider design;
- amendment-history implementation;
- physical database technology.

Those details require later bounded investigations and design decisions.
