# Phase 3 Betting Price Interpretation Regimes Addendum

## Status

Accepted addendum to:

- `docs/PHASE_3_BETTING_PRICES_AND_MARKET_OBSERVATIONS_DESIGN.md`

This document tightens the treatment of starting prices, Tote and pari-mutuel returns, jurisdiction-specific market rules, and source-supplied conversions.

It deliberately does **not** define physical tables, SQL, indexes, migrations, ingestion code, or a complete worldwide catalogue of betting rules.

The purpose is to preserve a small safe core now and permit evidence-led extension when later jurisdiction or field studies justify it.

---

## 1. Reason for the addendum

A source-presented betting value can look like an ordinary price while representing materially different evidence.

For example, a displayed number may originate from:

- a British fixed-odds starting-price procedure;
- an Irish or other jurisdiction-specific starting-price procedure;
- a Tote or pari-mutuel win dividend;
- a place or show dividend;
- a payoff quoted for a particular unit stake;
- a converted foreign return;
- a source-normalised decimal or fractional-looking representation;
- a value whose original market mechanism is not yet known.

The same displayed number can therefore imply different stake conventions, return conventions, market mechanisms, deductions, and probability interpretations.

The parent design correctly treats prices as market observations, but it must be read with this stronger rule:

> A betting value is interpretable only within its supported jurisdiction, effective period, market mechanism, bet type, and source-transformation history.

A numeric value alone does not establish those semantics.

---

## 2. Core design principle

The project must design for **safe extension**, not attempt to encode every historical betting rule in every racing jurisdiction before a study needs it.

The initial governed database should store only what is evidenced.

It must:

- preserve original source evidence;
- represent known semantics where supported;
- preserve unresolved meaning explicitly;
- prevent incompatible values from entering the same analysis silently;
- allow later evidence to enrich interpretation without changing the original observation identity.

The governing principle is:

> Store only what is currently evidenced, preserve unresolved meaning explicitly, and extend the governed interpretation when a focused investigation justifies it.

---

## 3. Minimum stable core

The stable core does not need a complete model of every possible bookmaker, exchange, Tote, dividend, tax, takeout, or settlement rule.

It should be capable of preserving:

- the immutable raw betting value;
- its immutable source record and exact source version;
- the relevant source race occurrence;
- the runner or other betting-selection context where supported;
- the source-presented format;
- the source-presented market label or marker, if any;
- jurisdiction where supported;
- observation or finality status where supported;
- an optional governed interpretation regime;
- explicit unresolved-semantics status;
- evidence, method, confidence, and governance release.

The core must not require every observation to have a fully resolved regime.

An unresolved observation remains valid source evidence.

It is simply not eligible for analyses requiring semantics that have not been established.

---

## 4. Governed betting-market interpretation regime

A betting-market interpretation regime is an optional governed context used to explain how a class of betting values should be interpreted.

It is not itself a market observation and must not replace the raw source value.

A regime may eventually describe, where evidenced and analytically necessary:

- governing jurisdiction;
- effective start and end dates;
- market mechanism;
- bet type;
- price or dividend stage;
- pool or operator context;
- betting-interest basis;
- stake unit;
- whether the returned figure includes the original stake;
- odds, payoff, or dividend convention;
- deductions, takeout, commission, tax, or breakage treatment;
- rounding rules;
- finality status;
- source conversion or normalisation method;
- applicable official rule source;
- evidence status and confidence;
- governance release.

These attributes are available extension points, not mandatory populated fields for all current observations.

The regime should contain only attributes established by evidence.

Unknown attributes remain unknown.

---

## 5. Regime identity and effective dating

A regime requires independent governed identity.

It must not be identified solely by:

- jurisdiction name;
- a generic label such as `SP`;
- odds format;
- source field name;
- displayed numeric range;
- race date without supporting rules evidence.

A jurisdiction can have multiple regimes over time.

A single race date may also involve multiple market mechanisms or bet types.

A regime assignment therefore requires evidence appropriate to the source and analytical claim.

Effective dates must be explicit where rule changes are known.

A regime boundary does not imply that every mathematical feature changed at that date. It records that the procedure, sampled market, rule set, or interpretation context changed sufficiently to require separate governance.

---

## 6. British starting-price regimes within Source Version 1

The current source covers British racing across a period in which the official starting-price basis changed materially.

At minimum, later field governance must distinguish the following periods.

### 6.1 Traditional on-course basis before 1 June 2020

