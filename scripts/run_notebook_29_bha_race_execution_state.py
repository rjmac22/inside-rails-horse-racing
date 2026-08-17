from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
NOTEBOOK = REPO_ROOT / "notebooks" / "29_bha_race_execution_state.ipynb"
CACHE_DIR = REPO_ROOT / "data" / "cache" / "bha_race_execution_state"
BACKUP = CACHE_DIR / "notebook_29_pre_autonomous_backup.ipynb"


def md(text: str, *, tags: list[str] | None = None):
    cell = nbformat.v4.new_markdown_cell(text.strip() + "\n")
    if tags:
        cell.metadata["tags"] = tags
    return cell


def code(text: str, *, tags: list[str] | None = None):
    cell = nbformat.v4.new_code_cell(text.strip() + "\n")
    if tags:
        cell.metadata["tags"] = tags
    return cell


def build_notebook():
    nb = nbformat.v4.new_notebook()
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
# Notebook 29 — BHA race-level execution state

## Purpose

Notebook 28 established that fixture discovery, fixture administrative state, programmed races and realised official results are different evidence layers. It also showed that fixture-search `resultsAvailable=true` is not a safe completed-racing predicate.

Notebook 26 had already exposed two potentially important fields on individual BHA race records: `abandonedReasonCode` and `winnersDetails`.

The bounded question is:

> **What BHA race-level evidence reliably distinguishes a programmed Great Britain race that produced an official result from a programmed race that did not?**

For this notebook, **realised race** means a programmed BHA race whose dedicated official race-results resource contains one or more result rows. That matches the population-correctness question inherited from Notebook 26. It does not attempt to answer the subtly different physical question of whether a race started before later being voided or left without an official result.

The dedicated result resource is therefore the validation target. Race-level `abandonedReasonCode` and `winnersDetails` are candidate signals to be measured against it, not trusted from their names.

This notebook establishes source semantics and a candidate predicate only. It does **not** crawl every 2015-present race and does **not** authorise Database v5.

## Controlled evidence

The notebook starts with three deliberately different cases:

1. **27 May 2026** — completed-racing control. Notebook 26 previously reconciled 34 BHA races on this date and found no non-zero race-level abandonment codes or missing winner details.
2. **Uttoxeter, 13 February 2016** — programme-change control. A BHA notice dated 10 February 2016 states that two steeplechases were abandoned because of waterlogging while the fixture was being safeguarded as an all-hurdle card. Locator: `https://www.britishhorseracing.com/press_releases/all-hurdle-card-for-uttoxeter-on-13-february/`.
3. **1 April 2020** — programme-without-racing control during the COVID-19 suspension already governed in Notebook 28's external controls.

The external controls identify useful cases. The race-level classification itself comes from the structured BHA responses captured here.
"""
        ),
        code(
            r'''
from __future__ import annotations

import json
from pathlib import Path
import time

import pandas as pd
from IPython.display import Markdown, display

from inside_rails.bha_api import BhaApiClient, ACCESS_PROFILE, default_bha_cache_dir

# Resolve the repository explicitly so the notebook remains safe to run manually.
cwd = Path.cwd().resolve()
if (cwd / "NOTEBOOK_WORKING_RULES.md").exists():
    repo_root = cwd
elif (cwd.parent / "NOTEBOOK_WORKING_RULES.md").exists():
    repo_root = cwd.parent
else:
    raise RuntimeError(f"Could not identify repository root from {cwd}")

cache_dir = default_bha_cache_dir(repo_root, "bha_race_execution_state")
cache_dir.mkdir(parents=True, exist_ok=True)

bha = BhaApiClient(cache_dir)
LIVE_REQUEST_DELAY_SECONDS = 0.15

race_records: list[dict] = []
fixture_records: list[dict] = []
request_records: list[dict] = []

print("repo_root:     ", repo_root)
print("cache_dir:     ", cache_dir)
print("BHA API:       ", bha.api_root)
print("access profile:", ACCESS_PROFILE)
print("Authorization value displayed: NO")
'''
        ),
        md(
            """
## Method and safeguards

