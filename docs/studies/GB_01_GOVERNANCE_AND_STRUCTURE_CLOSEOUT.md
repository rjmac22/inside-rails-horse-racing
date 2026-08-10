# Great Britain Study 01 — Governance and Structure Closeout

## Study

Notebook:

`studies/jurisdictions/great_britain/01_governance_and_structure.ipynb`

Supporting field-governance investigation:

`notebooks/race_type_raw_semantics.ipynb`

Accepted analytical database:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Database status: accepted, immutable, read-only.

Study population: 111,634 Great Britain races from 1 January 2015 through 27 May 2026.

## Bounded question

How is British racing organised at the level needed to describe the observed national racing programme coherently?

The notebook distinguishes official racing terminology from the study-specific grouping required for descriptive analysis, then measures meeting size, racing-day scale, weekly structure and seasonal structure.

## Analytical definition

For this study only, a **course-date meeting** is all Great Britain races sharing the same `raw_date` and `candidate_course_label`.

This is an explicit analytical grouping. It is not presented as a BHA definition of either a meeting or a fixture, and it is not a reader-facing definition of a distinct physical racecourse.

## Principal findings

Across 111,634 Great Britain races:

- 15,865 course-date meetings were observed;
- seven races was the most common meeting size and the median meeting size;
- 94.8% of meetings contained six to eight races;
- 4,016 British racing days were observed;
- the median racing day contained four course-date meetings and 28 races;
- Saturday carried the largest programme, with a median of five meetings and 38 races in complete non-2020 years;
- Sunday was materially smaller, with a median of two meetings and 14 races;
- racing nevertheless occurred on at least 97.5% of calendar dates for every weekday in the complete non-2020 comparison years;
- the programme expanded strongly into spring and summer;
- May was the busiest month by mean races per racing day in every complete non-2020 year from 2015 to 2025;
- the busiest-to-quietest monthly gap ranged from 10.9 to 15.2 races per racing day in every one of those years;
- 2020 was a clear structural exception in several measures and is not used as a normal-year baseline;
- 2026 is partial through 27 May and is not treated as a complete calendar year in annual comparisons.

The descriptive conclusion is that British racing operates as an almost-daily national programme built from relatively standard-sized individual cards, with a stable underlying daily scale but strong and repeatable weekly and seasonal variation.

## Supporting race-type investigation

The study exposed a material reliability question in `race_type_raw`, so that issue was moved out of the reader-facing study and investigated separately rather than being silently repaired in study code.

The supporting investigation established:

- all 111,634 Great Britain races have one of the four stored broad values `Flat`, `Hurdle`, `Chase` or `NH Flat`;
- 25 exact source classifications were externally verified as wrong and are governed through the read-only post-v3 study overlay;
- an independent stratified pilot of 200 additional races, 50 from each stored category, produced 200 external agreements and no additional disagreement;
- the field is therefore suitable for broad descriptive work when known exact corrections are applied, but it is not claimed to be error-free.

The correction materially changed a rare-category result: 25 apparent mixed Flat/National Hunt course-date meetings under the raw field became 11 genuine mixed meetings after the verified corrections. The final corrected meeting composition was 9,786 Flat-only, 6,068 National Hunt-only and 11 mixed meetings.

## Manual and external verification

Closeout decision: **captured**.

The general governance claims used by this notebook are recorded in `data/reference/manual_verifications.csv`:

- `ST01-GOV-0001` — BHA governance, administration and regulation role;
- `ST01-GOV-0002` — official BHA distinction between the fixture list and race programmes.

Both are high-confidence `evidence_only` records. They support terminology and interpretation and do not alter Database v3.

The race-type correction evidence is retained in the specialist post-v3 verification and resolution artifacts rather than duplicated in the general manual-verification register.

## Reproducibility

Closeout route: **executable notebook**.

On 10 August 2026 the study notebook was executed from top to bottom in a fresh kernel against accepted Database v3 using the documented repository environment:

```text
PYTHONPATH=/home/rob/Documents/inside-rails-horse-racing/src
```

The successful command wrote a temporary executed copy to:

`/tmp/gb_governance_fresh_run.ipynb`

No analytical cell failed.

An initial attempt without the documented `PYTHONPATH` failed before analysis because the `inside_rails` package could not be imported. No notebook-local `sys.path` workaround was added; rerunning under the documented environment succeeded.

## Persisted outputs

No separate governed data product is required for the main descriptive study.

The tables and figures are study-specific derivations that are regenerated deterministically from accepted Database v3 when the notebook is executed. Creating duplicate CSV exports of each descriptive table would add storage and maintenance without creating a reusable analytical contract.

Persistent evidence required by the supporting race-type investigation is retained separately, including:

- `data/reference/gb_race_type_pilot_verification_200_verified.csv`;
- the governed post-v3 external verification candidate and resolution registers.

## Reusable implementation decision

**No new reusable implementation is required for the main study.**

The course-date meeting grouping is intentionally a study-specific analytical definition and should not be promoted into Database v3 or a production module as though it were an official racing entity.

The only correctness-critical reusable requirement discovered by the study was application of known post-v3 corrections. That requirement is already handled by `inside_rails.study_overlay`, which keeps Database v3 immutable while exposing governed study-facing values.

