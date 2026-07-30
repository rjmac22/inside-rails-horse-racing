# Notebook 15 — beaten-distance semantics

## The conclusion

The two source distance fields are useful, but only when interpreted against the physical finish rather than assuming they always describe the final official result.

`ovr_btn` records cumulative distance from the source physical-finish first-place reference. `btn` records the incremental margin from the preceding physical finisher or stored distance group. Both fields should therefore be retained raw, parsed conservatively and accompanied by exception flags.

## Why this matters

Official finishing positions can be amended after interference, disqualification or other adjudication while the stored distance sequence continues to describe the physical order across the line. Consequently:

- an official winner can retain a positive `ovr_btn`;
- a later official finisher can retain zero `ovr_btn`;
- a zero `btn` can identify a shared stored-distance group without proving an official dead heat; and
- a text `-` means distance unavailable, not zero.

Treating either distance field as a simple official-result calculation would silently corrupt valid evidence and conceal genuine source defects.

## Evidence

Notebook 15 profiled 1,851,285 governed runner rows across 189,043 provisional races.

The only populated text value in either field was `-`, appearing 93,992 times in each field and associated with non-finishers. The investigation found 500 positive-distance official-winner rows across 499 races and 371 later numeric finishers with zero overall distance. Bounded external verification separated amended results, physical dead heats and confirmed source defects.

The study also found 2,750 rows with positive `ovr_btn`, zero `btn` and official position greater than one. Nearly all were explained by repeated positions or exact same-`ovr_btn` groups. This supports a same-distance-group interpretation, but not an automatic official-dead-heat label.

## Database decision

The database will preserve both raw fields and derive numeric values only from validated numeric storage. The `-` sentinel becomes a null numeric derivative with explicit unavailable status. Structural contradictions generate review flags; they do not trigger automatic correction.

Governed external evidence is retained under verification IDs `NB15-BTN-0001` through `NB15-BTN-0017`. Corrections, where later permitted, must occur in a downstream reconciliation layer with provenance and must never overwrite immutable source values.

## Limitations

The source does not directly label every amended result or physical dead heat. Structural patterns are diagnostic rather than infallible. The module therefore identifies review states but cannot select a correction without governed external evidence.

Notebook 15 establishes semantics and safe integration rules. It does not reconstruct a new official result order or infer missing margins.
