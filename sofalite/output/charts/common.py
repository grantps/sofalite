from abc import ABC
from dataclasses import dataclass
from typing import Callable, Literal, Sequence

import jinja2

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, TEXT_WIDTH_WHEN_ROTATED, LeftMarginOffsetDetails, XAxisSpec)
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import StyleDets
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.charts.utils import (
    get_axis_lbl_drop, get_height, get_left_margin_offset,
    get_x_axis_lbl_dets, get_x_font_size, get_y_max, get_y_title_offset)
from sofalite.output.styles.misc import common_css, get_styled_dojo_css, get_styled_misc_css
from sofalite.utils.dates import get_epoch_secs_from_datetime_str
from sofalite.utils.maths import format_num

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

    MIN_PIXELS_PER_X_ITEM = 10
    DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM = 8
    DOJO_MICRO_TICKS_NEEDED_PER_X_ITEM = 100

    DUMMY_TOOL_TIPS = ['', ]  ## no labels or markers on trend line so dummy tool tips OK

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
            conf["axis_font_colour"] = "{{axis_font}}";
            conf["axis_lbl_drop"] = {{axis_lbl_drop}};
            conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
            conf["chart_bg_colour"] = "{{chart_bg}}";
            conf["connector_style"] = "{{connector_style}}";
            conf["grid_line_width"] = {{grid_line_width}};
            conf["left_margin_offset"] = {{left_margin_offset}};
            conf["major_grid_line_colour"] = "{{major_grid_line}}";
            conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
            conf["n_records"] = "{{n_records}}";
            conf["plot_bg_colour"] = "{{plot_bg}}";
            conf["plot_font_colour"] = "{{plot_font}}";
            conf["plot_font_colour_filled"] = "{{plot_font_filled}}";
            conf["tooltip_border_colour"] = "{{tooltip_border}}";
            conf["x_axis_lbls"] = {{x_axis_lbls}};
            conf["x_font_size"] = {{x_font_size}};
            conf["x_title"] = "{{x_title}}";
            conf["y_max"] = {{y_max}};
            conf["y_title"] = "{{y_title}}";
            conf["y_title_offset"] = {{y_title_offset}};
            // distinct fields for line charts
            conf["has_micro_ticks"] = {{has_micro_ticks_js_bool}};
            conf["is_time_series"] = {{is_time_series_js_bool}};

        {{chart_js_fn_name}}("line_chart_{{chart_uuid}}", series, conf);
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

    @dataclass(frozen=True)
    class CommonColourSpec:
        axis_font: str
        chart_bg: str
        # colours: Sequence[str]  ## line
        # fill: str  ## area
        # line: str  ## are
        major_grid_line: str
        plot_bg: str
        plot_font: str
        plot_font_filled: str
        tooltip_border: str

    @dataclass(frozen=True)
    class CommonOptions:
        has_micro_ticks_js_bool: Literal['true', 'false']
        has_minor_ticks_js_bool: Literal['true', 'false']
        is_multi_chart: bool
        is_time_series: bool
        is_time_series_js_bool: Literal['true', 'false']
        show_markers: bool
        # show_smooth_line: bool  ## line
        # show_trend_line: bool  ## line

    @dataclass(frozen=True)
    class CommonMiscSpec:
        chart_js_fn_name: str
        axis_lbl_drop: int
        axis_lbl_rotate: int
        connector_style: str
        dp: int
        grid_line_width: int
        height: float  ## pixels
        left_margin_offset: int
        legend_lbl: str
        n_records: int
        x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
        x_axis_specs: Sequence[XAxisSpec] | None
        x_font_size: float
        x_title: str
        y_max: int
        y_title: str
        y_title_offset: int
        width: float  ## pixels

    @staticmethod
    def get_time_series_vals(
            x_axis_specs: Sequence[XAxisSpec], y_vals: Sequence[float], x_title: str) -> str:
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

    @staticmethod
    def get_width_after_left_margin(*,
            is_multi_chart: bool, multi_chart_width_factor: float, n_x_items: int,
            n_series: int, max_x_lbl_width: int, is_time_series: bool, major_ticks: bool,
            x_title: str) -> float:
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
            width_per_x_item = LineArea.MIN_PIXELS_PER_X_ITEM
        else:
            width_per_x_item = (max([LineArea.MIN_PIXELS_PER_X_ITEM,
                max_x_lbl_width * AVG_CHAR_WIDTH_PIXELS]) + padding_pixels)
        width_x_title = len(x_title) * AVG_CHAR_WIDTH_PIXELS + padding_pixels
        width = max([n_x_items * width_per_x_item, width_x_title, min_chart_width])
        if major_ticks:
            width = max(width * 0.4, min_chart_width)
        if is_multi_chart:
            width = width * multi_chart_width_factor
        return width

    @staticmethod
    def get_misc_spec(charting_spec: ChartingSpec, style_dets: StyleDets,
            legend_lbl: str, left_margin_offset_dets: LeftMarginOffsetDetails) -> CommonMiscSpec:
        ## convenience pre-calcs
        rotated_x_lbls = charting_spec.rotate_x_lbls
        is_multi_chart = (len(charting_spec.generic_charting_dets.charts_details) > 1)
        first_chart_dets = charting_spec.generic_charting_dets.charts_details[0]
        n_series = len(first_chart_dets.series_dets)
        first_series = first_chart_dets.series_dets[0]
        first_x_axis_spec = first_series.x_axis_specs[0]
        x_lbl_len = len(first_x_axis_spec.lbl)
        n_x_items = len(first_series.x_axis_specs)
        max_x_lbl_length = charting_spec.generic_charting_dets.max_x_lbl_length
        ## calculation
        n_records = 'N = ' + format_num(first_chart_dets.n_records) if charting_spec.show_n else ''
        x_axis_lbl_dets = get_x_axis_lbl_dets(first_series.x_axis_specs)
        x_font_size = get_x_font_size(n_x_items=n_x_items, is_multi_chart=is_multi_chart)
        if charting_spec.is_time_series:
            x_axis_specs = first_series.x_axis_specs
            x_axis_lbls = '[]'
        else:
            x_axis_specs = None
            x_axis_lbls = '[' + ',\n            '.join(x_axis_lbl_dets) + ']'
        y_max = get_y_max(charting_spec.generic_charting_dets.charts_details)
        axis_lbl_drop = get_axis_lbl_drop(is_multi_chart=is_multi_chart, rotated_x_lbls=rotated_x_lbls,
            max_lbl_lines=charting_spec.generic_charting_dets.max_lbl_lines)
        axis_lbl_rotate = -90 if rotated_x_lbls else 0
        max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if rotated_x_lbls else max_x_lbl_length)
        horiz_x_lbls = not rotated_x_lbls
        major_ticks = False if charting_spec.is_time_series and horiz_x_lbls else charting_spec.major_ticks  ## override
        width_after_left_margin = LineArea.get_width_after_left_margin(
            is_multi_chart=is_multi_chart, multi_chart_width_factor=0.9, n_x_items=n_x_items, n_series=n_series,
            max_x_lbl_width=max_x_lbl_width, is_time_series=charting_spec.is_time_series,
            major_ticks=major_ticks, x_title=charting_spec.x_title)
        y_title_offset = get_y_title_offset(
            max_y_lbl_length=charting_spec.generic_charting_dets.max_y_lbl_length,
            x_lbl_len=x_lbl_len, rotated_x_lbls=rotated_x_lbls)
        left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
            offsets=left_margin_offset_dets, is_multi_chart=is_multi_chart,
            y_title_offset=y_title_offset, rotated_x_lbls=rotated_x_lbls)
        width = width_after_left_margin + left_margin_offset
        height = get_height(axis_lbl_drop=axis_lbl_drop,
            rotated_x_lbls=rotated_x_lbls, max_x_lbl_length=max_x_lbl_length)
        return LineArea.CommonMiscSpec(
            chart_js_fn_name='makeLineChart',
            axis_lbl_drop=axis_lbl_drop,
            axis_lbl_rotate=axis_lbl_rotate,
            connector_style=style_dets.dojo.connector_style,
            dp=charting_spec.dp,
            grid_line_width=style_dets.chart.grid_line_width,
            height=height,
            left_margin_offset=left_margin_offset,
            legend_lbl=legend_lbl,
            n_records=n_records,
            width=width,
            x_axis_lbls=x_axis_lbls,
            x_axis_specs=x_axis_specs,
            x_font_size=x_font_size,
            x_title=charting_spec.x_title,
            y_max=y_max,
            y_title=charting_spec.y_title,
            y_title_offset=y_title_offset,)
