# Inside Rails Horse Racing Project — Lessons Learned

## Purpose

This document records the reusable lessons from the Inside Rails horse-racing data and writing project.

The project is not a database-building exercise for its own sake. Its purpose is to understand what racing data actually means, test claims responsibly, preserve uncertainty, create reusable analytical infrastructure, and turn the findings into readable work.

The central principle is:

> Do not ask what the database says until you have established what the database means.

---

## 1. Keep the project purpose explicit

The project is intended to:

- test claims from racing books, journalism, betting culture and received wisdom;
- expose hidden assumptions in apparently simple fields;
- build defensible analytical foundations;
- produce useful writing rather than endless notebooks;
- identify narrow, neglected situations where careful analysis may reveal value;
- develop transferable research and data skills.

Whenever scope expands, ask:

> Does this work improve reliability, answer a defined research question, or support a piece of writing?

If not, it may be database hobbyism rather than project work.

---

## 2. Start with the writing question, not the dataset

A better workflow is:

1. Identify a claim worth investigating.
2. Define what would count as evidence.
3. Determine whether the source can support that evidence.
4. Audit only the fields needed.
5. Build only the infrastructure required.
6. Write the conclusion with uncertainty intact.

This is stronger than asking what can be analysed merely because the data exists.

---

## 3. Treat source data as an argument, not as truth

The source database contains important structural and semantic problems, including:

- reused `race_id` values;
- inconsistent field meanings;
- mixed jurisdictions and racing codes;
- ambiguous runner numbers;
- inconsistent result encodings;
- source rows below declared runner counts;
- selective starting-price coverage;
- course labels requiring jurisdiction context;
- off-times that cannot be interpreted safely without timezone work.

The working rule is:

> Every field is provisional until its semantics, coverage and failure modes have been investigated.

Large datasets can still be badly designed. Volume does not create meaning.

---

## 4. Field names are not definitions

A field called `off`, `ran`, `num`, `pos`, `sp`, `weight` or `race_id` does not prove what it means.

Important fields should be investigated through:

- distinct-value profiling;
- null and blank coverage;
- range checks;
- cross-field consistency;
- jurisdiction comparisons;
- temporal comparisons;
- edge-case inspection;
- physical source lineage;
- checks against real-world conventions.

Field references should preserve raw meaning, candidate meaning, confirmed meaning, exceptions, jurisdiction dependence, confidence and transformation rules.

---

## 5. Reconstruct identity before analysis

The supplied `race_id` could not safely serve as a unique race key.

A provisional race identity was instead developed from date, course and off time, with race name retained as validating evidence. Runner identity was based on reconstructed race identity plus horse label.

General lessons:

- never assume a supplied identifier is unique;
- test uniqueness across the full source;
- distinguish natural identity from surrogate identity;
- retain original identifiers for lineage;
- preserve source database, table and row identifiers.

---

## 6. Preserve lineage even when the source is wrong

Do not discard unreliable source fields silently.

Preserve:

- source database;
- source table;
- source row ID;
- supplied race ID;
- raw field values;
- transformed values;
- transformation method;
- review notes;
- confidence.

Lineage is part of the evidence and makes later correction possible.

---

## 7. Separate raw, canonical and interpreted values

Do not overwrite raw values with cleaned values.

Examples:

- carried weight should preserve the source value, parsed components, total pounds or kilograms, jurisdiction convention and parsing status;
- finishing position should preserve the raw token, numeric placing, non-completion code, disqualification status and unknown cases.

Canonicalisation should improve comparability without erasing the original evidence.

---

## 8. Jurisdiction matters everywhere

The same-looking field may mean different things in different countries.

This applies to:

- weight units;
- runner numbers;
- starting prices;
- time formats;
- daylight-saving rules;
- race classifications;
- result codes;
- field completeness.

Global transformation rules should not be built until jurisdiction variation has been checked. Jurisdiction policy should be stored explicitly as data rather than hidden in notebook logic.

