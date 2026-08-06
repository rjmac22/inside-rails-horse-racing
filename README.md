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

**Status: fully closed.**

The series established source immutability, lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree identity, connection-field governance, and conservative comment-field governance.

Retained governed limits include:

- Notebook 08 preserves the lone unresolved starting-price value `F`;
- Notebook 19 preserves one unresolved authority-dependent transition for `Runninsonofagun (IRE)`;
- Notebook 20 preserves 18 unresolved connection blanks after 28 confirmed supplementations;
- Notebook 21 preserves exact comment text and does not authorise a general narrative parser.

Notebook 11 has a durable source-to-output builder and independent validator for all 189,043 source race occurrences. The accepted result contains 169,465 resolved and 19,578 unresolved canonical race-time decisions.

### Participant identity programme — consolidated Notebook 22

**Status: fully closed.**

Notebook 22 established a conservative identity layer for jockey, trainer and owner labels while preserving raw source values, row lineage and unresolved relationships.

The owner-identity scope originally scheduled as Notebook 23 was completed inside Notebook 22, so no separate Notebook 23 is required.

### Targeted cross-notebook implementation audit

**Status: completed on 5 August 2026.**

The audit repaired bounded implementation defects involving stale closeout records, provenance enforcement, missing usable outputs, exact decision closure, correction lineage, source-wide validators, an obsolete construction utility and canonical race-time regeneration.

Final integrated evidence:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

### Minimum stable core and physical database candidate

**Status: complete through independently validated disposable candidate on 6 August 2026. No database release has been accepted.**

The project now has SQLite schema version 1 implementing the authorised minimum structural core:

- a complete immutable raw mirror;
- deterministic source, race and runner identifiers;
- 189,043 source race occurrences;
- 1,851,285 runner participations;
- governance method and release records;
- import manifest and validation-result structures;
- STRICT tables, foreign keys, indexes and protective triggers;
- durable fail-closed construction and cleanup;
- complete builder readback;
- a separate source-wide independent validator.

Generated candidate:

```text
path: data/processed/database/candidates/raceform_v1_minimum_core_candidate.sqlite3
size: 1,730,048,000 bytes
SHA-256: 7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2
manifest status: built
release accepted: false
```

Independent validation checked:

```text
1,851,286 raw records
68,497,582 raw values
68,497,582 SQLite storage classes
189,043 race codes, groupings and runner counts
1,851,285 runner codes and source-row links
```

The final bounded database gate passed:

```text
72 passed in 14.54s
```

The candidate remains ignored generated output. It is not installed as a live database and has not been promoted or marked `release_accepted`.

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

## Durable project controls

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT_PHASE_4_ADDENDUM.md`;
- `docs/CROSS_NOTEBOOK_IMPLEMENTATION_COMPLETENESS_AUDIT.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/PHASE_4_MINIMUM_CORE_LESSONS_LEARNED.md`;
- `docs/PHASE_4_RAW_MIRROR_CANDIDATE_EVIDENCE.md`;
- `docs/PHASE_4_CORE_STRUCTURE_PROTOTYPE_EVIDENCE.md`;
- `docs/PHASE_4_MINIMUM_CORE_CANDIDATE_EVIDENCE.md`.

## Next bounded action

Define the release-acceptance and promotion boundary for the validated minimum-core candidate.

That work must remain separate from the completed candidate build and must cover project acceptance evidence, active-release resolution, atomic promotion or replacement, prior-release preservation, rollback behaviour and the final accepted database location.

No branch movement, merge or database promotion should occur without explicit review and acceptance.

Only after release acceptance should governed field-level and identity-aware analytical structures be added to the minimum core.

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
