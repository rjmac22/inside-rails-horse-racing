# Inside Rails Study Data Access

## Purpose

This document is a mandatory pre-study reference for reader-facing analytical studies.

Read it alongside `docs/STUDY_RESEARCH_PLAYBOOK.md` and `docs/STUDY_REVISIT_REGISTER.md` before beginning a new study.

Its purpose is to prevent repeated mistakes about source paths, database identity, release status and read/write boundaries.

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

The naming convention is:

- validated but not release-accepted candidate: `inside_rails_v1_candidate.sqlite3`;
- accepted/promoted Version 1 database: `inside_rails_v1.sqlite3`.

The name `raceform` must not be used for an Inside Rails-generated database.

This distinction is intentional:

- `raceform.db` means immutable third-party source evidence;
- `inside_rails_v1_candidate.sqlite3` means an Inside Rails-built candidate that has not yet been accepted;
- `inside_rails_v1.sqlite3` means the accepted Inside Rails Version 1 database.

A future schema or release version should follow the same project-owned naming pattern rather than inheriting a source-provider filename.

---

## Release status rule

Before selecting a study data source, check the current database release state.

A database that is merely built or independently validated must not be silently treated as an accepted live analytical release.

Until `inside_rails_v1.sqlite3` has been explicitly release-accepted and promoted under the governed release procedure, studies must use the appropriate governed source/reference outputs rather than pretending a candidate is live.

When an accepted analytical database becomes available, this document must be updated with its canonical local path and release identifier before a study begins using it.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. which database or governed outputs the study will use;
2. the exact canonical path;
3. whether the database is source, candidate or accepted release;
4. that the connection mode matches the data-access rule;
5. that relevant fields and identities are already governed;
6. that no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths or database names from memory when they are recorded here.
