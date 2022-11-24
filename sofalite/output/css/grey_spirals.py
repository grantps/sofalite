from sofalite.conf.misc import StyleDets

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

def get_style_dets(rel_img_root: str) -> StyleDets:
    style_dets = StyleDets(
        first_cell_font_colour=WHITE,
        heading_cell_border_grey=DARKER_MID_GREY,
        data_cell_border_grey=MID_GREY,
        tbl_heading_lbl_bg_colour=LIGHT_GREY,
        tbl_var_font_colour=BLACK_BLUE,
        tbl_row_borders_top_bottom=BLACK,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK,
        spaceholder=GREY_BLUE,
        spaceholder_bg_img_or_none='img/grey_spirals.gif',
        gui_msg_font_colour=BLACK_BROWN,  ## replacing #29221c;
        gui_note_bg_colour=BURNT_ORANGE,
        gui_note_font_colour=WHITE,
        chart_bg_colour=WHITE,
        chart_font_colour=BLUE_GREY,
        plot_bg=VERY_PALE_TURQUOISE,
        plot_font_colour=BLUE_GREY,
        plot_bg_filled=VERY_PALE_TURQUOISE,
        plot_font_colour_filled=BLUE_GREY,
        axis_font_colour=BLUE_GREY,
        major_grid_line_colour=TURQUOISE_BLUE,
        grid_line_width=1,
        stroke_width=3,
        tooltip_border_colour=TURQUOISE_BLUE,
        normal_curve_colour=BLUE_GREY,
        colour_mappings=[
            (ANOTHER_TURQUOISE, TURQUOISE_BLUE),
            (BLACK_BLUE, MID_GREY_BLUE),
            (GREY_BLUE, MURKY_BLUE_GREY),
            (DARK_MURKY_BLUE_GREY, FADED_DARK_MURKY_BLUE_GREY),
            (MURKY_GREY_BLUE, MURKY_GREY),
        ],
        connector_style='paleblue',
        tooltip_connector_up=f"{rel_img_root}/tooltipConnectorUp-paleblue.png",
        tooltip_connector_down=f"{rel_img_root}/tooltipConnectorUDown-paleblue.png",
        tooltip_connector_left=f"{rel_img_root}/tooltipConnectorLeft-paleblue.png",
        tooltip_connector_right=f"{rel_img_root}/tooltipConnectorRight-paleblue.png",
    )
    return style_dets
