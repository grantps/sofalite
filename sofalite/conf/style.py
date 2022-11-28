
from dataclasses import dataclass
from typing import Sequence

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
    gui_msg_font_colour: str  ## TODO: used?
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
    plot_bg_colour: str
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
