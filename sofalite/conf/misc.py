from dataclasses import dataclass
from enum import Enum
import platform
from typing import Sequence

SOFASTATS_REPORT_EXTRAS_ROOT = 'http://www.sofastatistics.com/sofastats_report_extras/'

class StrConst(str, Enum):

    def __str__(self):
        return self.value

    @property
    def str(self):
        """

        Sometimes you really need a true str so here is syntactic sugar

        (e.g. some Pandas operations seem to type check rather than duck type).

        """

        return str(self.value)

class Platform(StrConst):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())

@dataclass(frozen=True)
class NiceInitialBinDets:
    n_bins: int
    lower_limit: float
    upper_limit: float

@dataclass(frozen=True)
class HistogramDetails:
    bins_freqs: Sequence[int]
    lower_real_limit: float
    bin_width: float
    n_extra_points: int

@dataclass(frozen=True)
class BarChartDetails:
    title: str
    subtitle: str
    rotate: bool = False
    show_n: bool = False
    show_borders: bool = False

@dataclass(frozen=True)
class ColourWithHighlight:
    main: str
    highlight: str

@dataclass(frozen=False, kw_only=True)  ## unfrozen so post init possible
class TableStyleDets:
    ## font colours
    first_cell_font_colour: str
    var_font_colour: str
    heading_footnote_font_colour: str
    footnote_font_colour: str
    gui_msg_font_colour: str
    gui_note_font_colour: str
    ## background colours
    first_cell_bg_colour: str
    heading_lbl_bg_colour: str
    gui_note_bg_colour: str
    ## borders
    main_border: str
    heading_cell_border: str
    first_row_border: str | None = None
    ## spaceholders
    spaceholder: str
    spaceholder_bg_img_or_none: str

    def __post_init__(self):
        if self.first_row_border is None:
            self.first_row_border = self.var_font_colour

@dataclass(frozen=True)
class ChartStyleDets:
    chart_bg_colour: str
    chart_font_colour: str
    plot_bg: str
    plot_font_colour: str
    plot_bg_filled: str
    plot_font_colour_filled: str
    axis_font_colour: str
    major_grid_line_colour: str
    grid_line_width: int
    stroke_width: int
    tooltip_border_colour: str
    normal_curve_colour: str
    colour_mappings: Sequence[ColourWithHighlight]

@dataclass(frozen=True)
class DojoStyleDets:
    connector_style: str
    tooltip_connector_up: str
    tooltip_connector_down: str
    tooltip_connector_left: str
    tooltip_connector_right: str

@dataclass(frozen=True)
class StyleDets:
    table: TableStyleDets
    chart: ChartStyleDets
    dojo: DojoStyleDets
