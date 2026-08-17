from __future__ import annotations

import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import nbformat

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
NOTEBOOK = REPO_ROOT / "notebooks" / "28_bha_historical_race_data_depth.ipynb"
CACHE_DIR = REPO_ROOT / "data" / "cache" / "bha_historical_race_data_depth"
DIAGNOSTIC_JSON = CACHE_DIR / "historical_depth_query_mode_refinement.json"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from inside_rails.bha_api import ACCESS_PROFILE, BhaApiClient  # noqa: E402


# Each date has independent evidence that British racing either occurred or, in the
# 2020 control, was formally suspended. This lets us separate query behaviour from
# historical source coverage.
CASES = [
    (
        "1994-04-09",
        "1994 known-racing control",
        "Aintree Grand National ran on this date",
        "https://www.racingpost.com/results/32/aintree/1994-04-09/57601",
    ),
    (
        "1995-04-08",
        "1995 BHA anchor",
        "existing Notebook 28 fixture-discovery anchor",
        None,
    ),
    (
        "2020-04-01",
        "2020 suspended-racing control",
        "British racing was suspended from 18 March through April",
        "https://www.britishhorseracing.com/press_releases/26644/",
    ),
    (
        "2022-04-09",
        "2022 known-racing control",
        "Aintree Grand National Festival",
        "https://www.britishhorseracing.com/the-2022-grand-national-festival-blog/",
    ),
    (
        "2023-04-15",
        "2023 known-racing control",
        "Aintree Grand National",
        "https://www.britishhorseracing.com/press_releases/bha-statement-following-the-2023-grand-national/",
    ),
    (
        "2024-04-13",
        "2024 known-racing control",
        "Aintree fixture in BHA Programme Book update",
        "https://www.britishhorseracing.com/2024-programme-book-2-update/",
    ),
    (
        "2025-03-14",
        "2025 known-racing control",
        "Cheltenham fixture in BHA Programme Book update",
        "https://www.britishhorseracing.com/2025-programme-book-1-update/",
    ),
    (
        "2026-05-27",
        "2026 modern control",
        "existing Notebook 27/28 five-fixture control",
        None,
    ),
]

YEAR_STATE_RE = re.compile(r"^(?:refined )?(\d{4})\s+(\d+)\s+(\{.*\})$")


def rows(response):
    payload = response.payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def require_interpretable(response, label: str) -> None:
    status = response.response_status
    if status in {401, 403}:
        raise RuntimeError(f"{label}: access failure HTTP {status}: {response.error}")
    if status is None:
        raise RuntimeError(f"{label}: no HTTP status: {response.error}")
    if status >= 500:
        raise RuntimeError(f"{label}: server failure HTTP {status}: {response.error}")


def probe(bha: BhaApiClient, race_date: str, results_available: bool | None) -> dict:
    response = bha.fixture_search(
        race_date,
        race_date,
        results_available=results_available,
        page=1,
        per_page=100,
    )
    mode = (
        "unfiltered"
        if results_available is None
        else "resultsAvailable=true"
        if results_available
        else "resultsAvailable=false"
    )
    require_interpretable(response, f"{race_date} {mode}")
    data = rows(response) if response.ok else []
    return {
        "mode": mode,
        "status": response.response_status,
        "fixture_count": len(data),
        "courses": [item.get("courseName") for item in data],
        "fixture_ids": [item.get("fixtureId") for item in data],
        "cache_path": str(response.cache_path),
        "from_cache": response.from_cache,
    }


def extract_year_states(notebook) -> dict[int, dict]:
    states: dict[int, dict] = {}
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") != "stream":
                continue
            text = output.get("text", "")
            if isinstance(text, list):
                text = "".join(text)
            for line in str(text).splitlines():
                match = YEAR_STATE_RE.match(line.strip())
                if match:
                    states[int(match.group(1))] = ast.literal_eval(match.group(3))
    return states


def query(case: dict, mode: str) -> dict:
    for item in case["queries"]:
        if item["mode"] == mode:
            return item
    raise KeyError((case["date"], mode))


