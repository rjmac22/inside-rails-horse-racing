# Manual verification retrospective backfill

## Status

**Superseded retrospective record.**

The original Notebooks 00–14 backfill incorrectly classified several externally checked notebook facts as non-reusable. The correction audit is governed by:

`docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md`

and the missing durable evidence is recorded in:

`data/reference/external_verification_reconciliation.csv`

Do not use the earlier seven-row retrospective result as proof that all pre-Notebook-14 external evidence was captured.

## What was wrong

The original review correctly preserved two Notebook 12 course-location assignments and five Notebook 14 published-result checks, but it missed reusable external evidence in Notebooks 05, 06, 08, 11 and 13.

Most importantly, it incorrectly stated that Notebook 08's standalone `F` was not an externally verified correction. The committed Notebook 08 record says the opposite: Almendares (GB), source rowid 1708860, was externally verified as **5/2 favourite** in the 2025 Wickerr Stakes. The raw `F` remains immutable evidence, but the verified numeric price must be separately governed and analytically usable.

## Corrected notebook dispositions

| Notebook | Corrected retrospective disposition |
|---:|---|
| 00 | Methodology only; no source-value external correction identified. |
| 01 | Source-structure analysis; no source-value external correction identified. |
| 02 | Source profiling; no source-value external correction identified. |
| 03 | Source-key analysis; no source-value external correction identified. |
| 04 | Eight NH Flat/type conflicts were deferred for later external validation; no completed exact correction recovered by the v3 audit. |
| 05 | **Missed:** Cinnamon Carter (AUS), Morphettville 2015-05-16 4:38, source rowid 55516, raw `pos=10`, externally verified dead heat for 12th. |
| 06 | **Missed:** Sha Tin 2015-01-25 8:35 and Kyoto 2015-01-04 6:45 were externally verified as official 1600m races despite raw `dist='1m'`. This is official-distance enrichment, not a rewrite of the source-literal parse. |
| 07 | No reusable external source-value verification recovered. |
| 08 | **Missed:** Ptit Zig and Really Unique external confirmations; Lady Sabelia partial/ambiguous corroboration; and the exact Almendares `F` -> **5/2 favourite** correction. |
| 09 | Authority/context evidence is already preserved in the specialist jurisdiction-context reference. |
| 10 | Field-treatment governance only. |
| 11 | **Missed:** ten externally checked advertised-time records; three also contain distinct actual-off-time evidence. The advertised-time values already agree with the canonical temporal reconstruction, but the external evidence itself must be durable. |
| 12 | Two manually selected course-location assignments were correctly captured; the broader specialist reference remains authoritative. |
| 13 | **Missed:** controlled external prize-schedule checks for the 2018 Pegasus World Cup and 2019 Prix de l'Arc de Triomphe. Preserve as local-currency enrichment; do not overwrite source-presented prize. |
| 14 | Five published-result checks were correctly captured, but later v3 reconciliation additionally promotes exact contradicted runner counts where external evidence supplies the replacement value. |

## Corrected evidence population

The pre-Notebook-14 correction audit adds **19** missing external-verification rows through `data/reference/external_verification_reconciliation.csv`.

The existing `data/reference/manual_verifications.csv` remains the accepted 85-row Notebook 12/14–20 evidence register used by Database v2. Database v3 loads the 19 reconciliation rows in addition to those 85 rows, for an expected total of **104** manual-verification rows.

Typed analytical corrections/enrichments are separately declared in:

`data/reference/external_value_resolutions.csv`

This separation prevents free-text evidence from having to double as machine-readable analytical values.

## Ongoing rule

For future investigations, external evidence must be recorded while it is being used, with enough provenance to determine whether it is:

- confirmation/evidence only;
- a distinct enrichment;
- an exact correction; or
- proof that a raw value is wrong while the replacement remains unresolved.

Raw source values are never overwritten. Exact externally established facts must nevertheless be made usable through the governed analytical layer.
