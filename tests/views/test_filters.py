from decimal import Decimal

import pytest

from schemes.views.filters import pounds, remove_exponent


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (Decimal("0"), "£0"),
        (Decimal("0.99"), "£1"),
        (Decimal("1.00"), "£1"),
        (Decimal("1000000"), "£1,000,000"),
    ],
)
def test_pounds(value: Decimal, expected_value: str) -> None:
    assert pounds(value) == expected_value


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (Decimal("0"), Decimal("0")),
        (Decimal("0.10"), Decimal("0.1")),
        (Decimal("1.00"), Decimal("1")),
        (Decimal("10.00"), Decimal("10")),
        (Decimal("1E2"), Decimal("100")),
    ],
)
def test_remove_exponent(value: Decimal, expected_value: Decimal) -> None:
    assert remove_exponent(value) == expected_value
