# Report 00 — Project Scope and Methodology

## Executive conclusion

Inside Rails will be built as a notebook-led, evidence-based relational database project.

The project will begin with the supplied `raceform.db` source, but the wider Kaggle download will be treated as a collection of separate data products rather than as one ready-made database.

No cleaning, integration or target-schema decision will be made until the source structure and racing meaning have been profiled sufficiently to support a defensible transformation rule.

The final database platform also remains deliberately open. SQLite is currently the source format, not yet the selected destination technology.

## Why this matters

The largest early risk is not technical failure. It is building a polished database around assumptions that have not been tested.

Horse-racing data can contain:

- incomplete identifiers;
- repeated snapshots;
- amended results;
- unusual but valid values;
- overlapping historical products;
- fields whose meaning changes by context;
- names that do not uniquely identify real-world entities.

Applying generic cleaning rules too early could remove legitimate records, create false joins or conceal uncertainty.

The methodology therefore prioritises source preservation, profiling, domain interpretation and validation before transformation.

## Scope established

The first phase will focus on:

`data/raw/form_2015-present/form_2015-present/raceform.db`

Other supplied products remain outside the immediate integration scope, including:

- `archive_1988-2004`;
- `archive_2005-2014`;
- recent form HTML;
- daily racecards;
- BHA ratings;
- Betfair data.

These sources may be incorporated later only after their structures, identifiers, overlaps and business meanings have been investigated separately.

## Methodological commitments

The project will:

1. preserve raw source data unchanged;
2. profile before cleaning;
3. understand racing meaning before transforming;
4. separate observation from interpretation and design decisions;
5. prefer reversible transformations;
6. test keys, joins and business rules;
7. record uncertainty instead of hiding it;
8. retain traceability from analytical outputs back to source;
9. use visible validation and reconciliation checks;
10. document significant architectural and data-quality decisions;
11. develop new analytical logic visibly in notebooks before extracting stable reusable code;
12. require each bounded study to resolve a database-design or transformation question rather than merely describe a field;
13. translate every material conclusion into a practical database consequence;
14. move incrementally from investigation into staging and implementation rather than waiting for perfect knowledge of the complete source.

## Investigation-to-implementation cycle

The standard project cycle is:

1. **Profile the source.** Establish physical structure, field behaviour, domain meaning and anomalies without altering the raw data.
2. **Form a candidate rule.** State a proposed key, parser, classification, relationship or transformation in explicit terms.
3. **Test the rule.** Measure coverage, uniqueness, exceptions and failure modes against the complete relevant source population.
4. **Inspect exceptions.** Determine whether exceptions are valid domain cases, source defects, unresolved ambiguity or evidence that the candidate rule is wrong.
5. **Record the decision.** Separate observed evidence, interpretation, confidence and the resulting design choice.
6. **Implement reversibly.** Preserve raw values and source lineage while adding parsed, canonical, surrogate or status fields separately.
7. **Validate independently.** Add assertions, reconciliation queries, scripts, tests or constraints that will detect future failure.
8. **Close out and proceed.** Update the notebook, report, closeout record and project entry documents before beginning the next bounded question.

This cycle is preferable to designing a complete polished schema first and attempting to force the source into it afterward.

## Required database consequence

A completed investigation must lead to one or more explicit consequences. Typical consequences are:

- preserve the raw value unchanged;
- parse a separate canonical value;
- assign an independent surrogate identifier;
- retain a source identifier for lineage but not business identity;
- classify a row as valid, exceptional, unresolved or rejected;
- add a review or data-quality flag;
- defer enrichment until an authoritative external source is available;
- add a constraint, assertion or reconciliation check;
- revise or abandon the proposed rule.

A notebook that only reports frequencies or anomalies without affecting a design, transformation or validation decision is incomplete.

## Stopping rule

Investigation should stop when the project can:

> state a defensible transformation or design rule, identify its known exceptions, preserve unresolved cases without information loss, and implement a validation that detects when the rule fails.

