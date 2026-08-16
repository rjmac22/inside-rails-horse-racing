# Great Britain Studies 01–05 — primary-source retrospective audit

Audit date: 16 August 2026

Governance rule applied:

`docs/PRIMARY_SOURCE_FIRST_RESEARCH_RULE.md`

## Purpose

This audit asks whether the completed and current Great Britain conceptual studies establish sporting and administrative meaning from suitable primary official evidence before relying on Inside Rails or other third-party representations.

It does **not** assume that a study is invalid merely because its discovery process began in the database. The question is whether each material conclusion is adequately grounded before it is treated as publication-ready.

Audit statuses:

- `primary-grounded`
- `primary-grounded before conclusion`
- `targeted revalidation required`
- `reopen`

---

## Study 01 — Governance and structure

Notebook:

`studies/jurisdictions/great_britain/01_governance_and_structure.ipynb`

### Status

**targeted revalidation required**

### What remains valid

Study 01's database-native descriptive findings remain legitimate as statements about the observed Inside Rails Great Britain population, including counts and distributions such as:

- 111,634 governed GB race occurrences in the accepted population used by later studies;
- course-date analytical grouping counts;
- card-size distributions;
- racing-day distributions.

These are database observations and do not require BHA to tell us what the database contains.

### What needs qualification / primary grounding

Study 01 predates the later conceptual distinction established in Study 04 between an analytical `date + racecourse` grouping and an official BHA fixture/meeting entity.

Any Study 01 wording that presents the course-date grouping as a real official `meeting`, rather than an analytical grouping, must be treated as superseded by Study 04.

Likewise, a statement such as:

> the database contains 111,634 GB race occurrences

is supported internally.

A stronger statement such as:

> Great Britain staged exactly 111,634 races in the period

requires official population-completeness evidence. The later BHA reconciliation work strengthens confidence but does not automatically convert every old database count into an official-population claim.

### Required action before publication

- retain numerical findings when explicitly labelled as Inside Rails / observed-population results;
- cross-reference Study 04 for the meaning of `fixture` and `meeting`;
- remove or qualify any wording that treats `date + racecourse` as official fixture identity;
- do not claim complete official GB population coverage without the relevant official completeness evidence.

No wholesale rerun is required for the descriptive counts solely because of this governance change.

---

## Study 02 — Types of British racing

Notebook:

`studies/jurisdictions/great_britain/02_types_of_british_racing.ipynb`

### Status

**targeted revalidation required**

### What remains valid

The study explicitly says that the Flat / Jump structure should not be assumed merely because labels appear in the database. Its observed population counts remain valid as statements about the governed study classification:

- Flat: 70,208;
- Hurdle: 22,653;
- Chase: 15,664;
- NH Flat: 3,109.

The derived analytical grouping Flat versus Jump is also reproducible from those governed labels.

### Primary-source gap

The committed notebook states that recognised British racing terminology should be established first, but its main evidence chain does not preserve the same explicit BHA-primary documentation standard later achieved in Study 04.

Before publication, the following conceptual claims should be re-established directly from BHA primary material / structured BHA data:

- British racing's broad Flat versus Jump structure;
- Hurdle and Chase as Jump forms;
- National Hunt Flat as part of the Jump programme despite being run without obstacles;
- the distinction between BHA's broad structured race criterion (`FLAT` / `JUMP`) and the finer Hurdle / Chase / NH Flat subtype representation used by Inside Rails.

The current BHA API discovery is particularly useful because `raceCriteriaRaceType` supplies an official structured broad category against which the Inside Rails classification can be checked.

### Separate technical debt

Study 02 uses the historical post-v3 overlay helper, whose exact source identity mechanism includes the old source off-time key. That is a technical implementation issue separate from this primary-source audit.

Do not carry that mechanism into Study 05 or use it as a reason to define sporting concepts from the third-party source.

### Required action before publication

- add a bounded BHA-primary evidence note for the conceptual hierarchy;
- distinguish official BHA broad category from Inside Rails finer subtype classification;
- retain the population counts as Inside Rails analytical results;
- do not rewrite the historical discovery path; simply ensure the final conclusion is primary-grounded.

A complete Study 02 rebuild is not currently required.

---

## Study 03 — British racecourse and course identity

Notebook:

`studies/jurisdictions/great_britain/03_british_racecourse_and_course_identity.ipynb`

Supporting evidence:

61 individual racecourse notebooks under:

`studies/jurisdictions/great_britain/racecourses/`

### Status

**primary-grounded before conclusion**

### Why

Study 03 is already built around evidence notebooks with explicit assertion-level provenance. The national consolidation requires source authority, source title, source URL and access date, and retains unresolved questions rather than inventing precision.

Important identity corrections were grounded in first-hand official/operator evidence. A clear example is Newmarket, where Jockey Club evidence establishes Rowley Mile and July Course as separate racecourses rather than allowing Source Version 1 labels to define the sporting entity.

This is closely aligned with the new standing rule.

### Required audit action

