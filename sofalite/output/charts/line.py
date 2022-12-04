from dataclasses import dataclass
import logging
from typing import Literal, Sequence
import uuid

import jinja2

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, TEXT_WIDTH_WHEN_ROTATED,
    ChartDetails, DojoSeriesDetails, GenericChartingDetails, LeftMarginOffsetDetails, XAxisSpec)
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import StyleDets
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.charts.utils import (
    get_axis_lbl_drop, get_height, get_left_margin_offset,
    get_x_axis_lbl_dets, get_x_font_size, get_y_max, get_y_title_offset)
from sofalite.output.styles.misc import common_css, get_styled_dojo_css, get_styled_misc_css
from sofalite.utils.dates import get_epoch_secs_from_datetime_str
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM = 8
DOJO_MICRO_TICKS_NEEDED_PER_X_ITEM = 100

left_margin_offset_dets = LeftMarginOffsetDetails(
    initial_offset=15, wide_offset=25, rotate_offset=5, multi_chart_offset=10)

@dataclass(frozen=True, kw_only=True)
class LineChartingSpec:
    """
    Compared with bar lacks show_borders.

    Only single-series line charts can have a trend line (or the smoothed option).
    """
    ## specific details for line charting
    x_title: str
    y_title: str
    rotate_x_lbls: bool = False
    show_n: bool = False
    x_font_size: int = 12
    dp: int
    is_time_series: bool = False
    major_ticks: bool = False
    show_trend_line: bool = False
    show_smooth_line: bool = False
    ## generic charting details
    generic_charting_dets: GenericChartingDetails

    def __post_init(self):
        multi_series = len(self.generic_charting_dets.charts_details[0].series_dets) > 1
        if multi_series and (self.show_trend_line or self.show_smooth_line):
            raise Exception("A smoothed line or a trend line can only be show if one series of results "
                "i.e. not split by another variable e.g. one line chart per gender")

@dataclass(frozen=True)
class OverallLineChartingDets:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    axis_font_colour: str
    axis_lbl_drop: int
    axis_lbl_rotate: int
    chart_bg_colour: str
    colours: Sequence[str]
    connector_style: str
    dp: int
    grid_line_width: int
    has_micro_ticks_js_bool: Literal['true', 'false']
    has_minor_ticks_js_bool: Literal['true', 'false']
    height: float  ## pixels
    is_time_series: bool
    is_time_series_js_bool: Literal['true', 'false']
    left_margin_offset: int
    legend_lbl: str
    major_grid_line_colour: str
    multi_chart: bool
    n_records: int
    plot_bg_colour: str
    plot_font_colour: str
    plot_font_colour_filled: str
    show_trend_line: bool
    tooltip_border_colour: str
    x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
    x_axis_specs: Sequence[XAxisSpec] | None
    x_font_size: float
    x_title: str
    y_max: int
    y_title: str
    y_title_offset: int
    width: float  ## pixels

MIN_PIXELS_PER_X_ITEM = 10

def get_width_after_left_margin(*, multi_chart: bool, n_x_items: int, n_series: int,
        max_x_lbl_width: int, is_time_series: bool, major_ticks: bool, x_title: str) -> float:
    """
    Get initial width (will make a final adjustment based on left margin offset).
    major_ticks -- e.g. want to only see the main labels and won't need it
    to be so wide.
    time_series -- can narrow a lot because standard-sized labels and
    usually not many.
    """
    min_chart_width = 700 if n_series < 5 else 900  # when vertically squeezed good to have more horizontal room
    padding_pixels = 20 if n_x_items < 8 else 25
    if is_time_series:
        width_per_x_item = MIN_PIXELS_PER_X_ITEM
    else:
        width_per_x_item = (max([MIN_PIXELS_PER_X_ITEM,
            max_x_lbl_width * AVG_CHAR_WIDTH_PIXELS]) + padding_pixels)
    width_x_title = len(x_title) * AVG_CHAR_WIDTH_PIXELS + padding_pixels
    width = max([n_x_items * width_per_x_item, width_x_title, min_chart_width])
    if major_ticks:
        width = max(width * 0.4, min_chart_width)
    if multi_chart:
        width = width * 0.9
    return width

