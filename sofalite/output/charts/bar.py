from dataclasses import dataclass
from typing import Literal, Sequence
import uuid

import jinja2

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, MIN_CHART_WIDTH_PIXELS, TEXT_WIDTH_WHEN_ROTATED,
    BarChartingSpec, IndivChartSpec, DojoSeriesDetails, LeftMarginOffsetDetails
)
from sofalite.conf.style import ColourWithHighlight, StyleDets
from sofalite.output.charts.common import ChartingSpec as CommonChartingSpec
from sofalite.output.charts.utils import (get_axis_lbl_drop, get_left_margin_offset, get_height,
    get_x_axis_lbl_dets, get_x_font_size, get_y_title_offset)
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

MIN_PIXELS_PER_X_ITEM = 30
MIN_CLUSTER_WIDTH_PIXELS = 60
PADDING_PIXELS = 35
DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM = 10  ## whatever works. Tested on cluster of Age vs Cars

left_margin_offset_dets = LeftMarginOffsetDetails(
    initial_offset=25, wide_offset=35, rotate_offset=15, multi_chart_offset=15)

@dataclass(frozen=True)
class CommonColourSpec:
    axis_font: str
    chart_bg: str
    colour_cases: Sequence[str]
    colours: Sequence[str]
    major_grid_line: str
    plot_bg: str
    plot_font: str
    plot_font_filled: str
    tooltip_border: str

@dataclass(frozen=True)
class CommonOptions:
    has_minor_ticks_js_bool: Literal['true', 'false']
    is_multi_chart: bool
    show_borders: bool
    show_n_records: bool

@dataclass(frozen=True)
class CommonMiscSpec:
    axis_lbl_drop: int
    axis_lbl_rotate: int
    connector_style: str
    grid_line_width: int
    height: float  ## pixels
    left_margin_offset: int
    legend_lbl: str
    stroke_width: int
    width: float  ## pixels
    x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
    x_font_size: float
    x_gap: int
    x_axis_title: str
    y_max: int
    y_title: str
    y_title_offset: int

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: CommonMiscSpec
    options: CommonOptions

tpl_chart = """\
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

make_chart_{{chart_uuid}} = function(){

    var series = new Array();
    {% for series_dets in dojo_series_dets %}
      var series_{{series_dets.series_id}} = new Array();
          series_{{series_dets.series_id}}["lbl"] = "{{series_dets.lbl}}";
          series_{{series_dets.series_id}}["vals"] = {{series_dets.vals}};
          // options - stroke_width_to_use, fill_colour, y_lbls_str
          series_{{series_dets.series_id}}["options"] = {{series_dets.options}};
      series.push(series_{{series_dets.series_id}});
    {% endfor %}

    var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font}}";
        conf["axis_lbl_drop"] = {{axis_lbl_drop}};
        conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
        conf["chart_bg_colour"] = "{{chart_bg}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["grid_line_width"] = {{grid_line_width}};
        conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
        conf["left_margin_offset"] = {{left_margin_offset}};
        conf["major_grid_line_colour"] = "{{major_grid_line}}";
        conf["n_records"] = "{{n_records}}";
        conf["plot_bg_colour"] = "{{plot_bg}}";
        conf["plot_font_colour"] = "{{plot_font}}";
        conf["plot_font_colour_filled"] = "{{plot_font_filled}}";
        conf["tooltip_border_colour"] = "{{tooltip_border}}";
        conf["x_axis_lbls"] = {{x_axis_lbls}};
        conf["x_font_size"] = {{x_font_size}};
        conf["x_title"] = "{{x_axis_title}}";
        conf["y_max"] = {{y_max}};
        conf["y_title"] = "{{y_title}}";
        conf["y_title_offset"] = {{y_title_offset}};
        // distinct fields for bar charts
        conf["highlight"] = highlight_{{chart_uuid}};
        conf["x_gap"] = {{x_gap}};

    makeBarChart("bar_chart_{{chart_uuid}}", series, conf);
}
</script>

<div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
{{indiv_title_html}}
    <div id="bar_chart_{{chart_uuid}}"
        style="width: {{width}}px; height: {{height}}px;">
    </div>
    {% if legend_lbl %}
        <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
            {{legend_lbl}}:
        </p>
        <div id="legend_for_bar_chart_{{chart_uuid}}">
        </div>
    {% endif %}
</div>
"""

