"""Governed source-field inventory reconciled from Notebook 10.

The register preserves Notebook 10's bounded investigation groups while tracking
which later notebook or durable artifact now governs each field.
"""

from __future__ import annotations

from dataclasses import dataclass


SOURCE_FIELDS = (
    "date", "course", "race_id", "off", "race_name", "type", "class",
    "pattern", "rating_band", "age_band", "sex_rest", "dist", "going",
    "ran", "num", "pos", "ovr_btn", "btn", "horse", "age", "sex",
    "wgt", "draw", "hg", "jockey", "trainer", "owner", "or", "rpr",
    "ts", "sp", "sire", "dam", "damsire", "prize", "time", "comment",
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
    "course": ("race_identity_and_timing", "course_jurisdiction_and_identity", "structural_derivation", "04/09", "closed"),
    "race_id": ("race_identity_and_timing", "race_identity", "source_lineage", "03", "closed"),
    "off": ("race_identity_and_timing", "off_time_and_temporal_semantics", "deterministic_parsing", "11", "implemented_pending_audit"),
    "race_name": ("race_classification_and_conditions", "race_classification_and_eligibility", "raw_preservation", "10", "preserve"),
    "type": ("race_classification_and_conditions", "race_classification_and_eligibility", "raw_plus_context", "09", "closed"),
    "class": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "pattern": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "rating_band": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "age_band": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "sex_rest": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "dist": ("race_classification_and_conditions", "race_distance", "deterministic_parsing", "06", "closed"),
    "going": ("race_classification_and_conditions", "race_classification_and_eligibility", "semantic_investigation", "future", "open"),
    "ran": ("race_structure_and_result", "runner_counts_numbers_and_entries", "semantic_investigation", "future", "open"),
    "num": ("race_structure_and_result", "runner_counts_numbers_and_entries", "raw_preservation", "03/future", "open"),
    "pos": ("race_structure_and_result", "finishing_positions_and_outcomes", "deterministic_parsing", "05", "closed"),
    "ovr_btn": ("race_structure_and_result", "beaten_distance_semantics", "semantic_investigation", "future", "open"),
    "btn": ("race_structure_and_result", "beaten_distance_semantics", "semantic_investigation", "future", "open"),
    "horse": ("runner_identity_and_characteristics", "horse_and_pedigree_identity", "source_identity", "03/future", "open"),
    "age": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "semantic_investigation", "future", "open"),
    "sex": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "semantic_investigation", "future", "open"),
    "wgt": ("runner_identity_and_characteristics", "carried_weight", "deterministic_parsing", "07", "closed"),
    "draw": ("runner_identity_and_characteristics", "runner_numbers_and_draw", "raw_preservation", "02/10", "preserve"),
    "hg": ("runner_identity_and_characteristics", "runner_characteristics_and_equipment", "semantic_investigation", "future", "open"),
    "jockey": ("connections_and_ownership", "connections_and_owner_identity", "entity_resolution", "future", "open"),
    "trainer": ("connections_and_ownership", "connections_and_owner_identity", "entity_resolution", "future", "open"),
    "owner": ("connections_and_ownership", "connections_and_owner_identity", "entity_resolution", "future", "open"),
    "or": ("performance_market_and_value", "ratings_semantics_and_availability", "semantic_investigation", "future", "open"),
    "rpr": ("performance_market_and_value", "ratings_semantics_and_availability", "semantic_investigation", "future", "open"),
    "ts": ("performance_market_and_value", "ratings_semantics_and_availability", "semantic_investigation", "future", "open"),
    "sp": ("performance_market_and_value", "starting_price_and_market_context", "deterministic_parsing", "08/09", "implemented_with_governed_anomaly"),
    "sire": ("pedigree", "horse_and_pedigree_identity", "entity_resolution", "future", "open"),
    "dam": ("pedigree", "horse_and_pedigree_identity", "entity_resolution", "future", "open"),
    "damsire": ("pedigree", "horse_and_pedigree_identity", "entity_resolution", "future", "open"),
    "prize": ("performance_market_and_value", "prize_and_currency_semantics", "deterministic_parsing", "13", "closed"),
    "time": ("race_identity_and_timing", "race_time_semantics", "semantic_investigation", "future", "open"),
    "comment": ("free_text", "comment_and_embedded_information", "raw_free_text", "future", "open"),
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