---

## 9. Time analysis requires geography first

The off-time work showed that a source time is not analytically usable until we know:

- whether it is local time;
- which course it belongs to;
- which civil timezone applies;
- whether daylight saving is handled correctly;
- whether the course identity is historically stable.

The completed reference now contains:

- 395 permanent course identities;
- 395 valid IANA timezone assignments;
- 0 unresolved;
- 51 distinct IANA timezones.

Assignment methods are preserved as:

- existing resolved course location;
- jurisdiction default;
- manual timezone review;
- manual reference CSV.

The broader lesson is that apparently simple temporal fields often depend on identity, geography and civil-time rules.

---

## 10. Define the minimum required output before building the solution

The timezone task initially drifted toward exact venue geocoding, but the real downstream requirement was only a defensible IANA timezone.

For future tasks, define:

- required output;
- minimum acceptable evidence;
- useful enrichment;
- future research;
- explicitly out-of-scope work.

Optional completeness should not block necessary progress.

---

## 11. Separate identity, location and analytical sufficiency

These are distinct:

- course identity;
- exact venue address;
- coordinates;
- timezone;
- current venue name;
- historical venue name;
- venue status.

A timezone can be defensible even when an exact historical address remains uncertain. Reference tables should keep these concepts separate and record the evidence for each.

---

## 12. Use defaults only where they are genuinely safe

Jurisdiction defaults are appropriate only where one relevant civil timezone safely applies.

They were not appropriate for multi-timezone jurisdictions such as the United States, Australia, Canada and Brazil.

The safe sequence is:

1. classify jurisdictions;
2. document why a default is safe;
3. apply defaults only to the safe group;
4. resolve multi-timezone jurisdictions at course level;
5. validate complete coverage before writing.

---

## 13. Automation should generate candidates, not manufacture certainty

Geocoding produced convincing false positives, including wrong parks, administrative regions, roads containing “Racecourse”, nearby sports facilities and same-name venues in the wrong city.

Examples included Arlington Park, Launceston, Ballarat, Belmont Park, Gulfstream Park and Saratoga.

The correct role of automation was to:

- generate candidates;
- rank likely matches;
- cache raw responses;
- reduce the manual workload.

The final decision still required human review.

General rule:

> Use automation for scale and recall; use manual review for ambiguity and consequence.

---

## 14. Do not overengineer a finite residue set

Once the unresolved timezone set had fallen to 64 courses, direct research was faster and safer than building another alias and scoring layer.

Automate work that is large, repetitive, stable and likely to recur. Review manually when the remaining task is finite, ambiguous and high consequence.

Engineering effort should always be compared with the size of the remaining problem.

---

## 15. Cache external requests from the beginning

External-data notebooks should preserve:

- exact query text;
- provider and parameters;
- raw responses;
- request status;
- cache reuse behaviour.

A failed display or summary cell should never force repeated external calls. Caches are reproducibility infrastructure, not temporary clutter.

---

## 16. Manual research should be ingestible

Manual decisions should not remain as scattered prose.

The manual course-resolution CSV preserved:

- source label;
- jurisdiction;
- race count;
- official venue name;
- address;
- locality and region;
- country;
- IANA timezone;
- venue status;
- alternative names;
- confidence;
- review note;
- source URLs.

When manual review produces a reusable decision, store it in a machine-readable reference file.

---

## 17. Preserve historical and alternative names

Renamed, rebranded and closed venues must retain historical identity.

Examples included Indiana Grand, Penn National, Gulfstream Park West, Northlands Park, Golden Gate Fields, Parx and Thistledown.

Store the source-era name, current name, former names, venue status, historical location and review notes. Do not silently replace the source label.

---

## 18. One-off race meetings need proportionate handling

Not every course label represents a permanent commercial racecourse. Some represent annual steeplechase meetings, estate courses, park courses or historic meetings.

