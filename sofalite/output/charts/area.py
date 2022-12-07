from dataclasses import astuple, dataclass
import uuid

import jinja2

from sofalite.conf.chart import (
    ChartDetails, DojoSeriesDetails, GenericChartingDetails, LeftMarginOffsetDetails, PlotStyle)
from sofalite.conf.style import StyleDets
from sofalite.output.charts.common import ChartingSpec as CommonChartingSpec, LineArea
from sofalite.utils.misc import todict

@dataclass(frozen=True, kw_only=True)
class ChartingSpec(CommonChartingSpec):
    """
    Compared with bar lacks show_borders.

    Only single-series line charts can have a trend line (or the smoothed option).
    """
    ## specific details for line charting
    dp: int
    is_time_series: bool = False
    major_ticks: bool = False
    rotate_x_lbls: bool = False
    show_markers: bool = True
    show_n: bool = False
    x_font_size: int = 12
    x_title: str
    y_title: str
    ## generic charting details
    generic_charting_dets: GenericChartingDetails

    def __post_init(self):
        multi_series = len(self.generic_charting_dets.charts_details[0].series_dets) > 1
        if multi_series and (self.show_trend_line or self.show_smooth_line):
            raise Exception("A smoothed line or a trend line can only be show if one series of results "
                "i.e. not split by another variable e.g. one line chart per gender")

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

def get_common_charting_spec(charting_spec: ChartingSpec, style_dets: StyleDets) -> CommonChartingSpec:
    ## convenience pre-calcs
    is_multi_chart = (len(charting_spec.generic_charting_dets.charts_details) > 1)
    first_chart_dets = charting_spec.generic_charting_dets.charts_details[0]
    first_series = first_chart_dets.series_dets[0]
    n_x_items = len(first_series.x_axis_specs)
    ## colours
    first_colour_mapping = style_dets.chart.colour_mappings[0]
    line_colour, fill_colour = astuple(first_colour_mapping)
    ## misc
    has_minor_ticks_js_bool = 'true' if n_x_items >= LineArea.DOJO_MINOR_TICKS_NEEDED_PER_X_ITEM else 'false'
    has_micro_ticks_js_bool = 'true' if n_x_items > LineArea.DOJO_MICRO_TICKS_NEEDED_PER_X_ITEM else 'false'
    is_time_series_js_bool = 'true' if charting_spec.is_time_series else 'false'
    legend_lbl = ''
    left_margin_offset_dets = LeftMarginOffsetDetails(
        initial_offset=18, wide_offset=25, rotate_offset=5, multi_chart_offset=10)
    colour_spec = CommonColourSpec(
        axis_font=style_dets.chart.axis_font_colour,
        chart_bg=style_dets.chart.chart_bg_colour,
        line=line_colour,
        fill=fill_colour,
        major_grid_line=style_dets.chart.major_grid_line_colour,
        plot_bg=style_dets.chart.plot_bg_colour,
        plot_font=style_dets.chart.plot_font_colour,
        plot_font_filled=style_dets.chart.plot_font_colour_filled,
        tooltip_border=style_dets.chart.tooltip_border_colour,
    )
    misc_spec = LineArea.get_misc_spec(charting_spec, style_dets, legend_lbl, left_margin_offset_dets)
    options = LineArea.CommonOptions(
        has_micro_ticks_js_bool=has_micro_ticks_js_bool,
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        is_multi_chart=is_multi_chart,
        is_time_series=charting_spec.is_time_series,
        is_time_series_js_bool=is_time_series_js_bool,
        show_markers=charting_spec.show_markers,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_dets: ChartDetails,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    single_series = len(indiv_chart_dets.series_dets) == 1
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''
    indiv_title_html = (f"<p><b>{indiv_chart_dets.lbl}</b></p>" if common_charting_spec.options.is_multi_chart else '')
    ## each standard series
    dojo_series_dets = []
    marker_plot_style = PlotStyle.DEFAULT if common_charting_spec.options.show_markers else PlotStyle.UNMARKED
    for i, series in enumerate(indiv_chart_dets.series_dets):
        series_id = f"{i:>02}"
        series_lbl = series.legend_lbl
        if common_charting_spec.options.is_time_series:
            series_vals = LineArea.get_time_series_vals(
                common_charting_spec.misc_spec.x_axis_specs, series.y_vals, common_charting_spec.misc_spec.x_title)
        else:
            series_vals = str(series.y_vals)
        ## options
        ## e.g. {stroke: {color: '#e95f29', width: '6px'}, yLbls: ['x-val: 2016-01-01<br>y-val: 12<br>0.8%', ... ], plot: 'default'};
        line_colour = common_charting_spec.colour_spec.line
        fill_colour = common_charting_spec.colour_spec.fill
        y_lbls_str = str(series.tool_tips)
        options = (f"""{{stroke: {{color: "{line_colour}", width: "6px"}}, """
            f"""fill: "{fill_colour}", """
            f"""yLbls: {y_lbls_str}, plot: "{marker_plot_style}"}}""")
        dojo_series_dets.append(DojoSeriesDetails(series_id, series_lbl, series_vals, options))
    indiv_context = {
        'chart_uuid': chart_uuid,
        'dojo_series_dets': dojo_series_dets,
        'indiv_title_html': indiv_title_html,
        'page_break': page_break,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(LineArea.tpl_chart)
    html_result = template.render(context)
    return html_result
