# BHA structured source usage

## Purpose

This document records the source-capability and semantic boundaries established by Notebooks 26–28 for the structured service used by the British Horseracing Authority public frontend.

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

## `resultsAvailable` is not a governed completed-racing flag

The fixture-search parameter/field name must not be interpreted naively.

Notebook 28 established the decisive fixture-level counterexample at Worcester on 25 September 2020:

- the Worcester fixture was recovered through a fixture search using `resultsAvailable=true`;
- fixture detail returned HTTP 200 with `resultsAvailable=0`;
- fixture detail returned `abandonedReasonCode=1`;
- fixture detail returned `goingText = "ABANDONED - Abandoned (72 Hours Before)"`;
- the fixture race-list resource returned HTTP 200 and retained one programmed race.

Therefore:

> `resultsAvailable=true` on fixture search is **not** sufficient evidence that the fixture or its programmed races actually produced official results.

The query parameter is a transport/query behaviour observed in the BHA frontend estate, not an Inside Rails semantic contract.

## Race-level execution evidence is the relevant next layer

Notebook 26 had already established an important distinction that must not be lost when using the Worcester fixture example.

The **individual BHA race-detail object** exposes race-level execution/result evidence, including:

- `abandonedReasonCode`;
- `winnersDetails`;
- result-runner/result-winner group material inspected in the controlled race-detail work.

The completed 27 May 2026 34-race pilot used those individual race objects; the inspected completed races carried zero race-level abandonment code and populated winner/result evidence.

This means the correct conceptual hierarchy is not “fixture status decides whether every listed race ran”. Instead:

> **race list = programmed race; race-level state/result = candidate evidence that the individual race was realised; fixture state = administrative context.**

The exact race-level realised-race predicate is **not yet governed population-wide**. A later validation must establish how race-level `abandonedReasonCode`, result/winner material and runner results behave across completed, abandoned and other non-realised race cases before one combination is adopted as a universal rule.

## Programme state, race state and realised racing are separate

Future work must preserve at least these distinctions:

1. **fixture discovery/programme evidence** — the fixture appears in the BHA fixture surface;
2. **fixture administrative state** — fixture-level abandonment/status/detail evidence;
3. **race programme evidence** — an individual race appears in the fixture race-list resource;
4. **race-level execution state** — the individual race object carries race-specific state such as `abandonedReasonCode` and result/winner metadata;
5. **official result evidence** — the individual race/result resources contain official result material;
6. **runner-level result evidence** — official result runner rows are present.

A programmed race can remain visible even when its fixture was abandoned. Race-list presence alone therefore does not prove that a race took place. Conversely, fixture-level status should not be substituted for the race-level evidence when the question is whether one particular programmed race went ahead.

## Population work

For race-population completeness or reconstruction:

- do not use fixture discovery alone as the completed-race denominator;
- do not use `resultsAvailable=true` as a completed-racing predicate;
- start from the **individual race object and its official result evidence** when deciding whether a programmed race was realised;
- treat race-level `abandonedReasonCode`, winner/result material and runner results as the candidate execution evidence to be validated population-wide;
- use fixture detail/status as administrative context, especially for whole-fixture abandonment, rather than automatically using it as the primary race-level execution decision;
- use race-list evidence to establish what was programmed, not what necessarily happened;
- preserve BHA fixture/race identifiers as external provenance until a separate identity-governance decision is made;
- test continuity for the exact period and source family required rather than assuming that a populated older and newer sample proves complete history between them.

## Database consequence

Notebook 28 authorises **no Database v5 change**.

Database v4 remains the accepted immutable analytical release. The findings justify source-governed future acquisition/reconciliation work, not automatic import.

If a later investigation proposes a database population repair or new official-source layer, it must separately establish:

- the exact race-level completed/realised predicate;
- historical coverage and continuity over the required period;
- identity/reconciliation rules;
- update behaviour;
- persisted provenance;
- licensing/usage implications where relevant;
- candidate-build and validation requirements.

## Provenance

Primary historical-depth investigation:

`notebooks/28_bha_historical_race_data_depth.ipynb`

The race-level execution fields were already inspected in:

`notebooks/26_gb_race_population_completeness.ipynb`

Reader report:

`reports/notebook_28_bha_historical_race_data_depth.md`

Closeout:

`docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md`

External controls used for the bounded 1994 and 2020 context are preserved in:

`data/reference/bha_historical_depth_external_controls.csv`
