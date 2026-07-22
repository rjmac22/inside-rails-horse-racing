"""Validate carried-weight parsing against the source database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from inside_rails.carried_weight import parse_carried_weight


DATA_ROW_PREDICATE = "rowid <> 1"
EXPECTED_DATA_ROWS = 1_851_285
EXPECTED_DISTINCT_VALUES = 79


def main() -> None:
    database_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "form_2015-present"
        / "form_2015-present"
        / "raceform.db"
    )

    if not database_path.exists():
        raise FileNotFoundError(f"Source database not found: {database_path}")

    connection = sqlite3.connect(
        f"file:{database_path}?mode=ro",
        uri=True,
    )

    try:
        raw_values = pd.read_sql_query(
            f"""
            SELECT
                wgt AS raw_wgt,
                typeof(wgt) AS sqlite_storage_class,
                COUNT(*) AS runner_records,
                CAST(substr(wgt, 1, instr(wgt, '-') - 1) AS INTEGER)
                    AS sql_stones,
                CAST(substr(wgt, instr(wgt, '-') + 1) AS INTEGER)
                    AS sql_pounds,
                (
                    CAST(substr(wgt, 1, instr(wgt, '-') - 1) AS INTEGER) * 14
                    + CAST(substr(wgt, instr(wgt, '-') + 1) AS INTEGER)
                ) AS sql_total_pounds
            FROM data
            WHERE {DATA_ROW_PREDICATE}
            GROUP BY wgt, typeof(wgt)
            ORDER BY wgt
            """,
            connection,
        )
    finally:
        connection.close()

    results = pd.DataFrame(
        parse_carried_weight(raw_wgt)
        for raw_wgt in raw_values["raw_wgt"]
    )

    validation = pd.concat(
        [raw_values.reset_index(drop=True), results.reset_index(drop=True)],
        axis=1,
    )

    assert raw_values["runner_records"].sum() == EXPECTED_DATA_ROWS
    assert len(raw_values) == EXPECTED_DISTINCT_VALUES
    assert raw_values["sqlite_storage_class"].eq("text").all()

    assert validation["parse_status"].eq("parsed").all()
    assert validation["notation_family"].eq("stones_and_pounds").all()
    assert validation["ambiguity_flag"].eq(False).all()
    assert validation["anomaly_flags"].eq(()).all()

    assert validation["parsed_stones"].eq(validation["sql_stones"]).all()
    assert validation["parsed_pounds"].eq(validation["sql_pounds"]).all()
    assert validation["source_implied_total_pounds"].eq(
        validation["sql_total_pounds"]
    ).all()

    assert validation["source_implied_total_pounds"].between(96, 179).all()
    assert validation["source_implied_kilograms"].notna().all()
    assert validation["official_weight_verified"].eq(False).all()

    # Canonical unseen values may parse when their structure is unambiguous.
    assert parse_carried_weight("7-0")["parse_status"] == "parsed"
    assert parse_carried_weight("13-0")["parse_status"] == "parsed"

    # Unsupported future values must remain explicitly unresolved.
    unresolved_examples = [
        "9-14",
        "10-20",
        "09-0",
        "9-00",
        " 9-0",
        "9-0 ",
        "9 - 0",
        "9/0",
        "126",
        "126lb",
        "57kg",
        "57.0",
        "9-0½",
        "9-0.5",
        "",
        None,
        126,
        57.0,
    ]

    for raw_wgt in unresolved_examples:
        parsed = parse_carried_weight(raw_wgt)
        assert parsed["parse_status"] != "parsed"
        assert parsed["source_implied_total_pounds"] is None
        assert parsed["source_implied_kilograms"] is None

    print("Carried-weight validation passed.")
    print(f"Runner records checked: {raw_values['runner_records'].sum():,}")
    print(f"Distinct raw values: {len(raw_values):,}")
    print(f"Parsed runner records: {raw_values['runner_records'].sum():,}")
    print("Unresolved current runner records: 0")
    print("Official-weight verified rows: 0")


if __name__ == "__main__":
    main()
