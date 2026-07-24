# Notebook 09 Report — Course Jurisdiction, Racing Authority and Betting-Market Context

## Conclusion

The source database does not contain a universal racing-code, regulatory or betting-market model.

Course jurisdiction can be derived reproducibly across the complete source, but fields such as `type`, `dist`, `wgt` and `sp` must remain source observations whose deeper meaning may depend on jurisdiction, racing code, effective period, race context and provider convention.

Core reconstruction can proceed without completing worldwide racing research, provided that source values are preserved, candidate jurisdiction is stored separately, and later researched interpretation is held in an evidence-backed enrichment layer.

## Supporting evidence

- All 189,043 provisional races received a candidate jurisdiction.
- The source contains 36 candidate jurisdictions.
- The 528 raw course values reduce to 395 jurisdiction-qualified candidate venue or configuration identities.
- 135 candidate identities are represented by multiple raw course forms.
- No same-date collisions were found among those multiple raw forms.
- Great Britain contains four observed source racing types: Flat, Hurdle, Chase and NH Flat.
- All four Great Britain types were assigned to the British Horseracing Authority context while retaining code-specific interpretation.
- Ireland contains the same four source types and requires historical segmentation across the source period.
- Irish races from 2015–2017 were separated from races from 2018 onward to reflect the regulatory transition to the Irish Horseracing Regulatory Board.
- France contains 23 source-labelled `NH Flat` races, all of which are AQPS races run without obstacles.
- Those French AQPS records expose a coherent provider classification question that cannot yet be translated safely into a native France Galop code.
- The notebook passed Restart Kernel and Run All Cells without error.
- The independent course-jurisdiction validator passed.

## Reusable course and jurisdiction mapping

Stable course and jurisdiction logic was extracted to:

- `src/inside_rails/course_jurisdiction.py`
- `scripts/validate_course_jurisdiction.py`

The reusable mapping supports:

- extraction of recognised terminal jurisdiction suffixes;
- historical unsuffixed-course mappings;
- preservation of meaningful course configuration markers;
- derivation of candidate jurisdiction;
- derivation of candidate course labels;
- complete-source validation against the 189,043 provisional races.

Candidate jurisdiction is a reproducible structural derivation. It is not a substitute for a permanently verified canonical venue, authority or racing-code record.

## Classification grain

The notebook established that contextual classification must be allowed to escalate only as far as the evidence requires:

- jurisdiction level where context is stable;
- jurisdiction plus racing code where Flat and jumps require distinct interpretation;
- effective-period segmentation where the authority or rules framework changed during 2015–2026;
- course or race level only for documented exceptions;
- unresolved research status where no defensible interpretation has yet been established.

This prevents both false universalisation and unnecessary construction of a shallow worldwide reference catalogue.

## Worked jurisdiction examples

### Great Britain

The British Horseracing Authority governs the observed Flat, Hurdle, Chase and National Hunt Flat source types.

The authority context is shared, but the source types remain separate because they represent materially different racing-code contexts. Detailed rules-edition changes during the source period remain a later research question.

### Ireland

Ireland requires both racing-code and historical-period context.

The source population was divided into:

- 2015–2017;
- 2018 onward.

The later period uses the Irish Horseracing Regulatory Board as the regulatory authority, while Horse Racing Ireland remains a distinct administrative industry body. The four observed source types were retained separately.

### France

France Galop provides the principal authority context for the observed French thoroughbred races.

The source-labelled French `NH Flat` population consists of 23 AQPS races at Saint-Cloud, Longchamp and Chantilly. The evidence supports treating this as a coherent source-specific classification issue, but not yet replacing the raw source type with a claimed native French racing code.

The unresolved question is retained in a research register rather than forced into a completed classification.

## Bounded scope

Notebook 09 does not attempt to produce a complete worldwide regulator, rules and betting-market catalogue.

Its worked examples are limited to Great Britain, Ireland and France. Hong Kong, the United States and other jurisdictions will be researched later when a country-specific or analytical study requires their detailed context.

The escalation rule is:

> Add deeper jurisdiction, code, period, course or race-level context only when the planned analysis or observed source behaviour requires it.

## Separation of information layers

The future database must keep three information layers distinct.

### Source layer

Preserve values exactly as supplied, including source course, type, distance, carried weight and starting-price text.

### Structural derivation layer

Store reproducible derivations such as candidate race identity, candidate course identity, candidate jurisdiction and parsed source representations.

### Research interpretation layer

Store evidence-backed authority, racing-code, rules-period, wagering-system and source-to-native interpretation records separately, with confidence, evidence and effective periods.

Incomplete research must remain unassigned rather than guessed.

## Database consequence

The following are required before core reconstruction:

- retain source `type` exactly as supplied;
- store candidate jurisdiction separately from source course text;
- preserve raw `sp` while keeping market interpretation separate.

The following can be added later through research enrichment:

- native racing-code mappings;
- authority and rules records with effective periods;
- unresolved interpretation issues and later resolutions;
- detailed jurisdiction-specific betting-market context.

No final target schema was designed in this notebook.

## Confidence

**High** for complete candidate-jurisdiction assignment across the current source.

**High** for the reusable course-label and jurisdiction mapping under the currently observed domain.

**High** that source racing type and price fields cannot be treated as universal native concepts.

**High** for the need to separate source, structural derivation and researched interpretation layers.

**Incomplete** for jurisdiction-specific authority, rules and wagering histories not fully researched in this bounded study.

**Unresolved** for the exact native classification of the 23 French AQPS races labelled `NH Flat` by the source.

## Next action

Create Notebook 10 to inventory and triage every remaining source field.

Notebook 10 should identify:

- fields already investigated;
- fields that can be preserved without further semantic work;
- fields requiring dedicated profiling notebooks;
- fields requiring later jurisdiction-specific research.

After the remaining field studies are complete, consolidate the reconstruction requirements into a conceptual staging model before defining the physical schema.
