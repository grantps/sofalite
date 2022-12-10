from dataclasses import dataclass
from typing import Sequence
import uuid

import jinja2

from sofalite.conf.chart import IndivChartSpec, PieChartingSpec
from sofalite.conf.style import StyleDets
from sofalite.output.charts.common import (
    ChartingSpec as CommonChartingSpec, get_common_charting_spec, get_indiv_chart_html)
from sofalite.output.styles.misc import get_long_colour_list
from sofalite.utils.misc import todict

@dataclass(frozen=True)
class CommonColourSpec:
    colour_cases: Sequence[str]
    plot_bg: str
    plot_bg_filled: str
    plot_font: str
    plot_font_filled: str
    slice_colours: Sequence[str]
    tooltip_border: str

@dataclass(frozen=True)
class CommonOptions:
    is_multi_chart: bool

@dataclass(frozen=True)
class CommonMiscSpec:
    connector_style: str
    height: float  ## pixels
    lbl_offset: int
    radius: float
    slice_font_size: int
    slice_lbls: Sequence[str]
    slice_vals: Sequence[float]
    width: float  ## pixels

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart dets
    and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: CommonMiscSpec
    options: CommonOptions

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

 make_chart_{{chart_uuid}} = function(){

     slices = [
       {% for slice_str in slice_strs %}\n            {{slice_str}}{% endfor %}
     ];

     var conf = new Array();
         conf["connector_style"] = "{{connector_style}}";
         conf["n_records"] = "{{n_records}}";
         conf["plot_bg_colour_filled"] = "{{plot_bg_filled}}";
         conf["plot_font_colour_filled"] = "{{plot_font_filled}}";
         conf["radius"] = {{radius}};
         conf["slice_colours"] = {{slice_colours_as_displayed}};
         conf["slice_font_size"] = {{slice_font_size}};
         conf["tooltip_border_colour"] = "{{tooltip_border}}";
         // distinct fields for pie charts
         conf["highlight"] = highlight_{{chart_uuid}};
         conf["lbl_offset"] = {{lbl_offset}};

     makePieChart("pie_chart_{{chart_uuid}}", slices, conf);
 }
 </script>

 <div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
 {{indiv_title_html}}
     <div id="pie_chart_{{chart_uuid}}"
         style="width: {{width}}px; height: {{height}}px;">
     </div>
     {% if legend_lbl %}
         <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
             {{legend_lbl}}:
         </p>
         <div id="legend_for_pie_chart_{{chart_uuid}}">
         </div>
     {% endif %}
 </div>
 """

@get_common_charting_spec.register
def get_common_pie_charting_spec(charting_spec: PieChartingSpec, style_dets: StyleDets) -> CommonChartingSpec:
    ## colours
    colour_mappings = style_dets.chart.colour_mappings
    colour_cases = [f'case "{colour_mapping.main}": hlColour = "{colour_mapping.highlight}"'
        for colour_mapping in colour_mappings]
    slice_colours = get_long_colour_list(colour_mappings)
    ## misc
    height = 370 if charting_spec.is_multi_chart else 420
    lbl_offset = -20 if charting_spec.is_multi_chart else -30
    radius = 120 if charting_spec.is_multi_chart else 140
    slice_font_size = 14 if charting_spec.n_charts < 10 else 10
    slice_vals = charting_spec.indiv_chart_specs[0].data_series_specs[0].amounts
    slice_lbls = [spec.lbl for spec in charting_spec.category_specs]
    if charting_spec.is_multi_chart:
        slice_font_size *= 0.8
    colour_spec = CommonColourSpec(
        colour_cases=colour_cases,
        plot_bg=style_dets.chart.plot_bg_colour,
        plot_bg_filled=style_dets.chart.plot_bg_colour_filled,
        plot_font=style_dets.chart.plot_font_colour,
        plot_font_filled=style_dets.chart.plot_font_colour_filled,
        slice_colours=slice_colours,
        tooltip_border=style_dets.chart.tooltip_border_colour,
    )
    misc_spec = CommonMiscSpec(
        connector_style=style_dets.dojo.connector_style,
        height=height,
        lbl_offset=lbl_offset,
        radius=radius,
        slice_font_size=slice_font_size,
        slice_lbls=slice_lbls,
        slice_vals=slice_vals,
        width=450,
    )
    options = CommonOptions(
        is_multi_chart=charting_spec.is_multi_chart,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

@get_indiv_chart_html.register
def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: IndivChartSpec,
        *,  chart_counter: int) -> str:
    """
    Note - to keep the same colours for the same slice categories
    it is important to keep them aligned even if some slices are not displayed
    (because 'y' value is 0).
    """
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = (f"<p><b>{indiv_chart_spec.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else '')
    ## slices
    only_series = indiv_chart_spec.data_series_specs[0]
    slice_lbls = common_charting_spec.misc_spec.slice_lbls
    slice_colours = common_charting_spec.colour_spec.slice_colours
    slice_colours = slice_colours[:len(slice_lbls)]
    slice_details = zip(
        slice_lbls,
        only_series.amounts,  ## the actual frequencies e.g. 120 for avg NZ IQ
        slice_colours,
        only_series.tooltips,
        strict=True)
    slice_strs = []
    slice_colours_as_displayed = []
    for slice_lbl, slice_val, colour, tool_tip in slice_details:
        if slice_val == 0:
            continue
        slice_str = f"""{{"val": {slice_val}, "lbl": "{slice_lbl}", "tooltip": "{tool_tip}"}},"""
        slice_strs.append(slice_str)
        slice_colours_as_displayed.append(colour)
    slice_strs[-1] = slice_strs[-1].rstrip(',')
    indiv_context = {
        'chart_uuid': chart_uuid,
        'indiv_title_html': indiv_title_html,
        'page_break': page_break,
        'slice_colours_as_displayed': slice_colours_as_displayed,
        'slice_strs': slice_strs,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result