Before the closed-doors resumption of British racing, official SPs were traditionally returned from the on-course betting market under the then-applicable SPRC procedure.

These values must not automatically be treated as methodologically identical to later off-course-derived SPs.

### 6.2 Temporary off-course procedure from 1 June 2020

When British racing resumed behind closed doors on 1 June 2020, on-course bookmakers were unavailable.

The SPRC introduced temporary arrangements based on betting shows from a sample of major off-course bookmakers operating in Great Britain.

The broad calculation principles remained related to the prior procedure, but the sampled market changed materially.

This is therefore a required analytical regime boundary.

### 6.3 Policy decision in March 2021

The SPRC subsequently decided in March 2021 that future SPs would be determined mainly from off-course prices because those prices represented the overwhelming majority of the British racing betting market.

This decision establishes the intended long-term market basis.

It does not necessarily create a new mathematical regime for every study by itself.

A field investigation should determine whether the effective analytical boundary remains 1 June 2020 until the permanent rules began, or whether any intervening procedural changes require additional subdivision.

### 6.4 Permanent revised procedure from 1 May 2022

Updated permanent arrangements took effect on 1 May 2022.

The revised framework formalised matters including qualifying price sources, common ownership, independent feeds, market-share criteria, and treatment of differing each-way terms in sample selection.

This is a separate governed regime from the temporary closed-doors procedure.

### 6.5 Changes approved in July 2026

The current SPRC rules state that further changes were approved in July 2026, including a nine-bookmaker qualified universe, a usual minimum sample of six, and a 1.5% market-share qualification criterion.

Source Version 1 ends on 27 May 2026.

Those July 2026 changes therefore fall outside the current source period and must not be retroactively assigned to Source Version 1 races.

They should be considered when a later source version extends beyond the rule change.

### 6.6 British analytical consequence

British SP studies spanning 2015 to 2026 must not treat the field as a single homogeneous measurement without testing and disclosing regime effects.

This applies particularly to studies of:

- overround;
- favourite-longshot bias;
- price calibration;
- favourite performance;
- SP returns;
- market efficiency;
- temporal trends;
- pre- and post-pandemic comparisons.

A detected change around a regime boundary may reflect a change in SP construction rather than a change in horse performance, bettor behaviour, or race competitiveness.

---

## 7. Official evidence for British regime boundaries

The British regime account above is based on the Starting Price Regulatory Commission's published material, including:

- SPRC homepage and archived announcement describing temporary off-course arrangements from 1 June 2020;
- SPRC April 2022 statement describing the March 2021 decision and permanent arrangements effective from 1 May 2022;
- SPRC rules and regulations reflecting changes approved in July 2026;
- SPRC background material explaining the shift from the traditional on-course basis to a mainly off-course basis.

Relevant official pages:

- <https://www.thesprc.org/>
- <https://www.thesprc.org/about-us/>
- <https://www.thesprc.org/rules-regulations/>

A later implementation or field-governance notebook should capture dated copies or hashes of the exact rule evidence used, because live webpages can change.

---

## 8. Foreign and jurisdiction-specific values

Values from non-British races must not be assumed to represent British-style fixed-odds SP merely because the source displays them in a familiar format.

Potential underlying mechanisms include:

- fixed-odds starting prices;
- official industry returns under a different sampling procedure;
- Tote or pari-mutuel win dividends;
- place or show dividends;
- pool payoffs quoted per local unit stake;
- converted returns supplied by an intermediary;
- locally calculated fallback pools;
- values whose original mechanism is unresolved.

Until a jurisdiction-specific investigation confirms the semantics, such observations should be governed as:

> Source-presented market values with unresolved betting semantics.

They may remain available for inventory, completeness, parsing, and source-quality analysis.

They must not automatically enter analyses that require fixed-odds SP semantics.

---

## 9. Odds, dividends, and payoffs are separate concepts

The design must not collapse the following into one undifferentiated numeric price:

- quoted fixed odds;
- official starting price;
- pari-mutuel or Tote dividend;
- monetary payoff;
- profit multiple;
- gross return multiple;
- source-converted odds-equivalent value.

A reported value may represent:

- profit excluding returned stake;
- total return including stake;
- dividend per unit stake;
- payoff per a jurisdiction-specific stake unit;
- an odds ratio;
- a source-generated normalised display.

A value cannot be transformed safely into implied probability or return without knowing which convention applies.

Where the convention is unresolved, the project must preserve the raw value and withhold the derived interpretation.

---

