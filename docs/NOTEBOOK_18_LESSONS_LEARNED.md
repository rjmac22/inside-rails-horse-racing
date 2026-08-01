# Notebook 18 — Lessons Learned

## Analytical lessons

- Shared storage location does not imply shared meaning. Official marks, retrospective performance ratings and speed figures require separate semantics and timing.
- Physical missing-value profiling must inspect exact Unicode tokens. Searching only for an ASCII hyphen would have missed every unavailable rating.
- An extreme value should not be corrected from appearance alone. The source-wide distribution established that `rpr = 775` was invalid, but not whether the intended value was 75 or unavailable.
- Exact source lineage permits a narrow governed exclusion without imposing a speculative global range rule.
- Availability combinations are useful only until they answer the governance question. Once independent nullability was established, further combination profiling would have been scope drift.

## Database lessons

- Preserve raw values even when an analytical value is excluded.
- Give each rating field an independent parsed value and status.
- Keep observed source ranges as regression baselines rather than universal business rules.
- Unexpected future representations should remain unresolved instead of being silently coerced.
- A generic `rating_available` field would erase meaningful differences between producers and purposes.

## Process lessons

- Capture external semantic evidence in the permanent verification register while the source is still open.
- Update count-sensitive register tests in the same change as new verification rows.
- Commit the analytical notebook before attempting remote notebook edits.
- Treat a timed-out GitHub write as unknown until the remote file is checked; it may have completed successfully.
- Do not force full-suite or all-validator execution during an unfinished notebook series. Use focused implementation tests and the notebook-specific validator, then reserve the project-wide sweep for series closeout.

## Reusable assets created

- `src/inside_rails/ratings.py`;
- `tests/test_ratings.py`;
- `scripts/validate_ratings.py`;
- `docs/NOTEBOOK_18_RATINGS_DATABASE_INTEGRATION.md`;
- `docs/NOTEBOOK_18_RATINGS_REPORT.md`;
- permanent verification records `NB18-OR-0001`, `NB18-RPR-0001` and `NB18-TS-0001`.

## Validation outcome

Notebook 18 closeout validation passed locally on 1 August 2026:

- `22 passed in 0.06s` across `tests/test_ratings.py` and `tests/test_manual_verifications.py`;
- the independent ratings validator passed across **1,851,285** governed runner rows;
- `or`: **1,116,633 available**, **734,652 unavailable**, **0 invalid**, observed candidate range **1–181**;
- `rpr`: **1,644,175 available**, **207,109 unavailable**, **1 invalid**, observed candidate range **1–184**;
- `ts`: **1,227,384 available**, **623,901 unavailable**, **0 invalid**, observed candidate range **1–178**;
- the manual-verification validator passed across **36 governed rows**;
- verification statuses: **25 confirmed**, **10 contradicted**, **1 partially confirmed**;
- database actions: **13 evidence-only**, **1 preserve-raw-unresolved**, **8 reference-enrichment**, **11 source-correction-candidate**, **3 source-supplementation**.

The complete repository test suite and all-validator sweep remain deferred until the end of the source-field series or repair branch.
