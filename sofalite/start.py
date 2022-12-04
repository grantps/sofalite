"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from webbrowser import open_new_tab

from sofalite.output.charts import bar, line
from sofalite.conf.chart import (
    ChartDetails, GenericChartingDetails, SeriesDetails, XAxisSpec)
from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.output.charts.bar import BarChartingSpec
from sofalite.output.charts.line import LineChartingSpec
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
    x_axis_specs = [
        XAxisSpec(val=1, lbl='Linux', lbl_split_into_lines='Linux'),
        XAxisSpec(val=2, lbl='Windows', lbl_split_into_lines='Windows'),
        XAxisSpec(val=3, lbl='Mac', lbl_split_into_lines='Mac'),
    ]
    series_dets_nz = SeriesDetails(
        legend_lbl='NZ',  ## e.g. "Italy", or None if only one series
        x_axis_specs=x_axis_specs,
        y_vals=[10.123456789, 6, 7.501],
        tool_tips=['10', '6', '7.5'],  ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]
    )
    series_dets_aus = SeriesDetails(
        legend_lbl='Australia',
        x_axis_specs=x_axis_specs,
        y_vals=[12.88, 4, 10.6574],
        tool_tips=['13', '4', '11'],
    )
    series_dets_japan = SeriesDetails(
        legend_lbl='Japan',
        x_axis_specs=x_axis_specs,
        y_vals=[7.99, 5.8, 12.12],
        tool_tips=['8', '6', '12'],
    )
    series_dets_taiwan = SeriesDetails(
        legend_lbl='Taiwan',
        x_axis_specs=x_axis_specs,
        y_vals=[26, 4, 17.1],
        tool_tips=['26', '4', '17'],
    )
    series_dets_usa = SeriesDetails(
        legend_lbl='USA',
        x_axis_specs=x_axis_specs,
        y_vals=[14, 15, 11],
        tool_tips=['14', '15', '11'],
    )
    chart_details = ChartDetails(
        n_records=1024,
        lbl='Countries',  ## e.g. "Gender: Male" or None if only one chart
        series_dets=[series_dets_nz, series_dets_aus, series_dets_japan,
            series_dets_taiwan, series_dets_usa],
    )
    generic_charting_dets = GenericChartingDetails(
        overall_title='overall title',
        overall_subtitle='overall subtitle',
        overall_legend_lbl='Gender',
        max_x_lbl_length=10,  ## may be needed to set chart height if labels are rotated
        max_y_lbl_length=2,  ## used to set left axis shift of chart(s) - so there is room for the y labels
        max_lbl_lines=1,  ## used to set axis lbl drop
        charts_details=[chart_details],
    )
    bar_charting_spec = BarChartingSpec(
        x_title='Operating System',
        y_title='Technical Excellence',
        rotate_x_lbls=False,
        show_n=True,
        show_borders=False,
        x_font_size=12,
        dp=4,
        generic_charting_dets=generic_charting_dets,
    )
    style_dets = get_style_dets(style='two_degrees')
    html = bar.get_html(bar_charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_bar_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

x_axis_specs_cars = [
    XAxisSpec(val=1, lbl='BMW', lbl_split_into_lines='BMW'),
    XAxisSpec(val=2, lbl='PORSCHE', lbl_split_into_lines='PORSCHE'),
    XAxisSpec(val=3, lbl='AUDI', lbl_split_into_lines='AUDI'),
    XAxisSpec(val=4, lbl='MERCEDES', lbl_split_into_lines='MERCEDES'),
    XAxisSpec(val=5, lbl='VOLKSWAGEN', lbl_split_into_lines='VOLKSWAGEN'),
    XAxisSpec(val=6, lbl='FERRARI', lbl_split_into_lines='FERRARI'),
    XAxisSpec(val=7, lbl='FIAT', lbl_split_into_lines='FIAT'),
    XAxisSpec(val=8, lbl='LAMBORGHINI', lbl_split_into_lines='LAMBORGHINI'),
    XAxisSpec(val=9, lbl='MASERATI', lbl_split_into_lines='MASERATI'),
    XAxisSpec(val=10, lbl='HONDA', lbl_split_into_lines='HONDA'),
    XAxisSpec(val=11, lbl='TOYOTA', lbl_split_into_lines='TOYOTA'),
    XAxisSpec(val=12, lbl='MITSUBISHI', lbl_split_into_lines='MITSUBISHI'),
    XAxisSpec(val=13, lbl='NISSAN', lbl_split_into_lines='NISSAN'),
    XAxisSpec(val=14, lbl='MAZDA', lbl_split_into_lines='MAZDA'),
    XAxisSpec(val=15, lbl='SUZUKI', lbl_split_into_lines='SUZUKI'),
    XAxisSpec(val=16, lbl='DAIHATSU', lbl_split_into_lines='DAIHATSU'),
    XAxisSpec(val=17, lbl='ISUZU', lbl_split_into_lines='ISUZU'),
]
x_axis_specs_billing = [
    XAxisSpec(val='2022-01-01', lbl='2022-01-01', lbl_split_into_lines='2022-01-01'),
    XAxisSpec(val='2022-02-01', lbl='2022-02-01', lbl_split_into_lines='2022-02-01'),
    XAxisSpec(val='2022-03-01', lbl='2022-03-01', lbl_split_into_lines='2022-03-01'),
    XAxisSpec(val='2022-04-01', lbl='2022-04-01', lbl_split_into_lines='2022-04-01'),
    XAxisSpec(val='2022-05-01', lbl='2022-05-01', lbl_split_into_lines='2022-05-01'),
    XAxisSpec(val='2022-06-01', lbl='2022-06-01', lbl_split_into_lines='2022-06-01'),
    XAxisSpec(val='2022-07-01', lbl='2022-07-01', lbl_split_into_lines='2022-07-01'),
    XAxisSpec(val='2022-08-01', lbl='2022-08-01', lbl_split_into_lines='2022-08-01'),
    XAxisSpec(val='2022-09-01', lbl='2022-09-01', lbl_split_into_lines='2022-09-01'),
    XAxisSpec(val='2022-10-01', lbl='2022-10-01', lbl_split_into_lines='2022-10-01'),
    XAxisSpec(val='2022-11-01', lbl='2022-11-01', lbl_split_into_lines='2022-11-01'),
    XAxisSpec(val='2022-12-01', lbl='2022-12-01', lbl_split_into_lines='2022-12-01'),
    XAxisSpec(val='2023-01-01', lbl='2023-01-01', lbl_split_into_lines='2023-01-01'),
    XAxisSpec(val='2023-02-01', lbl='2023-02-01', lbl_split_into_lines='2023-02-01'),
    XAxisSpec(val='2023-03-01', lbl='2023-03-01', lbl_split_into_lines='2023-03-01'),
    XAxisSpec(val='2023-04-01', lbl='2023-04-01', lbl_split_into_lines='2023-04-01'),
    XAxisSpec(val='2023-05-01', lbl='2023-05-01', lbl_split_into_lines='2023-05-01'),
]

series_dets_cars = SeriesDetails(
    legend_lbl=None,  ## e.g. "Italy", or None if only one series
    x_axis_specs=x_axis_specs_cars,
    y_vals=[135, 62, 116, 75, 158, 80, 160, 59, 59, 98, 171, 94, 96, 92, 24, 14, 7],
    tool_tips=['135<br>9.0%', '62<br>4.1%', '116<br>7.7%', '75<br>5.0%', '158<br>10.5%', '80<br>5.3%', '160<br>10.7%',
               '59<br>3.9%', '59<br>3.9%', '98<br>6.5%', '171<br>11.4%', '94<br>6.3%', '96<br>6.4%', '92<br>6.1%',
               '24<br>1.6%', '14<br>0.9%', '7<br>0.5%'],
    ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]
)
series_dets_billing = SeriesDetails(
    legend_lbl=None,  ## e.g. "Italy", or None if only one series
    x_axis_specs=x_axis_specs_billing,
    y_vals=[135, 62, 116, 75, 158, 80, 160, 59, 59, 98, 171, 94, 96, 92, 24, 14, 7],
    tool_tips=['135<br>9.0%', '62<br>4.1%', '116<br>7.7%', '75<br>5.0%', '158<br>10.5%', '80<br>5.3%', '160<br>10.7%',
               '59<br>3.9%', '59<br>3.9%', '98<br>6.5%', '171<br>11.4%', '94<br>6.3%', '96<br>6.4%', '92<br>6.1%',
               '24<br>1.6%', '14<br>0.9%', '7<br>0.5%'],
    ## HTML tooltips ready to display e.g. ["46<br>23%", "32<br>16%", "94<br>47%"]
)

