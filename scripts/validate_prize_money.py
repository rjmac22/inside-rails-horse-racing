#!/usr/bin/env python3
"""Independent smoke validation for governed prize-money parsing."""

from __future__ import annotations

from decimal import Decimal

from inside_rails.prize_money import parse_prize_money


def main() -> None:
    cases = [
        (
            1234.56,
            "Great Britain",
            {
                "prize_canonical_minor_units": 123456,
                "prize_currency": "GBP",
                "prize_interpretation_status": "canonical",
            },
        ),
        (
            "€12,345.67",
            "Ireland",
            {
                "prize_source_presented_amount": Decimal("12345.67"),
                "prize_canonical_minor_units": 1234567,
                "prize_currency": "EUR",
                "prize_interpretation_status": "canonical",
            },
        ),
        (
            500000,
            "United States",
            {
                "prize_source_presented_amount": Decimal("500000"),
                "prize_canonical_minor_units": None,
                "prize_currency": None,
                "prize_interpretation_status": "currency_unresolved",
            },
        ),
        (
            None,
            "Great Britain",
            {
                "prize_canonical_minor_units": None,
                "prize_currency": None,
                "prize_interpretation_status": "blank",
            },
        ),
    ]

    for raw_prize, jurisdiction, expected in cases:
        result = parse_prize_money(raw_prize, jurisdiction)
        for field, expected_value in expected.items():
            actual = result[field]
            if actual != expected_value:
                raise AssertionError(
                    f"{jurisdiction=} {raw_prize=} {field=}: "
                    f"expected {expected_value!r}, got {actual!r}"
                )

    print(f"Prize-money validation passed for {len(cases)} governed cases.")


if __name__ == "__main__":
    main()
