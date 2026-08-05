# Phase 3 Betting Prices and Market Observations Design

## Status

Accepted conceptual design for Phase 3 entity and key work.

This document defines the governed identity and evidence model for betting prices, odds, favourite status, and related market observations.

It deliberately does **not** define physical tables, SQL, indexes, migrations, or ingestion code.

Field-specific implementation must wait for a dedicated source-field audit of the available betting-price columns and their observed values.

---

## 1. Purpose

Betting prices are easy to misuse because a price can look like a simple runner attribute while actually representing a market observation made:

- for a particular runner;
- in a particular market;
- by or through a particular source;
- at a particular point in time;
- under a particular odds format;
- with particular liquidity, commission, deduction, and settlement assumptions.

A price is therefore not an intrinsic or permanent property of a horse, runner, race, jockey, trainer, owner, course, or recurring race series.

The design must preserve the original evidence while allowing governed interpretations and later market datasets to be added without silently collapsing unlike observations.

The central rule is:

> A betting price is a time-specific market observation, not an intrinsic attribute of the horse or race.

---

## 2. Core conceptual separation

The model must keep the following concepts separate.

### 2.1 Raw price assertion

The exact odds or price text supplied by a source record.

This is immutable supplier evidence.

Examples may include:

- fractional odds;
- decimal odds;
- American odds;
- abbreviations such as evens;
- favourite markers;
- joint-favourite or co-favourite markers;
- suspended, withdrawn, unavailable, or blank values;
- text whose precise meaning is unresolved.

The raw assertion must remain available even after successful parsing or later correction.

### 2.2 Governed market observation

A project interpretation that a particular price was observed for a particular betting selection in a defined market context.

A governed observation must be able to carry:

- the linked runner or other betting selection;
- market type;
- source or market operator;
- observation timestamp or temporal status;
- odds format;
- original text;
- parsed numeric representation where valid;
- side, where relevant;
- availability status;
- interpretation method;
- evidence status;
- confidence or review status;
- governance release.

### 2.3 Market snapshot

A coherent set of observations intended to describe one market at one defined point or event stage.

A snapshot may be required to derive:

- favourite status;
- joint- or co-favourite status;
- market rank;
- bookmaker overround;
- exchange book percentages;
- runner implied probabilities;
- price dispersion across operators.

A collection of prices from different times or incompatible market types must not be treated as one coherent snapshot.

### 2.4 Derived betting metric

A calculated value based on one or more governed market observations.

Examples include:

- implied probability;
- normalised probability;
- market rank;
- overround;
- exchange spread;
- price movement;
- favourite indicator;
- starting-price return measures;
- value or calibration metrics.

Derived metrics are analytical outputs, not original market evidence.

---

## 3. Relationship to existing Phase 3 entities

### 3.1 Runner record

The normal win-market selection is the runner record, not the provisional horse occurrence.

This distinction matters because:

- the same horse can have different prices in different races;
- the same horse can have multiple observations within one race;
- a runner may become a non-runner after prices were observed;
- market evidence belongs to the race participation context.

A governed market observation may therefore link to a runner record while retaining its own independent technical identity.

### 3.2 Source record

The raw price assertion remains linked to the immutable source record that supplied it.

A source record locator does not itself establish:

- the market type;
- the exact observation time;
- whether the value is forecast, opening, live, or starting price;
- whether the price came from a bookmaker, exchange, tissue, or aggregation;
- whether the value was subsequently corrected.

Those meanings require governed interpretation and evidence.

### 3.3 Source race occurrence

Every market observation must be scoped to the source race occurrence or a later reconciled real-world race identity.

Prices from different races must never be merged merely because:

- the horse name is the same;
- the course and date are the same;
- the race has the same title;
- the market price is identical.

### 3.4 Recurring race series

Betting observations attach to individual editions and runners, not permanently to the recurring race series.

A recurring race may have very different:

- fields;
- market strength;
- liquidity;
- favourite structure;
- operator coverage;
- betting rules;
- overround;
- price formation.

Series-level market analysis must aggregate edition-level observations under explicit admission rules.

### 3.5 Race result state

Betting observations and official outcomes are separate evidence layers.

A later result amendment may alter settlement or analysis, but must not overwrite the historical price observation.

Any return calculation must identify:

- the market observation used;
- the accepted result state used;
- settlement rules assumed;
- dead-heat treatment;
- deductions or commission considered.

---