def get_trend_y_vals(y_vals: Sequence[float]) -> Sequence[float]:
    """
    Returns values to plot a straight line which fits the y_vals provided
    """
    sum_y = sum(y_vals)
    logging.debug(f"sumy={sum_y}")
    n = len(y_vals)
    sum_x = sum(range(1, n + 1))
    logging.debug(f"{sum_x=}")
    sum_xy = 0
    sum_x2 = 0
    for x, y_val in enumerate(y_vals, 1):
        sum_xy += x * y_val
        sum_x2 += x ** 2
    logging.debug(f"{sum_xy}")
    logging.debug(f"{sum_x2=}")
    b_num = (n * sum_xy) - (sum_x * sum_y)
    logging.debug(f"b_num={b_num}")
    b_denom = (n * sum_x2) - (sum_x ** 2)
    logging.debug(f"b_denom={b_denom}")
    b = b_num / (1.0 * b_denom)
    a = (sum_y - (sum_x * b)) / (1.0 * n)
    trend_y_vals = []
    for x in range(1, n + 1):
        trend_y_vals.append(a + b * x)
    return trend_y_vals

def get_time_series_vals(x_axis_specs: Sequence[XAxisSpec], y_vals: Sequence[float], x_title: str) -> str:
    xs = []
    try:
        for x_axis_spec in x_axis_specs:
            val = str(x_axis_spec.val)
            xs.append(get_epoch_secs_from_datetime_str(val) * 1_000)
    except Exception as e:
        raise Exception(f"Problem processing x-axis specs for {x_title}. "
            f"Orig error: {e}")
    ys = y_vals
    xys = zip(xs, ys, strict=True)
    series_vals = str([{'x': xy[0], 'y': xy[1]} for xy in xys])
    return series_vals

tpl_chart = """
<script type="text/javascript">

make_chart_{{chart_uuid}} = function(){

    var series = new Array();
    {% for series_dets in dojo_series_dets %}
      var series_{{series_dets.series_id}} = new Array();
          series_{{series_dets.series_id}}["lbl"] = "{{series_dets.lbl}}";
          series_{{series_dets.series_id}}["vals"] = {{series_dets.vals}};
          // options - line_colour, fill_colour, y_lbls_str
          series_{{series_dets.series_id}}["options"] = {{series_dets.options}};
      series.push(series_{{series_dets.series_id}});
    {% endfor %}

    var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font_colour}}";
        conf["axis_lbl_drop"] = {{axis_lbl_drop}};
        conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
        conf["chart_bg_colour"] = "{{chart_bg_colour}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["grid_line_width"] = {{grid_line_width}};
        conf["left_margin_offset"] = {{left_margin_offset}};
        conf["major_grid_line_colour"] = "{{major_grid_line_colour}}";
        conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
        conf["n_records"] = "{{n_records}}";
        conf["plot_bg_colour"] = "{{plot_bg_colour}}";
        conf["plot_font_colour"] = "{{plot_font_colour}}";
        conf["plot_font_colour_filled"] = "{{plot_font_colour_filled}}";
        conf["tooltip_border_colour"] = "{{tooltip_border_colour}}";
        conf["x_axis_lbls"] = {{x_axis_lbls}};
        conf["x_font_size"] = {{x_font_size}};
        conf["x_title"] = "{{x_title}}";
        conf["y_max"] = {{y_max}};
        conf["y_title"] = "{{y_title}}";
        conf["y_title_offset"] = {{y_title_offset}};
        // distinct fields for line charts
        conf["has_micro_ticks"] = {{has_micro_ticks_js_bool}};
        conf["is_time_series"] = {{is_time_series_js_bool}};

    makeLineChart("line_chart_{{chart_uuid}}", series, conf);
}
</script>

<div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
{{indiv_title_html}}
    <div id="line_chart_{{chart_uuid}}"
        style="width: {{width}}px; height: {{height}}px;">
    </div>
    {% if legend_lbl %}
        <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
            {{legend_lbl}}:
        </p>
        <div id="legend_for_line_chart_{{chart_uuid}}">
        </div>
    {% endif %}
</div>
"""

