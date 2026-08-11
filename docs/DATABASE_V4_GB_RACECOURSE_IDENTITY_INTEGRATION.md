# Database v4 — Study 03 British racecourse/course identity integration

## Status

This document defines the **candidate-only** Database v4 integration of completed Study 03.

Database v3 remains the current accepted, immutable study database. This work does not mutate or replace it and does not create an accepted Database v4 release.

The completed Study 03 evidence snapshot is commit:

`5bb1b18482ddf59b3bdac7fc8545b675a9757df0`

The governed Study 03 source of truth is:

- `studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`;
- the 60 notebooks under `studies/jurisdictions/great_britain/racecourses/`.

The canonical build entrypoint verifies that those notebook paths are unchanged from the completed Study 03 commit before constructing a candidate. Each venue notebook's exact build-time bytes are also recorded by SHA-256 in the candidate.

## Smallest correct model

Study 03 establishes four distinct evidence layers:

1. existing source-facing `reference_course` identities;
2. 60 governed British racecourse parent/grouping records in the completed research notebooks;
3. stable constituent course/track identity;
4. the Study 03 inventory rows from which stable course identity is resolved.

Database v4 keeps those completed notebooks immutable but adds one further database-consumer distinction that became necessary before Study 04: **the actual racecourse identity to which a Source Version 1 race should attach**.

For 59 ordinary Study 03 parent identities, the research parent is already the racecourse identity. Newmarket is different. The completed Newmarket notebook deliberately used one analytical parent, `Newmarket`, over two officially established peer racecourses: the Rowley Mile and the July Course. Database v4 therefore preserves `Newmarket` as the Study 03 grouping name on the source-label bridge but resolves it into two actual racecourse identities for Source Version 1.

The final Database v4 cardinalities are fail-closed:

- 60 racecourse evidence notebooks;
- 65 Great Britain source-label mappings;
- 60 Study 03 parent/grouping identities represented by those mappings;
- **61 Source Version 1 racecourse identities** after the Newmarket split;
- 90 Study 03 course/track inventory rows;
- 86 stable course/track identities;
- 7 unresolved governance records.

The integration still **does not assign a physical course/track ID to race occurrences**. It establishes racecourse-level identity only. A source label often does not identify which peer physical track, course configuration, rail position or route was used.

## Newmarket Source Version 1 resolution

### Official structure

The Jockey Club explicitly states that Newmarket has two racecourses: the **Rowley Mile** and the **July Course**.

Official evidence used by the completed Study 03 Newmarket notebook includes:

- `https://www.thejockeyclub.co.uk/newmarket/about/`
- `https://www.thejockeyclub.co.uk/newmarket/owners-and-trainers/arrival/`

The official Newmarket racecourse map likewise identifies separate Rowley Mile and July Course racecourses:

- `https://www.thejockeyclub.co.uk/newmarket/plan-your-day/racecourse-map/`

### Source-label convention

Source Version 1 contains two distinct Newmarket source labels:

- `Newmarket`
- `Newmarket (July)`

The explicit `(July)` qualifier gives direct evidence for:

`Newmarket (July)` → `Newmarket — July Course`

The plain label is resolved as:

`Newmarket` → `Newmarket — Rowley Mile`

by a **Source Version 1 label convention**, not by treating the word `Newmarket` in isolation as proof.

The convention is supported by external dated evidence across the source period. Examples include:

- Racing Post results for 31 July 2015 label the meeting `NEWMARKET (JULY)`:
  `https://www.racingpost.com/results/2015-07-31`
- Racing Post results for 31 October 2015 label the meeting `NEWMARKET`:
  `https://www.racingpost.com/results/2015-10-31`
- Jockey Club reporting from July 2020 explicitly describes racing moving from the Rowley Mile to the July Course for July and August:
  `https://www.thejockeyclub.co.uk/newmarket/media/news/2020/07/notice-about-exercising-around-the-july-course/`

The build records different resolution methods so the distinction remains visible:

- `Newmarket (July)` → `explicit_source_label`;
- `Newmarket` → `source_label_convention`;
- ordinary Study 03 mappings → `study03_identity_direct`.

This rule is **bounded to Source Version 1**. A future source version must revalidate its Newmarket naming convention. It must not silently inherit `Newmarket` → Rowley Mile merely because Database v4 used that interpretation for Source Version 1.

## New schema objects and semantics

### `governance_study03_racecourse_notebook`

One row per completed venue notebook. Stores the repository-relative notebook path, SHA-256 of the exact notebook bytes used for the build, the Study 03 evidence commit and the Database v4 governance release.

This keeps the build tied to explicit evidence rather than silently copying notebook conclusions into an untraceable reference table.

### `reference_racecourse_identity`

The final Source Version 1 racecourse identity layer.

After the bounded Source Version 1 refinement it contains **61** rows. The completed Study 03 `Newmarket` analytical parent is converted into:

- `Newmarket — Rowley Mile`;
- `Newmarket — July Course`.

Both are `venue` identities. The original completed-research grouping name remains recoverable on the mapping bridge rather than being misrepresented as a third Newmarket racecourse.

