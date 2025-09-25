import datetime
from decimal import Decimal

import pytest

from schemes.views.filters import date, pounds, remove_exponent


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (datetime.date(2020, 1, 2), "2 Jan 2020"),
        (datetime.date(2020, 1, 10), "10 Jan 2020"),
        (datetime.datetime(2020, 1, 10, 12), "10 Jan 2020"),
    ],
)
def test_date(value: datetime.date, expected_value: str) -> None:
    assert date(value) == expected_value


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (0, "£0"),
        (1, "£1"),
        (1_000_000, "£1,000,000"),
    ],
)
def test_pounds(value: int, expected_value: str) -> None:
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
    assert remove_exponent(value).compare_total(expected_value) == Decimal(0)
