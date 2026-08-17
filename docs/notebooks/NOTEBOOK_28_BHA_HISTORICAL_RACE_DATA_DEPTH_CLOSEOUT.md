# Notebook 28 closeout — BHA historical race-data depth

Closeout date: **17 August 2026**

Notebook:

`notebooks/28_bha_historical_race_data_depth.ipynb`

Reader report:

`reports/notebook_28_bha_historical_race_data_depth.md`

## Status

**Fully closed — archival construction-record route.**

Notebook 28 is retained as the executed evidence record of the historical-depth investigation. It is not a production acquisition pipeline and should not be rerun merely to refresh historical counts, because the public BHA surface can change through time. Reusable HTTP/cache behaviour lives in `src/inside_rails/bha_api.py`.

## Bounded question

> How far back does the BHA provide usable official fixture, race, result and runner data, and what source capabilities are available at each historical depth?

## Final conclusion

There is no single defensible historical start date for the BHA structured estate.

The investigation established:

1. fixture discovery is populated on the controlled 8 April 1995 date;
2. a controlled 9 April 1994 query is empty despite independent result evidence confirming racing at Aintree that day, giving strong observed lower-edge evidence around 1995 without creating a contractual start-date claim;
3. sampled 1999 fixture-detail and fixture-race-list resources return direct HTTP 404;
4. sampled 2000 fixture-detail, race-list, race-detail, official-result and runner-level resources are populated;
5. the direct pre-2000 boundary for race-detail/results endpoints remains unresolved because pre-2000 races are not addressable through the surviving public fixture-race-list chain;
6. the apparent 2022–2025 hole from the first pass was not reproduced on known racing dates and is not accepted as an archive gap;
7. fixture-search `resultsAvailable=true` is **not** a safe completed-racing predicate.

The decisive semantic counterexample is Worcester on 25 September 2020. The fixture was recovered through `resultsAvailable=true`, while its own detail reported `resultsAvailable=0`, `abandonedReasonCode=1` and `ABANDONED - Abandoned (72 Hours Before)`. The race-list resource still retained one programmed race.

Therefore fixture discovery, fixture administrative state, race programme, realised official result and runner-level result are separate evidence states.

## Confidence and unresolved limits

### High-confidence conclusions

- the 1995 fixture catalogue observation is real;
- the sampled 1999→2000 fixture-detail/race-list split is real;
- populated result/runner resources are demonstrated from sampled 2000 races;
- `resultsAvailable=true` does not mean “this fixture produced results”;
- race-list presence does not prove that a race took place.

### Explicitly unresolved

- exact first fixture-search date;
- exact first fixture-detail/race-list date within the 1999→2000 transition;
- direct pre-2000 race-detail/result endpoint boundary;
- complete continuity of every resource family across every historical period;
- any formal stability guarantee for the observed public frontend service.

These are not blockers for the stated Notebook 28 question.

## Raw evidence and lineage

All BHA structured requests used the reusable cached client:

`src/inside_rails/bha_api.py`

Local cache namespace:

`data/cache/bha_historical_race_data_depth/`

The cache preserves request URL, parameters, HTTP status, raw response, parsed payload, access profile and frontend asset fingerprint while never persisting the frontend Bearer value.

The committed notebook preserves the executed result tables and audited conclusion.

Derived local closeout artifacts include:

- `historical_depth_boundary_summary.json`;
- `historical_depth_probe_matrix.csv`;
- `historical_depth_year_matrix.csv`;
- `historical_depth_query_mode_refinement.json`.

They remain local cache evidence rather than database inputs.

## Manual / external verification decision

Status: **`specialist_reference`**.

The bounded external controls required for the 1994 lower-edge interpretation and the 2020 suspension context are preserved in:

`data/reference/bha_historical_depth_external_controls.csv`

That file records the exact claim, evidence type, locator, access date, governing notebook, confidence, permitted use and limits. No external control is authorised to rewrite Source Version 1 or Database v4.

The core `resultsAvailable` semantic conclusion is source-internal BHA evidence from the Worcester fixture and does not depend on a commercial secondary source.

