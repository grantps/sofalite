import jinja2

from sofalite.conf.misc import StyleDets
from sofalite.utils.misc import todict

def get_css_from_style_dets(style_dets: StyleDets) -> str:
    css_tpl = """\
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
            color: {{gui_msg_font_colour}};
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
            background-color: {{gui_note_bg_colour}};
            color: {{gui_note_font_colour}};
            font-weight: bold;
            padding: 2px;
        }
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

        th, .rowvar, .rowval, .datacell, .firstdatacell {
            border: solid 1px {{heading_cell_border_grey}};
        }
        th{
            margin: 0;
            padding: 0px 6px;
        }
        td{
            padding: 2px 6px;
            border: solid 1px {{data_cell_border_grey}};
            font-size: 13px;
        }
        .subtable{
            border-top: solid 3px {{data_cell_border_grey}};
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
            color: {{first_cell_font_colour}};
        }
        .firstcolvar, .firstrowvar{
            background-color: {{tbl_var_font_colour}};
        }
        .firstrowvar{
            border-left: solid 1px {{tbl_var_font_colour}};
            border-bottom:  solid 1px {{tbl_var_font_colour}};
        }
        .topline{
            border-top: 2px solid {{data_cell_border_grey}};
        }
        .spaceholder {
            background-image: {{spaceholder_bg_img_or_none}} !important; /*else tundra forces none*/
            background-color: {{spaceholder}};
        }
        .firstcolvar{
            padding: 9px 6px;
            vertical-align: top;
        }
        .rowvar, .colvar{
            font-family: Ubuntu, Helvetica, Arial, sans-serif;
            font-weight: bold;
            font-size: 14px;
            color: {{tbl_var_font_colour}};
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
        .page-break-before{
            page-break-before: always;
            border-bottom: none;
            width: auto;
            height: 18px;
        }
        td.lbl{
            text-align: left;
            background-color: {{tbl_heading_lbl_bg_colour}};
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
        .tbl-heading-footnote{
            color: {{heading_footnote_font_colour}};
        }
        .footnote{
            color: {{footnote_font_colour}};
        }
        /* Tool tip connector arrows */
        .dijitTooltipBelow-defbrown {
          padding-top: 13px;
        }
        .dijitTooltipAbove-defbrown {
          padding-bottom: 13px;
        }
        .tundra .dijitTooltipBelow-defbrown .dijitTooltipConnector {
          top: 0px;
          left: 3px;
          background: url("{{tooltip_connector_up}}") no-repeat top left !important;
          width:16px;
          height:14px;
        }
        .dj_ie .tundra .dijitTooltipBelow-defbrown .dijitTooltipConnector {
          background-image: url("{{tooltip_connector_up}}") !important;
        }
        .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {
          bottom: 0px;
          left: 3px;
          background:url("{{tooltip_connector_down}}") no-repeat top left !important;
          width:16px;
          height:14px;
        }
        .dj_ie .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {
          background-image: url("{{tooltip_connector_down}}") !important;
        }
        .dj_ie6 .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {
          bottom: -3px;
        }
        .tundra .dijitTooltipLeft-defbrown {
          padding-right: 14px;
        }
        .dj_ie6 .tundra .dijitTooltipLeft-defbrown {
          padding-left: 15px;
        }
        .tundra .dijitTooltipLeft-defbrown .dijitTooltipConnector {
          right: 0px;
          bottom: 3px;
          background:url("{{tooltip_connector_right}}") no-repeat top left !important;
          width:16px;
          height:14px;
        }
        .dj_ie .tundra .dijitTooltipLeft-defbrown .dijitTooltipConnector {
          background-image: url("{{tooltip_connector_right}}") !important;
        }
        .tundra .dijitTooltipRight-defbrown {
          padding-left: 14px;
        }
        .tundra .dijitTooltipRight-defbrown .dijitTooltipConnector {
          left: 0px;
          bottom: 3px;
          background:url("{{tooltip_connector_left}}") no-repeat top left !important;
          width:16px;
          height:14px;
        }
        .dj_ie .tundra .dijitTooltipRight-defbrown .dijitTooltipConnector {
          background-image: url("{{tooltip_connector_left}}") !important;
        }
    """
    environment = jinja2.Environment()
    template = environment.from_string(css_tpl)
    context = todict(style_dets, shallow=True)
    css = template.render(context)
    return css