## 4. Raw odds preservation

Every raw odds or price value must be retained exactly as supplied.

Preservation includes:

- original characters;
- punctuation;
- spacing;
- capitalisation;
- odds format;
- suffixes and favourite markers;
- operator-specific abbreviations;
- blanks and nulls;
- malformed or unparseable values.

Parsing must never replace the raw source value.

A successfully parsed price is a governed interpretation of the raw assertion, not a corrected version of the source text.

---

## 5. Market observation identity

A market observation requires its own project-wide technical identifier.

It must not use the numeric odds value as an identifier.

It must not assume that one runner has only one price.

A runner may legitimately have multiple observations because of:

- different operators;
- different times;
- different market types;
- opening and closing prices;
- bookmaker and exchange prices;
- back and lay sides;
- different each-way terms;
- corrected or superseding observations;
- multiple source deliveries.

The observation identity must therefore remain independent of the runner identity and source-record identity.

---

## 6. Market type must be explicit

Prices from unlike markets must remain distinct.

Potential market types include, but are not limited to:

- win;
- place;
- each-way;
- without-favourite;
- forecast;
- reverse forecast;
- exacta;
- trifecta;
- match bet;
- top finishing position;
- exchange win;
- exchange place;
- ante-post;
- day-of-race;
- starting price.

The initial implementation should support only market types established by evidence in the available source.

The conceptual model must not imply that all listed market types exist in Source Version 1.

A price without a resolved market type remains unresolved market evidence and must not be admitted to market-specific analysis.

---

## 7. Price stage and temporal meaning

The following price stages are conceptually distinct:

- tissue or forecast price;
- early or ante-post price;
- opening price;
- live pre-race quote;
- final bookmaker show;
- official starting price;
- exchange quote at a defined pre-off time;
- exchange starting price;
- in-play price;
- corrected historical price.

A shared numeric value does not make two observations equivalent.

For example, a forecast price of 5/1 and an official starting price of 5/1 are separate facts.

The model must not label a price as starting price unless the source semantics or external evidence support that interpretation.

---

## 8. Observation time

Observation time should be represented with the strongest supported precision.

Possible temporal states include:

- exact timestamp known;
- timestamp known to minute;
- date and market stage known;
- relative offset from off-time known;
- known only as starting price;
- known only as pre-race;
- observation time unresolved.

The system must distinguish:

- advertised race time;
- governed actual off-time;
- source capture time;
- publication time;
- market observation time.

These are not interchangeable.

A source record associated with a race does not prove that its price was captured at the advertised or actual off-time.

If exact observation time is unavailable, the uncertainty must remain explicit.

---

## 9. Source and operator identity

The source of a price must remain explicit.

Conceptually relevant distinctions include:

- source provider;
- source product;
- exact source version;
- bookmaker or operator;
- betting exchange;
- odds compiler or tissue author;
- aggregation service;
- official industry return;
- project-derived consensus.

The supplier of the dataset may differ from the operator whose market price is represented.

A source field may contain an official returned starting price without identifying an individual bookmaker.

The design must allow these distinctions without forcing an operator identity where none is evidenced.

---

## 10. Odds format and governed numeric representation

The raw format must be retained.

A governed observation may additionally store a mathematically equivalent representation where parsing is reliable.

Potential governed representations include:

- fractional numerator and denominator;
- decimal odds;
- net profit multiple;
- gross return multiple;
- unadjusted implied probability.

Conversions must be deterministic and documented.

For positive fractional odds `a/b`:

- decimal odds are `(a / b) + 1`;
- unadjusted implied probability is `b / (a + b)`.

For decimal odds `d` greater than 1:

- unadjusted implied probability is `1 / d`.

The project must not silently treat:

- evens;
- odds-on fractions;
- malformed fractions;
- non-numeric status text;
- zero;
- negative values;
- unavailable quotes

as ordinary valid prices without explicit parsing rules.

Numeric conversion does not remove bookmaker margin, exchange commission, or market bias.

---

## 11. Bookmaker and exchange prices

Bookmaker prices and exchange prices must remain separate.

### 11.1 Bookmaker observations

A bookmaker observation may require context such as:

- operator;
- fixed-odds quote;
- each-way terms;
- rule deductions;
- best-odds-guaranteed eligibility;
- availability or suspension status;
- observation time.

### 11.2 Exchange observations

An exchange observation may require:

