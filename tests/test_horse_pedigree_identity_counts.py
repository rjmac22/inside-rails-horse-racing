import pandas as pd

from inside_rails.horse_pedigree_identity_counts import (
    populated_contradiction_labels,
    populated_nunique,
)


def test_populated_nunique_ignores_null_and_blank_strings() -> None:
    values = pd.Series([None, "", "   ", "Sire A", "Sire A", "Sire B"])
    assert populated_nunique(values) == 2


def test_blank_to_populated_change_is_not_a_contradiction() -> None:
    rows = pd.DataFrame(
        [
            {"horse": "Example (GB)", "sire": "Sire A", "dam": "", "damsire": ""},
            {
                "horse": "Example (GB)",
                "sire": "Sire A",
                "dam": "Dam A",
                "damsire": "Damsire A",
            },
        ]
    )
    assert populated_contradiction_labels(rows, "dam").empty


def test_two_populated_values_are_a_contradiction() -> None:
    rows = pd.DataFrame(
        [
            {
                "horse": "Example (GB)",
                "sire": "Sire A",
                "dam": "Dam A",
                "damsire": "Damsire A",
            },
            {
                "horse": "Example (GB)",
                "sire": "Sire A",
                "dam": "Dam B",
                "damsire": "Damsire A",
            },
        ]
    )
    assert populated_contradiction_labels(rows, "dam").tolist() == ["Example (GB)"]
