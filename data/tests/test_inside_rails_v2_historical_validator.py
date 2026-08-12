from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_inside_rails_v2.py"


def _load_script():
    module_name = "validate_inside_rails_v2_historical_test"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_v2_validator_replays_exact_historical_reference_snapshot() -> None:
    module = _load_script()

    assert module.V2_REFERENCE_COMMIT == "68ac0364c4af2a104ea76c8765fd0e220aaf8e84"
    assert set(module.V2_REFERENCE_PATHS) == {
        "data/reference/manual_verifications.csv",
        "data/reference/connection_identity_repairs.csv",
        "data/reference/runner_record_supplementations.csv",
        "data/reference/horse_pedigree_identity_governance.csv",
    }

    with module.historical_v2_reference_root() as snapshot_root:
        for relative in module.V2_REFERENCE_PATHS:
            assert (snapshot_root / relative).is_file()

        with (snapshot_root / "data/reference/manual_verifications.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            manual_rows = list(csv.DictReader(handle))

    assert len(manual_rows) == 85