Resolve what is needed now, record provisional identification where appropriate, and revisit detailed history only when that course is studied directly.

Do not block a large project over a one-race edge case when the required analytical field is still defensible.

---

## 19. Notebook design must support fresh-kernel reruns

Avoidable failures came from assumed variables and column names such as `PROJECT_ROOT`, `COURSE_LOCATION_REFERENCE_PATH`, `timezone_policy` and `jurisdiction_default_iana_timezone`. There was also a Boolean-count bug caused by a missing `.sum()`.

Before a notebook is complete:

- define paths explicitly near the start;
- inspect dataframe columns before large merges;
- remove temporary repair cells;
- fix the original failed cell;
- ensure top-to-bottom execution from a fresh kernel;
- ensure request cells use caches;
- reload and validate written outputs.

Exploratory repair is normal. Leaving the notebook dependent on the repair sequence is not.

---

## 20. Use one conceptual stage at a time

The strongest workflow was:

1. explain the stage in markdown;
2. run one cell;
3. inspect the output;
4. decide the next step.

Large speculative cells hide assumptions, are harder to debug and increase the risk of writing bad reference data.

---

## 21. Do not write permanent references prematurely

The timezone reference was not written until all 395 courses had valid assignments and all timezone names passed `ZoneInfo` validation.

The safe persistence sequence is:

1. build preview;
2. inspect exceptions;
3. validate counts and uniqueness;
4. validate values;
5. write once;
6. reload;
7. validate the persisted file.

Permanent references should represent a completed decision state, not an in-progress guess.

---

## 22. Keep evidence paths separate

The same final field may be supported by different evidence.

Resolution metadata should preserve:

- method;
- reason;
- confidence;
- source;
- review status.

This allows weaker assignments to be revisited without rechecking everything.

---

## 23. Coverage statistics must be interpreted carefully

A field can look well populated while still being analytically misleading.

Examples:

- starting prices may cover only leading finishers;
- runner counts may not equal source rows;
- numeric positions may omit non-completions;
- race IDs may be populated but non-unique;
- off-times may be complete but unusable without timezone context.

Always profile row, race, course, temporal and jurisdiction coverage, plus the pattern of missingness.

---

## 24. Strange rows are evidence, not inconvenience

Rows with impossible or unusual-looking combinations should be investigated rather than deleted automatically.

Anomalies can reveal extraction rules, field semantics, jurisdiction conventions, historical changes and vendor shortcuts. Edge cases often teach more than the median row.

---

## 25. Avoid premature “clean data” language

Use explicit statuses such as:

- raw;
- parsed;
- canonical;
- interpreted;
- provisionally resolved;
- manually validated;
- unresolved.

Calling a field “clean” too early creates false confidence.

---

## 26. The source is not analysis-ready

The source appears useful for methodological and exploratory work, but it should not be treated as a turnkey professional database.

It can still support:

- methodological writing;
- source-quality investigation;
- illustrative analysis;
- narrow exploratory studies;
- testing definitions and assumptions;
- skill development.

The distinction between “useful” and “professionally trustworthy” must remain explicit.

---

## 27. Do not publish the bulk source data

The publishing stance should remain:

- publish conclusions;
- publish methodology;
- publish small illustrative tables;
- preserve raw-data lineage privately;
- avoid redistributing the full dataset;
- seek legal advice if publication approaches source-data reproduction.

The value should come from interpretation, not repackaging someone else’s database.

---

## 28. The strongest writing may come from hidden methodological problems

Potential stories include:

- why race IDs cannot be trusted;
- what “off time” means in a global database;
- how starting-price coverage can look complete but be selective;
- why finishing position is not a single numeric field;
- how weight conventions break naive analysis;
- why databases create false precision.

These stories are valuable because readers rarely see the infrastructure beneath racing statistics.

---

## 29. Explain uncertainty without making the work unreadable

A useful article structure is:

