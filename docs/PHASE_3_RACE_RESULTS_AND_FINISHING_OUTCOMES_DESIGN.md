# Phase 3 Race Results and Finishing Outcomes Design

## Purpose

This document records the reviewed conceptual design for race results, runner outcomes, finishing order, official classification, non-completions, non-runners, dead-heats and later result amendments.

It is deliberately conceptual. It does not define SQL tables, physical data types, indexes or database technology.

The governing principles are:

- preserve every raw result value exactly as supplied;
- distinguish runner participation from what happened after the start;
- distinguish physical finishing outcome from official classified result;
- represent non-completions and non-runners as typed outcomes rather than invented numerical places;
- preserve dead-heats explicitly;
- preserve void, abandoned and otherwise non-standard race outcomes;
- treat later official amendments as new governed result states rather than silent overwrites;
- validate the accepted result as one coherent race-level state.

## Core design rule

Runner participation, physical finishing outcome and official classified result are related but separate concepts.

A runner record establishes that a horse was represented as participating in one source race occurrence. It does not by itself establish that the horse started, completed, crossed the line in a particular order or retained that order in the official result.

The raw source values remain immutable evidence. Governed result interpretation is attached separately and must retain its method, evidence, status and governance release.

## Conceptual layers

### 1. Raw runner-result assertion

**Grain:** The complete set of exact source-presented result values carried by one source record and inherited by its runner record.

**Status:** Immutable source assertion.

**Candidate identifier:** Supporting source record and the relevant source fields. No official finishing identity is derived directly from parsed text or numbers.

**Identifier scope:** Source-record-scoped.

**Required lineage and evidence:**

- source provider, product and exact source version;
- source relation and source record;
- runner record;
- every raw finishing, position, distance, status and result-related value unchanged;
- null, blank, malformed and unusual source storage states;
- any raw race-level result or status values required to interpret the runner outcome.

**Known uncertainty:** A displayed numerical position may represent physical order, official classification, a dead-heat place or an amended result depending on the source. A blank or textual code may mean non-runner, non-completion, missing data or an unclassified outcome.

**Expected relationships:**

- every current runner record retains its raw runner-result assertion;
- one raw assertion may support one or more candidate governed interpretations;
- one accepted governed interpretation may be assigned within one result-governance release;
- later evidence never replaces the raw assertion.

**Accepted rules:**

- raw position and result values are evidence, not permanent governed facts;
- parsing must not convert an unusual outcome into an ordinary numerical position merely to simplify analysis;
- source blanks remain distinguishable from confirmed non-runners, confirmed non-completions and unresolved values.

### 2. Governed runner participation status

**Grain:** One governed statement about whether one runner record took part in the race under one accepted result state.

**Status:** Governed interpretation.

**Candidate identifier:** Runner record plus result-state version, supported by an independent technical relationship identifier if required by the later physical design.

**Identifier scope:** Result-state-scoped.

**Expected participation statuses include:**

- declared or represented in the source card;
- started;
- did not start;
- withdrawn;
- reserve not admitted;
- race did not take place for that runner because the race was void or abandoned before a valid start;
- unresolved.

The final controlled vocabulary must be derived from validated source semantics and racing-jurisdiction rules rather than invented during schema implementation.

**Required lineage and evidence:**

- runner record and raw result assertion;
- source race occurrence;
- source and external evidence used to determine participation;
- decision method;
- result-state version;
- resolution status and confidence;
- amendment provenance where later evidence changes the accepted status.

**Known uncertainty:** A runner may appear in a result source but not have started. A source may also omit or inconsistently encode withdrawn runners.

**Accepted rules:**

- non-runners are not assigned finishing positions;
- participation status must be established before completion or classification logic is applied;
- unresolved participation remains explicit and is not silently treated as a starter or non-runner.

### 3. Governed physical finishing outcome

**Grain:** One governed interpretation of what physically happened to one starter during and at the end of one race.

**Status:** Governed race outcome.

**Candidate identifier:** Runner record plus result-state version.

**Identifier scope:** Result-state-scoped.

**Expected physical outcome families include:**

- completed and crossed the finish;
- fell;
- unseated rider;
- pulled up;
- refused;
- ran out;
- brought down;
- slipped or otherwise lost rider where separately supported;
- dismounted or stopped under a jurisdiction-specific code;
- completed but physical order unresolved;
- race void or no valid finishing outcome;
- another validated non-completion status;
- unresolved.

The detailed vocabulary and mappings require a source-field study. Similar abbreviations must not be assumed equivalent across jurisdictions or periods without validation.

**Required lineage and evidence:**

- runner record and participation status;
- raw source codes and values;
- interpreted physical outcome family;
- completion indicator where supported;
- physical crossing-order information where supported;
- decision method and evidence;
- governance release, confidence and resolution status.

**Known uncertainty:** Some sources primarily record official classification rather than physical crossing order. A disqualified horse may have completed physically but have no retained official place.

