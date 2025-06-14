import base64
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import Any

import jinja2

from sofalite.conf.main import VAR_LABELS
from sofalite.data_extraction.stats.spearmansr import get_worked_result_data
from sofalite.data_extraction.utils import get_paired_data
from sofalite.output.stats.common import get_optimal_min_max
from sofalite.output.charts.mpl_pngs import get_scatterplot_fig
from sofalite.output.charts.scatterplot import Coord, ScatterplotConf, ScatterplotSeries
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_style_spec
from sofalite.output.utils import get_p_explain, get_two_tailed_explanation_rel
from sofalite.stats_calc.engine import get_regression_result, spearmansr
from sofalite.stats_calc.interfaces import CorrelationResult
from sofalite.utils.maths import format_num
from sofalite.utils.misc import pluralise_with_s
from sofalite.utils.stats import get_p_str

def get_worked_example(results: CorrelationResult, style_name_hyphens: str) -> str:
    row_or_rows_str = partial(pluralise_with_s, 'row')
    css_first_row_var = f"firstrowvar-{style_name_hyphens}"
    html = [(f"""<hr>
    <h2>Worked Example of Key Calculations</h2>
    <h3>Step 1 - Set up table of paired results</h3>
    <table>
    <thead>
      <tr>
          <th class='{css_first_row_var}'>{results.variable_a_label}</th>
          <th class='{css_first_row_var}'>{results.variable_b_label}</th>
      </tr>
    </thead>
    <tbody>""")]
    max_display_rows = 50
    init_tbl = results.worked_result.initial_tbl
    for row in init_tbl[:max_display_rows]:
        html.append(f"<tr><td>{row.x}</td><td>{row.y}</td></tr>")
    diff_init = len(init_tbl) - max_display_rows
    if diff_init > 0:
        html.append(f"<tr><td colspan='2'>{format_num(diff_init)} {row_or_rows_str(diff_init)} not displayed</td></tr>")
    html.append('</tbody></table>')
    html.append(f"""
      <h3>Step 2 - Work out ranks for the x and y values</h3>
      <p>Rank such that all examples of a value get the mean rank for all
      items of that value</p>
      <table>
      <thead>
          <tr>
          <th class='{css_first_row_var}'>{results.variable_a_label}</th>
          <th class='{css_first_row_var}'>Rank within<br>{results.variable_b_label}</th></tr>
      </thead>
      <tbody>""")
    x_ranked = results.worked_result.x_and_rank
    for x, x_rank in x_ranked[:max_display_rows]:
        html.append(f'<tr><td>{x}</td><td>{x_rank}</td></tr>')
    diff_x_ranked = len(x_ranked) - max_display_rows
    if diff_x_ranked > 0:
        html.append(
            f"<tr><td colspan='2'>{format_num(diff_x_ranked)} {row_or_rows_str(diff_x_ranked)} not displayed</td></tr>")
    html.append('</tbody></table>')
    html.append(f"""
      <p>Do the same for {results.variable_b_label} values</p>
      <table>
      <thead>
          <tr>
            <th class='{css_first_row_var}'>{results.variable_b_label}</th>
            <th class='{css_first_row_var}'>Rank within<br>{results.variable_b_label}</th>
          </tr>
      </thead>
      <tbody>""")
    y_ranked = results.worked_result.y_and_rank
    for y, y_rank in y_ranked[:max_display_rows]:
        html.append(f'<tr><td>{y}</td><td>{y_rank}</td></tr>')
    diff_y_ranked = len(y_ranked) - max_display_rows
    if diff_y_ranked > 0:
        html.append(
            f"<tr><td colspan='2'>{format_num(diff_y_ranked)} {row_or_rows_str(diff_y_ranked)} not displayed</td></tr>")
    html.append('</tbody></table>')
    html.append(f"""
      <h3>Step 3 - Add ranks to original table or pairs</h3>
      <table>
      <thead>
          <tr>
              <th class='{css_first_row_var}'>{results.variable_a_label}</th>
              <th class='{css_first_row_var}'>{results.variable_b_label}</th>
              <th class='{css_first_row_var}'>{results.variable_a_label} Ranks</th>
              <th class='{css_first_row_var}'>{results.variable_b_label} Ranks</th>
          </tr>
      </thead>
      <tbody>""")
    for row in init_tbl[:max_display_rows]:
        html.append(f"<tr><td>{row.x}</td><td>{row.y}</td><td>{row.rank_x}</td><td>{row.rank_y}</td></tr>")
    if diff_init > 0:
        html.append(f"<tr><td colspan='4'>{format_num(diff_init)} {row_or_rows_str(diff_init)} not displayed</td></tr>")
    html.append('</tbody></table>')
    html.append(f"""
      <h3>Step 4 - Add difference in ranks and get square of diff</h3>
      <table>
      <thead>
          <tr>
              <th class='{css_first_row_var}'>{results.variable_a_label}</th>
              <th class='{css_first_row_var}'>{results.variable_b_label}</th>
              <th class='{css_first_row_var}'>{results.variable_a_label} Ranks</th>
              <th class='{css_first_row_var}'>{results.variable_b_label} Ranks</th>
              <th class='{css_first_row_var}'>Difference</th>
              <th class='{css_first_row_var}'>Diff Squared</th>
          </tr>
      </thead>
      <tbody>""")
    for row in init_tbl[:max_display_rows]:
        html.append(f"""<tr>
              <td>{row.x}</td>
              <td>{row.y}</td>
              <td>{row.diff}</td>
              <td>{row.rank_x}</td>
              <td>{row.rank_y}</td>
              <td>{row.diff_squared}</td>
          </tr>""")
    if diff_init > 0:
        html.append(f"<tr><td colspan='6'>{format_num(diff_init)} {row_or_rows_str(diff_init)} not displayed</td></tr>")
    html.append('</tbody></table>')
    n = format_num(results.worked_result.n_x)
    n_cubed_minus_n = format_num(results.worked_result.n_cubed_minus_n)
    html.append(f"""
      <h3>Step 5 - Count N pairs, cube it, and subtract N</h3>
      N = {n}<br>N<sup>3</sup> - N = {n_cubed_minus_n}""")
    tot_d_squared = format_num(results.worked_result.tot_d_squared)
    tot_d_squared_minus_6 = format_num(results.worked_result.tot_d_squared_x_6)
    n_cubed_minus_n = format_num(results.worked_result.n_cubed_minus_n)
    pre_rho = format_num(results.worked_result.pre_rho)
    rho = results.worked_result.rho
    html.append(f"""
      <h3>Step 6 - Total squared diffs, multiply by 6, divide by N<sup>3</sup> -
      N value</h3>
      Total squared diffs = {tot_d_squared}
      <br>Multiplied by 6 = {tot_d_squared_minus_6}<br>
      Divided by N<sup>3</sup> - N value ({n_cubed_minus_n}) = {pre_rho}
      """)
    html.append(f"""
      <h3>Step 7 - Subtract from 1 to get Spearman's rho</h3>
      rho = 1 - {pre_rho} = {rho} (all rounded to 4dp)""")
    html.append(
        "<p>The only remaining question is the probability of a rho that size occurring for a given N value</p>")
    return '\n'.join(html)

