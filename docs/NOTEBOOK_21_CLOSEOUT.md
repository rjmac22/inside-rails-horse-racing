# Notebook 21 Closeout — Comment and Embedded Information

## Status

**Implemented; focused local validation passed; pending end-of-series repository sweep.**

The analytical investigation and durable implementation are complete. Focused tests and the independent source-wide validator passed locally on 4 August 2026. Final closure now depends only on the complete repository test suite, all applicable validators, repair of any cross-notebook integration defects, and final branch reconciliation.

## Bounded question

What does the runner-level `comment` field contain, how consistently is it populated and structured, which information can be governed safely, and what must remain preserved as source free text?

## Final conclusion

Substantive comments are generally runner-level English-language descriptions of race position and performance. The meaning is broadly consistent across inspected jurisdictions, but availability differs sharply by jurisdiction and feed.

The field is valuable as raw evidence and for bounded manual or assisted analysis. Notebook 21 does not authorise a general parser. Exact raw text, source absence, unresolved short values, jurisdiction and lineage must remain recoverable.

## Evidence summary

- governed runner rows: **1,851,285**;
- provisional races: **189,043**;
- SQL nulls: **0**;
- empty strings: **340,394**;
- populated comments: **1,510,891**;
- distinct populated values: **1,426,745**;
- probable-placeholder or unresolved-code rows: **238**;
- substantive-text rows: **1,510,653**;
- candidate jurisdictions represented: **36**;
- unresolved candidate-jurisdiction races: **0**.

Great Britain and Ireland have complete comment coverage in this source. Several overseas feeds are sparse or selective. Cross-jurisdiction inspection found comparable in-running prose when comments were present.

## Reproducibility classification

Notebook 21 uses the **executable notebook route**.

The notebook was restarted and rerun from the beginning during construction after the unsafe jurisdiction cell was deleted. The saved notebook contains the successful analytical path and executed outputs. Temporary SQL state is created only in a separate writable temporary analytics database; the source database remains read-only and immutable.

Known historical failures during construction were:

- a source-wide Series-returning row-wise jurisdiction operation that exhausted the kernel;
- an attempted temporary-table write against the immutable source connection;
- a pandas grouping-column retention failure in an intermediate sampling cell.

Those approaches were removed or replaced. They are documented as workflow lessons and must not be restored.

## Raw evidence and lineage

- source database: `data/raw/form_2015-present/form_2015-present/raceform.db`;
- source table: `data`;
- governed predicate: `rowid <> 1`;
- source field: `comment`;
- source grain: runner-level source assertion;
- physical row lineage: `rowid` retained by the integration contract;
- raw values are never trimmed, rewritten or overwritten.

## Manual-verification decision

`not_applicable`

Final governed conclusions were derived from source-internal profiling and direct inspection of source rows. An informal specialist suggestion about isolated letter values was recorded as a hypothesis, was not accepted as external validation, and was not supported by source testing. No final correction, exception or enrichment depends on external evidence.

## Persisted outputs

- `data/processed/comment_information/comment_source_profile.csv`;
- `data/processed/comment_information/comment_semantic_decisions.csv`.

These preserve the compact source-wide baselines and the final decision register. They do not reproduce bulk comment text. Focused tests reload and verify both files.

## Reusable implementation

- `src/inside_rails/comment_information.py` preserves raw text and assigns only conservative source states.

No narrative, incident, market or attributed-report parser is implemented because the evidence does not support a complete deterministic rule.

## Focused tests

- `tests/test_comment_information.py` covers empty strings, unexpected nulls, probable placeholders, unresolved source codes, exact substantive preservation, leading whitespace, short substantive comments, and persisted-output reload checks.

Local result on 4 August 2026:

```text
........                                                                 [100%]
8 passed in 0.46s
```

## Independent validation

- `scripts/validate_comment_information.py` opens the source in read-only immutable mode;
- applies `rowid <> 1`;
- validates the full runner population and provisional race count;
- checks the complete comment-state partition;
- fails on changed null, blank, placeholder/code or substantive baselines.

Local result on 4 August 2026:

```text
runner_rows: 1,851,285
null_rows: 0
empty_rows: 340,394
placeholder_or_code_rows: 238
substantive_rows: 1,510,653
provisional_races: 189,043
comment information validation: PASS
```

## Database and integration consequence

See `docs/COMMENT_INFORMATION_INTEGRATION.md`.

The raw comment remains an atomic source field. Conservative state classification is permitted. Any future extracted assertion must live separately with source row lineage, method/version, evidence span where possible, confidence and review status.

## Reader-facing report

See `docs/REPORT_21_COMMENT_AND_EMBEDDED_INFORMATION.md`.

## Lessons learned

See `docs/NOTEBOOK_21_LESSONS_LEARNED.md` and the project-wide lessons document.

## Status-document updates

The following agree on the implemented Notebook 21 state and the remaining end-of-series gate:

- `data/reference/source_field_governance.csv`;
- `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md`;
- `README.md`;
- `docs/PROJECT_PLAN.md`;
- `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`.

## Remaining closure gate

1. run the complete repository test suite;
2. run every applicable independent validator, treating Notebook 08's lone governed `F` failure as expected evidence;
3. repair any cross-notebook integration defects;
4. record the exact branch-level validation evidence;
5. update this status to `fully closed` only after the recorded sweep passes;
6. verify a clean synchronized branch.
