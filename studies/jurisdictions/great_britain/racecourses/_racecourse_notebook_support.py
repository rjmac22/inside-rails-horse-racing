"""Shared renderer for Study 03 Great Britain racecourse evidence notebooks."""
from pathlib import Path
import base64
import gzip
import json

import pandas as pd
from IPython.display import Markdown, display

_CACHE = None


def _project_root():
    root = Path.cwd()
    while not (root / "studies").exists() and root != root.parent:
        root = root.parent
    return root


def _load_all():
    global _CACHE
    if _CACHE is None:
        path = (
            _project_root()
            / "studies"
            / "jurisdictions"
            / "great_britain"
            / "racecourses"
            / "_racecourse_research_payload.b64"
        )
        assert path.exists(), f"Research payload not found: {path}"
        _CACHE = json.loads(
            gzip.decompress(base64.b64decode(path.read_text())).decode()
        )
    return _CACHE


def _frame(record, name):
    packed = record["tables"][name]
    return pd.DataFrame(packed["rows"], columns=packed["columns"])


def _show_table(df):
    if len(df):
        display(df)
    else:
        display(Markdown("_None._"))


def render_venue(key):
    record = _load_all()[key]
    canon = record["canonical"]
    labels = ", ".join(f"`{x}`" for x in record["source_labels"])
    tables = {name: _frame(record, name) for name in record["tables"]}

    source_label_mapping = tables["source_label_mapping"]
    location_metadata = tables["location_metadata"]
    location_provenance = tables["location_provenance"]
    course_inventory = tables["course_inventory"]
    course_physical_characteristics = tables["course_physical_characteristics"]
    historical_changes = tables["historical_changes"]
    course_characteristic_provenance = tables["course_characteristic_provenance"]
    course_candidates_not_promoted = tables["course_candidates_not_promoted"]
    human_review_items = tables["human_review_items"]
    unresolved_questions = tables["unresolved_questions"]

    display(
        Markdown(
            f"## Scope\n\n"
            f"- Racecourse: **{canon}**\n"
            f"- Jurisdiction: **Great Britain**\n"
            f"- Study period: **2015-01-01 to 2026-05-27**\n"
            f"- Study 03 source label(s): {labels}\n"
            f"- Research-dossier venue label: `{record['display']}`\n"
            f"- Physical-model confidence: **{record['model_confidence']}**\n"
            f"- Key temporal boundary: "
            f"{record['key_temporal_boundary'] or 'none established in the dossier'}"
        )
    )

    display(
        Markdown(
            f"## Racecourse identity\n\n"
            f"**Governed racecourse identity:** `{canon}`\n\n"
            f"{record['summary']}\n\n"
            "Evidence, Inside Rails derivation, candidates and unresolved questions "
            "are kept separate."
        )
    )

    display(Markdown("## Source-data labels"))
    _show_table(source_label_mapping)

    display(
        Markdown(
            "## Location metadata\n\n"
            "Location is venue-level. Coordinates and elevation are retained only at "
            "the precision supported by the cited sources and are not represented as "
            "surveyed course geometry or an elevation profile."
        )
    )
    _show_table(location_metadata)
    _show_table(location_provenance)

    display(
        Markdown(
            "## Recognised courses and tracks\n\n"
            "The governed inventory contains only physical courses/tracks/configurations "
            "supported at the level claimed by the research dossier. Descriptive names "
            "remain descriptive where a canonical source name is not established."
        )
    )
    _show_table(course_inventory)

    surface = "; ".join(
        f"**{row.course_or_track_name}** — "
        f"{row.surface if pd.notna(row.surface) else 'unresolved'}"
        for row in course_inventory.itertuples()
    )
    handed = "; ".join(
        f"**{row.course_or_track_name}** — "
        f"{row.handedness if pd.notna(row.handedness) else 'unresolved'}"
        for row in course_inventory.itertuples()
    )
    use = "; ".join(
        f"**{row.course_or_track_name}** — "
        f"{row.primary_use if pd.notna(row.primary_use) else 'unresolved'}"
        for row in course_inventory.itertuples()
    )
    display(
        Markdown(
            f"## Surface\n\n{surface}\n\n"
            f"## Handedness\n\n{handed}\n\n"
            f"## Racing use\n\n{use}"
        )
    )

    display(Markdown("## Course layout and physical characteristics"))
    _show_table(course_physical_characteristics)

    display(
        Markdown(
            "## Historical changes\n\n"
            "Historical layouts and changes are date-bounded where the evidence allows. "
            "Older structures are not projected across redevelopment or resurfacing boundaries."
        )
    )
    _show_table(historical_changes)

    display(
        Markdown(
            f"## Source mapping\n\n"
            f"{labels} → **{canon}** → governed constituent inventory above.\n\n"
            "This preserves the Study 03 rule: `source label != racecourse != course/track`."
        )
    )

    display(
        Markdown(
            "## Evidence and provenance\n\n"
            "Every material assertion retains source authority, source title, exact URL, "
            "validity period, evidence note and verification status. Derived conclusions "
            "remain labelled as Inside Rails derivations."
        )
    )
    _show_table(course_characteristic_provenance)

    display(Markdown("## Candidates not promoted"))
    _show_table(course_candidates_not_promoted)

    display(Markdown("## Human-review items"))
    _show_table(human_review_items)

    display(
        Markdown(
            "## Unresolved questions\n\n"
            "Unknowns remain unresolved rather than being filled from general racing knowledge."
        )
    )
    _show_table(unresolved_questions)

    display(
        Markdown(
            f"## Conclusion\n\n{record['summary']}\n\n"
            "The notebook records the strongest supported physical model without converting "
            "race-type terminology or uncertain candidates into unsupported course identities."
        )
    )

    assert len(source_label_mapping) >= 1
    assert len(location_metadata) == 1
    assert location_metadata.iloc[0]["racecourse_identity"] == canon
    assert location_metadata.iloc[0]["iana_timezone"] == "Europe/London"
    assert len(course_inventory) >= 1
    if len(course_characteristic_provenance):
        assert (
            course_characteristic_provenance["source_url"]
            .fillna("")
            .str.len()
            .gt(0)
            .all()
        )

    print(f"{canon} venue, course model and provenance checks passed.")
    display(Markdown("## Findings from later studies\n\n_None yet._"))

    return tables
