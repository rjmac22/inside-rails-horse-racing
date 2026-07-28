"""Conservative off-time parsing and explicit temporal reconstruction.

Notebook 11 established that the source ``off`` value is a UK-facing advertised
or scheduled clock representation. Parsing the clock text is deterministic;
choosing a 12-hour branch for ambiguous values is not. This module therefore
never selects an ambiguous branch without an explicit caller decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from enum import StrEnum
import re
from zoneinfo import ZoneInfo


_OFF_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})$")
UK_TIMEZONE = ZoneInfo("Europe/London")


class OffTimeKind(StrEnum):
    EXPLICIT_24H = "explicit_24h"
    AMBIGUOUS_12H = "ambiguous_12h"
    UNRESOLVED = "unresolved"


class OffTimeBranch(StrEnum):
    A = "A"
    B = "B"
    EXPLICIT_24H = "explicit_24h"


@dataclass(frozen=True)
class ParsedOffTime:
    raw_off: object
    kind: OffTimeKind
    hour: int | None
    minute: int | None
    candidate_a: time | None
    candidate_b: time | None


@dataclass(frozen=True)
class ReconstructedAdvertisedTime:
    source_date: date
    raw_off: str
    selected_branch: OffTimeBranch
    advertised_start_uk: datetime
    advertised_start_utc: datetime
    advertised_start_course_local: datetime
    course_timezone: str


def parse_off_time(raw_off: object) -> ParsedOffTime:
    """Parse the exact clock grammar without guessing an ambiguous branch."""
    if not isinstance(raw_off, str):
        return ParsedOffTime(raw_off, OffTimeKind.UNRESOLVED, None, None, None, None)

    match = _OFF_PATTERN.fullmatch(raw_off)
    if match is None:
        return ParsedOffTime(raw_off, OffTimeKind.UNRESOLVED, None, None, None, None)

    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23 or minute > 59:
        return ParsedOffTime(raw_off, OffTimeKind.UNRESOLVED, None, None, None, None)

    if hour == 0 or hour >= 13:
        explicit = time(hour, minute)
        return ParsedOffTime(
            raw_off,
            OffTimeKind.EXPLICIT_24H,
            hour,
            minute,
            explicit,
            None,
        )

    candidate_a = time(hour, minute)
    candidate_b = time((hour + 12) % 24, minute)
    return ParsedOffTime(
        raw_off,
        OffTimeKind.AMBIGUOUS_12H,
        hour,
        minute,
        candidate_a,
        candidate_b,
    )


def reconstruct_advertised_time(
    source_date: date,
    raw_off: str,
    selected_branch: OffTimeBranch,
    course_timezone: str,
) -> ReconstructedAdvertisedTime:
    """Build UK, UTC and course-local timestamps from an explicit decision.

    ``source_date`` is combined with the selected UK-facing advertised clock.
    Timezone conversion may naturally move the course-local date backward or
    forward. No branch, timezone or daylight-saving rule is inferred here.
    """
    parsed = parse_off_time(raw_off)
    if parsed.kind == OffTimeKind.UNRESOLVED:
        raise ValueError(f"unresolved off value: {raw_off!r}")

    if parsed.kind == OffTimeKind.EXPLICIT_24H:
        if selected_branch != OffTimeBranch.EXPLICIT_24H:
            raise ValueError("explicit 24-hour values require explicit_24h branch")
        selected_time = parsed.candidate_a
    else:
        if selected_branch == OffTimeBranch.A:
            selected_time = parsed.candidate_a
        elif selected_branch == OffTimeBranch.B:
            selected_time = parsed.candidate_b
        else:
            raise ValueError("ambiguous values require branch A or B")

    assert selected_time is not None
    uk_datetime = datetime.combine(source_date, selected_time, tzinfo=UK_TIMEZONE)
    utc_datetime = uk_datetime.astimezone(timezone.utc)
    local_datetime = utc_datetime.astimezone(ZoneInfo(course_timezone))

    return ReconstructedAdvertisedTime(
        source_date=source_date,
        raw_off=raw_off,
        selected_branch=selected_branch,
        advertised_start_uk=uk_datetime,
        advertised_start_utc=utc_datetime,
        advertised_start_course_local=local_datetime,
        course_timezone=course_timezone,
    )
