from dataclasses import dataclass
from functools import partial
from typing import Any

import jinja2

from sofalite.conf.main import DATABASE_FOLDER, VAR_LABELS
from sofalite.data_extraction.db import Sqlite
from sofalite.data_extraction.interfaces import ValSpec
from sofalite.data_extraction.stats.msgs import (
    ci_explain, kurtosis_explain,
    normality_measure_explain, obrien_explain, one_tail_explain,
    p_explain_multiple_groups,
    skew_explain, std_dev_explain,
)
from sofalite.data_extraction.stats.ttest_indep import get_results
from sofalite.output.charts import mpl_pngs
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType
from sofalite.output.stats.common import get_group_histogram_html
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofalite.stats_calc.interfaces import NumericSampleSpecFormatted, TTestIndepResultExt
from sofalite.utils.maths import format_num
from sofalite.utils.stats import get_p_str

def make_ttest_indep_html(result: TTestIndepResultExt, style_spec: StyleSpec, *,
        dp: int, show_workings=False) -> str:
    tpl = """\
    <style>
        {{generic_unstyled_css}}
        {{styled_stats_tbl_css}}
    </style>

    <div class='default'>
    <h2>{{title}}</h2>

    <p>p value: {{p}}<a class='tbl-heading-footnote' href='#ft1'><sup>1</sup></a></p>
    <p>t statistic: {{t}}</p>
    <p>Degrees of Freedom (df): {{df}}</p>
    <p>O'Brien's test for homogeneity of variance: {{obriens_msg}}<a href='#ft2'><sup>2</sup></a></p>

    <h3>Group summary details</h3>
    <table cellspacing='0'>
      <thead>
        <tr>
          <th class='firstcolvar'>Group</th>
          <th class='firstcolvar'>N</th>
          <th class='firstcolvar'>Mean</th>
          <th class='firstcolvar'>CI 95%<a class='tbl-heading-footnote' href='#ft3'><sup>3</sup></a></th>
          <th class='firstcolvar'>Standard Deviation<a class='tbl-heading-footnote' href='#ft4'><sup>4</sup></a></th>
          <th class='firstcolvar'>Min</th>
          <th class='firstcolvar'>Max</th>
          <th class='firstcolvar'>Kurtosis<a class='tbl-heading-footnote' href='#ft5'><sup>5</sup></a></th>
          <th class='firstcolvar'>Skew<a class='tbl-heading-footnote' href='#ft6'><sup>6</sup></a></th>
          <th class='firstcolvar'>p abnormal<a class='tbl-heading-footnote' href='#ft7'><sup>7</sup></a></th>
        </tr>
      </thead>
      <tbody>
        {% for group_spec in group_specs %}
          <tr>
            <td class='lbl'>{{group_spec.lbl}}</td>
            <td class='right'>{{group_spec.n}}</td>
            <td class='right'>{{group_spec.mean}}</td>
            <td class='right'>{{group_spec.ci95}}</td>
            <td class='right'>{{group_spec.stdev}}</td>
            <td class='right'>{{group_spec.sample_min}}</td>
            <td class='right'>{{group_spec.sample_max}}</td>
            <td class='right'>{{group_spec.kurtosis}}</td>
            <td class='right'>{{group_spec.skew}}</td>
            <td class='right'>{{group_spec.p}}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><a id='ft1'></a><sup>1</sup>{{p_explain_multiple_groups}}<br><br>{{one_tail_explain}}</p>
    <p><a id='ft2'></a><sup>2</sup>{{obrien_explain}}</p>
    <p><a id='ft3'></a><sup>3</sup>{{ci_explain}}</p>
    <p><a id='ft4'></a><sup>4</sup>{{std_dev_explain}}</p>
    <p><a id='ft5'></a><sup>5</sup>{{kurtosis_explain}}</p>
    <p><a id='ft6'></a><sup>6</sup>{{skew_explain}}</p>
    <p><a id='ft7'></a><sup>7</sup>{{normality_measure_explain}}</p>
    {% for histogram2show in histograms2show %}
      {{histogram2show}}  <!-- either an <img> or an error message <p> -->
    {% endfor %}
    {% if workings_msg %}
      {{workings_msg}}
    {% endif %}
    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec.table)
    title = (f"Results of independent samples t-test of average {result.measure_fld_lbl} "
        f'''for "{result.group_lbl}" groups "{result.group_a_spec.lbl}" and "{result.group_b_spec.lbl}"''')
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    ## format group details needed by second table
    formatted_group_specs = []
    mpl_pngs.set_gen_mpl_settings(axes_lbl_size=10, xtick_lbl_size=8, ytick_lbl_size=8)
    histograms2show = []
    for orig_group_spec in [result.group_a_spec, result.group_b_spec]:
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
            html_or_msg = (
                f"<b>{orig_group_spec.lbl}</b> - unable to display histogram. Reason: {e}")
        else:
            html_or_msg = histogram_html
        histograms2show.append(html_or_msg)
    workings_msg = "<p>No worked example available for this test</p>" if show_workings else ''
    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,
        't': round(result.t, dp),
        'p': get_p_str(result.p),
        'df': result.degrees_of_freedom,
        'obriens_msg': result.obriens_msg,
        'p_explain_multiple_groups': p_explain_multiple_groups,
        'one_tail_explain': one_tail_explain,
        'obrien_explain': obrien_explain,
        'ci_explain': ci_explain,
        'std_dev_explain': std_dev_explain,
        'kurtosis_explain': kurtosis_explain,
        'skew_explain': skew_explain,
        'normality_measure_explain': normality_measure_explain,
        'group_specs': formatted_group_specs,
        'histograms2show': histograms2show,
        'workings_msg': workings_msg,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=True)
class TTestIndepSpec:
    style_name: str
    tbl_name: str
    grouping_fld_name: str
    group_a_val: Any
    group_b_val: Any
    measure_fld_name: str
    tbl_filt_clause: str | None = None
    cur: Any | None = None

    def to_html_spec(self) -> HTMLItemSpec:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        grouping_fld_lbl = VAR_LABELS.var2var_lbl.get(self.grouping_fld_name, self.grouping_fld_name)
        measure_fld_lbl = VAR_LABELS.var2var_lbl.get(self.measure_fld_name, {})
        val2lbl = VAR_LABELS.var2val2lbl.get(self.grouping_fld_name)
        group_a_val_spec = ValSpec(val=self.group_a_val, lbl=val2lbl.get(self.group_a_val, str(self.group_a_val)))
        group_b_val_spec = ValSpec(val=self.group_b_val, lbl=val2lbl.get(self.group_b_val, str(self.group_b_val)))
        ## data
        get_results_for_cur = partial(get_results,
            tbl_name=self.tbl_name, tbl_filt_clause=self.tbl_filt_clause,
            grouping_fld_name=self.grouping_fld_name, grouping_fld_lbl=grouping_fld_lbl,
            group_a_val_spec=group_a_val_spec, group_b_val_spec=group_b_val_spec,
            grouping_val_is_numeric=True,
            measure_fld_name=self.measure_fld_name, measure_fld_lbl=measure_fld_lbl
        )
        local_cur = not bool(self.cur)
        if local_cur:
            with Sqlite(DATABASE_FOLDER) as (_con, cur):
                results = get_results_for_cur(cur)
        else:
            results = get_results_for_cur(self.cur)
        html = make_ttest_indep_html(results, style_spec, dp=3, show_workings=False)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
