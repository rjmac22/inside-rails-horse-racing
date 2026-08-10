from datetime import date

from inside_rails.participant_identity import (
    has_exact_owner_token_multiset,
    has_reordered_owner_token_sequence,
    is_bounded_trainer_mlle_mme_transition,
    owner_token_multiset_key,
    same_race_supported_owner_keys,
    split_recognised_person_title,
)


def test_recognised_title_is_separated_without_changing_raw_label() -> None:
    governed = split_recognised_person_title("  Mlle   Marie Velon  ")
    assert governed.raw_label == "  Mlle   Marie Velon  "
    assert governed.title == "mlle"
    assert governed.post_title_label == "Marie Velon"
    assert governed.comparison_label == "marie velon"


def test_unknown_leading_word_is_not_treated_as_title() -> None:
    governed = split_recognised_person_title("Sheikh Hamdan Al Maktoum")
    assert governed.title is None
    assert governed.post_title_label == "Sheikh Hamdan Al Maktoum"


def test_blank_label_remains_blank_and_unresolved() -> None:
    governed = split_recognised_person_title("   ")
    assert governed.title is None
    assert governed.post_title_label == ""
    assert governed.comparison_label == ""


def test_owner_token_multiset_preserves_duplicate_tokens() -> None:
    key = owner_token_multiset_key("Mrs Jennifer Marsh Mrs Louise Marsh")
    assert key.count("mrs") == 2
    assert key.count("marsh") == 2


def test_exact_owner_token_multiset_ignores_order_and_punctuation() -> None:
    assert has_exact_owner_token_multiset(
        "Michael Tabor Derrick Smith Mrs John Magnier",
        "Mrs John Magnier, Michael Tabor & Derrick Smith",
    )


def test_owner_token_multiset_rejects_missing_member() -> None:
    assert not has_exact_owner_token_multiset(
        "Michael Tabor Derrick Smith Mrs John Magnier",
        "Michael Tabor Derrick Smith",
    )


def test_blank_owner_labels_do_not_match() -> None:
    assert not has_exact_owner_token_multiset("", "   ")


def test_reordered_owner_sequence_requires_genuine_order_change() -> None:
    assert has_reordered_owner_token_sequence(
        "Amo Racing Limited Giselle De Aguiar",
        "Giselle De Aguiar Amo Racing Limited",
    )
    assert not has_reordered_owner_token_sequence(
        "Amo Racing Limited",
        "Amo Racing Limited",
    )


def test_bounded_trainer_transition_accepts_observed_window() -> None:
    assert is_bounded_trainer_mlle_mme_transition(
        earlier_title="mlle",
        later_title="mme",
        earlier_post_title_label="Marie Velon",
        later_post_title_label="Marie Velon",
        earlier_last_date=date(2023, 10, 15),
        later_first_date=date(2024, 2, 1),
        active_periods_overlap=False,
    )


def test_bounded_trainer_transition_rejects_overlap() -> None:
    assert not is_bounded_trainer_mlle_mme_transition(
        earlier_title="mlle",
        later_title="mme",
        earlier_post_title_label="L Pontoir",
        later_post_title_label="L Pontoir",
        earlier_last_date=date(2023, 11, 1),
        later_first_date=date(2024, 1, 20),
        active_periods_overlap=True,
    )


def test_bounded_trainer_transition_rejects_outside_date_window() -> None:
    assert not is_bounded_trainer_mlle_mme_transition(
        earlier_title="mlle",
        later_title="mme",
        earlier_post_title_label="Example Trainer",
        later_post_title_label="Example Trainer",
        earlier_last_date=date(2021, 12, 31),
        later_first_date=date(2024, 1, 10),
        active_periods_overlap=False,
    )


def test_bounded_trainer_transition_rejects_different_names() -> None:
    assert not is_bounded_trainer_mlle_mme_transition(
        earlier_title="mlle",
        later_title="mme",
        earlier_post_title_label="Marie Velon",
        later_post_title_label="Marie Dupont",
        earlier_last_date=date(2023, 12, 1),
        later_first_date=date(2024, 1, 10),
        active_periods_overlap=False,
    )


def test_same_race_owner_support_requires_multiple_sequences() -> None:
    supported = same_race_supported_owner_keys(
        [[
            "Michael Tabor Derrick Smith Mrs John Magnier",
            "Mrs John Magnier Michael Tabor Derrick Smith",
            "Unrelated Owner",
        ]]
    )
    expected_key = owner_token_multiset_key(
        "Michael Tabor Derrick Smith Mrs John Magnier"
    )
    assert supported == frozenset({expected_key})


def test_same_race_owner_support_does_not_cross_races() -> None:
    supported = same_race_supported_owner_keys(
        [
            ["Michael Yarrow Heather Yarrow"],
            ["Heather Yarrow Michael Yarrow"],
        ]
    )
    assert supported == frozenset()
