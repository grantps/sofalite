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
from sofalite.output.utils import format_num, get_p
from sofalite.stats_calc.interfaces import ChiSquareResult, ChiSquareWorkedResultData

def get_observed_vs_expected_tbl(
            variable_name_a: str, variable_name_b: str,
            variable_a_values: Sequence[int | str], variable_b_values: Sequence[int | str],
            observed_values_a_then_b_ordered: Sequence[float],
            expected_values_a_then_b_ordered: Sequence[float],
            style_name_hyphens: str,
        ) -> str:

    ## output.styles.utils.get_styled_stats_tbl_css controls the styles that will apply to these classes
    css_datacell = f"datacell-{style_name_hyphens}"
    css_spaceholder = f"spaceholder-{style_name_hyphens}"
    css_first_col_var = f"firstcolvar-{style_name_hyphens}"
    css_first_row_var = f"firstrowvar-{style_name_hyphens}"
    css_row_val = f"rowval-{style_name_hyphens}"
    cells_per_col = 2  ## obs, exp

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
    html.append(f"\n<tr><th class='{css_spaceholder}' colspan=2 rowspan=3></th>")
    colspan2use = (n_variable_b_values + 1) * cells_per_col
    html.append(f"<th class='{css_first_col_var}' colspan={colspan2use}>{variable_label_b_html}</th></tr>")
    html.append('\n<tr>')
    for val in variable_b_labels_html:
        html.append(f'<th colspan={cells_per_col}>{val}</th>')
    html.append(f"<th colspan={cells_per_col}>TOTAL</th></tr>\n<tr>")
    for _val in range(n_variable_b_values + 1):
        html.append("<th>Obs</th><th>Exp</th>")
    html.append("</tr>")
    ## body
    html.append("\n\n</thead><tbody>")
    item_i = 0
    html.append(f"\n<tr><td class='{css_first_row_var}' rowspan={n_variable_a_values + 1}>{variable_label_a_html}</td>")
    col_obs_tots = [0, ] * n_variable_b_values
    col_exp_tots = [0, ] * n_variable_b_values
    ## total row totals
    row_obs_tot_tot = 0
    row_exp_tot_tot = 0
    for val_a in variable_a_labels_html:
        row_obs_tot = 0
        row_exp_tot = 0
        html.append(f"<td class='{css_row_val}'>{val_a}</td>")
        for col_i, unused in enumerate(variable_b_labels_html):
            obs = observed_values_a_then_b_ordered[item_i]
            exp = expected_values_a_then_b_ordered[item_i]
            html.append(f"<td class='{css_datacell}'>{obs}</td><td class='{css_datacell}'>{round(exp, 1)}</td>")
            row_obs_tot += obs
            row_exp_tot += exp
            col_obs_tots[col_i] += obs
            col_exp_tots[col_i] += exp
            item_i += 1
        ## add total for row
        row_obs_tot_tot += row_obs_tot
        row_exp_tot_tot += row_exp_tot
        html.append(f"<td class='{css_datacell}'>"
            + f"{row_obs_tot}</td><td class='{css_datacell}'>"
            + f'{round(row_exp_tot, 1)}</td>')
        html.append('</tr>\n<tr>')
    ## add totals row
    col_tots = zip(col_obs_tots, col_exp_tots)
    html.append(f"<td class='{css_row_val}'>TOTAL</td>")
    for col_obs_tot, col_exp_tot in col_tots:
        html.append(f"<td class='{css_datacell}'>{col_obs_tot}</td>"
            f"<td class='{css_datacell}'>{round(col_exp_tot, 1)}</td>")
    ## add total of totals
    tot_tot_str = round(row_exp_tot_tot, 1)
    html.append(f"<td class='{css_datacell}'>{row_obs_tot_tot}</td><td class='{css_datacell}'>{tot_tot_str}</td>")
    html.append('</tr>')
    html.append(f'\n</tbody>\n</table>\n')
    return '\n'.join(html)

