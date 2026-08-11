# Database v4 — Study 03 British racecourse/course identity integration

## Status

This document defines the **candidate-only** Database v4 integration of completed Study 03.

Database v3 remains the current accepted, immutable study database. This work does not mutate or replace it and does not create an accepted Database v4 release.

The corrected completed Study 03 evidence snapshot is commit:

`01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b`

The governed Study 03 source of truth is:

- `studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`;
- the **61 racecourse notebooks** under `studies/jurisdictions/great_britain/racecourses/`.

The canonical build fails closed unless those study paths are unchanged from the fixed Study 03 evidence commit. Each racecourse notebook's exact build-time bytes are also recorded by SHA-256 in the candidate.

## Corrected Study 03 model

Study 03 establishes four distinct layers:

1. existing source-facing `reference_course` identities;
2. governed British racecourse identity;
3. stable constituent course/track identity;
4. the Study 03 inventory rows from which stable course identity is resolved.

The corrected national cardinalities are:

- **61 racecourse evidence notebooks**;
- **65 Great Britain source-label mappings**;
- **61 governed racecourse identities**;
- **90 Study 03 course/track inventory rows**;
- **86 stable course/track identities**;
- **7 unresolved governance records**.

The integration **does not assign a physical course/track ID to race occurrences**. It establishes racecourse-level identity only. A source label often does not identify which peer physical track, course configuration, rail position or route was used.

## Newmarket correction

### Official structure

The Jockey Club explicitly describes Newmarket as having two racecourses:

- the **Rowley Mile**;
- the **July Course**.

Study 03 therefore now contains two separate racecourse evidence notebooks:

- `racecourses/newmarket_rowley_mile.ipynb`;
- `racecourses/newmarket_july_course.ipynb`.

The previous combined `racecourses/newmarket.ipynb` analytical-parent notebook has been removed.

Official evidence includes:

- `https://www.thejockeyclub.co.uk/newmarket/about/`
- `https://www.thejockeyclub.co.uk/newmarket/owners-and-trainers/arrival/`

The two racecourses also have distinct official visitor postcodes:

- Rowley Mile: `CB8 0TF`;
- July Course: `CB8 0XE`.

### Source Version 1 label resolution

Source Version 1 contains two Newmarket labels:

- `Newmarket`;
- `Newmarket (July)`.

Study 03 now governs the mapping directly:

- `Newmarket (July)` → `Newmarket — July Course` using `explicit_source_label`;
- `Newmarket` → `Newmarket — Rowley Mile` using `source_label_convention`.

The plain-label convention is supported by the coexistence of the July-specific label plus dated racing evidence, including a plain Newmarket Rowley Mile result and explicit `NEWMARKET (JULY)` results. Jockey Club material also documents the seasonal move from Rowley Mile racing to July Course racing.

This convention is **bounded to Source Version 1**. A future source version must revalidate its Newmarket naming convention rather than silently inheriting the rule.

## Schema objects

### `governance_study03_racecourse_notebook`

One row per completed racecourse notebook: **61 rows**. Stores the repository-relative notebook path, SHA-256 of the exact notebook bytes used for the build, the Study 03 evidence commit and the Database v4 governance release.

### `reference_racecourse_identity`

The **61 governed racecourse identities**. Newmarket contains two separate venue identities:

- `Newmarket — Rowley Mile`;
- `Newmarket — July Course`.

There is no synthetic `Newmarket` analytical racecourse identity in Database v4.

Operational status is not part of identity. Historical identities such as Towcester remain valid identities.

### `reference_course_racecourse_map`

The exact 65-row bridge from the existing Great Britain `reference_course` population to the governed racecourse identities.

Each row stores:

- `study03_grouping_name`;
- `racecourse_resolution_method`;
- `racecourse_resolution_evidence`.

For ordinary racecourses the method is `study03_identity_direct`. The two Newmarket rows preserve the specific methods above.

Missing, extra, duplicate or pending mappings fail the build.

### `reference_racecourse_course_identity`

The **86 stable course/track identities**.

The only national Study 03 identity collapses remain:

- Southwell Fibresand and Tapeta inventory states → one `All-Weather Flat Track`;
- Newcastle former Flat turf and later Tapeta inventory states → one `Flat Track`;
- Windsor's traditional and temporary Jump configurations → one `Windsor Turf Course`.

Newmarket Rowley Mile owns `Rowley Mile Course`; Newmarket July Course owns `July Course`.

### `reference_racecourse_course_inventory`

The **90 Study 03 inventory rows**, each mapped to its stable course/track identity. The original inventory row is retained as canonical JSON.

### `governance_racecourse_unresolved_question`