The investigation is deliberately staged.

### Resource layers

For each selected fixture the notebook retrieves:

- fixture-search evidence;
- fixture detail, used only as administrative context;
- the fixture-races resource, which supplies individual programmed race records;
- individual race detail for the same BHA race reference;
- the dedicated race-results resource.

The race-list and race-detail records are compared instead of assumed to be interchangeable.

### Candidate rules

For every addressable race the notebook tests whether official result presence is predicted by:

1. race-level `abandonedReasonCode == 0`;
2. non-empty race-level `winnersDetails`;
3. both together.

The three candidates are evaluated separately on the fixture-races record and the individual race-detail record.

### Failure handling

HTTP 401/403, server errors, authorization failures and transport failures abort the study. HTTP 404 and successful-empty results remain visible as source states. Every request is cached by the reusable BHA client; a small pacing delay is applied only to live requests.

### Scope control

After the three controls, the notebook challenges the signals using at most one ordinary fixture from each year 2015–2026. It does not escalate into an all-fixture crawl. Any contradiction becomes a named investigation queue; zero contradictions supports only a candidate for a later population-wide validation.
"""
        ),
        code(
            r'''
def data_rows(response):
    """Return top-level BHA `data` rows without inventing deeper semantics."""
    payload = response.payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    if isinstance(payload, list):
        return payload
    return []


def first_record(response):
    """Return the first data record, falling back to a direct dict payload."""
    rows = data_rows(response)
    if rows and isinstance(rows[0], dict):
        return rows[0]
    if isinstance(response.payload, dict):
        return response.payload
    return {}


def require_interpretable(response, context):
    """Fail closed when an HTTP outcome cannot be used as racing evidence."""
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


def logged(response, phase, capability, identity):
    """Preserve request provenance and pace only genuinely live calls."""
    require_interpretable(response, f"{phase}/{capability}/{identity}")
    request_records.append(
        {
            "phase": phase,
            "capability": capability,
            "identity": identity,
            "http_status": response.response_status,
            "ok": response.ok,
            "from_cache": response.from_cache,
            "cache_path": str(response.cache_path),
            "error": response.error,
        }
    )
    if not response.from_cache:
        time.sleep(LIVE_REQUEST_DELAY_SECONDS)
    return response


def fixture_search_all(start, end):
    """Fetch every page for one bounded fixture-search window."""
    first = logged(
        bha.fixture_search(start, end, page=1, per_page=100),
        "fixture_search",
        "fixture_discovery",
        f"{start}..{end}:1",
    )
    if not first.ok:
        return []
    rows = list(data_rows(first))
    last_page = int((first.payload or {}).get("last_page") or 1)
    for page in range(2, last_page + 1):
        response = logged(
            bha.fixture_search(start, end, page=page, per_page=100),
            "fixture_search",
            "fixture_discovery",
            f"{start}..{end}:{page}",
        )
        if not response.ok:
            raise RuntimeError(f"Fixture pagination failed on page {page}")
        rows.extend(data_rows(response))
    return rows


def as_int(value):
    if value in {None, ""}:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def list_count(value):
    return len(value) if isinstance(value, list) else None


def semantic_keys(record):
    tokens = ("abandon", "winner", "result", "status", "stage", "void")
    return sorted(
        key for key in record
        if any(token in key.lower() for token in tokens)
    )


def race_ref(race):
    year = race.get("yearOfRace")
    race_id = race.get("raceId")
    division = race.get("divisionSequence")
    if year is None or race_id is None or division is None:
        return None
    return int(year), race_id, division


def result_state(response):
    """Use the dedicated result resource as the realised-race validation target."""
    require_interpretable(response, response.candidate_identity)
    if response.response_status == 404:
        return "absent_404", 0
    if not response.ok:
        return f"http_{response.response_status}", 0
    rows = data_rows(response)
    return ("official_result_rows", len(rows)) if rows else ("success_empty", 0)
'''
        ),
        code(
            r'''
def probe_fixture(fixture, label, phase):
    """Preserve fixture context and compare three evidence layers for every race."""
    fixture_year = as_int(fixture.get("fixtureYear"))
    fixture_id = fixture.get("fixtureId")
    if fixture_year is None or fixture_id is None:
        raise RuntimeError(f"Fixture is not addressable: {fixture}")

    fixture_detail_response = logged(
        bha.fixture_detail(fixture_year, fixture_id),
        phase,
        "fixture_detail",
        f"{fixture_year}:{fixture_id}",
    )
    race_list_response = logged(
        bha.fixture_races(fixture_year, fixture_id),
        phase,
        "fixture_races",
        f"{fixture_year}:{fixture_id}",
    )

    fixture_detail = first_record(fixture_detail_response)
    races = data_rows(race_list_response)

    fixture_records.append(
        {
            "label": label,
            "phase": phase,
            "fixture_year": fixture_year,
            "fixture_id": fixture_id,
            "fixture_date": fixture.get("fixtureDate"),
            "course_name": fixture.get("courseName"),
            "search_abandoned_reason_code": as_int(fixture.get("abandonedReasonCode")),
            "search_results_available": fixture.get("resultsAvailable"),
            "detail_abandoned_reason_code": as_int(fixture_detail.get("abandonedReasonCode")),
            "detail_results_available": fixture_detail.get("resultsAvailable"),
            "detail_going_text": fixture_detail.get("goingText"),
            "programmed_races": len(races),
        }
    )

    if not race_list_response.ok:
        return

    for race in races:
        ref = race_ref(race)
        base = {
            "label": label,
            "phase": phase,
            "fixture_year": fixture_year,
            "fixture_id": fixture_id,
            "fixture_date": fixture.get("fixtureDate"),
            "course_name": fixture.get("courseName"),
            "race_time": race.get("raceTime"),
            "race_name": race.get("raceName"),
            "list_abandoned_reason_code": as_int(race.get("abandonedReasonCode")),
            "list_winner_count": list_count(race.get("winnersDetails")),
            "list_semantic_keys": semantic_keys(race),
        }

        if ref is None:
            race_records.append(
                {
                    **base,
                    "race_ref": None,
                    "detail_http_status": None,
                    "detail_abandoned_reason_code": None,
                    "detail_winner_count": None,
                    "detail_semantic_keys": [],
                    "results_http_status": None,
                    "results_state": "not_addressable",
                    "official_result_rows": 0,
                    "official_result_produced": None,
                }
            )
            continue

        year, race_id, division = ref
        ref_text = f"{year}:{race_id}:{division}"
        detail_response = logged(
            bha.race_detail(year, race_id, division),
            phase,
            "race_detail",
            ref_text,
        )
        results_response = logged(
            bha.race_results(year, race_id, division),
            phase,
            "race_results",
            ref_text,
        )

        detail = first_record(detail_response)
        results_kind, result_rows = result_state(results_response)

        race_records.append(
            {
                **base,
                "race_ref": ref_text,
                "detail_http_status": detail_response.response_status,
                "detail_abandoned_reason_code": as_int(detail.get("abandonedReasonCode")),
                "detail_winner_count": list_count(detail.get("winnersDetails")),
                "detail_semantic_keys": semantic_keys(detail),
                "results_http_status": results_response.response_status,
                "results_state": results_kind,
                "official_result_rows": result_rows,
                "official_result_produced": result_rows > 0,
            }
        )


def find_fixture(date_text, course_text):
    """Discover a control fixture from date/course rather than hard-code BHA ids."""
    fixtures = fixture_search_all(date_text, date_text)
    matches = [
        row for row in fixtures
        if course_text.lower() in str(row.get("courseName", "")).lower()
    ]
    if len(matches) != 1:
        print(
            f"CONTROL NOTE: expected one {course_text} fixture on {date_text}; "
            f"found {len(matches)}"
        )
        return None
    return matches[0]
'''
        ),
        md(
            """
