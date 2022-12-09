"""
When we chart some data we might produce one individual chart or a series of charts
(for example, one chart per country).

Each chart might have one series of values or multiple series. A clustered bar chart,
for example, will have one series per group.

Sometimes we will have multiple charts and each chart will have multiple series
e.g. we have a chart per gender and within each chart a series per country.

Sometimes we will have a single chart with only one series of data.

So ...

A charting_spec is the top-level object.
It defines attributes shared across all individual charts:
  * x_axis_specs or slice_category_specs defining val and lbl (split into lines)
and depending on type of chart:
  * x_axis_title
  * y_axis_title
  * rotate_x_lbls
  * show_n_records
  * show_borders
  * x_axis_font_size
  * etc.
It is often extended e.g. for bar, line etc
Will have two children: Axes vs NoAxes (pie) versions
Axes will have lots of children - bar, line, area etc
indiv_chart_specs (often just one) are below charting_spec
Each indiv_chart_spec has data_series_specs below (often just one)
Each data_series_item amount, lbl, and tooltip
"""
from dataclasses import dataclass
from typing import Any, Literal, Sequence

from sofalite.conf.misc import StrConst

AVG_LINE_HEIGHT_PIXELS = 12
AVG_CHAR_WIDTH_PIXELS = 6.5
DOJO_Y_TITLE_OFFSET_0 = 45
TEXT_WIDTH_WHEN_ROTATED = 4
MIN_CHART_WIDTH_PIXELS = 450
MAX_SAFE_X_LBL_LEN_PIXELS = 180

JS_BOOL = Literal['true', 'false']

## The categories e.g. NZ (common across all individual charts and series within any charts)
@dataclass(frozen=True)
class CategorySpec:
    """
    lbl: HTML label e.g. "Ubuntu<br>Linux" - ready for display in chart
    """
    val: Any
    lbl: str

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
        self.amounts = [data_item.amount for data_item in self.data_items]
        self.tooltips = [data_item.tooltip for data_item in self.data_items]

@dataclass
class IndivChartSpec:
    lbl: str | None
    data_series_specs: Sequence[DataSeriesSpec]

    def __post_init__(self):
        self.n_records = 0
        for data_series_spec in self.data_series_specs:
            for data_item in data_series_spec.data_items:
                self.n_records += data_item.amount

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
        ## Derived attributes
        self.is_multi_chart = len(self.indiv_chart_specs) > 1
        self.n_series = len(self.indiv_chart_specs[0].data_series_specs)
        self.is_single_series = (self.n_series == 1)

@dataclass
class ChartingSpecAxes(ChartingSpec):
    legend_lbl: str
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

        max_x_lbl_length = 0
        max_x_lbl_lines = 0
        for category_spec in self.category_specs:
            x_lbl_length = len(category_spec.lbl)
            if x_lbl_length > max_x_lbl_length:
                max_x_lbl_length = x_lbl_length
            x_lbl_lines = len(category_spec.lbl.split('<br>'))
            if x_lbl_lines > max_x_lbl_lines:
                max_x_lbl_lines = x_lbl_lines

        max_y_lbl_length = 0
        max_y_val = 0
        for indiv_chart_spec in self.indiv_chart_specs:
            for data_series_spec in indiv_chart_spec.data_series_specs:
                for data_item in data_series_spec.data_items:
                    y_lbl_length = len(data_item.lbl)
                    if y_lbl_length > max_y_lbl_length:
                        max_y_lbl_length = y_lbl_length
                    y_val = data_item.amount
                    if y_val > max_y_val:
                        max_y_val = y_val

        self.max_x_lbl_length = max_x_lbl_length ## may be needed to set chart height if labels are rotated
        self.max_y_lbl_length = max_y_lbl_length  ## used to set left axis shift of chart(s) - so there is room for the y labels
        self.max_x_lbl_lines = max_x_lbl_lines  ## used to set axis lbl drop
        self.max_y_val = max_y_val

@dataclass
class ChartingSpecNoAxes(ChartingSpec):
    ...

@dataclass
class BarChartingSpec(ChartingSpecAxes):
    show_borders: bool

@dataclass
class LineChartingSpec(ChartingSpecAxes):
    is_time_series: bool
    show_major_ticks_only: bool
    show_markers: bool
    show_smooth_line: bool
    show_trend_line: bool

    def __post_init__(self):
        super().__post_init__()
        if (self.show_smooth_line or self.show_trend_line) and not self.single_series:
            raise Exception("Only single-series line charts can have a trend line or the smoothed option.")

@dataclass
class AreaChartingSpec(ChartingSpecAxes):
    is_time_series: bool
    show_major_ticks_only: bool
    show_markers: bool

@dataclass
class PieChartingSpec(ChartingSpecNoAxes):
    ...

class PlotStyle(StrConst):
    """
    Self-defined plot names added with addPlot in the sofalite chart js file.
     Each has different settings re: tension and markers.
    """
    UNMARKED = 'unmarked'
    DEFAULT = 'default'
    CURVED = 'curved'

@dataclass(frozen=True)
class LeftMarginOffsetDetails:
    initial_offset: int
    wide_offset: int
    rotate_offset: int
    multi_chart_offset: int

@dataclass(frozen=True)
class DojoSeriesDetails:
    series_id: str  ## e.g. 01
    lbl: str
    vals: Sequence[float]
    options: str
