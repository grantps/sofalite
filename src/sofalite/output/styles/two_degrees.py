from sofalite.conf.main import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.output.styles.interfaces import (
    ChartStyleSpec, ColourWithHighlight, DojoStyleSpec, StyleSpec, TableStyleSpec)

DARK_BLUE = '#4472c3'
DARK_BLUE_HIGHLIGHT = '#6c96e0'
ORANGE = '#eb7c30'
ORANGE_HIGHLIGHT = '#ebc613'
RED = '#ff0000'
RED_HIGHLIGHT = '#b81a1a'
LIGHT_BLUE = '#00b5f0'
LIGHT_BLUE_HIGHLIGHT = '#77bad0'
YELLOW = '#f7ae54'
YELLOW_HIGHLIGHT = '#f88e0a'
BLACK_BLUE = '#333435'
MID_GREY = '#c0c0c0'
BLUE_GREY = '#6798a8'
DARKER_GREY = '#919191'
WHITE = '#ffffff'
BLACK = '#000000'

def get_style_spec() -> StyleSpec:
    connector_style = 'greypurp'
    table_spec = TableStyleSpec(
        var_font_colour_first_level=WHITE,
        var_font_colour_not_first_level=BLACK_BLUE,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK_BLUE,
        gui_msg_font_colour=BLACK_BLUE,  ## replacing #29221c;
        gui_note_font_colour=BLACK_BLUE,
        ## background colours
        var_bg_colour_first_level=LIGHT_BLUE,
        var_bg_colour_not_first_level=MID_GREY,
        gui_note_bg_colour=MID_GREY,
        ## borders
        var_border_colour_first_level=BLUE_GREY,
        var_border_colour_not_first_level=DARKER_GREY,
        ## spaceholders
        spaceholder_bg_colour=LIGHT_BLUE,
        spaceholder_bg_img=None,
    )
    chart_spec = ChartStyleSpec(
        chart_bg_colour=WHITE,
        chart_font_colour=BLACK_BLUE,
        plot_bg_colour=WHITE,
        plot_font_colour=BLACK_BLUE,
        plot_bg_colour_filled=WHITE,
        plot_font_colour_filled=BLACK_BLUE,
        axis_font_colour=BLACK_BLUE,
        major_grid_line_colour=MID_GREY,
        grid_line_width=1,
        stroke_width=1,
        tooltip_border_colour=BLACK_BLUE,
        normal_curve_colour=BLACK_BLUE,
        colour_mappings=[
            ColourWithHighlight(DARK_BLUE, DARK_BLUE_HIGHLIGHT),
            ColourWithHighlight(ORANGE, ORANGE_HIGHLIGHT),
            ColourWithHighlight(RED, RED_HIGHLIGHT),
            ColourWithHighlight(LIGHT_BLUE, LIGHT_BLUE_HIGHLIGHT),
            ColourWithHighlight(YELLOW, YELLOW_HIGHLIGHT),
        ],
    )
    dojo_spec = DojoStyleSpec(
        connector_style=connector_style,
        tooltip_connector_up=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorUp-{connector_style}.png",
        tooltip_connector_down=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorDown-{connector_style}.png",
        tooltip_connector_left=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorLeft-{connector_style}.png",
        tooltip_connector_right=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorRight-{connector_style}.png",
    )
    style_spec = StyleSpec(
        name='two_degrees',
        table=table_spec,
        chart=chart_spec,
        dojo=dojo_spec,
    )
    return style_spec
