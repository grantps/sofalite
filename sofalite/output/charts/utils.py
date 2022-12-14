import logging
from typing import Sequence

from sofalite.conf.charting.misc import (
    AVG_CHAR_WIDTH_PIXELS, AVG_LINE_HEIGHT_PIXELS, DOJO_Y_AXIS_TITLE_OFFSET, MAX_SAFE_X_LBL_LEN_PIXELS,
    LeftMarginOffsetDetails)
from sofalite.conf.charting.std_specs import CategorySpec

def get_left_margin_offset(*, width_after_left_margin: float, offsets: LeftMarginOffsetDetails,
        is_multi_chart: bool, y_axis_title_offset: float, rotated_x_lbls: bool) -> int:
    wide = width_after_left_margin > 1_200
    initial_offset = offsets.wide_offset if wide else offsets.initial_offset  ## otherwise gets squeezed out e.g. in pct
    offset = initial_offset + y_axis_title_offset - DOJO_Y_AXIS_TITLE_OFFSET
    offset = offset + offsets.rotate_offset if rotated_x_lbls else offset
    offset = offset + offsets.multi_chart_offset if is_multi_chart else offset
    return offset

def get_x_font_size(*, n_x_items: int, is_multi_chart: bool) -> float:
    if n_x_items <= 5:
        x_font_size = 10
    elif n_x_items > 10:
        x_font_size = 8
    else:
        x_font_size = 9
    x_font_size = x_font_size * 0.75 if is_multi_chart else x_font_size
    return x_font_size

def get_height(*, axis_lbl_drop: float, rotated_x_lbls=False, max_x_axis_lbl_len: float) -> float:
    height = 310
    if rotated_x_lbls:
        height += AVG_CHAR_WIDTH_PIXELS * max_x_axis_lbl_len
    height += axis_lbl_drop  ## compensate for loss of bar display height
    return height

def get_axis_lbl_drop(*, is_multi_chart: bool, rotated_x_lbls: bool, max_x_axis_lbl_lines: int) -> int:
    axis_lbl_drop = 10 if is_multi_chart else 15
    if not rotated_x_lbls:
        extra_lines = max_x_axis_lbl_lines - 1
        axis_lbl_drop += AVG_LINE_HEIGHT_PIXELS * extra_lines
    logging.debug(axis_lbl_drop)
    return axis_lbl_drop

def get_y_axis_title_offset(*, x_axis_title_len: int, rotated_x_lbls=False) -> int:
    """
    Need to shift y-axis title left by y_axis_title_offset if first x-axis label is wide.
    """
    ## 45 is a good total offset with label width of 20
    y_axis_title_offset = DOJO_Y_AXIS_TITLE_OFFSET - 20  ## e.g. 20
    ## first x-axis label adjustment
    horiz_x_lbls = not rotated_x_lbls
    if horiz_x_lbls:
        if x_axis_title_len * AVG_CHAR_WIDTH_PIXELS > MAX_SAFE_X_LBL_LEN_PIXELS:
            lbl_width_shifting = (x_axis_title_len * AVG_CHAR_WIDTH_PIXELS) - MAX_SAFE_X_LBL_LEN_PIXELS
            lbl_shift = lbl_width_shifting / 2  ## half of label goes to the right
            y_axis_title_offset += lbl_shift
    y_axis_title_offset = max([y_axis_title_offset, DOJO_Y_AXIS_TITLE_OFFSET])
    return y_axis_title_offset

def get_x_axis_lbl_dets(x_axis_specs: Sequence[CategorySpec]) -> list[str]:
    """
    Note - can be a risk that a split label for the middle x value
    will overlap with x-axis label below
    """
    lbl_dets = []
    for n, x_axis_spec in enumerate(x_axis_specs, 1):
        lbl_dets.append(f'{{value: {n}, text: "{x_axis_spec.lbl}"}}')
    return lbl_dets

def get_optimal_axis_bounds(axis_min: float, axis_max: float) -> tuple[float, float]:
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
    logging.debug(f"Orig min max: {axis_min} {axis_max}")
    if axis_min == axis_max:
        my_val = axis_min
        if my_val < 0:
            axis_min = 1.1 * my_val
            axis_max = 0
        elif my_val == 0:
            axis_min = -1
            axis_max = 1
        elif my_val > 0:
            axis_min = 0
            axis_max = 1.1 * my_val
    elif axis_min >= 0 and axis_max >= 0:  ## both +ve
        """
        Snap min to 0 if gap small rel to range, otherwise make min y-axis just
        below min point. Make max y-axis just above the max point. Make the
        padding from 0 the lesser of 0.1 of axis_min and 0.1 of val_range. The
        outer padding can be the lesser of the axis_max and 0.1 of val_range.
        """
        gap = axis_min
        val_range = (axis_max - axis_min)
        try:
            gap2range = gap / (val_range * 1.0)
            if gap2range < 0.6:  ## close enough to snap to 0
                axis_min = 0
            else:  ## can't just be 0.9 min - e.g. looking at years from 2000-2010 would be 1800 upwards!
                axis_min -= min(0.1 * gap, 0.1 * val_range)  ## gap is never 0 and is at least 0.6 of valrange
        except ZeroDivisionError:
            pass
        axis_max += min(0.1 * axis_max, 0.1 * val_range)
    elif axis_min <= 0 and axis_max <= 0:  ## both -ve
        """
        Snap max to 0 if gap small rel to range, otherwise make max y-axis just
        above max point. Make min y-axis just below min point. Make the padding
        the lesser of 0.1 of gap and 0.1 of val_range.
        """
        gap = abs(axis_max)
        val_range = abs(axis_max - axis_min)
        try:
            gap2range = gap / (val_range * 1.0)
            if gap2range < 0.6:
                axis_max = 0
            else:
                axis_max += min(0.1 * gap, 0.1 * val_range)
        except ZeroDivisionError:
            pass
        axis_min -= min(0.1 * abs(axis_min), 0.1 * val_range)  ## make even more negative, but by the least possible
    elif axis_min <= 0 <= axis_max:  ## spanning y-axis (even if all 0s ;-))
        """
        Pad max - no harm if 0.
        Pad min with 0.1*axismin. No harm if 0.
        """
        axis_max = 1.1 * axis_max
        axis_min = 1.1 * axis_min
    else:
        pass
    logging.debug(f"Final {axis_min=}; Final {axis_max=}")
    return axis_min, axis_max
