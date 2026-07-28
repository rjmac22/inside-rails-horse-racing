"""Governed finishing-position and outcome parsing from Notebook 05."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
import sqlite3

from inside_rails.source_sqlite import quote_identifier

_POSITIVE_INTEGER = re.compile(r"^[1-9][0-9]*$")
_ZERO_INTEGER = re.compile(r"^0+$")


class ResultKind(StrEnum):
    FINISH_POSITION = "finish_position"
    ZERO_SENTINEL = "zero_sentinel"
    DISQUALIFIED = "disqualified"
    NON_FINISH_OUTCOME = "non_finish_outcome"
    MISSING = "missing"


@dataclass(frozen=True)
class ParsedResult:
    raw_pos: object
    result_kind: ResultKind
    finish_position: int | None
    outcome_code: str | None


def parse_result(raw_pos: object) -> ParsedResult:
    """Parse source ``pos`` without discarding its original representation."""

    if raw_pos is None:
        return ParsedResult(raw_pos, ResultKind.MISSING, None, None)

    text = str(raw_pos).strip()
    if text == "":
        return ParsedResult(raw_pos, ResultKind.MISSING, None, None)
    if _POSITIVE_INTEGER.fullmatch(text):
        return ParsedResult(raw_pos, ResultKind.FINISH_POSITION, int(text), None)
    if _ZERO_INTEGER.fullmatch(text):
        return ParsedResult(raw_pos, ResultKind.ZERO_SENTINEL, None, text)

    code = text.upper()
    if code == "DSQ":
        return ParsedResult(raw_pos, ResultKind.DISQUALIFIED, None, code)

    return ParsedResult(raw_pos, ResultKind.NON_FINISH_OUTCOME, None, code)


def profile_result_representation(
    connection: sqlite3.Connection,
    table_name: str = "data",
    header_rowid: int = 1,
) -> dict[str, int]:
    """Reconcile the complete source ``pos`` representation."""

    table = quote_identifier(table_name)
    row = connection.execute(
        f"""
        WITH source AS (
            SELECT TRIM(CAST(pos AS TEXT)) AS pos_text
            FROM {table}
            WHERE rowid <> ?
        )
        SELECT
            COUNT(*) AS data_rows,
            SUM(CASE WHEN pos_text GLOB '[1-9]*' AND pos_text NOT GLOB '*[^0-9]*' THEN 1 ELSE 0 END),
            SUM(CASE WHEN pos_text <> '' AND pos_text NOT GLOB '*[^0]*' THEN 1 ELSE 0 END),
            SUM(CASE WHEN UPPER(pos_text) = 'DSQ' THEN 1 ELSE 0 END),
            SUM(CASE WHEN pos_text <> ''
                      AND NOT (pos_text GLOB '[1-9]*' AND pos_text NOT GLOB '*[^0-9]*')
                      AND NOT (pos_text NOT GLOB '*[^0]*')
                      AND UPPER(pos_text) <> 'DSQ'
                     THEN 1 ELSE 0 END),
            SUM(CASE WHEN pos_text = '' OR pos_text IS NULL THEN 1 ELSE 0 END)
        FROM source
        """,
        (header_rowid,),
    ).fetchone()

    if row is None:
        raise RuntimeError(f"Unable to profile race results for table: {table_name}")

    keys = (
        "data_rows",
        "positive_numeric_position_rows",
        "zero_position_rows",
        "disqualified_rows",
        "other_text_outcome_rows",
        "missing_position_rows",
    )
    return dict(zip(keys, row, strict=True))
