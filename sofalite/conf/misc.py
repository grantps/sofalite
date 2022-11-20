from dataclasses import dataclass
from enum import Enum
import platform
from typing import Sequence

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
class StyleDets:
    ## table
    first_cell_font_colour: str
    heading_cell_border_grey: str
    data_cell_border_grey: str
    tbl_heading_lbl_bg_colour: str
    tbl_var_font_colour: str
    tbl_var_bg_colour: str
    tbl_row_borders_top_bottom: str
    heading_footnote_font_colour: str
    footnote_font_colour: str
    spaceholder: str
    spaceholder_bg_img_or_none: str
    ## misc
    gui_msg_font_colour: str
    gui_note_bg_colour: str
    gui_note_font_colour: str
    ## charting
    chart_bg: str
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
    colour_mappings: Sequence[tuple[str, str]]
    connector_style: str
    tooltip_connector_up: str
    tooltip_connector_down: str
    tooltip_connector_left: str
    tooltip_connector_right: str
