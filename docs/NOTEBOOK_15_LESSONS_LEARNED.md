# Notebook 15 lessons learned

## Physical finish and official result can diverge

A result field can be updated after adjudication while related distance fields continue to describe the physical order across the line. Cross-field consistency must therefore be interpreted against each field's actual reference frame, not an assumed single final result state.

## Zero is relational, not self-explanatory

A zero incremental margin with positive overall distance means no recorded separation from another runner at the same stored overall distance. It does not, by itself, establish an official dead heat. Zero values require field-specific semantics rather than generic missing-value or winner logic.

## Contradictions should become flags before corrections

Positive overall distance on an official winner and zero overall distance on a later finisher are valuable diagnostic states. The safe implementation is to preserve them and generate review flags. Automatic correction would collapse amended results, physical dead heats and genuine source defects into one unsupported rule.

## Mixed storage requires explicit numeric helpers

The fresh-kernel rerun exposed a pandas aggregation failure because raw finishing position contains both numeric values and text outcomes. Arithmetic must use explicitly derived numeric helper columns while the raw mixed-type field remains intact for lineage and result-state analysis.

## External verification belongs in governed provenance

Manual checking was necessary to separate amendments from source defects. Those decisions became reusable only when captured under stable verification IDs in `data/reference/manual_verifications.csv`. Manual research should feed a governed reconciliation layer, not disappear into notebook prose or overwrite the source.

## A notebook is not reproducible merely because every cell once ran

The completed exploratory session had retained variables that concealed a mixed-type failure. Restarting the kernel demonstrated that visible outputs are not proof of a valid dependency chain. A successful fresh-kernel run remains the decisive notebook-level reproducibility check.
