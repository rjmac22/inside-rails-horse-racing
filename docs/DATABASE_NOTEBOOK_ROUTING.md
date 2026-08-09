# Database vs Study Notebook Routing

## Purpose

This document defines where new Inside Rails investigations belong so field-governance work is not accidentally treated as reader-facing study work.

## Core rule

Use `notebooks/` for investigations whose primary question is about the data itself, including:

- what a raw or governed field means;
- whether a field is complete, internally consistent or analytically safe;
- the vocabulary, semantics or failure modes of a source field;
- whether a new canonical or governed interpretation is justified;
- whether a reusable transformation or reference is required;
- whether a database defect or missing governance could affect analytical correctness;
- any source/database investigation that may have a database integration consequence.

These are **database/source-governance investigations**, even when the need for them is discovered while working on a reader-facing study.

Use `studies/` only for reader-facing analytical research questions that consume already-governed data to investigate racing questions, relationships or claims.

## Escalation from a study

If a reader-facing study reaches a field whose semantics are not sufficiently established:

1. pause that line of study work;
2. record the blocker;
3. open the next sequential database notebook under `notebooks/`;
4. investigate the field using the database/source-governance workflow;
5. complete the applicable notebook wrap-up, implementation, tests, validation and database-consequence documentation;
6. only then return to the reader-facing study if the result is material to it.

Do **not** create a second governance system under `studies/` merely because the question arose there.

## Accepted database releases

Accepted database releases are immutable evidence.

An investigation may read the current accepted release through the project read-only connection helper, but must not modify or rebuild the accepted release in place. Any future database change must follow the normal candidate, validation and release process.

## Current example — `race_type_raw`

The investigation of `race_type_raw` is a database/source-semantics investigation because the question is what the field actually represents and whether its values can support governed analytical use.

It therefore belongs in the database notebook series under:

`notebooks/23_race_type_raw_semantics.ipynb`

It does **not** belong under `studies/`.

## Mandatory companion documents

Before database/source-governance notebook work, read and apply:

- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- the relevant existing field-governance and database-integration documentation;
- `docs/STUDY_REVISIT_REGISTER.md` when a change could affect a completed or in-progress reader-facing study.
