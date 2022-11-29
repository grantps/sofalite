from dataclasses import dataclass
from typing import Sequence
import uuid

import jinja2

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, MIN_CHART_WIDTH_PIXELS, TEXT_WIDTH_WHEN_ROTATED,
    BarChartDetails, ChartDetails, OverallBarChartDets)
from sofalite.conf.misc import SOFALITE_WEB_RESOURCES_ROOT
from sofalite.conf.style import ColourWithHighlight, StyleDets
from sofalite.output.charts.utils import (get_axis_lbl_drop, get_left_margin_offset, get_height,
    get_x_axis_lbl_dets, get_x_font_size, get_y_max, get_y_title_offset)
from sofalite.output.charts.html import html_bottom, tpl_html_top
from sofalite.output.styles.misc import common_css, get_styled_dojo_css, get_styled_misc_css
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

MIN_PIXELS_PER_BAR = 30
MIN_CLUSTER_WIDTH_PIXELS = 60
PADDING_PIXELS = 35
DOJO_MINOR_TICKS_NEEDED_FROM_N = 10  ## whatever works. Tested on cluster of Age vs Cars

@dataclass(frozen=True)
class DojoSeriesDetails:
    series_id: str  ## e.g. 01
    series_lbl: str
    y_vals: Sequence[float]
    options: str

tpl_chart = """
<script type="text/javascript">

var highlight_{{chart_uuid}} = function(colour){
    var hlColour;
    switch (colour.toHex()){
        {% for colour_case in colour_cases %}\n            {{colour_case}}; break;{% endfor %}
        default:
            hlColour = hl(colour.toHex());
            break;
    }
    return new dojox.color.Color(hlColour);
}

make_bar_chart_{{chart_uuid}} = function(){

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
        conf["margin_offset_l"] = {{left_margin_offset}};
        conf["minor_ticks"] = {{minor_ticks}};
        conf["n_chart"] = "{{n_records}}";
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

        conf["xgap"] = {{x_gap}};
        conf["highlight"] = highlight_{{chart_uuid}};

    makeBarChart("bar_chart_{{chart_uuid}}", series, conf);
}
</script>

<div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
{{indiv_title_html}}
    <div id="bar_chart_{{chart_uuid}}"
        style="width: {{width}}px; height: {{height}}px;">
    </div>
    {% if legend %}
        <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
            {{legend}}:
        </p>
        <div id="legend_for_bar_chart_{{chart_uuid}}">
        </div>
    {% endif %}
</div>
"""

def get_x_gap(*, n_clusters: int, multi_chart: bool) -> int:
    if n_clusters <= 2:
        x_gap = 20
    elif n_clusters <= 5:
        x_gap = 10
    elif n_clusters <= 8:
        x_gap = 8
    elif n_clusters <= 10:
        x_gap = 6
    elif n_clusters <= 16:
        x_gap = 5
    else:
        x_gap = 4
    x_gap = x_gap * 0.8 if multi_chart else x_gap
    return x_gap

def get_width_after_left_margin(*, multi_chart: bool, n_clusters: int, n_bars_in_cluster: int,
        max_x_lbl_width: int, x_title: str) -> float:
    """
    Get initial width (will make a final adjustment based on left margin offset).
    If wide labels, may not display almost any if one is too wide.
    Widen to take account.
    """
    min_width_per_cluster_pixels = (n_bars_in_cluster * MIN_PIXELS_PER_BAR)
    max_x_lbl_width_pixels = max_x_lbl_width * AVG_CHAR_WIDTH_PIXELS
    widest_pixels = max(
        [min_width_per_cluster_pixels, MIN_CLUSTER_WIDTH_PIXELS, max_x_lbl_width_pixels]
    )
    width_per_cluster_pixels = widest_pixels + PADDING_PIXELS
    width_x_title_pixels = len(x_title) * AVG_CHAR_WIDTH_PIXELS + PADDING_PIXELS
    width_cluster_pixels = n_clusters * width_per_cluster_pixels
    width = max([width_cluster_pixels, width_x_title_pixels, MIN_CHART_WIDTH_PIXELS])
    width = width * 0.9 if multi_chart else width
    return width

