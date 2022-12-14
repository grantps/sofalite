from dataclasses import dataclass
from typing import Literal, Sequence
import uuid

import jinja2

from sofalite.conf.charting.misc import ScatterplotDojoSeriesSpec, LeftMarginOffsetDetails
from sofalite.conf.charting.other_specs import ScatterChartingSpec, ScatterIndivChartSpec
from sofalite.conf.style import ColourWithHighlight, StyleDets
from sofalite.output.charts.common import get_common_charting_spec, get_indiv_chart_html
from sofalite.output.charts.utils import get_left_margin_offset, get_y_axis_title_offset
from sofalite.output.styles.misc import get_long_colour_list
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

left_margin_offset_dets = LeftMarginOffsetDetails(
    initial_offset=25, wide_offset=35, rotate_offset=15, multi_chart_offset=15)

@dataclass(frozen=True)
class CommonColourSpec:
    axis_font: str
    chart_bg: str
    colour_cases: Sequence[str]
    colours: Sequence[str]
    major_grid_line: str
    plot_bg: str
    plot_font: str
    plot_font_filled: str
    tooltip_border: str

@dataclass(frozen=True)
class CommonOptions:
    has_minor_ticks_js_bool: Literal['true', 'false']
    is_multi_chart: bool
    show_dot_borders: bool
    show_n_records: bool
    show_regression_line_js_bool: Literal['true', 'false']

@dataclass(frozen=True)
class CommonMiscSpec:
    axis_lbl_drop: int
    connector_style: str
    grid_line_width: int
    height: float  ## pixels
    left_margin_offset: int
    legend_lbl: str
    stroke_width: int
    width: float  ## pixels
    x_axis_font_size: float
    x_axis_title: str
    x_max: int
    x_min: int
    y_axis_title: str
    y_axis_title_offset: int
    y_max: int
    y_min: int

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: CommonMiscSpec
    options: CommonOptions

tpl_chart = """\
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

    var series = new Array();
    {% for series_dets in dojo_series_dets %}
      var series_{{series_dets.series_id}} = new Array();
          series_{{series_dets.series_id}}["lbl"] = "{{series_dets.lbl}}";
          series_{{series_dets.series_id}}["xy_pairs"] = {{series_dets.xy_pairs}};
          // options - stroke_width_to_use, fill_colour
          series_{{series_dets.series_id}}["options"] = {{series_dets.options}};
      series.push(series_{{series_dets.series_id}});
    {% endfor %}

    var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font}}";
        conf["axis_lbl_drop"] = {{axis_lbl_drop}};
        conf["chart_bg_colour"] = "{{chart_bg}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["grid_line_width"] = {{grid_line_width}};
        conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
        conf["highlight"] = highlight_{{chart_uuid}};
        conf["left_margin_offset"] = {{left_margin_offset}};
        conf["major_grid_line_colour"] = "{{major_grid_line}}";
        conf["n_records"] = "{{n_records}}";
        conf["plot_bg_colour"] = "{{plot_bg}}";
        conf["plot_font_colour"] = "{{plot_font}}";
        conf["plot_font_colour_filled"] = "{{plot_font_filled}}";
        conf["show_regression_line"] = {{show_regression_line_js_bool}};
        conf["tooltip_border_colour"] = "{{tooltip_border}}";
        conf["x_axis_title"] = "{{x_axis_title}}";
        conf["x_axis_font_size"] = {{x_axis_font_size}};
        conf["x_max"] = {{x_max}};
        conf["x_min"] = {{x_min}};
        conf["y_axis_title"] = "{{y_axis_title}}";
        conf["y_axis_title_offset"] = {{y_axis_title_offset}};
        conf["y_max"] = {{y_max}};
        conf["y_min"] = {{y_min}};

    makeScatterplot("scatterplot_{{chart_uuid}}", series, conf);
}
</script>

<div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
{{indiv_title_html}}
    <div id="scatterplot_{{chart_uuid}}"
        style="width: {{width}}px; height: {{height}}px;">
    </div>
    {% if legend_lbl %}
        <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
            {{legend_lbl}}:
        </p>
        <div id="legend_for_scatterplot_{{chart_uuid}}">
        </div>
    {% endif %}
</div>
"""

