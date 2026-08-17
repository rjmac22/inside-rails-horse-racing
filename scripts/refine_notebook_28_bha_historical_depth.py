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

from inside_rails.bha_api import BhaApiClient, ACCESS_PROFILE  # noqa: E402


# These dates are not arbitrary. Each is independently known to have British racing
# or, for 2020-04-01, to fall inside the BHA's formally suspended-racing period.
# The purpose is to distinguish a source-history gap from a query-mode artefact.
DIAGNOSTIC_CASES = [
    {
        "date": "1994-04-09",
        "label": "1994 known-racing control",
        "context": "Aintree Grand National ran on this date",
        "external_source": "https://www.racingpost.com/results/32/aintree/1994-04-09/57601",
    },
    {
        "date": "1995-04-08",
        "label": "1995 BHA anchor",
        "context": "existing Notebook 28 fixture-discovery anchor",
        "external_source": None,
    },
    {
        "date": "2020-04-01",
        "label": "2020 suspended-racing control",
        "context": "British racing was suspended from 18 March through April",
        "external_source": "https://www.britishhorseracing.com/press_releases/26644/",
    },
    {
        "date": "2022-04-09",
        "label": "2022 known-racing control",
        "context": "Aintree Grand National Festival",
        "external_source": "https://www.britishhorseracing.com/the-2022-grand-national-festival-blog/",
    },
    {
        "date": "2023-04-15",
        "label": "2023 known-racing control",
        "context": "Aintree Grand National",
        "external_source": "https://www.britishhorseracing.com/press_releases/bha-statement-following-the-2023-grand-national/",
    },
    {
        "date": "2024-04-13",
        "label": "2024 known-racing control",
        "context": "Aintree fixture listed in BHA Programme Book update",
        "external_source": "https://www.britishhorseracing.com/2024-programme-book-2-update/",
    },
    {
        "date": "2025-03-14",
        "label": "2025 known-racing control",
        "context": "Cheltenham fixture listed in BHA Programme Book update",
        "external_source": "https://www.britishhorseracing.com/2025-programme-book-1-update/",
    },
    {
        "date": "2026-05-27",
        "label": "2026 modern control",
        "context": "existing Notebook 27/28 five-fixture results control",
        "external_source": None,
    },
]


LINE_PATTERN = re.compile(r"^(?:refined )?(\d{4})\s+(\d+)\s+(\{.*\})$")


def _rows(response):
    payload = response.payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def _require_interpretable(response, context: str) -> None:
    status = response.response_status
    error_text = response.error or ""
    if status in {401, 403}:
        raise RuntimeError(f"{context}: access failure HTTP {status}: {error_text}")
    if status is None:
        raise RuntimeError(f"{context}: no HTTP status: {error_text}")
    if status >= 500:
        raise RuntimeError(f"{context}: server failure HTTP {status}: {error_text}")


def _probe_fixture_search(bha: BhaApiClient, race_date: str, mode: bool | None) -> dict:
    response = bha.fixture_search(
        race_date,
        race_date,
        results_available=mode,
        page=1,
        per_page=100,
    )
    mode_name = (
        "unfiltered"
        if mode is None
        else "resultsAvailable=true"
        if mode
        else "resultsAvailable=false"
    )
    _require_interpretable(response, f"{race_date} {mode_name}")

    rows = _rows(response) if response.ok else []
    return {
        "mode": mode_name,
        "status": response.response_status,
        "ok": response.ok,
        "fixture_count": len(rows),
        "reported_total": (
            response.payload.get("total")
            if isinstance(response.payload, dict)
            else None
        ),
        "courses": [row.get("courseName") for row in rows],
        "fixture_ids": [row.get("fixtureId") for row in rows],
        "cache_path": str(response.cache_path),
        "from_cache": response.from_cache,
    }