- exchange operator;
- back or lay side;
- quoted price;
- available stake or liquidity;
- matched or unmatched status;
- market depth level;
- commission assumptions;
- observation time.

A back price and lay price are not interchangeable.

A top-of-book quote without available volume is not equivalent to an executable price for any desired stake.

An exchange starting price is not the same concept as a bookmaker starting price.

The initial source may not provide these details, but the model must not prevent later evidence from recording them correctly.

---

## 12. Market availability and missingness

The system must distinguish at least the following states:

- valid quoted price;
- price not supplied by the source;
- market not offered;
- selection not quoted;
- market suspended;
- runner withdrawn;
- price temporarily unavailable;
- source value malformed;
- market type unresolved;
- observation time unresolved;
- true source null;
- blank source text.

A missing or blank price must not be interpreted as:

- zero odds;
- zero probability;
- an infinite price;
- a non-runner;
- an unavailable market;
- an even-money price.

Those are different states requiring separate evidence.

---

## 13. Non-runners and withdrawn selections

A runner may have valid historical price observations and later become a non-runner.

The price observations remain historical evidence.

The runner outcome layer determines whether the selection participated.

Market analysis must specify how non-runners are treated, including whether it uses:

- prices before withdrawal;
- a final market after withdrawals;
- rule-based deductions;
- reconstructed overround excluding non-runners;
- official starting-price fields that already reflect the final field.

A withdrawal must not cause earlier price evidence to be deleted.

---

## 14. Favourite status

Favourite status is a derived market property.

It is not a permanent source-independent attribute of a runner or horse.

A favourite derivation must identify:

- the market type;
- the observation stage or timestamp;
- the operator or source universe;
- the eligible selections;
- the comparison price representation;
- treatment of non-runners;
- treatment of missing prices;
- tie rules.

The model must represent:

- sole favourite;
- joint favourite;
- co-favourite where the source terminology uses it;
- equal shortest prices across more than two runners;
- unresolved favourite status;
- source-supplied favourite marker that conflicts with parsed prices.

A source suffix such as favourite or joint favourite is raw evidence and may be governed independently from a favourite status derived from a complete snapshot.

The two should not be silently forced to agree.

---

## 15. Market snapshots and coherence

A coherent market snapshot should normally require observations that share compatible:

- race identity;
- market type;
- source or defined source set;
- observation time or permitted time window;
- odds basis;
- availability rules;
- runner eligibility state.

The project must not calculate an apparent market book by mixing, for example:

- one runner's opening price;
- another runner's starting price;
- a third runner's exchange price;
- a fourth runner's forecast price.

Where a historical source supplies only one price per runner without reliable timestamps, the resulting set may be treated as a source-defined snapshot only after a field study confirms that interpretation.

Until then, it remains a set of raw price assertions attached to source records.

---

## 16. Implied probability and overround

Unadjusted implied probability is a deterministic transformation of valid odds.

It is not automatically a calibrated estimate of true winning probability.

For bookmaker win markets, the sum of unadjusted implied probabilities may exceed 100% because of overround and market structure.

Any normalisation method must be named and versioned.

Possible analytical methods include:

- simple proportional normalisation;
- additive adjustment;
- power method;
- odds-ratio method;
- favourite-longshot-bias models;
- no normalisation.

The Phase 3 identity model does not select a preferred probability-removal method.

A study must declare:

- the input snapshot;
- inclusion and exclusion rules;
- the overround calculation;
- the margin-removal method, if any;
- whether exchange commission was included;
- how non-runners and missing prices were treated.

---

## 17. Exchange commission and executable returns

Exchange quoted odds do not by themselves determine net customer return.

Net return may depend on:

- commission rate;
- commission basis;
- market-level net winnings;
- discounts or premium charges;
- matched stake;
- liquidity;
- partial matching;
- settlement rules.

A study that compares bookmaker and exchange prices must not compare gross bookmaker decimal odds directly with exchange odds while ignoring commission unless it explicitly states that it is comparing unadjusted quoted prices.

---

## 18. Each-way terms and place components

An each-way bet is not fully described by a win price alone.

A complete each-way observation may require:

- win odds;
- place fraction;
- number of places;
- field-size rules;
- handicap or race-type rules;
- dead-heat settlement;
- deductions;
- operator-specific enhancements.

The initial source may not contain these terms.

The absence of each-way terms means an exact each-way return must not be reconstructed merely from a win price.

---

## 19. Starting price