## Phase 1 — controlled contradiction tests

The three controls are now acquired at individual-race grain.

The Uttoxeter case is deliberately allowed to fail as a *historical programme representation* without aborting the notebook. A pre-race abandoned/replaced race may have disappeared from the current final programme surface. If so, that is itself evidence about archive semantics; it must not be converted into a fake mixed-race observation.
"""
        ),
        code(
            r'''
# Completed-racing control: all five fixtures and every race on 27 May 2026.
completed_fixtures = fixture_search_all("2026-05-27", "2026-05-27")
if len(completed_fixtures) != 5:
    raise RuntimeError(
        f"Modern control changed: expected 5 fixtures, found {len(completed_fixtures)}"
    )
for fixture in completed_fixtures:
    probe_fixture(fixture, "completed_control_2026_05_27", "control_completed")

# Notebook 26 previously established 34 completed races on this date. Treat that as
# a schema/transport positive control: if the dedicated results resource no longer
# exposes result rows for all 34, stop before learning any execution-state rule.
completed_control_rows = [
    row for row in race_records
    if row["label"] == "completed_control_2026_05_27"
]
if len(completed_control_rows) != 34:
    raise RuntimeError(
        f"Modern race control changed: expected 34 race rows, found {len(completed_control_rows)}"
    )
if not all(row["official_result_produced"] is True for row in completed_control_rows):
    bad = [
        row["race_ref"] for row in completed_control_rows
        if row["official_result_produced"] is not True
    ]
    raise RuntimeError(
        "Dedicated result-resource positive control failed for known completed races: "
        f"{bad[:10]}"
    )

# Pre-race programme-change control: do not invent the two abandoned chases if the
# final structured archive only retains the revised card.
uttoxeter = find_fixture("2016-02-13", "Uttoxeter")
if uttoxeter is not None:
    probe_fixture(uttoxeter, "uttoxeter_2016_02_13", "control_programme_change")

# Programme-without-racing control during the governed 2020 suspension context.
suspended_fixtures = fixture_search_all("2020-04-01", "2020-04-01")
for fixture in suspended_fixtures:
    probe_fixture(fixture, "suspension_control_2020_04_01", "control_nonrealised")

control_df = pd.DataFrame(race_records)

print("Controlled fixture observations:", len(fixture_records))
print("Controlled race observations:", len(control_df))
print(
    control_df.groupby("label", dropna=False)[
        "official_result_produced"
    ].agg(["count", "sum"]).to_string()
)
'''
        ),
        md(
            """