def _extract_existing_year_states(notebook) -> dict[int, dict]:
    """Recover the executed coarse/refinement states already present in Notebook 28."""
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
            for raw_line in str(text).splitlines():
                line = raw_line.strip()
                match = LINE_PATTERN.match(line)
                if not match:
                    continue
                year = int(match.group(1))
                states[year] = ast.literal_eval(match.group(3))
    return states


def _mode_result(case_result: dict, mode_name: str) -> dict:
    for item in case_result["queries"]:
        if item["mode"] == mode_name:
            return item
    raise KeyError((case_result["date"], mode_name))


def _compact(result: dict) -> str:
    count = result["fixture_count"]
    status = result["status"]
    if count:
        courses = ", ".join(str(value) for value in result["courses"][:4])
        suffix = "" if count <= 4 else f", +{count - 4} more"
        return f"HTTP {status}; {count} fixtures ({courses}{suffix})"
    return f"HTTP {status}; 0 fixtures"


def _markdown_table(case_results: list[dict]) -> str:
    lines = [
        "| Date | Control | Unfiltered `/fixtures` | `resultsAvailable=true` |",
        "|---|---|---|---|",
    ]
    for case in case_results:
        unfiltered = _mode_result(case, "unfiltered")
        completed = _mode_result(case, "resultsAvailable=true")
        lines.append(
            f"| {case['date']} | {case['label']} | {_compact(unfiltered)} | {_compact(completed)} |"
        )
    return "\n".join(lines)


