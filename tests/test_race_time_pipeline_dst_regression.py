import pandas as pd

from inside_rails.race_time_pipeline import build_canonical_race_times


def _race(date: str, off: str, race_id: int) -> dict[str, object]:
    return {
        "date": date,
        "course": "DST Gap Course",
        "off": off,
        "race_id": race_id,
        "race_name": f"Race {race_id}",
        "type": "Flat",
        "candidate_course_label": "DST Gap Course",
        "candidate_jurisdiction": "Great Britain",
        "iana_timezone": "Europe/London",
    }


def test_pipeline_aggregates_meeting_with_dst_gap_nat_and_valid_timestamp() -> None:
    races = pd.DataFrame(
        [
            _race("2025-03-30", "1:30", 1),
            _race("2025-03-30", "2:00", 2),
            _race("2025-10-15", "19:00", 3),
        ]
    )

    canonical = build_canonical_race_times(races)

    pre = canonical.loc[canonical["date"].eq("2025-03-30")]
    assert len(pre) == 2
    assert pre["temporal_resolution_status"].eq("unresolved").all()
    assert pre["candidate_a_course_local"].isna().sum() == 1
    assert pre["candidate_b_course_local"].notna().all()
