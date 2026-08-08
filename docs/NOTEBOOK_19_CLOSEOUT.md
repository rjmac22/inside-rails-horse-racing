# Notebook 19 Closeout — Horse and Pedigree Identity

## Status

**Analytically closed; final authority response incorporated on 8 August 2026; focused local regeneration and validation required before the updated governed outputs are accepted.**

Notebook 19 remains a **non-rerunnable archival construction record**. Durable implementation, governed reference data, focused tests, the independent source-wide validator and database-integration documentation live outside the notebook.

The 5 August 2026 authority gate reduced the unresolved population from five cases to one. On 8 August 2026 Weatherbys Ireland supplied the final outstanding pedigree confirmation. That response changes the last governed `Unresolved` transition to `Corrected` and requires regeneration of the two source-derived Notebook 19 outputs.

## Bounded question

What do the runner-level `horse`, `sire`, `dam` and `damsire` fields represent, how stable and complete are their labels, and which identity or pedigree relationships can be preserved safely without inventing entity equivalence from names alone?

## Executive conclusion

The raw `horse` field is a source-presented label, not a permanent horse identifier.

The same displayed horse name and breeding-country suffix can be reused by different real horses. One real horse can also appear with incorrect, incomplete or inconsistent pedigree assertions. Horse identity and pedigree therefore require a governed analytical layer rather than direct use of the raw strings.

The 353 material transitions between temporally separated structured pedigree histories now have the expected final authority-reviewed partition:

- 92 `Corrected` transitions;
- 261 `Different horse` transitions;
- 0 `Unresolved` transitions.

Because the final authority decision is a correction rather than an identity split, the expected provisional source-internal horse-occurrence population remains **611** from 350 exact source labels and 703 separated pedigree groups.

These updated counts must be confirmed by the focused tests and independent source-wide validator before the regenerated outputs are accepted.

## Core evidence

The source population contains 1,851,285 governed runner rows and 189,043 provisional races under `rowid <> 1`.

The validated identity funnel before the final 8 August output regeneration is structurally unchanged:

- 5,573 raw contradiction labels;
- 368 structured contradiction labels after reversible dam-suffix treatment;
- 96,404 structured pedigree rows;
- 741 structured pedigree groups;
- 350 temporally separated exact labels;
- 703 separated pedigree groups;
- 353 governed transitions;
- expected 611 provisional occurrences.

Complete pedigree changes combined with long chronological gaps and incompatible age progression provide strong evidence of exact-label reuse. Short-gap exceptions and partial changes were reviewed separately rather than forced through a universal rule.

## Analytical outcomes

### Corrected

A corrected boundary remains one horse history. The governed analytical layer may use the established pedigree while preserving every raw source value and its lineage.

Correction does not authorise a global string-cleaning rule. Terminal numerals, prefixes, country suffixes and spelling differences are governed only within the bounded claim for which evidence exists.

### Different horse

A different-horse boundary means that one exact source label represents separate real horses. The histories must receive separate provisional occurrence identifiers before horse-level analysis.

The provisional identifier prevents accidental merging inside this source. It is not an official registration number or globally unique identity.

### Unresolved

The durable implementation retains an `Unresolved` state for future evidence gaps. Following the final Weatherbys Ireland response on 8 August 2026, the current Notebook 19 governed transition population is expected to contain **zero unresolved transitions**.

## Final authority resolution — Runninsonofagun (IRE)

The previously unresolved case was:

`Runninsonofagun (IRE)`

The source transition is between otherwise matching pedigree histories:

- sire: `Inns Of Court (IRE)`;
- dam: `High Society Lady (IRE)`;
- earlier raw damsire assertion: `General Monash`;
- later raw damsire assertion: `Society Rock`.

The specialist governance row had also retained stale sire/dam metadata from an earlier review state (`Jet Away (GB)` / `Sounds Of Thunder (IRE)`). The governed transition output showed the correct source history and the specialist reference has now been corrected to match it.

On 8 August 2026 the user supplied an email response from **Georgina Doherty, Senior Pedigree Researcher, Weatherbys Ireland**, confirming:

> High Society Lady (IRE) is by Society Rock (IRE).

Database consequence:

- `NB19-ID-0013` changes from `Unresolved` to `Corrected`;
- governed damsire becomes `Society Rock (IRE)`;
- raw competing assertions `General Monash` and `Society Rock` remain preserved;
- no horse-identity split is created;
- the occurrence sequence therefore does not change;
- the transition decision basis becomes the normal bounded correction path rather than `pending_official_confirmation`.

## Other authority-reviewed bounded corrections

The earlier authority review established bounded corrections including:

- `Almavillalobas (GB)` — governed dam `Nation (USA)`;
- `Colwyn Bay (FR)` — governed pedigree `Falco (USA)` / `Eudora (IRE)` / `King's Best (USA)`;
- `Diamond Tipp (IRE)` — governed pedigree `Diamond Boy (FR)` / `Soundout (IRE)` / `Oscar (IRE)`;
- `LAziza Des Places (FR)` — governed sire `Alanadi (FR)`.

