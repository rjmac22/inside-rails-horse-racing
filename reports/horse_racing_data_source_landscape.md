# Horse-racing data source landscape — public, open and licensable information

**Checked:** 13 August 2026  
**Scope:** materially relevant sources for Inside Rails research centred on British racing  
**Status:** source and licensing landscape; **no decision is made here about what Inside Rails should buy, ingest or govern**

This report complements [`notebook_27_bha_official_source_feasibility.md`](notebook_27_bha_official_source_feasibility.md), which maps the BHA public-information estate in detail.

---

# Executive conclusion

Inside Rails has access to a much larger evidence base than the Raceform/Kaggle-derived analytical database alone suggests.

The useful information landscape separates into seven different evidence layers:

1. **Official racing administration and governance** — BHA, Weatherbys, racecourse rights holders and official international authorities.
2. **Industry economics and participation** — HBLB, Gambling Commission, fixture/attendance/turnover statistics and public company records.
3. **Betting-market information** — Betfair Exchange prices, traded volume, settlement and market histories.
4. **Race-running information** — GPS tracking, sectional times, speed, stride, jumping and in-running position from RaceiQ/Coursetrack/Total Performance Data.
5. **Weather, soil and geography** — Met Office, UKCEH COSMOS-UK, Ordnance Survey and related open environmental datasets.
6. **Bloodstock, breeding and sales** — Weatherbys, Tattersalls and other sales-company records.
7. **Independent analysis, media and international comparison** — Timeform, Racing Post/Spotlight Sports Group, SIS, IFHA, IHRB and France Galop.

The central licensing finding is equally important:

> **Publicly visible is not the same as open data, and a consumer subscription is not a commercial data licence.**

The sources fall into four practically different access classes:

- **explicitly open/reusable** — for example Met Office HadUK-Grid, UKCEH COSMOS-UK and Ordnance Survey OpenData;
- **public to view or download, but with source-specific or unresolved reuse rights** — for example many BHA/HBLB reports, official international databases and public bloodstock-sale pages;
- **paid for personal/research consumption** — for example Betfair Historical Data tiers, Timeform sectional archives and Racing Post+;
- **commercially licensable feeds/APIs/content** — for example Racecourse Data Company, Race-Day Data, Weatherbys, Total Performance Data, Spotlight Sports Group, Timeform commercial products and SIS.

Several commercially important products publish no general price. They require a quote based on use case, distribution, territory, traffic or customer type. Where a current published price was found, it is recorded below.

The practical consequence is that Inside Rails does **not** need to build one giant replacement database before doing research. A study can assemble the smallest evidence set needed for its question: BHA for official racing facts, HBLB for attendance/economics, Betfair for market beliefs, RaceiQ/TPD for how races were run, Met Office/UKCEH for physical conditions, and sales/breeding sources where horse economics matter.

This report presents that landscape. It deliberately leaves the selection decision to the user.

---

# 1. Access and licensing vocabulary

The following labels are used throughout the report.

| Label | Meaning |
|---|---|
| **OPEN** | An explicit open licence or similarly clear reuse permission was identified. |
| **PUBLIC** | The information can be viewed or downloaded without payment, but broad automated/commercial reuse rights are not assumed. |
| **PAID-PERSONAL** | A consumer/private-use product is available for payment. This does not imply redistribution or commercial publication rights. |
| **COMMERCIAL-LICENCE** | The supplier explicitly licenses data, APIs, feeds or content commercially. |
| **RESTRICTED** | The information is confidential, participant-only, internal or otherwise not generally available. |
| **UNRESOLVED** | A public surface exists but licence terms, data access or historical limits were not established sufficiently in this sweep. |

Prices are a **13 August 2026 snapshot** and can change. Supplier terms, VAT/tax, territory, redistribution, derived-data rights and publication use must be checked for any source selected for systematic use.

This report is a research-source inventory, not legal advice.

---

# 2. Master source map

| Source | Evidence domain | Public access | Explicit open reuse | Commercial licence/feed | Published price found |
|---|---|---|---|---|---|
| **BHA** | Official GB fixtures, races, results, participants, ratings, going, statistics, regulation | Yes | Not established generally | Public frontend uses structured services; broad commercial terms not established | No broad data rate found |
| **HBLB** | Attendance, abandonments, turnover summaries, funding, research, industry economics | Yes | Source-specific; not assumed generally | Some underlying information is restricted | Public services £0 |
| **Racecourse Data Company (RDC)** | Official pre-raceday British racing data rights | Via licensed distributors | No | Yes | **Yes — 2026 rate card** |
| **RMG Race-Day Data (RDD)** | Going, withdrawals, jockey changes, race status, betting shows, results | No general raw feed | No | Yes, via PA Betting Services | Current rate card exists; numeric rate not established here |
| **Weatherbys** | Racing administration, registrations, entries, declarations, horse/breeding/sales data | Some public information | No general open licence identified | Yes — raw files, feeds, API/bespoke data | Quote |
| **RaceiQ / Racing TV** | Public sectionals and tracking-derived metrics | Yes | No open bulk licence identified | Underlying tracking rights separately licensable | £0 to view |
| **Total Performance Data / Coursetrack** | GPS, sectionals, speed, points, routes, jumps, live/post-race tracking | Some public representations | No | Yes | Quote |
| **Betfair Exchange Historical Data** | Prices, traded volume, market state and settlement | Basic free; richer paid | No general open licence | Yes; commercial uses require appropriate agreement | **Yes** |
| **Gambling Commission** | Gambling-sector/operator statistics | Yes | Publication-specific | Not normally a commercial feed product | £0 public downloads |
| **Met Office HadUK-Grid / MIDAS-Open** | Historical weather/climate | Yes | **Yes** | Also paid DataHub services | £0 open datasets |
| **Met Office DataHub** | Recent/live observations and atmospheric data | Yes via API/account | Licensed API use | Yes | **Yes** |
| **UKCEH COSMOS-UK** | Soil moisture and meteorological observations | Yes | **Yes — OGL** | Not required for open dataset/API | £0 |
| **Ordnance Survey** | Geography, boundaries, names, features and mapping | Yes | **Yes** for OpenData | Premium APIs also available | **Yes** |
| **Companies House** | Company, officer, PSC, filing and accounts information | Yes | Broad public reuse subject to third-party/data-protection caveats | Free API/bulk products | £0 |
| **Tattersalls** | Bloodstock sale lots, pedigree context, consignor, purchaser, price | Yes | **No — terms restrict automated/commercial harvesting** | Commercial use requires permission/licence | £0 view/export; commercial price quote/not published |
| **Goffs** | Bloodstock sale results | Yes | Not established in this sweep | Not established | £0 view; licence/price unresolved |
| **Timeform** | Ratings, form, analysis, sectional archives, proprietary metrics | Limited public | No | Yes | **Yes for sectional archive; B2B quote** |
| **Racing Post / Spotlight Sports Group** | Form, ratings, comments, profiles, pedigree, stats, tipping, API/content | Partial free + subscription | No | Yes | **Consumer price published; B2B quote** |
| **SIS** | Global live racing pictures/data/commentary/graphics/markets | Product descriptions public | No | Yes | Quote |
| **PA Betting Services** | Distribution of official race-day/pre-race products | Product/service layer | No | Yes | Quote / source-specific rights charges |
| **IFHA** | International rankings, standards, statistics and reference material | Yes | General reuse not established here | Not investigated as a commercial feed | £0 public material |
| **IHRB** | Official Irish regulation, ground, non-runners, ratings, stewards/appeals | Yes | General reuse not established here | Not established | £0 public material |
| **France Galop** | Official French horses, actors, results, sectionals, statistics, replays | Yes | General bulk reuse not established here | Not established in this sweep | £0 public material |

