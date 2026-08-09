# Database v3 External Verification Reconciliation

## Status

**Canonical repair specification for the successor to accepted Database v2.**

Database v2 remains immutable at:

`data/processed/database/releases/inside_rails_v2.sqlite3`

Accepted Database v2 SHA-256:

`80b41071254fb9d9a78392e019fd386c6319938282494046fb917d29e3257abe`

Database v3 is a bounded correction release. It exists because the retrospective manual-verification backfill incorrectly classified some externally established notebook evidence as non-reusable and because several exact `source_correction_candidate` decisions were preserved as evidence without being made analytically usable.

This repair does not reopen source interpretation generally and does not modify Source Version 1 or Database v2 in place.

## Governing rule

> Raw source assertions are immutable. When external evidence establishes an exact fact, the governed database must expose that fact as usable analytical data with explicit provenance. When external evidence proves a raw analytical value wrong but does not establish a defensible replacement, the raw value remains visible as evidence but the study-facing analytical value must not silently remain usable as if it were correct.

Evidence that merely confirms an already-correct source value or explains a source convention may remain evidence-only.

## Audit scope

The committed Notebook 04–22 investigation chain was reviewed against:

- the notebook evidence itself;
- `data/reference/manual_verifications.csv`;
- the Database v2 physical/governed schema;
- Database v2 study-facing views;
- specialist course, temporal, pedigree, participant and connection governance.

The generated `docs/MANUAL_VERIFICATION_CANDIDATES.md` is a discovery queue only. Its 390 flagged cells are not 390 corrections.

## Notebook reconciliation

| Notebook | Disposition | Database v3 consequence |
|---|---|---|
| 04 | No completed exact external correction recovered. Eight NH Flat/type conflicts were explicitly deferred for later validation. | No invented correction. |
| 05 | One exact source result anomaly was externally verified but omitted from the durable manual register. | Cinnamon Carter source rowid 55516: raw `pos=10`, governed finish position `12`, with verified dead-heat context. |
| 06 | Two exact official metric race distances were externally verified while the generic parser correctly remained source-literal. | Sha Tin 2015-01-25 08:35 and Kyoto 2015-01-04 06:45 expose official distance `1600m` as external enrichment while retaining raw `dist='1m'` and source-implied 1609.344m. |
| 07 | No reusable external source-value verification recovered. | No correction. |
| 08 | Retrospective backfill was wrong: the standalone `F` was externally resolved. Other sampled prices either confirmed the raw value or remained ambiguous/unverified. | Almendares source rowid 1708860: raw `sp='F'`, governed analytical SP `5/2 favourite`; Ptit Zig and Really Unique preserved as confirmation evidence; Lady Sabelia preserved as partial/ambiguous evidence. |
| 09 | External authority/context evidence is already represented by the versioned jurisdiction-context reference. | Already governed and usable; no duplicate correction. |
| 10 | Field-treatment governance only. | Already integrated. |
| 11 | Ten external advertised-time validations were not preserved in the generic manual register. The canonical v2 advertised times already agree with them. Three records also preserve distinct actual-off-time evidence. | Add the ten verification records. Keep advertised time as the canonical concept; expose externally reported actual-off text where available without replacing advertised time. |
| 12 | Course/timezone reference already governed; two explicitly manual assignments are already in the register. | Already governed and usable. |
| 13 | Two controlled external prize-schedule validations were not preserved in the generic register. | Preserve Pegasus 2018 and Arc 2019 validation evidence and expose their externally established/candidate official local-currency placing schedules as enrichment; do not overwrite source-presented prize. |
| 14 | Five external checks are already registered. Two contradicted `ran` values were never promoted analytically. | Ohi 2024-06-26 governed runner count `13`; Morioka 2024-09-03 governed runner count `12`. Existing Nantes/Tosen Thunder supplementations remain. Funabashi raw `ran=6` remains correct while coverage stays known-partial. |
| 15 | Existing external evidence is registered. Great Navigator supplementation is usable, but its race-level count and four contradicted beaten-distance cases need stronger analytical treatment. | Great Navigator race count `9`; Gavea Gevrey-Chambertain distance `16.5`; Nardo exact incremental text `head` with numeric zero invalidated; Red Fog and Cabernet Franc zero distances invalidated where replacement remains unresolved. |
| 16 | Two exact contradicted values are registered but not promoted. | Compiegne age band raw `5yo` -> governed `5yo+`; Ecstasy raw age `31` -> governed age `3`. |
| 17 | Two exact sex corrections and verified headgear/sex-code references are already integrated in v2. | Already governed and usable. |
| 18 | OR/RPR/TS semantic references and the source-internal invalid RPR case are already integrated. | Already governed and usable. |
| 19 | Specialist pedigree corrections/equivalences are already integrated through the dedicated governance layer. | Already governed and usable. |
| 20 | 28 confirmed connection supplementations and 18 unresolved blanks are already integrated. | Already governed and usable. |
| 21 | No separate external source-value correction recovered; comment work is source-internal/conservative. | No correction. |
| 22 | Participant identity decisions are already represented by the provisional identity layer. No separately durable external source-value correction was identified by this reconciliation. | No new correction. |

## Missing pre-Notebook-14 verification evidence

The new governed reference:

`data/reference/external_verification_reconciliation.csv`

contains only the reusable external checks missing from the existing 85-row manual-verification register. It does not duplicate existing Notebook 12 or Notebook 14–20 rows.

Expected new rows: **19**.

