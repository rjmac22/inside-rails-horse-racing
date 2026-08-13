#!/usr/bin/env python3
"""Append the BHA website sweep reports to Notebook 27 without altering existing cells.

This helper exists because the GitHub connector can inspect the pushed notebook but cannot
patch one Jupyter cell in-place safely. The script is deliberately append-only and idempotent:
if a report heading is already present anywhere in the notebook, that report is skipped.
"""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path("/home/rob/Documents/inside-rails-horse-racing")
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "27_bha_official_source_feasibility.ipynb"


REPORTS: list[tuple[str, str]] = [
    (
        "bha-site-wide-sweep-method",
        r"""## Phase 5 — Site-wide BHA public-information sweep

### Research question

> **What distinct information systems, datasets, reports, regulatory corpora and public utilities are available through the BHA website and its first-party linked services?**

The purpose of this phase is discovery and description, not selection.

The BHA website itself is used as the discovery universe rather than relying on a remembered list of useful racing sources. The sweep covers:

- main navigation;
- BHA Search;
- downloadable resources;
- public databases and search tools;
- embedded first-party applications;
- the Judicial Panel site;
- public reports, statistics and technical documents;
- public regulatory and welfare information;
- first-party linked BHA software where the main site embeds or directly links it.

A source is retained in the inventory even where it is aggregate, regulatory, documentary, historical, difficult to automate, or not obviously relevant to Database v4.

The user will decide later what should be acquired, governed, validated against, researched or ignored.

### Completeness rule

The sweep treats **distinct information systems/source families** as the unit of coverage. It does not attempt to copy every individual press release, PDF or rule into this notebook.

A searchable archive containing thousands of documents is therefore recorded as a source family, while individual documents are sampled only where necessary to establish what information the archive contains.

### Public site-search surface observed

The BHA Search page currently exposes separate result families for pages, resources, press releases, disciplinary notices, posts and racing-related results. During the sweep it displayed **861 Resources** and **124 Disciplinary Notices**; the site also exposes large press-release and post archives.

Source: https://www.britishhorseracing.com/bha-search/

### Important boundary

Public availability is evidence that information can be viewed or downloaded. It is not, by itself, evidence of an unrestricted licence for systematic commercial republication.
""",
    ),
    (
        "bha-annual-racing-data-pack-report",
        r"""## BHA Full-Year Racing Data Packs — source-family conclusion

The BHA publishes annual **Racing Data Packs** containing official aggregate statistics about the British racing programme.

The representative source inspected was the **2025 Annual Racing Data Pack**, a seven-page report comparing **2021–2025**.

### Information demonstrated

The pack contains annual measures for:

- fixtures programmed and fixtures run;
- abandonments and additions;
- races run;
- entries, declarations, eliminations and non-runners;
- prize money / race-value material;
- average field size;
- total runners and individual runners;
- average runs per horse;
- race-card-size measures;
- small-field and larger-field KPIs;
- competitiveness measures;
- policy/innovation-specific measures.

### Fixture semantics

The report distinguishes **Fixtures Programmed** from **Fixtures Ran**. Those are different populations and should not be treated interchangeably.

It also states that **Mixed fixtures are recategorised as Flat** for its reporting. That is an explicit BHA aggregation rule which could create a legitimate difference from another classification method.

Observed 2025 programmed-fixture values included:

- Flat Turf — 548;
- Flat AWT — 349;
- Jump — 563;
- Total — 1,460.

### Race population

Observed 2025 race counts were:

- Flat Turf — 3,748;
- Flat AWT — 2,793;
- Chase — 1,249;
- Hurdle — 2,042;
- NHF — 243;
- Hunter — 52;
- Total — 10,127.

These are useful official aggregate benchmarks, but reconciliation requires the same jurisdiction, period, void-race treatment and category rules.

### Runners

The report explicitly distinguishes **Total Runners** from **Individual Runners**.

Observed 2025 Total Runners included:

- Flat Turf — 33,011;
- Flat AWT — 25,165;
- Jump — 28,124;
- Total — 86,300.

Observed 2025 Individual Runners included:

- Flat — 10,029;
- Jump — 7,307;
- Dual — 713;
- Total — 18,049.

Observed average runs per horse were Flat 5.42, Jump 3.51 and Overall 4.78.

### Grain and limitation

This is an aggregate reporting source, not a fixture/race/runner feed. It is particularly informative as an official definition, historical-trend and validation source.

Public labelled annual packs were observed for **2015–2025**.

Source: https://www.britishhorseracing.com/regulation/reports-and-statistics/racing-statistics/

### Unresolved

Preserve until a particular comparison is required:

- exact void-race treatment;
- exact population rules for entries/declarations/eliminations/non-runners;
- precise prize-money versus race-value definitions;
- stability of methodology across historic packs;
- revision/correction practice.
""",
    ),
    (
        "bha-monthly-racing-data-pack-report",
        r"""## BHA Monthly Racing Data Packs — source-family conclusion

The BHA publishes monthly **Racing Data Packs** containing current-year and year-to-date operational statistics.

The representative source inspected was the **May 2026 Racing Data Pack**, a four-page PDF.

### Information demonstrated

The May 2026 pack contains YTD/current measures for:

- programmed, abandoned, added and run fixtures;
- race volume;
- average field size;
- races with 8+ runners;
- favourite/competitiveness measures;
- total prize money paid out;
- handicap race values;
- Horses in Training summary measures;
- race punctuality;
- race clashes / race-time operational measures.

This overlaps with the annual pack, but it is not merely the annual pack divided by month. It contains operational measures not observed in the inspected annual product.

### Horses in Training timing rule

The monthly pack explicitly describes its Horses in Training comparison as a **snapshot on 31 May of each year**.

That differs from the dedicated Horse Population Report, whose normal monthly snapshot rule is the 15th of the month unless otherwise stated.

Therefore those two products should not be forced to reconcile without aligning their dates and population rules.

The initial text extraction produced values including Flat 9,467, Jump 2,838, Dual 460 and Total 12,763, but table alignment was not sufficiently proven to govern those extracted numbers as a coherent row. The source definition is established; those specific extracted values remain provisional pending table-specific parsing.

### Punctuality relationship

The monthly pack exposes aggregate race-time punctuality and clash measures. The dedicated Race Off-Times report subsequently established the more precise BHA rule that punctuality is measured against a Scheduled Time that incorporates BHA Racing Department Requested Delays.

### Grain

The monthly pack is an aggregate/YTD dashboard product. It does not itself demonstrate individual fixture, race or horse records.

Source: https://www.britishhorseracing.com/regulation/reports-and-statistics/racing-statistics/

### Unresolved

- exact definitions of every competitiveness/clash metric;
- table-specific extraction of the May 2026 Horses in Training row;
- methodology stability across earlier monthly packs;
- which monthly measures are later revised in annual reporting.
""",
    ),
    (
        "bha-jockey-winners-totals-report",
        r"""## BHA Jockey Winners Totals — source-family conclusion

The site-wide sweep identified a distinct public **Jockeys winners totals** table that was not covered by the earlier jockey profile/championship investigation.

The BHA states that the table shows the number of **British winners ridden by British-licensed jockeys since 1 January 1995**.

### Demonstrated fields

The public template exposes:

- Jockey Name;
- Wins;
- Runs;
- Racing Today.

### Historical boundary

The page explicitly says accurate electronic winner data before 1995 is not available. Jockeys who were already riding before that date are marked with an asterisk and only their winners since 1 January 1995 are counted.

That makes **1995 a source-definition boundary**, not necessarily the start of a jockey's career.

Source: https://www.britishhorseracing.com/racing/jockeys-winners-totals/

### Relationship to the jockey profile source

This is a separate aggregate/career-history surface from the previously inspected jockey search/profile and championship data. It should not be silently assumed to have identical career-population rules.
""",
    ),
    (
        "bha-trainers-map-report",
        r"""## BHA Trainers Map — source-family conclusion

The BHA exposes a distinct **Trainers Map** application in addition to the trainer search/profile pages.

The BHA describes the map as providing, for every registered trainer in Britain:

- exact location;
- contact details;
- yard size;
- performance information;
- licence type.

The embedded first-party application can be searched by:

- trainer name;
- full or partial postcode;
- county;
- licence type.

The BHA page defines the displayed licence categories as Flat, Jump and Combined.

Sources:

- https://www.britishhorseracing.com/racing/participants/trainers/trainers-map/
- https://crate.horseracing.software/tom/

### Relationship to existing trainer work

The earlier trainer profile investigation demonstrated trainer identity, licence information, performance history, championship and non-runner measures. The map adds an explicit public **location/search geography** surface and states that it includes yard size and contact/performance information.

No bulk extraction of trainer locations was performed during this sweep.
""",
    ),
    (
        "bha-industry-statistics-dashboard-report",
        r"""## BHA Industry Statistics dashboard — source-family conclusion

The BHA's **Industry statistics** navigation item is not the same page as the PDF Racing Statistics archive.

It embeds a first-party application at:

https://dashing.horseracing.software/

The application identifies itself as **Dashing - BHA** and displays a prominent **beta** warning stating that there may be bugs or data issues rendering information incorrect.

This establishes a distinct interactive statistics product in addition to:

- annual Racing Data Pack PDFs;
- monthly Racing Data Pack PDFs;
- Horse Population Reports;
- Race Off-Times PDFs.

BHA entry point: https://www.britishhorseracing.com/industry-statistics/

### Current investigation boundary

The public web extraction exposed the application shell and beta warning but did not expose its dashboard measures or underlying data calls. Those contents remain **unresolved**, not absent.

A later browser/app-level probe is required before describing the measures contained in Dashing.
""",
    ),
    (
        "bha-racing-updates-hoy-report",
        r"""## BHA Racing Updates / HOY — source-family conclusion

The top-level **Racing updates** link embeds a distinct first-party application rather than an ordinary BHA news page.

The current application is hosted at:

https://crate.horseracing.software/hoy/

and identifies itself as **hoy v2.13**.

### Demonstrated behaviour

The application supports:

- automatic update checking;
- optional audio alerts for new updates;
- filtering update types;
- remembered filter/settings choices via cookies.

It states that fixture dates and race times are shown in **GB / Europe-London time**, while other times are local to the viewer.

The application also links an older v1 surface.

BHA entry point: https://www.britishhorseracing.com/racing-updates/

### Current investigation boundary

During the sweep the application returned an error retrieving the latest update data, so the current update-type taxonomy and record schema were not demonstrated.

This is therefore a confirmed live/operational information system whose detailed data contents remain unresolved, rather than evidence that no data exists.
""",
    ),
    (
        "bha-claiming-races-report",
        r"""## BHA Claiming-Race Records — source-family conclusion

The BHA ownership section contains a public searchable **Claiming races** service.

The page describes its purpose as searching for **claimed horses and who they have been claimed by**.

### Public historical window

The interface explicitly states:

**Last 6 months of Claims.**

This is a demonstrated public-window rule and should not be interpreted as evidence that BHA holds only six months internally.

### Race-level fields visible in the public template

The page template exposes:

- CourseName;
- RaceDate;
- RaceTime.

The claimant display template exposes:

- claimer Status;
- optional claimer Type.

The text also establishes that claimant names are part of the public service, although the current web extraction did not return populated rows.

### Claiming semantics stated by BHA

- all horses in a Claiming Race may be claimed at a value set against the horse by the trainer when entering;
- in a Selling Race all horses except the winner may be claimed, while the winner is auctioned on course;
- Rules prohibit a person being party to more than one claim and address conflicts involving registered partnerships;
- a successful unfriendly claim can create a six-month running restriction if the horse is subsequently sold, gifted or leased to an unsuccessful claimant.

Source: https://www.britishhorseracing.com/regulation/ownership/claiming-races/

### Grain and unresolved questions

The demonstrated grain is **claim transaction linked to a race/horse/claimant**, but the full structured schema and backend route were not exposed by the public page extraction.

Unresolved:

- claim value field availability;
- friendly/unfriendly flag representation;
- horse/claimer identifiers;
- whether unsuccessful claimants are publicly represented;
- history beyond the six-month public interface.
""",
    ),
    (
        "bha-non-racing-agreements-report",
        r"""## BHA Non-Racing Agreements — source-family conclusion

The BHA publishes a searchable chart of **all horses currently subject to non-racing agreements**.

### Demonstrated public fields

The current page exposes columns for:

- Horse;
- Owners, with `(B)uyer` and `(S)eller` roles;
- Start Date.

The interface can be searched by horse name and is paginated.

Source: https://www.britishhorseracing.com/regulation/ownership/non-racing-agreements/

### Grain and temporal semantics

This is a **current-state horse/agreement** source, not demonstrated agreement history. The wording `currently subject` is important: disappearance from the current chart is not evidence that an agreement never existed.

The detailed legal effect, termination/end-date semantics and any historic archive remain unresolved.
""",
    ),
    (
        "bha-horse-name-availability-report",
        r"""## BHA Horse Name Availability — source-family conclusion

The BHA provides a public interactive **Horse name availability** checker.

A horse eligible to race under Rules or in Point-to-Points must have a unique registered name, which remains with that horse for life.

### Demonstrated output

A search can return:

- name available;
- name unavailable;
- suggested alternative names.

The BHA explicitly warns that an `available` result means only that the name is not currently registered to another horse or protected by a previous horse's performances. It remains subject to further registration checks.

Source: https://www.britishhorseracing.com/regulation/ownership/horse-name-availability/

### Grain

This is a **name-candidate availability utility**, not a horse-identity database and not proof that an available name will be accepted for registration.
""",
    ),
    (
        "bha-racing-colours-report",
        r"""## BHA Racing Colours — source-family conclusion

The BHA ownership section exposes three distinct public colour/silks mechanisms:

1. **Standard Colours** — an interactive builder that can choose, check availability and register a standard set of colours;
2. **Bespoke Colours** — custom designs outside all normal standard-design restrictions, subject to application;
3. **Vintage Colours** — a public marketplace for the right to register existing colours.

The standard builder states that 18 colours can be combined across body, sleeve and cap designs.

The Vintage Colours section publishes individual listings with:

- textual colour/design description;
- asking price;
- purchase action.

The page states that vintage silks listed there have been registered for more than five years.

Source: https://www.britishhorseracing.com/regulation/ownership/racing-colours/

### Grain

This is a combination of **availability/design utility** and **current marketplace listings**, not a demonstrated historical database of all registered racing colours.
""",
    ),
    (
        "bha-handicapping-appeals-report",
        r"""## BHA Handicapping Appeals — source-family conclusion

The BHA publishes the process and outcomes of independent **handicapping appeals**.

An appeal may concern a horse's handicap rating or the refusal to allot a rating.

### Review process

The published process is:

1. trainer contacts the responsible handicapper;
2. trainer escalates to the Head of Handicapping;
3. if still unresolved, trainer submits an appeal;
4. an independent Handicapping Ombudsman considers the trainer's and handicapper's positions;
5. any rating revision is published in the normal Tuesday reassessment cycle;
6. written reasons are supplied to the trainer and subsequently published on the BHA website.

The page states that weekly rating changes are published at **7am Tuesday** and gives a Wednesday submission deadline for an appeal to affect the current handicapping week.

### Published outcomes

The public page lists named horse/date appeal outcomes, demonstrated from 2019 through 2026, including Tunisya, Masterpiece, A Dream To Share, Gentleman Bill, Cairo, Fair Angellica, In Excelsis Deo, Traprain Law, Nimbus Boy and others.

Source: https://www.britishhorseracing.com/regulation/handicapping-appeals/

### Form inconsistency preserved

The process page currently states an appeal charge of **£225 + VAT**, while the separate public appeal form states **£234 (£195 + VAT)**.

This is a current-source inconsistency and is deliberately not reconciled by assumption.

### Grain

This is a **horse-level regulatory decision/reasons archive**, potentially useful for understanding how disputed ratings are reasoned about. It is not a general rating-history feed.
""",
    ),
    (
        "bha-ratings-classifications-report",
        r"""## BHA Ratings Classifications and Champion Tables — source-family conclusion

The ratings area contains historical classification/leaderboard products in addition to the current Ratings Database already investigated.

Observed families include:

- International Flat classifications for high-rated horses;
- Anglo-Irish Jump classifications;
- European two-year-old classifications;
- Longines World's Best Racehorse material;
- Anglo-Irish Jump Champion tables by distance/category.

The public classification page exposes downloadable historic classification documents, including Anglo-Irish Jump files across multiple seasons from the mid-2000s onward and European two-year-old classifications for multiple years.

The champion-table pages provide historical top performers rather than current weekly handicap marks.

These are distinct **end-of-season / historical elite-performance sources**, and should not be conflated with the weekly official-rating database.

Entry point: https://www.britishhorseracing.com/regulation/official-ratings/ratings-classifications/
""",
    ),
    (
        "bha-rules-guides-calculators-report",
        r"""## BHA Rules, General Instructions, Guides and Calculators — source-family conclusion

The BHA's **Rules of Racing and guides** area is a major first-party semantic/reference corpus.

It contains considerably more than the formal Rules microsite.

### BHA General Instructions

The public page provides a full index and twelve General Instruction sections covering subjects including:

1. Compliance;
2. Race Planning;
3. The Racecourse;
4. Integrity Services;
5. Broadcasting & Photography;
6. Appointment of Stewards & Clerks of the Course;
7. Racecourse stabling/canteen/overnight accommodation;
8. Raceday operational areas including weighing and Stewards room;
9. Passcards, racecourse personnel and racecards;
10. Starting arrangements, farriers and AFOs;
11. Medical services on racecourses;
12. Veterinary services on racecourses.

### Additional rule/reference material

The area also exposes:

- current Equine Anti-Doping Rules and penalties;
- Rules of Racing microsite;
- pre-1 September 2019 Rules archive;
- Bloodstock Industry Code;
- specified-sale guidance;
- commercial-arrangement guidance;
- health-and-safety templates/guides;
- shared-ownership manuals/codes/policies;
- horse naming and leasing guidance;
- current rates of exchange;
- Point-to-Point regulations;
- multiple weight-for-age scales;
- sponsorship codes;
- owner VAT guidance.

### Interactive calculators

Two first-party utilities are linked directly from the Rules area:

- **Vaccination Calculator**;
- **Horses in Training Calculator**.

These are distinct operational rule-calculation tools and should be investigated separately if their calculations become relevant to governed data.

Source: https://www.britishhorseracing.com/regulation/rules-guides/

### Role in Inside Rails research

This corpus can provide authoritative semantics for fields and administrative states that cannot safely be inferred from API names alone.
""",
    ),
    (
        "bha-licensing-racecourse-technical-report",
        r"""## BHA Licensing and Racecourse Technical Resources — source-family conclusion

The BHA publishes a broad licensing corpus for racing participants and racecourses.

### Participant licensing

The Licensing Team states that it licenses, permits or registers:

- Trainers;
- Jockeys;
- Amateur Riders;
- Agents;
- Valets;
- equine pools.

Public pages provide application forms, guidance, suitability criteria and licence-fee information. Licensing decisions can be referred to the independent Licensing Committee.

### Racecourse licensing

Racecourses are licensed through Raceday Operations with suitability assessments by Licensing.

The public forms/resources area exposes technical documents including:

- Racecourse Licence Suitability Policy;
- Artificial Surface Approval Protocol;
- changes to Flat race distances;
- financial suitability assessment;
- Fundamental Turf Management Principles;
- guidelines for converted racetracks;
- guidelines for new racecourses;
- new entrants policy;
- starts and remeasurement data;
- track-design information.

The racecourse area separately explains the 2015 Jump-distance measurement change: distances moved from a mid-course survey-wheel method to professional measurement along a line two yards off the innermost running rail, to the nearest yard.

Sources:

- https://www.britishhorseracing.com/regulation/licensing/about-licensing/
- https://www.britishhorseracing.com/regulation/licensing/forms-info/
- https://www.britishhorseracing.com/racecourse/

### Grain

This family is primarily **regulatory/technical reference evidence**, with some downloadable course-distance/start/remeasurement data products.
""",
    ),
    (
        "bha-equine-anti-doping-report",
        r"""## BHA Equine Anti-Doping, Medication and Testing — source-family conclusion

The BHA publishes both regulatory guidance and a historical testing time series for equine anti-doping.

### Testing types described

Public material describes:

- pre-race testing;
- post-race/raceday testing;
- targeted and random out-of-competition testing;
- permanent-import testing;
- international-runner testing;
- sales-house testing;
- A/B sample and chain-of-custody procedures.

The BHA states that regulatory samples are sent to LGC.

### Public testing time series

The testing page publishes annual counts for **2014–2025** with columns:

- Raceday;
- Out of Competition;
- Positives.

Observed rows include:

- 2014 — 8,287 / 1,182 / 24;
- 2020 — 5,873 / 842 / 19;
- 2024 — 9,040 / 2,174 / 23;
- 2025 — 8,237 / 2,918 / 18.

Source: https://www.britishhorseracing.com/regulation/anti-doping-medication-control/forms/

### Prohibited-substance reference corpus

The BHA also publishes:

- detection-time information;
- testing procedure documents;
- medication-control guidance;
- notices about specific drugs/products;
- equine anti-doping forms;
- current rules and penalties.

The Centre for Racehorse Studies describes controlled research used to generate detection-time evidence and analytical-method development.

### Foal traceability

A separate 30-day foal-notification process requires a GB thoroughbred foal bred for racing to be notified to the General Stud Book at Weatherbys within 30 days of birth. This supports pre-training traceability and eligibility.

This is administrative semantics; the public page does not expose individual foal records.
""",
    ),
    (
        "bha-human-anti-doping-report",
        r"""## BHA Jockey Human Anti-Doping Testing — source-family conclusion

Separate from equine testing, the BHA publishes **jockey testing statistics** within its human anti-doping/integrity material.

The current page exposes annual counts for testing methods including:

- Breath;
- Urine;
- Hair.

The displayed series covers **2020–2025**.

For 2025 the page shows:

- Breath — 5,520;
- Urine — 1,528;
- Hair — 32.

Source: https://www.britishhorseracing.com/regulation/anti-doping/

This is a participant-regulation aggregate time series and is distinct from equine anti-doping testing.
""",
    ),
    (
        "bha-equine-welfare-fatality-report",
        r"""## BHA Equine Welfare and Fatal-Injury Statistics — source-family conclusion

The BHA publicly publishes **fatal injury data** in its Making Horseracing Safer section.

Separate presentation is provided for:

- all racing;
- Jump racing;
- Flat racing;
- All-Weather racing.

### Critical methodology changes

The BHA explicitly documents changes in what counts as a raceday fatality.

From **2021**, reporting captures a horse fatally injured or euthanised on welfare grounds as a direct result of raceday injuries either on raceday or within 48 hours.

From **2024**, reporting is broadened further to include any horse fatally injured within 48 hours of a raceday incident, including elective euthanasia.

Therefore a historical trend crossing 2021 or 2024 cannot be interpreted as a perfectly stable measurement series without accounting for these definition changes.

Source: https://www.britishhorseracing.com/regulation/making-horseracing-safer/

### Other welfare information publicly described

The same area discusses:

- racecourse faller-rate monitoring;
- racing-surface and obstacle safety work;
- Racing Risk Models built from a long historical evidence base;
- veterinary/raceday examination protocols;
- hot-weather procedures;
- welfare research and Horse Welfare Strategy material.

The underlying individual-level Racing Risk Model data is not demonstrated as a public dataset.
""",
    ),
    (
        "bha-whip-statistics-report",
        r"""## BHA Whip Referrals and Offence Statistics — source-family conclusion

The BHA's public whip page contains a substantial statistical reporting surface, not merely rule guidance.

### Annual/current measures

The page publishes:

- total rides;
- referrals to the Whip Review Committee;
- breaches found;
- breaches as a percentage of rides;
- offence counts and shares by offence type;
- rides, offences and offence rates by jockey licence type;
- horse disqualifications caused by serious whip offences.

### 2025 example

For calendar year 2025 the page reports:

- 86,262 rides;
- 565 referrals;
- 509 breaches;
- breach rate 0.59%.

It breaks those breaches down into categories such as:

- Above permitted level;
- Incorrect place;
- Without time to respond;
- Above shoulder height;
- Out of contention;
- Down shoulder in forehand;
- Weal;
- Clearly winning;
- Excessive down shoulder;
- Excessive force.

Licence-type rows include Fully professional, Apprentice, Conditional, Amateur and International.

### 2026 partial-year reporting

The same page also publishes current 2026 data for a stated partial-year period, so period boundaries must be preserved rather than comparing a partial year directly with completed calendar years.

Source: https://www.britishhorseracing.com/regulation/the-whip-2-2-2/

### Grain

The principal public tables are aggregate. Named horse/date disqualifications are also listed, but no complete individual referral/offence row feed was demonstrated from this page.
""",
    ),
    (
        "bha-judicial-excluded-report",
        r"""## BHA Judicial Decisions, Disqualified/Excluded Persons and Forfeit Lists — source-family conclusion

The BHA exposes several related but distinct regulatory-decision sources.

### Independent Judicial Panel site

The Judicial Panel comprises:

- Disciplinary Panel;
- Licensing Committee;
- Appeal Board.

The public Judicial Panel site provides a searchable **Disciplinary / Appeal Hearings** archive and separate Licensing Committee decisions.

The Licensing Committee page demonstrates decisions extending back through multiple years and currently includes a 2026 decision.

Sources:

- https://judicialpanel.britishhorseracing.com/
- https://judicialpanel.britishhorseracing.com/results/
- https://judicialpanel.britishhorseracing.com/licensing-committee/

### Disqualified and Excluded Persons

The main BHA site provides a searchable **current-state** list with three distinct groups:

1. Debt/arrears — Forfeit List;
2. Judicial Panel decisions;
3. Disciplinary Officer exclusion orders.

Demonstrated fields include:

**Debt/arrears**
- year name published;
- person;
- disqualified/excluded state;
- sum outstanding.

**Judicial decisions**
- decision date;
- person;
- disqualified/excluded state;
- length/extent of penalty.

**Disciplinary Officer exclusion orders**
- decision date;
- person;
- length/extent of penalty;
- reason.

The Forfeit List wording says a person's name remains until arrears are paid.

Source: https://www.britishhorseracing.com/disqualified-excluded-persons/

### Legacy disciplinary notices

BHA Search also exposes a legacy **Disciplinary Notices** corpus. Individual notices can contain detailed charges, Rules, named horses/races, evidence, findings, penalties and panel membership.

This should be distinguished from the current Judicial Panel decision system rather than treated as one homogeneous archive.
""",
    ),
    (
        "bha-point-to-point-arabian-report",
        r"""## BHA Point-to-Point and Purebred Arabian Information — source-family conclusion

The BHA publishes dedicated regulatory/fixture information for racing outside the ordinary licensed Thoroughbred fixture surface.

### Point-to-Point

The public Point-to-Point area provides:

- current-season fixture information;
- regulations;
- instructions;
- penalties/allowances;
- horse eligibility material;
- rider qualification/licensing information;
- Hunter's Certificate semantics.

A Hunter's Certificate affiliates a horse and owner to a Hunt and an area for a season.

Point-to-Point courses are described as BHA-approved rather than licensed in the same way as ordinary racecourses.

Source: https://www.britishhorseracing.com/regulation/point-to-point/

### Purebred Arabian racing

The BHA page describes the Arabian Racing Organisation as the authority operating with BHA support/permission. BHA approves relevant fixture/regulatory arrangements and provides integrity services where appropriate.

The page links current fixture information, while much of the detailed participant/horse administration is held through ARO/Weatherbys rather than demonstrated as a first-party BHA public database.

This is an important **source-boundary finding**: BHA oversight does not imply that all underlying Arabian participant data is publicly hosted by BHA.
""",
    ),
    (
        "bha-publications-search-news-report",
        r"""## BHA Publications, Resource Library, Search and News Archives — source-family conclusion

The BHA website contains several large documentary archives that can provide historical context, policy provenance and information not present in structured racing databases.

### BHA Publications

The Publications page provides downloadable historic material including:

- business plans;
- annual reports/reviews;
- Fact Books;
- disciplinary/integrity reviews;
- Fillies and Mares Review;
- Jump Racing reviews;
- Grand National Review;
- whip review material;
- Economic Impact reports.

Observed historic annual/fact publications extend back into the 2000s.

Source: https://www.britishhorseracing.com/about/publications/bha-publications/

### BHA Search / Resources

The site-wide search currently exposes a large **Resources** corpus; during this sweep it displayed **861 resources**. Results include PDFs and other files such as data packs, decision documents, fact sheets, transcripts and regulatory resources.

Source: https://www.britishhorseracing.com/bha-search/

### Press releases and posts

The BHA also provides searchable/date-filterable press releases and a large news/blog/post archive.

These can contain time-specific evidence about:

- fixture transfers and race-programme changes;
- rule changes;
- licensing/regulatory decisions;
- welfare/integrity incidents;
- data releases;
- policy rationale;
- historical operational changes.

Source: https://www.britishhorseracing.com/news-media/press-releases/

These archives are **event/document sources**, not stable rectangular datasets. Their value is often provenance for why a structured value or rule changed.
""",
    ),
    (
        "bha-ownership-sponsorship-admin-report",
        r"""## BHA Ownership, Shared-Ownership and Sponsorship Administration — source-family conclusion

Beyond owner championships and the public ownership utilities, the BHA publishes substantial administrative semantics for ownership.

### Ownership types

The Owners' Toolkit describes five ownership forms:

- Sole;
- Company;
- Partnership;
- Syndicate;
- Racing Club.

It explains who registers where, responsible-person concepts and Racing Admin processes. This material can help interpret owner identities that appear in racing data.

### Shared ownership

The BHA publishes a Shared Ownership Manual, Syndicate/Racing Club codes and licensing material for people managing publicly promoted Syndicates or Racing Clubs.

### Sponsorship

The BHA sponsorship page describes registration requirements for Owner, Trainer and Jockey sponsorship and commercial arrangements with betting organisations.

It also publishes sponsorship codes and a Sports Gambling Sponsorship Code annual evaluation.

Source: https://www.britishhorseracing.com/regulation/sponsorship/

These are regulatory/administrative sources. No public master table of all sponsorship agreements was demonstrated.
""",
    ),
    (
        "bha-veterinary-participant-health-report",
        r"""## BHA Veterinary Resources and Participant Health/Safety — source-family conclusion

The BHA publishes operational health and welfare guidance for both horses and human participants.

### Veterinary resource library

The equine welfare Resources page exposes forms/notices including:

- approved racecourse-vet application;
- veterinary non-runner certificate;
- tubed-horse certificate;
- pregnant-horse notification;
- pregnancy-loss notification;
- veterinary notices;
- shockwave stand-down guidance;
- shoe-dispensation process/forms;
- suitability-to-race information.

Source: https://www.britishhorseracing.com/regulation/welfare-info/

### Participant health and safety

The participant-health area publishes medical, concussion and racecourse medical standards, fitness-to-ride information and equipment/protocol material.

The BHA also states that it maintains a **confidential jockey injury database** including relevant off-course injuries.

That database is an explicit **non-public information boundary**: its existence is documented, but the individual injury records are not publicly available through the website.

This distinction matters to a full availability audit: information known to exist internally is not the same as publicly obtainable information.
""",
    ),
    (
        "bha-racecourse-directory-report",
        r"""## BHA Racecourse Directory and Public Racecourse Surface — source-family conclusion

In addition to the racecourse technical documents and GoingStick work already investigated, the current BHA racing site has a public **Racecourses** directory.

The page states that there are **59 racecourses in Britain** on the current public racing directory and provides discovery through:

- interactive map;
- A–Z list;
- postcode / nearest-racecourse search.

Source: https://www.britishhorseracing.com/racing/racecourses/

The individual racecourse-profile application did not expose a populated representative profile through the web extraction used in this sweep, so its full profile field schema remains unresolved here.

The `59` value belongs to the current public directory's concept of racecourse and should not be substituted for the governed racecourse/course identity counts established by Study 03 without semantic alignment.
""",
    ),
    (
        "bha-site-wide-coverage-ledger",
        r"""## BHA website sweep — coverage ledger

The following ledger records the distinct public information families demonstrated so far. `Reported` means the family has a dedicated notebook conclusion either earlier in Notebook 27 or in this sweep. `Unresolved surface` means the public system is confirmed but some app-level schema/content could not be recovered by the present web inspection.

| Information family | Principal grain | Delivery | Status |
|---|---|---|---|
| Fixtures / fixture detail | fixture | structured service | Reported earlier |
| Fixture going / weather / watering / track state | fixture/track/time | structured service | Reported earlier |
| Fixture officials | fixture/person | structured service | Reported earlier |
| Races | race | structured service | Reported earlier |
| Entries | race/horse | structured service | Reported earlier |
| Nominations | race/horse | structured service | Reported earlier |
| Results | race/runner | structured service | Reported earlier |
| Balloted / trans routes | race/horse | structured service | Reported earlier; populated schema unresolved |
| Stewards Reports | fixture/race/document | PDF | Reported earlier |
| GoingStick current/archive | course/time | public archive | Reported earlier |
| Official Ratings database | horse | structured service/export | Reported earlier |
| Latest performance-figure export | horse/recent-run sequence | CSV export | Reported earlier |
| Horse profiles | horse | structured service | Reported earlier |
| Horse performances | horse/race | structured service | Reported earlier |
| Horse training history | horse/trainer/time | structured service | Reported earlier |
| Jockey profiles/championships | jockey/race/period | structured service | Reported earlier |
| Jockey winners totals since 1995 | jockey | dynamic table | Reported in site sweep |
| Trainer profiles/performance | trainer/race | structured service | Reported earlier |
| Trainer non-runners | trainer/period | structured service | Reported earlier |
| Trainers Map | trainer/location | embedded app | Reported in site sweep |
| Owner championships | owner/season | structured service | Reported earlier |
| Full-year fixture workbook | fixture | XLSX/PDF | Reported earlier |
| Annual Racing Data Packs | annual aggregate | PDF | Reported in site sweep |
| Monthly Racing Data Packs | monthly/YTD aggregate | PDF | Reported in site sweep |
| Horse Population Reports | admin horse population | PDF | Reported earlier |
| Race Off-Times | aggregate/course | PDF | Reported earlier |
| Industry Statistics / Dashing | interactive aggregate | embedded app | Unresolved surface |
| Racing Updates / HOY | live operational update | embedded app | Unresolved surface |
| Claiming-race records | claim/race/horse/claimer | dynamic search | Reported in site sweep |
| Non-racing agreements | horse/agreement | dynamic search | Reported in site sweep |
| Horse-name availability | candidate name | interactive utility | Reported in site sweep |
| Racing colours | colours/availability/listing | embedded utility + marketplace | Reported in site sweep |
| Handicapping appeals | horse/decision | page + decisions | Reported in site sweep |
| Ratings classifications | season/horse | documents/tables | Reported in site sweep |
| Longines / Jump champion tables | season/category/horse | table/document | Reported in site sweep |
| Rules of Racing | rule/version | rules microsite | Reported in site sweep |
| General Instructions | operational rule/reference | PDF | Reported in site sweep |
| Vaccination Calculator | horse/vaccination dates | embedded utility | Discovered; calculation schema unresolved |
| Horses in Training Calculator | administrative calculation | embedded utility | Discovered; calculation schema unresolved |
| Weight-for-age scales | age/date/distance/code | document | Reported in site sweep |
| Participant licensing | participant/licence type | pages/forms/guides | Reported in site sweep |
| Licensing Committee decisions | person/application/decision | Judicial Panel documents | Reported in site sweep |
| Racecourse licensing/technical documents | course/technical rule | PDF/docs | Reported in site sweep |
| Race-distance change / starts / remeasurement resources | course/distance/start | documents/data files | Reported in site sweep |
| Equine anti-doping testing | year/test type | table + rules/guides | Reported in site sweep |
| Equine prohibited-substance/detection-time guidance | substance/procedure | documents | Reported in site sweep |
| 30-day foal notification | foal/admin rule | page/process | Reported in site sweep |
| Jockey human anti-doping testing | year/test method | table | Reported in site sweep |
| Fatal-injury statistics | year/code | charts/tables | Reported in site sweep |
| Whip referrals/offences | year/licence/offence | tables | Reported in site sweep |
| Veterinary forms/notices | veterinary/admin event | documents/forms | Reported in site sweep |
| Participant medical/concussion standards | participant/standard | pages/docs | Reported in site sweep |
| Confidential jockey injury database | jockey/injury | internal database | Known non-public boundary |
| Disqualified/Excluded persons | person/current status | dynamic search | Reported in site sweep |
| Forfeit List / arrears | person/debt | dynamic search | Reported in site sweep |
| Judicial disciplinary/appeal decisions | case/decision | searchable site/docs | Reported in site sweep |
| Legacy Disciplinary Notices | case/document | BHA Search archive | Reported in site sweep |
| Point-to-Point | fixture/horse/rider/rule | documents/links | Reported in site sweep |
| Purebred Arabian racing | fixture/regulatory context | BHA page + external authority | Reported in site sweep |
| Ownership types/shared ownership | owner/admin structure | pages/docs | Reported in site sweep |
| Sponsorship administration/codes | participant/agreement rules | pages/docs/forms | Reported in site sweep |
| BHA Publications / Fact Books / Reviews | document/year | PDF archive | Reported in site sweep |
| BHA Resource library | document/resource | site search | Reported in site sweep |
| Press releases | event/document | searchable archive | Reported in site sweep |
| News/blogs/posts/podcast | event/editorial | searchable archive | Reported in site sweep |
| Industry links / external racing bodies | organisation | directory | Discovered reference surface |
| Industry strategy / research reports | study/strategy/document | pages/reports | Discovered reference surface |
| Racing Digital | future/admin platform context | page | Discovered; not current public data feed |

### Remaining unresolved systems after the web-only sweep

The principal confirmed public systems whose **contents have not yet been sufficiently enumerated** are:

1. **Industry Statistics / Dashing** — beta application shell observed, dashboard measures not recovered;
2. **Racing Updates / HOY** — live update application observed, current update taxonomy/schema not recovered because its data request failed;
3. **Vaccination Calculator** — public utility discovered, calculation inputs/outputs not yet mapped;
4. **Horses in Training Calculator** — public utility discovered, calculation inputs/outputs not yet mapped;
5. **individual Racecourse profile app** — directory demonstrated, representative profile fields not recovered;
6. any backend schemas for public dynamic tools such as Claims, Non-Racing Agreements, Horse Name Availability and Racing Colours that are not exposed in rendered templates.

These remain unresolved because the browser-facing application data was not exposed by the web extraction, **not because the information has been judged unimportant**.

### Decision boundary

No database-adoption or publication-priority decision is made by this ledger.

Its purpose is to make the available BHA information visible so that later decisions can be made from an explicit evidence inventory rather than from memory.
""",
    ),
]


