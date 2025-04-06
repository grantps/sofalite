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
from dataclasses import dataclass
from functools import singledispatch
from typing import Callable, Literal, Sequence

import jinja2

from sofalite.conf.charts.misc import (
    AVG_CHAR_WIDTH_PIXELS, TEXT_WIDTH_WHEN_ROTATED, LeftMarginOffsetDetails)
from sofalite.conf.charts.output.standard import AreaChartingSpec, CategorySpec, LineChartingSpec
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import StyleSpec
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.charts.utils import (
    get_axis_lbl_drop, get_height, get_left_margin_offset,
    get_x_axis_lbl_dets, get_x_axis_font_size, get_y_axis_title_offset)
from sofalite.output.styles.misc import get_generic_css, get_styled_dojo_css, get_styled_misc_css
from sofalite.utils.dates import get_epoch_secs_from_datetime_str

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
            conf["x_axis_font_size"] = {{x_axis_font_size}};
            conf["x_axis_lbls"] = {{x_axis_lbls}};
            conf["y_axis_max"] = {{y_axis_max}};
            conf["x_axis_title"] = "{{x_axis_title}}";
            conf["y_axis_title"] = "{{y_axis_title}}";
            conf["y_axis_title_offset"] = {{y_axis_title_offset}};
            // distinct fields for line charts
            conf["has_micro_ticks"] = {{has_micro_ticks_js_bool}};
            conf["is_time_series"] = {{is_time_series_js_bool}};

        {{chart_js_fn_name}}("line_area_chart_{{chart_uuid}}", series, conf);
    }
    </script>

    <div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
    {{indiv_title_html}}
        <div id="line_area_chart_{{chart_uuid}}"
            style="width: {{width}}px; height: {{height}}px;">
        </div>
        {% if legend_lbl %}
            <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
                {{legend_lbl}}:
            </p>
            <div id="legend_for_line_area_chart_{{chart_uuid}}">
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
        is_single_series: bool
        is_time_series: bool
        is_time_series_js_bool: Literal['true', 'false']
        show_markers: bool
        show_n_records: bool
        # show_smooth_line: bool  ## line
        # show_trend_line: bool  ## line

    @dataclass(frozen=True)
    class CommonMiscSpec:
        chart_js_fn_name: str
        axis_lbl_drop: int
        axis_lbl_rotate: int
        connector_style: str
        grid_line_width: int
        height: float  ## pixels
        left_margin_offset: int
        legend_lbl: str
        x_axis_font_size: float
        x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
        x_axis_specs: Sequence[CategorySpec] | None
        x_axis_title: str
        y_axis_title: str
        y_axis_max: int
        y_axis_title_offset: int
        width: float  ## pixels

    @staticmethod
    def get_time_series_vals(
            x_axis_specs: Sequence[CategorySpec], y_vals: Sequence[float], x_axis_title: str) -> str:
        xs = []
        try:
            for x_axis_spec in x_axis_specs:
                val = str(x_axis_spec.val)
                xs.append(get_epoch_secs_from_datetime_str(val) * 1_000)
        except Exception as e:
            raise Exception(f"Problem processing x-axis specs for {x_axis_title}. "
                f"Orig error: {e}")
        ys = y_vals
        xys = zip(xs, ys, strict=True)
        series_vals = str([{'x': xy[0], 'y': xy[1]} for xy in xys])
        return series_vals

    @staticmethod
    def get_width_after_left_margin(*,
            is_multi_chart: bool, multi_chart_width_factor: float, n_x_items: int,
            n_series: int, max_x_lbl_width: int, is_time_series: bool, show_major_ticks_only: bool,
            x_axis_title: str) -> float:
        """
        Get initial width (will make a final adjustment based on left margin offset).
        show_major_ticks_only -- e.g. want to only see the main labels and won't need it
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
        width_x_axis_title = len(x_axis_title) * AVG_CHAR_WIDTH_PIXELS + padding_pixels
        width = max([n_x_items * width_per_x_item, width_x_axis_title, min_chart_width])
        if show_major_ticks_only:
            width = max(width * 0.4, min_chart_width)
        if is_multi_chart:
            width = width * multi_chart_width_factor
        return width

    @staticmethod
    def get_misc_spec(charting_spec: LineChartingSpec | AreaChartingSpec, style_spec: StyleSpec,
            legend_lbl: str, left_margin_offset_dets: LeftMarginOffsetDetails) -> CommonMiscSpec:
        ## calculation
        if isinstance(charting_spec, LineChartingSpec):
            chart_js_fn_name = 'makeLineChart'
        elif isinstance(charting_spec, AreaChartingSpec):
            chart_js_fn_name = 'makeAreaChart'
        else:
            raise TypeError(f"Expected either Line or Area charting spec but got {type(charting_spec)}")
        x_axis_lbl_dets = get_x_axis_lbl_dets(charting_spec.category_specs)
        x_axis_font_size = get_x_axis_font_size(
            n_x_items=charting_spec.n_x_items, is_multi_chart=charting_spec.is_multi_chart)
        if charting_spec.is_time_series:
            x_axis_specs = charting_spec.category_specs
            x_axis_lbls = '[]'
        else:
            x_axis_specs = None
            x_axis_lbls = '[' + ',\n            '.join(x_axis_lbl_dets) + ']'
        y_axis_max = charting_spec.max_y_val * 1.1
        axis_lbl_drop = get_axis_lbl_drop(is_multi_chart=charting_spec.is_multi_chart,
            rotated_x_lbls=charting_spec.rotate_x_lbls,
            max_x_axis_lbl_lines=charting_spec.max_x_axis_lbl_lines)
        axis_lbl_rotate = -90 if charting_spec.rotate_x_lbls else 0
        max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if charting_spec.rotate_x_lbls else charting_spec.max_x_axis_lbl_len)
        horiz_x_lbls = not charting_spec.rotate_x_lbls
        show_major_ticks_only = (False if charting_spec.is_time_series and horiz_x_lbls
            else charting_spec.show_major_ticks_only)  ## override
        width_after_left_margin = LineArea.get_width_after_left_margin(
            is_multi_chart=charting_spec.is_multi_chart, multi_chart_width_factor=0.9,
            n_x_items=charting_spec.n_x_items, n_series=charting_spec.n_series,
            max_x_lbl_width=max_x_lbl_width, is_time_series=charting_spec.is_time_series,
            show_major_ticks_only=show_major_ticks_only, x_axis_title=charting_spec.x_axis_title)
        x_axis_title_len = len(charting_spec.x_axis_title)
        y_axis_title_offset = get_y_axis_title_offset(
            x_axis_title_len=x_axis_title_len, rotated_x_lbls=charting_spec.rotate_x_lbls)
        left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
            offsets=left_margin_offset_dets, is_multi_chart=charting_spec.is_multi_chart,
            y_axis_title_offset=y_axis_title_offset, rotated_x_lbls=charting_spec.rotate_x_lbls)
        width = left_margin_offset + width_after_left_margin
        height = get_height(axis_lbl_drop=axis_lbl_drop,
            rotated_x_lbls=charting_spec.rotate_x_lbls, max_x_axis_lbl_len=charting_spec.max_x_axis_lbl_len)
        return LineArea.CommonMiscSpec(
            chart_js_fn_name=chart_js_fn_name,
            axis_lbl_drop=axis_lbl_drop,
            axis_lbl_rotate=axis_lbl_rotate,
            connector_style=style_spec.dojo.connector_style,
            grid_line_width=style_spec.chart.grid_line_width,
            height=height,
            left_margin_offset=left_margin_offset,
            legend_lbl=legend_lbl,
            width=width,
            x_axis_font_size=x_axis_font_size,
            x_axis_lbls=x_axis_lbls,
            x_axis_specs=x_axis_specs,
            x_axis_title=charting_spec.x_axis_title,
            y_axis_title=charting_spec.y_axis_title,
            y_axis_max=y_axis_max,
            y_axis_title_offset=y_axis_title_offset,)
