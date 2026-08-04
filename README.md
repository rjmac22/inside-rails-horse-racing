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

### Participant identity programme — consolidated Notebook 22

**Status: implementation complete; final strengthened-validator run pending.**

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

Focused test evidence on 4 August 2026:

```text
14 passed in 0.61s
```

The earlier source-wide validator version passed on 4 August 2026:

```text
jockeys: 7,917 labels; 212 groups; 216 candidate relationships
trainers: 10,708 labels; 26 accepted groups; 6,350 mapped rows
owners: 98,234 labels; 41 accepted groups; 9,788 mapped rows; 895 unresolved groups
participant identity validation: PASS
```

The final closeout audit added a direct jockey mapping file and strengthened the validator to enforce exact jockey candidate closure, the one accepted relationship, the one distinct-person decision, all 214 unresolved relationships, decisive external provenance and the exact two-row mapping. One fresh local PASS from that strengthened validator remains required before Notebook 22 returns to fully closed status.

## End-of-source-field-series validation

Final local validation after Notebook 21 on 4 August 2026:

```text
256 passed in 0.96s
```

All 26 then-discovered `scripts/validate_*.py` validators passed, including complete source-wide checks over the immutable 1,851,285-row population.

The sweep found and repaired two integration defects:

- a sub-minor-unit Great Britain prize value fell through to `currency_unresolved` instead of `invalid`;
- the source-field loader did not yet allow the explicit later-notebook pending-validation status.

The field-governance registers were then reconciled. Final status totals are:

```text
closed: 34
implemented_with_governed_anomaly: 1
preserve: 2
```

All 37 source fields require raw preservation and match the SQLite names, order and declared types.

A new full repository suite and all-validator sweep remain deferred until the next appropriate end-of-series or repair-branch gate.

## Durable project controls

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_22_CLOSEOUT.md`;
- `docs/PARTICIPANT_IDENTITY_INTEGRATION.md`.

## Next bounded action

Run `python scripts/validate_participant_identity.py` once against the immutable local source and record the strengthened validator PASS.

After that validation gate, complete the mandatory Notebook 19 authority-response gate. Once both gates are recorded, proceed to entity and key design using the governed race, runner, horse, jockey, trainer and ownership identity requirements.

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
