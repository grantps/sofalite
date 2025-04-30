from pathlib import Path
from webbrowser import open_new_tab

import pandas as pd

# noinspection PyUnresolvedReferences
from sofalite.output.charts import area, bar, boxplot, histogram, line, pie, scatterplot  ## needed so singledispatch registration can occur
from sofalite.output.charts.area import AreaChartSpec
from sofalite.output.charts.bar import (
    ClusteredBarChartSpec, MultiBarChartSpec, MultiClusteredBarChartSpec, SimpleBarChartSpec)
from sofalite.output.charts.boxplot import BoxplotChartSpec, MultiSeriesBoxplotChartSpec
from sofalite.output.charts.histogram import HistogramChartSpec, MultiChartHistogramChartSpec
from sofalite.output.charts.line import MultiLineChartSpec
from sofalite.output.charts.pie import PieChartSpec
from sofalite.output.charts.scatterplot import (MultiChartScatterChartSpec, MultiChartSeriesScatterChartSpec,
    MultiSeriesScatterChartSpec, SingleSeriesScatterChartSpec)
from sofalite.stats_calc.interfaces import BoxplotType, SortOrder

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

def simple_bar_chart():
    chart = SimpleBarChartSpec(
        style_name='default', #'prestige_screen',
        category_fld_name='browser',
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
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_simple_bar_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Simple Bar Chart')
    open_new_tab(url=f"file://{fpath}")

def simple_bar_chart_lots_of_x_vals():
    chart = SimpleBarChartSpec(
        style_name='prestige_screen',
        category_fld_name='car',
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
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_simple_bar_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Simple Bar Chart - Lots of x values')
    open_new_tab(url=f"file://{fpath}")

def multi_bar_chart():
    chart = MultiBarChartSpec(
        style_name='default',
        chart_fld_name='country',
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
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_bar_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Multi Bar Chart')
    open_new_tab(url=f"file://{fpath}")

def clustered_bar_chart():
    chart = ClusteredBarChartSpec(
        style_name='default',
        series_fld_name='country',
        category_fld_name='gender',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_clustered_bar_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Clustered Bar Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_clustered_bar_chart():
    chart = MultiClusteredBarChartSpec(
        style_name='default',
        chart_fld_name='country',
        series_fld_name='gender',
        category_fld_name='browser',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_clustered_bar_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Multi Clustered Bar Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_line_chart():
    chart = MultiLineChartSpec(
        style_name='default',
        series_fld_name='country',
        category_fld_name='browser',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        is_time_series=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=False,
        show_trend_line=False,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_line_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Line Chart')
    open_new_tab(url=f"file://{fpath}")

def area_chart():
    chart = AreaChartSpec(
        style_name='default',
        chart_fld_name='country',
        category_fld_name='browser',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        is_time_series=False,
        show_major_ticks_only=True,
        show_markers=True,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_area_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Area Chart')
    open_new_tab(url=f"file://{fpath}")

def pie_chart():
    chart = PieChartSpec(
        style_name='default',
        chart_fld_name='country',
        category_fld_name='browser',
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
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_pie_chart_from_item.html')
    html_item_spec.to_file(fpath, 'Pie Chart')
    open_new_tab(url=f"file://{fpath}")

def single_series_scatterplot():
    chart = SingleSeriesScatterChartSpec(
        style_name='default',
        x_fld_name='age',
        y_fld_name='weight',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_single_series_scatterplot_from_item.html')
    html_item_spec.to_file(fpath, 'Pie Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_series_scatterplot():
    chart = MultiSeriesScatterChartSpec(
        style_name='default',
        series_fld_name='gender',
        x_fld_name='age',
        y_fld_name='weight',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_series_scatterplot_from_item.html')
    html_item_spec.to_file(fpath, 'Pie Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_chart_scatterplot():
    chart = MultiChartScatterChartSpec(
        style_name='default',
        chart_fld_name='gender',
        x_fld_name='age',
        y_fld_name='weight',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_chart_scatterplot_from_item.html')
    html_item_spec.to_file(fpath, 'Pie Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_chart_series_scatterplot():
    chart = MultiChartSeriesScatterChartSpec(
        style_name='default',
        chart_fld_name='gender',
        series_fld_name='country',
        x_fld_name='age',
        y_fld_name='weight',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_chart_series_scatterplot_from_item.html')
    html_item_spec.to_file(fpath, 'Pie Chart')
    open_new_tab(url=f"file://{fpath}")

def histogram_chart():
    chart = HistogramChartSpec(
        style_name='default',
        fld_name='age',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        x_axis_font_size=12,
        dp=3,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_histogram_from_item.html')
    html_item_spec.to_file(fpath, 'Histogram Chart')
    open_new_tab(url=f"file://{fpath}")

def multi_chart_histogram():
    chart = MultiChartHistogramChartSpec(
        style_name='default',
        chart_fld_name='gender',
        fld_name='age',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        x_axis_font_size=12,
        dp=3,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multi_chart_histogram_from_item.html')
    html_item_spec.to_file(fpath, 'Multi Chart Histogram Chart')
    open_new_tab(url=f"file://{fpath}")

def boxplot_chart():
    chart = BoxplotChartSpec(
        style_name='default',
        category_fld_name='browser',
        fld_name='age',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE,
        show_n_records=True,
        x_axis_font_size=12,
        dp=3,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_boxplot_from_item.html')
    html_item_spec.to_file(fpath, 'Boxplot')
    open_new_tab(url=f"file://{fpath}")

def multi_series_boxplot():
    chart = MultiSeriesBoxplotChartSpec(
        style_name='default',
        series_fld_name='gender',
        category_fld_name='country',
        fld_name='age',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.LABEL,
        boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE,
        show_n_records=True,
        x_axis_font_size=12,
        dp=3,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/test_multiseries_boxplot_from_item.html')
    html_item_spec.to_file(fpath, 'Multi-Series Boxplot')
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    # simple_bar_chart()
    # simple_bar_chart_lots_of_x_vals()
    # multi_bar_chart()
    # clustered_bar_chart()
    # multi_clustered_bar_chart()
    # multi_line_chart()
    # area_chart()
    # pie_chart()
    # single_series_scatterplot()
    # multi_series_scatterplot()
    # multi_chart_scatterplot()
    # multi_chart_series_scatterplot()
    # histogram_chart()
    # multi_chart_histogram()
    # boxplot_chart()
    multi_series_boxplot()
