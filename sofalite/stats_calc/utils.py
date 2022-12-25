import logging
from typing import Callable, Sequence

from sofalite.stats_calc import utils as stats_utils
from sofalite.utils.maths import to_precision

def get_p_str(p: float) -> str:
    """
    Get a nice representation of p value including significance if relevant.
    """
    p_str = to_precision(num=p, precision=4)
    if p < 0.001:
        p_str = f'< 0.001 ({p_str})'
    return p_str

def get_obriens_msg(samples: Sequence[Sequence[float]], sim_variance_fn: Callable, *, high=False) -> str:
    try:
        ## sim_variance threshold parameter not used or relevant because ignoring is_similar part of output
        _is_similar, p_sim = sim_variance_fn(samples, high=high)
        obriens_msg = stats_utils.get_p_str(p_sim)
    except Exception as e:
        logging.info("Unable to calculate O'Briens test "
            f"for homogeneity of variance.\nOrig error: {e}")
        obriens_msg = "Unable to calculate O'Briens test for homogeneity of variance"
    return obriens_msg
