# Notebook 27 — BHA official public information feasibility

Source notebook: `notebooks/27_bha_official_source_feasibility.ipynb`

Report status: **public-information feasibility inventory; no Database v5 design or adoption decision**

## Executive conclusion

The BHA public web estate is substantially richer than a results website or a single racing API.

The investigation has demonstrated or confirmed five distinct layers of information:

1. **Structured race and fixture information** — fixtures, races, entries, nominations, results, going, officials and related race resources used by the BHA public frontend.
2. **Horse and participant information** — official ratings, rating history, horse profiles, performance histories, training history, jockeys, trainers, trainer non-runners, championships, owner championships and participant geography.
3. **Live operational and administrative information** — Stewards Reports, racing updates, non-runners, going/weather updates, annual fixture planning, claiming records, non-racing agreements, horse-name and racing-colour utilities.
4. **Statistical and population information** — annual and monthly Racing Data Packs, Horse Population Reports, Race Off-Times reporting and a separate interactive Industry Statistics application.
5. **Regulatory, technical and decision material** — Rules of Racing, General Instructions, handicapping appeals, disciplinary results, disqualified/excluded persons, racecourse standards, anti-doping, welfare and other public regulatory resources.

The most important overall finding is therefore not that the BHA has one promising replacement feed. It is that the BHA website sits on top of a **network of different official information systems with different grains, semantics, histories and publication mechanisms**.

Some of those sources contain information that cannot be reconstructed reliably from ordinary race results. Examples demonstrated during the study include:

- administrative Horses in Training populations;
- horse training history;
- official rating history;
- race-linked performance figures in some participant records;
- programmed rather than merely completed fixtures;
- watering and going-history observations;
- official racecourse-region definitions;
- claiming transactions;
- current non-racing agreements;
- Stewards incidents and veterinary notes;
- BHA-adjusted punctuality definitions;
- historical jockey-winner totals with an explicit electronic-data boundary;
- trainer location and yard information.

The investigation also demonstrated why none of these sources should be copied into a governed database on field names alone. Several apparently obvious fields have meanings that differ from a naive interpretation. Examples include a non-finisher `finishTime` that can equal the winner's time, performance rows carrying a horse's current rating rather than its historical race-date rating, `maxRunners` representing capacity rather than declarations, and BHA punctuality being calculated against a scheduled time that incorporates requested delays.

A single answer to **“how far back does the BHA data go?”** is therefore not appropriate. Historical depth varies by source family. The public evidence already ranges from modern live operational feeds to jockey-winner data explicitly bounded at 1 January 1995, fixture metadata observed back to the 1990s, annual statistics from 2015, Horse Population comparisons from 2017, and older ratings/classification and press-release archives. Historical depth should be measured **source by source once the user decides which information families matter**.

Several areas remain deliberately unresolved. The most important are the contents and backend of the separate Dashing Industry Statistics application, populated schemas for some race sub-resources such as `trans` and `balloted`, precise owner-championship temporal boundaries in the structured response, the complete public schema/history of claiming records, and source-specific historical limits for any information family selected for systematic acquisition.

This report therefore does **not** decide what Inside Rails should import, treat as validation only, or ignore. It presents the information landscape so that those decisions can be made separately.

---

## 1. Evidence standard used in this report

Three statuses are used throughout.

### Demonstrated

A representative source was actually inspected in Notebook 27 or its preceding controlled BHA reconciliation work. Fields, records, document contents or explicit definitions were observed directly.

### Site-confirmed

The current public BHA website clearly exposes the source family or utility, but Notebook 27 did not fully reverse-engineer its record schema or acquire a representative populated dataset.

### Unresolved

The public surface exists or a field/route was observed, but an important semantic, historical or technical question remains open.

These statuses describe the **strength of the evidence**, not the usefulness of the information.

---

## 2. Public-information landscape

