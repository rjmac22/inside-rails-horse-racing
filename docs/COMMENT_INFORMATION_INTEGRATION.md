# Comment Information Integration

## Scope

This contract governs the source `data.comment` field established by Notebook 21.

## Raw preservation

The immutable source value must be retained exactly as supplied, including:

- empty strings;
- rare placeholder-like tokens;
- unresolved one-character codes;
- leading whitespace anomalies;
- hyphen-delimited narrative;
- attributed reports;
- terminal market material;
- malformed or nested parenthetical structures.

No integration step may trim, rewrite, translate or split the raw value in place.

## Rendered-output safeguard

A Study 01 follow-up diagnostic on 8 August 2026 investigated an apparent copied value resembling `Walkover<br><br><br>`.

The source-wide check found **zero admitted comments containing a literal `<` character**. The accepted Inside Rails Version 1 database stores the decisive Hereford / Queensbury Boy value exactly as `Walkover`: SQLite type `text`, character length 8, no line feed, no carriage return, and UTF-8 hexadecimal `57616C6B6F766572`.

The apparent `<br>` material was introduced after the stored value, during rendered-output / copy-paste transport. The pasted representation also merged text from a separate diagnostic cell, confirming that the markup was not part of the governed comment value.

Database consequence:

- do **not** add `comment_plain_text` merely to remove HTML-like markup;
- do **not** add generic HTML stripping, `<br>` removal or newline stripping on the basis of copied notebook output;
- inspect the stored value directly before treating presentation markup as source evidence;
- preserve Notebook 21's conservative raw-comment governance unchanged unless new stored-data evidence establishes a real source-format requirement.

This diagnostic does not prohibit a future bounded presentation field if independently justified by actual stored source content. It establishes only that the observed Study 01 markup did not justify one.

## Governed fields

A future staging or core model should expose at least:

| Field | Type | Meaning |
|---|---|---|
| `raw_comment` | nullable text only if the target database requires it | Exact immutable source value. The present source contains no SQL nulls. |
| `comment_state` | constrained text | `empty_string`, `probable_placeholder`, `unresolved_source_code`, `substantive_text`, or `unexpected_null`. |
| `comment_analytically_available` | boolean | True only for `substantive_text`. |
| `source_rowid` | integer | Physical source-row lineage. |
| `source_database` | text | Source database identifier. |
| `source_table` | text | `data`. |
| `candidate_jurisdiction` | text | Governed candidate jurisdiction from the existing jurisdiction implementation. |
| `jurisdiction_evidence` | text | Method/evidence used to assign candidate jurisdiction. |

Any later extracted assertion must live in a separate child table and include:

- the source runner key and source row identifier;
- the unchanged raw comment;
- extraction method and version;
- assertion type and extracted value;
- source character span where technically possible;
- confidence and review status;
- language and translation provenance where applicable.

## Null, blank and unresolved treatment

- Preserve `''` as source-presented absence. Do not convert it into a claim that no race incident occurred.
- A SQL null is unexpected for this source and must fail validation or be quarantined explicitly.
- Preserve `A`, `B` and `V` as unresolved source codes. Do not map them to headgear or any other meaning without independent evidence.
- Preserve `.`, `..`, `-`, ` -`, `/` and `1` as probable placeholders rather than substantive prose.
- Do not classify other short comments as placeholders merely because they are brief.

## Jurisdiction and coverage

The broad semantic meaning of substantive comments is consistent across the inspected jurisdictions, but availability is not. Great Britain and Ireland are complete in the governed source, while several overseas feeds are sparse or selective.

Every analytical product using comments must therefore report or control for comment coverage by jurisdiction, period and relevant race population. Empty comments must not be treated as missing at random.

## Embedded information

Notebook 21 does not authorise a general parser. In particular:

- British and Irish terminal parentheticals may combine market movements and attributed reports;
- malformed, adjacent and nested parentheses exist;
- the field is predominantly structured by spaced hyphens rather than sentences;
- punctuation alone is not a safe segmentation rule.

Market extraction, incident classification, tactical labels and performance-language features remain separate future studies requiring independently validated rules.

## Join and cardinality requirements

The source comment is runner-level and must remain attached to the exact source runner row. Do not join it by horse label alone. Use physical lineage and the governed race/runner reconstruction appropriate to the target database.

Any derived assertion table may contain zero, one or many assertions per source comment. It must therefore use a one-to-many relationship from the governed runner record and retain assertion identifiers.

## Update and validation procedure

For a new source snapshot:

1. open the source read-only and apply `rowid <> 1`;
2. rerun `scripts/validate_comment_information.py`;
3. investigate any changed population baseline before updating expected counts;
4. profile new short tokens and unexpected nulls;
5. compare jurisdiction and period coverage with the prior snapshot;
6. preserve newly observed unresolved values rather than extending a parser speculatively;
7. rebuild downstream comment-state fields and assertion tables;
8. record method/version changes and reconciliation counts.

The current source-wide baselines are 1,851,285 governed runner rows, 340,394 empty strings, 238 probable-placeholder or unresolved-code rows, and 1,510,653 substantive-text rows.
