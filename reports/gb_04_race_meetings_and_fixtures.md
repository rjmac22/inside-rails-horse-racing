# Great Britain Study 04 — Race Meetings and Fixtures

## Conclusion

A **fixture** and a **meeting** are not reliably the same conceptual unit in British racing.

The official evidence supports treating a fixture as the more precise administrative scheduling object. The term meeting is more contextual and can refer either to an individual day's racing or to a wider named event covering several dated fixtures.

The study also established that **`date + racecourse` is not a universal fixture identity**. Two fixtures can occur at one racecourse on the same date, while fixture dates, staging racecourses, times and programmes can also change.

## Database consequence

Database v4 can safely support a descriptive **source racecourse-date group** for observed races sharing one source date and one governed racecourse identity. That grouping is analytical only; it is not claimed to be an official fixture or meeting identity.

Study 04 therefore added no inferred fixture IDs, meeting IDs or session IDs to Database v4.

## Follow-up

The official fixture and result evidence revealed a more useful next question: whether every Great Britain race that officially produced a result is represented in the Inside Rails source population. That completeness audit was separated from Study 04.

## Technical record

- [Study notebook](../studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb)
- [Formal closeout](../docs/studies/GB_04_RACE_MEETINGS_AND_FIXTURES_CLOSEOUT.md)
- [Closeout register](../docs/STUDY_CLOSEOUT_REGISTER.md)

**Status: fully closed — 12 August 2026.**