| Information family | Delivery | Principal grain | Evidence status | Information demonstrated or confirmed |
|---|---|---:|---|---|
| Fixture search and fixture detail | BHA frontend + structured service | fixture | Demonstrated | dates, course/fixture identity, session/type and fixture-linked resources |
| Fixture going | structured service | fixture / track / observation time | Demonstrated | going conditions/history, GoingStick observations, weather, watering, tracks, race/timetable associations |
| Fixture officials | structured service | fixture / official role | Demonstrated | officials attached to the fixture |
| Races / race detail | structured service | race | Demonstrated | BHA race references and race metadata |
| Entries | structured service | race / entered horse | Demonstrated | pre-race horse records and entry-stage data |
| Nominations | structured service | race / nominated horse | Demonstrated; semantics partly unresolved | nomination-like records; equality with entries is not assumed |
| Results | structured service | race / runner | Demonstrated | result and runner information used by the BHA frontend |
| Balloted / `trans` race resources | structured service | unresolved | Route demonstrated; populated schema unresolved | tested requests returned valid empty responses |
| Stewards Reports | searchable BHA page + PDF | fixture / race / runner incident | Demonstrated | officials, going, rail, non-runners, withdrawals, jockey changes, enquiries, incidents, fines and veterinary notes |
| Racecourses directory | public interactive directory | racecourse | Site-confirmed | course type, handedness and location/next-fixture information exposed by the public directory |
| Racing Updates / HOY | embedded first-party live application | live fixture/race update | Site-confirmed; backend not fully mapped | live operational updates including going/weather/non-runner information were observed during the sweep |
| Official Ratings database | structured service + public exports | horse / current published rating | Demonstrated | Flat/AWT/Chase/Hurdle ratings, weekly changes, trainer and pedigree-linked information |
| Latest performance-figure export | signed public download | horse / recent performance sequence | Demonstrated | latest and previous assessed performance figures; export is not race-keyed |
| Ratings classifications | HTML/PDF resources | season / horse / category | Site-confirmed | Anglo-Irish Jumps and international/age classifications |
| Longines World’s Best Racehorse Rankings | public tables/archive | year / distance category / horse | Site-confirmed | historical top-rated performers by distance category |
| Horse database/profile | structured service | horse | Demonstrated | identity, DOB, pedigree, ownership/trainer information, career, ratings history |
| Horse performances | structured service | horse × race | Demonstrated | race references and performance records |
| Horse training history | structured service | horse × trainer period | Demonstrated | temporal trainer history |
| Jockey database/profile | structured service | jockey | Demonstrated | identity/licence, career and recent performance information |
| Jockey championships | structured service | jockey × championship | Demonstrated | wins/rides/strike-rate style championship measures with explicit periods for inspected data |
| Jockey Winners Totals | public table | jockey career aggregate | Site-confirmed | wins, runs and racing-today indicator since the explicit 1 January 1995 electronic-data boundary |
| Trainer database/profile | structured service | trainer | Demonstrated | licence, career, horses in training, location and championship information |
| Trainer performances | structured service | trainer × race performance | Demonstrated | race-linked performances including performance figure and creator on some records |
| Trainer non-runners | structured service | trainer × reporting period | Demonstrated | declarations, non-runners and rate for observed period |
| Trainers Map | embedded first-party map | trainer / location | Site-confirmed | exact location, contact details, yard size, performance information and licence type |
| Owner championships | structured service | owner × championship | Demonstrated | rank, leading earner, wins, runs and prize money |
| Full-year Fixture List | Excel/PDF | planned fixture | Demonstrated | Date, Weekday, Course, Time, CourseGroup, Region, Code, Surface and Type; Premier fixture subset |
| Annual Racing Data Packs | PDF | annual aggregate | Demonstrated | fixtures, races, administrative pipeline, value/prize measures, field size, runners, KPIs and policy measures |
| Monthly Racing Data Packs | PDF | YTD/current aggregate | Demonstrated | fixture/race volume, competitiveness, prize/value, horse-population headlines, punctuality and clashes |
| Horse Population Reports | PDF | administrative population / YTD runner aggregate | Demonstrated | Horses in Training, age, ratings, sex, breeding, regions, runners and frequency of runs with detailed definitions |
| Race Off-Times | PDF | national / racecourse / reason aggregate | Demonstrated | punctuality, median delay, late-race counts, course league table and late reasons |
| Industry Statistics / Dashing | embedded first-party application | unresolved dashboard | Site-confirmed; contents unresolved | distinct beta statistics application separate from the PDF statistics archive |
| Claiming races | searchable public page | claim transaction | Site-confirmed; full schema unresolved | claimed horses and claimants; public interface states a six-month claims window |
| Non-racing agreements | searchable public page | current horse/agreement | Site-confirmed | current horses subject to non-racing agreements |
| Horse-name availability | public interactive checker | proposed horse name | Site-confirmed | available/unavailable result and suggestions, subject to further registration checks |
| Racing Colours | interactive builder + marketplace | colour registration/right | Site-confirmed | standard availability/registration, bespoke colours and vintage-colours marketplace |
| Horses in Training Calculator | public rule utility | date calculation | Site-confirmed | rule-based eligibility timing utility linked from the Rules/Guides area |
| Vaccination Calculator | public rule utility | vaccination schedule | Site-confirmed | primary-course/booster timing utility linked from the Rules/Guides area |
| Rules of Racing / General Instructions | searchable microsite + documents | rule / instruction | Site-confirmed | Rules, historical Rules, BHAGIs and operational/regulatory guidance |
| Handicapping appeals | public page + published outcomes | horse / appeal | Site-confirmed | appeal process and published previous appeal outcomes |
| Disciplinary results | searchable archive/resources | case / hearing | Site-confirmed | hearing results, reasons, appeals and historical disciplinary notices |
| Disqualified / Excluded persons | searchable current list | person / status | Site-confirmed | current disqualification/exclusion status and reason/type |
| Anti-doping, welfare and veterinary material | pages/resources | rule / guidance / report | Site-confirmed at family level | anti-doping rules, testing/prohibited-substance guidance and welfare/veterinary publications |
| Racecourse licensing / technical material | General Instructions + resources | racecourse / technical requirement | Site-confirmed at family level | racecourse standards, starts, medical/veterinary operations and other technical material |
| Point-to-Point / Purebred Arabian regulation | pages/resources | regulatory programme | Site-confirmed at family level | separate regulatory/reference material linked through the BHA site |
| BHA Search / Resource / News archives | public search/archive | document/content item | Site-confirmed | pages, downloadable resources, press releases, disciplinary notices, posts and racing-related search surfaces |

The table is deliberately broader than “things that look like database columns”. It records the public information landscape first. Selection comes later.

---

## 3. Structured fixture and race information

### 3.1 Public frontend and structured service

The BHA results and racecard interfaces are data-driven. The study observed the service root:

`https://api09.horseracing.software/bha/v1`

The service is used by the public BHA frontend. That observation does **not** establish that it is a formally documented public API contract or guarantee endpoint stability.

The active route families demonstrated during the study were:

- `/fixtures`
- `/fixtures/{fixtureYear}/{fixtureId}`
- `/fixtures/{fixtureYear}/{fixtureId}/going`
- `/fixtures/{fixtureYear}/{fixtureId}/officials`
- `/fixtures/{fixtureYear}/{fixtureId}/races`
- `/races/{yearOfRace}/{raceId}/{divisionSequence}`
- race `balloted`
- race `entries`
- race `nominations`
- race `results`
- race `trans`

This is materially more than a results endpoint. It exposes different stages and aspects of a race occurrence.

A previous controlled pilot used BHA results for five GB fixtures on 27 May 2026 and reconciled **34 BHA races to 34 Database v4 GB races**. That established enough current-result suitability to justify the broader feasibility study, but it was a pilot rather than proof of complete historical coverage.

### 3.2 Identity observations

The study found that BHA identifiers must be treated carefully:

- `fixtureId` was not assumed globally unique across years;
- `raceId` can be reused;
- the observed BHA race reference `yearOfRace + raceId + divisionSequence` behaved as a useful external provenance reference in the inspected sample;
- it was **not** adopted as Inside Rails' governed race identity.

The existing Inside Rails race-occurrence identity remained separate from BHA provenance during this feasibility work.

### 3.3 Result and entry semantic traps

Several fields cannot safely be interpreted from their names alone.

#### `finishTime`

A non-finisher can carry the winner's time in the result response. It is therefore not universally the time at which that horse completed the race.

#### Weight at the entry stage

Weight-like fields on an entry record were not proven to be the final carried weight. Entry-stage and result-stage meanings must remain separate unless demonstrated.

#### `maxRunners`

This is a capacity/maximum-runners concept, not the number of declarations.

#### Nominations versus entries

On a completed-race sample, nomination records could look similar to entry records. That visual equality is not evidence that BHA uses the two resources as semantic synonyms throughout the race lifecycle.

#### `balloted` and `trans`

Both routes returned successful but empty responses in bounded testing. Their existence is demonstrated; the schema and population rules of a populated response are not.

### 3.4 Results-availability query behaviour

During an earlier January-to-May fixture acquisition test, some returned fixtures did not satisfy the expected `resultsAvailable = true` interpretation even when the query was designed around results availability. That behaviour remains unresolved and is another reason not to treat query labels as a governed semantic contract without testing.

---

## 4. Fixture going, weather, watering and operational state

