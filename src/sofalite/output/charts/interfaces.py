from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from sofalite.conf import AVG_CHAR_WIDTH_PIXELS
from sofalite.utils.dates import get_epoch_secs_from_datetime_str


class PlotStyle(StrEnum):
    """
    Self-defined plot names added with addPlot in the sofalite chart js file.
     Each has different settings re: tension and markers.
    """
    UNMARKED = 'unmarked'
    DEFAULT = 'default'
    CURVED = 'curved'

## The categories e.g. NZ (common across all individual charts and series within any charts)
@dataclass(frozen=True)
class CategorySpec:
    """
    lbl: HTML label e.g. "Ubuntu<br>Linux" - ready for display in chart
    """
    val: Any
    lbl: str

@dataclass(frozen=True)
class DojoSeriesDetails:
    series_id: str  ## e.g. 01
    lbl: str
    vals: Sequence[float]
    options: str

@dataclass(frozen=True)
class LeftMarginOffsetDetails:
    initial_offset: int
    wide_offset: int
    rotate_offset: int
    multi_chart_offset: int

## Not the categories now but the data per category e.g. 123
@dataclass(frozen=True)
class DataItem:
    """
    lbl: HTML label e.g. "Ubuntu<br>Linux" - ready for display in chart
    """
    amount: float
    lbl: str
    tooltip: str

@dataclass
class DataSeriesSpec:
    lbl: str | None
    data_items: Sequence[DataItem]

    def __post_init__(self):
        """
        Used in JS which often grabs bits separately.
        """
        self.amounts = []
        self.lbls = []
        self.tooltips = []
        for data_item in self.data_items:
            if data_item is not None:
                self.amounts.append(data_item.amount)
                self.lbls.append(data_item.lbl)
                self.tooltips.append(data_item.tooltip)
            else:
                self.amounts.append(0)
                self.lbls.append('')
                self.tooltips.append('')

@dataclass
class IndivChartSpec:
    lbl: str | None
    data_series_specs: Sequence[DataSeriesSpec]
    n_records: int

@dataclass
class ChartingSpec:
    category_specs: Sequence[CategorySpec]
    indiv_chart_specs: Sequence[IndivChartSpec]
    show_n_records: bool

    def __post_init__(self):
        ## Validation
        ## Check number of categories matches number of data items in every series
        n_categories = len(self.category_specs)
        for indiv_chart_spec in self.indiv_chart_specs:
            for data_series_spec in indiv_chart_spec.data_series_specs:
                n_data_items = len(data_series_spec.data_items)
                if n_data_items != n_categories:
                    raise Exception("Must be same number of categories "
                        "as data items in every series in every individual chart "
                        f"but {n_categories=} while {n_data_items=}")
        ## Derived attributes (could make actual fields using = fields(init=False) but OK as mere attributes)
        self.n_charts = len(self.indiv_chart_specs)
        self.is_multi_chart = self.n_charts > 1
        self.n_series = len(self.indiv_chart_specs[0].data_series_specs)
        self.is_single_series = (self.n_series == 1)

@dataclass
class ChartingSpecAxes(ChartingSpec):

    legend_lbl: str | None
    rotate_x_lbls: bool
    x_axis_font_size: int
    x_axis_title: str
    y_axis_title: str

    def __post_init__(self):
        """
        Check number of categories matches number of data items in every series
        """
        super().__post_init__()
        ## derived attributes
        self.n_x_items = len(self.category_specs)

        max_x_axis_lbl_len = 0
        max_x_axis_lbl_lines = 0
        for category_spec in self.category_specs:
            x_axis_lbl_len = len(category_spec.lbl)
            if x_axis_lbl_len > max_x_axis_lbl_len:
                max_x_axis_lbl_len = x_axis_lbl_len
            x_lbl_lines = len(category_spec.lbl.split('<br>'))
            if x_lbl_lines > max_x_axis_lbl_lines:
                max_x_axis_lbl_lines = x_lbl_lines

        max_y_val = 0
        for indiv_chart_spec in self.indiv_chart_specs:
            for data_series_spec in indiv_chart_spec.data_series_specs:
                for data_item in data_series_spec.data_items:
                    if data_item is None:
                        continue
                    y_val = data_item.amount
                    if y_val > max_y_val:
                        max_y_val = y_val

        self.max_x_axis_lbl_len = max_x_axis_lbl_len  ## may be needed to set chart height if labels are rotated
        self.max_x_axis_lbl_lines = max_x_axis_lbl_lines  ## used to set axis lbl drop
        self.max_y_val = max_y_val

@dataclass
class ChartingSpecNoAxes(ChartingSpec):
    def __post_init__(self):
        super().__post_init__()

@dataclass
class AreaChartingSpec(ChartingSpecAxes):
    is_time_series: bool
    show_major_ticks_only: bool
    show_markers: bool

@dataclass
class LineChartingSpec(ChartingSpecAxes):
    is_time_series: bool
    show_major_ticks_only: bool
    show_markers: bool
    show_smooth_line: bool
    show_trend_line: bool

    def __post_init__(self):
        super().__post_init__()
        if (self.show_smooth_line or self.show_trend_line) and not self.is_single_series:
            raise Exception("Only single-series line charts can have a trend line or the smoothed option.")


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