Starting price must be treated as a governed market stage, not assumed from any generic odds field.

Where a source value is confirmed as an official starting price, the observation should retain:

- the raw returned text;
- the governing jurisdiction;
- the return system or authority where known;
- odds format;
- favourite markers;
- result linkage;
- any correction evidence;
- governance release.

Different jurisdictions and periods may use different starting-price determination processes.

Cross-jurisdiction comparisons must therefore preserve the applicable regime and date context.

---

## 20. Price movement

Price movement requires at least two temporally ordered, compatible observations.

The project must not infer shortening or drifting from:

- two prices from different operators without a defined comparison rule;
- forecast price versus starting price without naming that comparison;
- bookmaker versus exchange prices;
- observations whose times are unresolved;
- different market types.

A governed movement measure should state:

- start observation;
- end observation;
- time interval or market stages;
- source universe;
- numeric scale;
- direction convention;
- handling of withdrawals and missing observations.

---

## 21. Corrections and supersession

Later evidence may establish that a source price was:

- malformed;
- misformatted;
- attached to the wrong runner;
- reported under the wrong market type;
- not actually a starting price;
- subsequently corrected by an official source;
- invalidated by a source-version defect.

The original source assertion must remain immutable.

A correction should be represented through governed evidence with:

- correction type;
- prior interpretation;
- corrected interpretation;
- evidence reference;
- decision status;
- effective governance release;
- reviewer or method where applicable.

The design should support append-only interpretive history rather than silent replacement.

---

## 22. Versioning and governance releases

Market interpretations must be reproducible under a named governance release.

A release may define:

- accepted parsers;
- odds-format rules;
- market-type mappings;
- timestamp interpretation rules;
- favourite derivation rules;
- availability classifications;
- source exclusions;
- known defects;
- reconciliation decisions.

A later release may improve interpretation without changing the immutable raw source evidence.

Analytical outputs must identify the governance release used.

---

## 23. Reconciliation across source versions and providers

Cross-version or cross-provider matching must be explicit.

Two observations should not be treated as duplicates merely because they share:

- runner label;
- race label;
- odds value;
- source date;
- apparent starting-price marker.

Potential reconciliation evidence may include:

- reconciled real-world race identity;
- governed runner identity within the race;
- market type;
- operator or return authority;
- observation timestamp or stage;
- exact raw price;
- source lineage;
- correction notices.

The outcome of reconciliation may be:

- same market observation represented twice;
- distinct observations at the same price;
- correction or supersession;
- conflicting evidence;
- unresolved relationship.

No cross-source equivalence should be assumed at ingestion.

---

## 24. Validation requirements

Future implementation should support validation of at least the following invariants.

### 24.1 Evidence preservation

- Every governed price interpretation links back to immutable source evidence or documented external evidence.
- Raw price text remains unchanged.
- A failed parse does not destroy or replace the raw value.

### 24.2 Observation integrity

- Every observation links to one defined betting selection.
- Every observation has a market type or an explicit unresolved status.
- Every valid numeric odds representation satisfies its format constraints.
- Invalid or unavailable states are not stored as valid numeric odds.

### 24.3 Temporal integrity

- Exact timestamps include timezone or an explicit unresolved timezone status.
- Relative observations identify the time reference used.
- Starting-price status is not inferred solely from proximity to advertised off-time.

### 24.4 Snapshot integrity

- Snapshot members share compatible race and market context.
- A snapshot does not mix back and lay prices as one price series.
- A snapshot does not silently mix bookmaker, exchange, forecast, and starting-price observations.
- Favourite derivation rules are deterministic for the accepted snapshot.

### 24.5 Derived metric integrity

- Implied probabilities derive from valid governed odds.
- Overround calculations disclose included selections.
- Normalised probabilities identify their adjustment method.
- Return calculations identify settlement and commission assumptions.

### 24.6 Version integrity

- Interpretive changes create a new governed state or release.
- Prior accepted interpretations remain traceable.
- Source-version lineage is retained.

---

## 25. Admission rules for analytical studies

Every betting-price study must state its admission rules.

At minimum, it should define:

- source version or versions;
- jurisdiction and date range;
- race universe;
- market type;
- price stage or observation-time rule;
- operator or source universe;
- odds parser version;
- handling of missing and malformed values;
- handling of non-runners;
- handling of joint favourites;
- handling of dead-heats;
- overround treatment;
- exchange commission treatment;
- result-state version;
- governance release.

