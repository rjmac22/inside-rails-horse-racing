# Notebook 22 Report — Participant Identity

## Executive conclusion

Participant identity cannot be reconstructed safely through broad string cleaning.

The defensible approach is to preserve every raw jockey, trainer and owner label, accept only narrow relationships supported by source-internal evidence, and keep unresolved candidates separate from governed mappings.

## Core evidence

### Jockeys

The source contains 7,917 distinct populated jockey labels.

Strict comparison after removing only a recognised leading personal title produced:

- 212 candidate groups;
- 426 candidate labels;
- 216 candidate relationships.

Only `Mlle Marie Velon` and `Mme Marie Velon` were accepted as the same provisional jockey label identity. `Miss B ONeill` and `Mr B ONeill` were confirmed different through a same-race collision. The remaining 214 relationships remain unresolved.

### Trainers

The source contains 10,708 distinct populated trainer labels and nine blank rows already governed by Notebook 20.

A source-wide title profile showed a material `Mlle` to `Mme` presentation change around the start of 2024, but residual `Mlle` use and long-gap candidates prevented a general rule.

A bounded chronology rule accepted 26 transitions where the exact post-title label matched, active periods did not overlap, the `Mlle` label ended in the second half of 2023 and the `Mme` label began in the first half of 2024.

The rule covers:

- 26 provisional trainer identities;
- 52 raw labels;
- 6,350 runner rows;
- 27 preserved unresolved candidate groups.

### Owners

The source contains 98,234 distinct populated owner labels and 35 blank rows already governed by Notebook 20.

Owner labels are structurally mixed and may represent people, organisations or compressed ownership groups. Exact token-multiset comparison generated 936 groups whose labels contained the same tokens in different orders.

All 936 were genuine order changes rather than punctuation-only variants. Same-race evidence showed that 41 groups used differently ordered versions of the same exact composition within one reconstructed race.

The accepted owner rule covers:

- 41 provisional ownership-composition identities;
- 95 raw labels;
- 9,788 runner rows.

The remaining 895 groups, covering 1,822 labels and 24,406 rows, remain unresolved.

## Interpretation

The source sometimes changes how the same participant or ownership composition is presented. However, the same-looking string operation can also collapse distinct people, changing groups or unrelated organisations.

Candidate generation therefore has value for recall, but it is not proof. The accepted relationships are deliberately narrow:

- one jockey title relationship supported by the evidence reviewed;
- a bounded trainer title transition with chronology controls;
- owner token-order equivalence only where same-race presentation proves the order is non-semantic.

## Confidence

Confidence is high for the accepted source-label relationships within their stated scope.

Confidence is not high enough to claim comprehensive real-world identity reconstruction. The mappings describe source-label equivalence or ownership-composition equivalence, not legal identity, licensing status, ownership shares or complete career histories.

## Limitations

- Initials and abbreviated names can collide.
- Personal titles are not globally stable identity markers.
- Trainer title transitions outside the bounded 2023–2024 window remain unresolved.
- Owner labels can combine several people and organisations without explicit separators.
- Same token membership does not prove equivalence unless supported by additional evidence.
- The source does not provide authoritative participant identifiers.
- Notebook 20 remains the governing source for blank connection-field supplementations.

## Database consequence

The target database must separate:

- immutable raw participant labels;
- provisional accepted identities;
- label-to-identity mappings;
- unresolved candidate relationships;
- evidence, method, confidence and status;
- verified blank-field supplementations with permanent provenance.

Analytical facts must not join unresolved candidates as if they were accepted identities. Owner compositions must not be decomposed into individual owners without another governed study.

## Practical implication

Trainer, jockey and owner performance summaries should remain raw-label analyses unless they explicitly use the governed mapping layer and disclose its limits.

The accepted mappings improve comparability for a small evidence-backed population while avoiding the much larger error risk created by universal normalisation.

## Next action

Complete the reusable implementation, focused tests, independent source-wide validator and project-status closeout. Physical participant schema design may proceed only after the governed files and validation are committed and the Notebook 19 authority-response gate is complete.