---

# 3. Official British racing administration

## 3.1 British Horseracing Authority — BHA

**Role:** governing and regulatory authority for British horseracing.

**Access classes:** PUBLIC; structured public-frontend services observed; broad reuse/commercial licence unresolved.

Notebook 27 established that the BHA public estate contains much more than final race results. Demonstrated or site-confirmed information includes:

- fixtures and fixture detail;
- races and race detail;
- entries;
- nominations;
- results and runners;
- going, going history, GoingStick, weather and watering;
- officials;
- Stewards Reports;
- racecourse information;
- live racing updates/non-runners;
- horse profiles and performances;
- horse training history;
- official ratings and rating history;
- performance figures;
- jockey and trainer profiles/statistics;
- trainer non-runners;
- championships;
- owner championships;
- annual fixture lists;
- annual/monthly Racing Data Packs;
- Horse Population Reports;
- Race Off-Times reporting;
- claiming-race information;
- handicapping appeals;
- disciplinary/regulatory material;
- racecourse technical information;
- Rules and General Instructions;
- anti-doping, welfare and licensing resources.

The BHA should generally be treated as the primary authority when the research question concerns an **official British racing fact, definition, administrative state or regulatory outcome**.

That does not mean every BHA field can be interpreted naively. Notebook 27 demonstrated semantic traps such as current ratings appearing in historical performance rows and race-result timing fields whose meaning is not simply the literal field name.

**Historical depth:** varies materially by information family. There is no defensible single “BHA start date”.

**Price:** public website/reports £0 to access. No broad published public data/API licensing rate was established.

**Reuse:** public accessibility must not be treated as an open licence. Any systematic commercial extraction or republication requires source-specific terms review.

Full findings: [`notebook_27_bha_official_source_feasibility.md`](notebook_27_bha_official_source_feasibility.md).

---

## 3.2 Weatherbys

**Role:** a central racing-administration and data-management organisation working under contract to the BHA, as well as a commercial racing/breeding data supplier.

**Access classes:** PUBLIC for some information; COMMERCIAL-LICENCE for data supply/API/feed products.

Weatherbys describes racing-administration work covering areas such as:

- race entries;
- qualifications and eligibility checking;
- weights based on BHA ratings and race conditions;
- jockey bookings;
- declarations;
- final runners;
- eliminations;
- stall allocation;
- horse registrations and naming;
- racing colours;
- sponsorship administration;
- post-race finishing positions;
- rider weights;
- non-runner information;
- prize-money administration;
- General Stud Book and breeding information.

Its commercial data-supply operation advertises:

- race data;
- performance data;
- horse data;
- sales data;
- breeding histories;
- ownership information;
- bespoke raw data files;
- one-off or ongoing feeds;
- APIs including specialist breeding/stallion products;
- tailored analysis/data extracts.

This makes Weatherbys important because some of its information is not merely third-party form commentary: it originates inside racing's administrative machinery.

**Price:** no current standard data-feed/API price was published on the pages inspected. Commercial supply is **quote/contact**.

**Public entry points:**  
https://www.weatherbys.co.uk/racing  
https://www.weatherbys.co.uk/commercial/data-supply

---

## 3.3 Racecourse Data Company — official pre-raceday data rights

**Role:** rights-management company representing British racecourses for official pre-raceday data.

**Access class:** COMMERCIAL-LICENCE.

The current RDC site states that it represents **59 British racecourses** and licenses official **Pre-Raceday Data (PRD)**.

The licensed information includes items such as:

- final fields;
- owners;
- trainers;
- jockeys;
- weights;
- racing colours;
- draw;
- ratings.

RDC lists four official on-sellers:

- PA Betting Services;
- Spotlight Sports Group / Racing Post;
- Racing and Sports;
- SIS.

### Published 2026 RDC rate card

The following figures were published in the 2026 RDC rate card checked during this sweep.

#### General-use licences

| Licence category | Published 2026 rate |
|---|---:|
| Bookmaker — LBO | **£71.73 per shop/year** |
| Bookmaker — Online | **£26,172/year** |
| International bookmaker — LBO | **£21.26 per shop** |
| International bookmaker — Online | **£2,126** |
| Racecourse racecard | **£1,435** |
| Racecourse website | **£1,435** |
| Daily newspaper | **£3,113** |
| Non-daily newspaper | **£373** |
| Media website | **£1,721** |
| Pro punters | **£3,000** |
| Distributor licence | **£71,727** |

