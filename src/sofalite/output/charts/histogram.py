from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal
import uuid

import jinja2

from sofalite.conf import HISTO_AVG_CHAR_WIDTH_PIXELS
from sofalite.data_extraction.charts.histogram import HistoIndivChartSpec
from sofalite.output.charts.common import get_common_charting_spec, get_indiv_chart_html
from sofalite.output.styles.interfaces import ColourWithHighlight, StyleSpec
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

MIN_CHART_WIDTH = 700
MIN_PIXELS_PER_BAR = 30
PADDING_PIXELS = 5

@dataclass(frozen=True, kw_only=True)
class HistogramConf:
    var_lbl: str
    chart_lbl: str | None
    inner_bg_colour: str
    bar_colour: str
    line_colour: str

@dataclass(frozen=True)
class HistogramData:
    vals: Sequence[float]

@dataclass(frozen=True)
class CommonColourSpec:
    axis_font: str
    chart_bg: str
    colour_cases: Sequence[str]
    fill: str
    major_grid_line: str
    normal_curve: str
    plot_bg: str
    plot_font: str
    plot_font_filled: str
    tooltip_border: str

@dataclass(frozen=True)
class CommonOptions:
    has_minor_ticks_js_bool: Literal['true', 'false']
    is_multi_chart: bool
    show_borders: bool
    show_n_records: bool
    show_normal_curve_js_bool: Literal['true', 'false']

@dataclass(frozen=True)
class CommonMiscSpec:
    bin_lbls: Sequence[str]  ## e.g. ["1 to < 6.0", ... "91.0 to <= 96.0"]
    blank_x_axis_lbls: str
    connector_style: str
    grid_line_width: int
    height: float  ## pixels
    left_margin_offset: int
    normal_stroke_width: int
    stroke_width: int
    var_lbl: str
    width: float  ## pixels
    x_axis_font_size: float
    x_axis_max_val: float
    x_axis_min_val: float
    y_axis_max_val: float
    y_axis_title: str
    y_axis_title_offset: int

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: CommonMiscSpec
    options: CommonOptions

tpl_chart = """
 <script type="text/javascript">

var highlight_{{chart_uuid}} = function(colour){
    var hlColour;
    switch (colour.toHex()){
        {% for colour_case in colour_cases %}\n            {{colour_case}}; break;{% endfor %}
        default:
            hlColour = hl(colour.toHex());
            break;
    }
    return new dojox.color.Color(hlColour);
}

 make_chart_{{chart_uuid}} = function(){

    var data_spec = new Array();
        data_spec["series_lbl"] = "{{var_lbl}}";
        data_spec["y_vals"] = {{y_vals}};
        data_spec["norm_y_vals"] = {{norm_y_vals}};
        data_spec["bin_lbls"] = {{bin_lbls}};
        data_spec["style"] = {
            stroke: {
                color: "white", width: "{{stroke_width}}px"
            },
            fill: "{{fill}}"
        };
        data_spec["norm_style"] = {
            plot: "normal",
            stroke: {
                color: "{{normal_curve}}",
                width: "{{normal_stroke_width}}px"
            },
            fill: "{{fill}}"
        };

    var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font}}";
        conf["blank_x_axis_lbls"] = {{blank_x_axis_lbls}};
        conf["chart_bg_colour"] = "{{chart_bg}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["grid_line_width"] = {{grid_line_width}};
        conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
        conf["highlight"] = highlight_{{chart_uuid}};
        conf["left_margin_offset"] = {{left_margin_offset}};
        conf["major_grid_line_colour"] = "{{major_grid_line}}";
        conf["n_records"] = "{{n_records}}";
        conf["normal_curve_colour"] = "{{normal_curve}}";
        conf["plot_bg_colour"] = "{{plot_bg}}";
        conf["plot_font_colour"] = "{{plot_font}}";
        conf["plot_font_colour_filled"] = "{{plot_font_filled}}";
        conf["show_normal_curve"] = {{show_normal_curve_js_bool}};
        conf["tooltip_border_colour"] = "{{tooltip_border}}";
        conf["x_axis_font_size"] = {{x_axis_font_size}};
        conf["x_axis_max_val"] = {{x_axis_max_val}};
        conf["x_axis_min_val"] = {{x_axis_min_val}};
        conf["y_axis_max_val"] = {{y_axis_max_val}};
        conf["y_axis_title"] = "{{y_axis_title}}";
        conf["y_axis_title_offset"] = {{y_axis_title_offset}};

     makeHistogram("histogram_{{chart_uuid}}", data_spec, conf);
 }
 </script>

 <div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
 {{indiv_title_html}}
     <div id="histogram_{{chart_uuid}}"
         style="width: {{width}}px; height: {{height}}px;">
     </div>
 </div>
 """

def get_width(var_lbl: str, *, n_bins: int,
        x_axis_min_val: float, x_axis_max_val: float, is_multi_chart: bool) -> float:
    max_lbl_width = max(len(str(round(x, 0))) for x in (x_axis_min_val, x_axis_max_val))
    min_bin_width = max(max_lbl_width * HISTO_AVG_CHAR_WIDTH_PIXELS, MIN_PIXELS_PER_BAR)
    width_x_axis_title = len(var_lbl) * HISTO_AVG_CHAR_WIDTH_PIXELS + PADDING_PIXELS
    width = max([n_bins * min_bin_width, width_x_axis_title, MIN_CHART_WIDTH])
    if is_multi_chart:
        width = width * 0.9  ## vulnerable to x-axis labels vanishing on minor ticks
    return width

