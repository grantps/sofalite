from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from typing import Any
import uuid

import jinja2

from sofalite.conf.main import AVG_CHAR_WIDTH_PIXELS, DATABASE_FOLDER, TEXT_WIDTH_WHEN_ROTATED, VAR_LABELS
from sofalite.data_extraction.charts.boxplot import (
    BoxplotChartingSpec, BoxplotIndivChartSpec, get_by_category_charting_spec, get_by_series_category_charting_spec)
from sofalite.data_extraction.db import Sqlite
from sofalite.output.charts.common import get_common_charting_spec, get_html, get_indiv_chart_html
from sofalite.output.charts.interfaces import JSBool, LeftMarginOffsetSpec
from sofalite.output.charts.utils import (
    get_axis_lbl_drop, get_height, get_left_margin_offset, get_x_axis_lbls_val_and_text,
    get_x_axis_font_size, get_y_axis_title_offset)
from sofalite.output.interfaces import HTMLItemSpec, OutputItemType
from sofalite.output.styles.interfaces import ColourWithHighlight, StyleSpec
from sofalite.output.styles.utils import get_long_colour_list, get_style_spec
from sofalite.stats_calc.interfaces import BoxplotType, SortOrder
from sofalite.utils.maths import format_num
from sofalite.utils.misc import todict

left_margin_offset_spec = LeftMarginOffsetSpec(
    initial_offset=25, wide_offset=35, rotate_offset=10, multi_chart_offset=0)

@dataclass(frozen=True)
class DojoBoxSpec:
    """
    Has huge overlap with non_standard.BoxplotDataItem
    """
    center: float
    indiv_box_lbl: str
    box_bottom: float
    box_bottom_rounded: float
    bottom_whisker: float
    bottom_whisker_rounded: float
    median: float
    median_rounded: float
    outliers: Sequence[float] | None
    outliers_rounded: Sequence[float] | None
    box_top: float
    box_top_rounded: float
    top_whisker: float
    top_whisker_rounded: float

