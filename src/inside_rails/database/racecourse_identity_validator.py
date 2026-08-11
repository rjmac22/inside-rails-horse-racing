"""Independent read-only validation for Database v4 racecourse-identity candidates."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from time import perf_counter
import unicodedata
from typing import Any

from inside_rails.database.minimum_core_candidate_io import require_no_sidecars, validate_file_hash
from inside_rails.database.schema import configure_governed_connection
from inside_rails.source_sqlite import connect_read_only


APPLICATION_ID = 1_230_130_259
SCHEMA_VERSION = 4
EXPECTED_BASE_RELEASE_SHA256 = bytes.fromhex(
    "aa64991d0b2ae437539b38f799e57eb45450969a863caa54b9eea0d8f969dac0"
)
EXPECTED_BASE_RELEASE_SIZE_BYTES = 3_137_081_344
EXPECTED_BASE_DATABASE_RELEASE_CODE = "db:20260809T132557790891Z:84258cbc"
EXPECTED_PHYSICAL_RECORD_COUNT = 1_851_286
EXPECTED_ADMITTED_RECORD_COUNT = 1_851_285
EXPECTED_EXCLUDED_RECORD_COUNT = 1
EXPECTED_RACE_OCCURRENCE_COUNT = 189_043
EXPECTED_RUNNER_PARTICIPATION_COUNT = 1_851_285
EXPECTED_GB_RACE_COUNT = 111_634
EXPECTED_NOTEBOOK_COUNT = 61
EXPECTED_SOURCE_LABEL_COUNT = 65
EXPECTED_RACECOURSE_IDENTITY_COUNT = 61
EXPECTED_COURSE_INVENTORY_COUNT = 90
EXPECTED_STABLE_COURSE_IDENTITY_COUNT = 86
EXPECTED_UNRESOLVED_COUNT = 7
EXPECTED_BUILDER_VALIDATION_COUNT = 4
EXPECTED_V4_GOVERNANCE_RELEASE_ID = 4
STUDY03_EVIDENCE_COMMIT = "01c93aeff7f0a4ab7a22f6c37ad41656f7746e3b"
STUDY03_NOTEBOOK = (
    "studies/jurisdictions/great_britain/"
    "03_british_racecourse_and_course_identity.ipynb"
)
RACECOURSE_DIRECTORY = "studies/jurisdictions/great_britain/racecourses"

RESOLVED_STABLE_COLLAPSES = {
    ("Southwell", "All-Weather Flat Track — Fibresand"): "All-Weather Flat Track",
    ("Southwell", "All-Weather Flat Track — Tapeta"): "All-Weather Flat Track",
    ("Newcastle", "Former Flat Turf Track"): "Flat Track",
    ("Newcastle", "All-Weather Tapeta Track"): "Flat Track",
    ("Windsor", "Traditional Figure-of-Eight Turf Course"): "Windsor Turf Course",
    ("Windsor", "2024/25 Jump Extended Left-Hand Oval"): "Windsor Turf Course",
    ("Windsor", "2025/26 Jump Figure-of-Eight Configuration"): "Windsor Turf Course",
}
EXPECTED_NEWMARKET = {
    "Newmarket": (
        "Newmarket — Rowley Mile",
        "source_label_convention",
        "studies/jurisdictions/great_britain/racecourses/newmarket_rowley_mile.ipynb",
    ),
    "Newmarket (July)": (
        "Newmarket — July Course",
        "explicit_source_label",
        "studies/jurisdictions/great_britain/racecourses/newmarket_july_course.ipynb",
    ),
}
_ALLOWED_RESOLUTION_METHODS = {
    "study03_identity_direct",
    "explicit_source_label",
    "source_label_convention",
}
_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class ExpectedStudy03Snapshot:
    notebooks: tuple[tuple[str, bytes], ...]
    mappings: tuple[dict[str, Any], ...]
    inventory: tuple[dict[str, Any], ...]
    unresolved: tuple[dict[str, Any], ...]
    racecourse_names: tuple[str, ...]
    stable_keys: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RacecourseIdentityValidationSummary:
    candidate_path: str
    base_release_path: str
    candidate_sha256_hex: str
    manifest_status: str
    notebook_rows: int
    source_label_rows: int
    racecourse_rows: int
    inventory_rows: int
    stable_course_rows: int
    unresolved_rows: int
    gb_race_rows: int
    gb_distinct_race_rows: int
    raw_record_rows_compared: int
    structural_race_rows_compared: int
    structural_runner_rows_compared: int
    reference_course_rows_compared: int
    quick_check: str
    foreign_key_check_rows: int
    elapsed_seconds: float


def _git_bytes(root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip() or "unknown git error"
        raise RuntimeError(f"Unable to read frozen Study 03 evidence {path}: {detail}")
    return bytes(result.stdout)


def _git_notebook_paths(root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", STUDY03_EVIDENCE_COMMIT, RACECOURSE_DIRECTORY],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(f"Unable to enumerate frozen Study 03 evidence: {detail}")
    paths = tuple(
        sorted(
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip().endswith(".ipynb")
        )
    )
    if len(paths) != EXPECTED_NOTEBOOK_COUNT:
        raise RuntimeError(
            f"Frozen Study 03 notebook count changed: expected {EXPECTED_NOTEBOOK_COUNT}, observed {len(paths)}"
        )
    return paths


def _dataframe_literal_rows(notebook_bytes: bytes, variable_name: str, *, source: str, required: bool) -> list[dict[str, Any]]:
    notebook = json.loads(notebook_bytes.decode("utf-8"))
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = "".join(cell.get("source", []))
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in tree.body:
            targets: list[ast.expr] = []
            value: ast.expr | None = None
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
                value = node.value
            if value is None or not any(
                isinstance(target, ast.Name) and target.id == variable_name
                for target in targets
            ):
                continue
            if not (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Attribute)
                and isinstance(value.func.value, ast.Name)
                and value.func.value.id == "pd"
                and value.func.attr == "DataFrame"
                and value.args
            ):
                raise RuntimeError(f"{source}: {variable_name!r} is not a static pd.DataFrame literal")
            data = ast.literal_eval(value.args[0])
            columns = None
            for keyword in value.keywords:
                if keyword.arg == "columns":
                    columns = ast.literal_eval(keyword.value)
            if isinstance(data, list):
                if not data:
                    return []
                if all(isinstance(row, dict) for row in data):
                    return [dict(row) for row in data]
                if columns is not None and all(isinstance(row, (list, tuple)) for row in data):
                    if any(len(row) != len(columns) for row in data):
                        raise RuntimeError(f"{source}: {variable_name!r} row/column mismatch")
                    return [dict(zip(columns, row, strict=True)) for row in data]
            if isinstance(data, dict) and all(isinstance(values, list) for values in data.values()):
                lengths = {len(values) for values in data.values()}
                if len(lengths) != 1:
                    raise RuntimeError(f"{source}: {variable_name!r} unequal column lengths")
                count = next(iter(lengths), 0)
                return [{key: values[index] for key, values in data.items()} for index in range(count)]
            raise RuntimeError(f"{source}: unsupported {variable_name!r} DataFrame literal")
    if required:
        raise RuntimeError(f"{source}: {variable_name!r} not found")
    return []


def _slug(value: str) -> str:
    normalised = unicodedata.normalize("NFKD", value)
    ascii_value = normalised.encode("ascii", "ignore").decode("ascii").lower()
    slug = _SLUG_NON_ALNUM.sub("-", ascii_value).strip("-")
    if not slug:
        raise RuntimeError(f"Cannot derive expected stable slug from {value!r}")
    return slug


def _canonical_json(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def collect_expected_study03_snapshot(project_root: str | Path) -> ExpectedStudy03Snapshot:
    """Reconstruct expected Database v4 reference rows from the frozen Git snapshot."""

    root = Path(project_root).expanduser().resolve()
    verify = subprocess.run(
        ["git", "cat-file", "-e", f"{STUDY03_EVIDENCE_COMMIT}^{{commit}}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if verify.returncode != 0:
        raise RuntimeError(f"Frozen Study 03 commit unavailable: {STUDY03_EVIDENCE_COMMIT}")
    _git_bytes(root, STUDY03_EVIDENCE_COMMIT, STUDY03_NOTEBOOK)

    notebooks: list[tuple[str, bytes]] = []
    mappings: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for path in _git_notebook_paths(root):
        payload = _git_bytes(root, STUDY03_EVIDENCE_COMMIT, path)
        notebooks.append((path, hashlib.sha256(payload).digest()))
        source_rows = _dataframe_literal_rows(payload, "source_label_mapping", source=path, required=True)
        inventory_rows = _dataframe_literal_rows(payload, "course_inventory", source=path, required=True)
        unresolved_rows = _dataframe_literal_rows(payload, "unresolved_questions", source=path, required=False)
        for number, row in enumerate(source_rows, start=1):
            enriched = dict(row)
            enriched["source_notebook"] = path
            enriched["source_row_number"] = number
            mappings.append(enriched)
        for number, row in enumerate(inventory_rows, start=1):
            enriched = dict(row)
            enriched["source_notebook"] = path
            enriched["source_row_number"] = number
            inventory.append(enriched)
        for number, row in enumerate(unresolved_rows, start=1):
            enriched = dict(row)
            enriched["source_notebook"] = path
            enriched["source_row_number"] = number
            unresolved.append(enriched)

    if (len(mappings), len(inventory), len(unresolved)) != (
        EXPECTED_SOURCE_LABEL_COUNT,
        EXPECTED_COURSE_INVENTORY_COUNT,
        EXPECTED_UNRESOLVED_COUNT,
    ):
        raise RuntimeError(
            "Frozen Study 03 population changed: "
            f"mappings={len(mappings)}, inventory={len(inventory)}, unresolved={len(unresolved)}"
        )

    labels: set[str] = set()
    racecourses: set[str] = set()
    newmarket: dict[str, tuple[str, str, str]] = {}
    for row in mappings:
        if str(row.get("jurisdiction", "")).strip() != "Great Britain":
            raise RuntimeError(f"Unexpected frozen jurisdiction in {row['source_notebook']}")
        label = str(row.get("candidate_course_label", "")).strip()
        racecourse = str(row.get("racecourse_identity", "")).strip()
        if not label or not racecourse or label in labels:
            raise RuntimeError(f"Invalid or duplicate frozen source mapping: {row!r}")
        labels.add(label)
        racecourses.add(racecourse)
        method = str(row.get("racecourse_resolution_method") or "study03_identity_direct").strip()
        if method not in _ALLOWED_RESOLUTION_METHODS:
            raise RuntimeError(f"Unsupported frozen resolution method: {method!r}")
        if label in EXPECTED_NEWMARKET:
            newmarket[label] = (racecourse, method, str(row["source_notebook"]))

    if len(racecourses) != EXPECTED_RACECOURSE_IDENTITY_COUNT:
        raise RuntimeError(f"Frozen racecourse count changed: {len(racecourses)}")
    if newmarket != EXPECTED_NEWMARKET:
        raise RuntimeError(f"Frozen Newmarket resolution changed: {newmarket!r}")

    stable_keys: set[tuple[str, str]] = set()
    for row in inventory:
        racecourse = str(row.get("racecourse_identity", "")).strip()
        raw_name = str(row.get("course_or_track_name", "")).strip()
        if racecourse not in racecourses or not raw_name:
            raise RuntimeError(f"Invalid frozen course inventory row: {row!r}")
        stable = RESOLVED_STABLE_COLLAPSES.get((racecourse, raw_name), raw_name)
        row["stable_course_identity"] = stable
        stable_keys.add((racecourse, stable))
    if len(stable_keys) != EXPECTED_STABLE_COURSE_IDENTITY_COUNT:
        raise RuntimeError(f"Frozen stable-course count changed: {len(stable_keys)}")

    return ExpectedStudy03Snapshot(
        notebooks=tuple(sorted(notebooks)),
        mappings=tuple(sorted(mappings, key=lambda row: str(row["candidate_course_label"]))),
        inventory=tuple(sorted(inventory, key=lambda row: (str(row["source_notebook"]), int(row["source_row_number"])))),
        unresolved=tuple(sorted(unresolved, key=lambda row: (str(row["source_notebook"]), int(row["source_row_number"])))),
        racecourse_names=tuple(sorted(racecourses)),
        stable_keys=tuple(sorted(stable_keys)),
    )


def _compare_ordered_rows(candidate: sqlite3.Connection, base: sqlite3.Connection, query: str, *, label: str) -> int:
    left = candidate.execute(query)
    right = base.execute(query)
    count = 0
    while True:
        left_row = left.fetchone()
        right_row = right.fetchone()
        if left_row is None or right_row is None:
            if left_row != right_row:
                raise RuntimeError(f"Database v4 changed {label} row count/order")
            break
        if tuple(left_row) != tuple(right_row):
            raise RuntimeError(
                f"Database v4 changed {label} at compared row {count + 1}: "
                f"candidate={tuple(left_row)!r}, base={tuple(right_row)!r}"
            )
        count += 1
    return count


def _validate_manifest_and_lineage(connection: sqlite3.Connection) -> str:
    rows = connection.execute(
        """
        SELECT schema_version, physical_record_count, admitted_record_count,
               excluded_record_count, race_occurrence_count, runner_participation_count,
               build_status, failure_reason, prior_database_release_code,
               prior_release_preserved, code_commit, reference_data_commit,
               governance_release_id
        FROM import_manifest
        """
    ).fetchall()
    if len(rows) != 1:
        raise RuntimeError(f"Database v4 manifest count mismatch: {len(rows)}")
    row = rows[0]
    if tuple(row[:6]) != (
        SCHEMA_VERSION,
        EXPECTED_PHYSICAL_RECORD_COUNT,
        EXPECTED_ADMITTED_RECORD_COUNT,
        EXPECTED_EXCLUDED_RECORD_COUNT,
        EXPECTED_RACE_OCCURRENCE_COUNT,
        EXPECTED_RUNNER_PARTICIPATION_COUNT,
    ):
        raise RuntimeError(f"Database v4 manifest population mismatch: {row!r}")
    if row[6] not in {"built", "validated", "release_accepted"} or row[7] is not None:
        raise RuntimeError(f"Database v4 manifest status is not validatable: {row!r}")
    if row[8] != EXPECTED_BASE_DATABASE_RELEASE_CODE or int(row[9]) != 1:
        raise RuntimeError(f"Database v4 prior-release preservation mismatch: {row!r}")
    for value, name in ((row[10], "code_commit"), (row[11], "reference_data_commit")):
        text = str(value)
        if len(text) != 40 or any(char not in "0123456789abcdef" for char in text):
            raise RuntimeError(f"Database v4 invalid {name}: {value!r}")
    if int(row[12]) != EXPECTED_V4_GOVERNANCE_RELEASE_ID:
        raise RuntimeError(f"Database v4 manifest governance release mismatch: {row[12]!r}")

    releases = connection.execute(
        """
        SELECT governance_release_id, release_status, superseded_by_release_id
        FROM governance_release WHERE source_version_id=1 ORDER BY governance_release_id
        """
    ).fetchall()
    if releases != [
        (1, "superseded", 2),
        (2, "superseded", 3),
        (3, "superseded", 4),
        (4, "accepted", None),
    ]:
        raise RuntimeError(f"Database v4 governance lineage mismatch: {releases!r}")

    builder_rows = connection.execute(
        """
        SELECT validation_stage, outcome, required_for_acceptance
        FROM import_validation_result
        WHERE validator_name IN (
            'database-v4-racecourse-identity-builder',
            'sqlite-quick-check',
            'sqlite-foreign-key-check'
        )
        ORDER BY import_validation_result_id
        """
    ).fetchall()
    if len(builder_rows) < EXPECTED_BUILDER_VALIDATION_COUNT:
        raise RuntimeError(f"Database v4 builder validation evidence incomplete: {builder_rows!r}")
    if any(outcome != "passed" or int(required) != 1 for _, outcome, required in builder_rows):
        raise RuntimeError(f"Database v4 builder validation evidence contains failure: {builder_rows!r}")
    return str(row[6])


def _validate_notebooks(connection: sqlite3.Connection, expected: ExpectedStudy03Snapshot) -> None:
    observed = connection.execute(
        """
        SELECT source_notebook, notebook_sha256, study_evidence_commit, governance_release_id
        FROM governance_study03_racecourse_notebook
        ORDER BY source_notebook
        """
    ).fetchall()
    expected_rows = [
        (path, digest, STUDY03_EVIDENCE_COMMIT, EXPECTED_V4_GOVERNANCE_RELEASE_ID)
        for path, digest in expected.notebooks
    ]
    if observed != expected_rows:
        raise RuntimeError("Database v4 notebook provenance does not match frozen Study 03 bytes")


def _validate_racecourses_and_mappings(connection: sqlite3.Connection, expected: ExpectedStudy03Snapshot) -> None:
    expected_id_by_name = {name: index for index, name in enumerate(expected.racecourse_names, start=1)}
    expected_identities = [
        (
            expected_id_by_name[name],
            f"rc:gb:{_slug(name)}",
            name,
            "Great Britain",
            "venue",
            EXPECTED_V4_GOVERNANCE_RELEASE_ID,
        )
        for name in expected.racecourse_names
    ]
    observed_identities = connection.execute(
        """
        SELECT racecourse_identity_id, racecourse_identity_code, racecourse_name,
               jurisdiction, identity_kind, governance_release_id
        FROM reference_racecourse_identity
        ORDER BY racecourse_identity_id
        """
    ).fetchall()
    if observed_identities != expected_identities:
        raise RuntimeError("Database v4 racecourse identity population differs from frozen Study 03")

    observed_mappings = connection.execute(
        """
        SELECT candidate_course_label, racecourse_name, study03_grouping_name,
               racecourse_resolution_method, racecourse_resolution_evidence,
               source_notebook
        FROM view_gb_racecourse_identity_reference
        ORDER BY candidate_course_label
        """
    ).fetchall()
    expected_mappings = []
    for row in expected.mappings:
        racecourse = str(row["racecourse_identity"]).strip()
        expected_mappings.append(
            (
                str(row["candidate_course_label"]).strip(),
                racecourse,
                str(row.get("study03_grouping_name") or racecourse).strip(),
                str(row.get("racecourse_resolution_method") or "study03_identity_direct").strip(),
                str(row.get("racecourse_resolution_evidence") or row["source_notebook"]).strip(),
                str(row["source_notebook"]),
            )
        )
    if observed_mappings != expected_mappings:
        raise RuntimeError("Database v4 source-label racecourse mappings differ from frozen Study 03")

    newmarket = {
        label: (racecourse, method, notebook)
        for label, racecourse, _grouping, method, _evidence, notebook in observed_mappings
        if label in EXPECTED_NEWMARKET
    }
    if newmarket != EXPECTED_NEWMARKET:
        raise RuntimeError(f"Database v4 Newmarket resolution mismatch: {newmarket!r}")


def _validate_course_reference(connection: sqlite3.Connection, expected: ExpectedStudy03Snapshot) -> None:
    expected_racecourse_id = {name: index for index, name in enumerate(expected.racecourse_names, start=1)}
    expected_course_id = {key: index for index, key in enumerate(expected.stable_keys, start=1)}
    expected_courses = [
        (
            expected_course_id[(racecourse, course)],
            f"trk:gb:{_slug(racecourse)}:{_slug(course)}",
            expected_racecourse_id[racecourse],
            course,
            EXPECTED_V4_GOVERNANCE_RELEASE_ID,
        )
        for racecourse, course in expected.stable_keys
    ]
    observed_courses = connection.execute(
        """
        SELECT course_identity_id, course_identity_code, racecourse_identity_id,
               course_name, governance_release_id
        FROM reference_racecourse_course_identity
        ORDER BY course_identity_id
        """
    ).fetchall()
    if observed_courses != expected_courses:
        raise RuntimeError("Database v4 stable course identities differ from frozen Study 03")

    notebook_id_by_path = {
        path: index for index, (path, _digest) in enumerate(expected.notebooks, start=1)
    }
    expected_inventory = []
    for inventory_id, row in enumerate(expected.inventory, start=1):
        racecourse = str(row["racecourse_identity"]).strip()
        stable = str(row["stable_course_identity"]).strip()
        payload = {
            key: value
            for key, value in row.items()
            if key not in {"source_notebook", "source_row_number", "stable_course_identity"}
        }
        expected_inventory.append(
            (
                inventory_id,
                expected_course_id[(racecourse, stable)],
                notebook_id_by_path[str(row["source_notebook"])],
                int(row["source_row_number"]),
                str(row["course_or_track_name"]).strip(),
                None if row.get("surface") is None else str(row["surface"]).strip(),
                _canonical_json(payload),
                EXPECTED_V4_GOVERNANCE_RELEASE_ID,
            )
        )
    observed_inventory = connection.execute(
        """
        SELECT course_inventory_id, course_identity_id, racecourse_notebook_id,
               source_row_number, source_course_or_track_name, surface,
               inventory_payload_json, governance_release_id
        FROM reference_racecourse_course_inventory
        ORDER BY course_inventory_id
        """
    ).fetchall()
    if observed_inventory != expected_inventory:
        raise RuntimeError("Database v4 course inventory differs from frozen Study 03")
    for row in observed_inventory:
        payload = str(row[6])
        if _canonical_json(json.loads(payload)) != payload:
            raise RuntimeError("Database v4 course inventory JSON is not canonical")

    expected_unresolved = []
    for unresolved_id, row in enumerate(expected.unresolved, start=1):
        racecourse = str(row["racecourse_identity"]).strip()
        payload = {
            key: value
            for key, value in row.items()
            if key not in {"source_notebook", "source_row_number"}
        }
        expected_unresolved.append(
            (
                unresolved_id,
                expected_racecourse_id[racecourse],
                notebook_id_by_path[str(row["source_notebook"])],
                int(row["source_row_number"]),
                str(row["question"]).strip(),
                None if row.get("impact") is None else str(row["impact"]).strip(),
                None if row.get("unresolved_class") is None else str(row["unresolved_class"]).strip(),
                None if row.get("verification_status") is None else str(row["verification_status"]).strip(),
                _canonical_json(payload),
                EXPECTED_V4_GOVERNANCE_RELEASE_ID,
            )
        )
    observed_unresolved = connection.execute(
        """
        SELECT unresolved_question_id, racecourse_identity_id, racecourse_notebook_id,
               source_row_number, question, impact, unresolved_class,
               verification_status, unresolved_payload_json, governance_release_id
        FROM governance_racecourse_unresolved_question
        ORDER BY unresolved_question_id
        """
    ).fetchall()
    if observed_unresolved != expected_unresolved:
        raise RuntimeError("Database v4 unresolved governance rows differ from frozen Study 03")
    for row in observed_unresolved:
        payload = str(row[8])
        if _canonical_json(json.loads(payload)) != payload:
            raise RuntimeError("Database v4 unresolved JSON is not canonical")


def _validate_racecourse_race_view(connection: sqlite3.Connection, base: sqlite3.Connection, expected: ExpectedStudy03Snapshot) -> tuple[int, int]:
    base_gb = int(
        base.execute(
            "SELECT COUNT(*) FROM view_reconciled_race_occurrences WHERE candidate_jurisdiction='Great Britain'"
        ).fetchone()[0]
    )
    candidate_gb = int(
        connection.execute(
            "SELECT COUNT(*) FROM view_reconciled_race_occurrences WHERE candidate_jurisdiction='Great Britain'"
        ).fetchone()[0]
    )
    if (base_gb, candidate_gb) != (EXPECTED_GB_RACE_COUNT, EXPECTED_GB_RACE_COUNT):
        raise RuntimeError(f"Database v4 GB source race population changed: {(base_gb, candidate_gb)!r}")

    rows, distinct_rows = connection.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT source_race_occurrence_id)
        FROM view_gb_reconciled_race_occurrences_with_racecourse
        """
    ).fetchone()
    rows, distinct_rows = int(rows), int(distinct_rows)
    if (rows, distinct_rows) != (EXPECTED_GB_RACE_COUNT, EXPECTED_GB_RACE_COUNT):
        raise RuntimeError(f"Database v4 racecourse race-view cardinality changed: {(rows, distinct_rows)!r}")

    missing = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT source_race_occurrence_id
                FROM view_reconciled_race_occurrences
                WHERE candidate_jurisdiction='Great Britain'
                EXCEPT
                SELECT source_race_occurrence_id
                FROM view_gb_reconciled_race_occurrences_with_racecourse
            )
            """
        ).fetchone()[0]
    )
    extra = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT source_race_occurrence_id
                FROM view_gb_reconciled_race_occurrences_with_racecourse
                EXCEPT
                SELECT source_race_occurrence_id
                FROM view_reconciled_race_occurrences
                WHERE candidate_jurisdiction='Great Britain'
            )
            """
        ).fetchone()[0]
    )
    if missing or extra:
        raise RuntimeError(f"Database v4 racecourse race-view partition mismatch: missing={missing}, extra={extra}")

    source_counts = {
        str(label): int(count)
        for label, count in base.execute(
            """
            SELECT candidate_course_label, COUNT(*)
            FROM view_reconciled_race_occurrences
            WHERE candidate_jurisdiction='Great Britain'
            GROUP BY candidate_course_label
            """
        )
    }
    expected_mapping = {
        str(row["candidate_course_label"]).strip(): (
            str(row["racecourse_identity"]).strip(),
            str(row.get("racecourse_resolution_method") or "study03_identity_direct").strip(),
        )
        for row in expected.mappings
    }
    if set(source_counts) != set(expected_mapping):
        raise RuntimeError("Database v4 GB race source-label keyset differs from frozen Study 03")
    observed_distribution = connection.execute(
        """
        SELECT candidate_course_label, governed_racecourse_name,
               racecourse_resolution_method, COUNT(*)
        FROM view_gb_reconciled_race_occurrences_with_racecourse
        GROUP BY candidate_course_label, governed_racecourse_name, racecourse_resolution_method
        ORDER BY candidate_course_label
        """
    ).fetchall()
    expected_distribution = [
        (label, expected_mapping[label][0], expected_mapping[label][1], source_counts[label])
        for label in sorted(source_counts)
    ]
    if observed_distribution != expected_distribution:
        raise RuntimeError("Database v4 race-to-racecourse distribution differs from source population")

    newmarket_counts = {
        label: count
        for label, _racecourse, _method, count in observed_distribution
        if label in EXPECTED_NEWMARKET
    }
    if newmarket_counts != {"Newmarket": 1503, "Newmarket (July)": 1438}:
        raise RuntimeError(f"Database v4 Newmarket race counts changed: {newmarket_counts!r}")

    view_sql = connection.execute(
        "SELECT sql FROM sqlite_schema WHERE type='view' AND name='view_gb_reconciled_race_occurrences_with_racecourse'"
    ).fetchone()
    if view_sql is None or "reference_racecourse_course_identity" in str(view_sql[0]):
        raise RuntimeError("Database v4 racecourse race view improperly reaches physical course identity")
    columns = {
        str(row[1])
        for row in connection.execute("PRAGMA table_info(view_gb_reconciled_race_occurrences_with_racecourse)")
    }
    forbidden = {"course_identity_id", "course_identity_code", "governed_course_name"}
    if columns & forbidden:
        raise RuntimeError(f"Database v4 race view fabricates physical course assignment: {sorted(columns & forbidden)!r}")
    return rows, distinct_rows


