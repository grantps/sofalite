from dataclasses import dataclass
from typing import Sequence

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
