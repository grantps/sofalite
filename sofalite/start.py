"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from webbrowser import open_new_tab

from sofalite.output.charts import bar
from sofalite.conf.chart import (
    BarChartDetails, ChartDetails, OverallChartsDetails, SeriesDetails, XAxisDetails)
from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.output.styles.misc import get_style_dets
from sofalite.output.stats import anova as html_anova
from sofalite.sql_extraction.db import Sqlite
from sofalite.stats_calc import anova

def run_anova():
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        grouping_fld_vals_dets = [
            ValDets(lbl='Japan', val=1), ValDets(lbl='Italy', val=2), ValDets(lbl='Germany', val=3)]
        anova_results = anova.get_results(cur, tbl_name='demo_tbl',
            grouping_fld_lbl='Country of Residence', grouping_fld_name='country',
            grouping_fld_vals_dets=grouping_fld_vals_dets,
            grouping_val_is_numeric=True,
            measure_fld_lbl='Age', measure_fld_name='age', high_precision_required=False)
        style_dets = get_style_dets(style='prestige_screen')
        html = html_anova.make_anova_html(anova_results, style_dets, dp=3, show_workings=False)
        fpath = '/home/g/Documents/sofalite/reports/anova_age_by_country_prestige_screen.html'
        with open(fpath, 'w') as f:
            f.write(html)
        open_new_tab(url=f"file://{fpath}")

def run_bar_chart():
    x_axis_dets = [
        XAxisDetails(val=1, lbl='Linux', lbl_split_into_lines='Linux'),
        XAxisDetails(val=2, lbl='Windows', lbl_split_into_lines='Windows'),
        XAxisDetails(val=3, lbl='Mac', lbl_split_into_lines='Mac'),
    ]
    series_dets_nz = SeriesDetails(
        legend_lbl='NZ',  ## e.g. "Italy", or None if only one series
        x_axis_dets=x_axis_dets,
        y_vals=[10.123456789, 6, 7.501],
        tool_tips=['10', '6', '7.5'],  ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]
    )
    series_dets_aus = SeriesDetails(
        legend_lbl='Australia',
        x_axis_dets=x_axis_dets,
        y_vals=[12.88, 4, 10.6574],
        tool_tips=['13', '4', '11'],
    )
    series_dets_japan = SeriesDetails(
        legend_lbl='Japan',
        x_axis_dets=x_axis_dets,
        y_vals=[7.99, 5.8, 12.12],
        tool_tips=['8', '6', '12'],
    )
    series_dets_taiwan = SeriesDetails(
        legend_lbl='Taiwan',
        x_axis_dets=x_axis_dets,
        y_vals=[26, 4, 17.1],
        tool_tips=['26', '4', '17'],
    )
    series_dets_usa = SeriesDetails(
        legend_lbl='USA',
        x_axis_dets=x_axis_dets,
        y_vals=[14, 15, 11],
        tool_tips=['14', '15', '11'],
    )
    chart_details = ChartDetails(
        n_records=1024,
        lbl='Countries',  ## e.g. "Gender: Male" or None if only one chart
        series_dets=[series_dets_nz, series_dets_aus, series_dets_japan,
            series_dets_taiwan, series_dets_usa],
    )
    overall_details = OverallChartsDetails(
        overall_title='overall title',
        overall_subtitle='overall subtitle',
        overall_legend_lbl='Gender',
        max_x_lbl_length=10,  ## may be needed to set chart height if labels are rotated
        max_y_lbl_length=2,  ## used to set left axis shift of chart(s) - so there is room for the y labels
        max_lbl_lines=1,  ## used to set axis lbl drop
        charts_details=[chart_details],
    )
    bar_chart_details = BarChartDetails(
        x_title='Operating System',
        y_title='Technical Excellence',
        rotate_x_lbls=False,
        show_n=True,
        show_borders=False,
        x_font_size=12,
        dp=4,
        overall_details=overall_details,
    )
    style_dets = get_style_dets(style='two_degrees')
    html = bar.get_html(bar_chart_details, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_bar_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

# run_anova()
run_bar_chart()
