# Notebook 19 Closeout — Horse and Pedigree Identity

## Status

**Validated and analytically closed. Authority gate completed 5 August 2026.**

The analytical investigation is complete. The notebook is classified as a **non-rerunnable archival construction record**. Durable implementation, governed reference data, focused tests, an independent source-wide validator and database-integration documentation exist outside the notebook.

The two validator-generated CSV outputs were regenerated, written, reloaded and committed after the authority review.

## Bounded question

What do the runner-level `horse`, `sire`, `dam` and `damsire` fields represent, how stable and complete are their labels, and which identity or pedigree relationships can be preserved safely without inventing entity equivalence from names alone?

## Executive conclusion

The raw `horse` field is a source-presented label, not a permanent horse identifier.

The same displayed horse name and breeding-country suffix can be reused by different real horses. One real horse can also appear with incorrect, incomplete or inconsistent pedigree assertions. Horse identity and pedigree therefore require a governed analytical layer rather than direct use of the raw strings.

The 353 material transitions between temporally separated structured pedigree histories now produce:

- 91 `Corrected` transitions;
- 261 `Different horse` transitions;
- 1 `Unresolved` transition.

The governed split boundaries produce 611 provisional source-internal horse occurrences from 350 exact source labels and 703 structured pedigree groups.

## Core evidence

The source population contains 1,851,285 governed runner rows and 189,043 provisional races under `rowid <> 1`.

The source pedigree fields are highly populated, but repeated exact horse labels can carry incompatible pedigrees. The validated funnel is:

- 5,573 raw contradiction labels;
- 368 structured contradiction labels after reversible dam-suffix treatment;
- 96,404 structured pedigree rows;
- 741 structured pedigree groups;
- 350 temporally separated exact labels;
- 703 separated pedigree groups;
- 353 governed transitions;
- 611 provisional occurrences.

Complete pedigree changes combined with long chronological gaps and incompatible age progression provide strong evidence of exact-label reuse. Short-gap exceptions and partial changes were reviewed separately rather than forced through a universal rule.

External and manual evidence established bounded corrections and aliases including Almutawakel, New President, Herbert, Bonny Ezra, Alderley Charlie, Hangry and Felix Felicis. Forest King supplied a confirmed example of two different registered horses sharing the same exact source label.

The pre-database authority review added confirmed bounded corrections for:

- `Almavillalobas (GB)` — governed dam `Nation (USA)`;
- `Colwyn Bay (FR)` — governed pedigree `Falco (USA)` / `Eudora (IRE)` / `King's Best (USA)`;
- `Diamond Tipp (IRE)` — governed pedigree `Diamond Boy (FR)` / `Soundout (IRE)` / `Oscar (IRE)`;
- `LAziza Des Places (FR)` — governed sire `Alanadi (FR)`.

## Interpretation

### Corrected

A corrected boundary remains one horse history. The governed analytical layer may use the established pedigree while preserving every raw source value and its lineage.

Correction does not authorise a global string-cleaning rule. Terminal numerals, prefixes, country suffixes and spelling differences are governed only within the bounded claim for which evidence exists.

### Different horse

A different-horse boundary means that one exact source label represents separate real horses. The histories must receive separate provisional occurrence identifiers before horse-level analysis.

The provisional identifier prevents accidental merging inside this source. It is not an official registration number or globally unique identity.

### Unresolved

The sole unresolved case is:

- `Runninsonofagun (IRE)`.

Weatherbys Ireland had not replied by 5 August 2026. The competing raw damsire assertions remain preserved, governed pedigree values remain null, and no identity split is created merely from publication consensus.

## Confidence

Confidence is high in the central conclusion that raw horse labels cannot serve as permanent natural keys.

Confidence is high in the 261 different-horse boundaries because the dominant evidence combines materially different pedigrees, separated chronology and generally incompatible age progression.

Confidence in individual corrected pedigrees varies with the evidence recorded in the specialist governance reference. That confidence is preserved per decision rather than implied globally.

## Limitations

The result is bounded to the supplied source database, the governed `rowid <> 1` population and the period and jurisdictions represented there.

The study does not prove that every stable pedigree is correct. It does not provide official identities for every horse. It does not establish that a name and country suffix are unique outside this dataset. One material case remains unresolved.

The occurrence assignment is a source-internal analytical construction. It must not be represented as an official registration or life number.

## What the result justifies

The work justifies:

- preserving all four raw source fields;
- refusing to use raw `horse` as a permanent natural key;
- applying bounded governed pedigree corrections;
- splitting the 261 identified same-label histories;
- excluding or isolating the remaining unresolved pedigree relationship;
- rebuilding horse-level derived data around governed occurrence identity.