Before reader publication, perform a lightweight provenance classification across the material claims in the 61 evidence notebooks:

- primary official/regulator/operator evidence;
- secondary corroboration;
- unresolved.

Secondary sources may remain useful for historical or descriptive detail where no suitable primary source exists, but they should not be the sole basis for a material racecourse/course identity claim when a direct official authority is available.

### Conclusion

No wholesale reopening of Study 03 is justified by the new rule. Its method is already substantially primary-source-led and provenance-preserving.

---

## Study 04 — Race meetings and fixtures

Notebook:

`studies/jurisdictions/great_britain/04_race_meetings_and_fixtures.ipynb`

### Status

**primary-grounded**

### Why

Study 04 is the clearest existing model for the new standing rule.

Its opening method explicitly states:

1. establish BHA usage of `fixture` and `meeting`;
2. determine whether the concepts are equivalent;
3. only then investigate representation in Inside Rails data.

Its evidence notes use BHA primary material including:

- BHA General Instructions / Race Programming Policy;
- BHA fixture-list amendment material;
- BHA fixture-transfer releases;
- BHA additional-fixture material.

The study reaches the fixture/meeting distinction before constructing any database-derived identity.

### Conclusion

No primary-source remediation is required.

Study 04 should be treated as the template for future British conceptual studies.

---

## Study 05 — What is a British horse race?

Notebook:

`studies/jurisdictions/great_britain/05_what_is_a_british_horse_race.ipynb`

### Status

**primary-grounded before conclusion — current study requires narrative/source-order cleanup before closeout**

### What is already correct

The committed study design explicitly states:

> authoritative British racing terminology first, then test how those concepts are represented in Inside Rails data.

It identifies BHA Rules, official glossary, handicapping guidance and official race/programme material as the starting evidence set.

The study has also begun using the BHA structured API directly for concrete race representation, including fields such as:

- `raceCriteriaRaceType`;
- `raceClass`;
- `ratingBand`;
- `ageLimit`;
- `sexLimit`;
- `raceTime`.

This is the correct direction.

### Where the live exploration drifted

Some sub-investigations moved too quickly from Inside Rails fields into interpretation before the complete official rule/context had been established.

The age work exposed why this matters:

- `age_band_raw` matched BHA `ageLimit` text extremely well;
- a literal runner-age versus age-band test then produced 27 apparent breaches;
- 26 were Southern Hemisphere horses exactly one year below the literal minimum;
- the remaining case was Millies Kiss, the documented wrong-horse incident;
- primary BHA/international rule context was required to distinguish apparent representation differences from a genuine realised-field breach.

The rating-band work showed the same general lesson:

- source `0-X` notation cannot safely be assumed to be the formal BHA programmed rating band;
- direct BHA structured `ratingBand` is the appropriate official reference;
- commercial presentation can differ from the formal BHA representation.

### Required closeout action

Before Study 05 closes:

- make the final notebook narrative follow the evidence order `BHA meaning → BHA structured representation → Inside Rails comparison → population test → exception investigation`;
- retain exploratory history where useful, but do not present database-driven inference as the authority for the final concept;
- distinguish BHA race-level conditions from runner/source display conventions;
- use BHA `raceTime` / governed `advertised_start_course_local` and durable `source_race_occurrence_code` for Study 05 identity/matching work;
- do not introduce the legacy source off-time identity route into new Study 05 analysis;
- continue with sex restriction using BHA rules and BHA `sexLimit` before inspecting Inside Rails `sex_rest_raw`.

### Conclusion

Study 05 does not need to restart. The new rule formalises the method it was already moving toward and explains why the official-first ordering matters.

---

# Cross-study audit result

| Study | Status | Required response |
|---|---|---|
| 01 — Governance and structure | targeted revalidation required | qualify analytical meeting terminology and official-population claims |
| 02 — Types of British racing | targeted revalidation required | add explicit BHA-primary grounding for racing hierarchy |
| 03 — Racecourse/course identity | primary-grounded before conclusion | lightweight provenance-type spot audit only |
| 04 — Meeting/fixture | primary-grounded | no remediation |
| 05 — British horse race | primary-grounded before conclusion | clean final evidence order; continue BHA-first |

No study is currently classified `reopen` solely because of the primary-source-first rule.

---

# Programme-level actions

1. Treat `docs/PRIMARY_SOURCE_FIRST_RESEARCH_RULE.md` as mandatory for all new research.
2. Use Study 04 as the model sequence for conceptual studies.
3. Complete the small Study 01 and Study 02 primary-source remediation before either is used as a reader-facing authority.
4. Spot-audit Study 03 provenance rather than rebuilding the 61 notebooks.
5. Finish Study 05 under the new hierarchy.
6. Audit future pre-existing studies at publication-selection time using the same four statuses.
7. Correct stale documentation that still identifies Database v3 as the current accepted study database; Database v4 is the accepted release as of 12 August 2026.

This audit concerns **source authority and semantic order**. It does not replace existing database validation, implementation, provenance, completeness or closeout audits.
