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

**Status: fully closed on the retrospective implementation branch.**

The series established source immutability, lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price arithmetic, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and numbers, beaten-distance semantics, race classification, runner characteristics, ratings, horse and pedigree identity, connection-field governance, and conservative comment-field governance.

Notebook 08 retains one governed source anomaly: the standalone starting-price value `F` remains unresolved rather than being silently normalised. The source validator passes only when the exact unresolved population remains `{'F': 1}`.

Notebook 19 retains five deliberately unresolved horse/pedigree transitions pending the mandatory authority-response gate. Notebook 20 retains 18 unresolved connection blanks after 28 confirmed supplementations.

Notebook 21 established that substantive `comment` values are generally runner-level English-language descriptions of race position and performance, with strong jurisdiction- and feed-dependent coverage differences. Exact raw text remains preserved; `A`, `B` and `V` remain unresolved; no general narrative parser is authorised.

Notebook 21 baselines:

- 340,394 empty-string comments;
- 1,510,891 populated comments;
- 1,426,745 distinct populated values;
- 238 probable-placeholder or unresolved-code rows;
- 1,510,653 substantive-text rows;
- 0 SQL nulls.

## End-of-series validation

Final local validation on 4 August 2026:

```text
256 passed in 0.96s
```

All 26 discovered `scripts/validate_*.py` validators passed, including complete source-wide checks over the immutable 1,851,285-row population.

The final sweep found and repaired two integration defects:

- a sub-minor-unit Great Britain prize value fell through to `currency_unresolved` instead of `invalid`;
- the source-field loader did not yet allow the explicit later-notebook pending-validation status.

The field-governance registers were then reconciled. Final status totals are:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 source fields require raw preservation and match the SQLite names, order and declared types.

## Durable project controls

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`.

## Next bounded action

Before physical database construction, complete the mandatory Notebook 19 authority-response gate.

The next analytical programme is participant identity:

1. Notebook 22 — jockey and trainer identity;
2. Notebook 23 — owner identity and ownership structures.

Physical participant schema design and participant-level retrospective analysis remain blocked until those identity studies are complete.

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
