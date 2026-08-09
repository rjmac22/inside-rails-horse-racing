"""Build Database v2 race and source-backed runner governed extensions.

Source Version 1 is read from the copied Database v1 raw mirror in bounded race
batches. Each query is fully materialised before writes begin, so the builder
never attempts to commit while a long-running SQLite read cursor is active.
The default 500-race batch is small enough for the project's 8 GB development
machine while avoiding 189,043 one-race SQL round trips.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction
import json
import sqlite3
from typing import Any, Iterable

from inside_rails.beaten_distance import classify_beaten_distance_row
from inside_rails.carried_weight import parse_carried_weight
from inside_rails.comment_information import classify_comment
from inside_rails.course_jurisdiction import (
    derive_candidate_course_label,
    derive_candidate_race_jurisdiction,
)
from inside_rails.jurisdiction_context import resolve_jurisdiction_context
from inside_rails.prize_money import parse_prize_money
from inside_rails.race_classification import (
    classify_sex_restriction,
    parse_age_band,
    parse_class,
    parse_pattern,
    parse_rating_band,
)
from inside_rails.race_distance import parse_race_distance
from inside_rails.race_results import parse_result
from inside_rails.race_surface import derive_source_supported_surface
from inside_rails.ratings import parse_rating_triplet
from inside_rails.runner_characteristics import (
    VERIFIED_SEX_CORRECTIONS,
    normalise_runner_age,
    normalise_runner_sex,
    parse_runner_headgear,
)
from inside_rails.runner_entries import parse_runner_number, profile_reported_ran
from inside_rails.starting_price import StartingPriceKind, parse_starting_price


EXPECTED_RACES = 189_043
EXPECTED_RUNNERS = 1_851_285
RACE_DISTANCE_PARSER_VERSION = "notebook_06_validated_components_v1"
DEFAULT_RACE_BATCH_SIZE = 500

RACE_CONSTANT_FIELDS = (
    "race_name",
    "type",
    "class",
    "pattern",
    "rating_band",
    "age_band",
    "sex_rest",
    "dist",
)

_SOURCE_SELECT = """
SELECT
    race.source_race_occurrence_id,
    race.raw_date,
    race.raw_course,
    race.raw_off,
    race.admitted_runner_count,
    runner.runner_participation_id,
    source.source_record_id,
    source.source_rowid,
    source.race_id,
    source.race_name,
    source.type,
    source.class,
    source.pattern,
    source.rating_band,
    source.age_band,
    source.sex_rest,
    source.dist,
    source.ran,
    source.num,
    source.pos,
    source.ovr_btn,
    source.btn,
    source.horse,
    source.age,
    source.sex,
    source.wgt,
    source.hg,
    source.sp,
    source.jockey,
    source.trainer,
    source.prize,
    source."or",
    source.rpr,
    source.ts,
    source.comment
FROM core_source_race_occurrence AS race
JOIN core_runner_participation AS runner
  ON runner.source_race_occurrence_id = race.source_race_occurrence_id
JOIN source_raceform_v1_record AS source
  ON source.source_record_id = runner.source_record_id
