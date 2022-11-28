import decimal
import math

def format_num(num):
    try:
        formatted = f'{num:,}'  ## e.g. 1_000 -> '1,000'
    except ValueError:  ## e.g. a string '1000' -> '1,000'
        formatted = num
    return formatted

def to_precision(num: float, precision: int) -> str:
    """
    Returns a string representation of x formatted with a precision of p.

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp

    http://randlet.com/blog/python-significant-figures-format/
    """
    x = float(num)
    if x == 0.:
        return '0.' + '0' * (precision - 1)
    out = []
    if x < 0:
        out.append('-')
        x = -x
    e = int(math.log10(x))
    tens = math.pow(10, e - precision + 1)
    n = math.floor(x / tens)
    if n < math.pow(10, precision - 1):
        e = e - 1
        tens = math.pow(10, e - precision + 1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens - x):
        n = n + 1
    if n >= math.pow(10, precision):
        n = n / 10.
        e = e + 1
    m = '%.*g' % (precision, n)
    if e < -2 or e >= precision:
        out.append(m[0])
        if precision > 1:
            out.append('.')
            out.extend(m[1:precision])
        out.append('e')
        if e > 0:
            out.append('+')
        out.append(str(e))
    elif e == (precision - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e + 1])
        if e + 1 < len(m):
            out.append('.')
            out.extend(m[e + 1:])
    else:
        out.append('0.')
        out.extend(['0'] * -(e + 1))
        out.append(m)
    return ''.join(out)

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