def get_overall_charting_dets(
        charting_spec: LineChartingSpec, style_dets: StyleDets) -> OverallLineChartingDets:
    ## convenience pre-calcs
    rotated_x_lbls = charting_spec.rotate_x_lbls
    multi_chart = (len(charting_spec.generic_charting_dets.charts_details) > 1)
    first_chart_dets = charting_spec.generic_charting_dets.charts_details[0]
    n_series = len(first_chart_dets.series_dets)
    single_series = n_series == 1
    first_series = first_chart_dets.series_dets[0]
    first_x_axis_spec = first_series.x_axis_specs[0]
    x_lbl_len = len(first_x_axis_spec.lbl)
    n_x_items = len(first_series.x_axis_specs)
    max_x_lbl_length = charting_spec.generic_charting_dets.max_x_lbl_length
    ## colours
    colour_mappings = style_dets.chart.colour_mappings
    if single_series:
        colour_mappings = colour_mappings[:3]  ## only need the first 1-3 depending on whether trend and smoothed lines
    colours = [colour_mapping.main for colour_mapping in colour_mappings]
    ## misc
    n_records = 'N = ' + format_num(first_chart_dets.n_records) if charting_spec.show_n else ''
    x_axis_lbl_dets = get_x_axis_lbl_dets(first_series.x_axis_specs)
    if charting_spec.is_time_series:
        x_axis_specs = first_series.x_axis_specs
        x_axis_lbls = '[]'
    else:
        x_axis_specs = None
        x_axis_lbls = '[' + ',\n            '.join(x_axis_lbl_dets) + ']'
    y_max = get_y_max(charting_spec.generic_charting_dets.charts_details)
    has_minor_ticks_js_bool = 'true' if n_x_items >= DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM else 'false'
    has_micro_ticks_js_bool = 'true' if n_x_items > DOJO_MICRO_TICKS_NEEDED_PER_X_ITEM else 'false'
    is_time_series_js_bool = 'true' if charting_spec.is_time_series else 'false'
    legend_lbl = ('' if single_series
        else charting_spec.generic_charting_dets.overall_legend_lbl)
    ## sizing
    max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if rotated_x_lbls else max_x_lbl_length)
    y_title_offset = get_y_title_offset(
        max_y_lbl_length=charting_spec.generic_charting_dets.max_y_lbl_length,
        x_lbl_len=x_lbl_len, rotated_x_lbls=rotated_x_lbls)
    axis_lbl_drop = get_axis_lbl_drop(multi_chart=multi_chart, rotated_x_lbls=rotated_x_lbls,
        max_lbl_lines=charting_spec.generic_charting_dets.max_lbl_lines)
    axis_lbl_rotate = -90 if rotated_x_lbls else 0
    horiz_x_lbls = not rotated_x_lbls
    major_ticks = False if charting_spec.is_time_series and horiz_x_lbls else charting_spec.major_ticks  ## override
    width_after_left_margin = get_width_after_left_margin(
        multi_chart=multi_chart, n_x_items=n_x_items, n_series=n_series,
        max_x_lbl_width=max_x_lbl_width, is_time_series=charting_spec.is_time_series,
        major_ticks=major_ticks, x_title=charting_spec.x_title)
    x_font_size = get_x_font_size(n_x_items=n_x_items, multi_chart=multi_chart)
    left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
        offsets=left_margin_offset_dets, multi_chart=multi_chart,
        y_title_offset=y_title_offset, rotated_x_lbls=rotated_x_lbls)
    width = width_after_left_margin + left_margin_offset
    height = get_height(axis_lbl_drop=axis_lbl_drop,
        rotated_x_lbls=rotated_x_lbls, max_x_lbl_length=max_x_lbl_length)
    return OverallLineChartingDets(
        axis_font_colour=style_dets.chart.axis_font_colour,
        axis_lbl_drop=axis_lbl_drop,
        axis_lbl_rotate=axis_lbl_rotate,
        chart_bg_colour=style_dets.chart.chart_bg_colour,
        colours=colours,
        connector_style=style_dets.dojo.connector_style,
        dp=charting_spec.dp,
        grid_line_width=style_dets.chart.grid_line_width,
        has_micro_ticks_js_bool=has_micro_ticks_js_bool,
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        height=height,
        is_time_series=charting_spec.is_time_series,
        is_time_series_js_bool=is_time_series_js_bool,
        left_margin_offset=left_margin_offset,
        legend_lbl=legend_lbl,
        major_grid_line_colour=style_dets.chart.major_grid_line_colour,
        multi_chart=multi_chart,
        n_records=n_records,
        plot_bg_colour=style_dets.chart.plot_bg_colour,
        plot_font_colour=style_dets.chart.plot_font_colour,
        plot_font_colour_filled=style_dets.chart.plot_font_colour_filled,
        show_trend_line=charting_spec.show_trend_line,
        tooltip_border_colour=style_dets.chart.tooltip_border_colour,
        width=width,
        x_axis_lbls=x_axis_lbls,
        x_axis_specs=x_axis_specs,
        x_font_size=x_font_size,
        x_title=charting_spec.x_title,
        y_max=y_max,
        y_title=charting_spec.y_title,
        y_title_offset=y_title_offset,
    )

