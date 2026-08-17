# Notebook 28 — BHA historical race-data depth

Source notebook: `notebooks/28_bha_historical_race_data_depth.ipynb`

Status: **analytically complete; closeout governed on 17 August 2026**

## Executive conclusion

The BHA public structured racing estate does **not** have one defensible historical start date.

The current fixture-search surface is demonstrably populated on a controlled British racing date in **1995**, while sampled fixture-detail and fixture-race-list resources remain unavailable through **1999** and become populated in **2000**. Race-detail, official-result and runner-level resources are demonstrated from sampled 2000 races, but their direct pre-2000 endpoint boundary remains unresolved because the upstream pre-2000 race-list chain does not provide addressable BHA race references.

A second, more important semantic finding is that the fixture-search `resultsAvailable` parameter must **not** be treated as a completed-racing flag. An abandoned Worcester fixture on 25 September 2020 was recovered through a `resultsAvailable=true` fixture query even though its own fixture detail reported `resultsAvailable=0`, `abandonedReasonCode=1` and `ABANDONED - Abandoned (72 Hours Before)`. Its race-list resource still retained one programmed race.

Therefore fixture discovery, administrative state, programmed races and actually realised official results must remain separate evidence layers.

No Database v5 design or import decision follows automatically from this investigation.

## Core evidence

### Fixture catalogue lower edge

On 8 April 1995 the BHA fixture search returned:

| Course | fixtureId | Search `resultsAvailable` | abandonedReasonCode |
|---|---:|---:|---:|
| Aintree | 1114 | True | 0 |
| Beverley | 509 | True | 0 |
| Hereford | 910 | True | 0 |

All three corresponding fixture-detail requests returned HTTP 404. All three corresponding fixture-race-list requests also returned HTTP 404.

A controlled query for 9 April 1994 returned zero fixtures in both unfiltered and `resultsAvailable=true` modes. Independent historical result evidence confirms racing at Aintree on that date, so the 1994/1995 comparison is strong observed lower-edge evidence for the current fixture surface rather than merely a comparison between racing and a non-racing day.

This remains an **observed public-service boundary**, not a contractual BHA retention guarantee.

### Detailed-resource lower edge

The bounded historical sweep found:

| Year | Fixture discovery | Fixture detail | Fixture race list | Race detail | Official results | Runner rows |
|---:|---|---|---|---|---|---|
| 1995 | available | 404 | 404 | not addressable | not addressable | not addressable |
| 1998 | available | 404 | 404 | not addressable | not addressable | not addressable |
| 1999 | available | 404 | 404 | not addressable | not addressable | not addressable |
| 2000 | available | available | available | available | available | available |
| 2001 | available | available | mixed | available | available | available |
| 2005 | available | available | available | available | available | available |
| 2010 | available | available | available | available | available | available |
| 2015 | available | available | available | available | available | available |
| 2026 | available | available | available | available | available | available |

The correct interpretation is deliberately asymmetric:

- **fixture detail:** directly observed sampled lower-edge split from 1999 404 to 2000 populated;
- **fixture race lists:** directly observed sampled lower-edge split from 1999 404 to 2000 populated;
- **race detail:** demonstrated from sampled 2000 races, direct pre-2000 endpoint boundary unresolved;
- **official results / runner rows:** demonstrated from sampled 2000 races, direct pre-2000 endpoint boundary unresolved.

It would overstate the evidence to write “the BHA results API starts in 2000”.

## The apparent 2022–2025 gap

The first autonomous pass sampled seven-day windows that happened to return no fixtures for 2022–2025, despite populated earlier and current samples.

A targeted refinement used independently known racing dates:

| Date | Unfiltered fixture search | `resultsAvailable=true` |
|---|---:|---:|
| 2022-04-09 | 5 fixtures | 5 fixtures |
| 2023-04-15 | 5 fixtures | 5 fixtures |
| 2024-04-13 | 6 fixtures | 6 fixtures |
| 2025-03-14 | 5 fixtures | 5 fixtures |
| 2026-05-27 | 5 fixtures | 5 fixtures |

The apparent gap was therefore **not demonstrated as a historical archive hole**. It was an artefact of the particular first-pass windows and reinforces the need to test continuity using known racing dates rather than assuming a zero response proves historical absence.

## `resultsAvailable` semantic trap

The decisive source-internal counterexample is Worcester on 25 September 2020.

The fixture was recovered through `resultsAvailable=true`, but fixture detail returned:

```text
status: 200
resultsAvailable: 0
abandonedReasonCode: 1
goingText: ABANDONED - Abandoned (72 Hours Before)
```

Its fixture-race-list resource returned HTTP 200 with one programmed race.

Therefore:

> `resultsAvailable=true` on fixture search does not establish that a fixture or its programmed races produced official results.

This is a transport/query behaviour, not a governed racing concept.

## Interpretation

The BHA structured estate should be treated as a set of related source families rather than one homogeneous historical feed.

At minimum, future race-population work must distinguish:

1. fixture discovery/programme evidence;
2. fixture administrative/status evidence;
3. race-programme evidence;
4. realised official result evidence;
5. runner-level result evidence.

The existence of an object at an earlier layer does not prove the existence or meaning of a later one.

## Confidence

### High confidence

- fixture discovery is demonstrably available on the controlled 8 April 1995 date;
- sampled 1999 fixture-detail and fixture-race-list resources return direct HTTP 404;
- sampled 2000 resources are populated through runner-level result data;
- `resultsAvailable=true` cannot safely be interpreted as “fixture produced results”;
- programmed race material can survive for an abandoned fixture.

### Bounded / unresolved

- the exact first date of fixture-search coverage is not established;
- the exact first date of fixture-detail/race-list coverage is not established beyond the sampled 1999→2000 split;
- the direct pre-2000 boundary of race-detail/results endpoints is unresolved because pre-2000 race references are not addressable through the surviving public chain;
- complete continuity of every resource family across every year has not been proved;
- the observed service is not treated as a formally documented stable API contract.

## Database consequence

None at closeout.

Database v4 remains the accepted immutable analytical release. Notebook 28 does not authorise a Database v5 candidate, new fixture identity, new race identity or official-source import.

The durable consequence is the source-usage contract in `docs/BHA_STRUCTURED_SOURCE_USAGE.md`.

## Practical implication

The BHA structured service is materially more useful than Source Version 1 for official British source validation, but it cannot be used by simply downloading fixture rows and treating them as completed races.

For a completed-race population, official result evidence must be the realised-racing signal; fixture/race-list/admin data should explain scheduling and abandonment states around it.

## Next action

The next bounded source question should be:

> **What is the smallest reliable BHA evidence rule for identifying every actually run Great Britain race in the 2015-present period, despite fixture-search `resultsAvailable` semantics?**

This should establish a completed-race population rule before any Database v5 design or repair is attempted.
