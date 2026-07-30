# Notebook 17 — Runner Characteristics and Equipment

## Executive conclusion

The source fields `age`, `sex` and `hg` are usable, but not as unqualified facts.

`age` is a complete runner-level integer and should be preserved as the source-recorded age. `sex` is complete and governed by six standard codes except for two verified contamination rows. `hg` is blank on most rows, but every populated value can be decomposed into an ordered set of governed equipment components.

The headgear suffix `1` is useful only as a source-declared first-time marker from 15 October 2025 onward. It is not a complete historical record of first use.

## Core evidence

- 1,851,285 governed runner rows were investigated.
- `age` is populated on every row, with 19 distinct integer values.
- `sex` is populated on every row, with eight raw values.
- Six standard sex codes cover 1,851,283 rows.
- Two isolated sex values were externally verified as source-field contamination:
  - `BB` for Par Coeur (GER) reconciles to gelding;
  - `B` for La Venezolana (VEN) reconciles to filly.
- `hg` is blank on 1,122,490 rows and populated on 728,795 rows.
- All 60 populated headgear values decompose into governed equipment components.
- The source-specific component `c` is supported as eyecover by the Humble Spark source context.
- 5,932 rows contain a trailing `1`, first observed on 15 October 2025.
- No trailing `2` occurs in the source.

## Interpretation

### Age

Retain the supplied integer as `age_raw` and, where a canonical field is useful, expose the same value as `age_recorded`. Do not overwrite it automatically from race-level age-band text and do not clip extreme values without targeted verification.

### Sex

Preserve `sex_raw`. Expose a normalised value for `C`, `F`, `G`, `H`, `M` and `R`. Apply the two anomaly corrections only through exact verification-backed lineage. The raw values `B` and `BB` are not additional sex categories.

### Headgear

Preserve `hg_raw`. For populated values, expose the ordered raw tokens and normalised equipment components. Preserve the source-specific `c` token in lineage while normalising its interpreted component to eyecover.

A blank `hg` means no code was supplied in this field. It does not prove the absence of every possible item of equipment.

A trailing `1` may be exposed as `source_declared_first_time = true`. Absence of the suffix cannot be interpreted as a negative declaration, especially before 15 October 2025.

## Confidence

- High confidence in source-wide counts and vocabularies.
- High confidence in the six standard sex-code meanings.
- High confidence in the two bounded sex corrections because reusable provenance was captured.
- High confidence that all populated headgear strings can be decomposed by the governed vocabulary.
- High confidence that `c` functions as a source-specific eyecover token in the observed combinations.
- Moderate confidence in the precise operational meaning of trailing `1`; it clearly behaves as a source declaration, but local history does not support treating it as a complete lifetime-first-use fact.

## Limitations

The study does not establish official biological age, race eligibility, complete equipment absence, or lifetime equipment history. It also does not show that every defect originated in the live Racing Post presentation rather than extraction, transformation or community-dataset handling.

Three suffixed values have an exact unsuffixed value recorded earlier for the same horse. This prevents independent reconstruction of first-time status from the local database history.

## Database consequence

The derived runner model should preserve raw fields and add interpreted fields rather than replace source values. Exact verification IDs and interpretation statuses must accompany corrections. Unknown future values must fail validation and remain unresolved until governed.

## Practical implication

Headgear remains analytically useful for studying equipment use and combinations. The database cannot safely support historical first-time-equipment analysis before 15 October 2025, and it should not advertise a complete lifetime equipment record.

## Closeout validation

Notebook 17 is classified as a non-rerunnable archival construction record. Durable replacement validation passed with:

- `20 passed in 0.04s` across focused runner-characteristics and manual-verification tests;
- independent source validation across all 1,851,285 governed runner rows;
- 8 sex values governed, including 2 exact verification-backed corrections;
- 1,122,490 blank and 728,795 populated headgear rows reconciled;
- 5,932 trailing-`1` rows confirmed, first observed on 15 October 2025;
- manual-verification validation across 33 governed rows.

The analytical notebook and verification register were committed at `699375d`.

## Next action

Use the reusable parser and full-source validator during database construction. Revisit only unmatched future values or bounded anomalies rather than repeating the complete investigation. The next bounded source-field study is ratings semantics and availability for `or`, `rpr` and `ts`.