def get_x_gap(*, n_x_items: int, is_multi_chart: bool) -> int:
    if n_x_items <= 2:
        x_gap = 20
    elif n_x_items <= 5:
        x_gap = 10
    elif n_x_items <= 8:
        x_gap = 8
    elif n_x_items <= 10:
        x_gap = 6
    elif n_x_items <= 16:
        x_gap = 5
    else:
        x_gap = 4
    x_gap = x_gap * 0.8 if is_multi_chart else x_gap
    return x_gap

def get_width_after_left_margin(*, is_multi_chart: bool, n_x_items: int, n_series: int,
        max_x_lbl_width: int, x_axis_title: str) -> float:
    """
    Get initial width (will make a final adjustment based on left margin offset).
    If wide labels, may not display almost any if one is too wide.
    Widen to take account.
    """
    min_width_per_cluster_pixels = (n_x_items * MIN_PIXELS_PER_X_ITEM)
    max_x_lbl_width_pixels = max_x_lbl_width * AVG_CHAR_WIDTH_PIXELS
    widest_pixels = max(
        [min_width_per_cluster_pixels, MIN_CLUSTER_WIDTH_PIXELS, max_x_lbl_width_pixels]
    )
    width_per_cluster_pixels = widest_pixels + PADDING_PIXELS
    width_x_axis_title_pixels = len(x_axis_title) * AVG_CHAR_WIDTH_PIXELS + PADDING_PIXELS
    width_cluster_pixels = n_series * width_per_cluster_pixels
    width = max([width_cluster_pixels, width_x_axis_title_pixels, MIN_CHART_WIDTH_PIXELS])
    width = width * 0.9 if is_multi_chart else width
    return width

