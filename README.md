# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

The wider purpose is to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The raw files are excluded from Git because of size, licensing and reproducibility considerations. The supplied `raceform.db` has broader geographical and date coverage than the title suggests, including substantial international racing and records through 27 May 2026.

The governed source contains:

- 1,851,285 runner rows;
- 189,043 reconstructed provisional races;
- 37 source columns;
- no declared primary key, foreign keys, indexes or uniqueness constraints.

The candidate provisional race key is `date + course + off`. The raw SQLite database remains read-only, and source queries use `rowid <> 1`.

## Current status

### Source-field investigation series — Notebooks 00–21

**Status: fully closed.**

The series established source immutability, lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree identity, connection-field governance, and conservative comment-field governance.

Retained governed limits include:

- Notebook 08 preserves the lone unresolved starting-price value `F`;
- Notebook 19 preserves one unresolved authority-dependent transition for `Runninsonofagun (IRE)`;
- Notebook 20 preserves 18 unresolved connection blanks after 28 confirmed supplementations;
- Notebook 21 preserves exact comment text and does not authorise a general narrative parser.

Notebook 11 has a durable source-to-output builder and independent validator for all 189,043 provisional races. The accepted result contains 169,465 resolved and 19,578 unresolved canonical race-time decisions. Unsupported future values or changed populations fail closed for investigation.

### Participant identity programme — consolidated Notebook 22

**Status: fully closed.**

Notebook 22 established a conservative identity layer for jockey, trainer and owner labels while preserving raw source values, row lineage and unresolved relationships.

Governed outcomes:

- 7,917 jockey labels;
- 212 jockey candidate groups and 216 candidate relationships;
- one confirmed provisional jockey label identity: `Mlle Marie Velon` / `Mme Marie Velon`;
- one confirmed distinct-person jockey relationship: `Miss B ONeill` / `Mr B ONeill`;
- 214 jockey relationships retained unresolved;
- two direct jockey label mappings to `JOCKEY-PROVISIONAL-0001`;
- 26 bounded provisional trainer transitions covering 52 labels and 6,350 rows;
- 936 owner token-multiset candidate groups;
- 41 same-race-supported provisional ownership compositions covering 95 labels and 9,788 rows;
- 895 owner groups retained unresolved.

The owner-identity scope originally scheduled as Notebook 23 was completed inside Notebook 22, so no separate Notebook 23 is required.

### Targeted cross-notebook implementation audit

**Status: completed on 5 August 2026.**

The audit found and repaired bounded implementation defects involving stale closeout records, provenance enforcement, missing usable outputs, exact decision closure, correction lineage, source-wide validators, an obsolete construction utility and canonical race-time regeneration.

Every repair unit was reviewed individually before integration. The accepted content was consolidated on `audit/retrospective-implementation-integration` and then passed the final integrated gate.

## Validation history

The end-of-source-field-series validation on 4 August 2026 passed:

```text
256 passed in 0.96s
ALL 26 THEN-DISCOVERED VALIDATORS PASSED
```

The final integrated audit validation on 5 August 2026 passed:

```text
282 passed in 1.52s
ALL 28 VALIDATORS PASSED
```

The 28-validator sweep covered every current `scripts/validate_*.py` file, including complete immutable-source checks, governed-reference closure, source-to-output reconciliation and the accepted Notebook 11 canonical race-time output.

No genuine integration defect was found by the final sweep.

The field-governance registers remain reconciled to:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 source fields require raw preservation and match the SQLite names, order and declared types.

## Database admission rule

Every future database load is governed by `docs/DATABASE_IMPORT_VALIDATION_GATE.md`.

> No validated output, no database write. No partial success. The last known-good database remains intact.

Candidate outputs must be built away from the live database, validated source-wide, persisted and read back, loaded transactionally into temporary or replacement structures, and validated again after load. Unknown or changed cases must fail closed, remain explicitly unresolved or be quarantined; they must never be silently guessed or partially loaded.

## Durable project controls

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `docs/CROSS_NOTEBOOK_IMPLEMENTATION_COMPLETENESS_AUDIT.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/DATABASE_IMPORT_VALIDATION_GATE.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_11_CLOSEOUT.md`;
- `docs/NOTEBOOK_22_CLOSEOUT.md`;
- `docs/PARTICIPANT_IDENTITY_INTEGRATION.md`.

## Next bounded action

Proceed to Phase 3 entity and key design. Consolidate the governed race, runner, horse-occurrence, participant and ownership identity requirements before selecting or building the physical target database.

No further source-field notebook investigation is required unless a new source snapshot or failed validator produces concrete new evidence.

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
10. produce the report and lessons learned;
11. update the audit register, field governance, README and project plan;
12. commit and verify the complete closeout.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.
