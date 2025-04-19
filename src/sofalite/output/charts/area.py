from dataclasses import astuple, dataclass
import uuid

import jinja2

from sofalite.output.charts.interfaces import DojoSeriesDetails, PlotStyle

from sofalite.output.charts.interfaces import IndivChartSpec, LineArea
from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.charts.common import get_common_charting_spec, get_indiv_chart_html
from sofalite.output.charts.interfaces import AreaChartingSpec, LeftMarginOffsetDetails
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

@dataclass(frozen=True)
class CommonColourSpec(LineArea.CommonColourSpec):
    fill: str
    line: str

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart specs
    and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: LineArea.CommonMiscSpec
    options: LineArea.CommonOptions

@get_common_charting_spec.register
def get_common_charting_spec(charting_spec: AreaChartingSpec, style_specs: StyleSpec) -> CommonChartingSpec:
    ## colours
    first_colour_mapping = style_specs.chart.colour_mappings[0]
    line_colour, fill_colour = astuple(first_colour_mapping)
    ## misc
    has_minor_ticks_js_bool = ('true' if charting_spec.n_x_items >= LineArea.DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM
        else 'false')
    has_micro_ticks_js_bool = ('true' if charting_spec.n_x_items > LineArea.DOJO_MICRO_TICKS_NEEDED_PER_X_ITEM
        else 'false')
    is_time_series_js_bool = 'true' if charting_spec.is_time_series else 'false'
    legend_lbl = ''
    left_margin_offset_dets = LeftMarginOffsetDetails(
        initial_offset=18, wide_offset=25, rotate_offset=5, multi_chart_offset=10)
    colour_spec = CommonColourSpec(
        axis_font=style_specs.chart.axis_font_colour,
        chart_bg=style_specs.chart.chart_bg_colour,
        line=line_colour,
        fill=fill_colour,
        major_grid_line=style_specs.chart.major_grid_line_colour,
        plot_bg=style_specs.chart.plot_bg_colour,
        plot_font=style_specs.chart.plot_font_colour,
        plot_font_filled=style_specs.chart.plot_font_colour_filled,
        tooltip_border=style_specs.chart.tooltip_border_colour,
    )
    misc_spec = LineArea.get_misc_spec(charting_spec, style_specs, legend_lbl, left_margin_offset_dets)
    options = LineArea.CommonOptions(
        has_micro_ticks_js_bool=has_micro_ticks_js_bool,
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        is_multi_chart=charting_spec.is_multi_chart,
        is_single_series=charting_spec.is_single_series,
        is_time_series=charting_spec.is_time_series,
        is_time_series_js_bool=is_time_series_js_bool,
        show_markers=charting_spec.show_markers,
        show_n_records=charting_spec.show_n_records,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

@get_indiv_chart_html.register
def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: IndivChartSpec,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    if not common_charting_spec.options.is_single_series:
        raise Exception("Area charts must be single series charts")
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = (f"<p><b>{indiv_chart_spec.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else '')
    n_records = 'N = ' + format_num(indiv_chart_spec.n_records) if common_charting_spec.options.show_n_records else ''
    ## the standard series
    dojo_series_dets = []
    marker_plot_style = PlotStyle.DEFAULT if common_charting_spec.options.show_markers else PlotStyle.UNMARKED
    only_series = indiv_chart_spec.data_series_specs[0]
    series_id = '00'
    series_lbl = only_series.lbl
    if common_charting_spec.options.is_time_series:
        series_vals = LineArea.get_time_series_vals(common_charting_spec.misc_spec.x_axis_specs,
            only_series.amounts, common_charting_spec.misc_spec.x_axis_title)
    else:
        series_vals = str(only_series.amounts)
    ## options
    ## e.g. {stroke: {color: '#e95f29', width: '6px'}, yLbls: ['x-val: 2016-01-01<br>y-val: 12<br>0.8%', ... ], plot: 'default'};
    line_colour = common_charting_spec.colour_spec.line
    fill_colour = common_charting_spec.colour_spec.fill
    y_lbls_str = str(only_series.tooltips)
    options = (f"""{{stroke: {{color: "{line_colour}", width: "6px"}}, """
        f"""fill: "{fill_colour}", """
        f"""yLbls: {y_lbls_str}, plot: "{marker_plot_style}"}}""")
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
    template = environment.from_string(LineArea.tpl_chart)
    html_result = template.render(context)
    return html_result
