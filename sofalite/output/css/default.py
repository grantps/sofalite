from sofalite.conf.misc import StyleDets

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

def get_style_dets(rel_img_root: str) -> StyleDets:
    style_dets = StyleDets(
        first_cell_font_colour=WHITE,
        heading_cell_border_grey=DARKER_MID_GREY,
        data_cell_border_grey=MID_GREY,
        tbl_heading_lbl_bg_colour=LIGHT_GREY,
        tbl_var_font_colour=BLACK_BLUE,
        tbl_var_bg_colour=WHITE,
        tbl_row_borders_top_bottom=BLACK,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK,
        spaceholder=GREY_BLUE,
        spaceholder_bg_img_or_none='none',
        gui_msg_font_colour=BLACK_BROWN,  ## replacing #29221c;
        gui_note_bg_colour=BURNT_ORANGE,
        gui_note_font_colour=WHITE,
        chart_bg=WHITE,
        chart_font_colour=BLACK_BROWN,
        plot_bg=LIGHT_GREY_BLUE,
        plot_font_colour=BLACK_BROWN,
        plot_bg_filled=LIGHT_GREY_BLUE,
        plot_font_colour_filled=BLACK_BROWN,
        axis_font_colour=BLACK_BROWN,
        major_grid_line_colour=MID_GREY_BROWN,
        grid_line_width=1,
        stroke_width=1,
        tooltip_border_colour=CHARCOAL_BROWN,
        normal_curve_colour=BLACK_BROWN,
        colour_mappings=[
            (BURNT_ORANGE, ORANGE),
            (YORANGE, PALE_YORANGE),
            (BLUE_TURQUOISE, TURQUOISE),
            (DARK_GREEN, GREEN),
            (OFF_SCARLET, PALE_SCARLET),
        ],
        connector_style='defbrown',
        tooltip_connector_up=f"{rel_img_root}/tooltipConnectorUp-defbrown.png",
        tooltip_connector_down=f"{rel_img_root}/tooltipConnectorUDown-defbrown.png",
        tooltip_connector_left=f"{rel_img_root}/tooltipConnectorLeft-defbrown.png",
        tooltip_connector_right=f"{rel_img_root}/tooltipConnectorRight-defbrown.png",
    )
    return style_dets
