"""Governed SQLite database primitives for Inside Rails."""

from .fingerprints import canonical_raceform_v1_row_message, raceform_v1_row_sha256
from .identifiers import (
    governance_method_code,
    governance_release_code,
    order_race_groups_by_minimum_source_rowid,
    runner_participation_code,
    source_race_occurrence_code,
    source_record_code,
    source_relation_code,
    source_version_code,
)
from .schema import (
    APPLICATION_ID,
    MINIMUM_SQLITE_VERSION,
    SCHEMA_VERSION,
    configure_governed_connection,
    create_minimum_core_schema,
    schema_inventory,
)

__all__ = [
    "APPLICATION_ID",
    "MINIMUM_SQLITE_VERSION",
    "SCHEMA_VERSION",
    "canonical_raceform_v1_row_message",
    "configure_governed_connection",
    "create_minimum_core_schema",
    "governance_method_code",
    "governance_release_code",
    "order_race_groups_by_minimum_source_rowid",
    "raceform_v1_row_sha256",
    "runner_participation_code",
    "schema_inventory",
    "source_race_occurrence_code",
    "source_record_code",
    "source_relation_code",
    "source_version_code",
]
