from sofalite.utils.maths import to_precision

def get_p_str(p: float) -> str:
    """
    Get a nice representation of p value including significance if relevant.
    """
    p_str = to_precision(num=p, precision=4)
    if p < 0.001:
        p_str = f'< 0.001 ({p_str})'
    return p_str