def compact(item: dict) -> str:
    if not item["fixture_count"]:
        return f"HTTP {item['status']}; 0 fixtures"
    course_text = ", ".join(str(value) for value in item["courses"][:4])
    if item["fixture_count"] > 4:
        course_text += f", +{item['fixture_count'] - 4} more"
    return f"HTTP {item['status']}; {item['fixture_count']} fixtures ({course_text})"


def build_table(case_results: list[dict]) -> str:
    lines = [
        "| Date | Control | Unfiltered `/fixtures` | `resultsAvailable=true` |",
        "|---|---|---|---|",
    ]
    for case in case_results:
        lines.append(
            "| "
            + case["date"]
            + " | "
            + case["label"]
            + " | "
            + compact(query(case, "unfiltered"))
            + " | "
            + compact(query(case, "resultsAvailable=true"))
            + " |"
        )
    return "\n".join(lines)


def build_conclusion(case_results: list[dict], states: dict[int, dict], worcester: dict) -> str:
    by_date = {case["date"]: case for case in case_results}

    y1994_u = query(by_date["1994-04-09"], "unfiltered")["fixture_count"]
    y1994_r = query(by_date["1994-04-09"], "resultsAvailable=true")["fixture_count"]
    y1995_u = query(by_date["1995-04-08"], "unfiltered")["fixture_count"]
    y1995_r = query(by_date["1995-04-08"], "resultsAvailable=true")["fixture_count"]

    if y1994_u == 0 and y1994_r == 0 and max(y1995_u, y1995_r) > 0:
        fixture_lower_edge = (
            "A known racing date in 1994 (Aintree, 9 April) is empty in both tested "
            "fixture-search modes, while the 8 April 1995 anchor is populated. That is "
            "strong **observed lower-edge evidence around 1995** for the current fixture "
            "surface, not a contractual retention guarantee."
        )
    else:
        fixture_lower_edge = (
            "The known-racing 1994/1995 controls do not produce a clean lower-edge split, "
            "so the fixture-search start boundary remains unresolved."
        )

    modern_dates = ["2022-04-09", "2023-04-15", "2024-04-13", "2025-03-14"]
    query_mode_only = []
    both_empty = []
    for race_date in modern_dates:
        case = by_date[race_date]
        unfiltered = query(case, "unfiltered")["fixture_count"]
        completed = query(case, "resultsAvailable=true")["fixture_count"]
        if unfiltered == 0 and completed > 0:
            query_mode_only.append(race_date)
        elif unfiltered == 0 and completed == 0:
            both_empty.append(race_date)

    if query_mode_only and not both_empty:
        modern_text = (
            "The apparent 2022–2025 gap from the first pass is **query-mode dependent**: "
            "known racing dates that were empty in unfiltered searches become populated "
            "with `resultsAvailable=true`. Historical fixture discovery therefore cannot "
            "be characterised from unfiltered queries alone."
        )
    elif both_empty:
        modern_text = (
            "At least some independently known racing dates in 2022–2025 are empty in both "
            "tested query modes. The public structured surface therefore has a **modern "
            "historical availability anomaly/gap** and cannot be treated as a continuous "
            "archive merely because older and current years are populated."
        )
    else:
        modern_text = (
            "The known-racing-date controls do not reproduce the first-pass 2022–2025 "
            "pattern consistently; the apparent gap remains unresolved query behaviour."
        )

    suspended = by_date["2020-04-01"]
    suspended_u = query(suspended, "unfiltered")["fixture_count"]
    suspended_r = query(suspended, "resultsAvailable=true")["fixture_count"]
    if suspended_u > 0 and suspended_r == 0:
        programme_text = (
            "The 1 April 2020 control gives a clean semantic result: unfiltered fixture "
            "search retains programmed fixtures during the BHA's suspended-racing period, "
            "while `resultsAvailable=true` returns none. Fixture discovery is therefore "
            "programme/admin evidence, not proof that racing occurred."
        )
    else:
        programme_text = (
            "The 1 April 2020 query-mode control does not give a clean programmed-versus-"
            "completed split; the earlier Notebook 26 population evidence remains the "
            "stronger basis for programme/execution semantics."
        )

    state_1999 = states[1999]
    state_2000 = states[2000]

    fixture_detail_line = (
        "- **Fixture detail:** sampled 1999 requests return direct HTTP 404, while sampled "
        "2000 requests are populated. This is a directly observed sampled 1999→2000 "
        "lower-edge split."
        if state_1999.get("fixture_detail") == "absent_404"
        and state_2000.get("fixture_detail") == "available"
        else "- **Fixture detail:** the lower edge remains unresolved."
    )
    race_list_line = (
        "- **Fixture race lists:** sampled 1999 requests return direct HTTP 404, while "
        "sampled 2000 requests are populated. This is another directly observed sampled "
        "1999→2000 lower-edge split."
        if state_1999.get("race_list") == "absent_404"
        and state_2000.get("race_list") == "available"
        else "- **Fixture race lists:** the lower edge remains unresolved."
    )

    if worcester["found"]:
        worcester_text = (
            "The Worcester 25 September 2020 abandoned-fixture control was recovered in "
            f"`{worcester['found_in_mode']}` mode. Its detail and race-list evidence is "
            "preserved in the refinement section."
        )
    else:
        worcester_text = (
            "The Worcester 25 September 2020 re-probe did not recover a Worcester fixture "
            "from the tested query modes. Notebook 28 therefore does **not** claim that this "
            "run independently re-demonstrated the earlier Worcester control; Notebook 26's "
            "observation remains separate prior evidence."
        )

    parts = [
        "# Audited conclusion — BHA historical race-data depth",
        "",
        "The important result is **not a single start year**. The current BHA structured "
        "surface has different depths by resource family, query-mode effects, and partial "
        "or non-contiguous behaviour in some sampled periods.",
        "",
        "## Fixture discovery",
        "",
        fixture_lower_edge,
        "",
        modern_text,
        "",
        "## Detailed fixture/race/result resources",
        "",
        fixture_detail_line,
        race_list_line,
        "- **Race detail:** populated responses are demonstrated from sampled 2000 races. "
        "Pre-2000 races were `not_addressable` because the fixture race-list chain failed, "
        "so this notebook does **not** establish a direct race-detail endpoint start date.",
        "- **Official results and runner-level results:** populated responses are also "
        "demonstrated from sampled 2000 races, but their direct pre-2000 endpoint boundary "
        "remains unresolved for the same reason.",
        "",
        "## Programme state versus racing that actually occurred",
        "",
        programme_text,
        "",
        worcester_text,
        "",
        "Fixture-index presence, race-list presence and an actually run race are different "
        "evidence states and must not be collapsed into one population flag.",
        "",
        "## Practical source-capability conclusion",
        "",
        "1. Fixture discovery is observed on known racing dates from 1995; the 1994 control "
        "is lower-edge evidence rather than a contractual start date.",
        "2. Fixture detail and fixture race lists have a directly observed sampled lower edge "
        "between 1999 and 2000.",
        "3. Race detail, official results and runner rows are demonstrated from sampled 2000 "
        "races, but their direct pre-2000 endpoint boundary is unresolved.",
        "4. Historical fixture searching is sensitive to query semantics and/or archive "
        "population, so continuity must be tested rather than assumed.",
        "5. The structured service alone is not yet proven to be a continuous, complete "
        "official historical race-population source across every year and resource family.",
        "",
        "No Database v5 design or import decision follows automatically from this notebook.",
    ]
    return "\n".join(parts)


