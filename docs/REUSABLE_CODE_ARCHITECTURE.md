# Reusable Code Architecture

## Purpose

Inside Rails is notebook-led, but it is not notebook-only.

Finished notebooks should explain:

- the analytical question;
- the source evidence;
- the interpretation;
- the conclusions and uncertainty;
- the resulting database consequence;
- the validation that protects the decision.

Reusable technical plumbing should live outside notebooks so it can be tested, reused and reviewed independently.

## Project rule

New logic should normally be developed visibly in the notebook first.

Once the logic:

- has run successfully;
- is stable;
- is not specific to one displayed result;
- will be reused by another notebook, database build step or validation script;
- has a clear failure condition that can be tested;

it should be extracted into `src/inside_rails/`.

The finished notebook should retain the analytical intent, evidence, exception analysis and results rather than low-level implementation noise.

## Investigation-to-implementation handoff

Reusable code should be extracted only after the related investigation has reached the project stopping rule:

> the project can state a defensible transformation or design rule, identify its known exceptions, preserve unresolved cases without information loss, and implement a validation that detects when the rule fails.

The normal handoff is:

1. profile and interpret the source in a notebook;
2. state the candidate transformation or design rule;
3. test coverage and inspect material exceptions;
4. record the resulting database consequence;
5. implement the rule reversibly;
6. extract stable reusable plumbing;
7. add an independent validation route;
8. use the extracted code in later staging or database-build work.

Code should not be extracted merely because a notebook cell is long. Extraction is justified by stability, reuse, testability and a defined architectural responsibility.

## Current package structure

### `src/inside_rails/source_sqlite.py`

Responsible for source-database plumbing that is independent of a particular notebook display:

- opening SQLite files in read-only mode;
- safely quoting SQLite identifiers;
- inventorying schema objects;
- reading declared table-column metadata;
- constructing null-safe provisional composite-key expressions;
- reproducing the stable structural assertions established by Notebook 01.

It does not:

- clean source values;
- alter the raw database;
- decide the final relational schema;
- convert racing-domain codes;
- resolve real-world entity identity.

### `scripts/validate_source_profile.py`

Provides a command-line regression check for the specific `raceform.db` source profiled in Notebook 01.

It checks:

- row counts;
- apparent-race count;
- provisional runner-key uniqueness;
- date coverage;
- schema-object count;
- declared-column count;
- SQLite quick-check result.

Run from the project root with the package on `PYTHONPATH`:

```bash
PYTHONPATH=src python scripts/validate_source_profile.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

## Layer boundaries

The project should develop reusable code in layers.

### Generic technical layer

Code that could work with another SQLite source or another racing dataset:

- filesystem and project paths;
- read-only database connections;
- schema inspection;
- validation helpers;
- deterministic reporting utilities.

### Inside Rails source-adapter layer

Code that understands the supplied source product without yet imposing a final domain model:

- header-row exclusion rules;
- source-table names;
- provisional race and runner descriptions;
- source-specific profile assertions;
- source lineage;
- preservation of unresolved source states.

### Racing-domain layer

Code added only after the relevant meanings have been established:

- distance parsing;
- weight parsing;
- finishing-outcome interpretation;
- going classification;
- starting-price parsing;
- jurisdiction and course mapping;
- race, horse and participant identity rules.

Domain code should normally return explicit statuses or flags for exceptional and unresolved inputs rather than silently coercing them.

### Database-build layer

Code added after the target architecture is justified sufficiently for the bounded area being implemented:

- staging loads;
- reversible transformations;
- raw-to-canonical field mapping;
- surrogate-key assignment;
- core-table creation;
- constraints and indexes;
- reconciliation tests;
- analytical views.

The complete final schema does not need to be known before all staging work begins. Stable bounded rules should be implemented incrementally so that the emerging architecture is tested in practice.

## Database-consequence rule

Every stable analytical conclusion should be translated into an explicit implementation action. Examples include:

- preserve a raw value unchanged;
- add a parsed or canonical field;
- assign a surrogate identifier;
- retain a source identifier for lineage only;
- add a data-quality or review status;
- defer enrichment;
- reject a row through an explicit governed rule;
- add a constraint or reconciliation assertion;
- abandon or revise the candidate transformation.

A reusable function should exist to enact a justified rule, not to conceal an unresolved analytical decision.

## Validation rule

Every extracted reusable module should have a corresponding validation route.

Validation may be:

- a focused script under `scripts/`;
- automated tests;
- database reconciliation queries;
- schema or constraint assertions;
- expected exception counts;
- round-trip checks confirming that raw values and lineage remain recoverable.

Notebook output alone is not sufficient validation for code intended to support later project stages.

Validation should detect both technical failure and rule failure. For example, a parser merely running without an exception is insufficient if it silently changes the number of unresolved source values.

## Raw-data rule

Reusable utilities must never silently modify files under `data/raw/`.

Source access should default to read-only operation. Any later ingestion process must write to separate staging or build locations and preserve source lineage.

Parsed and canonical values must normally be stored separately from their raw source values. Corrections should be represented as governed transformations or audit records rather than overwriting evidence.

## Guardrail against premature abstraction

Do not create broad frameworks before the project has repeated evidence that they are needed.

Prefer:

- a small explicit function over a speculative abstraction;
- a source-specific adapter over a falsely generic interface;
- visible statuses over hidden fallback behaviour;
- a focused validation over a large untested utility layer.

Refactor toward generality only after multiple real project cases establish the common pattern.

## Guardrail against over-investigation

Reusable-code work should support forward movement into staging and implementation.

Do not continue profiling solely to eliminate every rare anomaly before code can be written. Once a defensible rule, known exception set, preservation mechanism and failure-detecting validation exist, implement the rule and move to the next bounded question.

Return to investigation when implementation exposes a failed assertion, unsafe join, information loss or materially misleading result.

## AI-assisted development rule

AI may accelerate syntax, query construction, debugging, refactoring and documentation, but generated work must be treated as untrusted until checked against the source evidence.

AI-assisted code must:

- be inspected for its actual transformation semantics;
- be run against the complete relevant population where practical;
- preserve raw values and lineage as required;
- expose rather than hide exceptions;
- pass the same validation expected of manually written code.

The user retains responsibility for the methodological judgement: what the data means, whether the rule is defensible and whether the evidence is sufficient to proceed.

## Documentation rule

Each completed notebook should normally produce:

- the finished notebook;
- a concise Minto-style report in `docs/`;
- a machine-readable closeout record;
- an explicit database consequence;
- reusable code where justified;
- a validation script or test where reusable code was extracted;
- updates to the README and project plan.

This mirrors the working method established in the Coral 2NL analysis project while adapting it to data engineering and horse-racing domain analysis.
