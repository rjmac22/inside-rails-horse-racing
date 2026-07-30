# Notebook 17 — Lessons Learned

## What proved harder than expected

The apparently simple `hg` field required full vocabulary decomposition, temporal analysis and source-history checks. The late appearance of trailing `1` showed that an equipment code can change meaning or coverage through a source-format change without any schema change.

## Wrong assumptions

- A populated first-time suffix cannot be assumed to exist throughout the source period.
- Local horse history cannot always validate a source-declared first-time marker.
- Rare values in `sex` were not additional categories; they were colour contamination.
- Published abbreviation tables do not necessarily describe every token used in an extracted source field.

## Scope expansion

The headgear work expanded into temporal and same-horse history analysis. This was justified because it changed the safe interpretation of the trailing suffix and prevented a false historical first-time feature.

## Automation and manual review

Source-wide profiling and parsing were appropriate for the 728,795 populated headgear rows. Manual review was faster and safer for the two sex anomalies and nine source-specific eyecover rows.

## Workflow errors not to repeat

- Read the wrap-up procedure before beginning closeout work, not after prompting from the user.
- Do not impose a fresh-kernel rerun when a completed notebook is better treated as an archival construction record.
- Move directly to durable external implementation and validation once the analytical notebook has served its purpose.
- Do not ask the user to perform repository closeout work that can be completed through the repository tools.

## Reusable assets created

- `src/inside_rails/runner_characteristics.py`;
- `tests/test_runner_characteristics.py`;
- `scripts/validate_runner_characteristics.py`;
- governed sex and headgear CSV outputs;
- database-integration documentation;
- reader-facing Notebook 17 report;
- permanent manual-verification records.

## Procedure change

The notebook wrap-up procedure now requires fresh-kernel restart safety only where future executable reruns are genuinely needed. Otherwise a notebook may be explicitly archived with persisted outputs and durable replacement validation outside the notebook.
