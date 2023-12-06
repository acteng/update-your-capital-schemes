from decimal import Decimal


def pounds(d: Decimal) -> str:
    return "£{:,}".format(round(d))


def remove_exponent(d: Decimal) -> Decimal:
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