WHERE race.source_race_occurrence_id BETWEEN ? AND ?
ORDER BY race.source_race_occurrence_id, source.source_rowid
"""

_SOURCE_COLUMNS = (
    "source_race_occurrence_id",
    "raw_date",
    "raw_course",
    "raw_off",
    "admitted_runner_count",
    "runner_participation_id",
    "source_record_id",
    "source_rowid",
    "race_id",
    "race_name",
    "type",
    "class",
    "pattern",
    "rating_band",
    "age_band",
    "sex_rest",
    "dist",
    "ran",
    "num",
    "pos",
    "ovr_btn",
    "btn",
    "horse",
    "age",
    "sex",
    "wgt",
    "hg",
    "sp",
    "jockey",
    "trainer",
    "prize",
    "or",
    "rpr",
    "ts",
    "comment",
)

_RACE_INSERT = """
INSERT INTO core_source_race_occurrence_governed (
    source_race_occurrence_id, governance_release_id,
    candidate_course_label, candidate_jurisdiction, jurisdiction_evidence,
    reference_course_id, jurisdiction_context_id, jurisdiction_context_status,
    candidate_surface, surface_evidence,
    raw_dist, distance_miles_component, distance_whole_furlongs_component,
    distance_has_half_furlong, distance_total_furlongs,
    distance_source_implied_yards, distance_source_implied_metres,
    distance_official_verified, distance_parse_status, distance_parser_version,
    source_reported_ran, source_runner_row_count, source_ran_distinct_value_count,
    source_ran_consistency_status, source_row_count_vs_ran_status,
    source_runner_coverage_status, source_ran_external_status,
    source_ran_manual_verification_id,
    race_name_raw, race_type_raw, class_raw, pattern_raw, rating_band_raw,
    age_band_raw, sex_rest_raw,
    class_number, class_parse_status,
    pattern_family, pattern_level_raw, pattern_parse_status,
    rating_lower_bound, rating_upper_bound, rating_band_parse_status,
    stated_minimum_age, stated_maximum_age, age_band_open_ended,
    age_band_syntax, age_band_interpretation_status,
    sex_rest_category, sex_rest_interpretation_status
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""

_RUNNER_INSERT = """
INSERT INTO core_runner_participation_governed (
    runner_participation_id, governance_release_id,
    result_kind, finish_position, outcome_code,
    weight_notation_family, carried_weight_stones,
    carried_weight_remainder_pounds, carried_weight_total_pounds,
    carried_weight_implied_kg, weight_parse_status, weight_ambiguity_flag,
    weight_anomaly_flags_json, official_weight_verified,
    starting_price_kind, starting_price_numerator, starting_price_denominator,
    starting_price_fractional_odds, starting_price_decimal_odds,
    starting_price_implied_probability, starting_price_favourite_marker,
    starting_price_favourite_status, starting_price_market_context_status,
    starting_price_analytical_numerator, starting_price_analytical_denominator,
    starting_price_analytical_favourite_status, starting_price_value_status,
    starting_price_manual_verification_id,
    prize_source_presented_amount, prize_canonical_minor_units, prize_currency,
    prize_interpretation_status, prize_interpretation_method,
    prize_conversion_multiplier, prize_confidence,
    source_num_storage_class, source_positive_runner_number, source_num_state,
    source_num_within_race_multiplicity, source_num_uniqueness_status,
    ovr_btn_numeric, ovr_btn_status, btn_numeric, btn_status,
    positive_official_winner_distance, later_position_zero_overall,
    same_distance_group, beaten_distance_requires_review,
    age_recorded, age_interpretation_status,
    sex_normalised, sex_interpretation_status, sex_manual_verification_id,
    headgear_raw_components_json, headgear_components_json,
    headgear_component_count, headgear_use_suffix,
    headgear_source_declared_first_time, headgear_interpretation_status,
    or_governed, or_status, rpr_governed, rpr_status, ts_governed, ts_status,
    jockey_governed, jockey_value_status, jockey_connection_value_decision_id,
    trainer_governed, trainer_value_status, trainer_connection_value_decision_id,
    owner_governed, owner_value_status, owner_connection_value_decision_id,
    comment_state, comment_analytically_available
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""


@dataclass(frozen=True)
class GovernedPopulationSummary:
    race_rows: int
    runner_rows: int
    unresolved_distance_rows: int
    all_weather_races: int
    temporal_external_ran_verifications: int
    connection_supplementations_applied: int
    connection_unresolved_blanks: int
    corrected_sex_rows: int
    invalid_rpr_rows: int
    unresolved_starting_price_rows: int


class GovernedPopulationError(RuntimeError):
    """Raised when source/current governance no longer matches the accepted contract."""


def _rows_as_dicts(rows: Iterable[tuple[object, ...]]) -> Iterable[dict[str, Any]]:
    for raw in rows:
        yield dict(zip(_SOURCE_COLUMNS, raw, strict=True))


def _same_source_value(left: object, right: object) -> bool:
    return type(left) is type(right) and left == right


def _constant_race_value(rows: list[dict[str, Any]], field: str) -> object:
    first = rows[0][field]
    if any(not _same_source_value(first, row[field]) for row in rows[1:]):
        race_key = (
            rows[0]["raw_date"],
            rows[0]["raw_course"],
            rows[0]["raw_off"],
        )
        raise GovernedPopulationError(
            f"Race-level source field {field!r} is not constant for {race_key!r}"
        )
    return first


def _fraction_text(value: Fraction | None) -> str | None:
    return None if value is None else str(value)


def _decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _compact_json(values: object) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def _manual_verification_ids(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        str(code): int(identifier)
        for code, identifier in connection.execute(
            "SELECT verification_code, manual_verification_id FROM governance_manual_verification"
        )
    }


def _course_ids(connection: sqlite3.Connection) -> dict[tuple[str, str], int]:
    return {
        (str(label), str(jurisdiction)): int(identifier)
        for identifier, label, jurisdiction in connection.execute(
            """
            SELECT reference_course_id, candidate_course_label, candidate_jurisdiction
            FROM reference_course
            """
        )
    }


def _jurisdiction_context_ids(
    connection: sqlite3.Connection,
) -> dict[tuple[str, str, str, str | None], int]:
    return {
        (str(jurisdiction), str(source_type), str(start), end): int(identifier)
        for identifier, jurisdiction, source_type, start, end in connection.execute(
            """
            SELECT jurisdiction_context_id, jurisdiction, source_type,
                   effective_from, effective_to
            FROM reference_jurisdiction_context
            """
        )
    }


def _connection_decisions(
    connection: sqlite3.Connection,
) -> dict[tuple[int, str], tuple[int, str | None, str]]:
    rows = connection.execute(
        """
        SELECT decision.connection_value_decision_id,
               decision.source_record_id,
               field.field_name,
               decision.governed_value,
               decision.value_status
        FROM governance_connection_value_decision AS decision
        JOIN source_relation_field AS field
          ON field.source_relation_field_id = decision.source_relation_field_id
        """
    )
    return {
        (int(source_record_id), str(field_name)): (
            int(decision_id),
            governed_value,
            str(value_status),
        )
        for decision_id, source_record_id, field_name, governed_value, value_status in rows
    }


def _ran_external_governance(
    connection: sqlite3.Connection,
) -> dict[int, tuple[str, int]]:
    """Return exact external status and evidence for governed source-ran checks."""

    result: dict[int, tuple[str, int]] = {}
    nb14_rows = connection.execute(
        """
        SELECT source_race_occurrence_id, manual_verification_id,
               verification_status, verification_code
        FROM governance_manual_verification
        WHERE governing_notebook = '14'
          AND verification_code LIKE 'NB14-RAN-%'
          AND source_race_occurrence_id IS NOT NULL
        """
    ).fetchall()
    for race_id, verification_id, status, code in nb14_rows:
        if status == "contradicted":
            external = "externally_contradicted"
        elif status == "confirmed":
            external = "externally_verified"
        else:
            raise GovernedPopulationError(
                f"{code}: unexpected ran verification status {status!r}"
            )
        result[int(race_id)] = (external, int(verification_id))

    # Great Navigator is the one accepted supplementation whose published
    # result also proves source ran=8 is contradicted by a nine-runner field.
    supplementation = connection.execute(
        """
        SELECT source_race_occurrence_id, manual_verification_id
        FROM governance_runner_record_supplementation
        WHERE supplementation_code = 'RUNNER-SUPPLEMENT-0003'
          AND source_reported_ran <> published_runner_count
        """
    ).fetchall()
    if len(supplementation) != 1:
        raise GovernedPopulationError(
            "RUNNER-SUPPLEMENT-0003 must provide the Great Navigator ran contradiction"
        )
    race_id, verification_id = supplementation[0]
    result[int(race_id)] = ("externally_contradicted", int(verification_id))
    return result


def _sex_verification_code(row: dict[str, Any]) -> str | None:
    raw_sex = row["sex"]
    if raw_sex in {"C", "F", "G", "H", "M", "R"}:
        return "NB17-SEX-0001"
    for key in VERIFIED_SEX_CORRECTIONS:
        (
            governed_raw_sex,
            verification_code,
            source_date,
            source_course,
            source_off,
            source_horse,
        ) = key
        if (
            raw_sex == governed_raw_sex
            and str(row["raw_date"]) == source_date
            and str(row["raw_course"]) == source_course
            and str(row["raw_off"]) == source_off
            and str(row["horse"]) == source_horse
        ):
            return verification_code
    return None


def _governed_connection(
    *,
    row: dict[str, Any],
    field: str,
    decisions: dict[tuple[int, str], tuple[int, str | None, str]],
) -> tuple[str | None, str, int | None]:
    raw_value = row[field]
    decision = decisions.get((int(row["source_record_id"]), field))
    source_blank = raw_value is None or str(raw_value).strip() == ""

    if not source_blank:
        if decision is not None:
            raise GovernedPopulationError(
                f"Connection decision would overwrite source rowid {row['source_rowid']} {field}"
            )
        return str(raw_value), "source_present", None

    if decision is None:
        raise GovernedPopulationError(
            f"Source rowid {row['source_rowid']} has an ungoverned blank {field}"
        )
    decision_id, governed_value, value_status = decision
    if value_status == "externally_supplemented":
        if governed_value is None or not str(governed_value).strip():
            raise GovernedPopulationError("Externally supplemented connection is blank")
        return str(governed_value), value_status, decision_id
    if value_status == "source_blank_unresolved":
        if governed_value is not None:
            raise GovernedPopulationError("Unresolved connection unexpectedly has a value")
        return None, value_status, decision_id
    raise GovernedPopulationError(f"Unsupported connection decision status {value_status!r}")


def _race_governed_row(
    rows: list[dict[str, Any]],
    *,
    governance_release_id: int,
    course_ids: dict[tuple[str, str], int],
    jurisdiction_context_ids: dict[tuple[str, str, str, str | None], int],
    ran_external: dict[int, tuple[str, int]],
) -> tuple[tuple[object, ...], str]:
    first = rows[0]
    race_id = int(first["source_race_occurrence_id"])
    if len(rows) != int(first["admitted_runner_count"]):
        raise GovernedPopulationError(
            f"Race {race_id} source row count changed: {len(rows)} vs {first['admitted_runner_count']}"
        )

    constants = {field: _constant_race_value(rows, field) for field in RACE_CONSTANT_FIELDS}
    jurisdiction_result = derive_candidate_race_jurisdiction(
        {
            "course": first["raw_course"],
            "date": first["raw_date"],
            "type": constants["type"],
            "race_name": constants["race_name"],
        }
    )
    candidate_jurisdiction = str(jurisdiction_result.iloc[0])
    jurisdiction_evidence = str(jurisdiction_result.iloc[1])
    candidate_course_label = derive_candidate_course_label(first["raw_course"])
    course_key = (candidate_course_label, candidate_jurisdiction)
    reference_course_id = course_ids.get(course_key)
    if reference_course_id is None:
        raise GovernedPopulationError(f"Unmatched governed course identity: {course_key!r}")

    context = resolve_jurisdiction_context(
        candidate_jurisdiction,
        str(constants["type"]),
        date.fromisoformat(str(first["raw_date"])),
    )
    if context is None:
        jurisdiction_context_id = None
        jurisdiction_context_status = "unresearched"
    else:
        context_key = (
            context.jurisdiction,
            context.source_type,
            context.effective_from.isoformat(),
            context.effective_to.isoformat() if context.effective_to else None,
        )
        jurisdiction_context_id = jurisdiction_context_ids[context_key]
        jurisdiction_context_status = "matched"

    surface = derive_source_supported_surface(first["raw_course"])
    distance = parse_race_distance(constants["dist"])
    class_result = parse_class(constants["class"])
    pattern_result = parse_pattern(constants["pattern"])
    rating_result = parse_rating_band(constants["rating_band"])
    age_band_result = parse_age_band(constants["age_band"])
    sex_rest_result = classify_sex_restriction(constants["sex_rest"])

    external_status, verification_id = ran_external.get(
        race_id,
        ("unverified", None),
    )
    ran_result = profile_reported_ran(
        (row["ran"] for row in rows),
        source_runner_row_count=len(rows),
        source_ran_external_status=external_status,
    )

    return (
        (
            race_id,
            governance_release_id,
            candidate_course_label,
            candidate_jurisdiction,
            jurisdiction_evidence,
            reference_course_id,
            jurisdiction_context_id,
            jurisdiction_context_status,
            surface.candidate_surface,
            surface.evidence,
            constants["dist"],
            distance["miles"],
            distance["whole_furlongs"],
            int(distance["has_half_furlong"])
            if distance["has_half_furlong"] is not None
            else None,
            distance["total_furlongs"],
            distance["source_implied_yards"],
            distance["source_implied_metres"],
            int(distance["official_distance_verified"]),
            distance["parse_status"],
            RACE_DISTANCE_PARSER_VERSION,
            ran_result["source_reported_ran"],
            ran_result["source_runner_row_count"],
            ran_result["source_ran_distinct_value_count"],
            ran_result["source_ran_consistency_status"],
            ran_result["source_row_count_vs_ran_status"],
            ran_result["source_runner_coverage_status"],
            ran_result["source_ran_external_status"],
            verification_id,
            constants["race_name"],
            constants["type"],
            constants["class"],
            constants["pattern"],
            constants["rating_band"],
            constants["age_band"],
            constants["sex_rest"],
            class_result["class_number"],
            class_result["class_parse_status"],
            pattern_result["pattern_family"],
            pattern_result["pattern_level_raw"],
            pattern_result["pattern_parse_status"],
            rating_result["rating_lower_bound"],
            rating_result["rating_upper_bound"],
            rating_result["rating_band_parse_status"],
            age_band_result["stated_minimum_age"],
            age_band_result["stated_maximum_age"],
            int(age_band_result["age_band_open_ended"])
            if age_band_result["age_band_open_ended"] is not None
            else None,
            age_band_result["age_band_syntax"],
            age_band_result["age_band_interpretation_status"],
            sex_rest_result["sex_rest_category"],
            sex_rest_result["sex_rest_interpretation_status"],
        ),
        candidate_jurisdiction,
    )


def _runner_governed_rows(
    rows: list[dict[str, Any]],
    *,
    candidate_jurisdiction: str,
    governance_release_id: int,
    manual_ids: dict[str, int],
    connection_decisions: dict[tuple[int, str], tuple[int, str | None, str]],
) -> tuple[list[tuple[object, ...]], dict[str, int]]:
    positive_nums = Counter(
        int(row["num"])
        for row in rows
        if isinstance(row["num"], int)
        and not isinstance(row["num"], bool)
        and int(row["num"]) > 0
    )

    output: list[tuple[object, ...]] = []
    counters = {
        "connection_supplementations": 0,
        "connection_unresolved": 0,
        "corrected_sex": 0,
        "invalid_rpr": 0,
        "unresolved_sp": 0,
    }

    for row in rows:
        result = parse_result(row["pos"])
        weight = parse_carried_weight(row["wgt"])
        sp = parse_starting_price(row["sp"])
        prize = parse_prize_money(row["prize"], candidate_jurisdiction)

        num_multiplicity = (
            positive_nums.get(int(row["num"]))
            if isinstance(row["num"], int)
            and not isinstance(row["num"], bool)
            and int(row["num"]) > 0
            else None
        )
        number = parse_runner_number(
            row["num"],
            within_race_multiplicity=num_multiplicity,
        )
        beaten = classify_beaten_distance_row(
            raw_pos=row["pos"],
            raw_ovr_btn=row["ovr_btn"],
            raw_btn=row["btn"],
        )
        age_result = normalise_runner_age(row["age"])

        sex_code = _sex_verification_code(row)
        sex_result = normalise_runner_sex(
            row["sex"],
            verification_id=sex_code,
            source_date=str(row["raw_date"]),
            source_course=str(row["raw_course"]),
            source_off=str(row["raw_off"]),
            source_horse=str(row["horse"]),
        )
        sex_manual_id = (
            manual_ids.get(str(sex_result["verification_id"]))
            if sex_result["verification_id"]
            else None
        )
        if sex_result["interpretation_status"] == "verified_source_correction":
            counters["corrected_sex"] += 1

        headgear = parse_runner_headgear(row["hg"])
        ratings = parse_rating_triplet(
            row["or"],
            row["rpr"],
            row["ts"],
            source_rowid=int(row["source_rowid"]),
        )
        if ratings["rpr_status"] == "invalid_source_value":
            counters["invalid_rpr"] += 1

        jockey = _governed_connection(
            row=row,
            field="jockey",
            decisions=connection_decisions,
        )
        trainer = _governed_connection(
            row=row,
            field="trainer",
            decisions=connection_decisions,
        )
        owner = _governed_connection(
            row=row,
            field="owner",
            decisions=connection_decisions,
        )
        for connection_value in (jockey, trainer, owner):
            if connection_value[1] == "externally_supplemented":
                counters["connection_supplementations"] += 1
            elif connection_value[1] == "source_blank_unresolved":
                counters["connection_unresolved"] += 1

        comment = classify_comment(row["comment"])

        if sp.price_kind in {StartingPriceKind.FRACTIONAL, StartingPriceKind.EVENS}:
            analytical_numerator = sp.numerator
            analytical_denominator = sp.denominator
            analytical_favourite = sp.favourite_status
            sp_value_status = "source_parsed"
        elif sp.price_kind == StartingPriceKind.MISSING:
            analytical_numerator = None
            analytical_denominator = None
            analytical_favourite = None
            sp_value_status = "missing"
        else:
            analytical_numerator = None
            analytical_denominator = None
            analytical_favourite = None
            sp_value_status = "unresolved"
            counters["unresolved_sp"] += 1

        # Notebook 08's historical manual check was not promoted to a governed
        # correction. The current standalone F therefore remains unresolved and
        # has no Database v2 manual-verification FK.
        sp_manual_id = None

        output.append(
            (
                int(row["runner_participation_id"]),
                governance_release_id,
                result.result_kind.value,
                result.finish_position,
                result.outcome_code,
                weight["notation_family"],
                weight["parsed_stones"],
                weight["parsed_pounds"],
                weight["source_implied_total_pounds"],
                weight["source_implied_kilograms"],
                weight["parse_status"],
                int(weight["ambiguity_flag"]),
                _compact_json(weight["anomaly_flags"]),
                int(weight["official_weight_verified"]),
                sp.price_kind.value,
                sp.numerator,
                sp.denominator,
                _fraction_text(sp.fractional_odds),
                _fraction_text(sp.decimal_odds),
                _fraction_text(sp.implied_probability),
                sp.favourite_marker,
                sp.favourite_status,
                sp.market_context_status,
                analytical_numerator,
                analytical_denominator,
                analytical_favourite,
                sp_value_status,
                sp_manual_id,
                _decimal_text(prize["prize_source_presented_amount"]),
                prize["prize_canonical_minor_units"],
                prize["prize_currency"],
                prize["prize_interpretation_status"],
                prize["prize_interpretation_method"],
                _decimal_text(prize["prize_conversion_multiplier"]),
                prize["prize_confidence"],
                number["source_num_storage_class"],
                number["source_positive_runner_number"],
                number["source_num_state"],
                number["source_num_within_race_multiplicity"],
                number["source_num_uniqueness_status"],
                beaten["numeric_ovr_btn"],
                beaten["ovr_btn_status"],
                beaten["numeric_btn"],
                beaten["btn_status"],
                int(beaten["positive_official_winner_distance"]),
                int(beaten["later_position_zero_overall"]),
                int(beaten["same_distance_group"]),
                int(beaten["requires_review"]),
                age_result["normalised_age"],
                age_result["interpretation_status"],
                sex_result["normalised_sex"],
                sex_result["interpretation_status"],
                sex_manual_id,
                _compact_json(headgear["raw_components"]),
                _compact_json(headgear["normalised_components"]),
                headgear["component_count"],
                headgear["use_suffix"],
                int(headgear["source_declared_first_time"]),
                headgear["interpretation_status"],
                ratings["or"],
                ratings["or_status"],
                ratings["rpr"],
                ratings["rpr_status"],
                ratings["ts"],
                ratings["ts_status"],
                *jockey,
                *trainer,
                *owner,
                comment.comment_state,
                int(comment.substantive_text is not None),
            )
        )

    return output, counters


def _iter_races(
    raw_rows: Iterable[tuple[object, ...]],
) -> Iterable[list[dict[str, Any]]]:
    """Yield one race at a time from one already-materialised source batch."""

    current_id: int | None = None
    current_rows: list[dict[str, Any]] = []
    for row in _rows_as_dicts(raw_rows):
        race_id = int(row["source_race_occurrence_id"])
        if current_id is None:
            current_id = race_id
        if race_id != current_id:
            yield current_rows
            current_rows = []
            current_id = race_id
        current_rows.append(row)
    if current_rows:
        yield current_rows


def populate_governed_race_and_runner_extensions(
    connection: sqlite3.Connection,
    *,
    governance_release_id: int,
    race_batch_size: int = DEFAULT_RACE_BATCH_SIZE,
) -> GovernedPopulationSummary:
    """Populate race and runner governed extensions from the copied v1 core.

    Each batch query is fully fetched before derived rows are written and
    committed. A partial candidate can therefore contain committed batches after
    a later failure, but the manifest remains ``building`` and the outer build
    deletes the entire disposable file; partial success is never accepted.
    """

    if race_batch_size <= 0:
        raise ValueError("race_batch_size must be positive")
    manifest = connection.execute(
        "SELECT governance_release_id, build_status FROM import_manifest WHERE import_manifest_id = 1"
    ).fetchone()
    if manifest != (governance_release_id, "building"):
        raise GovernedPopulationError(
            f"Population requires the active building manifest; observed {manifest!r}"
        )

    for table in (
        "core_source_race_occurrence_governed",
        "core_runner_participation_governed",
    ):
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count:
            raise GovernedPopulationError(
                f"Population requires empty {table}; found {count} rows"
            )

    manual_ids = _manual_verification_ids(connection)
    course_ids = _course_ids(connection)
    jurisdiction_context_ids = _jurisdiction_context_ids(connection)
    connection_decisions = _connection_decisions(connection)
    ran_external = _ran_external_governance(connection)

    race_ids = [
        int(value)
        for value, in connection.execute(
            "SELECT source_race_occurrence_id FROM core_source_race_occurrence ORDER BY source_race_occurrence_id"
        ).fetchall()
    ]
    if len(race_ids) != EXPECTED_RACES or len(race_ids) != len(set(race_ids)):
        raise GovernedPopulationError(
            f"Structural race ID inventory changed: {len(race_ids)} rows"
        )

    race_rows = 0
    runner_rows = 0
    unresolved_distance_rows = 0
    all_weather_races = 0
    aggregate = {
        "connection_supplementations": 0,
        "connection_unresolved": 0,
        "corrected_sex": 0,
        "invalid_rpr": 0,
        "unresolved_sp": 0,
    }

    for start in range(0, len(race_ids), race_batch_size):
        batch_ids = race_ids[start : start + race_batch_size]
        first_race_id = batch_ids[0]
        last_race_id = batch_ids[-1]

        # Fetch the complete bounded batch before any writes/commit. This avoids
        # holding an active SELECT statement across a commit on the same SQLite
        # connection while keeping memory bounded to a few thousand runner rows.
        raw_batch = connection.execute(
            _SOURCE_SELECT,
            (first_race_id, last_race_id),
        ).fetchall()
        if not raw_batch:
            raise GovernedPopulationError(
                f"Race batch {first_race_id}..{last_race_id} returned no source rows"
            )

        race_insert_rows: list[tuple[object, ...]] = []
        runner_insert_rows: list[tuple[object, ...]] = []
        observed_batch_ids: list[int] = []

        for source_race_rows in _iter_races(raw_batch):
            race_values, candidate_jurisdiction = _race_governed_row(
                source_race_rows,
                governance_release_id=governance_release_id,
                course_ids=course_ids,
                jurisdiction_context_ids=jurisdiction_context_ids,
                ran_external=ran_external,
            )
            race_insert_rows.append(race_values)
            observed_batch_ids.append(int(race_values[0]))
            race_rows += 1
            if race_values[18] == "unresolved":
                unresolved_distance_rows += 1
            if race_values[8] == "all_weather_unspecified":
                all_weather_races += 1

            governed_runner_rows, counters = _runner_governed_rows(
                source_race_rows,
                candidate_jurisdiction=candidate_jurisdiction,
                governance_release_id=governance_release_id,
                manual_ids=manual_ids,
                connection_decisions=connection_decisions,
            )
            runner_insert_rows.extend(governed_runner_rows)
            runner_rows += len(governed_runner_rows)
            for key, value in counters.items():
                aggregate[key] += value

        if observed_batch_ids != batch_ids:
            raise GovernedPopulationError(
                "Bounded source query did not return exactly the expected race IDs: "
                f"expected {batch_ids[:3]}..{batch_ids[-3:]}, "
                f"observed {observed_batch_ids[:3]}..{observed_batch_ids[-3:]}"
            )

        connection.executemany(_RACE_INSERT, race_insert_rows)
        connection.executemany(_RUNNER_INSERT, runner_insert_rows)
        connection.commit()

    if race_rows != EXPECTED_RACES:
        raise GovernedPopulationError(
            f"Expected {EXPECTED_RACES} race extensions; built {race_rows}"
        )
    if runner_rows != EXPECTED_RUNNERS:
        raise GovernedPopulationError(
            f"Expected {EXPECTED_RUNNERS} runner extensions; built {runner_rows}"
        )
    if aggregate["connection_supplementations"] != 28:
        raise GovernedPopulationError(
            "Expected 28 applied connection supplementations; "
            f"observed {aggregate['connection_supplementations']}"
        )
    if aggregate["connection_unresolved"] != 18:
        raise GovernedPopulationError(
            "Expected 18 unresolved connection blanks; "
            f"observed {aggregate['connection_unresolved']}"
        )
    if aggregate["corrected_sex"] != 2:
        raise GovernedPopulationError(
            f"Expected 2 exact sex corrections; observed {aggregate['corrected_sex']}"
        )
    if aggregate["invalid_rpr"] != 1:
        raise GovernedPopulationError(
            f"Expected 1 exact invalid RPR; observed {aggregate['invalid_rpr']}"
        )
    if aggregate["unresolved_sp"] != 1:
        raise GovernedPopulationError(
            f"Expected 1 unresolved starting-price row; observed {aggregate['unresolved_sp']}"
        )

    return GovernedPopulationSummary(
        race_rows=race_rows,
        runner_rows=runner_rows,
        unresolved_distance_rows=unresolved_distance_rows,
        all_weather_races=all_weather_races,
        temporal_external_ran_verifications=len(ran_external),
        connection_supplementations_applied=aggregate["connection_supplementations"],
        connection_unresolved_blanks=aggregate["connection_unresolved"],
        corrected_sex_rows=aggregate["corrected_sex"],
        invalid_rpr_rows=aggregate["invalid_rpr"],
        unresolved_starting_price_rows=aggregate["unresolved_sp"],
    )


__all__ = [
    "GovernedPopulationError",
    "GovernedPopulationSummary",
    "populate_governed_race_and_runner_extensions",
]
