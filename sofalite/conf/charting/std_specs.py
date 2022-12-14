from dataclasses import dataclass
from typing import Any, Sequence

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
        self.amounts = []
        self.lbls = []
        self.tooltips = []
        for data_item in self.data_items:
            self.amounts.append(data_item.amount)
            self.lbls.append(data_item.lbl)
            self.tooltips.append(data_item.tooltip)

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
        if (self.show_smooth_line or self.show_trend_line) and not self.is_single_series:
            raise Exception("Only single-series line charts can have a trend line or the smoothed option.")

@dataclass
class AreaChartingSpec(ChartingSpecAxes):
    is_time_series: bool
    show_major_ticks_only: bool
    show_markers: bool

@dataclass
class PieChartingSpec(ChartingSpecNoAxes):
    def __post_init__(self):
        super().__post_init__()
        if not self.is_single_series:
            raise TypeError("Pie Charts have to have only one data series per chart")
