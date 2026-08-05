# Notebook 18 Closeout — Ratings Semantics and Availability

## Status

**Analytically closed; semantic-provenance validation repaired.**

Notebook 18’s parser, exact RPR anomaly and source-wide availability counts remain unchanged. The cross-notebook audit found that the independent validator did not protect the three publisher-reference decisions defining the meanings of `or`, `rpr` and `ts`.

## Bounded conclusion

- `or` is a current pre-race official handicap mark applicable to the runner for the race;
- `rpr` is a retrospective Racing Post performance rating and may later be revised;
- `ts` is a retrospective speed figure for the completed performance.

The three fields are not interchangeable and must keep separate values and availability states.

## Durable implementation

- parser: `src/inside_rails/ratings.py`;
- focused tests: `tests/test_ratings.py`;
- independent validator: `scripts/validate_ratings.py`;
- integration contract: `docs/NOTEBOOK_18_RATINGS_DATABASE_INTEGRATION.md`;
- report: `docs/NOTEBOOK_18_RATINGS_REPORT.md`;
- lessons: `docs/NOTEBOOK_18_LESSONS_LEARNED.md`;
- permanent semantic evidence: `data/reference/manual_verifications.csv`.

## Governed semantic evidence

The exact three-record partition is:

- `NB18-OR-0001`;
- `NB18-RPR-0001`;
- `NB18-TS-0001`.

All are confirmed high-confidence publisher-reference enrichments accessed on 1 August 2026. The validator now enforces each exact semantic statement, source field, raw token, evidence locator, notebook assignment and database action.

## Source-wide baselines

| Field | Available | Unavailable | Invalid | Candidate range |
|---|---:|---:|---:|---:|
| `or` | 1,116,633 | 734,652 | 0 | 1–181 |
| `rpr` | 1,644,175 | 207,109 | 1 | 1–184 |
| `ts` | 1,227,384 | 623,901 | 0 | 1–178 |

The governed population is 1,851,285 runner rows.

Source rowid `1619851` retains the exact invalid `rpr=775` anomaly. It remains null analytically with status `invalid_source_value`; no replacement value is inferred.

## Manual-verification decision

`captured`

The three publisher records are permanent semantic evidence, not row-level correction mappings.

## Database consequence

Preserve all three raw fields and separate analytical integers and statuses. Do not convert unavailable values to zero. Do not require all three ratings for general runner usability. Apply the exact RPR anomaly only to its physical source row and raw value.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_ratings.py
PYTHONPATH=src .venv/bin/python scripts/validate_ratings.py
```

Both must pass locally before this review unit is accepted. Full repository and all-validator runs remain deferred until the final repair-series gate.
