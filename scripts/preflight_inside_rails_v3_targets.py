#!/usr/bin/env python3
"""Resolve every Database v3 correction/enrichment target against accepted v2."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inside_rails.database.external_reconciliation import (  # noqa: E402
    EXPECTED_RESOLUTIONS,
    RESOLUTION_PATH,
    _blank_to_none,
    _integer,
    _read_csv,
    _resolve_race,
    _resolve_source_record,
)
from inside_rails.database.external_reconciliation_candidate import (  # noqa: E402
    EXPECTED_BASE_RELEASE_SHA256,
    default_base_release_path,
)
from inside_rails.database.raw_mirror_prototype import sha256_file  # noqa: E402
from inside_rails.database.schema import configure_governed_connection  # noqa: E402
from inside_rails.source_sqlite import connect_read_only  # noqa: E402


def main() -> None:
    base = default_base_release_path(ROOT)
    if not base.exists():
        raise FileNotFoundError(f"Accepted Database v2 release not found: {base}")

    observed_hash = sha256_file(base)
    if observed_hash != EXPECTED_BASE_RELEASE_SHA256:
        raise RuntimeError(
            "Accepted Database v2 SHA-256 mismatch: "
            f"expected={EXPECTED_BASE_RELEASE_SHA256.hex()} observed={observed_hash.hex()}"
        )

    rows = _read_csv(ROOT / RESOLUTION_PATH)
    if len(rows) != EXPECTED_RESOLUTIONS:
        raise RuntimeError(
            f"Expected {EXPECTED_RESOLUTIONS} typed resolutions; observed {len(rows)}"
        )

    race_targets = 0
    runner_targets = 0
    with connect_read_only(base) as connection:
        configure_governed_connection(connection, query_only=True)
        for row in rows:
            race_id = _resolve_race(
                connection,
                source_date=row["source_date"],
                source_course=row["source_course"],
                source_off=row["source_off"],
            )
            race_targets += 1

            if row["scope"] == "runner":
                source_record_id = _resolve_source_record(
                    connection,
                    race_id=race_id,
                    source_rowid=_integer(row["source_rowid"]),
                    source_horse=_blank_to_none(row["source_horse"]),
                    source_position=_integer(row["source_position"]),
                )
                if source_record_id is None:
                    raise RuntimeError(
                        f"Runner resolution {row['resolution_id']} did not resolve a source record"
                    )
                runner_targets += 1
            elif row["scope"] != "race":
                raise RuntimeError(
                    f"Unsupported resolution scope {row['scope']!r} for {row['resolution_id']}"
                )

    print(f"Accepted v2 SHA-256: {observed_hash.hex()}")
    print(f"Typed resolutions checked: {len(rows)}")
    print(f"Race targets resolved: {race_targets}")
    print(f"Runner targets resolved: {runner_targets}")
    print("Database v3 target preflight: PASSED")


if __name__ == "__main__":
    main()
