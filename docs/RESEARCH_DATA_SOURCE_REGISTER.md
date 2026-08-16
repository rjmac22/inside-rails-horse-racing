# Inside Rails Research Data Source Register

## Purpose

This register records data and evidence that Inside Rails can already use, may already possess locally, or can reasonably obtain or look up if a study makes it useful.

It is **not** a promise to integrate every source into the database. Its purpose is to prevent a study from being artificially limited by whatever happens to be in the current accepted database.

This register must be read together with:

`docs/PRIMARY_SOURCE_FIRST_RESEARCH_RULE.md`

The standing source-authority rule is:

> For a question about what a racing jurisdiction is, means, permits, requires, schedules, classifies or officially records, establish the concept from the best available primary official source before using Inside Rails or another third-party dataset to define it.

The standing source-discovery rule remains:

> If a study raises a question that could be materially answered, checked or strengthened with information outside the current accepted database, actively identify and verify the best available source before concluding that the information is unavailable.

The assistant should do source discovery and verification as part of the research workflow rather than relying on the user to remember that another dataset, API or website exists.

A newly discovered source can be used in three different ways:

1. **bounded lookup / manual verification** — use a small amount of external evidence to check a specific fact;
2. **study-specific external dataset/API use** — obtain or call data needed for one research question without automatically changing the core database;
3. **governed database integration** — escalate only when the source or transformation is correctness-critical or clearly reusable across studies.

Raw third-party data must remain separate from governed analytical interpretations. Access to a source does not by itself establish that its fields are reliable, equivalent to Inside Rails concepts, or licensed for bulk republication.

---

## Availability status vocabulary

### `accepted_database`

Already integrated into the current accepted Inside Rails database and normally available through governed study-facing interfaces.

### `local_unintegrated`

Known from the supplied source collection or repository history but not part of the current accepted analytical database. Exact local path, file inventory, coverage and quality must be confirmed before use.

### `public_external`

Publicly accessible external data or reference material that can be researched or obtained when required. Availability, terms and format must be rechecked at the time of use.

### `account_or_paid`

Available through an account, subscription, purchase, licensed feed or other access condition. Cost and terms must be assessed before acquisition.

### `manual_reference`

Useful for bounded verification or contextual checking, but not assumed to be suitable or permitted for bulk automated ingestion.

### `verify_when_needed`

A potentially useful category or provider for which exact current access, historical depth, fields or terms must be established before relying on it.

---

## 1. Current accepted Inside Rails analytical data

Status: `accepted_database`

Canonical release:

`data/processed/database/releases/inside_rails_v4.sqlite3`

Database v4 was accepted and promoted on **12 August 2026**.

Preferred study-facing interfaces include:

- `view_reconciled_race_occurrences`;
- `view_gb_reconciled_race_occurrences_with_racecourse` for GB racecourse-aware race work;
- `view_reconciled_source_runner_participations`;
- `view_reconciled_runner_records`.

Current governed coverage includes, among other things:

- race and runner structural identity;
- course/jurisdiction and GB racecourse identity context;
- race type/classification and surface governance;
- source-literal distance interpretation plus bounded official-distance enrichments;
- carried weight;
- starting-price arithmetic and favourite status;
- advertised/scheduled time governance and integrated actual-off enrichments;
- prize semantics and integrated external prize-schedule enrichments;
- runner counts, results and beaten-distance governance;
- age/sex and other runner characteristics;
- ratings semantics;
- comments;
- bounded horse/pedigree and participant-identity governance;
- bounded external corrections, invalidations and supplementations.

Important boundary:

> The accepted Inside Rails database is an analytical representation, not the authority that defines what British racing concepts mean.

Always check `docs/STUDY_DATABASE_REFERENCE.md` for the current accepted release and exact field/view contract before using these concepts.

---

## 2. Known supplied products not automatically integrated

Status: `local_unintegrated`

