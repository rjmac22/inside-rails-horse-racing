# Inside Rails Notebook Working Rules

## 1. Purpose

These rules govern all notebook-led investigations in the Inside Rails horse-racing project.

They exist to keep the work reproducible, auditable, easy to follow, safe for source data, consistent across notebooks, and focused on evidence rather than assumptions.

These rules apply unless a notebook explicitly documents a justified exception.

## 2. One Cell at a Time

Work must proceed one notebook cell at a time.

The assistant must:

1. provide one small Markdown or code cell;
2. wait for the user to run it;
3. analyse the resulting output;
4. explain what the output means;
5. provide the next single cell.

The assistant must not provide several future cells at once, skip ahead, assume a cell ran successfully, continue without seeing the output, or silently change the investigation plan.

A cell should do one clear job only.

## 3. Every Code Cell Must Be Explained

Every code cell must contain comments explaining:

- what the cell is doing;
- why it is being run;
- what it reads;
- what it may create or modify;
- what result is expected.

Comments must be written for a future reader of the notebook, not merely for the current conversation.

For simple cells, a short comment is sufficient. For destructive, external, cached, or complex work, the comments must describe the safeguards.

## 4. Markdown Before Major Steps

A short Markdown cell should introduce each major phase of work, including scope, source inspection, methodology, cache design, validation, result classification, and final recommendations.

Markdown should explain the reasoning and intended evidence before the corresponding code runs.

## 5. Source Database Safety

The raw source database must remain read-only.

For the current Raceform-derived source:

```python
DATA_ROW_PREDICATE = "rowid <> 1"
```

All source queries must exclude the non-data first row using this predicate.

The assistant must never update the source database, alter its schema, create tables inside it, write indexes to it, or clean source values in place.

Any derived output must be written elsewhere.

## 6. Repository Awareness

Before giving path-dependent code, the assistant must inspect or establish:

- the notebook working directory;
- the repository root;
- relevant input and output paths;
- relevant modules and reference files;
- dependency conventions;
- cache conventions.

Notebook code must use an explicit `repo_root` rather than assume the notebook runs from the repository root.

## 7. Use Existing Project Code

Before creating new logic, inspect relevant modules under `src/inside_rails/`.

Existing functions should be reused where appropriate. Stable reusable logic should eventually be moved into a project module and then imported back into the notebook.

## 8. Do Not Make the User Do Work the Assistant Can Do

The assistant must not ask the user to perform work that the assistant can complete through available repository access, tools, connected services, or direct inspection.

This includes asking the user to paste accessible module contents, dependency files, repository structure, configuration files, or other information the assistant can retrieve directly.

The user should only be asked to run notebook cells or provide output that the assistant cannot access independently.

## 9. Ask Before Any Write Action

Read-only inspection may be performed without asking.

Before any write action, the assistant must ask for explicit approval. This includes:

- creating, editing, moving, or deleting repository files;
- committing or pushing changes;
- creating branches or pull requests;
- modifying reference data;
- changing calendar events;
- sending, drafting, forwarding, archiving, deleting, or relabelling email;
- modifying any external service.

Approval applies only to the specific write action described unless the user clearly approves a wider set of actions.

Notebook cells that the user runs themselves are not treated as assistant-performed writes, but the cell must still clearly state what it will create or modify.

## 10. No Unnecessary Repetition

Do not ask the user to rerun or repaste information already supplied.

Before providing a cell, check the established notebook state and previous outputs.

Do not repeat imports, path setup, package checks, counts, or definitions unless necessary.

## 11. Package Installation

Before installing a package:

1. check whether it is already installed;
2. inspect the repository dependency convention;
3. explain why the package is needed;
4. install only the necessary package or packages.

Package-installation cells must not be mixed with analytical work.

Any new project dependency should eventually be recorded in the repository dependency configuration.

## 12. External APIs

No bulk external requests may be sent before the following are established:

- provider suitability;
- terms and usage policy;
- identification requirements;
- rate limit;
- query design;
- cache design;
- error handling;
- ambiguity handling;
- audit fields;
- retry policy.

The first test must use one or a very small number of records.

## 13. Caching Rules

Every external request must be cached, including successful responses, empty results, ambiguous results, provider errors, rejected results, and manually superseded results.

The cache must preserve at least:

- candidate identity;
- exact query sent;
- provider name;
- request parameters;
- request timestamp;
- response status;
- raw response;
- error details where applicable.

Cached results must be reused unless there is an explicit reason to refresh them.

## 14. External Result Validation

The first returned result must never be silently accepted.

External results must be evaluated against explicit checks such as jurisdiction agreement, venue type, name resemblance, address resemblance, coordinate credibility, duplicate-name risk, known collisions, and plausible alternatives.

Accepted, rejected, ambiguous, and unresolved results must remain distinguishable.

## 15. No Guessing

Missing or uncertain values must remain explicit.

Statuses should clearly distinguish cases such as unassigned, automatically validated, provisionally matched, manual review required, manually validated, rejected, and unresolved.

The assistant must not fill a value merely because it seems likely.

## 16. Preserve Raw and Derived Values

Never overwrite raw source values with cleaned or interpreted values.

Preserve raw source labels, raw dates and times, raw API queries and responses, provider identifiers, derived values, validation statuses, and evidence notes.

Raw, normalized, inferred, and manually reviewed fields must remain conceptually separate.

### `raw_off` usage boundary

