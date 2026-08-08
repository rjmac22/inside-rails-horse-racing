# Inside Rails Study Data Access

## Purpose

This document is a mandatory pre-study reference for reader-facing analytical studies.

Read it alongside:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Its purpose is to prevent repeated mistakes about source paths, database identity, release status and read/write boundaries.

The fuller study-facing database structure, table grains, identifier rules and current release state are maintained in `docs/STUDY_DATABASE_REFERENCE.md` and must be read before every study.

---

## Repository and branch

Repository:

`rjmac22/inside-rails-horse-racing`

Working repository root on the primary local development machine:

`~/Documents/inside-rails-horse-racing`

Study notebooks live under:

`studies/`

---

## Immutable third-party source

The original third-party SQLite source retains its original filename for lineage:

`raceform.db`

Canonical local Source Version 1 path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

This file is source evidence, not the Inside Rails database.

Standing rules:

- open it read-only;
- do not rename or modify it;
- all source-data queries use `rowid <> 1`;
- preserve the accepted Source Version 1 identity and existing field-governance decisions;
- authorised Source Version 1 race identity is exact raw `date + course + off`.

The original `raceform.db` filename may appear in source-lineage documentation, but it must not be used as the name of an Inside Rails-built analytical database.

---

## Inside Rails database naming

Inside Rails-generated databases use project-owned names.

The approved naming convention is:

- validated but not release-accepted candidate: `inside_rails_v1_candidate.sqlite3`;
- accepted/promoted Version 1 database: `inside_rails_v1.sqlite3`.

The name `raceform` must not be used for an Inside Rails-generated database.

This distinction is intentional:

- `raceform.db` means immutable third-party source evidence;
- `inside_rails_v1_candidate.sqlite3` means an Inside Rails-built candidate that has not yet been accepted;
- `inside_rails_v1.sqlite3` means the accepted Inside Rails Version 1 database.

A future schema or release version should follow the same project-owned naming pattern rather than inheriting a source-provider filename.

### Current legacy candidate filename

The already-built Phase 4 disposable candidate predates this naming decision and currently uses:

`data/processed/database/candidates/raceform_v1_minimum_core_candidate.sqlite3`

This is a legacy generated filename only. The candidate is not release-accepted and must not become the accepted database name.

Updating the builder/output convention to the approved Inside Rails filename is pending governed database work.

---

## Release status rule

Before selecting a study data source, check `docs/STUDY_DATABASE_REFERENCE.md` for the current release state.

A database that is merely built or independently validated must not be silently treated as an accepted live analytical release.

Until `inside_rails_v1.sqlite3` has been explicitly release-accepted and promoted under the governed release procedure, studies must use the appropriate governed source/reference outputs rather than pretending a candidate is live.

When an accepted analytical database becomes available, this document and `docs/STUDY_DATABASE_REFERENCE.md` must be updated with its canonical local path and release identifier before a study begins using it.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. `docs/STUDY_DATABASE_REFERENCE.md` has been read;
2. which database or governed outputs the study will use;
3. the exact canonical path;
4. whether the database is source, candidate or accepted release;
5. that the connection mode matches the data-access rule;
6. that relevant fields and identities are already governed;
7. that no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths, database names, table grains or release status from memory when they are recorded in the study documents.