The fixture-going resource is not merely a single current-going string.

A representative Newton Abbot fixture exposed information spanning:

- current/recorded conditions;
- condition history;
- weather;
- watering;
- tracks;
- race associations;
- timetable material;
- GoingStick observations.

The sample contained a sequence of condition observations across several days before racing and a watering timeline. This establishes a potentially valuable temporal operational source for questions where the state of the course **before** raceday matters.

Important cautions:

- a null reading at one observation does not prove there was no earlier reading;
- similar or repeated snapshots can occur;
- numeric timetable meanings were not fully governed during this study;
- the relationship between a fixture-level observation and a particular race/track must be preserved rather than flattened blindly.

This source is directly relevant to any later study comparing official going with weather or course-management activity, but Notebook 27 did not make that research decision.

---

## 5. Stewards Reports

The BHA provides a public Stewards Reports search and also links reports from the results area:

https://www.britishhorseracing.com/racing/stewards-reports/

A representative report was downloaded and proved machine-readable as PDF text.

Observed content included:

- officials;
- going;
- rail information;
- non-runners;
- withdrawals;
- jockey changes;
- race-by-race Stewards sections;
- incidents;
- fines;
- veterinary information and notes.

The public search surface also distinguishes material such as Stewards enquiries/reports, runner notes, fixture notes and non-race-related incidents.

One important provenance trap was demonstrated: an old report could display a “Published” date corresponding to current retrieval/generation rather than the original historical publication date. That displayed value must not be used naively as the event-publication timestamp.

A bounded search did not establish a separate structured Stewards backend suitable for direct ingestion. PDF remains the demonstrated public format.

Historical scope is not yet governed. The current public page describes an archive and the site indexes older Stewards material, but systematic boundary testing was not required for the current feasibility question.

---

## 6. Racing Updates / live operational information

The BHA's top-level **Racing updates** page embeds a distinct first-party application rather than an ordinary article page:

- BHA entry point: https://www.britishhorseracing.com/racing-updates/
- observed embedded application: `https://crate.horseracing.software/hoy/`

The site-wide sweep established this as a live operational information family separate from the fixture API and Stewards PDFs.

Observed/indexed update material included categories such as:

- going updates;
- weather information;
- non-runner updates;
- timestamps and fixture/race references;
- GoingStick information;
- some soil-moisture observations;
- non-runner cloth/stall information and a stated withdrawal reason in observed material.

The application also exposes update filtering and automatic-update behaviour. It states that fixture dates and race times are presented in GB / Europe-London time, while other displayed times may be local to the viewer.

The complete backend schema and historical retention policy were not mapped. This should therefore be treated as a confirmed **live operational source family**, not as a fully specified acquisition feed.

---

## 7. Official Ratings and performance figures

### 7.1 Ratings database

The public BHA Ratings database states that it contains published handicap ratings for horses running in Britain, updated weekly on Tuesday morning:

https://www.britishhorseracing.com/regulation/official-ratings/ratings-database/

The study demonstrated a structured ratings resource and fields including:

- horse identity/name;
- year of foaling;
- sex;
- trainer and trainer ID;
- Flat rating;
- AWT rating;
- Chase rating;
- Hurdle rating;
- rating differences/new-rating indicators;
- collateral-related information;
- pedigree-linked fields;
- last-update information.

A bounded response contained 11,840 records at the time of testing. That count should **not** be silently relabelled “all active British horses”; the exact population definition must follow the BHA source semantics.

The public interface also offers exports for:

- the full ratings list;
- weekly rating changes;
- latest performance figures.

### 7.2 Performance-figure export

The latest-performance-figures download was obtainable via a signed URL discovered from the public ratings surface.

Observed export columns included:

- Racehorse;
- YOF;
- Sex;
- Trainer;
- Latest;
- two through six runs ago.

BHA describes a performance figure as an assessment of the level achieved in an individual race.

However, this particular export is a **recent-performance sequence**, not a race-keyed historical table: it did not expose a race ID or race date for each figure. Symbols/values including `x` and `0` remained unresolved during the bounded investigation.

Signed URL values are ephemeral access material and should not be persisted as governed data.

### 7.3 Race-linked performance figures elsewhere

A separate trainer-performance resource demonstrated that some participant performance rows contain:

- `performanceFigure`;
- `performanceFigureCreatedBy`;
- race references and other race metadata.

This is important because it shows that race-linked performance-figure information exists somewhere in the BHA public-data estate even though the ratings-page export itself is not race-keyed.

Population/completeness rules for those trainer-performance figures remain unresolved.

### 7.4 Ratings classifications and historical rankings

The BHA also exposes official classification material separate from the current ratings database:

https://www.britishhorseracing.com/regulation/official-ratings/ratings-classifications/

The current page includes historical Anglo-Irish Jumps classifications and European two-year-old classifications, while the Longines page provides historical top performers by distance category from 2005 onwards:

https://www.britishhorseracing.com/regulation/official-ratings/longines-worlds-best-racehorse-rankings/

These are separate historical/classification products and should not be conflated with a horse's current weekly handicap rating.

---

## 8. Horse database and temporal horse information

The BHA horse search describes itself as a database for breeding, performance information and statistics:

https://www.britishhorseracing.com/racing/horses/

The study demonstrated public structured routes for:

- horse search;
- horse profile;
- performances;
- training history.

A representative profile exposed information including:

- horse identity;
- date/year information;
- sex;
- sire/dam and lineage IDs;
- trainer;
- owner information/type;
- career information;
- official-rating history.

The performance resource contained race references and performance attributes. The training-history route provides genuinely temporal trainer information rather than merely the current trainer.

### Critical rating-history trap

Historical horse-performance rows in the inspected example displayed the horse's **current Flat rating** even for races that occurred before that rating had been published according to the separate rating history.

Therefore a rating field embedded in a historical performance row cannot automatically be treated as the horse's official rating on the race date.

The rating-history resource, race conditions and performance-row rating fields must remain semantically distinct until proven otherwise.

The horse performance endpoint did not expose the same performance-figure field demonstrated in trainer performance records during the bounded sample.

---

## 9. Jockey information

The BHA jockey surface provides current licensed-jockey search, championship data, career information and links to Stewards/appeal material:

https://www.britishhorseracing.com/racing/participants/jockeys/

The study demonstrated information including:

- identity;
- date of birth/age-type fields;
- licence information;
- lowest riding weight;
- days since last win;
- career wins/rides;
- strike rate;
- Group/Listed measures;
- prize-related measures;
- recent performances.

### Championship periods

