import datetime
from decimal import Decimal


def date(d: datetime.date) -> str:
    return "{:%-d %b %Y}".format(d)


def pounds(i: int) -> str:
    return "£{:,}".format(i)


def remove_exponent(d: Decimal) -> Decimal:
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