## Reusable implementation

Applicable and complete.

Reusable source-access implementation:

`src/inside_rails/bha_api.py`

The client provides cached fixture search/detail/race-list and race detail/result calls, current public-frontend authorization acquisition in memory only, fail-closed provenance and deterministic cache identities.

Notebook-only historical probing and presentation logic remains in the notebook/scripts and is not promoted into the production package because it is investigation-specific.

## Focused tests and validation evidence

Focused BHA client test run supplied during this investigation:

```text
pytest -q tests/test_bha_api.py
.....                                                                    [100%]
5 passed in 0.45s
```

Autonomous Notebook 28 execution completed successfully on 17 August 2026 after generated-cell compile and notebook round-trip checks passed.

The targeted refinement script also completed successfully and rewrote the notebook with the audited conclusion.

No new database transformation, governed parser, source-wide classification rule or database reference loader was created by Notebook 28. A new source-wide validator is therefore **not applicable** to this closeout.

The specialist external-control CSV is documentary provenance only; it is not loaded into Database v4 and does not authorise a transformation.

## Database / integration consequence

No database change is authorised.

Database v4 remains the accepted immutable analytical release:

`data/processed/database/releases/inside_rails_v4.sqlite3`

Notebook 28 does not create:

- Database v5;
- a BHA fixture entity;
- a BHA race identity;
- a completed-race import;
- a historical population repair.

The durable source-use consequence is documented in:

`docs/BHA_STRUCTURED_SOURCE_USAGE.md`

## Reader-facing report

Complete:

`reports/notebook_28_bha_historical_race_data_depth.md`

The report records the conclusion, evidence, confidence, limitations, database consequence, practical implication and next action without reproducing bulk BHA responses.

## Lessons learned

1. **Do not infer semantics from an API parameter name.** `resultsAvailable=true` can return an abandoned fixture whose detail says `resultsAvailable=0`.
2. **Historical depth is a source-family question, not one date.** Fixture discovery, fixture detail, race lists and results have different observed boundaries.
3. **`not_addressable` is not the same as endpoint absence.** A downstream endpoint cannot be assigned a 404/start boundary when the upstream public chain supplies no identifier with which to test it.
4. **Zero-result historical probes need positive controls.** The apparent 2022–2025 gap disappeared when independently known racing dates were tested.
5. **Automation should fail closed and then be audited.** The first generated conclusion over-compressed direct 404s and upstream non-addressability; the audit refinement corrected the wording before closeout.
6. **Do not build a database because an API exists.** Establish source semantics, continuity and the minimum evidence rule first.

## Closeout checklist

| Requirement | Status | Evidence / reason |
|---|---|---|
| Final conclusion and limitations | complete | executed notebook + audited conclusion |
| Reproducibility / archival classification | complete | archival construction record; reusable client retained separately |
| Persisted evidence | complete | committed executed notebook; cached request/derived evidence locally retained |
| Reusable code | complete | `src/inside_rails/bha_api.py` |
| Focused tests | complete | 5 BHA client tests passed |
| Independent source-wide validator | not applicable | no source-wide transformation/classification or DB integration created |
| Database integration consequence | complete | no DB change; usage contract in `docs/BHA_STRUCTURED_SOURCE_USAGE.md` |
| Manual-verification decision | complete | `specialist_reference` |
| Reader report | complete | Notebook 28 report |
| Lessons learned | complete | this closeout record |
| Audit/status records | complete | post-v4 investigation register + README/project plan updates |
| Database v5 decision | explicitly out of scope | no candidate or schema design authorised |

## Next bounded question

Before any Database v5 population repair is designed, establish:

> **What is the smallest reliable BHA evidence rule for identifying every actually run Great Britain race in the 2015-present period, despite fixture-search `resultsAvailable` semantics?**

The next investigation should use result evidence as the realised-racing signal and fixture/admin/race-list evidence as explanatory programme state. It should not assume that fixture-search filtering already provides the completed-race population.
