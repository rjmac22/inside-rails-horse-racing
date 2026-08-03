# Inside Rails: Horse-Racing Database

A notebook-led data-engineering, database-design and racing-research project using historical horse-racing results.

## Project aim

Build a documented, reproducible and professionally structured analytical database from third-party racing data. Source data is preserved unchanged, transformations are tested, and important design decisions are explained in publishable Jupyter notebooks.

The wider purpose is not database construction for its own sake. The project is intended to establish what racing data means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure and produce readable work.

## Data source

Kaggle: *Horse Racing Results UK/Ireland 2015–2025* by deltaromeo.

The raw files are excluded from Git because of size, licensing and reproducibility considerations. The supplied `raceform.db` has broader geographical and date coverage than the title suggests, including substantial international racing and records through 27 May 2026.

The source contains:

- 1,851,285 governed runner rows;
- 189,043 reconstructed provisional races;
- 37 source columns;
- no declared primary key, foreign keys, indexes or uniqueness constraints.

The candidate provisional race key is `date + course + off`. The raw SQLite database remains read-only, and source queries use `DATA_ROW_PREDICATE = "rowid <> 1"`.

## Current status

### Notebooks 00–16

**Status:** complete and retrospectively implemented or fully closed as recorded in the audit register.

These notebooks established source immutability, grain and lineage, race and runner reconstruction, jurisdiction and surface context, result semantics, race-distance and carried-weight parsing, bounded starting-price parsing, temporal reconstruction, course timezone mapping, prize-money semantics, runner counts and runner-number governance, beaten-distance semantics, race classification and eligibility, and complete governance of all 37 source fields.

Notebook 08 retains one deliberate governed source failure: the malformed standalone starting-price value `F` remains unresolved rather than being silently normalised.

### Notebook 17 — Runner characteristics and equipment

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Notebook 17 governed runner age, sex and headgear, including exact verification-backed corrections for two contaminated sex values and source-specific eyecover normalisation.

### Notebook 18 — Ratings semantics and availability

**Status:** fully closed.

Notebook 18 established separate governed meanings for `or`, `rpr` and `ts`, preserved unavailable ratings as null rather than zero, and isolated the exact invalid `rpr = 775` source row without inventing a replacement.

### Notebook 19 — Horse and pedigree identity

**Status:** fully closed as a non-rerunnable archival construction record with durable replacement validation.

Notebook 19 established that raw `horse` is a source label rather than a permanent natural key. The same exact label can refer to different real horses, while one horse can carry inconsistent pedigree assertions.

The source-wide governed result contains:

- 5,573 exact labels with at least one raw populated pedigree contradiction;
- 368 labels retaining contradiction after reversible dam-suffix treatment;
- 350 temporally separated contradictory labels;
- 353 governed transitions;
- 87 `Corrected` transitions;
- 261 `Different horse` transitions;
- 5 `Unresolved` transitions;
- 611 provisional source-internal horse occurrences.

Durable implementation includes the specialist governance reference, reusable code, focused tests, independent validator, database-integration documentation and committed processed outputs.

Before physical database construction, all pending studbook and racing-authority responses must be checked and the affected Notebook 19 governance and outputs regenerated where necessary.

### Notebook 20 — Connections and ownership identity

**Status:** fully closed.

Notebook 20 established that `jockey`, `trainer` and `owner` are source-presented runner-level labels rather than canonical identities for people, partnerships, syndicates, licences or organisations.

Across the governed source population, 46 blank connection-field occurrences affect 44 runner rows:

- 2 blank `jockey` values;
- 9 blank `trainer` values;
- 35 blank `owner` values.

External review produced:

- 28 confirmed source supplementations;
- 5 conflicting-evidence trainer records preserved unresolved;
- 13 insufficient-evidence owner records preserved unresolved.

The raw database remains immutable. Confirmed values are applied only through the exact `(source_rowid, source_field)` governed repair reference, and populated source values can never be overwritten. Raw connection labels remain atomic text and are not treated as global entity identifiers.

Durable implementation includes 46 permanent manual-verification records, a 28-row connection-repair reference, reusable application logic, focused tests, an independent source-wide validator, database-integration documentation and the formal Notebook 20 closeout record.

## Retrospective implementation audit

See:

- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`

The branch `audit/retrospective-implementation-closeout` remains open while the final source-field study continues. The complete test suite and all applicable validators will run again after that study closes and before final merge.

## Next bounded action

Begin the final remaining source-field study: `comment` and its embedded information.

The study should establish:

- physical storage and blank behaviour;
- whether comments are runner-level source text consistently;
- recurring vocabulary and punctuation structures;
- which facts are explicitly present versus inferred;
- whether embedded distances, incidents, tactics, equipment references or timing information can be extracted safely;
- which information must remain raw free text;
- what provenance and confidence are required for any derived features.

No comment-derived field should be treated as authoritative merely because a phrase can be parsed. Raw text and extraction lineage must remain recoverable.

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
9. add focused tests and independent validation where justified;
10. produce the report and lessons learned;
11. update the audit register, field governance, README and project plan;
12. commit and verify the complete closeout.

The stopping rule is:

> Investigate until a defensible rule can be stated, its known exceptions identified, unresolved cases preserved without information loss, and a validation implemented that will detect failure.

See:

- `docs/REPORT_00_PROJECT_SCOPE_AND_METHODOLOGY.md`
- `docs/REUSABLE_CODE_ARCHITECTURE.md`
- `docs/PROJECT_PLAN.md`
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`