The **seven unresolved Study 03 records** remain explicit governance residue. They are not guessed or discarded.

## Views

`view_gb_racecourse_identity_reference` exposes the 65-row source-label → racecourse bridge, including resolution method/evidence.

`view_gb_course_track_identities` exposes the 86 stable course/track identities.

`view_gb_reconciled_race_occurrences_with_racecourse` is the Study 04-facing interface. It preserves one row per Great Britain race occurrence and adds:

- `racecourse_identity_id`;
- `racecourse_identity_code`;
- `governed_racecourse_name`;
- `racecourse_identity_kind`;
- `study03_grouping_name`;
- `racecourse_resolution_method`;
- `racecourse_resolution_evidence`.

The builder verifies that this view has exactly the same row count and distinct race-occurrence count as the GB population in `view_reconciled_race_occurrences`. It therefore cannot silently multiply races through the racecourse join.

No existing race-facing view is joined to the 86 stable course identities, so no race is fabricated as having used a particular physical track.

## Deliberately excluded from Database v4 candidate scope

This integration does **not** add:

- race-occurrence → physical-track assignment;
- rail/dolling/start-position geometry;
- route or spur identities below the Study 03 stable course layer;
- surveyed track geometry;
- a duplicate course-location system;
- all assertion-level provenance rows or all bibliographic source records;
- a generic EAV characteristics model;
- a promotion/acceptance path.

## Candidate build

From the repository root:

```bash
python scripts/build_inside_rails_v4.py
```

Default immutable base:

`data/processed/database/releases/inside_rails_v3.sqlite3`

Default output:

`data/processed/database/candidates/inside_rails_v4_candidate.sqlite3`

The canonical build:

1. verifies the fixed Study 03 evidence snapshot;
2. verifies the exact accepted Database v3 hash, size, release code, schema version, manifest state, validation count and governance lineage;
3. copies v3 to a disposable candidate;
4. migrates schema version 3 → 4;
5. creates the v4 governance release and import manifest inside the candidate;
6. parses static `pd.DataFrame` declarations from all 61 racecourse notebooks;
7. reconciles all 65 GB source labels to `reference_course`;
8. loads 61 racecourse identities, 90 inventory rows, 86 stable course identities and seven unresolved rows;
9. verifies the Newmarket Rowley Mile/July Course mappings and the one-row-per-GB-race Study 04 view;
10. runs `PRAGMA quick_check` and `PRAGMA foreign_key_check`;
11. verifies the accepted Database v3 hash is unchanged.

A failure removes the disposable output and leaves Database v3 untouched.

## Independent Database v4 validation

The standalone independent validator is:

```bash
python scripts/validate_inside_rails_v4.py
```

It is deliberately separate from the builder and Study 03 loader. In particular, it reconstructs the expected reference population directly from the frozen Git snapshot at `01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b` rather than importing the loader's expected rows.

The validator checks, read-only:

- exact accepted Database v3 hash and size before and after validation;
- Database v4 application/schema headers, manifest population and governance lineage;
- the exact 61 frozen racecourse notebook paths and SHA-256 values;
- all 65 source-label → racecourse mappings and their resolution provenance;
- all 61 racecourse identities and stable codes;
- all 86 stable course/track identities;
- all 90 inventory rows, including canonical JSON payloads;
- all seven unresolved governance rows, including canonical JSON payloads;
- governance-release ownership of every v4 reference/governance row;
- exact preservation of the v3 raw mirror, structural race core, structural runner core and `reference_course` population by streaming ordered comparison;
- exact GB source-label distribution into the racecourse-facing view;
- one row per each of the 111,634 GB race occurrences, with no missing or extra race IDs;
- the expected 1,503 plain-Newmarket Rowley Mile races and 1,438 `Newmarket (July)` July Course races;
- absence of a race-occurrence → physical-course identity join;
- `PRAGMA quick_check` and `PRAGMA foreign_key_check`.

The validator never writes the candidate or accepted Database v3.

Database v4 also increases the governed applicable-validator inventory from 31 to 32. The canonical project-wide sweep remains:

```bash
python scripts/run_applicable_validators.py
```

and now includes `validate_inside_rails_v4.py` as an applicable no-positional-input validator.

## Acceptance boundary

A successful build stops at:

`import_manifest.build_status = 'built'`

and reports:

`release_accepted = false`

This is intentional. A successful standalone v4 validation is evidence only; it does not mutate or promote the candidate.

Before Database v4 can be promoted, the repository still requires the complete test suite, the complete 32-validator applicable gate, a final standalone v4 validation at the release boundary, and an explicit promotion/acceptance implementation. Database v3 remains the accepted study database until those gates pass and promotion is deliberately performed.
