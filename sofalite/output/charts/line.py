import jinja2

from sofalite.conf.chart import LineChartDetails
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import StyleDets
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.styles.misc import common_css, get_styled_dojo_css, get_styled_misc_css

tpl_chart = """
<script type="text/javascript">

    make_line_chart_{{chart_uuid}} = function(){

        var series = new Array();
        {% for series_dets in dojo_series_dets %}
          var series_{{series_dets.series_id}} = new Array();
              series_{{series_dets.series_id}}["seriesLabel"] = "{{series_dets.series_lbl}}";
              series_{{series_dets.series_id}}["yVals"] = {{series_dets.y_vals}};
              series_{{series_dets.series_id}}["options"] = {{series_dets.options}};
          series.push(series_{{series_dets.series_id}});
        {% endfor %}

        var conf = new Array();
            conf["axis_font_colour"] = "{{axis_font_colour}}";
            conf["axis_lbl_drop"] = {{axis_lbl_drop}};
            conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
            conf["chart_bg"] = "{{chart_bg_colour}}";
            conf["connector_style"] = "{{connector_style}}";
            conf["gridline_width"] = {{grid_line_width}};
            conf["major_gridline_colour"] = "{{major_grid_line_colour}}";
            conf["margin_offset_l"] = {{margin_offset_l}};
            conf["minor_ticks"] = {{minor_ticks}};
            conf["n_chart"] = {{n_records}};
            conf["plot_bg"] = "{{plot_bg_colour}}";
            conf["plot_font_colour"] = "{{plot_font_colour}}";
            conf["plot_font_colour_filled"] = "{{plot_font_colour_filled}}";
            conf["tooltip_border_colour"] = "{{tooltip_border_colour}}";
            conf["xaxis_lbls"] = {{x_axis_lbls}};
            conf["xfontsize"] = {{x_font_size}};
            conf["x_title"] = "{{x_title}}";
            conf["ymax"] = {{y_max}};
            conf["y_title"] = "{{y_title}}";
            conf["y_title_offset"] = {{y_title_offset}};

            conf["time_series"] = {{time_series}};
            conf["micro_ticks"] = {{micro_ticks}};

        makeLineChart("line_chart_{{chart_uuid}}", series, conf);
    }
"""

def get_html(chart_dets: LineChartDetails, style_dets: StyleDets) -> str:
    styled_dojo_css = get_styled_dojo_css(style_dets.dojo)
    styled_misc_css = get_styled_misc_css(style_dets.chart, style_dets.table)
    context = {
        'sofalite_web_resources_root': SOFALITE_WEB_RESOURCES_ROOT,
        'common_css': common_css,
        'styled_dojo_css': styled_dojo_css,
        'styled_misc_css': styled_misc_css,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl_html_top)
    html_top = template.render(context)
    html_result = [html_top, ]
    overall_chart_dets = get_overall_chart_dets(chart_dets, style_dets)
    for n, chart_dets in enumerate(chart_dets.overall_details.charts_details, 1):
        chart_html = get_indiv_chart_html(overall_chart_dets, chart_dets, chart_counter=n)
        html_result.append(chart_html)
    html_result.append(html_bottom)
    return '\n\n'.join(html_result)
