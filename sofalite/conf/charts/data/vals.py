from dataclasses import dataclass
from typing import Sequence

from sofalite.conf.charts.output.non_standard import HistoIndivChartSpec
from sofalite.stats_calc.engine import get_normal_ys
from sofalite.stats_calc.histogram import get_bin_details_from_vals

@dataclass(frozen=False)
class ValsSpec:
    lbl: str | None
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
            lbl=self.lbl,
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
class ChartValsSpecs:
    chart_fld_lbl: str
    chart_vals_specs: Sequence[ValsSpec]

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
