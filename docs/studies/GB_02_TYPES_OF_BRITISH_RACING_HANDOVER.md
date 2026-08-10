# Great Britain Study 02 — Types of British Racing Handover

## Status entering the study

Great Britain Study 01 — governance and structure — is fully closed on 10 August 2026.

Governing closeout record:

`docs/studies/GB_01_GOVERNANCE_AND_STRUCTURE_CLOSEOUT.md`

Study 01 established the scale and calendar structure of the British racing programme. Do not reopen its course-date meeting definition, physical-venue detour or race-type reliability audit unless new evidence creates a genuine correctness issue.

## Proposed notebook

`studies/jurisdictions/great_britain/02_types_of_british_racing.ipynb`

## Central reader-facing question

What kinds of racing make up British horse racing?

The notebook should answer one coherent conceptual and descriptive question. Do not extend it into the later racecourse study merely because course differences become interesting.

## Conceptual order

Begin with authoritative British racing terminology before querying the database.

Establish first:

1. the top-level relationship between Flat racing and Jump/National Hunt racing;
2. where Hurdle, Chase and National Hunt Flat races sit within that structure;
3. which terms are formal authority terminology and which are Inside Rails analytical labels;
4. whether the four study-facing broad values are sufficient for the bounded descriptive questions in this notebook.

Do not say that Britain has four equivalent top-level racing codes merely because the database exposes four broad race-type values.

Only after the conceptual structure is established should the notebook count or compare the categories.

## Accepted analytical database

Use accepted Database v3 read-only:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Preferred race interface:

`view_reconciled_race_occurrences`

Expected race rows across all jurisdictions: 189,043.

Great Britain population previously established: 111,634 races from 1 January 2015 through 27 May 2026.

Use the project read-only helper:

```python
from inside_rails.source_sqlite import connect_read_only
```

Do not query Source Version 1 directly unless the new question genuinely concerns raw source evidence.

## Race-type governance already completed

Do not reopen the `race_type_raw` reliability investigation as though it remains unresolved.

Supporting notebook:

`notebooks/race_type_raw_semantics.ipynb`

Established Great Britain raw distribution:

- Flat: 70,218;
- Hurdle: 22,645;
- Chase: 15,671;
- NH Flat: 3,100;
- total: 111,634;
- no blank or unexpected broad values.

The separate governance investigation found 25 externally verified incorrect Great Britain race-type assignments.

An independent stratified random pilot checked 200 additional Great Britain races, 50 from each stored category. All 200 externally checked races agreed with the stored broad type and none overlapped the 25 known errors.

Interpretation: the source field is structurally complete and generally reliable for broad descriptive Great Britain analysis, but it is not error-free.

Persistent pilot evidence:

`data/reference/gb_race_type_pilot_verification_200_verified.csv`

## Required study-facing race-type field

When race type is needed, use the governed post-v3 overlay and analyse `race_type_study`, not uncorrected `race_type_raw`.

Helper:

```python
from inside_rails.study_overlay import build_race_overlay_query
```

The base race SELECT passed to the helper must expose:

- `raw_date`;
- `raw_course`;
- `raw_off`;
- `race_type_raw`;
- `advertised_start_course_local`.

`raw_off` is present only because exact Source Version 1 date + course + off identity is required to join post-v3 corrections. Do not use `raw_off` as the preferred analytical or display time.

The overlay adds:

- `race_type_study`;
- `race_type_study_source`;
- `race_type_study_verification_id`;
- study-facing advertised-time fields and provenance;
- external actual-off fields where available.

Database v3 remains immutable.

Focused overlay tests previously passed five tests. The default pending register currently contains 31 race-level post-v3 resolutions: 25 race-type corrections, three advertised course-local time corrections and three actual-off enrichments.

## Existing corrected meeting-composition result

Study 01 already established the corrected composition of its 15,865 analytical course-date meetings:

- Flat-only: 9,786;
- National Hunt-only: 6,068;
- mixed Flat and National Hunt: 11.

The raw source field had made 25 meetings appear mixed. Fourteen of those apparent mixtures were artefacts of incorrect race-type classifications.

The final mixed share is about 0.07% of the course-date meetings in the Study 01 population.

This result may be reused as prior evidence where relevant. Do not rerun the old raw-field version or describe mixed meetings as absent.

## Likely analytical sequence after definitions are established

Keep the notebook question-led rather than prewriting the whole analysis. A sensible initial sequence is:

1. establish the authoritative Flat / Jump conceptual structure;
2. test whether the governed four-category field maps cleanly enough to that broad structure for descriptive use;
3. measure how much Great Britain racing is Flat versus Jump;
4. describe the composition of Jump racing across Hurdle, Chase and NH Flat;
5. if useful, show how the Flat/Jump balance changes through the year;
6. stop when those results answer what kinds of racing make up the British programme.

Do not automatically add course, class, handicap, betting or profitability analyses. Those are separate questions unless evidence from this notebook makes one necessary to explain the bounded result.

## Calendar cautions inherited from Study 01

The source period ends on 27 May 2026, so 2026 is partial and should not be placed on equal footing with complete calendar years in annual or monthly seasonality comparisons.

2020 is descriptively exceptional in several Study 01 programme measures. If this notebook performs seasonal or annual type comparisons, show 2020 rather than deleting it, but do not use it as the ordinary baseline without justification.

Do not assign a causal COVID explanation merely because 2020 looks unusual. A causal explanation requires separately governed external evidence.

## Racecourse question remains deferred

Do not treat `candidate_course_label` as a settled reader-facing definition of a physical racecourse.

Study 01 used `raw_date + candidate_course_label` only as an explicit analytical course-date meeting grouping.

The separate future question remains:

What does racecourse/course/physical venue mean officially and in Inside Rails data?

Resolve that before counting British racecourses or presenting course labels as physical venues.

## Research rhythm

Use one conceptual stage at a time:

question -> analysis -> result -> explanation -> appropriate visual -> next question

Inspect every output before deciding the next analysis.

Keep denominators, sample sizes, anomalies and uncertainty visible.

Do not create a graph merely because a table exists. Use the simplest visual that materially improves understanding. Bar charts start at zero. Avoid log scales that exaggerate tiny categories.

The notebook should stop when the reader-facing question has been answered rather than exhausting every possible cross-tabulation.

## Study-document workflow

Read the current required study references before beginning:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- `docs/STUDY_DATABASE_REFERENCE.md`;
- `docs/STUDY_DATA_ACCESS.md`;
- `docs/STUDY_REVISIT_REGISTER.md`.

At closeout use:

- `docs/NOTEBOOK_WRAP_UP_PROCEDURE.md`;
- `docs/STUDY_CLOSEOUT_REGISTER.md`.

The project plan now explicitly says to review the study-document burden after roughly three to five fully closed reader-facing studies and consolidate into leaner start/closeout guidance if the evidence supports it.

## Immediate first step

Create/open `02_types_of_british_racing.ipynb` and establish the authoritative Flat / Jump / Hurdle / Chase / National Hunt Flat terminology before running descriptive counts.
