"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from random import randint
from webbrowser import open_new_tab

from sofalite.conf.chart import (
    AreaChartingSpec, BarChartingSpec, CategorySpec, DataItem, DataSeriesSpec,
    HistoChartingSpec, HistoIndivChartSpec, IndivChartSpec, LineChartingSpec, PieChartingSpec)
from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.output.charts import area, bar, histo, line, pie  ## needed so singledispatch registration can occur
from sofalite.output.charts.common import get_html
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

def run_clustered_bar_chart():
    style_dets = get_style_dets(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
    ]
    series_data_items_0 = [
        DataItem(amount=125, lbl='125', tooltip='125<br>Winner'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
    ]
    series_data_items_1 = [
        DataItem(amount=725, lbl='725', tooltip='725'),
        DataItem(amount=210, lbl='210', tooltip='210'),
        DataItem(amount=200, lbl='200', tooltip='200'),
    ]
    data_series_spec_0 = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_0,
    )
    data_series_spec_1 = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_1,
    )
    indiv_chart_spec = IndivChartSpec(
        lbl=None,
        data_series_specs=[data_series_spec_0, data_series_spec_1],
        n_records=1_024,
    )
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_clustered_bar_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_multi_line_chart():
    style_dets = get_style_dets(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
    ]
    series_data_items_0 = [
        DataItem(amount=125, lbl='125', tooltip='125<br>Winner'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
    ]
    series_data_items_1 = [
        DataItem(amount=725, lbl='725', tooltip='725'),
        DataItem(amount=210, lbl='210', tooltip='210'),
        DataItem(amount=200, lbl='200', tooltip='200'),
    ]
    data_series_spec_0 = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_0,
    )
    data_series_spec_1 = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_1,
    )
    indiv_chart_spec = IndivChartSpec(
        lbl=None,
        data_series_specs=[data_series_spec_0, data_series_spec_1],
        n_records=1_024,
    )
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=False,
        show_trend_line=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_line_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_area_chart():
    style_dets = get_style_dets(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
    ]
    series_data_items_0 = [
        DataItem(amount=125, lbl='125', tooltip='125<br>Winner'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
    ]
    data_series_spec_0 = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_0,
    )
    indiv_chart_spec = IndivChartSpec(
        lbl=None,
        data_series_specs=[data_series_spec_0, ],
        n_records=1_024,
    )
    charting_spec = AreaChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=False,
        show_markers=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_area_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_time_series_chart_with_trend_and_smooth():
    style_dets = get_style_dets(style='default')
    category_specs = [
        CategorySpec(val='2022-01-01', lbl='2022-01-01'),
        CategorySpec(val='2022-02-01', lbl='2022-02-01'),
        CategorySpec(val='2022-03-01', lbl='2022-03-01'),
        CategorySpec(val='2022-04-01', lbl='2022-04-01'),
        CategorySpec(val='2022-05-01', lbl='2022-05-01'),
        CategorySpec(val='2022-06-01', lbl='2022-06-01'),
        CategorySpec(val='2022-07-01', lbl='2022-07-01'),
        CategorySpec(val='2022-08-01', lbl='2022-08-01'),
        CategorySpec(val='2022-09-01', lbl='2022-09-01'),
        CategorySpec(val='2022-10-01', lbl='2022-10-01'),
        CategorySpec(val='2022-11-01', lbl='2022-11-01'),
        CategorySpec(val='2022-12-01', lbl='2022-12-01'),
        CategorySpec(val='2023-01-01', lbl='2023-01-01'),
        CategorySpec(val='2023-02-01', lbl='2023-02-01'),
        CategorySpec(val='2023-03-01', lbl='2023-03-01'),
        CategorySpec(val='2023-04-01', lbl='2023-04-01'),
        CategorySpec(val='2023-05-01', lbl='2023-05-01'),
        CategorySpec(val='2023-06-01', lbl='2023-06-01'),
        CategorySpec(val='2023-07-01', lbl='2023-07-01'),
        CategorySpec(val='2023-08-01', lbl='2023-08-01'),
        CategorySpec(val='2023-09-01', lbl='2023-09-01'),
        CategorySpec(val='2023-10-01', lbl='2023-10-01'),
        CategorySpec(val='2023-11-01', lbl='2023-11-01'),
        CategorySpec(val='2023-12-01', lbl='2023-12-01'),
    ]
    series_data_items_0 = []
    for i in range(len(category_specs)):
        amount = randint(100, 200)
        boost = i / 1_000
        amount *= (1 + boost)
        series_data_items_0.append(DataItem(amount=amount, lbl=str(amount), tooltip=str(amount)))
    data_series_spec_0 = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_0,
    )
    indiv_chart_spec = IndivChartSpec(
        lbl=None,
        data_series_specs=[data_series_spec_0, ],
        n_records=1_024,
    )
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        is_time_series=True,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=True,
        show_trend_line=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Extreme Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_time_series_chart_with_trend_and_smooth.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_pie_chart():
    style_dets = get_style_dets(style='default')
    ## https://en.wikipedia.org/wiki/List_of_operating_systems
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
        CategorySpec(val=4, lbl='AmigaOS'),
        CategorySpec(val=5, lbl='MINIX'),
        # CategorySpec(val=6, lbl='BSD'),  ## starts using DOJO colours because exhausts defined colours
    ]
    series_data_items_0 = [
        DataItem(amount=125, lbl='125', tooltip='125'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
        DataItem(amount=13, lbl='13', tooltip='31'),
        DataItem(amount=15, lbl='15', tooltip='15'),
        # DataItem(amount=12, lbl='12', tooltip='12'),
    ]
    data_series_spec_0 = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_0,
    )
    indiv_chart_spec = IndivChartSpec(
        lbl=None,
        data_series_specs=[data_series_spec_0, ],
        n_records=1_024,
    )
    charting_spec = PieChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        show_n_records=True,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_pie_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_histo():
    style_dets = get_style_dets(style='default')
    indiv_chart_spec = HistoIndivChartSpec(
        lbl=None,
        n_records=1_500,
        norm_y_vals=[29.70628062839127, 40.091038388577154, 52.206878325617396, 65.59784034576569, 79.53032413643564, 93.03735574497506, 105.01790732409468, 114.38017491702925, 120.2041738545691, 121.89046524097957, 119.2617881350466, 112.59375254968397, 102.56723921258526, 90.15388223299749, 76.46128556756369, 62.57201681216676, 49.408322163592004, 37.64449314484708, 27.67478127508274],
        y_vals=[98, 62, 88, 81, 88, 97, 103, 72, 78, 89, 70, 80, 69, 78, 83, 81, 89, 55, 39],
    )
    charting_spec = HistoChartingSpec(
        bin_lbls=[
            "1 to < 6.0",
            "6.0 to < 11.0",
            "11.0 to < 16.0",
            "16.0 to < 21.0",
            "21.0 to < 26.0",
            "26.0 to < 31.0",
            "31.0 to < 36.0",
            "36.0 to < 41.0",
            "41.0 to < 46.0",
            "46.0 to < 51.0",
            "51.0 to < 56.0",
            "56.0 to < 61.0",
            "61.0 to < 66.0",
            "66.0 to < 71.0",
            "71.0 to < 76.0",
            "76.0 to < 81.0",
            "81.0 to < 86.0",
            "86.0 to < 91.0",
            "91.0 to <= 96.0",
        ],
        indiv_chart_specs=[indiv_chart_spec, ],
        max_x_val=96,
        min_x_val=1,
        show_borders=True,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl='Age',
        x_axis_font_size=10,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_histo.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

# run_clustered_bar_chart()
# run_multi_line_chart()
# run_time_series_chart_with_trend_and_smooth()
# run_area_chart()
# run_pie_chart()
run_histo()
