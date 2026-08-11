#!/usr/bin/env python3
"""One-use repair: replace 58 wrapper notebooks with self-contained evidence notebooks."""
from __future__ import annotations
import base64, gzip, json, math, pprint
from pathlib import Path

PATCH_B64 = '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'
ACCESS_DATE = "2026-08-11"
FORBIDDEN = ("_racecourse_notebook_support", "_racecourse_research_payload", "base64", "gzip", "exec(")

def decode_b64_gzip(text):
    return json.loads(gzip.decompress(base64.b64decode(text)).decode())

def get_table(record, name):
    return record["tables"][name]

def records_for(record, name):
    p=get_table(record,name)
    return [dict(zip(p["columns"], row)) for row in p["rows"]]

def add_column(packed, name, value, after=None, before=None):
    if name in packed["columns"]:
        return
    cols=list(packed["columns"])
    if after in cols:
        idx=cols.index(after)+1
    elif before in cols:
        idx=cols.index(before)
    else:
        idx=len(cols)
    cols.insert(idx,name)
    rows=[]
    for row in packed["rows"]:
        row=list(row)
        row.insert(idx,value)
        rows.append(row)
    packed["columns"]=cols
    packed["rows"]=rows

def normalize_records(records):
    patch=decode_b64_gzip(PATCH_B64)
    for key, changes in patch.items():
        rec=records[key]
        for field in ("model_confidence","summary","key_temporal_boundary"):
            if field in changes:
                rec[field]=changes[field]
        for table_name, packed in changes.get("tables",{}).items():
            rec["tables"][table_name]=packed

    for key, rec in records.items():
        lp=rec["tables"]["location_provenance"]
        note_idx=lp["columns"].index("evidence_note")
        for row in lp["rows"]:
            note=row[note_idx]
            if key != "newmarket" and isinstance(note,str) and note.startswith("Stable venue identity. For Newmarket"):
                row[note_idx]="Stable venue identity."
        if "characteristic" in lp["columns"]:
            lp["columns"][lp["columns"].index("characteristic")]="field"
        add_column(lp,"accessed_date",ACCESS_DATE,after="source_url")

        physical=rec["tables"]["course_physical_characteristics"]
        add_column(physical,"accessed_date",ACCESS_DATE,after="exact_source_url")

        history=rec["tables"]["historical_changes"]
        add_column(history,"accessed_date",ACCESS_DATE,after="source_url")

        prov=rec["tables"]["course_characteristic_provenance"]
        add_column(prov,"jurisdiction","Great Britain",after="assertion_id")
        add_column(prov,"accessed_date",ACCESS_DATE,after="source_url")

        candidates=rec["tables"]["course_candidates_not_promoted"]
        add_column(candidates,"accessed_date",ACCESS_DATE,after="source_url")
    return records

def dataframe_code(variable, record, table_name):
    p=get_table(record,table_name)
    rows=[[None if (isinstance(v,float) and math.isnan(v)) else v for v in row] for row in p["rows"]]
    return (
        f"{variable} = pd.DataFrame(\n"
        f"    {pprint.pformat(rows, width=140, sort_dicts=False)},\n"
        f"    columns={pprint.pformat(p['columns'], width=140, sort_dicts=False)},\n"
        f")\n{variable}"
    )

def md(source, cid):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":source}

def code(source, cid):
    return {"cell_type":"code","execution_count":None,"id":cid,"metadata":{},"outputs":[],"source":source}

