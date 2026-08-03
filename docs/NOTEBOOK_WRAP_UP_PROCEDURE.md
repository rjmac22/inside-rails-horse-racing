# Notebook Wrap-Up Procedure

## Purpose

This procedure applies to every future Inside Rails research notebook. A notebook is not complete merely because the analysis has reached a conclusion or the saved notebook runs successfully.

The wrap-up must preserve the reasoning, extract reusable implementation, validate the source-wide consequence, update the project's public status documents, and leave the project ready for the next investigation.

## Closure standard

A notebook is fully closed only when every applicable item below has been completed. Where an item genuinely does not apply, record that explicitly rather than omitting it.

## Working discipline during notebook construction

Use a lightweight behavioural check before each substantive analytical cell rather than a rigid notebook template or style validator.

Before proposing or running the next step, confirm that:

- the cell has one clear analytical purpose;
- repository paths, helper functions and other project details have been checked against the repository rather than reconstructed from memory;
- non-obvious code includes enough comments to preserve its purpose, assumptions and limits for a later reader;
- raw values, source lineage and unresolved states remain preserved;
- the cell does not assume a conclusion, parser, reference output or reusable implementation before the evidence supports it;
- the next analytical step follows from the inspected output rather than from a prewritten sequence.

This is a judgement rule, not a demand that every trivial line receive a comment or that every notebook follow an identical cell structure. The aim is to prevent rushed, unexplained or assumption-led work without turning exploratory research into a compliance form.

## 1. Analytical conclusion

- State the bounded question investigated.
- State the final conclusion in plain language.
- Summarise the evidence supporting it.
- Record confidence, limitations, unresolved cases, and jurisdiction or period boundaries.
- Distinguish source fact, derived interpretation, external validation, and inference.
- State what the result does and does not justify analytically or for betting decisions.

## 2. Raw evidence and lineage

- Preserve raw source values unchanged.
- Preserve the source database, table, row identifier, and supplied identifiers required for lineage.
- Record transformation status and method separately from the raw value.
- Preserve anomalies as evidence; do not silently normalise them away.
- Where a known anomaly is intentionally allowed to fail validation, document the exact expected failure and why it remains unresolved.

### Manual and external verification

Every notebook closeout must make an explicit manual-verification decision. It must state either:

- `captured`: one or more bounded claims depended on manual or external evidence and have been recorded with reusable provenance;
- `specialist_reference`: equivalent evidence is preserved in a more specific governed reference table; or
- `not_applicable`: all conclusions were derived from source-internal analysis and no manual or external claim was used.

Whenever a conclusion, exception decision, correction candidate or reference enrichment depends on manual research or external evidence:

- add one row per bounded claim to `data/reference/manual_verifications.csv` while the evidence is open;
- record the exact source locators and raw value under review;
- record the verification question, result, status, confidence and permitted database action;
- preserve the evidence type, stable locator and access date;
- cite the permanent `verification_id` in the notebook or closeout record;
- never use the register to overwrite immutable source data directly;
- run `tests/test_manual_verifications.py` and `scripts/validate_manual_verifications.py` before closure.

A more specific governed reference table may replace a manual-verification row only when it preserves equivalent evidence, method, confidence and provenance. See `docs/MANUAL_VERIFICATION_REGISTER.md`.

Manual-verification capture may not be deferred until the final database build. A notebook that used external evidence but did not preserve it remains incomplete until the evidence is recovered or repeated and governed.

## 3. Notebook reproducibility or archival classification

Choose the closure route that matches the notebook's future purpose.

### Executable notebook route

Use this route only when the notebook is intended to remain a repeatable analytical workflow or when future users need to regenerate its outputs directly.

- Restart the kernel and run the notebook from top to bottom.
- Define every path, constant, dataframe, helper, and dependency before first use.
- Remove temporary recovery cells or repair the original failing cell.
- Ensure external requests use persisted caches where applicable.
- Reload and validate every file written by the notebook.

### Archival construction-record route

Use this route when the notebook's purpose is to preserve the completed investigation and reasoning rather than to serve as the durable production workflow.

A notebook does not need to be made fresh-kernel restart-safe merely for neatness when:

- the analysis has already been completed and can be read from the saved notebook;
- governed outputs have been persisted and reloaded;
- reusable logic, tests and independent validation will live outside the notebook;
- rerunning the notebook would duplicate permanent writes, depend on changed external inputs, or require disproportionate repair work without improving reliability.

For this route:

- classify the notebook explicitly as a non-rerunnable archival construction record;
- preserve the executed outputs, reasoning, anomalies and lineage needed to understand the conclusion;
- do not spend time removing harmless exploratory or recovery history solely to manufacture a clean rerun;
- provide durable replacement validation through persisted outputs, reusable implementation, focused tests and an independent source-wide validator;
- record any material cell that is known to be unsafe or misleading to rerun.

Restart safety is therefore required only when future rerun capability is genuinely needed. Archival classification must not be used to avoid creating the durable implementation and validation required by the remaining closeout steps.

## 4. Reusable implementation

For any governed transformation, reference table, or classification rule:

- move repeatable logic into `src/inside_rails/`;
- keep notebook-only display and exploratory code out of the production module;
- expose a clear public function or loader;
- preserve unresolved states rather than guessing;
- separate arithmetic parsing from contextual or jurisdictional interpretation;
- use governed reference data where rules vary by course, jurisdiction, authority, period, or source convention.

A notebook that establishes reusable rules is not fully closed while those rules exist only inside notebook cells.

## 5. Unit tests

Add focused tests for:

- canonical valid examples;
- boundary values;
- null, blank, malformed, and unknown inputs;
- jurisdiction or period distinctions;
- known source anomalies;
- duplicate or cardinality failures for reference data;
- invalid reference values;
- unresolved behaviour;
- round-trip or reconstruction behaviour where applicable.

Tests must verify failure behaviour as well as successful examples.

## 6. Independent validation

Create or update an independent validator under `scripts/` where the notebook establishes a source-wide rule or governed reference.

The validator should, as applicable:

- open the immutable source read-only;
- apply the governed data-row predicate;
- validate the entire relevant source population rather than only notebook samples;
- verify complete partitioning of source values;
- check expected counts, uniqueness, cardinality, coverage, and unresolved cases;
- fail loudly when a new malformed value, unmatched identity, duplicate reference row, invalid timezone, or other ungoverned case appears;
- print concise counts that can be copied into the closeout record.

A passing unit-test suite does not replace source-wide validation.

## 7. Database and integration consequence

Create or update an integration document under `docs/` describing:

- raw fields that must be preserved;
- canonical or interpreted fields to be added;
- data types and units;
- null and unresolved treatment;
- join keys and cardinality requirements;
- lineage, method, evidence, confidence, and status fields;
- constraints and validation checks;
- whether existing derived data must be rebuilt;
- how future source updates or new reference identities are handled;
- the migration or reference-update procedure.

Do not leave database consequences implicit in notebook prose.

## 8. Reference-data update procedure

For governed CSV or other reference data:

1. identify new or changed source identities;
2. research only the unmatched or changed residue;
3. preserve evidence, method, confidence, and review notes;
4. append or amend the reference without deleting historical source labels;
5. validate required columns, uniqueness, values, and effective periods;
6. run unit tests;
7. run the independent validator;
8. rebuild dependent derived tables;
9. compare counts and unmatched identities with the previous version;
10. commit the reference and evidence files together.

Never update expected validator counts merely to make a changed file pass. First establish why the population changed.

## 9. Reader-facing report

Produce the Minto-style notebook report with:

- executive conclusion;
- core evidence;
- interpretation;
- confidence;
- limitations;
- database consequence;
- practical implication;
- next action.

Use small illustrative tables rather than reproducing bulk source data.

## 10. Lessons learned

Discuss and record:

- what took longer or proved harder than expected;
- which assumptions were wrong;
- where scope expanded and whether it was justified;
- where automation helped or hindered;
- whether manual review would have been faster;
- which workflow errors should not recur;
- which reusable assets were created;
- which project-wide procedures should change.

Lessons must identify concrete future behaviour, not merely say that the task was difficult.

## 11. Audit register and project status

Before declaring closure:

- update `docs/RETROSPECTIVE_IMPLEMENTATION_AUDIT.md` or its successor register;
- update the field-governance register where a field has moved from open to implemented or closed;
- record exact local test and validator results;
- update `README.md` so its notebook statuses, counts, reusable outputs and next bounded action match the repository;
- update `docs/PROJECT_PLAN.md` so completed studies are removed from the future-work list and the next investigation is stated correctly;
- update closeout records and lessons documents where applicable;
- search the README and project plan for stale counts, stale “in progress” labels and references to already-completed future work;
- identify the next notebook or state explicitly that no further notebook action is required.

The README and project plan are mandatory closeout artifacts, not optional housekeeping. A notebook may not be marked fully closed while either document still describes an earlier project state.

Analytical completion, implementation completion, local validation and status-document completion are separate states and must not be conflated.

## 12. Final project-level check

At the end of a notebook series or repair branch:

- run the complete test suite;
- run every applicable independent source validator;
- confirm that any deliberate validator failure is documented and still fails for the intended reason only;
- inspect the final audit register for stale “pending validation” entries;
- verify that reference baselines, README, project plan and integration documentation agree with the current files;
- commit the final documentation updates before merge.

## Mandatory closeout checklist

A future notebook may be marked **fully closed** only when it has, where applicable:

1. a final conclusion and limitations;
2. either a fresh-kernel rerun when future executable reruns are needed, or an explicit archival classification with durable replacement validation;
3. persisted and reloaded outputs;
4. reusable code or governed reference data;
5. unit tests including failure cases;
6. an independent source-wide validator;
7. database integration and update documentation;
8. an explicit manual-verification decision and captured reusable provenance where applicable;
9. a reader-facing report;
10. lessons learned;
11. updated audit and field-governance records;
12. an updated `README.md`;
13. an updated `docs/PROJECT_PLAN.md`;
14. successful local validation evidence.

If any applicable item is missing, mark the notebook **implemented pending validation**, **implementation incomplete**, **status documentation incomplete**, or another precise status. Do not call it complete.
