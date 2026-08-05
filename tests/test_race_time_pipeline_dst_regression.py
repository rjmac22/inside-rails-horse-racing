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


def test_dst_gap_meeting_remains_outside_profile_resolution() -> None:
    rows = [
        _race("2025-03-30", "1:30", 1),
        _race("2025-03-30", "2:00", 2),
    ]
    rows.extend(
        _race(f"2025-10-{day:02d}", "02:00", race_id)
        for day, race_id in zip(range(15, 20), range(3, 8), strict=True)
    )

    canonical = build_canonical_race_times(pd.DataFrame(rows))

    pre = canonical.loc[canonical["date"].eq("2025-03-30")]
    assert len(pre) == 2
    assert pre["temporal_resolution_status"].eq("unresolved").all()
    assert pre["decision_method"].eq("unresolved").all()
    assert pre["selected_branch"].isna().all()
    assert pre["candidate_a_course_local"].isna().sum() == 1
    assert pre["candidate_b_course_local"].notna().all()

    post = canonical.loc[canonical["date"].ge("2025-10-15")]
    assert len(post) == 5
    assert post["temporal_resolution_status"].eq("resolved").all()
