from dataclasses import dataclass
from pathlib import Path

import jinja2

from sofalite.conf.main import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.output.charts.utils import get_styled_dojo_chart_js
from sofalite.output.styles.misc import (get_generic_unstyled_css, get_style_spec, get_styled_dojo_chart_css,
    get_styled_placeholder_css_for_main_tbls, get_styled_stats_tbl_css)

@dataclass(frozen=True)
class HTMLItemSpec:
    html_item_str: str
    style_name: str
    includes_charts: bool = False
    includes_stats_tbl: bool = False
    includes_main_tbl: bool = False

    def __post_init__(self):
        n_inclusions = 0
        if self.includes_charts: n_inclusions += 1
        if self.includes_main_tbl: n_inclusions += 1
        if self.includes_stats_tbl: n_inclusions += 1
        if n_inclusions != 1:
            raise Exception("Must have one of includes_charts, includes_main_tbl, or includes_stats_tbl, and only one")

    def to_standalone_html(self, title: str) -> str:
        style_spec = get_style_spec(self.style_name)
        tpl_bits = []
        html_and_some_head_tpl = """\
        <!DOCTYPE html>
        <head>
        <title>{{title}}</title>
        <style type="text/css">
        <!--
        {{generic_unstyled_css}}
        -->
        </style>
        """
        tpl_bits.append(html_and_some_head_tpl)
        if self.includes_charts:
            charting_links_tpl = """\
            <link rel='stylesheet' type='text/css' href="{{sofalite_web_resources_root}}/tundra.css" />
            <script src="{{sofalite_web_resources_root}}/dojo.xd.js"></script>
            <script src="{{sofalite_web_resources_root}}/sofalitedojo_minified.js"></script>
            <script src="{{sofalite_web_resources_root}}/sofalite_charts.js"></script>            
            """
            charting_css_js_tpl = """\
            <style type="text/css">
            <!--
                .dojoxLegendNode {
                    border: 1px solid #ccc;
                    margin: 5px 10px 5px 10px;
                    padding: 3px
                }
                .dojoxLegendText {
                    vertical-align: text-top;
                    padding-right: 10px
                }
                @media print {
                    .screen-float-only{
                    float: none;
                    }
                }
                @media screen {
                    .screen-float-only{
                    float: left;
                    }
                }
            {{styled_dojo_chart_css}}
            -->
            </style>
            {{styled_dojo_chart_js}}
            """
            tpl_bits.append(charting_links_tpl)
            tpl_bits.append(charting_css_js_tpl)
        if self.includes_main_tbl:
            spaceholder_css_tpl = """\
            <style type="text/css">
            <!--
            {{styled_placeholder_css_for_main_tbls}}
            -->
            </style>
            """
            tpl_bits.append(spaceholder_css_tpl)
        if self.includes_stats_tbl:
            stats_tbl_tpl = """\
            <style type="text/css">
            <!--
            {{styled_stats_tbl_css}}
            -->
            </style>
            """
            tpl_bits.append(stats_tbl_tpl)
        head_end_tpl = "</head>"
        tpl_bits.append(head_end_tpl)
        body_start_tpl = "<body class='tundra'>"
        tpl_bits.append(body_start_tpl)
        tpl_bits.append(self.html_item_str)
        body_and_html_end_tpl = """\
        </body>
        </html>
        """
        tpl_bits.append(body_and_html_end_tpl)
        tpl = '\n'.join(tpl_bits)

        environment = jinja2.Environment()
        template = environment.from_string(tpl)
        context = {
            'generic_unstyled_css': get_generic_unstyled_css(),
            'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
            'title': title,
        }
        if self.includes_charts:
            context['styled_dojo_chart_css'] = get_styled_dojo_chart_css(style_spec.dojo)
            context['styled_dojo_chart_js'] = get_styled_dojo_chart_js(style_spec.dojo)
        if self.includes_main_tbl:
            context['styled_placeholder_css_for_main_tbls'] = get_styled_placeholder_css_for_main_tbls(self.style_name)
        if self.includes_stats_tbl:
            context['styled_stats_tbl_css'] = get_styled_stats_tbl_css(style_spec.table)
        html = template.render(context)
        return html

    def to_file(self, fpath: Path, title: str):
        with open(fpath, 'w') as f:
            f.write(self.to_standalone_html(title))