The inspected Flat championship data had an explicit 2026 championship period rather than representing a calendar-year or career total. The public jockey page likewise states that the Flat championship runs from the 2000 Guineas to British Champions Day, while Jump/Conditional jockey championships run April-to-April.

Championship aggregates therefore require their championship calendar; they are not generic career fields.

### Jockey Winners Totals

The site-wide sweep identified a distinct public table:

https://www.britishhorseracing.com/racing/jockeys-winners-totals/

The BHA explicitly defines this as the number of **British winners ridden by British-licensed jockeys since 1 January 1995**.

Displayed fields are:

- Jockey Name;
- Wins;
- Runs;
- Racing Today.

The page states that accurate electronic winner data before 1995 is not available. Jockeys who rode before that date are marked with an asterisk and only their winners from 1 January 1995 are counted.

This is one of the clearest demonstrated historical-data boundaries on the BHA website. It is a boundary of the electronic winner series, not necessarily the start of a jockey's career.

---

## 10. Trainer information

The BHA trainer surface states that users can search for contact details and performance information and provides both a trainer database and a map:

https://www.britishhorseracing.com/racing/participants/trainers/

### 10.1 Trainer profile and championships

The structured trainer work demonstrated information including:

- trainer identity;
- licence type;
- training-since information;
- horses in training;
- county/location-related information;
- career totals;
- Flat and Jump championship material.

The public page provides an important championship semantic:

- Flat trainer championship: prize-money basis, January to December;
- Jump trainer championship: prize-money basis, April to April.

It also notes a post-2018 interpretation of `Prizes`, including placed horses and appearance-money recipients. This is another example of a measure whose definition changes over time.

### 10.2 Trainer performances

A representative trainer-performance endpoint returned race-linked records containing information such as:

- race references;
- animal/jockey/trainer IDs;
- ratings fields;
- betting ratio;
- course;
- performance figure;
- performance-figure creator;
- prize;
- race metadata;
- result;
- weight.

The inspected trainer had a profile `careerRunners` figure of 1,821 while the performance endpoint reported 1,802 records. That mismatch remains unresolved and should be preserved rather than forced into equality.

### 10.3 Trainer non-runners

The BHA exposes trainer non-runner reporting as a distinct public surface/resource.

A bounded structured sample for one trainer and one reporting window demonstrated:

- reporting start/end dates;
- declarations;
- non-runners;
- non-runner rate.

The observed example had 325 declarations and 18 non-runners in its stated period. It was one sample and does not establish the universal historical or aggregation rules of the service.

### 10.4 Trainers Map

A separate map is publicly exposed:

https://www.britishhorseracing.com/racing/participants/trainers/trainers-map/

The BHA describes it as providing, for **every registered trainer in Britain**:

- exact location;
- contact details;
- yard size;
- performance information;
- licence type.

It also defines the displayed licence categories as Flat, Jump and Combined.

This makes participant geography a distinct public information source rather than something that must be inferred from race appearances.

---

## 11. Owner information

The BHA's public owner racing surface is currently an **Owners Championship**, not an analogous full owner-profile database:

https://www.britishhorseracing.com/racing/participants/owners/

The study demonstrated a structured championship resource for Flat and Jump owners.

Observed fields included:

- championship type;
- owner ID;
- owner name;
- rank;
- leading earner horse;
- wins;
- runs;
- prize money.

The public page supplies championship timing semantics that were not present in the inspected structured rows:

- Flat Owners Championship begins at the QIPCO Guineas Festival and ends in October;
- Jump Owners Championship runs through the jumps season from April to Sandown's Bet365 Gold Cup day.

This is important because the API rows should not be interpreted without the page-level championship period.

No analogous public owner search/profile/performance API was demonstrated in the bounded frontend investigation.

---

## 12. Full-year Fixture List and planned racing programme

The public Full Year area is:

https://www.britishhorseracing.com/racing/fixtures/full-year/

The 2026 source exposed:

- Fixture List Excel;
- Fixture List PDF;
- Premier Racedays.

The Excel workbook was inspected directly without installing a new dependency.

### Main list

The main 2026 sheet contained 1,458 planned fixtures from 1 January to 31 December 2026 and fields:

- Date;
- Weekday;
- Course;
- Time;
- CourseGroup;
- Region;
- Code;
- Surface;
- Type.

Observed categories included:

- session/time: Afternoon, Evening, Floodlit;
- course group: ARC, Chester Race Company, Independent, Jockey Club;
- region: North, Midlands, South;
- code: Flat, Jump, Both;
- surface: Turf, AWT;
- type: National/BHA, National/BHA Floodlit, Racecourse/Normal.

The workbook also contained:

- a grid view;
- a Premier Fixture List;
- historical Fixture Numbers.

The Premier sheet contained 52 fixtures and was an exact unique Date+Course subset of the main list in the inspected workbook.

The Fixture Numbers sheet provided annual comparisons from 2018 through 2026.

### Planning versus execution

This workbook is an official **planning/classification source**. Future fixtures in it are not evidence that racing actually occurred.

The BHA's own Race Planning material distinguishes Racecourse Fixtures and BHA Fixtures and describes the fixture-allocation process. That provides context for the workbook's `Type` family, but the exact mapping of every workbook label should remain separately governed.

### Region definition

A particularly useful semantic was later supplied by the Horse Population Report, which states that its training regions use the same regional scheme as the Fixture List:

- North: latitude greater than `53.42911`;
- South: latitude less than `51.88002`;
- Midlands: between those boundaries.

This proves that `Region` is an explicit BHA administrative geography, not an informal interpretation of English regions.

---

## 13. Annual Racing Data Packs

The BHA Racing Statistics archive is:

https://www.britishhorseracing.com/regulation/reports-and-statistics/racing-statistics/

The inspected representative annual source was the **2025 Annual Racing Data Pack**, a seven-page report comparing 2021–2025.

### Information demonstrated

The annual pack covers:

- fixtures programmed;
- fixtures run;
- abandonments/additions;
- races run;
- entries;
- declarations;
- eliminations;
- non-runners;
- prize/race-value material;
- average field size;
- total runners;
- individual runners;
- average runs per horse;
- race-card-size measures;
- small-field/larger-field KPIs;
- competitiveness measures;
- selected policy/innovation measures.

### Important reporting rules

The report distinguishes **Fixtures Programmed** from **Fixtures Ran**.

It also states that **Mixed fixtures are recategorised as Flat** for this reporting. Reproducing a BHA headline therefore requires reproducing its classification rule rather than merely counting rows that appear similar.

Observed 2025 race totals included 10,127 races across the pack's Flat Turf, Flat AWT, Chase, Hurdle, NHF and Hunter categories.