1. the interesting claim;
2. the apparent simple answer;
3. the hidden data problem;
4. the evidence;
5. the corrected conclusion;
6. the practical implication.

Technical detail should support the story rather than overwhelm it.

---

## 30. Avoid “get rich quick” positioning

The project should remain informed rather than promotional, sceptical rather than cynical, practical rather than magical, and transparent about uncertainty.

The proposition is not “follow me and win.” It is:

> Understand what the evidence actually says before risking money or repeating racing folklore.

---

## 31. Narrow neglected situations are more plausible than universal systems

If betting value emerges, it is more likely to come from narrow, messy, poorly understood situations than from a universal model covering every race.

Small, boring and well-defined edges are more credible than grand systems.

---

## 32. Separate research conclusions from betting decisions

A statistically interesting pattern does not automatically imply a bet.

A betting decision also requires odds, price sensitivity, sample stability, liquidity, friction, closing-price comparison and bankroll discipline.

The project’s writing and analytical value can exist even when no bet is justified.

---

## 33. Produce a Minto-style report after each investigation

Each completed investigation should produce:

- conclusion;
- supporting evidence;
- confidence;
- limitations;
- practical implications;
- next actions.

This prevents notebooks from becoming piles of outputs without a decision.

---

## 34. Stop when the research question is answered

Completion criteria should be declared in advance.

Examples:

- relevant identities resolved;
- transformations validated;
- known exceptions documented;
- output written and reloaded;
- downstream notebook unblocked.

Further enrichment should become a separate task.

---

## 35. Keep a decision log for major scope changes

Record decisions such as:

- rejecting the source as professionally trustworthy;
- preserving it for lineage and methodological analysis;
- using a book-first writing approach;
- separating exact location from timezone sufficiency;
- applying defaults only where safe;
- using manual review for the unresolved residue;
- not publishing the bulk dataset.

This prevents later notebooks from reopening settled strategic questions without reason.

---

## 36. Build reusable assets, not notebook-only answers

Reusable project assets include:

- permanent course identity reference;
- course-location and timezone reference;
- jurisdiction policy tables;
- manual-resolution references;
- geocoding cache;
- provider-response logs;
- source field-quality profiles;
- transformation modules;
- lineage rules;
- notebook templates;
- Minto report template.

Each notebook should leave behind something reusable where justified.

---

## 37. Move stable code out of notebooks

Exploratory code belongs in notebooks initially. Stable reusable logic should move into modules.

Candidate modules include course identity resolution, result parsing, carried-weight parsing, timezone conversion, reference validation and profiling utilities.

The notebook should show the investigation, not permanently house every implementation detail.

---

## 38. Test modules against observed edge cases

Tests should be built from real anomalies found during profiling, including malformed values, jurisdiction variants, historical variants, sentinels and collision cases.

The field audit should feed the test suite.

---

## 39. Do not let tool-building replace research

Infrastructure is justified when it removes a genuine blocker or will be reused.

Ask:

> After this task, what research question becomes answerable that was not answerable before?

If the answer is unclear, pause.

---

## 40. Time spent is not wasted when it creates method and writing material

The project has produced practical experience with messy real-world data, research discipline, reproducibility habits, source scepticism, technical writing material and reusable methodology.

The payoff is not only a final database.

---

## 41. The project should remain enjoyable, but enjoyment is not a scope rule

The work can justify itself through learning, craft, curiosity, writing and intellectual satisfaction.

But enjoyment should not excuse endless scope. The right balance is enjoyable work, explicit goals, visible outputs, regular completion points and publishable conclusions.

---

## 42. Recommended workflow for future investigations

### Stage 1 — Question

- State the claim.
- Explain why it matters.
- Define the unit of analysis.
- Define what would count as evidence.

### Stage 2 — Source suitability

- Identify required fields.
- Review existing field-audit findings.
- Check coverage and failure modes.
- Decide whether the source can answer the question.

### Stage 3 — Definitions

