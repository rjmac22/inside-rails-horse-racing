# Source Field Governance and Database Integration

## Purpose

Notebook 10 is a governance inventory, not a parser. Its durable output is the rule that every physical source column must have one explicit analytical family, investigation group, treatment, governing artifact and current status.

The governed register is implemented in `src/inside_rails/field_governance.py` and validated against the immutable SQLite schema by `scripts/validate_field_governance.py`.

## Source preservation

All 37 physical source columns must be retained unchanged in the staging source layer. A treatment such as `deterministic_parsing` authorises additive derived fields only; it never authorises replacement of the raw value.

Blank strings and SQL `NULL` remain distinct source states until a field-specific investigation explicitly governs their interpretation.

## Register grain

The register contains exactly one row per physical source field. The key is the source column name.

Each row records:

- analytical family;
- bounded investigation group;
- current treatment;
- governing notebook or durable artifact;
- current audit status.

The register is intentionally current rather than frozen at the date of Notebook 10. Later completed studies update the governing artifact and status while retaining Notebook 10's original bounded grouping.

## Reconciliation examples

- `prize` remains in `prize_and_currency_semantics`, but is now governed by Notebook 13 and marked closed.
- `off` remains in `off_time_and_temporal_semantics`, but points to Notebook 11 and awaits its retrospective audit.
- `sp` is governed jointly by Notebook 08 arithmetic parsing and Notebook 09 contextual separation, while retaining the known source anomaly.
- unresolved classification, ratings, identity, connection and comment fields remain open rather than being marked complete merely because they are preserved.

## Database use

The field-governance register should control staging migrations and downstream model design.

Before adding or removing a derived column:

1. identify the source field's governance row;
2. confirm that the treatment permits the proposed derivation;
3. preserve the physical source value and lineage;
4. attach the governing artifact version to the derived transformation;
5. reject ungoverned source columns or silent schema drift.

## Update path

For every replacement or extended source snapshot:

1. run `tests/test_field_governance.py`;
2. run `scripts/validate_field_governance.py` against the immutable source;
3. fail if the physical source column sequence differs from the governed 37-field inventory;
4. add any genuinely new source field to the register before ingestion proceeds;
5. update a field's status only when its governing notebook satisfies the project closeout standard;
6. retain historical governance versions when a treatment changes.

Notebook 10 is closed only when the register and validator pass locally. It does not imply that every open field has been semantically resolved.