Expected Database v3 manual-verification population after insertion: **104** rows.

## Typed analytical resolutions

The generic manual-verification table is intentionally evidence-oriented: `verified_value` is free text. Database v3 therefore adds a typed reconciliation layer rather than forcing studies to parse prose.

Canonical typed input:

`data/reference/external_value_resolutions.csv`

The physical Database v3 table stores one typed resolution per affected field/fact and links it back to the relevant manual-verification row. Resolution kinds are:

- `correction` — external evidence supplies a replacement analytical value;
- `enrichment` — external evidence supplies a distinct useful fact that must not overwrite the raw source concept;
- `invalidation` — external evidence proves the raw analytical value wrong, but no defensible numeric replacement is available.

Study-facing reconciled views must prefer typed corrections where present, retain raw/v2 values alongside them, and expose resolution/provenance status.

## Exact required analytical outcomes

### Starting price

Almendares (GB), Del Mar, 20 July 2025, 1:03, source rowid 1708860:

- raw source `sp`: `F`;
- governed fractional price: `5/2`;
- governed decimal odds: `3.5`;
- governed implied probability: `2/7` (~0.2857142857);
- governed favourite status: `favourite`;
- value status: externally corrected.

The parser itself must continue to refuse to infer a numeric price from a bare `F`.

### Finishing position

Cinnamon Carter (AUS), Morphettville, 16 May 2015, 4:38, source rowid 55516:

- raw `pos`: `10`;
- governed finish position: `12`;
- external context: dead heat for 12th with Mighty Maher (AUS).

### Official distance enrichment

- Sha Tin (HK), 25 January 2015, 8:35: official `1600m`, raw source `1m`;
- Kyoto (JPN), 4 January 2015, 6:45: official `1600m`, raw source `1m`.

Do not replace the literal source parse. Expose both concepts.

### Governed runner count

- Ohi (JPN), 26 June 2024, 11:07: raw `ran=5`, governed externally verified runner count `13`;
- Morioka (JPN), 3 September 2024, 11:07: raw `ran=5`, governed externally verified runner count `12`;
- Gulfstream Park (USA), 23 December 2023, 9:36: raw `ran=8`, externally verified runner count `9`; Great Navigator remains the already-governed supplemented fifth-place runner.

A corrected race count does not authorise invention of missing runner rows when identities/results were not captured.

### Beaten distances

- Gavea (BRZ), 6 April 2025, 7:35, Gevrey-Chambertain: raw `ovr_btn=0`, `btn=0`; governed numeric values `16.5` and `16.5` lengths.
- Saint-Cloud (FR), 11 April 2017, 12:47, Nardo: raw zero distance is known wrong; externally established incremental relation is `head` behind the second. No numeric head conversion is invented and the overall replacement remains unresolved.
- Gulfstream Park (USA), 9 April 2020, 6:30, Red Fog: raw zero distances are known wrong; replacement remains unresolved, so analytical numeric values become null with explicit status.
- Longchamp (FR), 31 August 2023, 12:48, Cabernet Franc: raw zero distances are known wrong; replacement remains unresolved, so analytical numeric values become null with explicit status.

### Age/eligibility

- Compiegne (FR), 16 May 2017, 1:35: raw age band `5yo`; governed condition `5yo+` with minimum age 5 and open-ended maximum;
- Woodbine (CAN), 27 July 2024, 9:47, Ecstasy (USA): raw age `31`; governed age `3`.

### Actual-off-time enrichment

Advertised/scheduled time remains the canonical temporal concept. External actual-off observations are distinct enrichments:

- Keeneland (USA), 11 October 2025, race_id 905191: actual off approximately `22:17` UK-facing time;
- Curragh (IRE), 30 June 2024, race_id 871044: actual off approximately `13:10:07`;
- Newmarket (July), 13 July 2024, race_id 870497: actual off approximately `13:41`.

### Prize-schedule enrichment

For the 2018 Pegasus World Cup, expose the externally recorded USD placing schedule while preserving the source prize field as its own presented/converted concept:

- 1st $7,000,000;
- 2nd $1,600,000;
- 3rd $1,300,000;
- 4th $1,000,000;
- 5th $850,000;
- 6th–12th $650,000 each.

For the 2019 Prix de l'Arc de Triomphe, preserve the notebook's externally checked/candidate official EUR schedule as medium-confidence enrichment:

- 1st €2,857,000;
- 2nd €1,143,000;
- 3rd €571,500;
- 4th €285,500;
- 5th €143,000.

These local-currency schedules must not overwrite the raw/source-presented prize values.

## Release architecture

Database v3 must:

1. verify the exact accepted Database v2 SHA-256;
2. copy Database v2 to a new disposable candidate;
3. migrate only the copy to SQLite `user_version = 3`;
4. retain all v2 source/core/governed data;
5. add the missing manual-verification evidence;
6. add typed external-value resolutions;
7. expose reconciled study-facing views;
8. create a new governance release which supersedes Database v2 only inside the v3 copy;
9. create a fresh v3 import manifest referencing Database v2 as the prior accepted release;
10. validate that raw/source/core rows remain unchanged from Database v2;
11. pass focused tests, the complete repository test suite and all applicable independent validators before promotion;
12. promote by copying/accepting the validated candidate, never by modifying Database v2.

## Closure condition

Database v3 work is closed only when the accepted v3 release exists, its release/hash is documented, Database v2 is unchanged, study-facing documentation points to v3, and the repository state is remote-verified.

Study 01 remains paused until that boundary is reached.