The report separately distinguishes **Total Runners** from **Individual Runners**, so runner appearances and unique horses must not be conflated.

### Grain

The annual pack is an aggregate statistical/reporting product. It does not replace individual fixture/race/runner records.

### Public history

The current archive exposes labelled full-year Racing Data Packs for **2015–2025**.

Older years appearing in WordPress upload-path metadata should not be treated as evidence of an older labelled annual pack unless a corresponding product is actually demonstrated.

---

## 14. Monthly Racing Data Packs

The inspected representative monthly source was **May 2026**.

The four-page pack contains YTD/current measures including:

- programmed, abandoned, added and run fixtures;
- race volume;
- average field size;
- 8+ runner measures;
- favourite/competitiveness measures;
- total prize money paid out;
- handicap race values;
- Horses in Training headline measures;
- punctuality;
- race clashes/race-time operational measures.

The monthly pack is therefore not simply an annual pack divided by month. It adds current/YTD operational measures.

### Horse-population snapshot difference

The monthly pack explicitly states that its Horses in Training comparison is taken as a **snapshot on 31 May of each year**.

That differs from the dedicated Horse Population Report's normal 15th-of-month snapshot convention.

The initial PDF text extraction surfaced candidate 2026 values, but the table extraction was not sufficiently aligned to govern those numbers as a coherent row. The timing definition is established; the extracted row remains provisional.

### Punctuality relationship

The monthly pack reports a percentage of GB races within 120 seconds of scheduled time including requested delays. The dedicated Off-Times product provides the more explicit definition discussed below.

---

## 15. Horse Population Reports

The dedicated Horse Population Reports are one of the richest public administrative-statistics sources identified in the study.

The inspected source was the report updated **31 May 2026**, containing 27 pages.

### 15.1 Administrative source basis

The report states that Horses in Training information uses returns from the **Weatherbys Racing Administration System**, completed by trainers and updated when horses enter or leave their care as a condition of licence.

This population is therefore not equivalent to “horses that appeared in our race results”.

### 15.2 Snapshot and YTD timing

Unless otherwise stated:

- Horses in Training snapshots use the **15th day of the month**;
- YTD figures run through the date on the front of the report.

This is why the dedicated May report should not automatically reconcile to the monthly Racing Data Pack's separate 31 May snapshot.

### 15.3 Ratings and temporal semantics

The report states that ratings use the most recently published BHA Handicapping Team ratings available for the relevant snapshot, with ratings published weekly.

It also defines temporal treatment of gender and training-type changes. These rules matter when attempting historical population reconstruction.

### 15.4 Inclusion and recoding rules

The report contains explicit population rules, including age/training-type treatment and Hunter Chaser exclusions.

Examples demonstrated include:

- yearlings are not part of headline Flat/Dual totals unless separately shown;
- young horses are excluded from headline Jump/Hunter populations according to stated age rules;
- very young Dual horses can be recoded as Flat for the population presentation;
- Hunter Chasers are excluded from the main Jump and overall figures unless shown separately;
- horses temporarily racing abroad for GB trainers at the reporting time are excluded from the relevant snapshot.

### 15.5 Runner definitions

The report distinguishes:

- **Total Runners** — runner appearances;
- **Individual Runners** — each horse counted once.

Unless otherwise specified, its runner measures include horses that ran in GB races, including voided races, and exclude withdrawals. Hunter Chases have separate treatment.

### 15.6 Dimensions available

Across the 27 pages, the report provides information by:

- training type;
- age;
- rating band;
- gender;
- breeding country;
- training region;
- home nation;
- total runners;
- individual runners;
- country trained;
- GB-trained runners abroad;
- frequency of runs;
- young horses entering training.

The **young horses entering training** material is a clear example of information that cannot be inferred safely from race appearances alone.

### 15.7 Region definition

The report explicitly defines the same North/Midlands/South geography used for the Fixture List:

- North: north of latitude `53.42911`;
- South: south of latitude `51.88002`;
- Midlands: between.

Training centres are separately defined using postcodes/surrounding areas.

### 15.8 Observed history

The public report archive currently exposes monthly Horse Population Reports from 2020 onward, while the inspected report itself contains comparison series extending back to 2017 for some measures.

That distinction matters: downloadable report history and the historical time series inside a report are different concepts.

---

## 16. Race Off-Times

The dedicated Race Off-Times product is also exposed through the Racing Statistics page.

The inspected representative report covered **1 April 2025 to 31 March 2026**.

It is an aggregate/course-level operational report, not a race-level off-time feed.

### 16.1 BHA punctuality definition

The report defines a race as on time for the punctuality measure when it starts within **120 seconds** of the Scheduled Time.

Crucially, that Scheduled Time takes account of **BHA Racing Department Requested Delays**.

Therefore:

`actual off time - originally advertised time`

is not guaranteed to reproduce the BHA punctuality statistic.

### 16.2 Information displayed

For the inspected reporting period the headline measures included:

- punctuality: **82.4%**;
- median race delay: **0:45**;
- late races: **1,779**.

The report also provides a racecourse league table with fields such as:

- Course;
- Races;
- Late Races;
- Punctuality;
- Median Race Delay;
- Most Common Reason.

Observed late-reason categories included examples such as:

- Late to post;
- Loading/Starting Issues;
- Unruly/Loose horse;
- Avoiding Clash;
- Track Issue;
- Ambulance Issue;
- Equipment/Shoeing;
- television/broadcast-related reasons;
- Other.

### 16.3 What it does not expose

The inspected PDF did not demonstrate individual rows containing:

- BHA race ID;
- race date;
- original scheduled time;
- adjusted scheduled time;
- actual off-time;
- individual delay seconds;
- individual requested-delay duration;
- individual late reason.

Its demonstrated grains are national aggregate, racecourse aggregate and late-reason aggregate.

### 16.4 Public history

The current Racing Statistics page exposes several rolling and full-year Race Off-Times PDFs covering reporting periods across 2024–2026.

---

## 17. Industry Statistics / Dashing

The BHA navigation includes a separate **Industry statistics** application in addition to the PDF Racing Statistics archive.

BHA entry point:

https://www.britishhorseracing.com/industry-statistics/

Observed embedded application:

`https://dashing.horseracing.software/`

The application identified itself as a BHA statistics product and displayed a **beta** warning indicating that bugs or data issues could render information incorrect.

The available web tooling exposed the application shell but did not recover the dashboard's measures or underlying data calls sufficiently to document them.

The correct conclusion is therefore:

- a distinct interactive official statistics product is publicly exposed;
- its detailed contents remain **unresolved** in this study;
- absence of extracted dashboard values is not evidence that the dashboard contains no useful information.

