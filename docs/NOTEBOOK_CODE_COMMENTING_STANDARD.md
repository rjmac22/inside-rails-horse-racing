# Notebook Code Commenting Standard

## Purpose

Inside Rails notebooks are analytical records intended to be understood by a reader who did not write the code.

A code cell is not sufficiently documented merely because the preceding Markdown explains the analytical question. The Python itself must contain useful inline comments showing how the cell performs the work.

## Required commenting level

Every substantive notebook code cell must include concise comments that explain, where applicable:

- what source, file, table or dataframe is being read;
- why constants, columns or filters are being defined;
- what each material query, transformation, grouping or join is intended to establish;
- why a classification or calculation is safe at that stage;
- what an assertion or validation check protects against;
- which assumptions are provisional, governed or deliberately unresolved;
- what is being displayed and why that output is needed for the next decision.

Comments should describe analytical intent and failure protection, not merely restate Python syntax.

Good:

```python
# Fail if the permanent governance register no longer contains the columns
# required to interpret the three rating fields consistently.
missing_columns = required_columns - set(field_governance.columns)
```

Insufficient:

```python
# Get missing columns.
missing_columns = required_columns - set(field_governance.columns)
```

## Relationship with Markdown stages

The notebook working sequence remains:

1. one bounded Markdown explanation;
2. one commented code cell;
3. inspect and interpret the output;
4. decide the next conceptual stage.

The Markdown explains the analytical purpose and boundaries. Inline comments explain how the code implements that stage. Neither replaces the other.

## Performance and memory guardrail

Before running a transformation across a large source population, identify the smallest grain at which the decision can be made.

Do not use row-wise `DataFrame.apply` with a function that returns a `Series` across a large dataframe when the same result can be produced by:

- reducing first to distinct decision inputs;
- applying the function only to the small exceptional residue;
- using vectorised conditions;
- building a lookup table and joining it back;
- performing grouped or set-based work in SQL.

Series-returning row-wise application creates a large intermediate object and can exhaust notebook memory even when the final output is small. It is especially unsafe across source-wide race or runner populations.

Before supplying or running such a cell:

1. estimate the number of rows the Python function will process;
2. check whether most rows share repeated input combinations;
3. reduce to the smallest distinct or grouped decision grain;
4. isolate genuinely context-dependent exceptions;
5. join the compact result back only when necessary;
6. prefer SQL or vectorised operations for source-wide counting and classification.

A source-wide validator may still process the full population, but it should do so with bounded-memory, set-based or streaming logic rather than constructing one Python `Series` per source row.

## Proportionate use

Comments are required around meaningful blocks, assumptions, transformations and checks. They are not required on every trivial assignment or every line.

The aim is that the user can follow what the code is doing without reverse-engineering unfamiliar Python, while avoiding noisy comments that obscure the analysis.

## Review rule

Before supplying or committing a notebook code cell, check that a reader can answer:

- What is this block doing?
- Why is it doing it?
- What could fail?
- What does the validation establish?
- Is the transformation running at the smallest safe decision grain?
- Could it create a large row-wise intermediate object unnecessarily?

If those answers are not clear from the Markdown and inline comments together, the cell is not ready.
