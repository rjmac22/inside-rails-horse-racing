# Notebook 22 Lessons Learned — Participant Identity

## 1. Candidate generation is not identity resolution

Removing a title or sorting tokens can produce useful candidate sets, but neither operation proves that two labels represent the same participant.

Future identity studies must keep candidate generation, evidence collection and accepted mappings as separate stages.

## 2. Same-race evidence is unusually valuable

The strongest owner evidence came from differently ordered labels with the same exact token multiset appearing within one reconstructed race.

That observation demonstrated source-presentation variation directly, without requiring speculative external matching.

Future work should look first for source-internal contradictions or co-occurrences that can prove or disprove an identity rule.

## 3. Population-wide chronology must precede transition rules

The trainer investigation initially produced a broader non-overlap population. The population-wide title profile then showed that only a narrow 2023–2024 transition window was defensible.

Future temporal identity rules must inspect the full chronology before treating non-overlapping periods as evidence.

## 4. Long gaps are not positive identity evidence

Two labels can share the same post-title text and never overlap while still lacking enough evidence for a merge. A long gap may increase uncertainty rather than resolve it.

Future rules must state an evidence-bearing time boundary instead of accepting every non-overlap.

## 5. Structurally mixed fields need structurally limited claims

The owner field combines individuals, partnerships, syndicates, companies, clubs, studs and compressed groups. One universal owner parser would manufacture false precision.

Future ownership studies should distinguish composition identity, organisation identity and individual identity rather than treating them as one problem.

## 6. Preserve the level of identity actually established

The accepted owner relationships establish that complete named compositions are equivalent under the source presentation. They do not establish each member's legal identity or share.

Future schema and writing must use labels such as `provisional_ownership_composition` rather than overstating the result as a verified owner entity.

## 7. Existing verification work must be inherited, not repeated

All jockey, trainer and owner blanks had already been governed by Notebook 20. Reconciliation through the permanent verification register avoided reopening settled cases or creating a parallel evidence system.

Future notebooks must check existing governed references before initiating new manual research.

## 8. Targeted external verification should resolve material decisions

Source-internal evidence was sufficient for the bounded trainer and owner rules, but the two decisive jockey cases benefited from targeted published evidence.

The Marie Velon participant profile supported a same-person source-label decision, while the published B O'Neill collision-race result supported a distinct-person decision. Both records retained candidate IDs, evidence locators, access dates, evidence types, confidence and database actions in the governed jockey review queue.

Future external research should be narrow, decision-specific and permanently attached to the governed candidate record rather than used as undocumented background knowledge.

## 9. Repository paths must be checked before use

An early attempt reconstructed the manual-verification location from memory and was wrong. The documented permanent register is `data/reference/manual_verifications.csv`.

Future work must read repository documentation and existing code before proposing paths, helper functions or closeout steps.

## 10. Closure route must be chosen from the procedure

A fresh-kernel rerun was initially proposed automatically. The wrap-up procedure allows an archival construction-record route where the notebook preserves reasoning and durable implementation lives outside it.

Future closeout work must choose the executable or archival route explicitly rather than assuming rerun safety is always required. An archival notebook does not require notebook-level rerun or save-and-reload proof unless it is intentionally being converted into the repeatable execution path.

## 11. One bounded step remains the strongest working method

The investigation improved when each output determined the next question: title candidates, chronology, bounded rule, persistence, source join and unresolved separation.

Future notebooks should continue to use one conceptual stage at a time and avoid speculative all-in-one identity pipelines.

## Reusable assets created

Notebook 22 created:

- conservative participant-label helper functions;
- focused unit tests for titles, chronology and owner token order;
- an independent source-wide participant identity validator;
- governed trainer mapping and unresolved outputs;
- governed owner mapping and unresolved outputs;
- a participant identity integration contract;
- explicit archival classification and reader-facing report.

## Concrete future behaviour

- Never treat title removal as a general merge rule.
- Never treat token sorting as proof.
- Use source-internal same-race evidence where available.
- Use targeted external verification where a material decision remains unresolved.
- Preserve external evidence locators, access dates, confidence and actions in the governed candidate record.
- Preserve exact raw labels and unresolved candidates.
- Store the scope of identity established in the identity type itself.
- Read the repository procedure and existing references before proposing closeout actions.
