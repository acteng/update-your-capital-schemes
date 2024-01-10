from decimal import Decimal


def pounds(i: int) -> str:
    return "£{:,}".format(i)


def remove_exponent(d: Decimal) -> Decimal:
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
