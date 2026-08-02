import pandas as pd

from inside_rails.horse_pedigree_identity import (
    build_provisional_occurrences,
    build_transition_governance,
    parse_dam_label,
)


def test_parse_parenthesized_dam_suffix() -> None:
    assert parse_dam_label("Ascolini (NZ)") == ("Ascolini", "NZ", "parenthesized")


def test_parse_bare_dam_suffix() -> None:
    assert parse_dam_label("Example Mare IRE") == ("Example Mare", "IRE", "bare")


def test_parse_unsuffixed_and_blank_dam() -> None:
    assert parse_dam_label("Sun Song") == ("Sun Song", None, "unsuffixed")
    assert parse_dam_label("") == ("", None, "blank")
    assert parse_dam_label(None) == ("", None, "blank")


def _groups() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "horse": "Reused (GB)",
                "group_number": 1,
                "sire": "Sire A",
                "dam_structured_key": ("Dam A", "GB"),
                "damsire": "DS A",
                "runner_rows": 3,
                "first_date": pd.Timestamp("2018-01-01"),
                "last_date": pd.Timestamp("2018-12-31"),
                "minimum_age": 4,
                "maximum_age": 4,
                "sex_values": "g",
            },
            {
                "horse": "Reused (GB)",
                "group_number": 2,
                "sire": "Sire B",
                "dam_structured_key": ("Dam B", "GB"),
                "damsire": "DS B",
                "runner_rows": 2,
                "first_date": pd.Timestamp("2025-01-01"),
                "last_date": pd.Timestamp("2025-06-01"),
                "minimum_age": 3,
                "maximum_age": 3,
                "sex_values": "g",
            },
            {
                "horse": "Felix Felicis (FR)",
                "group_number": 1,
                "sire": "Affinisea (IRE)",
                "dam_structured_key": ("Just Eile", "IRE"),
                "damsire": "Presenting (GB)",
                "runner_rows": 1,
                "first_date": pd.Timestamp("2024-10-04"),
                "last_date": pd.Timestamp("2024-10-04"),
                "minimum_age": 2,
                "maximum_age": 2,
                "sex_values": "c",
            },
            {
                "horse": "Felix Felicis (FR)",
                "group_number": 2,
                "sire": "Olympic Glory (IRE)",
                "dam_structured_key": ("Sorina", "FR"),
                "damsire": "Le Havre (IRE)",
                "runner_rows": 4,
                "first_date": pd.Timestamp("2024-10-22"),
                "last_date": pd.Timestamp("2025-01-17"),
                "minimum_age": 2,
                "maximum_age": 3,
                "sex_values": "c",
            },
            {
                "horse": "Diamond Tipp (IRE)",
                "group_number": 1,
                "sire": "Diamond Boy (FR)",
                "dam_structured_key": ("Sound Out", None),
                "damsire": "Great Palm (USA)",
                "runner_rows": 1,
                "first_date": pd.Timestamp("2024-07-05"),
                "last_date": pd.Timestamp("2024-07-05"),
                "minimum_age": 7,
                "maximum_age": 7,
                "sex_values": "m",
            },
            {
                "horse": "Diamond Tipp (IRE)",
                "group_number": 2,
                "sire": "Diamond Boy (FR)",
                "dam_structured_key": ("Soundout", None),
                "damsire": "Oscar (IRE)",
                "runner_rows": 3,
                "first_date": pd.Timestamp("2024-08-18"),
                "last_date": pd.Timestamp("2025-01-01"),
                "minimum_age": 7,
                "maximum_age": 8,
                "sex_values": "m",
            },
        ]
    )


def test_transition_outcomes_distinguish_split_correction_and_unresolved() -> None:
    transitions = build_transition_governance(_groups())
    outcomes = transitions.set_index("horse")["analytical_outcome"].to_dict()
    assert outcomes == {
        "Reused (GB)": "Different horse",
        "Felix Felicis (FR)": "Corrected",
        "Diamond Tipp (IRE)": "Unresolved",
    }


def test_occurrence_assignment_only_splits_different_horse_boundaries() -> None:
    groups = _groups()
    transitions = build_transition_governance(groups)
    occurrences = build_provisional_occurrences(groups, transitions)
    counts = occurrences.groupby("horse").size().to_dict()
    assert counts == {
        "Diamond Tipp (IRE)": 1,
        "Felix Felicis (FR)": 1,
        "Reused (GB)": 2,
    }
    unresolved = occurrences.set_index("horse").loc["Diamond Tipp (IRE)"]
    assert unresolved["unresolved_boundaries"] == 1