#### Specialist-use licences

| Licence category | Published 2026 rate |
|---|---:|
| Print / wallsheet | **0.5% of net circulation revenue** |
| Form publications | **£7,173 flat fee** |
| Website | **£0.00213 per page view** |
| Tablet/mobile | **£0.00213 per page view** |
| B2C broadcaster | **£0.00213 per unique viewer/subscription/day** |
| B2B broadcaster — UK | **£11.47 per shop** |
| B2B broadcaster — international | **£2,126 per £10m customer turnover** |
| Syndicate/racehorse-ownership groups on own platforms | **£0** |

The exact licence category, distributor charges, tax/VAT and permitted use should be confirmed with RDC before relying on these figures commercially.

**Source:**  
https://www.racecoursedatacompany.com/  
https://www.racecoursedatacompany.com/wp-content/uploads/2025/12/RDC-Ratecard-2026.pdf

---

## 3.4 RMG Race-Day Data

**Role:** official race-day data product associated with Racecourse Media Group racecourses.

**Access class:** COMMERCIAL-LICENCE.

RMG's Race-Day Data product covers live race-day information including:

- going;
- withdrawals;
- jockey changes;
- race status;
- betting shows;
- results.

RMG states that the product is delivered through **PA Betting Services** and requires a licence. Its current site provides a rate-card route, but a reliable current numerical 2026 charge was not established during this sweep.

**Price:** commercial licence; **current numerical rate unresolved/confirm with supplier**.

**Source:**  
https://www.racecoursemediagroup.com/company-structure/rdd/

---

# 4. Industry economics, attendance and participation

## 4.1 Horserace Betting Levy Board — HBLB

**Role:** statutory levy body with public racing/industry data services.

**Access class:** PUBLIC. Some underlying commercial betting information is RESTRICTED.

The HBLB public estate includes distinct data services for:

- racecourse attendance;
- abandoned fixtures;
- race turnover performance;
- equine science/research projects;
- levy/racing funding material;
- public reports and statistics.

### Attendance

The public Attendance Enquiry provides data from **1989 onwards** and includes a downloadable-data function.

The HBLB defines attendance as components including:

- paying public;
- annual members;
- complimentary badges.

The source also documents a methodology change from **1 March 2022**, when actual annual-member attendance and under-18 attendance were incorporated differently. It notes that attendance figures are supplied by racecourses and are not independently verified by HBLB.

This makes the data useful not only for attendance counts but for understanding exactly what is being counted.

### Betting turnover

HBLB publishes public race-turnover analyses and high-level trends. It also publishes selected top-race turnover information.

However, detailed underlying **race-by-race major-bookmaker turnover is confidential**, so the public data should not be mistaken for a complete downloadable betting-market history.

### Equine research

The HBLB research estate includes publicly searchable funded equine-science projects, providing a distinct evidence source for veterinary/welfare research rather than race performance.

### Funding/prize-money material

HBLB publishes funding/rate-card material and has published race-level contribution information in downloadable formats for recent periods.

**Price:** £0 for the public services identified.

**Licence:** public availability is demonstrated, but a single general open-data licence covering every HBLB product was not established. Reuse terms should be checked per publication/data service.

**Sources:**  
https://www.hblb.org.uk/  
https://www.hblb.org.uk/attendance

---

## 4.2 Gambling Commission

**Role:** official gambling regulator; useful for the economics of betting rather than race administration.

**Access class:** PUBLIC.

The Gambling Commission publishes downloadable statistics covering the regulated gambling sector, including quarterly/periodic operator statistics and regulatory-return information.

Potentially useful information includes:

- remote and non-remote gambling activity;
- gross gambling yield;
- turnover/stakes measures where published;
- betting-shop counts;
- operator/channel trends;
- product/category data where horse racing is separately identified;
- industry changes over time.

The regulator's datasets operate at a very different grain from Betfair market histories or race-level results. They are most useful for **market-size and industry-economics questions**.

**Price:** £0 for public downloads.

**Licence:** publication/reuse terms should be checked for the selected dataset; this report does not assert a universal OGL for all Commission publications.

**Source:**  
https://www.gamblingcommission.gov.uk/statistics-and-research

---

# 5. Betting-market information

## 5.1 Betfair Exchange Historical Data

**Role:** historical market evidence showing what exchange participants were willing to back/lay and how those prices/liquidity changed.

**Access classes:** PUBLIC/PAID-PERSONAL for historical-data products; COMMERCIAL-LICENCE/approval for some business uses.

Betfair's Historical Data service provides detailed Exchange market, price and settlement data from **April 2015 onward**.

Depending on tier, useful information includes:

- market status/state;
- runner selections;
- last traded prices;
- back/lay price ladders;
- traded volumes;
- timestamped market updates;
- final settlement/results.

This enables research that ordinary starting-price fields cannot support, including:

- market probability through time;
- price drift/steam;
- late information arrival;
- liquidity;
- favourite-longshot effects;
- market efficiency;
- closing-price benchmarks;
- strategy backtesting against the market that actually existed at the time.

### Historical Data prices

| Horse-racing historical tier | Resolution/content | Current published price |
|---|---|---:|
| Basic | 1-minute intervals, last traded price, no volume | **Free** |
| Advanced | 1-second intervals, top three price levels, volume | **£69/month or £699/year** |
| Pro | API-tick data (~50 ms), full price ladder, volume | **£230/month or £2,299/year** |

### Exchange API key

For the Exchange API, Betfair currently distinguishes development/delayed access from a live key.

| Access | Published price |
|---|---:|
| Delayed App Key for development/private betting use | **£0** |
| Live App Key activation for betting use | **£499 one-off** |

Commercial software, odds publication, operator or redistributive use may require additional approval/licensing beyond a personal betting API key.