def make_spearmansr_html(results: CorrelationResult, style_spec: StyleSpec, *, dp: int, show_workings=False) -> str:
    tpl = """\
    <h2>{{ title }}</h2>

    <p>Two-tailed p value: {{ p_str }} <a href='#ft1'><sup>1</sup></a></p>

    <p>Spearman's R statistic: {{ spearmans_r_rounded }}</p>

    <p>{{ degrees_of_freedom_msg }}</p>

    <p>Linear Regression Details: <a href='#ft2'><sup>2</sup></a></p>

    <ul>
        <li>Slope: {{ slope_rounded }}</li>
        <li>Intercept: {{ intercept_rounded }}</li>
    </ul>

    {{ scatterplot_html }}

    {% if worked_example %}
      {{ worked_example }}
    {% endif %}

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}
    """
    title = ('''Results of Spearman's Test of Linear Correlation for '''
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

    worked_example = get_worked_example(results, style_spec.style_name_hyphens) if show_workings else ''

    context = {
        'degrees_of_freedom_msg': degrees_of_freedom_msg,
        'footnotes': [p_full_explanation, look_at_scatterplot_msg],
        'intercept_rounded': intercept_rounded,
        'p_str': p_str,
        'pearsons_r_rounded': pearsons_r_rounded,
        'scatterplot_html': scatterplot_html,
        'slope_rounded': slope_rounded,
        'title': title,
        'worked_example': worked_example,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class SpearmansRSpec(Source):
    style_name: str
    variable_a_name: str
    variable_b_name: str
    dp: int = 3
    show_workings: bool = False

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
        pearsonsr_calc_result = spearmansr(paired_data.variable_a_vals, paired_data.variable_b_vals)
        regression_result = get_regression_result(xs=paired_data.variable_a_vals,ys=paired_data.variable_b_vals)

        if self.show_workings:
            spearmansr_worked_result_data = get_worked_result_data(
                variable_a_values=paired_data.variable_a_vals,
                variable_b_values=paired_data.variable_b_vals,
            )
        else:
            spearmansr_worked_result_data = None
        results = CorrelationResult(
            variable_a_label=variable_a_label,
            variable_b_label=variable_b_label,
            coords=coords,
            stats_result=pearsonsr_calc_result,
            regression_result=regression_result,
            worked_result=spearmansr_worked_result_data,
        )
        html = make_spearmansr_html(results, style_spec, dp=self.dp, show_workings=self.show_workings)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
