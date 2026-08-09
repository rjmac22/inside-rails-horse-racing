from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_applicable_validators.py"
EXPECTED_SOURCE_POSITIONAL_VALIDATORS = {
    "validate_beaten_distances.py",
    "validate_course_jurisdiction.py",
    "validate_field_governance.py",
    "validate_jurisdiction_context.py",
    "validate_off_time.py",
    "validate_race_identity.py",
    "validate_race_results.py",
    "validate_race_surface.py",
    "validate_source_fields.py",
    "validate_source_profile.py",
    "validate_starting_price.py",
}


def _load_runner():
    module_name = "run_applicable_validators"
    spec = importlib.util.spec_from_file_location(module_name, RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_validator_inventory_and_exclusions_are_exact() -> None:
    runner = _load_runner()
    scripts = runner.discover_validator_scripts()
    plans = runner.build_validator_plan()

    assert len(scripts) == runner.EXPECTED_VALIDATOR_COUNT == 34
    assert len(plans) == runner.EXPECTED_APPLICABLE_COUNT == 31
    assert set(runner.EXCLUDED_VALIDATORS) == {
        "validate_core_structure_prototype.py",
        "validate_raw_mirror_candidate.py",
        "validate_minimum_core_candidate.py",
    }
    assert {plan.script.name for plan in plans}.isdisjoint(runner.EXCLUDED_VALIDATORS)


def test_exact_required_source_positional_map_is_preserved() -> None:
    runner = _load_runner()
    plans = runner.build_validator_plan()
    required_source = {
        plan.script.name
        for plan in plans
        if plan.required_positionals
    }

    assert required_source == EXPECTED_SOURCE_POSITIONAL_VALIDATORS
    for plan in plans:
        if plan.script.name in EXPECTED_SOURCE_POSITIONAL_VALIDATORS:
            assert plan.required_positionals == ("database",)
        else:
            assert plan.required_positionals == ()


def test_every_required_positional_is_governed_before_execution() -> None:
    runner = _load_runner()
    plans = runner.build_validator_plan()

    for plan in plans:
        assert len(plan.command) == 2 + len(plan.required_positionals)
        for argument, value in zip(
            plan.required_positionals,
            plan.command[2:],
            strict=True,
        ):
            if argument in runner.SOURCE_ARGUMENT_NAMES:
                assert Path(value) == runner.SOURCE_VERSION_1
            elif argument in runner.REFERENCE_ARGUMENT_NAMES:
                assert Path(value) == runner.COURSE_LOCATION_REFERENCE
            else:  # pragma: no cover - build_validator_plan must fail first.
                raise AssertionError(f"ungoverned required positional: {argument}")


def test_beaten_distance_validator_receives_source_version_1() -> None:
    runner = _load_runner()
    plans = {plan.script.name: plan for plan in runner.build_validator_plan()}
    plan = plans["validate_beaten_distances.py"]

    assert plan.required_positionals == ("database",)
    assert Path(plan.command[-1]) == runner.SOURCE_VERSION_1


def test_v3_validator_remains_in_applicable_gate() -> None:
    runner = _load_runner()
    plans = {plan.script.name for plan in runner.build_validator_plan()}

    assert "validate_inside_rails_v3.py" in plans
