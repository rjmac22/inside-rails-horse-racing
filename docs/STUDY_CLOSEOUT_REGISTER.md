# Inside Rails Reader Study Closeout Register

## Purpose

This register records the concise closure state of reader-facing studies. Detailed evidence remains in the study notebooks, handovers/closeout documents and database release records.

## Status vocabulary

- `in_progress` — analytical work is active;
- `analytically_complete` — the bounded question has been answered, but closeout work remains;
- `closeout_validation_pending` — analytical/documentation closeout is complete but required validation evidence is not yet recorded;
- `fully_closed` — every applicable closeout item is complete and the resulting reusable state is recorded;
- `revisit_required` — a later finding materially affects a previously closed study and the revisit register governs the next action.

## Studies

| Study | Notebook / evidence | Main reusable consequence | Closeout status | Next action |
|---|---|---|---|---|
| Great Britain 01 — Governance and structure | `studies/jurisdictions/great_britain/01_governance_and_structure.ipynb` | established programme/calendar structure; course-date meeting remained explicitly analytical | `fully_closed` | completed |
| Great Britain 02 — Types of British racing | `studies/jurisdictions/great_britain/02_types_of_british_racing.ipynb`; `docs/studies/GB_02_TYPES_OF_BRITISH_RACING_HANDOVER.md` | authoritative Flat/Jump conceptual structure; governed broad race-type analysis | `fully_closed` | completed |
| Great Britain 03 — British racecourse/course identity | `studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb` plus 61 racecourse notebooks | 61 racecourse identities, 65 source mappings, 86 stable course/track identities; integrated into accepted Database v4 | `fully_closed` | completed |
| Great Britain 04 — Race meetings and fixtures | `studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`; `docs/studies/GB_04_RACE_MEETINGS_AND_FIXTURES_CLOSEOUT.md` | fixture/meeting semantics established; source racecourse-date group retained as analytical only; no fixture entity implemented | `fully_closed` | audit GB race-population completeness |

## Great Britain Study 01

Governing closeout record:

`docs/studies/GB_01_GOVERNANCE_AND_STRUCTURE_CLOSEOUT.md`

Fresh-kernel execution passed on 10 August 2026. The governed manual-verification register passed at the Study 01 boundary with 87 rows.

Study 01 deliberately did **not** settle the official meaning of racecourse or meeting. Its `raw_date + candidate_course_label` grouping was an analytical device for describing programme structure.

## Great Britain Study 02

Handover / study-start record:

`docs/studies/GB_02_TYPES_OF_BRITISH_RACING_HANDOVER.md`

Study 02 established the authoritative conceptual relationship between Flat racing and Jump/National Hunt racing before using the governed analytical broad race-type values.

Known verified broad race-type corrections remain governed through the read-only post-release overlay where they are not native to the accepted database.

## Great Britain Study 03

National notebook:

`studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`

Evidence base:

- 61 per-racecourse notebooks under `studies/jurisdictions/great_britain/racecourses/`;
- corrected frozen evidence commit `01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b`.

Final governed baseline:

```text
racecourse notebooks: 61
GB source-label mappings: 65
governed racecourse identities: 61
course/track inventory rows: 90
stable course/track identities: 86
unresolved governance rows: 7
```

Study 03 established the modelling distinction:

> `racecourse -> course/track -> time-bounded characteristics`

The Newmarket correction is explicit:

- plain `Newmarket` → `Newmarket — Rowley Mile`;
- `Newmarket (July)` → `Newmarket — July Course`.

There is no synthetic combined Newmarket racecourse identity.

Study 03 was integrated into accepted Database v4 on 12 August 2026.

Accepted v4 release:

```text
path: data/processed/database/releases/inside_rails_v4.sqlite3
SHA-256: 45ad0c3d81d457385d655d9c47b030c5815c638e477281a9be8aabf164eecff7
manifest status: release_accepted
user_version: 4
```

Final release-boundary evidence:

```text
focused tests: 13 passed in 1.11s
complete repository suite: 435 passed in 15.47s
applicable independent validators: 32 passed
standalone v4 validator: passed
promotion: release_accepted=true
```

Full release record:

`docs/DATABASE_V4_RELEASE_ACCEPTANCE_AND_PROMOTION.md`

## Great Britain Study 04

National notebook:

`studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`

Closeout record:

`docs/studies/GB_04_RACE_MEETINGS_AND_FIXTURES_CLOSEOUT.md`

Study 04 established that **fixture** is the more precise BHA administrative scheduling object, while **meeting** is context-dependent and may refer either to one fixture/day or to a wider multi-day event.

Database v4 cannot reconstruct persistent BHA fixture identity from completed race results alone.

The accepted source-level analytical term is **source racecourse-date group**.

No meeting, fixture or session entity was added to Database v4.

Fresh-kernel execution passed on 12 August 2026.

Six Study 04 BHA evidence claims are governed in the manual-verification register. The focused manual-verification test passed with 11 tests and the independent register validator passed with 93 governed rows.

## Next bounded investigation

Audit Great Britain race-population completeness:

**Are any Great Britain races that officially produced results missing from Source Version 1 / Database v4?**

Use authoritative completed-race evidence as the external population reference. Do not mistake a scheduled but abandoned or cancelled fixture for a missing source race.