The project does not require every source oddity to be fully explained before progress can continue. Rare unresolved cases may be retained explicitly with raw values, lineage and review status.

Further investigation is justified when an unresolved issue could materially:

- merge distinct real-world entities;
- split one entity incorrectly;
- alter official results or financial values;
- create false joins;
- discard source records;
- make downstream analysis misleading;
- prevent a reliable validation rule from being written.

Further investigation is not automatically justified merely because an anomaly exists.

## Guardrails against over-investigation

The main methodological risk after premature cleaning is endless profiling. To prevent this:

- each notebook should answer one bounded design question;
- the question and expected database consequence should be stated near the start;
- conclusions should distinguish material exceptions from harmless source variation;
- known unresolved rows should be counted and preserved rather than allowed to block the entire build;
- target-schema design may remain provisional, but staging implementation should begin once stable source rules exist;
- repeated analysis should be driven by a decision or failed validation, not by a desire for exhaustive description;
- low-value polishing of already sufficient evidence should not displace the next implementation step.

The aim is not perfect understanding of every dirty row. The aim is a trustworthy system that represents what is known, preserves what is uncertain and makes failures visible.

## Role of notebooks, reusable code and AI assistance

Notebooks are the visible analytical record. They should show the question, evidence, interpretation, uncertainty and resulting decision.

Stable technical plumbing should be extracted into `src/inside_rails/` only after it has worked correctly in the notebook and is genuinely reusable. Extracted code must have an independent validation route.

AI assistance may accelerate query writing, debugging, documentation and review, but it does not replace project judgement. The controlling decisions remain evidence-based:

- what the source values mean;
- whether a candidate rule is justified;
- which exceptions are material;
- what uncertainty must be preserved;
- when evidence is sufficient to proceed.

Generated code and explanations must therefore be inspected against actual outputs and validated like any other contribution.

## Planned architecture

The project will use four conceptual layers:

- **Raw:** immutable original source files.
- **Staging:** controlled reproduction of source data with technical lineage and reversible parsed fields.
- **Core:** validated relational entities, keys, constraints and relationships.
- **Analytical:** convenient views or derived datasets for research.

This architecture does not yet prescribe a physical database platform.

Possible technologies may include SQLite, DuckDB, PostgreSQL or another suitable relational system. The decision will be made after profiling clarifies the data volume, structure and operating requirements.

## Decisions made

- `raceform.db` is the first source to investigate.
- Raw files are immutable.
- The download is not assumed to be one unified database.
- Separate source products will not be merged automatically.
- Missing values will not be blindly imputed.
- Duplicate-looking rows will not be blindly deleted.
- Statistical outliers will not be treated automatically as errors.
- Source identifiers will be tested before being accepted as keys.
- The target relational schema will not be designed before sufficient profiling.
- Staging implementation will begin incrementally once bounded source rules are stable.
- Unresolved exceptions will be preserved and flagged rather than silently normalised.
- The target database platform remains open.

## Open decisions

The following remain unresolved:

- target database technology;
- staging and core physical implementation;
- final entity model;
- table grain;
- key strategy;
- source-product integration rules;
- update and ingestion design;
- analytical engine and deployment approach.

These are intentionally deferred until evidence is available.

## Confidence

**High confidence** in the methodological direction.

The principles are standard, conservative and appropriate for a professional data-engineering project.

The workflow is particularly suitable for a portfolio project because it preserves an auditable chain from raw evidence through design decision to tested implementation.

Confidence in individual schema, key and integration decisions must be stated separately and revised as evidence accumulates.

## Practical implication

The next task is not generic data cleaning.

Each next task should be framed as a bounded database question, such as:

- how a source field should be represented;
- whether a candidate identity rule is safe;
- which raw variants map to one canonical value;
- which exceptions require flags rather than correction;
- what validation will protect the resulting implementation.

The project should proceed from those findings into incremental staging structures rather than postponing all implementation until every field has been studied.

## Next action

Create and complete:

`notebooks/01_source_database_structure_profile.ipynb`
