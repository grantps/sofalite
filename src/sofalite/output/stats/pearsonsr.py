import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import jinja2

from sofalite import logger
from sofalite.conf.main import VAR_LABELS
from sofalite.data_extraction.utils import get_paired_data
from sofalite.output.charts.mpl_pngs import get_scatterplot_fig
from sofalite.output.charts.scatterplot import Coord, ScatterplotConf, ScatterplotSeries
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_style_spec
from sofalite.output.utils import get_p_explain, get_two_tailed_explanation_rel
from sofalite.stats_calc.engine import get_regression_result, pearsonr
from sofalite.stats_calc.interfaces import PearsonsRResult
from sofalite.utils.stats import get_p_str

def _get_optimal_min_max(axismin, axismax):
    """
    For boxplots and scatterplots.

    axismin -- the minimum y value exactly
    axismax -- the maximum y value exactly

    Generally, we want box and scatter plots to have y-axes starting from just
    below the minimum point (e.g. lowest outlier). That is avoid the common case
    where we have the y-axis start at 0, and all our values range tightly
    together. In which case, for boxplots, we will have a series of tiny
    boxplots up the top and we won't be able to see the different parts of it
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
    padding from 0 the lesser of 0.1 of axismin and 0.1 of valrange. The
    outer padding can be the lesser of the axismax and 0.1 of valrange.

    3) min and max are -ve
    -------
    |   *
    |
    Snap max to 0 if gap small rel to range, otherwise make max y-axis just
    above max point. Make min y-axis just below min point. Make the
    padding the lesser of 0.1 of gap and 0.1 of valrange.

    4) min is -ve and max is +ve
    |   *
    -------
    |   *
    Make max 1.1*axismax. No harm if 0.
    Make min 1.1*axismin. No harm if 0.
    """
    logger.debug(f"Orig min max: {axismin} {axismax}")
    if axismin == axismax:
        myvalue = axismin
        if myvalue < 0:
            axismin = 1.1 * myvalue
            axismax = 0
        elif myvalue == 0:
            axismin = -1
            axismax = 1
        elif myvalue > 0:
            axismin = 0
            axismax = 1.1 * myvalue
    elif axismin >= 0 and axismax >= 0:  ## both +ve
        """
        Snap min to 0 if gap small rel to range, otherwise make min y-axis just
        below min point. Make max y-axis just above the max point. Make the
        padding from 0 the lesser of 0.1 of axismin and 0.1 of valrange. The
        outer padding can be the lesser of the axismax and 0.1 of valrange.
        """
        gap = axismin
        valrange = (axismax - axismin)
        try:
            gap2range = gap / (valrange * 1.0)
            if gap2range < 0.6:  ## close enough to snap to 0
                axismin = 0
            else:  ## can't just be 0.9 min - e.g. looking at years from 2000-2010 would be 1800 upwards!
                axismin -= min(0.1 * gap, 0.1 * valrange)  ## gap is never 0 and is at least 0.6 of valrange
        except ZeroDivisionError:
            pass
        axismax += min(0.1 * axismax, 0.1 * valrange)
    elif axismin <= 0 and axismax <= 0:  ## both -ve
        """
        Snap max to 0 if gap small rel to range, otherwise make max y-axis just
        above max point. Make min y-axis just below min point. Make the padding
        the lesser of 0.1 of gap and 0.1 of valrange.
        """
        gap = abs(axismax)
        valrange = abs(axismax - axismin)
        try:
            gap2range = gap / (valrange * 1.0)
            if gap2range < 0.6:
                axismax = 0
            else:
                axismax += min(0.1 * gap, 0.1 * valrange)
        except ZeroDivisionError:
            pass
        axismin -= min(0.1 * abs(axismin), 0.1 * valrange)  ## make even more negative, but by the least possible
    elif axismin <= 0 and axismax >= 0:  ## spanning y-axis (even if all 0s ;-))
        """
        Pad max with 0.1*axismax. No harm if 0.
        Pad min with 0.1*axismin. No harm if 0.
        """
        axismax = 1.1 * axismax
        axismin = 1.1 * axismin
    else:
        pass
    logger.debug(f"Final axismin: {axismin}; Final axismax {axismax}")
    return axismin, axismax

