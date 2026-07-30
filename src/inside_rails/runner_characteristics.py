"""Governed runner age, sex and headgear interpretation.

Notebook 17 established the bounded semantics for the source fields ``age``,
``sex`` and ``hg``. Raw values remain immutable. These helpers expose only the
normalisations supported by the governed evidence and preserve unresolved
states rather than guessing.
"""

from __future__ import annotations

from typing import Any

SEX_CODE_MAP: dict[str, str] = {
    "C": "colt",
    "F": "filly",
    "G": "gelding",
    "H": "horse",
    "M": "mare",
    "R": "rig",
}

VERIFIED_SEX_CORRECTIONS: dict[tuple[str, str], str] = {
    ("BB", "NB17-SEX-0002"): "gelding",
    ("B", "NB17-SEX-0003"): "filly",
}

HEADGEAR_COMPONENT_MAP: dict[str, str] = {
    "e/c": "eyecover",
    "e/s": "eyeshield",
    "h": "hood",
    "b": "blinkers",
    "p": "cheekpieces",
    "t": "tongue_tie",
    "v": "visor",
    "e": "eye_hood",
    "c": "eyecover",
}

HEADGEAR_TOKENS: tuple[str, ...] = (
    "e/c",
    "e/s",
    "h",
    "b",
    "p",
    "t",
    "v",
    "e",
    "c",
)


def normalise_runner_age(raw_age: Any) -> dict[str, Any]:
    """Preserve one source-recorded integer age without clipping or inference."""

    result: dict[str, Any] = {
        "raw_age": raw_age,
        "normalised_age": None,
        "interpretation_status": "unresolved",
    }

    if isinstance(raw_age, bool) or not isinstance(raw_age, int):
        return result

    result.update(
        {
            "normalised_age": raw_age,
            "interpretation_status": "source_recorded_integer",
        }
    )
    return result


def normalise_runner_sex(
    raw_sex: Any,
    *,
    verification_id: str | None = None,
) -> dict[str, Any]:
    """Normalise an exact governed sex code or verification-backed anomaly."""

    result: dict[str, Any] = {
        "raw_sex": raw_sex,
        "normalised_sex": None,
        "verification_id": verification_id,
        "interpretation_status": "unresolved",
    }

    common_value = SEX_CODE_MAP.get(raw_sex)
    if common_value is not None:
        result.update(
            {
                "normalised_sex": common_value,
                "verification_id": "NB17-SEX-0001",
                "interpretation_status": "verified_common_code",
            }
        )
        return result

    corrected_value = VERIFIED_SEX_CORRECTIONS.get((raw_sex, verification_id or ""))
    if corrected_value is not None:
        result.update(
            {
                "normalised_sex": corrected_value,
                "interpretation_status": "verified_source_correction",
            }
        )

    return result


def parse_runner_headgear(raw_hg: Any) -> dict[str, Any]:
    """Parse one governed headgear value while preserving source component order."""

    result: dict[str, Any] = {
        "raw_hg": raw_hg,
        "raw_components": [],
        "normalised_components": [],
        "component_count": 0,
        "source_declared_first_time": False,
        "use_suffix": None,
        "interpretation_status": "unresolved",
    }

    if raw_hg is None or raw_hg == "":
        result["interpretation_status"] = "blank_field_not_supplied"
        return result

    if not isinstance(raw_hg, str):
        return result

    remaining = raw_hg
    use_suffix: str | None = None

    if remaining.endswith("1"):
        use_suffix = "1"
        remaining = remaining[:-1]
    elif remaining[-1:].isdigit():
        return result

    if not remaining:
        return result

    raw_components: list[str] = []
    normalised_components: list[str] = []

    while remaining:
        matched_token = next(
            (token for token in HEADGEAR_TOKENS if remaining.startswith(token)),
            None,
        )
        if matched_token is None:
            return result

        raw_components.append(matched_token)
        normalised_components.append(HEADGEAR_COMPONENT_MAP[matched_token])
        remaining = remaining[len(matched_token) :]

    result.update(
        {
            "raw_components": raw_components,
            "normalised_components": normalised_components,
            "component_count": len(raw_components),
            "source_declared_first_time": use_suffix == "1",
            "use_suffix": use_suffix,
            "interpretation_status": "fully_decomposed_source_code",
        }
    )
    return result