## Candidate predicates and race-list/detail consistency

The next cell measures the candidate signals against the dedicated result endpoint. `official_result_produced` is not inferred from the candidate fields; it has already been derived from populated dedicated result rows.

It also checks whether the fixture-races record and individual race-detail record disagree on abandonment or winner counts.
"""
        ),
        code(
            r'''
def with_candidates(frame):
    out = frame.copy()
    out["list_abandonment_rule"] = out["list_abandoned_reason_code"] == 0
    out["list_winner_rule"] = out["list_winner_count"].fillna(0) > 0
    out["list_combined_rule"] = out["list_abandonment_rule"] & out["list_winner_rule"]
    out["detail_abandonment_rule"] = out["detail_abandoned_reason_code"] == 0
    out["detail_winner_rule"] = out["detail_winner_count"].fillna(0) > 0
    out["detail_combined_rule"] = out["detail_abandonment_rule"] & out["detail_winner_rule"]
    return out


def contradiction_table(frame):
    comparable = frame.loc[frame["official_result_produced"].notna()].copy()
    candidates = [
        "list_abandonment_rule",
        "list_winner_rule",
        "list_combined_rule",
        "detail_abandonment_rule",
        "detail_winner_rule",
        "detail_combined_rule",
    ]
    rows = []
    actual = comparable["official_result_produced"].astype(bool)
    for candidate in candidates:
        predicted = comparable[candidate].astype(bool)
        mismatch = predicted != actual
        rows.append(
            {
                "candidate": candidate,
                "races_tested": len(comparable),
                "contradictions": int(mismatch.sum()),
                "false_positive": int((predicted & ~actual).sum()),
                "false_negative": int((~predicted & actual).sum()),
            }
        )
    return pd.DataFrame(rows)


control_df = with_candidates(control_df)
control_candidates = contradiction_table(control_df)

abandonment_disagreement = control_df.loc[
    control_df["detail_http_status"].notna()
    & (
        control_df["list_abandoned_reason_code"].fillna(-999999)
        != control_df["detail_abandoned_reason_code"].fillna(-999999)
    )
]
winner_disagreement = control_df.loc[
    control_df["detail_http_status"].notna()
    & (
        control_df["list_winner_count"].fillna(-1)
        != control_df["detail_winner_count"].fillna(-1)
    )
]

print(control_candidates.to_string(index=False))
print("Race-list/detail abandonment disagreements:", len(abandonment_disagreement))
print("Race-list/detail winner-count disagreements:", len(winner_disagreement))
'''
        ),
        md(
            """