@dataclass(frozen=True)
class BoxplotDojoSeriesSpec:
    """
    Used for DOJO boxplots (which have series).
    Scatterplots, and more general charts with series (e.g. bar charts and line charts),
    have different specs of their own for DOJO series.
    """
    box_specs: Sequence[DojoBoxSpec]
    lbl: str
    series_id: str  ## e.g. 01
    stroke_colour: str

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
    // add each box to single multi-series
    var series_conf = new Array();  // for legend settings via dummy (invisible) chart
    var series = new Array();

    {% for series_spec in dojo_series_specs %}

        var series_conf_{{series_spec.series_id}} = new Array();
        series_conf_{{series_spec.series_id}} = {
          seriesLabel: "{{series_spec.lbl}}",
          seriesStyle: {
              stroke: {
                  color: "{{series_spec.stroke_colour}}",
                  width: "1px"
              },
              fill: getfainthex("{{series_spec.stroke_colour}}")
          }
        };
        series_conf.push(series_conf_{{series_spec.series_id}});

        // all of the actual series data (i.e. not just the legend details) is box-level i.e. nested under series

        {% for box_spec in series_spec.box_specs %}
            var box_{{series_spec.series_id}}_{{loop.index0}} = new Array();
            box_{{series_spec.series_id}}_{{loop.index0}}['stroke'] = "{{series_spec.stroke_colour}}";
            box_{{series_spec.series_id}}_{{loop.index0}}['center'] = "{{box_spec.center}}";
            box_{{series_spec.series_id}}_{{loop.index0}}['fill'] = getfainthex("{{series_spec.stroke_colour}}");
            box_{{series_spec.series_id}}_{{loop.index0}}['width'] = {{bar_width}};
            box_{{series_spec.series_id}}_{{loop.index0}}['indiv_boxlbl'] = "{{box_spec.indiv_box_lbl}}";

            var summary_data_{{series_spec.series_id}}_{{loop.index0}} = new Array();
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['bottom_whisker'] = {{box_spec.bottom_whisker}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['bottom_whisker_rounded'] = {{box_spec.bottom_whisker_rounded}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['box_bottom'] = {{box_spec.box_bottom}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['box_bottom_rounded'] = {{box_spec.box_bottom_rounded}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['median'] = {{box_spec.median}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['median_rounded'] = {{box_spec.median_rounded}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['box_top'] = {{box_spec.box_top}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['box_top_rounded'] = {{box_spec.box_top_rounded}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['top_whisker'] = {{box_spec.top_whisker}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['top_whisker_rounded'] = {{box_spec.top_whisker_rounded}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['outliers'] = {{box_spec.outliers}};
            summary_data_{{series_spec.series_id}}_{{loop.index0}}['outliers_rounded'] = {{box_spec.outliers_rounded}};
            box_{{series_spec.series_id}}_{{loop.index0}}['summary_data'] = summary_data_{{series_spec.series_id}}_{{loop.index0}};

            series.push(box_{{series_spec.series_id}}_{{loop.index0}});

        {% endfor %}

    {% endfor %}  // series_spec

    var conf = new Array();
        conf["axis_font_colour"] = "{{axis_font}}";
        conf["axis_lbl_drop"] = {{axis_lbl_drop}};
        conf["axis_lbl_rotate"] = {{axis_lbl_rotate}};
        conf["chart_bg_colour"] = "{{chart_bg}}";
        conf["connector_style"] = "{{connector_style}}";
        conf["grid_line_width"] = {{grid_line_width}};
        conf["has_minor_ticks"] = {{has_minor_ticks_js_bool}};
        conf["highlight"] = highlight_{{chart_uuid}};
        conf["left_margin_offset"] = {{left_margin_offset}};
        conf["n_records"] = "{{n_records}}";
        conf["plot_bg_colour"] = "{{plot_bg}}";
        conf["plot_font_colour"] = "{{plot_font}}";
        conf["tooltip_border_colour"] = "{{tooltip_border}}";
        conf["x_axis_lbls"] = {{x_axis_lbls}};
        conf["x_axis_title"] = "{{x_axis_title}}";
        conf["x_axis_font_size"] = {{x_axis_font_size}};
        conf["x_axis_max_val"] = {{x_axis_max_val}};
        conf["y_axis_max_val"] = {{y_axis_max_val}};
        conf["y_axis_min_val"] = {{y_axis_min_val}};
        conf["y_axis_title"] = "{{y_axis_title}}";
        conf["y_axis_title_offset"] = {{y_axis_title_offset}};

    makeBoxAndWhisker("boxplot_{{chart_uuid}}", series, series_conf, conf);
}
</script>

<div class="screen-float-only" style="margin-right: 10px; {{page_break}}">
{{indiv_title_html}}
    <div id="boxplot_{{chart_uuid}}"
        style="width: {{width}}px; height: {{height}}px;">
    </div>
    {% if legend_lbl %}
        <p style="float: left; font-weight: bold; margin-right: 12px; margin-top: 9px;">
            {{legend_lbl}}:
        </p>
        <div id="dummy_boxplot_{{chart_uuid}}"
            style="float: right; width: 100px; height: 100px; visibility: hidden;">
        </div>
        <div id="legend_for_boxplot_{{chart_uuid}}">
        </div>
    {% endif %}
</div>
"""

@dataclass(frozen=True)
class CommonColourSpec:
    axis_font: str
    chart_bg: str
    colours: Sequence[str]
    major_grid_line: str
    plot_bg: str
    plot_font: str
    plot_font_filled: str
    tooltip_border: str

@dataclass(frozen=True)
class CommonOptions:
    has_minor_ticks_js_bool: JSBool
    show_n_records: bool

@dataclass(frozen=True)
class CommonMiscSpec:
    axis_lbl_drop: int
    axis_lbl_rotate: int
    connector_style: str
    grid_line_width: int
    height: float  ## pixels
    left_margin_offset: float
    legend_lbl: str
    width: float  ## pixels
    x_axis_lbls: str  ## e.g. [{value: 1, text: "Female"}, {value: 2, text: "Male"}]
    x_axis_font_size: float
    x_axis_max_val: float
    x_axis_title: str
    y_axis_title: str
    y_axis_title_offset: int
    y_axis_max_val: float
    y_axis_min_val: float

@dataclass(frozen=True)
class CommonChartingSpec:
    """
    Ready to combine with individual chart spec and feed into the Dojo JS engine.
    """
    colour_spec: CommonColourSpec
    misc_spec: CommonMiscSpec
    options: CommonOptions

def get_width_after_left_margin(*, n_x_items: int, n_series: int,
        max_x_lbl_width: int, x_axis_title: str) -> float:
    PADDING_PIXELS = 50
    MIN_PIXELS_PER_BOX = 30
    MIN_CHART_WIDTH = (200 if n_x_items == 1  # only one box
        else 400)
    min_pixels_per_cat = MIN_PIXELS_PER_BOX * n_series
    width_per_cat = (max([min_pixels_per_cat, max_x_lbl_width * AVG_CHAR_WIDTH_PIXELS]) + PADDING_PIXELS)
    width_x_axis_title = len(x_axis_title) * AVG_CHAR_WIDTH_PIXELS + PADDING_PIXELS
    width = max([width_per_cat * n_x_items, width_x_axis_title, MIN_CHART_WIDTH])
    return width

@get_common_charting_spec.register
def get_common_charting_spec(charting_spec: BoxplotChartingSpec, style_spec: StyleSpec) -> CommonChartingSpec:
    colour_mappings = style_spec.chart.colour_mappings
    if charting_spec.is_single_series:
        colour_mappings = colour_mappings[:1]  ## only need the first
        ## This is an important special case because it affects the bar charts using the default style
        if colour_mappings[0].main == '#e95f29':  ## BURNT_ORANGE
            colour_mappings = [ColourWithHighlight('#e95f29', '#736354'), ]
    colours = get_long_colour_list(colour_mappings)
    axis_lbl_drop = get_axis_lbl_drop(
        is_multi_chart=False, rotated_x_lbls=charting_spec.rotate_x_lbls,
        max_x_axis_lbl_lines=charting_spec.max_x_axis_lbl_lines)
    axis_lbl_rotate = -90 if charting_spec.rotate_x_lbls else 0
    has_minor_ticks_js_bool: JSBool = 'true' if charting_spec.has_minor_ticks else 'false'
    legend_lbl = '' if charting_spec.is_single_series else charting_spec.legend_lbl
    x_axis_lbls_val_and_text = get_x_axis_lbls_val_and_text(charting_spec.category_specs)
    x_axis_lbls = '[' + ',\n            '.join(x_axis_lbls_val_and_text) + ']'
    y_axis_max_val = charting_spec.y_axis_max_val * 1.1
    ## sizing
    height = get_height(axis_lbl_drop=axis_lbl_drop,
        rotated_x_lbls=charting_spec.rotate_x_lbls, max_x_axis_lbl_len=charting_spec.max_x_axis_lbl_len)
    max_x_lbl_width = (TEXT_WIDTH_WHEN_ROTATED if charting_spec.rotate_x_lbls else charting_spec.max_x_axis_lbl_len)
    width_after_left_margin = get_width_after_left_margin(
        n_x_items=charting_spec.n_x_items, n_series=charting_spec.n_series,
        max_x_lbl_width=max_x_lbl_width, x_axis_title=charting_spec.x_axis_title)
    x_axis_title_len = len(charting_spec.x_axis_title)
    y_axis_title_offset = get_y_axis_title_offset(
        x_axis_title_len=x_axis_title_len, rotated_x_lbls=charting_spec.rotate_x_lbls)
    left_margin_offset = get_left_margin_offset(width_after_left_margin=width_after_left_margin,
        offsets=left_margin_offset_spec, is_multi_chart=False,
        y_axis_title_offset=y_axis_title_offset, rotated_x_lbls=charting_spec.rotate_x_lbls)
    x_axis_font_size = get_x_axis_font_size(n_x_items=charting_spec.n_x_items, is_multi_chart=False)
    width = left_margin_offset + width_after_left_margin

    colour_spec = CommonColourSpec(
        axis_font=style_spec.chart.axis_font_colour,
        chart_bg=style_spec.chart.chart_bg_colour,
        colours=colours,
        major_grid_line=style_spec.chart.major_grid_line_colour,
        plot_bg=style_spec.chart.plot_bg_colour,
        plot_font=style_spec.chart.plot_font_colour,
        plot_font_filled=style_spec.chart.plot_font_colour_filled,
        tooltip_border=style_spec.chart.tooltip_border_colour,
    )
    misc_spec = CommonMiscSpec(
        axis_lbl_drop=axis_lbl_drop,
        axis_lbl_rotate=axis_lbl_rotate,
        connector_style=style_spec.dojo.connector_style,
        grid_line_width=style_spec.chart.grid_line_width,
        height=height,
        left_margin_offset=left_margin_offset,
        legend_lbl=legend_lbl,
        width=width,
        x_axis_lbls=x_axis_lbls,
        x_axis_font_size=x_axis_font_size,
        x_axis_max_val=charting_spec.x_axis_max_val,
        x_axis_title=charting_spec.x_axis_title,
        y_axis_max_val=y_axis_max_val,
        y_axis_min_val=charting_spec.y_axis_min_val,
        y_axis_title=charting_spec.y_axis_title,
        y_axis_title_offset=y_axis_title_offset,
    )
    options = CommonOptions(
        has_minor_ticks_js_bool=has_minor_ticks_js_bool,
        show_n_records=charting_spec.show_n_records,
    )
    return CommonChartingSpec(
        colour_spec=colour_spec,
        misc_spec=misc_spec,
        options=options,
    )

@get_indiv_chart_html.register
def get_indiv_chart_html(common_charting_spec: CommonChartingSpec, indiv_chart_spec: BoxplotIndivChartSpec,
        *,  chart_counter: int) -> str:
    context = todict(common_charting_spec.colour_spec, shallow=True)
    context.update(todict(common_charting_spec.misc_spec, shallow=True))
    context.update(todict(common_charting_spec.options, shallow=True))
    chart_uuid = str(uuid.uuid4()).replace('-', '_')  ## needs to work in JS variable names
    page_break = 'page-break-after: always;' if chart_counter % 2 == 0 else ''

    bar_width = indiv_chart_spec.bar_width
    n_records = 'N = ' + format_num(indiv_chart_spec.n_records) if common_charting_spec.options.show_n_records else ''

    dojo_series_specs = []
    for i, data_series_spec in enumerate(indiv_chart_spec.data_series_specs):
        series_id = f"{i:>02}"
        stroke_colour = common_charting_spec.colour_spec.colours[i]
        box_specs = []
        for box_item in data_series_spec.box_items:
            if not box_item:
                continue
            has_outliers = bool(box_item.outliers)
            if has_outliers:
                outliers = box_item.outliers
                outliers_rounded = box_item.outliers_rounded
            else:
                outliers = []
                outliers_rounded = []
            box_spec = DojoBoxSpec(
                center=box_item.center,
                indiv_box_lbl=box_item.indiv_box_lbl,
                box_bottom=box_item.box_bottom,
                box_bottom_rounded=box_item.box_bottom_rounded,
                bottom_whisker=box_item.bottom_whisker,
                bottom_whisker_rounded=box_item.bottom_whisker_rounded,
                median=box_item.median,
                median_rounded=box_item.median_rounded,
                outliers=outliers,
                outliers_rounded=outliers_rounded,
                box_top=box_item.box_top,
                box_top_rounded=box_item.box_top_rounded,
                top_whisker=box_item.top_whisker,
                top_whisker_rounded=box_item.top_whisker_rounded,
            )
            box_specs.append(box_spec)
        series_spec = BoxplotDojoSeriesSpec(
            box_specs=box_specs,
            lbl=data_series_spec.lbl,
            series_id=series_id,
            stroke_colour=stroke_colour,
        )
        dojo_series_specs.append(series_spec)
    indiv_context = {
        'bar_width': bar_width,
        'chart_uuid': chart_uuid,
        'dojo_series_specs': dojo_series_specs,
        'n_records': n_records,
        'page_break': page_break,
    }
    context.update(indiv_context)
    environment = jinja2.Environment()
    template = environment.from_string(tpl_chart)
    html_result = template.render(context)
    return html_result

@dataclass(frozen=True)
class BoxplotChartSpec:
    style_name: str
    category_fld_name: str
    fld_name: str
    tbl_name: str
    tbl_filt_clause: str | None = None
    cur: Any | None = None
    category_sort_order: SortOrder = SortOrder.VALUE
    boxplot_type: BoxplotType = BoxplotType.IQR_1_PT_5_OR_INSIDE
    rotate_x_lbls: bool = False
    show_n_records: bool = True
    x_axis_font_size: int = 12
    dp: int = 3

    def to_html_spec(self) -> HTMLItemSpec:
        # style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        category_fld_lbl = VAR_LABELS.var2var_lbl.get(self.category_fld_name, self.category_fld_name)
        category_vals2lbls = VAR_LABELS.var2val2lbl.get(self.category_fld_name, self.category_fld_name)
        fld_lbl = VAR_LABELS.var2var_lbl.get(self.fld_name, self.fld_name)
        ## data
        get_by_category_charting_spec_for_cur = partial(get_by_category_charting_spec,
            tbl_name=self.tbl_name,
            category_fld_name=self.category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=self.fld_name, fld_lbl=fld_lbl,
            category_vals2lbls=category_vals2lbls, category_sort_order=self.category_sort_order,
            tbl_filt_clause=self.tbl_filt_clause,
            boxplot_type=self.boxplot_type,
        )
        local_cur = not bool(self.cur)
        if local_cur:
            with Sqlite(DATABASE_FOLDER) as (_con, cur):
                intermediate_charting_spec = get_by_category_charting_spec_for_cur(cur)
        else:
            intermediate_charting_spec = get_by_category_charting_spec_for_cur(self.cur)
        ## charts details
        category_specs = intermediate_charting_spec.to_sorted_category_specs()
        indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=self.dp)
        charting_spec = BoxplotChartingSpec(
            category_specs=category_specs,
            indiv_chart_specs=[indiv_chart_spec, ],
            legend_lbl=intermediate_charting_spec.series_fld_lbl,
            rotate_x_lbls=self.rotate_x_lbls,
            show_n_records=self.show_n_records,
            x_axis_title=intermediate_charting_spec.category_fld_lbl,
            y_axis_title=intermediate_charting_spec.fld_lbl,
        )
        ## output
        html = get_html(charting_spec, style_spec)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.CHART,
        )

@dataclass(frozen=True)
class MultiSeriesBoxplotChartSpec:
    style_name: str
    series_fld_name: str
    category_fld_name: str
    fld_name: str
    tbl_name: str
    tbl_filt_clause: str | None = None
    cur: Any | None = None
    category_sort_order: SortOrder = SortOrder.VALUE
    boxplot_type: BoxplotType = BoxplotType.IQR_1_PT_5_OR_INSIDE
    rotate_x_lbls: bool = False
    show_n_records: bool = True
    x_axis_font_size: int = 12
    dp: int = 3

    def to_html_spec(self) -> HTMLItemSpec:
        # style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        series_fld_lbl = VAR_LABELS.var2var_lbl.get(self.series_fld_name, self.series_fld_name)
        category_fld_lbl = VAR_LABELS.var2var_lbl.get(self.category_fld_name, self.category_fld_name)
        series_vals2lbls = VAR_LABELS.var2val2lbl.get(self.series_fld_name, self.series_fld_name)
        category_vals2lbls = VAR_LABELS.var2val2lbl.get(self.category_fld_name, self.category_fld_name)
        fld_lbl = VAR_LABELS.var2var_lbl.get(self.fld_name, self.fld_name)
        ## data
        get_by_series_category_charting_spec_for_cur = partial(get_by_series_category_charting_spec,
            tbl_name=self.tbl_name,
            series_fld_name=self.series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=self.category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=self.fld_name, fld_lbl=fld_lbl,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls, category_sort_order=self.category_sort_order,
            tbl_filt_clause=self.tbl_filt_clause,
            boxplot_type=self.boxplot_type,
        )
        local_cur = not bool(self.cur)
        if local_cur:
            with Sqlite(DATABASE_FOLDER) as (_con, cur):
                intermediate_charting_spec = get_by_series_category_charting_spec_for_cur(cur)
        else:
            intermediate_charting_spec = get_by_series_category_charting_spec_for_cur(self.cur)
        ## charts details
        category_specs = intermediate_charting_spec.to_sorted_category_specs()
        indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=self.dp)
        charting_spec = BoxplotChartingSpec(
            category_specs=category_specs,
            indiv_chart_specs=[indiv_chart_spec, ],
            legend_lbl=intermediate_charting_spec.series_fld_lbl,
            rotate_x_lbls=self.rotate_x_lbls,
            show_n_records=self.show_n_records,
            x_axis_title=intermediate_charting_spec.category_fld_lbl,
            y_axis_title=intermediate_charting_spec.fld_lbl,
        )
        ## output
        html = get_html(charting_spec, style_spec)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.CHART,
        )