- Define every important term.
- Specify inclusions and exclusions.
- Record jurisdiction-specific rules.
- Predeclare transformations.

### Stage 4 — Minimal infrastructure

- Build only what is needed.
- Reuse references and modules.
- Cache external data.
- Preserve lineage.

### Stage 5 — Analysis

- Begin with descriptive checks.
- Inspect edge cases.
- Compare alternative definitions.
- Quantify uncertainty.

### Stage 6 — Validation

- Test sensitivity.
- Review anomalies.
- Check temporal and jurisdiction coverage.
- Compare with external references where appropriate.
- Ensure reproducibility.

### Stage 7 — Conclusion

Produce conclusion, evidence, confidence, limitations, practical implication and next action.

### Stage 8 — Persistence

- write reusable references;
- reload and validate;
- move stable code into modules;
- clean temporary cells;
- commit changes.

### Stage 9 — Writing

- turn the finding into a reader-facing story;
- explain the hidden methodological issue;
- use small illustrative tables;
- avoid overstating betting value.

### Stage 10 — Lessons learned discussion

After every notebook, explicitly discuss:

- what took longer or proved harder than expected;
- where scope expanded and whether that was justified;
- which assumptions were wrong;
- what worked well;
- where automation helped;
- where manual review would have been faster;
- which workflow errors should not be repeated;
- which reusable assets were created;
- what should change in future notebooks;
- whether the lesson is notebook-specific or project-wide.

Record the outcome in the notebook wrap-up, this project lessons file, or a permanent workflow/template file.

The notebook is not fully wrapped up until this discussion has happened and reusable lessons have been captured.

---

## 43. Reusable stop rules

Stop and reassess when:

- the task no longer supports a defined research question;
- optional enrichment is blocking a sufficient answer;
- automation is taking longer than manual review;
- the remaining set is small and ambiguous;
- a permanent reference is about to be written with unresolved rows;
- conclusions depend on a field whose meaning has not been established;
- the project is producing infrastructure but no writing or decisions.

---

## 44. Notebook wrap-up procedure

Every notebook should end with:

1. State the final conclusion.
2. Summarise the evidence and confidence.
3. Record limitations and unresolved questions.
4. Confirm which files, references or modules were created or updated.
5. Confirm that outputs were persisted and reloaded successfully.
6. Confirm that the notebook can run top to bottom from a fresh kernel.
7. Remove or clearly mark temporary repair cells.
8. Produce the Minto-style notebook report.
9. Discuss lessons learned from the notebook.
10. Update project-wide lessons, templates or procedures where reusable.
11. State the next action, or explicitly state that no further action is required.

The lessons-learned discussion is mandatory and should identify concrete changes to future behaviour rather than merely saying the task was harder than expected.

---

## 45. Lessons from off-time and temporal reconstruction

Notebook 11 showed that a fully populated clock field can still be semantically incomplete.

The source `off` field contained no blanks and every value looked like a valid time, but its representation changed on 15 October 2025:

- before the boundary, times used a 12-hour clock without AM/PM;
- from the boundary onward, times used explicit 24-hour `HH:MM` notation;
- throughout both periods, the displayed time was UK-facing rather than racecourse-local.

The reusable lessons are:

- detect temporal format changes before normalising values;
- never infer that a source time is local merely because it belongs to an overseas event;
- reconstruct civil time in the source timezone before converting to UTC and then to course-local time;
- use historical IANA timezone rules rather than fixed offsets;
- preserve both candidate interpretations where a 12-hour source omits AM/PM;
- classify ambiguous and nonexistent daylight-saving times explicitly rather than silently coercing them;
- distinguish evening or night racing from an entire meeting placed in the local dead of night;
- treat schedule-based inference as evidence with a method and confidence level, not as source fact;
- test rules against external historical racecards across jurisdictions and edge cases;
- keep unresolved records as a managed evidence backlog instead of forcing complete coverage.

