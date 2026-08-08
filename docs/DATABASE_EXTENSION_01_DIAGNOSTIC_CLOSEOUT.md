# Database Extension 01 Diagnostic Closeout

## Status

**Fully closed — archival diagnostic; no database implementation required.**

Date: 8 August 2026

Working notebook:

`notebooks/database_extension_01_study_facing_time_and_comments.ipynb`

This notebook was opened after Study 01 appeared to expose source comment markup such as:

`Walkover<br><br><br>`

The bounded diagnostic question became:

> Is HTML-like markup actually stored in the governed source/database comment value, and does that justify a reusable comment-cleaning database transformation?

The answer is **no**.

---

## 1. Final analytical conclusion

No evidence supports an HTML-cleaning or plain-text comment transformation.

The immutable Source Version 1 population contains **zero admitted comments with a literal `<` character**.

The accepted Inside Rails Version 1 database stores the 12 May 2026 Hereford / Queensbury Boy comment exactly as:

`Walkover`

The accepted database evidence for that value is:

```text
source_race_occurrence_code: race:77b5dbbbfdee69d4d92a5826:000188205
source_record_code: rec:77b5dbbbfdee69d4d92a5826:data:0001843163
source_rowid: 1843163
raw_date: 2026-05-12
raw_course: Hereford
raw_off: 14:38
raw_horse: Queensbury Boy (IRE)
raw_comment: Walkover
SQLite storage type: text
character length: 8
contains literal <: false
contains line feed: false
contains carriage return: false
UTF-8 hexadecimal: 57616C6B6F766572
```

The hexadecimal value decodes exactly to `Walkover` and contains no additional presentation characters.

The later copied notebook output itself showed the decisive transport artefact: immediately after the valid hexadecimal value, the pasted representation continued with HTML line-break syntax and text from a **separate diagnostic cell**, including `Python executable:` and encoded newlines. That cannot originate from the stored comment value.

The defensible conclusion is therefore that HTML-like tokens were introduced somewhere in the rendered-output / copy-paste transport between the notebook display and the chat message. The evidence does not isolate which UI component performed that conversion, and no such isolation is required for the database decision.

Confidence: **high**.

---

## 2. What the result does and does not establish

### Established

- Source Version 1 does not contain literal `<` characters in admitted comments.
- The accepted Inside Rails database preserves the Hereford comment as exactly `Walkover`.
- The apparent `<br>` sequence was not stored source data and was not part of the accepted database value.
- The existing Notebook 21 conservative comment governance remains valid.
- No comment-cleaning database extension is justified by this evidence.

### Not established

- The exact browser, notebook-renderer, clipboard or chat-ingestion component responsible for inserting HTML presentation syntax was not isolated.
- This diagnostic does not create or authorise a general comment parser.
- This diagnostic does not change comment-field semantics.
- This diagnostic does not resolve the separate question of exposing already-governed race-time fields conveniently to reader-facing studies.

---

## 3. Raw evidence and lineage

Raw source and accepted-database values were inspected without rewriting them.

The project-owned race and source-record identifiers above preserve exact lineage for the decisive Hereford example.

No source value was normalised, trimmed, parsed or replaced.

The apparent markup was treated as suspect presentation evidence until the stored value was checked directly.

---

## 4. Manual-verification decision

`not_applicable`

All conclusions in this diagnostic were derived from the immutable source, the accepted Inside Rails database and the observed notebook/chat output. No external racing claim or manual web evidence was used.

No row is required in `data/reference/manual_verifications.csv`.

---

## 5. Notebook closure route

**Archival construction-record route.**

The notebook preserves useful diagnostic history, including failed assumptions and environment recovery, but it is not a durable production workflow and does not need to be manufactured into a clean fresh-kernel analytical pipeline.

Known exploratory history includes:

- an over-specific raw-source lookup that returned zero rows;
- an initial Jupyter import failure caused by the project `src` layout not being inherited correctly;
- investigation of the `rails` launcher and replacement of its relative `PYTHONPATH=src` with the absolute project `src` path;
- a broad substring locator that intentionally returned non-walkover narrative rows alongside exact walkovers.

These cells are construction history, not reusable transformation logic.

The durable conclusion is recorded in this closeout document and should also remain in the saved notebook output.

---

## 6. Reusable implementation

**Not applicable.**

No governed transformation, parser, classification or reference data was established.

Creating `comment_plain_text`, an HTML stripper, newline stripping, or another production helper would contradict the evidence and create unnecessary infrastructure.

---

## 7. Unit tests

**Not applicable.**

No production code or governed transformation was introduced by this diagnostic.

Existing comment-governance tests remain authoritative for the governed Notebook 21 behaviour.

---

## 8. Independent source-wide validation

**No new validator required.**

