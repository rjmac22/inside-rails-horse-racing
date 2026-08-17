# Notebook 29 — BHA race-level execution state

Source notebook: `notebooks/29_bha_race_execution_state.ipynb`

Status: **analytically complete; candidate semantics established**

## Executive conclusion

Notebook 29 established that **race-level `abandonedReasonCode` is not a reliable realised-race predicate**.

The decisive counterexample is the programmed Worcester race retained for the wholly abandoned fixture on 25 September 2020. The race remained addressable as BHA race `2020:8816:0` and carried race-level `abandonedReasonCode = 0`, yet its race-detail object reported `resultsAvailable = 0` and its dedicated race-results endpoint returned HTTP 404.

Two candidate signals survived the bounded positive/negative contradiction test:

1. **fixture-race-list `winnersDetails` non-empty**;
2. **race-detail `resultsAvailable == 1`**.

The first is operationally cheaper because it is returned with the fixture race list rather than requiring one race-detail request per race.

Race-detail `winnersDetails` is explicitly rejected: it was empty/absent for all 34 completed-race controls even though those races had official result rows.

Notebook 29 does **not** yet authorise the winner signal as a universal 2015-present population predicate. It nominates that signal for population-wide validation in the next bounded notebook.

## Bounded question

> What BHA race-level evidence reliably distinguishes a programmed Great Britain race that produced an official result from a programmed race that did not?

For this investigation, a **realised race** means a programmed BHA race whose dedicated race-results resource contains one or more official result rows.

That is intentionally narrower than the physical question of whether a race started before later being voided or otherwise left without an official result.

## Positive control

Notebook 29 reproduced the established 27 May 2026 control:

- 5 BHA fixtures;
- 34 individual programmed races;
- 34/34 dedicated race-results resources populated;
- 34/34 fixture-race-list records with `abandonedReasonCode = 0`;
- 34/34 fixture-race-list records with non-empty `winnersDetails`;
- 34/34 race-detail records with `abandonedReasonCode = 0`;
- 34/34 race-detail records with `resultsAvailable = 1` after the audit refinement;
- race-detail `winnersDetails` was not a usable result-presence field.

## Negative control — Worcester, 25 September 2020

Notebook 28 had already established the fixture context:

- fixtureId `1838`;
- fixture detail `resultsAvailable = 0`;
- fixture detail `abandonedReasonCode = 1`;
- `goingText = "ABANDONED - Abandoned (72 Hours Before)"`;
- one programmed race retained in the fixture-races resource.

Notebook 29 followed that surviving programmed race to individual-race grain.

Observed race evidence:

| Evidence | Worcester programmed race |
|---|---|
| BHA race reference | `2020:8816:0` |
| fixture-race-list `abandonedReasonCode` | `0` |
| fixture-race-list `winnersDetails` | empty |
| race-detail `abandonedReasonCode` | `0` |
| race-detail `resultsAvailable` | `0` |
| race-detail `winnersDetails` | absent / not useful |
| dedicated race-results resource | HTTP 404 |
| realised-race target | `False` |

This is the key semantic result:

> **`abandonedReasonCode == 0` at individual-race level does not prove that the race produced an official result.**

The value means only that the race object does not carry a non-zero abandonment reason in that field. It is not a completed-race flag.

## Candidate-rule contradiction table

The audited 35-race control set contains 34 realised races and one addressable non-realised race.

| Candidate | Contradictions | Interpretation |
|---|---:|---|
| fixture-race-list `abandonedReasonCode == 0` | 1 | rejected; false-positive on Worcester |
| fixture-race-list `winnersDetails` non-empty | 0 | candidate for population-wide validation |
| fixture-race-list abandonment + winner | 0 | survives, but abandonment adds no demonstrated value |
| race-detail `abandonedReasonCode == 0` | 1 | rejected; false-positive on Worcester |
| race-detail `resultsAvailable == 1` | 0 | candidate / corroborating signal |
| race-detail `winnersDetails` non-empty | 34 | rejected; false-negative on every realised control |
| race-detail abandonment + `resultsAvailable` | 0 | survives, but abandonment adds no demonstrated value |

## Resource semantics

Notebook 29 reinforces that similarly named or related fields cannot be moved between BHA resource families without testing.

In particular:

- `winnersDetails` is useful on the **fixture-races** record in this test;
- `winnersDetails` is not useful as a result-presence signal on the **race-detail** record;
- `resultsAvailable` on **race detail** agreed with dedicated result availability in the bounded test;
- `abandonedReasonCode` on both race-list and race-detail records is insufficient by itself.

## Operational implication

For a future historical population census, the smallest promising source rule is:

> **programmed race + non-empty fixture-race-list `winnersDetails` = candidate realised race**

Why this candidate is preferred for validation:

- one fixture-races request returns all programmed races for that fixture;
- it already carries winner material;
- it avoids a separate race-detail request for every apparent completed race;
- every candidate-negative or anomalous row can then be challenged through race detail and the dedicated result endpoint.

This is an efficiency decision, not a semantic shortcut. The field still needs population-wide validation.

## What Notebook 29 does not establish

Notebook 29 does not establish:

- complete stability of `winnersDetails` across 2015–2026;
- that every non-empty winner record necessarily has a dedicated result across the entire period;
- that every empty winner record necessarily lacks an official result across the entire period;
- the final BHA completed-race population;
- a repair rule for Source Version 1 or Database v4;
- any Database v5 design.

## Next bounded action

Notebook 30 should perform a **population-wide candidate-state census** over the exact Source Version 1 period, 1 January 2015 through 27 May 2026.

It should:

1. enumerate every BHA fixture and fixture-race-list row in that period;
2. preserve every race's `winnersDetails` state and BHA external reference;
3. exhaustively challenge every candidate-negative, non-addressable and anomalous race;
4. verify a deterministic positive sample across years, months and racecourses through race detail and the dedicated result endpoint;
5. stop and classify contradictions rather than silently coercing them;
6. nominate a governed realised-race population rule only if the evidence survives.

No Database v5 work should begin before that validation is complete.
