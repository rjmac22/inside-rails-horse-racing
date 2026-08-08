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

## Current status

### Source-field investigation series — Notebooks 00–21

**Status: fully closed, with a post-closeout Notebook 19 authority amendment awaiting focused regenerated-output validation.**

The series established source immutability, lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree identity, connection-field governance, and conservative comment-field governance.

Retained governed limits include:

- Notebook 08 preserves the lone unresolved starting-price value `F`;
- Notebook 19 now has zero expected unresolved horse/pedigree transitions after Weatherbys Ireland confirmed on 8 August 2026 that High Society Lady (IRE) is by Society Rock (IRE); `Runninsonofagun (IRE)` therefore uses governed damsire `Society Rock (IRE)` while the competing raw source assertions remain preserved;
- Notebook 20 preserves 18 unresolved connection blanks after 28 confirmed supplementations;
- Notebook 21 preserves exact comment text and does not authorise a general narrative parser.

The Notebook 19 transition baseline changes from the historical 5 August authority state `91 corrected / 261 different horse / 1 unresolved` to an expected `92 / 261 / 0`. The focused tests and independent source-wide validator must regenerate and reload the two processed identity outputs before the amended state is accepted as fully validated.

Notebook 11 has a durable source-to-output builder and independent validator for all 189,043 source race occurrences. The accepted result contains 169,465 resolved and 19,578 unresolved canonical race-time decisions.

### Participant identity programme — consolidated Notebook 22

**Status: fully closed.**

Notebook 22 established a conservative identity layer for jockey, trainer and owner labels while preserving raw source values, row lineage and unresolved relationships.

The owner-identity scope originally scheduled as Notebook 23 was completed inside Notebook 22, so no separate Notebook 23 is required.

### Targeted cross-notebook implementation audit

**Status: completed on 5 August 2026 for the then-governed evidence state.**

The audit repaired bounded implementation defects involving stale closeout records, provenance enforcement, missing usable outputs, exact decision closure, correction lineage, source-wide validators, an obsolete construction utility and canonical race-time regeneration.

Historical integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

The 8 August Notebook 19 Weatherbys Ireland response is a later governed evidence amendment and receives a separate focused validation rather than rewriting that historical gate.

### Minimum stable core and accepted Database v1

**Status: release accepted and promoted on 8 August 2026.**

The project has SQLite schema version 1 implementing the authorised minimum structural core:

- a complete immutable raw mirror;
- deterministic source, race and runner identifiers;
- 189,043 source race occurrences;
- 1,851,285 runner participations;
- governance method and release records;
- import manifest and validation-result structures;
- STRICT tables, foreign keys, indexes and protective triggers;
- durable fail-closed construction and cleanup;
- complete builder readback;
- a separate source-wide independent validator;
- an explicit fail-closed release-acceptance and atomic-promotion boundary.

Preserved validated candidate:

```text
path: data/processed/database/candidates/inside_rails_v1_candidate.sqlite3
size: 1,730,048,000 bytes
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
manifest status: built
```

Accepted Version 1 release:

```text
path: data/processed/database/releases/inside_rails_v1.sqlite3
size: 1,730,048,000 bytes
SHA-256: 2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934
manifest status: release_accepted
validation-result rows: 7
quick_check: ok
foreign_key_check rows: 0
SQLite application_id: 1230130259
SQLite user_version: 1
candidate hash unchanged during promotion: true
```

Independent candidate validation checked:

```text
1,851,286 raw records
68,497,582 raw values
68,497,582 SQLite storage classes
189,043 race codes, groupings and runner counts
1,851,285 runner codes and source-row links
```

The bounded database gate passed:

```text
72 passed in 14.54s
```

The Phase 4 repository-wide technical gate at commit `bf1d7f7b253edaf7232351e33ada92b039ca97ba` passed:

```text
354 passed in 18.28s
ALL 31 VALIDATORS PASSED
```

Release-management implementation then passed:

```text
focused promotion tests: 6 passed in 0.64s
complete repository tests: 360 passed in 15.36s
```

