# Inside Rails Project Plan

## Objective

Build a documented, reproducible and professionally structured horse-racing analytical database from supplied third-party source products, then use that governed foundation for evidence-led racing studies and reader-facing work.

Profiling and domain interpretation come before cleaning, schema design or predictive modelling. Immutable source evidence is never overwritten merely because a governed correction or enrichment exists.

## Standing method

For each substantive investigation:

1. state one bounded question;
2. declare the source/database and grain under investigation;
3. separate profiling evidence from interpretation;
4. avoid irreversible cleaning decisions inside exploratory work;
5. extract stable reusable plumbing only after it works;
6. add focused unit tests including failure behaviour;
7. validate extracted code and governed references independently;
8. document the database consequence where one exists;
9. produce a concise reader-facing report where applicable;
10. record decisions, uncertainty and lessons learned;
11. update the audit record, project plan and README when the project state changes;
12. commit and verify the complete closeout.

The full notebook procedure is in `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`.

For reader-facing studies, the mandatory pre-study references are:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

## Immutable Source Version 1

Canonical path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Standing rules:

- source file is immutable and read-only;
- all source-data admission uses `rowid <> 1`;
- authorised Source Version 1 race identity is exact raw `date + course + off`;
- physical source rows: **1,851,286**;
- admitted runner-bearing rows: **1,851,285**;
- source race occurrences: **189,043**;
- source columns: **37**;
- source SHA-256: `77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7`.

## Database admission gate

Every staging, core or analytical database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

The standing rule is:

> No validated output, no database write. No partial success. The last known-good database remains intact.

The complete repository test suite and all applicable independent validators form the minimum project-level gate. The canonical independent-validator runner is:

```bash
python scripts/run_applicable_validators.py
```

Its exact argument mapping and historical exclusions are governed by `docs/APPLICABLE_VALIDATOR_GATE.md`.

## Phase 1 — Source understanding

### Notebooks 00–03

**Status: fully closed.**

Established raw-source immutability, source grain and quality, physical lineage requirements, and candidate race and runner-record reconstruction.

## Phase 2 — Domain interpretation and source-field governance

### Notebooks 04–21

**Status: fully closed.**

The completed programme governs course and jurisdiction context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, betting-market context, temporal reconstruction, course mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree labels, connection-field blanks and comment-field states.

The raw/parser layer and governed analytical layer are deliberately distinct. For example, Notebook 08's lone raw starting-price value `F` remains parser-unresolved because the raw token contains no numeric price, while later external evidence establishes the Almendares price as `5/2 favourite`; Database v3 now exposes that correction analytically without rewriting the raw token.

Notebook 20 preserves 18 unresolved connection blanks after 28 confirmed supplementations. Notebook 21 does not authorise a general narrative comment parser.

End-of-source-field-series evidence on 4 August 2026:

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

## Participant identity programme

### Consolidated Notebook 22

**Status: fully closed.**

Notebook 22 established a conservative jockey/trainer/owner identity layer while preserving raw labels, source lineage and unresolved relationships.

## Targeted cross-notebook implementation-completeness audit

**Status: fully closed on 5 August 2026.**

The audit repaired stale closeout records, missing governed outputs, provenance enforcement, source-wide validation, correction-lineage gaps, obsolete construction utility code and canonical race-time regeneration.

Final integrated evidence at that boundary:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

## Phase 3 — Minimum stable entity and key design

**Status: completed and evidenced on 6 August 2026.**

Established the bounded minimum stable core required before field-level analytical integration:

- immutable physical source lineage;
- deterministic source-version, relation, record, race and runner codes;
- race occurrences grouped by exact raw `date + course + off`;
- one runner participation per admitted source record;
- explicit governance method/release records;
- import-manifest and validation-result structures;
- fail-closed lifecycle and acceptance-state constraints.

## Phase 4 — Database v1 minimum structural release

**Status: accepted and promoted on 8 August 2026; retained as historical release.**

Canonical retained v1 release:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
size: 1,730,048,000 bytes
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
manifest status: release_accepted
SQLite user_version: 1
```

Historical v1 release evidence remains in the Phase 3/4 documentation and should not be rewritten as though v1 were the current study database.

## Phase 4B — Database v2 governed integration

**Status: accepted and promoted on 9 August 2026; retained as prior release.**

Database v2 integrated Notebook 04–22 governed work into the structural database and exposed the first governed study-facing views.

Retained v2 release:

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
size: 3,137,044,480 bytes
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
manifest status: release_accepted
SQLite user_version: 2
```

