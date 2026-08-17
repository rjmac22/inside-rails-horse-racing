# Notebook 29 closeout — BHA race-level execution state

Closeout date: **17 August 2026**

Notebook:

`notebooks/29_bha_race_execution_state.ipynb`

Reader report:

`reports/notebook_29_bha_race_execution_state.md`

## Status

**Fully closed — race-level semantics/candidate nomination complete.**

Notebook 29 answered its bounded semantics question. It did not perform the all-period population validation, which is deliberately separated into the next notebook.

## Bounded question

> What BHA race-level evidence reliably distinguishes a programmed Great Britain race that produced an official result from a programmed race that did not?

For Notebook 29, realised racing is defined operationally as a programmed BHA race whose dedicated race-results resource contains one or more official result rows.

## Final conclusion

The investigation established that race-level `abandonedReasonCode` is **not** a completed-race predicate.

The decisive negative control is Worcester on 25 September 2020. The abandoned fixture retained one addressable programmed race, BHA race `2020:8816:0`. That race carried `abandonedReasonCode = 0` in both the fixture-races and race-detail records, but race-detail `resultsAvailable = 0` and the dedicated race-results resource returned HTTP 404.

Against the audited control set of 34 realised races plus one non-realised race:

- fixture-race-list `winnersDetails` non-empty: **0 contradictions**;
- race-detail `resultsAvailable == 1`: **0 contradictions**;
- fixture-race-list `abandonedReasonCode == 0`: **1 false-positive**;
- race-detail `abandonedReasonCode == 0`: **1 false-positive**;
- race-detail `winnersDetails` non-empty: **34 false-negatives**.

The smallest promising operational candidate is therefore fixture-race-list `winnersDetails` non-empty, with race-detail `resultsAvailable` as a more expensive corroborating signal.

Neither is yet authorised as a universal 2015-present predicate until Notebook 30 completes population-wide validation.

## Evidence hierarchy preserved

Notebook 29 leaves the following layers distinct:

1. fixture discovery = fixture/programme presence;
2. fixture detail = administrative context;
3. fixture-races = individual programmed race records;
4. race-detail = individual race state/details;
5. dedicated race-results = official result-presence target;
6. runner rows = runner-level result evidence.

The study explicitly rejected using fixture status or race-level abandonment code as a substitute for direct result evidence.

## Audit refinement

The first autonomous pass was not accepted at face value.

It initially had only 34 positive races and no addressable negative race. It also failed to test race-detail `resultsAvailable`, despite that field being present in the race-detail resource.

The audit refinement therefore:

- preserved the first pass as construction evidence;
- rediscovered Worcester through all fixture-search modes and deduplicated the fixture identity;
- followed the retained race-list row to race detail and dedicated results;
- added race-detail `resultsAvailable` to the candidate table;
- regenerated the final conclusion from the corrected positive/negative evidence.

That refinement produced the decisive race-level counterexample and candidate nomination.

## Reusable implementation

No new production parser or database transformation was justified.

Reusable source access remains:

`src/inside_rails/bha_api.py`

Notebook 29's acquisition, contradiction and presentation logic remains study-specific pending population validation.

## Persisted evidence

Local ignored cache namespace:

`data/cache/bha_race_execution_state/`

The executed committed notebook preserves the substantive result tables and audited conclusion.

The cache preserves individual BHA request/response provenance through the reusable client and derived research tables written by the notebook/refinement scripts.

## Validation evidence

The autonomous run completed successfully after:

- repository import preflight;
- generated code-cell compilation;
- notebook JSON round-trip validation.

The targeted audit refinement also completed successfully and rewrote the final audited conclusion.

No source-wide parser, database transformation or reference-table import was created, so a new independent database validator is **not applicable** to Notebook 29 closeout.

## Database consequence

None.

Database v4 remains the accepted immutable study database.

Notebook 29 does not create or authorise:

- Database v5;
- a BHA race identity entity;
- a repaired historical population;
- an import of BHA race/result rows;
- a migration of Source Version 1.

## Lessons learned

1. **Race-level abandonment code is still not execution truth.** A non-realised Worcester race carried `abandonedReasonCode = 0`.
2. **Resource family matters.** `winnersDetails` behaved differently on fixture-races versus race-detail records.
3. **A positive-only contradiction test cannot establish a predicate.** The first pass was correctly refused until an addressable negative race was obtained.
4. **Use the cheapest surviving signal first.** Fixture-race-list winner material can be inspected for all races with one request per fixture; race-detail/result endpoints should be reserved for exception and verification work where possible.
5. **Audit the field inventory against the candidate table.** The first pass exposed race-detail `resultsAvailable` but accidentally omitted it from the tested candidates.
6. **One problem per notebook remains the correct stop rule.** Notebook 29 establishes semantics; Notebook 30 validates population-wide behaviour.

## Closeout checklist

| Requirement | Status | Evidence / reason |
|---|---|---|
| Bounded conclusion | complete | audited executed Notebook 29 |
| Positive and negative controls | complete | 34 realised + Worcester non-realised race |
| Contradiction testing | complete | seven candidate rules audited |
| Raw/provenance preservation | complete | `BhaApiClient` cache + committed notebook |
| Reusable code decision | complete | existing BHA client retained; no premature production predicate |
| Reader report | complete | Notebook 29 report |
| Database consequence | complete | no DB change authorised |
| Lessons learned | complete | this closeout |
| Population-wide validation | deliberately separate | Notebook 30 |

## Next bounded question

> **Across the complete BHA fixture-race-list population corresponding to Source Version 1's GB date span (2015-01-01 through 2026-05-27), does non-empty fixture-race-list `winnersDetails` behave as a stable and sufficiently reliable realised-race signal, with race-detail `resultsAvailable` and dedicated results resolving every negative/anomalous case?**

That is Notebook 30. It should use a population-wide candidate census plus exhaustive exception validation rather than a brute-force dedicated-result call for every apparent completed race.
