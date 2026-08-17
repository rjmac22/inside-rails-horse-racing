from __future__ import annotations

import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
NOTEBOOK = REPO_ROOT / "notebooks" / "29_bha_race_execution_state.ipynb"
TAG = "notebook29-audit-refinement"
FINAL_TAG = "notebook29-audited-conclusion"


def prepare_pythonpath() -> None:
    src_text = str(SRC_DIR)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
    existing = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    if src_text not in existing:
        os.environ["PYTHONPATH"] = os.pathsep.join([src_text, *existing])
    from inside_rails.bha_api import ACCESS_PROFILE
    print(f"Repository src path: {SRC_DIR}")
    print(f"BHA client import preflight: PASS ({ACCESS_PROFILE})")


def add_cell(nb, kind: str, source: str, tags: list[str]) -> None:
    cell = (
        nbformat.v4.new_markdown_cell(source.strip() + "\n")
        if kind == "markdown"
        else nbformat.v4.new_code_cell(source.strip() + "\n")
    )
    cell.metadata["tags"] = tags
    nb.cells.append(cell)


def append_refinement(nb):
    # Idempotent replacement of any prior refinement attempt.
    nb.cells = [
        cell for cell in nb.cells
        if TAG not in set(cell.metadata.get("tags", []))
        and FINAL_TAG not in set(cell.metadata.get("tags", []))
    ]

    add_cell(
        nb,
        "markdown",
        """
# Audit refinement — omitted race-level field and Worcester negative control

The first autonomous pass is preserved above as construction evidence, but it is not sufficient to close Notebook 29.

The audit found three material problems:

1. all 34 addressable comparisons were realised races, so no candidate could be tested for false positives;
2. the attempted temporal challenge did not run in substance because every arbitrary April/November search window returned zero fixtures;
3. the race-detail schema exposed `resultsAvailable`, but the first pass did not record or test it.

This refinement keeps the question bounded. It does **not** try another broad temporal sample. Instead it tests the candidate semantics against:

- the existing 34 known completed races from 27 May 2026; and
- Worcester on 25 September 2020, where Notebook 28 established an abandoned fixture whose fixture-races resource still retained one programmed race.

The dedicated BHA race-results resource remains the target definition:

> **realised race = dedicated BHA race-results resource contains one or more result rows.**

If Worcester supplies an addressable non-realised race and one or more candidate fields survive without contradiction, the next notebook can perform the proper 2015-present population-wide validation. If Worcester is not addressable, Notebook 29 must close with that archive limitation rather than claiming a predicate.
""",
        [TAG],
    )

    add_cell(
        nb,
        "code",
        r'''
# Reuse the 34 completed-race observations already acquired by the first pass.
# Their dedicated result endpoints are the positive-control truth. The only field
# missing from the first-pass race-detail extraction is `resultsAvailable`, so we
# re-read the same race-detail resources (normally from cache) and add that field.

audit_rows = []

for row in race_records:
    if row["label"] != "completed_control_2026_05_27":
        continue
    year_text, race_id, division = row["race_ref"].split(":", 2)
    detail_response = logged(
        bha.race_detail(int(year_text), race_id, division),
        "audit_refinement",
        "race_detail",
        row["race_ref"],
    )
    detail = first_record(detail_response)
    audit_rows.append(
        {
            "label": row["label"],
            "race_ref": row["race_ref"],
            "course_name": row["course_name"],
            "list_abandoned_reason_code": row["list_abandoned_reason_code"],
            "list_winner_count": row["list_winner_count"],
            "detail_abandoned_reason_code": row["detail_abandoned_reason_code"],
            "detail_results_available": detail.get("resultsAvailable"),
            "detail_winner_count": row["detail_winner_count"],
            "results_state": row["results_state"],
            "official_result_rows": row["official_result_rows"],
            "official_result_produced": row["official_result_produced"],
        }
    )

assert len(audit_rows) == 34, f"Expected 34 completed controls, found {len(audit_rows)}"

# Worcester is deliberately rediscovered through all three fixture-search modes.
# Notebook 28 showed that the search parameter itself is not a semantic contract,
# so these modes are discovery routes only and are deduplicated by BHA fixture id.
worcester_candidates = []
for mode in (None, True, False):
    response = logged(
        bha.fixture_search(
            "2020-09-25",
            "2020-09-25",
            results_available=mode,
            page=1,
            per_page=100,
        ),
        "audit_refinement",
        "fixture_search",
        f"2020-09-25:{mode}",
    )
    for fixture in data_rows(response):
        if "worcester" in str(fixture.get("courseName", "")).lower():
            worcester_candidates.append((mode, fixture))

worcester_by_id = {}
for mode, fixture in worcester_candidates:
    key = (as_int(fixture.get("fixtureYear")), fixture.get("fixtureId"))
    if key[0] is None or key[1] is None:
        continue
    worcester_by_id.setdefault(key, {"fixture": fixture, "modes": []})
    worcester_by_id[key]["modes"].append(mode)

print("Worcester deduplicated fixture identities:", len(worcester_by_id))
for key, value in worcester_by_id.items():
    print(key, "discovery_modes=", value["modes"])

if len(worcester_by_id) != 1:
    raise RuntimeError(
        "Expected one Worcester fixture identity on 2020-09-25; "
        f"found {len(worcester_by_id)}"
    )

worcester_fixture = next(iter(worcester_by_id.values()))["fixture"]
fy = as_int(worcester_fixture.get("fixtureYear"))
fid = worcester_fixture.get("fixtureId")

fixture_detail_response = logged(
    bha.fixture_detail(fy, fid),
    "audit_refinement",
    "fixture_detail",
    f"{fy}:{fid}",
)
fixture_races_response = logged(
    bha.fixture_races(fy, fid),
    "audit_refinement",
    "fixture_races",
    f"{fy}:{fid}",
)
fixture_detail = first_record(fixture_detail_response)
worcester_races = data_rows(fixture_races_response)

print(
    "Worcester fixture:",
    {
        "fixtureYear": fy,
        "fixtureId": fid,
        "resultsAvailable": fixture_detail.get("resultsAvailable"),
        "abandonedReasonCode": fixture_detail.get("abandonedReasonCode"),
        "goingText": fixture_detail.get("goingText"),
        "programmed_races": len(worcester_races),
    },
)

worcester_rows = []
for race in worcester_races:
    ref = race_ref(race)
    base = {
        "label": "worcester_2020_09_25",
        "course_name": "Worcester",
        "list_abandoned_reason_code": as_int(race.get("abandonedReasonCode")),
        "list_winner_count": list_count(race.get("winnersDetails")),
    }
    if ref is None:
        worcester_rows.append(
            {
                **base,
                "race_ref": None,
                "detail_abandoned_reason_code": None,
                "detail_results_available": None,
                "detail_winner_count": None,
                "results_state": "not_addressable",
                "official_result_rows": 0,
                "official_result_produced": None,
            }
        )
        continue

    year_of_race, race_id, division = ref
    ref_text = f"{year_of_race}:{race_id}:{division}"
    detail_response = logged(
        bha.race_detail(year_of_race, race_id, division),
        "audit_refinement",
        "race_detail",
        ref_text,
    )
    results_response = logged(
        bha.race_results(year_of_race, race_id, division),
        "audit_refinement",
        "race_results",
        ref_text,
    )
    detail = first_record(detail_response)
    results_kind, result_rows = result_state(results_response)
    worcester_rows.append(
        {
            **base,
            "race_ref": ref_text,
            "detail_abandoned_reason_code": as_int(detail.get("abandonedReasonCode")),
            "detail_results_available": detail.get("resultsAvailable"),
            "detail_winner_count": list_count(detail.get("winnersDetails")),
            "results_state": results_kind,
            "official_result_rows": result_rows,
            "official_result_produced": result_rows > 0,
        }
    )

print("Worcester race rows:", len(worcester_rows))
if worcester_rows:
    display(pd.DataFrame(worcester_rows))

audit_rows.extend(worcester_rows)
audit_df = pd.DataFrame(audit_rows)
''',
        [TAG],
    )

    add_cell(
        nb,
        "markdown",
        """
## Candidate comparison

The refinement tests the source layers separately rather than assuming similarly named fields mean the same thing.

Candidate signals:

- fixture-race-list `abandonedReasonCode == 0`;
- fixture-race-list `winnersDetails` non-empty;
- race-detail `abandonedReasonCode == 0`;
- race-detail `resultsAvailable == 1`;
- race-detail `winnersDetails` non-empty;
- conservative combinations of those fields.

Missing values never count as positive evidence. The dedicated result endpoint remains the comparison target.
""",
        [TAG],
    )

    add_cell(
        nb,
        "code",
        r'''
# Build explicit boolean candidates and measure false positives/negatives against
# the dedicated official-result endpoint. Non-addressable Worcester rows remain in
# the notebook but are excluded from the contradiction table because they have no
# direct result endpoint with which to classify realised/non-realised state.

audit_df["list_abandonment_rule"] = audit_df["list_abandoned_reason_code"].eq(0).fillna(False)
audit_df["list_winner_rule"] = audit_df["list_winner_count"].fillna(0).gt(0)
audit_df["list_combined_rule"] = audit_df["list_abandonment_rule"] & audit_df["list_winner_rule"]
audit_df["detail_abandonment_rule"] = audit_df["detail_abandoned_reason_code"].eq(0).fillna(False)
audit_df["detail_results_available_rule"] = pd.to_numeric(
    audit_df["detail_results_available"], errors="coerce"
).eq(1).fillna(False)
audit_df["detail_winner_rule"] = audit_df["detail_winner_count"].fillna(0).gt(0)
audit_df["detail_abandonment_results_rule"] = (
    audit_df["detail_abandonment_rule"] & audit_df["detail_results_available_rule"]
)

comparable_audit = audit_df.loc[audit_df["official_result_produced"].notna()].copy()
comparable_audit["official_result_produced"] = comparable_audit["official_result_produced"].astype(bool)
actual = comparable_audit["official_result_produced"]

candidate_columns = [
    "list_abandonment_rule",
    "list_winner_rule",
    "list_combined_rule",
    "detail_abandonment_rule",
    "detail_results_available_rule",
    "detail_winner_rule",
    "detail_abandonment_results_rule",
]

candidate_rows = []
for candidate in candidate_columns:
    predicted = comparable_audit[candidate].astype(bool)
    mismatch = predicted != actual
    candidate_rows.append(
        {
            "candidate": candidate,
            "races_tested": len(comparable_audit),
            "contradictions": int(mismatch.sum()),
            "false_positive": int((predicted & ~actual).sum()),
            "false_negative": int((~predicted & actual).sum()),
        }
    )

candidate_audit_df = pd.DataFrame(candidate_rows)
realised_count = int(actual.sum())
nonrealised_count = int((~actual).sum())

print("Addressable comparisons:", len(comparable_audit))
print("Realised comparisons:", realised_count)
print("Non-realised comparisons:", nonrealised_count)
print()
print(candidate_audit_df.to_string(index=False))

# Persist compact derived evidence; raw BHA responses remain in the normal client cache.
audit_df.to_csv(cache_dir / "race_execution_audited_sample_matrix.csv", index=False)
candidate_audit_df.to_csv(cache_dir / "race_execution_audited_candidate_summary.csv", index=False)
''',
        [TAG],
    )

    add_cell(
        nb,
        "markdown",
        """
## Audited conclusion

A field may advance to population-wide validation only if the sample contains both realised and addressable non-realised races and the field has zero contradictions. This is deliberately stricter than merely observing that a field works on completed races.
""",
        [TAG],
    )

    add_cell(
        nb,
        "code",
        r'''
rows = candidate_audit_df.set_index("candidate").to_dict(orient="index")


def line(key, label):
    row = rows[key]
    if row["contradictions"]:
        return (
            f"- **{label}: contradicted** — {row['contradictions']} contradictions "
            f"({row['false_positive']} false-positive, {row['false_negative']} false-negative)."
        )
    if nonrealised_count == 0:
        return (
            f"- **{label}: uncontradicted but not validated** — zero contradictions "
            "on realised controls, but no addressable non-realised race survived."
        )
    return (
        f"- **{label}: supported for population-wide validation** — zero contradictions "
        f"across {row['races_tested']} races including {nonrealised_count} non-realised race(s)."
    )

worcester_addressable = sum(
    row.get("official_result_produced") is not None for row in worcester_rows
)
supported = candidate_audit_df.loc[
    candidate_audit_df["contradictions"].eq(0), "candidate"
].tolist()

if nonrealised_count > 0 and supported:
    next_action = (
        "Notebook 29 has enough negative evidence to nominate candidate race-level fields. "
        "The next bounded notebook should validate the surviving candidate(s) across all "
        "addressable GB races in 2015-present using exact known-racing dates/population acquisition."
    )
else:
    next_action = (
        "Do not scale yet. The next bounded notebook must recover additional official "
        "non-realised race controls that remain addressable in the current BHA archive, "
        "or establish that the archive does not preserve them consistently enough for a field predicate."
    )

audited_conclusion = "\n".join(
    [
        "# Audited conclusion — BHA race-level execution state",
        "",
        "## First-pass correction",
        "",
        "The first pass contained only 34 realised races; its arbitrary temporal windows returned no fixtures and did not constitute a temporal challenge.",
        "It also omitted race-detail `resultsAvailable`, which is explicitly tested here.",
        "",
        "## Worcester negative-control result",
        "",
        f"- Programmed Worcester race rows retained: **{len(worcester_rows)}**.",
        f"- Addressable Worcester race rows: **{worcester_addressable}**.",
        "",
        "## Candidate rules",
        "",
        line("list_abandonment_rule", "fixture-race-list `abandonedReasonCode == 0`"),
        line("list_winner_rule", "fixture-race-list `winnersDetails` non-empty"),
        line("list_combined_rule", "fixture-race-list abandonment + winner"),
        line("detail_abandonment_rule", "race-detail `abandonedReasonCode == 0`"),
        line("detail_results_available_rule", "race-detail `resultsAvailable == 1`"),
        line("detail_winner_rule", "race-detail `winnersDetails` non-empty"),
        line("detail_abandonment_results_rule", "race-detail abandonment + resultsAvailable"),
        "",
        "## Interpretation",
        "",
        "Fixture-race-list, race-detail and dedicated-result resources remain distinct evidence layers. The dedicated result endpoint is the realised-race validation target.",
        "",
        "## Next action",
        "",
        next_action,
        "",
        "No Database v5 design or import decision follows from Notebook 29.",
    ]
)

display(Markdown(audited_conclusion))
''',
        [TAG, "notebook29-audited-conclusion-generator"],
    )

    add_cell(
        nb,
        "markdown",
        "Audited conclusion will be inserted here after execution.",
        [FINAL_TAG],
    )
    return nb


