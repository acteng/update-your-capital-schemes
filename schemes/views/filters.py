import datetime
from decimal import Decimal


def date(value: datetime.date) -> str:
    return f"{value:%-d %b %Y}"


def pounds(value: int) -> str:
    return f"£{value:,}"


def remove_exponent(value: Decimal) -> Decimal:
    return value.quantize(Decimal(1)) if value == value.to_integral() else value.normalize()