No local-user probe is required merely to close this report; the unresolved status is retained explicitly.

---

## 18. Claiming races

The BHA ownership section contains a public **Claiming races** search:

https://www.britishhorseracing.com/regulation/ownership/claiming-races/

The BHA describes the service as a way to search for **claimed horses and who they have been claimed by**.

### Public semantics

The page explains that:

- all horses in a Claiming Race may be claimed at a value set by the trainer when making the entry;
- in a Selling Race, horses other than the winner may be claimed, while the winner is auctioned on the racecourse;
- the Rules restrict participation in multiple/conflicting claims;
- a successful unfriendly claim can create a six-month running restriction in the circumstances described by the BHA.

### Public window and grain

The inspected interface stated **Last 6 months of Claims**.

This establishes the public search window, not the BHA's internal retention period.

The page/template evidence indicates a transaction linked to a horse, race/course/date/time and claimant. The full populated structured schema was not recovered during this sweep.

Unresolved details include:

- whether claim value is exposed in the public response;
- friendly/unfriendly representation;
- stable horse/claimant identifiers;
- unsuccessful claimant representation;
- history beyond the six-month public window.

---

## 19. Non-racing agreements

The BHA publishes a searchable current list:

https://www.britishhorseracing.com/regulation/ownership/non-racing-agreements/

The page states that the chart lists **all horses which are currently subject to non-racing agreements**.

This is important temporal language. It describes current state, not a demonstrated historical agreement ledger.

The ownership guidance explains that a non-racing agreement concerns a retired horse transferred subject to a condition that it will not race again, with the BHA preventing entries under the Rules subject to the agreement's terms.

Observed page/template material includes horse and owner-role/start-date information, while the precise historic/end-date schema was not fully probed.

A horse disappearing from the current list would therefore not establish that no agreement had previously existed.

---

## 20. Horse-name availability

The BHA exposes a public checker:

https://www.britishhorseracing.com/regulation/ownership/horse-name-availability/

It can return:

- available;
- unavailable;
- suggested alternatives.

The BHA explicitly qualifies `available`: it means the name is not currently registered to another horse or protected because of a previous horse's performances, but the proposed name remains subject to further registration checks.

This utility is therefore a **name-candidate availability service**, not a horse-identity record and not proof that a name will be accepted.

---

## 21. Racing Colours

The BHA exposes three distinct public mechanisms through:

https://www.britishhorseracing.com/regulation/ownership/racing-colours/

### Standard Colours

An interactive tool allows users to choose colours/designs, check availability and register a standard set.

### Bespoke Colours

Custom designs can be proposed outside the usual standard-design restrictions, subject to the BHA application process.

### Vintage Colours

The page operates a public marketplace for the right to register existing colour designs, including descriptions and asking prices.

This is both an ownership-administration utility and a live public availability/marketplace surface.

---

## 22. Rule calculators and eligibility utilities

The Rules and Guides area links public calculators including:

- **Vaccination Calculator**;
- **Horses in Training Calculator**.

Source hub:

https://www.britishhorseracing.com/regulation/rules-guides/

These should be treated as rule/eligibility utilities rather than ordinary reference articles.

### Horses in Training Calculator

The site-wide inspection established that the utility applies the relevant **14-clear-day** timing rule and can calculate eligibility timing in either direction — from an arrival/in-training date to a first eligible race date, or from a proposed race date to the relevant latest qualifying date.

### Vaccination Calculator

The utility operationalises primary-course/booster timing rules. The surrounding BHA material documents the vaccination-interval changes introduced from 2022 and subsequent compliance requirements.

These calculators are useful evidence of **implemented rule logic** on the official site, but any database implementation would still need the governing Rule text and effective-date provenance rather than copying calculator output blindly.

---

## 23. Racecourse directory and technical information

The BHA public racing navigation includes a Racecourses directory:

https://www.britishhorseracing.com/racing/racecourses/

The site-wide sweep identified public attributes including:

- fixture type such as Flat/Jump/Mixed;
- handedness;
- distance from a supplied location;
- next-fixture information;
- first-race time.

The public renderer experienced an error during part of the sweep, so its underlying structured schema was not governed.

### Technical / licensing corpus

Racecourse information also exists in a different form in the BHA General Instructions and downloadable resources.

The Rules and Guides hub exposes General Instructions covering, among other things:

- race planning;
- the racecourse;
- integrity services;
- appointment of Stewards and Clerks of the Course;
- stabling/canteen/accommodation;
- raceday operational areas;
- starting arrangements;
- medical services;
- veterinary services.

The BHA Resource/Search archive also exposes racecourse-licensing guidance and historical technical documents.

This means racecourse “data” is not confined to a directory row: important course semantics and operating requirements live in the regulatory/technical corpus.

### GoingStick / TurfTrax history

Earlier bounded work also demonstrated a public GoingStick historical archive linked from the BHA/racecourse information environment. A Newton Abbot sample contained repeated observations across 2017–2026 with intraday readings and contextual weather/watering/going comments.

TurfTrax is a separately hosted service rather than evidence that every GoingStick observation is a BHA-owned dataset. The provenance relationship should be retained.

---

## 24. Rules of Racing and General Instructions

The BHA's Rules and Guides page is a major public reference corpus:

https://www.britishhorseracing.com/regulation/rules-guides/

It exposes:

- the current Rules of Racing microsite;
- Rules that were in effect until 31 August 2019;
- Equine Anti-Doping Rules and penalty material;
- the indexed BHA General Instructions;
- ownership manuals/guidelines;
- bloodstock guidance;
- commercial-arrangement guidance;
- sponsorship codes;
- weight-for-age scales;
- Point-to-Point regulations;
- health/safety and operational guidance;
- rule calculators.

For Inside Rails research this is an important distinction:

> a structured BHA field can tell us **what value the system returned**, while the Rules/General Instructions may be required to establish **what that value legally or operationally means**.

The reference corpus should therefore be treated as a semantic/effective-date source family in its own right.

---

## 25. Handicapping appeals

The BHA publishes the handicapping review/appeal process and previous outcomes:

https://www.britishhorseracing.com/regulation/handicapping-appeals/

The page describes a staged review process:

1. trainer raises the matter with the responsible handicapper;
2. trainer may escalate to the Head of Handicapping;
3. an appeal can then be launched for independent consideration by the handicapping ombudsman/deputy.

The page also publishes previous appeal results by horse/date, with a visible series extending through multiple years.

This source can therefore provide:

- examples of disputed rating decisions;
- reasoning/outcomes where published;
- evidence about how the BHA's rating process is reviewed.

