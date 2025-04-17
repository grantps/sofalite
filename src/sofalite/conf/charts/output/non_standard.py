from collections.abc import Sequence
from dataclasses import dataclass

from sofalite.conf.charts.output.standard import CategorySpec
from sofalite.conf.stats.utils import get_optimal_axis_bounds

## Histogram

@dataclass
class HistoIndivChartSpec:
    lbl: str | None
    n_records: int
    norm_y_vals: Sequence[float]
    y_vals: Sequence[int]

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
                max(indiv_chart_spec.norm_y_vals)
            )
            if indiv_chart_max_y_val > y_axis_max_val:
                y_axis_max_val = indiv_chart_max_y_val
        self.y_axis_max_val = y_axis_max_val

## Scatterplot

@dataclass
class ScatterDataSeriesSpec:
    lbl: str | None
    xy_pairs: Sequence[tuple[float, float]]

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
    legend_lbl: str | None
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
                indiv_x_axis_min_val = min(xs)
                all_min_xs.append(indiv_x_axis_min_val)
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
        self.x_axis_min_val, self.x_axis_max_val = get_optimal_axis_bounds(min_x_val, max_x_val)
        min_y_val = min(all_min_ys)
        max_y_val = max(all_max_ys)
        self.y_axis_min_val, self.y_axis_max_val = get_optimal_axis_bounds(min_y_val, max_y_val)
        ## Derived attributes (could make actual fields using = fields(init=False) but OK as mere attributes)
        self.n_charts = len(self.indiv_chart_specs)
        self.is_multi_chart = self.n_charts > 1
        self.n_series = len(self.indiv_chart_specs[0].data_series_specs)
        self.is_single_series = (self.n_series == 1)

## Boxplot

@dataclass
class BoxplotDataItem:
    ## indiv_box_lbl - derived from series lbl and category spec lbls in BoxplotIndivChartSpec
    box_bottom: float
    box_bottom_rounded: float
    bottom_whisker: float
    bottom_whisker_rounded: float
    median: float
    median_rounded: float
    outliers: Sequence[float] | None
    outliers_rounded: Sequence[float] | None
    box_top: float
    box_top_rounded: float
    top_whisker: float
    top_whisker_rounded: float
    ## center - derived from offset depending on which item on series (move rightwards) in BoxplotIndivChartSpec

@dataclass
class BoxplotDataSeriesSpec:
    lbl: str | None
    box_items: Sequence[BoxplotDataItem | None]  ## Use None to indicate a gap for a particular series e.g. US missing
    ## offset - set in BoxplotIndivChartSpec

@dataclass
class BoxplotIndivChartSpec:
    data_series_specs: Sequence[BoxplotDataSeriesSpec]
    n_records: int

    def __post_init__(self):
        n_series = len(self.data_series_specs)
        n_gaps = n_series - 1
        shrinkage = n_series * 0.6
        gap = 0.4 / shrinkage
        self.bar_width = 0.15 / shrinkage
        ## offset (left or right of whatever center is, offset is the same for all boxes in series)
        ## and actual center (different for every box in chart so boxes don't overlap / collide etc)
        offset_start = -((gap * n_gaps) / 2)  ## if only one box, offset = 0 i.e. middle
        for series_i, data_series_spec in enumerate(self.data_series_specs):
            data_series_spec.offset = offset_start + (series_i * gap)
            for box_n, box_item in enumerate(data_series_spec.box_items, 1):
                if not box_item:
                    continue
                box_item.center = box_n + data_series_spec.offset

@dataclass
class BoxplotChartingSpec:
    category_specs: Sequence[CategorySpec]
    indiv_chart_specs: Sequence[BoxplotIndivChartSpec]  ## even though only ever one follow the standard pattern so get_html works for all chart types the same way
    legend_lbl: str | None
    rotate_x_lbls: bool
    show_n_records: bool
    x_axis_title: str
    y_axis_title: str

    def __post_init__(self):
        if len(self.indiv_chart_specs) != 1:
            raise Exception("Boxplot charts can only have one individual chart")
        self.has_minor_ticks = len(self.category_specs) > 10
        self.n_series = len(self.indiv_chart_specs[0].data_series_specs)
        self.is_single_series = (self.n_series == 1)
        self.n_x_items = len(self.category_specs)
        ## get max x axis val
        self.x_axis_max_val = len(self.category_specs) + 0.5
        ## get min and max y values
        all_min_ys = []
        all_max_ys = []
        for data_series_spec in self.indiv_chart_specs[0].data_series_specs:
            for box_item in data_series_spec.box_items:
                if not box_item:
                    continue
                items_with_low_ys = [box_item.bottom_whisker, ]
                items_with_high_ys = [box_item.top_whisker, ]
                if box_item.outliers:
                    items_with_low_ys += box_item.outliers
                    items_with_high_ys += box_item.outliers
                box_min_y_val = min(items_with_low_ys)
                box_max_y_val = max(items_with_high_ys)
                all_min_ys.append(box_min_y_val)
                all_max_ys.append(box_max_y_val)
        min_y_val = min(all_min_ys)
        max_y_val = max(all_max_ys)
        self.y_axis_min_val, self.y_axis_max_val = get_optimal_axis_bounds(min_y_val, max_y_val)
        ## misc
        max_x_axis_lbl_len = 0
        max_x_axis_lbl_lines = 0
        for category_spec in self.category_specs:
            x_axis_lbl_len = len(category_spec.lbl)
            if x_axis_lbl_len > max_x_axis_lbl_len:
                max_x_axis_lbl_len = x_axis_lbl_len
            x_lbl_lines = len(category_spec.lbl.split('<br>'))
            if x_lbl_lines > max_x_axis_lbl_lines:
                max_x_axis_lbl_lines = x_lbl_lines
        self.max_x_axis_lbl_len = max_x_axis_lbl_len
        self.max_x_axis_lbl_lines = max_x_axis_lbl_lines  ## used to set axis lbl drop
        ## set box labels
        for indiv_chart_spec in self.indiv_chart_specs:
            for data_series_spec in indiv_chart_spec.data_series_specs:
                series_lbl = data_series_spec.lbl
                for box_item, category_spec in zip(data_series_spec.box_items, self.category_specs, strict=True):
                    if box_item:
                        box_item.indiv_box_lbl = f"{series_lbl}, {category_spec.lbl}"
