# Project rules

1. Raw source files are immutable.
2. Every transformation must be reproducible.
3. Preserve original source values alongside canonical values where useful.
4. Investigate apparent duplicates before deleting anything.
5. Treat missingness and outliers according to racing-domain meaning.
6. Separate source, staging, relational core and analytical views.
7. Enforce reliable rules with database constraints and validation tests.
8. Keep notebooks concise, readable and suitable for publication.
9. Reusable logic belongs in `src/inside_rails/` after it is stable.
10. Record material assumptions, limitations and rejected alternatives.
11. Source Version 1 `off` and its database `raw_off` representation may be used for technical checks, database validation, provenance, source identity and record reconciliation. They must not be used as analytical variables or as evidence for substantive racing conclusions. Analytical race-time work must use a separately governed time concept appropriate to the question.
