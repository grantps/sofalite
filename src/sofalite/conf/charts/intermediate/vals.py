from dataclasses import dataclass
from typing import Sequence

from sofalite.conf.charts.output.non_standard import (
    BoxplotDataItem, BoxplotDataSeriesSpec, BoxplotIndivChartSpec, HistoIndivChartSpec)
from sofalite.conf.charts.output.standard import CategorySpec
from sofalite.conf.stats.interfaces import BoxDets, BoxplotType, SortOrder
from sofalite.init_conf.stats.engine import get_normal_ys
from sofalite.conf.utils.histogram import get_bin_details_from_vals

@dataclass(frozen=False)
class BoxplotCategoryItemValsSpec:
    category_val: float | str  ## e.g. 1
    category_val_lbl: str  ## e.g. Japan
    vals: Sequence[float]

def get_sorted_category_specs(
        category_vals_specs: Sequence[BoxplotCategoryItemValsSpec], category_sort_order: SortOrder):
    """
    category_specs = [
        CategorySpec(val=1, lbl='New Zealand'),
        CategorySpec(val=2, lbl='United States'),
        CategorySpec(val=3, lbl='Canada'),
    ]
    """
    category_specs = []
    for category_vals_spec in category_vals_specs:
        category_spec = CategorySpec(
            val=category_vals_spec.category_val,
            lbl=category_vals_spec.category_val_lbl,
        )
        category_specs.append(category_spec)
    if category_sort_order == SortOrder.VALUE:
        sorted_category_specs = sorted(category_specs, key=lambda x: x.val)
    elif category_sort_order == SortOrder.LABEL:
        sorted_category_specs = sorted(category_specs, key=lambda x: x.lbl)
    else:
        raise ValueError("Boxplot categories can only be sorted by value or label")
    return sorted_category_specs

@dataclass(frozen=False)
class BoxplotCategoryValsSpecs:
    chart_lbl: str | None
    series_fld_lbl: str | None
    category_fld_lbl: str  ## e.g. Country
    fld_lbl: str
    category_vals_specs: Sequence[BoxplotCategoryItemValsSpec]
    category_sort_order: SortOrder
    boxplot_type: BoxplotType

    def to_sorted_category_specs(self):
        return get_sorted_category_specs(self.category_vals_specs, self.category_sort_order)

    def to_indiv_chart_spec(self, *, dp: int = 3) -> BoxplotIndivChartSpec:
        n_records = 0
        box_items = []
        for category_vals_spec in self.category_vals_specs:
            n_records += len(category_vals_spec.vals)
            box_dets = BoxDets(category_vals_spec.vals, self.boxplot_type)
            box_item = BoxplotDataItem(
                box_bottom=box_dets.box_bottom,
                box_bottom_rounded=round(box_dets.box_bottom, dp),
                bottom_whisker=box_dets.bottom_whisker,
                bottom_whisker_rounded=round(box_dets.bottom_whisker, dp),
                median=box_dets.median,
                median_rounded=round(box_dets.median, dp),
                outliers=box_dets.outliers,
                outliers_rounded=[round(outlier, dp) for outlier in box_dets.outliers],
                box_top=box_dets.box_top,
                box_top_rounded=round(box_dets.box_top, dp),
                top_whisker=box_dets.top_whisker,
                top_whisker_rounded=round(box_dets.top_whisker, dp)
            )
            box_items.append(box_item)
        data_series_spec = BoxplotDataSeriesSpec(
            lbl=None,
            box_items=box_items,
        )
        indiv_chart_spec = BoxplotIndivChartSpec(
            data_series_specs=[data_series_spec, ],
            n_records=n_records,
        )
        return indiv_chart_spec

@dataclass(frozen=False)
class BoxplotSeriesItemCategoryValsSpecs:
    series_val: float | str  ## e.g. 1
    series_val_lbl: str  ## e.g. Male
    category_vals_specs: Sequence[BoxplotCategoryItemValsSpec]

