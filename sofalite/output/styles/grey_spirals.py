from sofalite.conf.style import ChartStyleSpec, ColourWithHighlight, DojoStyleSpec, StyleSpec, TableStyleSpec
from sofalite.conf.misc import SOFALITE_FS_RESOURCES_ROOT, SOFALITE_WEB_RESOURCES_ROOT

BLUE_GREY = '#4c547c'
VERY_PALE_TURQUOISE = '#e8f4ff'
TURQUOISE_BLUE = '#6ecadf'
ANOTHER_TURQUOISE = '#359cb3'
BLACK_BLUE = '#333435'
MID_GREY_BLUE = '#74787c'
GREY_BLUE = '#ccd9d7'
MURKY_BLUE_GREY = '#9db6b2'
DARK_MURKY_BLUE_GREY = '#094457'
FADED_DARK_MURKY_BLUE_GREY = '#5d8997'  ## _you_ try and come up with better names! LOL
MURKY_GREY_BLUE = '#56948a'
MURKY_GREY = '#637572'
BURNT_ORANGE = '#e95f29'
BLACK_BROWN = '#423126'
WHITE = '#ffffff'
BLACK = '#000000'
DARKER_MID_GREY = '#a1a1a1'
LIGHT_GREY = '#f5f5f5'
MID_GREY = '#c0c0c0'

def get_style_spec() -> StyleSpec:
    connector_style = 'paleblue'
    table_spec = TableStyleSpec(
        var_font_colour_first_level=WHITE,
        var_font_colour_not_first_level=BLACK_BLUE,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK,
        gui_msg_font_colour=BLACK_BROWN,  ## replacing #29221c;
        gui_note_font_colour=WHITE,
        ## background colours
        var_bg_colour_first_level=BLACK_BLUE,
        var_bg_colour_not_first_level=LIGHT_GREY,
        gui_note_bg_colour=BURNT_ORANGE,
        ## borders
        var_border_colour_first_level=DARKER_MID_GREY,
        var_border_colour_not_first_level=MID_GREY,
        ## spaceholders
        spaceholder_bg_colour=GREY_BLUE,
        spaceholder_bg_img=f"{SOFALITE_FS_RESOURCES_ROOT}/grey_spirals.gif",
    )
    chart_spec = ChartStyleSpec(
        chart_bg_colour=WHITE,
        chart_font_colour=BLUE_GREY,
        plot_bg_colour=VERY_PALE_TURQUOISE,
        plot_font_colour=BLUE_GREY,
        plot_bg_colour_filled=VERY_PALE_TURQUOISE,
        plot_font_colour_filled=BLUE_GREY,
        axis_font_colour=BLUE_GREY,
        major_grid_line_colour=TURQUOISE_BLUE,
        grid_line_width=1,
        stroke_width=3,
        tooltip_border_colour=TURQUOISE_BLUE,
        normal_curve_colour=BLUE_GREY,
        colour_mappings=[
            ColourWithHighlight(ANOTHER_TURQUOISE, TURQUOISE_BLUE),
            ColourWithHighlight(BLACK_BLUE, MID_GREY_BLUE),
            ColourWithHighlight(GREY_BLUE, MURKY_BLUE_GREY),
            ColourWithHighlight(DARK_MURKY_BLUE_GREY, FADED_DARK_MURKY_BLUE_GREY),
            ColourWithHighlight(MURKY_GREY_BLUE, MURKY_GREY),
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
        table=table_spec,
        chart=chart_spec,
        dojo=dojo_spec,
    )
    return style_spec
