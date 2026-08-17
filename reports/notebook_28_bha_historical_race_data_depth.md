# Notebook 28 — BHA historical race-data depth

Source notebook: `notebooks/28_bha_historical_race_data_depth.ipynb`

Status: **analytically complete; closeout governed on 17 August 2026**

## Executive conclusion

The BHA public structured racing estate does **not** have one defensible historical start date.

The current fixture-search surface is demonstrably populated on a controlled British racing date in **1995**, while sampled fixture-detail and fixture-race-list resources remain unavailable through **1999** and become populated in **2000**. Race-detail, official-result and runner-level resources are demonstrated from sampled 2000 races, but their direct pre-2000 endpoint boundary remains unresolved because the upstream pre-2000 race-list chain does not provide addressable BHA race references.

A second, more important semantic finding is that the fixture-search `resultsAvailable` parameter must **not** be treated as a completed-racing flag. An abandoned Worcester fixture on 25 September 2020 was recovered through a `resultsAvailable=true` fixture query even though its own fixture detail reported `resultsAvailable=0`, `abandonedReasonCode=1` and `ABANDONED - Abandoned (72 Hours Before)`. Its race-list resource still retained one programmed race.

Notebook 26 had already inspected the **individual race object**, where the BHA exposes race-level `abandonedReasonCode`, `winnersDetails` and result-group material. That makes race-level state/result evidence—not fixture status—the correct candidate layer for deciding whether one particular programmed race went ahead. Fixture state remains administrative context, especially where a whole fixture was abandoned.

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

The decisive fixture-level counterexample is Worcester on 25 September 2020.

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

## Race-level execution state

For the question **“did this individual programmed race actually go ahead?”**, fixture-level abandonment is not the most precise source layer.

Notebook 26's controlled individual-race inspection exposed race-level fields including:

- `abandonedReasonCode`;
- `winnersDetails`;
- result-runner/result-winner group material.

The completed 27 May 2026 34-race pilot inspected individual race objects and found zero race-level abandonment codes with populated winner/result evidence across the completed sample.

The correct working hierarchy is therefore:

> **race list = programmed race; race-level state/result = candidate evidence that the race was realised; fixture state = administrative context.**

This does **not** yet authorise one universal race-level predicate. The candidate combination of race-level abandonment state plus winner/result/runner evidence still needs population-wide validation across completed and non-realised GB races.

## Interpretation

The BHA structured estate should be treated as a set of related source families rather than one homogeneous historical feed.

At minimum, future race-population work must distinguish:

1. fixture discovery/programme evidence;
2. fixture administrative/status evidence;
3. race-programme evidence;
4. race-level execution state;
5. official result evidence;
6. runner-level result evidence.

The existence of an object at an earlier layer does not prove the existence or meaning of a later one, and a fixture-level state should not automatically be substituted for an individual race-level state.

## Confidence

### High confidence

- fixture discovery is demonstrably available on the controlled 8 April 1995 date;
- sampled 1999 fixture-detail and fixture-race-list resources return direct HTTP 404;
- sampled 2000 resources are populated through runner-level result data;
- `resultsAvailable=true` cannot safely be interpreted as “fixture produced results”;
- programmed race material can survive for an abandoned fixture;
- the BHA individual race object exposes race-level abandonment/result evidence suitable for targeted execution-state testing.

### Bounded / unresolved

- the exact first date of fixture-search coverage is not established;
- the exact first date of fixture-detail/race-list coverage is not established beyond the sampled 1999→2000 split;
- the direct pre-2000 boundary of race-detail/results endpoints is unresolved because pre-2000 race references are not addressable through the surviving public chain;
- complete continuity of every resource family across every year has not been proved;
- the exact population-wide race-level predicate for “realised race” is not yet validated;
- the observed service is not treated as a formally documented stable API contract.

## Database consequence

None at closeout.

Database v4 remains the accepted immutable analytical release. Notebook 28 does not authorise a Database v5 candidate, new fixture identity, new race identity or official-source import.

The durable consequence is the source-usage contract in `docs/BHA_STRUCTURED_SOURCE_USAGE.md`.

## Practical implication

The BHA structured service is materially more useful than Source Version 1 for official British source validation, but it cannot be used by simply downloading fixture/race-list rows and treating them as completed races.

For an individual programmed race, the **race-level object/result state is the candidate realised-racing signal**. Fixture state should explain administrative context around it, not automatically decide every race's execution state.

## Next action

The next bounded source question should now be framed as a validation problem rather than a discovery problem:

> **Does the BHA race-level execution/result state (`abandonedReasonCode` plus official winner/result/runner evidence) provide a complete and stable realised-race predicate across all addressable Great Britain races in 2015-present?**

Validate that candidate rule across completed races, abandoned/non-realised race cases and whole-fixture abandonment before any Database v5 population repair or design is attempted.
