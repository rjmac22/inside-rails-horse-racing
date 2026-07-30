# Notebook 17 — Database Integration

## Scope

This document governs integration of the source fields `age`, `sex` and `hg` established by Notebook 17.

## Raw fields to preserve

The immutable runner lineage must retain:

- source database and table;
- source `rowid`;
- supplied race identifiers;
- reconstructed race and runner identities;
- `age_raw`;
- `sex_raw`;
- `hg_raw`.

Raw source values must never be overwritten by interpreted values.

## Derived runner fields

### Age

| Field | Type | Null treatment | Meaning |
|---|---|---|---|
| `age_recorded` | integer | unresolved if source is not an integer | Source-recorded runner age |
| `age_interpretation_status` | text | never null | `source_recorded_integer` or `unresolved` |

No automatic range clipping or correction from race-level `age_band` is permitted.

### Sex

| Field | Type | Null treatment | Meaning |
|---|---|---|---|
| `sex_normalised` | text | null when unresolved | `colt`, `filly`, `gelding`, `horse`, `mare` or `rig` |
| `sex_interpretation_status` | text | never null | Common-code, verified-correction or unresolved status |
| `sex_verification_id` | text | null unless evidence applies | Permanent verification identifier |

Common codes are governed by `NB17-SEX-0001`. The raw values `B` and `BB` may be corrected only for the exact verified runner rows represented by `NB17-SEX-0003` and `NB17-SEX-0002` respectively. A value-only global replacement is forbidden.

### Headgear

| Field | Type | Null treatment | Meaning |
|---|---|---|---|
| `headgear_raw_components` | ordered array or child rows | empty for blank/unresolved | Exact parsed source tokens |
| `headgear_components` | ordered array or child rows | empty for blank/unresolved | Governed component names |
| `headgear_component_count` | integer | zero for blank/unresolved | Number of parsed components |
| `headgear_use_suffix` | text | null when absent | Exact governed suffix, currently only `1` |
| `headgear_source_declared_first_time` | boolean | false when absent | Source declaration, not reconstructed lifetime fact |
| `headgear_interpretation_status` | text | never null | Blank, fully decomposed or unresolved status |

A blank raw value must be represented as `blank_field_not_supplied`, not as a confirmed universal absence of equipment.

The source-specific raw token `c` normalises to `eyecover` under `NB17-HG-0002`. The raw token remains available in `headgear_raw_components`.

## Join keys and cardinality

Runner-level interpretation must join one-to-one through immutable source row lineage. Verification-backed sex corrections must use the exact source identity captured by the manual-verification record rather than a global join on raw value.

Governed vocabulary tables require one row per raw value. Duplicate raw values are invalid.

## Lineage and evidence fields

Where interpreted fields are materialised, retain:

- interpretation method;
- interpretation status;
- verification ID where applicable;
- governing notebook (`17`);
- confidence;
- source row ID;
- source raw value.

## Constraints and validation

Database construction must fail when:

- an unseen sex value occurs;
- a common sex value does not normalise;
- a verified correction is applied without exact lineage;
- a populated headgear value cannot be fully decomposed;
- a numeric suffix other than the governed `1` occurs;
- governed reference rows are duplicated;
- source-wide counts unexpectedly change without investigation.

Historical absence of a trailing `1` must not be converted into `first_time = false` as an official negative claim. The stored boolean means only whether this source value carried the declaration.

## Existing derived data

Any derived runner table that currently overwrites `sex` or `hg`, treats blank `hg` as definite no-equipment, or reconstructs historical first-time status must be rebuilt.

## Future source updates

For new source snapshots:

1. run `scripts/validate_runner_characteristics.py`;
2. inspect only new or unmatched raw values and changed counts;
3. preserve new evidence before changing governed rules;
4. update tests and reference outputs together;
5. rebuild dependent runner tables;
6. compare unresolved values and population counts with the previous source version.

Expected counts must never be changed merely to make validation pass.