def get_common_charting_spec(charting_spec: BarChartingSpec, style_dets: StyleDets) -> CommonChartingSpec:
    """
    Get details that apply to all charts in bar chart set
    (often just one bar chart in set)

    Lots of interactive tweaking required to get charts to actually come out
    well under lots of interactive conditions (different numbers of columns etc.).

    Re: minor_ticks -- generally we don't want them
    as they result in lots of ticks between the groups in clustered bar charts
    each with a distracting and meaningless value
    e.g. if we have two groups 1 and 2 we don't want a tick for 0.8 and 0.9 etc.
    But if we don't have minor ticks when we have a massive number of clusters
    we get no ticks at all.
    Probably a dojo bug I can't fix, so I have to work around it.
    """
    ## colours
    colour_mappings = style_dets.chart.colour_mappings
    if charting_spec.is_single_series:
        colour_mappings = colour_mappings[:1]  ## only need the first
        ## This is an important special case because it affects the bar charts using the default style
        if colour_mappings[0].main == '#e95f29':  ## BURNT_ORANGE
            colour_mappings = [ColourWithHighlight('#e95f29', '#736354'), ]
    colours = [colour_mapping.main for colour_mapping in colour_mappings]
    colour_cases = [f'case "{colour_mapping.main}": hlColour = "{colour_mapping.highlight}"'
        for colour_mapping in colour_mappings]  ## actually only need first one for simple bar charts
    ## misc
    x_axis_lbl_dets = get_x_axis_lbl_dets(charting_spec.category_specs)
    x_axis_lbls = '[' + ',\n            '.join(x_axis_lbl_dets) + ']'
    y_max = charting_spec.max_y_val * 1.1
    has_minor_ticks_js_bool = 'true' if charting_spec.n_x_items >= DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM else 'false'
    legend_lbl = '' if charting_spec.is_single_series else charting_spec.legend_lbl
    stroke_width = style_dets.chart.stroke_width if charting_spec.show_borders else 0
    ## sizing
    max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if charting_spec.rotate_x_lbls else charting_spec.max_x_lbl_length)
    width_after_left_margin = get_width_after_left_margin(
        is_multi_chart=charting_spec.is_multi_chart,
        n_x_items=charting_spec.n_x_items, n_series=charting_spec.n_series,
        max_x_lbl_width=max_x_lbl_width, x_axis_title=charting_spec.x_axis_title)
    x_font_size = get_x_font_size(n_x_items=charting_spec.n_x_items, is_multi_chart=charting_spec.is_multi_chart)
    x_gap = get_x_gap(n_x_items=charting_spec.n_x_items, is_multi_chart=charting_spec.is_multi_chart)
    x_axis_title_len = len(charting_spec.x_axis_title)
    y_title_offset = get_y_title_offset(
        max_y_lbl_length=charting_spec.max_y_lbl_length,
        x_axis_title_len=x_axis_title_len, rotated_x_lbls=charting_spec.rotate_x_lbls)
    axis_lbl_drop = get_axis_lbl_drop(
        is_multi_chart=charting_spec.is_multi_chart, rotated_x_lbls=charting_spec.rotate_x_lbls,
        max_x_lbl_lines=charting_spec.max_x_lbl_lines)
    axis_lbl_rotate = -90 if charting_spec.rotate_x_lbls else 0
    left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
        offsets=left_margin_offset_dets, is_multi_chart=charting_spec.is_multi_chart,
        y_title_offset=y_title_offset, rotated_x_lbls=charting_spec.rotate_x_lbls)
    width = width_after_left_margin + left_margin_offset
    height = get_height(axis_lbl_drop=axis_lbl_drop,
        rotated_x_lbls=charting_spec.rotate_x_lbls, max_x_lbl_length=charting_spec.max_x_lbl_length)

    colour_spec = CommonColourSpec(
        axis_font=style_dets.chart.axis_font_colour,
        chart_bg=style_dets.chart.chart_bg_colour,
        colour_cases=colour_cases,
        colours=colours,
        major_grid_line=style_dets.chart.major_grid_line_colour,
        plot_bg=style_dets.chart.plot_bg_colour,
        plot_font=style_dets.chart.plot_font_colour,
        plot_font_filled=style_dets.chart.plot_font_colour_filled,
        tooltip_border=style_dets.chart.tooltip_border_colour,
    )
    misc_spec = CommonMiscSpec(
        axis_lbl_drop=axis_lbl_drop,
        axis_lbl_rotate=axis_lbl_rotate,
        connector_style=style_dets.dojo.connector_style,
        grid_line_width=style_dets.chart.grid_line_width,
        height=height,
        left_margin_offset=left_margin_offset,
        legend_lbl=legend_lbl,
        stroke_width=stroke_width,
        width=width,
        x_axis_lbls=x_axis_lbls,
        x_font_size=x_font_size,
        x_gap=x_gap,
        x_axis_title=charting_spec.x_axis_title,
        y_max=y_max,
        y_title=charting_spec.y_axis_title,
        y_title_offset=y_title_offset,
    )
    options = CommonOptions(
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        is_multi_chart=charting_spec.is_multi_chart,
        show_borders=charting_spec.show_borders,
        show_n_records=charting_spec.show_n_records,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: IndivChartSpec,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = f"<p><b>{indiv_chart_spec.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else ''
    n_records = 'N = ' + format_num(indiv_chart_spec.n_records) if common_charting_spec.options.show_n_records else ''
    dojo_series_dets = []
    for i, data_series_spec in enumerate(indiv_chart_spec.data_series_specs):
        series_id = f"{i:>02}"
        series_lbl = data_series_spec.lbl
        series_vals = str(data_series_spec.amounts)
        ## options e.g. {stroke: {color: "white", width: "0px"}, fill: "#e95f29", yLbls: ['66.38', ...]}
        fill_colour = common_charting_spec.colour_spec.colours[i]
        y_lbls_str = str(data_series_spec.tooltips)
        options = (f"""{{stroke: {{color: "white", width: "{common_charting_spec.misc_spec.stroke_width}px"}}, """
            f"""fill: "{fill_colour}", yLbls: {y_lbls_str}}}""")
        dojo_series_dets.append(DojoSeriesDetails(series_id, series_lbl, series_vals, options))
    indiv_context = {
        'chart_uuid': chart_uuid,
        'dojo_series_dets': dojo_series_dets,
        'indiv_title_html': indiv_title_html,
        'n_records': n_records,
        'page_break': page_break,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result
