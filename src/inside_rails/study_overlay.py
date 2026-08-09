"""Read-only overlays for verified facts awaiting the next database release.

Accepted Inside Rails database releases are immutable.  When later external
verification establishes an exact correction or enrichment, studies should not
knowingly continue to use the superseded value while waiting for a new release.

This module loads the typed post-release reconciliation register and builds a
pure SELECT query that overlays those values on a caller-supplied race query.
The accepted database and its raw/reconciled columns remain unchanged and the
overlay provenance is exposed explicitly in the result.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POST_V3_RESOLUTION_PATH = (
    REPOSITORY_ROOT / "data" / "reference" / "post_v3_external_value_resolutions.csv"
)

RACE_IDENTITY_COLUMNS = ("source_date", "source_course", "source_off")
SUPPORTED_RACE_FIELDS = {
    "type",
    "advertised_start_course_local",
    "actual_off_course_local",
}

_REQUIRED_COLUMNS = {
    "resolution_id",
    "verification_id",
    "scope",
    "source_date",
    "source_course",
    "source_off",
    "source_field",
    "resolution_kind",
    "governed_text_value",
    "analytical_action",
}


def load_pending_race_resolutions(
    path: str | Path = DEFAULT_POST_V3_RESOLUTION_PATH,
) -> list[dict[str, str]]:
    """Load and validate typed post-release race resolutions.

    The register is deliberately narrow.  Unsupported scopes or fields fail
    closed so a study cannot silently treat an ungoverned verification as an
    analytical correction.
    """

    resolution_path = Path(path).expanduser().resolve()
    if not resolution_path.is_file():
        raise FileNotFoundError(
            f"Post-release resolution register not found: {resolution_path}"
        )

    with resolution_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or ())
        missing_columns = sorted(_REQUIRED_COLUMNS - fieldnames)
        if missing_columns:
            raise ValueError(
                "Post-release resolution register is missing required columns: "
                + ", ".join(missing_columns)
            )
        rows = [dict(row) for row in reader]

    seen_field_keys: set[tuple[str, str, str, str]] = set()
    for row in rows:
        if row["scope"] != "race":
            raise ValueError(
                f"Unsupported post-release resolution scope: {row['scope']!r}"
            )

        source_field = row["source_field"]
        if source_field not in SUPPORTED_RACE_FIELDS:
            raise ValueError(
                f"Unsupported post-release race field: {source_field!r}"
            )

        if not all(row[column] for column in RACE_IDENTITY_COLUMNS):
            raise ValueError(
                "Every pending race resolution requires exact source "
                "date + course + off identity"
            )

        if not row["governed_text_value"]:
            raise ValueError(
                f"Resolution {row['resolution_id']} has no governed text value"
            )

        field_key = (
            row["source_date"],
            row["source_course"],
            row["source_off"],
            source_field,
        )
        if field_key in seen_field_keys:
            raise ValueError(
                "Duplicate pending resolution for source race field: "
                + " | ".join(field_key)
            )
        seen_field_keys.add(field_key)

    return rows


def _cte_values(
    rows: Iterable[dict[str, str]],
) -> tuple[str, list[str]]:
    """Return a parameterised VALUES body for one overlay CTE."""

    materialised = list(rows)
    if not materialised:
        # Keep the generated query valid when a supported overlay category has
        # no current rows.  The SELECT returns the same five text columns but
        # deliberately produces zero records.
        return (
            "SELECT NULL, NULL, NULL, NULL, NULL WHERE 0",
            [],
        )

    placeholders = ", ".join(["(?, ?, ?, ?, ?)"] * len(materialised))
    parameters: list[str] = []
    for row in materialised:
        parameters.extend(
            [
                row["source_date"],
                row["source_course"],
                row["source_off"],
                row["governed_text_value"],
                row["verification_id"],
            ]
        )
    return f"VALUES {placeholders}", parameters


def build_race_overlay_query(
    base_query: str,
    path: str | Path = DEFAULT_POST_V3_RESOLUTION_PATH,
) -> tuple[str, tuple[str, ...]]:
    """Wrap a race-level SELECT with the current verified post-release overlay.

    ``base_query`` must expose these Database v3 columns:

    - ``raw_date``;
    - ``raw_course``;
    - ``raw_off``;
    - ``race_type_raw``;
    - ``advertised_start_course_local``.

    ``raw_off`` is used only as part of the authorised Source Version 1 race
    identity for the join.  The helper does not make it the preferred display
    time.  Studies should normally display the governed course-local time.

    The returned SELECT preserves every base column and adds study-facing
    overlay values plus explicit provenance.  No write, temporary table or
    database mutation is performed.
    """

    stripped_query = base_query.strip().rstrip(";")
    if not stripped_query:
        raise ValueError("base_query must contain a race-level SELECT")

    resolutions = load_pending_race_resolutions(path)

    type_values, type_parameters = _cte_values(
        row for row in resolutions if row["source_field"] == "type"
    )
    time_values, time_parameters = _cte_values(
        row
        for row in resolutions
        if row["source_field"] == "advertised_start_course_local"
    )
    actual_values, actual_parameters = _cte_values(
        row
        for row in resolutions
        if row["source_field"] == "actual_off_course_local"
    )

    sql = f"""
    WITH
    base_races AS (
        {stripped_query}
    ),
    pending_race_type(
        source_date,
        source_course,
        source_off,
        governed_text_value,
        verification_id
    ) AS (
        {type_values}
    ),
    pending_advertised_local(
        source_date,
        source_course,
        source_off,
        governed_text_value,
        verification_id
    ) AS (
        {time_values}
    ),
    pending_actual_local(
        source_date,
        source_course,
        source_off,
        governed_text_value,
        verification_id
    ) AS (
        {actual_values}
    )
    SELECT
        b.*,
        COALESCE(rt.governed_text_value, b.race_type_raw) AS race_type_study,
        CASE
            WHEN rt.verification_id IS NULL THEN 'database_v3'
            ELSE 'post_v3_external_overlay'
        END AS race_type_study_source,
        rt.verification_id AS race_type_study_verification_id,
        COALESCE(
            at.governed_text_value,
            b.advertised_start_course_local
        ) AS advertised_start_course_local_study,
        CASE
            WHEN at.verification_id IS NULL THEN 'database_v3'
            ELSE 'post_v3_external_overlay'
        END AS advertised_start_course_local_study_source,
        at.verification_id AS advertised_start_course_local_study_verification_id,
        ao.governed_text_value AS actual_off_course_local_external,
        ao.verification_id AS actual_off_course_local_external_verification_id
    FROM base_races AS b
    LEFT JOIN pending_race_type AS rt
      ON rt.source_date = b.raw_date
     AND rt.source_course = b.raw_course
     AND rt.source_off = b.raw_off
    LEFT JOIN pending_advertised_local AS at
      ON at.source_date = b.raw_date
     AND at.source_course = b.raw_course
     AND at.source_off = b.raw_off
    LEFT JOIN pending_actual_local AS ao
      ON ao.source_date = b.raw_date
     AND ao.source_course = b.raw_course
     AND ao.source_off = b.raw_off
    """

    parameters = tuple(type_parameters + time_parameters + actual_parameters)
    return sql, parameters
