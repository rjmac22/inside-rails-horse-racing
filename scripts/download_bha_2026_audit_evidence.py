#!/usr/bin/env python3
"""Download bounded official BHA 2026 audit evidence and record provenance.

This script is intentionally limited to static BHA source documents used by the
Great Britain race-population completeness audit. It does not collect race
results and does not infer fixture identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESTINATION = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "bha"
    / "gb_race_population_completeness"
    / "2026"
)
MANIFEST_PATH = DESTINATION / "manifest.json"

FIXTURE_PRESS_RELEASE = (
    "https://www.britishhorseracing.com/press_releases/"
    "bha-publishes-2026-fixture-list/"
)
RACING_STATISTICS_PAGE = (
    "https://www.britishhorseracing.com/regulation/"
    "reports-and-statistics/racing-statistics/"
)

SOURCES = [
    {
        "filename": "2026_Fixture_List.pdf",
        "url": "https://media.britishhorseracing.com/bha/Fixture_List/2026_Fixture_List.pdf",
        "source_page": FIXTURE_PRESS_RELEASE,
        "evidence_role": "original published 2026 fixture plan",
        "format": "pdf",
    },
    {
        "filename": "2026_Fixture_List.xlsx",
        "url": "https://media.britishhorseracing.com/bha/Fixture_List/2026_Fixture_List.xlsx",
        "source_page": FIXTURE_PRESS_RELEASE,
        "evidence_role": "machine-readable original published 2026 fixture plan",
        "format": "xlsx",
    },
    {
        "filename": "2026_Headline_Measures.pdf",
        "url": "https://media.britishhorseracing.com/bha/Fixture_List/2026_Headline_Measures.pdf",
        "source_page": FIXTURE_PRESS_RELEASE,
        "evidence_role": "published context for the original 2026 fixture list",
        "format": "pdf",
    },
    {
        "filename": "January26.pdf",
        "url": "https://media.britishhorseracing.com/bha/Racing_Statistics/Racing_Data_Packs_By_Month_2026/January26.pdf",
        "source_page": RACING_STATISTICS_PAGE,
        "evidence_role": "official BHA January 2026 racing data pack",
        "format": "pdf",
    },
    {
        "filename": "February26.pdf",
        "url": "https://media.britishhorseracing.com/bha/Racing_Statistics/Racing_Data_Packs_By_Month_2026/February26.pdf",
        "source_page": RACING_STATISTICS_PAGE,
        "evidence_role": "official BHA February 2026 racing data pack",
        "format": "pdf",
    },
    {
        "filename": "March26.pdf",
        "url": "https://media.britishhorseracing.com/bha/Racing_Statistics/Racing_Data_Packs_By_Month_2026/March26.pdf",
        "source_page": RACING_STATISTICS_PAGE,
        "evidence_role": "official BHA March 2026 racing data pack",
        "format": "pdf",
    },
    {
        "filename": "April26.pdf",
        "url": "https://media.britishhorseracing.com/bha/Racing_Statistics/Racing_Data_Packs_By_Month_2026/April26.pdf",
        "source_page": RACING_STATISTICS_PAGE,
        "evidence_role": "official BHA April 2026 racing data pack",
        "format": "pdf",
    },
    {
        "filename": "May26.pdf",
        "url": "https://media.britishhorseracing.com/bha/Racing_Statistics/Racing_Data_Packs_By_Month_2026/May26.pdf",
        "source_page": RACING_STATISTICS_PAGE,
        "evidence_role": "official BHA May 2026 racing data pack",
        "format": "pdf",
    },
]

USER_AGENT = (
    "Inside-Rails-Horse-Racing/1.0 "
    "(research evidence preservation; bounded static-document download)"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_payload(source: dict[str, str], data: bytes) -> None:
    if len(data) < 1_000:
        raise ValueError(f"payload unexpectedly small: {len(data):,} bytes")

    if source["format"] == "pdf" and not data.startswith(b"%PDF-"):
        raise ValueError("response is not a PDF payload")

    if source["format"] == "xlsx" and not data.startswith(b"PK"):
        raise ValueError("response is not an XLSX/ZIP payload")


def fetch(source: dict[str, str], force: bool) -> dict[str, object]:
    destination = DESTINATION / source["filename"]

    if destination.exists() and not force:
        data = destination.read_bytes()
        validate_payload(source, data)
        return {
            **source,
            "status": "existing_local_file_verified",
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "retrieved_at_utc": None,
            "response_content_type": None,
        }

    request = Request(
        source["url"],
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*;q=0.8",
        },
    )

    with urlopen(request, timeout=90) as response:  # noqa: S310 - fixed HTTPS URLs only
        data = response.read()
        content_type = response.headers.get("Content-Type")
        final_url = response.geturl()

    validate_payload(source, data)

    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(destination)

    return {
        **source,
        "status": "downloaded",
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "response_content_type": content_type,
        "response_final_url": final_url,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload and replace files that already exist",
    )
    args = parser.parse_args()

    DESTINATION.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    failures = 0

    for source in SOURCES:
        print(f"{source['filename']}: ", end="", flush=True)
        try:
            record = fetch(source, force=args.force)
        except (HTTPError, URLError, OSError, ValueError) as exc:
            failures += 1
            record = {
                **source,
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            print(f"FAILED — {exc}")
        else:
            print(
                f"{record['status']} — {record['bytes']:,} bytes — "
                f"sha256={str(record['sha256'])[:12]}…"
            )
        records.append(record)

    manifest = {
        "audit": "Great Britain race-population completeness",
        "scope": "bounded official BHA static source documents for 2026",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_note": (
            "These are raw external evidence artifacts. The original fixture list is "
            "planning evidence, not the completed-race completeness denominator."
        ),
        "sources": records,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"\nManifest: {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")
    if failures:
        print(f"{failures} download(s) failed; manifest records the failures.")
        return 1

    print(f"All {len(records)} source artifacts are present and validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
