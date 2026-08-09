# Inside Rails Study Research Playbook

## Purpose

This document records the reusable research rules, analytical standards, workflow decisions, publication safeguards and lessons learned from Inside Rails studies.

It applies to reader-facing analytical studies rather than source-field and database-construction investigations.

Read this document before beginning every new study.

Update it when a completed study reveals a genuinely reusable lesson, mistake, safeguard or better way of working. Do not add study-specific findings that have no broader methodological value.

The purpose is to make each new study better than the last rather than repeatedly rediscovering the same analytical and workflow lessons.

---

## 1. The evidence writes the story

The central research principle is:

> The evidence writes the story; the story does not decide what evidence we need.

Begin with a worthwhile question, not a desired conclusion.

Do not decide in advance what the article is going to say and then select analyses that support that narrative.

A study may:

- support the original idea;
- qualify it;
- reveal that the effect is much smaller than expected;
- show that another variable matters more;
- expose a data limitation that changes the question;
- produce an unexpected result;
- produce a null result.

All of these are legitimate outcomes.

The eventual article should be shaped around the strongest defensible finding produced by the research.

---

## 2. Questions are allowed; conclusions are not

Evidence-led research does not mean aimless exploration.

Each study should begin with a bounded research question.

For example:

> What relationship, if any, exists between field size and the predictability of British horse races?

This is preferable to:

> Large fields are less predictable.

The first states what we want to discover.

The second risks turning an untested proposition into the organising assumption of the analysis.

---

## 3. Work one analytical question at a time

Do not write an entire predetermined sequence of analyses before seeing the first result.

Use the following cycle:

1. state the current bounded question;
2. explain why answering it is necessary;
3. run the smallest appropriate analysis;
4. inspect the result;
5. record what it establishes and what it does not establish;
6. decide what question follows from that evidence.

Later analysis should therefore respond to earlier evidence.

This reduces confirmation bias and prevents unnecessary work.

---

## 4. Establish the population before analysing relationships

Before testing an interesting racing claim, establish exactly what observations are being analysed.

At minimum consider:

- jurisdiction;
- racing code or type where relevant;
- period;
- number of races;
- number of runners where relevant;
- inclusion and exclusion rules;
- missingness in fields required by the study;
- known governed source anomalies affecting those fields.

Do not allow an attractive chart to become the first time we discover that the underlying population is not what we thought it was.

---

## 5. Use governed fields only

A field name is not evidence that a source field means what it appears to mean.

Before relying on a field:

- check the existing field-governance work;
- use the authorised race and runner identities;
- preserve the project's source admission rules;
- respect documented anomalies and unresolved states;
- do not invent a new interpretation merely because it would make the study easier.

Where an analytically necessary field has not been sufficiently governed, stop that line of analysis and investigate the field properly rather than silently assuming its meaning.

---

## 6. Escalate material database work out of the study

Study notebooks must not become a second database-building system.

If a study reveals a database defect, missing governed transformation, or reusable enhancement that materially affects the reliability or repeatability of the analysis, pause the study and handle that work in the database layer first.

Use three categories:

### Required database fix

Leave the study when the issue affects correctness, such as:

- wrong or unstable race population;
- unreliable field semantics;
- broken or unsuitable join keys;
- missing canonical transformations;
- material source anomalies not covered by governance;
- a database defect that could distort the study conclusion.

### Reusable database enhancement

Usually leave the study when the missing structure will clearly support multiple future studies and belongs in the analytical data layer rather than one notebook.

### Study-specific derivation

Keep a transformation inside the study when it exists only to answer that study's question and does not need database-level governance or reuse.

The test is:

> Would leaving this inside the study compromise correctness, governance, or meaningful reuse?

If yes, escalate it. If it is merely a convenient study-specific dataframe calculation, keep it in the study.

When a study is paused for database work, record:

- the study blocker;
- why database work is required;
- the database artifact or governed implementation that resolves it;
- the version or commit used when the study resumes.

---

## 7. Separate observation from explanation

First establish what happened.

Only then ask why it may have happened.

