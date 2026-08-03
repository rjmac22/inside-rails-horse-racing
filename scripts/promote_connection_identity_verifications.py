#!/usr/bin/env python3
"""Promote Notebook 20 evidence into governed permanent references."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inside_rails.connection_identity import (
    build_connection_repairs,
    build_manual_verifications,
    load_connection_evidence,
    load_connection_repairs,
    write_connection_repairs,
)
from inside_rails.manual_verifications import (
    EXPECTED_COLUMNS as MANUAL_VERIFICATION_COLUMNS,
    load_manual_verifications,
    validate_manual_verifications,
)

EVIDENCE_LOG = (
    PROJECT_ROOT
    / "data"
    / "derived"
    / "connection_identity"
    / "manual_connection_repair_evidence_log.csv"
)
MANUAL_VERIFICATION_REGISTER = (
    PROJECT_ROOT / "data" / "reference" / "manual_verifications.csv"
)
CONNECTION_REPAIR_REFERENCE = (
    PROJECT_ROOT / "data" / "reference" / "connection_identity_repairs.csv"
)
NOTEBOOK_20_PREFIX = "NB20-CONNECTION-"


def _write_manual_register(rows: tuple[object, ...]) -> None:
    temporary = MANUAL_VERIFICATION_REGISTER.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANUAL_VERIFICATION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    temporary.replace(MANUAL_VERIFICATION_REGISTER)


def main() -> None:
    evidence = load_connection_evidence(EVIDENCE_LOG)
    notebook_rows = build_manual_verifications(evidence)
    repairs = build_connection_repairs(evidence)

    existing = load_manual_verifications(MANUAL_VERIFICATION_REGISTER)
    existing_notebook_rows = tuple(
        row for row in existing if row.verification_id.startswith(NOTEBOOK_20_PREFIX)
    )

    if existing_notebook_rows:
        if existing_notebook_rows != notebook_rows:
            raise ValueError(
                "Notebook 20 manual-verification rows already exist but do not match "
                "the completed evidence log; reconcile them explicitly rather than "
                "overwriting governed records"
            )
        combined = existing
        register_changed = False
    else:
        combined = validate_manual_verifications((*existing, *notebook_rows))
        _write_manual_register(combined)
        register_changed = True

    write_connection_repairs(CONNECTION_REPAIR_REFERENCE, repairs)

    reloaded_register = load_manual_verifications(MANUAL_VERIFICATION_REGISTER)
    reloaded_repairs = load_connection_repairs(CONNECTION_REPAIR_REFERENCE)
    reloaded_notebook_rows = tuple(
        row
        for row in reloaded_register
        if row.verification_id.startswith(NOTEBOOK_20_PREFIX)
    )

    if reloaded_notebook_rows != notebook_rows:
        raise AssertionError("Notebook 20 register reload does not match generated rows")
    if reloaded_repairs != repairs:
        raise AssertionError("connection repair reference reload does not match generated rows")

    confirmed = sum(row.verification_status == "confirmed" for row in notebook_rows)
    unresolved = sum(row.verification_status == "unresolved" for row in notebook_rows)

    print("Notebook 20 connection verification promotion passed.")
    print(f"  evidence records: {len(evidence)}")
    print(f"  permanent verification records: {len(notebook_rows)}")
    print(f"  confirmed source supplementations: {confirmed}")
    print(f"  unresolved preserved blanks: {unresolved}")
    print(f"  governed connection repairs: {len(reloaded_repairs)}")
    print(f"  manual register changed: {register_changed}")
    print(
        "  wrote and reloaded: "
        f"{MANUAL_VERIFICATION_REGISTER.relative_to(PROJECT_ROOT)}"
    )
    print(
        "  wrote and reloaded: "
        f"{CONNECTION_REPAIR_REFERENCE.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
