import decimal

def n2d(f):
    """
    Convert a floating point number to a Decimal with no loss of information

    http://docs.python.org/library/decimal.html with added error trapping and
    handling of non-floats.
    """
    if not isinstance(f, float):
        try:
            f = float(f)
        except (ValueError, TypeError):
            raise Exception(f'Unable to convert value "{f}" to Decimal')
    try:
        n, d = f.as_integer_ratio()
    except Exception:
        raise Exception(
            f'Unable to turn value "{f}" into integer ratio for unknown reason.')
    numerator, denominator = decimal.Decimal(n), decimal.Decimal(d)
    ctx = decimal.Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[decimal.Inexact]:
        ctx.flags[decimal.Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result