For example, an observed relationship between field size and favourite win rate does not by itself establish that field size causes greater uncertainty.

Possible explanations or confounders may include:

- race type;
- handicap status;
- class;
- code;
- distance;
- composition of the betting market;
- favourite starting price;
- other characteristics of races that tend to have particular field sizes.

Do not introduce controls or subgroup analyses automatically. Introduce them when the observed evidence creates a reason to test an explanation.

---

## 8. Description comes before modelling

Begin with transparent descriptive evidence wherever it can answer the question.

Prefer initially:

- counts;
- distributions;
- proportions;
- medians and quantiles where appropriate;
- small tables;
- clearly labelled plots.

Do not use a complicated model merely because one is available.

More advanced statistical methods should answer a question that simpler analysis cannot answer adequately.

---

## 9. Define measures before interpreting them

Terms such as:

- predictable;
- competitive;
- strong favourite;
- upset;
- large field;
- short priced;
- profitable;

are analytical concepts, not self-defining facts.

Before drawing conclusions from one of these ideas:

1. define the measure;
2. explain why that measure represents the concept;
3. examine its limitations;
4. distinguish alternative reasonable definitions where material.

Do not allow convenient thresholds to masquerade as natural categories.

---

## 10. Avoid arbitrary buckets unless they earn their place

Continuous or count variables should normally be inspected in their original form before being grouped.

For example, do not immediately classify field sizes as small, medium and large without first examining the actual distribution and deciding whether grouping helps interpretation.

Where categories are introduced:

- explain the boundary;
- test whether the conclusion depends materially on it;
- prefer racing-relevant or evidence-supported boundaries over visually convenient ones.

---

## 11. Use a meaningful baseline

A result is not interesting merely because it has a number attached to it.

Before interpreting a difference, establish the appropriate comparison or baseline.

Possible baselines include:

- another field-size range;
- the overall race population;
- market-implied expectation;
- another justified race population;
- an earlier period where temporal comparison is the question.

The baseline must answer the same substantive question and not be chosen merely because it makes the result look stronger.

---

## 12. Separate exploratory and confirmatory findings

A pattern discovered while exploring the data is not automatically confirmed by the same data that revealed it.

Mark findings as exploratory when they emerge after looking through multiple possibilities.

Where a finding is important enough to support a strong claim, prefer confirmation using one or more of:

- a different time period;
- a holdout population;
- a different suitable subgroup;
- a reasonable alternative definition;
- an independently derived measure.

Do not rewrite the analytical history so that a discovered relationship appears to have been the original hypothesis.

---

## 13. Watch multiple comparisons and subgroup searching

The more categories, periods, courses, distances, trainers, classes or other slices we examine, the more likely some apparently striking result will occur by chance.

Do not keep slicing the data until an interesting pattern appears.

The more exploratory searching that preceded a finding, the more cautious the interpretation and publication language should be.

Rankings and extreme subgroup claims require particular care because selecting the highest or lowest values is itself a form of multiple comparison.

---

## 14. Avoid retrospective threshold optimisation

Do not search for the exact cutoff that produces the strongest result and then present that threshold as though it had prior racing meaning.

Examples include optimising:

- a field-size cutoff;
- a starting-price cutoff;
- a distance boundary;
- a minimum race count;
- a historical date boundary.

If a threshold is explored, disclose that fact and test sensitivity to reasonable neighbouring definitions.

---

## 15. Test sensitivity to reasonable definitions

A strong finding should not normally depend on one fragile arbitrary analytical choice.

Where reasonable alternatives exist, ask whether the conclusion survives changes to:

- thresholds;
- inclusion criteria;
- time periods;
- category definitions;
- treatment of borderline cases;
- reasonable versions of the outcome measure.

If the conclusion changes materially, that sensitivity is part of the finding.

---

## 16. Prefer replication over complexity

When a result looks surprising, first ask whether it replicates before reaching for a more complicated model.

Useful replication may involve:

- another time period;
- another suitable subset;
- another defensible measure;
- another reasonable definition.

