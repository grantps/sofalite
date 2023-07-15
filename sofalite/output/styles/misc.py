"""
CSS needed for header:

General e.g. body - font, background colour etc (see get_generic_css())

Dojo for charts - want name-spaced CSS for every style in styles folder.
Non-CSS styling, e.g. colour for pie chart slices, already set in JS functions directly.

Tables - only want general table settings in CSS (e.g. spacing) - nothing style-specific.
All specifics should be either:

In main output tables via Pandas, non-CSS styling
OR
in simple stats data tables via inline CSS drawing on details directly accessing
and using style-specific values e.g. spaceholder background.

So ...

want to be able to get:

* general (i.e. not style-specific) CSS for table, Dojo, and page styling
* Dojo CSS for all available styles (whether or not used in specific chart in HTML output).
  Never need to check which chart items use which styles before finalising Dojo CSS.
  KISS - not especially inefficient.
* access to specific style settings for insertion via pandas styling and in-line styling (vs internal CSS)
  will be based on style dets data classes
"""
from enum import Enum
import importlib
from pathlib import Path
from typing import Sequence

import jinja2

from sofalite.conf.style import (
    DOJO_COLOURS, ChartStyleDets, ColourWithHighlight, DojoStyleDets, StyleDets, TableStyleDets)
from sofalite.utils.misc import todict

class CSS(Enum):
    """
    Only need to put CSS in variables rather than just some text to insert into HTML when used,
    in addition to CSS strings for insertion at top of HTML,
    in strings supplied to tables via Pandas df styling.
    The latter requires us being able to pull it apart and get specific CSS strings for specific parts of the table as
    inline CSS.
    """
    ROW_LEVEL_1_VAR = [
        "font-family: Ubuntu, Helvetica, Arial, sans-serif;",
        "font-weight: bold;",
        "font-size: 14px;"
    ]
    CORNER_SPACEHOLDER = ROW_LEVEL_1_VAR
    COL_LEVEL_1_VAR = ROW_LEVEL_1_VAR + [
        'padding: 9px 6px;',
        'vertical-align: top;',
    ]
    COL_VALUE = [
        'font-size: 12px;',
        'vertical-align: top;',
    ]
    MEASURE = COL_VALUE
    ROW_VALUE = [
        'margin: 0;',
    ]
    LEFT = [
        'text-align: left;',
    ]
    RIGHT = [
        'text-align: right;',
    ]
    DATA_TBL_TOTAL_ROW = [
        'font-weight: bold;',
        'border-top: solid 2px black;',
        'border-bottom: double 3px black;',
    ]
    DATA_TBL_DATA_CELL = [
        'text-align: right; margin: 0;',
    ]

def get_generic_css() -> str:
    """
    Get CSS with no style-specific aspects:
    table, Dojo, and page styling
    """
    generic_css = f"""\
    body {{
        font-size: 12px;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
    }}
    h1, h2 {{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
    }}
    h1 {{
        font-size: 18px;
    }}
    h2 {{
        font-size: 16px;
    }}
    .page-break-before {{
        page-break-before: always;
        border-bottom: none;
        width: auto;
        height: 18px;
    }}
    /* Note - tables are not just used for report tables but also in chart legends and more besides  */
    tr, td, th {{
        margin: 0;
    }}
    th {{
        margin: 0;
        padding: 0px 6px;
    }}
    td {{
        padding: 2px 6px;
        font-size: 13px;
    }}
    table {{
        border-collapse: collapse;
    }}
    .row-level-1-var {{
        {CSS.ROW_LEVEL_1_VAR}
    }}
    .col-level-1-var {{
        {CSS.COL_LEVEL_1_VAR}
    }}
    .row-value {{
        {CSS.ROW_VALUE}
    }}
    .col-value {{
        {CSS.COL_VALUE}
    }}
    .corner-spaceholder {{
        {CSS.CORNER_SPACEHOLDER}
    }}
    tr.data-tbl-data-cell td {{
        {CSS.DATA_TBL_DATA_CELL}
    }}
    tr.data-tbl-total-row td {{
        {CSS.DATA_TBL_TOTAL_ROW}
    }}
    .ftnote-line{{
        /* for hr http://www.w3schools.com/TAGS/att_hr_align.asp*/
        width: 300px;
        text-align: left; /* IE and Opera*/
        margin-left: 0; /* Firefox, Chrome, Safari */
    }}
    .left {{
        {CSS.LEFT}
    }}
    .right {{
        {CSS.RIGHT}
    }}
    """
    return generic_css

def get_style_dets(style: str) -> StyleDets:
    """
    Get dataclass with key colour details and so on e.g.
    style_dets.table_dets.heading_cell_border (DARKER_MID_GREY)
    style_dets.table_dets.first_row_border (None)
    """
    style_module = importlib.import_module(f"sofalite.output.styles.{style}")
    return style_module.get_style_dets()

