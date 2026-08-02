# Notebook 19 Closeout — Horse and Pedigree Identity

## Status

**Implemented pending local validation.**

The analytical investigation is complete. The notebook is classified as a **non-rerunnable archival construction record**. Durable implementation, governed reference data, focused tests, an independent source-wide validator and database-integration documentation now exist outside the notebook. The notebook must not be marked fully closed until the focused local tests and source-wide validator have passed and their exact results have been recorded.

## Bounded question

What do the runner-level `horse`, `sire`, `dam` and `damsire` fields represent, how stable and complete are their labels, and which identity or pedigree relationships can be preserved safely without inventing entity equivalence from names alone?

## Executive conclusion

The raw `horse` field is a source-presented label, not a permanent horse identifier.

The same displayed horse name and breeding-country suffix can be reused by different real horses. One real horse can also appear with incorrect, incomplete or inconsistent pedigree assertions. Horse identity and pedigree therefore require a governed analytical layer rather than direct use of the raw strings.

The 353 material transitions between temporally separated structured pedigree histories produced:

- 87 `Corrected` transitions across 84 exact labels;
- 261 `Different horse` transitions across 261 exact labels;
- 5 `Unresolved` transitions across 5 exact labels.

The governed split boundaries produce 611 provisional source-internal horse occurrences from 350 exact source labels and 703 structured pedigree groups.

## Core evidence

The source population contains 1,851,285 governed runner rows and 189,043 provisional races under `rowid <> 1`.

The source pedigree fields are highly populated, but repeated exact horse labels can carry incompatible pedigrees. After reversible treatment of dam suffix formatting, 368 repeated labels retained structured pedigree contradictions. Most contradictory histories were temporally separated.

Complete pedigree changes combined with long chronological gaps and incompatible age progression provide strong evidence of exact-label reuse. Short-gap exceptions and partial changes were reviewed separately rather than forced through a universal rule.

External and manual evidence established bounded corrections and aliases including Almutawakel, New President, Herbert, Bonny Ezra, Alderley Charlie, Hangry and Felix Felicis. Forest King supplied a confirmed example of two different registered horses sharing the same exact source label.

## Interpretation

### Corrected

A corrected boundary remains one horse history. The governed analytical layer may use the established pedigree while preserving every raw source value and its lineage.

Correction does not authorise a global string-cleaning rule. Terminal numerals, prefixes, country suffixes and spelling differences are governed only within the bounded claim for which evidence exists.

### Different horse

A different-horse boundary means that one exact source label represents separate real horses. The histories must receive separate provisional occurrence identifiers before horse-level analysis.

The provisional identifier prevents accidental merging inside this source. It is not an official registration number or globally unique identity.

### Unresolved

The unresolved cases are:

- `Almavillalobas (GB)`;
- `Colwyn Bay (FR)`;
- `Diamond Tipp (IRE)`;
- `LAziza Des Places (FR)`;
- `Runninsonofagun (IRE)`.

Authority enquiries were sent on 2 August 2026. Until a reply is received, the competing raw assertions remain preserved, governed pedigree values remain null, and no identity split is created merely from publication consensus.

## Confidence

Confidence is high in the central conclusion that raw horse labels cannot serve as permanent natural keys.

Confidence is high in the 261 different-horse boundaries because the dominant evidence combines materially different pedigrees, separated chronology and generally incompatible age progression.

Confidence in individual corrected pedigrees varies with the evidence recorded in the specialist governance reference. That confidence is preserved per decision rather than implied globally.

## Limitations

The result is bounded to the supplied source database, the governed `rowid <> 1` population and the period and jurisdictions represented there.

The study does not prove that every stable pedigree is correct. It does not provide official identities for every horse. It does not establish that a name and country suffix are unique outside this dataset. Five material cases remain unresolved.

The occurrence assignment is a source-internal analytical construction. It must not be represented as an official registration or life number.

## What the result justifies

The work justifies:

- preserving all four raw source fields;
- refusing to use raw `horse` as a permanent natural key;
- applying bounded governed pedigree corrections;
- splitting the 261 identified same-label histories;
- excluding or isolating unresolved pedigree relationships;
- rebuilding horse-level derived data around governed occurrence identity.

