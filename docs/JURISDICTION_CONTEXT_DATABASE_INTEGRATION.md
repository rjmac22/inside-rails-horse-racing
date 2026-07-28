# Jurisdiction Context Database Integration

## Scope

Notebook 09 established a layered model rather than a universal international racing dictionary. The durable reference in `src/inside_rails/jurisdiction_context.py` contains only the bounded worked examples investigated in the notebook: Great Britain, Ireland and France.

It must not be presented as complete worldwide coverage.

## Separation of layers

### Source layer

Preserve the original runner and race fields unchanged, including:

- `course`
- `type`
- `dist`
- `wgt`
- `sp`

### Structural derivation layer

Store reproducible values separately, including candidate jurisdiction and candidate course identity from `course_jurisdiction.py`.

### Research interpretation layer

Join evidence-backed contextual records separately. Recommended fields include:

- `jurisdiction`
- `source_type`
- `effective_from`
- `effective_to`
- `regulatory_authority`
- `administrative_body`
- `native_code_status`
- `wagering_context_status`
- `evidence_scope`
- reference version or commit

The interpretation layer must never overwrite the raw source type.

## Grain and join key

The bounded context reference is keyed by:

1. candidate jurisdiction;
2. source `type`;
3. race date falling within one effective period.

The join must be many races to zero or one context row. A race receiving more than one context row is a reference error and must fail validation.

Zero matches are allowed outside the bounded researched examples. They mean `unresearched`, not that the jurisdiction has no authority or wagering system.

## Governed examples

- Great Britain: four source types under the British Horseracing Authority context.
- Ireland: four source types split across 2015–2017 and 2018 onward; the regulatory authority changes while Horse Racing Ireland remains separately represented as the administrative body.
- France: France Galop authority context; source-labelled `NH Flat` remains an unresolved AQPS source-classification question.
- Wagering context remains unresolved for every governed row. Notebook 09 did not establish bookmaker, pool, exchange or settlement comparability.

## Effective-period rules

For each jurisdiction and source type:

- periods must not overlap;
- `effective_to` must not precede `effective_from`;
- a current open-ended period uses null `effective_to`;
- historical changes require a new versioned row, not mutation of past records.

## Provenance and update policy

The reference is derived from Notebook 09 and its closeout/report artifacts. It is deliberately bounded and version controlled.

For any extension:

1. define the analytical reason for adding the jurisdiction or deeper grain;
2. collect authoritative evidence;
3. distinguish regulatory, administrative and wagering roles;
4. specify effective dates;
5. preserve unresolved questions explicitly;
6. add unit tests for boundaries, overlaps and zero/one cardinality;
7. run `scripts/validate_jurisdiction_context.py` against the immutable source;
8. rebuild the interpretation layer without changing source or structural records.

## Replacement-source validation

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_jurisdiction_context.py

PYTHONPATH=src .venv/bin/python scripts/validate_jurisdiction_context.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

Validation must confirm:

- 189,043 provisional races in the current immutable snapshot;
- complete zero-or-one assignment for the GB, Ireland and France worked examples;
- exactly 23 French source-labelled `NH Flat` races;
- no overlapping context periods;
- no invented wagering-context assignments.