**Sources:**  
https://support.developer.betfair.com/hc/en-us/articles/360002407732-What-data-is-provided-by-the-Historical-Data-service  
https://historicdata.betfair.com/

---

# 6. How races were actually run — tracking and sectionals

## 6.1 RaceiQ / Racing TV

**Role:** public presentation of tracking/sectional information and derived race-performance metrics.

**Access class:** PUBLIC for viewing. No open bulk-data licence was identified.

Racing TV states that RaceiQ data/metrics are available free through its results products, with British data backdated to **March 2023** and Irish data to **January 2024**.

Information exposed includes combinations of:

- sectional timing for every horse/every furlong;
- in-running position;
- cumulative time relative to the leader;
- pace graphs;
- speed-related measures;
- stride length/frequency;
- acceleration measures such as 0–20 MPH;
- jumping measures;
- Jump Index;
- Lengths Gained Jumping;
- Par Sectionals;
- Time Index;
- other RaceiQ derived metrics.

This is a fundamentally different evidence layer from form/results data because it describes **how a horse moved through the race**, not just its final outcome.

**Price:** £0 for public website/app viewing.

**Licence:** free viewing must not be interpreted as permission to bulk harvest, redistribute or republish the underlying tracking data.

**Source:**  
https://www.racingtv.com/raceiq

---

## 6.2 Total Performance Data / Coursetrack

**Role:** underlying GPS/tracking and sectional data supplier/licensor.

**Access class:** COMMERCIAL-LICENCE, with some public representations through racing-media products.

TPD advertises APIs/feeds covering areas such as:

### Live

- live tracking;
- race progress;
- fixtures/race lists;
- jump locations/events;
- routes;
- par points.

### Post-race

- sectional history;
- sectional feeds/charts;
- points/coordinate data;
- route data;
- race lists and fixture information.

TPD states that its database contains very large international histories and describes UK coverage including tens of thousands of races since **2016**.

Industry arrangements have consolidated Coursetrack and TPD British tracking so that British racecourse tracking can be presented through public media products while TPD provides commercial licensing for underlying data products.

**Price:** **available on request / quote**.

**Source:**  
https://www.totalperformancedata.com/live-pr-api-2/

---

## 6.3 At The Races

At The Races results pages can expose tracking-derived information such as sectionals, stride and jumping metrics where available.

**Access:** PUBLIC viewing.

**Price:** £0 to view.

For systematic/raw tracking-data rights, the relevant commercial supplier rather than the public ATR presentation should be investigated.

---

# 7. Weather, soil and environmental evidence

## 7.1 Met Office HadUK-Grid

**Role:** authoritative UK climate observations in gridded form.

**Access class:** **OPEN**.

HadUK-Grid provides UK climate variables on a **1 km grid** and is released under the **Open Government Licence**.

Examples of historical coverage include:

- daily rainfall: **1891–present**;
- daily maximum/minimum temperature: **1960–present**;
- monthly rainfall: extending back to **1836**;
- monthly temperature series: extending back into the nineteenth century.

Depending on variable/product, useful measures include:

- rainfall;
- temperature;
- frost;
- sunshine;
- pressure and other climate measures.

This is potentially useful for long-run course/environment studies because it avoids dependence on a weather website's undocumented historical reconstruction.

**Price:** £0.

**Licence:** Open Government Licence, subject to the source's attribution/terms.

**Source:**  
https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets

---

## 7.2 Met Office MIDAS-Open and historical station data

The Met Office also exposes open historical observation archives including **MIDAS-Open** and related station datasets.

These can provide station-based observations rather than gridded estimates, depending on variable and station history.

**Access:** OPEN/PUBLIC according to selected dataset.

**Price:** £0 for open datasets.

**Source:**  
https://www.metoffice.gov.uk/research/climate/maps-and-data/data

---

## 7.3 Met Office DataHub — recent/live observations

**Role:** programmatic access to current/recent meteorological products.

**Access class:** licensed API with free and paid tiers.

### Land observations

The inspected product provides recent land observations, including hourly JSON observations from a network of UK stations, with a limited recent-history window.

Current published request tiers were:

| Calls/day | Price/month |
|---:|---:|
| 360 | **Free** |
| 900 | **£9** |
| 3,600 | **£32** |
| 18,000 | **£146** |
| 36,000 | **£250** |
| 72,000 | **£437** |

Published prices are stated excluding applicable tax/VAT.

### Atmospheric data allowance

The DataHub also publishes data-volume plans. Current figures inspected were:

| Monthly allowance | Price/month |
|---:|---:|
| 1 GB | **Free** |
| 10 GB | **£15** |
| 25 GB | **£35** |
| 50 GB | **£65** |
| 100 GB | **£128** |
| 150 GB | **£189** |
| 250 GB | **£308** |
| 400 GB | **£476** |
| 600 GB | **£690** |

The DataHub terms provide an API/data licence rather than an open-public-domain grant and require applicable attribution, including the stated Met Office attribution requirements.

**Source:**  
https://datahub.metoffice.gov.uk/

---

## 7.4 UKCEH COSMOS-UK

**Role:** environmental monitoring, particularly soil moisture, with meteorological measurements at monitoring sites.

**Access class:** **OPEN — Open Government Licence**.

The current public dataset identified in this sweep covers **2013–2025**, with a public near-real-time API extending the source to current observations.

Variables include combinations of:

- volumetric soil-water content;
- precipitation;
- air temperature;
- atmospheric pressure;
- wind;
- relative humidity;
- solar/radiative variables;
- soil temperature;
- soil heat flux;
- other site meteorology.

Data are available at useful temporal resolutions including sub-daily and daily products.

This source is especially interesting for going/ground studies because it provides **measured soil moisture**, but the monitoring stations are not racecourses. Any racecourse use requires a defensible spatial matching/interpolation method; a nearby station must not be labelled a course measurement.

**Price:** £0.

**Licence:** OGL.

