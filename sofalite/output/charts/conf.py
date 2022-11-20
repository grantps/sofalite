from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Coord:
    x: float
    y: float

@dataclass(frozen=True)
class ScatterplotSeries:
    label: str
    coords: Sequence[Coord]
    dot_colour: str
    dot_line_colour: str | None = None
    show_regression_dets: bool = False

@dataclass(frozen=True, kw_only=True)
class ScatterplotConf:
    width_inches: float
    height_inches: float
    show_dot_lines: bool = False
    xmin: float | None = None  ## if not set pylab will autoset chart bounds
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None

@dataclass(frozen=True, kw_only=True)
class HistogramConf:
    var_lbl: str
    chart_lbl: str | None
    inner_bg_colour: str
    bar_colour: str
    line_colour: str

@dataclass(frozen=True)
class HistogramData:
    vals: Sequence[float]
