# Beaten-distance integration contract

## Source fields

Notebook 15 governs the source runner fields `ovr_btn` and `btn`.

- `ovr_btn` is the cumulative distance from the source physical-finish first-place reference.
- `btn` is the incremental margin from the preceding physical finisher or stored distance group.
- The text sentinel `-` means that a numeric beaten distance is unavailable. It must not become zero.

The source values remain immutable and must be retained alongside every derivative.

## Recommended staging columns

For each source runner row, stage:

- `raw_ovr_btn`
- `ovr_btn_numeric`
- `ovr_btn_status`
- `raw_btn`
- `btn_numeric`
- `btn_status`
- `positive_official_winner_distance`
- `later_position_zero_overall`
- `same_distance_group`
- `beaten_distance_requires_review`

The reusable implementation is `src/inside_rails/beaten_distance.py`.

## Permitted derivation

Numeric SQLite integer and real values may be converted to a numeric derivative. The raw value must remain available. The `-` sentinel produces a null numeric derivative with status `unavailable`. Unknown strings, blanks, booleans and nulls remain unresolved.

## Governed exceptions

A positive `ovr_btn` on official position 1 can indicate an amended result or a source anomaly. A zero `ovr_btn` on a later numeric position can indicate a demoted physical winner, a physical dead heat or a source defect. Both states require review and must not be silently corrected.

A zero `btn` with positive `ovr_btn` identifies membership of a same-stored-distance group. It does not prove an official dead heat.

External verification provenance for bounded Notebook 15 cases is stored in `data/reference/manual_verifications.csv` under `NB15-BTN-0001` through `NB15-BTN-0017`. Any downstream correction must retain the relevant verification identifier and must not overwrite the source row.

## Validation

Run the focused tests with:

```bash
pytest -q tests/test_beaten_distance.py
```

Run the independent source-wide validator with:

```bash
python scripts/validate_beaten_distances.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

The validator checks that text values remain limited to the governed `-` sentinel, that the two distance fields retain matching sentinel populations, and reports the governed anomaly populations without treating them as automatic failures.
