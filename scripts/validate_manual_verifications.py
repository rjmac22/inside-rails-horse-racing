#!/usr/bin/env python3
"""Validate the governed manual-verification register."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from inside_rails.manual_verifications import load_manual_verifications

REGISTER = Path("data/reference/manual_verifications.csv")


def main() -> None:
    rows = load_manual_verifications(REGISTER)
    status_totals = Counter(row.verification_status for row in rows)
    action_totals = Counter(row.database_action for row in rows)

    print(f"Manual-verification register passed: {len(rows)} governed rows.")
    if rows:
        print("Verification statuses:")
        for status, count in sorted(status_totals.items()):
            print(f"  {status}: {count}")
        print("Database actions:")
        for action, count in sorted(action_totals.items()):
            print(f"  {action}: {count}")
    else:
        print("Register schema is active; retrospective evidence backfill is pending.")


if __name__ == "__main__":
    main()