The investigation also exposed a limitation in using recent data as a historical schedule reference. The explicit 24-hour period began in October 2025, so early course profiles underrepresented British and Irish summer evening racing. A course-specific profile could support a branch when the same decision remained stable across several margins, but a profile mismatch could not safely reject both candidates because the reference period was seasonally incomplete.

This led to a useful evidence hierarchy:

1. source-explicit 24-hour time;
2. high-confidence course-local dead-of-night rejection;
3. supported branch selection from a stable course profile;
4. unresolved, with both candidates preserved.

The final temporal population resolved 169,465 of 189,043 races, or 89.64%, while leaving 19,578 unresolved. The important achievement was not nominal completeness but an auditable distinction between explicit, reconstructed and unresolved times.

Workflow lessons from the notebook were equally important:

- row-wise timezone conversion across large dataframes is slow; convert distinct values or use vectorised operations where possible;
- pandas `groupby.apply` can remove grouping columns in version-dependent ways, so reusable logic should not depend on notebook-specific behaviour;
- timezone-aware columns must be created with compatible dtypes rather than initialised as timezone-naive `NaT` columns;
- exploratory notebook logic should be transferred into a reusable module and independently validated before closeout;
- the notebook should preserve the reasoning and evidence, while the module should preserve the repeatable transformation.

Notebook 11 produced `src/inside_rails/race_times.py` and `scripts/validate_race_times.py`. The database build should use those reusable components and store raw values, candidate branches, selected timestamps, decision method, confidence and resolution status separately.

---

## 46. Lessons from prize-money semantics and availability

Notebook 13 showed that a monetary field cannot be understood from its declared SQLite type or apparent numeric value alone.

The source `prize` field contains runner-level recorded prize money, not total race prize money. Its physical representation varies:

- Great Britain uses numeric values that can be parsed directly as GBP;
- Ireland uses euro-prefixed text values that can be parsed directly as EUR;
- other jurisdictions contain source-presented numeric values whose original currency is not safely identifiable from the stored value alone.

External checks showed that at least some foreign prize amounts had been converted before storage. Selected United States and French race schedules could be reconstructed using fixed source multipliers, but those multipliers did not necessarily represent the correct historical market exchange rate.

The reusable data lessons are:

- declared database types do not guarantee consistent physical storage;
- preserve the raw monetary value before parsing or interpreting it;
- store confirmed monetary amounts as integer minor units rather than floating-point numbers;
- assign a currency only where the evidence supports it;
- distinguish direct source amounts from converted or reconstructed amounts;
- retain the conversion method, multiplier, evidence and confidence separately;
- do not convert blank runner values to zero;
- do not label summed runner prizes as the advertised purse or total race value;
- do not assume a fixed number of runners receive recorded prize money;
- defer foreign-currency reconstruction until the relevant jurisdiction and period can be validated.

The investigation also demonstrated the value of anomalies. Nearly all populated United States prize rows from 2018 reconstructed under one source multiplier, while a small Santa Anita batch reconstructed under another. That pattern may indicate a source rate change, processing batch or alternative data route, but explaining it belongs in a separate jurisdiction-level study.

Scope discipline was important. Historical changes in the number of runners with recorded prize money and full foreign-currency reconstruction were both interesting, but neither was required to establish the field's meaning and safe storage. The notebook recorded those questions and stopped rather than allowing them to take over the field audit.

A fresh-kernel rerun exposed a hidden-state dependency: `numeric_prize_rows` existed during exploration but was not created correctly by the saved top-to-bottom notebook sequence. The repair initially recreated the dataframe without `candidate_jurisdiction`, causing a second failure in a later grouping cell.

The reusable workflow lessons are:

- a notebook that works only because variables survive in memory is not reproducible;
- every dataframe must be created in a saved cell before its first use;
- creation cells must include every column required by later merges, groups and summaries;
- repair the original dependency rather than relying on temporary recovery cells;
- restart the kernel and run every cell from top to bottom before declaring completion;
- treat a fresh-kernel failure as a notebook-design fault, not merely an execution inconvenience.

