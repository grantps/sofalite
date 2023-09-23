import jinja2

from sofalite.conf.stats_output import (
    ci_explain, kurtosis_explain,
    normality_measure_explain, obrien_explain, one_tail_explain,
    p_explain_multiple_groups,
    skew_explain, std_dev_explain,
)
from sofalite.conf.style import StyleSpec
from sofalite.output.charts import mpl_pngs
from sofalite.output.stats.common import get_group_histogram_html
from sofalite.output.styles.misc import get_generic_css, get_styled_dojo_css, get_styled_misc_css
from sofalite.conf.stats_calc import NumericSampleDetsFormatted, TTestIndepResultExt
from sofalite.stats_calc.utils import get_p_str
from sofalite.utils.maths import format_num

def make_ttest_indep_html(results: TTestIndepResultExt, style_spec: StyleSpec, *,
        dp: int, show_workings=False) -> str:
    tpl = """\
    <style>
        {{generic_css}}
        {{styled_misc_css}}
        {{styled_dojo_css}}
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
        {% for group_dets in groups_dets %}
          <tr>
            <td class='lbl'>{{group_dets.lbl}}</td>
            <td class='right'>{{group_dets.n}}</td>
            <td class='right'>{{group_dets.mean}}</td>
            <td class='right'>{{group_dets.ci95}}</td>
            <td class='right'>{{group_dets.stdev}}</td>
            <td class='right'>{{group_dets.sample_min}}</td>
            <td class='right'>{{group_dets.sample_max}}</td>
            <td class='right'>{{group_dets.kurtosis}}</td>
            <td class='right'>{{group_dets.skew}}</td>
            <td class='right'>{{group_dets.p}}</td>
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
    generic_css = get_generic_css()
    styled_misc_css = get_styled_misc_css(style_spec.chart, style_spec.table)
    styled_dojo_css = get_styled_dojo_css(style_spec.dojo)
    title = (f"Results of independent samples t-test of average {results.measure_fld_lbl} "
        f'''for "{results.group_lbl}" groups "{results.group_a_dets.lbl}" and "{results.group_b_dets.lbl}"''')
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    ## format group details needed by second table
    formatted_groups_dets = []
    mpl_pngs.set_gen_mpl_settings(axes_lbl_size=10, xtick_lbl_size=8, ytick_lbl_size=8)
    histograms2show = []
    for orig_group_dets in [results.group_a_dets, results.group_b_dets]:
        n = format_num(orig_group_dets.n)
        ci95_left = num_tpl.format(round(orig_group_dets.ci95[0], dp))
        ci95_right = num_tpl.format(round(orig_group_dets.ci95[1], dp))
        ci95 = f"{ci95_left} - {ci95_right}"
        stdev = num_tpl.format(round(orig_group_dets.stdev, dp))
        sample_mean = num_tpl.format(round(orig_group_dets.mean, dp))
        kurt = num_tpl.format(round(orig_group_dets.kurtosis, dp))
        skew_val = num_tpl.format(round(orig_group_dets.skew, dp))
        p = get_p_str(orig_group_dets.p)
        formatted_group_dets = NumericSampleDetsFormatted(
            lbl=orig_group_dets.lbl,
            n=n,
            mean=sample_mean,
            ci95=ci95,
            stdev=stdev,
            sample_min=str(orig_group_dets.sample_min),
            sample_max=str(orig_group_dets.sample_max),
            kurtosis=kurt,
            skew=skew_val,
            p=p,
        )
        formatted_groups_dets.append(formatted_group_dets)
        ## make images
        try:
            histogram_html = get_group_histogram_html(
                results.measure_fld_lbl, style_spec.chart, orig_group_dets.lbl, orig_group_dets.vals)
        except Exception as e:
            html_or_msg = (
                f"<b>{orig_group_dets.lbl}</b> - unable to display histogram. Reason: {e}")
        else:
            html_or_msg = histogram_html
        histograms2show.append(html_or_msg)
    workings_msg = "<p>No worked example available for this test</p>" if show_workings else ''
    context = {
        'generic_css': generic_css,
        'styled_misc_css': styled_misc_css,
        'styled_dojo_css': styled_dojo_css,
        'title': title,
        't': round(results.t, dp),
        'p': get_p_str(results.p),
        'df': results.degrees_of_freedom,
        'obriens_msg': results.obriens_msg,
        'p_explain_multiple_groups': p_explain_multiple_groups,
        'one_tail_explain': one_tail_explain,
        'obrien_explain': obrien_explain,
        'ci_explain': ci_explain,
        'std_dev_explain': std_dev_explain,
        'kurtosis_explain': kurtosis_explain,
        'skew_explain': skew_explain,
        'normality_measure_explain': normality_measure_explain,
        'groups_dets': formatted_groups_dets,
        'histograms2show': histograms2show,
        'workings_msg': workings_msg,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html