def _build_audited_conclusion(
    case_results: list[dict],
    year_states: dict[int, dict],
    worcester: dict,
) -> str:
    by_date = {case["date"]: case for case in case_results}

    d1994_u = _mode_result(by_date["1994-04-09"], "unfiltered")
    d1994_r = _mode_result(by_date["1994-04-09"], "resultsAvailable=true")
    d1995_u = _mode_result(by_date["1995-04-08"], "unfiltered")
    d1995_r = _mode_result(by_date["1995-04-08"], "resultsAvailable=true")

    lower_fixture = (
        "A known racing date in 1994 (Aintree, 9 April) returned no fixture records "
        "in either tested query mode, while the 8 April 1995 BHA anchor returned "
        "fixture records. This is strong **observed lower-edge evidence** for the "
        "current fixture-search surface around 1995, but it is still an observed "
        "public-service boundary rather than a contractual retention guarantee."
        if (
            d1994_u["fixture_count"] == 0
            and d1994_r["fixture_count"] == 0
            and max(d1995_u["fixture_count"], d1995_r["fixture_count"]) > 0
        )
        else (
            "The 1994/1995 known-racing-date controls did not produce a clean lower-edge "
            "split, so the fixture-search start boundary remains unresolved."
        )
    )

    modern_dates = ["2022-04-09", "2023-04-15", "2024-04-13", "2025-03-14"]
    query_mode_only = []
    both_empty = []
    both_populated = []
    for race_date in modern_dates:
        case = by_date[race_date]
        unfiltered = _mode_result(case, "unfiltered")["fixture_count"]
        completed = _mode_result(case, "resultsAvailable=true")["fixture_count"]
        if unfiltered == 0 and completed > 0:
            query_mode_only.append(race_date)
        elif unfiltered == 0 and completed == 0:
            both_empty.append(race_date)
        elif unfiltered > 0 and completed > 0:
            both_populated.append(race_date)

    if query_mode_only and not both_empty:
        modern_interpretation = (
            "The apparent 2022–2025 gap in the first pass is **query-mode dependent**, "
            "not a simple archive hole: known racing dates that were empty without the "
            "filter are populated when `resultsAvailable=true` is supplied. The fixture "
            "surface therefore cannot be characterised from unfiltered historical queries alone."
        )
    elif both_empty:
        modern_interpretation = (
            "At least some independently known racing dates in 2022–2025 returned zero "
            "fixtures in both tested query modes. The current public structured surface "
            "therefore has a **modern historical availability anomaly/gap** and cannot be "
            "treated as a continuous archive merely because older and current years are populated."
        )
    else:
        modern_interpretation = (
            "The known-racing-date controls did not reproduce the first-pass 2022–2025 "
            "emptiness consistently; the apparent gap must be treated as unresolved query behaviour."
        )

    suspended = by_date["2020-04-01"]
    suspended_u = _mode_result(suspended, "unfiltered")
    suspended_r = _mode_result(suspended, "resultsAvailable=true")
    if suspended_u["fixture_count"] > 0 and suspended_r["fixture_count"] == 0:
        programme_state = (
            "The 1 April 2020 control is a direct semantic demonstration: the unfiltered "
            "fixture search retains programmed fixtures during the BHA's suspended-racing "
            "period, while the completed-results filter returns none. Fixture discovery is "
            "therefore evidence of programme/admin state, not proof that racing occurred."
        )
    else:
        programme_state = (
            "The 1 April 2020 query-mode control did not produce the expected clean "
            "programmed-versus-completed split; programme/execution semantics therefore "
            "remain governed by the earlier Notebook 26 evidence rather than this control alone."
        )

    state_1999 = year_states.get(1999, {})
    state_2000 = year_states.get(2000, {})
    fixture_detail_edge = (
        state_1999.get("fixture_detail") == "absent_404"
        and state_2000.get("fixture_detail") == "available"
    )
    race_list_edge = (
        state_1999.get("race_list") == "absent_404"
        and state_2000.get("race_list") == "available"
    )

    detailed_lines = []
    if fixture_detail_edge:
        detailed_lines.append(
            "- **Fixture detail:** sampled 1999 fixture-detail requests return direct HTTP 404, "
            "while sampled 2000 fixture-detail requests are populated. That is a genuine "
            "directly observed 1999→2000 lower-edge split for this resource family."
        )
    if race_list_edge:
        detailed_lines.append(
            "- **Fixture race lists:** sampled 1999 race-list requests return direct HTTP 404, "
            "while sampled 2000 race lists are populated. This is also a direct 1999→2000 "
            "lower-edge split, subject to the study's bounded sampling."
        )

    detailed_lines.extend(
        [
            "- **Race detail:** populated race-detail responses are demonstrated from sampled "
            "2000 records. Pre-2000 BHA races were not addressable through the surviving "
            "fixture/race-list chain, so this study does **not** establish a direct race-detail "
            "endpoint start date.",
            "- **Official results and runner-level results:** populated responses are likewise "
            "demonstrated from sampled 2000 records, but the lower endpoint boundary remains "
            "unresolved because no pre-2000 BHA race reference was available to challenge the "
            "result route directly.",
        ]
    )

    if worcester.get("found"):
        worcester_line = (
            "The Worcester 25 September 2020 abandoned-fixture control was recovered in the "
            "refinement pass and its fixture detail/race-list evidence is preserved below."
        )
    else:
        worcester_line = (
            "The attempted Worcester 25 September 2020 re-probe did not recover a Worcester "
            "fixture from the tested fixture-search modes. Notebook 28 therefore does **not** "
            "claim to have independently re-demonstrated that earlier control; the earlier "
            "Notebook 26 observation remains separate prior evidence."
        )

    return "\n".join(
        [
            "# Audited conclusion — BHA historical race-data depth",
            "",
            "The important result is **not a single start year**. The current BHA structured "
            "surface has different depths by resource family, query-mode effects, and "
            "non-contiguous/partial behaviour in some sampled periods.",
            "",
            "## Fixture discovery",
            "",
            lower_fixture,
            "",
            modern_interpretation,
            "",
            "## Detailed fixture/race/result resources",
            "",
            *detailed_lines,
            "",
            "## Programme state versus racing that actually occurred",
            "",
            programme_state,
            "",
            worcester_line,
            "",
            "This reinforces the earlier population-audit rule: fixture-index presence, "
            "race-list presence and an actually run race are different evidence states.",
            "",
            "## Practical source-capability conclusion",
            "",
            "For the current public structured service, the defensible findings are:",
            "",
            "1. fixture discovery is observed on known racing dates from 1995, with the 1994 "
            "control used only as lower-edge evidence;",
            "2. fixture detail and fixture race lists have a directly observed sampled lower "
            "edge between 1999 and 2000;",
            "3. race detail, official results and runner rows are demonstrated from sampled "
            "2000 races, but their direct pre-2000 endpoint boundary is unresolved;",
            "4. historical fixture searching is sensitive to query semantics and/or archive "
            "population, so continuity must be tested rather than assumed; and",
            "5. the structured service alone is not yet proven to be a continuous, complete "
            "official historical race-population source across every year and resource family.",
            "",
            "No Database v5 design or import decision follows automatically from this notebook."
        ]
    )


