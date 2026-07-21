# Report 00 — Project Scope and Methodology

## Executive conclusion

Inside Rails will be built as a notebook-led, evidence-based relational database project.

The project will begin with the supplied `raceform.db` source, but the wider Kaggle download will be treated as a collection of separate data products rather than as one ready-made database.

No cleaning, integration or target-schema decision will be made until the source structure and racing meaning have been profiled.

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
4. separate observation from decision;
5. prefer reversible transformations;
6. test keys, joins and business rules;
7. record uncertainty instead of hiding it;
8. retain traceability from analytical outputs back to source;
9. use visible validation and reconciliation checks;
10. document significant architectural and data-quality decisions.

## Planned architecture

The project will use four conceptual layers:

- **Raw:** immutable original source files.
- **Staging:** controlled reproduction of source data with technical lineage.
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
- The target relational schema will not be designed before profiling.
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

**Low confidence** would currently be justified for any detailed schema, key or integration decision because the primary source database has not yet been structurally profiled.

## Practical implication

The next task is not data cleaning.

The next task is to inspect `raceform.db` as supplied and establish:

- tables and views;
- columns and declared types;
- row counts;
- indexes;
- declared keys;
- foreign keys;
- date coverage;
- likely table grain;
- likely relationships;
- areas requiring racing-domain investigation.

## Next action

Create and complete:

`notebooks/01_source_database_structure_profile.ipynb`
