# Inside Rails Study Data Access

## Purpose

This document is a mandatory pre-study reference for reader-facing analytical studies.

Read it alongside:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/RESEARCH_DATA_SOURCE_REGISTER.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

Its purpose is to prevent repeated mistakes about source paths, database identity, release status and read/write boundaries.

The fuller study-facing database structure, table grains, identifier rules and current release state are maintained in `docs/STUDY_DATABASE_REFERENCE.md` and must be read before every study. Potential local and external information sources that may become useful during a study are maintained in `docs/RESEARCH_DATA_SOURCE_REGISTER.md`.

---

## Repository and local study environment

Repository:

`rjmac22/inside-rails-horse-racing`

Primary local repository root:

`~/Documents/inside-rails-horse-racing`

### Notebook location rule

Notebook location is determined by the purpose of the work:

- database construction, source-field semantics, field governance, parsing, identity, reference-data and other database-correctness investigations belong under `notebooks/`;
- reader-facing analytical studies that consume already-governed data belong under `studies/`.

If a reader-facing study exposes an unresolved field-semantics or database-governance question, pause that line of study work and investigate it in the database notebook series under `notebooks/`. Do not create database-governance notebooks under `studies/` merely because the issue was discovered during a study.

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

Normal reader-facing studies should not query Source Version 1 directly when the required governed data is already integrated into Database v4.

Use the raw source only when the research question explicitly concerns source evidence, source anomalies or a validation/reconciliation step.

---

## Current Inside Rails study database

### Accepted Database v4

Database v4 was release-accepted and promoted on **12 August 2026**.

Canonical path:

`data/processed/database/releases/inside_rails_v4.sqlite3`

SHA-256:

`45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7`

Release identity:

- manifest status: `release_accepted`;
- SQLite `application_id`: `1230130259`;
- SQLite `user_version`: `4`;
- `PRAGMA quick_check`: `ok`;
- foreign-key-check rows: `0`;
- validation-result rows: `7`.

Promotion preserved:

- the exact Database v4 candidate at SHA-256 `04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`;
- accepted Database v3 at SHA-256 `aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`.

Reader-facing studies should use this Database v4 release by default and consume it read-only.

Database v4 preserves the full v3 reconciled analytical layer and adds the completed Study 03 British racecourse/course identity reference layer.

### Preserved Database v4 candidate

Path:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

SHA-256:

`04e027d09cd323df5b0a6ae97c6660018a1aa2576bacf8a12d546d2c4217e06e`

Status:

`built`

This is immutable pre-release evidence, not the normal study database.

### Retained Database v3

Path:

`data/processed/database/releases/inside_rails_v3.sqlite3`

SHA-256:

`aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0`

Database v3 is retained for rollback and historical reproducibility. It is no longer the default reader-facing study database.

### Retained Database v2

Path:

`data/processed/database/releases/inside_rails_v2.sqlite3`

SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

### Retained Database v1

Path:

`data/processed/database/releases/inside_rails_v1.sqlite3`

SHA-256:

`2b9ffff749dc4337b0372814ccf8efb38dd262b1f25449af400de0cb353c8934`

Prior releases are historical release/rollback evidence and are not the normal study database.

---

## Database-selection rule

The normal analytical source is the exact accepted Database v4 release path above.

There is **no fallback** from Database v4 to:

- the Database v4 candidate;
- Database v3;
- Database v2;
- Database v1;
- Source Version 1.

If Database v4 is absent or fails an identity check, fail closed rather than silently changing the data source.

The project does not currently use an implemented `active_database.json` resolver for studies. Take the release path from the canonical study documentation rather than guessing or inventing an active alias.

---

## Read-only access

Use the project read-only connection helper:

```python
from inside_rails.source_sqlite import connect_read_only

DATABASE = "data/processed/database/releases/inside_rails_v4.sqlite3"

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
sqlite3 -readonly data/processed/database/releases/inside_rails_v4.sqlite3
```

Do not use the accepted release as a notebook scratch database. Persist study-specific outputs elsewhere.

---

## Preferred analytical interfaces

### Race-level work

Prefer:

`view_reconciled_race_occurrences`

Expected rows:

`189043`

This remains the normal general race-level interface because Database v4 preserves the Database v3 reconciliation layer unchanged.

### Great Britain racecourse-aware race work

Prefer:

`view_gb_reconciled_race_occurrences_with_racecourse`

Expected rows:

`111634`

Grain:

> one reconciled Great Britain source race occurrence with governed racecourse identity.

Use this when the study question needs the Study 03 racecourse identity layer. It adds racecourse identity without assigning a physical track/course below racecourse level.

The view must preserve one row per GB race occurrence. Do not infer a physical course/track ID from the racecourse identity alone.

### Racecourse reference work

Use:

- `view_gb_racecourse_identity_reference` for the 65 source-label → racecourse mappings;
- `view_gb_course_track_identities` for the 86 stable Study 03 course/track identities.

Current Study 03 reference baseline:

- racecourse notebooks: **61**;
- source-label mappings: **65**;
- governed racecourses: **61**;
- course/track inventory rows: **90**;
- stable course/track identities: **86**;
- unresolved governance rows: **7**.

The stable course/track reference is not a race-occurrence assignment table.

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

### Carried Database v2/v3 governed views

The older `view_governed_*` and `view_reconciled_*` interfaces remain present inside Database v4 for lineage, comparison and general analysis. Do not bypass a newer governed interface when the study question depends on information added later.

---

## Reconciliation rule

Database v4 preserves Database v3's rule that raw source assertions remain immutable while externally established exact facts are analytically usable.

For study work:

