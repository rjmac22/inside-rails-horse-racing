"""Extract candidate manual/external verification passages from committed notebooks.

This is a discovery aid for retrospective backfill. It does not create governed
verification rows automatically because evidence provenance and database action
must be reviewed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

NOTEBOOK_DIR = Path("notebooks")
OUTPUT_PATH = Path("docs/MANUAL_VERIFICATION_CANDIDATES.md")

TERMS = (
    "http://",
    "https://",
    "manual",
    "manually",
    "external",
    "published result",
    "checked against",
    "verified",
    "validation_status",
    "nominatim",
    "wikipedia",
    "racing post",
    "racecard",
    "official result",
)


def plain_text(cell: dict) -> str:
    text = "".join(cell.get("source", []))
    for output in cell.get("outputs", []):
        data = output.get("data", {})
        value = data.get("text/plain", [])
        if isinstance(value, list):
            text += "\n" + "".join(value)
        elif isinstance(value, str):
            text += "\n" + value
        stream = output.get("text", [])
        if isinstance(stream, list):
            text += "\n" + "".join(stream)
        elif isinstance(stream, str):
            text += "\n" + stream
    return text


def compact(text: str, limit: int = 1800) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "\n…"


def main() -> None:
    sections: list[str] = [
        "# Retrospective Manual-Verification Candidates",
        "",
        "Generated from committed notebook source and plain-text outputs.",
        "Every candidate requires review before becoming a governed row in `data/reference/manual_verifications.csv`.",
        "",
    ]
    candidate_count = 0

    for path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        matches: list[tuple[int, str, tuple[str, ...]]] = []
        for index, cell in enumerate(notebook.get("cells", [])):
            text = plain_text(cell)
            lower = text.lower()
            hits = tuple(term for term in TERMS if term in lower)
            if hits:
                matches.append((index, compact(text), hits))

        if not matches:
            continue

        sections.extend((f"## `{path}`", ""))
        for index, text, hits in matches:
            candidate_count += 1
            sections.extend(
                (
                    f"### Cell {index}",
                    "",
                    f"Matched: {', '.join(f'`{hit}`' for hit in hits)}",
                    "",
                    "```text",
                    text,
                    "```",
                    "",
                )
            )

    sections.insert(4, f"Candidate cells found: **{candidate_count}**.")
    OUTPUT_PATH.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {candidate_count} candidate cells.")


if __name__ == "__main__":
    main()