**Sources:**  
https://catalogue.ceh.ac.uk/documents/dde10e2b-ee1a-4b2b-a247-176db2f7bb31  
https://catalogue.ceh.ac.uk/id/e29d2d3b-8aaf-4b13-9577-5ca9b8215e73

---

# 8. Geography and physical context

## 8.1 Ordnance Survey

**Role:** authoritative Great Britain geographic data.

**Access classes:** **OPEN** for OpenData; paid/licensed for premium services.

OS OpenData can provide inputs useful for:

- authoritative place names;
- coordinates/reference geography;
- administrative boundaries;
- transport/geographic context;
- terrain/feature context depending on product;
- distance/spatial analysis.

The free OpenData catalogue supports formats such as GeoPackage, GML, Shapefile and CSV depending on product.

### OpenData

**Price:** £0.

OpenData is licensed for commercial and personal reuse under the applicable OS OpenData/Open Government licensing terms.

### DataHub premium APIs

Current DataHub pricing inspected includes the first **£1,000 of eligible premium API usage per month free**, with usage charges beyond the allowance. Example published transaction prices include:

| Product/API | Example price per transaction |
|---|---:|
| OS NGD Features | **£0.19** |
| Premium tiles | **£0.0331** |
| OS Maps leisure | **£0.000525** |
| Premium map | **£0.0331** |
| OS Features premium | **£0.19** |
| OS Names / Linked Identifiers | **Free** |
| OS Places | **£0.0282** with separate/special terms |

Exact transaction definitions and licensing terms differ by API.

**Sources:**  
https://www.ordnancesurvey.co.uk/products/open-data  
https://osdatahub.os.uk/plans

---

# 9. Companies, ownership structures and industry entities

## 9.1 Companies House

**Role:** official UK corporate register rather than a racing source.

**Access class:** PUBLIC; free API/bulk datasets with important third-party copyright/data-protection caveats.

Potentially useful information includes:

- company identity/status;
- registered office;
- officers/directors;
- persons with significant control;
- filing history;
- accounts filings;
- charges;
- incorporation/dissolution events;
- company-name history.

This could support research into:

- racecourse operating companies;
- commercial ownership structures;
- racing/media/data suppliers;
- trainer/owner businesses where correctly entity-resolved;
- industry company accounts and changes over time.

Companies House provides:

- public website search;
- a free public API;
- monthly company bulk-data files.

The public API rate limit is currently **600 requests per five minutes**.

**Price:** £0 for the public API and standard public bulk products identified.

Companies House states that it does not impose its own general rules on reuse of public-register information, but users remain responsible for data protection and any third-party copyright contained in filings. That distinction matters especially for document reproduction.

**Sources:**  
https://www.gov.uk/guidance/searching-the-companies-house-register  
https://developer.company-information.service.gov.uk/

---

# 10. Bloodstock, breeding and sales

## 10.1 Tattersalls

**Role:** major bloodstock auction house with public historical sale/result information.

**Access classes:** PUBLIC viewing/download; commercial reuse requires permission/licence under site terms.

Public sale-result pages expose information including:

- lot number;
- horse/name;
- sire;
- dam;
- sex/type/year context depending on sale;
- consignor;
- purchaser;
- sale price;
- sale-level turnover;
- average;
- median;
- top price.

Some sale-result pages provide an **XLS export**.

That creates potential links between bloodstock economics and subsequent racing outcomes, for example:

- purchase price versus performance;
- trainer/owner/buyer outcomes;
- sire/dam economics;
- resale paths;
- sale cohorts;
- market trends.

### Licensing warning

Tattersalls' current website terms prohibit using automated systems/crawlers to harvest, access or analyse site information without permission. The terms allow ordinary personal use but state that commercial use requires a licence from Tattersalls or relevant licensors.

Therefore:

> **An XLS download button does not make Tattersalls an open bulk dataset.**

**Price:** £0 to view/use the public interface. Commercial data/content licence price was not published in the inspected material — **contact/quote**.

**Sources:**  
https://www.tattersalls.com/  
https://secure.tattersalls.com/

---

## 10.2 Goffs

Goffs public sale material exposes bloodstock catalogue/result information including combinations of:

- lot;
- horse;
- sire/dam;
- consignor;
- purchaser;
- sale result/price;
- sale summary measures.

**Price:** public browsing £0.

**Licence/bulk extraction:** not resolved sufficiently in this sweep. It should remain **UNRESOLVED** until its current website/data terms are checked for the exact intended use.

---

## 10.3 Weatherbys breeding data

Weatherbys should also be considered separately from auction houses because it maintains authoritative breeding/registration information and offers commercial breeding datasets/APIs.

Commercial products advertised include pedigree/breeding histories, sales information, Stallion Data API products, Return of Mares material and bespoke data supply.

**Price:** quote.

---

# 11. Proprietary analysis and racing-media data

## 11.1 Timeform

**Role:** proprietary form/ratings/analysis provider rather than an official regulator.

**Access classes:** PAID-PERSONAL and COMMERCIAL-LICENCE.

### Sectional archives

Timeform sells downloadable sectional-time archives in XLSX form.

The current product material describes historical archives from **2015 onward** and includes Timeform-derived measures such as finishing-speed calculations/upgrades alongside underlying sectional information.

**Published price:** **£100 per subscription period/archive** for the inspected sectional product.

The product is licensed for private individual use; sharing/republishing without permission is not granted by buying the consumer product.

### Commercial products/API

Timeform advertises commercial data/API products covering racing/form information, with historical coverage in some products extending to the early 1990s.

Not every Timeform product is supplied by API; for example some sectional products are spreadsheet products rather than API endpoints.

**Commercial price:** **quote/contact**. No reliable current general 2026 B2B API price was published in the inspected commercial pages.

Old historical prices found on archived Timeform pages were deliberately **not** treated as current prices.

**Sources:**  
https://www.timeform.com/horse-racing/shop/sectional-times  
https://www.timeform.com/commercial/products

---

## 11.2 Racing Post / Spotlight Sports Group

**Role:** major racing-media, form and commercial data/content provider.

