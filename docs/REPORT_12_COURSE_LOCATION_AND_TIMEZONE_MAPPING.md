# Notebook 12 — Course Location and Timezone Mapping

## Executive conclusion

The permanent course reference now assigns a valid IANA timezone to all 394 jurisdiction-qualified course identities used by the source data.

This is sufficient to interpret source `off` values as local civil times and allows Notebook 11 to continue without requiring complete exact venue geocoding.

## Core findings

- 394 permanent course identities were retained.
- 394 course identities have valid IANA timezone assignments.
- 0 course identities remain unresolved for timezone interpretation.
- 51 distinct IANA timezones are represented.
- Course identity remains based on `candidate_course_label + candidate_jurisdiction`.
- Exact physical venue details remain incomplete for some courses.
- Missing exact venue coordinates do not block timezone interpretation where a defensible jurisdiction-level or course-level timezone assignment exists.

## Evidence

Timezone coverage was completed through four broad evidence paths:

1. existing resolved course-location evidence;
2. safe jurisdiction-level defaults where one timezone applies;
3. manually reviewed course-level assignments in multi-timezone jurisdictions;
4. structured manual reference files retained alongside the final reference.

Every nonblank timezone value was validated through Python's `zoneinfo.ZoneInfo`.

The permanent reference is stored at:

`data/reference/course_locations.csv`

Independent validation confirms:

- 394 unique course identities;
- no duplicate identity pairs;
- 394 timezone assignments;
- no unresolved timezone values;
- 51 distinct valid IANA timezone names.

## Interpretation

The source `off` field does not itself contain timezone information. Timezone interpretation therefore requires a separate governed course reference.

A complete exact geospatial model is not necessary for the present bounded question. The required output is a defensible local timezone for each course identity. Exact venue names, addresses and coordinates remain useful enrichment but are not required to continue the off-time study.

Course location and timezone should remain reference-data attributes rather than being inferred repeatedly inside analytical notebooks.

## Database consequence

The future staging or core race representation should:

- preserve raw `date`, `course` and `off` values;
- join course reference data using the jurisdiction-qualified candidate course identity;
- retain `iana_timezone` separately from raw clock text;
- preserve timezone resolution method and evidence;
- represent exact venue coordinates as nullable enrichment;
- reject duplicate course-reference identities;
- validate all assigned timezone names;
- explicitly flag future source courses that do not match the reference.

Timezone assignment must not overwrite or reinterpret the raw source value.

## Reusable implementation

Reusable course-reference logic is stored in:

`src/inside_rails/course_locations.py`

It provides:

- required-column validation;
- duplicate course-identity detection;
- IANA timezone validation;
- latitude and longitude range validation;
- many-to-one merging of course reference fields onto race data.

Independent validation is stored in:

`scripts/validate_course_locations.py`

Run from the project root with:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_course_locations.py
```

## Confidence

**High** for timezone coverage and validity within the current 394-course reference.

**Moderate** for exact venue-location completeness because some records remain supported by jurisdiction defaults or course-level timezone research rather than full geospatial confirmation.

## Limitations

- Exact venue names, localities, regions and coordinates are incomplete for some identities.
- Historical venue changes and renamed courses may require later effective-period treatment.
- Future source extracts may introduce new course identities that require manual addition.
- Notebook 12 is an archived executed research record rather than a permanent rerunnable pipeline because its input state changed when the final reference was persisted.

## Practical implications

Notebook 11 can now resume and interpret source `off` values using governed local civil timezones.

Future unmatched courses should be researched and appended to the permanent reference as they appear rather than rerunning the original global resolution exercise.

## Lessons learned

- Define the minimum downstream output before pursuing optional enrichment.
- Exact location completeness and timezone sufficiency are different problems.
- Automation is useful for candidate generation but must not manufacture certainty.
- Manual review is often faster once the unresolved residue is small and ambiguous.
- A completed research notebook and a reusable production pipeline are different artefacts.
- Save and commit the completed executed notebook before attempting a fresh-kernel rerun or cleanup.

## Next action

Return to Notebook 11 and complete the off-time and temporal-semantics investigation using `data/reference/course_locations.csv` as the governed timezone reference.
