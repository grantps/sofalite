from dataclasses import dataclass
from typing import Sequence

from sofalite.conf.charts.output.non_standard import ScatterDataSeriesSpec, ScatterIndivChartSpec

@dataclass(frozen=True)
class XYSpecs:
    x_fld_lbl: str
    y_fld_lbl: str
    xys: Sequence[tuple[float, float]]

    def to_indiv_chart_specs(self) -> Sequence[ScatterIndivChartSpec]:
        data_series_spec = ScatterDataSeriesSpec(
            lbl=None,
            xy_pairs=self.xys,
        )
        indiv_chart_spec = ScatterIndivChartSpec(
            data_series_specs=[data_series_spec],
            lbl=None,
        )
        indiv_chart_specs = [indiv_chart_spec, ]
        return indiv_chart_specs

@dataclass(frozen=True)
class SeriesXYSpec:
    lbl: str
    xys: Sequence[tuple[float, float]]

@dataclass(frozen=True)
class SeriesXYSpecs:
    series_fld_lbl: str
    x_fld_lbl: str
    y_fld_lbl: str
    series_xy_specs: Sequence[SeriesXYSpec]

    def to_indiv_chart_specs(self) -> Sequence[ScatterIndivChartSpec]:
        data_series_specs = []
        for series_xy_spec in self.series_xy_specs:
            data_series_spec = ScatterDataSeriesSpec(
                lbl=series_xy_spec.lbl,
                xy_pairs=series_xy_spec.xys,
            )
            data_series_specs.append(data_series_spec)
        indiv_chart_spec = ScatterIndivChartSpec(
            data_series_specs=data_series_specs,
            lbl=None,
        )
        indiv_chart_specs = [indiv_chart_spec, ]
        return indiv_chart_specs\

@dataclass(frozen=True)
class ChartXYSpec:
    lbl: str
    xys: Sequence[tuple[float, float]]

@dataclass(frozen=True)
class ChartXYSpecs:
    x_fld_lbl: str
    y_fld_lbl: str
    charts_xy_specs: Sequence[ChartXYSpec]

    def to_indiv_chart_specs(self) -> Sequence[ScatterIndivChartSpec]:
        indiv_chart_specs = []
        for charts_xy_spec in self.charts_xy_specs:
            data_series_spec = ScatterDataSeriesSpec(
                lbl=None,
                xy_pairs=charts_xy_spec.xys,
            )
            indiv_chart_spec = ScatterIndivChartSpec(
                data_series_specs=[data_series_spec, ],
                lbl=charts_xy_spec.lbl,
            )
            indiv_chart_specs.append(indiv_chart_spec)
        return indiv_chart_specs

@dataclass(frozen=True)
class ChartSeriesXYSpec:
    lbl: str
    series_xy_specs: Sequence[SeriesXYSpec]

@dataclass(frozen=True)
class ChartSeriesXYSpecs:
    series_fld_lbl: str
    x_fld_lbl: str
    y_fld_lbl: str
    chart_series_xy_specs: Sequence[ChartSeriesXYSpec]

    def to_indiv_chart_specs(self) -> Sequence[ScatterIndivChartSpec]:
        indiv_chart_specs = []
        for chart_series_xy_spec in self.chart_series_xy_specs:
            data_series_specs = []
            for series_xy_spec in chart_series_xy_spec.series_xy_specs:
                data_series_spec = ScatterDataSeriesSpec(
                    lbl=series_xy_spec.lbl,
                    xy_pairs=series_xy_spec.xys,
                )
                data_series_specs.append(data_series_spec)
            indiv_chart_spec = ScatterIndivChartSpec(
                data_series_specs=data_series_specs,
                lbl=chart_series_xy_spec.lbl,
            )
            indiv_chart_specs.append(indiv_chart_spec)
        return indiv_chart_specs
