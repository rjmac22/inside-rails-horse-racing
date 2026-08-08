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

- validated candidate: `inside_rails_v1_candidate.sqlite3`;
- accepted/promoted Version 1 database: `inside_rails_v1.sqlite3`.

The name `raceform` must not be used for an Inside Rails-generated database.

This distinction is intentional:

- `raceform.db` means immutable third-party source evidence;
- `inside_rails_v1_candidate.sqlite3` means the preserved validated pre-release candidate;
- `inside_rails_v1.sqlite3` means the accepted Inside Rails Version 1 database.

A future schema or release version should follow the same project-owned naming pattern rather than inheriting a source-provider filename.

Canonical local candidate path:

`data/processed/database/candidates/inside_rails_v1_candidate.sqlite3`

Canonical accepted-release path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

Accepted-release SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

The preserved candidate remains unchanged at SHA-256:

`7dd61b51904b324a83c4ceb28486c716226c8de7d37952a713e90ae3a81f65a2`

---

## Release status rule

Inside Rails Version 1 was release-accepted and promoted on 8 August 2026.

Current status:

- accepted release exists at the canonical release path;
- import manifest status is `release_accepted`;
- release validation result count is 7;
- SQLite `quick_check` returned `ok`;
- foreign-key check returned zero rows;
- candidate hash remained unchanged during promotion.

Reader-facing studies should use the accepted release by default and open it read-only.

There is no fallback from the accepted release path to the candidate or raw source. If the accepted release is absent or its identity cannot be verified when verification is required, fail closed rather than silently changing data source.

The candidate remains evidence and rollback material. It is not the normal study database.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. `docs/STUDY_DATABASE_REFERENCE.md` has been read;
2. the accepted Version 1 database is the intended study source unless the question explicitly requires raw/source evidence;
3. the exact canonical path is `data/processed/database/releases/inside_rails_v1.sqlite3`;
4. the release state is `release_accepted`;
5. the connection is read-only and query-only where applicable;
6. relevant fields and identities are already governed;
7. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths, database names, table grains or release status from memory when they are recorded in the study documents.