def get_worked_example(worked_result_data: ChiSquareWorkedResultData) -> str:
    html = []
    html.append("""
    <hr>
    <h2>Worked Example of Key Calculations</h2>
    <h3>Step 1 - Calculate row and column sums</h3>""")
    html.append('<h4>Row sums</h4>')
    for row_n in range(1, worked_result_data.row_n + 1):
        vals_added = ' + '.join(format_num(x) for x in worked_result_data.row_n2obs_row[row_n])
        row_sums = format_num(worked_result_data.row_n2row_sum[row_n])
        html.append(f"""
        <p>Row {row_n} Total: {vals_added} = <strong>{row_sums}</strong></p>
        """)
    html.append('<h4>Column sums</h4>')
    for col_n in range(1, worked_result_data.col_n + 1):
        vals_added = ' + '.join(format_num(x) for x in worked_result_data.col_n2obs_row[col_n])
        col_sums = format_num(worked_result_data.col_n2col_sum[col_n])
        html.append(f"""
        <p>Col {col_n} Total: {vals_added} = <strong>{col_sums}</strong></p>
        """)
    html.append("""
    <h3>Step 2 - Calculate expected values per cell</h3>
    <p>Multiply row and column sums for cell and divide by grand total
    </p>""")
    for coord, cell_data in worked_result_data.cells_data.items():
        row_n, col_n = coord
        row_sum = format_num(cell_data.row_sum)
        col_sum = format_num(cell_data.col_sum)
        grand_tot = format_num(worked_result_data.grand_tot)
        expected = format_num(cell_data.expected_value)
        html.append(f"""<p>Row {row_n}, Col {col_n}: ({row_sum} x {col_sum})
        /{grand_tot} = <strong>{expected}</strong></p>""")
    html.append("""
    <h3>Step 3 - Calculate the differences between observed and expected per
    cell, square them, and divide by expected value</h3>""")
    for coord, cell_data in worked_result_data.cells_data.items():
        row_n, col_n = coord
        larger = format_num(cell_data.max_of_observed_and_expected)
        smaller = format_num(cell_data.min_of_observed_and_expected)
        expected = format_num(cell_data.expected_value)
        diff = format_num(cell_data.expected_value)
        diff_squ = format_num(cell_data.diff_squared)
        pre_chi = format_num(cell_data.pre_chi)
        html.append(f"""
        <p>Row {row_n}, Col {col_n}:
        ({larger} - {smaller})<sup>2</sup> / {expected}
        = ({diff})<sup>2</sup> / {expected}
        = {diff_squ} / {expected}
        = <strong>{pre_chi}</strong></p>""")
    html.append(
        '<h3>Step 4 - Add up all the results to get Χ<sup>2</sup></h3>')
    vals_added = ' + '.join(str(x) for x in worked_result_data.pre_chis)
    html.append(
        f'<p>{vals_added} = <strong>{worked_result_data.chi_square}</strong></p>')
    row_n = worked_result_data.row_n
    col_n = worked_result_data.col_n
    row_n_minus_1 = worked_result_data.row_n_minus_1
    col_n_minus_1 = worked_result_data.col_n_minus_1
    degrees_of_freedom = worked_result_data.degrees_of_freedom
    html.append(f"""
    <h3>Step 5 - Calculate degrees of freedom</h3>
    <p>N rows - 1 multiplied by N columns - 1</p>
    <p>({row_n} - 1) x ({col_n} - 1) = {row_n_minus_1} x {col_n_minus_1}
    = <strong>{degrees_of_freedom}</strong></p>""")
    html.append("""<p>The only remaining question is the probability of a
        Chi Square value that size occurring for a given degrees of freedom
        value</p>""")
    return '\n'.join(html)