Other accepted bounded corrections and splits remain preserved in `data/reference/horse_pedigree_identity_governance.csv`.

## Confidence

Confidence is high in the central conclusion that raw horse labels cannot serve as permanent natural keys.

Confidence is high in the 261 different-horse boundaries because the dominant evidence combines materially different pedigrees, separated chronology and generally incompatible age progression.

The final Runninsonofagun damsire correction is high confidence because it is supported by direct Weatherbys Ireland pedigree confirmation.

Confidence in individual corrected pedigrees remains decision-specific and is preserved in the specialist governance reference.

## Limitations

The result is bounded to the supplied source database, the governed `rowid <> 1` population and the period and jurisdictions represented there.

The study does not prove that every stable pedigree is correct. It does not provide official identities for every horse. It does not establish that a name and country suffix are unique outside this dataset.

The occurrence assignment is a source-internal analytical construction. It must not be represented as an official registration or life number.

## What the result justifies

The work justifies:

- preserving all four raw source fields;
- refusing to use raw `horse` as a permanent natural key;
- applying bounded governed pedigree corrections;
- splitting the 261 identified same-label histories;
- using the final Weatherbys-backed Runninsonofagun damsire correction;
- rebuilding horse-level derived data around governed occurrence identity.

It does not justify overwriting the source, globally stripping suffixes or numerals, inferring identity from name similarity, or treating the source as professionally complete.

## Manual-verification decision

**`specialist_reference`**

Notebook 19 depends on manual and external evidence. Three claims are recorded in `data/reference/manual_verifications.csv`. Equivalent evidence, status, confidence, decision identifiers and database consequences for the remaining bounded decisions and authority enquiries are preserved in:

`data/reference/horse_pedigree_identity_governance.csv`

The specialist table is the governing reference for Notebook 19 identity and pedigree decisions. It never overwrites immutable source data.

The final `NB19-ID-0013` evidence locator records the Weatherbys Ireland email confirmation supplied by the user on 8 August 2026, with high confidence and the corrected governed damsire.

## Archival classification

Notebook 19 is a **non-rerunnable archival construction record**.

The saved executed notebook preserves the completed investigation, output tables, anomalies, external-review reasoning and original conclusion. It is not intended to regenerate permanent outputs directly.

A fresh-kernel rerun would depend on interactive research, authority enquiries and external evidence that may change. Production outputs are regenerated only through the governed reference and independent source-wide validator.

Durable replacement validation is provided by:

- `data/reference/horse_pedigree_identity_governance.csv`;
- `src/inside_rails/horse_pedigree_identity.py`;
- `src/inside_rails/horse_pedigree_identity_counts.py`;
- `tests/test_horse_pedigree_identity.py`;
- `tests/test_horse_pedigree_identity_counts.py`;
- `scripts/validate_horse_pedigree_identity.py`;
- `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Historical validation evidence

### Original closeout validation — 3 August 2026

Focused tests:

```bash
pytest tests/test_horse_pedigree_identity.py tests/test_horse_pedigree_identity_counts.py
```

Result: **12 passed in 0.63s**.

Earlier combined focused validation also passed:

```bash
pytest tests/test_horse_pedigree_identity.py tests/test_manual_verifications.py
python scripts/validate_manual_verifications.py
```

Results:

- **20 tests passed in 0.55s**;
- manual-verification register passed with **39 governed rows**.

### Pre-database authority gate — 5 August 2026

The focused identity tests and independent source-wide validator passed with the then-final governed baselines:

- 353 transitions;
- 91 `Corrected`;
- 261 `Different horse`;
- 1 `Unresolved`;
- 611 provisional occurrences.

Those counts are historical evidence of the 5 August authority state and are now superseded by the 8 August Weatherbys Ireland confirmation.

## Required post-authority validation — 8 August 2026

The updated repository now expects:

- 353 governed transitions;
- 92 `Corrected`;
- 261 `Different horse`;
- 0 `Unresolved`;
- 611 provisional occurrences;
- zero unresolved boundaries in the persisted occurrence output.

Before this update is accepted, run locally from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_horse_pedigree_identity.py \
  tests/test_horse_pedigree_identity_counts.py

PYTHONPATH=src .venv/bin/python \
  scripts/validate_horse_pedigree_identity.py
```

The validator must regenerate, write and reload:

- `data/processed/horse_pedigree_identity/transition_governance.csv`;
- `data/processed/horse_pedigree_identity/provisional_horse_occurrences.csv`.

The complete repository test suite and all-validator sweep remain deferred to the Database v2 acceptance boundary rather than this bounded authority update.

## Database consequence

Raw horse and pedigree labels remain immutable. The clean layer adds governed occurrence identity, governed pedigree fields, analytical outcome, decision basis, evidence identifier, confidence, review status and unresolved state.

Any existing derived table that groups histories by raw `horse` alone must be rebuilt. Full requirements and the update procedure are recorded in `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Remaining action

Regenerate and validate the two Notebook 19 processed outputs from the immutable source using the focused commands above. Once they pass and are committed, Notebook 19 will again have no outstanding authority case or implementation residue.
