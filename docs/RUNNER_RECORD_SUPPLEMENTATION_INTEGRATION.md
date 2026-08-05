# Missing-runner supplementation integration

## Purpose

Notebooks 14 and 15 identified three published runners that are absent from the immutable source race rows. The accepted decisions require a usable governed output; they must not remain only in the manual-verification register.

The permanent supplementation reference is:

`data/reference/runner_record_supplementations.csv`

The loader is:

`src/inside_rails/runner_record_supplementations.py`

## Governed population

The exact accepted supplementations are:

| Verification | Race | Missing runner | Verified result facts |
|---|---|---|---|
| `NB14-RAN-0001` | Nantes, 2024-06-18 2:14 | Saucats | outcome `F`; position unresolved |
| `NB14-RAN-0005` | Ohi, 2025-10-09 11:07 | Tosen Thunder (JPN) | did not finish; position unresolved |
| `NB15-BTN-0001` | Gulfstream Park, 2023-12-23 9:36 | Great Navigator (USA) | finished fifth |

No other Notebook 14 or 15 external decision authorises runner creation.

The complete decision partitions remain:

- Notebook 14: two source supplementations and three source-correction candidates;
- Notebook 15: one source supplementation, twelve evidence-only interpretations and four source-correction candidates.

Correction candidates and evidence-only decisions are excluded from the supplementation table.

## Raw preservation and lineage

The future database must preserve every immutable source row and the raw race-level `ran` value. Supplemented records are separate analytical additions and must carry:

- `supplementation_id`;
- permanent `verification_id`;
- exact source race key: `date + course + off`;
- missing horse label;
- source runner-row count;
- raw source `ran`;
- externally published runner count;
- verified position where established;
- verified outcome where established;
- evidence type, locator and access date;
- confidence and authorised action.

A supplementation is not a recovered complete source row. Unsupported values remain null.

## Permitted fields

### Saucats

Permitted:

- horse label `Saucats`;
- fall outcome `F`.

Not permitted:

- numeric finishing position;
- any unverified runner characteristic, connection, betting, rating, prize, pedigree, margin or comment field.

### Tosen Thunder

Permitted:

- horse label `Tosen Thunder (JPN)`;
- did-not-finish state.

Not permitted:

- numeric finishing position;
- any other unsupported runner field.

### Great Navigator

Permitted:

- horse label `Great Navigator (USA)`;
- official finishing position 5;
- finished state.

Not permitted:

- inferred draw, age, sex, carried weight, starting price, jockey, trainer, owner, ratings, prize, pedigree, margins or comment.

## Database model

Use a separate governed supplementation table at grain:

`one externally verified missing runner per source race key and horse label`

Recommended key:

`(source_date, source_course, source_off, source_horse)`

Do not insert the rows into immutable staging. During clean runner construction:

1. load the immutable source runner rows;
2. validate the exact source race state;
3. append the governed supplementation rows to a clearly labelled clean-layer union;
4. retain `record_origin = externally_supplemented`;
5. retain the verification and evidence fields;
6. leave unsupported columns null;
7. reconcile clean runner counts against the governed published total without rewriting raw `ran`.

## Failure controls

Processing must fail when:

- a supplemented horse is now present in the source race;
- the source race key is absent or no longer unique;
- the source runner-row count or raw `ran` differs from the governed reference;
- a supplementation lacks direct evidence or a permanent verification ID;
- a correction-candidate or evidence-only decision appears in the supplementation table;
- a non-finisher receives a numeric position;
- a finished runner lacks its verified position;
- downstream code fills unsupported fields by inference.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_runner_record_supplementations.py

PYTHONPATH=src .venv/bin/python \
  scripts/validate_runner_record_supplementations.py
```

The existing Notebook 14 and 15 field validators remain applicable. This validator adds exact decision closure and source-absence checks for the accepted missing runners.
