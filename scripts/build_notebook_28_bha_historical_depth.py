from __future__ import annotations

from pathlib import Path
import shutil

import nbformat as nbf

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "notebooks" / "28_bha_historical_race_data_depth.ipynb"
CACHE_DIR = REPO_ROOT / "data" / "cache" / "bha_historical_race_data_depth"
BACKUP = CACHE_DIR / "notebook_28_pre_autonomous_backup.ipynb"


def md(text: str, *, tags: list[str] | None = None):
    cell = nbf.v4.new_markdown_cell(text.strip() + "\n")
    if tags:
        cell.metadata["tags"] = tags
    return cell


def code(text: str, *, tags: list[str] | None = None):
    cell = nbf.v4.new_code_cell(text.strip() + "\n")
    if tags:
        cell.metadata["tags"] = tags
    return cell


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        }
    )

    nb.cells = [
        md(
            """
# Notebook 28 — BHA historical race-data depth

## Purpose

This notebook establishes how far back the BHA provides usable official British fixture, race, result and runner information.

It follows two earlier pieces of work:

- **Notebook 26 — GB race-population completeness**, which established that Source Version 1 is materially incomplete for GB racing in parts of 2020 and therefore cannot be treated as the sole authority for complete historical race population.
- **Notebook 27 — BHA official-source feasibility**, which established that the BHA public estate exposes structured fixture, race and result resources and that historical depth varies by source family, but did not establish a governed historical boundary for detailed race data.

The research question is:

> **How far back does the BHA provide usable official fixture, race, result and runner data, and what source capabilities are available at each historical depth?**

Historical depth is tested separately for:

1. fixture discovery;
2. fixture administrative/status detail;
3. race-list availability;
4. race-detail availability;
5. official result availability;
6. runner-level result availability; and
7. evidence sufficient to distinguish programmed, abandoned and actually run racing.

This is a source-capability and provenance investigation. It is **not** a Database v5 design exercise.
"""
        ),
        md(
            """
## Evidence and access rules

The notebook uses the reusable `inside_rails.bha_api` client rather than embedding HTTP logic in research cells.

The client reproduces the access pattern used by the current public BHA Results frontend. The frontend Authorization value is recovered into memory only and is never printed or persisted. Cached BHA responses retain the request URL, parameters, response status, raw response, parsed payload, frontend asset fingerprint and access-profile provenance.

Important interpretation rules:

- a successful fixture-search response proves only fixture-index availability for that query;
- a fixture index record does **not** prove that fixture detail, race lists, race detail or results survive to the same depth;
- HTTP `404` on an individual historical resource is recorded as an absent resource, not a transport failure;
- HTTP `401`, `403`, `5xx`, authorization failure or transport failure aborts the study rather than being misclassified as a historical boundary;
- HTTP `200` with an empty `data` list is kept distinct from HTTP `404`;
- `resultsAvailable` is observed but is not treated as a complete semantic contract;
- race-list presence alone does not prove racing took place, because Notebook 26 demonstrated that programmed races can survive for an abandoned fixture;
- Source Version 1 may be used later for technical reconciliation, but not as substantive evidence for the BHA historical boundary.

The investigation is deliberately bounded. It uses representative historical windows, then refines only where the observed source families change state.
"""
        ),
        code(
            """
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pandas as pd

from inside_rails.bha_api import BhaApiClient, ACCESS_PROFILE, default_bha_cache_dir

# Resolve the repository explicitly so notebook execution is independent of the
# directory from which Jupyter was launched.
cwd = Path.cwd().resolve()
if (cwd / "NOTEBOOK_WORKING_RULES.md").exists():
    repo_root = cwd
elif (cwd.parent / "NOTEBOOK_WORKING_RULES.md").exists():
    repo_root = cwd.parent
else:
    raise RuntimeError(f"Could not identify Inside Rails repository root from {cwd}")

cache_dir = default_bha_cache_dir(repo_root, "bha_historical_race_data_depth")
cache_dir.mkdir(parents=True, exist_ok=True)

bha = BhaApiClient(cache_dir)

probe_records: list[dict] = []
year_results: dict[int, dict] = {}

print("repo_root:     ", repo_root)
print("cache_dir:     ", cache_dir)
print("BHA API:       ", bha.api_root)
print("access profile:", ACCESS_PROFILE)
print("Authorization value displayed: NO")
"""
        ),
        md(
            """
## Method

Two kinds of evidence are used.

### Anchors

First, the notebook reproduces observations already established in the preceding work:

- **27 May 2026** — the known modern control where the fixture search returns five result-bearing fixtures;
- **8 April 1995** — a known historical date where the fixture index has already been observed to return Aintree, Beverley and Hereford.

These anchors test that the reusable transport still behaves like the earlier work before historical conclusions are extended.

### Adaptive historical probing

For each sampled year the notebook:

1. searches a bounded seven-day April window;
2. if no fixtures are returned, tries a second seven-day September window;
3. samples at most two discovered fixtures for deeper endpoint testing;
4. tests fixture detail and fixture race lists independently;
5. where a race list survives, samples at most one addressable race per fixture;
6. tests race detail and official results independently;
7. records whether the result resource actually contains runner rows.

The initial years are deliberately sparse. Where an older sampled year lacks a capability and a newer sampled year has it, the notebook probes the intervening years only. This refines an observed transition without turning the study into a full-history download.

The resulting boundary is therefore an **observed public-resource boundary**, with explicit evidence strength. It is not assumed to be a contractual BHA retention guarantee.
"""
        ),
        code(
            """
def data_rows(response):
    \"\"\"Return a BHA payload's top-level data rows without assuming field semantics.\"\"\"
    payload = response.payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def require_interpretable(response, context: str):
    \"\"\"Fail closed on access/transport failures that cannot define history.\"\"\"
    status = response.response_status
    error_text = response.error or ""

    if status in {401, 403}:
        raise RuntimeError(f"{context}: access failure HTTP {status}: {error_text}")
    if status is not None and status >= 500:
        raise RuntimeError(f"{context}: server failure HTTP {status}: {error_text}")
    if status is None:
        raise RuntimeError(f"{context}: no interpretable HTTP status: {error_text}")
    if error_text.startswith(("authorization_error:", "url_error:", "timeout_error:")):
        raise RuntimeError(f"{context}: transport/access failure: {error_text}")


def response_outcome(response):
    \"\"\"Classify resource availability while keeping 200-empty distinct from 404.\"\"\"
    require_interpretable(response, response.candidate_identity)

    if response.response_status == 404:
        return "absent_404", 0

    if response.ok:
        rows = data_rows(response)
        if rows:
            return "available", len(rows)
        return "success_empty", 0

    return f"http_{response.response_status}", 0


def record_response(*, phase, year, window, capability, response, course=None,
                    fixture_id=None, race_ref=None, note=None):
    outcome, rows = response_outcome(response)
    probe_records.append(
        {
            "phase": phase,
            "year": year,
            "window": window,
            "capability": capability,
            "course": course,
            "fixture_id": fixture_id,
            "race_ref": race_ref,
            "http_status": response.response_status,
            "outcome": outcome,
            "data_rows": rows,
            "from_cache": response.from_cache,
            "cache_path": str(response.cache_path),
            "note": note,
        }
    )
    return outcome, rows


def fixture_search_all(from_date: str, to_date: str, *, results_available=None):
    \"\"\"Fetch every page for one bounded fixture-search window.\"\"\"
    first = bha.fixture_search(
        from_date,
        to_date,
        results_available=results_available,
        page=1,
        per_page=100,
    )
    require_interpretable(first, f"fixture search {from_date}..{to_date}")

    if not first.ok:
        return first, []

    rows = list(data_rows(first))
    last_page = int((first.payload or {}).get("last_page") or 1)

    for page in range(2, last_page + 1):
        response = bha.fixture_search(
            from_date,
            to_date,
            results_available=results_available,
            page=page,
            per_page=100,
        )
        require_interpretable(response, f"fixture search {from_date}..{to_date} page {page}")
        if not response.ok:
            raise RuntimeError(
                f"Fixture pagination changed state at page {page}: "
                f"HTTP {response.response_status}"
            )
        rows.extend(data_rows(response))

    return first, rows


def unique_fixture_sample(rows, limit=2):
    \"\"\"Take a bounded first/last fixture sample without duplicate identities.\"\"\"
    if not rows:
        return []

    candidates = [rows[0]]
    if len(rows) > 1:
        candidates.append(rows[-1])

    result = []
    seen = set()
    for row in candidates:
        key = (row.get("fixtureYear"), row.get("fixtureId"))
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result[:limit]


def first_addressable_race(rows):
    \"\"\"Return the first race row carrying the provenance tuple required by BHA routes.\"\"\"
    for row in rows:
        if (
            row.get("yearOfRace") is not None
            and row.get("raceId") is not None
            and row.get("divisionSequence") is not None
        ):
            return row
    return None


def probe_year(year: int, *, phase: str):
    \"\"\"Probe one year's source-family capability using at most two small windows.\"\"\"
    if year in year_results:
        return year_results[year]

    windows = [
        (f"{year}-04-01", f"{year}-04-07"),
        (f"{year}-09-01", f"{year}-09-07"),
    ]

    discovery_response = None
    fixtures = []
    used_window = None

    for start, end in windows:
        discovery_response, fixtures = fixture_search_all(start, end)
        used_window = f"{start}..{end}"

        probe_records.append(
            {
                "phase": phase,
                "year": year,
                "window": used_window,
                "capability": "fixture_discovery",
                "course": None,
                "fixture_id": None,
                "race_ref": None,
                "http_status": discovery_response.response_status,
                "outcome": "available" if fixtures else "success_empty",
                "data_rows": len(fixtures),
                "from_cache": discovery_response.from_cache,
                "cache_path": str(discovery_response.cache_path),
                "note": "bounded fixture-search window",
            }
        )

        if fixtures:
            break

    capability_observations = {
        "fixture_discovery": ["available" if fixtures else "success_empty"],
        "fixture_detail": [],
        "race_list": [],
        "race_detail": [],
        "official_results": [],
        "runner_level_results": [],
    }

    for fixture in unique_fixture_sample(fixtures):
        fixture_year = int(fixture.get("fixtureYear") or year)
        fixture_id = fixture.get("fixtureId")
        course = fixture.get("courseName")

        detail = bha.fixture_detail(fixture_year, fixture_id)
        detail_outcome, _ = record_response(
            phase=phase,
            year=year,
            window=used_window,
            capability="fixture_detail",
            response=detail,
            course=course,
            fixture_id=fixture_id,
        )
        capability_observations["fixture_detail"].append(detail_outcome)

        race_list = bha.fixture_races(fixture_year, fixture_id)
        race_list_outcome, race_count = record_response(
            phase=phase,
            year=year,
            window=used_window,
            capability="race_list",
            response=race_list,
            course=course,
            fixture_id=fixture_id,
        )
        capability_observations["race_list"].append(race_list_outcome)

        races = data_rows(race_list) if race_list_outcome == "available" else []
        race = first_addressable_race(races)

        if race is None:
            capability_observations["race_detail"].append("not_addressable")
            capability_observations["official_results"].append("not_addressable")
            capability_observations["runner_level_results"].append("not_addressable")
            continue

        year_of_race = int(race["yearOfRace"])
        race_id = race["raceId"]
        division = race["divisionSequence"]
        race_ref = f"{year_of_race}:{race_id}:{division}"

        race_detail = bha.race_detail(year_of_race, race_id, division)
        race_detail_outcome, _ = record_response(
            phase=phase,
            year=year,
            window=used_window,
            capability="race_detail",
            response=race_detail,
            course=course,
            fixture_id=fixture_id,
            race_ref=race_ref,
        )
        capability_observations["race_detail"].append(race_detail_outcome)

        results = bha.race_results(year_of_race, race_id, division)
        results_outcome, runner_rows = record_response(
            phase=phase,
            year=year,
            window=used_window,
            capability="official_results",
            response=results,
            course=course,
            fixture_id=fixture_id,
            race_ref=race_ref,
        )
        capability_observations["official_results"].append(results_outcome)
        capability_observations["runner_level_results"].append(
            "available" if results_outcome == "available" and runner_rows > 0
            else results_outcome
        )

    def summarise(values):
        values = [v for v in values if v != "not_addressable"]
        if not values:
            return "not_addressable"
        if "available" in values and any(v != "available" for v in values):
            return "mixed"
        if "available" in values:
            return "available"
        if all(v == "absent_404" for v in values):
            return "absent_404"
        if all(v == "success_empty" for v in values):
            return "success_empty"
        return "mixed"

    result = {
        "year": year,
        "window": used_window,
        "fixtures_found": len(fixtures),
        "capabilities": {
            capability: summarise(values)
            for capability, values in capability_observations.items()
        },
    }
    year_results[year] = result
    return result
"""
        ),
        md(
            """
## Phase 1 — modern control and 1995 anchor

The modern control is not a historical-depth inference. Its purpose is to prove that this notebook is still speaking to the same public BHA structured service used in the earlier 34/34 pilot.

The 1995 anchor then reproduces the first material historical observation: fixture discovery can survive even when deeper fixture resources do not.
"""
        ),
        code(
            """
# Modern control already established by Notebook 27.
modern_response, modern_rows = fixture_search_all(
    "2026-05-27",
    "2026-05-27",
    results_available=True,
)

assert modern_response.ok
assert len(modern_rows) == 5, (
    "Known modern BHA control changed: expected five fixtures on 2026-05-27, "
    f"found {len(modern_rows)}"
)

print("Modern control — 2026-05-27")
for row in modern_rows:
    print(
        row.get("courseName"),
        "| fixtureId=", row.get("fixtureId"),
        "| resultsAvailable=", row.get("resultsAvailable"),
    )

# Reproduce the known 1995 fixture-index observation.
anchor_response, anchor_rows = fixture_search_all("1995-04-08", "1995-04-08")

print("\nHistorical anchor — 1995-04-08")
print("fixtures:", len(anchor_rows))
for row in anchor_rows:
    print(
        row.get("courseName"),
        "| fixtureId=", row.get("fixtureId"),
        "| resultsAvailable=", row.get("resultsAvailable"),
        "| abandonedReasonCode=", row.get("abandonedReasonCode"),
    )

# Challenge every fixture on this bounded date at the next two source layers.
anchor_detail = []
anchor_races = []

for fixture in anchor_rows:
    fy = int(fixture["fixtureYear"])
    fid = fixture["fixtureId"]
    course = fixture.get("courseName")

    detail = bha.fixture_detail(fy, fid)
    races = bha.fixture_races(fy, fid)

    detail_outcome, _ = response_outcome(detail)
    races_outcome, _ = response_outcome(races)

    anchor_detail.append((course, detail.response_status, detail_outcome))
    anchor_races.append((course, races.response_status, races_outcome))

print("\n1995 fixture detail")
for item in anchor_detail:
    print(item)

print("\n1995 race lists")
for item in anchor_races:
    print(item)
"""
        ),
        md(
            """
### Anchor interpretation

The code above deliberately challenges the fixture-index result at deeper layers rather than treating `resultsAvailable=True` as proof that detailed historical result resources exist.

If the three 1995 fixture records are returned but their individual detail and race-list routes return `404`, the correct conclusion is a **source-family divergence**:

> the historical fixture catalogue survives deeper than the detailed fixture/race backend.

That finding is recorded as a bounded observation for 8 April 1995; it is not yet the exact transition date.
"""
        ),
        md(
            """
## Phase 2 — coarse historical capability sweep

The first pass uses sparse years chosen to span the known modern service, Source Version 1's 2015 start, the 2000s, the suspected older-backend transition, and the 1990s.

This is intentionally not a crawl. Each year uses at most two seven-day discovery windows and at most two fixture samples.
"""
        ),
        code(
            """
coarse_years = [
    2026,
    2020,
    2015,
    2010,
    2005,
    2001,
    2000,
    1999,
    1998,
    1995,
    1990,
    1985,
]

for year in coarse_years:
    result = probe_year(year, phase="coarse")
    print(year, result["fixtures_found"], result["capabilities"])

coarse_df = pd.DataFrame(
    [
        {
            "year": year,
            "window": year_results[year]["window"],
            "fixtures_found": year_results[year]["fixtures_found"],
            **year_results[year]["capabilities"],
        }
        for year in sorted(year_results, reverse=True)
    ]
)

coarse_df
"""
        ),
        md(
            """
## Phase 3 — adaptive boundary refinement

For each detailed source family, the notebook looks for an observed pair of sampled years where:

- the older year is `absent_404` or `success_empty`; and
- the newer year is `available`.

Only the intervening years are added. This is a conservative year-level refinement: it locates the transition band without assuming that a single sampled fixture proves every record in that year behaves identically.

Fixture discovery is refined similarly when an older sampled year has no records in either bounded window and a newer sampled year does.
"""
        ),
        code(
            """
capabilities = [
    "fixture_discovery",
    "fixture_detail",
    "race_list",
    "race_detail",
    "official_results",
    "runner_level_results",
]


def state(year, capability):
    return year_results[year]["capabilities"][capability]


def is_available(value):
    return value in {"available", "mixed"}


def is_nonavailable(value):
    return value in {"absent_404", "success_empty"}


def transition_intervals(capability):
    years = sorted(year_results)
    intervals = []

    for older, newer in zip(years, years[1:]):
        older_state = state(older, capability)
        newer_state = state(newer, capability)

        if is_nonavailable(older_state) and is_available(newer_state):
            intervals.append((older, newer))

    return intervals


# Iterate because adding an intermediate year can reveal a smaller transition interval.
for _ in range(4):
    missing_years = set()

    for capability in capabilities:
        for older, newer in transition_intervals(capability):
            if newer - older <= 1:
                continue
            missing_years.update(range(older + 1, newer))

    missing_years -= set(year_results)

    if not missing_years:
        break

    for year in sorted(missing_years):
        result = probe_year(year, phase="refinement")
        print("refined", year, result["capabilities"])


refined_df = pd.DataFrame(
    [
        {
            "year": year,
            "window": year_results[year]["window"],
            "fixtures_found": year_results[year]["fixtures_found"],
            **year_results[year]["capabilities"],
        }
        for year in sorted(year_results)
    ]
)

refined_df
"""
        ),
        md(
            """
## Phase 4 — administrative state: programmed, abandoned and actually run

Historical depth alone is not enough to construct a race population.

Notebook 26 already exposed the important counterexample: the BHA race-list resource can retain programmed races for a fixture that was wholly abandoned. This notebook rechecks that source behaviour against **Worcester on 25 September 2020**.

The purpose is not to redefine abandonment. It is to prove which BHA layers must be combined before a race can be treated as having actually taken place.
"""
        ),
        code(
            """
worcester_response, worcester_candidates = fixture_search_all(
    "2020-09-25",
    "2020-09-25",
)

worcester_rows = [
    row
    for row in worcester_candidates
    if str(row.get("courseName") or "").strip().lower() == "worcester"
]

print("Worcester fixture candidates:", len(worcester_rows))

admin_state_evidence = {}

if worcester_rows:
    fixture = worcester_rows[0]
    fy = int(fixture["fixtureYear"])
    fid = fixture["fixtureId"]

    detail = bha.fixture_detail(fy, fid)
    races = bha.fixture_races(fy, fid)

    require_interpretable(detail, "Worcester 2020 fixture detail")
    require_interpretable(races, "Worcester 2020 race list")

    detail_rows = data_rows(detail)
    race_rows = data_rows(races)
    detail_row = detail_rows[0] if detail_rows else {}

    admin_state_evidence = {
        "fixture_search_resultsAvailable": fixture.get("resultsAvailable"),
        "fixture_search_abandonedReasonCode": fixture.get("abandonedReasonCode"),
        "fixture_detail_status": detail.response_status,
        "fixture_detail_resultsAvailable": detail_row.get("resultsAvailable"),
        "fixture_detail_abandonedReasonCode": detail_row.get("abandonedReasonCode"),
        "fixture_detail_goingText": detail_row.get("goingText"),
        "race_list_status": races.response_status,
        "programmed_races_returned": len(race_rows),
    }

admin_state_evidence
"""
        ),
        md(
            """
## Phase 5 — consolidate evidence and derive observed boundaries

The summary below distinguishes three ideas:

- **earliest observed available year** — the oldest sampled/refined year where the capability produced usable rows;
- **latest older non-available sampled year** — the nearest older year observed as `404`/empty where one exists;
- **evidence status** — whether the result is an open-ended lower bound or a bracketed year-level transition.

A bracket is not silently promoted into an exact date boundary. Mixed behaviour remains mixed.
"""
        ),
        code(
            """
def boundary_summary(capability):
    rows = []

    for year in sorted(year_results):
        rows.append((year, state(year, capability)))

    available_years = [year for year, value in rows if is_available(value)]
    if not available_years:
        return {
            "capability": capability,
            "earliest_observed_available_year": None,
            "latest_older_nonavailable_year": None,
            "boundary_status": "no_available_sample",
        }

    earliest = min(available_years)
    older_nonavailable = [
        year
        for year, value in rows
        if year < earliest and is_nonavailable(value)
    ]

    latest_older = max(older_nonavailable) if older_nonavailable else None

    if latest_older is None:
        status = "open_ended_older_than_or_equal_to_observation"
    elif earliest - latest_older == 1:
        status = "bracketed_between_adjacent_year_samples"
    else:
        status = "bracketed_between_sampled_years"

    return {
        "capability": capability,
        "earliest_observed_available_year": earliest,
        "latest_older_nonavailable_year": latest_older,
        "boundary_status": status,
    }


boundary_rows = [boundary_summary(capability) for capability in capabilities]
boundary_df = pd.DataFrame(boundary_rows)

probe_df = pd.DataFrame(probe_records)

# Preserve compact derived evidence separately from the raw per-request BHA caches.
probe_matrix_path = cache_dir / "historical_depth_probe_matrix.csv"
boundary_path = cache_dir / "historical_depth_boundary_summary.json"

probe_df.to_csv(probe_matrix_path, index=False)

boundary_payload = {
    "research_question": (
        "How far back does the BHA provide usable official fixture, race, "
        "result and runner data?"
    ),
    "access_profile": ACCESS_PROFILE,
    "boundaries": boundary_rows,
    "year_capability_matrix": refined_df.to_dict(orient="records"),
    "admin_state_evidence": admin_state_evidence,
}

boundary_path.write_text(
    json.dumps(boundary_payload, indent=2, sort_keys=True),
    encoding="utf-8",
)

print("probe matrix:", probe_matrix_path)
print("boundary summary:", boundary_path)

boundary_df
"""
        ),
        md(
            """
## Interpretation rules for the conclusion

The generated conclusion below is based only on the responses preserved by this run.

In particular:

- “available to year X” means **demonstrated at least to that observed year**, not a contractual start date;
- an adjacent-year bracket is reported as a bracket unless the data establish something more exact;
- fixture discovery and detailed race/result resources are reported separately;
- a race list is described as a programme resource unless administrative/result evidence demonstrates that racing actually occurred;
- no Database v5 design follows automatically from these findings.
"""
        ),
        code(
            """
from IPython.display import Markdown, display


def boundary_sentence(row):
    capability = row["capability"].replace("_", " ")
    earliest = row["earliest_observed_available_year"]
    older = row["latest_older_nonavailable_year"]
    status = row["boundary_status"]

    if earliest is None:
        return f"- **{capability}:** no usable populated sample was demonstrated."

    if status == "bracketed_between_adjacent_year_samples":
        return (
            f"- **{capability}:** usable evidence is demonstrated in {earliest}; "
            f"the nearest older sampled year, {older}, was non-available, so the "
            f"observed year-level transition is bracketed between {older} and {earliest}."
        )

    if older is not None:
        return (
            f"- **{capability}:** usable evidence is demonstrated at least to {earliest}; "
            f"the nearest older non-available sampled year is {older}."
        )

    return (
        f"- **{capability}:** usable evidence is demonstrated at least to {earliest}; "
        "this run did not establish an older non-available boundary."
    )


sentences = [boundary_sentence(row) for row in boundary_rows]

anchor_lines = []
if anchor_rows:
    anchor_lines.append(
        f"On **8 April 1995**, fixture discovery returned **{len(anchor_rows)} fixtures**."
    )
if anchor_detail and all(status == 404 for _, status, _ in anchor_detail):
    anchor_lines.append(
        "All three corresponding fixture-detail requests returned **HTTP 404**."
    )
if anchor_races and all(status == 404 for _, status, _ in anchor_races):
    anchor_lines.append(
        "All three corresponding fixture-race-list requests returned **HTTP 404**."
    )

admin_lines = []
if admin_state_evidence:
    admin_lines.append(
        "The Worcester 25 September 2020 control again demonstrates that programme "
        "and execution state must be separated: a fixture can carry abandonment/admin "
        "evidence while the race-list layer still retains programmed race material."
    )

conclusion = "\n".join(
    [
        "# Conclusion — BHA historical race-data depth",
        "",
        "The BHA public structured estate does **not** have one historical start date. "
        "Its source families have different observed depths.",
        "",
        *anchor_lines,
        "",
        "## Observed capability boundaries",
        "",
        *sentences,
        "",
        "## Population implication",
        "",
        *admin_lines,
        "",
        "Fixture-index presence, race-list presence and an actually run race are not "
        "interchangeable concepts. Any future governed race-population work must use "
        "the smallest combination of official administrative and result evidence that "
        "can distinguish programmed, abandoned and realised racing.",
        "",
        "## Scope boundary",
        "",
        "This notebook establishes public-source capability and provenance only. It does "
        "**not** design Database v5, adopt BHA identifiers as Inside Rails identities, "
        "or decide which source families should be persisted rather than queried on demand.",
    ]
)

display(Markdown(conclusion))
""",
            tags=["conclusion-generator"],
        ),
        md(
            """
# Conclusion — pending execution

The autonomous runner replaces this placeholder with the evidence-derived Markdown conclusion after all probe cells execute successfully.
""",
            tags=["generated-conclusion"],
        ),
    ]

    return nb


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve the user's pre-autonomous local notebook exactly once.
    if TARGET.exists() and not BACKUP.exists():
        shutil.copy2(TARGET, BACKUP)
        print(f"Backed up existing Notebook 28 to: {BACKUP}")

    notebook = build_notebook()

    # Sanity-check every generated code cell before replacing the notebook.
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook28-cell-{index}", "exec")

    nbf.write(notebook, TARGET)
    print(f"Built Notebook 28: {TARGET}")
    print(f"Cells: {len(notebook.cells)}")


if __name__ == "__main__":
    main()
