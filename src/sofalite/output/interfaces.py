"""
Note - output.utils.get_report() replies on the template param names here so keep aligned.
Not worth formally aligning them given how easy to do manually and how static.
"""
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import jinja2

from sofalite.conf.main import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.output.charts.conf import DOJO_CHART_JS
from sofalite.output.styles.utils import (get_generic_unstyled_css, get_style_spec, get_styled_dojo_chart_css,
    get_styled_placeholder_css_for_main_tbls, get_styled_stats_tbl_css)

HTML_AND_SOME_HEAD_TPL = """\
<!DOCTYPE html>
<head>
<title>{{title}}</title>
<style type="text/css">
<!--
{{generic_unstyled_css}}
-->
</style>
"""

CHARTING_LINKS_TPL = """\
<link rel='stylesheet' type='text/css' href="{{sofalite_web_resources_root}}/tundra.css" />
<script src="{{sofalite_web_resources_root}}/dojo.xd.js"></script>
<script src="{{sofalite_web_resources_root}}/sofalitedojo_minified.js"></script>
<script src="{{sofalite_web_resources_root}}/sofalite_charts.js"></script>            
"""

CHARTING_CSS_TPL = """\
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
"""

CHARTING_JS_TPL = """\
{{dojo_chart_js}}
"""

SPACEHOLDER_CSS_TPL = """\
<style type="text/css">
<!--
{{styled_placeholder_css_for_main_tbls}}
-->
</style>
"""

STATS_TBL_TPL = """\
<style type="text/css">
<!--
{{styled_stats_tbl_css}}
-->
</style>
"""

HEAD_END_TPL = "</head>"

BODY_START_TPL = "<body class='tundra'>"

BODY_AND_HTML_END_TPL = """\
</body>
</html>
"""

class OutputItemType(StrEnum):
    CHART = 'chart'
    MAIN_TABLE = 'main_table'
    STATS = 'stats'

@dataclass(frozen=True)
class HTMLItemSpec:
    html_item_str: str
    style_name: str
    output_item_type: OutputItemType

    def to_standalone_html(self, title: str) -> str:
        style_spec = get_style_spec(self.style_name)
        tpl_bits = [HTML_AND_SOME_HEAD_TPL, ]
        if self.output_item_type == OutputItemType.CHART:
            tpl_bits.append(CHARTING_LINKS_TPL)
            tpl_bits.append(CHARTING_CSS_TPL)
            tpl_bits.append(CHARTING_JS_TPL)
        if self.output_item_type == OutputItemType.MAIN_TABLE:
            tpl_bits.append(SPACEHOLDER_CSS_TPL)
        if self.output_item_type == OutputItemType.STATS:
            tpl_bits.append(STATS_TBL_TPL)
        tpl_bits.append(HEAD_END_TPL)
        tpl_bits.append(BODY_START_TPL)
        tpl_bits.append(self.html_item_str)  ## <======= the actual item content e.g. chart
        tpl_bits.append(BODY_AND_HTML_END_TPL)
        tpl = '\n'.join(tpl_bits)

        environment = jinja2.Environment()
        template = environment.from_string(tpl)
        context = {
            'generic_unstyled_css': get_generic_unstyled_css(),
            'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
            'title': title,
        }
        if self.output_item_type == OutputItemType.CHART:
            context['styled_dojo_chart_css'] = get_styled_dojo_chart_css(style_spec.dojo)
            context['dojo_chart_js'] = DOJO_CHART_JS
        if self.output_item_type == OutputItemType.MAIN_TABLE:
            context['styled_placeholder_css_for_main_tbls'] = get_styled_placeholder_css_for_main_tbls(self.style_name)
        if self.output_item_type == OutputItemType.STATS:
            context['styled_stats_tbl_css'] = get_styled_stats_tbl_css(style_spec.table)
        html = template.render(context)
        return html

    def to_file(self, fpath: Path, title: str):
        with open(fpath, 'w') as f:
            f.write(self.to_standalone_html(title))

class HasToHTMLItemSpec(Protocol):
    def to_html_spec(self) -> HTMLItemSpec: ...

@dataclass(frozen=True)
class Report:
    html: str  ## include title

    def to_file(self, fpath: Path):
        with open(fpath, 'w') as f:
            f.write(self.html)