Notebook 00 records that the original downloaded source collection contained or was expected to contain several products beyond Source Version 1:

- historical archives covering approximately 1988–2004;
- historical archives covering approximately 2005–2014;
- recent form HTML files;
- daily racecards;
- BHA ratings data;
- Betfair data.

These are **candidate resources, not accepted database inputs**.

Before a study uses any of them:

1. inventory the actual files currently present locally;
2. establish exact date/jurisdiction coverage;
3. establish grain and identifiers;
4. identify provenance and any licensing/usage constraints;
5. profile the fields needed by the study;
6. determine whether a bounded study-specific use is enough or whether governed integration is justified.

Do not merge them with Database v4 solely because names or dates appear to match.

---

## 3. British Horseracing Authority — primary official British racing evidence

Status: `public_external` / `manual_reference` / study-specific structured data

Availability checked: **16 August 2026**.

For questions about what British racing means, permits, requires, schedules, classifies or officially records, BHA material is normally the primary starting point.

### Rules, General Instructions and official guidance

Potential study uses:

- sporting and administrative terminology;
- race conditions and eligibility;
- weights, penalties and allowances;
- handicapping;
- race programming;
- fixture administration;
- race-type and classification semantics.

Entry point:

`https://www.britishhorseracing.com/regulation/rules-guides/`

### BHA Results service and structured API

The public BHA Results frontend uses a structured backend currently available at:

`https://api09.horseracing.software`

Observed useful endpoint patterns include:

- fixture data: `/bha/v1/fixtures/`
- races in a fixture: `/bha/v1/fixtures/{fixtureYear}/{fixtureId}/races`
- race detail: `/bha/v1/races/{yearOfRace}/{raceId}/{divisionSequence}`
- result detail: the corresponding race path with `/results`

Observed race-list/detail fields include, among others:

- `raceId`;
- `fixtureId`;
- `divisionSequence`;
- `raceDate`;
- `raceTime`;
- `raceName`;
- `raceCriteriaRaceType`;
- `raceClass`;
- `ratingBand`;
- `ageLimit`;
- `sexLimit`;
- distance fields;
- going;
- prize amount;
- runner/result availability.

Potential study uses:

- official fixture/race occurrence verification;
- official structured representation of race conditions;
- result reconciliation;
- historical race examples;
- direct comparison of BHA concepts with Inside Rails/source fields.

Important boundary:

An official API field is strong primary structured evidence but is not self-interpreting. Establish the governing concept from BHA rules/terminology where necessary, then use the structured field to see how that concept is represented in actual official records.

The API should not automatically be bulk-ingested into a new database merely because it exists. Historical depth, stability, identifiers, access behaviour and source terms should be established for the particular use.

BHA Results entry point:

`https://www.britishhorseracing.com/racing/results/`

### Official ratings database

BHA publishes current official handicap ratings and states that the database is updated weekly on Tuesday morning. The site currently permits export of the full ratings list, weekly rating changes and latest performance figures to Excel free of charge.

Potential study uses:

- current official ratings;
- rating changes through time when snapshots are preserved;
- comparison between source ratings and official contemporary values;
- studies of handicap treatment or rating movement.

Locator:

`https://www.britishhorseracing.com/regulation/official-ratings/ratings-database/`

### Horse search / breeding and performance information

BHA provides a horse search covering breeding, performance information and statistics for horses in Britain.

Potential study uses:

- bounded horse identity checks;
- breeding/context verification;
- official-rating context;
- manual verification of ambiguous source labels.

Locator:

`https://www.britishhorseracing.com/racing/horses/`

### BHA performance figures

BHA states that it calculates a performance figure for every horse in every race and retains performance figures for each run of a horse's career.

Potential study uses:

- methodological comparison with source ratings;
- contextual validation of performance trends;
- research questions about official handicapping/performance assessment.

Exact bulk accessibility must be checked when a study requires historical performance-figure data.

Locator:

