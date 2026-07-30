# Notebook 15 field governance — `ovr_btn` and `btn`

| Field | Raw preservation | Numeric derivation | Confirmed meaning | Governed exceptions | Prohibited assumption |
|---|---|---|---|---|---|
| `ovr_btn` | Required | SQLite integer/real only | Cumulative distance from the source physical-finish first-place reference | Positive value on official position 1; zero on later numeric position | Do not assume it always measures distance behind the final official winner |
| `btn` | Required | SQLite integer/real only | Incremental margin from the preceding physical finisher or stored distance group | Zero with positive `ovr_btn` identifies a same-stored-distance group | Do not treat zero as proof of an official dead heat |
| both | Required | `-` becomes null numeric with `unavailable` status | Text sentinel means distance unavailable | Other text values remain unresolved | Do not convert `-` to zero or overwrite contradictions |

## Review policy

`positive_official_winner_distance` and `later_position_zero_overall` are review flags. They do not authorise automatic correction. Any downstream reconciliation must cite governed external evidence, preserve the source row and retain the applicable verification identifier.

Notebook 15 verification provenance is stored in `data/reference/manual_verifications.csv` under `NB15-BTN-0001` through `NB15-BTN-0017`.

## Durable artifacts

- `src/inside_rails/beaten_distance.py`
- `tests/test_beaten_distance.py`
- `scripts/validate_beaten_distances.py`
- `docs/BEATEN_DISTANCE_INTEGRATION.md`
- `reports/notebook_15_beaten_distance_semantics.md`
- `data/derived/notebook_15_beaten_distance_semantics/beaten_distance_field_decisions.csv`