A simple relationship that repeatedly reappears is often more persuasive than a complicated model fitted once.

---

## 17. Check temporal stability

A relationship over the whole database may conceal meaningful changes through time.

Important findings should be checked for temporal stability where the question implies a general or current racing relationship.

Do not assume that a result averaged across many years describes every year or remains current.

---

## 18. Check whether aggregate findings are composition effects

A national or overall result may be driven by a smaller number of dominant groups.

Where material, inspect whether an aggregate finding is largely explained by differences in composition such as:

- racing code;
- handicap status;
- class;
- course;
- period;
- race type;
- other strongly uneven characteristics.

Remain alert to Simpson's paradox: an aggregate relationship can weaken, disappear or reverse within relevant subgroups.

Do not stratify everything automatically. Investigate composition when the observed population gives a reason to suspect it matters.

---

## 19. No causal language without causal evidence

Most Inside Rails studies will use observational historical data.

Prefer language such as:

- associated with;
- varies with;
- more common in;
- observed alongside;

unless the design genuinely supports a causal interpretation.

Do not convert an association into a causal story because the explanation sounds plausible.

---

## 20. Do not use future information accidentally

Any analysis intended to represent information available before a race must only use information that would have been available at the relevant decision time.

Prevent leakage from information such as:

- finishing positions;
- later ratings;
- subsequent form;
- retrospectively derived information unavailable before the race;
- future races involving the same participant.

Distinguish clearly between retrospective explanation and prospective usefulness.

A variable can explain historical outcomes while being unusable for a real pre-race decision.

---

## 21. Distinguish predictability from betting value

A statistical relationship is not automatically a betting opportunity.

For example:

- favourites winning more often does not imply profitable favourite betting;
- larger variance does not imply exploitable mispricing;
- a subgroup outperforming another subgroup does not establish positive expected value.

Claims about betting value require additional evidence including, where applicable:

- available odds;
- price sensitivity;
- market margin;
- sample stability;
- realistic bet selection;
- transaction or liquidity constraints;
- out-of-sample or temporal robustness.

Research conclusions and betting decisions must remain separate.

---

## 22. The market expectation matters

Where starting prices or probabilities are involved, distinguish:

> What happened?

from:

> What was expected to happen at the prices available?

A lower raw win rate in one type of race may simply reflect shorter or longer prices in that population.

Where the data permits it, compare outcomes with market-implied expectations before interpreting differences as evidence of unusual predictability or mispricing.

Do not make this comparison until the relevant price data and probability treatment are justified.

---

## 23. Null and boring results are valid

If a sensible analysis shows little or no meaningful relationship, that may itself answer a widely held racing belief.

Repeated subgroup searching increases the likelihood of finding accidental patterns.

Any exploratory finding discovered after extensive searching should be labelled as exploratory and treated more cautiously than a relationship tested from a prior question.

Do not manufacture novelty where the evidence mainly confirms something ordinary.

---

## 24. Effect size matters more than mere statistical significance

With a large historical database, very small differences can become statistically detectable.

Ask:

- How large is the difference?
- Is it stable?
- Is it practically meaningful?
- Would a reader care?
- Does it change how the racing question should be understood?

A tiny effect with a very small p-value is still a tiny effect.

Statistical uncertainty should be reported where useful, but significance testing must not become a substitute for interpretation.

---

## 25. Keep sample sizes visible

Rates and percentages should be accompanied by enough information to understand the underlying sample.

A striking percentage based on a very small number of races should not visually compete with a stable estimate based on thousands of races without that distinction being obvious.

Where useful, present raw counts beside rates.

---

## 26. Show uncertainty where it affects interpretation

Use confidence intervals, uncertainty bands or other appropriate measures when sampling uncertainty materially affects interpretation.

Do not add uncertainty displays mechanically to every output simply to appear technical.

Statistical uncertainty must also be kept separate from source-quality and semantic uncertainty.

A narrow confidence interval does not prove that the underlying data means what we think it means.

---

## 27. Respect dependence and repeated observations

Horse-racing data is hierarchical and repeated.