A study must not present an odds field as starting price, opening price, or live price unless that semantic interpretation has been established.

---

## 26. Required disclosures for common analyses

### 26.1 Favourite performance

Disclose:

- how favourite status was determined;
- market snapshot used;
- whether source favourite markers or derived shortest prices were used;
- treatment of joint favourites;
- treatment of missing prices and non-runners;
- accepted result state.

### 26.2 Starting-price returns

Disclose:

- proof that the field represents starting price;
- odds format conversion;
- stake convention;
- dead-heat settlement;
- deductions or commission assumptions;
- treatment of void races and non-runners.

### 26.3 Market efficiency or calibration

Disclose:

- probability transformation;
- overround-removal method;
- grouping or binning method;
- sample weighting;
- treatment of ties and missing observations;
- confidence intervals or uncertainty assessment.

### 26.4 Price movement

Disclose:

- start and end market stages;
- observation timing;
- source/operator scope;
- movement scale;
- treatment of withdrawals;
- whether prices were executable.

### 26.5 Bookmaker versus exchange comparison

Disclose:

- bookmaker source;
- exchange side;
- liquidity requirement;
- commission assumption;
- timestamps;
- whether comparisons are quoted or executable returns.

---

## 27. Known limitations before implementation

The current Phase 3 design does not yet establish:

- which Source Version 1 fields contain odds;
- the precise semantics of those fields;
- whether a field is forecast, opening, live, or starting price;
- whether favourite markers are embedded in raw text;
- whether operator identity is available;
- whether prices share a coherent capture time;
- whether exchange evidence exists;
- whether price corrections are present;
- whether odds formats vary by jurisdiction;
- whether non-runner treatment is encoded consistently.

These are field-governance questions for a dedicated source audit and notebook.

The model intentionally leaves them unresolved rather than inventing certainty.

---

## 28. Deferred extensions

The following are valid later extensions but are not required for the first implementation:

- high-frequency exchange order-book observations;
- matched-volume histories;
- operator-specific each-way terms;
- best-odds-guaranteed modelling;
- rule deductions;
- ante-post voiding rules;
- customer-specific commission rates;
- promotional boosts;
- cash-out prices;
- in-play market histories;
- multi-market selections;
- pool-betting dividends;
- tote takeout and breakage;
- cross-market arbitrage observations;
- model-generated fair prices;
- proprietary tissue forecasts.

These should be added as separate evidence or derived layers, not forced into a single generic odds column.

---

## 29. Implementation implications for later schema work

Without prescribing SQL, the eventual schema will need to support independent identities or governed records for:

- raw price assertion;
- betting selection;
- market definition;
- market operator or source context;
- market observation;
- market snapshot;
- favourite derivation;
- price correction or supersession;
- derived market metric;
- governance release.

The schema must support multiple observations per runner and multiple runners per snapshot.

It must also support unresolved semantics without fabricating false entities or numeric values.

---

## 30. Decision summary

The accepted Phase 3 betting-price design is:

1. Preserve every raw odds value exactly as supplied.
2. Treat prices as time-specific market observations.
3. Give market observations independent technical identity.
4. Link ordinary win-market selections to runner records, not permanent horse identity.
5. Keep forecast, opening, live, starting, bookmaker, and exchange prices distinct.
6. Keep exchange back and lay observations distinct.
7. Retain odds format and original text alongside governed numeric conversions.
8. Distinguish missing, unavailable, malformed, withdrawn, and unresolved states.
9. Derive favourite status only from a defined market snapshot or preserve it explicitly as a source assertion.
10. Represent joint and co-favourites without forcing a unique favourite.
11. Do not assume source capture time equals advertised or actual off-time.
12. Preserve historical prices for runners who later become non-runners.
13. Treat implied probability, overround, movement, and returns as derived metrics.
14. Require explicit commission, settlement, non-runner, and dead-heat assumptions.
15. Preserve corrections and interpretive changes append-only through governance releases.
16. Defer field-specific implementation until a source audit establishes actual odds-field semantics.

---

## 31. Boundary with the next design topics

This document resolves the conceptual identity and governance boundary for betting prices and market observations.

It does not yet resolve:

- ratings and performance measures;
- carried weight, allowances, and claims;
- equipment and medication assertions;
- sectional timing and race-position observations;
- weather observations and going reconciliation;
- physical table design.

Those remain separate bounded design questions.
