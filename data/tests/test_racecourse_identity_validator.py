from __future__ import annotations

from pathlib import Path

from inside_rails.database.racecourse_identity_validator import (
    EXPECTED_COURSE_INVENTORY_COUNT,
    EXPECTED_NOTEBOOK_COUNT,
    EXPECTED_RACECOURSE_IDENTITY_COUNT,
    EXPECTED_SOURCE_LABEL_COUNT,
    EXPECTED_STABLE_COURSE_IDENTITY_COUNT,
    EXPECTED_UNRESOLVED_COUNT,
    STUDY03_EVIDENCE_COMMIT,
    collect_expected_study03_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]


def test_independent_v4_validator_reconstructs_frozen_study03_exactly() -> None:
    snapshot = collect_expected_study03_snapshot(ROOT)

    assert STUDY03_EVIDENCE_COMMIT == "01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b"
    assert len(snapshot.notebooks) == EXPECTED_NOTEBOOK_COUNT == 61
    assert len(snapshot.mappings) == EXPECTED_SOURCE_LABEL_COUNT == 65
    assert len(snapshot.racecourse_names) == EXPECTED_RACECOURSE_IDENTITY_COUNT == 61
    assert len(snapshot.inventory) == EXPECTED_COURSE_INVENTORY_COUNT == 90
    assert len(snapshot.stable_keys) == EXPECTED_STABLE_COURSE_IDENTITY_COUNT == 86
    assert len(snapshot.unresolved) == EXPECTED_UNRESOLVED_COUNT == 7

    paths = {path for path, _digest in snapshot.notebooks}
    assert "studies/jurisdictions/great_britain/racecourses/newmarket.ipynb" not in paths
    assert "studies/jurisdictions/great_britain/racecourses/newmarket_rowley_mile.ipynb" in paths
    assert "studies/jurisdictions/great_britain/racecourses/newmarket_july_course.ipynb" in paths

    newmarket = {
        row["candidate_course_label"]: (
            row["racecourse_identity"],
            row["racecourse_resolution_method"],
            row["source_notebook"],
        )
        for row in snapshot.mappings
        if row["candidate_course_label"] in {"Newmarket", "Newmarket (July)"}
    }
    assert newmarket == {
        "Newmarket": (
            "Newmarket — Rowley Mile",
            "source_label_convention",
            "studies/jurisdictions/great_britain/racecourses/newmarket_rowley_mile.ipynb",
        ),
        "Newmarket (July)": (
            "Newmarket — July Course",
            "explicit_source_label",
            "studies/jurisdictions/great_britain/racecourses/newmarket_july_course.ipynb",
        ),
    }
