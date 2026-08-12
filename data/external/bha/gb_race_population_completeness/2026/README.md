# BHA 2026 race-population audit evidence

This directory preserves bounded, unmodified British Horseracing Authority source artifacts used by `notebooks/26_gb_race_population_completeness.ipynb`.

## Evidence role

Keep three concepts separate:

1. **original published 2026 fixture plan** — planning evidence;
2. **subsequent BHA fixture/result observations** — evidence of how the year actually evolved;
3. **official completed race results** — the decisive external population for the Source Version 1 completeness audit through 2026-05-27.

A scheduled fixture that later did not produce official results is not, by itself, evidence of a Source Version 1 defect.

## Static source artifacts retained here

The downloader preserves the following official BHA files unchanged:

- `2026_Fixture_List.pdf`
- `2026_Fixture_List.xlsx`
- `2026_Headline_Measures.pdf`
- `January26.pdf`
- `February26.pdf`
- `March26.pdf`
- `April26.pdf`
- `May26.pdf`

The fixture-list files were linked by the BHA press release publishing the 2026 Fixture List. The monthly PDFs are linked by the BHA Racing Statistics page as the 2026 Racing Data Packs.

## Reproducible acquisition

From the repository root:

```bash
python scripts/download_bha_2026_audit_evidence.py
```

The script:

- downloads only the explicitly listed HTTPS resources;
- validates PDF/XLSX file signatures;
- writes each original file without transformation;
- records byte size, SHA-256, source URL, source page and retrieval timestamp in `manifest.json`;
- leaves race-result acquisition out of scope until the BHA results interface has been separately verified.

Use `--force` only when deliberately taking a fresh observation of the same source URLs:

```bash
python scripts/download_bha_2026_audit_evidence.py --force
```

A forced redownload may legitimately produce a different checksum if the BHA has replaced a file at the same URL. Treat such a difference as a new source observation; do not silently overwrite historical evidence without recording the change.

## Provenance and ownership

These files are third-party BHA source material retained for research reproducibility. Their presence here does not make them Inside Rails-authored material. Preserve original filenames, source URLs and checksums.
