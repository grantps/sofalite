from dataclasses import dataclass
from typing import Literal, Sequence

from sofalite.conf.misc import StrConst

AVG_LINE_HEIGHT_PIXELS = 12
AVG_CHAR_WIDTH_PIXELS = 6.5
HISTO_AVG_CHAR_WIDTH_PIXELS = 10.5
DOJO_Y_AXIS_TITLE_OFFSET = 45
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

@dataclass(frozen=True)
class ScatterplotDojoSeriesSpec:
    series_id: str  ## e.g. 01
    lbl: str
    xy_pairs: Sequence[tuple[float, float]]
    options: str

@dataclass(frozen=True)
class DojoBoxSpec:
    """
    Has huge overlap with other_specs.BoxplotDataItem
    """
    center: float
    indiv_box_lbl: str
    lower_box_val: float
    lower_box_val_rounded: float
    lower_whisker_val: float
    lower_whisker_val_rounded: float
    median_val: float
    median_val_rounded: float
    outliers: Sequence[float] | None
    outliers_rounded: Sequence[float] | None
    upper_box_val: float
    upper_box_val_rounded: float
    upper_whisker_val: float
    upper_whisker_val_rounded: float

@dataclass(frozen=True)
class BoxplotDojoSeriesSpec:
    box_specs: Sequence[DojoBoxSpec]
    lbl: str
    series_id: str  ## e.g. 01
    stroke_colour: str
