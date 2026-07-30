# Manual verification register

## Purpose

Manual web research, official-result checks and other external verification must not remain only in notebook prose, browser history or memory.

The permanent register is:

`data/reference/manual_verifications.csv`

It records the exact source subject checked, the question asked, the external evidence used, the conclusion reached, confidence and the permitted future database action.

The raw racing source is never overwritten by this register. Verified missing, incorrect or incomplete source facts are stored separately as governed evidence and, where justified, must support a downstream supplementation, correction, enrichment or reconciliation layer.

Manual verification is not merely an anomaly log. When reliable evidence establishes a usable fact, the authorised database action must preserve and apply that fact during processing rather than knowingly carrying the defective source state forward as the only database representation.

## Durable implementation

- `data/reference/manual_verifications.csv` — governed row-level evidence register;
- `src/inside_rails/manual_verifications.py` — loader and structural validation;
- `tests/test_manual_verifications.py` — schema, status and failure-case tests;
- `scripts/validate_manual_verifications.py` — independent register validator.

## Register grain

One row represents one bounded verification claim about one identifiable source subject or raw source value.

A single race may therefore have several rows where different fields or questions were checked. Evidence from different sources must remain in separate rows rather than being merged into one unsupported conclusion.

## Required fields

- `verification_id` — permanent unique identifier, using the `MV-####` convention;
- `subject_type` — race, runner, course, jurisdiction, source value or another explicit subject type;
- `source_date`, `source_course`, `source_off`, `source_horse` — source locators where applicable;
- `source_field`, `raw_source_value` — the exact field and raw value under review where applicable;
- `verification_question` — the bounded question asked;
- `verified_value` — the externally supported value or conclusion, blank where unresolved;
- `verification_status` — governed outcome;
- `evidence_type` — official result, governing-body record, racecourse record, archive, secondary report or another explicit type;
- `evidence_locator` — stable URL, publication reference, archive reference or repository evidence path;
- `evidence_accessed_date` — ISO date on which the evidence was checked;
- `governing_notebook` — notebook or repair task that owns the decision;
- `confidence` — high, medium or low;
- `notes` — concise limitations or reconciliation context;
- `database_action` — the only authorised downstream use.

At least one source locator or raw source value must be present. Confirmed rows require a nonblank verified value.

## Governed verification statuses

- `confirmed` — evidence directly supports the recorded verified value;
- `contradicted` — evidence directly contradicts the raw source claim or value;
- `partially_confirmed` — only part of the source claim could be established;
- `unresolved` — the check was performed but the evidence was insufficient or conflicting.

## Governed database actions

- `evidence_only` — retain as support for an analytical conclusion only where the verified claim does not establish a database fact that should be applied;
- `reference_enrichment` — add the verified fact to a governed reference table after its own validation and uniqueness checks;
- `source_supplementation` — add a verified record or field that is absent from the immutable source during downstream processing, with explicit external provenance;
- `source_correction_candidate` — retain the raw source unchanged and apply the verified correction through a governed amendment or reconciliation layer once the required implementation and validation exist;
- `preserve_raw_unresolved` — retain evidence of the attempted check but make no correction, supplementation or enrichment because the result remains unresolved.

No row may authorise direct overwriting of immutable source data.

Where reliable external evidence establishes a missing or incorrect database fact, `evidence_only` is not sufficient. The register must authorise the narrowest applicable downstream action, and the future database build must consume that governed action.

## Downstream processing rule

Every verified intervention must preserve the distinction between:

- immutable source-present values;
- externally supplemented values;
- externally corrected values;
- derived values; and
- unresolved values.

Where the evidence supports it, downstream processing must:

1. retain the immutable raw source record unchanged;
2. load the governed manual-verification or specialist-reference record;
3. add or correct the verified fact in the processed database;
4. record the verification identifier, evidence method, confidence and action used;
5. prevent the supplemented or corrected value from being presented as source-original; and
6. leave every unsupported field null or unresolved rather than inventing it.

Examples include:

- adding a verified missing runner or race record;
- correcting a verified finishing position or result attribute;
- supplying a verified course, jurisdiction or identity mapping;
- overriding an unsafe source interpretation during processing; and
- preserving an unresolved contradiction without fabricating a replacement value.

A manually verified missing record is not complete merely because the omission has been documented. If the evidence establishes enough information to process the record safely, the governed supplementary record must be included in the future database build.

## Notebook procedure

Whenever manual verification is used:

1. create the register row while the evidence is open;
2. copy the exact source locators and raw value rather than relying on prose descriptions;
3. record the access date and evidence locator;
4. state the bounded conclusion and confidence;
5. select the database action explicitly;
6. capture every verified value needed for the authorised action and leave unsupported values unresolved;
7. cite the `verification_id` in notebook conclusions, exception tables or closeout records;
8. document how the future database build will consume the verification where the action is not `evidence_only` or `preserve_raw_unresolved`;
9. run the focused tests and register validator before notebook closure.

A notebook that depends materially on manual verification is not fully closed until those checks are represented in this register or in a more specific governed reference table that preserves equivalent provenance.

A notebook is also not fully closed where a confirmed supplementation or correction has been captured but its required downstream implementation, validation or integration consequence has been left unspecified.

## Retrospective backfill

The schema is now active, but earlier manual checks from completed notebooks still require a controlled backfill from committed notebook evidence and closeout records.

The backfill must cover, where evidence was actually consulted:

- race and runner identity exceptions;
- course and jurisdiction reconciliation;
- result and starting-price anomalies;
- off-time and timezone checks;
- prize-money examples;
- the five Notebook 14 races where source rows fall below `ran`;
- selected shared runner-number and coupled-entry checks.

Backfill rows must not invent missing URLs, dates or conclusions. Where the committed record lacks sufficient provenance, record the verification as unresolved or repeat the external check.

Where a repeated or recovered check confirms a missing or incorrect database fact, the backfill must assign the applicable downstream supplementation, correction or enrichment action rather than defaulting to evidence-only documentation.

## Validation

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_manual_verifications.py
PYTHONPATH=src .venv/bin/python scripts/validate_manual_verifications.py
```

The validator currently accepts an empty data register so the schema can be established before retrospective extraction. Once backfill begins, rows are governed by the same validation rules as future checks.