## Phase 2 — stratified temporal challenge

A rule that works only on obvious controls is not enough. The notebook therefore selects **one ordinary fixture per year from 2015 through 2026**.

To avoid accidentally sampling the same seasonal context every year, odd years use a 1–7 April window and even years use a 1–7 November window. The first addressable fixture in the returned window is selected deterministically. Control fixture identities are excluded.

Every race in the selected fixture is probed through race detail and dedicated results. The selection table is persisted so the sample is reproducible.

This remains a semantics challenge, not population validation.
"""
        ),
        code(
            r'''
control_keys = {(row["fixture_year"], row["fixture_id"]) for row in fixture_records}
selected = []

for year in range(2015, 2027):
    if year % 2:
        start, end, season = f"{year}-04-01", f"{year}-04-07", "spring"
    else:
        start, end, season = f"{year}-11-01", f"{year}-11-07", "autumn"

    fixtures = fixture_search_all(start, end)
    fixture = next(
        (
            row for row in fixtures
            if as_int(row.get("fixtureYear")) is not None
            and row.get("fixtureId") is not None
            and (as_int(row.get("fixtureYear")), row.get("fixtureId")) not in control_keys
        ),
        None,
    )

    if fixture is None:
        print(f"{year}: no addressable fixture selected from {start}..{end}")
        continue

    key = (as_int(fixture.get("fixtureYear")), fixture.get("fixtureId"))
    control_keys.add(key)
    selected.append(
        {
            "year": year,
            "season": season,
            "window": f"{start}..{end}",
            "fixture_date": fixture.get("fixtureDate"),
            "course_name": fixture.get("courseName"),
            "fixture_year": fixture.get("fixtureYear"),
            "fixture_id": fixture.get("fixtureId"),
        }
    )
    probe_fixture(fixture, f"stratified_{year}_{season}", "stratified")

selected_df = pd.DataFrame(selected)
print(selected_df.to_string(index=False))
'''
        ),
        md(
            """
## Full sampled contradiction test

The controls and stratified sample are now evaluated together.

