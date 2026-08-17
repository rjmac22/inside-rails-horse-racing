# BHA structured source usage

## Purpose

This document records the source-capability and semantic boundaries established by Notebooks 26–29 for the structured service used by the British Horseracing Authority public frontend.

It is a source-usage contract for future Inside Rails research. It is **not** a Database v5 design, an API-stability guarantee, or permission to treat every returned field as a governed racing concept.

## Public structured service

Observed service root:

`https://api09.horseracing.software/bha/v1`

The reusable client is:

`src/inside_rails/bha_api.py`

It reproduces the access pattern used by the current public BHA Results frontend, keeps the frontend Bearer value in memory only, and caches returned BHA responses with request/status/provenance metadata.

The service is used by a public BHA frontend. Inside Rails does **not** treat that observation as a documented or permanent public API contract.

## Historical depth established by Notebook 28

The current structured surface does not have one defensible historical start date.

### Fixture discovery

- fixture discovery is populated on the controlled 8 April 1995 date;
- the controlled 9 April 1994 BHA fixture query is empty, while independent result evidence confirms racing at Aintree that day;
- the 1994/1995 comparison is therefore strong observed lower-edge evidence around 1995, not a contractual archive boundary.

### Fixture detail and fixture race lists

In bounded samples:

- 1999 fixture-detail requests return HTTP 404;
- 1999 fixture-race-list requests return HTTP 404;
- corresponding sampled 2000 resources are populated.

This establishes a directly observed sampled lower-edge split between 1999 and 2000 for those two resource families.

### Race detail, official results and runner results

Populated race-detail, result and runner-level resources are demonstrated from sampled 2000 races.

The direct pre-2000 endpoint boundary is **unresolved** because pre-2000 fixture race lists were unavailable, so no BHA race reference survived through the public chain with which to challenge those endpoints directly.

Do not rewrite this as “results start in 2000”.

## Fixture-search `resultsAvailable` is not a completed-racing flag

Notebook 28 established the decisive fixture-level counterexample at Worcester on 25 September 2020:

- the Worcester fixture was recoverable through a fixture search using `resultsAvailable=true`;
- fixture detail returned HTTP 200 with `resultsAvailable=0`;
- fixture detail returned `abandonedReasonCode=1`;
- fixture detail returned `goingText = "ABANDONED - Abandoned (72 Hours Before)"`;
- the fixture-races resource returned HTTP 200 and retained one programmed race.

Therefore:

> `resultsAvailable=true` on fixture search is **not** sufficient evidence that the fixture or its programmed races actually produced official results.

The query parameter is a transport/query behaviour observed in the BHA frontend estate, not an Inside Rails semantic contract.

## Race-level execution semantics established by Notebook 29

Notebook 29 followed the Worcester programme evidence to individual-race grain.

The retained programmed race was addressable as:

`2020:8816:0`

Its evidence was:

- fixture-race-list `abandonedReasonCode = 0`;
- fixture-race-list `winnersDetails` empty;
- race-detail `abandonedReasonCode = 0`;
- race-detail `resultsAvailable = 0`;
- race-detail `winnersDetails` absent/not useful;
- dedicated race-results resource HTTP 404.

This proves:

> **race-level `abandonedReasonCode == 0` is not a realised-race predicate.**

A zero code means only that the race record does not carry a non-zero abandonment reason in that field. It does not prove that the programmed race produced an official result.

### Candidate signals surviving Notebook 29

Against 34 realised controls plus the Worcester non-realised control:

- fixture-race-list `winnersDetails` non-empty: **0 contradictions**;
- race-detail `resultsAvailable == 1`: **0 contradictions**;
- fixture-race-list `abandonedReasonCode == 0`: **1 false-positive**;
- race-detail `abandonedReasonCode == 0`: **1 false-positive**;
- race-detail `winnersDetails` non-empty: **34 false-negatives**.

The smallest promising operational candidate is therefore:

> **non-empty `winnersDetails` on the fixture-races record**

Race-detail `resultsAvailable == 1` is a useful corroborating candidate, but it requires an additional request for each race.

Neither candidate is yet authorised as a universal historical predicate. Notebook 30 must validate population-wide behaviour across the exact Source Version 1 date span before that decision is made.

## Programme state, race state and realised racing are separate

Future work must preserve at least these distinctions:

1. **fixture discovery/programme evidence** — the fixture appears in the BHA fixture surface;
2. **fixture administrative state** — fixture-level abandonment/status/detail evidence;
3. **race programme evidence** — an individual race appears in the fixture-races resource;
4. **race-level state** — fields attached to the individual race record, which must be interpreted by resource family;
5. **official result evidence** — the dedicated race-results resource contains official result rows;
6. **runner-level result evidence** — official result runner rows are present.

A programmed race can remain visible even when its fixture was abandoned. Race-list presence alone therefore does not prove that a race took place. Conversely, fixture-level status should not be substituted for the race-level evidence when the question is whether one particular programmed race produced an official result.

## Resource-family warning

The same apparent concept can behave differently on different BHA resources.

Notebook 29 demonstrated this directly for `winnersDetails`:

- on the **fixture-races** record, non-empty `winnersDetails` agreed with the 34 realised controls and was empty for Worcester;
- on **race detail**, `winnersDetails` was absent/not useful on the 34 realised controls and therefore must not be used as a completed-race signal.

Field name alone is not a semantic contract. Always bind an interpretation to the exact resource family that was validated.

## Population work

For race-population completeness or reconstruction:

- do not use fixture discovery alone as the completed-race denominator;
- do not use fixture-search `resultsAvailable=true` as a completed-racing predicate;
- do not use race-level `abandonedReasonCode == 0` as a completed-racing predicate;
- use fixture-races as programme evidence and preserve every programmed race before classification;
- treat fixture-race-list non-empty `winnersDetails` as the **candidate** low-cost realised-race signal pending Notebook 30 validation;
- use race-detail `resultsAvailable` and the dedicated race-results endpoint to challenge candidate-negative, anomalous and sampled candidate-positive rows;
- treat race-detail `winnersDetails` as **not authorised** for result-presence classification;
- preserve BHA fixture/race identifiers as external provenance until a separate identity-governance decision is made;
- test continuity for the exact period and source family required rather than assuming that a populated older and newer sample proves complete history between them.

## Database consequence

Notebooks 28–29 authorise **no Database v5 change**.

Database v4 remains the accepted immutable analytical release. The findings justify source-governed future acquisition/reconciliation work, not automatic import.

If a later investigation proposes a database population repair or new official-source layer, it must separately establish:

- the final realised-race population predicate;
- historical coverage and continuity over the required period;
- identity/reconciliation rules;
- update behaviour;
- persisted provenance;
- licensing/usage implications where relevant;
- candidate-build and validation requirements.

## Provenance

Historical-depth investigation:

`notebooks/28_bha_historical_race_data_depth.ipynb`

Race-level execution semantics:

`notebooks/29_bha_race_execution_state.ipynb`

Reports:

- `reports/notebook_28_bha_historical_race_data_depth.md`
- `reports/notebook_29_bha_race_execution_state.md`

Closeouts:

- `docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md`
- `docs/notebooks/NOTEBOOK_29_BHA_RACE_EXECUTION_STATE_CLOSEOUT.md`

External controls used for the bounded 1994 and 2020 context are preserved in:

`data/reference/bha_historical_depth_external_controls.csv`
