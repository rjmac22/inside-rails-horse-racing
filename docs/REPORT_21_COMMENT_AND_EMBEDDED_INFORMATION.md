# Notebook 21 Report — Comment and Embedded Information

## Executive conclusion

The source `comment` field is meaningful runner-level racing evidence, but it is not a safely parseable universal structure.

When substantively populated, the field is generally an English-language description of race position and performance. That broad meaning is consistent across inspected British, Irish and overseas feeds. The main source limitation is not semantic inconsistency but sharply different availability by jurisdiction.

The correct database decision is to preserve the exact raw comment, classify only conservative source states, retain jurisdiction and lineage, and defer general structured extraction.

## Core evidence

The governed source contains:

- 1,851,285 runner rows;
- 189,043 provisional races;
- 340,394 empty-string comments;
- no SQL null comments;
- 1,510,891 populated comments;
- 1,426,745 distinct populated values;
- populated lengths from 1 to 2,206 characters.

A conservative partition identifies 238 rows as probable placeholders or unresolved source codes and 1,510,653 rows as substantive text.

Coverage is strongly jurisdiction-dependent. Great Britain and Ireland are complete in this source. Hong Kong and the United Arab Emirates are nearly complete. France, the United States, Australia, Japan and several other overseas feeds are sparse or selective.

A bounded cross-jurisdiction sample showed recognisably similar in-running prose in Great Britain, Ireland, France, Germany, Australia, Italy, Hong Kong, the United States and the UAE. Typical comment lengths were broadly comparable outside the shorter and more repetitive UAE sample.

Terminal parenthetical material is concentrated in Great Britain and Ireland. It can contain market movements, attributed jockey or trainer statements, adjacent brackets, nesting and malformed source structure.

## Interpretation

The field should be understood as a runner-level source assertion rather than an objective structured fact.

Substantive comments can support:

- direct qualitative race review;
- bounded manual investigations;
- article evidence and illustrative examples;
- later validated studies of tactics, incidents, jumping errors and finishing effort.

They do not currently support an authorised general parser. A phrase being recognisable to a reader does not prove that it can be extracted completely and consistently across the source.

## Confidence

Confidence is high in the physical profile, source-state partition and broad runner-level meaning. Confidence is also high that comment missingness is jurisdiction- and feed-dependent.

Confidence is low in any universal interpretation of rare short codes and in any simple rule for separating narrative, reports and market material.

## Limitations

- Coverage differs materially by jurisdiction and period.
- Empty comments are source absence, not evidence that no incident occurred.
- The source does not identify authorship, translation history or editorial workflow.
- Rare codes `A`, `B` and `V` remain unresolved.
- Parenthetical structures are not consistently well formed.
- The bounded jurisdiction sample describes form, not complete source-provider provenance.
- The notebook does not establish recoverability or licensing for missing overseas commentary.

## Database consequence

Preserve the exact raw comment and physical lineage. Add only a conservative governed state:

- `empty_string`;
- `probable_placeholder`;
- `unresolved_source_code`;
- `substantive_text`;
- `unexpected_null`.

Any future extracted information must be stored separately with method, version, character span where possible, confidence, review status and source lineage. It must never replace the raw comment.

## Practical implication

Comment-based analysis is most defensible for British and Irish racing in this source because coverage is complete. Overseas comparisons require explicit coverage controls.

The field is valuable now as preserved evidence and for bounded manual or assisted analysis. Large-scale structured extraction is a separate future research programme, not a prerequisite for completing the source-field series.

## Next action

Close Notebook 21, run its focused tests and independent validator, then perform the end-of-series complete test and validator sweep before beginning participant identity studies.
