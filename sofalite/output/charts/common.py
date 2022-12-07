from abc import ABC
from dataclasses import dataclass
from typing import Callable

import jinja2
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import StyleDets
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.styles.misc import common_css, get_styled_dojo_css, get_styled_misc_css

@dataclass(frozen=True)
class ChartingSpec(ABC):
    ...

def get_html(charting_spec: ChartingSpec, style_dets: StyleDets,
        common_spec_fn: Callable, indiv_chart_html_fn: Callable) -> str:
    """
    May be one chart, or, if charting by another variable, multiple charts.
    But each individual chart has standalone HTML str content
    that can be appended into the main HTML body between html_top and html_bottom.

    The common charting spec data object is required by each chart in the collection.

    We then need to translate that (alongside the individual chart spec) into HTML,
    so we can build the overall HTML.
    """
    styled_dojo_css = get_styled_dojo_css(style_dets.dojo)
    styled_misc_css = get_styled_misc_css(style_dets.chart, style_dets.table)
    context = {
        'common_css': common_css,
        'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
        'styled_dojo_css': styled_dojo_css,
        'styled_misc_css': styled_misc_css,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl_html_top)
    html_top = template.render(context)
    html_result = [html_top, ]
    common_charting_spec = common_spec_fn(charting_spec, style_dets)
    for n, chart_dets in enumerate(charting_spec.generic_charting_dets.charts_details, 1):
        indiv_chart_html = indiv_chart_html_fn(common_charting_spec, chart_dets, chart_counter=n)
        html_result.append(indiv_chart_html)
    html_result.append(html_bottom)
    return '\n\n'.join(html_result)


class LineArea:

    @staticmethod
    def placeholder():
        pass
