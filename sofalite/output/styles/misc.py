import importlib

import jinja2

from sofalite.conf.style import ChartStyleDets, DojoStyleDets, StyleDets, TableStyleDets
from sofalite.utils.misc import todict

def get_style_dets(style: str) -> StyleDets:
    style_module = importlib.import_module(f"sofalite.output.styles.{style}")
    return style_module.get_style_dets()

common_css = """\
    body{
        font-size: 12px;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
    }
    h1, h2{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
    }
    h1{
        font-size: 18px;
    }
    h2{
        font-size: 16px;
    }
    .gui-msg-medium, gui-msg-small{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
    }
    .gui-msg-medium{
        font-size: 16px;
    }
    *html .gui-msg-medium{
        font-weight: bold;
        font-size: 18px;
    }
    .gui-msg-small{
        font-size: 13px;
        line-height: 150%;
    }
    .gui-note{
        font-weight: bold;
        padding: 2px;
    }
    .page-break-before{
        page-break-before: always;
        border-bottom: none;
        width: auto;
        height: 18px;
    }
    /* Note - tables are not just used for report tables but also in chart legends and more besides  */
    tr, td, th{
        margin: 0;
    }
    .tbltitle, .tblsubtitle{
        margin: 0;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
    }
    .tbltitle{ /*spans*/
        padding: 0;
        font-size: 18px;
    }
    .tblsubtitle{
        padding: 12px 0px 0px 0px;
        font-size: 14px;
    }
    .tblcelltitle{ /*th*/
        text-align: left;
        border: none;
        padding: 0px 0px 12px 0px;
        margin: 0;
    }
    th{
        margin: 0;
        padding: 0px 6px;
    }
    td{
        padding: 2px 6px;
        font-size: 13px;
    }
    .rowval{
        margin: 0;
    }
    .datacell, .firstdatacell{
        text-align: right;
        margin: 0;
    }
    .firstcolvar, .firstrowvar, .spaceholder {
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
    }
    .firstcolvar{
        padding: 9px 6px;
        vertical-align: top;
    }
    .rowvar, .colvar{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
        background-color: white;
    }
    .colvar{
        padding: 6px 0px;
    }
    .colval, .measure{
        font-size: 12px;
        vertical-align: top;
    }
    table {
        border-collapse: collapse;
    }
    tr.total-row td{
        font-weight: bold;
        border-top: solid 2px black;
        border-bottom: double 3px black;
    }
    td.lbl{
        text-align: left;
    }
    td.right{
        text-align: right;
    }
    .ftnote-line{
        /* for hr http://www.w3schools.com/TAGS/att_hr_align.asp*/
        width: 300px;
        text-align: left; /* IE and Opera*/
        margin-left: 0; /* Firefox, Chrome, Safari */
    }
"""

def get_styled_misc_css(chart_style_dets: ChartStyleDets, table_style_dets: TableStyleDets) -> str:
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