def notebook(key, rec):
    canon=rec["canonical"]
    labels=", ".join(f"`{x}`" for x in rec["source_labels"])
    inv=records_for(rec,"course_inventory")
    names="; ".join(str(x["course_or_track_name"]) for x in inv)
    surface="\n".join(f"- **{x['course_or_track_name']}** — {x.get('surface') if x.get('surface') is not None else 'Unresolved'}" for x in inv)
    handed="\n".join(f"- **{x['course_or_track_name']}** — {x.get('handedness') if x.get('handedness') is not None else 'Unresolved'}" for x in inv)
    use="\n".join(f"- **{x['course_or_track_name']}** — {x.get('primary_use') if x.get('primary_use') is not None else 'Unresolved'}" for x in inv)
    p=key.replace("_","-")[:28]
    cells=[
      md(f"# {canon}\n\nRacecourse evidence notebook supporting Study 03: **British racecourse and course identity**.\n\nThis notebook is self-contained: the governed venue/course records and their provenance are written directly into the notebook.",p+"-title"),
      md(f"## Scope\n\n- Racecourse: **{canon}**\n- Jurisdiction: **Great Britain**\n- Study period: **2015-01-01 to 2026-05-27**\n- Study 03 source label(s): {labels}\n- Research-dossier venue label: `{rec['display']}`\n- Physical-model confidence: **{rec['model_confidence']}**\n- Key temporal boundary: {rec['key_temporal_boundary'] or 'None established in this research pass.'}",p+"-scope"),
      md(f"## Racecourse identity\n\n**Governed racecourse identity:** `{canon}`\n\n{rec['summary']}\n\nEvidence, Inside Rails derivation, candidates and unresolved questions are kept separate.",p+"-identity"),
      md("## Source-data labels\n\nThe following source label(s) map to this governed racecourse identity. A source label is not automatically a complete course/track inventory.",p+"-labels"),
      code("import pandas as pd",p+"-imports"),
      code(dataframe_code("source_label_mapping",rec,"source_label_mapping"),p+"-label-data"),
      md("## Location metadata\n\nLocation is a **venue-level** property. Coordinates and elevation are retained only at the precision supported by the cited sources; they are not represented as surveyed course-centre coordinates or a course elevation profile.",p+"-location"),
      code(dataframe_code("location_metadata",rec,"location_metadata"),p+"-location-data"),
      md("### Location provenance",p+"-location-prov"),
      code(dataframe_code("location_provenance",rec,"location_provenance"),p+"-location-prov-data"),
      md(f"## Recognised courses and tracks\n\nGoverned study-period inventory: **{names}**.\n\nNamed starts, temporary rail positions, race-type headings and uncertain candidates are not silently promoted to permanent course identities.",p+"-courses"),
      code(dataframe_code("course_inventory",rec,"course_inventory"),p+"-course-data"),
      md(f"## Surface\n\n{surface}",p+"-surface"),
      md(f"## Handedness\n\n{handed}",p+"-handed"),
      md(f"## Racing use\n\n{use}",p+"-use"),
      md("## Course layout and physical characteristics\n\nCourse-specific geometry, relationships, lengths, gradients and distinctive features are included only where the research supports them.",p+"-physical"),
      code(dataframe_code("course_physical_characteristics",rec,"course_physical_characteristics"),p+"-physical-data"),
      md("## Historical changes\n\nHistorical layouts, surfaces and racing-use changes are date-bounded where the evidence allows. Older physical models are not projected across redevelopment or resurfacing boundaries.",p+"-history"),
      code(dataframe_code("historical_changes",rec,"historical_changes"),p+"-history-data"),
      md(f"## Source mapping\n\n{labels} → **{canon}** → governed constituent course/track inventory above.\n\nThis preserves the Study 03 rule: `source label != racecourse != course/track`.",p+"-mapping"),
      md("## Evidence and provenance\n\nEach material assertion retains its source authority, source title, exact URL, temporal validity, evidence note and verification status. A course-identity citation is not automatically treated as proof of every characteristic.",p+"-provenance"),
      code(dataframe_code("course_characteristic_provenance",rec,"course_characteristic_provenance"),p+"-prov-data"),
      md("## Candidates not promoted\n\nNamed routes/components that do not meet the current governance threshold remain below the governed inventory.",p+"-candidates"),
      code(dataframe_code("course_candidates_not_promoted",rec,"course_candidates_not_promoted"),p+"-candidate-data"),
      md("## Human-review items\n\nContradictory or potentially misleading source material is retained for explicit review rather than silently normalised.",p+"-review"),
      code(dataframe_code("human_review_items",rec,"human_review_items"),p+"-review-data"),
      md("## Unresolved questions\n\nUnknowns remain unresolved rather than being filled from general racing knowledge.",p+"-unresolved"),
      code(dataframe_code("unresolved_questions",rec,"unresolved_questions"),p+"-unresolved-data"),
      md(f"## Conclusion\n\n{rec['summary']}\n\nThe notebook records the strongest supported physical model without converting race-type terminology or uncertain candidates into unsupported course identities.",p+"-conclusion"),
      code("assert len(source_label_mapping) >= 1\nassert len(location_metadata) == 1\n"+f"assert location_metadata.iloc[0]['racecourse_identity'] == {canon!r}\n"+"assert location_metadata.iloc[0]['iana_timezone'] == 'Europe/London'\nassert len(course_inventory) >= 1\nif len(course_characteristic_provenance):\n    assert course_characteristic_provenance['source_url'].fillna('').str.len().gt(0).all()\n"+f"print({canon!r} + ' venue, course model and provenance checks passed.')",p+"-checks"),
      md("## Findings from later studies\n\n_None yet._",p+"-later"),
    ]
    return {"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3 (ipykernel)","language":"python","name":"python3"}},"nbformat":4,"nbformat_minor":5}

def main():
    root=Path(__file__).resolve().parents[1]
    racecourses=root/"studies"/"jurisdictions"/"great_britain"/"racecourses"
    old_payload=racecourses/"_racecourse_research_payload.b64"
    records=decode_b64_gzip(old_payload.read_text())
    records=normalize_records(records)
    count=0
    for key,rec in sorted(records.items()):
        path=racecourses/f"{key}.ipynb"
        text=json.dumps(notebook(key,rec),ensure_ascii=False,indent=1)+"\n"
        for token in FORBIDDEN:
            assert token not in text,(path,token)
        json.loads(text)
        path.write_text(text)
        count+=1
    assert count==58,count
    print(f"Materialized {count} self-contained racecourse notebooks.")

if __name__=="__main__":
    main()
