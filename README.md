# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained and evidenced.

The wider purpose is to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The raw files are excluded from Git because of size, licensing and reproducibility considerations. The supplied `raceform.db` has broader geographical and date coverage than the title suggests, including substantial international racing and records through 27 May 2026.

Accepted Source Version 1 identity:

```text
SHA-256: 77b5dbbbfdee69d4d92a582655344e1e5ba29ca4646a5999c383de8161eeeaa7
size: 765,825,024 bytes
physical records: 1,851,286
admitted runner records: 1,851,285
retained excluded records: 1
source race occurrences: 189,043
source columns: 37
```

The authorised Source Version 1 race key is exact raw `date + course + off`. The raw SQLite database remains read-only, and source queries use `rowid <> 1`.

## Current accepted analytical database

### Database v3 — accepted 9 August 2026

Canonical study database:

```text
path: data/processed/database/releases/inside_rails_v3.sqlite3
size: 3,137,081,344 bytes
SHA-256: aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0
manifest status: release_accepted
validation-result rows: 7
quick_check: ok
foreign_key_check rows: 0
SQLite application_id: 1230130259
SQLite user_version: 3
```

Database v3 is the current read-only analytical source for reader-facing studies.

It preserves the complete Database v2 structure and adds the external-verification reconciliation layer needed to make previously established external facts analytically usable without altering immutable raw evidence.

Accepted v3 reconciliation population:

```text
manual-verification rows: 104
typed external-value resolutions: 37
race rows: 189,043
source-backed runner rows: 1,851,285
combined governed runner rows: 1,851,288
```

Preferred current study-facing views:

- `view_reconciled_race_occurrences`;
- `view_reconciled_source_runner_participations`;
- `view_reconciled_runner_records`.

Important examples now exposed through governed analytics include:

- Almendares (GB): raw `sp='F'` remains raw/parser-unresolved, while external evidence supplies governed `5/2 favourite`;
- Cinnamon Carter (AUS): governed finishing position `12` rather than raw `10`;
- exact externally verified runner-count corrections for Ohi, Morioka and the Great Navigator race;
- exact/invalidation treatment for the verified beaten-distance anomalies;
- Compiegne `5yo+` and Ecstasy age `3` corrections;
- two official 1600m distance enrichments;
- three actual-off-time enrichments;
- governed Pegasus 2018 and Arc 2019 prize-schedule enrichments.

The parser/source layer is not rewritten to pretend those corrected facts were present in the raw data. Raw lineage remains recoverable.

### Preserved earlier releases

Database v2 remains immutable and retained:

```text
path: data/processed/database/releases/inside_rails_v2.sqlite3
SHA-256: 80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe
```

Database v1 remains immutable and retained:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
```

They are historical release/rollback evidence, not the normal study database.

## Current status

### Source-field investigation series — Notebooks 00–21

**Status: fully closed.**

The series established source immutability, lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree identity, connection-field governance, and conservative comment-field governance.

Important distinction after the v3 reconciliation:

- the lone raw starting-price token `F` remains unresolved by the source parser because no numeric price is present in the raw token;
- external evidence independently established the corresponding Almendares price as `5/2 favourite`, and Database v3 now exposes that governed correction analytically.

Notebook 20 still preserves 18 unresolved connection blanks after 28 confirmed supplementations. Notebook 21 preserves exact comment text and does not authorise a general narrative parser.

### Participant identity programme — consolidated Notebook 22

**Status: fully closed.**

Notebook 22 established a conservative identity layer for jockey, trainer and owner labels while preserving raw source values, row lineage and unresolved relationships.

### Database release programme

- Database v1: minimum structural core, accepted 8 August 2026;
- Database v2: Notebook 04–22 governed integration, accepted 9 August 2026;
- Database v3: external-verification reconciliation repair, accepted 9 August 2026.

Database v3 supersedes v2 for normal analytical use. Prior releases remain immutable.

### Reader-facing Study 01 — field size and race predictability

**Status: in progress and no longer blocked by database integration.**

The first reader-facing study asks:

> What relationship, if any, exists between field size and the predictability of British horse races?

Established before the database pause:

- 111,634 British races before the walkover exclusion;
- field-size mode 8 and median 9;
- approximately 74.0% of British races have 6–12 runners;
- approximately 89.8% have 5–14 runners;
- 21 one-runner British races were inspected and confirmed as genuine walkovers;
- the competitive British population is therefore 111,613 races.

The earlier apparent `Walkover<br><br><br>` defect was a rendered-output/copy-paste artefact, not stored database content.

Study 01 should now resume against accepted Database v3 using the reconciled study-facing views and the canonical study documentation.

## Final Database v3 acceptance evidence

Promotion implementation head:

```text
0b535cb5bfdcb22b7693e8a26a82acfcb025529d
```

Focused canonical-validator-runner tests:

```text
5 passed in 0.44s
```

Complete repository suite:

```text
412 passed in 18.64s
```

Applicable independent-validator gate:

```text
31 validators passed
```

The standalone Database v3 validator then reconfirmed the exact candidate against accepted Database v2 before promotion.

Promotion confirmed:

```text
release_accepted: true
candidate_hash_unchanged: true
prior_release_preserved: true
quick_check: ok
foreign_key_check rows: 0
validation-result rows: 7
```

The exact accepted v3 release SHA-256 is:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

## Database admission rule

Every database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

> No validated output, no database write. No partial success. The last known-good database remains intact.

The complete repository suite and all applicable independent validators are part of the project-level gate. The canonical validator procedure is now permanent:

```bash
python scripts/run_applicable_validators.py
```

Do not reconstruct an ad-hoc shell loop for the validator gate.

## Study database rules

Before every reader-facing study, read:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

The exact current database path, release identity, study-facing views and population semantics are governed by `docs/STUDY_DATABASE_REFERENCE.md` rather than memory.

Normal studies must use accepted Database v3 read-only. There is no silent fallback to Database v2, Database v1, a validated candidate or Source Version 1.

## Durable project controls

See:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/APPLICABLE_VALIDATOR_GATE.md`;
- `docs/DATABASE_USER_GUIDE.md`;
- `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`;
- `docs/DATABASE_V3_RELEASE_ACCEPTANCE_AND_PROMOTION.md`;
- `docs/PROJECT_PLAN.md`.

Historical Phase 3/4 and Database v1/v2 evidence documents remain in the repository as historical records and should not be rewritten to pretend they described Database v3 at the time.

## Next bounded action

Resume reader-facing Study 01 using accepted Database v3 and its reconciled study-facing views.

Study work remains evidence-led: the question comes first, the population and grain are declared, governed field interpretations are respected, and unexpected or null results are valid outcomes.

## Working method

The project follows an evidence-led investigation-to-implementation cycle:

1. profile the relevant governed data without altering immutable evidence;
2. state one bounded question;
3. test coverage, uniqueness, exceptions and failure modes;
4. inspect material exceptions and preserve unresolved cases explicitly;
5. separate observation, interpretation, confidence and design decision;
6. translate any correctness-critical reusable finding into a practical database consequence;
7. implement the rule reversibly while retaining raw values and lineage;
8. extract stable reusable logic into `src/inside_rails/`;
9. add focused tests and independent validation;
10. record evidence, limitations and lessons learned;
11. update the audit record, README and project plan where applicable;
12. commit and verify the complete closeout.