It does not justify overwriting the source, globally stripping suffixes or numerals, inferring identity from name similarity, or treating the source as professionally complete.

## Manual-verification decision

**`specialist_reference`**

Notebook 19 depends on manual and external evidence. Three claims are recorded in `data/reference/manual_verifications.csv`. Equivalent evidence, status, confidence, decision identifiers and database consequences for the remaining bounded decisions and authority enquiries are preserved in:

`data/reference/horse_pedigree_identity_governance.csv`

The specialist table is the governing reference for Notebook 19 identity and pedigree decisions. It never overwrites immutable source data.

## Archival classification

Notebook 19 is a **non-rerunnable archival construction record**.

The saved executed notebook preserves the completed investigation, output tables, anomalies, external-review reasoning and final conclusion. It is not intended to regenerate permanent outputs directly.

A fresh-kernel rerun would add little reliability and would depend on interactive research, authority enquiries and external evidence that may change. Material exploratory classification cells must not be rerun and treated as production output independently of the governed reference and source-wide validator.

Durable replacement validation is provided by:

- `data/reference/horse_pedigree_identity_governance.csv`;
- `src/inside_rails/horse_pedigree_identity.py`;
- `src/inside_rails/horse_pedigree_identity_counts.py`;
- `tests/test_horse_pedigree_identity.py`;
- `tests/test_horse_pedigree_identity_counts.py`;
- `scripts/validate_horse_pedigree_identity.py`;
- `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Validation evidence

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

The focused identity tests were updated to enforce the final authority-reviewed unresolved set:

```bash
pytest -q tests/test_horse_pedigree_identity.py
```

Result: **9 passed in 0.59s**.

Independent source-wide validation:

```bash
python scripts/validate_horse_pedigree_identity.py
```

Result: **passed** with the final governed baselines:

- raw contradiction labels: 5,573;
- structured contradiction labels: 368;
- structured pedigree rows: 96,404;
- structured pedigree groups: 741;
- temporally separated horse labels: 350;
- separated pedigree groups: 703;
- governed transitions: 353;
- `Corrected`: 91;
- `Different horse`: 261;
- `Unresolved`: 1;
- provisional occurrences: 611.

The validator successfully wrote and reloaded both processed outputs.

## Persisted outputs

The independent validator wrote and reloaded:

- `data/processed/horse_pedigree_identity/transition_governance.csv`;
- `data/processed/horse_pedigree_identity/provisional_horse_occurrences.csv`.

The authority-reviewed outputs and updated reusable expected populations were committed and pushed in commit `7bdff5d`.

## Lessons learned

### Identity cannot be repaired with generic string cleaning

Suffixes, terminal numerals, prefixes and spelling differences can be formatting variants, aliases, metadata defects or real entity distinctions. Identity work must begin with contradiction structure and bounded evidence, not global replacements.

### Populated-value semantics must survive extraction

The independent implementation initially counted blank pedigree strings as competing labels, adding two false contradictions. Notebook 19 counted multiple populated labels. Production extraction must preserve that semantic distinction explicitly and test it.

### Full pedigree change is powerful but not sufficient alone

A complete pedigree change usually identified label reuse, but short-gap cases such as Felix Felicis demonstrated that a source row can instead carry the wrong pedigree. Chronology and age progression must remain part of identity classification.

### Manual review was appropriate for the finite residue

Once the unresolved set fell to five consequential cases, authority enquiries were more defensible than another automated similarity layer. Four replies or official confirmations resolved four cases; the unanswered case remains unresolved rather than guessed.

### The main analytical model should stay simple

The useful downstream outcomes are `Corrected`, `Different horse` and `Unresolved`. Detailed variant taxonomies are audit provenance, not the main analytical interface.

### External evidence must be captured while open

Future work should create the manual-verification or specialist-reference row at the time evidence is reviewed, not during final closeout.

### Stop exploratory analysis when the bounded question is answered

Once the three-outcome model and transition counts were established, the work should move directly to durable closeout implementation.

## Database consequence

Raw horse and pedigree labels remain immutable. The clean layer adds governed occurrence identity, governed pedigree fields, analytical outcome, decision basis, evidence identifier, confidence, review status and unresolved state.

Any existing derived table that groups histories by raw `horse` alone must be rebuilt. Full requirements and the update procedure are recorded in `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Remaining action

Notebook 19 no longer blocks database design. `Runninsonofagun (IRE)` remains a governed unresolved case pending any future Weatherbys Ireland response.

The next repository gate is the targeted cross-notebook implementation-completeness audit. The complete repository test suite and all-validator sweep remain deferred until the next appropriate branch-level gate.
