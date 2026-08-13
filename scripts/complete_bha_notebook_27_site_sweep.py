#!/usr/bin/env python3
"""Complete the site-wide BHA public-information sweep in Notebook 27.

Run this script once from the repository root after pulling the branch. It calls the
base append helper for the established reports, suppresses reports superseded by later
site-sweep evidence, and then appends the final follow-up reports. Existing notebook
cells are never deleted, edited or reordered.
"""

from __future__ import annotations

import json
from pathlib import Path

import append_bha_notebook_27_site_sweep as base


PROJECT_ROOT = Path("/home/rob/Documents/inside-rails-horse-racing")
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "27_bha_official_source_feasibility.ipynb"

# These base reports were written before the final web cross-check. Suppress them so the
# notebook receives only the richer final versions below. The first helper remains useful
# for every other already-established report.
SUPERSEDED_BASE_IDS = {
    "bha-racing-updates-hoy-report",
    "bha-racecourse-directory-report",
    "bha-site-wide-coverage-ledger",
}

base.REPORTS = [
    item
    for item in base.REPORTS
    if item[0] not in SUPERSEDED_BASE_IDS
]

FOLLOWUP_REPORTS: list[tuple[str, str]] = [
    (
        "bha-horses-in-training-calculator-report",
        r"""## BHA Horses in Training Calculator — source-family conclusion

The BHA Rules and Guides area links a first-party **Horses in Training Calculator** at:

https://crate.horseracing.software/rulesbook/horsesintraining/

The application identifies itself as **Horse In Training Calculator - v1.1**.

### Rule represented by the calculator

The calculator states that Running Requirements Code paragraph 13 requires a horse to have been in training with an appropriately licensed trainer for the **fourteen clear days before the day of a race**.

This is a precise administrative eligibility rule and should not be approximated as simply `14 days` without preserving the wording `fourteen clear days before the day of a race`.

### Two calculation directions

The public utility supports two inverse questions:

1. **Arrived At Yard → Date to Race**
   - input the date on which a horse arrived at the yard;
   - receive the date from which it may race.

2. **Date of Race → required arrival date**
   - input a proposed race date;
   - receive the latest date by which the horse must have arrived at the yard.

### Grain and role

This is a **rule-calculation utility**, not a public horse-by-horse training-history database.

It is useful evidence for interpreting training-history and race-eligibility dates elsewhere in BHA data.

Sources:

- https://www.britishhorseracing.com/regulation/rules-guides/
- https://crate.horseracing.software/rulesbook/horsesintraining/
""",
    ),
    (
        "bha-vaccination-calculator-report",
        r"""## BHA Vaccination Calculator — source-family conclusion

The BHA Rules and Guides area links a first-party **Vaccination Calculator** at:

https://vaca.horseracing.software/

The utility is explicitly tied to the **BHA Rules of Racing – Vaccination Code**.

### Primary-course information demonstrated

The calculator exposes a primary course comprising:

- 1st Vaccination;
- 2nd Vaccination;
- 3rd Vaccination;
- subsequent boosters.

It also publishes the rule change that took effect on **1 January 2022**.

Observed interval table:

| Stage | Historic interval | Interval from 1 January 2022 |
|---|---:|---:|
| V2 | 21–92 days | 21–60 days |
| V3 | 150–215 days | 120–180 days |
| Booster | not more than 1 year apart | not more than 6 months apart |

### Transition rules stated by the calculator

- a horse with a compliant primary course and compliant subsequent boosters through 31 December 2021 did not have to restart vaccination;
- a primary course started by 31 December 2021 continued under the old intervals even where V2/V3 occurred in 2022;
- a primary course starting from 1 January 2022 must use the new intervals.

### Additional current racecourse-access rule

BHA rule-change material subsequently clarified that a horse must not enter racecourse property within **seven days of a vaccination** and that horses entering racecourse property must be fully compliant with the Vaccinations Code.

### Grain and role

This is a **rule/eligibility calculator**, not a public database of individual horses' vaccination records.

The BHA also refers to vaccination records being maintained/verified through the Weatherbys Vaccination App. Those individual records are not demonstrated as publicly downloadable from this calculator.

Sources:

- https://www.britishhorseracing.com/regulation/rules-guides/
- https://vaca.horseracing.software/
""",
    ),
    (
        "bha-racing-updates-hoy-final-report",
        r"""## BHA Racing Updates / HOY — source-family conclusion

The top-level **Racing updates** link exposes a distinct first-party live operational application at:

https://crate.horseracing.software/hoy/

The application identifies itself as **hoy v2.13**.

### Application behaviour

The interface supports:

- automatic checking for new updates;
- optional audio alerts;
- filtering by update type;
- remembered settings/filter choices via cookies.

It states that fixture dates and race times are shown in **GB / Europe-London time**, while other displayed times are local to the viewer.

### Public update families demonstrated

Indexed HOY output demonstrates at least:

- **GOING** updates;
- **WEATHER** updates;
- **Non-runner** updates.

This is materially richer than an ordinary news feed.

### Going update information demonstrated

Observed Going records can contain:

- update type;
- update timestamp;
- fixture date;
- racecourse;
- current going description;
- GoingStick value;
- GoingStick observation date/time;
- free-text course/condition notes;
- soil-moisture percentage where supplied.

Examples in indexed public output include GoingStick observations and soil-moisture readings for courses such as Brighton, Ffos Las and Windsor.

### Weather update information demonstrated

Observed Weather records can contain:

- fixture date;
- racecourse;
- update timestamp;
- free-text current/recent weather;
- recent rainfall amounts;
- forecast temperatures;
- forecast narrative extending to raceday.

### Non-runner update information demonstrated

Observed Non-runner records can contain:

- horse name and country suffix;
- fixture date;
- racecourse;
- scheduled race time;
- race title/class text;
- cloth number;
- stall number where applicable;
- colours image/description;
- stated reason for withdrawal.

Observed reason examples include `Going` and `Vets Cert (Pulled Shoe Off)`.

### Relationship to other BHA sources

HOY overlaps partly with fixture-going and non-runner information already observed elsewhere, but it provides a **live update/event presentation** with explicit update timestamps and operational free text.

Whether HOY retains a stable public historical archive, and the complete closed taxonomy of update types, remain unresolved.

BHA entry point: https://www.britishhorseracing.com/racing-updates/
""",
    ),
    (
        "bha-racecourse-directory-final-report",
        r"""## BHA Racecourse Directory — source-family conclusion

The current BHA racing site provides a public **Racecourses** directory.

The page currently states that there are **59 racecourses in Britain**, from Perth to Newton Abbot.

This is the BHA website directory's current racecourse count and must not be substituted automatically for the governed racecourse/course identity counts established elsewhere in Inside Rails.

### Discovery/search mechanisms

The public directory supports:

- interactive map;
- A–Z list;
- location/postcode search for the nearest racecourse.

### Racecourse information exposed by the page template

The current template demonstrates fields/concepts for:

- racecourse name;
- fixture type;
- track handedness;
- distance in miles from a supplied location;
- next fixture date;
- first race time at the next fixture.

The page's fixture-type filter exposes:

- Flat;
- Jump;
- Mixed.

### Current application condition

During the sweep the live page displayed **Error loading racecourses**, while the template fields remained visible in the HTML.

Therefore the field surface is demonstrated but a populated current 59-row dataset was not recovered by this web renderer.

Source: https://www.britishhorseracing.com/racing/racecourses/
""",
    ),
    (
        "bha-public-vs-internal-data-boundaries-report",
        r"""## BHA website sweep — known non-public/internal data boundaries

A full availability audit should record not only what is public but also important information systems that the BHA publicly says exist **without exposing their underlying records as public website data**.

### Integrity/race-analysis information

The BHA's Integrity material says analysts monitor betting markets and study races using speed maps and a database supplied by an industry software company to assess likely race shape, performance and betting behaviour.

The website describes this capability but does not expose that underlying analytical database publicly.

### Jockey medical/research information

BHA data-protection material describes medical/research databases used for jockey health, concussion and occupational-health research, with access restricted to appropriate medical/BHA personnel and controlled sharing.

Those individual medical records are not a public website dataset.

### Whole-life thoroughbred database

The Life After Racing material states that the BHA is developing an integrated whole-life thoroughbred database combining information from 30-day foal notification through racing and post-retirement.

The existence/development of that system is public information; its underlying individual records are not demonstrated as a public source.

### Why this distinction matters

> **BHA possesses or describes information** is not equivalent to **Inside Rails can obtain that information from the public BHA website**.

The site-wide catalogue therefore distinguishes public sources from known internal/non-public information systems rather than silently treating both as available.

Sources:

- https://www.britishhorseracing.com/regulation/integrity/intelligence/
- https://www.britishhorseracing.com/about/data-protection/
- https://www.britishhorseracing.com/regulation/life-after-racing/
""",
    ),
    (
        "bha-site-wide-final-coverage-ledger",
        r"""## BHA website sweep — final coverage ledger

This ledger records the distinct public information families demonstrated by the site-wide BHA sweep together with important known non-public boundaries.

`Reported earlier` means the family already has a dedicated investigation/conclusion in Notebook 27 before this sweep. `Reported in sweep` means a dedicated report is appended by the site-sweep completion helper. `Surface unresolved` means the public application is confirmed but its detailed measures/schema could not be recovered through the present web inspection.

| Information family | Principal grain | Delivery | Coverage status |
|---|---|---|---|
| Fixtures / fixture detail | fixture | structured service | Reported earlier |
| Fixture going / weather / watering / track state | fixture/track/time | structured service | Reported earlier |
| Fixture officials | fixture/person | structured service | Reported earlier |
| Races / race detail | race | structured service | Reported earlier |
| Entries | race/horse | structured service | Reported earlier |
| Nominations | race/horse | structured service | Reported earlier |
| Results | race/runner | structured service | Reported earlier |
| Balloted / trans routes | race/horse | structured service | Reported earlier; populated schema unresolved |
| Stewards Reports | fixture/race/document | PDF | Reported earlier |
| GoingStick current/archive | course/time | public archive | Reported earlier |
| Official Ratings database | horse | structured service/export | Reported earlier |
| Weekly rating changes / exports | horse | export | Reported earlier |
| Latest performance figures export | horse/recent-run sequence | CSV export | Reported earlier |
| Horse search/profile | horse | structured service | Reported earlier |
| Horse performances | horse/race | structured service | Reported earlier |
| Horse training history | horse/trainer/time | structured service | Reported earlier |
| Jockey profiles/championships | jockey/race/period | structured service | Reported earlier |
| Jockey winners totals since 1 Jan 1995 | jockey | dynamic table | Reported in sweep |
| Trainer profiles/performance | trainer/race | structured service | Reported earlier |
| Trainer non-runners | trainer/period | structured service | Reported earlier |
| Trainers Map | trainer/location | embedded app | Reported in sweep |
| Owner championships | owner/season | structured service | Reported earlier |
| Full-year Fixture List | fixture | XLSX/PDF | Reported earlier |
| Annual Racing Data Packs | annual aggregate | PDF | Reported in sweep |
| Monthly Racing Data Packs | monthly/YTD aggregate | PDF | Reported in sweep |
| Horse Population Reports | administrative horse population | PDF | Reported earlier |
| Race Off-Times | aggregate/course | PDF | Reported earlier |
| Industry Statistics / Dashing | interactive aggregate | embedded app | Surface unresolved; beta shell confirmed |
| Racing Updates / HOY | operational event/update | embedded app/indexed feed | Reported in sweep |
| Claiming-race records | claim/race/horse/claimer | dynamic search | Reported in sweep |
| Non-racing agreements | horse/agreement | dynamic search | Reported in sweep |
| Horse-name availability | candidate name | interactive utility | Reported in sweep |
| Racing colours | colours/availability/listing | utility + marketplace | Reported in sweep |
| Handicapping appeals | horse/decision | page + decisions | Reported in sweep |
| Ratings classifications | season/horse | documents/tables | Reported in sweep |
| Longines / Jump champion tables | season/category/horse | table/document | Reported in sweep |
| Rules of Racing | rule/version | rules microsite | Reported in sweep |
| General Instructions | operational rule/reference | PDFs | Reported in sweep |
| Vaccination Calculator | vaccination dates/rule | embedded utility | Reported in sweep |
| Horses in Training Calculator | arrival/race eligibility date | embedded utility | Reported in sweep |
| Weight-for-age scales | age/date/distance/code | documents | Reported in sweep |
| Participant licensing | participant/licence type | pages/forms/guides | Reported in sweep |
| Licensing Committee decisions | person/application/decision | Judicial Panel documents | Reported in sweep |
| Racecourse directory | course/current fixture context | dynamic directory | Reported in sweep |
| Racecourse licensing/technical documents | course/technical rule | PDFs/docs | Reported in sweep |
| Race-distance changes / starts / remeasurement | course/distance/start | documents/data files | Reported in sweep |
| Equine anti-doping testing | year/test type | table + rules/guides | Reported in sweep |
| Prohibited-substance/detection-time guidance | substance/procedure | documents | Reported in sweep |
| 30-day foal notification | foal/admin rule | process/page | Reported in sweep |
| Jockey human anti-doping testing | year/test method | table | Reported in sweep |
| Fatal-injury statistics | year/code | charts/tables | Reported in sweep |
| Whip referrals/offences | year/licence/offence | tables | Reported in sweep |
| Veterinary forms/notices | veterinary/admin event | documents/forms | Reported in sweep |
| Participant medical/concussion standards | participant/standard | pages/docs | Reported in sweep |
| Disqualified/Excluded persons | person/current status | dynamic search | Reported in sweep |
| Forfeit List / arrears | person/debt | dynamic search | Reported in sweep |
| Judicial disciplinary/appeal decisions | case/decision | searchable site/docs | Reported in sweep |
| Legacy Disciplinary Notices | case/document | BHA Search archive | Reported in sweep |
| Point-to-Point | fixture/horse/rider/rule | documents/links | Reported in sweep |
| Purebred Arabian racing | fixture/regulatory context | BHA page + linked authority | Reported in sweep |
| Ownership types/shared ownership | owner/admin structure | pages/docs | Reported in sweep |
| Sponsorship administration/codes | participant/agreement rules | pages/docs/forms | Reported in sweep |
| BHA Publications / Fact Books / Reviews | document/year | PDF archive | Reported in sweep |
| BHA Resource library | document/resource | site search | Reported in sweep |
| Press releases | event/document | searchable archive | Reported in sweep |
| News/blogs/posts/podcast | event/editorial | searchable archive | Reported in sweep |
| Industry links / external racing bodies | organisation | directory | Discovered reference surface |
| Industry strategy / research reports | study/strategy/document | pages/reports | Discovered reference surface |
| Racing Digital | future/admin platform context | page | Discovered; not demonstrated public data feed |
| BHA integrity race-analysis databases | race/betting analytical | internal/non-public | Known boundary |
| Jockey medical/research databases | jockey/medical | internal/non-public | Known boundary |
| Whole-life thoroughbred database | horse/life-course | developing internal system | Known boundary |

### Residual unresolved public surface

After the broad public-site sweep, the principal confirmed application whose **actual data measures remain insufficiently enumerated** is:

**Industry Statistics / Dashing** (`https://dashing.horseracing.software/`).

The BHA Racing Statistics page says its official PDF racing statistics can also be found on the Industry Statistics page, which indicates overlap with the already-mapped statistical material. The Dashing application itself currently exposes only its beta shell to this web inspection, including a warning that bugs/data issues may render information incorrect.

The exact dashboard tabs, measures, filtering dimensions and underlying calls therefore remain unresolved rather than being invented from the PDFs.

### Dynamic-backend boundary

For several public interactive services — for example Claims, Non-Racing Agreements, Racing Colours and Horse Name Availability — the user-facing information and grain have been demonstrated while the complete backend schema has not. A complete backend schema is not required to establish that the public information family exists, but would require a separate application-code/network probe if later acquisition is considered.

### Site-sweep conclusion

The broad BHA public website is not merely a results/ratings site. It exposes a combination of:

- structured fixture/race/participant data;
- live operational updates;
- current-state administrative registers;
- interactive eligibility/availability calculators;
- official aggregate statistics;
- racecourse technical data and standards;
- regulatory decisions;
- welfare, anti-doping and integrity statistics;
- historical reports/publications;
- rules, definitions and administrative guidance.

This sweep records availability and semantics. It does **not** decide which sources Inside Rails should acquire or govern.
""",
    ),
]


def append_followups() -> None:
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

    for cell_id, markdown in FOLLOWUP_REPORTS:
        heading = markdown.strip().splitlines()[0]
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
        print("No follow-up cells appended; all headings already exist.")
        return

    temp_path = NOTEBOOK_PATH.with_suffix(".ipynb.tmp")
    temp_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(NOTEBOOK_PATH)

    print(f"Appended {len(appended)} final sweep cells to {NOTEBOOK_PATH}")
    for heading in appended:
        print(f"  + {heading}")
    for heading in skipped:
        print(f"  = already present: {heading}")


def main() -> None:
    base.main()
    append_followups()


if __name__ == "__main__":
    main()
