from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from sofalite.conf.main import VAR_LABELS
from sofalite.data_extraction.interfaces import ValSpec
from sofalite.data_extraction.stats.anova import get_results
from sofalite.data_extraction.stats.msgs import (
    ci_explain, kurtosis_explain,
    normality_measure_explain, obrien_explain, one_tail_explain,
    p_explain_multiple_groups,
    skew_explain, std_dev_explain,
)
from sofalite.output.charts import mpl_pngs
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofalite.output.stats.common import get_group_histogram_html
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofalite.stats_calc.interfaces import AnovaResultExt, NumericSampleSpecFormatted
from sofalite.utils.maths import format_num, is_numeric
from sofalite.utils.stats import get_p_str

def make_anova_html(result: AnovaResultExt, style_spec: StyleSpec, *, dp: int, show_workings=False) -> str:
    tpl = """\
    <style>
        {{ generic_unstyled_css }}
        {{ styled_stats_tbl_css }}
    </style>

    <div class='default'>
    <h2>{{ title }}</h2>
    <h3>Analysis of variance table</h3>
    <table cellspacing='0'>
    <thead>
      <tr>
        <th class='firstcolvar-{{ style_name_hyphens }}'>Source</th>
        <th class='firstcolvar-{{ style_name_hyphens }}'>Sum of Squares</th>
        <th class='firstcolvar-{{ style_name_hyphens }}'>df</th>
        <th class='firstcolvar-{{ style_name_hyphens }}'>Mean Sum of Squares</th>
        <th class='firstcolvar-{{ style_name_hyphens }}'>F</th>
        <th class='firstcolvar-{{ style_name_hyphens }}'>p<a class='tbl-heading-footnote' href='#ft1'><sup>1</sup></a></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class='lbl-{{ style_name_hyphens }}'>Between</td>
        <td class='right'>{{ sum_squares_between_groups }}</td>
        <td class='right'>{{ degrees_freedom_between_groups }}</td>
        <td class='right'>{{ mean_squares_between_groups }}</td>
        <td class='right'>{{ F }}</td>
        <td>{{p}}</td>
      </tr>
      <tr>
        <td class='lbl-{{ style_name_hyphens }}'>Within</td>
        <td class='right'>{{ sum_squares_within_groups }}</td>
        <td class='right'>{{ degrees_freedom_within_groups }}</td>
        <td class='right'>{{ mean_squares_within_groups }}</td>
        <td></td>
        <td></td>
      </tr>
    </tbody>
    </table>
    <p>O'Brien's test for homogeneity of variance: {{ obriens_msg }}<a href='#ft2'><sup>2</sup></a></p>
    <h3>Group summary details</h3>
    <table cellspacing='0'>
      <thead>
        <tr>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Group</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>N</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Mean</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>CI 95%<a class='tbl-heading-footnote' href='#ft3'><sup>3</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Standard Deviation<a class='tbl-heading-footnote' href='#ft4'><sup>4</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Min</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Max</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Kurtosis<a class='tbl-heading-footnote' href='#ft5'><sup>5</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Skew<a class='tbl-heading-footnote' href='#ft6'><sup>6</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>p abnormal<a class='tbl-heading-footnote' href='#ft7'><sup>7</sup></a></th>
        </tr>
      </thead>
      <tbody>
        {% for group_spec in group_specs %}
          <tr>
            <td class='lbl-{{ style_name_hyphens }}'>{{ group_spec.lbl }}</td>
            <td class='right'>{{ group_spec.n }}</td>
            <td class='right'>{{ group_spec.mean }}</td>
            <td class='right'>{{ group_spec.ci95 }}</td>
            <td class='right'>{{ group_spec.stdev }}</td>
            <td class='right'>{{ group_spec.sample_min }}</td>
            <td class='right'>{{ group_spec.sample_max }}</td>
            <td class='right'>{{ group_spec.kurtosis }}</td>
            <td class='right'>{{ group_spec.skew }}</td>
            <td class='right'>{{ group_spec.p }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><a id='ft1'></a><sup>1</sup>{{ p_explain_multiple_groups }}<br><br>{{one_tail_explain}}</p>
    <p><a id='ft2'></a><sup>2</sup>{{ obrien_explain }}</p>
    <p><a id='ft3'></a><sup>3</sup>{{ ci_explain }}</p>
    <p><a id='ft4'></a><sup>4</sup>{{ std_dev_explain }}</p>
    <p><a id='ft5'></a><sup>5</sup>{{ kurtosis_explain }}</p>
    <p><a id='ft6'></a><sup>6</sup>{{ skew_explain }}</p>
    <p><a id='ft7'></a><sup>7</sup>{{ normality_measure_explain }}</p>
    {% for histogram2show in histograms2show %}
      {{ histogram2show }}  <!-- either an <img> or an error message <p> -->
    {% endfor %}
    {% if workings_msg %}
      {{ workings_msg }}
    {% endif %}
    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    group_vals = [group_spec.lbl for group_spec in result.group_specs]
    if len(group_vals) < 2:
        raise Exception(f"Expected multiple groups in ANOVA. Details:\n{result}")
    group_lbl_a = group_vals[0]
    group_lbl_b = group_vals[-1]
    title = (f"Results of ANOVA test of average {result.measure_fld_lbl} "
        f'''for "{result.group_lbl}" groups from "{group_lbl_a}" to "{group_lbl_b}"''')
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    ## format group details needed by second table
    formatted_group_specs = []
    mpl_pngs.set_gen_mpl_settings(axes_lbl_size=10, xtick_lbl_size=8, ytick_lbl_size=8)
    histograms2show = []
    for orig_group_spec in result.group_specs:
        n = format_num(orig_group_spec.n)
        ci95_left = num_tpl.format(round(orig_group_spec.ci95[0], dp))
        ci95_right = num_tpl.format(round(orig_group_spec.ci95[1], dp))
        ci95 = f"{ci95_left} - {ci95_right}"
        std_dev = num_tpl.format(round(orig_group_spec.std_dev, dp))
        sample_mean = num_tpl.format(round(orig_group_spec.mean, dp))
        kurt = num_tpl.format(round(orig_group_spec.kurtosis, dp))
        skew_val = num_tpl.format(round(orig_group_spec.skew, dp))
        formatted_group_spec = NumericSampleSpecFormatted(
            lbl=orig_group_spec.lbl,
            n=n,
            mean=sample_mean,
            ci95=ci95,
            std_dev=std_dev,
            sample_min=str(orig_group_spec.sample_min),
            sample_max=str(orig_group_spec.sample_max),
            kurtosis=kurt,
            skew=skew_val,
            p=orig_group_spec.p,
        )
        formatted_group_specs.append(formatted_group_spec)
        ## make images
        try:
            histogram_html = get_group_histogram_html(
                result.measure_fld_lbl, style_spec.chart, orig_group_spec.lbl, orig_group_spec.vals)
        except Exception as e:
            html_or_msg = f"<b>{orig_group_spec.lbl}</b> - unable to display histogram. Reason: {e}"
        else:
            html_or_msg = histogram_html
        histograms2show.append(html_or_msg)
    workings_msg = "<p>No worked example available for this test</p>" if show_workings else ''
    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,

        'degrees_freedom_between_groups': f"{result.degrees_freedom_between_groups:,}",
        'F': num_tpl.format(round(result.F, dp)),
        'ci_explain': ci_explain,
        'degrees_freedom_within_groups': f"{result.degrees_freedom_within_groups:,}",
        'group_specs': formatted_group_specs,
        'histograms2show': histograms2show,
        'kurtosis_explain': kurtosis_explain,
        'mean_squares_between_groups': num_tpl.format(round(result.mean_squares_between_groups, dp)),
        'mean_squares_within_groups': num_tpl.format(round(result.mean_squares_within_groups, dp)),
        'normality_measure_explain': normality_measure_explain,
        'obrien_explain': obrien_explain,
        'obriens_msg': result.obriens_msg,
        'one_tail_explain': one_tail_explain,
        'p': get_p_str(result.p),
        'p_explain_multiple_groups': p_explain_multiple_groups,
        'skew_explain': skew_explain,
        'std_dev_explain': std_dev_explain,
        'sum_squares_between_groups': num_tpl.format(round(result.sum_squares_between_groups, dp)),
        'sum_squares_within_groups': num_tpl.format(round(result.sum_squares_within_groups, dp)),
        'workings_msg': workings_msg,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class AnovaSpec(Source):
    style_name: str
    grouping_fld_name: str
    group_vals: Collection[Any]
    measure_fld_name: str

    ## do not try to DRY this repeated code ;-) - see doc string for Source
    csv_fpath: Path | None = None
    csv_separator: str = ','
    overwrite_csv_derived_tbl_if_there: bool = False
    cur: Any | None = None
    dbe_name: str | None = None  ## database engine name
    src_tbl_name: str | None = None
    tbl_filt_clause: str | None = None

    high_precision_required: bool = True
    dp: int = 3

    def to_html_spec(self) -> HTMLItemSpec:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        grouping_fld_lbl = VAR_LABELS.var2var_lbl.get(self.grouping_fld_name, self.grouping_fld_name)
        measure_fld_lbl = VAR_LABELS.var2var_lbl.get(self.measure_fld_name, self.measure_fld_name)
        val2lbl = VAR_LABELS.var2val2lbl.get(self.grouping_fld_name)
        grouping_fld_vals_spec = list({
            ValSpec(val=group_val, lbl=val2lbl.get(group_val, str(group_val))) for group_val in self.group_vals})
        grouping_fld_vals_spec.sort(key=lambda vs: vs.lbl)
        ## data
        grouping_val_is_numeric = all(is_numeric(x) for x in self.group_vals)
        results = get_results(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            grouping_fld_name=self.grouping_fld_name, grouping_fld_lbl=grouping_fld_lbl,
            grouping_fld_vals_spec=grouping_fld_vals_spec,
            grouping_val_is_numeric=grouping_val_is_numeric,
            measure_fld_name=self.measure_fld_name, measure_fld_lbl=measure_fld_lbl,
            high_precision_required=self.high_precision_required)
        html = make_anova_html(results, style_spec, dp=self.dp, show_workings=False)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
