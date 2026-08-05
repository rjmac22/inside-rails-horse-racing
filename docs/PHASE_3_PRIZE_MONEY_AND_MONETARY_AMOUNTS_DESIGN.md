# Phase 3 Prize Money and Monetary Amounts Design

## Status

Accepted conceptual design for Phase 3 entity and key planning.

This document records the intended semantic model for prize money and other monetary values before any physical schema or SQL implementation is introduced.

It is deliberately conservative. The current source contains a `prize` value on runner rows, but Notebook 13 established that this field should normally be interpreted as a runner-level recorded prize amount rather than automatically as the official value of the race.

## Purpose

The database must preserve monetary evidence without collapsing several different facts into one number.

The principal design rule is:

> A runner's recorded prize allocation, the sum of populated runner prizes, an advertised race value and the official race purse are related but distinct monetary facts.

This separation is required because the current source may contain:

- runner-level allocations;
- blank runner values;
- incomplete payment coverage;
- different currencies;
- different displayed precision;
- converted or source-presented foreign values;
- values whose exact semantic meaning has not yet been established;
- values that differ from later official evidence.

## Scope

This design covers:

- immutable raw monetary assertions from source records;
- governed interpretations of runner prize amounts;
- currency and unit scale;
- blank, zero and unresolved values;
- race-level calculated totals;
- advertised race values;
- official purse or fund values;
- payment coverage and number of paid runners;
- monetary evidence provenance;
- later correction or supplementation;
- analysis admission and disclosure requirements.

It does not yet define:

- SQL tables;
- column names;
- indexes;
- database constraints;
- jurisdiction-specific prize schedules;
- tax treatment;
- exchange-rate conversion methods;
- inflation adjustment;
- official governing-body integrations.

Those belong to later implementation or dedicated analytical studies.

## Evidence from Notebook 13

Notebook 13 established the following working interpretation for the current source:

- the `prize` field is recorded on runner rows;
- values can vary between runners in the same race;
- populated British values can be parsed as sterling amounts;
- populated Irish euro-prefixed values can be parsed as euro amounts;
- blank values should remain null rather than being replaced with zero;
- sums of runner values should be described as recorded runner prize totals, not automatically as total race purses;
- the count of paid runners should be based on observed populated runner rows, not an assumed payment schedule;
- foreign values outside governed jurisdictions require later jurisdiction-specific study.

This design generalises those conclusions into a durable model.

## Core concepts

The model separates at least seven concepts.

### 1. Raw monetary assertion

A raw monetary assertion is the exact source-presented value associated with one immutable source record and one source field.

For the current source, this includes the exact `prize` text or value attached to a runner row.

The raw assertion must preserve:

- the exact source value;
- whether the source value was blank;
- the source record;
- the source field;
- the exact source version;
- the source relation;
- any source-presented symbol, prefix, suffix, punctuation or decimal precision.

The raw assertion is evidence. It is not itself a verified monetary fact.

### 2. Governed runner prize allocation

A governed runner prize allocation is the project's interpretation that a specific monetary amount was recorded or evidenced for a specific runner's participation in a specific race.

It must remain linked to:

- the runner record;
- the supporting raw monetary assertion or external evidence;
- the interpreted amount;
- currency;
- unit scale;
- semantic status;
- interpretation method;
- confidence or review status;
- governance release.

A runner prize allocation is not automatically the amount ultimately received by an owner, trainer, jockey or other beneficiary.

It represents the prize amount attached to the runner under the supported interpretation.

### 3. Recorded runner prize total

A recorded runner prize total is a derived sum of governed runner prize allocations admitted for one race under a stated rule.

It is not automatically:

- the official race purse;
- the advertised race value;
- the total fund distributed;
- the total including bonuses, premiums or breeder awards;
- the total including missing runner allocations.

Every such total must identify:

- the race occurrence;
- the governing result or prize release used;
- which runner allocations were included;
- the currency;
- whether any values were unresolved or excluded;
- the calculation rule.

### 4. Advertised race value

An advertised race value is a race-level amount presented before or around the event as the stated value of the race.

It may represent different things in different jurisdictions or publications, including:

- total prize fund;
- guaranteed value;
- value to the winner;
- added money;
- minimum value;
- a marketing description.

It must therefore carry an explicit semantic type and provenance.

An advertised value must never be inferred merely by summing runner-level prize values.