## Unit-test decision

**No new unit tests are required for the main descriptive calculations.**

The notebook does not introduce a parser, canonical transformation, reusable classifier or governed reference loader.

The supporting overlay already has focused tests in `tests/test_study_overlay.py`, including failure behaviour for duplicate resolutions, unsupported fields and invalid resolution treatment, plus a guard that the default register contains all 25 verified race-type corrections. The focused overlay test run performed during the supporting investigation passed five tests.

## Independent-validator decision

**No new independent source-wide validator is required for the main study.**

The study creates no new source-wide transformation or governed reference that needs a production admission gate. Its population and descriptive outputs are regenerated directly from the accepted read-only database and the already-governed study overlay.

This decision must not be read as a general exemption for reader-facing studies. A future study that creates a reusable governed transformation or reference must still add independent validation under the normal closeout rules.

## Database and integration consequence

**No Database v3 migration is authorised by this study.**

- Database v3 remains unchanged and read-only.
- `raw_date + candidate_course_label` remains a study definition rather than a new database entity.
- `candidate_course_label` is not promoted to a definition of a physical racecourse.
- the known race-type corrections remain in the governed post-v3 overlay pending a future database release decision.
- the separate question of course identity versus physical venue is explicitly deferred to a later racecourse study.

## Confidence and limitations

Confidence is high for the descriptive structural findings within the declared Great Britain population.

Important limits are:

- the course-date meeting is analytical rather than an official BHA entity definition;
- 2026 is incomplete;
- 2020 is descriptively exceptional, but this study does not assign a causal explanation without separately governed external evidence;
- the study describes programme organisation and scale, not commercial importance, scheduling motives, causal effects or betting value;
- racecourse identity and physical-venue semantics remain outside scope;
- detailed Flat-versus-Jump structure belongs to the next bounded study rather than being appended to this notebook.

## Revisit-register decision

No completed or published earlier reader-facing study is identified as materially invalidated by this work, so no `STUDY_REVISIT_REGISTER` entry is required at closeout.

The race-type investigation corrected the current study before closure rather than creating a later change to a previously closed result.

## Reader-facing report

### Executive conclusion

British racing is an almost-daily national programme assembled from relatively standard-sized individual cards. A typical course-date meeting contains seven races; a typical national racing day contains about four meetings and 28 races. The programme is systematically larger on Saturdays and through late spring and summer, while 2020 is a clear exception to the otherwise stable observed structure.

### Core evidence

The conclusion is based on 111,634 Great Britain races, 15,865 course-date meetings and 4,016 racing days from 1 January 2015 through 27 May 2026, with complete non-2020 years used where a normal annual, weekly or seasonal comparison is required.

### Interpretation

The observed programme has both a stable core scale and a repeatable calendar rhythm. The evidence supports describing what a normal British racing programme looks like; it does not establish why the programme is scheduled that way.

### Practical implication

Readers can treat a seven-race card and roughly four-meeting national day as useful descriptive reference points, while recognising that Saturdays and spring/summer dates usually carry materially more racing. These are empirical patterns, not regulatory rules.

### Next action

Open a separate bounded study of the **types of British racing** before moving on to racecourses.

## Lessons learned

1. **A reader-facing notebook needs a stopping rule.** One notebook should answer one coherent reader question plus only the subquestions needed to support it. Interesting adjacent questions should become later notebooks rather than extending the current one indefinitely.
2. **Field-governance detours should leave the study when correctness is at stake.** The race-type issue was correctly moved into a separate governance notebook. That prevented an ad-hoc study repair from becoming an undocumented rule.
3. **Rare categories are disproportionately vulnerable to small source-error counts.** Fourteen wrong race-type assignments materially distorted an apparent 25-meeting mixed category even though the broad field was generally reliable.
4. **Optional enrichment must not silently become identity.** Using nullable physical-venue enrichment as the meeting grouping collapsed unrelated races. The analytical course label was sufficient for this study, while the deeper racecourse/venue question was deferred.
5. **Reproducibility depends on the documented execution environment.** The first fresh-kernel command failed because `PYTHONPATH` was absent; the correct response was to use the project environment, not add a notebook path hack.
6. **Not every study needs new production code, tests and validators.** Applicability must be decided explicitly. Descriptive calculations that create no reusable governed contract should not generate ceremonial infrastructure.
7. **The study documentation set should itself be reviewed empirically.** After several reader-facing studies have been completed, review which pre-study and closeout documents genuinely prevented errors and which merely duplicated instructions. Consider consolidating them into lean study-start and study-closeout guides while retaining detailed database documents for cases that actually touch those concerns.

## Closeout status

Analytical work: complete.

Fresh-kernel reproducibility: passed.

Manual/external evidence: captured.

Main-study reusable implementation: not applicable.

Main-study new unit tests: not applicable.

Main-study new independent validator: not applicable.

Database migration: not applicable.

Reader-facing report: recorded above.

Lessons learned: recorded above.

README / project plan / audit register: must be updated to point to this closeout and the next bounded study.

Local validation still required before the notebook is labelled **fully closed**: rerun the applicable manual-verification/register validation after the two Study 01 BHA evidence rows, and record the result. Until that final check is recorded, the precise status is **analytically complete, closeout pending local validation**.
