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

## Validation status

The manual-verification register has already passed its focused test and validator with 36 governed rows.

The ratings implementation and source-wide validator must be executed locally against the immutable source before Notebook 18 is marked fully closed. Exact outputs should be recorded here after that run.