It is a decision-document family, not a substitute for the current ratings database.

---

## 26. Disciplinary results and decisions

The BHA maintains a public disciplinary-results surface:

https://www.britishhorseracing.com/news-media/disciplinary-results/

The page points users to recent Disciplinary Notices and a fuller archive in the Resource Centre. The BHA site search also treats **Disciplinary Notices** as a distinct result family.

The archive contains material including:

- enquiry results;
- Disciplinary Panel reasons;
- appeal findings/reasons;
- participant/racecourse cases;
- dates and published outcomes.

This is potentially a rich historical regulatory corpus, but Notebook 27 did not attempt to convert the case archive into a structured case database.

Its value here is to establish that official public decision history exists and can be separately investigated where a research question requires it.

---

## 27. Disqualified and Excluded persons

The BHA publishes a current searchable list:

https://www.britishhorseracing.com/disqualified-excluded-persons/

The page states that anyone **currently** disqualified or excluded can be viewed and can be searched by person or reason/type.

It distinguishes routes into the list including:

- debt/arrears / Forfeit List;
- Disciplinary Panel decisions;
- independent Disciplinary Officer exclusion orders.

The page also links the relevant Rules and disciplinary decisions.

Again, `currently` matters: this is a current-status source unless a separate historical series is established.

---

## 28. Anti-doping, welfare, veterinary and participant material

The BHA regulation/navigation estate exposes substantial public reference material beyond race results, including:

- Equine Anti-Doping Rules;
- prohibited-substance/testing information;
- veterinary and vaccination guidance;
- horse-welfare information and research/publications;
- participant medical, mental-health and concussion material;
- training/development resources.

The current study confirmed these as public source families but did not attempt to inventory every document within them.

A useful boundary emerged during the wider sweep: the BHA may describe internal integrity, race-shape, veterinary/medical or research databases in public material, but a reference to an **internal database is not evidence that the database itself is publicly obtainable**.

The public audit should therefore distinguish:

- public reports/guidance/statistics;
- public search systems;
- internal systems merely mentioned by the BHA.

---

## 29. Point-to-Point, Purebred Arabian and adjacent regulatory areas

The regulation navigation includes dedicated BHA material for:

- Point-to-Point racing;
- Purebred Arabian horseracing;
- sponsorship;
- shared ownership;
- licensing and participant administration.

The Point-to-Point page, for example, provides current eligibility/regulatory information and links to season-specific material.

These areas were **confirmed as public reference/source families** but were not field-mapped to the same depth as the core GB race/participant data during Notebook 27.

Their inclusion in this report prevents them from disappearing merely because they are not immediate Database v4 enrichment candidates.

---

## 30. BHA Search, Resource Centre, press releases and publications

The BHA site search is itself an important discovery surface.

It separates categories including:

- Pages;
- Resources;
- Press Releases;
- Disciplinary Notices;
- Posts;
- racing-related search results.

This matters because many BHA datasets and technical documents are not represented by a permanent top-navigation item. They can instead appear as downloadable resources, historic notices or publications.

The press-release archive also extends well before the formation of the current BHA, including British Horseracing Board / Jockey Club-era material. That makes it a potentially useful historical evidence corpus for changes in rules, ratings publication, fixtures and regulation.

The unit of this feasibility audit is the **source family**, not every individual article or PDF. A complete copy of thousands of press releases is neither necessary nor equivalent to understanding which information systems exist.

---

## 31. Consolidated semantic findings that must not be lost

The following findings are especially important because they can cause silent analytical errors.

### Planned fixture is not executed fixture

The Full-Year Fixture List is programme/planning evidence. Results and run-fixture statistics are execution evidence.

### Programmed fixture is not fixture ran

The annual statistics explicitly distinguish these populations.

### Mixed fixtures can be recategorised for reporting

The annual Data Pack states that Mixed fixtures are recategorised as Flat for its reporting.

### `maxRunners` is not declarations

It represents maximum/capacity, not the observed declaration count.

### Entry weight is not proven final carried weight

Race-lifecycle stage matters.

### Non-finisher `finishTime` is not necessarily the horse's finish time

A DNF can carry the winner's time.

### Current rating can appear on an old performance row

Historical horse performance rows cannot be assumed to contain the race-date official rating.

### Performance figure and official rating are different concepts

The ratings-page performance-figure export represents assessed performance levels; current handicap rating is another field/system.

### The latest performance-figure export is not race-keyed

The trainer-performance source may provide race-linked figures, but its coverage/population still needs testing.

### Championship totals require championship periods

Jockey, trainer and owner championships use code-specific periods, not one universal calendar.

### Horses in Training is an administrative population

It comes from trainer-maintained Racing Administration returns, not a count of horses that happened to race.

### Monthly and dedicated Horse Population snapshots can differ legitimately

The monthly pack's May comparison uses 31 May; the dedicated population report normally uses a 15th-of-month snapshot unless otherwise stated.

### Total Runners and Individual Runners are different measures

One counts appearances; the other unique horses under the report's rules.

### Hunter and young-horse inclusion rules matter

The Horse Population Report has explicit age/type exclusions and recoding rules.

### BHA region is a defined latitude classification

North/Midlands/South is not an informal label.

### BHA punctuality is not simply advertised time versus actual off

The scheduled time used for the 120-second rule incorporates requested delays.

### Stewards PDF publication display can be dynamic

A displayed “Published” date is not automatically the original event/report publication date.

### Non-racing agreements page is current-state

Current absence does not establish historical absence.

### Jockey winner totals have an explicit 1 January 1995 electronic-data boundary

That is a source boundary, not necessarily a career boundary.

### Public frontend service is not automatically a documented API contract

Observed endpoints must retain provenance and change risk.

---

## 32. Historical depth demonstrated so far

There is no single BHA history boundary.

| Source family | Historical evidence demonstrated in this study |
|---|---|
| Fixture/race service | fixture metadata observed into the 1990s; older detailed resources behaved inconsistently, so no governed full-detail boundary yet |
| Jockey Winners Totals | explicit electronic-data boundary of 1 January 1995 |
| Full-Year Fixture workbook | 2026 workbook; embedded Fixture Numbers comparison 2018–2026; older fixture details available separately on request according to BHA page |
| Annual Racing Data Packs | public labelled packs 2015–2025 |
| Monthly Racing Data Packs | extensive archive across multiple years; current page includes series reaching at least into the 2010s |
| Horse Population Reports | downloadable reports from 2020; internal comparison series observed back to 2017 |
| GoingStick sample | Newton Abbot observations demonstrated across 2017–2026 |
| Race Off-Times | public reports covering periods across 2024–2026 |
| Claiming search | public interface explicitly states last six months |
| Ratings classifications | historical classification resources across many seasons; Longines summary from 2005 onwards |
| Handicapping appeals | published outcomes visible across multiple years |
| Disciplinary / press archives | historical material extending well before the current BHA website era |
| Non-racing agreements | current-state public chart; historical retention unresolved |
| Dashing Industry Statistics | history unresolved |
| HOY Racing Updates | retention/history unresolved |