chart_details_cars = ChartDetails(
    n_records=1024,
    lbl=None,  ## e.g. "Gender: Male" or None if only one chart
    series_dets=[series_dets_cars],
)
chart_details_billing = ChartDetails(
    n_records=1024,
    lbl=None,  ## e.g. "Gender: Male" or None if only one chart
    series_dets=[series_dets_billing],  ## TODO - spec(s)
)

generic_charting_dets_cars = GenericChartingDetails(
    overall_title='overall title',
    overall_subtitle='overall subtitle',
    overall_legend_lbl='Countries',
    max_x_lbl_length=10,  ## may be needed to set chart height if labels are rotated
    max_y_lbl_length=2,  ## used to set left axis shift of chart(s) - so there is room for the y labels
    max_lbl_lines=1,  ## used to set axis lbl drop
    charts_details=[chart_details_cars],
)
generic_charting_dets_billing = GenericChartingDetails(
    overall_title='overall title',
    overall_subtitle='overall subtitle',
    overall_legend_lbl='Countries',
    max_x_lbl_length=10,  ## may be needed to set chart height if labels are rotated
    max_y_lbl_length=2,  ## used to set left axis shift of chart(s) - so there is room for the y labels
    max_lbl_lines=1,  ## used to set axis lbl drop
    charts_details=[chart_details_billing],
)

line_charting_spec_cars = LineChartingSpec(
    dp=4,
    generic_charting_dets=generic_charting_dets_cars,
    is_time_series=False,
    major_ticks=False,
    rotate_x_lbls=True,
    show_markers=True,
    show_n=True,
    show_smooth_line=True,
    show_trend_line=True,
    x_title='Car',
    x_font_size=12,
    y_title='Frequency',
)
line_charting_spec_billing = LineChartingSpec(
    dp=4,
    generic_charting_dets=generic_charting_dets_billing,
    is_time_series=True,
    major_ticks=False,
    rotate_x_lbls=True,
    show_markers=True,
    show_n=True,
    show_smooth_line=True,
    show_trend_line=True,
    x_font_size=12,
    x_title='Billing Date',
    y_title='Frequency',
)

def run_line_chart_cars():
    style_dets = get_style_dets(style='default')
    html = line.get_html(line_charting_spec_cars, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_line_chart_cars.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")
def run_line_chart_billing():
    style_dets = get_style_dets(style='default')  ## prestige_screen
    html = line.get_html(line_charting_spec_billing, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_line_chart_billing.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

# run_anova()
# run_bar_chart()
run_line_chart_cars()
run_line_chart_billing()
