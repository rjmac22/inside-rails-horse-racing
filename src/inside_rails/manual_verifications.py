"""Load and validate governed manual source verifications."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

EXPECTED_COLUMNS = (
    "verification_id",
    "subject_type",
    "source_date",
    "source_course",
    "source_off",
    "source_horse",
    "source_field",
    "raw_source_value",
    "verification_question",
    "verified_value",
    "verification_status",
    "evidence_type",
    "evidence_locator",
    "evidence_accessed_date",
    "governing_notebook",
    "confidence",
    "notes",
    "database_action",
)

ALLOWED_VERIFICATION_STATUSES = {
    "confirmed",
    "contradicted",
    "partially_confirmed",
    "unresolved",
}

ALLOWED_CONFIDENCE = {"high", "medium", "low"}

ALLOWED_DATABASE_ACTIONS = {
    "evidence_only",
    "reference_enrichment",
    "source_correction_candidate",
    "preserve_raw_unresolved",
}


@dataclass(frozen=True)
class ManualVerification:
    verification_id: str
    subject_type: str
    source_date: str
    source_course: str
    source_off: str
    source_horse: str
    source_field: str
    raw_source_value: str
    verification_question: str
    verified_value: str
    verification_status: str
    evidence_type: str
    evidence_locator: str
    evidence_accessed_date: str
    governing_notebook: str
    confidence: str
    notes: str
    database_action: str


def _validate_date(value: str, field_name: str, verification_id: str) -> None:
    if not value:
        return
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"{verification_id}: {field_name} must be ISO YYYY-MM-DD, got {value!r}"
        ) from exc


def validate_manual_verifications(rows: Iterable[ManualVerification]) -> tuple[ManualVerification, ...]:
    materialised = tuple(rows)
    ids: set[str] = set()

    for row in materialised:
        if not row.verification_id:
            raise ValueError("verification_id must not be blank")
        if row.verification_id in ids:
            raise ValueError(f"duplicate verification_id: {row.verification_id}")
        ids.add(row.verification_id)

        if not row.subject_type:
            raise ValueError(f"{row.verification_id}: subject_type must not be blank")
        if not row.verification_question:
            raise ValueError(f"{row.verification_id}: verification_question must not be blank")
        if row.verification_status not in ALLOWED_VERIFICATION_STATUSES:
            raise ValueError(
                f"{row.verification_id}: invalid verification_status "
                f"{row.verification_status!r}"
            )
        if not row.evidence_type or not row.evidence_locator:
            raise ValueError(
                f"{row.verification_id}: evidence_type and evidence_locator are required"
            )
        if not row.governing_notebook:
            raise ValueError(f"{row.verification_id}: governing_notebook must not be blank")
        if row.confidence not in ALLOWED_CONFIDENCE:
            raise ValueError(f"{row.verification_id}: invalid confidence {row.confidence!r}")
        if row.database_action not in ALLOWED_DATABASE_ACTIONS:
            raise ValueError(
                f"{row.verification_id}: invalid database_action {row.database_action!r}"
            )

        _validate_date(row.source_date, "source_date", row.verification_id)
        _validate_date(
            row.evidence_accessed_date,
            "evidence_accessed_date",
            row.verification_id,
        )

        has_source_locator = any(
            (
                row.source_date,
                row.source_course,
                row.source_off,
                row.source_horse,
                row.source_field,
                row.raw_source_value,
            )
        )
        if not has_source_locator:
            raise ValueError(
                f"{row.verification_id}: at least one source locator/value must be present"
            )

        if row.verification_status == "confirmed" and not row.verified_value:
            raise ValueError(
                f"{row.verification_id}: confirmed rows require verified_value"
            )

    return materialised


def load_manual_verifications(path: str | Path) -> tuple[ManualVerification, ...]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError(
                "manual verification register columns do not match the governed schema"
            )
        rows = tuple(ManualVerification(**row) for row in reader)
    return validate_manual_verifications(rows)