Observations may share:

- races;
- horses;
- jockeys;
- trainers;
- owners;
- courses;
- dates;
- meetings;
- market conditions.

Do not casually treat every runner row as an independent observation where the analytical question operates at race level or repeated participants create dependence.

Choose the unit of analysis to match the research question.

For race-level questions, prefer race-level measures unless a runner-level structure is analytically necessary and properly handled.

---

## 28. Inspect denominators

Every percentage should have a clear denominator.

Record enough information to distinguish, for example:

- percentage of races;
- percentage of runners;
- percentage of races with usable prices;
- percentage among favourites;
- percentage among completed runners.

Unexpected changes in denominators may reveal missing data, selection effects or faulty joins.

---

## 29. Missing data can change the population

Do not simply drop null or unresolved values and continue.

Before exclusion:

- count them;
- identify their pattern;
- determine whether missingness differs by period, jurisdiction or race type where relevant;
- state what population remains after exclusion.

A clean-looking analytical dataframe may represent a highly selected subset of the source.

---

## 30. Define exclusions for analytical reasons

Do not exclude races, runners or categories because removing them improves the graph or strengthens the result.

Exclusions should follow from:

- the research question;
- data-governance requirements;
- incompatible race structures;
- unusable or unresolved evidence;
- another explicit analytical reason.

Record material exclusions and their effect on the population.

---

## 31. Strange observations are evidence

Extreme field sizes, unusual prices, unexpected outcomes and apparent anomalies should be inspected before being deleted.

They may reveal:

- source errors;
- unusual but legitimate races;
- coding problems;
- historical practices;
- analytical assumptions that do not hold universally.

Material unexpected results must also trigger an external verification check where a suitable authoritative or independent source is reasonably available. Do this before treating the observation as a genuine sporting phenomenon, using it to support a substantive explanation, or building further analysis on an unverified interpretation.

Prefer the most authoritative source appropriate to the fact being checked, such as an official governing body, official result, racecourse, regulator or other primary record. The purpose is not to replace the database analysis with external research, but to distinguish real-world exceptions from source errors, missing data, processing artefacts or misunderstood semantics.

If no suitable external evidence is reasonably available, record that fact and keep the unexpected result provisional or unresolved rather than silently treating it as true.

Preserve the provenance of material external checks under the project's external-claim and manual-verification rules.

Removal requires a defensible reason, not merely inconvenience.

---

## 32. Preserve negative evidence

When a plausible explanation or robustness test fails, retain that result in the research record.

Do not preserve only analyses that strengthen the eventual conclusion.

Negative evidence can narrow the explanation and prevents later researchers from repeating the same dead end.

---

## 33. Distinguish data uncertainty from statistical uncertainty

Statistical uncertainty describes uncertainty conditional on the analytical data and model assumptions.

It does not automatically capture:

- source errors;
- ambiguous semantics;
- selective missingness;
- unresolved identities;
- extraction limitations;
- historical coverage problems.

Report these separately where they matter.

---

## 34. Do not confuse precision with accuracy

Software can produce more decimal places than the evidence justifies.

Report precision appropriate to the measurement, sample size and analytical purpose.

Do not imply certainty through unnecessary decimal places.

---

## 35. Prefer reproducible transformations

Important analytical transformations should be explicit.

Avoid unexplained notebook behaviour such as:

- hidden dataframe filtering;
- silently overwritten variables;
- unexplained hard-coded exclusions;
- thresholds introduced without commentary.

A later reader should be able to reconstruct how the analytical population changed from one stage to the next.

---

## 36. Preserve the analytical path

The notebook should retain enough of the research history to distinguish:

- the original bounded question;
- exploratory analyses;
- hypotheses suggested by earlier outputs;
- robustness checks;
- failed explanations;
- confirmatory work.

Do not rewrite the notebook so thoroughly that a finding discovered on the ninth attempt appears to have been the plan from the beginning.

Exploratory repair may be cleaned where it is merely technical noise, but material analytical choices and dead ends should remain understandable.

---

## 37. Use a stopping rule for exploration

