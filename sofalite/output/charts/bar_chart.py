import uuid

import jinja2

from sofalite.conf.misc import BarChartDetails, StyleDets

def get_html(chart_dets: BarChartDetails, style_dets: StyleDets) -> str:
    chart_uuid = uuid.uuid4()
    tpl = """
    <script type="text/javascript">

    var highlight-{{chart_uuid}} = function(colour){
        var hlColour;
        switch (colour.toHex()){
            {% for colour_case in colour_cases %}
              {{colour_case}}
            {% endfor %}
            default:
                hlColour = hl(colour.toHex());
                break;
        }}
        return new dojox.color.Color(hlColour);
    }}

    make-bar-chart-{{chart_uuid}} = function(){
        var series0 = new Array();
        var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font_colour}}";
        conf["axis_lbl_drop"] = {{axis_lbl_drop}};
        conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
        conf["chart_bg"] = "{{chart_bg}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["gridline_width"] = {{gridline_width}};
        conf["highlight"] = highlight-{{chart_uuid}};
        conf["major_gridline_colour"] = "{{major_gridline_colour}}";
        conf["margin_offset_l"] = {{margin_offset_l}};
        conf["minor_ticks"] = {{minor_ticks}};
        conf["n_chart"] = "{{n_chart}}";
        conf["plot_bg"] = "{{plot_bg}}";
        conf["plot_font_colour"] = "{{plot_font_colour}}";
        conf["plot_font_colour_filled"] = "{{plot_font_colour_filled}}";
        conf["tooltip_border_colour"] = "{{tooltip_border_colour}}";
        conf["xaxis_lbls"] = {{xaxis_lbls}};
        conf["xfontsize"] = {{xfontsize}};
        conf["xgap"] = {{xgap}};
        conf["x_title"] = "{{x_title}}";
        conf["ymax"] = {{ymax}};
        conf["y_title_offset"] = {{y_title_offset}};
        conf["y_title"] = "{{y_title}}";
        makeBarChart("bar-chart-{{chart_uuid}}", series, conf);
    }
    </script>

    <div class="screen-float-only" style="margin-right: 10px; {{pagebreak}}">
    {{indiv_title_html}}
        <div id="bar-chart-{{chart_uuid}}"
            style="width: {{width}}px; height: {{height}}px;">
        </div>
    {{legend}}
    </div>
    """
    colour_cases = [f'case "{main_colour}": hlColour = "{highlight_colour}";'
        for main_colour, highlight_colour in style_dets.colour_mappings]
    axis_lbl_drop = get_axis_lbl_drop(multichart, rotate, max_lbl_lines)
    context = {
        'chart_uuid': chart_uuid,
        'colour_cases': colour_cases,
        'axis_font_colour': style_dets.axis_font_colour,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html
