"""Governed parsing for the source ``prize`` field.

Notebook 13 established that ``prize`` is runner-level recorded prize money,
not the advertised race purse. Only directly evidenced source conventions are
canonicalised here:

* Great Britain: numeric values interpreted as GBP.
* Ireland: euro-prefixed text values interpreted as EUR.
* All other populated values: preserved but currency-unresolved.

No foreign exchange reconstruction is performed. Blank values remain null and
must never be converted to zero.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from numbers import Integral, Real
from typing import Any


GB_JURISDICTIONS = frozenset({"Great Britain", "GB", "UK"})
IRELAND_JURISDICTIONS = frozenset({"Ireland", "IRE"})
_MINOR_UNIT = Decimal("0.01")


@dataclass(frozen=True)
class PrizeMoneyResult:
    """Governed interpretation of one raw runner-level prize value."""

    prize_raw: Any
    prize_source_presented_amount: Decimal | None
    prize_canonical_minor_units: int | None
    prize_currency: str | None
    prize_interpretation_status: str
    prize_interpretation_method: str
    prize_conversion_multiplier: Decimal | None
    prize_confidence: str

    def as_dict(self) -> dict[str, Any]:
        """Return a database-build-friendly mapping."""

        return asdict(self)


def _blank(raw_prize: Any) -> bool:
    return raw_prize is None or (isinstance(raw_prize, str) and not raw_prize.strip())


def _decimal_from_numeric(raw_prize: Any) -> Decimal | None:
    """Convert a finite non-Boolean numeric value to ``Decimal`` safely."""

    if isinstance(raw_prize, bool):
        return None
    if isinstance(raw_prize, Integral):
        return Decimal(int(raw_prize))
    if isinstance(raw_prize, Decimal):
        return raw_prize if raw_prize.is_finite() else None
    if isinstance(raw_prize, Real):
        value = Decimal(str(raw_prize))
        return value if value.is_finite() else None
    return None


def _decimal_from_euro_text(raw_prize: Any) -> Decimal | None:
    if not isinstance(raw_prize, str):
        return None

    text = raw_prize.strip()
    if not text.startswith("€"):
        return None

    numeric_text = text[1:].strip().replace(",", "")
    if not numeric_text:
        return None

    try:
        value = Decimal(numeric_text)
    except InvalidOperation:
        return None

    return value if value.is_finite() else None


def _to_exact_minor_units(amount: Decimal) -> int | None:
    """Return exact cents/pence, rejecting fractions below one minor unit."""

    if amount < 0:
        return None

    quantized = amount.quantize(_MINOR_UNIT)
    if quantized != amount:
        return None

    return int(quantized * 100)


def parse_prize_money(raw_prize: Any, candidate_jurisdiction: str | None) -> dict[str, Any]:
    """Interpret one raw runner-level prize value under Notebook 13 policy.

    The function intentionally does not infer currency from magnitude, race
    name, date, course, or an assumed exchange rate. Newly evidenced rules can
    be added later without changing the preserved raw value.
    """

    if _blank(raw_prize):
        return PrizeMoneyResult(
            prize_raw=raw_prize,
            prize_source_presented_amount=None,
            prize_canonical_minor_units=None,
            prize_currency=None,
            prize_interpretation_status="blank",
            prize_interpretation_method="source_blank_preserved",
            prize_conversion_multiplier=None,
            prize_confidence="confirmed",
        ).as_dict()

    jurisdiction = candidate_jurisdiction.strip() if candidate_jurisdiction else None

    if jurisdiction in GB_JURISDICTIONS:
        amount = _decimal_from_numeric(raw_prize)
        minor_units = _to_exact_minor_units(amount) if amount is not None else None
        if minor_units is not None:
            return PrizeMoneyResult(
                prize_raw=raw_prize,
                prize_source_presented_amount=amount,
                prize_canonical_minor_units=minor_units,
                prize_currency="GBP",
                prize_interpretation_status="canonical",
                prize_interpretation_method="direct_gb_numeric_gbp",
                prize_conversion_multiplier=None,
                prize_confidence="confirmed",
            ).as_dict()

    if jurisdiction in IRELAND_JURISDICTIONS:
        amount = _decimal_from_euro_text(raw_prize)
        minor_units = _to_exact_minor_units(amount) if amount is not None else None
        if minor_units is not None:
            return PrizeMoneyResult(
                prize_raw=raw_prize,
                prize_source_presented_amount=amount,
                prize_canonical_minor_units=minor_units,
                prize_currency="EUR",
                prize_interpretation_status="canonical",
                prize_interpretation_method="direct_ireland_euro_text",
                prize_conversion_multiplier=None,
                prize_confidence="confirmed",
            ).as_dict()

    source_amount = _decimal_from_numeric(raw_prize)
    if source_amount is None:
        source_amount = _decimal_from_euro_text(raw_prize)

    source_amount_is_valid = source_amount is not None and source_amount >= 0
    status = "currency_unresolved" if source_amount_is_valid else "invalid"
    method = (
        "source_presented_amount_currency_unresolved"
        if source_amount_is_valid
        else "unrecognised_source_value"
    )

    return PrizeMoneyResult(
        prize_raw=raw_prize,
        prize_source_presented_amount=source_amount,
        prize_canonical_minor_units=None,
        prize_currency=None,
        prize_interpretation_status=status,
        prize_interpretation_method=method,
        prize_conversion_multiplier=None,
        prize_confidence="unresolved",
    ).as_dict()