The 31-validator Phase 4 result is prior technical evidence durably associated with the accepted release; promotion did not pretend to rerun that historical sweep.

### Reader-facing Study 01 and Database v2 governed-integration inventory

**Status: in progress.**

The first reader-facing study has established the British race population and field-size distribution and has confirmed that the 21 one-runner British races are genuine walkovers rather than reconstruction errors.

A temporary diagnostic was opened after copied notebook output appeared to show `Walkover<br><br><br>`. That apparent comment-markup defect is now closed:

- Source Version 1 contains zero admitted comments with a literal `<` character;
- the accepted Database v1 Hereford / Queensbury Boy value is exactly `Walkover`;
- the apparent `<br>` markup was introduced during rendered-output / copy-paste transport;
- no comment-cleaning transformation or database change is required.

The durable consequence is recorded in `docs/COMMENT_INFORMATION_INTEGRATION.md`. Study work should not reopen this false comment defect without new stored-data evidence.

Study 01 also exposed that accepted Database v1 deliberately materialised only the minimum structural core while many reusable governed Notebook 04–22 outputs remained external. Notebook 25 is therefore inventorying those outputs before one coherent Database v2 design. Database v1 remains immutable; no v2 schema or database write is authorised until all notebook dispositions and final reconciliation items are explicit.

## Validation history

End of source-field series, 4 August 2026:

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

Final integrated implementation audit, 5 August 2026:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

Final bounded minimum-core gate, 6 August 2026:

```text
72 passed in 14.54s
```

Final Phase 4 repository-wide technical gate, 6 August 2026:

```text
354 passed in 18.28s
ALL 31 VALIDATORS PASSED
```

Release-boundary implementation gate, 8 August 2026:

```text
6 focused promotion tests passed
360 complete repository tests passed
```

Post-authority Notebook 19 focused validation on 8 August 2026 is still pending local execution and processed-output regeneration.

The field-governance registers remain reconciled to:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 source fields require raw preservation and match the SQLite names, order and declared types.

## Database admission rule

Every database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

> No validated output, no database write. No partial success. The last known-good database remains intact.

Candidate outputs must be built away from any live database, validated source-wide, persisted and read back, and accepted through a separate explicit gate. Unknown or changed cases must fail closed, remain explicitly unresolved or be quarantined; they must never be silently guessed or partially loaded.

Accepted Database v1 is consumed read-only from:

`data/processed/database/releases/inside_rails_v1.sqlite3`

## Durable project controls

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT_PHASE_4_ADDENDUM.md`;
- `docs/CROSS_NOTEBOOK_IMPLEMENTATION_COMPLETENESS_AUDIT.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/COMMENT_INFORMATION_INTEGRATION.md`;
- `docs/PHASE_4_MINIMUM_CORE_LESSONS_LEARNED.md`;
- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_FINAL_REPOSITORY_GATE_EVIDENCE.md`;
- `docs/PHASE_4_RELEASE_ACCEPTANCE_AND_PROMOTION_CONTRACT.md`;
- `docs/PHASE_4_RELEASE_ACCEPTANCE_EVIDENCE.md`.

## Next bounded action

Complete the focused Notebook 19 authority-amendment regeneration and validation, then continue the Notebook 25 Database v2 governed-integration inventory before returning immediately to Study 01.

The false comment-markup issue is closed. Study work remains evidence-led: the question comes first, the population and grain are declared, governed field interpretations are respected, and unexpected or null results are valid outcomes.

## Working method

The project follows an evidence-led investigation-to-implementation cycle:

1. profile the raw source without altering it;
2. state one bounded question;
3. test coverage, uniqueness, exceptions and failure modes;
4. inspect material exceptions and preserve unresolved cases explicitly;
5. separate observation, interpretation, confidence and design decision;
6. translate the conclusion into a practical database consequence;
7. implement the rule reversibly while retaining raw values and lineage;
8. extract stable reusable logic into `src/inside_rails/`;
9. add focused tests and independent validation;
10. record evidence, limitations and lessons learned;
11. update the audit record, README and project plan;
12. commit and verify the complete closeout.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.
