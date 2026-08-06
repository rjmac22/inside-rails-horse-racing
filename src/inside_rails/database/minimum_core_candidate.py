"""Build a complete disposable Source Version 1 minimum-core candidate."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from time import perf_counter

from inside_rails.database.accepted_source import (
    RACEFORM_V1_FILE_SHA256,
    validate_source_version_1_file_identity,
)
from inside_rails.database.core_structure_prototype import (
    VALIDATED_RAW_MIRROR_CANDIDATE_SHA256,
)
from inside_rails.database.minimum_core_candidate_io import (
    copy_candidate,
    remove_output,
    require_no_sidecars,
    validate_file_hash,
)
from inside_rails.database.minimum_core_candidate_manifest import (
    finalise_manifest,
    validate_final_manifest,
)
from inside_rails.database.minimum_core_candidate_model import (
    EXPECTED_RACE_OCCURRENCE_COUNT,
    TIMESTAMP_FORMAT,
    MinimumCoreCandidateSummary,
    artifact_paths,
    expected_hash,
    positive_integer,
    repository_commit as validate_repository_commit,
    suffix,
    timestamp,
)
from inside_rails.database.minimum_core_candidate_population import (
    populate_races,
    populate_runners,
)
from inside_rails.database.minimum_core_candidate_readback import readback_core
from inside_rails.database.minimum_core_candidate_seed import (
    insert_governance,
    insert_manifest,
    validate_raw_boundary,
)
from inside_rails.database.raw_mirror_prototype import (
    RACEFORM_V1_BASELINE,
    SourceBaseline,
    sha256_file,
)
from inside_rails.database.schema import configure_governed_connection


_readback_core = readback_core
_finalise_manifest = finalise_manifest
_validate_final_manifest = validate_final_manifest


def build_minimum_core_candidate(
    source_path: str | Path,
    raw_mirror_candidate_path: str | Path,
    output_path: str | Path,
    *,
    repository_commit: str,
    reference_data_commit: str | None = None,
    build_command: str = "python scripts/build_minimum_core_candidate.py",
    batch_size: int = 5_000,
    baseline: SourceBaseline = RACEFORM_V1_BASELINE,
    expected_race_count: int = EXPECTED_RACE_OCCURRENCE_COUNT,
    created_at_utc: str | None = None,
    import_suffix: str | None = None,
    database_suffix: str | None = None,
    expected_source_sha256: bytes = RACEFORM_V1_FILE_SHA256,
    expected_candidate_sha256: bytes = VALIDATED_RAW_MIRROR_CANDIDATE_SHA256,
) -> MinimumCoreCandidateSummary:
    """Build and structurally validate a complete disposable core candidate."""

    batch_size = positive_integer(batch_size, name="batch_size")
    expected_race_count = positive_integer(
        expected_race_count,
        name="expected_race_count",
    )
    repository_commit = validate_repository_commit(
        repository_commit,
        name="repository_commit",
    )
    reference_data_commit = validate_repository_commit(
        reference_data_commit or repository_commit,
        name="reference_data_commit",
    )
    if not isinstance(build_command, str) or not build_command.strip():
        raise ValueError("build_command must be non-empty text")
    expected_source_sha256 = expected_hash(
        expected_source_sha256,
        name="expected_source_sha256",
    )
    expected_candidate_sha256 = expected_hash(
        expected_candidate_sha256,
        name="expected_candidate_sha256",
    )
    started_at, compact_timestamp = timestamp(created_at_utc)
    manifest_code = (
        f"imp:{compact_timestamp}:{suffix(import_suffix, name='import_suffix')}"
    )
    database_release_code = (
        f"db:{compact_timestamp}:{suffix(database_suffix, name='database_suffix')}"
    )

    source = Path(source_path).expanduser().resolve()
    raw_candidate = Path(raw_mirror_candidate_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if len({source, raw_candidate, output}) != 3:
        raise ValueError("Source, raw-mirror candidate and output paths must differ")
    existing = [path for path in artifact_paths(output) if path.exists()]
    if existing:
        raise FileExistsError(
            "Minimum-core candidate artifact already exists: "
            + ", ".join(str(path) for path in existing)
        )

    build_started = perf_counter()
    source_hash_before = validate_source_version_1_file_identity(
        source,
        expected_source_sha256=expected_source_sha256,
    )
    raw_candidate_hash_before = validate_file_hash(
        raw_candidate,
        expected_candidate_sha256,
        label="Raw-mirror candidate",
    )

    try:
        copied_bytes, copy_elapsed = copy_candidate(raw_candidate, output)
        copied_hash = sha256_file(output)
        if copied_hash != raw_candidate_hash_before:
            raise RuntimeError(
                "Copied raw-mirror candidate hash mismatch before core load"
            )

        connection = sqlite3.connect(output)
        population_started = perf_counter()
        try:
            configure_governed_connection(connection, durable_candidate=True)
            validate_raw_boundary(
                connection,
                source_sha256=source_hash_before,
                baseline=baseline,
            )
            connection.execute("BEGIN IMMEDIATE")
            insert_governance(
                connection,
                source_sha256=source_hash_before,
                repository_commit=repository_commit,
                timestamp=started_at,
            )
            insert_manifest(
                connection,
                manifest_code=manifest_code,
                database_release_code=database_release_code,
                repository_commit=repository_commit,
                reference_data_commit=reference_data_commit,
                build_command=build_command.strip(),
                started_at=started_at,
                baseline=baseline,
                expected_race_count=expected_race_count,
            )
            race_count, race_batch_count = populate_races(
                connection,
                source_sha256=source_hash_before,
                expected_race_count=expected_race_count,
                batch_size=batch_size,
            )
            runner_count, runner_batch_count = populate_runners(
                connection,
                source_sha256=source_hash_before,
                expected_runner_count=baseline.admitted_record_count,
                batch_size=batch_size,
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        population_elapsed = perf_counter() - population_started

        (
            race_readback,
            runner_readback,
            initial_quick,
            initial_fk_rows,
            initial_application_id,
            initial_user_version,
        ) = _readback_core(
            output,
            source_sha256=source_hash_before,
            baseline=baseline,
            expected_race_count=expected_race_count,
            manifest_code=manifest_code,
            database_release_code=database_release_code,
        )
        if initial_quick != "ok" or initial_fk_rows:
            raise RuntimeError(
                "Initial minimum-core structural checks did not pass"
            )

        completed_at = (
            started_at
            if created_at_utc is not None
            else datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
        )
        _finalise_manifest(
            output,
            completed_at=completed_at,
            build_command=build_command.strip(),
        )
        (
            manifest_status,
            validation_result_count,
            final_quick,
            final_fk_rows,
            application_id,
            user_version,
        ) = _validate_final_manifest(
            output,
            manifest_code=manifest_code,
            database_release_code=database_release_code,
            baseline=baseline,
            expected_race_count=expected_race_count,
        )
        if (
            application_id != initial_application_id
            or user_version != initial_user_version
        ):
            raise RuntimeError(
                "SQLite header changed during manifest finalisation"
            )

        source_hash_after = validate_source_version_1_file_identity(
            source,
            expected_source_sha256=expected_source_sha256,
        )
        raw_candidate_hash_after = validate_file_hash(
            raw_candidate,
            expected_candidate_sha256,
            label="Raw-mirror candidate",
        )
        require_no_sidecars(output, label="Minimum-core candidate")
        if source_hash_after != source_hash_before:
            raise RuntimeError(
                "Immutable source hash changed during minimum-core build"
            )
        if raw_candidate_hash_after != raw_candidate_hash_before:
            raise RuntimeError(
                "Raw-mirror candidate hash changed during minimum-core build"
            )
    except Exception:
        remove_output(output)
        raise

    build_elapsed = perf_counter() - build_started
    total_core_rows = race_count + runner_count
    return MinimumCoreCandidateSummary(
        source_path=str(source),
        raw_mirror_candidate_path=str(raw_candidate),
        output_path=str(output),
        source_file_sha256_hex=source_hash_before.hex(),
        raw_mirror_candidate_sha256_hex=raw_candidate_hash_before.hex(),
        copied_raw_mirror_sha256_hex=copied_hash.hex(),
        output_file_sha256_hex=sha256_file(output).hex(),
        source_file_size_bytes=source.stat().st_size,
        raw_mirror_candidate_file_size_bytes=raw_candidate.stat().st_size,
        output_file_size_bytes=output.stat().st_size,
        physical_record_count=baseline.physical_record_count,
        admitted_record_count=baseline.admitted_record_count,
        excluded_record_count=baseline.excluded_record_count,
        race_occurrence_count=race_count,
        runner_participation_count=runner_count,
        race_batch_count=race_batch_count,
        runner_batch_count=runner_batch_count,
        batch_size=batch_size,
        copied_bytes=copied_bytes,
        copy_elapsed_seconds=copy_elapsed,
        core_population_elapsed_seconds=population_elapsed,
        build_elapsed_seconds=build_elapsed,
        core_rows_per_second=(total_core_rows / population_elapsed),
        race_readback_comparisons=race_readback,
        runner_readback_comparisons=runner_readback,
        manifest_code=manifest_code,
        database_release_code=database_release_code,
        manifest_status=manifest_status,
        validation_result_count=validation_result_count,
        quick_check=final_quick,
        foreign_key_check_rows=final_fk_rows,
        application_id=application_id,
        user_version=user_version,
        source_hash_unchanged=True,
        raw_mirror_candidate_hash_unchanged=True,
        persisted_readback_passed=True,
        release_accepted=False,
    )


__all__ = [
    "EXPECTED_RACE_OCCURRENCE_COUNT",
    "MinimumCoreCandidateSummary",
    "build_minimum_core_candidate",
]