- use the reconciled value where the database exposes an exact externally supported correction;
- keep source and reconciled concepts distinct in prose and output labels;
- where a raw analytical value is known wrong and no defensible replacement exists, accept the governed analytical null rather than restoring the raw value;
- do not infer missing numeric replacements from text-only evidence;
- do not overwrite source-presented prize, distance or advertised-time concepts with distinct external enrichments.

Examples and exact reconciliation cases are documented in `docs/STUDY_DATABASE_REFERENCE.md` and `docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`.

---

## Verified post-release overlay rule

An accepted database release remains immutable, but a later verified correction or enrichment must not be ignored merely because the next database release has not yet integrated it.

Standing rule:

> Once an external fact has been verified strongly enough for governed reuse and entered into the pending reconciliation registers, reader-facing studies must use that verified value immediately through the explicit read-only study overlay whenever the affected field is material to the analysis.

Current pending evidence register:

`data/reference/post_v3_external_verification_candidates.csv`

Current typed analytical register:

`data/reference/post_v3_external_value_resolutions.csv`

These filenames are historical names for the pending post-v3 register. Database v4 does not automatically imply that every entry in them has been integrated. A study must check whether the specific resolution is native to the accepted release before deciding whether the overlay still applies.

Reusable query helper:

```python
from inside_rails.study_overlay import build_race_overlay_query
```

The overlay must:

- leave the accepted Database v4 file unchanged;
- leave raw and accepted-release values visible for lineage;
- join race-level resolutions using the authorised exact source identity `raw_date + raw_course + raw_off`;
- expose a separate study-facing corrected/enriched value;
- expose whether that value came from the accepted database or the pending overlay;
- retain the verification identifier that supports each overlaid value;
- fail closed on duplicate or unsupported pending resolutions;
- use raw `off` only as an internal source-identity key where required, not as the default human-facing race-time display;
- stop applying a pending overlay once an accepted database release natively contains the same governed resolution.

Do not knowingly continue analysing a value already established as wrong simply to preserve the convenience of an older immutable release. Immutability protects historical releases; it does not require current studies to ignore newer verified evidence.

Evidence-only confirmations do not create replacement values. Unresolved or weak external observations must not be promoted into the overlay merely because they are present in a research notebook.

---

## External data-source discovery rule

Database v4 is the normal starting point, not an artificial ceiling on what a study is allowed to learn.

If the evidence suggests that a missing external variable, official record or independent source could materially answer, explain or test the current research question, check `docs/RESEARCH_DATA_SOURCE_REGISTER.md` and actively investigate the best current source before concluding that the information is unavailable.

The assistant should perform that discovery work proactively. The user should not need to remember which historical files, official websites, APIs, weather archives, exchange feeds or specialist sources might exist.

Possible outcomes are deliberately distinct:

1. use a bounded external lookup/manual verification;
2. acquire a study-specific external dataset;
3. escalate to governed database integration because the information is correctness-critical or clearly reusable;
4. decide not to acquire it because access, cost, licensing, quality or effort is disproportionate.

Do not automatically expand the database whenever another source exists. First establish whether the study actually needs the information and whether the source supports the concept being asked about.

If a study is materially limited by information that might exist outside Database v4, record the source search and resulting decision rather than simply writing that the database lacks the field.

---

## External verification provenance rule

An external verification is not complete unless another researcher can see exactly where the supporting evidence came from.

Standing rule:

> **No source locator = not verified.**

Every material external verification used in a study, database-correctness investigation, manual verification register, reconciliation decision or validation sample must preserve enough provenance to reconstruct the check.

At minimum record:

- the subject or record being verified;
- the field, claim or question being checked;
- the external source or publisher;
- a specific, reconstructible evidence locator — normally the exact result/page URL, document identifier, official record reference or equivalent stable locator;
- the externally supported value or conclusion;
- a short evidence note explaining what the source establishes;
- the access date where the source is liable to change or where the existing provenance standard requires it.

Where verification is performed row by row, the evidence locator must be recorded **per verified row**. A generic homepage, search-results page, source name without a locator, or statement such as "checked externally" is not sufficient provenance.

Prefer a race-specific or record-specific page over a generic date/meeting page when one is available. A broader meeting/date page may be used when it contains the exact result being verified and the row remains unambiguous, but the ledger must still retain that locator.

If the external source is ambiguous, inaccessible, or does not actually establish the fact being checked, do not mark the record verified. Use another source or leave the result provisional/unresolved.

This rule applies equally to evidence that confirms the database and evidence that contradicts it. Confirmations used to support a reliability claim require the same provenance standard as corrections.

Do not populate a verification result from the database value itself and then label it externally verified. The external evidence must independently support the recorded conclusion.

---

## Study-start check

Before writing the first analytical cell of any study, confirm:

1. `docs/STUDY_DATABASE_REFERENCE.md` has been read;
2. `docs/RESEARCH_DATA_SOURCE_REGISTER.md` has been read so known external/local capabilities are not forgotten;
3. the local Jupyter environment was started with the canonical `rails` alias;
4. the intended analytical source is the accepted Database v4 release unless the research question explicitly requires raw source evidence;
5. the exact path is `data/processed/database/releases/inside_rails_v4.sqlite3`;
6. the release state is `release_accepted`;
7. the connection is read-only;
8. the study's observation grain is stated;
9. the chosen race/runner population is stated;
10. the relevant fields and identities are governed sufficiently for the proposed use;
11. unresolved values, invalidations and external supplementations that affect the question are understood;
12. the pending post-release resolution register has been checked and any material verified overlay is being applied;
13. any external verification already relied on by the study has reconstructible provenance under the external verification provenance rule;
14. no unresolved entry in `docs/STUDY_REVISIT_REGISTER.md` blocks the work.

Do not reconstruct paths, database names, table grains, release status or the Jupyter launch command from memory when they are recorded in the project documents.
