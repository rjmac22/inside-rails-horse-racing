# Notebook 17 Closeout — Runner Characteristics and Equipment

## Status

**Archival analytical record with repaired clean-checkout implementation.**

Notebook 17’s conclusions remain unchanged. The cross-notebook audit found that its independent validator required three ignored local processed CSVs that were absent from a clean checkout, and that the two accepted anomalous sex corrections were not sufficiently bound to immutable runner lineage.

The repair removes those implementation defects without rerunning the archival notebook.

## Bounded conclusion

- `age` is a populated source-recorded integer and must not be treated automatically as an eligibility decision;
- six common `sex` codes have governed meanings;
- the rare source values `B` and `BB` are bounded source defects for two exact runners, not global sex codes;
- `hg` is a source-presented equipment shorthand that can be decomposed only through the governed current vocabulary;
- blank `hg` means the field was not supplied, not necessarily that no equipment was worn;
- a trailing `1` is a source declaration and not a reconstructed lifetime first-use fact.

## Durable implementation

- module: `src/inside_rails/runner_characteristics.py`;
- three-field governance: `data/reference/runner_characteristics_governance.csv`;
- focused tests: `tests/test_runner_characteristics.py`;
- independent validator: `scripts/validate_runner_characteristics.py`;
- integration contract: `docs/NOTEBOOK_17_DATABASE_INTEGRATION.md`;
- permanent evidence: `data/reference/manual_verifications.csv`.

## External-decision closure

The exact five-record partition is:

- `NB17-SEX-0001` — common sex-code reference enrichment;
- `NB17-HG-0001` — published headgear-code reference enrichment;
- `NB17-SEX-0002` — Par Coeur (GER) `BB` correction candidate;
- `NB17-SEX-0003` — La Venezolana (VEN) `B` correction candidate;
- `NB17-HG-0002` — source-specific `c=eyecover` enrichment.

Statuses and actions remain exactly:

- three confirmed reference enrichments;
- two contradicted source-correction candidates.

## Exact correction lineage

The `B` and `BB` corrections now require the complete verified key:

`raw sex + verification ID + date + course + off + horse`

The accepted keys are:

- Par Coeur (GER), Cologne (GER), 2017-10-15 1:35, raw `BB`, `NB17-SEX-0002` → gelding;
- La Venezolana (VEN), Gulfstream Park (USA), 2019-11-29 8:30, raw `B`, `NB17-SEX-0003` → filly.

The same verification ID on another runner remains unresolved.

## Clean-checkout repair

The old validator required:

- `data/processed/notebook_17_runner_characteristics/runner_sex_governance.csv`;
- `data/processed/notebook_17_runner_characteristics/runner_headgear_governance.csv`;
- `data/processed/notebook_17_runner_characteristics/runner_characteristics_decisions.csv`.

Those ignored files are not present in a clean checkout. They are no longer durable dependencies.

The replacement validator reads the committed three-field governance reference and reconstructs all source profiles directly from the immutable SQLite database.

## Source-wide validation contract

The validator now enforces:

- 1,851,285 governed runner rows;
- 19 distinct integer ages, minimum 1 and maximum 31;
- exact counts for all eight observed sex values;
- exactly one `B` and one `BB`, each on its governed runner lineage;
- 1,122,490 blank headgear rows;
- 728,795 populated headgear rows;
- 60 distinct populated headgear values;
- zero unresolved populated headgear values;
- 5,932 trailing-`1` rows and first occurrence on 2025-10-15;
- exact source row 1,347,987 for the `c=eyecover` decision;
- the exact three-row governance and five-record evidence partitions.

## Manual-verification decision

`captured`

The permanent manual-verification register remains the source of external evidence. The committed three-field reference stores the durable analytical treatment, not duplicate external claims.

## Database consequence

Preserve raw `age`, `sex` and `hg`. Store interpreted values separately with method, status and verification ID. Do not globally replace `B` or `BB`; do not represent blank headgear as confirmed no-equipment; do not infer official eligibility or historical first-use state.

## Validation commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_runner_characteristics.py
PYTHONPATH=src .venv/bin/python scripts/validate_runner_characteristics.py
```

Both must pass against the local immutable source before this review unit is accepted. The complete suite and all-validator sweep remain deferred to the final repair-series gate.
