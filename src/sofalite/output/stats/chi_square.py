from collections.abc import Sequence
from dataclasses import dataclass
from html import escape as html_escape
from pathlib import Path
from typing import Any

import jinja2

from sofalite.conf.main import VAR_LABELS
from sofalite.data_extraction.stats.chi_square import get_results
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofalite.output.utils import get_p
from sofalite.stats_calc.interfaces import ChiSquareResult

def get_observed_vs_expected_tbl(
            variable_name_a: str, variable_name_b: str,
            variable_a_values: Sequence[int | str], variable_b_values: Sequence[int | str],
            observed_values_a_then_b_ordered: Sequence[float],
            expected_values_a_then_b_ordered: Sequence[float],
            style_name_hyphens: str,
        ) -> str:

    ## TODO: use appropriate CSS classes as per new-style tables (albeit not pandas-generated) - uuids?
    ## output.styles.utils.get_styled_stats_tbl_css controls the styles that will apply to these classes
    CSS_DATACELL = f"datacell-{style_name_hyphens}"
    CSS_SPACEHOLDER = f"spaceholder-{style_name_hyphens}"
    CSS_FIRST_COL_VAR = f"firstcolvar-{style_name_hyphens}"
    CSS_FIRST_ROW_VAR = f"firstrowvar-{style_name_hyphens}"
    CSS_ROW_VAL = f"rowval-{style_name_hyphens}"

    CELLS_PER_COL = 2  ## obs, exp

    variable_label_a = VAR_LABELS.var2var_lbl.get(variable_name_a, variable_name_a)
    variable_label_b = VAR_LABELS.var2var_lbl.get(variable_name_b, variable_name_b)
    variable_label_a_html = html_escape(variable_label_a)
    variable_label_b_html = html_escape(variable_label_b)
    val2lbl_for_var_a = VAR_LABELS.var2val2lbl.get(variable_name_a, {})
    variable_a_labels = [val2lbl_for_var_a[val_a] for val_a in variable_a_values]
    val2lbl_for_var_b = VAR_LABELS.var2val2lbl.get(variable_name_b, {})
    variable_b_labels = [val2lbl_for_var_b[val_b] for val_b in variable_b_values]
    try:
        variable_a_labels_html = list(map(html_escape, variable_a_labels))
        variable_b_labels_html = list(map(html_escape, variable_b_labels))
    except AttributeError:
        ## e.g. an int
        variable_a_labels_html = variable_a_labels
        variable_b_labels_html = variable_b_labels

    n_variable_a_values = len(variable_a_values)
    n_variable_b_values = len(variable_b_values)

    html = []
    html.append(f"\n\n<table cellspacing='0'>\n<thead>")
    html.append(f"\n<tr><th class='{CSS_SPACEHOLDER}' colspan=2 rowspan=3></th>")
    colspan2use = (n_variable_b_values + 1) * CELLS_PER_COL
    html.append(f"<th class='{CSS_FIRST_COL_VAR}' colspan={colspan2use}>{variable_label_b_html}</th></tr>")
    html.append('\n<tr>')
    for val in variable_b_labels_html:
        html.append(f'<th colspan={CELLS_PER_COL}>{val}</th>')
    html.append(f"<th colspan={CELLS_PER_COL}>TOTAL</th></tr>\n<tr>")
    for _val in range(n_variable_b_values + 1):
        html.append("<th>Obs</th><th>Exp</th>")
    html.append("</tr>")
    ## body
    html.append("\n\n</thead><tbody>")
    item_i = 0
    html.append(f"\n<tr><td class='{CSS_FIRST_ROW_VAR}' rowspan={n_variable_a_values + 1}>{variable_label_a_html}</td>")
    col_obs_tots = [0, ] * n_variable_b_values
    col_exp_tots = [0, ] * n_variable_b_values
    ## total row totals
    row_obs_tot_tot = 0
    row_exp_tot_tot = 0
    for val_a in variable_a_labels_html:
        row_obs_tot = 0
        row_exp_tot = 0
        html.append(f"<td class='{CSS_ROW_VAL}'>{val_a}</td>")
        for col_i, unused in enumerate(variable_b_labels_html):
            obs = observed_values_a_then_b_ordered[item_i]
            exp = expected_values_a_then_b_ordered[item_i]
            html.append(f"<td class='{CSS_DATACELL}'>{obs}</td><td class='{CSS_DATACELL}'>{round(exp, 1)}</td>")
            row_obs_tot += obs
            row_exp_tot += exp
            col_obs_tots[col_i] += obs
            col_exp_tots[col_i] += exp
            item_i += 1
        ## add total for row
        row_obs_tot_tot += row_obs_tot
        row_exp_tot_tot += row_exp_tot
        html.append(f"<td class='{CSS_DATACELL}'>"
            + f"{row_obs_tot}</td><td class='{CSS_DATACELL}'>"
            + f'{round(row_exp_tot, 1)}</td>')
        html.append('</tr>\n<tr>')
    ## add totals row
    col_tots = zip(col_obs_tots, col_exp_tots)
    html.append(f"<td class='{CSS_ROW_VAL}'>TOTAL</td>")
    for col_obs_tot, col_exp_tot in col_tots:
        html.append(f"<td class='{CSS_DATACELL}'>{col_obs_tot}</td>"
            f"<td class='{CSS_DATACELL}'>{round(col_exp_tot, 1)}</td>")
    ## add total of totals
    tot_tot_str = round(row_exp_tot_tot, 1)
    html.append(f"<td class='{CSS_DATACELL}'>{row_obs_tot_tot}</td><td class='{CSS_DATACELL}'>{tot_tot_str}</td>")
    html.append('</tr>')
    html.append(f'\n</tbody>\n</table>\n')
    return '\n'.join(html)

