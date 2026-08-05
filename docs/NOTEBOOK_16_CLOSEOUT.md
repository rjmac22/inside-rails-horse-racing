# Notebook 16 Closeout — Race Classification and Eligibility

## Status

**Analytically closed; decision-validation repair prepared for focused local validation.**

Notebook 16’s parsers and source-wide vocabulary coverage remain unchanged. The cross-notebook audit found that the independent validator did not protect the notebook’s four external decisions or its persisted seven-row field-governance output. This repair strengthens validation only; it creates no automatic correction mapping.

## Bounded conclusion

The race-level source fields `race_name`, `type`, `class`, `pattern`, `rating_band`, `age_band` and `sex_rest` are structurally useful but context-dependent. Raw values remain authoritative source evidence. Parsed values represent bounded syntax or source categories, not a universal international race-quality or eligibility system.

## Durable implementation

- reusable parsers: `src/inside_rails/race_classification.py`;
- focused tests: `tests/test_race_classification.py`;
- independent validator: `scripts/validate_race_classification.py`;
- persisted decisions: `data/derived/notebook_16_race_classification_and_eligibility/race_classification_field_decisions.csv`;
- integration contract: `docs/RACE_CLASSIFICATION_DATABASE_INTEGRATION.md`;
- permanent external evidence: `data/reference/manual_verifications.csv`.

## Governed external decisions

The exact four-record partition is:

- two `source_correction_candidate` records:
  - `NB16-AGE-0001` — source `age_band=5yo`, externally evidenced as `5yo+`;
  - `NB16-AGE-0002` — Ecstasy (USA) source age 31, externally evidenced as age 3;
- one `evidence_only` record:
  - `NB16-AGE-0003` — published `4yo` wording alongside older runners;
- one `preserve_raw_unresolved` record:
  - `NB16-AGE-0004` — Greyville `2yo` race with all source runner ages stored as 3; cause unresolved.

No record authorises automatic correction during parsing. Any later reconciliation must be an explicit processed-layer decision retaining the permanent verification ID and immutable source value.

## Validator repair

The independent validator now enforces:

1. 1,851,285 governed runner rows and 189,043 provisional races;
2. race-level constancy of all seven governed fields;
3. complete parser coverage of the current distinct vocabularies;
4. the exact unresolved rating-band set `{'--', '(75-100)'}`;
5. exact presence and status of all seven persisted field-decision rows;
6. exact closure of the four external verification IDs;
7. the exact `2 correction / 1 evidence / 1 unresolved` action partition;
8. exact provenance, access dates, confidence and source locators;
9. the corresponding immutable source states for all four reviewed cases;
10. zero automatic external corrections.

## Manual-verification decision

`captured`

The four permanent records remain in `data/reference/manual_verifications.csv`. The validator treats the register as evidence and decision governance, not as a global correction table.

## Database consequence

Preserve all seven raw race-level fields. Store parsed structural fields separately. Keep correction candidates, evidence-only records and unresolved records disjoint. Do not enforce parsed age bounds against runner ages universally, and do not interpret `sex_rest=F` as universally fillies-only.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_race_classification.py
PYTHONPATH=src .venv/bin/python scripts/validate_race_classification.py
```

Both must pass against the local immutable source before this review unit is accepted. Full repository and all-validator runs remain deferred until the final repair-series gate.
