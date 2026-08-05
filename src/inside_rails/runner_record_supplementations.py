"""Govern bounded missing-runner supplementations from Notebooks 14 and 15."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


EXPECTED_COLUMNS = (
    "supplementation_id",
    "verification_id",
    "source_date",
    "source_course",
    "source_off",
    "source_horse",
    "source_runner_rows",
    "source_ran",
    "published_runners",
    "verified_pos",
    "verified_outcome",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "confidence",
    "database_action",
    "notes",
)
EXPECTED_SUPPLEMENTATION_IDS = {
    "RUNNER-SUPPLEMENT-0001",
    "RUNNER-SUPPLEMENT-0002",
    "RUNNER-SUPPLEMENT-0003",
}
EXPECTED_VERIFICATION_IDS = {
    "NB14-RAN-0001",
    "NB14-RAN-0005",
    "NB15-BTN-0001",
}
ALLOWED_OUTCOMES = {"F", "did_not_finish", "finished"}


@dataclass(frozen=True)
class RunnerRecordSupplementation:
    supplementation_id: str
    verification_id: str
    source_date: str
    source_course: str
    source_off: str
    source_horse: str
    source_runner_rows: int
    source_ran: int
    published_runners: int
    verified_pos: int | None
    verified_outcome: str
    verification_status: str
    evidence_type: str
    evidence_locator: str
    evidence_accessed_date: str
    confidence: str
    database_action: str
    notes: str

    @property
    def race_key(self) -> tuple[str, str, str]:
        return self.source_date, self.source_course, self.source_off

    @property
    def runner_key(self) -> tuple[str, str, str, str]:
        return (*self.race_key, self.source_horse)


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _positive_integer(value: str, label: str) -> int:
    if not value.isdigit() or int(value) <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return int(value)


def _optional_positive_integer(value: str, label: str) -> int | None:
    if not value:
        return None
    return _positive_integer(value, label)


def validate_runner_record_supplementations(
    rows: Iterable[RunnerRecordSupplementation],
) -> tuple[RunnerRecordSupplementation, ...]:
    materialised = tuple(rows)
    if len(materialised) != 3:
        raise ValueError(
            f"expected 3 governed runner supplementations, found {len(materialised)}"
        )

    supplementation_ids = {row.supplementation_id for row in materialised}
    verification_ids = {row.verification_id for row in materialised}
    if supplementation_ids != EXPECTED_SUPPLEMENTATION_IDS:
        raise ValueError(
            f"unexpected supplementation IDs: {sorted(supplementation_ids)!r}"
        )
    if verification_ids != EXPECTED_VERIFICATION_IDS:
        raise ValueError(
            f"unexpected verification IDs: {sorted(verification_ids)!r}"
        )
    if len({row.runner_key for row in materialised}) != len(materialised):
        raise ValueError("runner supplementation keys must be unique")

    for row in materialised:
        date.fromisoformat(row.source_date)
        date.fromisoformat(row.evidence_accessed_date)
        if not row.source_course or not row.source_off or not row.source_horse:
            raise ValueError(f"{row.supplementation_id}: source locators are required")
        if row.source_runner_rows >= row.published_runners:
            raise ValueError(
                f"{row.supplementation_id}: supplementation requires a published runner "
                "absent from the source race population"
            )
        if row.source_ran <= 0 or row.published_runners <= 0:
            raise ValueError(f"{row.supplementation_id}: runner counts must be positive")
        if row.verified_outcome not in ALLOWED_OUTCOMES:
            raise ValueError(
                f"{row.supplementation_id}: unsupported verified outcome "
                f"{row.verified_outcome!r}"
            )
        if row.verified_outcome == "finished" and row.verified_pos is None:
            raise ValueError(
                f"{row.supplementation_id}: finished supplementation requires position"
            )
        if row.verified_outcome != "finished" and row.verified_pos is not None:
            raise ValueError(
                f"{row.supplementation_id}: non-finish supplementation must not assign position"
            )
        if row.verified_pos is not None and row.verified_pos > row.published_runners:
            raise ValueError(
                f"{row.supplementation_id}: position exceeds published runners"
            )
        if row.verification_status != "confirmed":
            raise ValueError(f"{row.supplementation_id}: verification must be confirmed")
        if row.database_action != "source_supplementation":
            raise ValueError(
                f"{row.supplementation_id}: action must be source_supplementation"
            )
        if row.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"{row.supplementation_id}: invalid confidence")
        locators = [value.strip() for value in row.evidence_locator.split("|")]
        if not locators or any(not value.startswith("https://") for value in locators):
            raise ValueError(
                f"{row.supplementation_id}: direct HTTPS evidence is required"
            )
        if not row.evidence_type or not row.notes:
            raise ValueError(
                f"{row.supplementation_id}: evidence type and notes are required"
            )

    return tuple(sorted(materialised, key=lambda row: row.supplementation_id))


def load_runner_record_supplementations(
    path: str | Path,
) -> tuple[RunnerRecordSupplementation, ...]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError(
                "runner supplementation reference columns changed: "
                f"{tuple(reader.fieldnames or ())!r}"
            )
        output = []
        for raw in reader:
            row = {key: _clean(value) for key, value in raw.items()}
            output.append(
                RunnerRecordSupplementation(
                    supplementation_id=row["supplementation_id"],
                    verification_id=row["verification_id"],
                    source_date=row["source_date"],
                    source_course=row["source_course"],
                    source_off=row["source_off"],
                    source_horse=row["source_horse"],
                    source_runner_rows=_positive_integer(
                        row["source_runner_rows"],
                        f"{row['supplementation_id']}: source_runner_rows",
                    ),
                    source_ran=_positive_integer(
                        row["source_ran"],
                        f"{row['supplementation_id']}: source_ran",
                    ),
                    published_runners=_positive_integer(
                        row["published_runners"],
                        f"{row['supplementation_id']}: published_runners",
                    ),
                    verified_pos=_optional_positive_integer(
                        row["verified_pos"],
                        f"{row['supplementation_id']}: verified_pos",
                    ),
                    verified_outcome=row["verified_outcome"],
                    verification_status=row["verification_status"],
                    evidence_type=row["evidence_type"],
                    evidence_locator=row["evidence_locator"],
                    evidence_accessed_date=row["evidence_accessed_date"],
                    confidence=row["confidence"],
                    database_action=row["database_action"],
                    notes=row["notes"],
                )
            )
    return validate_runner_record_supplementations(output)
