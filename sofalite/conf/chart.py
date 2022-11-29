"""
When we chart some data we might produce one individual chart or a series of charts
(for example, one chart per country).

Each chart might have one series of values or multiple series. A clustered bar chart,
for example, will have one series per group.

Sometimes we will have multiple charts and each chart will have multiple series
e.g. we have a chart per gender and within each chart a series per country.

Sometimes we will have a single chart with only one series of data.
"""
from dataclasses import dataclass
from typing import Any, Literal, Sequence

from sofalite.conf.style import ColourWithHighlight

AVG_LINE_HEIGHT_PIXELS = 12
AVG_CHAR_WIDTH_PIXELS = 6.5
DOJO_Y_TITLE_OFFSET_0 = 45
TEXT_WIDTH_WHEN_ROTATED = 4
MIN_CHART_WIDTH_PIXELS = 450
MAX_SAFE_X_LBL_LEN_PIXELS = 180

JS_BOOL = Literal['true', 'false']

@dataclass(frozen=True)
class XAxisDetails:
    val: Any
    lbl: str  ## e.g. Ubuntu Linux
    lbl_split_into_lines: str  ## e.g. "Ubuntu\nLinux" - ready for display in chart

@dataclass(frozen=True)
class SeriesDetails:
    """
    A single chart might have multiple series
    e.g. a clustered bar chart might have a series of blue bars for Italy
    and a series of red bars for Germany.

    Pie charts only ever have one series per chart.
    """
    legend_lbl: str | None  ## e.g. "Italy", or None if only one series
    x_axis_dets: Sequence[XAxisDetails]
    y_vals: Sequence[float]
    tool_tips: Sequence[str]  ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]

@dataclass(frozen=True)
class ChartDetails:
    """
    Details for an individual chart (possibly the only one or one of a set).
    If we are splitting by country, for example, we will have separate chart details for
    Italy, Germany, and Japan.
    """
    n_records: int  ## number of values underlying chart e.g. N=534 records
    lbl: str | None  ## e.g. "Gender: Male" if multi-chart or None if only one chart
    series_dets: Sequence[SeriesDetails]  ## one or multiple series

@dataclass(frozen=True, kw_only=True)
class OverallChartsDetails:  ## Chart(s)Details ;-)
    """
    Overall details - whether for an individual chart only or for a set of charts
    (perhaps one per country).

    Includes charts as diverse as box plots and pie charts. Don't just think bar charts.

    max_x_lbl_length: potentially used to set height of each chart.
    All charts share same x labels - we need to know max of the labels
    in case x labels are rotated and they thus affect the chart height.
    """
    ## titles / labels
    overall_title: str | None = None  ## e.g. Age Group vs Gender - used to label output items
    overall_subtitle: str | None = None
    overall_legend_lbl: str | None = None  ## e.g. "Age Group", or None if only one chart in chart set
    ## formatting clues
    max_x_lbl_length: int  ## may be needed to set chart height if labels are rotated
    max_y_lbl_length: int  ## used to set left axis shift of chart(s) - so there is room for the y labels
    max_lbl_lines: int  ## used to set axis lbl drop
    ## the chart / charts details
    charts_details: Sequence[ChartDetails]  ## might be a sequence of one chart or of multiple charts

@dataclass(frozen=True, kw_only=True)
class BarChartDetails:
    ## specific details for bar charts
    x_title: str
    y_title: str
    rotate_x_lbls: bool = False
    show_n: bool = False
    show_borders: bool = False  ## show border lines around coloured bars?
    x_font_size: int = 12
    dp: int
    ## generic chart details
    overall_details: OverallChartsDetails

@dataclass(frozen=True, kw_only=True)
class LineChartDetails:
    """
    C.f. bar lacks show_borders
    """
    ## specific details for bar charts
    x_title: str
    y_title: str
    rotate_x_lbls: bool = False
    show_n: bool = False
    x_font_size: int = 12
    width: float  ## inches
    height: float
    dp: int
    ## generic chart details
    overall_details: OverallChartsDetails

@dataclass(frozen=True)
class OverallBarChartDets:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    multi_chart: bool
    legend: str
    axis_font_colour: str
    axis_lbl_drop: int
    axis_lbl_rotate: int
    chart_bg_colour: str
    connector_style: str
    grid_line_width: int
    major_grid_line_colour: str
    left_margin_offset: int
    minor_ticks: JS_BOOL
    n_records: int
    plot_bg_colour: str
    plot_font_colour: str
    plot_font_colour_filled: str
    tooltip_border_colour: str
    x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
    x_font_size: float
    x_gap: int
    x_title: str
    y_max: int
    y_title_offset: int
    y_title: str
    colour_mappings: Sequence[ColourWithHighlight]
    stroke_width: int
    show_borders: bool
    dp: int
    width: float  ## pixels
    height: float
