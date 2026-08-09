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

## Repository and local study environment

Repository:

`rjmac22/inside-rails-horse-racing`

Primary local repository root:

`~/Documents/inside-rails-horse-racing`

Study notebooks live under:

`studies/`

### Canonical local Jupyter startup

On the primary local development machine, start the Inside Rails Jupyter environment with:

```bash
rails
```

The alias must resolve to:

```bash
cd /home/rob/Documents/inside-rails-horse-racing && source .venv/bin/activate && PYTHONPATH=/home/rob/Documents/inside-rails-horse-racing/src jupyter lab
```

The repository uses a `src` layout. The absolute `PYTHONPATH` is intentional so kernels started under either `studies/` or `notebooks/` resolve the project package correctly.

Do not add notebook-local `sys.path` hacks if imports fail. Repair the launch environment instead.

---

## Immutable third-party source

Original filename:

`raceform.db`

Canonical Source Version 1 path:

`data/raw/form_2015-present/form_2015-present/raceform.db`

This file is source evidence, not the Inside Rails analytical database.

Standing rules:

- open it read-only;
- do not rename or modify it;
- source-data admission uses `rowid <> 1`;
- preserve the accepted Source Version 1 identity and existing field-governance decisions;
- authorised Source Version 1 race identity is exact raw `date + course + off`.

Normal reader-facing studies should not query Source Version 1 directly when the required governed data is already integrated into Database v2.

Use the raw source only when the research question explicitly concerns source evidence, source anomalies or a validation/reconciliation step.

---

## Current Inside Rails study database

### Accepted Database v2

Database v2 was release-accepted and promoted on **9 August 2026**.

Canonical path:

`data/processed/database/releases/inside_rails_v2.sqlite3`

SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Release identity:

- manifest status: `release_accepted`;
- SQLite `application_id`: `1230130259`;
- SQLite `user_version`: `2`;
- `PRAGMA quick_check`: `ok`;
- foreign-key-check rows: `0`;
- validation-result rows: `7`.

Promotion preserved:

- the exact validated Database v2 candidate;
- the accepted Database v1 release.

Reader-facing studies should use this Database v2 release by default and consume it read-only.

### Preserved Database v2 candidate

Path:

`data/processed/database/candidates/inside_rails_v2_candidate.sqlite3`

SHA-256:

`5fc6adaada69b7111a56021a9d67deeb62f6bb98268c69ad5c36009d337e39fe`

Status:

`validated`

This is pre-release evidence, not the normal study database.

### Retained Database v1

Path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v1 is retained for rollback and historical reproducibility. It is no longer the default reader-facing study database.

---

## Database-selection rule

The normal analytical source is the exact accepted Database v2 release path above.

There is **no fallback** from Database v2 to:

- the Database v2 candidate;
- Database v1;
- Source Version 1.

If Database v2 is absent or fails an identity check, fail closed rather than silently changing the data source.

The project does not currently use an implemented `active_database.json` resolver for studies. Take the release path from the canonical study documentation rather than guessing or inventing an active alias.

---

## Read-only access

Use the project read-only connection helper:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v2.sqlite3"

with connect_read_only(DATABASE) as connection:
    rows = connection.execute(
        "SELECT COUNT(*) FROM view_governed_race_occurrences"
    ).fetchone()[0]

print(rows)
```

Expected result:

```text
189043
```

For shell inspection:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v2.sqlite3
```

Do not use the accepted release as a notebook scratch database. Persist study-specific outputs elsewhere.

---

## Preferred analytical interfaces

### Race-level work

Prefer:

`view_governed_race_occurrences`

Expected rows:

`189043`

### Exact source-backed runner work

Prefer:

`view_governed_source_runner_participations`

Expected rows:

`1851285`

### Combined governed runner work

Prefer:

`view_governed_runner_records`

Expected rows:

`1851288`

This combined view includes the three explicitly verified missing-runner supplementations. State that fact when it affects the study population.

### Horse/pedigree identity work

Use:

`view_governed_horse_occurrence_assignments`

only when provisional Notebook 19 identity governance is relevant.

### Participant identity work

Use:

`view_governed_participant_label_identities`

only when accepted Notebook 22 mappings are relevant. Unresolved candidates remain unresolved.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. `docs/STUDY_DATABASE_REFERENCE.md` has been read;
2. the local Jupyter environment was started with the canonical `rails` alias;
3. the intended analytical source is the accepted Database v2 release unless the research question explicitly requires raw source evidence;
4. the exact path is `data/processed/database/releases/inside_rails_v2.sqlite3`;
5. the release state is `release_accepted`;
6. the connection is read-only;
7. the study's observation grain is stated;
8. the chosen race/runner population is stated;
9. the relevant fields and identities are governed sufficiently for the proposed use;
10. unresolved values and external supplementations that affect the question are understood;
11. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths, database names, table grains, release status or the Jupyter launch command from memory when they are recorded in the project documents.