`https://www.britishhorseracing.com/regulation/performance-figures/`

---

## 4. Betfair Exchange historical market data

Status: `account_or_paid`

Availability checked: **9 August 2026**.

Betfair's official Historical Data service provides time-stamped Exchange market data, including market, price and settlement information. Betfair states that this format is available from **April 2015**; Australian/New Zealand market data begins later. Historical files can be purchased/downloaded by registered Betfair customers and downloaded programmatically through the Historical Data API. Free samples are also advertised.

Potential study uses:

- pre-race price paths;
- traded prices and market movement;
- market settlement;
- favourite formation;
- exchange-implied probability rather than final SP alone;
- liquidity/volume questions where the purchased package supports them;
- backtesting questions requiring information available before the race;
- comparison between market expectation and realised outcome.

Official documentation:

`https://support.developer.betfair.com/hc/en-us/categories/10104265927580-Historical-Data`

Service:

`https://historicdata.betfair.com/`

Important boundary:

Do not purchase or bulk-download data merely because it exists. First establish that the proposed study needs the additional market resolution and that the required package contains the necessary fields.

---

## 5. Historical weather and course-condition data

The weather source should match the research question. Forecasts, station observations, reanalysis and climate averages are different concepts and must not be substituted silently.

### Met Office / CEDA MIDAS historical observations

Status: `public_external` / `account_or_paid` depending dataset/access route

Availability checked: **9 August 2026**.

The Met Office identifies MIDAS-Open as an open-access archive of UK weather data hosted by CEDA. CEDA provides historical hourly and daily station-observation datasets. The broader ongoing MIDAS hourly dataset spans from 1875 to the present but uses a request-access route; open snapshots are also published.

Potential study uses:

- observed rainfall before a race;
- temperature, wind, visibility and other observed course-area weather;
- comparison between declared going and preceding observed weather;
- course-specific weather histories;
- validation of reanalysis estimates.

Met Office data catalogue entry point:

`https://www.metoffice.gov.uk/research/climate/maps-and-data/data`

CEDA catalogue:

`https://catalogue.ceda.ac.uk/`

Study requirement:

Course-to-station matching, station distance/elevation and observation coverage must be made explicit. A nearby weather station is not automatically the weather that fell on the racecourse.

### Met Office HadUK-Grid

Status: `public_external`

Availability checked: **9 August 2026**.

HadUK-Grid provides gridded historical UK climate data, with some variables extending back to 1836, under the Open Government Licence.

Potential study uses:

- longer-horizon rainfall/temperature context;
- climate normals and course-region comparisons;
- daily/monthly historical context where exact hourly observations are unnecessary.

Locator:

`https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/overview`

### Open-Meteo historical weather

Status: `public_external`

Availability checked: **9 August 2026**.

Open-Meteo currently provides a no-key historical weather API including ERA5-based hourly historical data from 1940 and other model/reanalysis products.

Potential study uses:

- rapid exploratory weather joins by racecourse coordinates;
- hourly rainfall/temperature/wind histories;
- global courses where UK station archives are not applicable;
- sensitivity comparison against an observational source.

Locator:

`https://open-meteo.com/`

Important boundary:

Reanalysis/model data is not direct on-course observation. For a strong claim about actual weather at a British racecourse, prefer or cross-check against suitable observational evidence where practicable.

---

## 6. Jurisdiction-specific official racing authorities

Status: `verify_when_needed`

Database v4 contains international racing. If a material anomaly or study question concerns a non-British jurisdiction, first look for the relevant official racing authority or racecourse operator rather than assuming a British commercial racing website is the best authority.

Possible information includes:

- official result and runner count;
- race distance;
- race conditions;
- official going/surface;
- prize schedule;
- horse identity/pedigree;
- jockey/trainer/owner identity;
- race time or actual-off time;
- official ratings/handicap marks;
- stewarding information.

