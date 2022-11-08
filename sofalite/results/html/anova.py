from dataclasses import replace

import jinja2

from sofalite.results.html.css import default
from sofalite.results.html.conf import (
    ci_explain, kurtosis_explain,
    normality_measure_explain, obrien_explain, one_tail_explain,
    p_explain_multiple_groups,
    skew_explain, std_dev_explain,
)
from sofalite.results.stats.conf import AnovaResultExt, NumericSampleDetsExt
from sofalite.results.stats.utils import get_p_str
from sofalite.utils.maths import formatnum

def make_anova_html(results: AnovaResultExt, *, dp: int) -> str:
    anova_tpl = """\
    <head>
    <style>
        {{default_css}}
    </style>
    </head>
    <body class='default'>
    <h2>{{title}}</h2>
    <h3>Analysis of variance table</h3>
    <table cellspacing='0'>
    <thead>
      <tr>
        <th class='firstcolvar'>Source</th>
        <th class='firstcolvar'>Sum of Squares</th>
        <th class='firstcolvar'>df</th>
        <th class='firstcolvar'>Mean Sum of Squares</th>
        <th class='firstcolvar'>F</th>
        <th class='firstcolvar'>p<a class='tbl-header-footnote' href='#ft1'><sup>1</sup></a></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Between</td>
        <td class='right'>{{sum_squares_between_groups}}</td>
        <td class='right'>{{degrees_freedom_between_groups}}</td>
        <td class='right'>{{mean_squares_between_groups}}</td>
        <td class='right'>{{F}}</td>
        <td>{{p}}</td>
      </tr>
      <tr>
        <td>Within</td>
        <td class='right'>{{sum_squares_within_groups}}</td>
        <td class='right'>{{degrees_freedom_within_groups}}</td>
        <td class='right'>{{mean_squares_within_groups}}</td>
        <td></td>
        <td></td>
      </tr>
    </tbody>
    </table>
    <p>O'Brien's test for homogeneity of variance: {{obriens_msg}}<a href='#ft2'><sup>2</sup></a></p>
    <h3>Group summary details</h3>
    <table cellspacing='0'>
      <thead>
        <tr>
          <th class='firstcolvar'>Group</th>
          <th class='firstcolvar'>N</th>
          <th class='firstcolvar'>Mean</th>
          <th class='firstcolvar'>CI 95%<a class='tbl-header-footnote' href='#ft3'><sup>3</sup></a></th>
          <th class='firstcolvar'>Standard Deviation<a class='tbl-header-footnote' href='#ft4'><sup>4</sup></a></th>
          <th class='firstcolvar'>Min</th>
          <th class='firstcolvar'>Max</th>
          <th class='firstcolvar'>Kurtosis<a class='tbl-header-footnote' href='#ft5'><sup>5</sup></a></th>
          <th class='firstcolvar'>Skew<a class='tbl-header-footnote' href='#ft6'><sup>6</sup></a></th>
          <th class='firstcolvar'>p abnormal<a class='tbl-header-footnote' href='#ft7'><sup>7</sup></a></th>
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
    </body>
    """
    group_vals = [group_dets.lbl for group_dets in results.groups_dets]
    if len(group_vals) < 2:
        raise Exception(f"Expected multiple groups in ANOVA. Details:\n{results}")
    group_lbl_a = group_vals[0]
    group_lbl_b = group_vals[-1]
    title = (f"Results of ANOVA test of average {results.measure_fld_lbl} "
        f'''for "{results.group_lbl}" groups from "{group_lbl_a}" to "{group_lbl_b}"''')
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    ## format group details needed by second table
    formatted_groups_dets = []
    for orig_group_dets in results.groups_dets:
        n = formatnum(orig_group_dets.n)
        ci95_left = num_tpl.format(round(orig_group_dets.ci95[0], dp))
        ci95_right = num_tpl.format(round(orig_group_dets.ci95[1], dp))
        ci95 = f"{ci95_left} - {ci95_right}"
        stdev = num_tpl.format(round(orig_group_dets.stdev, dp))
        sample_mean = num_tpl.format(round(orig_group_dets.mean, dp))
        kurt = num_tpl.format(round(orig_group_dets.kurtosis, dp))
        skew_val = num_tpl.format(round(orig_group_dets.skew, dp))
        p = get_p_str(orig_group_dets.p)
        formatted_group_dets = replace(orig_group_dets, n=n, ci95=ci95, stdev=stdev,
            mean=sample_mean, kurtosis=kurt, skew=skew_val, p=p)
        formatted_groups_dets.append(formatted_group_dets)
    context = {
        'default_css': default,
        'title': title,
        'degrees_freedom_between_groups': f"{results.degrees_freedom_between_groups:,}",
        'sum_squares_between_groups': num_tpl.format(round(results.sum_squares_between_groups, dp)),
        'mean_squares_between_groups': num_tpl.format(round(results.mean_squares_between_groups, dp)),
        'F': num_tpl.format(round(results.F, dp)),
        'p': get_p_str(results.p),
        'sum_squares_within_groups': num_tpl.format(round(results.sum_squares_within_groups, dp)),
        'degrees_freedom_within_groups': f"{results.degrees_freedom_within_groups:,}",
        'mean_squares_within_groups': num_tpl.format(round(results.mean_squares_within_groups, dp)),
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
    }
    environment = jinja2.Environment()
    template = environment.from_string(anova_tpl)
    html = template.render(context)
    return html

    """
    for dic_sample_tup in dic_sample_tups:
        dic, sample = dic_sample_tup
        histlbl = dic['label']
        logging.debug(histlbl)
        ## histogram
        ## http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples
        charting_pylab.gen_config(
            axes_labelsize=10, xtick_labelsize=8, ytick_labelsize=8)
        fig = pylab.figure()
        fig.set_size_inches((5.0, 3.5))  ## see dpi to get image size in pixels
        css_dojo_dic = lib.OutputLib.extract_dojo_style(css_fpath)
        item_colours = output.colour_mappings_to_item_colours(
            css_dojo_dic['colour_mappings'])
        try:
            charting_pylab.config_hist(fig, sample, label_avg, histlbl,
                                       css_dojo_dic['plot_bg'], item_colours[0],
                                       css_dojo_dic['major_gridline_colour'], thumbnail=False)
            img_src = charting_pylab.save_report_img(
                add_to_report, report_fpath,
                save_func=pylab.savefig, dpi=100)
            html.append(f'\n{ms.IMG_SRC_START}{img_src}{ms.IMG_SRC_END}')
        except Exception as e:
            html.append(f'<b>{histlbl}</b> - unable to display histogram. '
                        f'Reason: {e}')
        output.append_divider(html, title, indiv_title=histlbl)
    ## details
    if details:
        html.append('<p>No worked example available for this test</p>')
    if page_break_after:
        html.append(f"<br><hr><br><div class='{CSS_PAGE_BREAK_BEFORE}'></div>")
    return ''.join(html)
    """








