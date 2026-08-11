"""Governed Study 03 British racecourse/course identity reference loading."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import unicodedata
from typing import Any

EXPECTED_NOTEBOOK_COUNT = 61
EXPECTED_SOURCE_LABEL_COUNT = 65
EXPECTED_RACECOURSE_IDENTITY_COUNT = 61
EXPECTED_COURSE_INVENTORY_COUNT = 90
EXPECTED_STABLE_COURSE_IDENTITY_COUNT = 86
EXPECTED_UNRESOLVED_COUNT = 7

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

_NEWMARKET_EXPECTED = {
    "Newmarket": ("Newmarket — Rowley Mile", "source_label_convention"),
    "Newmarket (July)": ("Newmarket — July Course", "explicit_source_label"),
}
_ALLOWED_RESOLUTION_METHODS = {
    "study03_identity_direct",
    "explicit_source_label",
    "source_label_convention",
}
_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Study03ReferenceSummary:
    notebook_count: int
    source_label_count: int
    racecourse_identity_count: int
    course_inventory_count: int
    stable_course_identity_count: int
    unresolved_count: int


def _slug(value: str) -> str:
    normalised = unicodedata.normalize("NFKD", value)
    ascii_value = normalised.encode("ascii", "ignore").decode("ascii").lower()
    slug = _SLUG_NON_ALNUM.sub("-", ascii_value).strip("-")
    if not slug:
        raise ValueError(f"Cannot derive a stable slug from {value!r}")
    return slug


def _dataframe_literal_rows(
    notebook_path: Path,
    variable_name: str,
    *,
    required: bool,
) -> list[dict[str, Any]]:
    """Read one static ``pd.DataFrame`` assignment without executing notebook code."""
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        try:
            tree = ast.parse(source)
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
                raise RuntimeError(
                    f"{variable_name!r} in {notebook_path.name} is not a static pd.DataFrame literal"
                )
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
                if columns is not None and all(
                    isinstance(row, (list, tuple)) for row in data
                ):
                    if any(len(row) != len(columns) for row in data):
                        raise RuntimeError(
                            f"{variable_name!r} in {notebook_path.name} has a row/column mismatch"
                        )
                    return [dict(zip(columns, row, strict=True)) for row in data]
            if isinstance(data, dict) and all(
                isinstance(values, list) for values in data.values()
            ):
                lengths = {len(values) for values in data.values()}
                if len(lengths) != 1:
                    raise RuntimeError(
                        f"{variable_name!r} in {notebook_path.name} has unequal column lengths"
                    )
                count = next(iter(lengths), 0)
                return [
                    {key: values[index] for key, values in data.items()}
                    for index in range(count)
                ]
            raise RuntimeError(
                f"{variable_name!r} in {notebook_path.name} uses an unsupported DataFrame literal"
            )
    if required:
        raise RuntimeError(f"{variable_name!r} not found in {notebook_path.name}")
    return []


def _clean_text(value: Any, *, field: str, notebook: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{notebook}: required {field!r} is missing or blank")
    return value.strip()


def _canonical_json(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def collect_study03_reference(project_root: str | Path) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    root = Path(project_root).expanduser().resolve()
    racecourse_dir = root / RACECOURSE_DIRECTORY
    notebooks = sorted(racecourse_dir.glob("*.ipynb"))
    if len(notebooks) != EXPECTED_NOTEBOOK_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_NOTEBOOK_COUNT} Study 03 racecourse notebooks; found {len(notebooks)}"
        )

    notebook_rows: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for notebook_path in notebooks:
        relative = notebook_path.relative_to(root).as_posix()
        notebook_rows.append(
            {
                "source_notebook": relative,
                "notebook_sha256": hashlib.sha256(notebook_path.read_bytes()).digest(),
            }
        )
        source_rows = _dataframe_literal_rows(
            notebook_path, "source_label_mapping", required=True
        )
        inventory_rows = _dataframe_literal_rows(
            notebook_path, "course_inventory", required=True
        )
        unresolved_rows = _dataframe_literal_rows(
            notebook_path, "unresolved_questions", required=False
        )

        for row_number, row in enumerate(source_rows, start=1):
            row = dict(row)
            row["source_notebook"] = relative
            row["source_row_number"] = row_number
            mappings.append(row)
        for row_number, row in enumerate(inventory_rows, start=1):
            row = dict(row)
            row["source_notebook"] = relative
            row["source_row_number"] = row_number
            inventory.append(row)
        for row_number, row in enumerate(unresolved_rows, start=1):
            row = dict(row)
            row["source_notebook"] = relative
            row["source_row_number"] = row_number
            unresolved.append(row)

    _validate_reference_population(mappings, inventory, unresolved)
    return notebook_rows, mappings, inventory, unresolved


def _validate_reference_population(
    mappings: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
) -> None:
    if len(mappings) != EXPECTED_SOURCE_LABEL_COUNT:
        raise RuntimeError(
            f"Study 03 source-label mapping count changed: expected {EXPECTED_SOURCE_LABEL_COUNT}, "
            f"observed {len(mappings)}"
        )

    mapping_keys: set[tuple[str, str]] = set()
    racecourses: set[str] = set()
    newmarket_observed: dict[str, tuple[str, str]] = {}
    for row in mappings:
        notebook = str(row["source_notebook"])
        jurisdiction = _clean_text(
            row.get("jurisdiction"), field="jurisdiction", notebook=notebook
        )
        if jurisdiction != "Great Britain":
            raise RuntimeError(
                f"{notebook}: unexpected Study 03 jurisdiction {jurisdiction!r}"
            )
        label = _clean_text(
            row.get("candidate_course_label"),
            field="candidate_course_label",
            notebook=notebook,
        )
        racecourse = _clean_text(
            row.get("racecourse_identity"),
            field="racecourse_identity",
            notebook=notebook,
        )
        method = str(
            row.get("racecourse_resolution_method") or "study03_identity_direct"
        ).strip()
        if method not in _ALLOWED_RESOLUTION_METHODS:
            raise RuntimeError(
                f"{notebook}: unsupported racecourse resolution method {method!r}"
            )
        key = (label, jurisdiction)
        if key in mapping_keys:
            raise RuntimeError(f"Duplicate Study 03 source mapping {key!r}")
        mapping_keys.add(key)
        racecourses.add(racecourse)
        if label in _NEWMARKET_EXPECTED:
            newmarket_observed[label] = (racecourse, method)

    if newmarket_observed != _NEWMARKET_EXPECTED:
        raise RuntimeError(
            f"Study 03 Newmarket source-label resolution changed: {newmarket_observed!r}"
        )
    if len(racecourses) != EXPECTED_RACECOURSE_IDENTITY_COUNT:
        raise RuntimeError(
            "Study 03 racecourse identity count changed: "
            f"expected {EXPECTED_RACECOURSE_IDENTITY_COUNT}, observed {len(racecourses)}"
        )
    if len(inventory) != EXPECTED_COURSE_INVENTORY_COUNT:
        raise RuntimeError(
            f"Study 03 course inventory count changed: expected {EXPECTED_COURSE_INVENTORY_COUNT}, "
            f"observed {len(inventory)}"
        )

    stable_keys: set[tuple[str, str]] = set()
    inventory_keys: set[tuple[str, int]] = set()
    for row in inventory:
        notebook = str(row["source_notebook"])
        racecourse = _clean_text(
            row.get("racecourse_identity"),
            field="racecourse_identity",
            notebook=notebook,
        )
        if racecourse not in racecourses:
            raise RuntimeError(
                f"{notebook}: inventory racecourse {racecourse!r} has no source mapping"
            )
        raw_name = _clean_text(
            row.get("course_or_track_name"),
            field="course_or_track_name",
            notebook=notebook,
        )
        stable_name = RESOLVED_STABLE_COLLAPSES.get((racecourse, raw_name), raw_name)
        row["stable_course_identity"] = stable_name
        source_key = (notebook, int(row["source_row_number"]))
        if source_key in inventory_keys:
            raise RuntimeError(f"Duplicate Study 03 inventory source row {source_key!r}")
        inventory_keys.add(source_key)
        stable_keys.add((racecourse, stable_name))

    if len(stable_keys) != EXPECTED_STABLE_COURSE_IDENTITY_COUNT:
        raise RuntimeError(
            "Study 03 stable course identity count changed: "
            f"expected {EXPECTED_STABLE_COURSE_IDENTITY_COUNT}, observed {len(stable_keys)}"
        )
    if len(unresolved) != EXPECTED_UNRESOLVED_COUNT:
        raise RuntimeError(
            f"Study 03 unresolved count changed: expected {EXPECTED_UNRESOLVED_COUNT}, "
            f"observed {len(unresolved)}"
        )


def load_study03_racecourse_identity(
    connection: sqlite3.Connection,
    project_root: str | Path,
    *,
    governance_release_id: int,
) -> Study03ReferenceSummary:
    notebook_rows, mappings, inventory, unresolved = collect_study03_reference(
        project_root
    )

    existing = {
        (str(label), str(jurisdiction)): int(reference_course_id)
        for reference_course_id, label, jurisdiction in connection.execute(
            """
            SELECT reference_course_id, candidate_course_label, candidate_jurisdiction
            FROM reference_course
            WHERE candidate_jurisdiction = 'Great Britain'
            """
        )
    }
    expected_keys = {
        (str(row["candidate_course_label"]).strip(), "Great Britain")
        for row in mappings
    }
    missing = sorted(expected_keys - set(existing))
    extra = sorted(set(existing) - expected_keys)
    if missing or extra:
        raise RuntimeError(
            "Existing Great Britain reference_course population does not match Study 03: "
            f"missing={missing[:5]!r}; extra={extra[:5]!r}"
        )

    notebook_id_by_path: dict[str, int] = {}
    for notebook_id, row in enumerate(
        sorted(notebook_rows, key=lambda item: item["source_notebook"]), start=1
    ):
        notebook_id_by_path[str(row["source_notebook"])] = notebook_id
        connection.execute(
            """
            INSERT INTO governance_study03_racecourse_notebook (
                racecourse_notebook_id, source_notebook, notebook_sha256,
                study_evidence_commit, governance_release_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                notebook_id,
                row["source_notebook"],
                row["notebook_sha256"],
                STUDY03_EVIDENCE_COMMIT,
                governance_release_id,
            ),
        )

    racecourse_names = sorted(
        {str(row["racecourse_identity"]).strip() for row in mappings}
    )
    racecourse_id_by_name: dict[str, int] = {}
    racecourse_code_seen: set[str] = set()
    for racecourse_id, racecourse_name in enumerate(racecourse_names, start=1):
        code = f"rc:gb:{_slug(racecourse_name)}"
        if code in racecourse_code_seen:
            raise RuntimeError(f"Racecourse code collision: {code}")
        racecourse_code_seen.add(code)
        racecourse_id_by_name[racecourse_name] = racecourse_id
        connection.execute(
            """
            INSERT INTO reference_racecourse_identity (
                racecourse_identity_id, racecourse_identity_code, racecourse_name,
                jurisdiction, identity_kind, governance_release_id
            ) VALUES (?, ?, ?, 'Great Britain', 'venue', ?)
            """,
            (
                racecourse_id,
                code,
                racecourse_name,
                governance_release_id,
            ),
        )

    for row in sorted(mappings, key=lambda item: str(item["candidate_course_label"])):
        label = str(row["candidate_course_label"]).strip()
        racecourse_name = str(row["racecourse_identity"]).strip()
        grouping_name = str(
            row.get("study03_grouping_name") or racecourse_name
        ).strip()
        resolution_method = str(
            row.get("racecourse_resolution_method") or "study03_identity_direct"
        ).strip()
        resolution_evidence = str(
            row.get("racecourse_resolution_evidence") or row["source_notebook"]
        ).strip()
        connection.execute(
            """
            INSERT INTO reference_course_racecourse_map (
                reference_course_id, racecourse_identity_id, racecourse_notebook_id,
                study03_grouping_name, racecourse_resolution_method,
                racecourse_resolution_evidence, governance_release_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                existing[(label, "Great Britain")],
                racecourse_id_by_name[racecourse_name],
                notebook_id_by_path[str(row["source_notebook"])],
                grouping_name,
                resolution_method,
                resolution_evidence,
                governance_release_id,
            ),
        )

    stable_keys = sorted(
        {
            (
                str(row["racecourse_identity"]).strip(),
                str(row["stable_course_identity"]).strip(),
            )
            for row in inventory
        }
    )
    course_id_by_key: dict[tuple[str, str], int] = {}
    course_codes: set[str] = set()
    for course_id, (racecourse_name, stable_name) in enumerate(stable_keys, start=1):
        code = f"trk:gb:{_slug(racecourse_name)}:{_slug(stable_name)}"
        if code in course_codes:
            raise RuntimeError(f"Stable course code collision: {code}")
        course_codes.add(code)
        course_id_by_key[(racecourse_name, stable_name)] = course_id
        connection.execute(
            """
            INSERT INTO reference_racecourse_course_identity (
                course_identity_id, course_identity_code, racecourse_identity_id,
                course_name, governance_release_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                course_id,
                code,
                racecourse_id_by_name[racecourse_name],
                stable_name,
                governance_release_id,
            ),
        )

    inventory_sorted = sorted(
        inventory,
        key=lambda row: (
            str(row["source_notebook"]),
            int(row["source_row_number"]),
        ),
    )
    for inventory_id, row in enumerate(inventory_sorted, start=1):
        racecourse_name = str(row["racecourse_identity"]).strip()
        stable_name = str(row["stable_course_identity"]).strip()
        payload = {
            key: value
            for key, value in row.items()
            if key
            not in {"source_notebook", "source_row_number", "stable_course_identity"}
        }
        connection.execute(
            """
            INSERT INTO reference_racecourse_course_inventory (
                course_inventory_id, course_identity_id, racecourse_notebook_id,
                source_row_number, source_course_or_track_name, surface,
                inventory_payload_json, governance_release_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inventory_id,
                course_id_by_key[(racecourse_name, stable_name)],
                notebook_id_by_path[str(row["source_notebook"])],
                int(row["source_row_number"]),
                str(row["course_or_track_name"]).strip(),
                None if row.get("surface") is None else str(row["surface"]).strip(),
                _canonical_json(payload),
                governance_release_id,
            ),
        )

    unresolved_sorted = sorted(
        unresolved,
        key=lambda row: (
            str(row["source_notebook"]),
            int(row["source_row_number"]),
        ),
    )
    for unresolved_id, row in enumerate(unresolved_sorted, start=1):
        racecourse_name = str(row.get("racecourse_identity") or "").strip()
        if not racecourse_name:
            raise RuntimeError(
                f"{row['source_notebook']}: unresolved row lacks racecourse_identity"
            )
        payload = {
            key: value
            for key, value in row.items()
            if key not in {"source_notebook", "source_row_number"}
        }
        connection.execute(
            """
            INSERT INTO governance_racecourse_unresolved_question (
                unresolved_question_id, racecourse_identity_id, racecourse_notebook_id,
                source_row_number, question, impact, unresolved_class,
                verification_status, unresolved_payload_json, governance_release_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                unresolved_id,
                racecourse_id_by_name[racecourse_name],
                notebook_id_by_path[str(row["source_notebook"])],
                int(row["source_row_number"]),
                _clean_text(
                    row.get("question"),
                    field="question",
                    notebook=str(row["source_notebook"]),
                ),
                None if row.get("impact") is None else str(row["impact"]).strip(),
                None
                if row.get("unresolved_class") is None
                else str(row["unresolved_class"]).strip(),
                None
                if row.get("verification_status") is None
                else str(row["verification_status"]).strip(),
                _canonical_json(payload),
                governance_release_id,
            ),
        )

    counts = (
        int(
            connection.execute(
                "SELECT COUNT(*) FROM governance_study03_racecourse_notebook"
            ).fetchone()[0]
        ),
        int(
            connection.execute(
                "SELECT COUNT(*) FROM reference_course_racecourse_map"
            ).fetchone()[0]
        ),
        int(
            connection.execute(
                "SELECT COUNT(*) FROM reference_racecourse_identity"
            ).fetchone()[0]
        ),
        int(
            connection.execute(
                "SELECT COUNT(*) FROM reference_racecourse_course_inventory"
            ).fetchone()[0]
        ),
        int(
            connection.execute(
                "SELECT COUNT(*) FROM reference_racecourse_course_identity"
            ).fetchone()[0]
        ),
        int(
            connection.execute(
                "SELECT COUNT(*) FROM governance_racecourse_unresolved_question"
            ).fetchone()[0]
        ),
    )
    expected = (
        EXPECTED_NOTEBOOK_COUNT,
        EXPECTED_SOURCE_LABEL_COUNT,
        EXPECTED_RACECOURSE_IDENTITY_COUNT,
        EXPECTED_COURSE_INVENTORY_COUNT,
        EXPECTED_STABLE_COURSE_IDENTITY_COUNT,
        EXPECTED_UNRESOLVED_COUNT,
    )
    if counts != expected:
        raise RuntimeError(f"Persisted Study 03 reference counts changed: {counts!r}")

    return Study03ReferenceSummary(*counts)


__all__ = [
    "EXPECTED_COURSE_INVENTORY_COUNT",
    "EXPECTED_NOTEBOOK_COUNT",
    "EXPECTED_RACECOURSE_IDENTITY_COUNT",
    "EXPECTED_SOURCE_LABEL_COUNT",
    "EXPECTED_STABLE_COURSE_IDENTITY_COUNT",
    "EXPECTED_UNRESOLVED_COUNT",
    "RESOLVED_STABLE_COLLAPSES",
    "STUDY03_EVIDENCE_COMMIT",
    "Study03ReferenceSummary",
    "collect_study03_reference",
    "load_study03_racecourse_identity",
]
