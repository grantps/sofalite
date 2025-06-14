import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import jinja2

from sofalite.conf.main import VAR_LABELS
from sofalite.data_extraction.utils import get_paired_data
from sofalite.output.stats.common import get_optimal_min_max
from sofalite.output.charts.mpl_pngs import get_scatterplot_fig
from sofalite.output.charts.scatterplot import Coord, ScatterplotConf, ScatterplotSeries
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_style_spec
from sofalite.output.utils import get_p_explain, get_two_tailed_explanation_rel
from sofalite.stats_calc.engine import get_regression_result, pearsonr
from sofalite.stats_calc.interfaces import CorrelationResult
from sofalite.utils.stats import get_p_str

def make_pearsonsr_html(results: CorrelationResult, style_spec: StyleSpec, *, dp: int) -> str:
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
        coords=results.coords,
        dot_colour=style_spec.chart.colour_mappings[0].main,
        dot_line_colour=style_spec.chart.major_grid_line_colour,
        show_regression_details=True,
    )
    vars_series = [scatterplot_series, ]
    xs = results.xs
    x_min, x_max = get_optimal_min_max(axis_min=min(xs), axis_max=max(xs))
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
        results = CorrelationResult(
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
