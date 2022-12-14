from dataclasses import dataclass
from typing import Sequence

from sofalite.output.charts.utils import get_optimal_axis_bounds

## Histogram

@dataclass
class HistoIndivChartSpec:
    lbl: str | None
    n_records: int
    norm_y_vals: Sequence[float]
    y_vals: Sequence[float]

@dataclass
class HistoChartingSpec:
    bin_lbls: Sequence[str]
    indiv_chart_specs: Sequence[HistoIndivChartSpec]
    max_x_val: float
    min_x_val: float
    show_borders: bool
    show_n_records: bool
    show_normal_curve: bool
    var_lbl: str | None
    x_axis_font_size: int

    def __post_init__(self):
        self.n_bins = len(self.bin_lbls)
        self.n_charts = len(self.indiv_chart_specs)
        self.is_multi_chart = self.n_charts > 1
        max_y_val = 0
        for indiv_chart_spec in self.indiv_chart_specs:
            indiv_chart_max_y_val = max(indiv_chart_spec.y_vals)
            if indiv_chart_max_y_val > max_y_val:
                max_y_val = indiv_chart_max_y_val
        self.max_y_val = max_y_val

## Scatterplot

@dataclass
class ScatterDataSeriesSpec:
    lbl: str | None
    xy_pairs: list[tuple[float, float]]

@dataclass
class ScatterIndivChartSpec:
    data_series_specs: Sequence[ScatterDataSeriesSpec]
    lbl: str | None

    def __post_init__(self):
        n_records = 0
        for data_series_spec in self.data_series_specs:
            n_records += len(data_series_spec.xy_pairs)
        self.n_records = n_records

@dataclass
class ScatterChartingSpec:
    indiv_chart_specs: Sequence[ScatterIndivChartSpec]
    legend_lbl: str
    show_dot_borders: bool
    show_n_records: bool
    show_regression_line: bool
    x_axis_font_size: int
    x_axis_title: str
    y_axis_title: str

    def __post_init__(self):
        ## Derived attributes (could make actual fields using = fields(init=False) but OK as mere attributes)
        all_min_xs = []
        all_max_xs = []
        all_min_ys = []
        all_max_ys = []
        has_plenty_list = []
        for indiv_chart_spec in self.indiv_chart_specs:
            for data_series_spec in indiv_chart_spec.data_series_specs:
                xs = [xy_pair[0] for xy_pair in data_series_spec.xy_pairs]
                ys = [xy_pair[1] for xy_pair in data_series_spec.xy_pairs]
                ## xs
                indiv_min_x_val = min(xs)
                all_min_xs.append(indiv_min_x_val)
                indiv_max_x_val = max(xs)
                all_max_xs.append(indiv_max_x_val)
                ## ys
                indiv_min_y_val = min(ys)
                all_min_ys.append(indiv_min_y_val)
                indiv_max_y_val = max(ys)
                all_max_ys.append(indiv_max_y_val)
                ## has_ticks
                x_set = set(xs)
                has_plenty_unique_x_vals = len(x_set) >= 4
                has_plenty_list.append(has_plenty_unique_x_vals)
        ## If any of the series in any of the charts have plenty of distinct x-values
        ## keep the minor ticks - otherwise drop them
        self.has_minor_ticks = any(has_plenty_list)
        min_x_val = min(all_min_xs)
        max_x_val = max(all_max_xs)
        self.min_x_val, self.max_x_val = get_optimal_axis_bounds(min_x_val, max_x_val)
        min_y_val = min(all_min_ys)
        max_y_val = max(all_max_ys)
        self.min_y_val, self.max_y_val = get_optimal_axis_bounds(min_y_val, max_y_val)
        ## Derived attributes (could make actual fields using = fields(init=False) but OK as mere attributes)
        self.n_charts = len(self.indiv_chart_specs)
        self.is_multi_chart = self.n_charts > 1
        self.n_series = len(self.indiv_chart_specs[0].data_series_specs)
        self.is_single_series = (self.n_series == 1)
