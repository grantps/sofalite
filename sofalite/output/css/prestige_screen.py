from sofalite.conf.misc import (SOFASTATS_REPORT_EXTRAS_ROOT,
    ChartStyleDets, ColourWithHighlight, DojoStyleDets, StyleDets, TableStyleDets)

GREY_PURPLE = '#5a5a79'
RED_BROWN = '#ae0000'
BROWN_RED = '#630000'
MUSTARD_GREY = '#b89430'
GREY_MUSTARD = '#bca874'
SLIGHTLY_DARK_MUSTARD_GREY = '#8d6800'
DARK_MUSTARD_GREY = '#634900'
CHARCOAL_BLUE = '#081e35'
SLIGHTLY_MURKY_GREY = '#636567'
LIGHTER_RED_BROWN = '#b23131'
NEARLY_RED = '#e50000'
FAINT_MUSTARD = '#debc60'
VERY_FAINT_MUSTARD = '#e1cc92'
PALE_BLUE_GREY = '#a2a4a6'
PALE_DIRTY_RED = '#824a4a'
BROWN = '#831818'
MURKY_BLUER_GREY = '#afb2b6'
BLACK_BLUE = '#333435'
BLACK_BROWN = '#423126'
LIGHT_GREY = '#f5f5f5'
BURNT_ORANGE = '#e95f29'
MID_GREY = '#c0c0c0'
GREY_BLUE = '#ccd9d7'
WHITE = '#ffffff'
BLACK = '#000000'

def get_style_dets() -> StyleDets:
    table_dets = TableStyleDets(
        first_cell_font_colour=WHITE,
        var_font_colour=BLACK_BLUE,
        heading_footnote_font_colour=WHITE,
        footnote_font_colour=BLACK,
        gui_msg_font_colour=BLACK_BROWN,  ## replacing #29221c;
        gui_note_font_colour=WHITE,
        ## background colours
        first_cell_bg_colour=BLACK_BLUE,
        heading_lbl_bg_colour=LIGHT_GREY,
        gui_note_bg_colour=BURNT_ORANGE,
        ## borders
        main_border=MID_GREY,
        heading_cell_border=MURKY_BLUER_GREY,
        first_row_border=None,
        ## spaceholders
        spaceholder=GREY_BLUE,
        spaceholder_bg_img_or_none=f"{SOFASTATS_REPORT_EXTRAS_ROOT}/prestige_spirals.gif",
    )
    chart_dets = ChartStyleDets(
        chart_bg_colour=WHITE,
        chart_font_colour=BLACK_BLUE,
        plot_bg=BLACK_BLUE,
        plot_font_colour=WHITE,
        plot_bg_filled=BLACK_BLUE,
        plot_font_colour_filled=WHITE,
        axis_font_colour=BLACK_BLUE,
        major_grid_line_colour=WHITE,
        grid_line_width=1,
        stroke_width=3,
        tooltip_border_colour=GREY_PURPLE,
        normal_curve_colour=WHITE,
        colour_mappings=[
            ColourWithHighlight(RED_BROWN, BROWN_RED),
            ColourWithHighlight(MUSTARD_GREY, DARK_MUSTARD_GREY),
            ColourWithHighlight(CHARCOAL_BLUE, BLACK_BLUE),
            ColourWithHighlight(BROWN_RED, RED_BROWN),
            ColourWithHighlight(SLIGHTLY_DARK_MUSTARD_GREY, DARK_MUSTARD_GREY),
            ColourWithHighlight(SLIGHTLY_MURKY_GREY, CHARCOAL_BLUE),
            ColourWithHighlight(LIGHTER_RED_BROWN, BROWN_RED),
            ColourWithHighlight(DARK_MUSTARD_GREY, MUSTARD_GREY),
            ColourWithHighlight(CHARCOAL_BLUE, BLACK_BLUE),  ## a repeat
            ColourWithHighlight(NEARLY_RED, BROWN_RED),
            ColourWithHighlight(FAINT_MUSTARD, PALE_BLUE_GREY),
            ColourWithHighlight(PALE_DIRTY_RED, BROWN_RED),
            ColourWithHighlight(VERY_FAINT_MUSTARD, DARK_MUSTARD_GREY),
            ColourWithHighlight(BLACK, CHARCOAL_BLUE),
            ColourWithHighlight(BROWN, BROWN_RED),
            ColourWithHighlight(GREY_MUSTARD, DARK_MUSTARD_GREY),
        ],
    )
    dojo_dets = DojoStyleDets(
        connector_style='paleblue',
        tooltip_connector_up=f"{SOFASTATS_REPORT_EXTRAS_ROOT}tooltipConnectorUp-paleblue.png",
        tooltip_connector_down=f"{SOFASTATS_REPORT_EXTRAS_ROOT}tooltipConnectorUDown-paleblue.png",
        tooltip_connector_left=f"{SOFASTATS_REPORT_EXTRAS_ROOT}tooltipConnectorLeft-paleblue.png",
        tooltip_connector_right=f"{SOFASTATS_REPORT_EXTRAS_ROOT}tooltipConnectorRight-paleblue.png",
    )
    style_dets = StyleDets(
        table=table_dets,
        chart=chart_dets,
        dojo=dojo_dets,
    )
    return style_dets
