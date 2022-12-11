from sofalite.conf.style import (
    ChartStyleDets, ColourWithHighlight, DojoStyleDets, StyleDets, TableStyleDets)
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT

BLACK_BLUE = '#333435'
BLACK_BROWN = '#423126'
LIGHT_GREY_BLUE = '#f2f1f0'
LIGHT_GREY = '#f5f5f5'
GREY_BLUE = '#ccd9d7'
MID_GREY_BROWN = '#b8a49e'
MID_GREY = '#c0c0c0'
DARKER_MID_GREY = '#a1a1a1'
CHARCOAL_BROWN = '#736354'
BURNT_ORANGE = '#e95f29'
ORANGE = '#ef7d44'
YORANGE = '#f4cb3a'
PALE_YORANGE = '#f7d858'
BLUE_TURQUOISE = '#4495c3'
TURQUOISE = '#62add2'
DARK_GREEN = '#44953a'
GREEN = '#62ad58'
OFF_SCARLET = '#f43a3a'
PALE_SCARLET = '#f75858'
WHITE = '#ffffff'
BLACK = '#000000'

def get_style_dets() -> StyleDets:
    connector_style = 'defbrown'
    table_dets = TableStyleDets(
        first_cell_font_colour=WHITE,
        var_font_colour=BLACK_BLUE,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK,
        gui_msg_font_colour=BLACK_BROWN,  ## replacing #29221c;
        gui_note_font_colour=BURNT_ORANGE,
        ## background colours
        first_cell_bg_colour=BLACK_BLUE,
        heading_lbl_bg_colour=LIGHT_GREY,
        gui_note_bg_colour=BURNT_ORANGE,
        ## borders
        main_border=MID_GREY,
        heading_cell_border=DARKER_MID_GREY,
        first_row_border=None,
        ## spaceholders
        spaceholder=GREY_BLUE,
        spaceholder_bg_img_or_none='none',
    )
    chart_dets = ChartStyleDets(
        chart_bg_colour=WHITE,
        chart_font_colour=BLACK_BROWN,
        plot_bg_colour=LIGHT_GREY_BLUE,
        plot_font_colour=BLACK_BROWN,
        plot_bg_colour_filled=LIGHT_GREY_BLUE,
        plot_font_colour_filled=BLACK_BROWN,
        axis_font_colour=BLACK_BROWN,
        major_grid_line_colour=MID_GREY_BROWN,
        grid_line_width=1,
        stroke_width=3,
        tooltip_border_colour=CHARCOAL_BROWN,
        normal_curve_colour=BLACK_BROWN,
        colour_mappings=[
            ColourWithHighlight(BURNT_ORANGE, ORANGE),
            ColourWithHighlight(YORANGE, PALE_YORANGE),
            ColourWithHighlight(BLUE_TURQUOISE, TURQUOISE),
            ColourWithHighlight(DARK_GREEN, GREEN),
            ColourWithHighlight(OFF_SCARLET, PALE_SCARLET),
        ],
    )
    dojo_dets = DojoStyleDets(
        connector_style=connector_style,
        tooltip_connector_up=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorUp-{connector_style}.png",
        tooltip_connector_down=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorDown-{connector_style}.png",
        tooltip_connector_left=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorLeft-{connector_style}.png",
        tooltip_connector_right=f"{SOFALITE_WEB_RESOURCES_ROOT}/tooltipConnectorRight-{connector_style}.png",
    )
    style_dets = StyleDets(
        table=table_dets,
        chart=chart_dets,
        dojo=dojo_dets,
    )
    return style_dets