**Access classes:** partial PUBLIC, PAID-PERSONAL subscription, COMMERCIAL-LICENCE/API.

The consumer and commercial products collectively include combinations of:

- racecards;
- results;
- horse form;
- trainer/jockey/owner profiles;
- statistics;
- pedigree/sales context;
- proprietary ratings;
- comments/analysis;
- tipping/content;
- race replays where rights permit;
- data products such as Predictor/BetFinder;
- commercial JSON/API feeds.

### Consumer subscription

A current standard Racing Post+ Insights subscription page inspected in July/August 2026 showed:

- **£29.95/month**;
- **£299/year**.

Promotional prices can differ, so those figures should not be treated as a permanent lowest available consumer price.

### Commercial/B2B

Spotlight Sports Group advertises Racing Post API/Superfeed products for commercial clients.

**Price:** quote/contact; no general B2B rate card was identified.

Racing Post/Spotlight is also one of RDC's official on-sellers for British pre-raceday data, meaning a commercial product may combine proprietary content with separately governed official-data rights.

**Sources:**  
https://www.racingpost.com/  
https://www.sportscontentsolutions.com/

---

## 11.3 SIS

**Role:** commercial live betting/racing content and data supplier.

**Access class:** COMMERCIAL-LICENCE.

SIS advertises a large international horse-racing portfolio across more than 170 venues, combining products such as:

- live pictures;
- racing data;
- commentary;
- graphics;
- markets/prices;
- betting-channel distribution.

SIS is also listed by RDC as an official on-seller of British pre-raceday data.

**Price:** quote/demo; no general published horse-racing feed price identified.

**Source:**  
https://www.sis.tv/24-7-live-betting-channels/

---

## 11.4 PA Betting Services

**Role:** commercial distribution layer for official/rights-managed racing data.

**Access class:** COMMERCIAL-LICENCE.

PA Betting Services is identified by RMG as the technical/distribution supplier for Race-Day Data and by RDC as an official pre-raceday data on-seller.

This matters because buying an official British racing feed can involve two distinct questions:

1. **who owns/licenses the underlying rights?**
2. **who technically supplies the feed?**

Supplier fees and rights-holder licence charges should therefore not automatically be assumed to be the same thing.

**Price:** quote/source-specific.

---

# 12. International official sources

These sources are not substitutes for the BHA for British regulatory facts. Their main value is cross-border racing, foreign performances and international comparison.

## 12.1 International Federation of Horseracing Authorities — IFHA

**Access class:** PUBLIC.

The IFHA public estate contains:

- World's Best Racehorse Rankings;
- international classifications/rankings;
- annual reports;
- Facts & Figures;
- International Cataloguing Standards;
- Blue Book material;
- protected-name information;
- integrity/reference material;
- international statistics and technical information;
- Global Reference Library material.

Historical reference publications extend over many years; Blue Book material located during the sweep reaches at least into the **2000s**.

**Price:** £0 for the public material identified.

**Licence:** broad bulk/commercial reuse rights were not established; check source-specific terms before systematic reuse.

**Source:**  
https://www.ifhaonline.org/

---

## 12.2 Irish Horseracing Regulatory Board — IHRB

**Role:** official Irish racing regulator.

**Access class:** PUBLIC.

Public racing/regulatory information includes:

- fixture/raceday information;
- Stewards enquiry reports;
- ground reports;
- non-runners/reserves;
- handicap ratings;
- safety limits;
- referrals;
- appeals and regulatory decisions.

This is particularly relevant when British horses/trainers participate in Irish racing or when a study compares British and Irish regulatory concepts.

**Price:** £0 for public pages/reports.

**Licence/API:** no broad public bulk-data/API licence was established in this sweep.

**Source:**  
https://www.ihrb.ie/

---

## 12.3 France Galop

**Role:** official French racing authority/operator for Flat and Jump racing under its remit.

**Access class:** PUBLIC; bulk/API commercial terms unresolved.

The public estate includes:

- horse information;
- trainer/jockey/owner/actor information;
- calendar;
- entries;
- declarations;
- past performances/results;
- race replays;
- official sectional information at covered racecourses;
- official statistics/publications.

France Galop has incorporated official sectionals into race-result material at covered tracks, with the modern sectional programme dating from around **2019–2020** depending on coverage.

Its **Baromètre du Galop** provides a particularly broad industry-statistics view, with downloadable material across themes such as:

- breeding/births/stallions;
- bloodstock sales;
- races/runners;
- incentives/prize structures;
- horse populations;
- competitiveness;
- owners/trainers/jockeys;
- employment;
- attendance/audiences;
- betting.

**Price:** £0 for the public information identified.

**Licence:** public viewing/download does not establish a general bulk-commercial licence; current terms would need checking before systematic acquisition.

**Source:**  
https://www.france-galop.com/

---

# 13. Published-price snapshot

The following table brings together the prices actually found rather than mixing them with quote-only products.

| Source/product | Access | Published price checked 13 Aug 2026 |
|---|---|---:|
| BHA public website/reports | Public | **£0** |
| HBLB public data services | Public | **£0** |
| RaceiQ public results/metrics | Public view | **£0** |
| Betfair Historical Basic | Personal/research | **£0** |
| Betfair Historical Advanced | Personal/research | **£69/month or £699/year** |
| Betfair Historical Pro | Personal/research | **£230/month or £2,299/year** |
| Betfair delayed development App Key | API development/private betting | **£0** |
| Betfair live betting App Key activation | API/private betting | **£499 one-off** |
| Met Office Land Observations | API | **360 calls/day free**; then £9–£437/month across published tiers |
| Met Office atmospheric allowance | API | **1 GB/month free**; then £15–£690/month across published tiers |
| HadUK-Grid | Open data | **£0** |
| UKCEH COSMOS-UK | Open data/API | **£0** |
| Ordnance Survey OpenData | Open data/API | **£0** |
| OS eligible premium API use | Commercial/premium | **first £1,000 eligible usage/month free**, then product transaction charges |
| Companies House API/bulk company data | Public | **£0** |
| Tattersalls public result pages/XLS where offered | Public/personal access | **£0**; commercial licence quote |
| Timeform sectional archive | Paid personal | **£100 per archive/subscription period** |
| Racing Post+ Insights | Consumer | **£29.95/month or £299/year** standard price observed |
| RDC Bookmaker LBO | Commercial licence | **£71.73/shop/year** |
| RDC Bookmaker Online | Commercial licence | **£26,172/year** |
| RDC Racecourse racecard | Commercial licence | **£1,435** |
| RDC Racecourse website | Commercial licence | **£1,435** |
| RDC Daily newspaper | Commercial licence | **£3,113** |
| RDC Media website | Commercial licence | **£1,721** |
| RDC Pro Punters | Commercial licence | **£3,000** |
| RDC Distributor | Commercial licence | **£71,727** |
| RDC Form Publications | Commercial licence | **£7,173** |
| RDC digital specialist use | Commercial licence | **£0.00213/page view or equivalent unit** depending category |