def make_pearsonsr_html(results: PearsonsRResult, style_spec: StyleSpec, *, dp: int) -> str:

    line_lst = [results.regression_result.y0, results.regression_result.y1]
    ""
    tpl = """\
    <h2>{{ title }}</h2>

    <p>Two-tailed p value: {{ p_str }} <a href='#ft1'><sup>1</sup></a></p>

    <p>Pearson's R statistic: {{ pearsons_r_rounded }}</p>

    <p>{{ degrees_of_freedom_msg }}</p>

    <p>Linear Regression Details: <a href='#ft2'><sup>2</sup></a></p>

    <ul>
        <li>Slope: {{ slope_rounded }}</li>
        <li>Intercept: {{ intercept_rounded }}</li>
    </ul>

    {{ scatterplot_html }}

    <p>{{ workings_msg }}</p>

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}
    """
    title = ('''Results of Pearson's Test of Linear Correlation for '''
        f'''"{results.variable_a_label}" vs "{results.variable_b_label}"''')
    p_str = get_p_str(results.stats_result.p)
    p_explain = get_p_explain(results.variable_a_label, results.variable_b_label)
    two_tailed_explanation_rel = get_two_tailed_explanation_rel()
    p_full_explanation = f"{p_explain}</br></br>{two_tailed_explanation_rel}"
    pearsons_r_rounded = round(results.stats_result.r, dp)
    degrees_of_freedom_msg = f"Degrees of Freedom (df): {results.stats_result.degrees_of_freedom}"
    look_at_scatterplot_msg = "Always look at the scatter plot when interpreting the linear regression line."
    slope_rounded = round(results.regression_result.slope, dp)
    intercept_rounded = round(results.regression_result.intercept, dp)

    scatterplot_series = ScatterplotSeries(
        label='sausage',
        coords=results.coords,
        dot_colour=style_spec.chart.colour_mappings[0].main,
        dot_line_colour=style_spec.chart.major_grid_line_colour,
        show_regression_details=True,
    )
    vars_series = [scatterplot_series, ]
    xs = results.xs
    x_min, x_max = _get_optimal_min_max(min(xs), max(xs))
    chart_conf = ScatterplotConf(
        width_inches=7.5,
        height_inches=4.0,
        inner_background_colour=style_spec.chart.plot_bg_colour,
        x_axis_label=results.variable_a_label,
        y_axis_label=results.variable_b_label,
        show_dot_lines=True,
        x_min=x_min,
        x_max = x_max,
    )
    fig = get_scatterplot_fig(vars_series, chart_conf)
    b_io = BytesIO()
    fig.savefig(b_io, bbox_inches='tight')  ## save to a fake file
    chart_base64 = base64.b64encode(b_io.getvalue()).decode('utf-8')
    scatterplot_html = f'<img src="data:image/png;base64,{chart_base64}"/>'
    context = {
        'degrees_of_freedom_msg': degrees_of_freedom_msg,
        'footnotes': [p_full_explanation, look_at_scatterplot_msg],
        'intercept_rounded': intercept_rounded,
        'p_str': p_str,
        'pearsons_r_rounded': pearsons_r_rounded,
        'scatterplot_html': scatterplot_html,
        'slope_rounded': slope_rounded,
        'title': title,
        'workings_msg': "No worked example available for this test",
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class PearsonsRSpec(Source):
    style_name: str
    variable_a_name: str
    variable_b_name: str
    dp: int = 3

    ## do not try to DRY this repeated code ;-) - see doc string for Source
    csv_fpath: Path | None = None
    csv_separator: str = ','
    overwrite_csv_derived_tbl_if_there: bool = False
    cur: Any | None = None
    dbe_name: str | None = None  ## database engine name
    src_tbl_name: str | None = None
    tbl_filt_clause: str | None = None

    def to_html_spec(self) -> HTMLItemSpec:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        variable_a_label = VAR_LABELS.var2var_lbl.get(self.variable_a_name, self.variable_a_name)
        variable_b_label = VAR_LABELS.var2var_lbl.get(self.variable_b_name, self.variable_b_name)
        ## data
        paired_data = get_paired_data(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_a_name=self.variable_a_name, variable_b_name=self.variable_b_name,
            tbl_filt_clause=self.tbl_filt_clause)
        coords = [Coord(x=x, y=y) for x, y in zip(paired_data.variable_a_vals, paired_data.variable_b_vals, strict=True)]
        pearsonsr_calc_result = pearsonr(paired_data.variable_a_vals, paired_data.variable_b_vals)
        regression_result = get_regression_result(xs=paired_data.variable_a_vals,ys=paired_data.variable_b_vals)
        results = PearsonsRResult(
            variable_a_label=variable_a_label,
            variable_b_label=variable_b_label,
            coords=coords,
            stats_result=pearsonsr_calc_result,
            regression_result=regression_result,
        )
        html = make_pearsonsr_html(results, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
