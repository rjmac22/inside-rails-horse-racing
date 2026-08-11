#!/usr/bin/env python3
"""Run the complete applicable independent-validator gate safely and reproducibly.

This is the canonical project-level validator runner. It discovers the current
``scripts/validate_*.py`` inventory, excludes only the three historical Database
v1 construction-only validators, resolves required positional inputs from each
validator's argparse declaration, and runs validators in deterministic filename
order.

The runner never uses ``shell=True`` and never changes the caller's shell
options. A validator failure stops this Python process with a non-zero status,
but it does not execute ``exit`` in the interactive shell that launched it.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
SOURCE_VERSION_1 = (
    ROOT
    / "data"
    / "raw"
    / "form_2015-present"
    / "form_2015-present"
    / "raceform.db"
)
COURSE_LOCATION_REFERENCE = ROOT / "data" / "reference" / "course_locations.csv"

EXPECTED_VALIDATOR_COUNT = 35
EXPECTED_APPLICABLE_COUNT = 32

EXCLUDED_VALIDATORS = {
    "validate_core_structure_prototype.py": (
        "historical Database v1 construction-only validator; requires disposable "
        "prototype artefacts that are not an acceptance dependency"
    ),
    "validate_raw_mirror_candidate.py": (
        "historical Database v1 construction-only validator; requires the disposed "
        "raw-mirror candidate"
    ),
    "validate_minimum_core_candidate.py": (
        "historical Database v1 construction-only validator; requires the disposed "
        "minimum-core candidate"
    ),
}

SOURCE_ARGUMENT_NAMES = frozenset({"database", "database_path", "source_database"})
REFERENCE_ARGUMENT_NAMES = frozenset({"reference_path"})


class ValidatorGateError(RuntimeError):
    """Raised when the validator inventory or argument contract is not governed."""


@dataclass(frozen=True)
class ValidatorPlan:
    script: Path
    command: tuple[str, ...]
    required_positionals: tuple[str, ...]


def _literal_keyword(call: ast.Call, name: str) -> object | None:
    for keyword in call.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return None


def required_positionals(script: Path) -> tuple[str, ...]:
    """Return required argparse positional names without importing the validator."""

    tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    required: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        argument = node.args[0].value
        if not isinstance(argument, str) or argument.startswith("-"):
            continue

        nargs = _literal_keyword(node, "nargs")
        if nargs in {"?", "*", 0}:
            continue
        required.append(argument)

    return tuple(required)


def _argument_value(script_name: str, argument: str) -> Path:
    if argument in SOURCE_ARGUMENT_NAMES:
        return SOURCE_VERSION_1
    if argument in REFERENCE_ARGUMENT_NAMES:
        return COURSE_LOCATION_REFERENCE
    raise ValidatorGateError(
        "Unknown required positional validator argument: "
        f"{script_name} requires {argument!r}. Update the governed runner before "
        "executing the acceptance gate."
    )


def discover_validator_scripts() -> tuple[Path, ...]:
    scripts = tuple(sorted(SCRIPTS_DIR.glob("validate_*.py")))
    if len(scripts) != EXPECTED_VALIDATOR_COUNT:
        raise ValidatorGateError(
            "Validator inventory changed: "
            f"expected {EXPECTED_VALIDATOR_COUNT}, observed {len(scripts)}. "
            "Review applicability before changing the acceptance baseline."
        )
    return scripts


def build_validator_plan() -> tuple[ValidatorPlan, ...]:
    plans: list[ValidatorPlan] = []
    scripts = discover_validator_scripts()

    for script in scripts:
        if script.name in EXCLUDED_VALIDATORS:
            continue
        positionals = required_positionals(script)
        resolved = tuple(str(_argument_value(script.name, name)) for name in positionals)
        plans.append(
            ValidatorPlan(
                script=script,
                command=(sys.executable, str(script), *resolved),
                required_positionals=positionals,
            )
        )

    if len(plans) != EXPECTED_APPLICABLE_COUNT:
        raise ValidatorGateError(
            "Applicable validator count changed: "
            f"expected {EXPECTED_APPLICABLE_COUNT}, observed {len(plans)}"
        )
    return tuple(plans)


def _validate_inputs(plans: tuple[ValidatorPlan, ...]) -> None:
    required_paths: set[Path] = set()
    for plan in plans:
        for name in plan.required_positionals:
            required_paths.add(_argument_value(plan.script.name, name))

    for path in sorted(required_paths):
        if not path.is_file():
            raise ValidatorGateError(f"Required validator input not found: {path}")


def _environment() -> dict[str, str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not existing else src + os.pathsep + existing
    return env


def _tail(text: str, lines: int = 80) -> str:
    return "\n".join(text.splitlines()[-lines:])


def _print_plan(plans: tuple[ValidatorPlan, ...]) -> None:
    for script in discover_validator_scripts():
        if script.name in EXCLUDED_VALIDATORS:
            print(f"SKIP  {script.name}  [{EXCLUDED_VALIDATORS[script.name]}]")
            continue
        plan = next(item for item in plans if item.script == script)
        command = " ".join(shlex.quote(part) for part in plan.command)
        print(f"RUN   {script.name}: {command}")


def run_gate(*, list_only: bool = False) -> int:
    plans = build_validator_plan()
    _validate_inputs(plans)

    if list_only:
        _print_plan(plans)
        print()
        print(f"Applicable validators: {len(plans)}")
        return 0

    env = _environment()
    passed = 0
    for plan in plans:
        result = subprocess.run(
            plan.command,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            passed += 1
            print(f"PASS  {plan.script.name}", flush=True)
            continue

        print(f"FAIL  {plan.script.name}", flush=True)
        combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
        if combined.strip():
            print(_tail(combined))
        print()
        print(f"Applicable validator sweep FAILED after {passed} passes.")
        return 1

    print()
    print(f"Applicable validator sweep PASSED: {passed} validators")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the governed validator commands and exclusions without running them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run_gate(list_only=args.list)
    except ValidatorGateError as exc:
        print(f"VALIDATOR GATE CONFIGURATION ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
