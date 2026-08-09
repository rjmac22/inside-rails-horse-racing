"""End-to-end construction of a disposable Database v2 integration candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sqlite3
from time import perf_counter
from typing import Any

from inside_rails.database.accepted_source import validate_source_version_1_file_identity
from inside_rails.database.governed_integration_candidate import (
    GovernedIntegrationPreparationSummary,
    default_base_release_path,
    default_v2_candidate_path,
    prepare_governed_integration_candidate,
)
from inside_rails.database.governed_integration_horse_identity import (
    populate_governed_horse_identity,
)
from inside_rails.database.governed_integration_participant_identity import (
    populate_governed_participant_identity,
)
from inside_rails.database.governed_integration_population import (
    populate_governed_race_and_runner_extensions,
)
from inside_rails.database.governed_integration_references import (
    load_governed_reference_structures,
)
from inside_rails.database.governed_integration_time import populate_governed_race_times
from inside_rails.database.governed_integration_validator import (
    GovernedIntegrationValidationSummary,
    validate_governed_integration_candidate,
)
from inside_rails.database.minimum_core_candidate_io import (
    remove_output,
    require_no_sidecars,
)
from inside_rails.database.minimum_core_candidate_model import timestamp
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import configure_governed_connection
from inside_rails.source_sqlite import connect_read_only


BUILDER_VALIDATION_ROWS = (
    (
        "persisted_readback",
        "database-v2-governed-integration-builder",
        "1",
        "Database v2 persisted table counts and study-facing view populations reconciled after build.",
    ),
    (
        "sqlite_integrity",
        "sqlite-quick-check",
        sqlite3.sqlite_version,
        "PRAGMA quick_check returned exactly ok after Database v2 population.",
    ),
    (
        "foreign_key_validation",
        "sqlite-foreign-key-check",
        sqlite3.sqlite_version,
        "PRAGMA foreign_key_check returned zero rows after Database v2 population.",
    ),
    (
        "post_load_validation",
        "database-v2-governed-integration-builder",
        "1",
        "Database v2 core extension, reference, supplementation and provisional-identity populations matched the governed build baselines.",
    ),
)


@dataclass(frozen=True)
class GovernedIntegrationBuildSummary:
    output_path: str
    base_release_path: str
    source_path: str
    repository_commit: str
    reference_data_commit: str
    governed_integration_release_id: int
    manifest_code: str
    database_release_code: str
    preparation: dict[str, Any]
    reference_counts: dict[str, int]
    race_runner_summary: dict[str, Any]
    temporal_summary: dict[str, int]
    horse_identity_summary: dict[str, int]
    participant_identity_summary: dict[str, int]
    independent_validation: dict[str, Any]
    final_candidate_sha256_hex: str
    final_manifest_status: str
    validation_result_count: int
    build_elapsed_seconds: float
    release_accepted: bool


def _source_path(project_root: Path) -> Path:
    return (
        project_root
        / "data"
        / "raw"
        / "form_2015-present"
        / "form_2015-present"
        / "raceform.db"
    )


def _reference_counts(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        "course": int(connection.execute("SELECT COUNT(*) FROM reference_course").fetchone()[0]),
        "jurisdiction_context": int(
            connection.execute("SELECT COUNT(*) FROM reference_jurisdiction_context").fetchone()[0]
        ),
        "field_treatment": int(
            connection.execute("SELECT COUNT(*) FROM governance_source_field_treatment").fetchone()[0]
        ),
        "manual_verification": int(
            connection.execute("SELECT COUNT(*) FROM governance_manual_verification").fetchone()[0]
        ),
        "connection_decision": int(
            connection.execute("SELECT COUNT(*) FROM governance_connection_value_decision").fetchone()[0]
        ),
        "runner_supplementation": int(
            connection.execute("SELECT COUNT(*) FROM governance_runner_record_supplementation").fetchone()[0]
        ),
        "horse_specialist_decision": int(
            connection.execute(
                "SELECT COUNT(*) FROM governance_horse_pedigree_specialist_decision"
            ).fetchone()[0]
        ),
    }


def _finish_builder_stage(
    connection: sqlite3.Connection,
    *,
    completed_at_utc: str,
) -> None:
    """Record only checks actually performed by the builder and mark it built."""

    quick_check = str(connection.execute("PRAGMA quick_check").fetchone()[0])
    if quick_check != "ok":
        raise RuntimeError(f"Database v2 builder quick_check failed: {quick_check!r}")
    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_rows:
        raise RuntimeError(
            "Database v2 builder foreign_key_check returned rows: "
            f"{foreign_key_rows[:5]}"
        )

    # The normal study-facing runner view must expose every source-backed runner
    # plus the three explicitly governed missing-runner supplementations.
    race_view_count = int(
        connection.execute("SELECT COUNT(*) FROM view_governed_race_occurrences").fetchone()[0]
    )
    source_runner_view_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM view_governed_source_runner_participations"
        ).fetchone()[0]
    )
    runner_view_count = int(
        connection.execute("SELECT COUNT(*) FROM view_governed_runner_records").fetchone()[0]
    )
    if race_view_count != 189_043:
        raise RuntimeError(f"Governed race view count changed: {race_view_count}")
    if source_runner_view_count != 1_851_285:
        raise RuntimeError(
            f"Governed source-runner view count changed: {source_runner_view_count}"
        )
    if runner_view_count != 1_851_288:
        raise RuntimeError(
            f"Governed combined runner view count changed: {runner_view_count}"
        )

    for validation_id, (
        stage,
        validator_name,
        validator_version,
        summary,
    ) in enumerate(BUILDER_VALIDATION_ROWS, start=1):
        command = (
            "python scripts/build_inside_rails_v2.py"
            if stage in {"persisted_readback", "post_load_validation"}
            else f"PRAGMA {'quick_check' if stage == 'sqlite_integrity' else 'foreign_key_check'}"
        )
        connection.execute(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id,
                validation_stage, validator_name, validator_version,
                required_for_acceptance, outcome, executed_at_utc,
                command, result_summary, details_artifact_path
            ) VALUES (?, 1, ?, ?, ?, 1, 'passed', ?, ?, ?, NULL)
            """,
            (
                validation_id,
                stage,
                validator_name,
                validator_version,
                completed_at_utc,
                command,
                summary,
            ),
        )

    # building -> built is the only state transition performed by the builder.
    # The independent validator records the subsequent built -> validated step.
    connection.execute(
        """
        UPDATE import_manifest
        SET build_completed_at_utc = ?,
            persisted_readback_passed = 1,
            sqlite_integrity_passed = 1,
            foreign_key_check_passed = 1,
            post_load_validation_passed = 1,
            build_status = 'built'
        WHERE import_manifest_id = 1
          AND build_status = 'building'
        """,
        (completed_at_utc,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Database v2 builder could not advance manifest to built")
    connection.commit()


def _record_independent_validation(
    candidate_path: Path,
    summary: GovernedIntegrationValidationSummary,
) -> tuple[str, int]:
    """Persist the successful read-only validator result after it returns."""

    executed_at_utc, _ = timestamp(None)
    connection = sqlite3.connect(candidate_path)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        next_id = int(
            connection.execute(
                "SELECT COALESCE(MAX(import_validation_result_id), 0) + 1 FROM import_validation_result"
            ).fetchone()[0]
        )
        connection.execute(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id,
                validation_stage, validator_name, validator_version,
                required_for_acceptance, outcome, executed_at_utc,
                command, result_summary, details_artifact_path
            ) VALUES (
                ?, 1, 'source_wide_validation',
                'database-v2-governed-integration-validator', '1',
                1, 'passed', ?,
                'python scripts/validate_inside_rails_v2.py', ?, NULL
            )
            """,
            (
                next_id,
                executed_at_utc,
                (
                    "Independent Database v2 read-only validation passed; "
                    f"raw_fingerprints={summary.raw_record_fingerprints_recomputed}; "
                    f"race_rows={summary.race_rows}; runner_rows={summary.runner_rows}; "
                    f"temporal_rows={summary.temporal_rows}; "
                    f"horse_transitions={summary.horse_transition_rows}; "
                    f"participant_candidates={summary.participant_candidate_rows}."
                ),
            ),
        )
        connection.execute(
            """
            UPDATE import_manifest
            SET build_status = 'validated'
            WHERE import_manifest_id = 1
              AND build_status = 'built'
            """
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise RuntimeError("Database v2 validator could not advance manifest to validated")
        connection.commit()

        status = str(
            connection.execute(
                "SELECT build_status FROM import_manifest WHERE import_manifest_id = 1"
            ).fetchone()[0]
        )
        result_count = int(
            connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0]
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    require_no_sidecars(candidate_path, label="Validated Database v2 candidate")
    return status, result_count


def build_governed_integration_candidate(
    project_root: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    base_release_path: str | Path | None = None,
    output_path: str | Path | None = None,
    build_command: str = "python scripts/build_inside_rails_v2.py",
) -> GovernedIntegrationBuildSummary:
    """Build and independently validate one complete disposable Database v2 candidate."""

    started = perf_counter()
    root = Path(project_root).expanduser().resolve()
    source = _source_path(root)
    base = Path(base_release_path).resolve() if base_release_path else default_base_release_path(root)
    output = Path(output_path).resolve() if output_path else default_v2_candidate_path(root)
    reference_commit = reference_data_commit or repository_commit

    # Notebook 19 still derives from the immutable third-party source. Gate the
    # exact Source Version 1 file before creating any candidate so stale or
    # substituted local input cannot silently enter Database v2.
    validate_source_version_1_file_identity(source)

    preparation: GovernedIntegrationPreparationSummary | None = None
    try:
        preparation = prepare_governed_integration_candidate(
            base,
            output,
            repository_commit=repository_commit,
            reference_data_commit=reference_commit,
            build_command=build_command,
        )

        connection = sqlite3.connect(output)
        try:
            configure_governed_connection(connection, durable_candidate=True)
            governance_release_id = preparation.governed_integration_release_id

            load_governed_reference_structures(
                connection,
                root,
                governance_release_id=governance_release_id,
            )
            connection.commit()
            reference_counts = _reference_counts(connection)

            race_runner = populate_governed_race_and_runner_extensions(
                connection,
                governance_release_id=governance_release_id,
            )
            temporal = populate_governed_race_times(
                connection,
                governance_release_id=governance_release_id,
            )
            horse = populate_governed_horse_identity(
                connection,
                root,
                governance_release_id=governance_release_id,
            )
            participant = populate_governed_participant_identity(
                connection,
                root,
                governance_release_id=governance_release_id,
            )

            completed_at_utc, _ = timestamp(None)
            _finish_builder_stage(
                connection,
                completed_at_utc=completed_at_utc,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        require_no_sidecars(output, label="Built Database v2 candidate")
        independent = validate_governed_integration_candidate(output, base, root)
        final_status, validation_result_count = _record_independent_validation(
            output,
            independent,
        )

        # The validator stage writes only its own evidence/status after the
        # read-only validation succeeds. Recheck physical integrity and source
        # immutability once more before returning the candidate to the user.
        with connect_read_only(output) as connection:
            configure_governed_connection(connection, query_only=True)
            if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
                raise RuntimeError("Database v2 failed quick_check after validation recording")
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Database v2 failed foreign_key_check after validation recording")
        validate_source_version_1_file_identity(source)
    except Exception:
        remove_output(output)
        raise

    return GovernedIntegrationBuildSummary(
        output_path=str(output),
        base_release_path=str(base),
        source_path=str(source),
        repository_commit=repository_commit,
        reference_data_commit=reference_commit,
        governed_integration_release_id=preparation.governed_integration_release_id,
        manifest_code=preparation.manifest_code,
        database_release_code=preparation.database_release_code,
        preparation=asdict(preparation),
        reference_counts=reference_counts,
        race_runner_summary=asdict(race_runner),
        temporal_summary=temporal,
        horse_identity_summary=horse,
        participant_identity_summary=participant,
        independent_validation=asdict(independent),
        final_candidate_sha256_hex=sha256_file(output).hex(),
        final_manifest_status=final_status,
        validation_result_count=validation_result_count,
        build_elapsed_seconds=perf_counter() - started,
        release_accepted=False,
    )


__all__ = [
    "GovernedIntegrationBuildSummary",
    "build_governed_integration_candidate",
]
