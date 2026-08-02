# Horse and Pedigree Identity Integration

## Scope

This document records the database consequence of Notebook 19, which investigated the runner-level `horse`, `sire`, `dam` and `damsire` source fields.

The immutable source remains:

- database: `data/raw/form_2015-present/form_2015-present/raceform.db`
- table: `data`
- governed row predicate: `rowid <> 1`
- provisional race identity: `date + course + off`

## Core conclusion

The raw `horse` label is not a permanent natural key. The same displayed horse name and country suffix can identify different real horses, while one real horse can also appear with inconsistent or incorrect pedigree assertions.

The clean analytical layer must therefore preserve raw labels and add governed identity and pedigree fields separately.

## Raw fields to preserve

The following source values must remain unchanged:

- source database and table
- source `rowid`
- supplied `race_id`
- `date`, `course` and `off`
- raw `horse`
- raw `sire`
- raw `dam`
- raw `damsire`
- source age and sex values used as supporting identity evidence

No governed correction may overwrite the immutable source.

## Governed reference

Bounded corrections, identity decisions and unresolved cases are stored in:

`data/reference/horse_pedigree_identity_governance.csv`

The reference preserves:

- a permanent decision identifier
- exact source horse label
- decision scope
- analytical outcome
- competing raw pedigree labels where applicable
- governed pedigree labels where established
- verification status
- verification or decision identifier
- evidence locator
- confidence
- review notes

Notebook 19 uses the `specialist_reference` manual-verification route. Three claims are also present in `data/reference/manual_verifications.csv`; the specialist reference governs the remaining bounded decisions and pending authority enquiries.

## Analytical outcomes

Every governed contradiction boundary must resolve to one of:

- `Corrected`: one horse history remains; governed pedigree values may replace raw alternatives in analytical views while raw values remain preserved.
- `Different horse`: the exact source horse label is reused and the histories must receive separate provisional occurrence identifiers.
- `Unresolved`: no correction or split is permitted until further evidence is obtained.

The expected Notebook 19 transition partition is:

- 87 `Corrected`
- 261 `Different horse`
- 5 `Unresolved`
- 353 total governed transitions

## Derived fields

The clean analytical layer should add, at minimum:

- `provisional_horse_occurrence_id` TEXT
- `horse_occurrence_sequence` INTEGER
- `horse_identity_outcome` TEXT
- `horse_identity_decision_basis` TEXT
- `horse_identity_split` BOOLEAN NULLABLE
- `governed_sire` TEXT NULLABLE
- `governed_dam` TEXT NULLABLE
- `governed_damsire` TEXT NULLABLE
- `identity_verification_id` TEXT NULLABLE
- `identity_confidence` TEXT NULLABLE
- `identity_review_status` TEXT
- `identity_unresolved` BOOLEAN

`provisional_horse_occurrence_id` is a source-internal analytical key only. It is not an official registration number, life number or globally unique horse identifier.

## Join keys and cardinality

The source-wide derivation begins at exact source horse-label and structured pedigree-group grain.

Structured pedigree groups are ordered by first and last observed dates. Governed split boundaries create occurrence sequences within each exact source horse label.

Required cardinality rules:

- each governed decision ID is unique
- each provisional occurrence ID is unique
- every governed transition has exactly one analytical outcome
- unresolved boundaries do not create an identity split
- split boundaries increment the occurrence sequence exactly once
- raw runner rows retain one source row identifier
- downstream joins from a source row to its occurrence must be many-to-one

## Null and unresolved treatment

Blank raw pedigree fields remain blank or null according to the raw preservation policy.

For `Unresolved` cases:

- governed pedigree fields remain null
- `horse_identity_split` remains null rather than false
- `identity_unresolved` is true
- dependent pedigree analysis must exclude or explicitly isolate the disputed field
- no consensus value may be substituted merely because it appears more frequently

## Reusable implementation

Reusable derivation logic lives in:

`src/inside_rails/horse_pedigree_identity.py`

The independent source-wide validator lives in:

`scripts/validate_horse_pedigree_identity.py`

The validator opens the immutable SQLite database read-only, applies `rowid <> 1`, checks the complete relevant population, writes governed processed outputs, reloads them and verifies expected counts and uniqueness.

## Persisted outputs

The validator writes:

- `data/processed/horse_pedigree_identity/transition_governance.csv`
- `data/processed/horse_pedigree_identity/provisional_horse_occurrences.csv`

These outputs must not be treated as valid until the validator has completed successfully and the written files have been reloaded.

## Rebuild consequence

Any existing derived table that groups runner histories by raw `horse` alone must be rebuilt before horse-level or pedigree-level analysis.

The rebuild must use the governed provisional occurrence identifier and governed pedigree fields where available. Analyses that do not depend on horse continuity may continue to retain raw labels, but must not imply permanent identity from them.

## Update procedure

When new source data or authority replies arrive:

1. identify new exact labels, changed pedigree assertions or unresolved authority cases;
2. preserve all new raw values and lineage;
3. research only the unmatched or changed residue;
4. append or amend the specialist governance reference without deleting historical source labels;
5. retain the existing decision ID where the bounded claim is being updated;
6. validate required columns, uniqueness, outcomes and evidence fields;
7. run the focused unit tests;
8. run the independent source-wide validator;
9. rebuild both processed outputs;
10. compare transition, outcome and occurrence counts with the previous validated version;
11. investigate every count change before updating an expected baseline;
12. rebuild dependent analytical tables.

Authority replies for the five unresolved cases should change the relevant row from `Unresolved` to either `Corrected` or `Different horse`, with the reply locator, date, confidence and permitted database consequence preserved.
