#!/usr/bin/env python3
"""Temporarily append Step 2 analysis cells to notebook 26.

This helper exists only to avoid clobbering locally executed notebook outputs while
adding the next governed analysis step. Run it once, then remove this helper from
the branch before the notebook change is committed.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "26_gb_race_population_completeness.ipynb"

INTRO_ID = "structure-original-2026-fixture-plan-intro"
CODE_ID = "structure-original-2026-fixture-plan"
CHECKPOINT_ID = "structure-original-2026-fixture-plan-checkpoint"

INTRO_SOURCE = """### Step 2 — Structure and validate the original 2026 fixture-plan rows

The first inspection established that `List - Full Year` declares **1,459 stored rows including the header**, leaving **1,458 data rows**. That agrees with the BHA's published total of 1,458 fixtures for the original 2026 list, so the sheet is now a strong candidate for the original-plan population.

This step still avoids turning spreadsheet rows into a governed fixture identity. Instead it asks whether the rows form an internally coherent set of **published fixture-plan observations**.

Checks performed here:

- preserve the nine BHA-supplied fields rather than inventing new schedule attributes;
- convert the stored Excel serial date while retaining the original serial value;
- verify that the supplied weekday agrees with the converted date;
- inspect missing values and exact duplicate source rows;
- inspect repeated `date + course` and `date + course + Time` combinations;
- treat the workbook's `Time` value as the BHA-supplied schedule/session label, **not** as a race off-time;
- do **not** infer a fixture ID from any combination of these columns.

The output of this cell determines whether one workbook data row can safely be described as one **original published fixture-plan observation** for this audit.
"""

CODE_SOURCE = r'''# Structure and validate every data row from the BHA original 2026 plan.
#
# This cell deliberately works from the worksheet XML already inspected in Step 1.
# It does not modify the retained XLSX and does not create a fixture identity.
#
# Important terminology:
#   - one spreadsheet row is provisionally a *published plan row*;
#   - the BHA column named "Time" is preserved as supplied (for example,
#     Afternoon/Floodlit). It is NOT interpreted as an individual race off-time;
#   - date + course is tested as a grouping only. Study 04 already established
#     that it cannot be assumed to be a universal fixture identity.

from datetime import date, timedelta

# Read all stored worksheet rows while preserving blank cells between populated
# columns. The first row is expected to be the BHA header row observed in Step 1.
stored_rows = []
for row in sheet_data.findall("x:row", NS):
    values_by_column = {
        column_number(cell.attrib["r"]): cell_value(cell)
        for cell in row.findall("x:c", NS)
    }
    stored_rows.append(
        [values_by_column.get(column) for column in range(1, 10)]
    )

expected_headers = [
    "Date",
    "Weekday",
    "Course",
    "Time",
    "CourseGroup",
    "Region",
    "Code",
    "Surface",
    "Type",
]

assert stored_rows, "The BHA list worksheet contains no stored rows."
assert stored_rows[0] == expected_headers, (
    "Unexpected BHA header structure. "
    f"Expected {expected_headers}, found {stored_rows[0]}"
)

# Preserve the BHA values first. Renaming below is only for clearer analysis;
# no source value is normalised or overwritten.
raw_plan_rows = pd.DataFrame(stored_rows[1:], columns=expected_headers)

# The retained workbook is the originally published 2026 list. Its row count
# should reconcile to the BHA-published total before we analyse its structure.
PUBLISHED_2026_FIXTURE_TOTAL = 1_458
assert len(raw_plan_rows) == PUBLISHED_2026_FIXTURE_TOTAL, (
    f"Expected {PUBLISHED_2026_FIXTURE_TOTAL:,} published plan rows, "
    f"found {len(raw_plan_rows):,}."
)

# Build an audit-friendly table. Keep the raw Excel serial date alongside the
# converted calendar date so the transformation remains transparent.
bha_2026_original_plan = raw_plan_rows.rename(
    columns={
        "Date": "date_serial_raw",
        "Weekday": "weekday_raw",
        "Course": "course_raw",
        "Time": "time_label_raw",
        "CourseGroup": "course_group_raw",
        "Region": "region_raw",
        "Code": "code_raw",
        "Surface": "surface_raw",
        "Type": "type_raw",
    }
).copy()

# Source row number is retained as provenance within the worksheet only. It is
# not a fixture identifier and must never be treated as one outside this file.
bha_2026_original_plan.insert(
    0,
    "source_sheet_row",
    range(2, len(bha_2026_original_plan) + 2),
)

# Modern Excel serial dates use the 1900 date system. Using 1899-12-30 as the
# effective epoch accounts for Excel's historical fictitious 1900-02-29 entry.
EXCEL_1900_EPOCH = date(1899, 12, 30)


def excel_serial_to_date(value):
    if value in (None, ""):
        return None
    return EXCEL_1900_EPOCH + timedelta(days=int(float(value)))


bha_2026_original_plan.insert(
    2,
    "fixture_date",
    bha_2026_original_plan["date_serial_raw"].map(excel_serial_to_date),
)

# Weekday is supplied independently by BHA, so agreement with the converted
# date is a useful internal-consistency check on both the source and our date
# interpretation.
bha_2026_original_plan["weekday_from_date"] = (
    bha_2026_original_plan["fixture_date"].map(
        lambda value: value.strftime("%A") if value is not None else None
    )
)
bha_2026_original_plan["weekday_matches_date"] = (
    bha_2026_original_plan["weekday_raw"]
    == bha_2026_original_plan["weekday_from_date"]
)

# Exact duplicates deliberately exclude source_sheet_row, because that column
# was added by us purely to retain worksheet provenance.
source_value_columns = [
    "date_serial_raw",
    "weekday_raw",
    "course_raw",
    "time_label_raw",
    "course_group_raw",
    "region_raw",
    "code_raw",
    "surface_raw",
    "type_raw",
]
exact_duplicate_mask = bha_2026_original_plan.duplicated(
    subset=source_value_columns,
    keep=False,
)

# Missing-value counts are calculated over the actual BHA-supplied fields, not
# over our derived audit columns.
missing_by_source_field = (
    bha_2026_original_plan[source_value_columns]
    .isna()
    .sum()
    .rename("missing_rows")
    .to_frame()
)

# These grouping checks are intentionally diagnostic only. Repeated date/course
# rows are especially important because they demonstrate why date + racecourse
# cannot silently become a fixture key.
repeated_date_course = (
    bha_2026_original_plan
    .groupby(["fixture_date", "course_raw"], dropna=False)
    .size()
    .rename("published_plan_rows")
    .reset_index()
    .query("published_plan_rows > 1")
    .sort_values(["published_plan_rows", "fixture_date", "course_raw"], ascending=[False, True, True])
)

repeated_date_course_time = (
    bha_2026_original_plan
    .groupby(["fixture_date", "course_raw", "time_label_raw"], dropna=False)
    .size()
    .rename("published_plan_rows")
    .reset_index()
    .query("published_plan_rows > 1")
    .sort_values(
        ["published_plan_rows", "fixture_date", "course_raw", "time_label_raw"],
        ascending=[False, True, True, True],
    )
)

plan_structure_summary = pd.Series(
    {
        "published_plan_rows": len(bha_2026_original_plan),
        "earliest_fixture_date": bha_2026_original_plan["fixture_date"].min(),
        "latest_fixture_date": bha_2026_original_plan["fixture_date"].max(),
        "distinct_course_labels": bha_2026_original_plan["course_raw"].nunique(dropna=True),
        "weekday_mismatches": int((~bha_2026_original_plan["weekday_matches_date"]).sum()),
        "exact_duplicate_source_rows": int(exact_duplicate_mask.sum()),
        "repeated_date_course_groups": len(repeated_date_course),
        "repeated_date_course_time_groups": len(repeated_date_course_time),
    },
    name="value",
)

print("Original 2026 BHA fixture-plan structure:")
display(plan_structure_summary.to_frame())

print("\nMissing values in BHA-supplied fields:")
display(missing_by_source_field)

print("\nFirst 10 structured original-plan rows:")
display(bha_2026_original_plan.head(10))

print("\nRepeated date + course groups (diagnostic only):")
display(repeated_date_course.head(25))

print("\nRepeated date + course + BHA Time-label groups (diagnostic only):")
display(repeated_date_course_time.head(25))
'''

CHECKPOINT_SOURCE = """#### Step 2 interpretation checkpoint

