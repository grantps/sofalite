from webbrowser import open_new_tab

import pandas as pd

from sofalite.conf.charts.output.non_standard import (BoxplotChartingSpec, HistoChartingSpec, ScatterChartingSpec)
from sofalite.conf.charts.output.standard import (AreaChartingSpec, BarChartingSpec, LineChartingSpec, PieChartingSpec)
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.conf.stats.interfaces import BoxplotType, SortOrder
# noinspection PyUnresolvedReferences
from sofalite.output.charts import area, bar, boxplot, histo, line, pie, scatterplot  ## needed so singledispatch registration can occur
from sofalite.output.charts.common import get_html
from sofalite.output.charts.main_interfaces import SimpleBarChartSpec
from sofalite.output.styles.misc import get_style_spec
from sofalite.sql_extraction.charts import box_vals, freq_specs, histo_vals, xys
from sofalite.sql_extraction.db import Sqlite

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

def simple_bar_chart():
    chart = SimpleBarChartSpec(
        style_name='prestige_screen',
        category_fld_name='gender',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.VALUE,
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html = chart.to_html()
    fpath = '/home/g/Documents/sofalite/reports/test_simple_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_bar_chart_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'gender'
    category_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {1: 'Male', 2: 'Female'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None, category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def clustered_bar_chart_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    category_fld_name = 'gender'
    category_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {1: 'Male', 2: 'Female'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_clustered_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_clustered_bar_chart_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    category_vals2lbls = {'Chrome': 'Google Chrome', }
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause="(gender = 1 OR browser != 'Firefox')",
            category_sort_order=SortOrder.VALUE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_clustered_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_line_chart_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec],
        is_time_series=False,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=False,
        show_trend_line=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_line_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def area_chart_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = AreaChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=False,
        show_markers=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_area_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def pie_chart_from_data():
    ## design
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## intermediate charting spec (including data)
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charting spec
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = PieChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        show_n_records=True,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_pie_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def single_series_scatterplot_from_data():
    # ## conf
    style_spec = get_style_spec(style_name='default')
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_series_xy_charting_spec(
            cur, tbl_name='demo_tbl',
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_single_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_series_scatterplot_from_data():
    # ## conf
    style_spec = get_style_spec(style_name='default')
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_series_xy_charting_spec(cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_scatterplot_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_chart_xy_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_series_scatterplot_from_data():
    ## conf
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_chart_series_xy_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            series_vals2lbls=series_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=series_fld_lbl,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def histogram_from_data():
    ## conf
    dp = 3
    style_spec = get_style_spec(style_name='default')
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = histo_vals.get_by_vals_charting_spec(
            cur, tbl_name='demo_tbl', fld_name=fld_name, fld_lbl=fld_lbl, tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    bin_lbls = intermediate_charting_spec.to_bin_lbls(dp=dp)
    x_axis_min_val, x_axis_max_val = intermediate_charting_spec.to_x_axis_range()
    charting_spec = HistoChartingSpec(
        bin_lbls=bin_lbls,
        indiv_chart_specs=indiv_chart_specs,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl=intermediate_charting_spec.fld_lbl,
        x_axis_font_size=12,
        x_axis_max_val=x_axis_max_val,
        x_axis_min_val=x_axis_min_val,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_histogram_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_histogram_from_data():
    ## conf
    dp = 3
    style_spec = get_style_spec(style_name='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = histo_vals.get_by_chart_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    bin_lbls = intermediate_charting_spec.to_bin_lbls(dp=dp)
    x_axis_min_val, x_axis_max_val = intermediate_charting_spec.to_x_axis_range()
    charting_spec = HistoChartingSpec(
        bin_lbls=bin_lbls,
        indiv_chart_specs=indiv_chart_specs,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl=intermediate_charting_spec.fld_lbl,
        x_axis_font_size=12,
        x_axis_max_val=x_axis_max_val,
        x_axis_min_val=x_axis_min_val,
    )
    ## output
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_histogram_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def boxplot_from_data():
    ## conf
    dp = 3
    style_spec = get_style_spec(style_name='default')
    category_fld_name = 'country'
    category_fld_lbl = 'Country'
    category_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = box_vals.get_by_series_category_charting_spec(cur, tbl_name='demo_tbl',
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            tbl_filt_clause=None,
            category_vals2lbls=category_vals2lbls,
            category_sort_order=SortOrder.VALUE,
            boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=dp)
    charting_spec = BoxplotChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title=intermediate_charting_spec.fld_lbl,
    )
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_boxplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_series_boxplot_from_data():
    ## conf
    dp = 3
    style_spec = get_style_spec(style_name='default')
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    category_fld_name = 'country'
    category_fld_lbl = 'Country'
    category_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = box_vals.get_by_series_category_charting_spec(cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            tbl_filt_clause=None,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            category_sort_order=SortOrder.VALUE,
            boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=dp)
    charting_spec = BoxplotChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title=intermediate_charting_spec.fld_lbl,
    )
    html = get_html(charting_spec, style_spec)
    fpath = '/home/g/Documents/sofalite/reports/test_multiseries_boxplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    simple_bar_chart()
    # multi_bar_chart_from_data()
    # clustered_bar_chart_from_data()
    # multi_clustered_bar_chart_from_data()
    # multi_line_chart_from_data()
    # area_chart_from_data()
    # pie_chart_from_data()
    # single_series_scatterplot_from_data()
    # multi_series_scatterplot_from_data()
    # multi_chart_scatterplot_from_data()
    # multi_chart_series_scatterplot_from_data()
    # histogram_from_data()
    # multi_chart_histogram_from_data()
    # boxplot_from_data()
    # multi_series_boxplot_from_data()
