# Post-v4 source investigation register

## Purpose

This register records correctness/source-capability investigations opened after Database v4 and outside the numbered Great Britain reader-study sequence.

These investigations can change what sources are trusted or how future population work must be designed without automatically changing the accepted database.

Database v4 remains immutable until a separate candidate build, validation and release process is explicitly authorised.

## Register

| Investigation | Primary evidence | Status | Durable consequence | Next action |
|---|---|---|---|---|
| Notebook 26 — Great Britain race-population completeness | `notebooks/26_gb_race_population_completeness.ipynb` | `fully_closed` | Source Version 1 / Database v4 is materially incomplete for GB racing in 2020; whole fixtures are absent from SV1 rather than lost during v4 construction | use BHA official evidence to establish a trustworthy realised-race population rule before repair design |
| Notebook 27 — BHA official-source feasibility | `notebooks/27_bha_official_source_feasibility.ipynb`; `reports/notebook_27_bha_official_source_feasibility.md` | `fully_closed_feasibility_inventory` | BHA public estate contains multiple useful official source families; no single feed/schema/database-adoption decision was authorised | historical-depth investigation completed in Notebook 28 |
| Notebook 28 — BHA historical race-data depth | `notebooks/28_bha_historical_race_data_depth.ipynb`; `reports/notebook_28_bha_historical_race_data_depth.md`; `docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md` | `fully_closed` | fixture discovery observed around 1995; sampled fixture-detail/race-list lower edge 1999→2000; fixture-search `resultsAvailable` is not a completed-racing semantic contract | race-level semantics completed in Notebook 29 |
| Notebook 29 — BHA race-level execution state | `notebooks/29_bha_race_execution_state.ipynb`; `reports/notebook_29_bha_race_execution_state.md`; `docs/notebooks/NOTEBOOK_29_BHA_RACE_EXECUTION_STATE_CLOSEOUT.md` | `fully_closed` | race-level `abandonedReasonCode == 0` rejected; fixture-race-list non-empty `winnersDetails` and race-detail `resultsAvailable == 1` survive bounded positive/negative contradiction testing | Notebook 30: population-wide candidate-state census and exception validation over 2015-01-01..2026-05-27 |
| Notebook 30 — BHA realised-race population validation | generated/executed by `scripts/run_notebook_30_bha_realised_race_population_validation.py` | `prepared_for_autonomous_execution` | pending — validates the cheapest surviving realised-race candidate across the exact Source Version 1 period without brute-force result calls for every apparent completed race | run autonomously, commit executed notebook, audit contradictions before any population-repair design |

## Notebook 26 — population completeness

The investigation established a genuine population defect in the immutable third-party source.

On 6 June 2020 official BHA evidence contained 28 GB races: Newcastle 10, Newmarket 9 and Lingfield Park 9. Source Version 1 contained only the 10 Newcastle GB races on that date. Database v4 inherited that omission rather than creating it.

The broader 2020 investigation found the missing-race pattern concentrated in complete missing fixtures. Retained fixtures reconciled exactly at race count in the deficient months.

Database consequence at closeout: **none**.

## Notebook 27 — BHA official-source feasibility

Notebook 27 demonstrated that the BHA public estate is a network of separate official information systems rather than one replacement database.

It established structured fixture/race/result access sufficient for a controlled 34/34 BHA-to-v4 reconciliation on 27 May 2026 and identified multiple additional official information families.

No Database v5 adoption decision followed from feasibility alone.

## Notebook 28 — historical depth

Notebook 28 established that historical depth differs by source family and that fixture-search `resultsAvailable=true` is not a completed-racing predicate.

The enduring source-use contract is:

`docs/BHA_STRUCTURED_SOURCE_USAGE.md`

## Notebook 29 — race-level execution-state semantics

Notebook 29 established the race-level counterexample needed to avoid another fixture-level shortcut.

Worcester on 25 September 2020 retained one addressable programmed race, BHA race `2020:8816:0`. The race carried `abandonedReasonCode = 0` on both fixture-races and race-detail records, but race-detail `resultsAvailable = 0` and the dedicated race-results endpoint returned HTTP 404.

Therefore race-level `abandonedReasonCode == 0` is **not** evidence that a programmed race produced an official result.

Against 34 realised races plus the Worcester non-realised race:

- fixture-race-list `winnersDetails` non-empty: 0 contradictions;
- race-detail `resultsAvailable == 1`: 0 contradictions;
- race-level abandonment-code-only rules: false-positive on Worcester;
- race-detail `winnersDetails`: false-negative on all 34 realised controls.

The smallest promising operational candidate is therefore non-empty fixture-race-list `winnersDetails`, with race-detail `resultsAvailable` as a corroborating signal.

This result is now governed in:

- `docs/BHA_STRUCTURED_SOURCE_USAGE.md`;
- `reports/notebook_29_bha_race_execution_state.md`;
- `docs/notebooks/NOTEBOOK_29_BHA_RACE_EXECUTION_STATE_CLOSEOUT.md`.

## Notebook 30 — population-wide validation

Bounded question:

> **Across the complete BHA fixture-race-list population corresponding to Source Version 1's GB date span (2015-01-01 through 2026-05-27), does non-empty fixture-race-list `winnersDetails` behave as a stable and sufficiently reliable realised-race signal?**

Method discipline:

- enumerate every fixture and every fixture-race-list row in the period;
- preserve every programmed race and its BHA external reference before classification;
- census `winnersDetails` state population-wide;
- exhaustively challenge every candidate-negative, non-addressable and anomalous row;
- challenge a deterministic positive sample spanning years, months and racecourses through race detail and dedicated results;
- use race-detail `resultsAvailable` as corroboration, not as an untested replacement;
- fail closed on transport/access errors and classify source 404/empty states explicitly;
- do not issue dedicated-result requests for every apparent completed race unless contradictions make that escalation necessary;
- do not design Database v5 in this notebook.

## Current next bounded action

Run Notebook 30 autonomously, commit the executed notebook, then audit its contradiction and unresolved classes.

Only after the realised-race rule is governed should the project design a separate official-BHA-to-Source-Version-1 population reconciliation or Database v5 repair.
