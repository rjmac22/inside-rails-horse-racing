"""Reusable code for the Inside Rails horse-racing database project."""

# Install Notebook 19's populated-only contradiction rule before consumers
# import the horse-pedigree implementation submodule directly.
from . import horse_pedigree_identity_counts as _horse_pedigree_identity_counts
from .prize_money import PrizeMoneyResult, parse_prize_money
from .race_classification import (
    AgeBandResult,
    ClassResult,
    PatternResult,
    RatingBandResult,
    SexRestrictionResult,
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)
from .ratings import (
    RatingResult,
    parse_rating,
    parse_rating_triplet,
)
from .source_sqlite import (
    HEADER_ROWID,
    PROVISIONAL_RACE_COLUMNS,
    PROVISIONAL_RUNNER_COLUMNS,
    connect_read_only,
    profile_source_database,
    quote_identifier,
)

__all__ = [
    "AgeBandResult",
    "ClassResult",
    "HEADER_ROWID",
    "PROVISIONAL_RACE_COLUMNS",
    "PROVISIONAL_RUNNER_COLUMNS",
    "PatternResult",
    "PrizeMoneyResult",
    "RatingBandResult",
    "RatingResult",
    "SexRestrictionResult",
    "classify_sex_restriction",
    "connect_read_only",
    "parse_age_band",
    "parse_class",
    "parse_pattern",
    "parse_prize_money",
    "parse_rating",
    "parse_rating_band",
    "parse_rating_triplet",
    "profile_source_database",
    "quote_identifier",
]