Notebook 13 established a governed treatment for `prize`: direct GBP and EUR parsing where confirmed, exact integer minor-unit storage, null preservation, precise race-level aggregation labels, and explicit unresolved status for foreign source-presented values.

---

## 47. Lessons from runner counts, numbers and entries

Notebook 14 showed that a structurally clean field can still have an unsafe real-world interpretation.

The source `ran` field is unusually consistent:

- all 1,851,285 values are integers between 1 and 40;
- every provisional race carries one consistent `ran` value;
- 189,038 of 189,043 races have stored runner rows equal to `ran`;
- five races have fewer stored rows than `ran`;
- no race has more stored rows than `ran`.

That internal cleanliness does not establish that `ran` is a complete or externally correct starter count. External checks found both:

- races where `ran` remained correct despite missing stored runner rows; and
- races where stored rows equalled `ran`, but the published field was larger.

The reusable lesson is:

> Internal consistency describes source behaviour; it does not prove external completeness or sporting meaning.

`ran` should therefore be preserved as `source_reported_ran`, with separate statuses for:

- within-race consistency;
- stored row count compared with `ran`;
- stored runner coverage; and
- external validation of `ran`.

The source `num` field also looked simpler than it was. It contains three observable raw states:

- positive integer;
- integer zero;
- blank text.

Only positive integers can safely produce a canonical runner number. Blank text and integer zero have different jurisdictional distributions, can coexist within the same race, and must remain distinct source states even though both produce a null canonical runner number.

Positive `num` is not universally unique within a race:

- 523 duplicated positive-number groups occur;
- 362 races are affected;
- 1,084 runner rows are involved;
- up to four horses can share one positive number.

Many duplicated numbers occur in jurisdictions with coupled or bracketed betting entries. However, rare cases outside those jurisdictions did not consistently resemble genuine coupling. A duplicated positive number can therefore indicate:

- a legitimate shared betting interest;
- an ambiguous source-number collision; or
- another source convention.

The field must not be used as a runner key, and duplicated values must not automatically be classified as duplicate runners or confirmed coupled entries.

The candidate natural runner identity remains:

`date + course + off + horse`

No race contains the same horse label more than once, and no horse is assigned multiple positive numbers within the same race.

The investigation produced several broader workflow lessons:

- test apparent identifiers for scope and uniqueness before using them as keys;
- preserve similar-looking empty states separately when the source distinguishes them;
- inspect rare exceptions rather than extending the dominant explanation automatically;
- record rejected analytical screens so plausible but invalid tests are not repeated;
- perform heavy filtering inside SQLite rather than loading the full source into pandas;
- after a kernel restart, rebuild notebook state from the saved cell sequence rather than relying on surviving visible output;
- treat course-reference gaps as reference-maintenance work, not parser logic;
- separate internal source validation from external evidence;
- do not reconstruct information, such as coupled-entry suffixes, that the source no longer preserves.

Notebook 14 established a governed treatment for `ran` and `num`: preserve the source-presented race count, derive explicit consistency and coverage statuses, retain raw runner-number states, canonicalise only positive integers, allow shared positive numbers, and keep runner identity independent of `num`.

---

## 48. Current project position

The project has established that the source cannot be treated as analysis-ready, but it can still support valuable work when identity is reconstructed, fields are audited, jurisdiction differences are respected, raw values are preserved and conclusions remain within the evidence.

The next phase should return to the intended rhythm:

1. choose a claim worth testing;
2. use the completed field work to determine whether it can be tested;
3. perform the narrow investigation;
4. produce a clear report;
5. turn the result into writing.

---

## Final principle

> Identify the exact downstream decision, use the least evidence needed to support it responsibly, preserve uncertainty, and stop when the question is answered.
