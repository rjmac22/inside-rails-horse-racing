# Manual verification retrospective backfill

## Purpose

This register records the completed retrospective review of Notebooks 00–14 for reusable manual and external verification evidence.

A notebook is marked reviewed only when its committed notebook cells, reports, closeout records and governed reference files have been checked and every reusable verification has either:

- been added to `data/reference/manual_verifications.csv`;
- been confirmed as already preserved with equivalent provenance in a more specific governed reference table; or
- been classified as source-internal analysis that does not require an external-verification row.

## Completed review

| Notebook | Investigation | Review result |
|---:|---|---|
| 00 | Project scope and methodology | Reviewed; methodology only, with no source-value manual verification. |
| 01 | Source database structure profile | Reviewed; conclusions derive from the immutable SQLite structure and source contents, not external manual checks. |
| 02 | Source field quality profile | Reviewed; profiling and anomaly findings are source-internal. |
| 03 | Race identity and source-key reconstruction | Reviewed; candidate-key and duplicate screens are source-internal and no reusable external identity correction was recorded. |
| 04 | Course jurisdiction and surface mapping | Reviewed; source-label interpretation is preserved in governed project logic/reference artifacts. No separate bounded external claim requiring a manual-verification row was recoverable. |
| 05 | Finishing positions and non-finish outcomes | Reviewed; outcome-code findings and exception screens are source-internal. |
| 06 | Race distance parsing | Reviewed; parsing rules and observed representations are source-internal. No separately recorded external distance correction was found. |
| 07 | Carried weight parsing | Reviewed; parsing, range and collision findings are source-internal. No manual source-value correction was found. |
| 08 | Starting-price parsing | Reviewed; the standalone `F` anomaly is an immutable source anomaly, not an externally verified correction. It remains governed by the starting-price validator. |
| 09 | Jurisdiction, authority and betting-market context | Reviewed; reusable classifications are preserved in their governed project artifacts. No additional bounded manual source-value verification was recorded. |
| 10 | Remaining source-field inventory and triage | Reviewed; field grouping and treatment decisions are governance analysis rather than external source-value verification. |
| 11 | Off-time and temporal semantics | Reviewed; clock parsing is source-internal and timezone enrichment is governed through the course-location reference. |
| 12 | Course location and timezone mapping | Reviewed; two manually selected Nominatim venue matches were added to the general register. Automatically validated or jurisdiction-default assignments remain in `course_locations.csv` and are not duplicated as manual rows. |
| 13 | Prize-money semantics and availability | Reviewed; currency and availability conclusions derive from source representations and jurisdiction rules. No race-level external prize correction was recorded. |
| 14 | Runner counts, numbers and entries | Reviewed; the five published-result checks are governed rows. Shared-number and coupled-entry analysis remained source-internal and did not justify additional external claims. |

## Governed retrospective evidence

The general register now contains seven rows:

- Notebook 12: two manually validated course-location assignments, La Plata and Palermo;
- Notebook 14: five published-result checks for Nantes, Ohi, Morioka, Funabashi and Ohi.

Notebook 14 includes two `source_correction_candidate` rows where the published field contradicted source `ran`. The remaining Notebook 14 rows preserve evidence of partial runner coverage without changing raw values.

## Specialist governed evidence

`data/reference/course_locations.csv` remains the authoritative reusable course-location and timezone reference. It preserves course labels, physical venue information, coordinates, timezone, evidence notes and validation status. The general manual register supplements it only for the two rows explicitly marked as manually validated.

Other governed parser anomalies, reference mappings and source-wide findings remain in their specialist modules, tests, validators and integration documents rather than being duplicated in the manual register.

## Discovery tooling

`scripts/extract_manual_verification_candidates.py` scans committed notebooks for candidate cells containing URLs or manual/external-verification language and writes `docs/MANUAL_VERIFICATION_CANDIDATES.md` when run locally. Its output is a review queue only; it must never create governed rows automatically.

## Ongoing rule

For every future notebook, manual or external evidence must be recorded while the source is open. Retrospective reconstruction from memory is prohibited.