## 10. Source transformations and converted foreign values

The source may have transformed a foreign market return before presenting it.

Possible transformations include:

- converting a dividend to fractional-looking odds;
- converting a payoff to decimal odds;
- changing the stake unit;
- removing or adding returned stake;
- changing currency presentation;
- rounding or truncating the result;
- mapping status text into a numeric field.

The displayed value is then evidence of what the source presented, not direct evidence of the original market quote or dividend.

A governed interpretation should distinguish, where supported:

1. the exact raw source-presented value;
2. the source-presented format;
3. the inferred or documented original market mechanism;
4. the original stake or return convention;
5. the source conversion method;
6. the project conversion method, if a further governed transformation is made.

Source conversion and project conversion must never be conflated.

If the source conversion method is unknown, it remains unresolved.

---

## 11. Race jurisdiction and betting-pool jurisdiction

The location of the race does not always identify the pool or market that produced a return.

Later investigations may need to distinguish:

- race jurisdiction;
- governing racing authority;
- betting operator or pool operator;
- pool jurisdiction;
- commingled or separate-pool status;
- fallback-pool status;
- source distributor.

These details are not mandatory for the current stable core.

They become necessary only when the available evidence or analytical question depends on them.

A race-jurisdiction label alone must not be treated as proof of the pool mechanism.

---

## 12. Bet type and betting-interest identity

Price interpretation also depends on what was bet upon.

Later investigations may need to distinguish:

- win;
- place;
- show;
- each-way;
- exotic pool;
- coupled entry;
- field entry;
- individual runner;
- other jurisdiction-specific betting interest.

Horse identity, runner identity, and betting-interest identity are related but separate.

Where multiple runners form one betting interest, one market value must not be counted as multiple independent prices merely because it appears against multiple source rows.

The initial schema does not need to solve every coupled-entry system now.

It must simply avoid making runner identity the only possible betting-selection model.

---

## 13. Deductions, takeout, commission, rounding, and breakage

A Tote dividend or exchange return can depend on rules not represented by the displayed value alone.

Later regime extensions may need to record:

- pool takeout;
- statutory deductions or taxes;
- jackpot or reserve deductions;
- exchange commission;
- rebate treatment;
- rounding;
- truncation;
- breakage;
- minimum-dividend rules;
- dead-heat settlement;
- refund rules;
- no-winning-ticket treatment.

These are not required in the initial general-purpose schema unless the source or study provides and needs them.

Their absence must prevent unsupported net-return or probability claims, not prevent preservation of the raw observation.

---

## 14. Observation stage and finality

A displayed Tote or pool value may be:

- an indicative pre-race quote;
- a live pool estimate;
- a minimum displayed range value;
- a final declared dividend;
- a subsequently corrected dividend;
- a source conversion of one of those states.

Observation stage and finality must remain explicit where known.

A pre-race pool estimate is not interchangeable with a final dividend.

A result-page value is not automatically proven to be final merely because it appears after the race.

Where finality cannot be established, the uncertainty remains explicit.

---

## 15. Admission rules for fixed-odds SP analysis

A value may enter a fixed-odds starting-price analysis only when the study has established, at an appropriate confidence level:

- that the field represents starting price rather than forecast, opening, live, Tote, or converted payoff data;
- the relevant jurisdiction;
- the applicable methodology regime or a justified reason why regime subdivision is unnecessary;
- the odds and stake-return convention;
- the eligible runner or betting-interest mapping;
- the treatment of non-runners and amendments;
- the result state used for settlement or outcome comparison.

A source-presented foreign value with unresolved market semantics fails these admission requirements.

It should be excluded from the fixed-odds SP analysis while remaining preserved in the database.

---

## 16. Admission rules for cross-jurisdiction analysis

Cross-jurisdiction market comparison requires more than converting all values to decimal odds.

A study must establish whether it is comparing:

- quoted fixed odds;
- official starting prices;
- final Tote dividends;
- gross payoff multiples;
- source-normalised values;
- or another defined measurement.

It must disclose:

- jurisdiction and effective regime;
- market mechanism;
- bet type;
- stake-return convention;
- treatment of deductions and commission;
- conversion history;
- unresolved exclusions;
- comparability limitations.

Mathematical conversion to a common numeric scale does not create semantic equivalence.

---

## 17. Deferred jurisdiction investigations

Jurisdiction-specific interpretation should proceed through focused studies rather than speculative schema design.

A later study may investigate one jurisdiction or market family at a time and establish:

- source-field value families;
- official terminology;
- applicable rule periods;
- original market mechanism;
- bet types represented;
- stake and return conventions;
- pool or operator context;
- conversion rules used by the source;
- known exceptions;
- validation examples;
- admission rules for analysis.

The resulting governed regime can then be added without changing the identity of existing source records or raw market observations.

This is the intended extension path.

---

## 18. Implementation boundary

The eventual first implementation need not include a large number of specialist fields or tables merely because this addendum identifies possible future requirements.

It needs only to avoid blocking later extension.

A suitable first implementation should be capable of:

- preserving raw source values;
- attaching a basic governed interpretation where known;
- linking an optional interpretation regime;
- storing unresolved status;
- retaining provenance and governance version;
- adding richer regime details later without rewriting original observations.

Specialised structures for commingling, pool calculations, takeout histories, betting interests, or settlement rules should be introduced only when a real source and bounded investigation require them.

---

## 19. Validation requirements

Future implementation should support at least the following checks.

### 19.1 Raw evidence

- Every interpreted value links to immutable source or external evidence.
- Raw source text remains unchanged.
- A project conversion does not replace the source-presented value.

### 19.2 Regime assignment

- Every regime assignment identifies its evidence and governance release.
- Effective dates are valid and non-contradictory within the relevant scope.
- July 2026 British rules are not assigned to races before their effective period.
- Source Version 1 British races after 27 May 2026 cannot exist under the validated current source cutoff.

### 19.3 Semantic safety

- Unresolved Tote or foreign values are not classified automatically as fixed-odds SP.
- Odds, dividends, and payoffs are not merged solely because numeric conversions match.
- Race jurisdiction is not substituted automatically for pool jurisdiction.
- Runner identity is not assumed to equal betting-interest identity in every jurisdiction.

### 19.4 Analytical admission

- Fixed-odds SP studies include only observations meeting their stated semantic requirements.
- Cross-period British studies disclose methodology-regime treatment.
- Cross-jurisdiction studies disclose market-mechanism and return-convention differences.
- Excluded unresolved observations remain countable for coverage reporting.

---

## 20. Required disclosure in later reports

A betting-price report should disclose, where relevant:

- which source field was used;
- source version and cutoff;
- jurisdiction coverage;
- regime mapping;
- unresolved counts;
- values excluded because semantics were not established;
- whether observations are fixed odds, SPs, dividends, payoffs, or source conversions;
- stake and return convention;
- treatment of deductions, commission, rounding, and dead-heats;
- any source or project conversion;
- governance release;
- sensitivity to regime boundaries.

A report must not hide unresolved foreign observations by silently dropping them without a coverage count.

---

## 21. Decision summary

The accepted addendum is:

1. A betting value is interpretable only within its supported jurisdiction, period, market mechanism, bet type, and source-transformation history.
2. The stable database core should remain small and evidence-led.
3. Raw source-presented betting values remain immutable even when their semantics are unresolved.
4. An optional governed betting-market interpretation regime provides effective-dated context.
5. British SPs within Source Version 1 require at least an on-course pre-1-June-2020 regime, a temporary off-course regime from 1 June 2020, and a permanent revised regime from 1 May 2022.
6. The March 2021 decision records the long-term policy shift but requires a field study before being treated as an additional mathematical breakpoint.
7. British changes approved in July 2026 fall outside Source Version 1's 27 May 2026 cutoff.
8. Foreign values must not be presumed to be British-style fixed-odds SP.
9. Tote dividends, payoffs, and source-converted values remain distinct from quoted odds.
10. Unresolved foreign observations are preserved but excluded from incompatible analyses.
11. Race jurisdiction, pool jurisdiction, operator, and commingling details are later extensions when evidence requires them.
12. Horse, runner, and betting-interest identity remain conceptually separate.
13. Takeout, commission, tax, breakage, rounding, and settlement rules are deferred extensions rather than mandatory speculative fields.
14. Mathematical conversion does not establish semantic comparability.
15. Jurisdiction-level investigations should extend governed interpretation without rewriting original observations.

---

## 22. Relationship to the parent design

This addendum strengthens and qualifies the parent design's sections on:

- odds format and numeric representation;
- market and operator identity;
- starting price;
- implied probability and overround;
- analytical admission;
- known limitations;
- deferred Tote and pool-betting extensions.

Where the parent document could be read as permitting a generic starting-price interpretation from familiar-looking values, this addendum takes precedence.

The next physical-schema phase should use both documents together.