@dataclass(frozen=False)
class BoxplotSeriesCategoryValsSpecs:
    series_fld_lbl: str  ## e.g. Gender
    category_fld_lbl: str  ## e.g. Country
    fld_lbl: str
    series_category_vals_specs: Sequence[BoxplotSeriesItemCategoryValsSpecs]
    category_sort_order: SortOrder
    boxplot_type: BoxplotType

    def to_sorted_category_specs(self):
        first_series_category_vals_specs = self.series_category_vals_specs[0].category_vals_specs  ## same for all of them so look at first chart
        return get_sorted_category_specs(first_series_category_vals_specs, self.category_sort_order)

    def to_indiv_chart_spec(self, *, dp: int = 3):
        n_records = 0
        data_series_specs = []
        for series_item_category_vals_specs in self.series_category_vals_specs:
            box_items = []
            for category_vals_spec in series_item_category_vals_specs.category_vals_specs:
                n_records += len(category_vals_spec.vals)
                box_dets = BoxDets(category_vals_spec.vals, self.boxplot_type)
                box_item = BoxplotDataItem(
                    box_bottom=box_dets.box_bottom,
                    box_bottom_rounded=round(box_dets.box_bottom, dp),
                    bottom_whisker=box_dets.bottom_whisker,
                    bottom_whisker_rounded=round(box_dets.bottom_whisker, dp),
                    median=box_dets.median,
                    median_rounded=round(box_dets.median, dp),
                    outliers=box_dets.outliers,
                    outliers_rounded=[round(outlier, dp) for outlier in box_dets.outliers],
                    box_top=box_dets.box_top,
                    box_top_rounded=round(box_dets.box_top, dp),
                    top_whisker=box_dets.top_whisker,
                    top_whisker_rounded=round(box_dets.top_whisker, dp)
                )
                box_items.append(box_item)
            data_series_spec = BoxplotDataSeriesSpec(
                lbl=None,
                box_items=box_items,
            )
            data_series_specs.append(data_series_spec)
        indiv_chart_spec = BoxplotIndivChartSpec(
            data_series_specs=data_series_specs,
            n_records=n_records,
        )
        return indiv_chart_spec

## ========================================================================================

@dataclass(frozen=False)
class HistoValsSpec:
    chart_lbl: str | None
    fld_lbl: str
    vals: Sequence[float]

    def __post_init__(self):
        bin_dets, bin_freqs = get_bin_details_from_vals(self.vals)
        self.bin_dets = bin_dets
        self.bin_freqs = bin_freqs

    def to_indiv_chart_specs(self) -> Sequence[HistoIndivChartSpec]:
        """
        Translate vals into all the bits and pieces required by each HistoIndivChartSpec
        using stats_calc.histogram
        """
        import numpy as np
        bin_starts = [start for start, end in self.bin_dets.bin_ranges]
        norm_y_vals = get_normal_ys(self.vals, np.array(bin_starts))
        sum_y_vals = sum(self.bin_freqs)
        sum_norm_y_vals = sum(norm_y_vals)
        norm_multiplier = sum_y_vals / sum_norm_y_vals
        adjusted_norm_y_vals = [val * norm_multiplier for val in norm_y_vals]
        indiv_chart_spec = HistoIndivChartSpec(
            lbl=self.chart_lbl,
            n_records=len(self.vals),
            norm_y_vals=adjusted_norm_y_vals,
            y_vals=self.bin_freqs,
        )
        return [indiv_chart_spec, ]

    def to_bin_lbls(self, *, dp: int = 3) -> list[str]:
        bin_lbls = self.bin_dets.to_bin_lbls(dp=dp)
        return bin_lbls

    def to_x_axis_range(self) -> tuple[float, float]:
        bin_dets, _bin_freqs = get_bin_details_from_vals(self.vals)
        x_axis_min_val = bin_dets.lower_limit
        x_axis_max_val = bin_dets.upper_limit
        return x_axis_min_val, x_axis_max_val

@dataclass(frozen=False)
class HistoValsSpecs:
    chart_fld_lbl: str
    fld_lbl: str
    chart_vals_specs: Sequence[HistoValsSpec]

    def __post_init__(self):
        vals = []
        for chart_vals_spec in self.chart_vals_specs:
            vals.extend(chart_vals_spec.vals)
        self.vals = vals
        bin_dets, bin_freqs = get_bin_details_from_vals(vals)
        self.bin_dets = bin_dets

    def to_indiv_chart_specs(self) -> Sequence[HistoIndivChartSpec]:
        indiv_chart_specs = []
        for chart_vals_spec in self.chart_vals_specs:
            indiv_chart_specs.extend(chart_vals_spec.to_indiv_chart_specs())
        return indiv_chart_specs

    def to_bin_lbls(self, *, dp: int = 3) -> list[str]:
        bin_lbls = self.bin_dets.to_bin_lbls(dp=dp)
        return bin_lbls

    def to_x_axis_range(self) -> tuple[float, float]:
        bin_dets, _bin_freqs = get_bin_details_from_vals(self.vals)
        x_axis_min_val = bin_dets.lower_limit
        x_axis_max_val = bin_dets.upper_limit
        return x_axis_min_val, x_axis_max_val