A study should not expand indefinitely because another subgroup or variable could be examined.

Continue when the next analysis is necessary to:

- answer the current question;
- test a plausible explanation raised by the evidence;
- challenge the robustness of an important finding;
- resolve a material limitation.

Otherwise record the follow-up as possible future work and stop.

---

## 38. Keep exploration and publication distinct

The research notebook may contain:

- dead ends;
- competing definitions;
- diagnostics;
- unsuccessful hypotheses;
- robustness checks.

The reader-facing article does not need to reproduce all of them.

Publication should present the evidence necessary to understand and scrutinise the conclusion while the notebook preserves the fuller research path.

Do not simplify the research merely to make the eventual article easier to write.

---

## 39. Reader relevance is separate from statistical interest

A statistically real pattern may still not justify publication.

At closeout ask whether the result:

- changes understanding;
- usefully quantifies something readers care about;
- challenges or qualifies received wisdom;
- reveals an important methodological issue;
- provides practical context unavailable from ordinary racecards or commentary.

A study can be analytically successful without producing a standalone article.

---

## 40. Do not force every study into an article

A study may conclude that:

- the source cannot answer the question reliably;
- the effect is unimportant;
- the proposed concept cannot be measured satisfactorily;
- more data is required;
- the finding duplicates something already well established without adding useful insight.

In those cases the correct outcome may be to document the research and not publish a standalone article.

Publication is an outcome of worthwhile evidence, not the justification for manufacturing a story.

---

## 41. Record decisions while they are fresh

When an analytical choice could materially affect the conclusion, record:

- what was decided;
- why;
- what alternatives were considered;
- what evidence supported the decision;
- whether the decision should become a reusable project rule.

Do not rely on remembering the rationale during article writing weeks later.

---

## 42. Trace every published claim to analytical evidence

Every published chart, table and headline number should be traceable to a specific saved analytical output or reproducible notebook result.

Prefer the chain:

> governed data -> study analysis -> saved publication output -> published claim

Avoid manually retyping analytical numbers into publication drafts where a reproducible export can be used instead.

This protects against transcription errors and makes later corrections easier.

---

## 43. Provide a compact methodology trail

Every published study should provide, either in the article or a linked technical note, enough information for a sceptical reader to understand:

- study population;
- period;
- important definitions;
- material exclusions;
- principal transformations;
- data source boundary;
- known limitations.

The main article should remain readable, but methodological transparency must always be available.

---

## 44. Preserve external claims and provenance

When testing received wisdom, journalism, books, rules, weather records or other external evidence, preserve the exact claim being tested and its provenance where practicable.

Prefer a specific attributable claim to vague formulations such as "people say".

Record material details such as:

- source;
- author or organisation where relevant;
- publication date;
- exact claim or faithful bounded paraphrase;
- stable locator;
- access date where appropriate.

Follow the project's manual-verification and provenance rules where external evidence affects governed data or a bounded analytical decision.

---

## 45. Use internal claim-strength labels

Before publication, classify major conclusions according to the evidence supporting them.

Useful categories may include:

- descriptive finding;
- robust association;
- exploratory association;
- methodological finding;
- unsupported or inconclusive.

Publication language must not become stronger than the internal evidence classification warrants.

---

## 46. Separate analytical and editorial decisions

The research determines what the evidence supports.

Editorial work determines how to explain it clearly and engagingly.

Do not allow considerations such as:

- a stronger headline;
- a cleaner narrative;
- a more dramatic visual;
- expected social-media engagement;

to feed back into which analytical result is treated as primary.

---

## 47. Distinguish analytical completion from publication readiness

A study can be analytically complete while still requiring:

- better explanation;
- publication-quality figures;
- external context;
- source or legal review;
- article editing.

Likewise, a polished article draft does not prove that the underlying study is analytically complete.

Track these as separate states.

---

## 48. Use fair comparisons

Before comparing groups, establish that the comparison is analytically meaningful.

Apparently similar populations may differ systematically in:

- race type;
- period;
- code;
- class;
- field size;
- price distribution;
- other relevant composition.

