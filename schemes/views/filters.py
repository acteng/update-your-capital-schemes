import datetime
from decimal import Decimal


def date(value: datetime.date) -> str:
    return "{:%-d %b %Y}".format(value)


def pounds(value: int) -> str:
    return "£{:,}".format(value)


def remove_exponent(value: Decimal) -> Decimal:
    return value.quantize(Decimal(1)) if value == value.to_integral() else value.normalize()