Prices should be rechecked at the point of purchase/licensing. A supplier may also apply VAT, distributor fees, minimum terms, territory restrictions or different categories depending on actual Inside Rails use.

---

# 14. Commercially licensable sources for which no standard price was found

| Source/product | What can be licensed | Price status |
|---|---|---|
| Weatherbys commercial data | races, horses, performances, breeding, sales, ownership, APIs/raw feeds/bespoke extracts | **Quote** |
| Total Performance Data | live/post-race tracking, sectionals, points, routes and related feeds | **Quote** |
| RMG Race-Day Data | going, withdrawals, jockey changes, race status, shows, results | **Rate-card/licence route exists; current numeric figure not established here** |
| PA Betting Services | official racing-data distribution | **Quote/source-specific** |
| SIS | live racing pictures/data/commentary/graphics/markets | **Quote** |
| Racing Post / Spotlight B2B | API/Superfeed, racecards, form, results, stats, proprietary content | **Quote** |
| Timeform commercial | form/ratings/data/API products | **Quote** |
| Tattersalls commercial reuse | commercial use of protected sale/content information | **Licence required; price not published** |

A missing published price does **not** imply that a source is unavailable. It usually means the supplier prices according to the use case.

---

# 15. Historical-depth map

Historical depth is source-specific. The following are demonstrated or stated boundaries found during this survey, not claims that every field within a source reaches the same date.

| Source | Historical depth observed/stated |
|---|---|
| BHA | Varies by family; some metadata reaches into the 1990s, while modern live/API products have different boundaries |
| HBLB attendance | **1989 onward** |
| RaceiQ GB | **March 2023 onward** public backfill stated |
| RaceiQ Ireland | **January 2024 onward** public backfill stated |
| TPD UK tracking | supplier describes UK history from **2016** |
| Betfair Historical Data | **April 2015 onward** |
| Met Office HadUK daily rainfall | **1891 onward** |
| Met Office HadUK daily max/min temperature | **1960 onward** |
| Met Office HadUK monthly rainfall | **1836 onward** |
| UKCEH COSMOS-UK | **2013 onward** |
| Timeform sectional archives | **2015 onward** |
| Timeform broader commercial racing coverage | some products described from the **early 1990s** |
| IFHA reference archive | historical publications located at least into the **2000s** |
| France Galop modern official sectionals | approximately **2019–2020 onward**, coverage dependent |
| Tattersalls | broad historical sale archive visible; exact systematic boundary not established |

Historical depth should be established properly only for a source selected for a particular study.

---

# 16. What these sources allow us to study

The strongest consequence of the source landscape is not the number of fields available. It is that previously separate questions can be connected using different authoritative or specialist evidence.

## 16.1 Going, weather and the physical course

Potential evidence stack:

- BHA going declarations/history;
- GoingStick;
- BHA watering/weather updates;
- Met Office station/gridded weather;
- UKCEH soil-moisture observations where spatially defensible;
- Ordnance Survey/geography;
- race results and sectionals.

Possible questions include how official going relates to preceding rainfall, temperature, watering and measured/nearby soil conditions, and whether race-running measures respond consistently to those descriptions.

---

## 16.2 How races were run

Potential evidence stack:

- BHA race/results information;
- RaceiQ public sectionals;
- TPD/Coursetrack tracking;
- Timeform sectional analysis;
- race video where viewing rights permit.

This supports questions about pace, position, energy distribution, jumping, finishing speed and tactical shape rather than only winner/loser outcomes.

---

## 16.3 What the market believed

Potential evidence stack:

- BHA official result/runner identity;
- Betfair timestamped prices and traded volume;
- public/official non-runner and going updates;
- sectionals/performance evidence after the event.

This allows study of information arrival, market efficiency, late price movement, liquidity and whether particular observable information is already priced into the market.

---

## 16.4 Racing economics and audience

Potential evidence stack:

- HBLB attendance;
- HBLB funding/turnover summaries;
- Gambling Commission sector statistics;
- BHA fixture/race statistics;
- Companies House accounts/company events;
- racecourse/company information.

This could support work on attendance trends, fixture economics, betting-channel change, racecourse business structures and broader industry health.

---

## 16.5 Bloodstock economics

Potential evidence stack:

- Tattersalls/Goffs sale results;
- Weatherbys pedigree/breeding data;
- BHA horse/racing history;
- official ratings/performance information;
- trainer/owner histories.

This could support purchase-price versus racing-performance studies, sire/dam economics, buyer/trainer outcomes and cohort analysis.

---

## 16.6 International comparison

Potential evidence stack:

- BHA;
- IHRB;
- France Galop;
- IFHA;
- equivalent national authorities added as required.

This supports cross-jurisdiction work without assuming British terminology or administrative rules are universal.

---

# 17. Important licensing and evidence cautions

## Public is not open

A website can be readable without granting permission for systematic harvesting, republication or commercial redistribution.

Tattersalls is the clearest example in this sweep: public results and downloadable files exist, but current terms explicitly restrict automated harvesting/commercial use without permission.