The implication for future work is methodological rather than a selection decision:

> historical boundary testing should be performed **per chosen information family**, using that source's actual semantics and delivery mechanism.

---

## 33. What remains unresolved

### Structured race resources

- populated schemas and population rules for `balloted` and `trans`;
- exact semantics of nominations across the race lifecycle;
- precise result-availability query behaviour;
- historical point at which each detailed race sub-resource becomes consistently usable.

### Ratings / performance

- exact population represented by the full current ratings count;
- meaning of unresolved performance-figure symbols such as `x` and `0`;
- population/completeness of race-linked trainer performance figures;
- whether an equivalent race-linked figure source exists through another public horse/race route.

### Participants

- reason for trainer profile `careerRunners` versus performance-endpoint total discrepancy;
- complete historical rules for trainer non-runner reporting;
- complete structured owner-championship period metadata;
- whether any public owner-profile service exists outside the observed championship surface.

### Live/administrative systems

- complete HOY backend schema and history;
- complete public claiming-record schema and history beyond six months;
- historical non-racing-agreement availability;
- racecourse-directory backend and temporal change history.

### Statistics

- detailed measures and backend of the Dashing Industry Statistics beta application;
- methodology stability/revision policy across historic annual/monthly packs;
- exact definitions of some competitiveness/clash measures;
- table-specific parsing of the May 2026 monthly Horses in Training headline row.

### Regulatory corpora

- systematic document inventory of every racecourse-technical/welfare/licensing resource was outside the bounded Notebook 27 work;
- historical/effective-date mapping would be required before using regulatory text to govern old race records.

### Rights / operational use

Public accessibility does not itself establish an unrestricted licence for bulk extraction or commercial republication. Before any production-scale acquisition or redistribution, the relevant BHA terms and any third-party rights attached to linked services/downloads should be reviewed for the intended use.

That is a due-diligence question, not a finding that the data cannot be analysed.

---

## 34. Decision questions for the next phase

This feasibility report intentionally does not answer these questions for the user.

The evidence is now sufficient to ask them explicitly:

1. Which source families contain information Inside Rails actually wants to preserve?
2. Which sources should be acquired as primary observations, which should be validation benchmarks, and which should remain reference/provenance material?
3. Which semantic traps require governed transformations or separate raw/derived fields?
4. Which source families justify historical-depth testing, and how far back does Inside Rails actually need to go for each?
5. Which administrative populations — for example Horses in Training, claims, agreements or planned fixtures — belong in the research model without being confused with race-result populations?
6. Which official assessments — ratings, performance figures, classifications — are useful to preserve, and at what temporal grain?
7. Which live operational streams — going history, HOY updates, non-runners, Stewards material — merit systematic acquisition?
8. Which regulatory/reference corpora need explicit effective-date governance to support later studies?
9. What legal/licensing due diligence is required before any systematic commercial acquisition or republication?

Only after those choices should Database v5 or another governed storage design be proposed.

---

## 35. Evidence and provenance

Primary research evidence is retained in:

- `notebooks/27_bha_official_source_feasibility.ipynb`;
- ignored research cache under `data/cache/bha_official_source_feasibility/` on the research machine;
- the preceding controlled BHA-v4 reconciliation evidence in Notebook 26.

The BHA frontend credential used for authenticated structured-resource probes is stored locally outside version control. It is not reproduced in this report.

Principal public entry points used or verified during the feasibility work include:

- BHA home / racing navigation: https://www.britishhorseracing.com/
- Results: https://www.britishhorseracing.com/racing/results/
- Stewards Reports: https://www.britishhorseracing.com/racing/stewards-reports/
- Full-Year Fixtures: https://www.britishhorseracing.com/racing/fixtures/full-year/
- Horses: https://www.britishhorseracing.com/racing/horses/
- Jockeys: https://www.britishhorseracing.com/racing/participants/jockeys/
- Jockey Winners Totals: https://www.britishhorseracing.com/racing/jockeys-winners-totals/
- Trainers: https://www.britishhorseracing.com/racing/participants/trainers/
- Trainers Map: https://www.britishhorseracing.com/racing/participants/trainers/trainers-map/
- Owners Championship: https://www.britishhorseracing.com/racing/participants/owners/
- Ratings database: https://www.britishhorseracing.com/regulation/official-ratings/ratings-database/
- Ratings classifications: https://www.britishhorseracing.com/regulation/official-ratings/ratings-classifications/
- Longines rankings: https://www.britishhorseracing.com/regulation/official-ratings/longines-worlds-best-racehorse-rankings/
- Racing Statistics: https://www.britishhorseracing.com/regulation/reports-and-statistics/racing-statistics/
- Industry Statistics: https://www.britishhorseracing.com/industry-statistics/
- Racing Updates: https://www.britishhorseracing.com/racing-updates/
- Claiming races: https://www.britishhorseracing.com/regulation/ownership/claiming-races/
- Non-racing agreements: https://www.britishhorseracing.com/regulation/ownership/non-racing-agreements/
- Horse-name availability: https://www.britishhorseracing.com/regulation/ownership/horse-name-availability/
- Racing Colours: https://www.britishhorseracing.com/regulation/ownership/racing-colours/
- Rules and Guides: https://www.britishhorseracing.com/regulation/rules-guides/
- Handicapping appeals: https://www.britishhorseracing.com/regulation/handicapping-appeals/
- Disciplinary results: https://www.britishhorseracing.com/news-media/disciplinary-results/
- Disqualified / Excluded persons: https://www.britishhorseracing.com/disqualified-excluded-persons/
- BHA Search: https://www.britishhorseracing.com/bha-search/

---

## Final answer

The BHA website provides enough distinct official information to justify treating it as an **information ecosystem**, not a single results source.

It includes current structured race data, temporal horse/participant records, planning/admin information, operational updates, official assessments, statistical benchmarks and the regulatory documents required to interpret many of those values correctly.

The feasibility question is therefore no longer simply **“Can we obtain BHA results?”** The answer to that has already been demonstrated for a controlled modern sample.

The useful next question is:

> **Which parts of this official information ecosystem does Inside Rails want, at what grain and historical depth, and for what purpose?**

That choice belongs to the next decision phase. This report deliberately leaves it open.