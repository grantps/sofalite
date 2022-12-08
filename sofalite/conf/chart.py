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

from sofalite.conf.misc import StrConst

AVG_LINE_HEIGHT_PIXELS = 12
AVG_CHAR_WIDTH_PIXELS = 6.5
DOJO_Y_TITLE_OFFSET_0 = 45
TEXT_WIDTH_WHEN_ROTATED = 4
MIN_CHART_WIDTH_PIXELS = 450
MAX_SAFE_X_LBL_LEN_PIXELS = 180

JS_BOOL = Literal['true', 'false']

class PlotStyle(StrConst):
    """
    Self-defined plot names added with addPlot in the sofalite chart js file.
     Each has different settings re: tension and markers.
    """
    UNMARKED = 'unmarked'
    DEFAULT = 'default'
    CURVED = 'curved'

@dataclass(frozen=True)
class ValSpec:
    val: Any
    lbl: str  ## e.g. Ubuntu Linux
    lbl_split_into_lines: str  ## e.g. "Ubuntu\nLinux" - ready for display in chart

@dataclass(frozen=True)
class XAxisSpec(ValSpec):
    ...

@dataclass(frozen=True)
class SliceSpec(ValSpec):
    ...

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

@dataclass(frozen=True, kw_only=True)
class SeriesDetails:
    """
    A single chart might have multiple series
    e.g. a clustered bar chart might have a series of blue bars for Italy
    and a series of red bars for Germany.

    Pie charts only ever have one series per chart.

    legend_lbl: Needed if multiple lines being displayed (and thus a legend displayed) e.g. "Italy".
    So needed if either multiple series or a single series with a smooth or trend line also displayed.
    """
    legend_lbl: str | None
    x_axis_specs: Sequence[XAxisSpec] | None = None
    slice_category_specs: Sequence[SliceSpec] | None = None
    y_vals: Sequence[float] | None = None
    slice_vals: Sequence[float] | None = None
    tool_tips: Sequence[str]  ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]

    def __post_init__(self):
        specs = [spec for spec in [self.x_axis_specs, self.slice_category_specs] if spec is not None]
        if len(specs) != 1:
            raise Exception("Must have either x_axis_specs or slice_category_specs")
        vals = [vals_list for vals_list in [self.y_vals, self.slice_vals] if vals_list is not None]
        if len(specs) != 1:
            raise Exception("Must have either y_vals or slice_vals")

@dataclass(frozen=True)
class ChartDetails:
    """
    Details for an individual chart (possibly the only one or one of a set).
    If we are splitting by country, for example, we will have separate chart details for
    Italy, Germany, and Japan.
    """
    n_records: int  ## number of values underlying chart e.g. N=534 records
    lbl: str | None  ## e.g. "Gender: Male" if multi-chart otherwise None
    series_dets: Sequence[SeriesDetails]  ## one or multiple series

@dataclass(frozen=True, kw_only=True)
class GenericChartingDetails:  ## Chart(s)Details ;-)
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
class GenericChartingDetailsPie:
    ## titles / labels
    overall_title: str | None = None  ## e.g. Age Group vs Gender - used to label output items
    overall_subtitle: str | None = None
    overall_legend_lbl: str | None = None  ## e.g. "Age Group", or None if only one chart in chart set
    ## the chart / charts details
    charts_details: Sequence[ChartDetails]  ## might be a sequence of one chart or of multiple charts