Database v2 is preserved for historical reproducibility and rollback. It is no longer the default study database.

## Phase 4C — Database v3 external-verification reconciliation

**Status: fully closed; accepted and promoted on 9 August 2026.**

Database v3 exists because the v2 integration did not make every externally established fact analytically usable. The repair audited the committed Notebook 04–22 evidence and reconciled omitted exact corrections/enrichments without mutating Source Version 1 or Database v2.

Canonical accepted v3 release:

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
size: 3,137,081,344 bytes
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
manifest status: release_accepted
validation-result rows: 7
SQLite application_id: 1230130259
SQLite user_version: 3
quick_check: ok
foreign_key_check rows: 0
```

Accepted governance additions:

```text
existing generic manual-verification rows: 85
new reconciled external-verification rows: 19
total manual-verification rows: 104
typed external-value resolutions: 37
```

Current study-facing reconciled views:

- `view_reconciled_race_occurrences` — **189,043** races;
- `view_reconciled_source_runner_participations` — **1,851,285** source-backed runners;
- `view_reconciled_runner_records` — **1,851,288** combined governed runners.

Exact v3 examples include:

- Almendares raw `F` → governed external `5/2 favourite`;
- Cinnamon Carter raw finish `10` → governed finish `12`;
- externally corrected race runner counts for Ohi, Morioka and the Great Navigator race;
- externally governed beaten-distance correction/invalidation cases;
- Compiegne `5yo+` and Ecstasy age `3`;
- official 1600m enrichments for the two verified race distances;
- three actual-off-time enrichments;
- Pegasus 2018 and Arc 2019 official/candidate local-currency prize-schedule enrichments.

Final acceptance evidence at the promotion implementation head:

```text
focused validator-runner tests: 5 passed in 0.44s
complete repository suite: 412 passed in 18.64s
applicable independent validators: 31 passed
standalone Database v3 validator: passed
```

Promotion repository commit:

`0b535cb5bfdcb22b7693e8a26a82acfcb025529d`

Promotion additionally confirmed candidate immutability, prior v2 preservation, `quick_check=ok`, zero foreign-key errors and seven accepted validation-evidence rows.

Governing documents:

- `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`;
- `docs/DATABASE_V3_RELEASE_ACCEPTANCE_AND_PROMOTION.md`;
- `docs/APPLICABLE_VALIDATOR_GATE.md`.

## Phase 5 — Analytical products and writing

**Status: in progress using accepted Database v3.**

### Study 01 — field size and race predictability

Research question:

> What relationship, if any, exists between field size and the predictability of British horse races?

Established before the database pause:

- 111,634 British races before the walkover exclusion;
- field-size mode 8 and median 9;
- approximately 74.0% of British races have 6–12 runners;
- approximately 89.8% have 5–14 runners;
- 21 one-runner British races were confirmed as genuine walkovers;
- competitive British population: **111,613** races.

The false `Walkover<br><br><br>` diagnostic is closed: Source Version 1 and the accepted database contain `Walkover`; the apparent markup was introduced during rendered-output/copy-paste transport.

The database integration blocker is also closed. Study 01 should resume read-only against Database v3 using the reconciled views documented in `docs/STUDY_DATABASE_REFERENCE.md` and `docs/STUDY_DATA_ACCESS.md`.

The immediate study programme remains question-led rather than schema-led. A study-specific derivation does not automatically belong in the database; only reusable or correctness-critical infrastructure should trigger a database-governance escalation.

## Current study-start rule

Before beginning or resuming a study:

1. read `docs/STUDY_RESEARCH_PLAYBOOK.md`;
2. read `docs/STUDY_DATABASE_REFERENCE.md`;
3. read `docs/STUDY_DATA_ACCESS.md`;
4. read `docs/STUDY_REVISIT_REGISTER.md`;
5. confirm the current accepted release in the canonical database reference;
6. use that exact accepted release read-only;
7. declare the observation grain and chosen race/runner population;
8. use reconciled/governed fields rather than rebuilding database corrections in the study;
9. escalate any new correctness-critical database defect out of the study;
10. record the exact database release and repository commit at study closeout.

As of 9 August 2026, the current accepted study database is **Database v3**.

## Next bounded action

Resume Study 01 against:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Use the v3 reconciled interfaces rather than the superseded v1/v2 study interfaces wherever the relevant fields are exposed.

No further database work is planned before Study 01 resumes unless the study discovers a new correctness-critical defect.