Do not imply that a raw difference represents the variable named in the headline when the comparison groups differ materially in other ways.

---

## 49. Be cautious with named entities and rankings

Claims about individual courses, trainers, jockeys, owners or other named entities can be especially vulnerable to small samples and noisy extremes.

Before publication consider:

- minimum sample size;
- uncertainty;
- temporal stability;
- multiple-comparison effects;
- whether the result is materially different from the broader population.

Rankings such as "best", "worst", "top 10" or "most unpredictable" require stronger safeguards than ordinary descriptive tables.

Do not turn noise into a reputational claim about a person or venue.

---

## 50. Every visual must answer a question

Do not create graphs merely because the data permits them.

For every analytical visual, be able to state what question it answers and why the visual communicates the evidence better than prose or a small table.

Prefer the simplest visual that carries the evidence.

---

## 51. Distinguish visual roles

Published visuals can serve different purposes.

### Evidence visual

A chart, table or data graphic that directly supports an analytical claim.

### Explanatory visual

An annotation, diagram or racecard-style explanation that helps the reader understand a concept or measure.

### Editorial image

A photograph or illustration used for context, atmosphere or visual interest.

Editorial images must not be presented as though they constitute analytical evidence.

---

## 52. Graphs are part of the argument, not decoration

The text should explain the analytical point revealed by a graph rather than merely reciting every plotted number.

Visual prominence should broadly reflect evidential importance.

Do not make a weak secondary result the dominant visual simply because it looks dramatic.

---

## 53. Do not create visual exaggeration

Never create a visual whose emotional impression materially overstates the magnitude of the evidence.

Avoid:

- unjustified truncated axes;
- disproportionate shapes or areas;
- selective ranges chosen to exaggerate change;
- oversized before-and-after treatment for tiny effects;
- decorative effects that imply more certainty than exists.

Where a non-zero axis or restricted range is analytically appropriate, make it clear and defensible.

---

## 54. Keep visual definitions consistent

If a measure or category is defined one way in an article, do not quietly redefine it in later figures.

Where a visual intentionally uses a different population or definition, state that difference clearly.

---

## 55. Make charts understandable when detached from the article

Charts may be screenshotted, shared or quoted without the surrounding text.

Where practical, a publication chart should contain enough context through its title, subtitle, labels, caption or source note to avoid becoming seriously misleading when viewed alone.

---

## 56. Use captions as analytical metadata

A useful chart caption should include enough of the following to understand the evidence:

- population;
- period;
- measure;
- material exclusion;
- source or methodology note where necessary.

Do not overload every chart, but do not rely on nearby prose for facts essential to interpreting it correctly.

---

## 57. Keep underlying publication data reproducible

Publication figures should be generated from saved analytical outputs rather than manually reconstructed values.

Export small figure or table datasets where useful so the exact plotted values can be regenerated and reviewed.

Presentation changes such as typography, annotation and layout are acceptable, but the underlying evidence must remain reproducible.

---

## 58. Do not sacrifice analytical honesty for a cleaner graphic

Do not remove awkward categories, uncertainty, missing-data information or inconvenient exceptions merely because the resulting figure looks better.

If an element materially changes interpretation, it belongs in the evidence or its accompanying explanation.

---

## 59. Let the evidence determine the publication asset set

Do not require every article to contain an arbitrary number of charts or a predetermined hero statistic.

After the research is complete, consider producing a publication asset pack containing only what the evidence justifies, such as:

- hero or editorial image concept;
- principal chart or charts;
- supporting figures where useful;
- a small evidence table;
- a defensible pull-out statistic;
- chart captions;
- exported figure data;
- source or methodology note;
- social-media visual where appropriate.

One excellent chart may be better than six mediocre ones.

---

## 60. Do not pretend a finding is more surprising than it is

If the evidence confirms something experienced racing readers already broadly understand, it can still be valuable if the study:

- quantifies the effect properly;
- shows where it does and does not hold;
- explains the mechanism more clearly;
- reveals limits or exceptions;
- provides transparent evidence that was previously difficult to verify.