@get_common_charting_spec.register
def get_common_charting_spec(charting_spec: ScatterChartingSpec, style_dets: StyleDets) -> CommonChartingSpec:
    ## colours
    colour_mappings = style_dets.chart.colour_mappings
    if charting_spec.is_single_series:
        ## This is an important special case because it affects the scatter plots charts using the default style
        if colour_mappings[0].main == '#e95f29':  ## BURNT_ORANGE
            colour_mappings = [ColourWithHighlight('#e95f29', '#736354'), ]
    colours = get_long_colour_list(colour_mappings)
    colour_cases = [f'case "{colour_mapping.main}": hlColour = "{colour_mapping.highlight}"'
        for colour_mapping in colour_mappings]
    ## misc
    has_minor_ticks_js_bool = 'true' if charting_spec.has_minor_ticks else 'false'
    stroke_width = style_dets.chart.stroke_width if charting_spec.show_dot_borders else 0
    show_regression_line_js_bool = 'true' if charting_spec.show_regression_line else 'false'
    ## sizing
    if charting_spec.is_multi_chart:
        width, height = (630, 350)
    else:
        width, height = (700, 385)
    x_axis_title_len = len(charting_spec.x_axis_title)
    y_axis_title_offset = get_y_axis_title_offset(
        x_axis_title_len=x_axis_title_len, rotated_x_lbls=False)
    left_margin_offset = get_left_margin_offset(width_after_left_margin=width - 25,  ## not a dynamic settings like x-axis label type charts so 25 is a good guess
        offsets=left_margin_offset_dets, is_multi_chart=charting_spec.is_multi_chart,
        y_axis_title_offset=y_axis_title_offset, rotated_x_lbls=False)

    colour_spec = CommonColourSpec(
        axis_font=style_dets.chart.axis_font_colour,
        chart_bg=style_dets.chart.chart_bg_colour,
        colour_cases=colour_cases,
        colours=colours,
        major_grid_line=style_dets.chart.major_grid_line_colour,
        plot_bg=style_dets.chart.plot_bg_colour,
        plot_font=style_dets.chart.plot_font_colour,
        plot_font_filled=style_dets.chart.plot_font_colour_filled,
        tooltip_border=style_dets.chart.tooltip_border_colour,
    )
    misc_spec = CommonMiscSpec(
        axis_lbl_drop=10,
        connector_style=style_dets.dojo.connector_style,
        grid_line_width=style_dets.chart.grid_line_width,
        height=height,
        left_margin_offset=left_margin_offset,
        legend_lbl=charting_spec.legend_lbl,
        stroke_width=stroke_width,
        width=width,
        x_axis_font_size=charting_spec.x_axis_font_size,
        x_axis_title=charting_spec.x_axis_title,
        x_max=charting_spec.max_x_val,
        x_min=charting_spec.min_x_val,
        y_axis_title=charting_spec.y_axis_title,
        y_axis_title_offset=y_axis_title_offset,
        y_max=charting_spec.max_y_val,
        y_min=charting_spec.min_y_val,
    )
    options = CommonOptions(
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        is_multi_chart=charting_spec.is_multi_chart,
        show_dot_borders=charting_spec.show_dot_borders,
        show_n_records=charting_spec.show_n_records,
        show_regression_line_js_bool=show_regression_line_js_bool,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

@get_indiv_chart_html.register
def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: ScatterIndivChartSpec,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = f"<p><b>{indiv_chart_spec.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else ''
    n_records = 'N = ' + format_num(indiv_chart_spec.n_records) if common_charting_spec.options.show_n_records else ''
    dojo_series_dets = []
    for i, data_series_spec in enumerate(indiv_chart_spec.data_series_specs):
        series_id = f"{i:>02}"
        series_lbl = data_series_spec.lbl
        xy_dicts = [f"{{x: {x}, y: {y}}}" for x, y in data_series_spec.xy_pairs]
        series_xy_pairs = '[' + ', '.join(xy_dicts) + ']'
        fill_colour = common_charting_spec.colour_spec.colours[i]
        options = (
            f"""{{stroke: {{color: "white", width: "{common_charting_spec.misc_spec.stroke_width}px"}}, """
            f"""fill: "{fill_colour}", marker: "m-6,0 c0,-8 12,-8 12,0 m-12,0 c0,8 12,8 12,0"}}""")
        dojo_series_dets.append(ScatterplotDojoSeriesSpec(series_id, series_lbl, series_xy_pairs, options))
    indiv_context = {
        'chart_uuid': chart_uuid,
        'dojo_series_dets': dojo_series_dets,
        'indiv_title_html': indiv_title_html,
        'n_records': n_records,
        'page_break': page_break,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result
