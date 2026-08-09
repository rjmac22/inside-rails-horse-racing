# `race_type_raw` Database Investigation — Handover

## Purpose

Investigate the semantics and analytical usability of `race_type_raw` as a database/source-governance question.

This is **not** a reader-facing study notebook. It belongs with the existing database field-investigation notebooks under `notebooks/`.

## Notebook path

Create and use:

`notebooks/23_race_type_raw_semantics.ipynb`

Notebook 22 is the latest completed database notebook, so this investigation continues the database notebook sequence as Notebook 23.

## Repository / workflow

Repository:

`rjmac22/inside-rails-horse-racing`

Branch:

`audit/retrospective-implementation-closeout`

Local checkout:

`~/Documents/inside-rails-horse-racing`

Mandatory project documents:

- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`;
- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/DATABASE_NOTEBOOK_ROUTING.md`;
- relevant existing race-classification / field-governance documentation;
- `docs/STUDY_REVISIT_REGISTER.md` if the result may affect reader-facing work.

## Current accepted analytical database

Database v3 is accepted and immutable.

Path:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Open read-only only. Do not modify or rebuild Database v3 during this investigation.

Use:

```python
from inside_rails.source_sqlite import connect_read_only
```

Preferred race-level interface:

`view_reconciled_race_occurrences`

Expected rows:

`189043`

## Bounded investigation question

Establish what `race_type_raw` actually represents in the accepted race-level data and whether it is sufficiently understood for governed analytical use.

The investigation should begin with evidence rather than a presumed racing definition.

Initial questions include:

1. Is `race_type_raw` present at the race-occurrence grain and how complete is it?
2. What literal values occur and with what frequencies?
3. How does the vocabulary vary by jurisdiction, period and other already-governed race context where relevant?
4. Does the field represent one racing concept consistently, or does it mix several concepts?
5. How does it relate to the race-classification governance already completed in the database notebook series?
6. Are there ambiguous, overloaded, malformed or jurisdiction-specific values that prevent a simple canonical interpretation?
7. Is any new governed field, parser, reference or database integration actually justified?

## Working discipline

Use the existing database-notebook method:

- one bounded question at a time;
- Markdown explanation before substantive analysis;
- inspect each output before deciding the next step;
- preserve literal raw values and lineage;
- do not invent categories before the evidence supports them;
- distinguish source observation from racing-domain interpretation;
- use external/manual verification only when a material semantic claim requires it, preserving provenance under project rules;
- stop when the field question is answered rather than expanding into unrelated racing taxonomy work.

## Database boundary

Database v3 is evidence for this investigation, not a scratch database.

If the investigation establishes a correctness-critical or reusable governance change, document the database consequence and follow the normal candidate/validation/release process separately. Do not alter the accepted v3 release in place.

## Relationship to reader-facing studies

If this investigation was triggered by a reader-facing study, keep the two workflows separate.

The database notebook establishes what `race_type_raw` means and what is safe to use. The reader-facing study may resume only with the governed result it actually needs.

Any material impact on an existing or in-progress study must be recorded through `docs/STUDY_REVISIT_REGISTER.md` where applicable.