Operational status is not part of identity. Historical identities such as Towcester remain valid identities.

### `reference_course_racecourse_map`

The exact 65-row bridge from the existing Great Britain `reference_course` population to the final Source Version 1 racecourse identities.

In addition to the target racecourse ID, each row stores:

- `study03_grouping_name` — the parent/grouping name from the completed Study 03 evidence;
- `racecourse_resolution_method` — how the source label was resolved at racecourse level;
- `racecourse_resolution_evidence` — the evidence pointer for that resolution.

The build reconciles the complete existing Great Britain `reference_course` key set against Study 03. Missing, extra, duplicate or pending mappings fail the build.

### `reference_racecourse_course_identity`

The 86 stable course/track identities.

The only national Study 03 identity collapses remain exactly:

- Southwell Fibresand and Tapeta inventory states → one `All-Weather Flat Track`;
- Newcastle former Flat turf and later Tapeta inventory states → one `Flat Track`;
- Windsor's traditional and temporary Jump configurations → one `Windsor Turf Course`.

For Newmarket, the Rowley Mile course identity belongs to `Newmarket — Rowley Mile` and the July Course identity belongs to `Newmarket — July Course`.

Surface, temporary configuration and operating period are therefore not treated as durable identity by themselves.

### `reference_racecourse_course_inventory`

The 90 Study 03 inventory rows, each mapped to its stable course/track identity.

The source inventory name and surface are exposed directly. The complete original row is retained as canonical JSON so notebook-specific descriptive fields are not lost or prematurely normalised into a wider physical-track schema.

### `governance_racecourse_unresolved_question`

The seven unresolved Study 03 records remain explicit governance residue. They are not guessed, discarded or allowed to block already-established parent/course identities.

### Views

`view_gb_racecourse_identity_reference` exposes the 65-row source-label → final racecourse bridge, including the original Study 03 grouping and resolution method/evidence.

`view_gb_course_track_identities` exposes the 86 stable course/track identities and the number of Study 03 inventory rows supporting each.

`view_gb_reconciled_race_occurrences_with_racecourse` is the Study 04-facing race-level interface. It preserves one row per Great Britain race occurrence from `view_reconciled_race_occurrences` and adds:

- `racecourse_identity_id`;
- `racecourse_identity_code`;
- `governed_racecourse_name`;
- `racecourse_identity_kind`;
- `study03_grouping_name`;
- `racecourse_resolution_method`;
- `racecourse_resolution_evidence`.

The builder verifies that this view has exactly the same number of rows and distinct race-occurrence IDs as the Great Britain population in `view_reconciled_race_occurrences`. It therefore cannot silently multiply races through the racecourse join.

No existing race-facing view is joined to the 86 stable course identities, so no race is fabricated as having used a particular physical track.

## Deliberately excluded from Database v4 candidate scope

This integration does **not** add:

- race-occurrence → physical-track assignment;
- rail/dolling/start-position geometry;
- route or spur identities below the Study 03 stable course layer;
- surveyed track geometry;
- a duplicate course-location system;
- all 1,902 assertion-level provenance rows or all bibliographic source records;
- a generic EAV characteristics model;
- a promotion/acceptance path.

The snapshot guard, 60 notebook SHA-256 rows, fixed Study 03 evidence commit and explicit Source Version 1 resolution metadata preserve traceability without duplicating the complete research notebooks into the database.

## Candidate build

From the repository root:

```bash
python scripts/build_inside_rails_v4.py
```

Default immutable base:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Default output:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

The canonical build first fails closed unless the Study 03 top-level notebook and racecourse-notebook directory match the completed Study 03 evidence commit. It then verifies the exact accepted Database v3 SHA-256, size, release code, schema version, manifest state, validation count and governance lineage before copying it.

It then:

1. creates a disposable copy;
2. migrates schema version 3 → 4;
3. creates the Database v4 governance method/release and import manifest;
4. parses only static `pd.DataFrame` declarations from the 60 Study 03 notebooks;
5. validates the exact completed Study 03 population and reconciles the 65 Great Britain source labels to `reference_course`;
6. applies the bounded Source Version 1 racecourse refinement, splitting the completed Newmarket analytical parent into Rowley Mile and July Course racecourses;
7. loads and checks the 61-racecourse final identity layer, 90 inventory rows, 86 stable course identities and seven unresolved rows;
8. verifies the 65-row source-label view and one-row-per-GB-race Study 04-facing racecourse view;
9. runs `PRAGMA quick_check` and `PRAGMA foreign_key_check`;
10. verifies the accepted Database v3 hash is unchanged.

A failure removes the disposable output and leaves Database v3 untouched.

## Acceptance boundary

A successful build stops at:

`import_manifest.build_status = 'built'`

and reports:

`release_accepted = false`

This is intentional. The repository import gate requires independent source-wide validation plus the complete project acceptance gate before a successor database can be accepted.

The next release step is therefore to add an independent Database v4 validator, deliberately update the governed validator inventory/procedure, run the complete repository suite and applicable-validator gate, and only then define Database v4 promotion/acceptance.