def get_overall_chart_dets(
        chart_dets: BarChartDetails, style_dets: StyleDets) -> OverallBarChartDets:
    """
    Get details that apply to all charts in bar chart set
    (often just one bar chart in set)

    Lots of interactive tweaking required to get charts to actually come out
    well under lots of interactive conditions (different numbers of columns etc).

    Re: minor_ticks -- generally we don't want them
    as they result in lots of ticks between the groups in clustered bar charts
    each with a distracting and meaningless value
    e.g. if we have two groups 1 and 2 we don't want a tick for 0.8 and 0.9 etc.
    But if we don't have minor ticks when we have a massive number of clusters
    we get no ticks at all.
    Probably a dojo bug I can't fix, so I have to work around it.
    """
    ## convenience pre-calcs
    rotated_x_lbls = chart_dets.rotate_x_lbls
    multi_chart = (len(chart_dets.overall_details.charts_details) > 1)
    first_chart_dets = chart_dets.overall_details.charts_details[0]
    single_series = len(first_chart_dets.series_dets) == 1
    first_series = first_chart_dets.series_dets[0]
    first_x_axis_dets = first_series.x_axis_dets[0]
    x_lbl_len = len(first_x_axis_dets.lbl)
    n_clusters = len(first_series.x_axis_dets)
    n_bars_in_cluster = len(first_chart_dets.series_dets)
    max_x_lbl_length = chart_dets.overall_details.max_x_lbl_length
    ## colour mappings
    colour_mappings = style_dets.chart.colour_mappings
    if single_series:
        colour_mappings = colour_mappings[:1]  ## only need the first
        ## This is an important special case because it affects the bar charts using the default style
        if colour_mappings[0].main == '#e95f29':  ## BURNT_ORANGE
            colour_mappings = [ColourWithHighlight('#e95f29', '#736354'), ]
    ## misc
    n_records = 'N = ' + format_num(first_chart_dets.n_records) if chart_dets.show_n else ''
    x_axis_lbl_dets = get_x_axis_lbl_dets(first_series.x_axis_dets)
    x_axis_lbls = '[' + ',\n            '.join(x_axis_lbl_dets) + ']'
    y_max = get_y_max(chart_dets.overall_details.charts_details)
    minor_ticks = 'true' if n_clusters >= DOJO_MINOR_TICKS_NEEDED_FROM_N else 'false'
    legend = chart_dets.overall_details.overall_legend_lbl
    stroke_width = style_dets.chart.stroke_width if chart_dets.show_borders else 0
    ## sizing
    max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if rotated_x_lbls else max_x_lbl_length)
    width_after_left_margin = get_width_after_left_margin(
        multi_chart=multi_chart, n_clusters=n_clusters, n_bars_in_cluster=n_bars_in_cluster,
        max_x_lbl_width=max_x_lbl_width, x_title=chart_dets.x_title)
    x_font_size = get_x_font_size(n_clusters=n_clusters, multi_chart=multi_chart)
    x_gap = get_x_gap(n_clusters=n_clusters, multi_chart=multi_chart)
    y_title_offset = get_y_title_offset(max_y_lbl_length=chart_dets.overall_details.max_y_lbl_length,
        x_lbl_len=x_lbl_len, rotated_x_lbls=rotated_x_lbls)
    axis_lbl_drop = get_axis_lbl_drop(multi_chart=multi_chart, rotated_x_lbls=rotated_x_lbls,
        max_lbl_lines=chart_dets.overall_details.max_lbl_lines)
    axis_lbl_rotate = -90 if rotated_x_lbls else 0
    left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
        y_title_offset=y_title_offset, rotated_x_lbls=rotated_x_lbls)
    width = width_after_left_margin + left_margin_offset
    height = get_height(axis_lbl_drop=axis_lbl_drop,
        rotated_x_lbls=rotated_x_lbls, max_x_lbl_length=max_x_lbl_length)
    return OverallBarChartDets(
        multi_chart=multi_chart,
        legend=legend,
        axis_font_colour=style_dets.chart.axis_font_colour,
        axis_lbl_drop=axis_lbl_drop,
        axis_lbl_rotate=axis_lbl_rotate,
        chart_bg_colour=style_dets.chart.chart_bg_colour,
        connector_style=style_dets.dojo.connector_style,
        grid_line_width=style_dets.chart.grid_line_width,
        major_grid_line_colour=style_dets.chart.major_grid_line_colour,
        left_margin_offset=left_margin_offset,
        minor_ticks=minor_ticks,
        n_records=n_records,
        plot_bg_colour=style_dets.chart.plot_bg_colour,
        plot_font_colour=style_dets.chart.plot_font_colour,
        plot_font_colour_filled=style_dets.chart.plot_font_colour_filled,
        tooltip_border_colour=style_dets.chart.tooltip_border_colour,
        x_axis_lbls=x_axis_lbls,  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
        x_font_size=x_font_size,
        x_gap=x_gap,
        x_title=chart_dets.x_title,
        y_max=y_max,
        y_title_offset=y_title_offset,
        y_title=chart_dets.y_title,
        colour_mappings=colour_mappings,
        stroke_width=stroke_width,
        show_borders=chart_dets.show_borders,
        dp=chart_dets.dp,
        width=width,
        height=height,
    )

def get_indiv_chart_html(overall_chart_dets: OverallBarChartDets, chart_dets: ChartDetails,
        *,  chart_counter: int) -> str:
    context = todict(overall_chart_dets, shallow=True)
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    colour_cases = [f'case "{colour_mapping.main}": hlColour = "{colour_mapping.highlight}"'
        for colour_mapping in overall_chart_dets.colour_mappings]  ## actually only need first one for simple bar charts
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = f"<p><b>{chart_dets.lbl}</b></p>" if overall_chart_dets.multi_chart else ''
    stroke_width_to_use = overall_chart_dets.stroke_width if overall_chart_dets.show_borders else 0
    dojo_series_dets = []
    multi_series = len(chart_dets.series_dets) > 1
    legend = overall_chart_dets.legend if multi_series else ''  ## only used for clustered bar charts
    for i, series in enumerate(chart_dets.series_dets):
        series_id = f"{i:>02}"
        series_lbl = series.legend_lbl
        y_vals = str(series.y_vals)
        ## options
        ## e.g. {stroke: {color: "white", width: "0px"}, fill: "#e95f29", yLbls: ['66.38', ...]}
        fill_colour = overall_chart_dets.colour_mappings[i].main
        y_lbls_str = str(series.tool_tips)
        options = (f"""{{stroke: {{color: "white", width: "{stroke_width_to_use}px"}}, """
            f"""fill: "{fill_colour}", yLbls: {y_lbls_str}}}""")
        dojo_series_dets.append(DojoSeriesDetails(series_id, series_lbl, y_vals, options))
    indiv_context = {
        'chart_uuid': chart_uuid,
        'colour_cases': colour_cases,
        'page_break': page_break,
        'indiv_title_html': indiv_title_html,
        'legend': legend,
        'dojo_series_dets': dojo_series_dets,
        'width': overall_chart_dets.width,
        'height': overall_chart_dets.height,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result

def get_html(chart_dets: BarChartDetails, style_dets: StyleDets) -> str:
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
