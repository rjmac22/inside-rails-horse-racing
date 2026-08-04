"""Governed source-field inventory reconciled from Notebook 10.

The register preserves Notebook 10's bounded investigation groups while tracking
which later notebook or durable artifact now governs each field.
"""

from __future__ import annotations

from dataclasses import dataclass

SOURCE_FIELDS = (
    "date", "course", "race_id", "off", "race_name", "type", "class",
    "pattern", "rating_band", "age_band", "sex_rest", "dist", "going",
    "ran", "num", "pos", "draw", "ovr_btn", "btn", "horse", "age",
    "sex", "wgt", "hg", "time", "sp", "jockey", "trainer", "prize",
    "or", "rpr", "ts", "sire", "dam", "damsire", "owner", "comment",
)


@dataclass(frozen=True)
class FieldGovernance:
    field: str
    family: str
    investigation_group: str
    treatment: str
    governing_notebook: str
    status: str


_GROUPS = {
    "date": ("race_identity_and_timing", "race_identity", "structural_derivation", "03", "closed"),
    "course": ("race_identity_and_timing", "course_jurisdiction_and_identity", "structural_derivation", "04/09/12", "closed"),
    "race_id": ("race_identity_and_timing", "race_identity", "source_lineage", "03", "closed"),
    "off": ("race_identity_and_timing", "off_time_and_temporal_semantics", "deterministic_parsing", "11", "closed"),
    "race_name": ("race_classification_and_conditions", "race_classification_and_eligibility", "raw_preservation", "03/16", "preserve"),
    "type": ("race_classification_and_conditions", "race_classification_and_eligibility", "raw_plus_context", "09/16", "closed"),
    "class": ("race_classification_and_conditions", "race_classification_and_eligibility", "governed_structural_parsing", "16", "closed"),
    "pattern": ("race_classification_and_conditions", "race_classification_and_eligibility", "governed_structural_parsing", "16", "closed"),
    "rating_band": ("race_classification_and_conditions", "race_classification_and_eligibility", "governed_structural_parsing", "16", "closed"),
    "age_band": ("race_classification_and_conditions", "race_classification_and_eligibility", "governed_structural_parsing", "16", "closed"),
    "sex_rest": ("race_classification_and_conditions", "race_classification_and_eligibility", "governed_structural_parsing", "16", "closed"),
    "dist": ("race_classification_and_conditions", "race_distance", "deterministic_parsing", "06", "closed"),
    "going": ("race_classification_and_conditions", "race_classification_and_eligibility", "raw_plus_governed_category", "16", "closed"),
    "ran": ("race_structure_and_result", "runner_counts_numbers_and_entries", "governed_semantic_profile", "14", "closed"),
    "num": ("race_structure_and_result", "runner_counts_numbers_and_entries", "raw_plus_governed_derivation", "14", "closed"),
    "pos": ("race_structure_and_result", "finishing_positions_and_outcomes", "deterministic_parsing", "05", "closed"),
    "draw": ("runner_identity_and_characteristics", "runner_numbers_and_draw", "raw_preservation", "02/10", "preserve"),
    "ovr_btn": ("race_structure_and_result", "beaten_distance_semantics", "governed_semantic_interpretation", "15", "closed"),
    "btn": ("race_structure_and_result", "beaten_distance_semantics", "governed_semantic_interpretation", "15", "closed"),
    "horse": ("runner_identity_and_characteristics", "horse_and_pedigree_identity", "governed_source_identity", "19", "closed"),
    "age": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "governed_semantic_interpretation", "17", "closed"),
    "sex": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "governed_semantic_interpretation", "17", "closed"),
    "wgt": ("runner_identity_and_characteristics", "carried_weight", "deterministic_parsing", "07", "closed"),
    "hg": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "governed_semantic_interpretation", "17", "closed"),
    "time": ("race_identity_and_timing", "race_time_semantics", "temporal_reconstruction", "11", "closed"),
    "sp": ("performance_market_and_value", "starting_price_and_market_context", "deterministic_parsing", "08/09", "implemented_with_governed_anomaly"),
    "jockey": ("connections_and_ownership", "connections_and_owner_identity", "source_label_governance", "20", "closed"),
    "trainer": ("connections_and_ownership", "connections_and_owner_identity", "source_label_governance", "20", "closed"),
    "prize": ("performance_market_and_value", "prize_and_currency_semantics", "deterministic_parsing", "13", "closed"),
    "or": ("performance_market_and_value", "ratings_semantics_and_availability", "governed_nullable_rating", "18", "closed"),
    "rpr": ("performance_market_and_value", "ratings_semantics_and_availability", "governed_nullable_rating", "18", "closed"),
    "ts": ("performance_market_and_value", "ratings_semantics_and_availability", "governed_nullable_rating", "18", "closed"),
    "sire": ("pedigree", "horse_and_pedigree_identity", "governed_source_identity", "19", "closed"),
    "dam": ("pedigree", "horse_and_pedigree_identity", "governed_source_identity", "19", "closed"),
    "damsire": ("pedigree", "horse_and_pedigree_identity", "governed_source_identity", "19", "closed"),
    "owner": ("connections_and_ownership", "connections_and_owner_identity", "source_label_governance", "20", "closed"),
    "comment": ("free_text", "comment_and_embedded_information", "raw_free_text", "21", "closed"),
}


FIELD_GOVERNANCE = tuple(
    FieldGovernance(field, *_GROUPS[field]) for field in SOURCE_FIELDS
)
FIELD_GOVERNANCE_BY_NAME = {row.field: row for row in FIELD_GOVERNANCE}


def validate_field_governance() -> None:
    """Raise if the register is incomplete, duplicated or internally invalid."""
    if len(SOURCE_FIELDS) != 37 or len(set(SOURCE_FIELDS)) != 37:
        raise ValueError("source field inventory must contain exactly 37 unique fields")
    if set(_GROUPS) != set(SOURCE_FIELDS):
        missing = set(SOURCE_FIELDS) - set(_GROUPS)
        extra = set(_GROUPS) - set(SOURCE_FIELDS)
        raise ValueError(f"field governance mismatch: missing={missing}, extra={extra}")
    if len(FIELD_GOVERNANCE_BY_NAME) != 37:
        raise ValueError("field governance names must be unique")
    for row in FIELD_GOVERNANCE:
        if not all((row.family, row.investigation_group, row.treatment, row.governing_notebook, row.status)):
            raise ValueError(f"incomplete governance row: {row.field}")