def get_dojo_trend_series_dets(
        overall_charting_dets: OverallLineChartingDets, indiv_chart_dets: ChartDetails) -> DojoSeriesDetails:
    only_series = indiv_chart_dets.series_dets[0]
    orig_y_vals = only_series.y_vals
    trend_y_vals = get_trend_y_vals(orig_y_vals)
    trend_series_id = '01'
    trend_series_lbl = 'Trend line'
    trend_line_colour = overall_charting_dets.colours[1]
    trend_options = f"""{{stroke: {{color: "{trend_line_colour}", width: "6px"}}, yLbls: [''], plot: 'default'}}"""
    if overall_charting_dets.is_time_series:
        ## can just use ends given linear gaps in time series
        trend_series_x_axis_specs = [
            overall_charting_dets.x_axis_specs[0], overall_charting_dets.x_axis_specs[-1]]
        trend_series_y_vals = [trend_y_vals[0], trend_y_vals[-1]]
        trend_series_vals = get_time_series_vals(
            trend_series_x_axis_specs, trend_series_y_vals, overall_charting_dets.x_title)
    else:
        trend_series_vals = trend_y_vals
    trand_series_dets = DojoSeriesDetails(
        trend_series_id, trend_series_lbl, trend_series_vals, trend_options)
    return trand_series_dets

def get_indiv_chart_html(overall_charting_dets: OverallLineChartingDets, indiv_chart_dets: ChartDetails,
        *,  chart_counter: int) -> str:
    context = todict(overall_charting_dets, shallow=True)
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = f"<p><b>{indiv_chart_dets.lbl}</b></p>" if overall_charting_dets.multi_chart else ''
    dojo_series_dets = []
    for i, series in enumerate(indiv_chart_dets.series_dets):
        series_id = f"{i:>02}"
        series_lbl = series.legend_lbl
        if overall_charting_dets.is_time_series:
            series_vals = get_time_series_vals(
                overall_charting_dets.x_axis_specs, series.y_vals, overall_charting_dets.x_title)
        else:
            series_vals = str(series.y_vals)
        ## options
        ## e.g. {stroke: {color: '#e95f29', width: '6px'}, yLbls: ['x-val: 2016-01-01<br>y-val: 12<br>0.8%', ... ], plot: 'default'};
        line_colour = overall_charting_dets.colours[i]
        y_lbls_str = str(series.tool_tips)
        options = f"""{{stroke: {{color: "{line_colour}", width: "6px"}}, yLbls: {y_lbls_str}, plot: 'default'}}"""
        dojo_series_dets.append(DojoSeriesDetails(series_id, series_lbl, series_vals, options))
    single_series = len(indiv_chart_dets.series_dets) == 1
    if overall_charting_dets.show_trend_line:
        if not single_series:
            raise Exception("Can only show trend lines if one series of results.")
        trend_series_dets = get_dojo_trend_series_dets(overall_charting_dets, indiv_chart_dets)
        dojo_series_dets.append(trend_series_dets)  ## seems that the later you add something the lower it is
    indiv_context = {
        'chart_uuid': chart_uuid,
        'dojo_series_dets': dojo_series_dets,
        'indiv_title_html': indiv_title_html,
        'page_break': page_break,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result

def get_html(charting_spec: LineChartingSpec, style_dets: StyleDets) -> str:
    styled_dojo_css = get_styled_dojo_css(style_dets.dojo)
    styled_misc_css = get_styled_misc_css(style_dets.chart, style_dets.table)
    context = {
        'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
        'common_css': common_css,
        'styled_dojo_css': styled_dojo_css,
        'styled_misc_css': styled_misc_css,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl_html_top)
    html_top = template.render(context)
    html_result = [html_top, ]
    overall_charting_dets = get_overall_charting_dets(charting_spec, style_dets)
    for n, chart_dets in enumerate(charting_spec.generic_charting_dets.charts_details, 1):
        chart_html = get_indiv_chart_html(overall_charting_dets, chart_dets, chart_counter=n)
        html_result.append(chart_html)
    html_result.append(html_bottom)
    return '\n\n'.join(html_result)
