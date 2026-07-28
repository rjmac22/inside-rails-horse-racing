# Race Identity Database Integration

## Governing source

Notebook 03 and `docs/REPORT_03_RACE_IDENTITY_AND_SOURCE_KEY_RECONSTRUCTION.md` established the current source-matching rules.

## Identity rules

Candidate race matching uses the exact raw values:

`date + course + off`

`race_name` is retained as a required validation attribute. It is not part of the leading candidate match because no current source slot contains multiple race names, but a future collision must fail validation rather than be silently merged.

Candidate source runner-record matching uses:

`date + course + off + horse`

This identifies a source runner row in the current extract. It is not a permanent horse entity key.

## Values that are not keys

- `race_id` is a non-unique source reference.
- `date + race_id` is also non-unique.
- `num` is a racecard or betting-entry attribute and may be shared by multiple horses.
- SQLite `rowid` is source lineage for one immutable extract, not a cross-snapshot identity.
- Physical row adjacency must not define race membership.

## Raw ingestion

The raw layer must preserve:

- source product or dataset identity;
- source database/file identity and version;
- source table name;
- original SQLite `rowid`;
- raw `race_id` and `num`;
- raw `date`, `course`, `off`, `race_name` and `horse`;
- every other source field unchanged.

The header row remains excluded through the governed source predicate.

## Staging structure

A staging implementation should create at least:

### `stg_race`

- `staging_race_id` — independent surrogate primary key;
- raw candidate identity columns: `date`, `course`, `off`;
- `race_name` validation attribute;
- retained source race references where useful, without uniqueness;
- source snapshot/version lineage.

A uniqueness constraint may be applied to the candidate race columns only within a specific governed source snapshot after validation has passed. It must not be treated as an eternal business key across providers or corrected snapshots.

### `stg_runner_record`

- `staging_runner_record_id` — independent surrogate primary key;
- foreign key to `stg_race.staging_race_id`;
- raw `horse`;
- raw `num` and `race_id`;
- source row lineage;
- all remaining raw runner attributes.

Within a validated source snapshot, the candidate race identity plus raw `horse` must reconcile one-to-one with source runner rows.

## Stable surrogate handling

Surrogate identifiers should be assigned by the staging database, not derived by concatenating descriptive text. Reprocessing the same immutable source snapshot should use lineage and candidate matching to avoid duplicate inserts.

Across a replacement source snapshot:

1. ingest into a new raw snapshot partition;
2. rerun `scripts/validate_race_identity.py` before merging;
3. compare candidate identities and validation attributes with the previous snapshot;
4. treat changed off-times, course labels, race names or horse names as possible corrections, not automatically as new entities;
5. preserve both source versions and record the reconciliation decision;
6. never overwrite old raw lineage.

## Failure policy

The staging load must stop or quarantine records when any of these occur:

- a null candidate identity component;
- more than one `race_name` within a candidate race slot;
- more than one source runner row for candidate race identity plus `horse`;
- a candidate race linked to more than one supplied `race_id` without explicit review;
- unexpected changes in the source-wide reconciliation totals.

Reuse of `race_id`, collision of `date + race_id`, or sharing of `num` are expected source behaviours and must not be treated as primary-key violations.

## Validation commands

Synthetic governed rules:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_race_identity.py
```

Current source reconciliation:

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_race_identity.py \
  data/raw/form_2015-present/form_2015-present/raceform.db
```

The expected totals are tied to the current immutable extract. A replacement snapshot requires reviewed expectation changes, not silent edits.