**Accepted rules:**

- a non-completion code is not a numerical finishing position;
- physical completion and official classification remain separate;
- the database must permit a horse to have crossed the line while later being disqualified, demoted or otherwise reclassified;
- unresolved codes remain unresolved rather than being forced into a catch-all completed or non-completed category.

### 4. Physical finishing-order placement

**Grain:** One governed physical crossing-order placement for one completing runner under one accepted result state, where the evidence supports physical order.

**Status:** Optional governed interpretation.

**Candidate identifier:** Runner record plus result-state version.

**Identifier scope:** Result-state-scoped.

**Required lineage and evidence:**

- source race occurrence;
- runner record;
- completed physical outcome;
- raw position and distance evidence;
- crossing-order rank where supported;
- dead-heat or shared-rank status where supported;
- decision method and confidence;
- unresolved or conflicting source evidence.

**Known uncertainty:** The source may expose only official places, not physical crossing order. In such cases, physical order must remain unavailable rather than copied from official classification without evidence.

**Accepted rules:**

- physical rank is optional and evidence-dependent;
- tied physical positions remain tied;
- rank values are not forced into a unique sequence where a dead-heat occurred;
- a horse that did not complete cannot receive a physical finishing rank.

### 5. Official classified result

**Grain:** One official or source-governed classification of one runner under one accepted race result state.

**Status:** Governed classification.

**Candidate identifier:** Runner record plus result-state version.

**Identifier scope:** Result-state-scoped.

**Required lineage and evidence:**

- runner record;
- raw source classification or position evidence;
- physical finishing outcome where available;
- classified place where applicable;
- classified status where no numerical place applies;
- dead-heat status;
- promotion, demotion or disqualification information;
- source authority and evidence date where externally confirmed;
- result-state version and amendment basis;
- confidence and resolution status.

**Known uncertainty:** The current source may not always distinguish an original result from a later amended official result. The project must not claim official amendment history unless supporting evidence exists.

**Accepted rules:**

- official classified place is separate from physical crossing order;
- a disqualified or demoted runner may retain a physical outcome while receiving a different official classification;
- no numerical place is invented for unclassified outcomes;
- one accepted result state may contain shared official places through a dead-heat;
- raw source values remain preserved after classification.

### 6. Dead-heat group

**Grain:** One governed group of two or more runners sharing the same supported physical or official place in one race result state.

**Status:** Governed race-result relationship.

**Candidate identifier:** Independent technical identifier scoped to one result state and result dimension.

**Identifier scope:** Race-result-state-scoped.

**Required lineage and evidence:**

- source race occurrence and result state;
- member runner records;
- shared rank or classified place;
- whether the tie applies to physical order, official classification or both;
- raw evidence and decision method;
- confidence and resolution status.

**Known uncertainty:** A source may encode shared places inconsistently or only imply a dead-heat through repeated positions or distances.

**Accepted rules:**

- repeated place numbers are not automatically accepted as a dead-heat without validated source semantics;
- confirmed dead-heats remain shared outcomes and are not rewritten into arbitrary sequential ranks;
- a dead-heat relationship is result-state-specific and may be affected by later official amendment.

### 7. Beaten-distance assertion and governed margin

**Grain:** One raw or governed statement about the distance between one runner and another relevant placing reference in one race result state.

**Status:** Raw source evidence plus optional governed interpretation.

**Candidate identifier:** Runner record, source field and result-state version, depending on the layer.

**Identifier scope:** Runner-result-scoped.

**Required lineage and evidence:**

- exact raw distance text or number;
- source semantics for whether the value is from the winner, previous finisher or another reference;
- unit or categorical term;
- parsed governed value where supported;
- dead-heat and non-completion context;
- decision method, confidence and unresolved state.

**Known uncertainty:** Racing sources can encode margins using categorical terms, fractions, accumulated distances or distances from the immediately preceding runner. The semantics must be studied before aggregation.

**Accepted rules:**

- raw beaten-distance values remain unchanged;
- no numeric conversion is authorised until the source semantics and unit family are validated;
- distances for non-completers are not treated as ordinary beaten margins;
- dead-heat margins must remain consistent with shared positions.

### 8. Race result state

**Grain:** One coherent governed version of the complete result for one source race occurrence.

**Status:** Versioned governed race-level state.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Source-race-occurrence-and-governance-release-scoped.

**Required lineage and evidence:**

- source race occurrence;
- every runner record represented in the state;
- participation, physical outcome and official classification for each runner;
- race-level status;
- source version and evidence set;
- governance code and reference-data release;
- created, reviewed and accepted dates;
- predecessor result state where amended;
- amendment reason and authority;
- validation evidence and unresolved-case counts.

**Expected race-level statuses include:**

- completed with an accepted result;
- completed but result partially unresolved;
- void;
- abandoned before a valid result;
- partially run or another exceptional jurisdiction-specific state;
- unresolved.

The controlled vocabulary must be established through a bounded field study.

