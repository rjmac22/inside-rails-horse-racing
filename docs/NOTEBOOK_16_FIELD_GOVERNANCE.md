# Notebook 16 field governance — race classification and eligibility

## Scope

Notebook 16 governs `race_name`, `type`, `class`, `pattern`, `rating_band`, `age_band` and `sex_rest` at provisional-race grain using the immutable source table `data`, predicate `rowid <> 1`, and candidate race key `date + course + off`.

## Governance decision

The fields are suitable for preservation and bounded structural parsing. They are not a universal official classification or eligibility model across jurisdictions.

| Field | Governed treatment | Interpretation boundary |
|---|---|---|
| `race_name` | Preserve raw text | Supporting wording only; extracted phrases are not automatically official conditions |
| `type` | Preserve observed source category | No deeper regulatory equivalence without jurisdiction context |
| `class` | Parse canonical `Class N` into `class_number` | Do not derive from rating bands or equate international class systems |
| `pattern` | Preserve Listed, Group and Grade families separately | Do not collapse into a universal hierarchy |
| `rating_band` | Parse only exact `N-N` integer ranges | Preserve `--` and `(75-100)` as unresolved source forms |
| `age_band` | Parse exact, open-ended and closed-range syntax as stated bounds | Do not treat bounds as universally enforceable against source runner age |
| `sex_rest` | Preserve explicit categories and mark `F` overloaded | Do not reconstruct official permitted-sex flags globally |

## Manual-verification decision

**Decision: `captured`.**

Notebook conclusions depend on bounded external evidence preserved in `data/reference/manual_verifications.csv`:

- `NB16-AGE-0001`: confirmed dropped plus sign; correction candidate;
- `NB16-AGE-0002`: confirmed implausible source runner age; correction candidate;
- `NB16-AGE-0003`: external evidence supporting contextual age-condition semantics; evidence only;
- `NB16-AGE-0004`: partially confirmed discrepancy; preserve raw unresolved.

No register row directly overwrites immutable source data. Any later reconciled value must preserve the original value, verification ID, method, confidence, and action.

## Reusable implementation

- `src/inside_rails/race_classification.py`
- public exports through `src/inside_rails/__init__.py`
- `tests/test_race_classification.py`
- `scripts/validate_race_classification.py`
- `docs/RACE_CLASSIFICATION_DATABASE_INTEGRATION.md`

## Validation evidence

Recorded locally on 30 July 2026:

- `pytest -q tests/test_race_classification.py`: **15 passed in 0.05s**;
- `python scripts/validate_race_classification.py`: **passed**;
- runner rows checked: **1,851,285**;
- provisional races checked: **189,043**;
- all governed fields remained constant within provisional race groups;
- all observed parser vocabularies were partitioned;
- unresolved rating-band forms were exactly `--` and `(75-100)`.

Manual-verification tests and validator remain part of the final closeout command because Notebook 16 used external evidence.

## Analytical permissions

Safe uses include descriptive analysis of raw categories, structural parsing, bounded jurisdiction-specific studies, source-quality work, and anomaly review.

Unsafe uses include a global race-quality hierarchy, automatic runner eligibility decisions, treating every `F` as fillies-only, interpreting blank `sex_rest` as unrestricted, or silently repairing contradictions.

## Closure status

Implementation, focused unit tests, source-wide validation, integration documentation, governed decision persistence, manual provenance, report, lessons, and project-status updates are complete in repository artifacts.

Fresh-kernel notebook execution and persisted-output reload must be recorded from the local notebook environment before the notebook is labelled fully closed. Until that evidence is supplied, the precise status is **implemented pending final notebook rerun validation**.
