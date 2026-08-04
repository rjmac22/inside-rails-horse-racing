# Notebook 21 Closeout — Comment and Embedded Information

## Status

**Fully closed on the retrospective implementation branch.**

The analytical investigation, durable implementation, focused validation, complete repository test suite, all applicable independent validators, cross-notebook repairs and field-governance reconciliation were completed on 4 August 2026.

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

The notebook was restarted and rerun from the beginning during construction after the unsafe jurisdiction cell was deleted. Temporary SQL state is created only in a separate writable temporary analytics database; the source database remains read-only and immutable.

Historical failed approaches were removed or replaced:

- a source-wide Series-returning row-wise jurisdiction operation that exhausted the kernel;
- an attempted temporary-table write against the immutable source connection;
- a pandas grouping-column retention failure in an intermediate sampling cell.

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

Final governed conclusions were derived from source-internal profiling and direct inspection. An informal specialist suggestion about isolated letter values was treated as a hypothesis, not accepted as validation, and was not supported by source testing.

## Persisted outputs

- `data/processed/comment_information/comment_source_profile.csv`;
- `data/processed/comment_information/comment_semantic_decisions.csv`.

Focused tests reload and verify both files.

## Reusable implementation

- `src/inside_rails/comment_information.py` preserves raw text and assigns only conservative source states.

No narrative, incident, market or attributed-report parser is implemented because the evidence does not support a complete deterministic rule.

## Focused validation

- `tests/test_comment_information.py`: **8 passed in 0.46s**;
- `scripts/validate_comment_information.py`: **PASS** across 1,851,285 governed runner rows and 189,043 provisional races.

Validated comment partition:

- empty rows: 340,394;
- probable-placeholder or unresolved-code rows: 238;
- substantive rows: 1,510,653;
- SQL null rows: 0.

## Branch-wide validation

Initial complete-suite execution exposed two integration defects:

1. a Great Britain prize-money value below the minor-unit boundary fell through to `currency_unresolved` rather than `invalid`;
2. the source-field governance loader did not yet permit the explicit `implemented_pending_validation` status used by later notebooks.

Both defects were repaired and covered by tests.

Final local branch evidence on 4 August 2026:

```text
256 passed in 0.96s
```

Every discovered `scripts/validate_*.py` validator then passed. The sweep covered all 26 validator scripts, including source-wide validators over the immutable 1,851,285-row population.

Notebook 08's lone raw starting-price value `F` remained exactly governed as unresolved. The starting-price validator passed while confirming:

```text
unresolved_rows: 1
observed={'F': 1}
expected={'F': 1}
```

Final governance reconciliation also passed:

```text
Field-governance validation passed.
Source rows checked: 1,851,285
Source fields governed: 37
Status totals:
  closed: 34
  implemented_with_governed_anomaly: 1
  preserve: 2

Source-field governance validation passed.
```

## Database and integration consequence

See `docs/COMMENT_INFORMATION_INTEGRATION.md`.

The raw comment remains an atomic source field. Conservative state classification is permitted. Any future extracted assertion must live separately with source row lineage, method/version, evidence span where possible, confidence and review status.

## Reader-facing report

See `docs/REPORT_21_COMMENT_AND_EMBEDDED_INFORMATION.md`.

## Lessons learned

See `docs/NOTEBOOK_21_LESSONS_LEARNED.md` and `docs/INSIDE_RAILS_PROJECT_LESSONS_LEARNED.md`.

## Closure consequence

The source-field investigation series is fully closed through Notebook 21. The next work is not another source-field semantics notebook.

Before physical database construction, complete the mandatory authority-response gate for Notebook 19. The next bounded analytical programme is participant identity:

1. Notebook 22 — jockey and trainer identity;
2. Notebook 23 — owner identity and ownership structures.

A final local clean-tree and branch-synchronisation check remains an operational branch-reconciliation step, not an analytical or implementation gap in Notebook 21.
