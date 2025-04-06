
from dataclasses import dataclass
from typing import Sequence

DOJO_COLOURS = ['indigo', 'gold', 'hotpink', 'firebrick', 'indianred',
    'mistyrose', 'darkolivegreen', 'darkseagreen', 'slategrey', 'tomato',
    'lightcoral', 'orangered', 'navajowhite', 'slategray', 'palegreen',
    'darkslategrey', 'greenyellow', 'burlywood', 'seashell',
    'mediumspringgreen', 'mediumorchid', 'papayawhip', 'blanchedalmond',
    'chartreuse', 'dimgray', 'lemonchiffon', 'peachpuff', 'springgreen',
    'aquamarine', 'orange', 'lightsalmon', 'darkslategray', 'brown', 'ivory',
    'dodgerblue', 'peru', 'lawngreen', 'chocolate', 'crimson', 'forestgreen',
    'darkgrey', 'lightseagreen', 'cyan', 'mintcream', 'transparent',
    'antiquewhite', 'skyblue', 'sienna', 'darkturquoise', 'goldenrod',
    'darkgreen', 'floralwhite', 'darkviolet', 'darkgray', 'moccasin',
    'saddlebrown', 'grey', 'darkslateblue', 'lightskyblue', 'lightpink',
    'mediumvioletred', 'deeppink', 'limegreen', 'darkmagenta', 'palegoldenrod',
    'plum', 'turquoise', 'lightgoldenrodyellow', 'darkgoldenrod', 'lavender',
    'slateblue', 'yellowgreen', 'sandybrown', 'thistle', 'violet', 'magenta',
    'dimgrey', 'tan', 'rosybrown', 'olivedrab', 'pink', 'lightblue',
    'ghostwhite', 'honeydew', 'cornflowerblue', 'linen', 'darkblue',
    'powderblue', 'seagreen', 'darkkhaki', 'snow', 'mediumblue', 'royalblue',
    'lightcyan', 'mediumpurple', 'midnightblue', 'cornsilk', 'paleturquoise',
    'bisque', 'darkcyan', 'khaki', 'wheat', 'darkorchid', 'deepskyblue',
    'salmon', 'darkred', 'steelblue', 'palevioletred', 'lightslategray',
    'aliceblue', 'lightslategrey', 'lightgreen', 'orchid', 'gainsboro',
    'mediumseagreen', 'lightgray', 'mediumturquoise', 'cadetblue',
    'lightyellow', 'lavenderblush', 'coral', 'lightgrey', 'whitesmoke',
    'mediumslateblue', 'darkorange', 'mediumaquamarine', 'darksalmon', 'beige',
    'blueviolet', 'azure', 'lightsteelblue', 'oldlace']

@dataclass(frozen=True)
class ColourWithHighlight:
    main: str
    highlight: str

@dataclass(frozen=False, kw_only=True)  ## unfrozen so post init possible
class TableStyleSpec:
    ## font colours
    var_font_colour_first_level: str
    var_font_colour_not_first_level: str
    heading_footnote_font_colour: str
    footnote_font_colour: str
    gui_msg_font_colour: str  ## TODO: used?
    gui_note_font_colour: str
    ## background colours
    var_bg_colour_first_level: str
    var_bg_colour_not_first_level: str
    gui_note_bg_colour: str
    ## borders
    var_border_colour_first_level: str  ## usually dark enough for heading cell and spaceholder colours (if they're dark, this must be dark)
    var_border_colour_not_first_level: str  ## usually more pale so numbers stand out
    ## spaceholders
    spaceholder_bg_colour: str | None = None
    spaceholder_bg_img: str | None = None

@dataclass(frozen=True)
class ChartStyleSpec:
    chart_bg_colour: str
    chart_font_colour: str
    plot_bg_colour: str
    plot_font_colour: str
    plot_bg_colour_filled: str
    plot_font_colour_filled: str
    axis_font_colour: str
    major_grid_line_colour: str
    grid_line_width: int
    stroke_width: int
    tooltip_border_colour: str
    normal_curve_colour: str
    colour_mappings: Sequence[ColourWithHighlight]

@dataclass(frozen=True)
class DojoStyleSpec:
    connector_style: str
    tooltip_connector_up: str
    tooltip_connector_down: str
    tooltip_connector_left: str
    tooltip_connector_right: str

@dataclass(frozen=True)
class StyleSpec:
    name: str
    table: TableStyleSpec
    chart: ChartStyleSpec
    dojo: DojoStyleSpec