The bounded source-wide SQL profile established zero admitted comments containing a literal `<` character. Because no new source-wide rule or generated output was created, there is no new implementation for a validator to reproduce independently.

Existing source and comment validators remain unchanged.

---

## 9. Database and integration consequence

**No comment-related database change.**

The accepted release remains immutable and unchanged:

`data/processed/database/releases/inside_rails_v1.sqlite3`

No new comment field, view, table, migration or parser is authorised.

Notebook 21's existing rule remains authoritative: preserve exact raw comment text and do not infer a general narrative parser.

The separate Study 01 race-time convenience issue remains outside this diagnostic closeout and must be handled, if still required, as its own bounded task rather than being bundled with a disproved comment problem.

---

## 10. Reference-data consequence

**Not applicable.**

No reference data was created or changed.

---

## 11. Reader-facing Minto report

### Executive conclusion

The apparent HTML in the walkover comment was not racing data. The accepted database stores the comment as plain `Walkover`; the HTML-like line breaks appeared only after notebook output was transported into chat.

### Core evidence

- zero admitted source comments contain `<`;
- the decisive accepted-database value is exactly eight characters: `Walkover`;
- its hexadecimal representation is exactly `57616C6B6F766572`;
- the later pasted output visibly joined the end of that value to text from a separate diagnostic cell using HTML/entity formatting.

### Interpretation

The database was behaving correctly. The apparent defect existed in presentation/transport, not in the governed source value.

### Confidence

High for the database conclusion. The exact UI component responsible for the copy/paste conversion was not isolated because doing so would not change the database decision.

### Limitation

Rendered or copied notebook output can contain transport formatting that is not present in the underlying Python or SQLite value.

### Database consequence

None for comments.

### Practical implication

Before escalating a suspicious rendered value into field governance or database work, inspect the underlying value directly using source/database lineage and representation checks such as exact value, length, `repr()` or hexadecimal bytes where appropriate.

### Next action

Return to Study 01. Treat any remaining race-time convenience requirement separately from this closed comment diagnostic.

---

## 12. Lessons learned

### Rendered output is not raw evidence

A value copied from a notebook display into another interface can acquire HTML tags or entities during rendering or clipboard transport.

Future behaviour:

1. when a suspicious token appears in copied/rendered output, do not immediately assume it exists in the source;
2. verify the exact stored value first;
3. use stable source lineage to identify the decisive row;
4. inspect `repr()`, character length and bytes/hex only when needed to distinguish invisible or presentation characters;
5. create a parser or database transformation only if the stored evidence actually contains the artefact.

### Do not build infrastructure for an artefact before proving the artefact exists

The initial proposal for `comment_plain_text` and HTML stripping was premature. The source-wide check disproved the premise immediately.

Future behaviour: profile first, then authorise the smallest transformation supported by the evidence — including no transformation when the evidence says none is needed.

### Repository launch details are part of reproducibility

The project uses a `src` layout. The local `rails` alias must launch Jupyter with the absolute project `src` path on `PYTHONPATH` so kernels under `notebooks/` and `studies/` import project modules consistently.

This operational rule is now documented in `docs/STUDY_DATA_ACCESS.md`.

---

## 13. Audit, governance and study-revisit consequence

- Comment-field governance status: **unchanged**.
- Accepted Database v1: **unchanged**.
- Study revisit register: **no entry required** because Study 01 is still an active investigation rather than a completed or published study requiring reassessment.
- No prior completed notebook conclusion is invalidated.

This closeout document is the durable audit record for the diagnostic.

---

## 14. README and project-plan review

`README.md` and `docs/PROJECT_PLAN.md` were reviewed during closeout.

Both already describe the project as being in the reader-facing analytical-study phase using accepted Database v1. This diagnostic does not change that project status, database population, release identity or field-governance totals, so no status rewrite is required merely to manufacture a documentation diff.

The next substantive action remains reader-facing study work.

---

## 15. Validation evidence

No production Python, SQL schema, generated database artifact or governed reference was changed by this diagnostic, so no new unit-test or validator run is required for the analytical conclusion.

The decisive checks were performed directly against the immutable/accepted data layers in the notebook:

- source-wide literal-`<` count: **0**;
- decisive Hereford stored comment: **`Walkover`**;
- stored comment length: **8**;
- literal `<`: **false**;
- line feed: **false**;
- carriage return: **false**;
- UTF-8 hex: **`57616C6B6F766572`**.

Documentation-only repository changes do not justify running the complete repository test suite or all independent validators.

---

## Closure decision

**Fully closed — archival diagnostic; no database implementation required.**

The false comment-markup problem is closed. Do not reopen it unless new evidence demonstrates that markup is actually present in a stored source or accepted-database comment value.