The notebook also detects **mixed realised/non-realised fixtures** directly from the official result evidence. This is stronger than assuming a fixture-level abandonment field proves individual race state. If no mixed fixture survives in the current structured sample, the absence remains explicit rather than being manufactured from an old programme notice.
"""
        ),
        code(
            r'''
sampled_df = with_candidates(pd.DataFrame(race_records))
sampled_candidates = contradiction_table(sampled_df)

comparable = sampled_df.loc[sampled_df["official_result_produced"].notna()].copy()
comparable["official_result_produced"] = comparable["official_result_produced"].astype(bool)
realised_comparisons = int(comparable["official_result_produced"].sum())
nonrealised_comparisons = int(len(comparable) - realised_comparisons)

candidate_columns = [
    "list_abandonment_rule",
    "list_winner_rule",
    "list_combined_rule",
    "detail_abandonment_rule",
    "detail_winner_rule",
    "detail_combined_rule",
]
conflict_mask = pd.Series(False, index=comparable.index)
for column in candidate_columns:
    conflict_mask |= comparable[column] != comparable["official_result_produced"]
conflicts_df = comparable.loc[conflict_mask].copy()

mixed_fixture_summary = (
    comparable.groupby(["fixture_year", "fixture_id", "course_name"], dropna=False)
    ["official_result_produced"]
    .agg(["count", "sum"])
    .reset_index()
)
mixed_fixture_summary["nonrealised"] = (
    mixed_fixture_summary["count"] - mixed_fixture_summary["sum"]
)
mixed_fixtures_df = mixed_fixture_summary.loc[
    (mixed_fixture_summary["sum"] > 0)
    & (mixed_fixture_summary["nonrealised"] > 0)
].copy()

abandonment_disagreement_all = comparable.loc[
    comparable["detail_http_status"].notna()
    & (
        comparable["list_abandoned_reason_code"].fillna(-999999)
        != comparable["detail_abandoned_reason_code"].fillna(-999999)
    )
]
winner_disagreement_all = comparable.loc[
    comparable["detail_http_status"].notna()
    & (
        comparable["list_winner_count"].fillna(-1)
        != comparable["detail_winner_count"].fillna(-1)
    )
]

print("Sampled race rows:", len(sampled_df))
print("Addressable result comparisons:", len(comparable))
print("Realised comparisons:", realised_comparisons)
print("Non-realised comparisons:", nonrealised_comparisons)
print("Fixtures containing both realised and non-realised races:", len(mixed_fixtures_df))
print("Races conflicting with at least one candidate:", len(conflicts_df))
print()
print(sampled_candidates.to_string(index=False))

if not mixed_fixtures_df.empty:
    print("\nMixed fixtures:")
    print(mixed_fixtures_df.to_string(index=False))

if not conflicts_df.empty:
    display(
        conflicts_df[
            [
                "label",
                "course_name",
                "race_ref",
                "list_abandoned_reason_code",
                "list_winner_count",
                "detail_abandoned_reason_code",
                "detail_winner_count",
                "results_state",
                "official_result_rows",
                "official_result_produced",
            ]
        ]
    )
'''
        ),
        md(
            """
## Source-field inventory and persisted evidence

Field names are not semantic contracts, but the observed status/result-related keys are retained so later work can detect resource-family changes.

The notebook writes compact derived evidence to the ignored cache namespace. Raw BHA responses remain in the per-request `BhaApiClient` cache.

Derived artifacts:

- `race_execution_fixture_context.csv`;
- `race_execution_sample_matrix.csv`;
- `race_execution_candidate_summary.csv`;
- `race_execution_conflicts.csv`;
- `race_execution_mixed_fixtures.csv`;
- `race_execution_selected_fixtures.csv`;
- `race_execution_request_log.csv`;
- `race_execution_method_summary.json`.

These are research evidence, not database inputs.
"""
        ),
        code(
            r'''
list_keys = sorted(
    {
        key
        for keys in sampled_df["list_semantic_keys"]
        if isinstance(keys, list)
        for key in keys
    }
)
detail_keys = sorted(
    {
        key
        for keys in sampled_df["detail_semantic_keys"]
        if isinstance(keys, list)
        for key in keys
    }
)

print("Race-list status/result keys:", list_keys)
print("Race-detail status/result keys:", detail_keys)

fixture_df = pd.DataFrame(fixture_records)
request_df = pd.DataFrame(request_records)

paths = {
    "fixture_context": cache_dir / "race_execution_fixture_context.csv",
    "sample_matrix": cache_dir / "race_execution_sample_matrix.csv",
    "candidate_summary": cache_dir / "race_execution_candidate_summary.csv",
    "conflicts": cache_dir / "race_execution_conflicts.csv",
    "mixed_fixtures": cache_dir / "race_execution_mixed_fixtures.csv",
    "selected_fixtures": cache_dir / "race_execution_selected_fixtures.csv",
    "request_log": cache_dir / "race_execution_request_log.csv",
    "method_summary": cache_dir / "race_execution_method_summary.json",
}

fixture_df.to_csv(paths["fixture_context"], index=False)
sampled_df.to_csv(paths["sample_matrix"], index=False)
sampled_candidates.to_csv(paths["candidate_summary"], index=False)
conflicts_df.to_csv(paths["conflicts"], index=False)
mixed_fixtures_df.to_csv(paths["mixed_fixtures"], index=False)
selected_df.to_csv(paths["selected_fixtures"], index=False)
request_df.to_csv(paths["request_log"], index=False)

method_summary = {
    "question": (
        "What BHA race-level evidence reliably distinguishes a programmed GB race "
        "that produced an official result from one that did not?"
    ),
    "realised_race_target": "dedicated BHA race-results resource has result rows",
    "sampled_races": int(len(sampled_df)),
    "addressable_result_comparisons": int(len(comparable)),
    "realised_result_comparisons": realised_comparisons,
    "nonrealised_result_comparisons": nonrealised_comparisons,
    "mixed_fixture_count": int(len(mixed_fixtures_df)),
    "race_list_detail_abandonment_disagreements": int(len(abandonment_disagreement_all)),
    "race_list_detail_winner_disagreements": int(len(winner_disagreement_all)),
    "candidate_results": sampled_candidates.to_dict(orient="records"),
    "conflicting_races": int(len(conflicts_df)),
    "population_wide_validation_completed": False,
    "database_v5_authorised": False,
}
paths["method_summary"].write_text(
    json.dumps(method_summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

for name, path in paths.items():
    print(f"{name}: {path}")
'''
        ),
        md(
            """