def validate_racecourse_identity_candidate(
    candidate_path: str | Path,
    base_release_path: str | Path,
    project_root: str | Path,
) -> RacecourseIdentityValidationSummary:
    """Independently validate Database v4 without writing candidate or accepted v3."""

    started = perf_counter()
    candidate_path = Path(candidate_path).expanduser().resolve()
    base_release_path = Path(base_release_path).expanduser().resolve()
    root = Path(project_root).expanduser().resolve()
    require_no_sidecars(candidate_path, label="Database v4 candidate")
    require_no_sidecars(base_release_path, label="Accepted Database v3 release")
    if not candidate_path.is_file():
        raise FileNotFoundError(f"Database v4 candidate not found: {candidate_path}")
    if not base_release_path.is_file():
        raise FileNotFoundError(f"Accepted Database v3 release not found: {base_release_path}")
    if base_release_path.stat().st_size != EXPECTED_BASE_RELEASE_SIZE_BYTES:
        raise RuntimeError("Accepted Database v3 size changed")
    validate_file_hash(base_release_path, EXPECTED_BASE_RELEASE_SHA256, label="Accepted Database v3 release")
    candidate_sha = hashlib.sha256()
    with candidate_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            candidate_sha.update(chunk)
    expected = collect_expected_study03_snapshot(root)

    with connect_read_only(candidate_path) as candidate, connect_read_only(base_release_path) as base:
        configure_governed_connection(candidate, query_only=True)
        configure_governed_connection(base, query_only=True)
        if int(candidate.execute("PRAGMA application_id").fetchone()[0]) != APPLICATION_ID:
            raise RuntimeError("Database v4 application_id mismatch")
        if int(candidate.execute("PRAGMA user_version").fetchone()[0]) != SCHEMA_VERSION:
            raise RuntimeError("Database v4 user_version mismatch")
        if int(base.execute("PRAGMA user_version").fetchone()[0]) != 3:
            raise RuntimeError("Accepted Database v3 user_version changed")

        manifest_status = _validate_manifest_and_lineage(candidate)
        _validate_notebooks(candidate, expected)
        _validate_racecourses_and_mappings(candidate, expected)
        _validate_course_reference(candidate, expected)

        raw_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT source_record_id, source_rowid, structural_status, row_sha256 FROM source_raceform_v1_record ORDER BY source_record_id",
            label="raw source mirror",
        )
        race_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT source_race_occurrence_id, source_race_occurrence_code, source_version_id, raw_date, raw_course, raw_off, admitted_runner_count, governance_release_id FROM core_source_race_occurrence ORDER BY source_race_occurrence_id",
            label="structural race core",
        )
        runner_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT runner_participation_id, runner_participation_code, source_race_occurrence_id, source_record_id, source_record_status, governance_release_id FROM core_runner_participation ORDER BY runner_participation_id",
            label="structural runner core",
        )
        reference_course_compared = _compare_ordered_rows(
            candidate,
            base,
            "SELECT * FROM reference_course ORDER BY reference_course_id",
            label="reference_course",
        )

        counts = (
            int(candidate.execute("SELECT COUNT(*) FROM governance_study03_racecourse_notebook").fetchone()[0]),
            int(candidate.execute("SELECT COUNT(*) FROM reference_course_racecourse_map").fetchone()[0]),
            int(candidate.execute("SELECT COUNT(*) FROM reference_racecourse_identity").fetchone()[0]),
            int(candidate.execute("SELECT COUNT(*) FROM reference_racecourse_course_inventory").fetchone()[0]),
            int(candidate.execute("SELECT COUNT(*) FROM reference_racecourse_course_identity").fetchone()[0]),
            int(candidate.execute("SELECT COUNT(*) FROM governance_racecourse_unresolved_question").fetchone()[0]),
        )
        if counts != (
            EXPECTED_NOTEBOOK_COUNT,
            EXPECTED_SOURCE_LABEL_COUNT,
            EXPECTED_RACECOURSE_IDENTITY_COUNT,
            EXPECTED_COURSE_INVENTORY_COUNT,
            EXPECTED_STABLE_COURSE_IDENTITY_COUNT,
            EXPECTED_UNRESOLVED_COUNT,
        ):
            raise RuntimeError(f"Database v4 persisted Study 03 counts changed: {counts!r}")

        for table in (
            "governance_study03_racecourse_notebook",
            "reference_racecourse_identity",
            "reference_course_racecourse_map",
            "reference_racecourse_course_identity",
            "reference_racecourse_course_inventory",
            "governance_racecourse_unresolved_question",
        ):
            bad_release = int(
                candidate.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE governance_release_id <> ?",
                    (EXPECTED_V4_GOVERNANCE_RELEASE_ID,),
                ).fetchone()[0]
            )
            if bad_release:
                raise RuntimeError(f"Database v4 {table} contains {bad_release} rows outside governance release 4")

        gb_rows, gb_distinct = _validate_racecourse_race_view(candidate, base, expected)
        quick = str(candidate.execute("PRAGMA quick_check").fetchone()[0])
        if quick != "ok":
            raise RuntimeError(f"Database v4 quick_check failed: {quick!r}")
        fk_rows = candidate.execute("PRAGMA foreign_key_check").fetchall()
        if fk_rows:
            raise RuntimeError(f"Database v4 foreign_key_check returned rows: {fk_rows[:5]}")

    validate_file_hash(
        base_release_path,
        EXPECTED_BASE_RELEASE_SHA256,
        label="Accepted Database v3 release after v4 validation",
    )
    return RacecourseIdentityValidationSummary(
        candidate_path=str(candidate_path),
        base_release_path=str(base_release_path),
        candidate_sha256_hex=candidate_sha.hexdigest(),
        manifest_status=manifest_status,
        notebook_rows=counts[0],
        source_label_rows=counts[1],
        racecourse_rows=counts[2],
        inventory_rows=counts[3],
        stable_course_rows=counts[4],
        unresolved_rows=counts[5],
        gb_race_rows=gb_rows,
        gb_distinct_race_rows=gb_distinct,
        raw_record_rows_compared=raw_compared,
        structural_race_rows_compared=race_compared,
        structural_runner_rows_compared=runner_compared,
        reference_course_rows_compared=reference_course_compared,
        quick_check=quick,
        foreign_key_check_rows=0,
        elapsed_seconds=perf_counter() - started,
    )


__all__ = [
    "ExpectedStudy03Snapshot",
    "RacecourseIdentityValidationSummary",
    "STUDY03_EVIDENCE_COMMIT",
    "collect_expected_study03_snapshot",
    "validate_racecourse_identity_candidate",
]
