# Notebook 17 — Database Integration

## Scope

This document governs integration of the source fields `age`, `sex` and `hg` established by Notebook 17.

The durable three-field decision reference is:

`data/reference/runner_characteristics_governance.csv`

The source-wide validator derives the current field profiles directly from the immutable SQLite source. It does not depend on ignored local `data/processed/` profile files.

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

Common codes are governed by `NB17-SEX-0001`.

The raw values `B` and `BB` may be corrected only when all of these values match the permanent verification:

1. raw sex value;
2. verification ID;
3. source date;
4. source course;
5. source off time;
6. source horse label.

The accepted exact corrections are:

- `NB17-SEX-0002`: Par Coeur (GER), Cologne, 2017-10-15 1:35, `BB` → `gelding`;
- `NB17-SEX-0003`: La Venezolana (VEN), Gulfstream Park, 2019-11-29 8:30, `B` → `filly`.

Reusing either verification ID on another runner remains unresolved. A value-only global replacement is forbidden.

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

## Governed evidence

The exact five-record external-decision partition is retained in `data/reference/manual_verifications.csv`:

- three confirmed `reference_enrichment` records;
- two contradicted `source_correction_candidate` records.

The validator enforces the exact IDs, statuses, actions, source locators, evidence locators, access dates, confidence and notes. Correction candidates are applied only through the exact-lineage API described above.

## Join keys and cardinality

Runner-level interpretation must join one-to-one through immutable source row lineage. Verification-backed sex corrections must use the exact source identity captured by the manual-verification record rather than a global join on raw value.

Governed vocabulary tables require one row per source field. Duplicate field decisions are invalid.

## Lineage and evidence fields

Where interpreted fields are materialised, retain:

- interpretation method;
- interpretation status;
- verification ID where applicable;
- governing notebook (`17`);
- confidence;
- source row ID;
- source race key;
- source horse label;
- source raw value.

## Source-wide validation baseline

The validator checks directly against all 1,851,285 governed runner rows.

Current baselines include:

- 19 distinct integer age values, from 1 to 31;
- exact sex counts for `C`, `F`, `G`, `H`, `M`, `R`, `B` and `BB`;
- exactly one `B` and one `BB`, each matching its governed runner lineage;
- 1,122,490 blank headgear rows;
- 728,795 populated headgear rows;
- 60 distinct populated headgear values;
- zero unresolved current populated headgear values;
- 5,932 trailing-`1` rows;
- first trailing-`1` date `2025-10-15`;
- exact source row `1347987` supporting the source-specific `c=eyecover` decision.

## Constraints and validation

Database construction must fail when:

- an unseen sex value occurs;
- a common sex value does not normalise;
- a verified correction is applied without exact lineage;
- a populated headgear value cannot be fully decomposed;
- a numeric suffix other than the governed `1` occurs;
- governed reference rows are duplicated;
- any of the five external decisions drifts or loses provenance;
- source-wide counts unexpectedly change without investigation.

Historical absence of a trailing `1` must not be converted into `first_time = false` as an official negative claim. The stored boolean means only whether this source value carried the declaration.

## Existing derived data

The three earlier local profile files under `data/processed/notebook_17_runner_characteristics/` are not clean-checkout dependencies and are not required by the durable validator. The committed three-row governance reference plus direct source-wide reconstruction supersedes that false dependency.

Any derived runner table that currently overwrites `sex` or `hg`, treats blank `hg` as definite no-equipment, or reconstructs historical first-time status must be rebuilt.

## Future source updates

For new source snapshots:

1. run `scripts/validate_runner_characteristics.py`;
2. inspect only new or unmatched raw values and changed counts;
3. preserve new evidence before changing governed rules;
4. update tests and committed governance together;
5. bind any accepted correction to exact source lineage;
6. rebuild dependent runner tables;
7. compare unresolved values and population counts with the previous source version.

Expected counts must never be changed merely to make validation pass.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_runner_characteristics.py
PYTHONPATH=src .venv/bin/python scripts/validate_runner_characteristics.py
```