Read the outputs before moving on.

What we want to establish is narrower than "these are fixture identities":

> Does each data row behave coherently as one **original published 2026 fixture-plan observation**?

The most important outputs are the row-count reconciliation, weekday mismatches, exact duplicate source rows and repeated date/course groupings. Repeated `date + course` rows are not errors; they are evidence that the audit must continue respecting Study 04's rule against manufacturing fixture identity from that pair.

Once this structure is understood, the next task is to acquire the **realised BHA result population** and use the original plan only as explanatory schedule evidence.
"""


def markdown_cell(cell_id: str, source: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source,
    }


def code_cell(cell_id: str, source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
existing_ids = {cell.get("id") for cell in notebook.get("cells", [])}

requested_ids = {INTRO_ID, CODE_ID, CHECKPOINT_ID}
if requested_ids <= existing_ids:
    print("Notebook 26 already contains Step 2; no changes made.")
    raise SystemExit(0)

if requested_ids & existing_ids:
    raise RuntimeError(
        "Notebook contains only part of the Step 2 cell set; refusing a partial update."
    )

notebook["cells"].extend(
    [
        markdown_cell(INTRO_ID, INTRO_SOURCE),
        code_cell(CODE_ID, CODE_SOURCE),
        markdown_cell(CHECKPOINT_ID, CHECKPOINT_SOURCE),
    ]
)

NOTEBOOK_PATH.write_text(
    json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print(f"Updated {NOTEBOOK_PATH.relative_to(PROJECT_ROOT)} with Step 2.")