def get_styled_dojo_css(style_dets: DojoStyleDets) -> str:
    tpl = """\
        /* Tool tip connector arrows */
        .dijitTooltipBelow-{{connector_style}} {
          padding-top: 13px;
        }
        .dijitTooltipAbove-{{connector_style}} {
          padding-bottom: 13px;
        }
        .tundra .dijitTooltipBelow-{{connector_style}} .dijitTooltipConnector {
          top: 0px;
          left: 3px;
          background: url("{{tooltip_connector_up}}") no-repeat top left !important;
          width: 16px;
          height: 14px;
        }
        .tundra .dijitTooltipAbove-{{connector_style}} .dijitTooltipConnector {
          bottom: 0px;
          left: 3px;
          background: url("{{tooltip_connector_down}}") no-repeat top left !important;
          width: 16px;
          height: 14px;
        }
        .tundra .dijitTooltipLeft-{{connector_style}} {
          padding-right: 14px;
        }
        .tundra .dijitTooltipLeft-{{connector_style}} .dijitTooltipConnector {
          right: 0px;
          bottom: 3px;
          background: url("{{tooltip_connector_right}}") no-repeat top left !important;
          width: 16px;
          height: 14px;
        }
        .tundra .dijitTooltipRight-{{connector_style}} {
          padding-left: 14px;
        }
        .tundra .dijitTooltipRight-{{connector_style}} .dijitTooltipConnector {
          left: 0px;
          bottom: 3px;
          background: url("{{tooltip_connector_left}}") no-repeat top left !important;
          width: 16px;
          height: 14px;
        }
    """
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    context = todict(style_dets, shallow=True)
    css = template.render(context)
    return css

def get_style_names() -> list[str]:
    """
    Just names, not paths.
    Names can be handed to get_style_dets(style_name)
    """
    from sofalite.output.styles import default  ## assumes default is always there
    style_root = Path(default.__file__).parent
    style_names = [fpath.name for fpath in style_root.iterdir() if fpath.suffix == '.py']
    return style_names

def get_all_dojo_css_styles() -> str:
    """
    Grab everything in case it is needed - OK if it isn't - KISS.
    """
    style_names = get_style_names()
    css_all = []
    for style_name in style_names:
        style_dets = get_style_dets(style_name)
        css_style = get_styled_dojo_css(style_dets)
        css_all.append(css_style)
    css = '\n\n'.join(css_all)
    return css

def get_all_style_dets() -> dict[str, StyleDets]:
    style_names = get_style_names()
    all_style_dets = {}
    for style_name in style_names:
        style_dets = get_style_dets(style_name)
        all_style_dets[style_name] = style_dets
    return all_style_dets

def get_styled_misc_css(chart_style_dets: ChartStyleDets, table_style_dets: TableStyleDets) -> str:
    """
    TODO: remove
    """
    tpl = """\
        .gui-msg-medium, gui-msg-small{
            color: {{gui_msg_font_colour}};
        }
        .gui-note{
            background-color: {{gui_note_bg_colour}};
            color: {{gui_note_font_colour}};
        }
        th, .rowvar, .rowval, .datacell, .firstdatacell {
            border: solid 1px {{heading_cell_border}};
        }
        td{
            border: solid 1px {{main_border}};
        }
        .subtable{
            border-top: solid 3px {{main_border}};
        }
        .firstcolvar, .firstrowvar, .spaceholder {
            color: {{first_cell_font_colour}};
        }
        .firstcolvar, .firstrowvar{
            background-color: {{first_cell_bg_colour}};
        }
        .firstrowvar{
            border-left: solid 1px {{first_row_border}};
            border-bottom:  solid 1px {{first_row_border}};
        }
        .topline{
            border-top: 2px solid {{main_border}};
        }
        .spaceholder {
            background-image: {{spaceholder_bg_img_or_none}} !important; /*else tundra forces none*/
            background-color: {{spaceholder}};
        }
        .rowvar, .colvar{
            color: {{var_font_colour}};
        }
        td.lbl{
            background-color: {{heading_lbl_bg_colour}};
        }
        .tbl-heading-footnote{
            color: {{heading_footnote_font_colour}};
        }
        .footnote{
            color: {{footnote_font_colour}};
        }
    """
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    context = todict(chart_style_dets, shallow=True)
    context.update(todict(table_style_dets, shallow=True))
    css = template.render(context)
    return css

def get_long_colour_list(colour_mappings: Sequence[ColourWithHighlight]) -> list[str]:
    defined_colours = [colour_mapping.main for colour_mapping in colour_mappings]
    long_colour_list = defined_colours + DOJO_COLOURS
    return long_colour_list

