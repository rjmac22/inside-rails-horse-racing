# Database v4 — Study 03 British racecourse/course identity integration

## Status

This document defines the **candidate-only** Database v4 integration of completed Study 03.

Database v3 remains the current accepted, immutable study database. This work does not mutate or replace it and does not create an accepted Database v4 release.

The completed Study 03 evidence snapshot is commit:

`5bb1b18482ddf59b3bdac7fc8545b675a9757df0`

The governed source of truth is:

- `studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`;
- the 60 notebooks under `studies/jurisdictions/great_britain/racecourses/`.

The canonical build entrypoint verifies that those notebook paths are unchanged from the completed Study 03 commit before constructing a candidate. Each venue notebook's exact build-time bytes are also recorded by SHA-256 in the candidate.

## Smallest correct model

Study 03 establishes four distinct layers:

1. existing source-facing `reference_course` identities;
2. governed British racecourse identity/grouping;
3. stable constituent course/track identity;
4. the Study 03 inventory rows from which stable course identity is resolved.

The integration therefore **does not redefine `reference_course`**. It adds a mapping from the existing 65 Great Britain source labels to 60 governed racecourse identities.

It also **does not assign a stable course/track ID to race occurrences**. A source course label often identifies only the parent racecourse, not which peer physical track was used. Creating race-to-track assignments would therefore fabricate information that Study 03 did not establish.

The governed cardinalities are fail-closed:

- 60 racecourse notebooks;
- 65 Great Britain source-label mappings;
- 60 governed racecourse identities/groupings;
- 90 Study 03 course/track inventory rows;
- 86 stable course/track identities;
- 7 unresolved governance records.

## New schema objects

### `governance_study03_racecourse_notebook`

One row per completed venue notebook. Stores the repository-relative notebook path, SHA-256 of the exact notebook bytes used for the build, the Study 03 evidence commit and the Database v4 governance release.

This keeps the build tied to explicit evidence rather than silently copying notebook conclusions into an untraceable reference table.

### `reference_racecourse_identity`

The 60 governed parent identities.

`identity_kind` is deliberately not hard-coded to "physical venue":

- `venue` for the ordinary parent identity;
- `analytical_grouping` for Newmarket, whose Study 03 parent groups the Rowley Mile and July Course even though official material describes those as two racecourses.

Operational status is not part of the identity. Historical identities such as Towcester remain valid identities.

### `reference_course_racecourse_map`

The exact 65-row bridge from the existing Great Britain `reference_course` population to the 60 governed parent identities.

The build reconciles the complete existing Great Britain `reference_course` key set against Study 03. Missing, extra or duplicate mappings fail the build.

### `reference_racecourse_course_identity`

The 86 stable course/track identities.

The only national Study 03 identity collapses are reproduced exactly:

- Southwell Fibresand and Tapeta inventory states → one `All-Weather Flat Track`;
- Newcastle former Flat turf and later Tapeta inventory states → one `Flat Track`;
- Windsor's traditional and temporary Jump configurations → one `Windsor Turf Course`.

Surface, temporary configuration and operating period are therefore not treated as durable identity by themselves.

### `reference_racecourse_course_inventory`

The 90 Study 03 inventory rows, each mapped to its stable course/track identity.

The source inventory name and surface are exposed directly. The complete original row is retained as canonical JSON so notebook-specific descriptive fields are not lost or prematurely normalised into a wider physical-track schema.

### `governance_racecourse_unresolved_question`

The seven unresolved Study 03 records remain explicit governance residue. They are not guessed, discarded or allowed to block already-established parent/course identities.

### Views

`view_gb_racecourse_identity_reference` exposes the safe 65-row source-label → governed-racecourse bridge.

`view_gb_course_track_identities` exposes the 86 stable course/track identities and the number of Study 03 inventory rows supporting each.

No existing race-facing view is multiplied by joining the 86 course identities.

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

The snapshot guard, 60 notebook SHA-256 rows and fixed Study 03 evidence commit preserve traceability to the full evidence record without duplicating the research notebooks into the database.

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
5. validates the exact governed population and reconciles the 65 Great Britain source labels to `reference_course`;
6. loads the new reference/governance tables transactionally;
7. checks persisted counts and the two new views;
8. runs `PRAGMA quick_check` and `PRAGMA foreign_key_check`;
9. verifies the accepted Database v3 hash is unchanged.

A failure removes the disposable output and leaves Database v3 untouched.

## Acceptance boundary

A successful build stops at:

`import_manifest.build_status = 'built'`

and reports:

`release_accepted = false`

This is intentional. The repository import gate requires independent source-wide validation plus the complete project acceptance gate before a successor database can be accepted.

The next release step is therefore to add an independent Database v4 validator, deliberately update the governed validator inventory/procedure, run the complete repository suite and applicable-validator gate, and only then define Database v4 promotion/acceptance.
