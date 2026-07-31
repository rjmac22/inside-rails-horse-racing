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

## Proportionate use

Comments are required around meaningful blocks, assumptions, transformations and checks. They are not required on every trivial assignment or every line.

The aim is that the user can follow what the code is doing without reverse-engineering unfamiliar Python, while avoiding noisy comments that obscure the analysis.

## Review rule

Before supplying or committing a notebook code cell, check that a reader can answer:

- What is this block doing?
- Why is it doing it?
- What could fail?
- What does the validation establish?

If those answers are not clear from the Markdown and inline comments together, the cell is not ready.