def _remove_prior_audit_cells(notebook) -> None:
    kept = []
    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        if tags & {"historical-depth-audit-refinement", "historical-depth-audit-results"}:
            continue
        kept.append(cell)
    notebook.cells = kept


def main() -> None:
    if not NOTEBOOK.is_file():
        raise FileNotFoundError(NOTEBOOK)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    year_states = _extract_existing_year_states(notebook)

    for required_year in (1999, 2000):
        if required_year not in year_states:
            raise RuntimeError(
                f"Executed Notebook 28 does not contain the required {required_year} probe state."
            )

    bha = BhaApiClient(CACHE_DIR)
    case_results = []
    for case in DIAGNOSTIC_CASES:
        queries = [
            _probe_fixture_search(bha, case["date"], None),
            _probe_fixture_search(bha, case["date"], True),
        ]
        case_results.append({**case, "queries": queries})
        print(
            case["date"],
            "| unfiltered:", queries[0]["fixture_count"],
            "| resultsAvailable=true:", queries[1]["fixture_count"],
        )

    # Revisit the earlier Worcester abandoned-fixture control using all three query modes.
    worcester_queries = [
        _probe_fixture_search(bha, "2020-09-25", None),
        _probe_fixture_search(bha, "2020-09-25", True),
        _probe_fixture_search(bha, "2020-09-25", False),
    ]
    worcester = {"date": "2020-09-25", "queries": worcester_queries, "found": False}

    for query in worcester_queries:
        for course, fixture_id in zip(query["courses"], query["fixture_ids"]):
            if str(course or "").strip().lower() != "worcester":
                continue
            worcester["found"] = True
            worcester["found_in_mode"] = query["mode"]
            worcester["fixture_id"] = fixture_id

            detail = bha.fixture_detail(2020, fixture_id)
            races = bha.fixture_races(2020, fixture_id)
            _require_interpretable(detail, "Worcester 2020 fixture detail")
            _require_interpretable(races, "Worcester 2020 race list")

            detail_rows = _rows(detail)
            detail_row = detail_rows[0] if detail_rows else {}
            worcester["detail"] = {
                "status": detail.response_status,
                "resultsAvailable": detail_row.get("resultsAvailable"),
                "abandonedReasonCode": detail_row.get("abandonedReasonCode"),
                "goingText": detail_row.get("goingText"),
                "cache_path": str(detail.cache_path),
            }
            worcester["race_list"] = {
                "status": races.response_status,
                "race_count": len(_rows(races)),
                "cache_path": str(races.cache_path),
            }
            break
        if worcester["found"]:
            break

    audited_conclusion = _build_audited_conclusion(case_results, year_states, worcester)

    diagnostic_payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "access_profile": ACCESS_PROFILE,
        "cases": case_results,
        "worcester": worcester,
        "existing_year_states": year_states,
    }
    DIAGNOSTIC_JSON.write_text(
        json.dumps(diagnostic_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    _remove_prior_audit_cells(notebook)

    result_table = _markdown_table(case_results)
    source_list = "\n".join(
        f"- {case['date']} — {case['context']}"
        + (f" — {case['external_source']}" if case["external_source"] else "")
        for case in DIAGNOSTIC_CASES
    )

    refinement_markdown = nbformat.v4.new_markdown_cell(
        "\n".join(
            [
                "## Audit refinement — known-racing dates and fixture query mode",
                "",
                "The first autonomous pass exposed two issues that must be separated from a "
                "true historical boundary: `not_addressable` is not a direct endpoint 404, and "
                "the fixture search showed non-monotonic modern behaviour. This refinement "
                "therefore tests known racing dates in both unfiltered mode and with "
                "`resultsAvailable=true`.",
                "",
                "The requests were executed by `scripts/refine_notebook_28_bha_historical_depth.py` "
                "through the same governed `BhaApiClient`; every response is cached in the "
                "Notebook 28 cache namespace.",
                "",
                result_table,
                "",
                "### Independent date/context controls",
                "",
                source_list,
                "",
                "### Worcester abandoned-fixture re-probe",
                "",
                f"Recovered Worcester fixture: **{worcester['found']}**.",
                (
                    f"Found through `{worcester.get('found_in_mode')}` with fixtureId "
                    f"`{worcester.get('fixture_id')}`; detail={worcester.get('detail')}; "
                    f"race_list={worcester.get('race_list')}."
                    if worcester["found"]
                    else "The tested query modes did not return a Worcester fixture on 25 September 2020."
                ),
            ]
        )
    )
    refinement_markdown.metadata["tags"] = ["historical-depth-audit-results"]

    documentary_code = nbformat.v4.new_code_cell(
        """# Documentary cell: the refinement script executed these query modes outside\n"
        "# the Jupyter kernel so that the existing executed study did not need to be rerun.\n"
        "# All responses are preserved by BhaApiClient in the same ignored cache namespace.\n"
        "\n"
        "diagnostic_cases = [\n"
        "    (\"1994-04-09\", None), (\"1994-04-09\", True),\n"
        "    (\"1995-04-08\", None), (\"1995-04-08\", True),\n"
        "    (\"2020-04-01\", None), (\"2020-04-01\", True),\n"
        "    (\"2022-04-09\", None), (\"2022-04-09\", True),\n"
        "    (\"2023-04-15\", None), (\"2023-04-15\", True),\n"
        "    (\"2024-04-13\", None), (\"2024-04-13\", True),\n"
        "    (\"2025-03-14\", None), (\"2025-03-14\", True),\n"
        "    (\"2026-05-27\", None), (\"2026-05-27\", True),\n"
        "]\n"
        "\n"
        "# Worcester is additionally tested with resultsAvailable=False because an\n"
        "# abandoned fixture is specifically a non-result-bearing administrative state.\n"
        "worcester_modes = [None, True, False]\n"""
    )
    documentary_code.metadata["tags"] = ["historical-depth-audit-refinement"]

    # Insert the refinement immediately before the generated conclusion section.
    conclusion_index = None
    for index, cell in enumerate(notebook.cells):
        tags = set(cell.metadata.get("tags", []))
        if "generated-conclusion" in tags:
            conclusion_index = index
            break
    if conclusion_index is None:
        conclusion_index = len(notebook.cells)

    notebook.cells[conclusion_index:conclusion_index] = [documentary_code, refinement_markdown]

    # Replace the earlier automated conclusion with the audited evidence wording.
    replaced = False
    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        if "generated-conclusion" in tags:
            cell.source = audited_conclusion.rstrip() + "\n"
            cell.metadata["tags"] = ["generated-conclusion", "audited-conclusion"]
            replaced = True
            break
    if not replaced:
        conclusion_cell = nbformat.v4.new_markdown_cell(audited_conclusion.rstrip() + "\n")
        conclusion_cell.metadata["tags"] = ["generated-conclusion", "audited-conclusion"]
        notebook.cells.append(conclusion_cell)

    nbformat.write(notebook, NOTEBOOK)

    print(f"Diagnostic evidence: {DIAGNOSTIC_JSON}")
    print(f"Audited Notebook 28: {NOTEBOOK}")
    print("\n" + audited_conclusion)


if __name__ == "__main__":
    main()