@dataclass
class HistoChartingSpec:
    bin_lbls: Sequence[str]
    indiv_chart_specs: Sequence[HistoIndivChartSpec]
    show_borders: bool
    show_n_records: bool
    show_normal_curve: bool
    var_lbl: str | None
    x_axis_font_size: int
    x_axis_max_val: float
    x_axis_min_val: float

    def __post_init__(self):
        self.n_bins = len(self.bin_lbls)
        self.n_charts = len(self.indiv_chart_specs)
        self.is_multi_chart = self.n_charts > 1
        y_axis_max_val = 0
        for indiv_chart_spec in self.indiv_chart_specs:
            indiv_chart_max_y_val = max(
                max(indiv_chart_spec.y_vals),
                max(indiv_chart_spec.norm_y_vals),
            )
            if indiv_chart_max_y_val > y_axis_max_val:
                y_axis_max_val = indiv_chart_max_y_val
        self.y_axis_max_val = y_axis_max_val

@get_common_charting_spec.register
def get_common_charting_spec(charting_spec: HistoChartingSpec, style_spec: StyleSpec) -> CommonChartingSpec:
    ## colours
    colour_mappings = style_spec.chart.colour_mappings[:1]  ## only need the first
    ## This is an important special case because it affects the histograms using the default style
    first_colour = colour_mappings[0].main
    if first_colour == '#e95f29':  ## BURNT_ORANGE
        colour_mappings = [ColourWithHighlight('#e95f29', '#736354'), ]
    colour_cases = [f'case "{colour_mapping.main}": hlColour = "{colour_mapping.highlight}"'
        for colour_mapping in colour_mappings]  ## actually only need first one for simple bar charts
    ## misc
    blank_x_axis_lbls = '[' + ', '.join(f"{{value: {n}, text: ''}}" for n in range(1, charting_spec.n_bins + 1)) + ']'
    height = 300 if charting_spec.is_multi_chart else 350
    y_axis_title_offset = 45
    left_margin_offset = 25
    stroke_width = style_spec.chart.stroke_width if charting_spec.show_borders else 0
    normal_stroke_width = 4
    show_normal_curve_js_bool = 'true' if charting_spec.show_normal_curve else 'false'
    width = get_width(charting_spec.var_lbl, n_bins=charting_spec.n_bins,
        x_axis_min_val=charting_spec.x_axis_min_val, x_axis_max_val=charting_spec.x_axis_max_val,
        is_multi_chart=charting_spec.is_multi_chart)
    x_axis_font_size = charting_spec.x_axis_font_size
    if charting_spec.is_multi_chart:
        x_axis_font_size *= 0.8
    colour_spec = CommonColourSpec(
        axis_font=style_spec.chart.axis_font_colour,
        chart_bg=style_spec.chart.chart_bg_colour,
        colour_cases=colour_cases,
        fill=first_colour,
        major_grid_line=style_spec.chart.major_grid_line_colour,
        normal_curve=style_spec.chart.normal_curve_colour,
        plot_bg=style_spec.chart.plot_bg_colour,
        plot_font=style_spec.chart.plot_font_colour,
        plot_font_filled=style_spec.chart.plot_font_colour_filled,
        tooltip_border=style_spec.chart.tooltip_border_colour,
    )
    misc_spec = CommonMiscSpec(
        bin_lbls=charting_spec.bin_lbls,
        blank_x_axis_lbls=blank_x_axis_lbls,
        connector_style=style_spec.dojo.connector_style,
        grid_line_width=style_spec.chart.grid_line_width,
        height=height,
        left_margin_offset=left_margin_offset,
        x_axis_min_val=charting_spec.x_axis_min_val,
        normal_stroke_width=normal_stroke_width,
        stroke_width=stroke_width,
        var_lbl=charting_spec.var_lbl,
        width=width,
        x_axis_font_size=charting_spec.x_axis_font_size,
        x_axis_max_val=charting_spec.x_axis_max_val,
        y_axis_max_val=charting_spec.y_axis_max_val,
        y_axis_title='Frequency',
        y_axis_title_offset=y_axis_title_offset,
    )
    options = CommonOptions(
        has_minor_ticks_js_bool='true',
        is_multi_chart=charting_spec.is_multi_chart,
        show_borders=charting_spec.show_borders,
        show_n_records=charting_spec.show_n_records,
        show_normal_curve_js_bool=show_normal_curve_js_bool,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

@get_indiv_chart_html.register
def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: HistoIndivChartSpec,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = (f"<p><b>{indiv_chart_spec.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else '')
    n_records = 'N = ' + format_num(indiv_chart_spec.n_records) if common_charting_spec.options.show_n_records else ''
    indiv_context = {
        'chart_uuid': chart_uuid,
        'indiv_title_html': indiv_title_html,
        'n_records': n_records,
        'norm_y_vals': indiv_chart_spec.norm_y_vals,
        'page_break': page_break,
        'y_vals': indiv_chart_spec.y_vals,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result