def promote_conclusion(nb) -> None:
    generator = None
    target = None
    for cell in nb.cells:
        tags = set(cell.metadata.get("tags", []))
        if "notebook29-audited-conclusion-generator" in tags:
            generator = cell
        if FINAL_TAG in tags:
            target = cell
    if generator is None or target is None:
        raise RuntimeError("Notebook 29 audit conclusion cells are missing.")

    markdown = None
    for output in generator.get("outputs", []):
        if output.get("output_type") not in {"display_data", "execute_result"}:
            continue
        value = output.get("data", {}).get("text/markdown")
        if value is not None:
            markdown = "".join(value) if isinstance(value, list) else str(value)
            break
    if not markdown:
        raise RuntimeError("Notebook 29 audit emitted no Markdown conclusion.")
    target.source = markdown.rstrip() + "\n"


def main() -> None:
    prepare_pythonpath()
    if not NOTEBOOK.is_file():
        raise RuntimeError(f"Executed Notebook 29 not found: {NOTEBOOK}")

    nb = append_refinement(nbformat.read(NOTEBOOK, as_version=4))

    # Compile-check every code cell before any live request is made.
    for index, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook29-audit-cell-{index}", "exec")
    nbformat.write(nb, NOTEBOOK)

    checked = nbformat.read(NOTEBOOK, as_version=4)
    for index, cell in enumerate(checked.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"notebook29-audit-roundtrip-{index}", "exec")

    print(f"Audit refinement appended to: {NOTEBOOK}")
    print("Generated code-cell compile check: PASS")
    print("Notebook round-trip check: PASS")
    print("Executing Notebook 29 with audit refinement...")

    client = NotebookClient(
        nb,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPO_ROOT)}},
        allow_errors=False,
    )
    try:
        client.execute()
        promote_conclusion(nb)
    except Exception:
        nbformat.write(nb, NOTEBOOK)
        print(f"Notebook 29 audit failed; partial outputs saved to {NOTEBOOK}", file=sys.stderr)
        raise

    nbformat.write(nb, NOTEBOOK)
    print(f"Audited Notebook 29 saved to: {NOTEBOOK}")
    print(f"Evidence cache: {REPO_ROOT / 'data' / 'cache' / 'bha_race_execution_state'}")


if __name__ == "__main__":
    main()