**Expected relationships:**

- one source race occurrence may have several historical governed result states over time;
- at most one result state is current and accepted for a stated governance release;
- every accepted runner outcome belongs to exactly one result state;
- an amended state points to its predecessor rather than overwriting it.

**Accepted rules:**

- later corrections create a new governed result state;
- historical accepted states remain reconstructable;
- a race-level result must be validated as a coherent whole rather than as unrelated runner rows;
- unresolved runners or race status are disclosed at state level.

### 9. Result-state amendment

**Grain:** One governed transition from an earlier race result state to a later state.

**Status:** Governed history and provenance.

**Candidate identifier:** Independent project-assigned technical identifier.

**Identifier scope:** Project-wide, connecting two states for the same source race occurrence or later reconciled real-world race.

**Required lineage and evidence:**

- prior result state;
- successor result state;
- amendment type;
- affected runner records and fields;
- old and new governed values;
- authority or evidence source;
- effective or published date where known;
- decision method, reviewer and governance release;
- confidence and unresolved points.

**Possible amendment families include:**

- corrected source parsing;
- official enquiry result;
- promotion or demotion;
- disqualification;
- reinstatement;
- correction of runner participation status;
- correction of a dead-heat or place;
- correction of race-level void or abandonment status;
- another validated amendment type.

**Accepted rules:**

- amendments are append-only governed history;
- a new state never destroys the source evidence or prior state;
- corrections to project logic and corrections issued by a racing authority remain distinguishable.

## Result reconciliation rules

An accepted race result state must satisfy the following conceptual checks where applicable:

1. Every runner record in the source race occurrence is represented exactly once in the result state.
2. Every runner has exactly one accepted participation status.
3. Only confirmed starters can receive physical race outcomes.
4. Only completing starters can receive a physical finishing-order placement.
5. Non-runners, withdrawals and reserves not admitted receive no finishing place.
6. Non-completion outcomes receive no invented numerical finishing place.
7. A classified numerical place must be compatible with the accepted official result status.
8. Shared physical or classified places must be supported by an explicit dead-heat relationship.
9. The result can contain no contradictory active classifications for the same runner.
10. The number and identity of winners must be consistent with dead-heat and race-status rules.
11. Void or abandoned race states must not expose ordinary winning and placing outcomes unless the jurisdiction-specific evidence explicitly requires another treatment.
12. Every governed value must retain lineage to source evidence, external evidence or a documented derivation.
13. Unresolved cases must be counted and retained rather than silently dropped.

These are conceptual invariants. Exact validator logic depends on the source-field semantics established by the later result study.

## Analytical use rules

### Winner and placing analysis

Winner or placing analysis must use the accepted official classification for a declared governance release, not an unexamined raw position field.

The analysis must disclose:

- whether official classification or physical crossing order is used;
- treatment of dead-heats;
- treatment of disqualifications and amendments;
- treatment of non-runners and non-completers;
- unresolved and excluded results;
- result-governance release.

### Completion and jumping-outcome analysis

Studies of falls, pull-ups, refusals or other non-completions must use governed typed outcomes. Source abbreviations must not be pooled until their semantics are validated.

### Beaten-distance analysis

Beaten-distance analysis must declare:

- the source semantics of the margin field;
- whether margins are cumulative or sequential;
- units and categorical conversions;
- treatment of dead-heats, non-completers and extreme values;
- unresolved or non-comparable jurisdictions.

### Result changes over time

Where amendment history exists, analysis must state whether it uses:

- the source-presented result;
- the latest accepted governed result;
- the result known as of a specified date;
- physical crossing order;
- official final classification.

## Admission requirements for the result layer

Before result data is admitted to the analytical database as governed outputs, the result implementation must have:

- a bounded field-semantics study;
- explicit raw-value inventories and edge-case examples;
- validated controlled vocabularies for participation, completion and classification statuses;
- persisted outputs reloaded independently;
- reusable implementation outside the exploratory notebook;
- focused unit tests;
- an independent source-wide validator;
- race-level reconciliation checks;
- unresolved-case and quarantine reporting;
- provenance for external corrections or official amendments;
- documentation of analytical limitations;
- an accepted governance release identifier.

A partial or failed result build must not be admitted as the accepted result state.

## Current accepted design boundary

This design establishes:

- immutable raw runner-result assertions;
- governed participation status;
- governed physical finishing outcomes;
- optional physical finishing order;
- separate official classified results;
- explicit dead-heat relationships;
- raw and governed beaten-distance evidence;
- versioned race result states;
- append-only result amendments;
- race-level reconciliation and analytical disclosure rules.

It does not yet define:

- SQL tables;
- physical key types;
- exact source field mappings;
- final controlled vocabularies;
- jurisdiction-specific official result rules;
- numerical margin parsing or unit conversion;
- complete historical amendment coverage;
- provider-independent real-world race result identity;
- physical database technology.

Those decisions require a later bounded result-field study and physical-schema design.