It does not justify overwriting the source, globally stripping suffixes or numerals, inferring identity from name similarity, or treating the source as professionally complete.

## Manual-verification decision

**`specialist_reference`**

Notebook 19 depends on manual and external evidence. Three claims are recorded in `data/reference/manual_verifications.csv`. Equivalent evidence, status, confidence, decision identifiers and database consequences for the remaining bounded decisions and pending enquiries are preserved in the more specific governed table:

`data/reference/horse_pedigree_identity_governance.csv`

The specialist table is the governing reference for Notebook 19 identity and pedigree decisions. It never overwrites immutable source data.

## Archival classification

Notebook 19 is a **non-rerunnable archival construction record**.

The saved executed notebook preserves the completed investigation, output tables, anomalies, external-review reasoning and final conclusion. It is not intended to regenerate permanent outputs directly.

A fresh-kernel rerun would add little reliability and would depend on interactive research, authority enquiries and external evidence that may change. Harmless exploratory and recovery history therefore need not be removed solely to manufacture restart safety.

Material caution: cells that perform exploratory classification or construct provisional decisions should not be rerun and treated as production output independently of the governed reference and source-wide validator.

Durable replacement validation is provided by:

- `data/reference/horse_pedigree_identity_governance.csv`;
- `src/inside_rails/horse_pedigree_identity.py`;
- `tests/test_horse_pedigree_identity.py`;
- `scripts/validate_horse_pedigree_identity.py`;
- `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Persisted outputs

The independent validator is responsible for writing and reloading:

- `data/processed/horse_pedigree_identity/transition_governance.csv`;
- `data/processed/horse_pedigree_identity/provisional_horse_occurrences.csv`.

These outputs remain pending until the validator runs successfully against the immutable local source.

## Lessons learned

### Identity cannot be repaired with generic string cleaning

The largest conceptual risk was treating suffixes, terminal numerals, prefixes or spelling differences as a formatting problem. Some are formatting variants, some are aliases, some are metadata defects and some distinguish real entities. Future identity work must begin with contradiction structure and bounded evidence, not global replacement rules.

### Full pedigree change is powerful but not sufficient alone

A complete pedigree change usually identified label reuse, but short-gap cases such as Felix Felicis demonstrated that a source row can instead carry the wrong pedigree. Chronology and age progression must remain part of identity classification.

### Manual review was appropriate for the finite residue

Once the unresolved set fell to five consequential cases, authority enquiries were more defensible than another automated similarity layer. Future notebooks should switch to manual review earlier when the remaining residue is small, ambiguous and high consequence.

### The main analytical model should stay simple

The useful downstream outcomes are `Corrected`, `Different horse` and `Unresolved`. Detailed variant taxonomies are audit provenance, not the main analytical interface. Future reports should distinguish implementation detail from the decision the reader or database needs.

### External evidence must be captured while open

Several external checks were initially discussed in notebook prose before permanent identifiers were assigned. Future work should create the manual-verification or specialist-reference row at the time the evidence is reviewed, not during final closeout.

### Stop exploratory analysis when the bounded question is answered

The investigation began to repeat its conclusion after the three-outcome model and transition counts were established. Future notebook work should move directly from answered question to closeout implementation rather than adding further summary stages.

## Database consequence

Raw horse and pedigree labels remain immutable. The clean layer adds governed occurrence identity, governed pedigree fields, analytical outcome, decision basis, evidence identifier, confidence, review status and unresolved state.

Any existing derived table that groups histories by raw `horse` alone must be rebuilt. Full requirements and the update procedure are recorded in `docs/HORSE_PEDIGREE_IDENTITY_INTEGRATION.md`.

## Remaining closeout actions

Before Notebook 19 can be marked fully closed:

1. run the focused horse-identity and manual-verification tests locally;
2. run the independent horse-identity validator against the immutable local source;
3. confirm that both processed outputs were written and reloaded;
4. record the exact commands and results in this closeout record and the retrospective audit;
5. update the README and project plan to the validated final state;
6. confirm that the source-field governance rows move from `implemented_pending_validation` only when validation evidence supports that change.

The complete repository test suite and all-validator sweep remain deferred until the end of the notebook series or repair branch.