Do not maintain a huge static list of every world racing authority here. Identify and verify the relevant authority when a study or anomaly actually requires it, then preserve the evidence in the study/manual-verification workflow.

---

## 7. Commercial racing websites and specialist databases

Status: `manual_reference` / `account_or_paid` / `verify_when_needed`

Examples may include Racing Post, Timeform, pedigree databases, race broadcasters and jurisdiction-specific commercial form providers.

Potential uses:

- bounded independent cross-checks;
- historical reporting;
- specialist pedigree or form context;
- comments, race narratives or sectional context not available from an official authority;
- triangulation when official archives are incomplete;
- investigation of how a commercial publication represents an official concept.

Standing rule:

> Commercial/third-party presentation must not define an official racing concept when suitable primary evidence exists.

Do not assume that because information is visible on a website it can be bulk scraped, republished or incorporated into a commercial analytical database. Check access terms, licensing and technical feasibility before systematic collection.

For a bounded manual verification, preserve the exact source, accessed date, locator and what fact it establishes.

---

## 8. Information categories to actively consider during studies

The following is a prompt list, not a mandatory shopping list. When a study reaches an explanatory or robustness question, ask whether any of these could materially change what can be learned:

- official race results and race conditions;
- declared and changing going;
- weather before and during the meeting;
- course coordinates, layout, elevation and surface;
- draw/stall position;
- rail movements/course configuration;
- race distance and measured/official distance;
- advertised, scheduled and actual-off times;
- starting price;
- exchange prices through time;
- traded volume/liquidity;
- bookmaker overround/market margin;
- official ratings and rating changes;
- performance figures;
- weights and allowances;
- non-runners and withdrawals;
- entries/declarations versus final runners;
- sectional times and pace data;
- finishing times and standard times;
- margins/beaten distances;
- steward reports and interference incidents;
- jockey, trainer and owner identity/history;
- horse age, sex, pedigree and breeding;
- equipment/headgear;
- course/distance/going history;
- prize schedules and race value;
- race class/type/eligibility conditions;
- broader calendar/fixture context;
- contemporary reporting that explains an unusual event.

The study should not collect all of these automatically. The evidence from the preceding analytical step should determine which additional information is worth obtaining.

---

## 9. Study-time source discovery rule

Before writing "the data cannot tell us" or abandoning an explanatory question because Database v4 lacks a field, perform this bounded check:

1. identify the exact missing information;
2. check the primary-source-first rule and identify the authority for the concept;
3. check this register for an already-known source;
4. inspect known local-but-unintegrated products if relevant;
5. search current official/authoritative sources for the missing information;
6. establish access, historical coverage, grain, fields and terms;
7. estimate whether acquisition effort is proportionate to the importance of the question;
8. choose bounded lookup, study-specific acquisition/API use, governed integration, or deliberate non-acquisition;
9. document the decision in the study when it materially limits the conclusion.

The assistant should perform the source-identification and verification steps proactively when the study reaches such a boundary.

---

## 10. Database-escalation rule

External information does **not** automatically belong in Database v4 or require Database v5.

Escalate out of the study only when one of these is true:

- the current database contains a correctness defect that would distort analysis;
- the missing external fact is needed to make an existing governed field analytically correct;
- the new source will clearly support multiple future studies and has a stable, governable interface;
- reproducibility would be materially weakened if each study had to reacquire/reinterpret the same data independently.

Otherwise keep the acquisition study-specific and preserve its provenance with the study outputs.

---

## 11. Maintenance rule

This register is intentionally a living capability map.

Update it when:

- a new local source product is discovered;
- a study identifies a useful external source or API worth remembering;
- an access route disappears or changes materially;
- a paid source is acquired;
- a previously study-specific source becomes a governed database input;
- a source proves unreliable or unsuitable;
- a new class of information becomes relevant to the research programme;
- the accepted Inside Rails database release changes.

Availability statements should include a check date where practical because websites, APIs, pricing and access conditions change.
