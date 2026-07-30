# Notebook 16 lessons learned

## What proved harder than expected

The apparent task was to interpret five compact classification and eligibility fields. The difficult part was establishing where stable syntax ended and jurisdiction-specific semantics began.

`sex_rest` looked especially simple. Source-wide comparison showed that `F` could not be treated as a literal universal permitted-sex code. Age-band contradictions also proved heterogeneous: some were age-band defects, some were runner-age defects, some reflected contextual semantics, and some remained unresolved.

## Assumptions that were wrong

- A populated compact code is not necessarily the official classification itself.
- `class`, `pattern` and `rating_band` are not alternative versions of one hierarchy.
- Exact-looking age syntax does not prove universally closed eligibility.
- A disagreement between race-level and runner-level fields does not establish which field is wrong.
- A new explicit category appearing in recent years does not imply a clean historical schema transition.

## Scope expansion

External age verification expanded the work beyond source-internal profiling. This was justified because the contradictions directly affected the safe interpretation of `age_band`.

A full official sex-condition reconstruction was not justified. It would require jurisdiction-specific official condition text and a separate governed provenance model. That work was explicitly deferred rather than approximated from `sex_rest`.

## Automation and manual review

Source-wide profiling efficiently identified contradiction clusters, coding transitions and unusual vocabularies. It could not determine the cause of individual age discrepancies.

Manual verification was appropriate for a small bounded set of materially different examples. Those decisions were captured immediately under `NB16-AGE-0001` through `NB16-AGE-0004` rather than left in notebook prose.

## Workflow errors not to repeat

The closeout process was initially treated as a sequence requiring repeated user prompts. That contradicted the project procedure. Once the analytical conclusion is settled, the assistant should inspect the established repository patterns and complete the whole applicable closeout package without handing repository-orientation work back to the user.

A validator was also first created without a direct-script `src/` bootstrap. Future validators should be runnable exactly as documented from the repository root before they are handed over.

## Reusable assets created

- governed parser module for five race-level fields;
- public package exports;
- 15 focused unit tests including malformed and unresolved behaviour;
- independent validator covering the complete source population;
- database-integration contract;
- persisted field-decision table;
- governed manual-verification evidence;
- field-governance record;
- reader-facing report.

## Concrete future behaviour

1. Treat compact vendor codes as source classifications until their relationship to official conditions is proved.
2. Parse syntax separately from semantic enforcement.
3. Investigate contradictions by cause family before designing corrections.
4. Use race-name wording only as supporting evidence and guard against title or sponsorship false positives.
5. Do not infer clean schema transitions from the first appearance of a new category.
6. When external evidence is used, capture the bounded claim immediately in the verification register.
7. Complete the full documented closeout package after the analytical conclusion, then ask the user only for genuinely local execution evidence that cannot be obtained through the repository connector.
