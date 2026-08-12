# Great Britain Study 04 — Race Meetings and Fixtures Closeout

## Study

Notebook:

`studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`

Accepted analytical database:

`data/processed/database/releases/inside_rails_v4.sqlite3`

Database status: accepted, immutable and read-only.

Study population: 111,634 reconciled Great Britain race occurrences with governed racecourse identity.

## Bounded question

What does British racing mean by a **meeting** and a **fixture**, and are they the same thing?

## Final conclusion

They are not reliably the same conceptual unit.

A **fixture** is the more precise BHA administrative scheduling object. BHA evidence shows that fixture properties can change, including staging racecourse, date, race times and race programme. Historical BHA evidence also establishes that two separate fixtures can occur at the same racecourse on the same date.

Therefore `date + racecourse` is not a defensible universal fixture identity.

**Meeting** is a less precise contextual racing term. BHA usage can describe either an individual fixture or day's racing, or a wider named event spanning several dated fixtures.

**Raceday** is ordinary or operational terminology rather than a stronger persistent identity.

## Source-level analytical grouping

Database v4 can directly support the descriptive grouping **source racecourse-date group**.

Definition: the set of observed Great Britain race occurrences sharing one source date and one governed racecourse identity.

This is an analytical grouping only. It does not assert that the group is one BHA fixture, one BHA meeting, one complete scheduled race programme or one persistent administrative object.

## Boundary evidence

Study 04 deliberately tested cases where simplistic identity rules might fail. The evidence established that:

- one named multi-day meeting can contain separately dated fixtures;
- two fixtures can occur at one racecourse on one date;
- fixtures can be transferred between racecourses;
- fixtures can be rescheduled;
- fixture race times can be materially changed;
- races within the programme can change;
- large temporal gaps between completed races may reflect abandonment or void races rather than separate fixtures.

The 2026 transferred-fixture comparison was particularly important. BHA evidence retained the administrative history of Brighton and Chepstow fixtures that were subsequently staged elsewhere. Database v4 correctly retained the realised racing at Great Yarmouth, Bath and Windsor but could not reconstruct that original fixture history from completed results alone.

## Database consequence

**No Database v4 migration is authorised.**

Do not add inferred fixture IDs, inferred meeting IDs, inferred session IDs, a `date + racecourse` fixture key, temporal-gap fixture splitting or inferred transfer history.

The earlier Phase 3 proposal for a persistent **source meeting occurrence** is superseded on this point.

A genuine BHA fixture layer remains possible in principle but is deferred until a concrete analytical requirement justifies the acquisition and maintenance effort.

## Manual and external verification

Closeout decision: **captured**.

Six bounded Study 04 claims are preserved in `data/reference/manual_verifications.csv`:

- `ST04-FIXTURE-0001`
- `ST04-FIXTURE-0002`
- `ST04-FIXTURE-0003`
- `ST04-FIXTURE-0004`
- `ST04-FIXTURE-0005`
- `ST04-FIXTURE-0006`

All six are confirmed, high-confidence, evidence-only records.

Validation performed on 12 August 2026:

```text
11 passed in 0.55s

Manual-verification register passed: 93 governed rows.
Verification statuses:
  confirmed: 64
  contradicted: 10
  partially_confirmed: 1
  unresolved: 18
Database actions:
  evidence_only: 21
  label_equivalence: 2
  preserve_raw_unresolved: 19
  reference_enrichment: 8
  source_correction_candidate: 12
  source_supplementation: 31
```

## Reproducibility

Closeout route: **executable notebook**.

Fresh-kernel execution initially exposed two execution-environment dependencies: the notebook lacked an explicit setup cell, and relative `PYTHONPATH=src` did not survive nbconvert's notebook-directory working directory. The notebook was corrected to define its imports and accepted Database v4 path explicitly, and the final execution used the documented absolute project `PYTHONPATH`.

Final command:

```bash
PYTHONPATH=/home/rob/Documents/inside-rails-horse-racing/src \
jupyter nbconvert \
  --to notebook \
  --execute studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb \
  --output gb04_fresh_run.ipynb \
  --output-dir /tmp \
  --ExecutePreprocessor.timeout=600
```

Final result:

```text
[NbConvertApp] Writing 131929 bytes to /tmp/gb04_fresh_run.ipynb
```

Fresh-kernel execution passed on 12 August 2026.

## Persisted-output decision

No separate study-derived dataset is required. The analytical tables are deterministic notebook outputs derived from accepted Database v4.

## Reusable-implementation decision

No new production implementation is required. Study 04 establishes domain terminology and modelling boundaries rather than a reusable transformation, parser or classifier.

## Unit-test decision

No new Study 04 analytical unit tests are required. The only governed reusable artifact changed by the study is the manual-verification register, whose existing tests were updated to cover the six Study 04 rows.

## Independent-validator decision

No new source-wide Study 04 validator is required. The study creates no new source-wide transformation or identity layer. The existing manual-verification validator was applicable and passed.

## Revisit decision

No previously closed reader-facing study is invalidated. Study 01 explicitly described its date/course grouping as analytical rather than an official meeting or fixture definition.

The historical Phase 3 meeting-identity design is retained as design history but marked superseded where Study 04 provides stronger evidence.

## Important follow-up discovered at closeout

Study 04 identified a potentially more valuable use for BHA fixture/results evidence than constructing a fixture entity.

The BHA evidence may allow Inside Rails to test whether Source Version 1 contains every Great Britain race that actually produced an official result. This is a **race-population completeness** question.

A scheduled fixture absent from Source Version 1 is not sufficient evidence of a source defect because fixtures or individual races may be abandoned, cancelled, transferred or otherwise changed.

The stronger test is **official completed BHA race result → corresponding Inside Rails race occurrence**.

If an officially completed race cannot be reconciled to Source Version 1, that would represent a genuine source-population completeness defect.

## Next bounded investigation

**Are any Great Britain races that officially produced results missing from Source Version 1 / Database v4?**

This is deliberately separated from Study 04 rather than expanding the meeting/fixture study further.

## Lessons learned

1. Sporting terminology should be established before creating database entities.
2. Boundary cases are especially powerful for identity questions.
3. Results evidence and administrative scheduling evidence answer different questions.
4. Large temporal gaps are anomaly signals, not reliable fixture boundaries.
5. Do not build an entity merely because it can be built.
6. An apparently administrative source can have a more valuable validation use elsewhere.
7. Existing database documentation should be consulted before schema rediscovery.
8. Racing-time analysis should use governed racecourse-local time rather than raw source clock values.
9. Non-obvious notebook code must state its purpose, population, assumptions and limits.
10. Fresh-kernel execution remains valuable because it exposes dependencies hidden by interactive notebook state.

## Closeout status

**Fully closed — 12 August 2026.**

Analytical question: complete.

External evidence: captured.

Manual-verification tests: passed.

Manual-verification independent validator: passed.

Fresh-kernel execution: passed.

New production implementation: not applicable.

Database migration: not applicable.

New independent source-wide validator: not applicable.

Reader-facing report: preserved in the notebook.

Lessons learned: recorded above.

Successor audit/status register: `docs/STUDY_CLOSEOUT_REGISTER.md`.

Next bounded action: Great Britain race-population completeness audit.