def main() -> None:
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK_PATH}")

    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise ValueError("Notebook does not contain a valid cells list")

    existing_markdown = "\n".join(
        "".join(cell.get("source", []))
        for cell in cells
        if cell.get("cell_type") == "markdown"
    )

    appended: list[str] = []
    skipped: list[str] = []

    for cell_id, markdown in REPORTS:
        heading = markdown.strip().splitlines()[0]

        # Idempotency is based on the visible report heading, not only on the cell ID,
        # because a user may already have added an equivalent cell manually.
        if heading in existing_markdown:
            skipped.append(heading)
            continue

        cells.append(
            {
                "cell_type": "markdown",
                "id": cell_id,
                "metadata": {},
                "source": [line + "\n" for line in markdown.strip().splitlines()],
            }
        )
        existing_markdown += "\n" + markdown
        appended.append(heading)

    if not appended:
        print("No cells appended; all sweep report headings are already present.")
        return

    # Write only after the complete in-memory notebook has been validated. Existing cells
    # are never edited or reordered by this helper; new Markdown cells are appended only.
    temp_path = NOTEBOOK_PATH.with_suffix(".ipynb.tmp")
    temp_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(NOTEBOOK_PATH)

    print(f"Appended {len(appended)} Markdown cells to {NOTEBOOK_PATH}")
    for heading in appended:
        print(f"  + {heading}")

    if skipped:
        print(f"Skipped {len(skipped)} existing report headings:")
        for heading in skipped:
            print(f"  = {heading}")


if __name__ == "__main__":
    main()
