"""End-to-end construction of a disposable Database v3 reconciliation candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sqlite3
from time import perf_counter
from typing import Any

from inside_rails.database.external_reconciliation import (
    ExternalReconciliationSummary,
    load_external_reconciliation,
)
from inside_rails.database.external_reconciliation_candidate import (
    ExternalReconciliationPreparationSummary,
    default_base_release_path,
    default_v3_candidate_path,
    prepare_external_reconciliation_candidate,
)
from inside_rails.database.external_reconciliation_validator import (
    ExternalReconciliationValidationSummary,
    validate_external_reconciliation_candidate,
)
from inside_rails.database.minimum_core_candidate_io import remove_output, require_no_sidecars
from inside_rails.database.minimum_core_candidate_model import timestamp
from inside_rails.database.raw_mirror_prototype import sha256_file
from inside_rails.database.schema import configure_governed_connection
from inside_rails.source_sqlite import connect_read_only


BUILDER_VALIDATION_ROWS = (
    ("persisted_readback", "database-v3-external-reconciliation-builder", "1", "Database v3 persisted reconciliation counts and study-facing view counts matched the governed contract."),
    ("sqlite_integrity", "sqlite-quick-check", sqlite3.sqlite_version, "PRAGMA quick_check returned exactly ok after Database v3 reconciliation population."),
    ("foreign_key_validation", "sqlite-foreign-key-check", sqlite3.sqlite_version, "PRAGMA foreign_key_check returned zero rows after Database v3 reconciliation population."),
    ("post_load_validation", "database-v3-external-reconciliation-builder", "1", "Database v3 loaded 19 missing evidence rows and 37 typed resolutions without rewriting source/core data."),
)


@dataclass(frozen=True)
class ExternalReconciliationBuildSummary:
    output_path: str
    base_release_path: str
    repository_commit: str
    reference_data_commit: str
    external_reconciliation_release_id: int
    manifest_code: str
    database_release_code: str
    preparation: dict[str, Any]
    reconciliation: dict[str, int]
    independent_validation: dict[str, Any]
    final_candidate_sha256_hex: str
    final_manifest_status: str
    validation_result_count: int
    build_elapsed_seconds: float
    release_accepted: bool


def _finish_builder_stage(connection: sqlite3.Connection, *, completed_at_utc: str) -> None:
    quick = str(connection.execute("PRAGMA quick_check").fetchone()[0])
    if quick != "ok":
        raise RuntimeError(f"Database v3 builder quick_check failed: {quick!r}")
    fk_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if fk_rows:
        raise RuntimeError(f"Database v3 builder foreign_key_check returned rows: {fk_rows[:5]}")

    counts = (
        int(connection.execute("SELECT COUNT(*) FROM view_reconciled_race_occurrences").fetchone()[0]),
        int(connection.execute("SELECT COUNT(*) FROM view_reconciled_source_runner_participations").fetchone()[0]),
        int(connection.execute("SELECT COUNT(*) FROM view_reconciled_runner_records").fetchone()[0]),
    )
    if counts != (189_043, 1_851_285, 1_851_288):
        raise RuntimeError(f"Database v3 reconciled view counts changed: {counts!r}")

    for validation_id, (stage, name, version, summary) in enumerate(BUILDER_VALIDATION_ROWS, start=1):
        command = (
            "python scripts/build_inside_rails_v3.py"
            if stage in {"persisted_readback", "post_load_validation"}
            else f"PRAGMA {'quick_check' if stage == 'sqlite_integrity' else 'foreign_key_check'}"
        )
        connection.execute(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id, validation_stage,
                validator_name, validator_version, required_for_acceptance,
                outcome, executed_at_utc, command, result_summary,
                details_artifact_path
            ) VALUES (?,1,?,?,?,1,'passed',?,?,?,?)
            """,
            (
                validation_id,
                stage,
                name,
                version,
                completed_at_utc,
                command,
                summary,
                "docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md",
            ),
        )

    connection.execute(
        """
        UPDATE import_manifest
        SET build_completed_at_utc=?, persisted_readback_passed=1,
            sqlite_integrity_passed=1, foreign_key_check_passed=1,
            post_load_validation_passed=1, build_status='built'
        WHERE import_manifest_id=1 AND build_status='building'
        """,
        (completed_at_utc,),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise RuntimeError("Database v3 builder could not advance manifest to built")
    connection.commit()


def _record_independent_validation(
    candidate_path: Path,
    summary: ExternalReconciliationValidationSummary,
) -> tuple[str, int]:
    executed_at, _ = timestamp(None)
    connection = sqlite3.connect(candidate_path)
    try:
        configure_governed_connection(connection, durable_candidate=True)
        next_id = int(
            connection.execute(
                "SELECT COALESCE(MAX(import_validation_result_id),0)+1 FROM import_validation_result"
            ).fetchone()[0]
        )
        connection.execute(
            """
            INSERT INTO import_validation_result (
                import_validation_result_id, import_manifest_id, validation_stage,
                validator_name, validator_version, required_for_acceptance,
                outcome, executed_at_utc, command, result_summary,
                details_artifact_path
            ) VALUES (?,1,'source_wide_validation',
                      'database-v3-external-reconciliation-validator','1',1,
                      'passed',?,'python scripts/validate_inside_rails_v3.py',?,?)
            """,
            (
                next_id,
                executed_at,
                (
                    "Independent Database v3 validation passed; "
                    f"raw_rows_compared={summary.raw_record_rows_compared}; "
                    f"race_core_rows_compared={summary.structural_race_rows_compared}; "
                    f"runner_core_rows_compared={summary.structural_runner_rows_compared}; "
                    f"manual_verifications={summary.manual_verification_rows}; "
                    f"typed_resolutions={summary.resolution_rows}."
                ),
                "docs/DATABASE_V3_EXTERNAL_VERIFICATION_RECONCILIATION.md",
            ),
        )
        connection.execute(
            "UPDATE import_manifest SET build_status='validated' WHERE import_manifest_id=1 AND build_status='built'"
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise RuntimeError("Database v3 validator could not advance manifest to validated")
        connection.commit()
        status = str(connection.execute("SELECT build_status FROM import_manifest").fetchone()[0])
        result_count = int(connection.execute("SELECT COUNT(*) FROM import_validation_result").fetchone()[0])
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    require_no_sidecars(candidate_path, label="Validated Database v3 candidate")
    return status, result_count


def build_external_reconciliation_candidate(
    project_root: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    base_release_path: str | Path | None = None,
    output_path: str | Path | None = None,
    build_command: str = "python scripts/build_inside_rails_v3.py",
) -> ExternalReconciliationBuildSummary:
    """Copy accepted v2, apply v3 reconciliation, and independently validate it."""

    started = perf_counter()
    root = Path(project_root).expanduser().resolve()
    base = Path(base_release_path).resolve() if base_release_path else default_base_release_path(root)
    output = Path(output_path).resolve() if output_path else default_v3_candidate_path(root)
    reference_commit = reference_data_commit or repository_commit

    preparation: ExternalReconciliationPreparationSummary | None = None
    try:
        preparation = prepare_external_reconciliation_candidate(
            base,
            output,
            repository_commit=repository_commit,
            reference_data_commit=reference_commit,
            build_command=build_command,
        )
        connection = sqlite3.connect(output)
        try:
            configure_governed_connection(connection, durable_candidate=True)
            reconciliation: ExternalReconciliationSummary = load_external_reconciliation(
                connection,
                root,
                governance_release_id=preparation.external_reconciliation_release_id,
            )
            connection.commit()
            completed_at, _ = timestamp(None)
            _finish_builder_stage(connection, completed_at_utc=completed_at)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        require_no_sidecars(output, label="Built Database v3 candidate")
        independent = validate_external_reconciliation_candidate(output, base)
        final_status, validation_count = _record_independent_validation(output, independent)

        with connect_read_only(output) as connection:
            configure_governed_connection(connection, query_only=True)
            if str(connection.execute("PRAGMA quick_check").fetchone()[0]) != "ok":
                raise RuntimeError("Database v3 failed quick_check after validation recording")
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("Database v3 failed foreign_key_check after validation recording")
    except Exception:
        remove_output(output)
        raise

    return ExternalReconciliationBuildSummary(
        output_path=str(output),
        base_release_path=str(base),
        repository_commit=repository_commit,
        reference_data_commit=reference_commit,
        external_reconciliation_release_id=preparation.external_reconciliation_release_id,
        manifest_code=preparation.manifest_code,
        database_release_code=preparation.database_release_code,
        preparation=asdict(preparation),
        reconciliation=asdict(reconciliation),
        independent_validation=asdict(independent),
        final_candidate_sha256_hex=sha256_file(output).hex(),
        final_manifest_status=final_status,
        validation_result_count=validation_count,
        build_elapsed_seconds=perf_counter() - started,
        release_accepted=False,
    )


__all__ = ["ExternalReconciliationBuildSummary", "build_external_reconciliation_candidate"]