## A consumer subscription is not a data licence

Buying Racing Post+, Timeform sectionals or a Betfair personal/research product does not automatically grant a right to redistribute the underlying data through an Inside Rails product.

## Derived findings and source data are different things

A licence may permit analysis while restricting reproduction of the underlying feed/content. Any publication workflow should distinguish:

- factual findings/calculations produced by Inside Rails;
- small illustrative source excerpts;
- redistribution of substantial protected source data.

The last category may require a different licence.

## Authority is domain-specific

The BHA is authoritative for British regulatory/racing-administration facts. It is not necessarily the authority for:

- exchange-market beliefs — Betfair is the direct evidence;
- weather — Met Office is stronger;
- company filings — Companies House is stronger;
- auction transaction records — the auction house is direct evidence;
- proprietary performance interpretation — Timeform/Racing Post are analytical sources, not governing authorities.

The correct source therefore depends on the claim being tested.

## Every source still needs semantic work

An official field name is not a semantic definition. Notebook 27 already demonstrated that apparently obvious racing fields can carry non-obvious meanings.

The same rule should apply across this landscape:

> **source → definition/grain/timing → evidence → analysis**

not:

> **field name → assumption → conclusion**.

---

# 18. Restricted or non-public information identified

Some useful information exists in the industry but is not presently a normal public research source.

Examples include:

- detailed underlying HBLB/major-bookmaker race-by-race turnover beyond published summaries;
- internal BHA integrity/race-shape investigative databases referenced in public material;
- participant-only racing-administration systems;
- full commercial live tracking coordinates where only public derived displays are available;
- protected live/media race pictures and video rights;
- commercial provider datasets where no public licence has been obtained.

These should not be treated as unavailable forever. They should simply be classified correctly: **not currently public evidence available to this project under the terms established here**.

---

# 19. Sources not yet exhaustively mapped

This report aims to cover the materially relevant source families for the current British-racing research programme. It does **not** claim that every horse-racing data vendor or national authority worldwide has been enumerated.

Areas that could be mapped later if a study requires them include:

- additional national authorities such as Australia, Hong Kong, Japan, USA/Canada and other European jurisdictions;
- racecourse-group proprietary information;
- specialist veterinary/equine datasets beyond HBLB-funded research;
- breeding databases and stud-book products in additional jurisdictions;
- bookmaker-specific historical prices outside Betfair;
- betting-exchange competitors;
- specialist tipping/model vendors;
- proprietary video/computer-vision providers;
- additional soil, hydrology and terrain datasets;
- further auction houses and private-sales data.

The threshold for adding one should be a research question that requires it, not completeness for its own sake.

---

# 20. Decision boundary

This report intentionally does **not** rank sources as “worth buying”, decide that Inside Rails should acquire a commercial feed, or prescribe a new database architecture.

It establishes the menu of evidence currently available.

For future studies the decision can therefore be made at study level:

1. What fact or relationship are we trying to establish?
2. Which source is authoritative/direct for that fact?
3. Is the required information public, open, consumer-paid or commercially licensed?
4. What exactly does the field/report/measurement mean?
5. What historical depth is required for this study?
6. What use/republication rights are required for the intended output?
7. Can the evidence be acquired reproducibly without building permanent database infrastructure?

That preserves the current Inside Rails research approach: **understand the evidence first, acquire only what the question requires, and govern permanently only when repeated use actually justifies it.**

---

# 21. Principal source links

### British official/industry

- BHA — https://www.britishhorseracing.com/
- HBLB — https://www.hblb.org.uk/
- HBLB Attendance — https://www.hblb.org.uk/attendance
- Weatherbys Racing — https://www.weatherbys.co.uk/racing
- Weatherbys Data Supply — https://www.weatherbys.co.uk/commercial/data-supply
- Racecourse Data Company — https://www.racecoursedatacompany.com/
- RDC 2026 Rate Card — https://www.racecoursedatacompany.com/wp-content/uploads/2025/12/RDC-Ratecard-2026.pdf
- RMG Race-Day Data — https://www.racecoursemediagroup.com/company-structure/rdd/

### Betting/economics

- Betfair Historical Data support — https://support.developer.betfair.com/hc/en-us/articles/360002407732-What-data-is-provided-by-the-Historical-Data-service
- Betfair Historical Data — https://historicdata.betfair.com/
- Gambling Commission Statistics — https://www.gamblingcommission.gov.uk/statistics-and-research

### Tracking/sectionals

- Racing TV RaceiQ — https://www.racingtv.com/raceiq
- Total Performance Data — https://www.totalperformancedata.com/

### Environment/geography

- Met Office HadUK-Grid — https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets
- Met Office climate data — https://www.metoffice.gov.uk/research/climate/maps-and-data/data
- Met Office DataHub — https://datahub.metoffice.gov.uk/
- UKCEH COSMOS-UK dataset — https://catalogue.ceh.ac.uk/documents/dde10e2b-ee1a-4b2b-a247-176db2f7bb31
- UKCEH COSMOS-UK near-real-time API — https://catalogue.ceh.ac.uk/id/e29d2d3b-8aaf-4b13-9577-5ca9b8215e73
- Ordnance Survey OpenData — https://www.ordnancesurvey.co.uk/products/open-data
- OS DataHub — https://osdatahub.os.uk/

### Corporate entities

- Companies House public register guidance — https://www.gov.uk/guidance/searching-the-companies-house-register
- Companies House developer/API — https://developer.company-information.service.gov.uk/

### Bloodstock/proprietary analysis

- Tattersalls — https://www.tattersalls.com/
- Timeform sectional archives — https://www.timeform.com/horse-racing/shop/sectional-times
- Timeform commercial products — https://www.timeform.com/commercial/products
- Racing Post — https://www.racingpost.com/
- SIS — https://www.sis.tv/

### International official sources

- IFHA — https://www.ifhaonline.org/
- IHRB — https://www.ihrb.ie/
- France Galop — https://www.france-galop.com/
