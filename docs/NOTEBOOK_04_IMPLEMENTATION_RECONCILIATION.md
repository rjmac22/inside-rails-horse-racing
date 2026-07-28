# Notebook 04 Implementation Reconciliation

## Conclusion

Notebook 04 contained two different implementation concerns:

1. course-label and candidate-jurisdiction reconstruction;
2. source-supported race-surface derivation.

They now have separate durable owners.

## Jurisdiction and course identity

Notebook 04's candidate jurisdiction and course-label logic is retained in:

- `src/inside_rails/course_jurisdiction.py`;
- `scripts/validate_course_jurisdiction.py`.

Notebook 09 later tested the broader jurisdiction, authority and betting-market context and is the semantic owner of candidate jurisdiction interpretation.

Notebook 12 later produced the permanent governed course-location and timezone reference:

- `data/reference/course_locations.csv`;
- `src/inside_rails/course_locations.py`;
- `scripts/validate_course_locations.py`.

The Notebook 04 count of 395 candidate venue/configuration identities and the Notebook 12 count of 394 permanent course identities must not be treated as contradictory interchangeable totals. Notebook 04 measured provisional text-derived venue/configuration identities. Notebook 12 created a curated permanent reference after later resolution work. The permanent reference is authoritative for location and timezone enrichment; the Notebook 04 mapping remains useful for reconstructing candidate labels and jurisdiction evidence from raw source rows.

## Surface

Notebook 04 established only one deterministic source-supported surface rule:

- if the exact raw course value contains `(AW)`, assign `all_weather_unspecified` with explicit-course-marker evidence;
- otherwise leave surface unresolved.

The source does not justify deriving turf, dirt, synthetic subtype or a canonical surface from `race_name`.

This rule is now implemented in:

- `src/inside_rails/race_surface.py`;
- `tests/test_race_surface.py`;
- `scripts/validate_race_surface.py`.

The current source reconciliation target is:

- 189,043 provisional races;
- 33,023 explicit all-weather races;
- 156,020 unresolved surface races;
- 528 raw course values.

## Database consequence

A staging race record should preserve:

- `raw_course`;
- candidate course label and jurisdiction plus their evidence;
- `candidate_surface`;
- `surface_evidence`;
- any later externally enriched surface in separate fields with source and version metadata.

External surface enrichment must not overwrite the source-supported result. It should be attached as a separate, versioned assertion.

## Update path

For every replacement source snapshot:

1. rerun the course-jurisdiction validator;
2. rerun the race-surface validator;
3. compare candidate identities with the permanent course reference;
4. preserve newly unresolved or colliding values for review;
5. never broaden surface inference from names without a separately governed investigation.

## NH Flat conflicts

Notebook 04 recorded eight explicit NH Flat/type conflicts. These are retained as source anomalies and are not part of the surface parser. Their final treatment belongs to race-type/classification governance rather than course surface reconstruction.

## Closure

Notebook 04 can be considered fully closed once the new surface tests and independent validator pass locally. Its jurisdiction findings are explicitly superseded semantically by Notebooks 09 and 12 where appropriate, without deleting the reusable raw-to-candidate mapping logic.
