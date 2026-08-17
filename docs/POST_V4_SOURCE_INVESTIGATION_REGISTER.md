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
| Notebook 28 — BHA historical race-data depth | `notebooks/28_bha_historical_race_data_depth.ipynb`; `reports/notebook_28_bha_historical_race_data_depth.md`; `docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md` | `fully_closed` | fixture discovery observed around 1995; sampled fixture-detail/race-list lower edge 1999→2000; race/result resources demonstrated from 2000; fixture-search `resultsAvailable` not a completed-racing semantic contract | Notebook 29: establish and contradiction-test candidate **race-level** realised-race signals before any population-wide crawl |
| Notebook 29 — BHA race-level execution state | `notebooks/29_bha_race_execution_state.ipynb` (generated/executed by `scripts/run_notebook_29_bha_race_execution_state.py`) | `prepared_awaiting_autonomous_execution` | pending — tests race-level `abandonedReasonCode` / `winnersDetails` against dedicated result-resource presence at individual-race grain | run the bounded controls + stratified contradiction sample; audit the executed notebook; only then decide whether a population-wide Notebook 30 is justified |

## Notebook 26 — population completeness

The investigation established a genuine population defect in the immutable third-party source.

On 6 June 2020 official BHA evidence contained 28 GB races:

- Newcastle — 10;
- Newmarket — 9;
- Lingfield Park — 9.

Source Version 1 contained only the 10 Newcastle GB races on that date. Database v4 inherited that omission rather than creating it.

The broader 2020 investigation found the missing-race pattern concentrated in complete missing fixtures. Retained fixtures reconciled exactly at race count in the deficient months.

Database consequence at closeout: **none**. Database v4 remains the accepted immutable release; the defect is documented rather than silently repaired.

## Notebook 27 — BHA official-source feasibility

Notebook 27 demonstrated that the BHA public estate is a network of separate official information systems rather than one replacement database.

It established structured fixture/race/result access sufficient for a controlled 34/34 BHA-to-v4 reconciliation on 27 May 2026 and identified additional official information families including going/weather/watering, officials, ratings, horse/participant histories, Stewards material, fixture lists and statistical packs.

Semantic field names were not accepted as contracts. Examples included non-finisher `finishTime`, entry-stage weight, `maxRunners`, nominations versus entries and other resource-specific traps.

No Database v5 adoption decision followed from feasibility alone.

## Notebook 28 — historical depth

Notebook 28 established that historical depth differs by source family.

Key bounded findings:

- controlled fixture discovery is populated on 8 April 1995;
- a known racing date on 9 April 1994 returns no fixture-search records, providing observed lower-edge evidence around 1995;
- sampled 1999 fixture-detail and fixture-race-list resources return direct HTTP 404;
- sampled 2000 fixture-detail, race-list, race-detail, result and runner-level resources are populated;
- the direct pre-2000 race-detail/result endpoint boundary remains unresolved because the upstream race-list chain supplies no addressable pre-2000 race reference;
- the first-pass apparent 2022–2025 gap was not reproduced on known racing dates;
- fixture-search `resultsAvailable=true` can return an abandoned fixture and is not a completed-racing predicate.

The enduring source-use contract is:

`docs/BHA_STRUCTURED_SOURCE_USAGE.md`

## Correct evidence grain for “did this race go ahead?”

Notebook 26's individual race-detail work exposed race-level:

- `abandonedReasonCode`;
- `winnersDetails`;
- result runner/winner material.

Therefore the next population question must be asked at **race grain**:

> **race list = programmed race; race-level state/result = candidate realised-race evidence; fixture state = administrative context.**

Fixture-level abandonment remains important for explaining whole-fixture state, but it must not automatically replace the race-level test when deciding whether one particular programmed race went ahead.

The exact combination of race-level abandonment/result/winner/runner evidence has not yet been validated.

## Notebook 29 — race-level execution-state semantics

Notebook 29 deliberately separates **semantic rule discovery** from **population-wide validation**.

Bounded question:

> **What BHA race-level evidence reliably distinguishes a programmed Great Britain race that produced an official result from a programmed race that did not?**

The dedicated BHA race-results resource is the validation target. Candidate signals are measured separately on the fixture-races record and the individual race-detail record:

- `abandonedReasonCode == 0`;
- non-empty `winnersDetails`;
- the combination of those two signals.

The notebook first uses controlled completed and non-realised/programme-change cases, then challenges the candidates using at most one ordinary fixture per year from 2015–2026. It also searches the sampled evidence for fixtures containing both realised and non-realised races rather than relying on fixture-level status to infer individual race state.

This is intentionally **not** an all-history crawl. A candidate with zero contradictions earns only the right to be tested population-wide in a later bounded investigation.

## Current next bounded investigation

Run and audit Notebook 29.

If one or more race-level candidates survive the controlled and stratified contradiction tests, open a separate Notebook 30 to ask:

> **Does the surviving race-level realised-race predicate remain complete and stable across all addressable Great Britain races in 2015-present?**

If no candidate survives, do not scale acquisition. Investigate the contradiction classes first.

Required discipline:

- start from individual race objects/results, not fixture-search `resultsAvailable`;
- include completed races and known non-realised/programme-change controls;
- use fixture status only as administrative/contextual evidence;
- distinguish race-list programme state from race-detail/result state;
- test semantics cheaply before population-wide validation;
- do not design Database v5 until the realised-race predicate is governed.
