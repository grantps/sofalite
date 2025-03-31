"""
Needed by dc's in conf.misc as well as other code
so putting it here at the lowest level so only one direction through layers
"""
from collections.abc import Sequence
from typing import Callable

from sofalite.init_conf.utils.maths import to_precision

def get_quartiles(vals):
    """
    From Wild & Seber Introduction to Probability and Statistics 1996 pp.74-77
    Depth of quartiles is (int(n/2)+1)/2
    (from left for LQ and from right for UQ).
    """
    new_vals = vals[:]
    new_vals.sort()  ## leaving vals untouched
    n = len(new_vals)
    if not n:
        raise Exception('No values supplied to get_quartiles.')
    depth = (int(n / 2.0) + 1.0) / 2.0
    l_depth = int(depth)
    ## NB zero-based so subtract 1 for position going upwards
    if int(depth) == depth:
        lq = new_vals[l_depth - 1]
        uq = new_vals[-l_depth]
    else:  ## int truncates towards 0 but depth is always a positive number
        ## 1,3,4,5,60 depth = 5/2 i.e. [2.5] i.e. 2 -> 2+1 i.e. 3 -> 3/2 i.e. 1.5
        # so lq = (1+3)/2 i.e. 2 and uq = (5+60)/2 i.e. 32.5
        u_depth = int(depth) + 1
        lq = (new_vals[l_depth - 1] + new_vals[u_depth - 1]) / 2.0
        uq = (new_vals[-l_depth] + new_vals[-u_depth]) / 2.0
    return lq, uq

def get_optimal_axis_bounds(x_axis_min_val: float, x_axis_max_val: float, *, debug=False) -> tuple[float, float]:
    """
    Useful for boxplots and scatterplots.

    axis_min -- the minimum y value exactly
    axis_max -- the maximum y value exactly

    Generally, we want box and scatter plots to have y-axes starting from just
    below the minimum point (e.g. lowest outlier). That is to avoid the common case
    where we have the y-axis start at 0, and all our values range tightly
    together. In which case, for boxplots, we will have a series of tiny
    boxplots up the top, and we won't be able to see the different parts of it
    e.g. LQ, median etc. For scatter plots our data will be too tightly
    scrunched up to see any spread.

    But sometimes the lowest point is not that far above 0, in which case we
    should set it to 0. A 0-based axis is preferable unless the values are a
    long way away. Going from 0.5-12 is silly. Might as well go from 0-12.
    4 scenarios:

    1) min and max are both the same
    Just try to set the max differently to the min so there is a range on the
    axis to display. See implementation for more details.

    2) min and max are both +ve
    |   *
    |
    -------
    Snap min to 0 if gap small rel to range, otherwise make min y-axis just
    below min point. Make max y-axis just above the max point. Make the
    padding from 0 the least of 0.1 of axis_min and 0.1 of val_range. The
    outer padding can be the least of the axis_max and 0.1 of val_range.

    3) min and max are -ve
    -------
    |   *
    |
    Snap max to 0 if gap small rel to range, otherwise make max y-axis just
    above max point. Make min y-axis just below min point. Make the
    padding the least of 0.1 of gap and 0.1 of val_range.

    4) min is -ve and max is +ve
    |   *
    -------
    |   *
    Make max 1.1 * axis_max. No harm if 0.
    Make min 1.1 * axis_min. No harm if 0.
    """
    if debug: print(f"Orig min max: {x_axis_min_val} {x_axis_max_val}")
    if x_axis_min_val == x_axis_max_val:
        my_val = x_axis_min_val
        if my_val < 0:
            x_axis_min_val = 1.1 * my_val
            x_axis_max_val = 0
        elif my_val == 0:
            x_axis_min_val = -1
            x_axis_max_val = 1
        elif my_val > 0:
            x_axis_min_val = 0
            x_axis_max_val = 1.1 * my_val
    elif x_axis_min_val >= 0 and x_axis_max_val >= 0:  ## both +ve
        """
        Snap min to 0 if gap small rel to range, otherwise make min y-axis just
        below min point. Make max y-axis just above the max point. Make the
        padding from 0 the lesser of 0.1 of axis_min and 0.1 of val_range. The
        outer padding can be the lesser of the axis_max and 0.1 of val_range.
        """
        gap = x_axis_min_val
        val_range = (x_axis_max_val - x_axis_min_val)
        try:
            gap2range = gap / (val_range * 1.0)
            if gap2range < 0.6:  ## close enough to snap to 0
                x_axis_min_val = 0
            else:  ## can't just be 0.9 min - e.g. looking at years from 2000-2010 would be 1800 upwards!
                x_axis_min_val -= min(0.1 * gap, 0.1 * val_range)  ## gap is never 0 and is at least 0.6 of valrange
        except ZeroDivisionError:
            pass
        x_axis_max_val += min(0.1 * x_axis_max_val, 0.1 * val_range)
    elif x_axis_min_val <= 0 and x_axis_max_val <= 0:  ## both -ve
        """
        Snap max to 0 if gap small rel to range, otherwise make max y-axis just
        above max point. Make min y-axis just below min point. Make the padding
        the lesser of 0.1 of gap and 0.1 of val_range.
        """
        gap = abs(x_axis_max_val)
        val_range = abs(x_axis_max_val - x_axis_min_val)
        try:
            gap2range = gap / (val_range * 1.0)
            if gap2range < 0.6:
                x_axis_max_val = 0
            else:
                x_axis_max_val += min(0.1 * gap, 0.1 * val_range)
        except ZeroDivisionError:
            pass
        x_axis_min_val -= min(0.1 * abs(x_axis_min_val), 0.1 * val_range)  ## make even more negative, but by the least possible
    elif x_axis_min_val <= 0 <= x_axis_max_val:  ## spanning y-axis (even if all 0s ;-))
        """
        Pad min with 0.1 * x_axis_min_val. No harm if 0.
        Pad max - no harm if 0.
        """
        x_axis_min_val = 1.1 * x_axis_min_val
        x_axis_max_val = 1.1 * x_axis_max_val
    else:
        pass
    if debug: print(f"Final {x_axis_min_val=}; Final {x_axis_max_val=}")
    return x_axis_min_val, x_axis_max_val

def get_p_str(p: float) -> str:
    """
    Get a nice representation of p value including significance if relevant.
    """
    p_str = to_precision(num=p, precision=4)
    if p < 0.001:
        p_str = f'< 0.001 ({p_str})'
    return p_str

def get_obriens_msg(samples_vals: Sequence[Sequence[float]], sim_variance_fn: Callable, *,
        high=False, debug=False) -> str:
    try:
        ## sim_variance threshold parameter not used or relevant because ignoring is_similar part of output
        _is_similar, p_sim = sim_variance_fn(samples_vals, high=high)
        obriens_msg = get_p_str(p_sim)
    except Exception as e:
        if debug: print(f"Unable to calculate O'Briens test for homogeneity of variance.\nOrig error: {e}")
        obriens_msg = "Unable to calculate O'Briens test for homogeneity of variance"
    return obriens_msg