## Evidence-derived conclusion

The final conclusion is generated from the observed contradiction counts. The runner promotes the rendered Markdown into the final notebook cell.

A zero-contradiction candidate is described only as **supported for population-wide validation** if the sample contains both realised and addressable non-realised races. Without negative evidence it remains merely uncontradicted and cannot be promoted.
"""
        ),
        code(
            r'''
rows = sampled_candidates.set_index("candidate").to_dict(orient="index")


def candidate_sentence(key, label):
    row = rows[key]
    if row["contradictions"] == 0 and nonrealised_comparisons == 0:
        return (
            f"- **{label}: not contradicted but insufficient** — 0 contradictions across "
            f"{row['races_tested']} addressable sampled races, but no addressable "
            "non-realised race was available to test false positives."
        )
    if row["contradictions"] == 0:
        return (
            f"- **{label}: supported for population-wide validation** — 0 contradictions across "
            f"{row['races_tested']} addressable sampled races, including "
            f"{nonrealised_comparisons} non-realised comparisons."
        )
    return (
        f"- **{label}: contradicted** — {row['contradictions']} contradictions "
        f"across {row['races_tested']} races "
        f"({row['false_positive']} false-positive, {row['false_negative']} false-negative)."
    )


supported = sampled_candidates.loc[
    sampled_candidates["contradictions"] == 0, "candidate"
].tolist()

if nonrealised_comparisons == 0:
    next_action = (
        "The sample contains no addressable non-realised race with which to challenge "
        "false positives. Do not scale acquisition. The next bounded problem is to "
        "locate or reconstruct an official BHA race-level non-realised control that "
        "remains addressable in the structured estate."
    )
elif supported:
    next_action = (
        "At least one race-level candidate survived the controlled and stratified tests. "
        "The next bounded problem is population-wide validation across all addressable "
        "GB races in 2015-present, designed around the cheapest surviving race-list "
        "signal and explicit investigation of any contradiction classes."
    )
else:
    next_action = (
        "No candidate survived. Do not scale acquisition. The next bounded problem is "
        "to explain the conflict classes in `race_execution_conflicts.csv`."
    )

conclusion = "\n".join(
    [
        "# Conclusion — BHA race-level execution state",
        "",
        "## Evidence tested",
        "",
        f"- Sampled race rows: **{len(sampled_df)}**.",
        f"- Addressable dedicated-result comparisons: **{len(comparable)}**.",
        f"- Realised comparisons: **{realised_comparisons}**.",
        f"- Non-realised comparisons: **{nonrealised_comparisons}**.",
        f"- Mixed realised/non-realised fixtures observed: **{len(mixed_fixtures_df)}**.",
        f"- Race-list/detail abandonment disagreements: **{len(abandonment_disagreement_all)}**.",
        f"- Race-list/detail winner-count disagreements: **{len(winner_disagreement_all)}**.",
        f"- Races conflicting with at least one candidate: **{len(conflicts_df)}**.",
        "",
        "## Candidate rules",
        "",
        candidate_sentence("list_abandonment_rule", "race-list `abandonedReasonCode == 0`"),
        candidate_sentence("list_winner_rule", "race-list `winnersDetails` non-empty"),
        candidate_sentence("list_combined_rule", "race-list abandonment + winner"),
        candidate_sentence("detail_abandonment_rule", "race-detail `abandonedReasonCode == 0`"),
        candidate_sentence("detail_winner_rule", "race-detail `winnersDetails` non-empty"),
        candidate_sentence("detail_combined_rule", "race-detail abandonment + winner"),
        "",
        "## Interpretation boundary",
        "",
        (
            "The dedicated BHA result resource is the realised-race validation target in "
            "this notebook. Fixture status remains administrative context; fixture-race-list "
            "presence remains programme evidence. A candidate field is not a governed "
            "completed-race predicate merely because it agrees in this sample."
        ),
        "",
        "No Database v5 change is authorised.",
        "",
        "## Next action",
        "",
        next_action,
    ]
)

display(Markdown(conclusion))
''',
            tags=["conclusion-generator"],
        ),
        md(
            """
