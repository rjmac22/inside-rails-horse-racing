# Notebook 21 Lessons Learned

## 1. Stop when field meaning is established

The comment field could support many future text-mining projects, but Notebook 21 only needed to establish meaning, coverage, preservation and safe governance. A general parser would have expanded scope without a defensible completeness standard.

Future behaviour: separate source-field governance from later feature-engineering studies.

## 2. Coverage can vary while semantics remain stable

Sparse overseas comments did not imply a different field meaning. Direct inspection showed broadly comparable in-running prose when populated, while jurisdiction profiles showed materially different availability.

Future behaviour: profile missingness by jurisdiction and race population before comparing any text-derived feature.

## 3. Reduce Python work to the smallest valid decision grain

Applying a Series-returning jurisdiction function across 189,043 race rows exhausted the notebook kernel. Most decisions depended only on 526 distinct ordinary course labels, with two bounded context-dependent course exceptions.

Future behaviour: estimate execution grain before running row-wise Python, reduce repeated inputs, isolate exceptions and join compact results back.

## 4. Immutable source means no temporary writes either

A temporary-table sampling join attempted to write into the read-only source database. SQLite correctly rejected it.

Future behaviour: create transient SQL state only in a separate writable in-memory or temporary-file analytics database, then attach the source read-only and immutable.

## 5. Full text must be visible during semantic inspection

Truncated dataframe display hid the exact end of comments, including terminal parenthetical material. Printing bounded examples in full exposed market text, attributed reports and malformed spacing.

Future behaviour: use full-text inspection for bounded semantic samples rather than relying on truncated tabular displays.

## 6. Short values require evidence, not intuition

The letters `A`, `B` and `V` invited an equipment interpretation, but source testing did not support it.

Future behaviour: preserve unexplained codes explicitly and defer interpretation until independent evidence exists.

## 7. Punctuation metrics can describe house style without parsing meaning

Near-zero comma and sentence-stop counts were not evidence of unstructured text. The source uses spaced hyphens as its dominant clause delimiter.

Future behaviour: inspect source-specific writing conventions before applying generic sentence or punctuation logic.

## 8. Conservative reusable code is still useful

The notebook did not justify a narrative parser, but it did justify a small reusable source-state classifier that preserves raw text, blanks, probable placeholders and unresolved codes.

Future behaviour: extract only the stable minimum rule supported by evidence; do not force every notebook to produce an ambitious transformation.

## 9. Workflow mistakes should become project guardrails

The kernel failure and immutable-source write attempt were not merely repaired locally. They resulted in permanent documentation covering large row-wise intermediates and temporary analytics write boundaries.

Future behaviour: convert consequential notebook failures into explicit reusable project rules.
