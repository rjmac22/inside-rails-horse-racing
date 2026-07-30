# Race-classification database integration contract

## Status

This contract implements the governed treatment established in Notebook 16.
The reusable parsers are in `src/inside_rails/race_classification.py`, the
focused tests are in `tests/test_race_classification.py`, and the source-wide
validator is `scripts/validate_race_classification.py`.

The governed source fields are race-level attributes under the provisional race
identity `date + course + off`:

- `race_name`;
- `type`;
- `class`;
- `pattern`;
- `rating_band`;
- `age_band`;
- `sex_rest`.

All seven fields were constant within each of the 189,043 provisional races in
the validated source population. Their raw values must remain available even
when a derived structural interpretation is also stored.

## Required race-level columns

### Preserved source values

| Column | Suggested type | Meaning |
|---|---:|---|
| `race_name_raw` | nullable text | Exact source race title |
| `race_type_raw` | nullable text | Exact source race-type value |
| `class_raw` | nullable text | Exact source class value |
| `pattern_raw` | nullable text | Exact source pattern value |
| `rating_band_raw` | nullable text | Exact source rating-band value |
| `age_band_raw` | nullable text | Exact source age-band value |
| `sex_rest_raw` | nullable text | Exact source sex-restriction shorthand |

The build may retain the original source column names in a staging table, but
processed race tables must make the raw-versus-derived distinction explicit.

### Class interpretation

| Column | Suggested type | Meaning |
|---|---:|---|
| `class_number` | nullable integer | Parsed integer from canonical `Class N` syntax |
| `class_parse_status` | text | `blank`, `canonical`, or `unrecognised` |

`class_number` is a structural extraction only. It does not establish that
similarly numbered classes are equivalent across jurisdictions.

### Pattern interpretation

| Column | Suggested type | Meaning |
|---|---:|---|
| `pattern_family` | nullable text | `Listed`, `Group`, or `Grade` |
| `pattern_level_raw` | nullable text | Source level such as `1`, `2`, `3`, `A`, `B`, or `C` |
| `pattern_parse_status` | text | `blank`, `canonical`, or `unrecognised` |

Group and Grade must remain distinct. The database must not create a universal
pattern hierarchy by silently collapsing the two families.

### Rating-band interpretation

| Column | Suggested type | Meaning |
|---|---:|---|
| `rating_lower_bound` | nullable integer | Lower bound from exact canonical `N-N` syntax |
| `rating_upper_bound` | nullable integer | Upper bound from exact canonical `N-N` syntax |
| `rating_band_parse_status` | text | `blank`, `canonical`, `unrecognised_source_form`, or `invalid_range_order` |

Only exact closed integer ranges are canonical. The observed values `--` and
`(75-100)` remain unresolved source forms and must not be silently coerced into
canonical ranges.

### Age-band interpretation

| Column | Suggested type | Meaning |
|---|---:|---|
| `stated_minimum_age` | nullable integer | Minimum age stated by the source syntax |
| `stated_maximum_age` | nullable integer | Maximum age stated by the source syntax |
| `age_band_open_ended` | nullable boolean | True only for explicit `Nyo+` syntax |
| `age_band_syntax` | text | `blank`, `exact_age`, `open_ended_minimum`, `closed_age_range`, `invalid_range_order`, or `unrecognised` |
| `age_band_interpretation_status` | text | `blank`, `source_stated_bounds_only`, or `unresolved` |

These are source-stated bounds, not globally authoritative runner-eligibility
rules. The build must not reject, alter, or exclude a runner merely because the
runner-level source age conflicts with the parsed race-level age band.

### Sex-restriction interpretation

| Column | Suggested type | Meaning |
|---|---:|---|
| `sex_rest_category` | nullable text | Preserved explicit source category where recognised |
| `sex_rest_interpretation_status` | text | `blank`, `explicit_source_category`, `overloaded_source_category`, or `unrecognised_source_category` |

No permitted-sex Boolean flags are currently governed. In particular,
`sex_rest = F` must not be interpreted universally as fillies-only. Blank must
not be interpreted automatically as unrestricted.

## Build integration pattern

For each race-level source record:

```python
from inside_rails import (
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)

class_fields = parse_class(row["class"])
pattern_fields = parse_pattern(row["pattern"])
rating_fields = parse_rating_band(row["rating_band"])
age_fields = parse_age_band(row["age_band"])
sex_fields = classify_sex_restriction(row["sex_rest"])
```

Persist all returned fields alongside the untouched source values. The build
must derive one race-level record only after confirming the field values are
constant within the governed race identity.

`race_name` may support later bounded phrase extraction, but Notebook 16 does
not authorise treating every detected title phrase as an official condition.
Sponsor names and race titles can contain misleading words.

## Relationships between fields

`class`, `pattern`, and `rating_band` are complementary attributes. They must
not overwrite or derive one another.

The database must not:

- derive `class` from `rating_band`;
- derive `rating_band` from `class`;
- replace `class` with `pattern` when both are populated;
- equate international uses of `Class 1` without jurisdictional evidence;
- create one global quality score from these labels alone.

Any later analytical hierarchy must be jurisdiction-, race-type-, and
period-specific and must retain the original fields.

## Manual verification and reconciliation

Notebook 16 created governed manual-verification records:

- `NB16-AGE-0001` — confirmed dropped plus sign; source correction candidate;
- `NB16-AGE-0002` — confirmed implausible runner age; source correction candidate;
- `NB16-AGE-0003` — confirmed semantics evidence; evidence only;
- `NB16-AGE-0004` — partially confirmed discrepancy; preserve raw unresolved.

The raw source remains immutable. A future processed database may apply a
reconciled value only when the verification register authorises that action.
Where a reconciliation is applied, store at least:

| Column | Suggested type | Meaning |
|---|---:|---|
| `verification_id` | nullable text | Permanent governed verification identifier |
| `reconciled_value` | nullable typed value | Corrected or supplemented processed value |
| `reconciliation_method` | nullable text | Named governed action |
| `reconciliation_confidence` | nullable text | Confidence recorded in the verification register |
| `source_value_status` | text | Distinguishes source-original, corrected, supplemented, and unresolved values |

Evidence-only and unresolved verification records must not silently alter source
values.

## Analytical safeguards

The integrated fields support:

- descriptive source-category analysis;
- jurisdiction-specific classification studies;
- parser coverage and source-quality monitoring;
- bounded analyses where official conditions have been established separately.

They do not by themselves support:

- one global race-quality hierarchy;
- authoritative runner-eligibility decisions;
- universal fillies-only, mixed-sex, or unrestricted classifications;
- global performance comparisons based on overloaded `sex_rest` shorthand;
- automatic deletion or correction of age disagreements.

## Validation commands

From the repository root:

```bash
pytest -q tests/test_race_classification.py
python scripts/validate_race_classification.py
```

The focused test file and source-wide validator must pass before these parsers
are used in the processed database build. The complete repository suite and
all-validator sweep remain governed by the notebook-series or repair-branch
closeout procedure rather than being required after this individual notebook.
