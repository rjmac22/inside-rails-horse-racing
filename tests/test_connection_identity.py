import csv
from dataclasses import replace

import pytest

from inside_rails.connection_identity import (
    EVIDENCE_REQUIRED_COLUMNS,
    REPAIR_COLUMNS,
    build_connection_repairs,
    build_manual_verifications,
    build_repair_lookup,
    load_connection_evidence,
    load_connection_repairs,
    resolve_connection_value,
    verification_id_for_repair,
    write_connection_repairs,
)


VERIFIED_IDS = {
    1,
    2,
    *range(9, 18),
    *range(24, 33),
    *range(34, 38),
    38,
    39,
    40,
    42,
}
CONFLICT_IDS = {41, 43, 44, 45, 46}


def _field_for(number: int) -> str:
    if number <= 2:
        return "jockey"
    if number <= 37:
        return "owner"
    return "trainer"


def _evidence_rows() -> list[dict[str, str]]:
    rows = []
    for number in range(1, 47):
        verified = number in VERIFIED_IDS
        if verified:
            decision = "verified_repair"
            confidence = "high"
        elif number in CONFLICT_IDS:
            decision = "conflicting_evidence"
            confidence = "conflicting"
        else:
            decision = "insufficient_evidence"
            confidence = "insufficient"
        rows.append(
            {
                "repair_record_id": f"connection_blank_{number:03d}",
                "source_rowid": str(10_000 + number),
                "race_id": str(20_000 + number),
                "date": "2022-01-01",
                "course": "Example (GB)",
                "off": "1:00",
                "horse": f"Horse {number} (GB)",
                "missing_source_field": _field_for(number),
                "proposed_repaired_value": f"Value {number}" if verified else "",
                "evidence_source_name": "Example source",
                "evidence_source_type": "exact historical result",
                "evidence_locator": (
                    f"https://example.test/race/{number}"
                    if verified
                    else f"notebooks/20.ipynb#connection_blank_{number:03d}"
                ),
                "evidence_accessed_date": "2026-08-03",
                "verification_decision": decision,
                "verification_confidence": confidence,
                "reviewer_notes": "Bounded evidence review completed.",
            }
        )
    return rows


def _write_evidence(path, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVIDENCE_REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_evidence_promotion_builds_46_register_rows_and_28_repairs(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    _write_evidence(evidence_path, _evidence_rows())

    evidence = load_connection_evidence(evidence_path)
    verifications = build_manual_verifications(evidence)
    repairs = build_connection_repairs(evidence)

    assert len(verifications) == 46
    assert sum(row.verification_status == "confirmed" for row in verifications) == 28
    assert sum(row.verification_status == "unresolved" for row in verifications) == 18
    assert all(
        row.confidence == "low"
        for row in verifications
        if row.verification_status == "unresolved"
    )
    assert all(
        "evidence confidence marker=" in row.notes
        for row in verifications
        if row.verification_status == "unresolved"
    )
    assert len(repairs) == 28
    assert {repair.source_field for repair in repairs} == {"jockey", "trainer", "owner"}


def test_verified_repair_rejects_unresolved_confidence_marker(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    rows = _evidence_rows()
    rows[0]["verification_confidence"] = "insufficient"
    _write_evidence(evidence_path, rows)

    with pytest.raises(ValueError, match="invalid confidence 'insufficient'"):
        load_connection_evidence(evidence_path)


def test_verification_ids_are_permanent_and_deterministic() -> None:
    assert verification_id_for_repair("connection_blank_001") == "NB20-CONNECTION-0001"
    assert verification_id_for_repair("connection_blank_046") == "NB20-CONNECTION-0046"
    with pytest.raises(ValueError, match="invalid repair_record_id"):
        verification_id_for_repair("blank_001")


def test_evidence_loader_rejects_an_incomplete_queue(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    _write_evidence(evidence_path, _evidence_rows()[:-1])
    with pytest.raises(ValueError, match="expected 46 evidence rows"):
        load_connection_evidence(evidence_path)


def test_repair_reference_round_trip_and_resolution(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    repair_path = tmp_path / "repairs.csv"
    _write_evidence(evidence_path, _evidence_rows())
    repairs = build_connection_repairs(load_connection_evidence(evidence_path))
    write_connection_repairs(repair_path, repairs)

    with repair_path.open(encoding="utf-8") as handle:
        first_row = next(csv.DictReader(handle))
    assert tuple(first_row) == REPAIR_COLUMNS

    reloaded = load_connection_repairs(repair_path)
    lookup = build_repair_lookup(reloaded)
    first = reloaded[0]

    governed = resolve_connection_value(
        first.source_rowid, first.source_field, "", lookup
    )
    assert governed.effective_value == first.governed_value
    assert governed.value_status == "externally_supplemented"
    assert governed.verification_id == first.verification_id

    unresolved = resolve_connection_value(999_999, "owner", "", lookup)
    assert unresolved.effective_value is None
    assert unresolved.value_status == "source_blank_unresolved"

    source_present = resolve_connection_value(999_999, "owner", "Raw Owner", lookup)
    assert source_present.effective_value == "Raw Owner"
    assert source_present.value_status == "source_present"


def test_repair_never_overwrites_a_populated_source_value(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    _write_evidence(evidence_path, _evidence_rows())
    repairs = build_connection_repairs(load_connection_evidence(evidence_path))
    lookup = build_repair_lookup(repairs)
    first = repairs[0]

    with pytest.raises(ValueError, match="would overwrite a populated source value"):
        resolve_connection_value(
            first.source_rowid, first.source_field, "Already populated", lookup
        )


def test_duplicate_source_row_and_field_is_rejected(tmp_path) -> None:
    evidence_path = tmp_path / "evidence.csv"
    repair_path = tmp_path / "repairs.csv"
    _write_evidence(evidence_path, _evidence_rows())
    repairs = list(build_connection_repairs(load_connection_evidence(evidence_path)))
    repairs[1] = replace(
        repairs[1],
        source_rowid=repairs[0].source_rowid,
        source_field=repairs[0].source_field,
    )

    with pytest.raises(ValueError, match="duplicate source-row repair key"):
        write_connection_repairs(repair_path, repairs)
