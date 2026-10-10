# Repository map (human + AI navigation)

Use this as a **locator**, not an alternative authority. Read the actual linked document before making claims or changes. Avoid creating new research just to maintain this index.

## Start here by task

| Goal | Source of truth |
| --- | --- |
| Overview and accepted database release | [README.md](README.md) |
| Current plan and sequence | [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) |
| Project rules | [docs/PROJECT_RULES.md](docs/PROJECT_RULES.md) |
| Parked reader/article ideas | [docs/READER_IDEA_BACKLOG.md](docs/READER_IDEA_BACKLOG.md) |
| Reader research procedure | [docs/STUDY_RESEARCH_PLAYBOOK.md](docs/STUDY_RESEARCH_PLAYBOOK.md) |
| Canonical database interfaces | [docs/STUDY_DATABASE_REFERENCE.md](docs/STUDY_DATABASE_REFERENCE.md) |
| Safe database access | [docs/STUDY_DATA_ACCESS.md](docs/STUDY_DATA_ACCESS.md) |
| Studies requiring reconsideration | [docs/STUDY_REVISIT_REGISTER.md](docs/STUDY_REVISIT_REGISTER.md) |
| Completed-study tracking | [docs/STUDY_CLOSEOUT_REGISTER.md](docs/STUDY_CLOSEOUT_REGISTER.md) |
| Source governance | [docs/RESEARCH_DATA_SOURCE_REGISTER.md](docs/RESEARCH_DATA_SOURCE_REGISTER.md), [metadata/SOURCE_REGISTER.md](metadata/SOURCE_REGISTER.md) |
| Database v4 release evidence | [docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md](docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md) |
| Study and research lessons | [docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md](docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md) |
| Data import / validation controls | [docs/DATABASE_IMPORT_VALIDATION_GATE.md](docs/DATABASE_IMPORT_VALIDATION_GATE.md), [docs/APPLICABLE_VALIDATOR_GATE.md](docs/APPLICABLE_VALIDATOR_GATE.md) |

## Directory guide

| Path | Purpose |
| --- | --- |
| [docs/](docs/) | Research instructions, plans, audit reports, study closeouts, database design, governance and release records |
| [studies/](studies/) | Reader-facing racing studies, especially `studies/jurisdictions/great_britain/` and its `racecourses/` subfolder |
| [notebooks/](notebooks/) | Numbered source/database research notebooks; [index](notebooks/README.md) |
| [src/](src/) | Reusable implementation |
| [scripts/](scripts/) | Workflow and validator scripts |
| [tests/](tests/) | Automated verification |
| [db/](db/) | Database implementation files |
| [data/](data/) | Source and derived datasets, including immutable evidence (follow documented access rules) |
| [metadata/](metadata/) | Source descriptions and provenance |
| [reports/](reports/) | Reports and outputs |
| [NOTEBOOK_WORKING_RULES.md](NOTEBOOK_WORKING_RULES.md) | Working conventions for notebooks |

## Naming shortcuts

- `docs/REPORT_*.md`: source investigation reports.
- `docs/NOTEBOOK_*_CLOSEOUT.*`: notebook closure evidence.
- `docs/PHASE_3_*.md` / `docs/PHASE_4_*.md`: earlier schema and release-design work.
- `docs/*_DATABASE_INTEGRATION.md`: field-level integration decisions.
- `docs/DATABASE_V*_RELEASE_ACCEPTANCE_AND_PROMOTION.md`: release history.
- `docs/studies/`: GB study closeout material.
- `studies/jurisdictions/great_britain/`: British racing studies.

## AI retrieval instructions

1. Start with the task row above; inspect actual contents of the relevant file, not merely filenames.
2. For reader studies, follow the existing mandatory references listed in README; the map changes no process or priorities.
3. Treat existing validated data, governance and source files as authoritative; do not assume a parked idea is an active task.
4. If a linked file moves, repair this map when encountered; don't attempt to manually catalogue every generated notebook, test or dataset.
5. The immediate editorial aim is **publish existing near-ready work**, not open new research workstreams.

Related separate repository: [Rails Sports](https://github.com/rjmac22/rails-sports).
