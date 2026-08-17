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

Notebook 28 established the decisive counterexample at Worcester on 25 September 2020:

- the Worcester fixture was recovered through a fixture search using `resultsAvailable=true`;
- fixture detail returned HTTP 200 with `resultsAvailable=0`;
- fixture detail returned `abandonedReasonCode=1`;
- fixture detail returned `goingText = "ABANDONED - Abandoned (72 Hours Before)"`;
- the fixture race-list resource returned HTTP 200 and retained one programmed race.

Therefore:

> `resultsAvailable=true` on fixture search is **not** sufficient evidence that the fixture or its programmed races actually produced official results.

The query parameter is a transport/query behaviour observed in the BHA frontend estate, not an Inside Rails semantic contract.

## Programme state, administrative state and realised racing are separate

Future work must preserve at least these distinctions:

1. **fixture discovery/programme evidence** — the fixture appears in the BHA fixture surface;
2. **fixture administrative state** — abandonment/status/detail evidence attached to the fixture;
3. **race programme evidence** — a race appears in the fixture race-list resource;
4. **realised official result evidence** — a race result resource contains an official result;
5. **runner-level result evidence** — official result runner rows are present.

A programmed race can remain visible even when the fixture was abandoned. Race-list presence alone therefore does not prove that a race took place.

## Population work

For race-population completeness or reconstruction:

- do not use fixture discovery alone as the completed-race denominator;
- do not use `resultsAvailable=true` as a completed-racing predicate;
- use official result evidence as the primary evidence that a race actually produced a result;
- use fixture detail/status and race-list evidence to explain programme changes, abandonment and other non-realised states;
- preserve BHA fixture/race identifiers as external provenance until a separate identity-governance decision is made;
- test continuity for the exact period and source family required rather than assuming that a populated older and newer sample proves complete history between them.

## Database consequence

Notebook 28 authorises **no Database v5 change**.

Database v4 remains the accepted immutable analytical release. The findings justify source-governed future acquisition/reconciliation work, not automatic import.

If a later investigation proposes a database population repair or new official-source layer, it must separately establish:

- the exact completed-race population predicate;
- historical coverage and continuity over the required period;
- identity/reconciliation rules;
- update behaviour;
- persisted provenance;
- licensing/usage implications where relevant;
- candidate-build and validation requirements.

## Provenance

Primary investigation:

`notebooks/28_bha_historical_race_data_depth.ipynb`

Reader report:

`reports/notebook_28_bha_historical_race_data_depth.md`

Closeout:

`docs/notebooks/NOTEBOOK_28_BHA_HISTORICAL_RACE_DATA_DEPTH_CLOSEOUT.md`

External controls used for the bounded 1994 and 2020 context are preserved in:

`data/reference/bha_historical_depth_external_controls.csv`