### 5. Official race purse or fund

An official race purse or prize fund is a race-level monetary fact supported by an authoritative source under a defined jurisdictional meaning.

It may still need to distinguish:

- gross purse;
- distributable purse;
- base purse;
- added money;
- bonuses;
- premiums;
- breeder or owner awards;
- scheme payments;
- amounts conditional on eligibility.

The database must not force all of these into one undifferentiated `prize_money` figure.

### 6. Payment coverage observation

A payment coverage observation describes how many runner records have a populated or governed monetary allocation under a specified source and release.

This is distinct from the official number of paid places.

For example:

- five runner rows may contain populated values;
- an official schedule may pay six places;
- one source value may be missing;
- one award may be conditional or recorded elsewhere.

The observed count and the official entitlement count must remain separate.

### 7. Monetary amendment or reconciliation

A monetary amendment or reconciliation records that later evidence supplements, corrects, supersedes or disputes an earlier governed interpretation.

Earlier evidence must not be silently overwritten.

The database must preserve the sequence of interpretations and the reason for change.

## Identity and attachment rules

### Raw evidence attachment

The exact raw `prize` value remains attached to the immutable source record.

It must not be moved onto a race-level entity merely because multiple rows share the same race occurrence.

### Runner allocation attachment

A governed runner prize allocation attaches to the runner record because the present source field is runner-level evidence.

This remains true even when all populated values in a race are identical or when the field later proves to encode a particular payment convention.

### Race-level amount attachment

Advertised race values, official purse values and calculated totals attach to the race occurrence or, where appropriate, to a specific result or prize state for that race.

They must not be stored as though they were runner attributes.

### Recurring race series

Prize values do not attach permanently to a recurring race series.

Each edition may have a different:

- purse;
- currency;
- sponsor contribution;
- payment schedule;
- eligibility rule;
- bonus structure.

Series-level prize analysis must aggregate edition-level monetary facts under explicit comparability rules.

## Monetary representation

A governed monetary amount must be represented conceptually by more than a bare numeric value.

At minimum it requires:

- amount;
- currency;
- unit scale or minor-unit interpretation;
- source or evidence basis;
- semantic type;
- status.

### Amount

The amount is the governed numeric interpretation.

For currencies with conventional minor units, implementation will normally favour an exact integer minor-unit representation once currency and scale are established.

This design does not mandate a physical datatype yet.

### Currency

Currency must be explicit whenever established.

Examples include:

- GBP;
- EUR;
- USD;
- AUD.

Currency must not be inferred solely from the location of the database, the nationality of the user or a default application setting.

### Unit scale

The interpretation must distinguish whether the governed amount is represented in:

- major currency units;
- minor currency units;
- another source-specific scale;
- an unresolved scale.

For example, a displayed value of `1250.50` may be governed as 125,050 pence only after sterling and two-decimal scale are established.

### Display precision

The source's displayed precision is evidence and should remain recoverable.

Whole-number, one-decimal and two-decimal source values must not be treated as proof of different economic meanings without investigation.

The governed amount may normalise them to a common exact unit while retaining the raw presentation.

## Blank, zero and unresolved values

### Blank is not zero

A blank raw prize value means no usable amount was recorded in that source field for that source record.

It does not prove:

- the runner received nothing;
- the runner was not entitled to prize money;
- the race paid no prize money;
- the amount was zero.

Blanks must remain unknown or unrecorded unless other evidence resolves them.

### Explicit zero

An explicit source zero is different from blank.

Even an explicit zero must retain its source evidence and may require interpretation. It could mean:

- genuinely zero allocation;
- a source placeholder;
- an unavailable amount encoded as zero;
- a conversion artefact.

A study must establish its meaning before treating it as a confirmed zero payment.

### Unresolved amount

A populated source value may remain unresolved when one or more of the following is unknown:

- currency;
- scale;
- semantic meaning;
- whether a conversion has already been applied;
- whether it is a runner allocation or another race-level value;
- whether symbols or punctuation were lost.

Unresolved values remain admissible as raw evidence but not as governed comparable money.

## Jurisdiction and currency governance

Currency interpretation may depend on:

- jurisdiction;
- race date;
- source conventions;
- source version;
- displayed currency symbol;
- governing-body evidence;
- historical currency changes;
- dual-currency or converted reporting.

### Current governed scope

Under Notebook 13's current findings:

- governed British values may be interpreted as GBP using the validated parser and rules;
- governed Irish euro-prefixed values may be interpreted as EUR using the validated parser and rules;
- other jurisdictions remain source-presented or unresolved until separately studied.

### No jurisdiction-only shortcut

Jurisdiction alone is not always enough to prove currency.

Sources may:

- convert foreign values into a preferred reporting currency;
- omit symbols;
- use local currency inconsistently;
- show historical currencies;
- mix original and converted values.

The accepted interpretation must therefore cite the actual evidence and rule used.

### Historical changes

Currency rules must be effective-dated where necessary.

A jurisdiction's present-day currency cannot be projected backwards without checking the race date and source convention.

## Semantic status of runner amounts

A runner monetary interpretation should support statuses such as:

- confirmed runner prize allocation;
- probable runner prize allocation;
- source-presented amount with unresolved currency;
- source-presented amount with unresolved scale;
- source-presented amount with unresolved meaning;
- externally confirmed allocation;
- corrected allocation;
- disputed allocation;
- not recorded;
- not applicable.

The exact vocabulary will be set during implementation governance, but the conceptual distinction is mandatory.

## Interpretation method and evidence

Every governed allocation must identify how it was obtained.

Possible methods include:

- direct parse of a currency-prefixed source value;
- direct parse under a jurisdiction-and-source rule;
- reconstruction from authoritative published results;
- reconciliation against an official payment schedule;
- manual review;
- later source-version correction;
- external governing-body confirmation.

The method must not be confused with confidence.

A deterministic parser can apply a rule consistently while the underlying semantic rule remains provisional.

## Calculated race totals

A calculated total is a derived analytical object, not an original source fact.

### Required distinctions

At least the following totals must remain distinguishable:

- sum of all governed populated runner allocations;
- sum of allocations for officially classified finishers;
- sum of allocations admitted under a particular governance release;
- sum excluding unresolved currencies;
- sum converted to a reporting currency;
- official race purse;
- advertised race value.

### Currency consistency

Amounts in different currencies must not be summed directly.

A race-level sum requires all included values to share a confirmed currency or to have been converted under a separately governed conversion method.

### Missing coverage

A sum of populated runner values remains a partial recorded total when any relevant runner amount is blank, unresolved or excluded.

It must not be labelled as complete merely because the arithmetic succeeded.

### Reproducibility

A calculated total must be reproducible from:

- the included allocation identifiers;
- the governance release;
- the calculation rule;
- the currency rule;
- any exclusion criteria.

## Official purse and advertised-value reconciliation

When both runner allocations and a race-level purse are available, their relationship should be tested rather than assumed.

Possible outcomes include:

- exact agreement;
- agreement after rounding;
- runner allocations represent only part of the purse;
- additional bonuses or premiums exist;
- one or more runner allocations are missing;
- the advertised value uses a different definition;
- the source converted one side but not the other;
- the sources disagree;
- the relationship remains unresolved.

A mismatch is evidence requiring explanation, not permission to overwrite one value with another.

## Amendments and versioning

Prize evidence may change after the original source version because of:

- official corrections;
- revised placings;
- disqualifications;
- appeals;
- redistribution of prize money;
- scheme eligibility decisions;
- source corrections;
- improved currency interpretation;
- improved parsing.

### Append-only principle

Later governed interpretations must supplement or supersede earlier ones through explicit versioning or status changes.

They must not erase:

- the original source value;
- the previous interpretation;
- the reason for amendment;
- the evidence available at the time.

### Result-state relationship

Where prize allocation depends on official classification, the monetary interpretation should identify the result state or official decision on which it relies.

A later result amendment may therefore generate a new prize allocation state without altering the original runner participation record.

## Foreign exchange conversion

Currency conversion is an analytical transformation, not part of the original monetary identity.

A converted value must remain linked to:

- the original amount;
- the original currency;
- the target currency;
- the exchange-rate source;
- the rate date or period;
- the rate type;
- the conversion method;
- rounding rules.

No conversion should replace the original governed amount.

This design does not yet choose between:

- race-date spot rates;
- monthly average rates;
- annual average rates;
- purchasing-power adjustments;
- source-provided conversions.

Each analytical use must state its method.

## Inflation and real-value analysis

Inflation adjustment is also a derived analytical layer.

A real-value amount must retain:

- nominal amount;
- currency;
- price index;
- base period;
- jurisdiction;
- transformation method.

It must not overwrite the nominal monetary fact.

Comparisons across long periods must not present nominal prize growth as real growth without disclosure.

## Analytical admission rules

### Runner-level prize studies

A runner-level prize study must state:

- which monetary statuses are admitted;
- which jurisdictions are included;
- which currencies are included;
- whether blanks are excluded or treated as missing;
- whether explicit zeros are admitted;
- whether official or source-recorded allocations are used;
- the governance release.

### Race-level prize studies

A race-level study must state whether its monetary measure is:

- recorded runner prize total;
- official purse;
- advertised value;
- winner's prize;
- another specifically defined amount.

The phrase `race prize money` is too ambiguous on its own.

### Cross-jurisdiction studies

Cross-jurisdiction comparisons must disclose:

- currency treatment;
- conversion method;
- unresolved-value exclusions;
- different prize-system definitions;
- coverage limitations.

### Paid-runner studies

The number of runner rows with populated prize values must be labelled as observed populated runner coverage unless official entitlement has been independently established.

### Series-level studies

Recurring race-series analysis must use edition-level monetary values and disclose how changes in:

- currency;
- purse definition;
- sponsorship;
- bonus structure;
- race conditions;
- venue;
- jurisdiction;
- inflation

were handled.

## Reconciliation and validation expectations

Future implementation should support validators for at least the following conditions.

### Raw preservation

- every governed interpretation retains a path to its raw or external evidence;
- the raw source value is unchanged;
- blank source values remain distinguishable from explicit zero.

### Currency and scale

- a confirmed amount has an explicit currency;
- a confirmed comparable amount has an explicit scale;
- unresolved currency or scale cannot silently enter governed sums;
- integer minor-unit conversion is exact under the accepted parser.

### Runner linkage

- a runner allocation links to exactly one runner record;
- the runner belongs to the stated race occurrence;
- incompatible duplicate accepted allocations for the same runner and prize state are prevented or flagged.

### Race totals

- every derived total identifies its included allocations;
- mixed currencies are rejected unless a governed conversion exists;
- incomplete coverage is flagged;
- calculated totals are not mislabelled as official purse values.

### Amendments

- superseded interpretations remain historically recoverable;
- amendment reasons and evidence are recorded;
- result-state-dependent allocations point to the relevant result state.

## Current-source decisions

For exact Source Version 1, the current accepted decisions are:

1. Preserve the exact raw `prize` value on every governed source record.
2. Treat the field primarily as runner-level recorded prize evidence.
3. Parse governed British values into exact GBP minor units under the validated rule.
4. Parse governed Irish euro-prefixed values into exact EUR minor units under the validated rule.
5. Retain blank values as unknown or unrecorded, not zero.
6. Label race-level sums as recorded runner prize totals.
7. Count populated runner rows as observed prize coverage, not automatically as the official number of paid places.
8. Preserve other jurisdictions as source-presented or unresolved until dedicated studies establish currency, scale and semantics.
9. Do not infer official race purse from runner-row sums.
10. Allow later official evidence to add, correct or reconcile monetary facts without overwriting the source.

## Deferred questions

The following remain deliberately deferred:

- exact official purse ontology by jurisdiction;
- bonus, premium and breeder-award modelling;
- participant shares paid to jockeys, trainers or owners;
- deductions and taxes;
- dead-heat prize splitting rules;
- retrospective redistribution after disqualification;
- foreign exchange methodology;
- inflation-adjusted reporting;
- official source integrations;
- physical database schema;
- API presentation rules.

Each requires either implementation design or separate empirical investigation.

## Non-goals

This model does not claim that:

- every populated source prize value is correct;
- every blank means no prize was paid;
- every source uses local currency;
- every source reports gross purse;
- summing runner values reconstructs the official purse;
- identical numeric values across currencies are comparable;
- a later corrected amount invalidates preservation of the original evidence.

## Final design rule

The database must preserve monetary evidence at the level at which it was supplied, govern interpretation separately, and require every derived total or comparison to identify exactly what monetary fact it represents.

A successful implementation will make it impossible to confuse:

- raw source text;
- governed runner allocation;
- observed payment coverage;
- calculated runner-prize total;
- advertised race value;
- official purse;
- converted or inflation-adjusted analytical value.

That separation is the foundation for trustworthy prize-money analysis.