def get_chi_square_charts() -> str:
    """
    def add_chi_square_clustered_barcharts(grid_bg, bar_colours, line_colour,
            lst_obs, var_label_a, var_label_b, val_labels_a, val_labels_b,
            val_labels_b_n, report_fpath, html, *, add_to_report):
        ## NB list_obs is bs within a and we need the other way around
        ## width = 7
        n_clusters = len(val_labels_b)
        if n_clusters < 8:
            width = 7
            height = None  ## allow height to be set by golden ratio
        else:
            width = n_clusters*1.5
            height = 4.5
        rows_n = int(len(lst_obs) / val_labels_b_n)
        cols_n = val_labels_b_n
        bs_in_as = np.array(lst_obs).reshape(rows_n, cols_n)
        as_in_bs_lst = bs_in_as.transpose().tolist()
        ## proportions of b within a
        propns_bs_in_as = []
        ## expected propn bs in as - so we have a reference to compare rest to
        total = sum(lst_obs)
        expected_propn_bs_in_as = []
        for as_in_b_lst in as_in_bs_lst:
            expected_propn_bs_in_as.append(float(sum(as_in_b_lst))/float(total))
        propns_bs_in_as.append(expected_propn_bs_in_as)
        ## actual observed bs in as
        bs_in_as_lst = bs_in_as.tolist()
        for bs in bs_in_as_lst:
            propns_lst = []
            for b in bs:
                propns_lst.append(float(b)/float(sum(bs)))
            propns_bs_in_as.append(propns_lst)
        propns_as_in_bs_lst = np.array(propns_bs_in_as).transpose().tolist()
        logging.debug(lst_obs)
        logging.debug(bs_in_as)
        logging.debug(as_in_bs_lst)
        logging.debug(bs_in_as_lst)
        title_tmp = _("%(laba)s and %(labb)s - %(y)s")
        title_overrides = {'fontsize': 14}
        ## chart 1 - proportions ****************************************************
        plot = boomslang.Plot()
        y_label = _('Proportions')
        title = title_tmp % {'laba': var_label_a, 'labb': var_label_b, 'y': y_label}
        plot.setTitle(title)
        plot.setTitleProperties(title_overrides)
        plot.setDimensions(width, height)
        plot.hasLegend(columns=val_labels_b_n, location='lower left')
        plot.setAxesLabelSize(11)
        plot.setXTickLabelSize(get_xaxis_fontsize(val_labels_a))
        plot.setLegendLabelSize(9)
        val_labels_a_with_ref = val_labels_a[:]
        val_labels_a_with_ref.insert(0, 'All\ncombined')
        logging.debug(grid_bg)
        logging.debug(bar_colours)
        logging.debug(line_colour)
        logging.debug(var_label_a)
        logging.debug(y_label)
        logging.debug(val_labels_a_with_ref)
        logging.debug(val_labels_b)
        logging.debug(propns_as_in_bs_lst)
        charting_pylab.config_clustered_barchart(grid_bg, bar_colours,
            plot, var_label_a, y_label, val_labels_a_with_ref, val_labels_b,
            propns_as_in_bs_lst)
        img_src = charting_pylab.save_report_img(add_to_report, report_fpath,
            save_func=plot.save, dpi=None)
        html.append(f'\n{mg.IMG_SRC_START}{img_src}{mg.IMG_SRC_END}')
        output.append_divider(html, title, indiv_title='proportion')
        ## chart 2 - freqs **********************************************************
        plot = boomslang.Plot()
        y_label = _('Frequencies')
        title = title_tmp % {'laba': var_label_a, 'labb': var_label_b, 'y': y_label}
        plot.setTitle(title)
        plot.setTitleProperties(title_overrides)
        plot.setDimensions(width, height)
        plot.hasLegend(columns=val_labels_b_n, location='lower left')
        plot.setAxesLabelSize(11)
        plot.setXTickLabelSize(get_xaxis_fontsize(val_labels_a))
        plot.setLegendLabelSize(9)
        ## only need 6 because program limits to that. See core_stats.get_obs_exp().
        charting_pylab.config_clustered_barchart(grid_bg, bar_colours,
            plot, var_label_a, y_label, val_labels_a, val_labels_b, as_in_bs_lst)
        img_src = charting_pylab.save_report_img(add_to_report, report_fpath,
            save_func=plot.save, dpi=None)
        html.append(f'\n{mg.IMG_SRC_START}{img_src}{mg.IMG_SRC_END}')
        output.append_divider(html, title, indiv_title='frequency')

    css_dojo_dic = lib.OutputLib.extract_dojo_style(css_fpath)
    item_colours = output.colour_mappings_to_item_colours(
        css_dojo_dic['colour_mappings'])
    output.append_divider(html, title, indiv_title='')
    add_chi_square_clustered_barcharts(css_dojo_dic['plot_bg'], item_colours,
        css_dojo_dic['major_gridline_colour'], lst_obs, var_label_a,
        var_label_b, val_labels_a, val_labels_b, val_labels_b_n,
        report_fpath, html, add_to_report=add_to_report)
    """
    return ''

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

    {% if worked_example %}
      {{ worked_example }}
    {% endif %}

    <hr><p>Interpreting the Proportions chart - look at the "All combined" category - the more different the other
    '{{ variable_label_a }}' categories look from this the more likely the Chi Square test will detect a difference.
    Within each '{{ variable_label_a }}' category the '{{ variable_label_b }}' values add up to 1 i.e. 100%.
    This is not the same way of displaying data as a clustered bar chart although the similarity can be confusing.</p>

    {{ chi_square_charts }}   
    
    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    variable_label_a = VAR_LABELS.var2var_lbl.get(result.variable_name_a, result.variable_name_a)
    variable_label_b = VAR_LABELS.var2var_lbl.get(result.variable_name_b, result.variable_name_b)
    title = (f"Results of Pearson's Chi Square Test of Association Between "
        f'"{variable_label_a}" and "{variable_label_b}"')
    worked_example = get_worked_example(result.chi_square_worked_result_data) if show_workings else ''
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
    chi_square_charts = get_chi_square_charts()
    context = {
        'chi_square_charts': chi_square_charts,  ## TODO: make binary of charts and embed
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
        'variable_label_a': variable_label_a,
        'variable_label_b': variable_label_b,
        'worked_example': worked_example,
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
        ## data
        results = get_results(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_name_a=self.variable_name_a, variable_name_b=self.variable_name_b,
            show_workings=self.show_workings)
        html = make_chi_square_html(results, style_spec, dp=self.dp, show_workings=self.show_workings)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