def get_worked_example() -> str:
    html = []
    html.append("""
    <hr>
    <h2>Worked Example of Key Calculations</h2>
    <h3>Step 1 - Calculate row and column sums</h3>""")
    html.append('<h4>Row sums</h4>')
    for row_n in range(1, details[mg.CHI_ROW_N] + 1):
        vals_added = ' + '.join(lib.formatnum(x) for x
            in details[mg.CHI_ROW_OBS][row_n])
        row_sums = lib.formatnum(details[mg.CHI_ROW_SUMS][row_n])
        html.append(f"""
        <p>Row {row_n} Total: {vals_added} = <strong>{row_sums}</strong></p>
        """)
    html.append('<h4>Column sums</h4>')
    for col_n in range(1, details[mg.CHI_COL_N] + 1):
        vals_added = ' + '.join(lib.formatnum(x) for x
            in details[mg.CHI_COL_OBS][col_n])
        col_sums = lib.formatnum(details[mg.CHI_COL_SUMS][col_n])
        html.append(f"""
        <p>Col {col_n} Total: {vals_added} = <strong>{col_sums}</strong></p>
        """)
    html.append("""
    <h3>Step 2 - Calculate expected values per cell</h3>
    <p>Multiply row and column sums for cell and divide by grand total
    </p>""")
    for coord, cell_data in details[mg.CHI_CELLS_DATA].items():
        row_n, col_n = coord
        row_sum = lib.formatnum(cell_data[mg.CHI_CELL_ROW_SUM])
        col_sum = lib.formatnum(cell_data[mg.CHI_CELL_COL_SUM])
        grand_tot = lib.formatnum(details[mg.CHI_GRAND_TOT])
        expected = lib.formatnum(cell_data[mg.CHI_EXPECTED])
        html.append(f"""<p>Row {row_n}, Col {col_n}: ({row_sum} x {col_sum})
        /{grand_tot} = <strong>{expected}</strong></p>""")
    html.append("""
    <h3>Step 3 - Calculate the differences between observed and expected per
    cell, square them, and divide by expected value</h3>""")
    for coord, cell_data in details[mg.CHI_CELLS_DATA].items():
        row_n, col_n = coord
        larger = lib.formatnum(cell_data[mg.CHI_MAX_OBS_EXP])
        smaller = lib.formatnum(cell_data[mg.CHI_MIN_OBS_EXP])
        expected = lib.formatnum(cell_data[mg.CHI_EXPECTED])
        diff = lib.formatnum(cell_data[mg.CHI_DIFF])
        diff_squ = lib.formatnum(cell_data[mg.CHI_DIFF_SQU])
        pre_chi = lib.formatnum(cell_data[mg.CHI_PRE_CHI])
        html.append(f"""
        <p>Row {row_n}, Col {col_n}:
        ({larger} - {smaller})<sup>2</sup> / {expected}
        = ({diff})<sup>2</sup> / {expected}
        = {diff_squ} / {expected}
        = <strong>{pre_chi}</strong></p>""")
    html.append(
        '<h3>Step 4 - Add up all the results to get Χ<sup>2</sup></h3>')
    vals_added = ' + '.join(str(x) for x in details[mg.CHI_PRE_CHIS])
    html.append(
        f'<p>{vals_added} = <strong>{details[mg.CHI_CHI_SQU]}</strong></p>')
    row_n = details[mg.CHI_ROW_N]
    col_n = details[mg.CHI_COL_N]
    row_n_minus_1 = details[mg.CHI_ROW_N_MINUS_1]
    col_n_minus_1 = details[mg.CHI_COL_N_MINUS_1]
    chi_df = details[mg.CHI_DF]
    html.append(f"""
    <h3>Step 5 - Calculate degrees of freedom</h3>
    <p>N rows - 1 multiplied by N columns - 1</p>
    <p>({row_n} - 1) x ({col_n} - 1) = {row_n_minus_1} x {col_n_minus_1}
    = <strong>{chi_df}</strong></p>""")
    html.append("""<p>The only remaining question is the probability of a
        Chi Square value that size occurring for a given degrees of freedom
        value</p>""")

