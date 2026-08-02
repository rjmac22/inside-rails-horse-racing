from pathlib import Path

import pandas as pd
import pytest

from inside_rails.horse_pedigree_identity import (
    IdentityGovernance,
    build_provisional_occurrences,
    build_transition_governance,
    load_identity_governance,
    parse_dam_label,
    structured_dam_key,
)

REFERENCE = Path("data/reference/horse_pedigree_identity_governance.csv")


def test_parse_parenthesized_dam_suffix() -> None:
    assert parse_dam_label("Ascolini (NZ)") == ("Ascolini", "NZ", "parenthesized")
    assert structured_dam_key("Ascolini (NZ)") == ("parsed_suffix", "Ascolini", "NZ")


def test_parse_bare_dam_suffix() -> None:
    assert parse_dam_label("Example Mare IRE") == ("Example Mare", "IRE", "bare")
    assert structured_dam_key("Example Mare IRE") == (
        "parsed_suffix",
        "Example Mare",
        "IRE",
    )


def test_terminal_numerals_are_not_country_suffixes() -> None:
    assert parse_dam_label("Sun Song II") == ("Sun Song II", None, "unsuffixed")
    assert structured_dam_key("Sun Song II") == (
        "raw_unsuffixed",
        "Sun Song II",
        None,
    )


def test_parse_unsuffixed_and_blank_dam() -> None:
    assert parse_dam_label("Sun Song") == ("Sun Song", None, "unsuffixed")
    assert structured_dam_key("Sun Song") == ("raw_unsuffixed", "Sun Song", None)
    assert parse_dam_label("") == ("", None, "blank")
    assert parse_dam_label(None) == ("", None, "blank")
    assert structured_dam_key(None) == ("blank", "", None)


def test_governed_reference_loads() -> None:
    governance = load_identity_governance(REFERENCE)
    assert len(governance.rows) == 16
    assert governance.full_pedigree_corrections == frozenset(
        {"Felix Felicis (FR)", "New President (FR)"}
    )
    assert governance.explicit_partial_splits == frozenset(
        {"Lyneham (FR)", "Marakan (IRE)", "What A Whopper (IRE)"}
    )
    assert governance.unresolved_horses == frozenset(
        {
            "Almavillalobas (GB)",
            "Colwyn Bay (FR)",
            "Diamond Tipp (IRE)",
            "LAziza Des Places (FR)",
            "Runninsonofagun (IRE)",
        }
    )


def test_duplicate_reference_decision_fails(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE, dtype=str, keep_default_na=False)
    frame.loc[1, "decision_id"] = frame.loc[0, "decision_id"]
    path = tmp_path / "duplicate.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="populated and unique"):
        load_identity_governance(path)


def test_unresolved_reference_cannot_assign_governed_pedigree(tmp_path: Path) -> None:
    frame = pd.read_csv(REFERENCE, dtype=str, keep_default_na=False)
    index = frame.index[frame["analytical_outcome"].eq("Unresolved")][0]
    frame.loc[index, "governed_dam"] = "Invented Dam"
    path = tmp_path / "invalid_unresolved.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="must not assign"):
        load_identity_governance(path)


def _governance() -> IdentityGovernance:
    return IdentityGovernance(
        rows=pd.DataFrame(
            {
                "horse": ["Felix Felicis (FR)", "Diamond Tipp (IRE)"],
                "verification_id": ["TEST-1", "TEST-2"],
            }
        ),
        full_pedigree_corrections=frozenset({"Felix Felicis (FR)"}),
        explicit_partial_splits=frozenset(),
        unresolved_horses=frozenset({"Diamond Tipp (IRE)"}),
    )


def _groups() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "horse": "Reused (GB)",
                "group_number": 1,
                "sire": "Sire A",
                "dam_structured_key": ("parsed_suffix", "Dam A", "GB"),
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
                "dam_structured_key": ("parsed_suffix", "Dam B", "GB"),
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
                "dam_structured_key": ("parsed_suffix", "Just Eile", "IRE"),
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
                "dam_structured_key": ("parsed_suffix", "Sorina", "FR"),
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
                "dam_structured_key": ("raw_unsuffixed", "Sound Out", None),
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
                "dam_structured_key": ("raw_unsuffixed", "Soundout", None),
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
    transitions = build_transition_governance(_groups(), _governance())
    outcomes = transitions.set_index("horse")["analytical_outcome"].to_dict()
    assert outcomes == {
        "Reused (GB)": "Different horse",
        "Felix Felicis (FR)": "Corrected",
        "Diamond Tipp (IRE)": "Unresolved",
    }


def test_occurrence_assignment_only_splits_different_horse_boundaries() -> None:
    groups = _groups()
    transitions = build_transition_governance(groups, _governance())
    occurrences = build_provisional_occurrences(groups, transitions)
    counts = occurrences.groupby("horse").size().to_dict()
    assert counts == {
        "Diamond Tipp (IRE)": 1,
        "Felix Felicis (FR)": 1,
        "Reused (GB)": 2,
    }
    unresolved = occurrences.set_index("horse").loc["Diamond Tipp (IRE)"]
    assert unresolved["unresolved_boundaries"] == 1
