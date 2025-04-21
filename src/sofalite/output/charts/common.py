"""
Why making single dispatch for:
* get_common_charting_spec
* get_indiv_chart_html?

Two options:
1) pass to a function which works out type of chart and then, using a switch logic,
calls the specific module and function required for that chart type.
2) pass to a function which will pass to the correct function without a switch logic.
Adding new outputs requires using the singledispatch decorator.
The core code doesn't have to change depending on which charts are available.
I chose option 2). It is a taste issue in this case - either would work.

get_html(charting_spec, style_spec)
"""
from functools import singledispatch

import jinja2

from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.styles.interfaces import StyleSpec

from sofalite.conf.main import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.output.styles.misc import get_generic_css, get_styled_dojo_css, get_styled_misc_css

def get_html_styling_top(style_spec: StyleSpec) -> str:
    generic_css = get_generic_css()
    styled_dojo_css = get_styled_dojo_css(style_spec.dojo)
    styled_misc_css = get_styled_misc_css(style_spec.chart, style_spec.table)
    context = {
        'generic_css': generic_css,
        'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
        'styled_dojo_css': styled_dojo_css,
        'styled_misc_css': styled_misc_css,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl_html_top)
    html_styling_top = template.render(context)
    return html_styling_top

## https://towardsdatascience.com/simplify-your-functions-with-functools-partial-and-singledispatch-b7071f7543bb
@singledispatch
def get_common_charting_spec(charting_spec, style_spec):
    raise NotImplementedError("Unable to find registered get_common_charting_spec function "
        f"for {type(charting_spec)}")

@singledispatch
def get_indiv_chart_html(common_charting_spec, chart_dets, chart_counter):
    raise NotImplementedError("Unable to find registered get_indiv_chart_html function "
        f"for {type(common_charting_spec)}")

def get_html(charting_spec, style_spec: StyleSpec) -> str:
    html_styling_top = get_html_styling_top(style_spec)
    common_charting_spec = get_common_charting_spec(charting_spec, style_spec)  ## correct version e.g. from pie module, depending on charting_spec type
    chart_html_strs = []
    for n, chart_dets in enumerate(charting_spec.indiv_chart_specs, 1):
        indiv_chart_html = get_indiv_chart_html(
            common_charting_spec, chart_dets, chart_counter=n)  ## as above through power of functools.singledispatch
        chart_html_strs.append(indiv_chart_html)
    html_indiv_charts = '\n\n'.join(chart_html_strs)
    html = '\n\n'.join([html_styling_top, html_indiv_charts, html_bottom])
    return html