Source Version 1 `off`, and the database field `raw_off` that preserves that source value, may be used for technical checks, database validation, provenance, source identity, record reconciliation and other non-analytical integrity work.

They must not be used as analytical variables or as evidence for substantive racing conclusions. If a study needs a race-time concept, it must use a separately governed field whose semantics are appropriate to the question, such as an authorised scheduled/advertised or actual-off concept.

Using `raw_off` as part of an authorised source identity or technical reconciliation key does not make it an analytically governed race-time field.

## 17. Validation Before Saving

Before writing a reusable reference file:

1. check row count;
2. check identity uniqueness;
3. check required columns;
4. check null patterns;
5. check status values;
6. check coordinate ranges;
7. check timezone validity;
8. check accepted records for completeness;
9. check unresolved records remain explicit;
10. run the reusable project validator.

The notebook must print a concise validation summary before saving.

## 18. Safe Writes

Before overwriting an important reference file, state exactly which file will be written, show how many rows will be written, validate the output frame, preserve stable column order, and use an atomic or backup-aware write where practical.

Interim outputs should be written to clearly named cache or working files.

## 19. Output Analysis

After every code cell, the assistant must explain:

- what the output confirms;
- whether it matches expectations;
- any anomalies;
- any limitations;
- what decision follows from it.

The assistant must not respond only with “good” or immediately provide another cell without analysis.

## 20. Investigation Discipline

Each notebook should distinguish observation, interpretation, inference, assumption, decision, and unresolved question.

Evidence must come before recommendations. Unexpected output should be investigated rather than dismissed.

## 21. Notebook Structure

A typical notebook should contain:

1. title and purpose;
2. established context;
3. paths and environment;
4. source or reference loading;
5. baseline validation;
6. investigation methodology;
7. incremental evidence;
8. anomaly review;
9. reusable implementation;
10. final validation;
11. saved outputs;
12. conclusions and recommendations.

## 22. Completion Criteria

A notebook is not complete merely because code has run.

Completion requires that the stated population has been processed, outputs are classified, unresolved cases are explicit, reusable code exists where needed, outputs have been saved, validators pass, conclusions are documented, and dependencies for later notebooks are clear.

The final Markdown section must state what was established, what remains uncertain, what files were created or changed, and what later notebook depends on the result.

## 23. Assistant Behaviour

The assistant must read the handover carefully, retain established findings, follow the one-cell workflow, include comments in code, inspect accessible repository files itself, avoid unnecessary work for the user, admit mistakes directly, correct process failures immediately, and protect the evidential chain of the project.

The assistant must not rush ahead, dump large blocks of code, provide uncommented cells, ask the user to retrieve accessible information, silently guess, change agreed definitions without discussion, or treat notebook output as disposable scratch work.

## 24. User Override

The user may override any procedural rule for a specific step.

A one-off override does not permanently change these rules unless the user explicitly says that it does.

## 25. Autonomous Governed Notebook Mode

The user has permanently authorised an autonomous notebook workflow for bounded Inside Rails research problems. When the assistant can define the investigation safely in advance, this section takes precedence over the interactive execution requirements in Sections 2, 19 and 23.

The purpose is to preserve the reasoning and evidential chain **inside the notebook** while avoiding use of the user as a manual cell-by-cell execution loop.

### Default autonomous workflow

For each bounded problem, the assistant should:

1. state one precise research/correctness question;
2. inspect the relevant repository docs, prior notebooks, reusable modules and governed evidence itself;
3. design the smallest investigation capable of answering the question;
4. generate a self-contained notebook containing the method, assumptions, controls, evidence hierarchy, limitations and decision logic in Markdown;
5. ensure every code cell is commented for a future reader, including what it reads, requests, derives and writes;
6. reuse governed project modules rather than reimplement stable plumbing in notebook cells;
7. cache all external requests and preserve raw/derived/provenance states under the normal caching rules;
8. include positive controls, contradiction tests and fail-closed handling before scaling the investigation;
9. compile-check all generated Python code and round-trip the notebook before any live external requests are made;
10. provide an autonomous local runner when live access or the user's local data/environment is required;
11. have the runner save partial notebook outputs if execution fails rather than discard debugging evidence;
12. derive the final notebook conclusion from the executed evidence rather than pre-writing the expected answer;
13. ask the user only to run the finished bounded investigation, normally with one command;
14. after execution, inspect the committed/pushed executed notebook directly, audit whether its conclusion is supported, and repair/refine it if necessary;
15. perform the normal notebook closeout only after the executed evidence has passed that audit.

### Scope discipline

Autonomous mode does not authorise an indiscriminate bulk crawl merely because the runner can perform one. Begin with the cheapest useful controls and contradiction tests. Escalate to source-wide or population-wide validation only when the earlier notebook has established the rule that the larger validation is meant to test.

When one problem reveals a materially different next question, close the answered notebook and open a new bounded notebook rather than allowing one notebook to grow indefinitely.

### When to use interactive one-cell mode

Return to the one-cell workflow when:

- the next method genuinely depends on human interpretation of an unforeseen result;
- external ambiguity cannot be handled safely by explicit classification logic;
- a write/destructive decision needs separate approval;
- automation would hide a material conceptual choice rather than merely execute an already governed method.

Interactive mode remains available as an investigative tool; it is no longer the default execution mechanism for a bounded problem that can be specified safely in advance.