Do not manufacture shock or novelty merely to create a stronger article hook.

---

## 61. Headlines must not overstate the evidence

Headline compression is unavoidable, but the headline must remain faithful to the actual result.

Do not convert a qualified finding into a categorical one merely because it is more clickable.

If the study says an apparent difference is largely explained by market price, the headline must not imply that the raw difference itself proves a distinct betting effect.

---

## 62. Prefer results that survive attempts to disprove them

Once an interesting result appears, ask:

> What reasonable test could make this result disappear?

Prefer findings that survive sensible challenges over findings supported only by additional demonstrations of the same relationship.

Potential challenges include:

- alternate definitions;
- different periods;
- removal of influential subgroups;
- composition checks;
- market expectation;
- missing-data sensitivity;
- replication.

The aim is not to attack every result indefinitely, but to test important findings against plausible failure modes.

---

## 63. Revisit previous studies when later work may affect them

Whenever later database work, new evidence, corrected semantics or a methodological lesson could materially change an earlier study, record the affected study immediately in `docs/STUDY_REVISIT_REGISTER.md`.

Do not rely on memory.

Not every upstream change requires a complete rerun. First assess whether the earlier study or publication is materially affected.

Database and governance closeout should ask:

> Could this change affect any completed study?

Study closeout should ask:

> Has anything discovered here created a reason to revisit an earlier study?

---

## 64. Correct published work transparently

If later evidence materially changes a published conclusion, correct the publication clearly rather than silently rewriting analytical history.

Depending on severity, the appropriate action may be:

- update note;
- correction;
- revised article;
- superseded study;
- withdrawal.

Minor wording, formatting or typographical changes do not require the same treatment as material analytical changes.

Preserve enough version history to establish what changed and why.

---

## 65. Finish with a bounded conclusion

Every completed study should state:

- the question;
- the population studied;
- the principal finding;
- the magnitude of the effect;
- confidence and uncertainty;
- important limitations;
- what the evidence supports;
- what the evidence does not support;
- whether further investigation is justified.

Do not extend the study indefinitely merely because another possible analysis exists.

---

## 66. Maintain a study manifest at closeout

Each completed study should preserve enough metadata to identify the exact analytical state that produced its conclusions and publication assets.

Where practical record:

- study identifier and notebook path;
- study status;
- source or database version;
- relevant repository commit;
- generated analytical outputs;
- publication figures and tables;
- publication status or article link when applicable;
- dependencies on governed references;
- outstanding revisit entries.

The exact durable format can evolve as the study series develops, but traceability should not depend on memory.

---

## 67. Update this playbook after each study

During study closeout, ask:

- What assumption did we make that turned out to be wrong?
- What analytical step was unnecessary?
- What mistake could recur?
- What method worked particularly well?
- What new safeguard should become standard?
- What should we do differently at the start of the next study?

Add only lessons with genuine cross-study value.

The goal is cumulative methodological improvement, not an ever-growing diary.

---

## 68. Comment substantive notebook code for analytical readability

Study notebooks are part of the research record, not disposable scratch code.

Substantive analytical code cells must contain concise comments wherever they help a later reader understand the reasoning or audit the population. In particular, comment:

- why a database, table, view or governed helper is being used;
- population-changing filters and exclusions;
- joins and the intended join grain;
- assertions that protect a research invariant;
- non-obvious transformations or derived measures;
- steps where the analytical unit changes, such as runner rows becoming race-level observations;
- choices that would otherwise be difficult to reconstruct from code alone.

Comments should explain **why a step exists or what analytical safeguard it provides**, not merely translate obvious Python syntax into English.

Do not clutter cells by commenting every import, assignment or self-explanatory line. The goal is readable, auditable research code rather than maximum comment density.

Where a code cell changes the study population or implements a material analytical decision, a reader should not need to reverse-engineer that decision from the code.

---

## 69. Interpret each analytical output before moving on

Do not move directly from one analytical output to the next question.

After each substantive analytical result:

1. inspect the output before writing further analysis;
2. add a concise notebook explanation of what the result establishes;
3. state what the result does **not** yet establish where that distinction matters;
4. keep important denominators, sample sizes, anomalies and uncertainty visible;
5. decide whether a chart or other visual would materially improve understanding;
6. if a visual is useful, create the simplest appropriate visual before moving on;
7. only then decide what analytical question follows from the evidence.

Do not accumulate a sequence of unexplained tables and charts and reconstruct the narrative retrospectively at the end of the study.

A chart is not mandatory after every table. Use one when it makes the distribution, comparison, trend or relationship materially easier to understand. Where a small table or prose communicates the evidence better, do not create a chart merely for decoration.

The notebook should therefore preserve the research rhythm:

> question -> analysis -> result -> explanation -> appropriate visual -> next question

This keeps the analytical reasoning visible and helps ensure that later questions respond to the evidence rather than to a predetermined story.

---

## 70. Annotate exploratory notebooks as a durable research record

Exploratory data analysis still drives the study and may eventually drive the published story. The notebook must therefore preserve enough context that a later reader can reopen it and understand what the researchers were talking about, what they were doing, and why the study changed direction.

For each substantive analytical stage, use Markdown to record the research reasoning around the code and output. Where applicable, make the following explicit:

- **Question** — what is being established at this point;
- **Why this matters** — why the question is necessary for the wider study;
- **Evidence / method** — the source, database view, population, definitions, exclusions or calculation being used;
- **What we found** — a plain-English account of the material result, with important counts or denominators visible;
- **Interpretation** — what the evidence reasonably supports;
- **What this does not establish** — claims that remain unsupported or questions still unresolved;
- **Data or definition issues** — anomalies, ambiguity, missingness, provenance questions or possible governance problems;
- **Next question** — why the observed evidence motivates the next analytical step.

These headings are a working pattern, not a requirement to repeat every heading mechanically when one or more would add no value. The requirement is that the reasoning trail remains explicit and recoverable.

Preserve material dead ends, surprises and changes of direction. Do not clean the notebook so aggressively that later readers cannot tell how the evidence actually led to the eventual conclusion or publication story.

Use Markdown for **research reasoning** and code comments for **implementation reasoning**. Markdown should explain what is being asked, learned and inferred; code comments should explain how the analytical step is implemented, why a safeguard exists, and what could fail.

A notebook should be understandable as a research record even months later, without relying on memory or on the eventual article to reconstruct its purpose.

---

## 71. Default to the governed course-local race time

When a study displays, orders or refers to a race by time, use the governed **course-local advertised/scheduled time** by default.

For Database v3 race-level work, the normal field is:

`advertised_start_course_local`

Present it to a human as an ordinary local clock time such as `15:05` unless the date, offset or full timestamp is materially relevant to the question.

Do not use raw source `off`, UK-facing time or UTC merely because those fields are convenient or already present in a dataframe.

Use another representation only when the research question specifically requires it, for example:

- investigating source `off` semantics or encoding;
- comparing UK-facing and course-local scheduling;
- timezone or daylight-saving analysis;
- UTC reconciliation;
- source-lineage or debugging work.

Raw `off` remains preserved source evidence and must not be mistaken for the preferred study-facing race-time display.

Externally reported actual-off observations are a separate concept and must not be substituted for advertised/scheduled time unless the study explicitly asks about actual off times.

---

## Current study-series rules

Study notebooks live separately from database-construction notebooks under:

`studies/`

The database notebooks establish what the source means and what transformations are governed.

The study notebooks use those governed foundations to investigate racing questions.

The two activities should remain conceptually separate even when a study exposes a new data-governance question.

Before beginning a new study, read at minimum:

- `docs/STUDY_RESEARCH_PLAYBOOK.md`;
- the relevant existing field-governance and database documentation for fields used by the study;
- `docs/STUDY_REVISIT_REGISTER.md` for any unresolved dependency or known impact relevant to the proposed work.

The current database release state must also be checked before selecting the study's analytical data source. A validated candidate must not be silently treated as an accepted live release.