def main() -> None:
    if not NOTEBOOK.is_file():
        raise FileNotFoundError(NOTEBOOK)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    states = extract_year_states(notebook)
    if 1999 not in states or 2000 not in states:
        raise RuntimeError("Notebook 28 is missing the executed 1999/2000 probe states.")

    bha = BhaApiClient(CACHE_DIR)
    case_results = []
    for race_date, label, context, source in CASES:
        result = {
            "date": race_date,
            "label": label,
            "context": context,
            "external_source": source,
            "queries": [probe(bha, race_date, None), probe(bha, race_date, True)],
        }
        case_results.append(result)
        print(
            race_date,
            "| unfiltered:", result["queries"][0]["fixture_count"],
            "| resultsAvailable=true:", result["queries"][1]["fixture_count"],
        )

    worcester_queries = [
        probe(bha, "2020-09-25", None),
        probe(bha, "2020-09-25", True),
        probe(bha, "2020-09-25", False),
    ]
    worcester = {"found": False, "queries": worcester_queries}

    for item in worcester_queries:
        for course, fixture_id in zip(item["courses"], item["fixture_ids"]):
            if str(course or "").strip().lower() != "worcester":
                continue
            worcester["found"] = True
            worcester["found_in_mode"] = item["mode"]
            worcester["fixture_id"] = fixture_id

            detail = bha.fixture_detail(2020, fixture_id)
            race_list = bha.fixture_races(2020, fixture_id)
            require_interpretable(detail, "Worcester fixture detail")
            require_interpretable(race_list, "Worcester race list")
            detail_data = rows(detail)
            detail_row = detail_data[0] if detail_data else {}
            worcester["detail"] = {
                "status": detail.response_status,
                "resultsAvailable": detail_row.get("resultsAvailable"),
                "abandonedReasonCode": detail_row.get("abandonedReasonCode"),
                "goingText": detail_row.get("goingText"),
                "cache_path": str(detail.cache_path),
            }
            worcester["race_list"] = {
                "status": race_list.response_status,
                "race_count": len(rows(race_list)),
                "cache_path": str(race_list.cache_path),
            }
            break
        if worcester["found"]:
            break

    conclusion = build_conclusion(case_results, states, worcester)

    DIAGNOSTIC_JSON.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "access_profile": ACCESS_PROFILE,
                "cases": case_results,
                "worcester": worcester,
                "existing_year_states": states,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    # Remove any prior refinement section so the script is idempotent.
    cleaned = []
    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        if "historical-depth-audit-results" in tags:
            continue
        cleaned.append(cell)
    notebook.cells = cleaned

    table = build_table(case_results)
    sources = "\n".join(
        f"- {case['date']} — {case['context']}"
        + (f" — {case['external_source']}" if case["external_source"] else "")
        for case in case_results
    )
    worcester_detail = (
        f"Recovered via `{worcester['found_in_mode']}` with fixtureId "
        f"`{worcester['fixture_id']}`. Detail: `{worcester.get('detail')}`. "
        f"Race list: `{worcester.get('race_list')}`."
        if worcester["found"]
        else "No Worcester fixture was returned by unfiltered, result-bearing or non-result-bearing searches."
    )

    refinement = nbformat.v4.new_markdown_cell(
        "\n".join(
            [
                "## Audit refinement — known-racing dates and fixture query mode",
                "",
                "The first autonomous pass exposed two issues that must not be mistaken for a "
                "historical boundary: `not_addressable` is not a direct endpoint 404, and the "
                "fixture search showed non-monotonic modern behaviour. This refinement tests "
                "known racing dates both unfiltered and with `resultsAvailable=true`.",
                "",
                "The requests were executed by `scripts/refine_notebook_28_bha_historical_depth.py` "
                "through the same governed `BhaApiClient`. Every response is cached in the same "
                "Notebook 28 cache namespace.",
                "",
                table,
                "",
                "### Independent date/context controls",
                "",
                sources,
                "",
                "### Worcester abandoned-fixture re-probe",
                "",
                f"Recovered Worcester fixture: **{worcester['found']}**.",
                "",
                worcester_detail,
            ]
        )
    )
    refinement.metadata["tags"] = ["historical-depth-audit-results"]

    conclusion_index = len(notebook.cells)
    for index, cell in enumerate(notebook.cells):
        if "generated-conclusion" in set(cell.metadata.get("tags", [])):
            conclusion_index = index
            break
    notebook.cells.insert(conclusion_index, refinement)

    replaced = False
    for cell in notebook.cells:
        if "generated-conclusion" in set(cell.metadata.get("tags", [])):
            cell.source = conclusion.rstrip() + "\n"
            cell.metadata["tags"] = ["generated-conclusion", "audited-conclusion"]
            replaced = True
            break
    if not replaced:
        cell = nbformat.v4.new_markdown_cell(conclusion.rstrip() + "\n")
        cell.metadata["tags"] = ["generated-conclusion", "audited-conclusion"]
        notebook.cells.append(cell)

    nbformat.write(notebook, NOTEBOOK)

    print(f"Diagnostic evidence: {DIAGNOSTIC_JSON}")
    print(f"Audited Notebook 28: {NOTEBOOK}")
    print()
    print(conclusion)


if __name__ == "__main__":
    main()
