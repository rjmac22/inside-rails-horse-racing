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

Normal reader-facing studies should not query Source Version 1 directly when the required governed data is already integrated into Database v3.

Use the raw source only when the research question explicitly concerns source evidence, source anomalies or a validation/reconciliation step.

---

## Current Inside Rails study database

### Accepted Database v3

Database v3 was release-accepted and promoted on **9 August 2026**.

Canonical path:

`data/processed/database/releases/inside_rails_v3.sqlite3`

SHA-256:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Release identity:

- manifest status: `release_accepted`;
- SQLite `application_id`: `1230130259`;
- SQLite `user_version`: `3`;
- `PRAGMA quick_check`: `ok`;
- foreign-key-check rows: `0`;
- validation-result rows: `7`.

Promotion preserved:

- the exact validated Database v3 candidate;
- the accepted Database v2 release.

Reader-facing studies should use this Database v3 release by default and consume it read-only.

### Preserved Database v3 candidate

Path:

`data/processed/database/candidates/inside_rails_v3_candidate.sqlite3`

SHA-256:

`0389a10c8eedf9c86fb1efb39b228624f4371736f3a4ecfcd3010a2033ef873b`

Status:

`validated`

This is pre-release evidence, not the normal study database.

### Retained Database v2

Path:

`data/processed/database/releases/inside_rails_v2.sqlite3`

SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Database v2 is retained for rollback and historical reproducibility. It is no longer the default reader-facing study database.

### Retained Database v1

Path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Database v1 is historical release evidence and is not the normal study database.

---

## Database-selection rule

The normal analytical source is the exact accepted Database v3 release path above.

There is **no fallback** from Database v3 to:

- the Database v3 candidate;
- Database v2;
- Database v1;
- Source Version 1.

If Database v3 is absent or fails an identity check, fail closed rather than silently changing the data source.

The project does not currently use an implemented `active_database.json` resolver for studies. Take the release path from the canonical study documentation rather than guessing or inventing an active alias.

---

## Read-only access

Use the project read-only connection helper:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v3.sqlite3"

with connect_read_only(DATABASE) as connection:
    rows = connection.execute(
        "SELECT COUNT(*) FROM view_reconciled_race_occurrences"
    ).fetchone()[0]

print(rows)
```

Expected result:

```text
189043
```

For shell inspection:

```bash
sqlite3 -readonly data/processed/database/releases/inside_rails_v3.sqlite3
```

Do not use the accepted release as a notebook scratch database. Persist study-specific outputs elsewhere.

---

## Preferred analytical interfaces

### Race-level work

Prefer:

`view_reconciled_race_occurrences`

Expected rows:

`189043`

This is the normal race-level interface because it includes Database v2 governance plus exact Database v3 external reconciliations.

### Exact source-backed runner work

Prefer:

`view_reconciled_source_runner_participations`

Expected rows:

`1851285`

Use this when the analytical population must match admitted physical source runner rows exactly while still applying reconciled corrections, enrichments and invalidations.

### Combined governed runner work

Prefer:

`view_reconciled_runner_records`

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

### Database v2 governed views

The older `view_governed_*` interfaces remain present inside Database v3 for lineage and comparison. Do not choose them for a new general study when a corresponding `view_reconciled_*` interface exists, because doing so can bypass exact externally resolved facts added in Database v3.

---

## Reconciliation rule

Database v3 keeps raw source assertions immutable while making externally established exact facts analytically usable.

For study work:

- use the reconciled value where the database exposes an exact externally supported correction;
- keep source and reconciled concepts distinct in prose and output labels;
- where a raw analytical value is known wrong and no defensible replacement exists, accept the governed analytical null rather than restoring the raw value;
- do not infer missing numeric replacements from text-only evidence;
- do not overwrite source-presented prize, distance or advertised-time concepts with distinct external enrichments.

Examples and exact reconciliation cases are documented in `docs/STUDY_DATABASE_REFERENCE.md` and `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. `docs/STUDY_DATABASE_REFERENCE.md` has been read;
2. the local Jupyter environment was started with the canonical `rails` alias;
3. the intended analytical source is the accepted Database v3 release unless the research question explicitly requires raw source evidence;
4. the exact path is `data/processed/database/releases/inside_rails_v3.sqlite3`;
5. the release state is `release_accepted`;
6. the connection is read-only;
7. the study's observation grain is stated;
8. the chosen race/runner population is stated;
9. the relevant fields and identities are governed sufficiently for the proposed use;
10. unresolved values, invalidations and external supplementations that affect the question are understood;
11. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths, database names, table grains, release status or the Jupyter launch command from memory when they are recorded in the project documents.