# Conclusion pending execution

The autonomous runner replaces this placeholder with the evidence-derived Markdown emitted by the preceding cell.
""",
            tags=["generated-conclusion"],
        ),
    ]
    return nb


def prepare_pythonpath() -> None:
    """Expose the src-layout package to both this process and the Jupyter kernel."""
    src_text = str(SRC_DIR)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
    current = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    if src_text not in current:
        os.environ["PYTHONPATH"] = os.pathsep.join([src_text, *current])

    from inside_rails.bha_api import ACCESS_PROFILE

    print(f"Repository src path: {SRC_DIR}")
    print(f"BHA client import preflight: PASS ({ACCESS_PROFILE})")


def promote_conclusion(notebook) -> None:
    generator = None
    target = None
    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        if "conclusion-generator" in tags:
            generator = cell
        if "generated-conclusion" in tags:
            target = cell
    if generator is None or target is None:
        raise RuntimeError("Notebook 29 conclusion tags are missing")

    markdown = None
    for output in generator.get("outputs", []):
        if output.get("output_type") not in {"display_data", "execute_result"}:
            continue
        value = output.get("data", {}).get("text/markdown")
        if value is not None:
            markdown = "".join(value) if isinstance(value, list) else str(value)
            break
    if not markdown:
        raise RuntimeError("Notebook 29 did not emit evidence-derived Markdown")
    target.source = markdown.rstrip() + "\n"


def main() -> None:
    prepare_pythonpath()
    notebook = build_notebook()

    # Compile every generated code cell before replacing/creating the notebook.
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook29-cell-{index}", "exec")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if NOTEBOOK.exists() and not BACKUP.exists():
        shutil.copy2(NOTEBOOK, BACKUP)
        print(f"Backed up existing Notebook 29 to: {BACKUP}")

    nbformat.write(notebook, NOTEBOOK)

    # Round-trip validation catches malformed JSON/source before any live BHA request.
    checked = nbformat.read(NOTEBOOK, as_version=4)
    for index, cell in enumerate(checked.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook29-roundtrip-{index}", "exec")

    print(f"Built Notebook 29: {NOTEBOOK}")
    print(f"Cells: {len(checked.cells)}")
    print("Generated code-cell compile check: PASS")
    print("Notebook round-trip check: PASS")

    client = NotebookClient(
        notebook,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPO_ROOT)}},
        allow_errors=False,
    )

    print("Executing Notebook 29 autonomously...")
    try:
        client.execute()
        promote_conclusion(notebook)
    except Exception:
        nbformat.write(notebook, NOTEBOOK)
        print(
            f"Notebook execution failed; partial outputs saved to {NOTEBOOK}",
            file=sys.stderr,
        )
        raise

    nbformat.write(notebook, NOTEBOOK)
    print(f"Executed Notebook 29 saved to: {NOTEBOOK}")
    print(f"Evidence cache: {CACHE_DIR}")


if __name__ == "__main__":
    main()