def make_chi_square_html(result: ChiSquareResult, style_spec: StyleSpec, *, dp: int, show_workings=False) -> str:
    tpl = """\
    <style>
        {{generic_unstyled_css}}
        {{styled_stats_tbl_css}}
    </style>

    <div class='default'>
    <h2>{{ title }}</h2>
    <p>p value {{ p_text }}<a href='#ft1'><sup>1</sup></a></p>

    <p>Pearson's Chi Square statistic: {{ chi_square }}</p>
    <p>Degrees of Freedom (df) {{ degrees_of_freedom }}</p>

    {{ observed_vs_expected_tbl }}

    <p>Minimum expected cell count: {{ min_count_rounded }}</p>
    <p>&#37; cells with expected count < 5: {{ pct_cells_lt_5_rounded }}</p>

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}

    {% if workings %}
      {{ workings }}
    {% endif %}
    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    variable_label_a = VAR_LABELS.var2var_lbl.get(result.variable_name_a, result.variable_name_a)
    variable_label_b = VAR_LABELS.var2var_lbl.get(result.variable_name_b, result.variable_name_b)
    title = (f"Results of Pearson's Chi Square Test of Association Between "
        f'"{variable_label_a}" and "{variable_label_b}"')
    workings = get_worked_example() if show_workings else ''
    p_text = get_p(result.p)
    p_explain = ("If p is small, e.g. less than 0.01, or 0.001, you can assume "
        "the result is statistically significant i.e. there is a relationship "
        f'between "{result.variable_name_a}" and "{result.variable_name_b}". Note: a statistically significant '
        "difference may not necessarily be of any practical significance.")
    one_tail_explain = (
        "This is a one-tailed result i.e. based on the likelihood of a difference in one particular direction")
    chi_square = round(result.chi_square, dp)
    observed_vs_expected_tbl = get_observed_vs_expected_tbl(
        variable_name_a=result.variable_name_a, variable_name_b=result.variable_name_b,
        variable_a_values=result.variable_a_values, variable_b_values=result.variable_b_values,
        observed_values_a_then_b_ordered=result.observed_values_a_then_b_ordered,
        expected_values_a_then_b_ordered=result.expected_values_a_then_b_ordered,
        style_name_hyphens=style_spec.style_name_hyphens,
    )
    min_count_rounded = round(result.minimum_cell_count, dp)
    pct_cells_lt_5_rounded = round(result.pct_cells_lt_5, 1)
    context = {
        'chi_square': chi_square,
        'degrees_of_freedom': result.degrees_of_freedom,
        'footnotes': [p_explain, one_tail_explain],
        'generic_unstyled_css': generic_unstyled_css,
        'min_count_rounded': min_count_rounded,
        'observed_vs_expected_tbl': observed_vs_expected_tbl,
        'p_text': p_text,
        'pct_cells_lt_5_rounded': pct_cells_lt_5_rounded,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,
        'working': workings,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class ChiSquareSpec(Source):
    style_name: str
    variable_name_a: str
    variable_name_b: str
    dp: int

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

        ## data
        results = get_results(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_name_a=self.variable_name_a, variable_name_b=self.variable_name_b, dp=self.dp)
        html = make_chi_square_html(results, style_spec, dp=self.dp, show_workings=False)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
