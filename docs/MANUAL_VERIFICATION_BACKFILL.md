# Manual verification retrospective backfill

## Purpose

This register tracks the controlled extraction of manual and external verification evidence from completed notebooks into `data/reference/manual_verifications.csv`.

A notebook is marked complete here only when committed notebook cells, reports, closeout records and reference files have been reviewed for manual evidence and every reusable verification has either:

- been added to the governed register;
- been confirmed as already preserved with equivalent provenance in a more specific governed reference table; or
- been recorded as unrecoverable and scheduled for repeat verification.

## Backfill register

| Notebook | Investigation | Backfill status | Required review |
|---:|---|---|---|
| 00 | Project scope and methodology | Not applicable | No source-value manual verification expected; methodology only. |
| 01 | Source database structure profile | Pending review | Confirm whether any external dataset-description or source-product facts were manually verified. |
| 02 | Source field quality profile | Pending review | Confirm whether any declared-type or source-schema interpretations used external evidence. |
| 03 | Race identity and source-key reconstruction | Pending | Race and runner identity exceptions and any externally checked candidate matches. |
| 04 | Course jurisdiction and surface mapping | Pending | Course identities, jurisdiction assignments, surface checks and evidence provenance. |
| 05 | Finishing positions and non-finish outcomes | Pending | Manually checked outcome codes and unusual result examples. |
| 06 | Race distance parsing | Pending | External distance-convention checks, if any. |
| 07 | Carried weight parsing | Pending | Jurisdiction and unit-convention checks, if any. |
| 08 | Starting-price parsing | Pending | The standalone `F` anomaly and any externally checked market representations. |
| 09 | Jurisdiction, authority and betting-market context | Pending | Authority, market and jurisdiction evidence not already preserved in governed references. |
| 10 | Remaining source-field inventory and triage | Pending | Any external semantic checks used to assign field families or treatments. |
| 11 | Off-time and temporal semantics | Pending | Manually verified clock interpretations and course/timezone evidence. |
| 12 | Course location and timezone mapping | Equivalent governed reference identified | `course_locations.csv` already preserves location evidence and validation status. Review remains required for any manual checks whose exact locator or access date is absent. |
| 13 | Prize-money semantics and availability | Pending | Manually checked prize examples, jurisdiction currency evidence and interpretation limits. |
| 14 | Runner counts, numbers and entries | Partially backfilled | Five published-result checks are governed rows. Review selected shared-number/coupled-entry examples and unresolved course labels for any additional external evidence. |

## Current governed rows

Notebook 14 contributes five race-level verification rows:

- Nantes, 18 June 2024;
- Ohi, 26 June 2024;
- Morioka, 3 September 2024;
- Funabashi, 26 September 2024;
- Ohi, 9 October 2025.

The first, fourth and fifth confirm that `ran` matched the published field while source runner coverage was partial. The second and third externally contradict the stored `ran` and are retained as source-correction candidates without changing the raw source.

## Discovery tooling

`scripts/extract_manual_verification_candidates.py` scans committed notebooks for candidate cells containing URLs or manual/external-verification language and writes `docs/MANUAL_VERIFICATION_CANDIDATES.md` when run locally. Its output is a review queue only; it must never create governed rows automatically.

## Backfill rule

Do not infer or reconstruct evidence from memory. Use committed artifacts first. Where the committed record lacks a stable evidence locator or access date, either:

1. repeat the external check and record a new verification date; or
2. add an unresolved row explaining the provenance gap.

The backfill is separate from Notebook 14 parser closure, but it must be completed before the final database build treats manual findings as reusable enrichment, correction or reconciliation data.
