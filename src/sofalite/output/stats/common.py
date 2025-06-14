from collections.abc import Sequence
import base64
from io import BytesIO

from sofalite import logger
from sofalite.output.charts import mpl_pngs
from sofalite.output.charts.histogram import HistogramConf
from sofalite.output.styles.interfaces import ChartStyleSpec

def get_optimal_min_max(*, axis_min, axis_max) -> tuple[float, float]:
    """
    For boxplots and scatterplots.

    Args:
        axis_min -- the minimum y value exactly
        axis_max -- the maximum y value exactly

    Generally, we want box and scatter plots to have y-axes starting from just below the minimum point
    (e.g. lowest outlier).
    That is, avoid the common case where we have the y-axis start at 0, and all our values range tightly together.
    In which case, for boxplots, we will have a series of tiny boxplots up the top,
    and we won't be able to see the different parts of it e.g. LQ, median etc.
    For scatter plots our data will be too tightly scrunched up to see any spread.

    But sometimes the lowest point is not that far above 0, in which case we should set it to 0.
    A 0-based axis is preferable unless the values are a long way away. Going from 0.5-12 is silly.
    Might as well go from 0-12.

    4 scenarios:

    1) min and max are both the same
    Just try to set the max differently to the min so there is a range on the axis to display.
    See implementation for more details.

    2) min and max are both +ve
    |   *
    |
    -------
    Snap min to 0 if gap small rel to range, otherwise make min y-axis just below min point.
    Make max y-axis just above the max point.
    Make the padding from 0 the lesser of 0.1 of axis_min and 0.1 of value_range.
    The outer padding can be the lesser of the axis_max and 0.1 of value_range.

    3) min and max are -ve
    -------
    |   *
    |
    Snap max to 0 if gap small rel to range, otherwise make max y-axis just above max point.
    Make min y-axis just below min point.
    Make the padding the lesser of 0.1 of gap and 0.1 of value_range.

    4) min is -ve and max is +ve
    |   *
    -------
    |   *
    Make max 1.1*axis_max. No harm if 0.
    Make min 1.1*axis_min. No harm if 0.
    """
    logger.debug(f"Orig min max: {axis_min} {axis_max}")
    if axis_min == axis_max:
        my_value = axis_min
        if my_value < 0:
            axis_min = 1.1 * my_value
            axis_max = 0
        elif my_value == 0:
            axis_min = -1
            axis_max = 1
        elif my_value > 0:
            axis_min = 0
            axis_max = 1.1 * my_value
    elif axis_min >= 0 and axis_max >= 0:  ## both +ve
        """
        Snap min to 0 if gap small rel to range, otherwise make min y-axis just below min point.
        Make max y-axis just above the max point.
        Make the padding from 0 the lesser of 0.1 of axis_min and 0.1 of value_range.
        The outer padding can be the lesser of the axis_max and 0.1 of value_range.
        """
        gap = axis_min
        value_range = (axis_max - axis_min)
        try:
            gap2range = gap / (value_range * 1.0)
            if gap2range < 0.6:  ## close enough to snap to 0
                axis_min = 0
            else:  ## can't just be 0.9 min - e.g. looking at years from 2000-2010 would be 1800 upwards!
                axis_min -= min(0.1 * gap, 0.1 * value_range)  ## gap is never 0 and is at least 0.6 of value_range
        except ZeroDivisionError:
            pass
        axis_max += min(0.1 * axis_max, 0.1 * value_range)
    elif axis_min <= 0 and axis_max <= 0:  ## both -ve
        """
        Snap max to 0 if gap small rel to range, otherwise make max y-axis just above max point.
        Make min y-axis just below min point. Make the padding the lesser of 0.1 of gap and 0.1 of value_range.
        """
        gap = abs(axis_max)
        value_range = abs(axis_max - axis_min)
        try:
            gap2range = gap / (value_range * 1.0)
            if gap2range < 0.6:
                axis_max = 0
            else:
                axis_max += min(0.1 * gap, 0.1 * value_range)
        except ZeroDivisionError:
            pass
        axis_min -= min(0.1 * abs(axis_min), 0.1 * value_range)  ## make even more negative, but by the least possible
    elif axis_min <= 0 and axis_max >= 0:  ## spanning y-axis (even if all 0s ;-))
        """
        Pad max with 0.1*axis_max. No harm if 0.
        Pad min with 0.1*axis_min. No harm if 0.
        """
        axis_max = 1.1 * axis_max
        axis_min = 1.1 * axis_min
    else:
        pass
    logger.debug(f"Final axis_min: {axis_min}; Final axis_max {axis_max}")
    return axis_min, axis_max

def get_group_histogram_html(measure_fld_lbl: str, style_spec: ChartStyleSpec,
        var_lbl: str, vals: Sequence[float]) -> str:
    """
    Make histogram image and return its HTML (with embedded image).
    """
    first_colour_mapping = style_spec.colour_mappings[0]
    chart_conf = HistogramConf(
        var_lbl=var_lbl,
        chart_lbl=measure_fld_lbl,
        inner_bg_colour=style_spec.plot_bg_colour,
        bar_colour=first_colour_mapping.main,
        line_colour=style_spec.major_grid_line_colour)
    fig = mpl_pngs.get_histogram_fig(chart_conf, vals)
    fig.set_size_inches((5.0, 3.5))  ## see dpi to get image size in pixels
    b_io = BytesIO()
    fig.savefig(b_io)  ## save to a fake file
    chart_base64 = base64.b64encode(b_io.getvalue()).decode('utf-8')
    html = f'<img src="data:image/png;base64,{chart_base64}"/>'
    return html
